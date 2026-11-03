"""Black Carbon intelligence dashboard.   streamlit run app/dashboard.py"""
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import ARTIFACTS
from src.predict import Predictor

PRIVATE = ROOT / "private_outputs"          # raw-ish files; exist only on your own machine
SEASONS = ["Winter", "Pre-monsoon", "Post-monsoon", "Monsoon"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

st.set_page_config(page_title="Black Carbon Intelligence", page_icon="🌫️", layout="wide")


@st.cache_resource
def load():
    return Predictor(ARTIFACTS)


@st.cache_data
def T(name):
    p = ARTIFACTS / "tables" / f"{name}.csv"
    return pd.read_csv(p) if p.exists() else None


def show(fig, h=360):
    fig.update_layout(height=h, margin=dict(t=40, b=10, l=10, r=10))
    st.plotly_chart(fig)


def na(msg="Not available for this training run."):
    st.info(msg)


try:
    P = load()
except FileNotFoundError:
    st.error("No trained artifacts found. Run `python run_pipeline.py --data <file>` first (or `--demo`).")
    st.stop()
meta = P.meta
BCP = meta["bc_percentiles"]


def badge(level):
    st.markdown(f"<div style='padding:10px 16px;border-radius:10px;background:{level['color']};color:white;"
                f"font-weight:700;display:inline-block'>{level['label']}</div>", unsafe_allow_html=True)
    st.write(level["advice"])
    st.caption("Levels are relative to this site's historical BC distribution — there is no official BC standard.")


# =================================================================== pages
def page_overview():
    st.subheader("Overview")
    qc = meta["qc"]
    c = st.columns(5)
    c[0].metric("Valid BC₆ readings", f"{qc.get('bc6_valid_after_qc', 0):,}")
    c[1].metric("Median BC₆", f"{BCP['p50']:,.0f} ng/m³")
    c[2].metric("90th percentile", f"{BCP['p90']:,.0f} ng/m³")
    c[3].metric("99th percentile", f"{BCP['p99']:,.0f} ng/m³")
    ws = meta.get("apportionment", {}).get("winter_bb_share")
    c[4].metric("Winter BC from biomass", f"{ws*100:.0f}%" if ws is not None else "n/a")
    st.markdown("### Key findings (computed from the data)")
    ins = meta.get("insights", [])
    if ins:
        cols = st.columns(2)
        for i, it in enumerate(ins):
            with cols[i % 2]:
                st.markdown(f"**{it['title']}**  \n{it['text']}")
    else:
        na()
    sk = T("skill_vs_persistence")
    if sk is not None and len(sk):
        st.markdown("### How much do the models add over 'BC stays as it is'?")
        fig = go.Figure([go.Bar(x=sk.Horizon, y=sk.R2_persistence, name="Persistence"),
                         go.Bar(x=sk.Horizon, y=sk.R2_model, name="Deployed model")])
        fig.update_layout(barmode="group", yaxis_title="Test R²")
        show(fig, 320)
        st.dataframe(sk.round(3), hide_index=True)
    dm = meta.get("deployed_models", {})
    if dm:
        st.markdown("### Live models (selected by validation R²)")
        st.dataframe(pd.DataFrame({"Task": list(dm), "Model": list(dm.values())}), hide_index=True)


def page_estimate():
    st.subheader("Virtual BC sensor — no aethalometer needed")
    st.write("Enter whatever you have (e.g. from a CPCB/UPPCB station). Missing fields use typical values.")
    med = meta["feature_medians_virtual"]
    c1, c2, c3 = st.columns(3)
    with c1:
        pm25 = st.number_input("PM2.5 (µg/m³)", 0.0, 1000.0, float(round(med.get("PM25", 80), 1)))
        pm10 = st.number_input("PM10 (µg/m³)", 0.0, 1500.0, float(round(med.get("PM10", 150), 1)))
        co = st.number_input("CO (mg/m³)", 0.0, 20.0, float(round(med.get("CO", 1), 2)))
        no2 = st.number_input("NO₂ (µg/m³)", 0.0, 300.0, float(round(med.get("NO2", 30), 1)))
    with c2:
        no = st.number_input("NO (µg/m³)", 0.0, 300.0, float(round(med.get("NO", 8), 1)))
        so2 = st.number_input("SO₂ (µg/m³)", 0.0, 200.0, float(round(med.get("SO2", 10), 1)))
        o3 = st.number_input("Ozone (µg/m³)", 0.0, 300.0, float(round(med.get("O3", 35), 1)))
        nh3 = st.number_input("NH₃ (µg/m³)", 0.0, 200.0, float(round(med.get("NH3", 20), 1)))
    with c3:
        at = st.number_input("Temperature (°C)", -5.0, 50.0, float(round(med.get("AT", 25), 1)))
        rh = st.number_input("Relative humidity (%)", 0.0, 100.0, float(round(med.get("RH", 60), 1)))
        ws = st.number_input("Wind speed (m/s)", 0.0, 20.0, float(round(med.get("WS", 1.5), 2)))
        when = st.datetime_input("Time of observation", pd.Timestamp.now().floor("15min")) \
            if hasattr(st, "datetime_input") else pd.Timestamp.now()
    base = {"PM25": pm25, "PM10": pm10, "CO": co, "NO2": no2, "NO": no, "SO2": so2, "O3": o3, "NH3": nh3,
            "AT": at, "RH": rh, "WS": ws, "SR": med.get("SR"), "WD": med.get("WD"), "BP": med.get("BP")}
    if st.button("Estimate BC₆", type="primary"):
        r = P.estimate(base, when)
        a, b = st.columns([1, 2])
        a.metric("Estimated BC₆", f"{r['pred']:,.0f} ng/m³", help="880 nm channel")
        a.caption(f"{int(r['interval_nominal']*100)}% interval: {r['lo']:,.0f} – {r['hi']:,.0f} ng/m³")
        with b:
            badge(r["level"])
        fig = go.Figure(go.Bar(x=list(BCP), y=list(BCP.values()), marker_color="#bbb"))
        fig.add_hline(y=r["pred"], line_color="crimson", annotation_text="your estimate")
        fig.update_layout(title="Where this sits in the site's history (ng/m³)")
        show(fig, 280)
        st.caption("Single-reading estimates are rougher than the test scores suggest: rolling-average features "
                   "cannot use history here. Use **Batch estimate** with a time series for better accuracy.")
    with st.expander("🔬 What-if analysis (model sensitivity — correlational, not causal)"):
        st.write("Vary one input and see how the estimated BC responds, holding everything else as entered above.")
        labels = {"WS": "Wind speed (m/s)", "AT": "Temperature (°C)", "RH": "Humidity (%)", "PM25": "PM2.5", "CO": "CO", "NO2": "NO₂"}
        var = st.selectbox("Vary", list(labels), format_func=lambda k: labels[k])
        rng_ = {"WS": (0.1, 6), "AT": (2, 42), "RH": (15, 100), "PM25": (5, 400), "CO": (0.1, 5), "NO2": (3, 120)}[var]
        xs = np.linspace(*rng_, 30)
        ys = [P.estimate({**base, var: float(x)}, when)["pred"] for x in xs]
        fig = go.Figure(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="crimson", width=3)))
        fig.update_layout(xaxis_title=labels[var], yaxis_title="Estimated BC₆ (ng/m³)")
        show(fig, 320)
        st.write("**Emission-scenario proxy:** scale all combustion tracers (CO, NO, NO₂, SO₂, PM2.5, PM10) together.")
        f = np.linspace(0.3, 1.3, 21)
        yy = [P.estimate({**base, **{k: base[k] * s for k in ["CO", "NO", "NO2", "SO2", "PM25", "PM10"]}}, when)["pred"] for s in f]
        fig = go.Figure(go.Scatter(x=f * 100, y=yy, mode="lines", line=dict(color="#2a9d8f", width=3)))
        fig.update_layout(xaxis_title="Tracers as % of the values entered", yaxis_title="Estimated BC₆ (ng/m³)")
        show(fig, 300)
        st.caption("This shows what the *statistical model* associates with lower tracer levels — it is not a causal "
                   "estimate of what an emission cut would do.")


