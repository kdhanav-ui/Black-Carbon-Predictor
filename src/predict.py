"""Inference layer shared by the FastAPI service and the Streamlit dashboard."""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .config import ARTIFACTS, HORIZONS
from .data import ensure_columns, prepare_recent, standardize_columns
from .features import make_features

LEVELS = [  # (label, colour, advice) - relative to THIS site's historical distribution
    ("Low", "#2a9d8f", "Typical-to-clean conditions for this site. No special action needed."),
    ("Moderate", "#e9c46a", "Normal range. Sensitive groups may prefer to limit long outdoor exertion near traffic."),
    ("High", "#f4a261", "Upper quarter of historical levels. Limit prolonged outdoor exercise near roads; keep windows closed at rush hour."),
    ("Very high", "#e76f51", "Top 10% of historical levels. Consider a well-fitted N95/FFP2 mask outdoors; avoid burning waste or biomass."),
    ("Extreme", "#9d0208", "Top 5% of historical levels. Minimise outdoor exposure, use indoor air cleaning if available, and follow local health advisories."),
]


class Predictor:
    def __init__(self, art_dir=ARTIFACTS):
        art = Path(art_dir)
        self.dir = art
        self.meta = json.loads((art / "meta.json").read_text())
        self.bundles = {p.stem: joblib.load(p) for p in (art / "models").glob("*.joblib")}

    # ---- interpretation
    def level(self, bc):
        p = self.meta["bc_percentiles"]
        i = 0 if bc < p["p25"] else 1 if bc < p["p75"] else 2 if bc < p["p90"] else 3 if bc < p["p95"] else 4
        return dict(zip(["label", "color", "advice"], LEVELS[i]))

    # ---- low-level
    def _predict(self, bundle, X_row):
        X = X_row.reindex(columns=bundle["features"])
        Xi = pd.DataFrame(bundle["imputer"].transform(X), columns=bundle["features"], index=X.index)
        p = float(np.clip(bundle["model"].predict(Xi)[0], 0, None))
        scale = max(p, 100.0)
        return {"pred": p, "lo": max(p - bundle["q"] * scale, 0.0), "hi": p + bundle["q"] * scale}, Xi

    # ---- nowcast from instantaneous readings (virtual sensor)
    def estimate(self, readings: dict, timestamp=None):
        """readings: any subset of AT, RH, WS, WD, SR, BP, PM25, PM10, CO, NO, NO2, NOX, SO2, O3, NH3, BENZENE."""
        ts = pd.Timestamp(timestamp or pd.Timestamp.now())
        row = pd.DataFrame([{k: v for k, v in readings.items() if v is not None}], index=[ts])
        row = ensure_columns(row)
        X = make_features(row, use_bc_history=False)
        out, _ = self._predict(self.bundles["virtual"], X)
        out["level"] = self.level(out["pred"])
        out["interval_nominal"] = self.meta["virtual_interval"]["nominal"]
        return out

    # ---- multi-horizon forecast from recent history
    def forecast(self, recent_raw: pd.DataFrame):
        df = prepare_recent(recent_raw)
        if "BC6" not in df or df["BC6"].dropna().empty:
            raise ValueError("Recent data must include a BC6 column with at least one valid reading.")
        df = df.loc[:df["BC6"].last_valid_index()]       # forecast from the latest BC reading
        X = make_features(df, use_bc_history=True).iloc[[-1]]
        t0 = df.index[-1]
        res = {}
        for h, steps in HORIZONS.items():
            r, _ = self._predict(self.bundles[f"h_{h}"], X)
            r["time"] = t0 + pd.Timedelta(minutes=15 * steps)
            r["level"] = self.level(r["pred"])
            res[h] = r
        ep = self.bundles.get("episode")
        episode = None
        if ep is not None:
            Xe = X.reindex(columns=ep["features"])
            Xi = pd.DataFrame(ep["imputer"].transform(Xe), columns=ep["features"])
            prob = float(ep["model"].predict_proba(Xi)[0, 1])
            episode = {"probability": prob, "warn": prob >= ep["decision_threshold"],
                       "threshold_ng_m3": ep["bc_threshold"], "horizon": "6h"}
        return {"issued_from": t0, "current_bc": float(df["BC6"].iloc[-1]), "horizons": res, "episode": episode,
                "history": df["BC6"].dropna().iloc[-96 * 2:]}

    # ---- batch nowcast for many rows (uploaded CSV or live feed)
    def estimate_batch(self, raw: pd.DataFrame) -> pd.DataFrame:
        std = standardize_columns(raw)
        if "Timestamp" not in std:
            raise ValueError("Need a Timestamp column.")
        keep = pd.to_datetime(std["Timestamp"], errors="coerce").dropna().dt.floor("15min")
        df = prepare_recent(raw)
        X = make_features(df, use_bc_history=False)
        b = self.bundles["virtual"]
        Xr = X.reindex(columns=b["features"])
        Xi = pd.DataFrame(b["imputer"].transform(Xr), columns=b["features"], index=Xr.index)
        pred = np.clip(b["model"].predict(Xi), 0, None)
        scale = np.maximum(pred, 100.0)
        out = pd.DataFrame({"bc6_estimate": pred, "lo": np.clip(pred - b["q"] * scale, 0, None),
                            "hi": pred + b["q"] * scale}, index=X.index)
        out = out.loc[out.index.isin(keep)]
        out["level"] = [self.level(v)["label"] for v in out["bc6_estimate"]]
        return out
