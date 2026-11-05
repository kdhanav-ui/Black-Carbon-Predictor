import React from 'react';
import { MetaData } from '../types';
import { BookOpen, ShieldCheck, Cpu, Database, Award, Info } from 'lucide-react';

interface Props {
  meta: MetaData;
}

export const MethodologyView: React.FC<Props> = ({ meta }) => {
  return (
    <div className="space-y-8 animate-fadeIn max-w-5xl mx-auto">
      {/* Header */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-400 text-xs font-semibold">
          <BookOpen className="w-3.5 h-3.5" />
          Academic Rigor & Scientific Pedigree
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Methodology, Quality Control & Provenance</h1>
        <p className="text-xs sm:text-sm text-slate-300">
          Complete scientific documentation of instrumentation, data curation, leak-free feature engineering, and
          internship research at IIT (BHU) Varanasi.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Section 1 */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-cyan-400 font-bold text-base">
            <Database className="w-5 h-5" />
            <h3>Instrumentation & Data Curation</h3>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Continuous multi-wavelength measurements collected via a research-grade <strong>Magee Scientific AE33 Aethalometer</strong>{' '}
            co-located with a CPCB/UPPCB Continuous Ambient Air Quality Monitoring Station (CAAQMS) at <strong>IIT (BHU), Varanasi</strong>,
            spanning 2021 through 2025 at 15-minute resolution.
          </p>
          <ul className="text-xs text-slate-400 list-disc list-inside space-y-1">
            <li>Channel 6 (880 nm) serves as the primary Black Carbon standard metric (BC₆).</li>
            <li>Dual-spot loading compensation algorithm active in the AE33 sensor.</li>
            <li>Zero/negative values and values above the 99.9th percentile removed during automated QC.</li>
          </ul>
        </div>

        {/* Section 2 */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-base">
            <Cpu className="w-5 h-5" />
            <h3>Leak-Free ML Pipeline & Conformal Bounds</h3>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Every feature at timestamp <em>t</em> strictly uses information available at or before <em>t</em>.
            Evaluation is conducted on a chronological 70/15/15 train/validation/test split separated by an embargo gap.
          </p>
          <ul className="text-xs text-slate-400 list-disc list-inside space-y-1">
            <li>Benchmarks: Ridge, kNN, MLP, Random Forest, ExtraTrees, XGBoost, LightGBM, and Ensembles.</li>
            <li>Split-conformal prediction intervals guarantee nominal 90% coverage with relative width scaling.</li>
            <li>Explainability powered by exact Tree-SHAP local attribution values.</li>
          </ul>
        </div>
      </div>

      {/* Research Credits Card */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 bg-gradient-to-r from-slate-950 via-slate-900 to-cyan-950/30 space-y-3">
        <div className="flex items-center gap-2 text-cyan-400 font-bold text-base">
          <Award className="w-5 h-5" />
          <h3>Research Credits & Institutional Acknowledgements</h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Developed by <strong>Dhanav Kumar</strong> (NIT Raipur) during a research internship at{' '}
          <strong>Indian Institute of Technology (BHU), Varanasi</strong>, supervised by <strong>Prof. Durga Prasad A.</strong>{' '}
          and <strong>Dr. Yogesh</strong>.
        </p>
        <p className="text-[11px] text-slate-400 leading-relaxed italic border-t border-slate-800 pt-3">
          Disclaimer: This system is a research, educational, and environmental analytics tool — not medical advice.
          Alert thresholds are calibrated relative to this site's historical atmospheric distribution.
        </p>
      </div>
    </div>
  );
};
