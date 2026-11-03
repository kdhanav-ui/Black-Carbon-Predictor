"""Live Varanasi outlook from Open-Meteo (free, no API key).

CAUTION: Open-Meteo air-quality values are *model* (CAMS) data, not station measurements, and NO / NOx / NH3 /
benzene are not provided. The resulting BC numbers are an INDICATIVE trend, not a calibrated forecast.
"""
import pandas as pd
import requests

LAT, LON = 25.3176, 82.9739      # Varanasi
W_URL = "https://api.open-meteo.com/v1/forecast"
A_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
W_VARS = "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,surface_pressure,shortwave_radiation,precipitation"
A_VARS = "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone"


def fetch(lat=LAT, lon=LON, past_days=1, forecast_days=3, timeout=20):
    common = dict(latitude=lat, longitude=lon, timezone="Asia/Kolkata", past_days=past_days, forecast_days=forecast_days)
    w = requests.get(W_URL, params={**common, "hourly": W_VARS, "wind_speed_unit": "ms"}, timeout=timeout)
    a = requests.get(A_URL, params={**common, "hourly": A_VARS}, timeout=timeout)
    w.raise_for_status(); a.raise_for_status()
    return w.json(), a.json()


def to_frame(weather: dict, aq: dict) -> pd.DataFrame:
    w = pd.DataFrame(weather["hourly"]).set_index("time")
    a = pd.DataFrame(aq["hourly"]).set_index("time")
    d = w.join(a, how="inner")
    out = pd.DataFrame({
        "Timestamp": pd.to_datetime(d.index),
        "AT": d["temperature_2m"].values, "RH": d["relative_humidity_2m"].values,
        "WS": d["wind_speed_10m"].values, "WD": d["wind_direction_10m"].values,
        "BP": d["surface_pressure"].values * 0.750062,           # hPa -> mmHg
        "SR": d["shortwave_radiation"].values, "RF": d["precipitation"].values,
        "PM25": d["pm2_5"].values, "PM10": d["pm10"].values,
        "CO": d["carbon_monoxide"].values / 1000.0,              # ug/m3 -> mg/m3
        "NO2": d["nitrogen_dioxide"].values, "SO2": d["sulphur_dioxide"].values, "O3": d["ozone"].values,
    })
    return out
