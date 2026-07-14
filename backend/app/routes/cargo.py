from fastapi import APIRouter, Query
from backend.app.services import synthetic_data as sd

router = APIRouter()

@router.get("/forecast")
def get_forecast(horizon: int = Query(default=30, ge=7, le=365)):
    return {"horizon_days": horizon, "forecasts": sd.generate_cargo_forecast(horizon)}

@router.get("/accuracy")
def get_accuracy():
    return {"models": sd.generate_forecast_accuracy()}

@router.get("/berths")
def get_berths():
    return {"berths": sd.generate_berth_status(12)}