def page_batch():
    st.subheader("Batch estimate — turn a time series of station data into BC")
    st.write("Upload a CSV with a `Timestamp` column and any of: PM2.5, PM10, CO, NO, NO2, NOx, SO2, NH3, Ozone, "
             "Benzene, AT, RH, WS, WD, SR, BP (names like `PM2.5 (µg/m³)` work). Hourly or 15-min data both work.")
    up = st.file_uploader("CSV file", type="csv", key="batch")
    if up is None:
        return
    try:
        out = P.estimate_batch(pd.read_csv(up))
    except Exception as e:
        st.error(f"Could not process the file: {e}")
        return
    st.success(f"Estimated BC₆ for {len(out):,} timestamps.")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=out.index, y=out.hi, line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=out.index, y=out.lo, fill="tonexty", fillcolor="rgba(42,157,143,0.2)",
                             line=dict(width=0), name="90% interval"))
    fig.add_trace(go.Scatter(x=out.index, y=out.bc6_estimate, name="BC₆ estimate", line=dict(color="#2a9d8f")))
    fig.update_layout(yaxis_title="ng/m³")
    show(fig, 380)
    c = out.level.value_counts().reindex(["Low", "Moderate", "High", "Very high", "Extreme"]).fillna(0)
    show(px.bar(x=c.index, y=c.values, labels={"x": "Level", "y": "Timestamps"}, title="Time spent in each level"), 280)
    st.download_button("Download estimates (CSV)", out.to_csv().encode(), "bc6_estimates.csv")


