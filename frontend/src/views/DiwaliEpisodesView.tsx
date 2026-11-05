import React, { useState, useEffect } from 'react';
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
                formatter={(val: any, name?: any) => [
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
