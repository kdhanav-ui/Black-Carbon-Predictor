"""Usage:
    python run_pipeline.py --data path/to/combined_2021_2025_with_BC6.xlsx
    python run_pipeline.py --demo            # synthetic data, to try the repo
Add --fast for a quick smoke run.
"""
import argparse
from pathlib import Path

from src.config import ARTIFACTS
from src.demo import make_demo
from src.train import run

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", help="xlsx/csv with Timestamp, BC6 (+ BC1..BC7 for source apportionment)")
    ap.add_argument("--out", default=str(ARTIFACTS))
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--with-extratrees", action="store_true", help="allow ExtraTrees in deployed blends (bigger files)")
    ap.add_argument("--demo", action="store_true", help="generate + use SYNTHETIC data")
    ap.add_argument("--demo-years", type=float, default=2.0)
    a = ap.parse_args()
    if a.demo:
        p = Path("data/demo_synthetic.csv")
        make_demo(str(p), years=a.demo_years)
        run(str(p), a.out, fast=a.fast, data_label="SYNTHETIC DEMO DATA (not real measurements)", with_trees=a.with_extratrees)
    elif a.data:
        run(a.data, a.out, fast=a.fast, with_trees=a.with_extratrees)
    else:
        ap.error("pass --data PATH or --demo")
