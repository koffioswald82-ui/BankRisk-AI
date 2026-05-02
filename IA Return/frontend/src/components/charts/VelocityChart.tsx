"use client";

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { CHART_COLORS } from "@/lib/utils";
import type { TeamTrend } from "@/types";

interface VelocityChartProps {
  data: TeamTrend[];
  topN?: number;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-card p-3 border border-slate-700 shadow-xl">
      <p className="text-xs text-slate-400 mb-2">{label}</p>
      {payload.map((p: any) => (
        <div key={p.name} className="flex items-center gap-2 text-xs">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: p.color }} />
          <span className="text-slate-300">{p.name}:</span>
          <span className="text-white font-medium">{p.value?.toFixed(2)}</span>
        </div>
      ))}
    </div>
  );
};

export function VelocityChart({ data, topN = 5 }: VelocityChartProps) {
  if (!data?.length) return null;

  const topTeams = data.slice(0, topN);

  const periods = topTeams[0]?.series.map(s => s.period) ?? [];
  const chartData = periods.map(period => {
    const point: Record<string, any> = { period };
    topTeams.forEach(team => {
      const match = team.series.find(s => s.period === period);
      point[team.team_name] = match?.value ?? 0;
    });
    return point;
  });

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis
          dataKey="period"
          tick={{ fill: "#64748b", fontSize: 10 }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          tick={{ fill: "#64748b", fontSize: 10 }}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{ fontSize: "11px", paddingTop: "12px" }}
          iconType="circle"
          iconSize={6}
        />
        {topTeams.map((team, i) => (
          <Line
            key={team.team_id}
            type="monotone"
            dataKey={team.team_name}
            stroke={CHART_COLORS[i % CHART_COLORS.length]}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, strokeWidth: 0 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
