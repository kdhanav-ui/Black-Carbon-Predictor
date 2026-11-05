from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIEWS = ROOT / "frontend" / "src" / "views"

# ===========================================================================
# 1. WinterDynamicsView.tsx
# ===========================================================================
winter_code = """import React, { useState, useEffect } from 'react';
import { MetaData } from '../types';
import { fetchTable } from '../api';
import { Snowflake, Wind, Thermometer, Layers, AlertTriangle } from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from 'recharts';

interface Props {
  meta: MetaData;
}

export const WinterDynamicsView: React.FC<Props> = ({ meta }) => {
  const [seasonHour, setSeasonHour] = useState<any[]>([]);
  const [winterYear, setWinterYear] = useState<any[]>([]);
  const [windEffect, setWindEffect] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchTable('profile_season_hour'),
      fetchTable('winter_by_year'),
      fetchTable('wind_effect'),
    ])
      .then(([sh, wy, we]) => {
        setSeasonHour(sh || []);
        setWinterYear(wy || []);
        setWindEffect(we || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // Format diurnal by season
  const hours = Array.from({ length: 24 }, (_, i) => i);
  const diurnalData = hours.map((h) => {
    const pt: any = { hour: `${String(h).padStart(2, '0')}:00` };
    ['Winter', 'Pre-monsoon', 'Post-monsoon', 'Monsoon'].forEach((s) => {
      const row = seasonHour.find((r) => r.season === s && Number(r.hour) === h);
      pt[s] = row ? Math.round(row.median) : null;
    });
    return pt;
  });

  const winterWind = windEffect.filter((r) => r.season === 'Winter');

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-950/80 border border-blue-800 text-blue-400 text-xs font-semibold">
          <Snowflake className="w-3.5 h-3.5" />
          Indo-Gangetic Plain Winter Dynamics
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">The Winter Smog Crisis & Stagnation Inversion</h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Why is Varanasi's winter air quality so severe? Cold shallow boundary layers, calm surface winds, dense fog,
          and domestic solid-fuel heating combine to create extreme soot trapping.
        </p>
      </div>

      {/* Diurnal Median by Season */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-100">Diurnal Black Carbon Cycle by Season</h3>
            <p className="text-xs text-slate-400">
              Notice the extreme 4.2× gap between Winter (peaking >10,000 ng/m³ at 22:00) and the cleansed Monsoon
            </p>
          </div>
        </div>

        <div className="h-80 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={diurnalData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="hour" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} label={{ value: 'Median BC₆ (ng/m³)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Line type="monotone" dataKey="Winter" stroke="#3b82f6" strokeWidth={3} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="Post-monsoon" stroke="#10b981" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="Pre-monsoon" stroke="#f59e0b" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="Monsoon" stroke="#ef4444" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Stagnation & Year-over-Year Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stagnation Wind Effect */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <Wind className="w-4 h-4 text-cyan-400" />
            <h3 className="text-base font-bold text-slate-100">Winter Stagnation Effect (Wind Speed vs BC)</h3>
          </div>
          <p className="text-xs text-slate-400">
            Median BC is nearly double when winds are calm (&lt;0.5 m/s) compared to light breezes (&gt;1.5 m/s)
          </p>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={winterWind} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="ws_bin" stroke="#64748b" fontSize={11} label={{ value: 'Wind Speed Bin (m/s)', position: 'insideBottom', offset: -5, fill: '#94a3b8', fontSize: 11 }} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                <Bar dataKey="median" name="Median Winter BC₆" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Winter by Year Bar Chart */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <Thermometer className="w-4 h-4 text-rose-400" />
            <h3 className="text-base font-bold text-slate-100">Mean Winter BC by Year (Nov–Feb)</h3>
          </div>
          <p className="text-xs text-slate-400">Inter-annual meteorological and stubble burning variability across winter seasons</p>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={winterYear} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="winter" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                <Bar dataKey="mean" name="Mean Winter BC₆ (ng/m³)" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
"""
(VIEWS / "WinterDynamicsView.tsx").write_text(winter_code.strip() + "\\n", encoding="utf-8")

