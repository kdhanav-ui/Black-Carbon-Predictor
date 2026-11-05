import React, { useState, useEffect } from 'react';
import { MetaData, ForecastResult } from '../types';
import { fetchForecast, fetchSampleRecent } from '../api';
import { LevelBadge } from '../components/LevelBadge';
import {
  TrendingUp,
  AlertTriangle,
  Upload,
  Clock,
  ShieldCheck,
  ShieldAlert,
  Sparkles,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';

interface Props {
  meta: MetaData;
}

export const ForecastView: React.FC<Props> = ({ meta }) => {
  const [result, setResult] = useState<ForecastResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [usingSample, setUsingSample] = useState(false);

  const loadSampleAndForecast = async () => {
    setLoading(true);
    setError(null);
    try {
      const sample = await fetchSampleRecent();
      const res = await fetchForecast(sample.records);
      setResult(res);
      setUsingSample(true);
    } catch (err: any) {
      setError(err.message || 'Forecast calculation failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSampleAndForecast();
  }, []);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    const reader = new FileReader();
    reader.onload = async (evt) => {
      try {
        const text = evt.target?.result as string;
        const lines = text.split('\n').filter((l) => l.trim().length > 0);
        const headers = lines[0].split(',').map((h) => h.trim());
        const records = lines.slice(1).map((line) => {
          const vals = line.split(',');
          const obj: Record<string, any> = {};
          headers.forEach((h, i) => {
            const val = vals[i]?.trim();
            obj[h] = val && !isNaN(Number(val)) ? Number(val) : val;
          });
          return obj;
        });
        const res = await fetchForecast(records);
        setResult(res);
        setUsingSample(false);
      } catch (err: any) {
        setError(err.message || 'Failed to parse and forecast CSV');
      } finally {
        setLoading(false);
      }
    };
    reader.readAsText(file);
  };

  // Prepare chart data combining recent history and future horizons
  const chartData: any[] = [];
  if (result) {
    (result.history_points || []).slice(-48).forEach((pt) => {
      chartData.push({
        time: pt.time.slice(5, 16),
        observed: pt.bc6,
        type: 'history',
      });
    });

    // Add forecast points
    Object.entries(result.horizons).forEach(([h, v]) => {
      chartData.push({
        time: `+${h}`,
        forecast: v.bc6_ng_m3,
        lo: v.interval_90[0],
        hi: v.interval_90[1],
        type: 'forecast',
      });
    });
  }

  const p90 = meta.bc_percentiles?.p90 || 11208;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-400 text-xs font-semibold mb-2">
              <TrendingUp className="w-3.5 h-3.5" />
              Multi-Horizon Predictive Center
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">15 Min to 24 Hour Forecasting & Early Warnings</h1>
            <p className="text-xs sm:text-sm text-slate-300">
              Real-time sequential multi-step forecast models with leak-free causal lag architecture and 6-hour severe
              smog episode sirens.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={loadSampleAndForecast}
              disabled={loading}
              className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition-all flex items-center gap-2"
            >
              <Clock className="w-4 h-4 text-cyan-400" />
              Load Recent Window
            </button>

            <label className="px-3.5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold transition-all cursor-pointer flex items-center gap-2 shadow-lg shadow-cyan-500/20">
              <Upload className="w-4 h-4" />
              Upload Time-Series CSV
              <input type="file" accept=".csv" onChange={handleFileUpload} className="hidden" />
            </label>
          </div>
        </div>

        {usingSample && (
          <div className="text-[11px] text-cyan-400 font-mono flex items-center gap-1.5 pt-1">
            <Sparkles className="w-3.5 h-3.5" />
            Loaded historical 15-min rolling validation sequence from Varanasi station.
          </div>
        )}
      </div>

      {loading && (
        <div className="glass-panel p-12 rounded-3xl flex flex-col items-center justify-center space-y-3">
          <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-slate-400">Computing 15m, 1h, 6h, and 24h horizons...</p>
        </div>
      )}

      {error && (
        <div className="glass-panel p-4 rounded-2xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {result && !loading && (
        <>
          {/* Episode Warning Siren Alert */}
          {result.episode_warning_6h && (
            <div
              className={`p-5 rounded-2xl border flex items-center gap-4 ${
                result.episode_warning_6h.warn
                  ? 'bg-rose-950/80 border-rose-600 text-rose-200 animate-pulse'
                  : 'bg-emerald-950/40 border-emerald-800/40 text-emerald-200'
              }`}
            >
              <div
                className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 ${
                  result.episode_warning_6h.warn ? 'bg-rose-600/30' : 'bg-emerald-600/30'
                }`}
              >
                {result.episode_warning_6h.warn ? (
                  <ShieldAlert className="w-6 h-6 text-rose-400" />
                ) : (
                  <ShieldCheck className="w-6 h-6 text-emerald-400" />
                )}
              </div>
              <div className="space-y-0.5">
                <span className="text-xs uppercase font-bold tracking-wider opacity-80">
                  6-Hour Episode Alert Status
                </span>
                <p className="text-sm font-semibold">
                  {result.episode_warning_6h.warn
                    ? `🚨 High Smog Risk: ${(result.episode_warning_6h.probability * 100).toFixed(0)}% probability of exceeding the severe episode threshold (${result.episode_warning_6h.threshold_ng_m3.toLocaleString()} ng/m³) within ~6 hours.`
                    : `Normal Outlook: Only ${(result.episode_warning_6h.probability * 100).toFixed(0)}% risk of severe episode within the next 6 hours.`}
                </p>
              </div>
            </div>
          )}

          {/* Horizon Metric Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(result.horizons).map(([h, v]) => (
              <div key={h} className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold uppercase text-cyan-400">+{h} Horizon</span>
                  <span className="text-[10px] text-slate-500 font-mono">{v.time.slice(11, 16)}</span>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-bold font-mono text-white tracking-tight">
                    {v.bc6_ng_m3.toLocaleString()}
                  </span>
                  <span className="text-xs font-mono text-slate-400">ng/m³</span>
                </div>
                <div className="flex items-center justify-between text-xs pt-1">
                  <span className={`font-mono font-semibold ${v.delta_vs_now >= 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {v.delta_vs_now >= 0 ? `+${v.delta_vs_now.toLocaleString()}` : v.delta_vs_now.toLocaleString()} vs now
                  </span>
                  <span className="text-[11px] px-2 py-0.5 rounded font-medium" style={{ backgroundColor: `${v.level.color}25`, color: v.level.color }}>
                    {v.level.label}
                  </span>
                </div>
                <div className="text-[10px] text-slate-500 font-mono">
                  90% Interval: {v.interval_90[0].toLocaleString()} – {v.interval_90[1].toLocaleString()}
                </div>
              </div>
            ))}
          </div>

          {/* Historical vs Forecast Chart */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-100">Observed History & Multi-Step Projections</h3>
                <p className="text-xs text-slate-400">
                  Last 48 hours of AE33 readings followed by 15m to 24h predictive horizon
                </p>
              </div>
              <div className="flex items-center gap-4 text-xs font-mono">
                <span className="flex items-center gap-1.5 text-slate-400">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" /> Observed History
                </span>
                <span className="flex items-center gap-1.5 text-rose-400 font-bold">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> Forecast
                </span>
              </div>
            </div>

            <div className="h-80 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#64748b" fontSize={11} label={{ value: 'BC₆ (ng/m³)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                    formatter={(val: any) => [`${Number(val).toLocaleString()} ng/m³`, 'Concentration']}
                  />
                  <ReferenceLine y={p90} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'P90 Severe Episode', fill: '#ef4444', fontSize: 10 }} />
                  <Line type="monotone" dataKey="observed" stroke="#06b6d4" strokeWidth={2} dot={false} connectNulls />
                  <Line type="monotone" dataKey="forecast" stroke="#ef4444" strokeWidth={3} strokeDasharray="3 3" dot={{ r: 4, fill: '#ef4444' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
