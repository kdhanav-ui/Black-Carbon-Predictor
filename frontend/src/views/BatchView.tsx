import React, { useState } from 'react';
import { MetaData, BatchResult } from '../types';
import { uploadBatch } from '../api';
import { Layers, Upload, Download, AlertTriangle, CheckCircle, FileText } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  BarChart,
  Bar,
} from 'recharts';

interface Props {
  meta: MetaData;
}

export const BatchView: React.FC<Props> = ({ meta }) => {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<BatchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleProcess = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await uploadBatch(file);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Batch estimation failed');
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (!result?.series) return;
    const header = 'Timestamp,BC6_Estimate_ng_m3,Lower_90_ng_m3,Upper_90_ng_m3,Level\n';
    const rows = result.series
      .map((s) => `${s.timestamp},${s.bc6_estimate},${s.lo},${s.hi},${s.level}`)
      .join('\n');
    const blob = new Blob([header + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'bc6_batch_estimates.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const distData = Object.entries(result?.level_distribution || {}).map(([level, count]) => ({
    level,
    count,
  }));

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-400 text-xs font-semibold">
          <Layers className="w-3.5 h-3.5" />
          Batch Inference Processing Laboratory
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Time-Series Batch Virtual Sensor</h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Upload any CSV with a <code className="text-cyan-400 font-mono">Timestamp</code> column and available station
          pollutant/weather columns (PM2.5, PM10, CO, NO₂, Temp, Humidity, Wind). The engine infers continuous 90%
          uncertainty-bounded Black Carbon time-series for every row.
        </p>
      </div>

      {/* Upload Zone */}
      <div className="glass-panel p-8 rounded-3xl border-2 border-dashed border-slate-700/80 flex flex-col items-center justify-center text-center space-y-4 hover:border-cyan-500/50 transition-colors">
        <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-cyan-400">
          <Upload className="w-7 h-7" />
        </div>
        <div>
          <span className="text-sm font-bold text-white block">Select or drop your CAAQMS CSV file</span>
          <span className="text-xs text-slate-400">Supports hourly or 15-minute resolution time-series datasets</span>
        </div>

        <div className="flex items-center gap-3">
          <label className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition-all cursor-pointer">
            Browse File
            <input type="file" accept=".csv" onChange={handleFileChange} className="hidden" />
          </label>

          {file && (
            <button
              onClick={handleProcess}
              disabled={loading}
              className="px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold transition-all shadow-lg shadow-cyan-500/20"
            >
              {loading ? 'Processing ML Batch...' : `Run Batch (${file.name})`}
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="glass-panel p-4 rounded-2xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Results View */}
      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="glass-panel p-4 rounded-2xl border border-slate-800">
              <span className="text-xs text-slate-400 block">Total Timestamps</span>
              <span className="text-2xl font-bold font-mono text-white">{result.total_rows.toLocaleString()}</span>
            </div>
            <div className="glass-panel p-4 rounded-2xl border border-slate-800">
              <span className="text-xs text-slate-400 block">Mean Inferred BC₆</span>
              <span className="text-2xl font-bold font-mono text-cyan-300">{result.mean_bc6.toLocaleString()} ng/m³</span>
            </div>
            <div className="glass-panel p-4 rounded-2xl border border-slate-800">
              <span className="text-xs text-slate-400 block">Median BC₆</span>
              <span className="text-2xl font-bold font-mono text-cyan-300">{result.median_bc6.toLocaleString()} ng/m³</span>
            </div>
            <div className="glass-panel p-4 rounded-2xl border border-slate-800">
              <span className="text-xs text-slate-400 block">90th Percentile</span>
              <span className="text-2xl font-bold font-mono text-rose-400">{result.p90_bc6.toLocaleString()} ng/m³</span>
            </div>
          </div>

          {/* Time Series Chart */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-100">Estimated Black Carbon Sequence</h3>
                <p className="text-xs text-slate-400">Showing sampled sequence with conformal uncertainty bands</p>
              </div>

              <button
                onClick={downloadCSV}
                className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-2"
              >
                <Download className="w-4 h-4 text-cyan-400" />
                Export Annotated CSV
              </button>
            </div>

            <div className="h-80 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={result.series} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="timestamp" stroke="#64748b" fontSize={10} />
                  <YAxis stroke="#64748b" fontSize={11} label={{ value: 'BC₆ (ng/m³)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                  <Line type="monotone" dataKey="bc6_estimate" name="BC₆ Estimate" stroke="#06b6d4" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
