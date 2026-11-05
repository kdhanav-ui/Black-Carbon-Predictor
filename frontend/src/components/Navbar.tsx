import React, { useState } from 'react';
import { ViewType } from '../types';
import {
  Activity, Sliders, TrendingUp, Radio, Calendar, Flame, Snowflake,
  Sparkles, BarChart3, Layers, BookOpen, Cpu, Menu, X, ChevronRight
} from 'lucide-react';

interface Props {
  currentView: ViewType;
  onSelectView: (view: ViewType) => void;
  deployedVirtualModel?: string;
}

export const Navbar: React.FC<Props> = ({ currentView, onSelectView, deployedVirtualModel }) => {
  const [open, setOpen] = useState(false);
  const navItems: { id: ViewType; label: string; icon: React.ReactNode; group: string }[] = [
    { id: 'overview', label: 'Overview', icon: <Activity />, group: 'Workspace' },
    { id: 'virtual_sensor', label: 'Virtual BC Sensor', icon: <Sliders />, group: 'Workspace' },
    { id: 'what_if', label: 'What-If Lab', icon: <Cpu />, group: 'Workspace' },
    { id: 'forecast', label: 'Forecast & Alerts', icon: <TrendingUp />, group: 'Workspace' },
    { id: 'live_sentinel', label: 'Live Varanasi', icon: <Radio />, group: 'Monitoring' },
    { id: 'plan_day', label: 'Plan Your Day', icon: <Calendar />, group: 'Monitoring' },
    { id: 'source_split', label: 'Source Apportionment', icon: <Flame />, group: 'Science' },
    { id: 'winter_dynamics', label: 'Winter Smog', icon: <Snowflake />, group: 'Science' },
    { id: 'episodes_events', label: 'Diwali & Episodes', icon: <Sparkles />, group: 'Science' },
    { id: 'model_benchmark', label: 'AI Leaderboard', icon: <BarChart3 />, group: 'Analytics' },
    { id: 'batch_lab', label: 'Batch Processing', icon: <Layers />, group: 'Analytics' },
    { id: 'methodology', label: 'About & Methods', icon: <BookOpen />, group: 'Analytics' },
  ];
  const groups = [...new Set(navItems.map(item => item.group))];

  const select = (id: ViewType) => {
    onSelectView(id);
    setOpen(false);
  };

  return (
    <>
      <header className="bc-header">
        <div className="bc-topbar">
          <button className="bc-menu-button" aria-label={open ? 'Close navigation' : 'Open navigation'} onClick={() => setOpen(v => !v)}>
            {open ? <X /> : <Menu />}
          </button>
          <div className="bc-brand-mark">🌫️</div>
          <div className="bc-brand-copy">
            <div className="bc-brand-title">Black Carbon Intelligence</div>
            <div className="bc-brand-subtitle">AE33 Research & Air Quality Analytics · IIT (BHU), Varanasi</div>
          </div>
          <div className="bc-header-status">
            <span className="bc-status-dot" />
            <span>API connected</span>
            {deployedVirtualModel && <span className="bc-model-chip">{deployedVirtualModel}</span>}
          </div>
        </div>
      </header>
      {open && <button className="bc-sidebar-backdrop" aria-label="Close navigation" onClick={() => setOpen(false)} />}
      <aside className={`bc-sidebar ${open ? 'is-open' : ''}`} aria-hidden={!open}>
        <div className="bc-sidebar-heading">
          <span>Navigation</span>
          <button onClick={() => setOpen(false)} aria-label="Close navigation"><X /></button>
        </div>
        {groups.map(group => (
          <div className="bc-nav-group" key={group}>
            <div className="bc-nav-label">{group}</div>
            {navItems.filter(item => item.group === group).map(item => {
              const active = currentView === item.id;
              return (
                <button key={item.id} className={`bc-nav-item ${active ? 'active' : ''}`} onClick={() => select(item.id)}>
                  <span className="bc-nav-icon">{item.icon}</span>
                  <span className="bc-nav-text">{item.label}</span>
                  {active && <ChevronRight className="bc-nav-chevron" />}
                </button>
              );
            })}
          </div>
        ))}
        <div className="bc-sidebar-footer">BLACK CARBON · RESEARCH CONSOLE</div>
      </aside>
    </>
  );
};