def page_forecast():
    st.subheader("Forecast the next 15 min – 24 h and get an episode warning")
    st.write("Upload recent 15-minute data (≥ 24 h recommended) containing `Timestamp`, `BC6` and any pollutant / weather columns.")
    sample = PRIVATE / "sample_recent.csv"
    if sample.exists():
        st.download_button("Download a sample file", sample.read_bytes(), "sample_recent.csv")
    up = st.file_uploader("Recent data (CSV)", type="csv", key="fc")
    raw = pd.read_csv(up) if up else (pd.read_csv(sample) if sample.exists() else None)
    if raw is None:
        return
    if up is None:
        st.info("No file uploaded — using the local sample window.")
    try:
        r = P.forecast(raw)
    except Exception as e:
        st.error(f"Could not forecast: {e}")
        return
    ep = r["episode"]
    if ep:
        if ep["warn"]:
            st.error(f"🚨 Episode warning: {ep['probability']*100:.0f}% chance BC₆ exceeds {ep['threshold_ng_m3']:,.0f} ng/m³ (site's top 10%) in ~6 h.")
        else:
            st.success(f"No episode expected in ~6 h (probability {ep['probability']*100:.0f}%).")
    cols = st.columns(len(r["horizons"]))
    for col, (h, v) in zip(cols, r["horizons"].items()):
        col.metric(f"+{h}", f"{v['pred']:,.0f}", delta=f"{v['pred']-r['current_bc']:+,.0f} vs now")
        col.caption(f"{v['lo']:,.0f}–{v['hi']:,.0f} · {v['level']['label']}")
    fig = go.Figure()
    hist = r["history"]
    fig.add_trace(go.Scatter(x=hist.index, y=hist.values, name="observed BC₆", line=dict(color="steelblue")))
    xs = [r["issued_from"]] + [v["time"] for v in r["horizons"].values()]
    ys = [r["current_bc"]] + [v["pred"] for v in r["horizons"].values()]
    fig.add_trace(go.Scatter(x=xs, y=ys, name="forecast", mode="lines+markers", line=dict(color="crimson", dash="dot")))
    hi = [v["hi"] for v in r["horizons"].values()]
    lo = [v["lo"] for v in r["horizons"].values()]
    fig.add_trace(go.Scatter(x=xs[1:] + xs[1:][::-1], y=hi + lo[::-1], fill="toself", name="90% interval",
                             fillcolor="rgba(220,20,60,0.15)", line=dict(width=0)))
    fig.update_layout(yaxis_title="BC₆ (ng/m³)")
    show(fig, 380)
    badge(r["horizons"]["6h"]["level"])


