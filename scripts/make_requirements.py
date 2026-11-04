"""Writes a correct requirements.txt from the libraries installed on YOUR PC (pickled models need matching versions).
Run inside the activated venv, after training:   python scripts/make_requirements.py
Only the packages the deployed dashboard really needs are included.
"""
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

root = Path(__file__).resolve().parent.parent
meta = json.loads((root / "artifacts" / "meta.json").read_text())
used = " ".join(meta.get("deployed_models", {}).values())

pkgs = ["streamlit", "pandas", "numpy", "scipy", "plotly", "joblib", "requests", "scikit-learn", "lightgbm"]
if "XGBoost" in used:
    pkgs.append("xgboost")
if "CatBoost" in used:
    pkgs.append("catboost")

lines = []
for p in pkgs:
    try:
        lines.append(f"{p}=={version(p)}")
    except PackageNotFoundError:
        sys.exit(f"{p} is not installed in this environment - activate your .venv first.")
(root / "requirements.txt").write_text("\n".join(lines) + "\n")
print("Wrote requirements.txt:\n" + "\n".join(lines))
print(f"\nYour Python is {sys.version.split()[0]}. In Streamlit Cloud (Advanced settings) choose the same minor version "
      f"({sys.version_info.major}.{sys.version_info.minor}).")
