"use client";

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import type { ROIScenario } from "@/types";
import { formatCurrency, formatPct } from "@/lib/utils";

interface ROIScenariosChartProps {
  data: ROIScenario[];
}

const SCENARIO_COLORS: Record<string, string> = {
  pessimistic: "#f43f5e",
  realistic:   "#6366f1",
  optimistic:  "#10b981",
};

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.[0]) return null;
  const d = payload[0].payload as ROIScenario;
  return (
    <div className="glass-card p-4 border border-slate-700 shadow-xl min-w-[200px]">
      <p className="text-sm font-semibold text-white mb-3">{d.label}</p>
      <div className="space-y-1.5 text-xs">
        <div className="flex justify-between">
          <span className="text-slate-400">ROI</span>
          <span className="text-white font-medium">{formatPct(d.roi_pct)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Net Benefit</span>
          <span className="text-white font-medium">{formatCurrency(d.net_benefit_usd, true)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Break-even</span>
          <span className="text-white font-medium">{d.break_even_months.toFixed(1)} months</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Probability</span>
          <span className="text-white font-medium">{(d.probability * 100).toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
};

export function ROIScenariosChart({ data }: ROIScenariosChartProps) {
  if (!data?.length) return null;

  return (
    <div className="space-y-6">
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
          <XAxis dataKey="label" tick={{ fill: "#64748b", fontSize: 11 }} tickLine={false} axisLine={false} />
          <YAxis tick={{ fill: "#64748b", fontSize: 10 }} tickLine={false} axisLine={false} tickFormatter={v => `${v.toFixed(0)}%`} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.02)" }} />
          <Bar dataKey="roi_pct" radius={[4, 4, 0, 0]} name="ROI %">
            {data.map((entry) => (
              <Cell key={entry.scenario_name} fill={SCENARIO_COLORS[entry.scenario_name] ?? "#6366f1"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-3 gap-3">
        {data.map(s => (
          <div key={s.scenario_name} className="glass-card p-3 space-y-1.5">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: SCENARIO_COLORS[s.scenario_name] }} />
              <span className="text-xs font-medium text-slate-300">{s.label}</span>
            </div>
            <p className="text-xl font-bold text-white">{formatPct(s.roi_pct)}</p>
            <p className="text-[10px] text-slate-500">
              {formatCurrency(s.cumulative_savings_12m, true)} cumulative / 12m
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
