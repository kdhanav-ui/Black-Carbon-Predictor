import {
  MetaData,
  EstimateResult,
  ForecastResult,
  WhatIfSweepResult,
  WhatIfScaleResult,
  LiveResult,
  BatchResult,
} from './types';

const BASE_URL = '/api';

export async function fetchMeta(): Promise<MetaData> {
  const res = await fetch(BASE_URL + '/meta');
  if (!res.ok) throw new Error('Failed to load system metadata');
  return res.json();
}

export async function fetchTable<T = any>(tableName: string): Promise<T[]> {
  const res = await fetch(BASE_URL + '/tables/' + tableName);
  if (!res.ok) throw new Error('Failed to load table ' + tableName);
  return res.json();
}

export async function estimateBC(
  readings: Record<string, number | null>,
  timestamp?: string | null,
  explain: boolean = true
): Promise<EstimateResult> {
  const res = await fetch(BASE_URL + '/estimate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ readings, timestamp, explain }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Prediction failed');
  }
  return res.json();
}

export async function sweepWhatIf(
  readings: Record<string, number | null>,
  variable: string,
  min_val: number,
  max_val: number,
  steps: number = 25
): Promise<WhatIfSweepResult> {
  const res = await fetch(BASE_URL + '/whatif/sweep', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ readings, variable, min_val, max_val, steps }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'What-if sweep failed (HTTP ' + res.status + ')');
  }
  return res.json();
}

export async function scaleWhatIf(
  readings: Record<string, number | null>,
  factors?: number[]
): Promise<WhatIfScaleResult> {
  const res = await fetch(BASE_URL + '/whatif/scale', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ readings, factors }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'What-if emission scaling failed (HTTP ' + res.status + ')');
  }
  return res.json();
}

export async function fetchForecast(records: any[]): Promise<ForecastResult> {
  const res = await fetch(BASE_URL + '/forecast', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ records }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Forecast computation failed');
  }
  return res.json();
}

export async function fetchSampleRecent(): Promise<{ total: number; records: any[] }> {
  const res = await fetch(BASE_URL + '/sample_recent');
  if (!res.ok) throw new Error('Failed to load sample dataset');
  return res.json();
}

export async function fetchLive(): Promise<LiveResult> {
  const res = await fetch(BASE_URL + '/live');
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Live telemetry fetch failed');
  }
  return res.json();
}

export async function uploadBatch(file: File): Promise<BatchResult> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(BASE_URL + '/batch', {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Batch processing failed');
  }
  return res.json();
}
