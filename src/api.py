"""REST API for Black Carbon Intelligence & Predictor.
Run standalone: uvicorn src.api:app --port 8000 --reload
Interactive docs: http://localhost:8000/docs
"""
import io
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import ARTIFACTS
from .predict import Predictor

app = FastAPI(
    title="Black Carbon Intelligence API",
    version="3.0",
    description="Virtual BC sensor, Tree-SHAP explainability, multi-horizon forecasts, what-if simulators, and live telemetry for Varanasi / Indo-Gangetic Plain."
)

# Enable CORS for local Vite dev server and external frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_pred: Optional[Predictor] = None
_tables_cache: Dict[str, List[Dict[str, Any]]] = {}
_live_cache: Dict[str, Any] = {"data": None, "timestamp": 0}


def get_predictor() -> Predictor:
    global _pred
    if _pred is None:
        try:
            _pred = Predictor()
        except FileNotFoundError:
            raise HTTPException(503, "Model artifacts not found. Run `python run_pipeline.py` first.")
    return _pred


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------
class EstimateRequest(BaseModel):
    timestamp: Optional[datetime] = None
    readings: Dict[str, Optional[float]] = Field(
        ...,
        examples=[{"PM25": 180, "PM10": 290, "CO": 2.1, "NO2": 48, "AT": 11, "RH": 82, "WS": 0.7}],
    )
    explain: bool = True


class WhatIfSweepRequest(BaseModel):
    timestamp: Optional[datetime] = None
    readings: Dict[str, Optional[float]]
    variable: str = Field("WS", description="Variable to sweep (WS, AT, RH, PM25, CO, NO2)")
    min_val: float = 0.1
    max_val: float = 6.0
    steps: int = 25


class WhatIfScaleRequest(BaseModel):
    timestamp: Optional[datetime] = None
    readings: Dict[str, Optional[float]]
    factors: Optional[List[float]] = [0.3, 0.5, 0.7, 0.85, 1.0, 1.15, 1.3]


