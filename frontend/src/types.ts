export interface LevelInfo {
  label: string;
  color: string;
  advice: string;
}

export interface FeatureImpact {
  feature: string;
  impact: number;
}

export interface ExplanationInfo {
  supported: boolean;
  top_drivers_positive: FeatureImpact[];
  top_drivers_negative: FeatureImpact[];
}

export interface EstimateResult {
  bc6_ng_m3: number;
  bc6_ug_m3: number;
  interval_90: [number, number];
  interval_width: number;
  nominal_coverage: number;
  level: LevelInfo;
  percentile_rank: number;
  bc_pm25_share_pct?: number | null;
  diagnostics: string[];
  explanation?: ExplanationInfo;
}

export interface HorizonForecast {
  time: string;
  bc6_ng_m3: number;
  delta_vs_now: number;
  interval_90: [number, number];
  level: LevelInfo;
  percentile_rank: number;
}

export interface EpisodeWarning {
  probability: number;
  warn: boolean;
  threshold_ng_m3: number;
  horizon: string;
}

export interface HistoryPoint {
  time: string;
  bc6: number;
}

export interface ForecastResult {
  issued_from: string;
  current_bc6: number;
  horizons: Record<string, HorizonForecast>;
  episode_warning_6h: EpisodeWarning | null;
  history_points: HistoryPoint[];
}

export interface WhatIfSweepResult {
  variable: string;
  xs: number[];
  ys: number[];
}

export interface WhatIfScaleResult {
  factors: number[];
  ys: number[];
}

export interface LivePoint {
  timestamp: string;
  bc6_estimate: number;
  lo: number;
  hi: number;
  level: string;
  temperature?: number | null;
  humidity?: number | null;
  wind_speed?: number | null;
  pm25?: number | null;
  pm10?: number | null;
  co?: number | null;
  historical_median?: number | null;
}

export interface LiveResult {
  status: string;
  source: string;
  updated_at: string;
  forecast_points: LivePoint[];
}

export interface BatchResult {
  total_rows: number;
  mean_bc6: number;
  median_bc6: number;
  p90_bc6: number;
  level_distribution: Record<string, number>;
  series: {
    timestamp: string;
    bc6_estimate: number;
    lo: number;
    hi: number;
    level: string;
  }[];
}

export interface InsightItem {
  title: string;
  text: string;
}

export interface MetaData {
  created: string;
  data_source: string;
  qc: {
    grid_rows: number;
    bc6_valid_before_qc: number;
    bc6_cap: number;
    bc6_valid_after_qc: number;
    raw_rows: number;
  };
  train_period: [string, string];
  test_period: [string, string];
  deployed_models: Record<string, string>;
  virtual_interval: {
    nominal: number;
    empirical_coverage: number;
    mean_width: number;
  };
  insights: InsightItem[];
  bc_percentiles: {
    p25: number;
    p50: number;
    p75: number;
    p90: number;
    p95: number;
    p99: number;
  };
  feature_medians_virtual: Record<string, number>;
}

export type ViewType =
  | 'overview'
  | 'virtual_sensor'
  | 'what_if'
  | 'forecast'
  | 'live_sentinel'
  | 'plan_day'
  | 'source_split'
  | 'winter_dynamics'
  | 'episodes_events'
  | 'model_benchmark'
  | 'batch_lab'
  | 'methodology';