def page_live():
    st.subheader("🌐 Live Varanasi outlook (beta)")
    st.warning("Uses free **model** air-quality/weather data (Open-Meteo / CAMS), not station measurements. NO, NOx, NH₃ and "
               "benzene are unavailable, and CAMS is known to be biased in the Indo-Gangetic Plain. Treat the shape of the curve "
               "(when it rises/falls) as indicative; absolute values may be off.")
    if st.button("Fetch latest data", type="primary"):
        try:
            from src import live
            w, a = live.fetch()
            raw = live.to_frame(w, a)
            out = P.estimate_batch(raw)
        except Exception as e:
            st.error(f"Could not fetch/process live data: {e}")
            return
        now = pd.Timestamp.now(tz="Asia/Kolkata").tz_localize(None).floor("h")
        prof = T("profile_hour_month")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=out.index, y=out.hi, line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=out.index, y=out.lo, fill="tonexty", fillcolor="rgba(231,111,81,0.2)", line=dict(width=0), name="90% interval"))
        fig.add_trace(go.Scatter(x=out.index, y=out.bc6_estimate, name="Indicative BC₆", line=dict(color="#e76f51", width=3)))
        if prof is not None:
            typ = [prof[(prof.month == t.month) & (prof.hour == t.hour)]["median"].mean() for t in out.index]
            fig.add_trace(go.Scatter(x=out.index, y=typ, name="Typical (median, same month & hour)", line=dict(color="#888", dash="dash")))
        fig.add_shape(type="line", x0=now, x1=now, y0=0, y1=1, yref="paper", line=dict(dash="dot"))
        fig.add_annotation(x=now, y=1, yref="paper", text="now", showarrow=False)
        fig.update_layout(yaxis_title="ng/m³")
        show(fig, 420)
        st.dataframe(out.round(0).tail(48))
        with st.expander("Inputs used"):
            st.dataframe(raw.tail(48))


def page_plan():
    st.subheader("🗓️ Plan your day — when is BC highest?")
    pr = T("profile_hour_month")
    if pr is None:
        return na()
    m = st.selectbox("Month", list(range(1, 13)), index=pd.Timestamp.now().month - 1, format_func=lambda i: MONTHS[i - 1])
    g = pr[pr.month == m].sort_values("hour")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=g.hour, y=g.exceed_p90 * 100, name="% of time in top-10% episodes", marker_color="#e76f51", yaxis="y2", opacity=.5))
    fig.add_trace(go.Scatter(x=g.hour, y=g["median"], name="Median BC₆", line=dict(color="#264653", width=3)))
    fig.update_layout(xaxis_title="Hour of day", yaxis_title="BC₆ (ng/m³)",
                      yaxis2=dict(overlaying="y", side="right", title="% time above P90", range=[0, 100]))
    show(fig, 380)
    best = g.nsmallest(3, "median").hour.tolist()
    worst = g.nlargest(3, "median").hour.tolist()
    c1, c2 = st.columns(2)
    c1.success("Cleanest hours (median): " + ", ".join(f"{h:02d}:00" for h in sorted(best)))
    c2.error("Dirtiest hours (median): " + ", ".join(f"{h:02d}:00" for h in sorted(worst)))
    st.caption("Plan outdoor exercise for the cleaner hours and away from busy roads. Based on historical patterns at this site.")
    hm = pr.pivot(index="month", columns="hour", values="exceed_p90") * 100
    hm.index = [MONTHS[i - 1] for i in hm.index]
    show(px.imshow(hm, aspect="auto", color_continuous_scale="YlOrRd", labels=dict(color="% time > P90", x="Hour", y=""),
                   title="Episode risk by month × hour"), 380)
    dh = T("profile_dow_hour")
    if dh is not None:
        h2 = dh.pivot(index="dow", columns="hour", values="mean")
        h2.index = [DAYS[i] for i in h2.index]
        show(px.imshow(h2, aspect="auto", color_continuous_scale="Magma_r", labels=dict(color="Mean BC₆"),
                       title="Mean BC₆ by weekday × hour"), 320)


