"""End-to-end training pipeline.

Experiments
  A. Virtual BC sensor   - nowcast BC6 from pollutants + meteorology ONLY (no BC history)
  B. Multi-horizon fcst  - 15 min / 1 h / 6 h / 24 h ahead, with BC history
  C. Episode warning     - will BC6 exceed the train P90 in 6 h?  (classifier)
  D. Leave-one-year-out  - out-of-fold predictions -> robust per-season (winter) metrics
  E. Source apportionment- biomass vs fossil-fuel BC (needs BC1..BC7 columns)

Everything uses chronological splits with an embargo gap, train-only imputation
and a regular 15-min grid, so reported scores are free of the leakage in v1.
"""
import json
import time
from datetime import datetime

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
import xgboost as xgb
from catboost import CatBoostRegressor
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import (average_precision_score, f1_score, mean_absolute_error,
                             mean_squared_error, precision_score, r2_score,
                             recall_score, roc_auc_score)
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import RobustScaler

from . import analysis, insights
from .blend import AvgBlend, LogModel, ResidualModel
from .config import (ARTIFACTS, CONFORMAL_LEVEL, EPISODE_HORIZON, EPISODE_QUANTILE,
                     HORIZONS, SEASON_NAMES, TARGET)
from .data import load_clean
from .features import make_features, make_target, source_apportionment

SEED = 42
np.random.seed(SEED)


def log(*a):
    print(time.strftime("[%H:%M:%S]"), *a, flush=True)


# ------------------------------------------------------------------ helpers
def metrics(name, y, p):
    y, p = np.asarray(y, float), np.asarray(p, float)
    return {"Model": name, "R2": r2_score(y, p),
            "RMSE": float(np.sqrt(mean_squared_error(y, p))),
            "MAE": mean_absolute_error(y, p),
            "MAPE(%)": float(np.mean(np.abs((y - p) / y)) * 100),
            "Bias": float(np.mean(p - y))}


def build_dataset(df, horizon_steps, use_bc):
    X = make_features(df, use_bc)
    y = make_target(df, horizon_steps)
    ok = y.notna() & (X[["CO", "PM25", "NO2", "AT", "WS"]].notna().sum(axis=1) >= 3)
    if use_bc:
        ok &= X["BC6_lag0"].notna()
    return X[ok], y[ok]


def chrono_split(X, y, embargo):
    """70/15/15 by time with an `embargo` gap so rolling windows never straddle splits."""
    n = len(X)
    a, b = int(n * 0.70), int(n * 0.85)
    sl = {"tr": slice(0, a), "va": slice(a + embargo, b), "te": slice(b + embargo, n)}
    return {k: (X.iloc[s], y.iloc[s]) for k, s in sl.items()}


def impute(split):
    """Median imputer fitted on TRAIN only (v1 fitted MICE on the whole dataset)."""
    imp = SimpleImputer(strategy="median", keep_empty_features=True).fit(split["tr"][0])
    cols = split["tr"][0].columns
    out = {k: (pd.DataFrame(imp.transform(X), columns=cols, index=X.index), y)
           for k, (X, y) in split.items()}
    return imp, out


def zoo(fast):
    n = 60 if fast else 400
    return {
        "Ridge": (Ridge(alpha=10), True),
        "KNN": (KNeighborsRegressor(n_neighbors=10, weights="distance", n_jobs=-1), True),
        "MLP": (MLPRegressor(hidden_layer_sizes=(128, 64, 32), early_stopping=True,
                             max_iter=60 if fast else 300, random_state=SEED), True),
        "RandomForest": (RandomForestRegressor(n_estimators=n // 2, max_depth=18, min_samples_leaf=2,
                                               n_jobs=-1, random_state=SEED), False),
        "ExtraTrees": (ExtraTreesRegressor(n_estimators=n // 2, max_depth=20, min_samples_leaf=2,
                                           n_jobs=-1, random_state=SEED), False),
        "ExtraTrees_compact": (ExtraTreesRegressor(n_estimators=40 if fast else 120, max_depth=18,
                                                   min_samples_leaf=5, n_jobs=-1, random_state=SEED), False),
        "XGBoost": (xgb.XGBRegressor(n_estimators=n * 3, learning_rate=0.05, max_depth=7,
                                     subsample=0.8, colsample_bytree=0.8, tree_method="hist",
                                     early_stopping_rounds=30, random_state=SEED, verbosity=0), False),
        "LightGBM": (make_lgbm(fast), False),
        "CatBoost": (CatBoostRegressor(iterations=n * 3, learning_rate=0.06, depth=7, random_seed=SEED,
                                       verbose=0, early_stopping_rounds=30, allow_writing_files=False), False),
    }


