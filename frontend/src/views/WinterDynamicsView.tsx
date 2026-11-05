import React, { useState, useEffect } from 'react';
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
              Notice the extreme 4.2× gap between Winter (peaking &gt;10,000 ng/m³ at 22:00) and the cleansed Monsoon
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
