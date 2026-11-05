import React, { useState, useEffect } from 'react';
import { MetaData } from '../types';
import { fetchTable } from '../api';
import { SourceSignatures } from '../components/SourceSignatures';
import { Flame, Info, CheckCircle2, Factory, TreePine } from 'lucide-react';
import {
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

export const SourceSplitView: React.FC<Props> = ({ meta }) => {
  const [monthlyData, setMonthlyData] = useState<any[]>([]);
  const [aaeData, setAaeData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchTable('apportionment_monthly'), fetchTable('aae_by_season')])
      .then(([m, a]) => {
        setMonthlyData(m || []);
        setAaeData(a || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const formattedMonthly = monthlyData.map((d) => ({
    month: MONTHS[(d.month || 1) - 1],
    fossil: Math.round(d.BC_ff || 0),
    biomass: Math.round(d.BC_bb || 0),
  }));

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-400 text-xs font-semibold">
          <Flame className="w-3.5 h-3.5" />
          Chemical Physics Source Attribution
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Source Apportionment: Fossil Fuel vs Biomass Burning</h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Deconvolving ambient soot into vehicular fossil fuel emissions (traffic diesel/gasoline) versus solid fuel
          biomass burning (wood heating & agricultural crop stubble) using the Sandradewi dual-wavelength model.
        </p>
      </div>

      {/* Physics Model Explainer Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center gap-2 text-cyan-400 font-bold text-sm">
            <Factory className="w-4 h-4" />
            <span>Fossil Fuel Soot (BC_ff)</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Dominated by high-temperature diesel and gasoline combustion. Displays nearly uniform optical absorption
            across the near-IR and UV spectra with an <strong>Absorption Ångström Exponent (AAE_ff ≈ 1.0)</strong>.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
          <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
            <TreePine className="w-4 h-4" />
            <span>Biomass Burning Soot (BC_bb)</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Produced by lower-temperature wood burning, cow dung cakes, and agricultural burning. Enriched in organic
            brown carbon compounds absorbing strongly at 470 nm with an <strong>AAE_bb ≈ 2.0</strong>.
          </p>
        </div>
      </div>

      {!loading && monthlyData.length === 0 && (
        <div className="glass-panel p-6 rounded-3xl border border-amber-800/50 bg-amber-950/20 space-y-3">
          <div className="flex items-center gap-2 text-amber-300 font-bold text-sm">
            <Info className="w-4 h-4" />
            <span>Quantitative fuel split needs BC2 + BC7 channels</span>
          </div>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
            The Sandradewi model needs two aethalometer wavelengths: <strong>BC2 (470 nm)</strong> and{' '}
            <strong>BC7 (950 nm)</strong>. The data used to train the deployed models only contains the BC6 (880 nm)
            channel, so an exact fossil-fuel vs biomass percentage can't be computed. The tracer-based source signatures below
            are derived from the data that is available.
          </p>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-[11px] font-mono text-cyan-300">
            python run_pipeline.py --data "your_AE33_export_with_BC1-BC7.xlsx"
          </div>
          <p className="text-xs text-slate-400">
            Re-run the pipeline with an AE33 export that includes all seven channels, then run{' '}
            <code className="text-cyan-300">python scripts/export_models_json.py</code> and redeploy. This page fills in automatically.
          </p>
        </div>
      )}

      {!loading && monthlyData.length === 0 && <SourceSignatures />}

      {/* Monthly Stacked Chart */}
      {monthlyData.length > 0 && (
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-100">Monthly Mean BC: Fossil Fuel vs Biomass Split</h3>
            <p className="text-xs text-slate-400">
              Notice the massive surge in biomass soot during the cold winter months (Nov–Feb) due to domestic space heating
            </p>
          </div>
        </div>

        <div className="h-80 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={formattedMonthly} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} label={{ value: 'Mean BC₆ (ng/m³)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                formatter={(val: any, name?: any) => [
                  `${Number(val).toLocaleString()} ng/m³`,
                  name === 'fossil' ? 'Fossil Fuel (Traffic)' : 'Biomass Burning (Wood/Crop)',
                ]}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Bar dataKey="fossil" name="Fossil Fuel (Traffic)" fill="#3b82f6" stackId="a" />
              <Bar dataKey="biomass" name="Biomass Burning (Wood/Crop)" fill="#f59e0b" stackId="a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      )}

      {/* AAE by Season Table */}
      {aaeData.length > 0 && (
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
          <h3 className="text-base font-bold text-slate-100">Absorption Ångström Exponent (AAE) by Season</h3>
          <p className="text-xs text-slate-400">
            Values near 1.0 indicate pure vehicular diesel/gasoline dominance; values above 1.3 indicate strong biomass
            burning smoke contributions.
          </p>
          <div className="overflow-x-auto pt-2">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono text-[11px] border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-4">Season</th>
                  <th className="py-2.5 px-4">Mean AAE (470–950 nm)</th>
                  <th className="py-2.5 px-4">Median AAE</th>
                  <th className="py-2.5 px-4">Dominant Atmospheric Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {aaeData.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-900/50">
                    <td className="py-2.5 px-4 font-semibold text-slate-100">{row.season}</td>
                    <td className="py-2.5 px-4 text-cyan-300">{Number(row.mean || row.aae_mean || 0).toFixed(2)}</td>
                    <td className="py-2.5 px-4 text-cyan-300">{Number(row.median || row.aae_median || 0).toFixed(2)}</td>
                    <td className="py-2.5 px-4 text-slate-300">
                      {Number(row.mean || row.aae_mean || 0) > 1.3 ? '🪵 Biomass Heating & Crop Smoke' : '🚗 Vehicular Traffic Dominant'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