def make_lgbm(fast):
    return lgb.LGBMRegressor(n_estimators=400 if fast else 2000, learning_rate=0.04, num_leaves=63,
                             subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                             reg_alpha=0.1, reg_lambda=1.0, random_state=SEED, verbosity=-1)


def fit_one(name, model, Xtr, ytr, Xva, yva):
    if name == "XGBoost":
        model.fit(Xtr, ytr, eval_set=[(Xva, yva)], verbose=False)
    elif name == "LightGBM":
        model.fit(Xtr, ytr, eval_set=[(Xva, yva)],
                  callbacks=[lgb.early_stopping(50, verbose=False)])
    elif name == "CatBoost":
        model.fit(Xtr, ytr, eval_set=(Xva, yva), verbose=False)
    else:
        model.fit(Xtr, ytr)
    return model


def benchmark(sp, names, fast, baselines):
    """Fit models in `names`; return metrics DF, test preds, val preds, fitted models, scaler."""
    (Xtr, ytr), (Xva, yva), (Xte, yte) = sp["tr"], sp["va"], sp["te"]
    sc = RobustScaler().fit(Xtr)
    scaled = {k: sc.transform(v[0]) for k, v in sp.items()}
    rows, pte, pva, fitted = [], {}, {}, {}
    for bname, fn in baselines.items():
        pte[bname], pva[bname] = fn(Xte), fn(Xva)
        rows.append(metrics(bname, yte, pte[bname]))
    for name, (model, needs_scale) in zoo(fast).items():
        if name not in names:
            continue
        t0 = time.time()
        A = scaled if needs_scale else {k: v[0] for k, v in sp.items()}
        model = fit_one(name, model, A["tr"], ytr, A["va"], yva)
        pte[name], pva[name] = model.predict(A["te"]), model.predict(A["va"])
        fitted[name] = model
        rows.append(metrics(name, yte, pte[name]))
        log(f"    {name:<13} R2={rows[-1]['R2']:.4f}  RMSE={rows[-1]['RMSE']:.0f}  ({time.time()-t0:.0f}s)")
    return pd.DataFrame(rows), pte, pva, fitted, sc


def add_ensemble(res, names, pte, pva, yva, yte):
    top = sorted(names, key=lambda m: r2_score(yva, pva[m]), reverse=True)[:3]
    w = np.array([max(r2_score(yva, pva[m]), 1e-6) for m in top])
    w = w / w.sum()
    p = sum(w[i] * pte[m] for i, m in enumerate(top))
    res = pd.concat([res, pd.DataFrame([metrics("Ensemble_Top3", yte, p)])], ignore_index=True)
    return res, f"Top-3 by val R2: {top}"


# Lean by default: boosted trees only -> files of a few MB that fit free hosting. Use --with-extratrees to add
# ExtraTrees_compact as a deployment candidate (more accurate sometimes, but ~40 MB per model).
DEPLOYABLE = ["XGBoost", "LightGBM"]


def fit_extras(spi, fast, residual):
    """Extra candidates: log-target LightGBM (skewed BC) and, for forecasts, a residual-vs-persistence LightGBM."""
    (Xtr, ytr), (Xva, yva), _ = spi["tr"], spi["va"], spi["te"]
    cb = [lgb.early_stopping(50, verbose=False)]
    out = {}
    m = make_lgbm(fast)
    m.fit(Xtr, np.log1p(ytr), eval_set=[(Xva, np.log1p(yva))], callbacks=cb)
    out["LightGBM_log"] = LogModel(m)
    if residual:
        m = make_lgbm(fast)
        m.fit(Xtr, ytr - Xtr["BC6_lag0"], eval_set=[(Xva, yva - Xva["BC6_lag0"])], callbacks=cb)
        out["LightGBM_resid"] = ResidualModel(m)
    return out


