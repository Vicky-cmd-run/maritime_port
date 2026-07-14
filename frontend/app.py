"""
YellowSense Maritime Intelligence Platform
==========================================
AI-Powered Maritime Port Intelligence & Decision Support Platform
Production-grade PoC — Warm Amber Theme, 9-Tab Horizontal Navigation
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timezone
from pathlib import Path
import base64
import time
import os

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="YellowSense Maritime Intelligence",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Constants ────────────────────────────────────────────────────────────────
API = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
LOGO_PATH = Path(__file__).parent.parent / "assets" / "logo11.png"
ARCH_DIR = Path(__file__).parent.parent

COMMODITY_COLORS = {
    "Coal": "#374151", "Iron Ore": "#DC2626", "Containers": "#2563EB",
    "Crude Oil": "#7C3AED", "LNG": "#059669", "Fertilizers": "#D97706",
    "Automobiles": "#0891B2", "Agricultural": "#65A30D",
}

SEVERITY_COLORS = {"Critical": "#DC2626", "High": "#D97706", "Medium": "#2563EB", "Low": "#059669"}
SEVERITY_BG = {"Critical": "#FEF2F2", "High": "#FFFBEB", "Medium": "#EFF6FF", "Low": "#F0FDF4"}

# ─── API Helper ───────────────────────────────────────────────────────────────
def api_get(path: str, params: dict = None):
    try:
        r = requests.get(f"{API}{path}", params=params, timeout=6)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"API GET Error ({path}): {e}")
        return None

def api_post(path: str, payload: dict = None):
    try:
        r = requests.post(f"{API}{path}", json=payload or {}, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"API POST Error ({path}): {e}")
        st.error(f"Backend API Error: {e}")
        return None

# ─── Logo Helper ──────────────────────────────────────────────────────────────
def get_logo_b64():
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# ─── Premium CSS — Cream / YellowSense Brand (Ref: Image 4) ── */
st.markdown("""
<style>
/* Using System Native Fonts */

/* ── Reset & Base ── */
html, body, [class*="css"] { font-family: system-ui, sans-serif; }
h1,h2,h3,h4,h5,h6 { font-family: system-ui, sans-serif; }

/* ── App Background — Very Pale Cream ── */
.stApp {
    background: #FCFAF5;
    color: #292524;
    min-height: 100vh;
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem;
    max-width: 1200px !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header, [data-testid="stSidebarNav"] { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }

/* ── Floating Header Card ── */
.ys-header {
    background: #FFFDF9;
    padding: 16px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    margin-bottom: 20px;
    border: 1px solid #F3E8D6;
}
.ys-header-left {
    display: flex;
    align-items: center;
    gap: 16px;
}
.ys-header-logo {
    height: 48px;
    width: auto;
    object-fit: contain;
}
.ys-header-title {
    font-family: system-ui, sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #1C1917;
    letter-spacing: -0.3px;
    line-height: 1.1;
}
.ys-header-subtitle {
    font-size: 13px;
    color: #92400E;
    font-weight: 600;
}
.ys-header-right {
    display: flex;
    align-items: center;
}
.ys-live-badge {
    background: #FEF3C7;
    color: #92400E;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    border: 1px solid #FDE68A;
}

/* ── Tab Navigation Pills ── */
div.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 8px;
    border-bottom: none;
    margin-bottom: 20px;
}
div.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 20px;
    color: #78716C;
    font-family: system-ui, sans-serif;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 18px;
    border: none;
    transition: all 0.2s ease;
}
div.stTabs [aria-selected="true"] {
    background: #FEF3C7 !important;
    color: #92400E !important;
    border-bottom: 2px solid #EF4444 !important;
    border-radius: 12px 12px 0 0;
    box-shadow: none !important;
}

/* ── Page Content Wrapper ── */
.ys-content {
    padding: 10px 0;
}

/* ── Section Headers ── */
.sec-title {
    font-family: system-ui, sans-serif;
    font-size: 24px;
    font-weight: 800;
    color: #1C1917;
    letter-spacing: -0.4px;
    margin: 0;
}
.sec-sub {
    font-size: 14px;
    color: #78716C;
    margin-top: 6px;
    margin-bottom: 24px;
}
.sec-tag { display: none; }

/* ── Cards / Panels ── */
.kpi-card, .panel, div[data-testid="stMetric"], .pipeline-stage, .copilot-response {
    background: #FFFFFF;
    border: 1px solid #F3E8D6;
    border-radius: 12px;
    padding: 20px 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}
.panel-title {
    font-family: system-ui, sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #1C1917;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #F9F5EC;
}

