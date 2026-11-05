import React, { useState, useEffect } from 'react';
import { MetaData, LiveResult } from '../types';
import { fetchLive } from '../api';
import { LevelBadge } from '../components/LevelBadge';
import {
  Radio,
  RefreshCw,
  Wind,
  Thermometer,
  Droplets,
  AlertTriangle,
  Clock,
  Sparkles,
  Info,
} from 'lucide-react';
import {
  AreaChart,
  Area,
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

export const LiveOutlookView: React.FC<Props> = ({ meta }) => {
  const [data, setData] = useState<LiveResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadLive = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchLive();
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch live Varanasi data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLive();
  }, []);

  const chartData = (data?.forecast_points || []).map((pt) => ({
    time: pt.timestamp.slice(5, 16),
    estimate: pt.bc6_estimate,
    lo: pt.lo,
    hi: pt.hi,
    historical: pt.historical_median,
    temp: pt.temperature,
    rh: pt.humidity,
    ws: pt.wind_speed,
  }));

  const latestPoint = data?.forecast_points?.[0];
  const p90 = meta.bc_percentiles?.p90 || 11208;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-800 text-emerald-400 text-xs font-semibold mb-2">
              <Radio className="w-3.5 h-3.5 animate-pulse" />
              Real-Time Atmospheric Feed
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Live Varanasi Air Quality Sentinel</h1>
            <p className="text-xs sm:text-sm text-slate-300">
              Coupled Open-Meteo & Copernicus CAMS live atmospheric simulation calibrated against 5-year IIT BHU
              diurnal baseline.
            </p>
          </div>

          <button
            onClick={loadLive}
            disabled={loading}
            className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/20"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh Telemetry
          </button>
        </div>

        <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-800/40 text-[11px] text-amber-300/90 flex items-start gap-2">
          <Info className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
          <span>
            <strong>Scientific Transparency:</strong> Uses real-time Open-Meteo meteorological measurements + Copernicus
            Atmosphere Monitoring Service (CAMS) assimilation for Varanasi (25.32°N, 82.97°E). Compare the simulated
            curve against the historical median line to see if today is cleaner or dirtier than normal.
          </span>
        </div>
      </div>

      {loading && (
        <div className="glass-panel p-12 rounded-3xl flex flex-col items-center justify-center space-y-3">
          <div className="w-8 h-8 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-slate-400">Fetching live Varanasi weather and CAMS co-pollutants...</p>
        </div>
      )}

      {error && (
        <div className="glass-panel p-4 rounded-2xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {data && !loading && (
        <>
          {/* Current Observation Hero Cards */}
          {latestPoint && (
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
              <div className="glass-panel p-4 rounded-2xl border border-slate-800">
                <span className="text-[11px] text-slate-400 font-medium block">Current Estimated BC₆</span>
                <span className="text-xl font-bold font-mono text-cyan-300">
                  {latestPoint.bc6_estimate.toLocaleString()}
                </span>
                <span className="text-[10px] text-slate-500 block font-mono">ng/m³ (880nm)</span>
              </div>
              <div className="glass-panel p-4 rounded-2xl border border-slate-800">
                <span className="text-[11px] text-slate-400 font-medium block">Temperature</span>
                <span className="text-xl font-bold font-mono text-white">{latestPoint.temperature}°C</span>
                <span className="text-[10px] text-slate-500 block">Ambient 2m</span>
              </div>
              <div className="glass-panel p-4 rounded-2xl border border-slate-800">
                <span className="text-[11px] text-slate-400 font-medium block">Humidity</span>
                <span className="text-xl font-bold font-mono text-white">{latestPoint.humidity}%</span>
                <span className="text-[10px] text-slate-500 block">Relative Humidity</span>
              </div>
              <div className="glass-panel p-4 rounded-2xl border border-slate-800">
                <span className="text-[11px] text-slate-400 font-medium block">Wind Speed</span>
                <span className="text-xl font-bold font-mono text-white">{latestPoint.wind_speed} m/s</span>
                <span className="text-[10px] text-slate-500 block">10m Dispersion</span>
              </div>
              <div className="glass-panel p-4 rounded-2xl border border-slate-800">
                <span className="text-[11px] text-slate-400 font-medium block">CAMS PM2.5</span>
                <span className="text-xl font-bold font-mono text-white">{latestPoint.pm25}</span>
                <span className="text-[10px] text-slate-500 block">µg/m³</span>
              </div>
              <div className="glass-panel p-4 rounded-2xl border border-slate-800">
                <span className="text-[11px] text-slate-400 font-medium block">Current Level</span>
                <span className="text-base font-bold text-white font-mono mt-1 block">{latestPoint.level}</span>
                <span className="text-[10px] text-slate-500 block">Site Relative</span>
              </div>
            </div>
          )}

          {/* 48-Hour Live Outlook Chart */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h3 className="text-base font-bold text-slate-100">Next 48 Hours: Projected Soot Trend</h3>
                <p className="text-xs text-slate-400">
                  Real-time virtual sensor inference overlaid with 5-year historical site median for the same month & hour
                </p>
              </div>
              <div className="flex items-center gap-4 text-xs font-mono">
                <span className="flex items-center gap-1.5 text-orange-400 font-semibold">
                  <span className="w-2.5 h-2.5 rounded-full bg-orange-500" /> Projected BC₆
                </span>
                <span className="flex items-center gap-1.5 text-slate-400 font-semibold">
                  <span className="w-2.5 h-2.5 rounded-full bg-slate-500" /> 5-Yr IIT BHU Median
                </span>
              </div>
            </div>

            <div className="h-80 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#64748b" fontSize={11} label={{ value: 'BC₆ (ng/m³)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                    formatter={(val: any, name?: any) => [
                      `${Number(val).toLocaleString()} ng/m³`,
                      name === 'estimate' ? 'Projected BC₆' : '5-Yr Historical Median',
                    ]}
                  />
                  <ReferenceLine y={p90} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'P90 Severe Episode', fill: '#ef4444', fontSize: 10 }} />
                  <Area type="monotone" dataKey="hi" stroke="none" fill="#f97316" fillOpacity={0.08} />
                  <Area type="monotone" dataKey="lo" stroke="none" fill="#0a0e17" fillOpacity={1} />
                  <Line type="monotone" dataKey="historical" stroke="#64748b" strokeWidth={2} strokeDasharray="4 4" dot={false} />
                  <Line type="monotone" dataKey="estimate" stroke="#f97316" strokeWidth={3} dot={{ r: 3, fill: '#f97316' }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