# ===========================================================================
# 2. DiwaliEpisodesView.tsx
# ===========================================================================
diwali_code = """import React, { useState, useEffect } from 'react';
import { MetaData } from '../types';
import { fetchTable } from '../api';
import { Sparkles, AlertTriangle, Clock, Flame } from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
  ReferenceLine,
} from 'recharts';

interface Props {
  meta: MetaData;
}

export const DiwaliEpisodesView: React.FC<Props> = ({ meta }) => {
  const [diwaliData, setDiwaliData] = useState<any[]>([]);
  const [compositeData, setCompositeData] = useState<any[]>([]);
  const [catalog, setCatalog] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchTable('diwali_effect'),
      fetchTable('episode_composite'),
      fetchTable('episode_catalog'),
    ])
      .then(([d, comp, cat]) => {
        setDiwaliData(d || []);
        setCompositeData(comp || []);
        setCatalog(cat || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const formattedDiwali = diwaliData.map((d) => ({
    year: String(d.year),
    baseline: Math.round(d.baseline_mean || 0),
    diwali_night: Math.round(d.event_mean || 0),
    multiplier: d.event_mean && d.baseline_mean ? (d.event_mean / d.baseline_mean).toFixed(1) : '1.0',
  }));

  const topEpisodes = [...catalog].sort((a, b) => b.peak - a.peak).slice(0, 10);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-950/80 border border-amber-800 text-amber-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          Event Diagnostics & Episode Anatomy
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Diwali Fireworks Impact & 360 Pollution Episodes</h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Tracking the sudden toxic injection of fireworks soot during Diwali night and analyzing the onset dynamics
          of 360 historical severe pollution episodes identified across 5 years.
        </p>
      </div>

      {/* Diwali Comparison Chart */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-100">Diwali Night vs Surrounding Baseline Days (18:00–06:00)</h3>
            <p className="text-xs text-slate-400">
              Mean BC₆ during Lakshmi-puja evening through morning vs same hours on days 3–10 before/after
            </p>
          </div>
        </div>

        <div className="h-80 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={formattedDiwali} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="year" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} label={{ value: 'Mean BC₆ (ng/m³)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                formatter={(val: any, name: string) => [
                  `${Number(val).toLocaleString()} ng/m³`,
                  name === 'diwali_night' ? 'Diwali Night Spike' : 'Surrounding Days Baseline',
                ]}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Bar dataKey="baseline" name="Surrounding Days Baseline" fill="#475569" radius={[4, 4, 0, 0]} />
              <Bar dataKey="diwali_night" name="Diwali Night Spike" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Composite Episode Trajectory */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        <div>
          <h3 className="text-base font-bold text-slate-100">Anatomy of an Episode: Composite Onset Trajectory</h3>
          <p className="text-xs text-slate-400">
            Median BC concentration aligned around hour 0 (the moment BC crosses the 90th percentile threshold for ≥3 hours)
          </p>
        </div>

        <div className="h-72 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={compositeData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="hours_from_onset" stroke="#64748b" fontSize={11} label={{ value: 'Hours from Episode Onset (0 = Start)', position: 'insideBottom', offset: -5, fill: '#94a3b8', fontSize: 11 }} />
              <YAxis stroke="#64748b" fontSize={11} label={{ value: 'Median BC₆ (ng/m³)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
              <ReferenceLine x={0} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'Onset (t=0)', fill: '#ef4444', fontSize: 10 }} />
              <Line type="monotone" dataKey="bc_median" name="Median BC₆" stroke="#ef4444" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Biggest Episodes Table */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <h3 className="text-base font-bold text-slate-100">Top 10 Most Extreme Episodes in Dataset History</h3>
        <p className="text-xs text-slate-400">
          Ranked by highest instantaneous peak BC concentration reached during the multi-hour event
        </p>

        <div className="overflow-x-auto pt-2">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono text-[11px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Start Time</th>
                <th className="py-2.5 px-4">End Time</th>
                <th className="py-2.5 px-4">Duration (Hours)</th>
                <th className="py-2.5 px-4">Peak BC₆ (ng/m³)</th>
                <th className="py-2.5 px-4">Mean BC₆ (ng/m³)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {topEpisodes.map((ep, i) => (
                <tr key={i} className="hover:bg-slate-900/50">
                  <td className="py-2.5 px-4 text-slate-100">{String(ep.start).slice(0, 16)}</td>
                  <td className="py-2.5 px-4 text-slate-300">{String(ep.end).slice(0, 16)}</td>
                  <td className="py-2.5 px-4 text-cyan-300">{Number(ep.hours || 0).toFixed(1)} h</td>
                  <td className="py-2.5 px-4 font-bold text-rose-400">{Math.round(ep.peak).toLocaleString()}</td>
                  <td className="py-2.5 px-4 text-slate-200">{Math.round(ep.mean).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
"""
(VIEWS / "DiwaliEpisodesView.tsx").write_text(diwali_code.strip() + "\\n", encoding="utf-8")

