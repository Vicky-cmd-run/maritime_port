from fastapi import APIRouter
from backend.app.services import synthetic_data as sd

router = APIRouter()

@router.get("/")
def get_vessels():
    vessels = sd.generate_vessels(25)
    return {"vessels": vessels, "count": len(vessels)}

@router.get("/eta")
def get_eta_predictions():
    vessels = sd.generate_vessels(25)
    eta_data = sorted(vessels, key=lambda v: v["hours_to_arrival"])
    return {"eta_predictions": eta_data}

@router.get("/congestion-alerts")
def get_congestion_alerts():
    vessels = sd.generate_vessels(25)
    alerts = sd.generate_congestion_alerts(vessels)
    return {"alerts": alerts, "count": len(alerts)}