div[data-testid="stMetricLabel"] { font-size: 11px; font-weight: 700; color: #78716C !important; text-transform: uppercase; letter-spacing: 0.6px; }
div[data-testid="stMetricValue"] { font-family: system-ui, sans-serif; font-size: 28px; font-weight: 800; color: #1C1917 !important; }

/* ── Custom Button ── */
div.stButton > button {
    background: #EAB308 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: system-ui, sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 8px 24px !important;
    box-shadow: 0 2px 4px rgba(234,179,8,0.2) !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:hover {
    background: #CA8A04 !important;
    box-shadow: 0 4px 8px rgba(202,138,4,0.3) !important;
}

/* ── Trace Steps & Logs ── */
.trace-step {
    display: flex; align-items: flex-start; gap: 14px;
    padding: 12px 16px; border-radius: 8px; margin-bottom: 8px;
    background: #FCFAF5; border: 1px solid #F3E8D6;
}
.trace-num {
    background: #EAB308; color: #FFFFFF;
    font-family: system-ui, sans-serif; font-weight: 800; font-size: 13px;
    width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.trace-component { font-weight: 700; font-size: 13px; color: #1C1917; }
.trace-action    { font-size: 13px; color: #44403C; }
.trace-detail    { font-size: 11px; color: #78716C; margin-top: 2px; }
.trace-ms        { font-size: 11px; color: #CA8A04; font-weight: 600; margin-left: auto; }

.log-container {
    background: #FCFAF5; border: 1px solid #F3E8D6; border-radius: 10px;
    padding: 16px; max-height: 340px; overflow-y: auto;
    font-family: 'JetBrains Mono', 'Courier New', monospace; font-size: 12px;
}
.log-row { padding: 4px 0; border-bottom: 1px solid #F9F5EC; display: flex; gap: 10px; }
.log-ts   { color: #A8A29E; min-width: 65px; }
.log-src  { color: #1C1917; font-weight: 700; min-width: 95px; }
.log-info { color: #57534E; }
.log-warn { color: #D97706; }

.stDataFrame { border: 1px solid #F3E8D6; border-radius: 8px; }
.stTextArea textarea { border: 1px solid #F3E8D6 !important; border-radius: 8px !important; background: #FFFFFF !important; }
.stTextArea textarea:focus { border-color: #EAB308 !important; box-shadow: 0 0 0 2px rgba(234,179,8,0.2) !important; }
.stSpinner > div { border-top-color: #EAB308 !important; }

/* ── Restored Missing Components ── */
.alert-card { border-radius: 10px; padding: 16px 18px; margin-bottom: 12px; border-left: 4px solid; }
.alert-critical { background: #FEF2F2; border-color: #DC2626; }
.alert-high     { background: #FFFBEB; border-color: #D97706; }
.alert-medium   { background: #EFF6FF; border-color: #2563EB; }
.alert-low      { background: #F0FDF4; border-color: #059669; }
.alert-title    { font-family: system-ui, sans-serif; font-size: 14px; font-weight: 700; color: #1C1917; }
.alert-desc     { font-size: 12px; color: #78716C; margin-top: 5px; line-height: 1.5; }
.alert-meta     { font-size: 11px; color: #92400E; margin-top: 8px; display: flex; gap: 16px; flex-wrap: wrap; }
.badge          { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
.badge-crit     { background: #FEE2E2; color: #DC2626; }
.badge-high     { background: #FEF3C7; color: #D97706; }
.badge-med      { background: #DBEAFE; color: #2563EB; }
.badge-low      { background: #DCFCE7; color: #059669; }

.rec-card { background: #FFFFFF; border: 1px solid #F3E8D6; border-radius: 12px; padding: 18px 20px; margin-bottom: 14px; border-left: 5px solid #F59E0B; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
.rec-action     { font-family: system-ui, sans-serif; font-size: 15px; font-weight: 700; color: #1C1917; }
.rec-rationale  { font-size: 12px; color: #78716C; margin-top: 5px; line-height: 1.5; }
.rec-impacts    { display: flex; gap: 16px; margin-top: 12px; flex-wrap: wrap; }
.rec-impact-pos { color: #059669; font-size: 13px; font-weight: 700; }
.rec-impact-neg { color: #DC2626; font-size: 13px; font-weight: 700; }
.rec-meta       { font-size: 11px; color: #92400E; margin-top: 8px; display: flex; gap: 14px; flex-wrap: wrap; }

.event-row { display: flex; align-items: flex-start; gap: 12px; padding: 10px 0; border-bottom: 1px solid #F3E8D6; }
.event-time { font-size: 11px; color: #78716C; min-width: 48px; font-weight: 600; }
.event-dot  { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
.event-dot-arrival  { background: #059669; }
.event-dot-alert    { background: #DC2626; }
.event-dot-departure{ background: #2563EB; }
.event-dot-forecast { background: #7C3AED; }
.event-dot-incentive{ background: #F59E0B; }
.event-dot-system   { background: #78716C; }
.event-msg  { font-size: 12.5px; color: #1C1917; line-height: 1.4; }

.opp-card { background: #FFFFFF; border: 1px solid #F3E8D6; border-left: 5px solid #F59E0B; border-radius: 12px; padding: 16px 18px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
.opp-rank        { font-family: system-ui, sans-serif; font-size: 24px; font-weight: 900; color: #F59E0B; }
.opp-commodity   { font-size: 13px; font-weight: 700; color: #92400E; }
.opp-route       { font-size: 12px; color: #57534E; margin: 3px 0; }
.opp-opportunity { font-size: 12px; color: #1C1917; line-height: 1.5; margin-top: 6px; }
.opp-metrics     { display: flex; gap: 14px; margin-top: 10px; }
.opp-revenue     { font-size: 15px; font-weight: 800; color: #059669; font-family: system-ui, sans-serif; }

.pipeline-stage-title { font-family: system-ui, sans-serif; font-size: 14px; font-weight: 700; color: #1C1917; margin-bottom: 6px; }
.pipeline-stage-sub   { font-size: 11px; color: #78716C; line-height: 1.4; }

/* Plotly Theme Updates */
.js-plotly-plot .plotly { border-radius: 10px; overflow: hidden; background: #FFFFFF; }

</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
logo_b64 = get_logo_b64()
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="ys-header-logo" />' if logo_b64 else ""
ts = datetime.now(timezone.utc).strftime("%d %b %Y  %H:%M UTC")

st.markdown(f"""
<div class="ys-header">
  <div class="ys-header-left">
    {logo_html}
    <div>
      <div class="ys-header-title">Maritime Intelligence Platform</div>
      <div class="ys-header-subtitle">AI-POWERED PORT DECISION SUPPORT SYSTEM</div>
    </div>
  </div>
  <div class="ys-header-right">
    <div class="ys-live-badge">
      <div class="ys-live-dot"></div>
      LIVE DATA
    </div>
    <div class="ys-timestamp">{ts}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Plotly Theme ─────────────────────────────────────────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#FFFFFF",
    font=dict(family="system-ui, sans-serif", color="#1C1917", size=13),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor="#F9F5EC", linecolor="#E5E7EB", tickfont=dict(color="#1C1917", size=12), title=dict(font=dict(color="#1C1917", size=14, weight="bold"))),
    yaxis=dict(gridcolor="#F9F5EC", linecolor="#E5E7EB", tickfont=dict(color="#1C1917", size=12), title=dict(font=dict(color="#1C1917", size=14, weight="bold"))),
)
GOLD = "#F59E0B"
GOLD_DARK = "#D97706"
GOLD_LIGHT = "#FDE68A"

# ─── Tab Navigation ───────────────────────────────────────────────────────────
tabs = st.tabs([
    "Executive Dashboard",
    "Vessel Intelligence",
    "Cargo Forecasting",
    "Trade Intelligence",
    "Anomaly Detection",
    "Incentive Engine",
    "Digital Twin",
    "AI Maritime Copilot",
    "Data Pipeline",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EXECUTIVE DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="ys-content">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-header">
      <span class="sec-title">Executive Command Center</span>
      <span class="sec-tag">Real-Time</span>
      <div class="sec-sub">Port-wide operational intelligence — live KPIs, vessel positions, berth utilization & revenue</div>
    </div>""", unsafe_allow_html=True)

    kpis = api_get("/executive/kpis") or {
        "berth_utilization_pct": 72.4, "berth_delta": "+2.1%",
        "active_vessels_inbound": 25, "vessels_delta": "+3",
        "daily_throughput_mt": 124000, "throughput_delta": "+3.2%",
        "revenue_cr": 118.5, "revenue_delta": "+6.8%",
        "congestion_index": 0.63, "congestion_delta": "-0.04",
        "vessels_at_anchor": 7, "anchor_delta": "+2",
        "avg_turnaround_hrs": 22.4, "turnaround_delta": "-1.2%",
        "forecast_accuracy_pct": 91.2, "accuracy_delta": "+0.8%",
    }

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Berth Utilization", f"{kpis['berth_utilization_pct']}%", kpis['berth_delta'])
        st.metric("Avg Turnaround", f"{kpis['avg_turnaround_hrs']}h", kpis['turnaround_delta'])
    with c2:
        st.metric("Vessels Inbound", str(kpis['active_vessels_inbound']), kpis['vessels_delta'])
        st.metric("Vessels at Anchor", str(kpis['vessels_at_anchor']), kpis['anchor_delta'])
    with c3:
        st.metric("Daily Throughput", f"{kpis['daily_throughput_mt']:,} MT", kpis['throughput_delta'])
        st.metric("Forecast Accuracy", f"{kpis['forecast_accuracy_pct']}%", kpis['accuracy_delta'])
    with c4:
        st.metric("Revenue Index", f"₹{kpis['revenue_cr']} Cr", kpis['revenue_delta'])
        st.metric("Congestion Index", f"{kpis['congestion_index']}", kpis['congestion_delta'])

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([3, 2])

    with col_left:
        # Vessel Map
        vessels_data = api_get("/vessels/") or {"vessels": []}
        vessels = vessels_data.get("vessels", [])
        if vessels:
            df_v = pd.DataFrame(vessels)
            fig_map = px.scatter(
                df_v, x="lon", y="lat", size="capacity_mt",
                color="commodity", color_discrete_map=COMMODITY_COLORS,
                hover_name="name", hover_data={"commodity": True, "destination_name": True, "speed_kn": True, "delay_prob": True},
                title="Live Vessel Positions (Indian Ocean / Bay of Bengal)",
                size_max=28,
            )
            fig_map.update_layout(**PLOTLY_THEME, height=360, showlegend=True,
                                   legend=dict(orientation="h", y=-0.15, font=dict(size=10)))
            fig_map.update_traces(marker=dict(opacity=0.85, line=dict(width=0.5, color="white")))
            st.plotly_chart(fig_map, use_container_width=True)

        # Revenue & Throughput Trend
        trend = api_get("/executive/revenue-trend") or {"dates": [], "revenue_cr": [], "throughput_mt": []}
        if trend.get("dates"):
            fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
            fig_trend.add_trace(go.Scatter(
                x=trend["dates"], y=trend["revenue_cr"], name="Revenue (₹ Cr)",
                line=dict(color=GOLD, width=2.5), fill="tozeroy",
                fillcolor="rgba(245,158,11,0.08)"
            ), secondary_y=False)
            fig_trend.add_trace(go.Scatter(
                x=trend["dates"], y=trend["throughput_mt"], name="Throughput (MT)",
                line=dict(color="#2563EB", width=2, dash="dot")
            ), secondary_y=True)
            fig_trend.update_layout(**PLOTLY_THEME, height=260, title="30-Day Revenue & Throughput Trend",
                                     legend=dict(orientation="h", y=-0.2))
            fig_trend.update_yaxes(title_text="Revenue (₹ Cr)", secondary_y=False,
                                    gridcolor="#FEF3C7", linecolor="#FDE68A")
            fig_trend.update_yaxes(title_text="Throughput (MT)", secondary_y=True,
                                    gridcolor="rgba(0,0,0,0)", linecolor="#FDE68A")
            st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        # Berth Status
        berths_data = api_get("/cargo/berths") or {"berths": []}
        berths = berths_data.get("berths", [])
        if berths:
            df_b = pd.DataFrame(berths)
            occupied_pct = df_b["occupied"].mean() * 100
            fig_berth = go.Figure(go.Bar(
                x=df_b["berth_id"],
                y=df_b["utilization_pct"],
                marker_color=[GOLD if o else "#E5E7EB" for o in df_b["occupied"]],
                text=df_b["commodity"].fillna("Free"),
                textposition="outside",
                textfont=dict(size=9),
            ))
            fig_berth.update_layout(**PLOTLY_THEME, height=260,
                                     title=f"Berth Occupancy — {occupied_pct:.0f}% Utilized",
                                     xaxis_title="Berth", yaxis_title="Utilization %")
            fig_berth.update_yaxes(range=[0, 115], gridcolor="#FEF3C7")
            st.plotly_chart(fig_berth, use_container_width=True)

        # Cargo by Commodity Donut
        if vessels:
            comm_counts = df_v["commodity"].value_counts().reset_index()
            comm_counts.columns = ["commodity", "count"]
            fig_donut = px.pie(
                comm_counts, names="commodity", values="count",
                color="commodity", color_discrete_map=COMMODITY_COLORS,
                title="Active Vessels by Commodity", hole=0.55,
            )
            fig_donut.update_layout(**PLOTLY_THEME, height=260,
                                     legend=dict(orientation="h", y=-0.1, font=dict(size=10)))
            fig_donut.update_traces(textposition="inside", textinfo="percent+label",
                                     textfont_size=10)
            st.plotly_chart(fig_donut, use_container_width=True)

        # Port Events
        st.markdown('<div class="panel"><div class="panel-title">Recent Port Events</div>', unsafe_allow_html=True)
        evts = api_get("/executive/events") or {"events": []}
        for e in evts.get("events", [])[:6]:
            dot_class = f"event-dot-{e.get('type', 'system')}"
            st.markdown(f"""
            <div class="event-row">
              <div class="event-time">{e['time']}</div>
              <div class="event-dot {dot_class}"></div>
              <div class="event-msg">{e['message']}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — VESSEL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="ys-content">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-header">
      <span class="sec-title">Global Vessel Intelligence Engine</span>
      <span class="sec-tag">Module 1</span>
      <div class="sec-sub">AIS tracking, ETA predictions, delay probability, route risk scoring — Kafka + Spark pipeline</div>
    </div>""", unsafe_allow_html=True)

    v_data = api_get("/vessels/") or {"vessels": []}
    alerts_data = api_get("/vessels/congestion-alerts") or {"alerts": []}
    vessels = v_data.get("vessels", [])
    alerts = alerts_data.get("alerts", [])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Vessels Tracked", len(vessels))
    c2.metric("High Risk Vessels", len([v for v in vessels if v.get("route_risk", 0) > 0.7]))
    c3.metric("Vessels < 48h ETA", len([v for v in vessels if v.get("hours_to_arrival", 999) < 48]))
    c4.metric("Avg Delay Probability", f"{sum(v.get('delay_prob',0) for v in vessels)/max(len(vessels),1):.0%}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])

    with col_l:
        if vessels:
            df_v = pd.DataFrame(vessels)
            show_cols = ["name", "flag", "commodity", "destination_name", "hours_to_arrival",
                         "speed_kn", "delay_prob", "route_risk", "status"]
            df_show = df_v[show_cols].copy()
            df_show.columns = ["Vessel", "Flag", "Commodity", "Destination", "ETA (hrs)",
                                "Speed (kn)", "Delay Prob", "Route Risk", "Status"]
            df_show = df_show.sort_values("ETA (hrs)")
            st.markdown('<div class="panel"><div class="panel-title">Vessel Tracker — 25 Active Vessels</div>', unsafe_allow_html=True)
            st.dataframe(df_show, use_container_width=True, height=380,
                         column_config={
                             "Delay Prob": st.column_config.ProgressColumn("Delay Prob", min_value=0, max_value=1, format="%.0%"),
                             "Route Risk": st.column_config.ProgressColumn("Route Risk", min_value=0, max_value=1, format="%.2f"),
                         })
            st.markdown('</div>', unsafe_allow_html=True)

            # ETA chart
            top_eta = df_v.nsmallest(15, "hours_to_arrival")
            fig_eta = px.bar(top_eta, x="hours_to_arrival", y="name", orientation="h",
                             color="commodity", color_discrete_map=COMMODITY_COLORS,
                             title="Next 15 Arrivals — Hours to Port",
                             labels={"hours_to_arrival": "Hours to Arrival", "name": ""})
            fig_eta.update_layout(**PLOTLY_THEME, height=380)
            fig_eta.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_eta, use_container_width=True)

    with col_r:
        st.markdown('<div class="panel"><div class="panel-title">Congestion Alerts</div>', unsafe_allow_html=True)
        if alerts:
            for a in alerts[:6]:
                sev = a.get("severity", "Medium")
                css_class = f"alert-{sev.lower()}"
                badge_class = f"badge-{sev[:4].lower()}"
                st.markdown(f"""
                <div class="alert-card {css_class}">
                  <div class="alert-title">{a['vessel']}</div>
                  <div class="alert-desc">{a['message']}</div>
                  <div class="alert-meta">
                    <span><b>Commodity:</b> {a['commodity']}</span>
                    <span><b>ETA:</b> {a['hours_to_arrival']}h</span>
                    <span><b>Risk:</b> {a['route_risk']:.2f}</span>
                    <span class="badge {badge_class}">{sev}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No active congestion alerts.")
        st.markdown('</div>', unsafe_allow_html=True)

        if vessels:
            df_risk = pd.DataFrame(vessels)
            fig_risk = px.scatter(df_risk, x="delay_prob", y="route_risk",
                                  size="capacity_mt", color="commodity",
                                  color_discrete_map=COMMODITY_COLORS,
                                  hover_name="name",
                                  title="Route Risk vs Delay Probability",
                                  labels={"delay_prob": "Delay Probability", "route_risk": "Route Risk Score"})
            fig_risk.add_hline(y=0.7, line_dash="dash", line_color="#DC2626", annotation_text="High Risk Threshold")
            fig_risk.add_vline(x=0.35, line_dash="dash", line_color="#D97706", annotation_text="High Delay")
            fig_risk.update_layout(**PLOTLY_THEME, height=300)
            st.plotly_chart(fig_risk, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CARGO FORECASTING
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="ys-content">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-header">
      <span class="sec-title">Cargo Demand Forecasting Engine</span>
      <span class="sec-tag">Module 2</span>
      <div class="sec-sub">Multi-horizon predictions — Prophet · XGBoost · TFT · PatchTST · Informer — Target: 85%+ MAPE</div>
    </div>""", unsafe_allow_html=True)

    col_ctrl, col_comm = st.columns([1, 2])
    with col_ctrl:
        horizon = st.selectbox("Forecast Horizon", [7, 30, 90, 365],
                               format_func=lambda x: {7:"7 Days",30:"30 Days",90:"90 Days",365:"1 Year"}[x], index=1)
    with col_comm:
        selected_comm = st.selectbox("Commodity", list(COMMODITY_COLORS.keys()), index=0)

    fc_data = api_get("/cargo/forecast", {"horizon": horizon}) or {"forecasts": {}}
    forecasts = fc_data.get("forecasts", {})
    acc_data = api_get("/cargo/accuracy") or {"models": []}

    if forecasts and selected_comm in forecasts:
        fc = forecasts[selected_comm]
        col_l, col_r = st.columns([3, 1])
        with col_l:
            fig_fc = go.Figure()
            fig_fc.add_trace(go.Scatter(
                x=fc["historical_dates"], y=fc["historical_values"],
                name="Historical", line=dict(color="#78716C", width=2)
            ))
            fig_fc.add_trace(go.Scatter(
                x=fc["forecast_dates"] + fc["forecast_dates"][::-1],
                y=fc["conf_high"] + fc["conf_low"][::-1],
                fill="toself", fillcolor="rgba(245,158,11,0.1)",
                line=dict(color="rgba(0,0,0,0)"), name="Confidence Band", showlegend=True
            ))
            fig_fc.add_trace(go.Scatter(
                x=fc["forecast_dates"], y=fc["forecast_values"],
                name="Forecast", line=dict(color=GOLD, width=2.5, dash="dash"),
                mode="lines+markers", marker=dict(size=5)
            ))
            trend_label = f"+{fc['trend_pct_annual']}% pa" if fc['trend_pct_annual'] > 0 else f"{fc['trend_pct_annual']}% pa"
            fig_fc.update_layout(**PLOTLY_THEME, height=380,
                                  title=f"{selected_comm} Cargo Volume Forecast — {horizon}-Day Horizon  ({trend_label})",
                                  xaxis_title="Date", yaxis_title="Volume (MT)")
            st.plotly_chart(fig_fc, use_container_width=True)

        with col_r:
            st.markdown('<div class="panel"><div class="panel-title">Forecast Stats</div>', unsafe_allow_html=True)
            avg_hist = sum(fc["historical_values"]) / len(fc["historical_values"])
            avg_fore = sum(fc["forecast_values"]) / len(fc["forecast_values"])
            delta_pct = (avg_fore - avg_hist) / avg_hist * 100
            st.metric("Avg Historical (MT)", f"{avg_hist:,.0f}")
            st.metric("Avg Forecast (MT)", f"{avg_fore:,.0f}", f"{delta_pct:+.1f}%")
            st.metric("Annual Trend", trend_label)
            st.metric("Conf Band Width", "±7%")
            st.markdown('</div>', unsafe_allow_html=True)

    # All commodities 30-day overview
    if forecasts:
        st.markdown("---")
        st.markdown("**30-Day Forecast Summary — All Commodities**")
        comm_metrics = []
        for comm, fc in forecasts.items():
            avg = sum(fc["forecast_values"][:30]) / min(30, len(fc["forecast_values"]))
            comm_metrics.append({"Commodity": comm, "Avg Forecast (MT)": round(avg), "Annual Trend": f"{fc['trend_pct_annual']:+.1f}%"})
        df_cm = pd.DataFrame(comm_metrics)
        fig_bar_all = px.bar(df_cm, x="Commodity", y="Avg Forecast (MT)",
                             color="Commodity", color_discrete_map=COMMODITY_COLORS,
                             title="Average Daily Forecast Volume by Commodity")
        fig_bar_all.update_layout(**PLOTLY_THEME, height=300, showlegend=False)
        st.plotly_chart(fig_bar_all, use_container_width=True)

    # Model Accuracy
    if acc_data.get("models"):
        st.markdown("---")
        st.markdown("**Forecasting Model Accuracy Comparison**")
        df_acc = pd.DataFrame(acc_data["models"])
        col_a, col_b = st.columns([2, 1])
        with col_a:
            fig_acc = px.bar(df_acc, x="model", y="accuracy_pct", color="status",
                             color_discrete_map={"Active": GOLD, "Baseline": "#D1D5DB"},
                             title="Model Accuracy % (Target: 85%+)",
                             text="accuracy_pct")
            fig_acc.add_hline(y=85, line_dash="dash", line_color="#059669", annotation_text="Target 85%")
            fig_acc.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_acc.update_layout(**PLOTLY_THEME, height=300)
            fig_acc.update_yaxes(range=[80, 100])
            st.plotly_chart(fig_acc, use_container_width=True)
        with col_b:
            st.dataframe(df_acc[["model", "mape_pct", "rmse", "mae", "status"]]
                         .rename(columns={"mape_pct": "MAPE%", "rmse": "RMSE", "mae": "MAE"}),
                         use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — TRADE INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="ys-content">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-header">
      <span class="sec-title">Trade Intelligence Engine</span>
      <span class="sec-tag">Module 3</span>
      <div class="sec-sub">Trade lane analysis, commodity price indices, market opportunities — GDELT + Bloomberg feeds</div>
    </div>""", unsafe_allow_html=True)

    lanes_data = api_get("/trade/lanes") or {"lanes": []}
    prices_data = api_get("/trade/commodity-prices") or {"prices": []}
    opps_data = api_get("/trade/opportunities") or {"opportunities": []}
    lanes = lanes_data.get("lanes", [])
    prices = prices_data.get("prices", [])
    opps = opps_data.get("opportunities", [])

    col_l, col_r = st.columns([3, 2])
    with col_l:
        if lanes:
            df_lanes = pd.DataFrame(lanes)
            df_lanes["Direction"] = df_lanes["growth_pct"].apply(lambda x: "Growing" if x > 0 else "Declining")
            fig_lanes = px.bar(df_lanes.sort_values("growth_pct"), x="growth_pct", y="route",
                               orientation="h", color="Direction",
                               color_discrete_map={"Growing": "#059669", "Declining": "#DC2626"},
                               title="Trade Lane Growth / Decline (YoY %)",
                               labels={"growth_pct": "Growth %", "route": ""},
                               text="growth_pct")
            fig_lanes.update_traces(texttemplate="%{text:+.1f}%", textposition="outside")
            fig_lanes.add_vline(x=0, line_color="#1C1917", line_width=1)
            fig_lanes.update_layout(**PLOTLY_THEME, height=400)
            st.plotly_chart(fig_lanes, use_container_width=True)

            st.markdown('<div class="panel"><div class="panel-title">Trade Lane Details</div>', unsafe_allow_html=True)
            df_show_lanes = df_lanes[["route", "commodity", "volume_mt", "growth_pct", "vessels_month"]].copy()
            df_show_lanes.columns = ["Route", "Commodity", "Volume (MT)", "Growth %", "Vessels/Month"]
            st.dataframe(df_show_lanes, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        # Commodity Prices
        if prices:
            st.markdown('<div class="panel"><div class="panel-title">Commodity Price Indices</div>', unsafe_allow_html=True)
            for p in prices:
                color = "#059669" if p["trend"] == "up" else "#DC2626"
                arrow = "▲" if p["trend"] == "up" else "▼"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #FEF3C7;">
                  <div>
                    <div style="font-size:12px;font-weight:700;color:#1C1917;">{p['commodity']}</div>
                    <div style="font-size:10px;color:#78716C;">{p['index']}</div>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-size:15px;font-weight:800;font-family:system-ui,sans-serif;color:#1C1917;">${p['price_usd']:,.2f}</div>
                    <div style="font-size:11px;color:{color};font-weight:600;">{arrow} {abs(p['change_30d']):.1f}% (30d)</div>
                  </div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Price trend chart for top commodity
            p_sel = prices[0]
            fig_price = go.Figure(go.Scatter(
                x=p_sel["series_dates"], y=p_sel["series_values"],
                fill="tozeroy", fillcolor="rgba(245,158,11,0.1)",
                line=dict(color=GOLD, width=2),
                name=p_sel["commodity"],
            ))
            fig_price.update_layout(**PLOTLY_THEME, height=220,
                                     title=f"{p_sel['commodity']} — 30-Day Price Trend (USD)",
                                     yaxis_title="USD")
            st.plotly_chart(fig_price, use_container_width=True)

    # Market Opportunities
    st.markdown("---")
    st.markdown("""<div class="sec-header" style="margin-top:0">
      <span class="sec-title" style="font-size:18px">Market Opportunities</span>
      <span class="sec-tag">AI Ranked</span>
    </div>""", unsafe_allow_html=True)
    cols_opp = st.columns(2)
    for i, opp in enumerate(opps):
        with cols_opp[i % 2]:
            conf_pct = int(opp['confidence'] * 100)
            st.markdown(f"""
            <div class="opp-card">
              <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                <div class="opp-rank">#{opp['rank']}</div>
                <div>
                  <div class="opp-commodity">{opp['commodity']}</div>
                  <div class="opp-route">{opp['route']}</div>
                </div>
              </div>
              <div class="opp-opportunity">{opp['opportunity']}</div>
              <div class="opp-metrics">
                <div><div class="opp-revenue">₹{opp['revenue_potential_cr']} Cr</div><div style="font-size:10px;color:#78716C;">Revenue Potential</div></div>
                <div><div class="opp-revenue" style="color:{GOLD};">{conf_pct}%</div><div style="font-size:10px;color:#78716C;">Confidence</div></div>
                <div><div style="font-size:13px;font-weight:700;color:#2563EB;">{opp['time_horizon']}</div><div style="font-size:10px;color:#78716C;">Time Horizon</div></div>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ANOMALY DETECTION
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="ys-content">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-header">
      <span class="sec-title">Anomaly Detection Engine</span>
      <span class="sec-tag">Module 4</span>
      <div class="sec-sub">Isolation Forest · LSTM · Autoencoder · Transformer — Cargo surges, vessel diversions, congestion spikes</div>
    </div>""", unsafe_allow_html=True)

    anom_data = api_get("/anomaly/events") or {"events": []}
    hist_data = api_get("/anomaly/history") or {"history": {}}
    anom_events = anom_data.get("events", [])
    anom_hist = hist_data.get("history", {})

    c1, c2, c3, c4 = st.columns(4)
    sev_counts = {}
    for e in anom_events:
        sev_counts[e["severity"]] = sev_counts.get(e["severity"], 0) + 1
    c1.metric("Critical Anomalies", sev_counts.get("Critical", 0))
    c2.metric("High Severity", sev_counts.get("High", 0))
    c3.metric("Medium Severity", sev_counts.get("Medium", 0))
    c4.metric("Low Severity", sev_counts.get("Low", 0))

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([2, 3])

    with col_l:
        st.markdown('<div class="panel"><div class="panel-title">Active Anomaly Events</div>', unsafe_allow_html=True)
        for ev in anom_events:
            sev = ev["severity"]
            css_cls = f"alert-{sev.lower()}"
            badge_cls = f"badge-{sev[:4].lower()}"
            ts_str = ev["timestamp"][:16].replace("T", "  ")
            st.markdown(f"""
            <div class="alert-card {css_cls}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div class="alert-title">{ev['event_id']} — {ev['type']}</div>
                <span class="badge {badge_cls}">{sev}</span>
              </div>
              <div class="alert-desc">{ev['description']}</div>
              <div class="alert-meta">
                <span><b>Commodity:</b> {ev['commodity']}</span>
                <span><b>Algorithm:</b> {ev['algorithm']}</span>
                <span><b>Confidence:</b> {int(ev['confidence']*100)}%</span>
                <span><b>Time:</b> {ts_str}</span>
              </div>
              <div style="margin-top:8px;font-size:11px;color:#92400E;background:rgba(245,158,11,0.08);padding:6px 10px;border-radius:6px;">
                <b>Action:</b> {ev['recommended_action']}
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if anom_hist:
            fig_hist = go.Figure()
            sev_order = ["Critical", "High", "Medium", "Low"]
            sev_colors_list = ["#DC2626", "#D97706", "#2563EB", "#059669"]
            dates = []
            for sev, color in zip(sev_order, sev_colors_list):
                if sev in anom_hist:
                    dates = anom_hist[sev]["dates"]
                    fig_hist.add_trace(go.Bar(
                        x=dates, y=anom_hist[sev]["counts"],
                        name=sev, marker_color=color, opacity=0.85
                    ))
            fig_hist.update_layout(**PLOTLY_THEME, height=300, barmode="stack",
                                    title="30-Day Anomaly Frequency by Severity",
                                    xaxis_title="Date", yaxis_title="Event Count",
                                    legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig_hist, use_container_width=True)

        # Algorithm Legend
        st.markdown("""
        <div class="panel">
          <div class="panel-title">Detection Algorithms Active</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;padding:12px;">
              <div style="font-weight:700;font-size:13px;color:#92400E;">Isolation Forest</div>
              <div style="font-size:11px;color:#78716C;margin-top:4px;">Detects outliers in vessel speed, cargo volume time-series via random partitioning</div>
            </div>
            <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;padding:12px;">
              <div style="font-weight:700;font-size:13px;color:#92400E;">LSTM Anomaly Detection</div>
              <div style="font-size:11px;color:#78716C;margin-top:4px;">Sequence modeling for vessel route deviation and temporal cargo anomalies</div>
            </div>
            <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;padding:12px;">
              <div style="font-weight:700;font-size:13px;color:#92400E;">Autoencoder</div>
              <div style="font-size:11px;color:#78716C;margin-top:4px;">Reconstruction-error based detection for multi-dimensional port metric anomalies</div>
            </div>
            <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;padding:12px;">
              <div style="font-weight:700;font-size:13px;color:#92400E;">Transformer Detector</div>
              <div style="font-size:11px;color:#78716C;margin-top:4px;">Attention-based model for complex multi-variable congestion pattern recognition</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — INCENTIVE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="ys-content">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-header">
      <span class="sec-title">Trade Incentive Recommendation Engine</span>
      <span class="sec-tag">Module 5</span>
      <div class="sec-sub">RL-based policy optimization, Monte Carlo simulation, revenue maximization — proactive trade incentives</div>
    </div>""", unsafe_allow_html=True)

    recs_data = api_get("/incentive/recommendations") or {"recommendations": []}
    recs = recs_data.get("recommendations", [])

    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown('<div class="panel"><div class="panel-title">AI Recommendations — Priority Ranked</div>', unsafe_allow_html=True)
        priority_colors = {"High": "#DC2626", "Medium": "#D97706", "Strategic": "#7C3AED"}
        for r in recs:
            pcolor = priority_colors.get(r["priority"], "#78716C")
            conf_pct = int(r["confidence"] * 100)
            st.markdown(f"""
            <div class="rec-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div class="rec-action">{r['rec_id']}: {r['action']}</div>
                <span class="badge" style="background:rgba(0,0,0,0.05);color:{pcolor};border:1px solid {pcolor}30;">{r['priority']}</span>
              </div>
              <div class="rec-rationale">{r['rationale']}</div>
              <div style="font-size:11px;background:#FFFBEB;border:1px solid #FDE68A;border-radius:6px;padding:6px 10px;margin:8px 0;color:#78716C;">
                <b>Current:</b> {r['current_metric']}
              </div>
              <div class="rec-impacts">
                <div><div class="rec-impact-pos">Traffic: {r['predicted_traffic_impact']}</div></div>
                <div><div class="rec-impact-pos">Revenue: {r['predicted_revenue_impact']}</div></div>
                <div><div style="font-size:13px;font-weight:700;color:{GOLD};">{conf_pct}% confidence</div></div>
              </div>
              <div class="rec-meta">
                <span><b>Method:</b> {r['method']}</span>
                <span><b>Implementation:</b> {r['implementation_weeks']} weeks</span>
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown("**Monte Carlo Policy Simulator**")
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        charge_delta = st.slider("Handling Charge Change (%)", min_value=-15.0, max_value=5.0, value=-5.0, step=0.5)
        incentive_pct = st.slider("Incentive Rate Offered (%)", min_value=0.0, max_value=15.0, value=8.0, step=0.5)
        scenario_name = st.selectbox("Scenario Type", ["container_charge", "lng_priority", "coal_volume", "auto_terminal"])

        if st.button("Run Monte Carlo Simulation (1000 iterations)"):
            with st.spinner("Running Monte Carlo..."):
                mc_result = api_post("/incentive/monte-carlo", {
                    "scenario": scenario_name,
                    "charge_delta": charge_delta,
                    "incentive_pct": incentive_pct
                })
                if mc_result and "samples" in mc_result:
                    st.markdown("**Revenue Distribution (₹ Cr)**")
                    fig_mc = go.Figure()
                    fig_mc.add_trace(go.Histogram(
                        x=mc_result["samples"], nbinsx=30,
                        marker_color=GOLD, opacity=0.8, name="Revenue Distribution"
                    ))
                    fig_mc.add_vline(x=mc_result["p50"], line_dash="dash", line_color="#DC2626",
                                     annotation_text=f"P50: ₹{mc_result['p50']} Cr")
                    fig_mc.add_vline(x=mc_result["mean"], line_dash="dot", line_color="#059669",
                                     annotation_text=f"Mean: ₹{mc_result['mean']} Cr")
                    fig_mc.update_layout(**PLOTLY_THEME, height=260,
                                         title="Monte Carlo Revenue Distribution",
                                         xaxis_title="Revenue (₹ Cr)", yaxis_title="Frequency")
                    st.plotly_chart(fig_mc, use_container_width=True)

                    c1, c2, c3 = st.columns(3)
                    c1.metric("P10 (Conservative)", f"₹{mc_result['p10']} Cr")
                    c2.metric("P50 (Median)", f"₹{mc_result['p50']} Cr")
                    c3.metric("P90 (Optimistic)", f"₹{mc_result['p90']} Cr")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7 — DIGITAL TWIN
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown('<div class="ys-content">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-header">
      <span class="sec-title">Digital Twin Simulator</span>
      <span class="sec-tag">Module 6</span>
      <div class="sec-sub">Virtual port environment — what-if scenarios for cargo, vessels, weather, and policy changes</div>
    </div>""", unsafe_allow_html=True)

    scenario_map = {
        "Cargo Surge +20%": "cargo_surge",
        "Vessel Delay Increase": "vessel_delay",
        "Trade Incentive Policy": "incentive_change",
        "Weather Disruption (Cyclone)": "weather_disruption",
    }
    sel_label = st.selectbox("Select Scenario", list(scenario_map.keys()))
    sel_key = scenario_map[sel_label]

    twin_data = api_get(f"/twin/scenario/{sel_key}") or {}
    result = twin_data.get("result", {})
    mc_data = twin_data.get("monte_carlo", {})

    if result:
        risk = result.get("risk_level", "Medium")
        risk_color = {"Low": "#059669", "Medium": "#D97706", "High": "#DC2626", "Critical": "#7C3AED"}.get(risk, "#78716C")

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#FFFBEB,#FEF3C7);border:1px solid #FDE68A;border-radius:12px;padding:18px 22px;margin-bottom:20px;display:flex;align-items:center;gap:16px;">
          <div style="font-family:system-ui,sans-serif;font-size:18px;font-weight:800;color:#1C1917;">{result.get('name','Scenario')}</div>
          <div style="font-size:13px;color:#78716C;">{result.get('description','')}</div>
          <div style="margin-left:auto;background:{risk_color}15;border:1px solid {risk_color}40;color:{risk_color};padding:5px 14px;border-radius:16px;font-size:11px;font-weight:700;">Risk: {risk}</div>
        </div>""", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Congestion Index", f"{result.get('congestion_index',0):.2f}", result.get("congestion_delta", ""))
        c2.metric("Berth Utilization", f"{result.get('berth_utilization_pct',0):.1f}%", result.get("berth_delta", ""))
        c3.metric("Storage Utilization", f"{result.get('storage_utilization_pct',0):.1f}%", result.get("storage_delta", ""))
        c4.metric("Expected Revenue", f"₹{result.get('expected_revenue_cr',0):.1f} Cr", result.get("revenue_delta", ""))

        st.markdown("<br>", unsafe_allow_html=True)
        col_l, col_r = st.columns(2)

        with col_l:
            categories = ["Congestion", "Berth Util", "Storage Util", "Revenue"]
            baseline_vals = [0.63, 72.4, 65.0, 100.0]
            scenario_vals = [
                result.get("congestion_index", 0.63) * 100,
                result.get("berth_utilization_pct", 72.4),
                result.get("storage_utilization_pct", 65.0),
                result.get("expected_revenue_cr", 100.0) / 1.2,
            ]
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=baseline_vals, theta=categories, fill="toself",
                                                  name="Baseline", line_color="#78716C", fillcolor="rgba(120,113,108,0.1)"))
            fig_radar.add_trace(go.Scatterpolar(r=scenario_vals, theta=categories, fill="toself",
                                                  name=sel_label, line_color=GOLD, fillcolor="rgba(245,158,11,0.15)"))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 120])),
                                     paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"),
                                     height=320, showlegend=True, title="Scenario vs Baseline Comparison",
                                     legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_r:
            add_cranes = result.get("additional_cranes_needed", 0)
            add_workforce = result.get("additional_workforce", 0)
            wf_color = "#DC2626" if add_workforce < 0 else "#059669"
            st.markdown(f"""
            <div class="panel">
              <div class="panel-title">Operational Impact Assessment</div>
              <div style="display:grid;gap:12px;">
                <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;padding:14px;">
                  <div style="font-size:11px;color:#78716C;text-transform:uppercase;letter-spacing:0.6px;">Additional Cranes Required</div>
                  <div style="font-size:28px;font-weight:800;font-family:system-ui,sans-serif;color:#1C1917;">{add_cranes}</div>
                </div>
                <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;padding:14px;">
                  <div style="font-size:11px;color:#78716C;text-transform:uppercase;letter-spacing:0.6px;">Workforce Delta</div>
                  <div style="font-size:28px;font-weight:800;font-family:system-ui,sans-serif;color:{wf_color};">{add_workforce:+d}</div>
                </div>
                <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;padding:14px;">
                  <div style="font-size:11px;color:#78716C;text-transform:uppercase;letter-spacing:0.6px;">Risk Classification</div>
                  <div style="font-size:20px;font-weight:800;font-family:system-ui,sans-serif;color:{risk_color};">{risk}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

        # Berth utilization comparison
        berths = api_get("/twin/berths") or {"berths": []}
        berths = berths.get("berths", [])
        if berths:
            df_b = pd.DataFrame(berths)
            import random as _rnd
            _rnd.seed(42)
            delta = float(result.get("berth_delta", "+0%").replace("%", ""))
            df_b["simulated_pct"] = df_b["utilization_pct"].apply(lambda x: min(100, x * (1 + delta / 100) + _rnd.gauss(0, 2)))
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(x=df_b["berth_id"], y=df_b["utilization_pct"],
                                       name="Baseline", marker_color="#D1D5DB"))
            fig_comp.add_trace(go.Bar(x=df_b["berth_id"], y=df_b["simulated_pct"],
                                       name=f"Simulated: {sel_label}", marker_color=GOLD, opacity=0.85))
            fig_comp.update_layout(**PLOTLY_THEME, barmode="group", height=280,
                                    title="Berth Utilization — Baseline vs Simulated")
            fig_comp.update_yaxes(range=[0, 110])
            st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 8 — AI MARITIME COPILOT
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[7]:
    st.markdown('<div class="ys-content">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-header">
      <span class="sec-title">AI Maritime Copilot</span>
      <span class="sec-tag">Module 7</span>
      <div class="sec-sub">LangGraph Cognitive Dispatcher — 3-tier fallback: LLM → SLM → Deterministic Zero-LLM</div>
    </div>""", unsafe_allow_html=True)

    # Agent Roster
    agents = [
        ("Forecast Agent", "Cargo volume prediction queries"),
        ("Trade Agent", "Global trade lane & commodity analysis"),
        ("Policy Agent", "Incentive & regulation recommendations"),
        ("Simulation Agent", "Digital twin & what-if scenarios"),
        ("Reporting Agent", "Executive summary generation"),
    ]
    agent_cols = st.columns(5)
    for i, (name, role) in enumerate(agents):
        with agent_cols[i]:
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid #FDE68A;border-top:3px solid #F59E0B;border-radius:10px;padding:12px;text-align:center;">
              <div style="font-family:system-ui,sans-serif;font-size:12px;font-weight:700;color:#1C1917;">{name}</div>
              <div style="font-size:10px;color:#78716C;margin-top:4px;">{role}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Suggested queries
    sugg_data = api_get("/copilot/suggested-queries") or {"queries": []}
    suggestions = sugg_data.get("queries", [])
    if suggestions:
        st.markdown("**Suggested Queries:**")
        chip_html = "".join([f'<span class="query-chip">{q}</span>' for q in suggestions[:4]])
        st.markdown(chip_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([2, 3])

    with col_l:
        query_input = st.text_area(
            "Ask the Maritime Copilot:",
            placeholder="e.g. Why is cargo forecast decreasing? What incentive should be applied?",
            height=120,
        )

        submit = st.button("Submit Query to Copilot")

        active_query = None
        if submit and query_input.strip():
            active_query = query_input

        # Quick query buttons
        st.markdown("**Or one-click submit a suggested query:**")
        qcols = st.columns(2)
        for i, q in enumerate(suggestions[:4]):
            with qcols[i % 2]:
                if st.button(q[:35] + "..." if len(q) > 35 else q, key=f"qbtn_{i}"):
                    active_query = q

        if active_query:
            with st.spinner("Dispatching through LangGraph..."):
                result = api_post("/copilot/query", {"query": active_query})
                if result:
                    st.session_state["last_copilot"] = result

    with col_r:
        if "last_copilot" in st.session_state:
            cop = st.session_state["last_copilot"]
            trace = cop.get("trace", {})
            response = cop.get("response", {})

            # Dispatch trace
            st.markdown('<div class="panel"><div class="panel-title">LangGraph Dispatch Trace</div>', unsafe_allow_html=True)
            tier_color = {"Tier 1: Heavy Synthesis (LLM)": "#DC2626",
                          "Tier 2: Fast Reasoning (SLM)": "#D97706",
                          "Tier 3: Deterministic Zero-LLM": "#059669"}.get(trace.get("tier", ""), GOLD)
            st.markdown(f"""
            <div style="display:flex;gap:20px;margin-bottom:14px;flex-wrap:wrap;">
              <span class="metric-pill">Complexity: {trace.get('complexity','')}</span>
              <span class="metric-pill" style="color:{tier_color};border-color:{tier_color}40;">Tier: {trace.get('tier','')}</span>
              <span class="metric-pill">Agent: {trace.get('agent','')}</span>
              <span class="metric-pill">Total: {trace.get('total_ms',0)}ms</span>
            </div>""", unsafe_allow_html=True)

            for step in trace.get("trace", []):
                st.markdown(f"""
                <div class="trace-step">
                  <div class="trace-num">{step['step']}</div>
                  <div style="flex:1;">
                    <div class="trace-component">{step['component']}</div>
                    <div class="trace-action">{step['action']}</div>
                    <div class="trace-detail">{step['detail']}</div>
                  </div>
                  <div class="trace-ms">{step['ms']}ms</div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Response
            if response:
                confidence_pct = int(response.get("confidence", 0.85) * 100)
                st.markdown(f"""
                <div class="copilot-response">
                  <div style="font-size:11px;color:#78716C;margin-bottom:12px;display:flex;gap:12px;flex-wrap:wrap;">
                    <span><b>Confidence:</b> {confidence_pct}%</span>
                    <span><b>Data Sources:</b> {", ".join(response.get("data_refs", []))}</span>
                  </div>
                  {response.get("answer","").replace(chr(10), "<br>")}
                </div>""", unsafe_allow_html=True)

                followups = response.get("suggested_followups", [])
                if followups:
                    st.markdown("<br>**Follow-up Questions:**")
                    fu_html = "".join([f'<span class="query-chip">{q}</span>' for q in followups])
                    st.markdown(fu_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#FFFBEB;border:2px dashed #FDE68A;border-radius:12px;padding:40px;text-align:center;color:#78716C;">
              <div style="font-family:system-ui,sans-serif;font-size:18px;font-weight:700;color:#92400E;margin-bottom:8px;">LangGraph Copilot Ready</div>
              <div style="font-size:13px;">Type a query and click Submit to see the 3-tier dispatch trace and AI response.</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 9 — DATA PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[8]:
    st.markdown('<div class="ys-content">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-header">
      <span class="sec-title">Synthetic Data Pipeline & Architecture</span>
      <span class="sec-tag">Infrastructure</span>
      <div class="sec-sub">Kafka ingestion → Spark fusion → Data pools → AI readiness — real-time processing metrics</div>
    </div>""", unsafe_allow_html=True)

    pipe_data = api_get("/pipeline/status") or {}
    log_data = api_get("/pipeline/log") or {"events": []}
    kafka = pipe_data.get("kafka", {})
    spark = pipe_data.get("spark", {})
    airflow = pipe_data.get("airflow", {})
    pools = pipe_data.get("data_pools", {})

    # Pipeline flow stages
    stage_cols = st.columns(4)
    stages = [
        ("1. DATA INGESTION", "Internal Port Authority Data\nExternal AIS · Weather · Commodity APIs\nKafka Stream · Airflow Scheduler"),
        ("2. SPATIO-TEMPORAL FUSION", "Spark Streaming (temporal alignment)\nPyTorch Grid Matching (ship + weather)\nSLM Text Processor (PII masking)"),
        ("3. DATA POOLS", "PostgreSQL (master port data)\nTimescaleDB (AIS time-series)\nMilvus / Pinecone (vector embeddings)"),
        ("4. AI ORCHESTRATION", "LangGraph Cognitive Dispatcher\n3-Tier Execution & Fallback\n5 Specialized AI Agents"),
    ]
    for col, (title, desc) in zip(stage_cols, stages):
        with col:
            st.markdown(f"""
            <div class="pipeline-stage">
              <div class="pipeline-stage-title">{title}</div>
              <div class="pipeline-stage-sub">{desc.replace(chr(10), '<br>')}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # System Metrics
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Kafka msg/sec", f"{kafka.get('messages_per_sec',0):,}")
    m2.metric("Consumer Lag", str(kafka.get("consumer_lag", 0)))
    m3.metric("Spark rows/sec", f"{spark.get('rows_per_sec',0):,}")
    m4.metric("Airflow Success", f"{airflow.get('success_rate_pct',0)}%")
    m5.metric("Total Records", f"{pools.get('postgresql_records',0)/1e6:.2f}M")
    m6.metric("Storage (GB)", f"{pools.get('total_storage_gb',0):.1f}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_log, col_pool = st.columns([3, 2])

    with col_log:
        st.markdown('<div class="panel"><div class="panel-title">Live Ingestion Event Log</div>', unsafe_allow_html=True)
        events = log_data.get("events", [])
        rows_html = ""
        for ev in events:
            lvl_class = "log-warn" if ev["level"] == "WARN" else "log-info"
            rows_html += f'<div class="log-row"><span class="log-ts">{ev["timestamp"]}</span><span class="log-src">[{ev["source"]}]</span><span class="{lvl_class}">{ev["message"]}</span></div>'
        st.markdown(f'<div class="log-container">{rows_html}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_pool:
        st.markdown('<div class="panel"><div class="panel-title">Data Pool Statistics</div>', unsafe_allow_html=True)
        pool_metrics = [
            ("PostgreSQL", "Relational master data", f"{pools.get('postgresql_records',0):,}", "records"),
            ("TimescaleDB", "AIS time-series", f"{pools.get('timescaledb_records',0)/1e6:.1f}M", "records"),
            ("Milvus Vectors", "Contextual RAG embeddings", f"{pools.get('milvus_vectors',0):,}", "vectors"),
        ]
        for name, desc, val, unit in pool_metrics:
            st.markdown(f"""
            <div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;padding:14px;margin-bottom:10px;">
              <div style="font-weight:700;font-size:13px;color:#92400E;">{name}</div>
              <div style="font-size:11px;color:#78716C;margin-bottom:6px;">{desc}</div>
              <div style="font-family:system-ui,sans-serif;font-size:22px;font-weight:800;color:#1C1917;">{val} <span style="font-size:11px;color:#78716C;">{unit}</span></div>
            </div>""", unsafe_allow_html=True)

        uptime_data = [
            ("Kafka", kafka.get("uptime_pct", 99.97)),
            ("Spark", spark.get("uptime_pct", 99.91)),
            ("Airflow", airflow.get("uptime_pct", 99.84)),
        ]
        for svc, pct in uptime_data:
            color = "#059669" if pct >= 99.9 else "#D97706"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #FEF3C7;">
              <span style="font-size:12px;font-weight:600;color:#1C1917;">{svc} Uptime</span>
              <span style="font-size:12px;font-weight:700;color:{color};">{pct}%</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Architecture Diagrams
    st.markdown("---")
    st.markdown("""<div class="sec-header" style="margin-top:0">
      <span class="sec-title" style="font-size:18px">System Architecture Diagrams</span>
    </div>""", unsafe_allow_html=True)

    arch_tabs = st.tabs([
        "LangGraph Dispatcher (Diagram 1)",
        "Data Ingestion & Fusion (Diagram 2)",
        "Backend & Security (Diagram 3)",
        "End-to-End Flow (Diagram 4)",
    ])
    for i, atab in enumerate(arch_tabs):
        with atab:
            img_path = ARCH_DIR / "assets" / f"{i+1}.jpeg"
            if img_path.exists():
                st.image(str(img_path), use_container_width=True)
            else:
                st.info(f"Architecture diagram {i+1} not found at {img_path}")

    st.markdown('</div>', unsafe_allow_html=True)
