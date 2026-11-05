import React, { useState, useEffect } from 'react';
import { MetaData } from '../types';
import { fetchTable } from '../api';
import { Calendar, Clock, ShieldCheck, AlertTriangle, ArrowRight, Sun, Moon } from 'lucide-react';
import {
  ComposedChart,
  Bar,
  Line,
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

const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

export const PlanYourDayView: React.FC<Props> = ({ meta }) => {
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth() + 1);
  const [profileData, setProfileData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTable('profile_hour_month')
      .then((data) => {
        setProfileData(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const monthRows = profileData.filter((r) => Number(r.month) === selectedMonth).sort((a, b) => a.hour - b.hour);

  const chartData = monthRows.map((r) => ({
    hour: `${String(r.hour).padStart(2, '0')}:00`,
    median: Math.round(r.median),
    mean: Math.round(r.mean),
    exceed_p90_pct: Math.round(Number(r.exceed_p90 || 0) * 100),
  }));

  // Best 3 hours (lowest median) and Worst 3 hours (highest median)
  const sortedByMedian = [...monthRows].sort((a, b) => a.median - b.median);
  const bestHours = sortedByMedian.slice(0, 3).map((r) => `${String(r.hour).padStart(2, '0')}:00`);
  const worstHours = sortedByMedian.slice(-3).reverse().map((r) => `${String(r.hour).padStart(2, '0')}:00`);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-400 text-xs font-semibold mb-2">
              <Calendar className="w-3.5 h-3.5" />
              Diurnal Exposure Optimizer
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Plan Your Day: Optimal Outdoor Windows</h1>
            <p className="text-xs sm:text-sm text-slate-300">
              Schedule outdoor workouts, cycling, commutes, and school departures during the cleanest atmospheric
              dispersion windows.
            </p>
          </div>

          {/* Month Selector */}
          <div className="flex items-center gap-1.5 overflow-x-auto p-1 rounded-xl bg-slate-900 border border-slate-800">
            {MONTH_NAMES.map((m, idx) => (
              <button
                key={m}
                onClick={() => setSelectedMonth(idx + 1)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                  selectedMonth === idx + 1
                    ? 'bg-cyan-500 text-slate-950 font-bold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {m}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Cleanest vs Dirtiest Callout Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-emerald-800/40 bg-emerald-950/15 space-y-2">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
            <Sun className="w-4 h-4 text-emerald-400" />
            <span>Recommended Outdoor Exercise Window ({MONTH_NAMES[selectedMonth - 1]})</span>
          </div>
          <div className="flex items-baseline gap-3">
            <span className="text-2xl font-extrabold font-mono text-emerald-300">
              {bestHours.join(' · ')}
            </span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Atmospheric boundary layer height expands in the afternoon, maximizing ventilation and solar dilution of
            combustion soot. Safest window for running, sports, and outdoor activities.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-rose-800/40 bg-rose-950/15 space-y-2">
          <div className="flex items-center gap-2 text-rose-400 font-bold text-sm">
            <Moon className="w-4 h-4 text-rose-400" />
            <span>Hazardous Soot Accumulation Trap ({MONTH_NAMES[selectedMonth - 1]})</span>
          </div>
          <div className="flex items-baseline gap-3">
            <span className="text-2xl font-extrabold font-mono text-rose-400">
              {worstHours.join(' · ')}
            </span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Severe ground-level thermal inversions trap nighttime diesel transit and residential heating smoke near the
            surface. Keep windows closed and avoid strenuous exertion near roadways.
          </p>
        </div>
      </div>

      {/* Diurnal Profile Chart */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-100">
              Hour-by-Hour Profile: {MONTH_NAMES[selectedMonth - 1]}
            </h3>
            <p className="text-xs text-slate-400">
              Median Black Carbon concentration (bars, left axis) vs Percentage of time exceeding the P90 episode
              threshold (line, right axis)
            </p>
          </div>
        </div>

        <div className="h-80 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="hour" stroke="#64748b" fontSize={11} />
              <YAxis yAxisId="left" stroke="#06b6d4" fontSize={11} label={{ value: 'Median BC₆ (ng/m³)', angle: -90, position: 'insideLeft', fill: '#06b6d4', fontSize: 11 }} />
              <YAxis yAxisId="right" orientation="right" stroke="#f43f5e" fontSize={11} domain={[0, 100]} label={{ value: '% Time > P90', angle: 90, position: 'insideRight', fill: '#f43f5e', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                formatter={(val: any, name?: any) => [
                  name === 'median' ? `${Number(val).toLocaleString()} ng/m³` : `${val}%`,
                  name === 'median' ? 'Median BC₆' : 'P90 Episode Risk',
                ]}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Bar yAxisId="left" dataKey="median" name="Median BC₆ Concentration" fill="#06b6d4" opacity={0.85} radius={[4, 4, 0, 0]} />
              <Line yAxisId="right" type="monotone" dataKey="exceed_p90_pct" name="% Probability of Severe Episode (>P90)" stroke="#f43f5e" strokeWidth={3} dot={{ r: 3, fill: '#f43f5e' }} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
