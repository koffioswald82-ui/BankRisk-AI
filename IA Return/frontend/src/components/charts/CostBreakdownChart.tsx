"use client";

import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import type { CostBreakdown } from "@/types";
import { formatCurrency } from "@/lib/utils";

const COLORS = ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#f43f5e"];

interface CostBreakdownChartProps {
  data: CostBreakdown[];
}

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.[0]) return null;
  const d = payload[0].payload as CostBreakdown;
  return (
    <div className="glass-card p-3 border border-slate-700 shadow-xl">
      <p className="text-sm font-semibold text-white mb-1">{d.category}</p>
      <p className="text-xs text-slate-300">{formatCurrency(d.amount_usd)}</p>
      <p className="text-xs text-slate-500">{d.percentage.toFixed(1)}% of total</p>
      <p className={`text-xs ${d.trend_pct >= 0 ? "text-accent-rose" : "text-accent-emerald"}`}>
        {d.trend_pct >= 0 ? "↑" : "↓"} {Math.abs(d.trend_pct).toFixed(1)}% MoM
      </p>
    </div>
  );
};

export function CostBreakdownChart({ data }: CostBreakdownChartProps) {
  if (!data?.length) return null;

  return (
    <div className="flex items-center gap-6">
      <ResponsiveContainer width={200} height={200}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={3}
            dataKey="amount_usd"
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} strokeWidth={0} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      <div className="flex-1 space-y-2">
        {data.map((item, i) => (
          <div key={item.category} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
              <span className="text-xs text-slate-300">{item.category}</span>
            </div>
            <div className="text-right">
              <p className="text-xs font-medium text-white">{formatCurrency(item.amount_usd, true)}</p>
              <p className="text-[10px] text-slate-500">{item.percentage.toFixed(0)}%</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