def pick_deployable(fitted, pva, yva, extras=None, Xva=None):
    """Choose the model to ship by VALIDATION R2 (never by test R2); also tries top-2 and top-3 blends."""
    cands = {m: fitted[m] for m in DEPLOYABLE if m in fitted}
    pv = {m: pva[m] for m in cands}
    for k, mdl in (extras or {}).items():
        cands[k], pv[k] = mdl, mdl.predict(Xva)
    ranked = sorted(cands, key=lambda m: r2_score(yva, pv[m]), reverse=True)
    for k in (2, 3):
        if len(ranked) >= k:
            top = ranked[:k]
            nm = "Blend(" + "+".join(top) + ")"
            cands[nm] = AvgBlend([cands[m] for m in top], top)
            pv[nm] = np.mean([pv[m] for m in top], axis=0)
    best = max(pv, key=lambda m: r2_score(yva, pv[m]))
    return best, cands[best]


def conformal(model, Xva, yva, Xte, yte, level=CONFORMAL_LEVEL, floor=100.0):
    """Split-conformal intervals with RELATIVE width (BC spans 3 orders of magnitude)."""
    pv = np.clip(model.predict(Xva), 0, None)
    scale = np.maximum(pv, floor)
    scores = np.abs(np.asarray(yva) - pv) / scale
    k = int(np.ceil((len(scores) + 1) * level))
    q = float(np.sort(scores)[min(k, len(scores)) - 1])
    pt = np.clip(model.predict(Xte), 0, None)
    st = np.maximum(pt, floor)
    lo, hi = np.clip(pt - q * st, 0, None), pt + q * st
    cov = float(np.mean((np.asarray(yte) >= lo) & (np.asarray(yte) <= hi)))
    return q, cov, float(np.mean(hi - lo))


def lgbm_contrib_importance(model, X, n=3000):
    s = X.sample(min(n, len(X)), random_state=SEED)
    contrib = model.predict(s, pred_contrib=True)[:, :-1]
    return (pd.DataFrame({"feature": X.columns, "mean_abs_contribution": np.abs(contrib).mean(0)})
            .sort_values("mean_abs_contribution", ascending=False).reset_index(drop=True))


