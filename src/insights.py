"""Data-driven insight tables for the dashboard (all aggregated - no raw time series).

Every function degrades gracefully when a column is missing.
"""
import numpy as np
import pandas as pd

from .config import SEASON_NAMES, TARGET, season_of

# Approximate Lakshmi-puja dates (Diwali night). Verify against your own calendar if you rely on them.
DIWALI = {2021: "2021-11-04", 2022: "2022-10-24", 2023: "2023-11-12", 2024: "2024-11-01", 2025: "2025-10-20"}
WS_BINS = [0, 0.5, 1, 1.5, 2, 3, 5, 50]
GROUPS = ["Calendar", "Weather", "Combustion gases", "Particulates", "Other pollutants", "BC history"]


def feature_group(name: str) -> str:
    n = name.replace("log_", "")
    if name.startswith("BC6_"):
        return "BC history"
    if name.startswith(("hour_", "doy_", "dow_", "is_", "month", "season")):
        return "Calendar"
    if n.split("_")[0] in {"AT", "RH", "WS", "WD", "SR", "RF", "BP", "PBLH", "dew", "u", "v", "stagnation",
                           "stability", "rain", "ventilation", "fire"}:
        return "Weather"
    if n.split("_")[0] in {"PM25", "PM10", "PM"}:
        return "Particulates"
    if n.split("_")[0] in {"CO", "NO", "NO2", "NOX", "SO2"}:
        return "Combustion gases"
    return "Other pollutants"


def _prep(df):
    d = df.copy()
    d["season"] = [SEASON_NAMES[season_of(m)] for m in d.index.month]
    d["hour"], d["month"], d["dow"], d["year"] = d.index.hour, d.index.month, d.index.dayofweek, d.index.year
    return d


def find_episodes(bc: pd.Series, thr: float, min_steps=12):
    flag = (bc > thr).fillna(False)
    run = (flag != flag.shift()).cumsum()
    out = []
    for _, g in bc.groupby(run):
        if len(g) >= min_steps and (g > thr).all():
            out.append((g.index[0], g.index[-1]))
    return out


