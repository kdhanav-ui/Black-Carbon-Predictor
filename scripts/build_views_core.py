from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIEWS = ROOT / "frontend" / "src" / "views"

# ===========================================================================
# 1. OverviewView.tsx
# ===========================================================================
overview_code = """import React, { useEffect, useState } from 'react';
import { MetaData, ViewType } from '../types';
import { MetricCard } from '../components/MetricCard';
import { fetchTable } from '../api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import {
  Activity,
  Flame,
  Snowflake,
  Wind,
  Sparkles,
  ArrowRight,
  Sliders,
  TrendingUp,
  Radio,
  CheckCircle2,
} from 'lucide-react';

interface Props {
  meta: MetaData;
  onNavigate: (view: ViewType) => void;
}

export const OverviewView: React.FC<Props> = ({ meta, onNavigate }) => {
  const [skillData, setSkillData] = useState<any[]>([]);
  const [loadingSkill, setLoadingSkill] = useState(true);

  useEffect(() => {
    fetchTable('skill_vs_persistence')
      .then((data) => {
        setSkillData(data);
        setLoadingSkill(false);
      })
      .catch(() => setLoadingSkill(false));
  }, []);

  const qc = meta.qc || {};
  const p = meta.bc_percentiles || { p25: 1479, p50: 3041, p75: 6481, p90: 11208, p95: 14903, p99: 24685 };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Welcome */}
      <div className="glass-panel-elevated p-6 sm:p-8 rounded-3xl relative overflow-hidden border border-cyan-500/20 bg-gradient-to-r from-slate-950 via-slate-900 to-cyan-950/40">
        <div className="max-w-3xl space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-700/50 text-cyan-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            Varanasi / Indo-Gangetic Plain · IIT (BHU)
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Black Carbon Intelligence Platform
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            High-precision virtual Aethalometer sensor, multi-horizon forecasting (15m–24h), severe episode early
            warning radar, and deep chemical physics source apportionment on 5 years of continuous AE33 records.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <button
              onClick={() => onNavigate('virtual_sensor')}
              className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs sm:text-sm flex items-center gap-2 transition-all shadow-lg shadow-cyan-500/25"
            >
              <Sliders className="w-4 h-4" />
              Estimate BC (Virtual Sensor)
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onNavigate('forecast')}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-100 font-semibold text-xs sm:text-sm flex items-center gap-2 transition-all border border-slate-700"
            >
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              Forecast Horizons
            </button>
            <button
              onClick={() => onNavigate('live_sentinel')}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-100 font-semibold text-xs sm:text-sm flex items-center gap-2 transition-all border border-slate-700"
            >
              <Radio className="w-4 h-4 text-emerald-400" />
              Live Varanasi Feed
            </button>
          </div>
        </div>
        <div className="absolute right-0 top-0 bottom-0 w-1/3 opacity-15 pointer-events-none bg-gradient-to-l from-cyan-400 to-transparent blur-3xl" />
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Valid AE33 Readings"
          value={(qc.bc6_valid_after_qc || 123643).toLocaleString()}
          subtitle="15-min continuous grid"
          icon={<Activity className="w-4 h-4" />}
          trend="QC Verified (100%)"
        />
        <MetricCard
          title="Site Median (P50)"
          value={`${p.p50?.toLocaleString() || '3,041'}`}
          badge="ng/m³"
          subtitle="Typical ambient level"
          icon={<Activity className="w-4 h-4" />}
        />
        <MetricCard
          title="90th Percentile (P90)"
          value={`${p.p90?.toLocaleString() || '11,208'}`}
          badge="ng/m³"
          subtitle="Top 10% severe episodes"
          icon={<Flame className="w-4 h-4 text-amber-400" />}
        />
        <MetricCard
          title="99th Percentile (P99)"
          value={`${Math.round(p.p99 || 24685).toLocaleString()}`}
          badge="ng/m³"
          subtitle="Extreme winter peaks"
          icon={<Flame className="w-4 h-4 text-rose-500" />}
        />
        <MetricCard
          title="Winter Biomass Share"
          value="~64%"
          subtitle="Aethalometer dual-wave split"
          icon={<Snowflake className="w-4 h-4 text-blue-400" />}
          trend="Woodsmoke & heating"
        />
      </div>

      {/* Key Findings Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-100 tracking-tight">Key Data-Driven Insights</h2>
            <p className="text-xs text-slate-400">Derived from 5 years of continuous AE33 measurements at IIT (BHU)</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {(meta.insights || []).map((it, idx) => (
            <div
              key={idx}
              className="glass-panel p-5 rounded-2xl border border-slate-800/80 hover:border-cyan-500/30 transition-all space-y-2 group"
            >
              <div className="flex items-center gap-2 text-cyan-400 font-semibold text-sm">
                <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
                <span>{it.title}</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{it.text}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Persistence vs Model Benchmark */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-6 rounded-3xl border border-slate-800/80 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-100">Model Skill vs Persistence Benchmark</h3>
              <p className="text-xs text-slate-400">
                How much predictive accuracy does ML add over assuming "BC remains what it is right now"?
              </p>
            </div>
            <span className="text-xs px-2.5 py-1 rounded-full bg-cyan-950 border border-cyan-800 text-cyan-300 font-mono">
              Test R² Score
            </span>
          </div>

          <div className="h-72 w-full pt-4">
            {loadingSkill ? (
              <div className="h-full flex items-center justify-center text-slate-500 text-xs">Loading benchmark...</div>
            ) : skillData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={skillData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="Horizon" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} domain={[-0.2, 1.0]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                    itemStyle={{ fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                  <Bar dataKey="R2_persistence" name="Persistence Baseline" fill="#475569" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="R2_model" name="Deployed ML Model" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500 text-xs">Benchmark data ready</div>
            )}
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed italic">
            * At 15m, persistence is already high (~0.91), but by 6h and 24h, persistence collapses (R² drops to -0.13),
            whereas the trained ML models retain strong predictive power (R² 0.59 at 6h, 0.50 at 24h).
          </p>
        </div>

        {/* Deployed Architecture Summary */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800/80 space-y-4">
          <h3 className="text-base font-bold text-slate-100">Live Production Models</h3>
          <p className="text-xs text-slate-400">Chosen automatically by out-of-fold validation R²</p>
          <div className="space-y-3 pt-2">
            {Object.entries(meta.deployed_models || {}).map(([task, modelName]) => (
              <div key={task} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs uppercase font-mono text-cyan-400 font-bold block">{task}</span>
                  <span className="text-xs text-slate-300 font-medium">{modelName}</span>
                </div>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-400">
                  Active
                </span>
              </div>
            ))}
          </div>

          <div className="p-4 rounded-2xl bg-cyan-950/30 border border-cyan-800/40 text-xs text-slate-300 space-y-1.5">
            <span className="font-semibold text-cyan-300 block">Conformal Guarantee</span>
            <p className="text-[11px] text-slate-400">
              Split-conformal prediction intervals guarantee nominal 90% coverage with empirical validation test
              coverage of{' '}
              <strong className="text-cyan-400">
                {(meta.virtual_interval?.empirical_coverage * 100).toFixed(1)}%
              </strong>
              .
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
"""
(VIEWS / "OverviewView.tsx").write_text(overview_code.strip() + "\\n", encoding="utf-8")

