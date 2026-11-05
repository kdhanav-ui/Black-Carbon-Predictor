import React, { useState, useEffect } from 'react';
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