def page_winter():
    st.subheader("❄️ Winter & seasons")
    sh = T("profile_season_hour")
    if sh is not None:
        sel = st.multiselect("Seasons", SEASONS, default=["Winter", "Monsoon"])
        fig = go.Figure()
        cols = {"Winter": "#1f77b4", "Pre-monsoon": "#ff7f0e", "Post-monsoon": "#2ca02c", "Monsoon": "#d62728"}
        for s in sel:
            g = sh[sh.season == s]
            fig.add_trace(go.Scatter(x=g.hour, y=g.p75, line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=g.hour, y=g.p25, fill="tonexty", line=dict(width=0), showlegend=False,
                                     fillcolor="rgba(150,150,150,0.15)"))
            fig.add_trace(go.Scatter(x=g.hour, y=g["median"], name=s, line=dict(color=cols[s], width=3)))
        fig.update_layout(xaxis_title="Hour", yaxis_title="BC₆ (ng/m³) — median and IQR")
        show(fig, 380)
    wy = T("winter_by_year")
    if wy is not None and len(wy):
        show(px.bar(wy, x="winter", y="mean", title="Mean winter BC₆ (Nov–Feb) by winter season", labels={"mean": "ng/m³"}), 300)
    we = T("wind_effect")
    if we is not None:
        s = st.selectbox("Wind effect — season", SEASONS, index=0)
        g = we[(we.season == s) & (we.n >= 50)]
        show(px.bar(g, x="ws_bin", y="median", title=f"Stagnation effect ({s}): median BC₆ by wind speed (m/s)"), 300)
    hm = T("winter_met_heatmap")
    if hm is not None and len(hm):
        pv = hm.pivot(index="T_bin", columns="RH_bin", values="median")
        show(px.imshow(pv, aspect="auto", color_continuous_scale="Blues", labels=dict(color="Median BC₆"),
                       title="Winter: BC₆ by temperature × humidity (cold & humid = fog/inversion regime)"), 380)
    sm, ym = T("seasonal_metrics_oof"), T("yearly_metrics_oof")
    if sm is not None:
        st.markdown("**Virtual-sensor skill on held-out years (leave-one-year-out)**")
        st.dataframe(sm.round(3), hide_index=True)
        if ym is not None:
            st.dataframe(ym.round(3), hide_index=True)
    cal = T("calibration_oof")
    if cal is not None:
        mx = float(max(cal.mean_pred.max(), cal.mean_actual.max()))
        fig = go.Figure(go.Scatter(x=cal.mean_pred, y=cal.mean_actual, mode="markers+lines", name="calibration"))
        fig.add_trace(go.Scatter(x=[0, mx], y=[0, mx], line=dict(color="red", dash="dash"), name="perfect"))
        fig.update_layout(xaxis_title="Mean predicted (per prediction-quantile)", yaxis_title="Mean actual",
                          title="Calibration (held-out years)")
        show(fig, 360)


