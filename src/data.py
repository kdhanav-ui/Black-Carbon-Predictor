"""Loading, standardising and quality-controlling AE33 + pollutant data.

Key design choice: everything is put on a REGULAR 15-minute grid *before* any
lag feature is built, so `shift(96)` really means 24 hours (the original
notebook dropped rows first, which silently broke the lag meaning).
"""
import numpy as np
import pandas as pd

from .config import BC_COLS, FREQ, MET, NAME_MAP, OPTIONAL, POLLUTANTS, TARGET

KNOWN = set(MET + POLLUTANTS + OPTIONAL + BC_COLS + [TARGET])


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """'PM2.5 (µg/m³)' -> 'PM25', 'AT (°C)' -> 'AT', unknown columns dropped."""
    ren = {}
    for c in df.columns:
        base = str(c).split(" (")[0].strip()
        base = NAME_MAP.get(base, base)
        if base in KNOWN or base == "Timestamp":
            ren[c] = base
    df = df.rename(columns=ren)
    df = df.loc[:, ~df.columns.duplicated()]
    return df[[c for c in df.columns if c in KNOWN or c == "Timestamp"]]


def to_grid(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["Timestamp"]).set_index("Timestamp").sort_index()
    df = df.apply(pd.to_numeric, errors="coerce")
    return df.resample(FREQ).mean()


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    for c in MET + POLLUTANTS:
        if c not in df.columns:
            df[c] = np.nan
    return df


def basic_qc(df: pd.DataFrame, clip_quantile=0.999):
    """Instrument-artefact removal. Bad BC values become NaN (rows are KEPT)."""
    df = df.copy()
    for c in POLLUTANTS:
        if c in df:
            df.loc[df[c] < 0, c] = np.nan
    if "RH" in df:
        df.loc[(df.RH < 0) | (df.RH > 100), "RH"] = np.nan
    if "WS" in df:
        df.loc[df.WS < 0, "WS"] = np.nan

    bc_cols = [c for c in BC_COLS if c in df]
    report = {"grid_rows": int(len(df))}
    if TARGET in df:
        report["bc6_valid_before_qc"] = int(df[TARGET].notna().sum())
        df.loc[df[TARGET] <= 0, bc_cols] = np.nan
        if clip_quantile:
            cap = float(df[TARGET].quantile(clip_quantile))
            df.loc[df[TARGET] > cap, bc_cols] = np.nan
            report["bc6_cap"] = cap
        report["bc6_valid_after_qc"] = int(df[TARGET].notna().sum())
    # causal short-gap fill (<= 1 h, forward only -> no future leakage)
    fill = [c for c in df.columns if c not in bc_cols]
    df[fill] = df[fill].ffill(limit=4)
    return df, report


def load_clean(path, clip_quantile=0.999):
    path = str(path)
    raw = pd.read_excel(path) if path.lower().endswith(("xlsx", "xls")) else pd.read_csv(path)
    n_raw = len(raw)
    df = ensure_columns(to_grid(standardize_columns(raw)))
    df, report = basic_qc(df, clip_quantile)
    report["raw_rows"] = int(n_raw)
    return df, report


def prepare_recent(raw: pd.DataFrame) -> pd.DataFrame:
    """For inference: user-supplied recent data -> gridded frame (no outlier clipping)."""
    df = ensure_columns(to_grid(standardize_columns(raw)))
    df, _ = basic_qc(df, clip_quantile=None)
    return df
