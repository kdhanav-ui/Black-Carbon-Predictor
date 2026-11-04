# 🌫️ Black Carbon Intelligence — Varanasi / Indo-Gangetic Plain

A leak-free ML system + 14-page public dashboard on 5 years of AE33 aethalometer data (IIT BHU, Varanasi):
virtual BC sensor, 15 min–24 h forecasts, episode warnings, biomass-vs-fossil source split, winter/season/Diwali/episode insights,
batch estimates, a "plan your day" risk planner and a beta live Varanasi outlook.

**Models:** for the virtual sensor and each horizon the pipeline benchmarks Ridge, kNN, MLP, Random Forest, Extra Trees, XGBoost,
LightGBM, CatBoost, a log-target LightGBM, a residual-to-persistence LightGBM (forecasts) and blends. The model that is **deployed**
is chosen by **validation R²** among the lean (small-file) candidates: XGBoost, LightGBM, their log/residual variants and blends.
All models are still benchmarked in the leaderboard so you can see how the deployed one compares (the training log prints this too).

---------------------------------------------------------------------------------------------------

# A. Train on your PC (VS Code)

1. Install **Python 3.13** (tick *Add to PATH*), **VS Code** + the *Python* extension, and **Git**.
2. VS Code → `File → Open Folder…` → this project folder.
3. Terminal (`Terminal → New Terminal`):
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   `Ctrl+Shift+P → Python: Select Interpreter → .venv`.
4. (Optional) check your file: `python scripts/inspect_data.py "C:\Users\kdhan\Downloads\combined_2021_2025_with_BC6.xlsx"`
5. Train (takes a while; add `--fast` for a quick trial):
   ```powershell
   python run_pipeline.py --data "C:\Users\kdhan\Downloads\combined_2021_2025_with_BC6.xlsx"
   ```
   Watch the lines `saved ...joblib  X MB` — every file should be small (a few MB). Add `--with-extratrees` only if you accept ~40 MB files.
6. Try it locally: `streamlit run app/dashboard.py` (http://localhost:8501).

# B. Prepare for deployment

```powershell
python scripts/make_requirements.py
```
This rewrites `requirements.txt` with the exact versions you trained with (pickled models need them) and tells you which Python
version to pick on Streamlit. Never type version numbers by hand.

# C. Push to GitHub

First time only: create an empty **public** repo `bc6-predictor` on github.com (no README), then
```powershell
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
git init
git add .
git commit -m "Black carbon dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/bc6-predictor.git
git push -u origin main
```
Later updates: `git add .` → `git commit -m "update"` → `git push`.
Check on github.com that `artifacts/models/*.joblib` and `artifacts/tables/*.csv` exist. `private_outputs/` and `.venv/` are git-ignored.

# D. Deploy on Streamlit Community Cloud (free)

1. https://share.streamlit.io → sign in with GitHub → **Create app → Deploy a public app from GitHub**.
2. Repository `YOUR-USERNAME/bc6-predictor`, branch `main`, main file `app/dashboard.py`.
3. **Advanced settings → Python version** = the same minor version as your PC (the script in step B prints it; e.g. 3.13).
4. **Deploy**. First build takes a few minutes. Afterwards every `git push` redeploys automatically.
5. Share the `https://<name>.streamlit.app` link. Free apps hibernate after inactivity; the first visitor wakes them (~30 s).

# E. Troubleshooting

| Symptom | Fix |
|---|---|
| `TypeError: Failed to fetch dynamically imported module …/index.xxxx.js` on charts | Stale browser tab after a reboot/redeploy: hard refresh (**Ctrl+Shift+R**) or open the link in a private window. Disable ad-blockers for the site. |
| Install error `No matching distribution…` / `Failed building wheel` | Wrong Python version on Streamlit or hand-typed versions. Re-run step B and set the same Python version in Streamlit. |
| "No trained artifacts found" | `artifacts/` was not pushed: `git add artifacts -f`, commit, push. |
| App restarts / out-of-memory | Use lean models (default). Check the `saved … MB` lines; retrain without `--with-extratrees`. |
| Error mentioning pickle / module / version | Library versions differ from training: redo step B and push. |
| VS Code yellow "import could not be resolved" | Select the `.venv` interpreter (step A3). |

# Limitations
Single site; alert levels are relative to this site's history (no official BC standard); the source split assumes AAE_ff = 1, AAE_bb = 2;
Diwali dates are approximate; the live page uses modelled CAMS data (not measurements); intervals assume future conditions resemble the
validation period. Research tool — not medical advice.

Author: Dhanav Kumar, NIT Raipur · Internship: IIT (BHU) Varanasi, Prof. Durga Prasad A. & Dr. Yogesh. Raw data is not included.
