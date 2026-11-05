# 🌫️ Black Carbon Intelligence Platform — Varanasi & Indo-Gangetic Plain

[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite%20%2B%20Tailwind-61dafb?logo=react&logoColor=black)](https://vitejs.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%203.0-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.13-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Machine Learning](https://img.shields.io/badge/ML-XGBoost%20%7C%20LightGBM%20%7C%20CatBoost-ff6f00)](https://xgboost.readthedocs.io/)

A state-of-the-art **AI Virtual Sensor, Multi-Horizon Forecast Radar, and Chemical Physics Analytics Suite** for atmospheric **Black Carbon (BC)** in the Indo-Gangetic Plain. Built on **5 years of continuous research-grade Magee Scientific AE33 Aethalometer data** collected at the **Indian Institute of Technology (BHU), Varanasi**.

---

## 🌟 What is Black Carbon & Why Does This Matter?
- **What is Black Carbon (BC)?** Think of it as pure soot: the tiny, dark, toxic particles emitted when diesel trucks drive, farmers burn crop stubble, or people burn firewood and biomass for winter heating.
- **Why is it dangerous?** It is small enough to enter deep into the lungs and bloodstream (causing respiratory and cardiovascular illness) and strongly absorbs solar radiation, accelerating climate warming and glacial melting in the Himalayas.
- **Why build this?** A research-grade Aethalometer costs **$50,000+** and needs constant maintenance. This platform provides a **Virtual Sensor** that predicts Black Carbon using standard, inexpensive government monitoring stations (CAAQMS) with **90% conformal uncertainty intervals**, forecasts up to **24 hours ahead**, and sounds early warnings before toxic smog episodes occur.

---

## 🚀 12 Interactive Studios Built In
1. **🏠 Executive Overview**: Live KPIs (123k+ valid 15-min readings, 3,041 ng/m³ median), key AI findings, and skill vs persistence benchmarks.
2. **🧪 Virtual BC Sensor Studio**: Enter standard weather and gas inputs (PM2.5, CO, NO₂, Wind, Temp) or pick 1-click presets (*Winter Smog*, *Rush Hour*, *Clean Monsoon*). Get instant BC readings, hazard badges, and **Tree-SHAP local feature attribution** showing which inputs drove the pollution.
3. **🔬 What-If Simulation Lab**: Drag sliders across physical ranges to see how changing wind speed, humidity, or temperature affects soot. Test policy interventions like *"What if combustion traffic is reduced by 30%?"*.
4. **🔮 Multi-Horizon Forecast Radar**: 15-minute, 1-hour, 6-hour, and 24-hour lead times with historical lookback and a **6-hour severe episode warning siren**.
5. **🌐 Live Varanasi Sentinel**: Real-time Open-Meteo & Copernicus CAMS integration for Varanasi (25.32°N, 82.97°E) with 48h projections compared against 5-year historical diurnal baselines.
6. **🗓️ Plan Your Day (Exposure Optimizer)**: Hour-by-hour exposure planner by month. Recommends the safest windows for outdoor jogging and warns against hazardous nighttime stagnation traps.
7. **🔥 Source Apportionment**: Sandradewi dual-wavelength model (470 nm vs 950 nm) deconvolving soot into **vehicular fossil fuel (traffic diesel)** vs **solid biomass burning (woodsmoke/heating)**.
8. **❄️ Winter Smog & Stagnation**: Deep dive into the Indo-Gangetic Plain winter crisis, wind stagnation curves, and inter-annual winter severity.
9. **🎆 Diwali & Episode Anatomy**: High-resolution analysis of Diwali fireworks spikes and composite onset trajectory of **360+ pollution episodes**.
10. **🏆 AI Leaderboards**: Cross-validation benchmark of LightGBM, XGBoost, CatBoost, ExtraTrees, Random Forest, Ridge, and MLP with conformal coverage diagnostics.
11. **📦 Batch Laboratory**: Drag-and-drop CSV time-series uploader for CAAQMS data with instant interactive plots and annotated CSV export.
12. **ℹ️ Scientific Methodology**: Full transparency on instrumentation, QC filters, embargoed splits, and academic citations.

---

## 💻 How to Run on Your Computer (Quick & Easy)

### Step 1: Open the Project
Open this folder in **VS Code** or your terminal.

### Step 2: Set up Python
In your terminal, activate your virtual environment (or install the dependencies):
```powershell
pip install -r requirements.txt
```

### Step 3: Launch Everything with 1 Click!
Just run:
```powershell
python run_app.py
```
🎉 **That's it!** 
The script will automatically check the frontend build, start the high-speed FastAPI server, and open your web browser to **`http://localhost:8000`**.

---

## 🌐 Deploy the full app (single service)

**Recommended: Render Blueprint + Docker.** The React dashboard and FastAPI model API deploy together,
so you do not need separate Vercel/Render URLs or API environment variables.

1. Push this project folder to GitHub.
2. In Render, select **New → Blueprint** and connect the repository.
3. Render reads `render.yaml`, builds the Docker image, and deploys the app.
4. Open the generated URL. Check `/api/health` to verify the model service.

The free Render instance may sleep when idle, so the first visit can take longer. See
[`DEPLOY.md`](DEPLOY.md) for exact local and cloud steps, troubleshooting, and Docker commands.

## 🛠️ Developer & Pipeline Commands

If you ever retrain models on a new dataset or run automated tests:

- **Run all automated tests:**
  ```powershell
  python -m pytest tests/
  ```
- **Retrain models on new data:**
  ```powershell
  python run_pipeline.py --data "path/to/your/data.xlsx"
  ```
- **Run frontend Vite live dev server (with hot reload):**
  ```powershell
  cd frontend
  npm run dev
  ```
  *(Runs on http://localhost:5173 and automatically proxies API requests to http://localhost:8000)*

- **Rebuild production frontend:**
  ```powershell
  cd frontend
  npm run build
  ```

---

## 📜 Scientific Provenance & Credits
- **Author:** Dhanav Kumar, National Institute of Technology (NIT) Raipur.
- **Research Supervision:** Prof. Durga Prasad A. & Dr. Yogesh, Indian Institute of Technology (BHU), Varanasi.
- **Instrumentation:** Continuous Magee Scientific AE33 Aethalometer co-located with CPCB CAAQMS, Varanasi, India (2021–2025).
- **Disclaimer:** Research, educational, and environmental analytics tool — not clinical medical advice. Alert thresholds are calibrated relative to this site's historical atmospheric distribution.



## Deploy the FastAPI API on Vercel

This repository exposes the FastAPI application from `src/api.py`. The root
`pyproject.toml` tells Vercel to use `src.api:app` as its entrypoint.

1. Import the repository into Vercel.
2. Keep the **Root Directory** set to the repository root (`bc6-predictor` if the repository contains this folder).
3. Ensure the root `pyproject.toml`, `requirements.txt`, `src/`, and `artifacts/` are included in the deployment.
4. Deploy and test `/api/health`.

The React/Vite frontend is a separate build (`frontend/`). For a split deployment,
host the frontend on Netlify and configure its API base URL to point to the deployed
FastAPI endpoint. Vercel's FastAPI deployment does not automatically serve the Vite
frontend as a static site.