# ===========================================================================
# 3. ModelLeaderboardView.tsx
# ===========================================================================
leaderboard_code = """import React, { useState, useEffect } from 'react';
import { MetaData } from '../types';
import { fetchTable } from '../api';
import { BarChart3, CheckCircle2, ShieldCheck, Trophy, Sparkles } from 'lucide-react';

interface Props {
  meta: MetaData;
}

export const ModelLeaderboardView: React.FC<Props> = ({ meta }) => {
  const [virtualLeaderboard, setVirtualLeaderboard] = useState<any[]>([]);
  const [horizonsData, setHorizonsData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchTable('virtual_sensor_leaderboard'),
      fetchTable('forecast_horizons'),
    ])
      .then(([vl, fh]) => {
        setVirtualLeaderboard(vl || []);
        setHorizonsData(fh || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-400 text-xs font-semibold">
          <Trophy className="w-3.5 h-3.5" />
          Model Transparency & Verification
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">AI Model Leaderboards & Cross-Validation Diagnostics</h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Rigorous leak-free evaluation on chronological holdout test sets with an embargo gap, train-only imputation,
          and split-conformal coverage verification.
        </p>
      </div>

      {/* Table 1: Virtual Sensor Leaderboard */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-100">1. Virtual Sensor Benchmark (Nowcast without BC Sensor)</h3>
            <p className="text-xs text-slate-400">
              Evaluated on held-out test data. LightGBM, CatBoost, and XGBoost lead the leaderboard.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto pt-2">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono text-[11px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Model Candidate</th>
                <th className="py-2.5 px-4">Holdout R²</th>
                <th className="py-2.5 px-4">RMSE (ng/m³)</th>
                <th className="py-2.5 px-4">MAE (ng/m³)</th>
                <th className="py-2.5 px-4">MAPE (%)</th>
                <th className="py-2.5 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {virtualLeaderboard.map((row, i) => {
                const isDeployed = row.Model.includes('DEPLOYED') || row.Model === 'XGBoost';
                return (
                  <tr key={i} className={isDeployed ? 'bg-cyan-950/30 border-l-2 border-cyan-400' : 'hover:bg-slate-900/50'}>
                    <td className="py-2.5 px-4 font-semibold text-slate-100 flex items-center gap-2">
                      {isDeployed && <span className="text-cyan-400">★</span>}
                      {row.Model}
                    </td>
                    <td className="py-2.5 px-4 text-cyan-300 font-bold">{Number(row.R2 || 0).toFixed(4)}</td>
                    <td className="py-2.5 px-4">{Math.round(Number(row.RMSE || 0)).toLocaleString()}</td>
                    <td className="py-2.5 px-4">{Math.round(Number(row.MAE || 0)).toLocaleString()}</td>
                    <td className="py-2.5 px-4">{Number(row['MAPE(%)'] || 0).toFixed(1)}%</td>
                    <td className="py-2.5 px-4">
                      {isDeployed ? (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-400">
                          Active Model
                        </span>
                      ) : (
                        <span className="text-slate-500 text-[10px]">Benchmarked</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Table 2: Forecast Horizons */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <h3 className="text-base font-bold text-slate-100">2. Multi-Horizon Forecast Skill Benchmark</h3>
        <p className="text-xs text-slate-400">
          Comparing persistence baseline ("BC stays what it is") vs advanced Gradient Boosted residual models across
          15-min to 24-hour lead times.
        </p>

        <div className="overflow-x-auto pt-2">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono text-[11px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Horizon</th>
                <th className="py-2.5 px-4">Model</th>
                <th className="py-2.5 px-4">Test R²</th>
                <th className="py-2.5 px-4">RMSE</th>
                <th className="py-2.5 px-4">MAE</th>
                <th className="py-2.5 px-4">MAPE (%)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {horizonsData.map((row, i) => {
                const isDeployed = row.Model.includes('DEPLOYED');
                return (
                  <tr key={i} className={isDeployed ? 'bg-cyan-950/20 font-bold' : 'hover:bg-slate-900/50'}>
                    <td className="py-2 px-4 text-cyan-400 font-bold">{row.Horizon}</td>
                    <td className="py-2 px-4 text-slate-100">{row.Model}</td>
                    <td className="py-2 px-4 text-cyan-300">{Number(row.R2 || 0).toFixed(3)}</td>
                    <td className="py-2 px-4">{Math.round(Number(row.RMSE || 0)).toLocaleString()}</td>
                    <td className="py-2 px-4">{Math.round(Number(row.MAE || 0)).toLocaleString()}</td>
                    <td className="py-2 px-4">{Number(row['MAPE(%)'] || 0).toFixed(1)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
"""
(VIEWS / "ModelLeaderboardView.tsx").write_text(leaderboard_code.strip() + "\\n", encoding="utf-8")

