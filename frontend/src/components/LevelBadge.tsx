import React from 'react';
import { LevelInfo } from '../types';
import { ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

interface Props {
  level: LevelInfo;
  percentile?: number;
  showAdvice?: boolean;
}

export const LevelBadge: React.FC<Props> = ({ level, percentile, showAdvice = true }) => {
  const getIcon = () => {
    switch (level.label) {
      case 'Low':
        return <ShieldCheck className="w-4 h-4 text-emerald-400" />;
      case 'Moderate':
        return <ShieldCheck className="w-4 h-4 text-amber-400" />;
      case 'High':
      case 'Very high':
        return <AlertTriangle className="w-4 h-4 text-rose-400" />;
      case 'Extreme':
        return <ShieldAlert className="w-4 h-4 text-red-500 animate-pulse" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-2">
      <div
        className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold shadow-sm border border-white/10"
        style={{ backgroundColor: `${level.color}25`, borderColor: level.color }}
      >
        {getIcon()}
        <span style={{ color: level.color }}>{level.label}</span>
        {percentile !== undefined && (
          <span className="text-xs px-1.5 py-0.5 rounded bg-black/40 text-slate-300 font-mono">
            P{Math.round(percentile)}
          </span>
        )}
      </div>
      {showAdvice && (
        <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
          {level.advice}
        </p>
      )}
    </div>
  );
};