# ------------------------------------------------------------------ main
def run(data_path, out_dir=ARTIFACTS, fast=False, data_label=None, with_trees=False):
    global DEPLOYABLE
    DEPLOYABLE = ["XGBoost", "LightGBM"] + (["ExtraTrees_compact"] if with_trees else [])
    out = analysis.prepare_dirs(out_dir)
    t_start = time.time()
    log("Loading + QC")
    df, qc_report = load_clean(data_path)
    log(f"  grid rows={qc_report['grid_rows']:,}  valid BC6 after QC={qc_report['bc6_valid_after_qc']:,}")

    tables, bundles = {}, {}
    meta = {"created": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "data_source": data_label or str(data_path), "fast_mode": fast,
            "qc": qc_report, "horizons": HORIZONS}

    # ---------------- A. virtual BC sensor
    log("A. Virtual BC sensor (no BC history)")
    X, y = build_dataset(df, 0, use_bc=False)
    sp = chrono_split(X, y, embargo=96)
    imp, spi = impute(sp)
    meta["train_period"] = [str(sp["tr"][0].index.min()), str(sp["tr"][0].index.max())]
    meta["test_period"] = [str(sp["te"][0].index.min()), str(sp["te"][0].index.max())]
    meta["n_train_val_test"] = [len(sp["tr"][0]), len(sp["va"][0]), len(sp["te"][0])]
    tr_clim = pd.concat([sp["tr"][0][["season"]].assign(hour=sp["tr"][0].index.hour), sp["tr"][1].rename("y")], axis=1)
    clim = tr_clim.groupby(["season", "hour"])["y"].mean()

    def climatology(Xs):
        key = pd.MultiIndex.from_arrays([Xs["season"].astype(int), Xs.index.hour])
        return clim.reindex(key).fillna(clim.mean()).values

    names = list(zoo(fast).keys())
    res_v, pte, pva, fitted, sc = benchmark(spi, names, fast, {"Climatology(season x hour)": climatology})
    res_v, ens_note = add_ensemble(res_v, names, pte, pva, spi["va"][1], spi["te"][1])
    log("  " + ens_note)
    extras = fit_extras(spi, fast, residual=False)
    res_v = pd.concat([res_v, pd.DataFrame([metrics(k, spi["te"][1], m.predict(spi["te"][0])) for k, m in extras.items()])], ignore_index=True)
    best_name, best_model = pick_deployable(fitted, pva, spi["va"][1], extras, spi["va"][0])
    log(f"  deploying {best_name} (highest validation R2)")
    dep_row = metrics(f"DEPLOYED: {best_name}", spi["te"][1], best_model.predict(spi["te"][0]))
    top_all = res_v.sort_values("R2").iloc[-1]
    log(f"  test R2: deployed={dep_row['R2']:.4f} vs best single model overall ({top_all['Model']})={top_all['R2']:.4f}")
    res_v = pd.concat([res_v, pd.DataFrame([dep_row])], ignore_index=True)
    tables["virtual_sensor_leaderboard"] = res_v.sort_values("R2", ascending=False).reset_index(drop=True)

    lg = fitted["LightGBM"]            # used for the feature-importance chart
    q, cov, width = conformal(best_model, spi["va"][0], spi["va"][1], spi["te"][0], spi["te"][1])
    log(f"  conformal q={q:.3f} coverage={cov:.3f} mean width={width:.0f} ng/m3")
    bundles["virtual"] = dict(model=best_model, imputer=imp, features=list(X.columns), q=q, steps=0,
                              use_bc=False, model_name=best_name)
    meta["deployed_models"] = {"virtual": best_name}
    meta["virtual_interval"] = {"nominal": CONFORMAL_LEVEL, "empirical_coverage": cov, "mean_width": width}
    imp_df = lgbm_contrib_importance(lg, spi["te"][0])
    tables["feature_importance_virtual"] = imp_df
    tables.update(_diagnostics(best_model, q, spi["te"][0], spi["te"][1]))
    tables["importance_groups_by_season"] = _group_importance_by_season(lg, spi["te"][0])

    # ---------------- B. multi-horizon forecasting
    log("B. Multi-horizon forecasts (with BC history)")
    hrows = []
    for hname, steps in HORIZONS.items():
        Xh, yh = build_dataset(df, steps, use_bc=True)
        sph = chrono_split(Xh, yh, embargo=96 + steps)
        imph, sphi = impute(sph)
        base = {"Persistence (BC now)": lambda Xs: Xs["BC6_lag0"].values}
        res_h, pte_h, pva_h, fit_h, _ = benchmark(sphi, ["Ridge", "ExtraTrees_compact", "XGBoost", "LightGBM"], fast, base)
        ex_h = fit_extras(sphi, fast, residual=True)
        res_h = pd.concat([res_h, pd.DataFrame([metrics(k, sphi["te"][1], m.predict(sphi["te"][0])) for k, m in ex_h.items()])], ignore_index=True)
        bn, bm = pick_deployable(fit_h, pva_h, sphi["va"][1], ex_h, sphi["va"][0])
        res_h = pd.concat([res_h, pd.DataFrame([metrics(f"DEPLOYED: {bn}", sphi["te"][1], bm.predict(sphi["te"][0]))])], ignore_index=True)
        meta["deployed_models"][hname] = bn
        res_h.insert(0, "Horizon", hname)
        hrows.append(res_h)
        qh, covh, wh = conformal(bm, sphi["va"][0], sphi["va"][1], sphi["te"][0], sphi["te"][1])
        bundles[f"h_{hname}"] = dict(model=bm, imputer=imph, features=list(Xh.columns),
                                     q=qh, steps=steps, use_bc=True, coverage=covh, model_name=bn)
        log(f"  [{hname}] deploying {bn}; conformal coverage={covh:.3f}")
        if hname == EPISODE_HORIZON:
            episode = _episode_model(sphi, imph, list(Xh.columns), steps, fast, out)
            bundles["episode"] = episode["bundle"]
            tables["episode_metrics"] = episode["table"]
    tables["forecast_horizons"] = pd.concat(hrows, ignore_index=True)

    # ---------------- D. leave-one-year-out (robust seasonal metrics)
    log("D. Leave-one-year-out CV (virtual sensor)")
    oof = _loyo(X, y, fast)
    if oof is not None:
        oof["season"] = [SEASON_NAMES[s] for s in X.loc[oof.index, "season"].astype(int)]
        tables["seasonal_metrics_oof"] = analysis.seasonal_metrics(oof)
        tables["yearly_metrics_oof"] = analysis.yearly_metrics(oof)
        oof.to_csv(out["private"] / "oof_virtual.csv.gz")
        tables["calibration_oof"] = analysis.calibration_table(oof)

    # ---------------- E. source apportionment
    log("E. Source apportionment")
    ap = source_apportionment(df)
    if ap is not None:
        ap_tabs = analysis.apportionment_tables(ap)
        tables.update(ap_tabs)
        meta["apportionment"] = {"available": True, "winter_bb_share": analysis.winter_bb_share(ap)}
    else:
        meta["apportionment"] = {"available": False}
        log("  BC1..BC7 columns not found -> skipped")

    # ---------------- F. insights
    log("F. Insight tables")
    thr90 = float(df[TARGET].quantile(0.90))
    ins = insights.build_all(df, ap, thr90)
    tables.update(ins["tables"])
    meta["insights"] = ins["headlines"]
    sk = tables["forecast_horizons"]
    skill = []
    for hname in HORIZONS:
        g = sk[sk.Horizon == hname].set_index("Model")
        dep = [m for m in g.index if m.startswith("DEPLOYED")]
        if dep and "Persistence (BC now)" in g.index:
            skill.append({"Horizon": hname, "Model": dep[0].replace("DEPLOYED: ", ""),
                          "R2_model": g.loc[dep[0], "R2"], "R2_persistence": g.loc["Persistence (BC now)", "R2"],
                          "RMSE_reduction_vs_persistence_%": (1 - g.loc[dep[0], "RMSE"] / g.loc["Persistence (BC now)", "RMSE"]) * 100})
    tables["skill_vs_persistence"] = pd.DataFrame(skill)

    # ---------------- save
    meta["bc_percentiles"] = {f"p{p}": float(df[TARGET].quantile(p / 100)) for p in (25, 50, 75, 90, 95, 99)}
    meta["feature_medians_virtual"] = {k: float(v) for k, v in
                                       pd.Series(imp.statistics_, index=X.columns).items()
                                       if k in ("AT", "RH", "WS", "WD", "SR", "BP", "PM25", "PM10", "CO", "NO", "NO2",
                                                "NOX", "SO2", "O3", "NH3", "BENZENE", "RF")}
    for k, b in bundles.items():
        joblib.dump(b, out["models"] / f"{k}.joblib", compress=3)
        mb = (out["models"] / f"{k}.joblib").stat().st_size / 1e6
        log(f"  saved {k}.joblib  {mb:.1f} MB" + ("   <-- large for free hosting; consider lean models" if mb > 25 else ""))
    for k, t in tables.items():
        t.to_csv(out["tables"] / f"{k}.csv", index=False)
    recent = df.loc[sp["te"][0].index.max() - pd.Timedelta(days=4):].reset_index()
    recent.to_csv(out["private"] / "sample_recent.csv", index=False)
    (out["root"] / "meta.json").write_text(json.dumps(meta, indent=2, default=float))

    analysis.make_figures(tables, df, ap, out["figures"])
    log(f"DONE in {(time.time()-t_start)/60:.1f} min -> {out['root']}")
    return tables, meta