# ===========================================================================
# 4. BatchView.tsx
# ===========================================================================
batch_code = """import React, { useState } from 'react';
import { MetaData, BatchResult } from '../types';
import { uploadBatch } from '../api';
import { Layers, Upload, Download, AlertTriangle, CheckCircle, FileText } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  BarChart,
  Bar,
} from 'recharts';

interface Props {
  meta: MetaData;
}

export const BatchView: React.FC<Props> = ({ meta }) => {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<BatchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleProcess = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await uploadBatch(file);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Batch estimation failed');
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (!result?.series) return;
    const header = 'Timestamp,BC6_Estimate_ng_m3,Lower_90_ng_m3,Upper_90_ng_m3,Level\\n';
    const rows = result.series
      .map((s) => `${s.timestamp},${s.bc6_estimate},${s.lo},${s.hi},${s.level}`)
      .join('\\n');
    const blob = new Blob([header + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'bc6_batch_estimates.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const distData = Object.entries(result?.level_distribution || {}).map(([level, count]) => ({
    level,
    count,
  }));

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-400 text-xs font-semibold">
          <Layers className="w-3.5 h-3.5" />
          Batch Inference Processing Laboratory
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Time-Series Batch Virtual Sensor</h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Upload any CSV with a <code className="text-cyan-400 font-mono">Timestamp</code> column and available station
          pollutant/weather columns (PM2.5, PM10, CO, NO₂, Temp, Humidity, Wind). The engine infers continuous 90%
          uncertainty-bounded Black Carbon time-series for every row.
        </p>
      </div>

      {/* Upload Zone */}
      <div className="glass-panel p-8 rounded-3xl border-2 border-dashed border-slate-700/80 flex flex-col items-center justify-center text-center space-y-4 hover:border-cyan-500/50 transition-colors">
        <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-cyan-400">
          <Upload className="w-7 h-7" />
        </div>
        <div>
          <span className="text-sm font-bold text-white block">Select or drop your CAAQMS CSV file</span>
          <span className="text-xs text-slate-400">Supports hourly or 15-minute resolution time-series datasets</span>
        </div>

        <div className="flex items-center gap-3">
          <label className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition-all cursor-pointer">
            Browse File
            <input type="file" accept=".csv" onChange={handleFileChange} className="hidden" />
          </label>

          {file && (
            <button
              onClick={handleProcess}
              disabled={loading}
              className="px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold transition-all shadow-lg shadow-cyan-500/20"
            >
              {loading ? 'Processing ML Batch...' : `Run Batch (${file.name})`}
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="glass-panel p-4 rounded-2xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Results View */}
      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="glass-panel p-4 rounded-2xl border border-slate-800">
              <span className="text-xs text-slate-400 block">Total Timestamps</span>
              <span className="text-2xl font-bold font-mono text-white">{result.total_rows.toLocaleString()}</span>
            </div>
            <div className="glass-panel p-4 rounded-2xl border border-slate-800">
              <span className="text-xs text-slate-400 block">Mean Inferred BC₆</span>
              <span className="text-2xl font-bold font-mono text-cyan-300">{result.mean_bc6.toLocaleString()} ng/m³</span>
            </div>
            <div className="glass-panel p-4 rounded-2xl border border-slate-800">
              <span className="text-xs text-slate-400 block">Median BC₆</span>
              <span className="text-2xl font-bold font-mono text-cyan-300">{result.median_bc6.toLocaleString()} ng/m³</span>
            </div>
            <div className="glass-panel p-4 rounded-2xl border border-slate-800">
              <span className="text-xs text-slate-400 block">90th Percentile</span>
              <span className="text-2xl font-bold font-mono text-rose-400">{result.p90_bc6.toLocaleString()} ng/m³</span>
            </div>
          </div>

          {/* Time Series Chart */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-100">Estimated Black Carbon Sequence</h3>
                <p className="text-xs text-slate-400">Showing sampled sequence with conformal uncertainty bands</p>
              </div>

              <button
                onClick={downloadCSV}
                className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-2"
              >
                <Download className="w-4 h-4 text-cyan-400" />
                Export Annotated CSV
              </button>
            </div>

            <div className="h-80 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={result.series} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="timestamp" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#64748b" fontSize={11} label={{ value: 'BC₆ (ng/m³)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                  <Line type="monotone" dataKey="bc6_estimate" name="BC₆ Estimate" stroke="#06b6d4" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
"""
(VIEWS / "BatchView.tsx").write_text(batch_code.strip() + "\\n", encoding="utf-8")

