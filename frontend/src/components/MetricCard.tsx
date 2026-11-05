import React from 'react';

interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  badge?: string;
  trend?: string;
}

export const MetricCard: React.FC<Props> = ({ title, value, subtitle, icon, badge, trend }) => {
  return (
    <div className="glass-panel p-5 rounded-2xl relative overflow-hidden transition-all duration-200 hover:border-slate-600/50 group">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</span>
        {icon && <div className="text-slate-400 group-hover:text-cyan-400 transition-colors">{icon}</div>}
      </div>
      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-2xl font-bold font-mono text-slate-100 tracking-tight">{value}</span>
        {badge && (
          <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-cyan-950/60 border border-cyan-800/40 text-cyan-300">
            {badge}
          </span>
        )}
      </div>
      {subtitle && <p className="text-xs text-slate-400 font-normal leading-relaxed">{subtitle}</p>}
      {trend && <p className="text-xs text-emerald-400 font-medium mt-1 flex items-center gap-1">{trend}</p>}
      <div className="absolute -right-6 -bottom-6 w-24 h-24 rounded-full opacity-5 pointer-events-none blur-xl bg-cyan-500" />
    </div>
  );
};
