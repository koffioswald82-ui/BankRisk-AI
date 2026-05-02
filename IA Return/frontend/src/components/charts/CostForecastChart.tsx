"use client";

import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from "recharts";
import type { ForecastPoint } from "@/types";
import { formatCurrency } from "@/lib/utils";

interface CostForecastChartProps {
  data: ForecastPoint[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-card p-3 border border-slate-700 shadow-xl min-w-[160px]">
      <p className="text-xs text-slate-400 mb-2">{label}</p>
      {payload.map((p: any) => (
        <div key={p.name} className="flex justify-between gap-4 text-xs">
          <span className="text-slate-400">{p.name}:</span>
          <span className="text-white font-medium">{formatCurrency(p.value ?? 0)}</span>
        </div>
      ))}
    </div>
  );
};

export function CostForecastChart({ data }: CostForecastChartProps) {
  if (!data?.length) return null;

  const forecastStart = data.find(d => d.actual === null)?.period;
  const actualCount = data.filter(d => d.actual !== null).length;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ComposedChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
        <defs>
          <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="ciGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.08} />
            <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis dataKey="period" tick={{ fill: "#64748b", fontSize: 10 }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fill: "#64748b", fontSize: 10 }} tickLine={false} axisLine={false} tickFormatter={v => `$${(v/1000).toFixed(0)}K`} />
        <Tooltip content={<CustomTooltip />} />
        {forecastStart && (
          <ReferenceLine
            x={forecastStart}
            stroke="#6366f1"
            strokeDasharray="4 4"
            strokeOpacity={0.5}
            label={{ value: "Forecast →", position: "top", fill: "#6366f1", fontSize: 10 }}
          />
        )}
        <Area type="monotone" dataKey="upper_bound" stroke="none" fill="url(#ciGrad)" name="Upper CI" />
        <Area type="monotone" dataKey="lower_bound" stroke="none" fill="white" fillOpacity={0} name="Lower CI" />
        <Line type="monotone" dataKey="actual" stroke="#10b981" strokeWidth={2.5} dot={false} name="Actual" connectNulls={false} />
        <Line type="monotone" dataKey="forecast" stroke="#6366f1" strokeWidth={2} strokeDasharray="5 3" dot={false} name="Forecast" />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
