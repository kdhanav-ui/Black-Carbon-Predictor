import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS = ROOT / "frontend" / "src" / "components"
VIEWS = ROOT / "frontend" / "src" / "views"

os.makedirs(COMPONENTS, exist_ok=True)
os.makedirs(VIEWS, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. LevelBadge.tsx
# ---------------------------------------------------------------------------
level_badge_code = """import React from 'react';
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
"""
(COMPONENTS / "LevelBadge.tsx").write_text(level_badge_code.strip() + "\\n", encoding="utf-8")

# ---------------------------------------------------------------------------
# 2. MetricCard.tsx
# ---------------------------------------------------------------------------
metric_card_code = """import React from 'react';

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
"""
(COMPONENTS / "MetricCard.tsx").write_text(metric_card_code.strip() + "\\n", encoding="utf-8")

# ---------------------------------------------------------------------------
# 3. Navbar.tsx
# ---------------------------------------------------------------------------
navbar_code = """import React from 'react';
import { ViewType } from '../types';
import {
  Activity,
  Sliders,
  TrendingUp,
  Radio,
  Calendar,
  Flame,
  Snowflake,
  Sparkles,
  BarChart3,
  Layers,
  BookOpen,
  Cpu,
} from 'lucide-react';

interface Props {
  currentView: ViewType;
  onSelectView: (view: ViewType) => void;
  deployedVirtualModel?: string;
}

export const Navbar: React.FC<Props> = ({ currentView, onSelectView, deployedVirtualModel }) => {
  const navItems: { id: ViewType; label: string; icon: React.ReactNode; group: string }[] = [
    { id: 'overview', label: 'Overview', icon: <Activity className="w-4 h-4" />, group: 'Core' },
    { id: 'virtual_sensor', label: 'Virtual BC Sensor', icon: <Sliders className="w-4 h-4" />, group: 'Core' },
    { id: 'what_if', label: 'What-If Lab', icon: <Cpu className="w-4 h-4" />, group: 'Core' },
    { id: 'forecast', label: 'Forecast & Alerts', icon: <TrendingUp className="w-4 h-4" />, group: 'Core' },
    { id: 'live_sentinel', label: 'Live Varanasi', icon: <Radio className="w-4 h-4" />, group: 'Telemetry' },
    { id: 'plan_day', label: 'Plan Your Day', icon: <Calendar className="w-4 h-4" />, group: 'Telemetry' },
    { id: 'source_split', label: 'Source Apportionment', icon: <Flame className="w-4 h-4" />, group: 'Science' },
    { id: 'winter_dynamics', label: 'Winter Smog', icon: <Snowflake className="w-4 h-4" />, group: 'Science' },
    { id: 'episodes_events', label: 'Diwali & Episodes', icon: <Sparkles className="w-4 h-4" />, group: 'Science' },
    { id: 'model_benchmark', label: 'AI Leaderboard', icon: <BarChart3 className="w-4 h-4" />, group: 'Analytics' },
    { id: 'batch_lab', label: 'Batch Processing', icon: <Layers className="w-4 h-4" />, group: 'Analytics' },
    { id: 'methodology', label: 'About & Methods', icon: <BookOpen className="w-4 h-4" />, group: 'Analytics' },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <span className="text-xl">🌫️</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-100 tracking-tight text-base sm:text-lg">
                  Black Carbon Intelligence
                </span>
                <span className="hidden sm:inline-block text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800/50">
                  Varanasi AE33
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                IIT (BHU) Continuous Aethalometer System · IGP Air Quality Platform
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {deployedVirtualModel && (
              <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-slate-400">Deployed Model:</span>
                <span className="font-semibold text-cyan-400 font-mono">{deployedVirtualModel}</span>
              </div>
            )}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
              <span className="font-mono">FastAPI 3.0</span>
            </div>
          </div>
        </div>

        {/* Navigation Bar */}
        <div className="flex items-center gap-1 overflow-x-auto py-2 scrollbar-none border-t border-slate-800/40 text-xs">
          {navItems.map((item) => {
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectView(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg whitespace-nowrap transition-all duration-150 font-medium ${
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
"""
(COMPONENTS / "Navbar.tsx").write_text(navbar_code.strip() + "\\n", encoding="utf-8")

print("Components successfully written!")