def build_all(df: pd.DataFrame, ap, thr90: float):
    d = _prep(df)
    v = d.dropna(subset=[TARGET])
    T, H = {}, []

    # ---- risk / profiles
    g = v.groupby(["month", "hour"])[TARGET]
    T["profile_hour_month"] = pd.DataFrame({"mean": g.mean(), "median": g.median(),
                                            "exceed_p90": g.apply(lambda s: (s > thr90).mean()), "n": g.size()}).reset_index()
    g = v.groupby(["dow", "hour"])[TARGET]
    T["profile_dow_hour"] = pd.DataFrame({"mean": g.mean(), "median": g.median(), "n": g.size()}).reset_index()
    g = v.groupby(["season", "hour"])[TARGET]
    T["profile_season_hour"] = pd.DataFrame({"mean": g.mean(), "median": g.median(),
                                             "p25": g.quantile(.25), "p75": g.quantile(.75)}).reset_index()

    # ---- yearly + winter-to-winter
    y = v.groupby("year")[TARGET].agg(mean="mean", median="median", p90=lambda s: s.quantile(.9), n="size").reset_index()
    T["yearly_stats"] = y
    w = v[v.month.isin([11, 12, 1, 2])].copy()
    w["winter"] = [f"{yr}-{str(yr+1)[2:]}" if m >= 11 else f"{yr-1}-{str(yr)[2:]}" for yr, m in zip(w.year, w.month)]
    ws = w.groupby("winter")[TARGET].agg(mean="mean", median="median", p90=lambda s: s.quantile(.9), n="size").reset_index()
    T["winter_by_year"] = ws[ws.n >= 500]

    # ---- stagnation (wind) and meteorology
    if "WS" in v:
        labels = ["0–0.5", "0.5–1", "1–1.5", "1.5–2", "2–3", "3–5", "5+"]
        t = v.assign(ws_bin=pd.cut(v["WS"], WS_BINS, labels=labels, include_lowest=True))
        we = t.groupby(["season", "ws_bin"], observed=True)[TARGET].agg(median="median", n="size").reset_index()
        we["ws_bin"] = we["ws_bin"].astype(str)
        T["wind_effect"] = we
    if {"AT", "RH"} <= set(v.columns):
        wv = v[v.season == "Winter"].dropna(subset=["AT", "RH"])
        if len(wv) > 500:
            tb = pd.qcut(wv["AT"], 7, duplicates="drop")
            rb = pd.qcut(wv["RH"], 5, duplicates="drop")
            m = wv.groupby([tb.rename("T_bin"), rb.rename("RH_bin")], observed=True)[TARGET].agg(median="median", n="size").reset_index()
            m["T_bin"], m["RH_bin"] = m["T_bin"].astype(str), m["RH_bin"].astype(str)
            T["winter_met_heatmap"] = m[m.n >= 30]

    # ---- BC share of PM2.5, BC/CO
    if "PM25" in v:
        r = v.dropna(subset=["PM25"])
        r = r[r.PM25 > 5].assign(bc_pm25_pct=lambda x: x[TARGET] / (x.PM25 * 1000) * 100)
        T["bc_share_pm25"] = r.groupby(["season", "hour"])["bc_pm25_pct"].median().reset_index()
    if "CO" in v:
        r = v.dropna(subset=["CO"])
        r = r[r.CO > 0.05].assign(bc_per_co=lambda x: x[TARGET] / x.CO)
        T["bc_co_ratio"] = r.groupby(["season", "hour"])["bc_per_co"].median().reset_index()

    # ---- correlations by season (Spearman)
    cols = [c for c in ["PM25", "PM10", "NO", "NO2", "NOX", "NH3", "SO2", "CO", "O3", "BENZENE", "AT", "RH", "WS", "SR", "BP", "PBLH", "fire_count"] if c in v]
    rows = []
    for s, gg in v.groupby("season"):
        for c in cols:
            x = gg[[c, TARGET]].dropna()
            if len(x) > 200:
                rows.append({"season": s, "variable": c, "spearman": x[c].corr(x[TARGET], method="spearman"), "n": len(x)})
    T["correlations_by_season"] = pd.DataFrame(rows)

    # ---- episodes
    eps = find_episodes(d[TARGET], thr90)
    erows = []
    for a, b in eps:
        seg = d.loc[a:b]
        r = {"start": a, "hours": len(seg) / 4, "peak": seg[TARGET].max(), "mean_bc": seg[TARGET].mean(),
             "onset_hour": a.hour, "month": a.month, "year": a.year, "season": SEASON_NAMES[season_of(a.month)]}
        for c in ["WS", "AT", "RH", "CO", "PM25"]:
            if c in seg:
                r[f"mean_{c}"] = seg[c].mean()
        erows.append(r)
    E = pd.DataFrame(erows)
    T["episode_catalog"] = E
    if len(E):
        comp = []
        for c in ["WS", "AT", "RH", "CO", "PM25"]:
            if f"mean_{c}" in E:
                base = d.groupby("season")[c].mean()
                for s, ge in E.groupby("season"):
                    comp.append({"variable": c, "season": s, "episode_mean": ge[f"mean_{c}"].mean(),
                                 "season_mean": base.get(s, np.nan), "n_episodes": len(ge)})
        T["episode_vs_baseline"] = pd.DataFrame(comp)
        steps = np.arange(-48, 97, 4)       # -12 h .. +24 h
        cb, cw = [], []
        for a, _ in eps:
            i = d.index.get_loc(a)
            if i + steps.min() >= 0 and i + steps.max() < len(d):
                cb.append(d[TARGET].iloc[i + steps].values)
                if "WS" in d:
                    cw.append(d["WS"].iloc[i + steps].values)
        if cb:
            T["episode_composite"] = pd.DataFrame({"hours_from_onset": steps / 4,
                                                   "bc_median": np.nanmedian(cb, axis=0),
                                                   "ws_median": np.nanmedian(cw, axis=0) if cw else np.nan,
                                                   "n": len(cb)})
        T["episode_calendar"] = E.groupby(["month"]).agg(episodes=("start", "size"), mean_hours=("hours", "mean")).reset_index()

    # ---- Diwali effect
    drows = []
    for yr, ds in DIWALI.items():
        t0 = pd.Timestamp(ds) + pd.Timedelta(hours=18)
        t1 = t0 + pd.Timedelta(hours=12)
        ev = d.loc[t0:t1, TARGET].dropna()
        base = []
        for off in list(range(-10, -2)) + list(range(3, 11)):
            seg = d.loc[t0 + pd.Timedelta(days=off):t1 + pd.Timedelta(days=off), TARGET].dropna()
            base.append(seg)
        base = pd.concat(base) if base else pd.Series(dtype=float)
        if len(ev) >= 20 and len(base) >= 100:
            drows.append({"year": yr, "date": ds, "event_mean": ev.mean(), "event_peak": ev.max(),
                          "baseline_mean": base.mean(), "ratio": ev.mean() / base.mean(), "n_event": len(ev)})
    T["diwali_effect"] = pd.DataFrame(drows)

    # ---- coverage (data quality)
    cov = d.groupby(["year", "month"])[TARGET].apply(lambda s: s.notna().mean()).reset_index(name="bc6_valid_fraction")
    T["coverage_monthly"] = cov
    miss = d.drop(columns=["season", "hour", "month", "dow", "year"]).isna().mean().reset_index()
    miss.columns = ["variable", "missing_fraction"]
    T["missingness"] = miss.sort_values("missing_fraction", ascending=False)

    # ---- source-apportionment extras
    if ap is not None:
        a = ap.join(d[["season", "hour", "month"] + [c for c in ["AT"] if c in d]]).dropna(subset=["bb_fraction"])
        if "AT" in a:
            a["T_bin"] = pd.qcut(a["AT"], 10, duplicates="drop").astype(str)
            T["bb_vs_temperature"] = a.groupby("T_bin").agg(bb_fraction=("bb_fraction", "mean"), AT=("AT", "mean"), n=("AT", "size")).reset_index().sort_values("AT")
        T["aae_by_season"] = a.groupby("season")["AAE"].describe()[["count", "25%", "50%", "75%"]].reset_index()

    # ---- headline insights (plain-language, numbers computed from the data)
    def med(s, h=None):
        x = v[v.season == s][TARGET]
        return x.median() if len(x) else np.nan
    mw, mm = med("Winter"), med("Monsoon")
    if np.isfinite(mw) and np.isfinite(mm) and mm > 0:
        H.append({"title": "Winter vs monsoon", "text": f"Median BC is {mw/mm:.1f}× higher in winter ({mw:,.0f} ng/m³) than in the monsoon ({mm:,.0f} ng/m³)."})
    sh = T["profile_season_hour"]
    if len(sh):
        w_ = sh[sh.season == "Winter"].set_index("hour")["median"]
        if len(w_):
            H.append({"title": "Worst hour in winter", "text": f"Winter BC peaks around {int(w_.idxmax()):02d}:00 (median {w_.max():,.0f} ng/m³) and is lowest around {int(w_.idxmin()):02d}:00 ({w_.min():,.0f})."})
    if "wind_effect" in T:
        we = T["wind_effect"][T["wind_effect"].season == "Winter"].dropna()
        we = we[we.n >= 100]
        if len(we) >= 2:
            lo, hi = we.iloc[0], we.iloc[-1]
            H.append({"title": "Stagnation effect (winter)", "text": f"On near-calm winter hours (wind {lo.ws_bin}) median BC is {lo['median']:,.0f} ng/m³ versus {hi['median']:,.0f} when wind is {hi.ws_bin} m/s."})
    if "bc_share_pm25" in T:
        b = T["bc_share_pm25"].groupby("season")["bc_pm25_pct"].median()
        if {"Winter", "Monsoon"} <= set(b.index):
            H.append({"title": "BC as a share of PM2.5", "text": f"BC makes up ~{b['Winter']:.1f}% of PM2.5 in winter versus ~{b['Monsoon']:.1f}% in the monsoon (median)."})
    if len(E):
        onset = E.onset_hour.mode().iloc[0]
        wshare = (E.season == "Winter").mean() * 100
        H.append({"title": "Pollution episodes", "text": f"{len(E)} episodes (BC above the site's top 10% for ≥3 h) were found; {wshare:.0f}% were in winter, median duration {E.hours.median():.1f} h, most often starting around {int(onset):02d}:00."})
    dw = T["diwali_effect"]
    if len(dw):
        H.append({"title": "Diwali night", "text": f"Evening-to-early-morning BC around Diwali was on average {dw.ratio.mean():.1f}× the surrounding days (range {dw.ratio.min():.1f}–{dw.ratio.max():.1f}×, {len(dw)} year(s) with data)."})
    wk = T["profile_dow_hour"].groupby("dow")["mean"].mean()
    if len(wk) == 7:
        H.append({"title": "Weekday vs weekend", "text": f"Weekend BC is {(wk[[5,6]].mean()/wk[[0,1,2,3,4]].mean()-1)*100:+.0f}% relative to weekdays on average."})
    wy = T["winter_by_year"]
    if len(wy) >= 2:
        H.append({"title": "Winter to winter", "text": f"Mean winter BC: " + ", ".join(f"{r.winter}: {r['mean']:,.0f}" for _, r in wy.iterrows()) + " ng/m³."})
    return {"tables": T, "headlines": H}