# ===========================================================================
# 2. VirtualSensorView.tsx
# ===========================================================================
virtual_sensor_code = """import React, { useState, useEffect } from 'react';
import { MetaData, EstimateResult } from '../types';
import { estimateBC } from '../api';
import { LevelBadge } from '../components/LevelBadge';
import {
  Sliders,
  Sparkles,
  AlertCircle,
  HelpCircle,
  BarChart2,
  CheckCircle,
  Gauge,
  Thermometer,
  Wind,
  Droplets,
  CloudRain,
  Flame,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  CartesianGrid,
} from 'recharts';

interface Props {
  meta: MetaData;
}

export const VirtualSensorView: React.FC<Props> = ({ meta }) => {
  const med = meta.feature_medians_virtual || {};

  const [inputs, setInputs] = useState<Record<string, number>>({
    PM25: Number(med.PM25 || 80),
    PM10: Number(med.PM10 || 150),
    CO: Number(med.CO || 1.2),
    NO2: Number(med.NO2 || 30),
    NO: Number(med.NO || 8),
    SO2: Number(med.SO2 || 10),
    O3: Number(med.O3 || 35),
    NH3: Number(med.NH3 || 20),
    AT: Number(med.AT || 25),
    RH: Number(med.RH || 60),
    WS: Number(med.WS || 1.5),
    WD: Number(med.WD || 180),
    SR: Number(med.SR || 5.0),
    BP: Number(med.BP || 750),
  });

  const [result, setResult] = useState<EstimateResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runEstimate = async (customInputs?: Record<string, number>) => {
    setLoading(true);
    setError(null);
    try {
      const data = await estimateBC(customInputs || inputs, null, true);
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Failed to estimate');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runEstimate();
  }, []);

  const handleSliderChange = (key: string, val: number) => {
    setInputs((prev) => ({ ...prev, [key]: val }));
  };

  // 1-Click Real World Presets
  const applyPreset = (preset: 'winter_smog' | 'monsoon_clean' | 'traffic_peak' | 'post_harvest') => {
    let p: Record<string, number> = {};
    if (preset === 'winter_smog') {
      p = { PM25: 240, PM10: 380, CO: 2.8, NO2: 65, NO: 25, SO2: 18, O3: 15, NH3: 35, AT: 11, RH: 88, WS: 0.4, WD: 310, SR: 2.0, BP: 755 };
    } else if (preset === 'monsoon_clean') {
      p = { PM25: 22, PM10: 45, CO: 0.4, NO2: 12, NO: 3, SO2: 5, O3: 20, NH3: 8, AT: 31, RH: 75, WS: 3.2, WD: 140, SR: 12.0, BP: 742 };
    } else if (preset === 'traffic_peak') {
      p = { PM25: 110, PM10: 190, CO: 1.9, NO2: 55, NO: 30, SO2: 12, O3: 32, NH3: 18, AT: 22, RH: 55, WS: 0.9, WD: 200, SR: 4.0, BP: 748 };
    } else {
      p = { PM25: 175, PM10: 290, CO: 2.2, NO2: 42, NO: 15, SO2: 15, O3: 25, NH3: 28, AT: 17, RH: 70, WS: 0.6, WD: 290, SR: 5.0, BP: 750 };
    }
    setInputs((prev) => ({ ...prev, ...p }));
    runEstimate(p);
  };

  const p90 = meta.bc_percentiles?.p90 || 11208;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-2">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-400 text-xs font-semibold mb-2">
              <Sliders className="w-3.5 h-3.5" />
              Virtual Sensor Studio
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Instant Black Carbon Estimator</h1>
            <p className="text-xs sm:text-sm text-slate-300">
              Infer ambient Black Carbon (BC₆) concentrations using standard regulatory CAAQMS gas and weather inputs.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs text-slate-400 font-medium mr-1">Presets:</span>
            <button
              onClick={() => applyPreset('winter_smog')}
              className="px-3 py-1.5 rounded-lg bg-blue-950/60 hover:bg-blue-900 border border-blue-700/50 text-blue-300 text-xs font-medium transition-colors"
            >
              ❄️ Winter Smog
            </button>
            <button
              onClick={() => applyPreset('traffic_peak')}
              className="px-3 py-1.5 rounded-lg bg-amber-950/60 hover:bg-amber-900 border border-amber-700/50 text-amber-300 text-xs font-medium transition-colors"
            >
              🚗 Rush Hour
            </button>
            <button
              onClick={() => applyPreset('post_harvest')}
              className="px-3 py-1.5 rounded-lg bg-rose-950/60 hover:bg-rose-900 border border-rose-700/50 text-rose-300 text-xs font-medium transition-colors"
            >
              🌾 Biomass Peak
            </button>
            <button
              onClick={() => applyPreset('monsoon_clean')}
              className="px-3 py-1.5 rounded-lg bg-emerald-950/60 hover:bg-emerald-900 border border-emerald-700/50 text-emerald-300 text-xs font-medium transition-colors"
            >
              🌧️ Clean Monsoon
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Controls vs Results */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Parameters (7 cols) */}
        <div className="lg:col-span-7 space-y-5">
          {/* Group 1: Core Particulates & Combustion */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 text-cyan-400 text-sm font-semibold border-b border-slate-800 pb-2">
              <Flame className="w-4 h-4" />
              <span>Primary Combustion Tracers & Particulates</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div>
                <div className="flex justify-between text-slate-300 font-medium mb-1">
                  <span>PM2.5 (µg/m³)</span>
                  <span className="font-mono text-cyan-300 font-bold">{inputs.PM25}</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="500"
                  step="1"
                  value={inputs.PM25}
                  onChange={(e) => handleSliderChange('PM25', Number(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-slate-300 font-medium mb-1">
                  <span>PM10 (µg/m³)</span>
                  <span className="font-mono text-cyan-300 font-bold">{inputs.PM10}</span>
                </div>
                <input
                  type="range"
                  min="10"
                  max="800"
                  step="5"
                  value={inputs.PM10}
                  onChange={(e) => handleSliderChange('PM10', Number(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-slate-300 font-medium mb-1">
                  <span>Carbon Monoxide (CO, mg/m³)</span>
                  <span className="font-mono text-cyan-300 font-bold">{inputs.CO.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="0.1"
                  max="6.0"
                  step="0.05"
                  value={inputs.CO}
                  onChange={(e) => handleSliderChange('CO', Number(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-slate-300 font-medium mb-1">
                  <span>Nitrogen Dioxide (NO₂, µg/m³)</span>
                  <span className="font-mono text-cyan-300 font-bold">{inputs.NO2}</span>
                </div>
                <input
                  type="range"
                  min="2"
                  max="150"
                  step="1"
                  value={inputs.NO2}
                  onChange={(e) => handleSliderChange('NO2', Number(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* Group 2: Meteorology & Dispersion */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 text-cyan-400 text-sm font-semibold border-b border-slate-800 pb-2">
              <Wind className="w-4 h-4" />
              <span>Meteorology & Ventilation Layer</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
              <div>
                <div className="flex justify-between text-slate-300 font-medium mb-1">
                  <span>Temperature (°C)</span>
                  <span className="font-mono text-cyan-300 font-bold">{inputs.AT}°C</span>
                </div>
                <input
                  type="range"
                  min="2"
                  max="45"
                  step="0.5"
                  value={inputs.AT}
                  onChange={(e) => handleSliderChange('AT', Number(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-slate-300 font-medium mb-1">
                  <span>Humidity (RH %)</span>
                  <span className="font-mono text-cyan-300 font-bold">{inputs.RH}%</span>
                </div>
                <input
                  type="range"
                  min="15"
                  max="100"
                  step="1"
                  value={inputs.RH}
                  onChange={(e) => handleSliderChange('RH', Number(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-slate-300 font-medium mb-1">
                  <span>Wind Speed (m/s)</span>
                  <span className="font-mono text-cyan-300 font-bold">{inputs.WS.toFixed(1)}</span>
                </div>
                <input
                  type="range"
                  min="0.1"
                  max="6.0"
                  step="0.1"
                  value={inputs.WS}
                  onChange={(e) => handleSliderChange('WS', Number(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* Group 3: Co-pollutants */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 text-cyan-400 text-sm font-semibold border-b border-slate-800 pb-2">
              <Droplets className="w-4 h-4" />
              <span>Secondary Gaseous Pollutants</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div>
                <label className="text-slate-400 text-[11px] block mb-1">NO (µg/m³)</label>
                <input
                  type="number"
                  value={inputs.NO}
                  onChange={(e) => handleSliderChange('NO', Number(e.target.value))}
                  className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 font-mono text-xs focus:border-cyan-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-slate-400 text-[11px] block mb-1">SO₂ (µg/m³)</label>
                <input
                  type="number"
                  value={inputs.SO2}
                  onChange={(e) => handleSliderChange('SO2', Number(e.target.value))}
                  className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 font-mono text-xs focus:border-cyan-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-slate-400 text-[11px] block mb-1">Ozone (µg/m³)</label>
                <input
                  type="number"
                  value={inputs.O3}
                  onChange={(e) => handleSliderChange('O3', Number(e.target.value))}
                  className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 font-mono text-xs focus:border-cyan-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-slate-400 text-[11px] block mb-1">NH₃ (µg/m³)</label>
                <input
                  type="number"
                  value={inputs.NH3}
                  onChange={(e) => handleSliderChange('NH3', Number(e.target.value))}
                  className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 font-mono text-xs focus:border-cyan-500 focus:outline-none"
                />
              </div>
            </div>
          </div>

          <button
            onClick={() => runEstimate()}
            disabled={loading}
            className="w-full py-3 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-sm tracking-wide shadow-lg shadow-cyan-500/20 transition-all flex items-center justify-center gap-2"
          >
            {loading ? <span className="animate-spin text-lg">⏳</span> : <Sparkles className="w-4 h-4" />}
            {loading ? 'Computing XGBoost Inference...' : 'Calculate Virtual BC Reading'}
          </button>
        </div>

        {/* Results Panel (5 cols) */}
        <div className="lg:col-span-5 space-y-5">
          {result && (
            <>
              {/* Primary Output Card */}
              <div className="glass-panel-elevated p-6 rounded-3xl border border-cyan-500/30 space-y-4 relative overflow-hidden bg-gradient-to-b from-slate-900 to-slate-950">
                <div className="flex items-center justify-between">
                  <span className="text-xs uppercase font-mono tracking-wider text-cyan-400 font-bold">
                    Estimated Black Carbon (BC₆)
                  </span>
                  <span className="text-[11px] text-slate-400 font-mono">880 nm channel</span>
                </div>

                <div className="flex items-baseline gap-3">
                  <span className="text-4xl sm:text-5xl font-black font-mono text-white tracking-tight">
                    {result.bc6_ng_m3.toLocaleString()}
                  </span>
                  <div className="text-slate-400 text-xs font-mono">
                    <span className="block font-bold text-slate-200">ng/m³</span>
                    <span>({result.bc6_ug_m3} µg/m³)</span>
                  </div>
                </div>

                {/* Level Badge */}
                <LevelBadge level={result.level} percentile={result.percentile_rank} />

                {/* 90% Conformal Prediction Interval */}
                <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1 text-xs">
                  <div className="flex justify-between text-slate-400">
                    <span>90% Conformal Interval:</span>
                    <span className="font-mono text-cyan-300 font-bold">
                      {result.interval_90[0].toLocaleString()} – {result.interval_90[1].toLocaleString()} ng/m³
                    </span>
                  </div>
                  <div className="flex justify-between text-[11px] text-slate-500">
                    <span>Site Percentile Placement:</span>
                    <span className="font-mono text-slate-300">P{Math.round(result.percentile_rank)} (of 5-yr history)</span>
                  </div>
                </div>

                {/* Percentile Bar */}
                <div className="space-y-1">
                  <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden flex">
                    <div
                      className="h-full transition-all duration-500 rounded-full"
                      style={{
                        width: `${Math.min(100, Math.max(2, result.percentile_rank))}%`,
                        backgroundColor: result.level.color,
                      }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                    <span>P0 (Clean)</span>
                    <span>P50 (Median)</span>
                    <span>P90 (Smog Alert)</span>
                    <span>P99</span>
                  </div>
                </div>

                {/* Physical Diagnostics */}
                {result.diagnostics.length > 0 && (
                  <div className="space-y-1.5 pt-2">
                    {result.diagnostics.map((diag, i) => (
                      <div
                        key={i}
                        className="p-2.5 rounded-lg bg-amber-950/40 border border-amber-800/40 text-amber-300 text-xs flex items-start gap-2"
                      >
                        <AlertCircle className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                        <span>{diag}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Tree SHAP Explainability Card */}
              {result.explanation?.supported && (
                <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <span className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                      <BarChart2 className="w-3.5 h-3.5 text-cyan-400" />
                      Tree-SHAP Feature Attribution
                    </span>
                    <span className="text-[10px] text-slate-400">Impact on BC (ng/m³)</span>
                  </div>

                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    Exact additive contributions computed via Tree SHAP. Positive values push estimated soot higher;
                    negative values disperse or dilute it.
                  </p>

                  <div className="space-y-2 pt-1">
                    {result.explanation.top_drivers_positive.slice(0, 4).map((d, i) => (
                      <div key={i} className="flex items-center justify-between text-xs">
                        <span className="font-mono text-slate-300 font-medium">{d.feature}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 bg-slate-800 rounded-full overflow-hidden flex justify-start">
                            <div
                              className="h-full bg-rose-500 rounded-full"
                              style={{ width: `${Math.min(100, (d.impact / 1500) * 100)}%` }}
                            />
                          </div>
                          <span className="font-mono text-rose-400 font-semibold w-16 text-right">+{d.impact}</span>
                        </div>
                      </div>
                    ))}

                    {result.explanation.top_drivers_negative.slice(0, 3).map((d, i) => (
                      <div key={i} className="flex items-center justify-between text-xs">
                        <span className="font-mono text-slate-300 font-medium">{d.feature}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 bg-slate-800 rounded-full overflow-hidden flex justify-end">
                            <div
                              className="h-full bg-emerald-500 rounded-full"
                              style={{ width: `${Math.min(100, (Math.abs(d.impact) / 1500) * 100)}%` }}
                            />
                          </div>
                          <span className="font-mono text-emerald-400 font-semibold w-16 text-right">{d.impact}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
"""
(VIEWS / "VirtualSensorView.tsx").write_text(virtual_sensor_code.strip() + "\\n", encoding="utf-8")

# ===========================================================================
# 3. WhatIfView.tsx
# ===========================================================================
whatif_code = """import React, { useState, useEffect } from 'react';
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

  const runSweep = async (varName: string) => {
    setLoading(true);
    const cfg = VARIABLES[varName];
    try {
      const res = await sweepWhatIf({}, varName, cfg.min, cfg.max, 25);
      const formatted = res.xs.map((x, i) => ({ x, y: res.ys[i] }));
      setSweepData(formatted);
    } catch (e) {
      console.error(e);
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
"""
(VIEWS / "WhatIfView.tsx").write_text(whatif_code.strip() + "\\n", encoding="utf-8")

# ===========================================================================
# 4. ForecastView.tsx
# ===========================================================================
forecast_code = """import React, { useState, useEffect } from 'react';
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
        const lines = text.split('\\n').filter((l) => l.trim().length > 0);
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
"""
(VIEWS / "ForecastView.tsx").write_text(forecast_code.strip() + "\\n", encoding="utf-8")

print("Core views generated successfully!")