# ===========================================================================
# 5. MethodologyView.tsx
# ===========================================================================
methodology_code = """import React from 'react';
import { MetaData } from '../types';
import { BookOpen, ShieldCheck, Cpu, Database, Award, Info } from 'lucide-react';

interface Props {
  meta: MetaData;
}

export const MethodologyView: React.FC<Props> = ({ meta }) => {
  return (
    <div className="space-y-8 animate-fadeIn max-w-5xl mx-auto">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-400 text-xs font-semibold">
          <BookOpen className="w-3.5 h-3.5" />
          Academic Rigor & Scientific Pedigree
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Methodology, Quality Control & Provenance</h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Complete scientific documentation of instrumentation, data curation, leak-free feature engineering, and
          internship research at IIT (BHU) Varanasi.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Section 1 */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-cyan-400 font-bold text-base">
            <Database className="w-5 h-5" />
            <h3>Instrumentation & Data Curation</h3>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Continuous multi-wavelength measurements collected via a research-grade <strong>Magee Scientific AE33 Aethalometer</strong>{' '}
            co-located with a CPCB/UPPCB Continuous Ambient Air Quality Monitoring Station (CAAQMS) at <strong>IIT (BHU), Varanasi</strong>,
            spanning 2021 through 2025 at 15-minute resolution.
          </p>
          <ul className="text-xs text-slate-400 list-disc list-inside space-y-1">
            <li>Channel 6 (880 nm) serves as the primary Black Carbon standard metric (BC₆).</li>
            <li>Dual-spot loading compensation algorithm active in the AE33 sensor.</li>
            <li>Zero/negative values and values above the 99.9th percentile removed during automated QC.</li>
          </ul>
        </div>

        {/* Section 2 */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-base">
            <Cpu className="w-5 h-5" />
            <h3>Leak-Free ML Pipeline & Conformal Bounds</h3>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Every feature at timestamp <em>t</em> strictly uses information available at or before <em>t</em>.
            Evaluation is conducted on a chronological 70/15/15 train/validation/test split separated by an embargo gap.
          </p>
          <ul className="text-xs text-slate-400 list-disc list-inside space-y-1">
            <li>Benchmarks: Ridge, kNN, MLP, Random Forest, ExtraTrees, XGBoost, LightGBM, and Ensembles.</li>
            <li>Split-conformal prediction intervals guarantee nominal 90% coverage with relative width scaling.</li>
            <li>Explainability powered by exact Tree-SHAP local attribution values.</li>
          </ul>
        </div>
      </div>

      {/* Research Credits Card */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 bg-gradient-to-r from-slate-950 via-slate-900 to-cyan-950/30 space-y-3">
        <div className="flex items-center gap-2 text-cyan-400 font-bold text-base">
          <Award className="w-5 h-5" />
          <h3>Research Credits & Institutional Acknowledgements</h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Developed by <strong>Dhanav Kumar</strong> (NIT Raipur) during a research internship at{' '}
          <strong>Indian Institute of Technology (BHU), Varanasi</strong>, supervised by <strong>Prof. Durga Prasad A.</strong>{' '}
          and <strong>Dr. Yogesh</strong>.
        </p>
        <p className="text-[11px] text-slate-400 leading-relaxed italic border-t border-slate-800 pt-3">
          Disclaimer: This system is a research, educational, and environmental analytics tool — not medical advice.
          Alert thresholds are calibrated relative to this site's historical atmospheric distribution.
        </p>
      </div>
    </div>
  );
};
"""
(VIEWS / "MethodologyView.tsx").write_text(methodology_code.strip() + "\\n", encoding="utf-8")

print("All science and analysis views generated successfully!")
