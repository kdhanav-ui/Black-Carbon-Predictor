import React, { useState, useEffect } from 'react';
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
