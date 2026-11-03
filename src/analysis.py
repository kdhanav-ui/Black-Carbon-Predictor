"""Seasonal / winter analysis tables and report figures."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .config import ARTIFACTS, SEASON_NAMES, TARGET

SEASON_ORDER = ["Winter", "Pre-monsoon", "Post-monsoon", "Monsoon"]
SEASON_COLORS = {"Winter": "#1f77b4", "Pre-monsoon": "#ff7f0e", "Post-monsoon": "#2ca02c", "Monsoon": "#d62728"}


def prepare_dirs(root):
    from pathlib import Path
    root = Path(root)
    d = {"root": root, "models": root / "models", "tables": root / "tables", "figures": root / "figures",
         "private": root.parent / "private_outputs"}
    for p in d.values():
        p.mkdir(parents=True, exist_ok=True)
    return d


def _m(g):
    return pd.Series({"N": len(g), "R2": r2_score(g.actual, g.pred),
                      "RMSE": float(np.sqrt(mean_squared_error(g.actual, g.pred))),
                      "MAE": mean_absolute_error(g.actual, g.pred),
                      "Mean_actual": g.actual.mean(), "Median_actual": g.actual.median()})


def seasonal_metrics(oof):
    t = oof.groupby("season").apply(_m, include_groups=False).reset_index()
    t["order"] = t["season"].map({s: i for i, s in enumerate(SEASON_ORDER)})
    return t.sort_values("order").drop(columns="order")


def yearly_metrics(oof):
    return oof.groupby("year").apply(_m, include_groups=False).reset_index()


def apportionment_tables(ap):
    a = ap.dropna(subset=["bb_fraction"]).copy()
    a["season"] = [SEASON_NAMES[s] for s in a.index.month.map(lambda m: 1 if m in (11, 12, 1, 2) else 2 if m in (3, 4, 5) else 3 if m in (6, 7, 8, 9) else 4)]
    a["hour"] = a.index.hour
    a["month"] = a.index.month
    diurnal = a.groupby(["season", "hour"]).agg(bb_fraction=("bb_fraction", "mean"), BC_bb=("BC_bb", "mean"),
                                                BC_ff=("BC_ff", "mean"), AAE=("AAE", "median")).reset_index()
    monthly = a.groupby("month").agg(bb_fraction=("bb_fraction", "mean"), BC_bb=("BC_bb", "mean"),
                                     BC_ff=("BC_ff", "mean"), AAE=("AAE", "median")).reset_index()
    return {"apportionment_diurnal": diurnal, "apportionment_monthly": monthly}


def winter_bb_share(ap):
    """Concentration-weighted biomass-burning share of winter BC."""
    w = ap[ap.index.month.isin([11, 12, 1, 2])].dropna(subset=["BC_bb", "BC_ff"])
    return float(w["BC_bb"].sum() / (w["BC_bb"].sum() + w["BC_ff"].sum())) if len(w) else None


def make_figures(tables, df, ap, fig_dir):
    # 1. virtual sensor leaderboard
    lb = tables["virtual_sensor_leaderboard"].sort_values("R2")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(lb["Model"], lb["R2"], color=plt.cm.viridis(np.linspace(0.2, 0.9, len(lb))))
    for i, v in enumerate(lb["R2"]):
        ax.text(max(v, 0) + 0.005, i, f"{v:.3f}", va="center", fontsize=8)
    ax.set_title("Virtual BC sensor (no BC history) - test R²"); ax.set_xlabel("R²")
    fig.tight_layout(); fig.savefig(fig_dir / "fig1_virtual_leaderboard.png", dpi=150); plt.close(fig)

    # 2. horizon degradation
    h = tables["forecast_horizons"]
    fig, ax = plt.subplots(figsize=(8, 5))
    for m, g in h.groupby("Model"):
        ax.plot(g["Horizon"], g["R2"], "o-", label=m)
    ax.set_title("Forecast skill vs horizon (test R²)"); ax.set_ylabel("R²"); ax.legend(fontsize=8); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(fig_dir / "fig2_horizon_skill.png", dpi=150); plt.close(fig)

    # 3. feature importance
    fi = tables["feature_importance_virtual"].head(20).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.barh(fi["feature"], fi["mean_abs_contribution"], color="#2a9d8f")
    ax.set_title("Top drivers of BC (virtual sensor, LightGBM contributions)")
    fig.tight_layout(); fig.savefig(fig_dir / "fig3_feature_importance.png", dpi=150); plt.close(fig)

    # 4. winter / seasonal panel
    d = df.dropna(subset=[TARGET]).copy()
    d["season"] = [SEASON_NAMES[1 if m in (11, 12, 1, 2) else 2 if m in (3, 4, 5) else 3 if m in (6, 7, 8, 9) else 4] for m in d.index.month]
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    for s in SEASON_ORDER:
        sub = d[d.season == s]
        if len(sub):
            axes[0][0].plot(*zip(*sub.groupby(sub.index.hour)[TARGET].median().items()), label=s, color=SEASON_COLORS[s], lw=2)
    axes[0][0].set(title="Diurnal BC6 by season (median)", xlabel="Hour", ylabel="ng/m³"); axes[0][0].legend()
    if ap is not None:
        a = ap.dropna(subset=["bb_fraction"]).copy()
        a["season"] = [SEASON_NAMES[1 if m in (11, 12, 1, 2) else 2 if m in (3, 4, 5) else 3 if m in (6, 7, 8, 9) else 4] for m in a.index.month]
        for s in SEASON_ORDER:
            sub = a[a.season == s]
            if len(sub):
                axes[0][1].plot(*zip(*sub.groupby(sub.index.hour)["bb_fraction"].mean().items()), label=s, color=SEASON_COLORS[s], lw=2)
        axes[0][1].set(title="Biomass-burning share of BC by hour", xlabel="Hour", ylabel="fraction"); axes[0][1].legend()
    else:
        axes[0][1].axis("off")
    if "seasonal_metrics_oof" in tables:
        sm = tables["seasonal_metrics_oof"]
        axes[1][0].bar(sm["season"], sm["R2"], color=[SEASON_COLORS[s] for s in sm["season"]])
        axes[1][0].set(title="Virtual-sensor R² by season (leave-one-year-out)", ylabel="R²")
    else:
        axes[1][0].axis("off")
    mon = d.groupby(d.index.month)[TARGET].mean()
    axes[1][1].bar(mon.index, mon.values, color=["#1f77b4" if m in (11, 12, 1, 2) else "#aec7e8" for m in mon.index])
    axes[1][1].set(title="Monthly mean BC6 (dark = winter)", xlabel="Month", ylabel="ng/m³")
    fig.tight_layout(); fig.savefig(fig_dir / "fig4_winter_seasonal.png", dpi=150); plt.close(fig)


def calibration_table(oof):
    """Predicted-vs-actual by prediction decile (aggregated, safe to publish)."""
    t = oof.copy()
    t["bin"] = pd.qcut(t.pred, 20, duplicates="drop")
    g = t.groupby("bin", observed=True).agg(mean_pred=("pred", "mean"), mean_actual=("actual", "mean"), n=("pred", "size")).reset_index(drop=True)
    return g
