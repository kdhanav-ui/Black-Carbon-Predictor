"""Central configuration for the BC6 predictor."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"

FREQ = "15min"
TARGET = "BC6"                       # AE33 880 nm channel (ng/m3)

# forecast horizons in 15-minute steps
HORIZONS = {"15min": 1, "1h": 4, "6h": 24, "24h": 96}
EPISODE_HORIZON = "6h"
EPISODE_QUANTILE = 0.90              # "episode" = BC above train P90
CONFORMAL_LEVEL = 0.90               # nominal coverage of prediction intervals

MET = ["AT", "RH", "WS", "WD", "SR", "RF", "BP"]
POLLUTANTS = ["PM25", "PM10", "NO", "NO2", "NOX", "NH3", "SO2", "CO", "O3", "BENZENE"]
OPTIONAL = ["PBLH", "fire_count"]    # used automatically if present in your data
BC_COLS = [f"BC{i}" for i in range(1, 8)]

# AE33 wavelengths (nm) and mass-absorption cross-sections (m2/g)
WAVELENGTH_NM = dict(zip(BC_COLS, [370, 470, 520, 590, 660, 880, 950]))
MAC = dict(zip(BC_COLS, [18.47, 14.54, 13.14, 11.58, 10.35, 7.77, 7.19]))

# column-name normalisation: "PM2.5 (µg/m³)" -> "PM25"
NAME_MAP = {"PM2.5": "PM25", "Ozone": "O3", "NOx": "NOX", "Benzene": "BENZENE"}

SEASON_NAMES = {1: "Winter", 2: "Pre-monsoon", 3: "Monsoon", 4: "Post-monsoon"}


def season_of(month: int) -> int:
    if month in (11, 12, 1, 2):
        return 1
    if month in (3, 4, 5):
        return 2
    if month in (6, 7, 8, 9):
        return 3
    return 4
