# 🌫️ Black Carbon Intelligence — Varanasi / Indo-Gangetic Plain

![CI](https://github.com/<your-username>/bc6-predictor/actions/workflows/ci.yml/badge.svg)

A leak-free ML system + 14-page public dashboard built on 5 years of AE33 aethalometer data (IIT BHU, Varanasi).

## What it does
| Page | Purpose |
|---|---|
| 🏠 Overview | KPIs, auto-generated key findings, model skill vs persistence |
| 🧪 Estimate now | **Virtual BC sensor** from pollutants + weather (+ what-if & emission-scenario sensitivity) |
| 📦 Batch estimate | Upload a station time series → BC estimates + 90 % intervals → CSV |
| 🔮 Forecast & warnings | 15 min / 1 h / 6 h / 24 h forecasts + 6-h **episode warning** |
| 🌐 Live Varanasi (beta) | Indicative BC outlook from free Open-Meteo model data |
| 🗓️ Plan your day | Hour × month episode-risk heatmaps; cleanest / dirtiest hours |
| ❄️ Winter & seasons | Diurnal profiles, winter-by-year, stagnation (wind) effect, cold-humid regime map, leave-one-year-out skill |
| 🔥 Sources | Biomass vs fossil-fuel split (aethalometer model), AAE, heating signal |
| 🌫️ Episodes | Episode catalogue, onset hour, duration, composite around onset, weather vs baseline |
| 🎆 Diwali & events | Festival-night uplift vs surrounding days |
| 🔬 Drivers | Driver groups by season, correlations, BC share of PM2.5, BC/CO ratio |
| 🏆 Models & diagnostics | Leaderboards, skill vs persistence, interval coverage, bias by level/season/hour |
| 🧾 Data & downloads | Coverage heatmap, missingness, one-click ZIP of all results |

**Prediction quality:** for the virtual sensor and each forecast horizon the pipeline benchmarks Ridge, kNN, MLP, Random Forest, Extra Trees (full + compact), XGBoost, LightGBM, CatBoost, a **log-target** LightGBM, a **residual-to-persistence** LightGBM (forecasts) and top-2/top-3 blends, then deploys the winner by **validation** R². 90 % split-conformal intervals are calibrated on the validation set.

## What changed vs the first version
1. Lag features inflated R² → persistence baseline reported next to every model; *virtual sensor* (no BC history) separated from *forecasting*.
2. Lags are built on a regular 15-min grid (before, "24 h" lag was not 24 h).
3. Imputer fit on train only; embargo gap between splits; unit test proves no future leakage.

## Run in VS Code (Windows)
1. Install **VS Code** + the **Python** extension. `File → Open Folder…` → this folder.
2. `Terminal → New Terminal`, then:
   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   If VS Code asks to use the new environment, click **Yes**. (Or `Ctrl+Shift+P → Python: Select Interpreter → .venv`.)
3. `Run and Debug` (Ctrl+Shift+D) → choose a configuration → ▶:
   * **1) Inspect my data** – prints recognised columns, QC report, yearly coverage
   * **2) Train on my data** (or **2b** fast trial) – prompts for your xlsx path
   * **3) Dashboard** – opens http://localhost:8501
   Or use the terminal: `python run_pipeline.py --data "C:\path\file.xlsx"` then `streamlit run app/dashboard.py`.

## Deploy publicly (free)
1. Train locally (`artifacts/` is created). Raw-ish files (`sample_recent.csv`, out-of-fold predictions) go to `private_outputs/`, which is git-ignored; `artifacts/` holds only models + aggregated tables.
2. **Pin versions** so pickled models load on the server: in the VS Code terminal run
   `pip freeze | findstr /i "scikit-learn lightgbm xgboost catboost pandas numpy joblib scipy"` and put those exact `==` versions in `requirements.txt`.
3. Create a GitHub repo, then:
   ```bat
   git init
   git add .
   git commit -m "BC intelligence dashboard"
   git branch -M main
   git remote add origin https://github.com/<you>/bc6-predictor.git
   git push -u origin main
   ```
4. Go to **share.streamlit.io** → *New app* → repo, branch `main`, file `app/dashboard.py` → *Advanced settings → Python 3.11 or 3.12* → **Deploy**. Share the `https://<name>.streamlit.app` link.
5. Alternatives: Hugging Face Spaces (Docker) or `docker build -t bc6 . && docker run -p 8501:8501 bc6`.

Before publishing, check with your supervisors that aggregated results from the IIT BHU data may be shared.

## Layout
```
src/data.py  src/features.py  src/train.py  src/insights.py  src/analysis.py
src/predict.py  src/live.py  src/blend.py  src/api.py   app/dashboard.py   tests/
```

## Limitations
Single site; alert levels are relative to this site's history (no official BC standard); the source split assumes AAE_ff = 1, AAE_bb = 2; Diwali dates are approximate; the live page uses modelled (CAMS) rather than measured inputs; intervals assume future conditions resemble the validation period. Research tool — not medical advice.

Author: Dhanav Kumar, NIT Raipur · Internship: IIT (BHU) Varanasi, Prof. Durga Prasad A. & Dr. Yogesh. Raw data is not included.