def page_sources():
    st.subheader("🔥 Where does the black carbon come from?")
    if not meta.get("apportionment", {}).get("available"):
        return na("Source split needs the AE33 multi-wavelength columns (BC1…BC7) in the training data.")
    st.write("Aethalometer model (Sandradewi et al., 2008): 470 nm vs 950 nm absorption, AAE_fossil = 1, AAE_biomass = 2.")
    ws = meta["apportionment"].get("winter_bb_share")
    if ws is not None:
        st.metric("Winter BC attributed to biomass burning", f"{ws*100:.0f}%")
    di, mo = T("apportionment_diurnal"), T("apportionment_monthly")
    fig = go.Figure()
    for s, g in di.groupby("season"):
        fig.add_trace(go.Scatter(x=g.hour, y=g.bb_fraction, name=s, mode="lines"))
    fig.update_layout(xaxis_title="Hour", yaxis_title="Biomass fraction of BC", yaxis_range=[0, 1])
    show(fig, 340)
    fig = go.Figure([go.Bar(x=mo.month, y=mo.BC_ff, name="Fossil fuel"), go.Bar(x=mo.month, y=mo.BC_bb, name="Biomass burning")])
    fig.update_layout(barmode="stack", xaxis_title="Month", yaxis_title="Mean BC₆ (ng/m³)")
    show(fig, 320)
    bt = T("bb_vs_temperature")
    if bt is not None:
        show(px.line(bt, x="AT", y="bb_fraction", markers=True, title="Biomass share vs temperature (residential-heating signal?)",
                     labels={"AT": "Temperature (°C)", "bb_fraction": "Biomass fraction"}), 320)
    aae = T("aae_by_season")
    if aae is not None:
        st.markdown("**Absorption Ångström exponent by season** (≈1 fossil-dominated, ≈2 biomass-dominated)")
        st.dataframe(aae.round(2), hide_index=True)


def page_episodes():
    st.subheader("🌫️ Anatomy of pollution episodes")
    cat = T("episode_catalog")
    if cat is None or not len(cat):
        return na("No episodes found.")
    c = st.columns(4)
    c[0].metric("Episodes", f"{len(cat)}")
    c[1].metric("Median duration", f"{cat.hours.median():.1f} h")
    c[2].metric("Longest", f"{cat.hours.max():.0f} h")
    c[3].metric("Highest peak", f"{cat.peak.max():,.0f} ng/m³")
    st.caption(f"Episode = BC₆ above the site's 90th percentile ({BCP['p90']:,.0f} ng/m³) for at least 3 hours.")
    cal = T("episode_calendar")
    if cal is not None:
        cal = cal.assign(Month=[MONTHS[m - 1] for m in cal.month])
        show(px.bar(cal, x="Month", y="episodes", title="Episodes by month"), 280)
    show(px.histogram(cat, x="onset_hour", nbins=24, title="When do episodes start? (hour of day)"), 280)
    show(px.histogram(cat, x="hours", nbins=30, title="Episode duration (hours)"), 280)
    comp = T("episode_composite")
    if comp is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=comp.hours_from_onset, y=comp.bc_median, name="BC₆ (median)", line=dict(color="crimson", width=3)))
        if comp.ws_median.notna().any():
            fig.add_trace(go.Scatter(x=comp.hours_from_onset, y=comp.ws_median, name="Wind speed (m/s)", yaxis="y2", line=dict(color="steelblue")))
        fig.add_shape(type="line", x0=0, x1=0, y0=0, y1=1, yref="paper", line=dict(dash="dot"))
        fig.update_layout(xaxis_title="Hours from episode onset", yaxis_title="BC₆",
                          yaxis2=dict(overlaying="y", side="right", title="Wind (m/s)"),
                          title=f"Composite of {int(comp.n.iloc[0])} episodes — what happens around onset")
        show(fig, 380)
    vb = T("episode_vs_baseline")
    if vb is not None:
        vb = vb.assign(diff_pct=(vb.episode_mean / vb.season_mean - 1) * 100)
        st.markdown("**Weather/pollutants during episodes vs the season's average**")
        st.dataframe(vb.round(2), hide_index=True)
    st.markdown("**Biggest episodes**")
    st.dataframe(cat.sort_values("peak", ascending=False).head(15).round(1), hide_index=True)


