import React, { useState, useEffect } from 'react';
import { MetaData, WhatIfSweepResult, WhatIfScaleResult } from '../types';
import { sweepWhatIf, scaleWhatIf } from '../api';
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
import { Cpu, Sliders, TrendingDown, ArrowRight } from 'lucide-react';

interface Props {
  meta: MetaData;
}

const VARIABLES: Record<string, { label: string; min: number; max: number; unit: string }> = {
  CO: { label: 'Carbon Monoxide (CO)', min: 0.2, max: 5.0, unit: 'mg/m³' },
  WS: { label: 'Wind Speed (WS)', min: 0.1, max: 6.0, unit: 'm/s' },
  PM25: { label: 'PM2.5 Concentration', min: 10, max: 350, unit: 'µg/m³' },
  AT: { label: 'Ambient Temperature', min: 4, max: 42, unit: '°C' },
  RH: { label: 'Relative Humidity', min: 20, max: 98, unit: '%' },
  NO2: { label: 'Nitrogen Dioxide (NO₂)', min: 5, max: 120, unit: 'µg/m³' },
};

export const WhatIfView: React.FC<Props> = ({ meta }) => {
  const [selectedVar, setSelectedVar] = useState('CO');
  const [sweepData, setSweepData] = useState<{ x: number; y: number }[]>([]);
  const [scaleData, setScaleData] = useState<{ factor: string; y: number }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runSweep = async (varName: string) => {
    setLoading(true);
    const cfg = VARIABLES[varName];
    try {
      const res = await sweepWhatIf({}, varName, cfg.min, cfg.max, 25);
      const formatted = res.xs.map((x, i) => ({ x, y: res.ys[i] }));
      setSweepData(formatted);
      setError(null);
    } catch (e) {
      console.error(e);
      setSweepData([]);
      setError((e as Error).message || 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  const runScale = async () => {
    try {
      const res = await scaleWhatIf({}, [0.3, 0.5, 0.7, 0.85, 1.0, 1.15, 1.3]);
      const formatted = res.factors.map((f, i) => ({ factor: `${f}%`, y: res.ys[i] }));
      setScaleData(formatted);
    } catch (e) {
      console.error(e);
      setError((e as Error).message || 'Simulation failed');
    }
  };

  useEffect(() => {
    runSweep(selectedVar);
    runScale();
  }, [selectedVar]);

  const cfg = VARIABLES[selectedVar];
  const p90 = meta.bc_percentiles?.p90 || 11208;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-400 text-xs font-semibold">
          <Cpu className="w-3.5 h-3.5" />
          Interactive Sensitivity Studio
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">What-If Simulation Laboratory</h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Simulate environmental sensitivities and policy-driven emission interventions. Discover how Black Carbon
          responds to individual atmospheric drivers and collective combustion reductions.
        </p>
      </div>

      {error && (
        <div className="glass-panel p-4 rounded-2xl border border-rose-800/50 bg-rose-950/20 text-xs sm:text-sm text-rose-300">
          <strong className="text-rose-200">Simulation unavailable:</strong> {error}
        </div>
      )}

      {/* Simulator 1: Single Variable Sweep */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-slate-100">1. Individual Driver Sensitivity Sweep</h2>
            <p className="text-xs text-slate-400">
              Vary one parameter across its realistic range while holding all other inputs at their historical site medians.
            </p>
          </div>

          {/* Variable Selection Pills */}
          <div className="flex flex-wrap gap-2">
            {Object.entries(VARIABLES).map(([key, v]) => (
              <button
                key={key}
                onClick={() => setSelectedVar(key)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  selectedVar === key
                    ? 'bg-cyan-500 text-slate-950 font-bold shadow'
                    : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800'
                }`}
              >
                {key} ({v.unit})
              </button>
            ))}
          </div>
        </div>

        {/* Sweep Chart */}
        <div className="h-80 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={sweepData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="x" stroke="#64748b" fontSize={11} label={{ value: `${cfg.label} (${cfg.unit})`, position: 'insideBottom', offset: -5, fill: '#94a3b8', fontSize: 11 }} />
              <YAxis stroke="#64748b" fontSize={11} label={{ value: 'Estimated BC₆ (ng/m³)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                formatter={(val: any) => [`${Number(val).toLocaleString()} ng/m³`, 'Estimated BC₆']}
                labelFormatter={(val) => `${cfg.label}: ${val} ${cfg.unit}`}
              />
              <ReferenceLine y={p90} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'P90 Severe Episode', fill: '#ef4444', fontSize: 10 }} />
              <Line type="monotone" dataKey="y" stroke="#06b6d4" strokeWidth={3} dot={{ r: 3, fill: '#06b6d4' }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Simulator 2: Emission Scenario Scaling */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        <div>
          <div className="flex items-center gap-2">
            <TrendingDown className="w-4 h-4 text-emerald-400" />
            <h2 className="text-base font-bold text-slate-100">2. Collective Combustion Emission Reduction Scenario</h2>
          </div>
          <p className="text-xs text-slate-400">
            Simulate a policy intervention where all primary combustion markers (CO, NO, NO₂, SO₂, PM2.5, PM10) are
            scaled together (e.g. strict vehicle bans or reduced biomass burning).
          </p>
        </div>

        <div className="h-80 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={scaleData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="factor" stroke="#64748b" fontSize={11} label={{ value: '% of Typical Combustion Emissions', position: 'insideBottom', offset: -5, fill: '#94a3b8', fontSize: 11 }} />
              <YAxis stroke="#64748b" fontSize={11} label={{ value: 'Estimated BC₆ (ng/m³)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                formatter={(val: any) => [`${Number(val).toLocaleString()} ng/m³`, 'Estimated BC₆']}
              />
              <ReferenceLine x="100%" stroke="#e2e8f0" strokeDasharray="2 2" label={{ value: 'Current Baseline', fill: '#e2e8f0', fontSize: 10 }} />
              <Line type="monotone" dataKey="y" stroke="#10b981" strokeWidth={3} dot={{ r: 4, fill: '#10b981' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed italic">
          * Note: This illustrates what the statistical machine learning model associates with lower tracer levels. It
          reflects atmospheric correlation rather than an unconstrained chemical-transport causal model.
        </p>
      </div>
    </div>
  );
};
