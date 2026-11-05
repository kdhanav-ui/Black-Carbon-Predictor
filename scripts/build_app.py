from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "frontend" / "src"

app_code = """import React, { useState, useEffect } from 'react';
import { ViewType, MetaData } from './types';
import { fetchMeta } from './api';
import { Navbar } from './components/Navbar';
import { OverviewView } from './views/OverviewView';
import { VirtualSensorView } from './views/VirtualSensorView';
import { WhatIfView } from './views/WhatIfView';
import { ForecastView } from './views/ForecastView';
import { LiveOutlookView } from './views/LiveOutlookView';
import { PlanYourDayView } from './views/PlanYourDayView';
import { SourceSplitView } from './views/SourceSplitView';
import { WinterDynamicsView } from './views/WinterDynamicsView';
import { DiwaliEpisodesView } from './views/DiwaliEpisodesView';
import { ModelLeaderboardView } from './views/ModelLeaderboardView';
import { BatchView } from './views/BatchView';
import { MethodologyView } from './views/MethodologyView';
import { AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewType>('overview');
  const [meta, setMeta] = useState<MetaData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMeta()
      .then((data) => {
        setMeta(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError('Could not connect to the FastAPI prediction service. Please ensure python src.api is running on port 8000.');
        setLoading(false);
      });
  }, []);

  const renderActiveView = () => {
    if (!meta) return null;
    switch (currentView) {
      case 'overview':
        return <OverviewView meta={meta} onNavigate={setCurrentView} />;
      case 'virtual_sensor':
        return <VirtualSensorView meta={meta} />;
      case 'what_if':
        return <WhatIfView meta={meta} />;
      case 'forecast':
        return <ForecastView meta={meta} />;
      case 'live_sentinel':
        return <LiveOutlookView meta={meta} />;
      case 'plan_day':
        return <PlanYourDayView meta={meta} />;
      case 'source_split':
        return <SourceSplitView meta={meta} />;
      case 'winter_dynamics':
        return <WinterDynamicsView meta={meta} />;
      case 'episodes_events':
        return <DiwaliEpisodesView meta={meta} />;
      case 'model_benchmark':
        return <ModelLeaderboardView meta={meta} />;
      case 'batch_lab':
        return <BatchView meta={meta} />;
      case 'methodology':
        return <MethodologyView meta={meta} />;
      default:
        return <OverviewView meta={meta} onNavigate={setCurrentView} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0e17] text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-slate-950">
      {/* Top Navbar */}
      <Navbar
        currentView={currentView}
        onSelectView={setCurrentView}
        deployedVirtualModel={meta?.deployed_models?.virtual}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {loading && (
          <div className="h-[60vh] flex flex-col items-center justify-center space-y-4">
            <div className="w-10 h-10 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs font-mono text-slate-400">Loading Black Carbon Intelligence System...</span>
          </div>
        )}

        {error && (
          <div className="glass-panel p-6 rounded-3xl border border-rose-800/50 bg-rose-950/20 max-w-xl mx-auto space-y-3 text-center my-12">
            <div className="w-12 h-12 rounded-2xl bg-rose-900/40 text-rose-400 flex items-center justify-center mx-auto">
              <AlertCircle className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white">FastAPI Service Connection Notice</h3>
            <p className="text-xs text-rose-300/90 leading-relaxed">{error}</p>
            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-[11px] font-mono text-cyan-300">
              Run: uvicorn src.api:app --port 8000
            </div>
          </div>
        )}

        {!loading && !error && renderActiveView()}
      </main>

      {/* Footer */}
      <footer className="glass-panel border-t border-slate-800/80 bg-slate-950/90 py-6 mt-12 text-center text-xs text-slate-500 space-y-1">
        <p>
          🌫️ <strong>Black Carbon Intelligence Platform</strong> · AE33 Continuous Aethalometer Research
        </p>
        <p>
          IIT (BHU) Varanasi · Prof. Durga Prasad A. & Dr. Yogesh · Developed by Dhanav Kumar, NIT Raipur
        </p>
      </footer>
    </div>
  );
};
export default App;
"""
(SRC / "App.tsx").write_text(app_code.strip() + "\\n", encoding="utf-8")
print("App.tsx written successfully!")