def page_events():
    st.subheader("🎆 Diwali & festival effect")
    d = T("diwali_effect")
    if d is None or not len(d):
        return na("No Diwali nights with enough data in this dataset.")
    fig = go.Figure([go.Bar(x=d.year.astype(str), y=d.baseline_mean, name="Surrounding days"),
                     go.Bar(x=d.year.astype(str), y=d.event_mean, name="Diwali evening → morning")])
    fig.update_layout(barmode="group", yaxis_title="Mean BC₆ (ng/m³)")
    show(fig, 340)
    st.dataframe(d.round(2), hide_index=True)
    st.caption("Window: 18:00 on the Lakshmi-puja date to 06:00 next day, compared with the same clock window on days "
               "3–10 before/after. Dates are approximate (regional calendars differ by a day) — verify before citing.")


def page_drivers():
    st.subheader("🔬 What drives black carbon?")
    g = T("importance_groups_by_season")
    if g is not None and len(g):
        show(px.bar(g, x="season", y="share_pct", color="group", title="Share of model explanatory power by driver group and season",
                    category_orders={"season": SEASONS}, labels={"share_pct": "% of mean |contribution|"}), 380)
    fi = T("feature_importance_virtual")
    if fi is not None:
        top = fi.head(20).iloc[::-1]
        show(px.bar(top, x="mean_abs_contribution", y="feature", orientation="h", title="Top individual features (virtual sensor)"), 480)
    co = T("correlations_by_season")
    if co is not None and len(co):
        pv = co.pivot(index="variable", columns="season", values="spearman")
        pv = pv[[s for s in SEASONS if s in pv.columns]]
        show(px.imshow(pv, color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto", text_auto=".2f",
                       title="Spearman correlation with BC₆, by season"), 420)
    b = T("bc_share_pm25")
    if b is not None:
        show(px.line(b, x="hour", y="bc_pm25_pct", color="season", title="BC as % of PM2.5 (median) — how 'sooty' is the particulate load?",
                     category_orders={"season": SEASONS}), 340)
    r = T("bc_co_ratio")
    if r is not None:
        show(px.line(r, x="hour", y="bc_per_co", color="season", title="BC / CO ratio (ng m⁻³ per mg m⁻³) — combustion-efficiency proxy",
                     category_orders={"season": SEASONS}), 340)


def page_models():
    st.subheader("🏆 Models & diagnostics")
    st.write("All scores are on a held-out chronological test set with an embargo gap, train-only imputation and a regular 15-min grid.")
    st.markdown("**A · Virtual sensor** (pollutants + weather only). The row marked DEPLOYED is what the app uses.")
    st.dataframe(T("virtual_sensor_leaderboard").round(3), hide_index=True)
    st.markdown("**B · Forecast skill by horizon** (persistence = 'BC stays as it is now')")
    st.dataframe(T("forecast_horizons").round(3), hide_index=True)
    ep = T("episode_metrics")
    if ep is not None:
        st.markdown("**C · Episode warning (6 h)**")
        st.dataframe(ep.round(3), hide_index=True)
    vi = meta.get("virtual_interval", {})
    st.markdown(f"**Prediction intervals:** nominal {vi.get('nominal', 0)*100:.0f}% → empirical test coverage "
                f"**{vi.get('empirical_coverage', 0)*100:.1f}%** (split-conformal).")
    for name, title, x in [("diag_by_season", "Error & interval coverage by season", "season"),
                           ("diag_by_hour", "Error by hour of day", "hour"),
                           ("diag_by_level", "Bias by BC level (decile of actual) — are high values under-predicted?", "decile_of_actual")]:
        d = T(name)
        if d is not None:
            st.markdown(f"**{title}**")
            c1, c2 = st.columns(2)
            c1.plotly_chart(px.bar(d, x=x, y="bias", title="Bias (pred − actual, ng/m³)").update_layout(height=280, margin=dict(t=40, b=10)))
            c2.plotly_chart(px.bar(d, x=x, y="coverage", title="Interval coverage").update_layout(height=280, margin=dict(t=40, b=10)))