def _diagnostics(model, q, Xte, yte, floor=100.0):
    pred = np.clip(model.predict(Xte), 0, None)
    sc = np.maximum(pred, floor)
    lo, hi = np.clip(pred - q * sc, 0, None), pred + q * sc
    d = pd.DataFrame({"actual": np.asarray(yte), "pred": pred, "inside": (np.asarray(yte) >= lo) & (np.asarray(yte) <= hi),
                      "hour": Xte.index.hour, "season": [SEASON_NAMES[int(x)] for x in Xte["season"]]})
    d["err"] = d.pred - d.actual
    d["abs_err"] = d.err.abs()
    agg = dict(n=("err", "size"), MAE=("abs_err", "mean"), bias=("err", "mean"), coverage=("inside", "mean"))
    out = {"diag_by_season": d.groupby("season").agg(**agg).reset_index(),
           "diag_by_hour": d.groupby("hour").agg(**agg).reset_index()}
    d["decile_of_actual"] = pd.qcut(d.actual, 10, labels=False, duplicates="drop") + 1
    out["diag_by_level"] = d.groupby("decile_of_actual").agg(**agg, mean_actual=("actual", "mean"),
                                                              mean_pred=("pred", "mean")).reset_index()
    return out


def _group_importance_by_season(model, X, n_per=1500):
    rows = []
    for s_id, s_name in SEASON_NAMES.items():
        sub = X[X["season"] == s_id]
        if len(sub) < 200:
            continue
        sub = sub.sample(min(n_per, len(sub)), random_state=SEED)
        contrib = np.abs(model.predict(sub, pred_contrib=True)[:, :-1]).mean(0)
        g = pd.Series(contrib, index=X.columns).groupby(insights.feature_group).sum()
        for k, v in (g / g.sum() * 100).items():
            rows.append({"season": s_name, "group": k, "share_pct": float(v)})
    return pd.DataFrame(rows)


