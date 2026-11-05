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


class _LazyBundles:
    """Loads each model file only when first used (keeps memory low on small servers)."""
    def __init__(self, folder):
        self.folder, self._cache = Path(folder), {}

    def _path(self, key):
        return self.folder / f"{key}.joblib"

    def __contains__(self, key):
        return self._path(key).exists()

    def __getitem__(self, key):
        if key not in self._cache:
            if not self._path(key).exists():
                raise KeyError(key)
            self._cache[key] = joblib.load(self._path(key))
        return self._cache[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


class Predictor:
    def __init__(self, art_dir=ARTIFACTS):
        art = Path(art_dir)
        self.dir = art
        self.meta = json.loads((art / "meta.json").read_text())
        self.bundles = _LazyBundles(art / "models")

    # ---- interpretation
    def level(self, bc):
        p = self.meta["bc_percentiles"]
        i = 0 if bc < p["p25"] else 1 if bc < p["p75"] else 2 if bc < p["p90"] else 3 if bc < p["p95"] else 4
        return dict(zip(["label", "color", "advice"], LEVELS[i]))

    def percentile_rank(self, bc):
        """Approximate percentile rank (0-100) within the site's historical BC distribution."""
        p = self.meta["bc_percentiles"]
        pts = [(0, 0), (p["p25"], 25), (p["p50"], 50), (p["p75"], 75), (p["p90"], 90), (p["p95"], 95), (p["p99"], 99)]
        if bc <= 0:
            return 0.0
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            if x0 <= bc <= x1:
                return round(y0 + (bc - x0) / (x1 - x0 + 1e-6) * (y1 - y0), 1)
        # Above p99
        return min(99.9, round(99.0 + (bc - p["p99"]) / (p["p99"] * 0.5 + 1e-6) * 0.9, 1))

    # ---- low-level
    def _predict(self, bundle, X_row):
        X = X_row.reindex(columns=bundle["features"])
        Xi = pd.DataFrame(bundle["imputer"].transform(X), columns=bundle["features"], index=X.index)
        p = float(np.clip(bundle["model"].predict(Xi)[0], 0, None))
        scale = max(p, 100.0)
        return {"pred": p, "lo": max(p - bundle["q"] * scale, 0.0), "hi": p + bundle["q"] * scale}, Xi

    def _explain(self, bundle, Xi):
        """Computes Tree SHAP contributions when supported by XGBoost, or falls back to feature sensitivities."""
        try:
            import xgboost as xgb
            model = bundle["model"]
            if hasattr(model, "get_booster"):
                booster = model.get_booster()
                dmat = xgb.DMatrix(Xi)
                contribs = booster.predict(dmat, pred_contribs=True)[0]
                feat_contribs = contribs[:-1]  # drop bias
                names = list(bundle["features"])
                items = sorted(zip(names, feat_contribs), key=lambda x: abs(x[1]), reverse=True)
                top_positive = [{"feature": k, "impact": round(float(v), 1)} for k, v in items if v > 0][:5]
                top_negative = [{"feature": k, "impact": round(float(v), 1)} for k, v in items if v < 0][:5]
                return {"supported": True, "top_drivers_positive": top_positive, "top_drivers_negative": top_negative}
        except Exception:
            pass
        return {"supported": False, "top_drivers_positive": [], "top_drivers_negative": []}

    # ---- nowcast from instantaneous readings (virtual sensor)
    def estimate(self, readings: dict, timestamp=None, explain: bool = True):
        """readings: any subset of AT, RH, WS, WD, SR, BP, PM25, PM10, CO, NO, NO2, NOX, SO2, O3, NH3, BENZENE."""
        ts = pd.Timestamp(timestamp or pd.Timestamp.now())
        row = pd.DataFrame([{k: v for k, v in readings.items() if v is not None}], index=[ts])
        row = ensure_columns(row)
        X = make_features(row, use_bc_history=False)
        out, Xi = self._predict(self.bundles["virtual"], X)
        out["level"] = self.level(out["pred"])
        out["percentile_rank"] = self.percentile_rank(out["pred"])
        out["interval_nominal"] = self.meta["virtual_interval"]["nominal"]

        # Physical diagnostics & sanity checks
        diagnostics = []
        pm25 = readings.get("PM25")
        if pm25 is not None and pm25 > 0:
            bc_ratio = (out["pred"] / 1000.0) / pm25  # ng/m3 -> ug/m3 / PM25
            out["bc_pm25_share_pct"] = round(bc_ratio * 100, 1)
            if bc_ratio > 1.0:
                diagnostics.append("Physical Warning: Estimated BC exceeds PM2.5. In ambient air, BC is typically 10-30% of PM2.5.")
            elif bc_ratio > 0.45:
                diagnostics.append("High Soot Fraction: BC makes up >45% of PM2.5, typical of intense combustion plumes (diesel/biomass).")
        else:
            out["bc_pm25_share_pct"] = None

        ws = readings.get("WS")
        rh = readings.get("RH")
        if ws is not None and ws < 0.8:
            if rh is not None and rh > 75:
                diagnostics.append("Stagnation Inversion: Low wind (<0.8 m/s) with high humidity (>75%) creates atmospheric trapping of soot.")
            else:
                diagnostics.append("Calm Winds: Stagnant dispersion layer enables local soot accumulation.")

        out["diagnostics"] = diagnostics
        if explain:
            out["explanation"] = self._explain(self.bundles["virtual"], Xi)
        return out

    # ---- what-if sensitivity sweep
    def what_if_sweep(self, readings: dict, variable: str, min_val: float, max_val: float, steps: int = 25, timestamp=None):
        ts = pd.Timestamp(timestamp or pd.Timestamp.now())
        base = {**self.meta.get("feature_medians_virtual", {}), **readings}
        xs = np.linspace(min_val, max_val, steps)
        ys = []
        for x in xs:
            modified = {**base, variable: float(x)}
            est = self.estimate(modified, ts, explain=False)
            ys.append(round(est["pred"], 1))
        return {"variable": variable, "xs": [round(float(x), 2) for x in xs], "ys": ys}

    # ---- what-if emission scaling
    def what_if_emission_scale(self, readings: dict, factors=None, timestamp=None):
        if factors is None:
            factors = [0.3, 0.5, 0.7, 0.85, 1.0, 1.15, 1.3]
        ts = pd.Timestamp(timestamp or pd.Timestamp.now())
        base = {**self.meta.get("feature_medians_virtual", {}), **readings}
        combustion_keys = ["CO", "NO", "NO2", "SO2", "PM25", "PM10"]
        ys = []
        for f in factors:
            mod = dict(base)
            for k in combustion_keys:
                if k in mod and mod[k] is not None:
                    mod[k] = mod[k] * f
            est = self.estimate(mod, ts, explain=False)
            ys.append(round(est["pred"], 1))
        return {"factors": [round(f * 100, 0) for f in factors], "ys": ys}

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
            r["percentile_rank"] = self.percentile_rank(r["pred"])
            res[h] = r
        ep = self.bundles.get("episode")
        episode = None
        if ep is not None:
            Xe = X.reindex(columns=ep["features"])
            Xi = pd.DataFrame(ep["imputer"].transform(Xe), columns=ep["features"])
            prob = float(ep["model"].predict_proba(Xi)[0, 1])
            episode = {"probability": prob, "warn": prob >= ep["decision_threshold"],
                       "threshold_ng_m3": ep["bc_threshold"], "horizon": "6h"}
        
        hist_series = df["BC6"].dropna().iloc[-96 * 2:]
        history_points = [{"time": str(t), "bc6": round(float(v), 1)} for t, v in zip(hist_series.index, hist_series.values)]

        return {
            "issued_from": t0,
            "current_bc": float(df["BC6"].iloc[-1]),
            "horizons": res,
            "episode": episode,
            "history_points": history_points,
            "history": hist_series
        }

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
