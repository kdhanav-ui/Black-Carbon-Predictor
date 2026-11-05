import React, { useEffect, useMemo, useState } from 'react';
import { fetchTable } from '../api';
import { Car, Flame, Moon, CalendarDays, Sparkles, Activity } from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
  ReferenceArea,
} from 'recharts';

// Tracer-based source indicators computed from the site's own AE33 + CAAQMS record.
// They do not replace a dual-wavelength (BC2/BC7) apportionment, but show where
// traffic-like and combustion/heating-like signatures appear in the data.

const SEASONS = ['Winter', 'Pre-monsoon', 'Monsoon', 'Post-monsoon'] as const;
const SEASON_COLORS: Record<string, string> = {
  Winter: '#60a5fa',
  'Pre-monsoon': '#f59e0b',
  Monsoon: '#2dd4bf',
  'Post-monsoon': '#f472b6',
};
const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const RUSH = new Set([7, 8, 9, 10, 18, 19, 20, 21]);
const NIGHT = new Set([22, 23, 0, 1, 2, 3]);
const AFTERNOON = new Set([12, 13, 14, 15, 16]);

const TRACERS: { key: string; label: string; group: 'traffic' | 'combustion' }[] = [
  { key: 'NOX', label: 'NOx', group: 'traffic' },
  { key: 'NO2', label: 'NO₂', group: 'traffic' },
  { key: 'BENZENE', label: 'Benzene', group: 'traffic' },
  { key: 'CO', label: 'CO', group: 'combustion' },
  { key: 'PM25', label: 'PM2.5', group: 'combustion' },
  { key: 'NH3', label: 'NH₃', group: 'combustion' },
  { key: 'SO2', label: 'SO₂', group: 'combustion' },
];

const tooltipStyle = { backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: 12 };
const fmt = (v: number) => Math.round(v).toLocaleString();
const mean = (a: number[]) => (a.length ? a.reduce((s, x) => s + x, 0) / a.length : NaN);

type Row = Record<string, any>;

