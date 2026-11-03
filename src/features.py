"""Leak-free feature engineering + aethalometer-model source apportionment.

Every feature at row t uses information available at time t or earlier.
`use_bc_history=False` builds the sensor-free "virtual BC sensor" feature set
(no BC-derived column at all).
"""
import numpy as np
import pandas as pd

from .config import MAC, MET, OPTIONAL, POLLUTANTS, TARGET, WAVELENGTH_NM, season_of

BC_LAGS = [0, 1, 2, 4, 8, 16, 32, 96]
BC_WINDOWS = [4, 16, 96]


def _flag(cond: pd.Series, ref: pd.Series) -> pd.Series:
    return cond.astype(float).where(ref.notna())


def make_features(df: pd.DataFrame, use_bc_history: bool) -> pd.DataFrame:
    idx = df.index
    X = pd.DataFrame(index=idx)

    # --- cyclical calendar features
    hour = idx.hour + idx.minute / 60
    X["hour_sin"], X["hour_cos"] = np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)
    doy = idx.dayofyear
    X["doy_sin"], X["doy_cos"] = np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)
    dow = idx.dayofweek
    X["dow_sin"], X["dow_cos"] = np.sin(2 * np.pi * dow / 7), np.cos(2 * np.pi * dow / 7)
    X["month"] = idx.month
    X["season"] = [season_of(m) for m in idx.month]
    X["is_winter"] = (X["season"] == 1).astype(float)
    X["is_weekend"] = (dow >= 5).astype(float)
    h = idx.hour
    X["is_rush"] = (((h >= 7) & (h <= 10)) | ((h >= 18) & (h <= 21))).astype(float)
    X["is_night"] = ((h >= 21) | (h <= 5)).astype(float)

    # --- raw measurements
    for c in MET + POLLUTANTS + [o for o in OPTIONAL if o in df]:
        X[c] = df[c] if c in df else np.nan

    # --- meteorology-derived
    T, RH, WS = X["AT"], X["RH"].clip(1, 100), X["WS"]
    gamma = np.log(RH / 100) + 17.625 * T / (243.04 + T)
    X["dew_point"] = 243.04 * gamma / (17.625 - gamma)
    wd = np.deg2rad(X["WD"])
    X["u_wind"], X["v_wind"] = -WS * np.sin(wd), -WS * np.cos(wd)
    X["stagnation"] = _flag(WS < 1.0, WS)
    X["stability_proxy"] = X["SR"] / WS.clip(lower=0.1)
    X["rain_flag"] = _flag(X["RF"] > 0.1, X["RF"])
    if "PBLH" in X:                      # physically-correct ventilation coefficient
        X["ventilation_coeff"] = X["PBLH"] * WS
        X["log_ventilation"] = np.log1p(X["ventilation_coeff"].clip(lower=0))

    # --- pollutant-derived
    X["CO_x_NO"] = X["CO"] * X["NO"]
    X["PM_fine_frac"] = X["PM25"] / (X["PM10"] + 1)
    X["NO2_NO_ratio"] = X["NO2"] / (X["NO"] + 1)
    X["CO_x_SO2"] = X["CO"] * X["SO2"]
    for c in ["PM25", "PM10", "CO", "SO2", "NO", "NO2", "NH3", "BENZENE"]:
        X[f"log_{c}"] = np.log1p(X[c].clip(lower=0))
    for c in ["CO", "PM25", "NO2"]:
        for w in (4, 16, 96):
            X[f"{c}_roll{w}"] = X[c].rolling(w, min_periods=1).mean()
    X["PM25_diff1h"] = X["PM25"].diff(4)

    # --- BC history (forecasting only; absent in the virtual sensor)
    if use_bc_history:
        bc = df[TARGET]
        for lag in BC_LAGS:
            X[f"BC6_lag{lag}"] = bc.shift(lag)
        for w in BC_WINDOWS:
            X[f"BC6_roll_mean{w}"] = bc.rolling(w, min_periods=1).mean()
            X[f"BC6_roll_std{w}"] = bc.rolling(w, min_periods=2).std()
        X["BC6_trend1h"] = bc - bc.shift(4)

    return X.replace([np.inf, -np.inf], np.nan)


def make_target(df: pd.DataFrame, horizon_steps: int) -> pd.Series:
    """BC6 `horizon_steps` x 15 min into the future (0 = nowcast)."""
    return df[TARGET].shift(-horizon_steps)


def source_apportionment(df: pd.DataFrame, short="BC2", long="BC7"):
    """Aethalometer model (Sandradewi et al., 2008): biomass vs fossil-fuel BC.

        b_abs(l) = b_ff(l) + b_bb(l),   b_x(l) ~ l^-AAE_x   (AAE_ff=1, AAE_bb=2)

    Solved from two channels (default 470 / 950 nm) and reported at 880 nm.
    The AE33 C-factor is common to all channels and cancels in the ratio.
    Returns None if the BC channels are not in the data.
    NOTE: uses same-time BC channels, so it is an ANALYSIS tool, never a model input.
    """
    if short not in df or long not in df:
        return None
    l1, l2 = WAVELENGTH_NM[short], WAVELENGTH_NM[long]
    b1 = (df[short] * MAC[short]).where(df[short] > 0)
    b2 = (df[long] * MAC[long]).where(df[long] > 0)
    a_ff, a_bb = 1.0, 2.0
    r_ff, r_bb = (l2 / l1) ** a_ff, (l2 / l1) ** a_bb
    bb2 = ((b1 - r_ff * b2) / (r_bb - r_ff)).clip(lower=0)
    bb2 = np.minimum(bb2, b2)
    ff2 = b2 - bb2
    lt = WAVELENGTH_NM["BC6"]
    bb_t = bb2 * (l2 / lt) ** a_bb
    ff_t = ff2 * (l2 / lt) ** a_ff
    out = pd.DataFrame({"bb_fraction": (bb_t / (bb_t + ff_t)).clip(0, 1),
                        "AAE": np.log(b1 / b2) / np.log(l2 / l1)}, index=df.index)
    out["BC_bb"] = df[TARGET] * out["bb_fraction"]
    out["BC_ff"] = df[TARGET] - out["BC_bb"]
    return out