def page_data():
    st.subheader("🧾 Data quality & downloads")
    st.json(dict(meta["qc"]))
    cov = T("coverage_monthly")
    if cov is not None:
        pv = cov.pivot(index="year", columns="month", values="bc6_valid_fraction")
        pv.columns = [MONTHS[m - 1] for m in pv.columns]
        show(px.imshow(pv, aspect="auto", color_continuous_scale="Greens", zmin=0, zmax=1,
                       labels=dict(color="Valid fraction"), title="BC₆ data coverage by month"), 300)
    ms = T("missingness")
    if ms is not None:
        show(px.bar(ms.head(20), x="missing_fraction", y="variable", orientation="h", title="Missing fraction after QC"), 420)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in (ARTIFACTS / "tables").glob("*.csv"):
            z.write(p, f"tables/{p.name}")
        z.writestr("meta.json", json.dumps(meta, indent=2, default=str))
        z.writestr("key_findings.md", "# Key findings\n\n" + "\n".join(f"- **{i['title']}:** {i['text']}" for i in meta.get("insights", [])))
    st.download_button("⬇️ Download all result tables + key findings (ZIP)", buf.getvalue(), "bc6_results.zip")


def page_about():
    st.subheader("ℹ️ About & method")
    st.markdown("""
**Data.** AE33 aethalometer (880 nm channel = BC₆) plus co-located pollutant and meteorological records, IIT (BHU) Varanasi, 2021–2025, 15-min resolution.

**Method.** Regular 15-min grid → QC (BC ≤ 0 and > 99.9th percentile removed) → causal short-gap fill → leak-free feature engineering
(calendar, meteorology, ventilation, combustion tracers, rolling pollutant means; BC lags only for forecasts) → chronological 70/15/15 split with embargo →
benchmark of linear, kNN, MLP, tree ensembles, boosted trees, log-target and residual-to-persistence models → deployed model chosen by validation R² →
split-conformal intervals → leave-one-year-out CV for seasonal robustness.

**Source split.** Aethalometer model with AAE_ff = 1 and AAE_bb = 2.

**Limitations.** Single site; alert levels are relative to this site's history (no official BC standard); the source split depends on assumed AAE values;
intervals assume future conditions resemble the validation period; the live page uses modelled (not measured) inputs. Research tool — **not medical advice**.

**Credits.** Dhanav Kumar, NIT Raipur · Internship at IIT (BHU) Varanasi under Prof. Durga Prasad A. and Dr. Yogesh.
""")


# =================================================================== router
PAGES = {"🏠 Overview": page_overview, "🧪 Estimate now": page_estimate, "📦 Batch estimate": page_batch,
         "🔮 Forecast & warnings": page_forecast, "🌐 Live Varanasi (beta)": page_live, "🗓️ Plan your day": page_plan,
         "❄️ Winter & seasons": page_winter, "🔥 Sources": page_sources, "🌫️ Episodes": page_episodes,
         "🎆 Diwali & events": page_events, "🔬 Drivers": page_drivers, "🏆 Models & diagnostics": page_models,
         "🧾 Data & downloads": page_data, "ℹ️ About": page_about}

st.title("🌫️ Black Carbon Intelligence — Varanasi / Indo-Gangetic Plain")
st.caption("Virtual BC sensor · multi-horizon forecasts · episode warnings · source split · seasonal & event insights")
if "SYNTHETIC" in meta["data_source"].upper():
    st.warning("⚠️ These models were trained on **synthetic demo data**. Outputs are NOT real air-quality information.")
page = st.sidebar.radio("Explore", list(PAGES))
st.sidebar.markdown("---")
st.sidebar.caption(f"Trained: {meta['created'][:10]}  \nData: {meta['data_source'][:60]}")
dm = meta.get("deployed_models", {})
if dm:
    st.sidebar.caption("Live models (picked by validation R²):  \n" + "  \n".join(f"{k}: {v}" for k, v in dm.items()))
PAGES[page]()