export const SourceSignatures: React.FC = () => {
  const [seasonHour, setSeasonHour] = useState<Row[]>([]);
  const [bcCo, setBcCo] = useState<Row[]>([]);
  const [dowHour, setDowHour] = useState<Row[]>([]);
  const [corr, setCorr] = useState<Row[]>([]);
  const [diwali, setDiwali] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    Promise.all([
      fetchTable('profile_season_hour'),
      fetchTable('bc_co_ratio'),
      fetchTable('profile_dow_hour'),
      fetchTable('correlations_by_season'),
      fetchTable('diwali_effect'),
    ])
      .then(([a, b, c, d, e]) => {
        setSeasonHour(a || []);
        setBcCo(b || []);
        setDowHour(c || []);
        setCorr(d || []);
        setDiwali(e || []);
      })
      .catch(() => setFailed(true))
      .finally(() => setLoading(false));
  }, []);

  // Diurnal BC median by season (one row per hour)
  const diurnal = useMemo(() => {
    return Array.from({ length: 24 }, (_, h) => {
      const row: Row = { hour: `${String(h).padStart(2, '0')}:00`, h };
      for (const s of SEASONS) {
        const r = seasonHour.find((x) => x.season === s && Number(x.hour) === h);
        if (r) row[s] = Math.round(Number(r.median));
      }
      return row;
    });
  }, [seasonHour]);

  // BC / CO ratio by season and hour
  const ratio = useMemo(() => {
    return Array.from({ length: 24 }, (_, h) => {
      const row: Row = { hour: `${String(h).padStart(2, '0')}:00` };
      for (const s of SEASONS) {
        const r = bcCo.find((x) => x.season === s && Number(x.hour) === h);
        if (r) row[s] = Math.round(Number(r.bc_per_co));
      }
      return row;
    });
  }, [bcCo]);

  // Rush-hour vs night median BC by weekday
  const weekly = useMemo(() => {
    return DAYS.map((label, d) => {
      const rows = dowHour.filter((x) => Number(x.dow) === d);
      return {
        day: label,
        rush: Math.round(mean(rows.filter((x) => RUSH.has(Number(x.hour))).map((x) => Number(x.median)))),
        night: Math.round(mean(rows.filter((x) => NIGHT.has(Number(x.hour))).map((x) => Number(x.median)))),
      };
    });
  }, [dowHour]);

  // Spearman correlation of BC with tracer gases, by season
  const tracerCorr = useMemo(() => {
    return TRACERS.map((t) => {
      const row: Row = { tracer: t.label, group: t.group };
      for (const s of SEASONS) {
        const r = corr.find((x) => x.season === s && x.variable === t.key);
        if (r && r.spearman !== null) row[s] = Math.round(Number(r.spearman) * 100) / 100;
      }
      return row;
    });
  }, [corr]);

  // Headline indicators
  const kpis = useMemo(() => {
    const seasonVals = (s: string, hours: Set<number>) =>
      seasonHour.filter((x) => x.season === s && hours.has(Number(x.hour))).map((x) => Number(x.median));
    const winterNight = mean(seasonVals('Winter', NIGHT));
    const winterAfternoon = mean(seasonVals('Winter', AFTERNOON));
    const monsoonNight = mean(seasonVals('Monsoon', NIGHT));
    const ratioBy = (s: string) => mean(bcCo.filter((x) => x.season === s).map((x) => Number(x.bc_per_co)));
    const weekdayRush = mean(weekly.slice(0, 5).map((w) => w.rush));
    const sundayRush = weekly[6]?.rush ?? NaN;
    const validDiwali = diwali.filter((d) => Number(d.baseline_mean) >= 1000);
    return {
      nightToAfternoon: winterNight / winterAfternoon,
      winterVsMonsoonNight: winterNight / monsoonNight,
      winterRatio: ratioBy('Winter'),
      postMonsoonRatio: ratioBy('Post-monsoon'),
      sundayDrop: (1 - sundayRush / weekdayRush) * 100,
      diwaliRatio: mean(validDiwali.map((d) => Number(d.ratio))),
      diwaliYears: validDiwali.length,
    };
  }, [seasonHour, bcCo, weekly, diwali]);

  if (loading) {
    return (
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 text-sm text-slate-400">Loading source signatures…</div>
    );
  }
  if (failed || !seasonHour.length) {
    return (
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 text-sm text-slate-400">
        Source signature tables could not be loaded.
      </div>
    );
  }

  const finite = (v: number) => Number.isFinite(v);

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h2 className="text-lg font-bold text-white tracking-tight">Source Signatures in the Varanasi Record</h2>
        <p className="text-xs sm:text-sm text-slate-400 max-w-4xl">
          Without the 470/950 nm channels, sources can still be read from <em>when</em> soot appears and{' '}
          <em>which gases travel with it</em>. Traffic emits soot alongside NOx and benzene during commute hours;
          biomass and residential burning produce soot with more CO, concentrated on cold nights. These are
          qualitative tracer indicators from 5 years of AE33 + CAAQMS data, not a quantitative fuel split.
        </p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Kpi
          icon={<Moon className="w-4 h-4 text-blue-400" />}
          title="Winter night vs afternoon"
          value={finite(kpis.nightToAfternoon) ? `${kpis.nightToAfternoon.toFixed(1)}×` : '–'}
          note="Median BC 22:00–03:00 vs 12:00–16:00. Night heating and fires under a shallow boundary layer."
        />
        <Kpi
          icon={<Flame className="w-4 h-4 text-amber-400" />}
          title="Winter vs monsoon nights"
          value={finite(kpis.winterVsMonsoonNight) ? `${kpis.winterVsMonsoonNight.toFixed(1)}×` : '–'}
          note="Same night hours, different season. Points to seasonal burning, not year-round traffic."
        />
        <Kpi
          icon={<Car className="w-4 h-4 text-cyan-400" />}
          title="Sunday rush-hour change"
          value={finite(kpis.sundayDrop) ? `${kpis.sundayDrop > 0 ? '−' : '+'}${Math.abs(kpis.sundayDrop).toFixed(0)}%` : '–'}
          note="Sunday vs weekday median BC at 07–10 h and 18–21 h. A small drop means traffic is not the only driver."
        />
        <Kpi
          icon={<Sparkles className="w-4 h-4 text-rose-400" />}
          title="Diwali night vs baseline"
          value={finite(kpis.diwaliRatio) ? `${kpis.diwaliRatio.toFixed(1)}×` : '–'}
          note={`Mean across ${kpis.diwaliYears} festival years with valid data. Fireworks and festival burning.`}
        />
      </div>

      {/* Diurnal by season */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="flex items-center gap-2 text-slate-100 font-bold text-base">
          <Activity className="w-4 h-4 text-cyan-400" />
          Daily BC Cycle by Season
        </div>
        <p className="text-xs text-slate-400">
          Median BC₆ by hour. Shaded bands mark the morning (07–10) and evening (18–21) commute. Winter BC climbs
          after dark and stays high overnight, well beyond the commute window, a signature of residential and
          biomass burning trapped under the night-time inversion.
        </p>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={diurnal} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <ReferenceArea x1="07:00" x2="10:00" fill="#22d3ee" fillOpacity={0.06} />
              <ReferenceArea x1="18:00" x2="21:00" fill="#22d3ee" fillOpacity={0.06} />
              <XAxis dataKey="hour" stroke="#64748b" fontSize={11} interval={2} />
              <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v: any, n?: any) => [`${fmt(Number(v))} ng/m³`, n]} />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              {SEASONS.map((s) => (
                <Line key={s} type="monotone" dataKey={s} stroke={SEASON_COLORS[s]} strokeWidth={2} dot={false} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* BC/CO */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-slate-100 font-bold text-base">
            <Flame className="w-4 h-4 text-amber-400" />
            BC / CO Ratio (ng/m³ per mg/m³)
          </div>
          <p className="text-xs text-slate-400">
            Diesel engines emit a lot of soot per unit of CO, so the ratio is high. Smouldering biomass emits much more
            CO, so the ratio is lower. Post-monsoon averages{' '}
            <strong className="text-slate-200">{finite(kpis.postMonsoonRatio) ? fmt(kpis.postMonsoonRatio) : '–'}</strong>{' '}
            against <strong className="text-slate-200">{finite(kpis.winterRatio) ? fmt(kpis.winterRatio) : '–'}</strong>{' '}
            in winter, consistent with the crop-residue burning season.
          </p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={ratio} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="hour" stroke="#64748b" fontSize={11} interval={3} />
                <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v: any, n?: any) => [fmt(Number(v)), n]} />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                {SEASONS.map((s) => (
                  <Line key={s} type="monotone" dataKey={s} stroke={SEASON_COLORS[s]} strokeWidth={2} dot={false} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Weekly */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-slate-100 font-bold text-base">
            <CalendarDays className="w-4 h-4 text-cyan-400" />
            Weekday Pattern: Rush Hour vs Night
          </div>
          <p className="text-xs text-slate-400">
            If traffic dominated, rush-hour BC would fall clearly on Sundays. Here it changes only slightly, while
            night-time levels stay high every day of the week. That points to sources that don't follow the work week,
            such as cooking, heating and open burning.
          </p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weekly} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v: any, n?: any) => [`${fmt(Number(v))} ng/m³`, n]} />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Bar dataKey="rush" name="Rush hours (07–10, 18–21)" fill="#22d3ee" radius={[4, 4, 0, 0]} />
                <Bar dataKey="night" name="Night (22–03)" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Tracer correlations */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <div className="flex items-center gap-2 text-slate-100 font-bold text-base">
          <Car className="w-4 h-4 text-cyan-400" />
          Which Gases Move with Black Carbon?
        </div>
        <p className="text-xs text-slate-400">
          Spearman correlation between BC₆ and each co-measured gas. NOx, NO₂ and benzene are traffic tracers; CO,
          PM2.5, NH₃ and SO₂ also come from biomass, coal and waste burning. In winter, BC
          tracks CO far more closely than NOx or NO₂, pointing to incomplete combustion such as biomass and waste
          burning rather than vehicle exhaust alone.
        </p>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={tracerCorr} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="tracer" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} domain={[-0.4, 1]} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v: any, n?: any) => [Number(v).toFixed(2), n]} />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              {SEASONS.map((s) => (
                <Bar key={s} dataKey={s} fill={SEASON_COLORS[s]} radius={[3, 3, 0, 0]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Diwali */}
      {diwali.length > 0 && (
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-slate-100 font-bold text-base">
            <Sparkles className="w-4 h-4 text-rose-400" />
            Festival Burning: Diwali Night vs Surrounding Baseline
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/80 text-slate-400 uppercase font-mono text-[11px] border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-4">Year</th>
                  <th className="py-2.5 px-4">Date</th>
                  <th className="py-2.5 px-4">Event mean</th>
                  <th className="py-2.5 px-4">Event peak</th>
                  <th className="py-2.5 px-4">Baseline mean</th>
                  <th className="py-2.5 px-4">Ratio</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {diwali.map((d, i) => {
                  const suspect = Number(d.baseline_mean) < 1000;
                  return (
                    <tr key={i} className={suspect ? 'text-slate-500' : 'hover:bg-slate-900/50'}>
                      <td className="py-2.5 px-4 font-semibold">{d.year}</td>
                      <td className="py-2.5 px-4">{d.date}</td>
                      <td className="py-2.5 px-4">{fmt(Number(d.event_mean))}</td>
                      <td className="py-2.5 px-4">{fmt(Number(d.event_peak))}</td>
                      <td className="py-2.5 px-4">{fmt(Number(d.baseline_mean))}</td>
                      <td className={`py-2.5 px-4 ${suspect ? '' : Number(d.ratio) > 1.3 ? 'text-rose-300' : 'text-slate-300'}`}>
                        {Number(d.ratio).toFixed(2)}×{suspect ? ' (excluded)' : ''}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {diwali.some((d) => Number(d.baseline_mean) < 1000) && (
            <p className="text-[11px] text-slate-500">
              Greyed-out years have a baseline far below this site's typical levels (median ≈ 3,000 ng/m³), which usually
              indicates an instrument gap or fault. They are excluded from the headline figure.
            </p>
          )}
        </div>
      )}
    </div>
  );
};

const Kpi: React.FC<{ icon: React.ReactNode; title: string; value: string; note: string }> = ({ icon, title, value, note }) => (
  <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
    <div className="flex items-center justify-between">
      <span className="text-[11px] uppercase tracking-wide text-slate-400 font-semibold">{title}</span>
      {icon}
    </div>
    <div className="text-2xl font-bold text-white font-mono">{value}</div>
    <p className="text-[11px] text-slate-400 leading-relaxed">{note}</p>
  </div>
);
