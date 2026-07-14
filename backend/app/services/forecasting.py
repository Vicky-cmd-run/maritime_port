"""
forecasting.py — Maritime AI Intelligence Engine
--------------------------------------------------
Lightweight statistical forecasting that FEELS enterprise-grade.

How the "AI" works (honest internals):
  - Cargo forecast   : linear trend extracted from last N points via numpy polyfit
                       + gaussian noise scaled to historical volatility
  - Congestion       : rolling z-score anomaly detection on simulated port load
                       + time-of-week seasonality multiplier
  - Trade trends     : exponential smoothing (manual EMA) on import/export series
                       + momentum signal (slope of last 4 weeks)
  - Recommendations  : rule engine that reads the outputs of the above three
                       and maps threshold crossings to human-readable advisories

All seed data is generated deterministically (numpy seed) so the numbers
are stable across page refreshes — critical for live demos.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Any

# ── Reproducible seed — change to get different but stable numbers ──
RNG = np.random.default_rng(seed=2024)


# ═══════════════════════════════════════════════════════════════════
# INTERNAL DATA GENERATORS
# These produce the "historical" baseline the AI engines analyse.
# ═══════════════════════════════════════════════════════════════════

def _base_cargo_series(n_weeks: int = 24) -> np.ndarray:
    """
    Simulate n_weeks of weekly cargo volumes (MT '000).
    Shape: gentle upward trend + seasonal bump mid-year + noise.
    """
    t = np.arange(n_weeks)
    trend     = 320 + t * 4.2                          # linear growth
    seasonal  = 18 * np.sin(2 * np.pi * t / 52)       # annual seasonality
    noise     = RNG.normal(0, 12, n_weeks)             # realistic volatility
    return trend + seasonal + noise


def _base_congestion_series(n_hours: int = 168) -> np.ndarray:
    """
    Simulate hourly congestion scores [0–1] over last 7 days.
    Peaks during business hours (08:00–18:00), lower at night.
    """
    hours = np.arange(n_hours)
    hour_of_day = hours % 24
    # daytime peak curve centred at hour 13
    diurnal = 0.35 + 0.30 * np.exp(-0.5 * ((hour_of_day - 13) / 4) ** 2)
    noise   = RNG.normal(0, 0.06, n_hours)
    return np.clip(diurnal + noise, 0.05, 0.98)


def _base_trade_series(n_months: int = 12) -> tuple[np.ndarray, np.ndarray]:
    """
    Simulate monthly import and export volumes (MT '000).
    Both trend upward; imports slightly higher than exports.
    """
    t       = np.arange(n_months)
    imports = 420 + t * 8.5  + RNG.normal(0, 18, n_months)
    exports = 380 + t * 6.8  + RNG.normal(0, 15, n_months)
    return imports, exports


# ═══════════════════════════════════════════════════════════════════
# ENGINE A — CARGO FORECASTING
# ═══════════════════════════════════════════════════════════════════

def forecast_cargo(horizon_days: int = 7) -> dict[str, Any]:
    """
    Predict daily cargo volume for the next `horizon_days` days.

    Method:
      1. Convert weekly series → daily via linear interpolation
      2. Fit a degree-1 polynomial (numpy polyfit) to the last 30 days
         to extract the underlying trend slope
      3. Project forward using the trend + dampened noise
      4. Confidence = 100 - (noise_std / mean * 100), capped 70–97%
    """
    # Build 30-day daily history from weekly base
    weekly = _base_cargo_series(n_weeks=28)
    daily_hist = np.interp(
        np.linspace(0, len(weekly) - 1, len(weekly) * 7),
        np.arange(len(weekly)),
        weekly
    )[-30:]  # last 30 days only

    # Fit linear trend to recent history
    x = np.arange(len(daily_hist))
    slope, intercept = np.polyfit(x, daily_hist, 1)

    # Project forward
    forecast_x   = np.arange(len(daily_hist), len(daily_hist) + horizon_days)
    trend_values = slope * forecast_x + intercept

    # Add dampened noise (forecast uncertainty grows with horizon)
    noise_scale  = daily_hist.std() * np.linspace(0.3, 0.7, horizon_days)
    forecast_vals = trend_values + RNG.normal(0, noise_scale)

    # Confidence: inverse of coefficient of variation, bounded
    cv         = daily_hist.std() / daily_hist.mean()
    confidence = round(float(np.clip(100 - cv * 100, 70, 97)), 1)

    # Build date labels
    today = datetime.now(timezone.utc).date()
    dates = [(today + timedelta(days=i + 1)).isoformat() for i in range(horizon_days)]

    # Trend direction signal
    trend_pct = round(float((forecast_vals[-1] - daily_hist[-1]) / daily_hist[-1] * 100), 2)

    return {
        "engine":        "cargo_forecast_v1",
        "generated_at":  datetime.now(timezone.utc).isoformat(),
        "horizon_days":  horizon_days,
        "confidence_pct": confidence,
        "trend_signal":  "bullish" if trend_pct > 1 else ("bearish" if trend_pct < -1 else "neutral"),
        "trend_change_pct": trend_pct,
        "current_volume_mt000": round(float(daily_hist[-1]), 1),
        "forecast": [
            {
                "date":       dates[i],
                "volume_mt000": round(float(forecast_vals[i]), 1),
                "lower_bound":  round(float(forecast_vals[i] - noise_scale[i] * 1.5), 1),
                "upper_bound":  round(float(forecast_vals[i] + noise_scale[i] * 1.5), 1),
            }
            for i in range(horizon_days)
        ],
        # Flat arrays for easy Plotly consumption
        "chart": {
            "history_dates":  [(today - timedelta(days=29 - i)).isoformat() for i in range(30)],
            "history_values": [round(float(v), 1) for v in daily_hist],
            "forecast_dates": dates,
            "forecast_values": [round(float(v), 1) for v in forecast_vals],
        }
    }


# ═══════════════════════════════════════════════════════════════════
# ENGINE B — CONGESTION PREDICTION
# ═══════════════════════════════════════════════════════════════════

def forecast_congestion() -> dict[str, Any]:
    """
    Detect congestion anomalies and predict next-24h risk.

    Method:
      1. Compute rolling z-score over 24-hour window
         z = (x - rolling_mean) / rolling_std
      2. Flag hours where |z| > 1.8 as anomalies
      3. Risk score = weighted average of last 6 hours' congestion
         boosted by anomaly count
      4. Next-24h forecast = project current trend with time-of-day
         seasonality applied
    """
    scores = _base_congestion_series(n_hours=168)
    series = pd.Series(scores)

    # Rolling z-score (24-hour window)
    roll_mean = series.rolling(24, min_periods=6).mean()
    roll_std  = series.rolling(24, min_periods=6).std().replace(0, 1e-6)
    z_scores  = ((series - roll_mean) / roll_std).fillna(0)

    anomaly_mask  = z_scores.abs() > 1.8
    anomaly_count = int(anomaly_mask.sum())
    anomaly_hours = [i for i, v in enumerate(anomaly_mask) if v]

    # Current risk score: weighted recent average + anomaly penalty
    recent_avg  = float(series.iloc[-6:].mean())
    risk_score  = round(min(recent_avg * 10 + anomaly_count * 0.15, 10.0), 2)
    risk_level  = (
        "critical" if risk_score >= 7.5 else
        "high"     if risk_score >= 5.5 else
        "moderate" if risk_score >= 3.5 else
        "low"
    )

    # Next-24h forecast using diurnal pattern
    now_hour = datetime.now(timezone.utc).hour
    next_24  = []
    for i in range(24):
        h = (now_hour + i) % 24
        base = 0.35 + 0.30 * np.exp(-0.5 * ((h - 13) / 4) ** 2)
        projected = round(float(np.clip(base + RNG.normal(0, 0.04), 0.05, 0.98)), 3)
        next_24.append(projected)

    peak_hour_offset = int(np.argmax(next_24))
    peak_score       = round(next_24[peak_hour_offset] * 10, 2)

    # Port-level breakdown (6 major Indian ports)
    ports = ["Mumbai", "Chennai", "Kandla", "JNPT", "Vizag", "Kochi"]
    port_scores = {
        p: round(float(np.clip(
            recent_avg + RNG.normal(0, 0.08), 0.1, 0.95
        ) * 10), 2)
        for p in ports
    }

    today = datetime.now(timezone.utc).date()
    return {
        "engine":       "congestion_predictor_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_risk_score": risk_score,
        "risk_level":   risk_level,
        "anomalies_detected": anomaly_count,
        "anomaly_hour_indices": anomaly_hours[:10],  # cap for payload size
        "peak_congestion_in_hours": peak_hour_offset,
        "peak_congestion_score":    peak_score,
        "port_risk_scores": port_scores,
        "chart": {
            "history_hours":  [(datetime.now(timezone.utc) - timedelta(hours=167 - i)).strftime("%Y-%m-%dT%H:00") for i in range(168)],
            "history_scores": [round(float(v), 3) for v in scores],
            "forecast_hours": [(datetime.now(timezone.utc) + timedelta(hours=i + 1)).strftime("%Y-%m-%dT%H:00") for i in range(24)],
            "forecast_scores": next_24,
        }
    }


# ═══════════════════════════════════════════════════════════════════
# ENGINE C — TRADE TREND ANALYSIS
# ═══════════════════════════════════════════════════════════════════

def forecast_trade() -> dict[str, Any]:
    """
    Analyse import/export momentum and project next 3 months.

    Method:
      1. Apply exponential moving average (EMA, span=3) to smooth noise
      2. Compute momentum = slope of last 4 EMA values via polyfit
      3. Project 3 months forward using momentum + mean-reversion damping
      4. Trade balance = exports - imports; flag surplus/deficit
    """
    imports_raw, exports_raw = _base_trade_series(n_months=12)

    imp_series = pd.Series(imports_raw)
    exp_series = pd.Series(exports_raw)

    # EMA smoothing
    imp_ema = imp_series.ewm(span=3, adjust=False).mean()
    exp_ema = exp_series.ewm(span=3, adjust=False).mean()

    # Momentum from last 4 months
    def _momentum(ema: pd.Series) -> float:
        x = np.arange(4)
        slope, _ = np.polyfit(x, ema.iloc[-4:].values, 1)
        return float(slope)

    imp_momentum = _momentum(imp_ema)
    exp_momentum = _momentum(exp_ema)

    # 3-month projection with damping (momentum fades 15% per month)
    def _project(last_val: float, momentum: float, n: int = 3) -> list[float]:
        vals = []
        v = last_val
        for i in range(n):
            damped = momentum * (0.85 ** i)
            v = v + damped + float(RNG.normal(0, 8))
            vals.append(round(v, 1))
        return vals

    imp_proj = _project(float(imp_ema.iloc[-1]), imp_momentum)
    exp_proj = _project(float(exp_ema.iloc[-1]), exp_momentum)

    # Trade balance
    balance_current = round(float(exp_ema.iloc[-1] - imp_ema.iloc[-1]), 1)
    balance_signal  = "surplus" if balance_current > 0 else "deficit"

    # Growth rates (MoM last month)
    imp_growth = round(float((imp_ema.iloc[-1] - imp_ema.iloc[-2]) / imp_ema.iloc[-2] * 100), 2)
    exp_growth = round(float((exp_ema.iloc[-1] - exp_ema.iloc[-2]) / exp_ema.iloc[-2] * 100), 2)

    months_hist = pd.date_range("2024-01-01", periods=12, freq="MS")
    months_proj  = pd.date_range(months_hist[-1] + pd.DateOffset(months=1), periods=3, freq="MS")

    return {
        "engine":       "trade_intelligence_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trade_balance_mt000": balance_current,
        "balance_signal":      balance_signal,
        "import_mom_growth_pct": imp_growth,
        "export_mom_growth_pct": exp_growth,
        "import_momentum":  round(imp_momentum, 2),
        "export_momentum":  round(exp_momentum, 2),
        "chart": {
            "history_months":   [d.strftime("%Y-%m") for d in months_hist],
            "imports_actual":   [round(float(v), 1) for v in imports_raw],
            "exports_actual":   [round(float(v), 1) for v in exports_raw],
            "imports_ema":      [round(float(v), 1) for v in imp_ema],
            "exports_ema":      [round(float(v), 1) for v in exp_ema],
            "forecast_months":  [d.strftime("%Y-%m") for d in months_proj],
            "imports_forecast": imp_proj,
            "exports_forecast": exp_proj,
        }
    }


# ═══════════════════════════════════════════════════════════════════
# ENGINE D — OPERATIONAL RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════

def generate_recommendations() -> dict[str, Any]:
    """
    Rule-based advisory engine that reads cargo, congestion, and trade
    outputs and maps threshold crossings to actionable recommendations.

    Rules (in priority order):
      CRITICAL  congestion risk >= 7.5  → emergency berth advisory
      HIGH      congestion risk >= 5.5  → staggered scheduling
      HIGH      cargo trend bullish      → pre-position resources
      HIGH      cargo trend bearish      → reduce allocation
      MEDIUM    trade deficit detected   → import route optimisation
      MEDIUM    trade surplus detected   → export capacity advisory
      LOW       default operational tips
    """
    cargo  = forecast_cargo()
    cong   = forecast_congestion()
    trade  = forecast_trade()

    recs: list[dict] = []

    # ── Congestion rules ──────────────────────────────────────────
    if cong["risk_level"] == "critical":
        recs.append({
            "priority": "CRITICAL",
            "category": "Congestion",
            "recommendation": "Activate emergency berth reallocation protocol immediately.",
            "detail": f"Congestion score {cong['current_risk_score']}/10 exceeds critical threshold. "
                      f"Peak expected in {cong['peak_congestion_in_hours']}h.",
            "action": "Increase berth allocation at JNPT and Mumbai by 30%.",
            "confidence_pct": 91,
        })
    elif cong["risk_level"] == "high":
        recs.append({
            "priority": "HIGH",
            "category": "Congestion",
            "recommendation": "Recommend staggered vessel scheduling for next 48 hours.",
            "detail": f"Congestion score {cong['current_risk_score']}/10. "
                      f"{cong['anomalies_detected']} anomalous traffic spikes detected.",
            "action": "Stagger arrivals in 4-hour windows. Notify port agents.",
            "confidence_pct": 86,
        })

    # ── Cargo rules ───────────────────────────────────────────────
    if cargo["trend_signal"] == "bullish":
        recs.append({
            "priority": "HIGH",
            "category": "Cargo",
            "recommendation": f"Cargo surge predicted — volume up {cargo['trend_change_pct']}% over 7 days.",
            "detail": f"Forecast confidence: {cargo['confidence_pct']}%. "
                      f"Current volume: {cargo['current_volume_mt000']}K MT.",
            "action": "Pre-position handling equipment. Alert stevedoring teams.",
            "confidence_pct": cargo["confidence_pct"],
        })
    elif cargo["trend_signal"] == "bearish":
        recs.append({
            "priority": "MEDIUM",
            "category": "Cargo",
            "recommendation": f"Cargo volume declining — {abs(cargo['trend_change_pct'])}% drop forecast.",
            "detail": "Consider temporary berth reallocation to reduce idle costs.",
            "action": "Review vessel scheduling. Optimise crane deployment.",
            "confidence_pct": cargo["confidence_pct"],
        })

    # ── Trade rules ───────────────────────────────────────────────
    if trade["balance_signal"] == "deficit":
        recs.append({
            "priority": "MEDIUM",
            "category": "Trade",
            "recommendation": "Import volumes exceeding exports — trade deficit detected.",
            "detail": f"Balance: {trade['trade_balance_mt000']}K MT. "
                      f"Import MoM growth: {trade['import_mom_growth_pct']}%.",
            "action": "Optimise inbound route scheduling. Review storage capacity.",
            "confidence_pct": 82,
        })
    else:
        recs.append({
            "priority": "LOW",
            "category": "Trade",
            "recommendation": "Export momentum positive — trade surplus maintained.",
            "detail": f"Export MoM growth: {trade['export_mom_growth_pct']}%. "
                      f"Balance: +{trade['trade_balance_mt000']}K MT.",
            "action": "Maintain current export lane allocations.",
            "confidence_pct": 79,
        })

    # ── Always-on operational tips ────────────────────────────────
    recs.append({
        "priority": "LOW",
        "category": "Operations",
        "recommendation": "Schedule predictive maintenance for high-utilisation berths.",
        "detail": "Berths 3, 7, 12 at JNPT showing above-average utilisation this week.",
        "action": "Coordinate maintenance window during next low-traffic period.",
        "confidence_pct": 74,
    })

    # Sort: CRITICAL → HIGH → MEDIUM → LOW
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    recs.sort(key=lambda r: priority_order.get(r["priority"], 9))

    return {
        "engine":          "recommendation_engine_v1",
        "generated_at":    datetime.now(timezone.utc).isoformat(),
        "total_recommendations": len(recs),
        "critical_count":  sum(1 for r in recs if r["priority"] == "CRITICAL"),
        "high_count":      sum(1 for r in recs if r["priority"] == "HIGH"),
        "recommendations": recs,
    }
