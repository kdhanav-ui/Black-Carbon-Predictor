"""Synthetic AE33-style dataset so the repo runs end-to-end without private data.

!! SYNTHETIC. Results trained on this are NOT scientific results. !!
"""
import numpy as np
import pandas as pd

from .config import BC_COLS, MAC, WAVELENGTH_NM


def make_demo(path: str, years: float = 2.0, seed: int = 0, start="2023-01-01") -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    t = pd.date_range(start, periods=int(years * 365 * 96), freq="15min")
    n = len(t)
    hour = t.hour + t.minute / 60
    doy = t.dayofyear.values
    winter = 0.5 + 0.5 * np.cos(2 * np.pi * (doy - 15) / 365)             # 1 in Jan, 0 in Jul
    night = ((hour >= 21) | (hour <= 6)).astype(float)
    rush = (((hour >= 7) & (hour <= 10)) | ((hour >= 18) & (hour <= 21))).astype(float)

    def ar1(phi, sigma):
        e = rng.normal(0, sigma, n)
        x = np.zeros(n)
        for i in range(1, n):
            x[i] = phi * x[i - 1] + e[i]
        return x

    at = 12 + 18 * (1 - winter) + 6 * np.sin(2 * np.pi * (hour - 9) / 24) + ar1(0.99, 0.15)
    rh = np.clip(70 - 25 * np.sin(2 * np.pi * (hour - 9) / 24) + ar1(0.99, 0.5), 15, 100)
    ws = np.clip(1.6 + 1.2 * np.sin(2 * np.pi * (hour - 8) / 24) - 0.6 * winter + ar1(0.97, 0.15), 0.1, 8)
    pbl = np.clip(600 + 900 * np.maximum(0, np.sin(2 * np.pi * (hour - 8) / 24)) * (1.2 - 0.6 * winter), 80, None)

    emis = np.exp(0.35 * ar1(0.995, 0.2)) * (1 + 0.8 * winter + 0.3 * rush + 0.4 * night * winter)
    stagn = 1 / (0.2 + ws * pbl / 1000)
    bc = np.clip(1800 * emis * stagn * np.exp(rng.normal(0, 0.12, n)), 50, 40000)

    co = 0.4 + bc / 4000 * np.exp(rng.normal(0, 0.45, n)) + rng.normal(0, 0.12, n)
    pm25 = 20 + bc / 55 * np.exp(rng.normal(0, 0.45, n)) + rng.normal(0, 12, n)
    no2 = 15 + bc / 400 * (1 + rush) * np.exp(rng.normal(0, 0.4, n)) + rng.normal(0, 6, n)
    no = 4 + bc / 700 * (1 + rush) + rng.normal(0, 1.5, n)

    bb_share = np.clip(0.25 + 0.35 * winter + 0.1 * night + rng.normal(0, 0.05, n), 0.02, 0.95)
    bb880, ff880 = bc * bb_share, bc * (1 - bb_share)
    babs880 = bb880 * MAC["BC6"], ff880 * MAC["BC6"]
    cols = {}
    for c in BC_COLS:
        lam = WAVELENGTH_NM[c]
        babs = babs880[1] * (880 / lam) ** 1.0 + babs880[0] * (880 / lam) ** 2.0
        cols[c] = babs / MAC[c] * np.exp(rng.normal(0, 0.02, n))

    df = pd.DataFrame({
        "Timestamp": t,
        "AT (°C)": at, "RH (%)": rh, "WS (m/s)": ws, "WD (deg)": rng.uniform(0, 360, n),
        "SR (W/mt2)": np.clip(700 * np.maximum(0, np.sin(2 * np.pi * (hour - 6) / 24)), 0, None),
        "RF (mm)": np.where(rng.random(n) < 0.01, rng.exponential(1, n), 0.0),
        "TOT-RF (mm)": 0.0, "BP (mmHg)": 745 + ar1(0.999, 0.05),
        "PM2.5 (µg/m³)": pm25, "PM10 (µg/m³)": pm25 * 1.8 + rng.normal(0, 10, n),
        "NO (µg/m³)": no, "NO2 (µg/m³)": no2, "NOx (ppb)": (no + no2) / 1.9,
        "NH3 (µg/m³)": 18 + rng.normal(0, 4, n), "SO2 (µg/m³)": 8 + rng.normal(0, 2, n),
        "CO (mg/m³)": co, "Ozone (µg/m³)": 30 + 40 * (1 - winter) + rng.normal(0, 8, n),
        "Benzene (µg/m³)": 2 + bc / 5000 + rng.normal(0, 0.3, n), "Toluene (µg/m³)": np.nan,
        **cols,
    })
    # realistic blemishes: outages, negatives, spikes
    for _ in range(25):
        s = rng.integers(0, n - 400)
        df.iloc[s:s + rng.integers(8, 400), df.columns.get_loc("BC6")] = np.nan
    df.loc[rng.choice(n, 40, replace=False), "BC6"] = -9999
    df.loc[rng.choice(n, 5, replace=False), "BC6"] = 90000
    df.loc[rng.choice(n, 500, replace=False), "CO (mg/m³)"] = np.nan
    df.to_csv(path, index=False)
    return df