class ForecastRequest(BaseModel):
    records: List[Dict[str, Any]] = Field(
        ..., description="Recent 15-min rows (>=24 h recommended): Timestamp, BC6 and any pollutants/met."
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    p = get_predictor()
    return {
        "status": "healthy",
        "data_source": p.meta.get("data_source", "Varanasi AE33"),
        "created": p.meta.get("created"),
        "deployed_models": p.meta.get("deployed_models", {}),
        "qc": p.meta.get("qc", {}),
    }


@app.get("/api/meta")
def meta():
    p = get_predictor()
    return p.meta


@app.get("/api/tables")
def list_tables():
    p = ARTIFACTS / "tables"
    if not p.exists():
        return {"tables": []}
    files = [f.stem for f in p.glob("*.csv")]
    return {"tables": sorted(files)}


@app.get("/api/tables/{table_name}")
def get_table(table_name: str):
    if table_name in _tables_cache:
        return _tables_cache[table_name]

    file_path = ARTIFACTS / "tables" / f"{table_name}.csv"
    if not file_path.exists():
        raise HTTPException(404, f"Table '{table_name}' not found.")

    try:
        df = pd.read_csv(file_path)
        # Replace inf and NaN for JSON compliance
        df = df.replace([np.inf, -np.inf], None)
        records = df.where(pd.notnull(df), None).to_dict(orient="records")
        _tables_cache[table_name] = records
        return records
    except Exception as e:
        raise HTTPException(500, f"Error reading table {table_name}: {e}")


@app.post("/api/estimate")
def estimate(req: EstimateRequest):
    p = get_predictor()
    try:
        clean_readings = {k: v for k, v in req.readings.items() if v is not None}
        out = p.estimate(clean_readings, req.timestamp, explain=req.explain)
        return {
            "bc6_ng_m3": round(out["pred"], 1),
            "bc6_ug_m3": round(out["pred"] / 1000.0, 2),
            "interval_90": [round(out["lo"], 1), round(out["hi"], 1)],
            "interval_width": round(out["hi"] - out["lo"], 1),
            "nominal_coverage": out.get("interval_nominal", 0.90),
            "level": out["level"],
            "percentile_rank": out.get("percentile_rank", 50.0),
            "bc_pm25_share_pct": out.get("bc_pm25_share_pct"),
            "diagnostics": out.get("diagnostics", []),
            "explanation": out.get("explanation", {}),
        }
    except Exception as e:
        raise HTTPException(422, f"Estimation error: {e}")


@app.post("/api/whatif/sweep")
def what_if_sweep(req: WhatIfSweepRequest):
    p = get_predictor()
    try:
        res = p.what_if_sweep(req.readings, req.variable, req.min_val, req.max_val, req.steps, req.timestamp)
        return res
    except Exception as e:
        raise HTTPException(422, f"What-if sweep error: {e}")


@app.post("/api/whatif/scale")
def what_if_scale(req: WhatIfScaleRequest):
    p = get_predictor()
    try:
        res = p.what_if_emission_scale(req.readings, req.factors, req.timestamp)
        return res
    except Exception as e:
        raise HTTPException(422, f"What-if scale error: {e}")


@app.post("/api/forecast")
def forecast(req: ForecastRequest):
    p = get_predictor()
    try:
        df = pd.DataFrame(req.records)
        r = p.forecast(df)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception as e:
        raise HTTPException(500, f"Forecasting error: {e}")

    horizons_formatted = {}
    for h, v in r["horizons"].items():
        horizons_formatted[h] = {
            "time": str(v["time"]),
            "bc6_ng_m3": round(v["pred"], 1),
            "delta_vs_now": round(v["pred"] - r["current_bc"], 1),
            "interval_90": [round(v["lo"], 1), round(v["hi"], 1)],
            "level": v["level"],
            "percentile_rank": v.get("percentile_rank", 50.0),
        }

    return {
        "issued_from": str(r["issued_from"]),
        "current_bc6": round(r["current_bc"], 1),
        "horizons": horizons_formatted,
        "episode_warning_6h": r["episode"],
        "history_points": r.get("history_points", []),
    }


@app.get("/api/sample_recent")
def get_sample_recent():
    p = Path(__file__).resolve().parent.parent / "private_outputs" / "sample_recent.csv"
    if not p.exists():
        raise HTTPException(404, "Sample data not found on server.")
    df = pd.read_csv(p)
    recs = df.astype(object).where(pd.notnull(df), None).to_dict(orient="records")
    return {"total": len(recs), "records": recs}


@app.get("/api/live")
def get_live():
    global _live_cache
    now = time.time()
    # Cache live data for 10 minutes to respect Open-Meteo limits
    if _live_cache["data"] is not None and (now - _live_cache["timestamp"] < 600):
        return _live_cache["data"]

    try:
        from . import live
        w, a = live.fetch()
        raw = live.to_frame(w, a)
        p = get_predictor()
        estimates = p.estimate_batch(raw)

        # Merge raw inputs and estimates
        combined = raw.copy()
        combined["Timestamp"] = pd.to_datetime(combined["Timestamp"])
        combined = combined.set_index("Timestamp")
        merged = combined.join(estimates, how="inner")

        # Get historical profile for median comparison
        prof = None
        prof_file = ARTIFACTS / "tables" / "profile_hour_month.csv"
        if prof_file.exists():
            prof = pd.read_csv(prof_file)

        records = []
        for ts, row in merged.iterrows():
            item = {
                "timestamp": str(ts),
                "bc6_estimate": round(float(row["bc6_estimate"]), 1),
                "lo": round(float(row["lo"]), 1),
                "hi": round(float(row["hi"]), 1),
                "level": row["level"],
                "temperature": round(float(row["AT"]), 1) if pd.notnull(row["AT"]) else None,
                "humidity": round(float(row["RH"]), 1) if pd.notnull(row["RH"]) else None,
                "wind_speed": round(float(row["WS"]), 2) if pd.notnull(row["WS"]) else None,
                "pm25": round(float(row["PM25"]), 1) if pd.notnull(row["PM25"]) else None,
                "pm10": round(float(row["PM10"]), 1) if pd.notnull(row["PM10"]) else None,
                "co": round(float(row["CO"]), 2) if pd.notnull(row["CO"]) else None,
            }
            if prof is not None:
                sub = prof[(prof.month == ts.month) & (prof.hour == ts.hour)]
                if not sub.empty:
                    item["historical_median"] = round(float(sub["median"].mean()), 1)
            records.append(item)

        result = {
            "status": "success",
            "source": "Open-Meteo + Copernicus CAMS (Varanasi Lat 25.32, Lon 82.97)",
            "updated_at": datetime.now().isoformat(),
            "forecast_points": records,
        }
        _live_cache = {"data": result, "timestamp": now}
        return result
    except Exception as e:
        raise HTTPException(502, f"Live fetch failed: {e}")


@app.post("/api/batch")
async def batch_estimate(file: UploadFile = File(...)):
    p = get_predictor()
    try:
        contents = await file.read()
        raw = pd.read_csv(io.BytesIO(contents))
        out = p.estimate_batch(raw)

        # Summary statistics
        level_counts = out["level"].value_counts().to_dict()
        mean_bc = float(out["bc6_estimate"].mean())
        median_bc = float(out["bc6_estimate"].median())
        p90_bc = float(out["bc6_estimate"].quantile(0.90))

        # Sample for frontend chart (at most 500 points for responsiveness)
        step = max(1, len(out) // 500)
        sampled = out.iloc[::step]
        series = [
            {
                "timestamp": str(ts),
                "bc6_estimate": round(float(row["bc6_estimate"]), 1),
                "lo": round(float(row["lo"]), 1),
                "hi": round(float(row["hi"]), 1),
                "level": row["level"],
            }
            for ts, row in sampled.iterrows()
        ]

        return {
            "total_rows": len(out),
            "mean_bc6": round(mean_bc, 1),
            "median_bc6": round(median_bc, 1),
            "p90_bc6": round(p90_bc, 1),
            "level_distribution": level_counts,
            "series": series,
        }
    except Exception as e:
        raise HTTPException(422, f"Batch estimate failed: {e}")


# ---------------------------------------------------------------------------
# Static frontend serving (when built)
# ---------------------------------------------------------------------------
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