def _episode_model(sphi, imp, feats, steps, fast, out):
    (Xtr, ytr), (Xva, yva), (Xte, yte) = sphi["tr"], sphi["va"], sphi["te"]
    thr = float(ytr.quantile(EPISODE_QUANTILE))
    ctr, cva, cte = (ytr > thr).astype(int), (yva > thr).astype(int), (yte > thr).astype(int)
    clf = lgb.LGBMClassifier(n_estimators=300 if fast else 1500, learning_rate=0.04, num_leaves=31,
                             subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                             scale_pos_weight=(1 - ctr.mean()) / max(ctr.mean(), 1e-3),
                             random_state=SEED, verbosity=-1)
    clf.fit(Xtr, ctr, eval_set=[(Xva, cva)], callbacks=[lgb.early_stopping(50, verbose=False)])
    pv, pt = clf.predict_proba(Xva)[:, 1], clf.predict_proba(Xte)[:, 1]
    grid = np.linspace(0.05, 0.95, 91)
    best = grid[int(np.argmax([f1_score(cva, pv >= g) for g in grid]))]
    pers = (Xte["BC6_lag0"] > thr).astype(int)
    rows = []
    for nm, pred, score in [("LightGBM episode classifier", (pt >= best).astype(int), pt),
                            ("Persistence rule (BC now > thr)", pers.values, Xte["BC6_lag0"].values)]:
        rows.append({"Model": nm, "ROC_AUC": roc_auc_score(cte, score), "PR_AUC": average_precision_score(cte, score),
                     "Precision": precision_score(cte, pred, zero_division=0),
                     "Recall": recall_score(cte, pred), "F1": f1_score(cte, pred, zero_division=0),
                     "Threshold_ng_m3": thr, "Horizon": EPISODE_HORIZON})
    log(f"  episode F1={rows[0]['F1']:.3f} (persistence {rows[1]['F1']:.3f})  thr={thr:.0f} ng/m3")
    return {"table": pd.DataFrame(rows),
            "bundle": dict(model=clf, imputer=imp, features=feats, steps=steps, use_bc=True,
                           decision_threshold=float(best), bc_threshold=thr)}


def _loyo(X, y, fast):
    years = sorted(X.index.year.unique())
    years = [yr for yr in years if (X.index.year == yr).sum() > 2000]
    if len(years) < 2:
        log("  <2 usable years -> skipped")
        return None
    parts = []
    for yr in years:
        te = X.index.year == yr
        gap = ~((X.index >= pd.Timestamp(f"{yr}-01-01") - pd.Timedelta(days=1)) &
                (X.index < pd.Timestamp(f"{yr+1}-01-01") + pd.Timedelta(days=1)))
        trm = gap  # train on all other years (1-day buffer around the held-out year)
        imp = SimpleImputer(strategy="median", keep_empty_features=True).fit(X[trm])
        m = make_lgbm(True)
        m.set_params(n_estimators=250 if fast else 600)
        m.fit(imp.transform(X[trm]), y[trm])
        p = m.predict(imp.transform(X[te]))
        parts.append(pd.DataFrame({"actual": y[te].values, "pred": np.clip(p, 0, None), "year": yr}, index=X.index[te]))
        log(f"    held-out {yr}: R2={r2_score(y[te], p):.3f}")
    return pd.concat(parts)
