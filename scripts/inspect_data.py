"""Prints what the pipeline will see in your file. Paste the output to Claude if anything looks off.
Usage: python scripts/inspect_data.py "C:\\path\\to\\file.xlsx"
"""
import sys
sys.path.insert(0, ".")
import pandas as pd
from src.data import standardize_columns, load_clean
from src.config import BC_COLS, MET, POLLUTANTS, OPTIONAL

path = sys.argv[1]
raw = pd.read_excel(path) if path.lower().endswith(("xlsx", "xls")) else pd.read_csv(path)
print(f"\nRAW FILE: {len(raw):,} rows x {raw.shape[1]} columns")
print("Raw column names:", list(raw.columns))
std = standardize_columns(raw)
print("\nRecognised columns:", [c for c in std.columns if c != "Timestamp"])
need = ["Timestamp", "BC6"] + MET + POLLUTANTS
print("Missing expected columns:", [c for c in need if c not in std.columns] or "none")
print("BC wavelength channels found:", [c for c in BC_COLS if c in std.columns] or "none -> source split will be skipped")
print("Optional columns found:", [c for c in OPTIONAL if c in std.columns] or "none")
df, rep = load_clean(path)
print("\nQC report:", rep)
print("\nShare of 15-min slots with valid BC6 per year:")
print(df["BC6"].notna().groupby(df.index.year).mean().round(3).to_string())
