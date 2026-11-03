"""REST API.   uvicorn src.api:app --port 8000   ->  docs at /docs"""
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .predict import Predictor

app = FastAPI(title="BC6 Black Carbon Predictor", version="2.0",
              description="Virtual BC sensor, multi-horizon forecasts and episode warnings (Varanasi / IGP).")
_pred: Optional[Predictor] = None


def predictor() -> Predictor:
    global _pred
    if _pred is None:
        try:
            _pred = Predictor()
        except FileNotFoundError:
            raise HTTPException(503, "Model artifacts not found. Run `python run_pipeline.py` first.")
    return _pred


class EstimateRequest(BaseModel):
    timestamp: Optional[datetime] = None
    readings: Dict[str, float] = Field(
        ..., examples=[{"PM25": 180, "PM10": 290, "CO": 2.1, "NO2": 48, "AT": 11, "RH": 82, "WS": 0.7}])


class ForecastRequest(BaseModel):
    records: List[Dict[str, Optional[float | str]]] = Field(
        ..., description="Recent 15-min rows (>=24 h recommended): Timestamp, BC6 and any pollutants/met.")


@app.get("/health")
def health():
    p = predictor()
    return {"status": "ok", "data_source": p.meta["data_source"], "created": p.meta["created"]}


@app.post("/estimate")
def estimate(req: EstimateRequest):
    out = predictor().estimate(req.readings, req.timestamp)
    return {"bc6_ng_m3": out["pred"], "interval_90": [out["lo"], out["hi"]], "level": out["level"]}


@app.post("/forecast")
def forecast(req: ForecastRequest):
    try:
        r = predictor().forecast(pd.DataFrame(req.records))
    except ValueError as e:
        raise HTTPException(422, str(e))
    return {
        "issued_from": str(r["issued_from"]), "current_bc6": r["current_bc"],
        "horizons": {h: {"time": str(v["time"]), "bc6_ng_m3": v["pred"], "interval_90": [v["lo"], v["hi"]],
                         "level": v["level"]["label"]} for h, v in r["horizons"].items()},
        "episode_warning_6h": r["episode"],
    }
