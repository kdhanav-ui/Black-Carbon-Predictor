import numpy as np
import pandas as pd

from src.blend import AvgBlend, LogModel, ResidualModel
from src.live import to_frame


def _fake(n=6):
    t = pd.date_range("2026-11-04 00:00", periods=n, freq="h").strftime("%Y-%m-%dT%H:%M").tolist()
    w = {"hourly": {"time": t, "temperature_2m": [15.0] * n, "relative_humidity_2m": [70.0] * n,
                    "wind_speed_10m": [1.2] * n, "wind_direction_10m": [90.0] * n,
                    "surface_pressure": [1000.0] * n, "shortwave_radiation": [0.0] * n, "precipitation": [0.0] * n}}
    a = {"hourly": {"time": t, "pm10": [120.0] * n, "pm2_5": [80.0] * n, "carbon_monoxide": [900.0] * n,
                    "nitrogen_dioxide": [30.0] * n, "sulphur_dioxide": [10.0] * n, "ozone": [20.0] * n}}
    return w, a


def test_live_frame_units_and_columns():
    df = to_frame(*_fake())
    assert len(df) == 6
    assert abs(df["CO"].iloc[0] - 0.9) < 1e-9            # ug/m3 -> mg/m3
    assert abs(df["BP"].iloc[0] - 750.062) < 1e-3        # hPa -> mmHg
    assert {"PM25", "PM10", "NO2", "SO2", "O3", "AT", "RH", "WS", "WD"} <= set(df.columns)


class _Const:
    def __init__(self, v): self.v = v
    def predict(self, X, **kw): return np.full(len(X), self.v, float)


def test_wrappers():
    X = pd.DataFrame({"BC6_lag0": [100.0, 200.0]})
    assert np.allclose(AvgBlend([_Const(1), _Const(3)], ["a", "b"]).predict(X), 2)
    assert np.allclose(ResidualModel(_Const(10)).predict(X), [110, 210])
    assert np.allclose(LogModel(_Const(np.log1p(500))).predict(X), 500, rtol=1e-6)
