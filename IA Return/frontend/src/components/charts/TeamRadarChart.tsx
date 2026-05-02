"use client";

import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  ResponsiveContainer, Tooltip, Legend,
} from "recharts";
import type { TeamRadar } from "@/types";
import { CHART_COLORS } from "@/lib/utils";

interface TeamRadarChartProps {
  data: TeamRadar[];
  selectedTeams?: string[];
}

export function TeamRadarChart({ data, selectedTeams }: TeamRadarChartProps) {
  if (!data?.length) return null;

  const teams = selectedTeams
    ? data.filter(t => selectedTeams.includes(t.team_id))
    : data.slice(0, 3);

  if (!teams.length) return null;

  const metrics = teams[0].data.map(d => d.metric);
  const chartData = metrics.map(metric => {
    const point: Record<string, any> = { metric };
    teams.forEach(team => {
      const val = team.data.find(d => d.metric === metric);
      point[team.team_name] = val?.value ?? 0;
    });
    return point;
  });

  return (
    <ResponsiveContainer width="100%" height={320}>
      <RadarChart data={chartData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
        <PolarGrid stroke="rgba(255,255,255,0.06)" />
        <PolarAngleAxis
          dataKey="metric"
          tick={{ fill: "#64748b", fontSize: 10 }}
          tickLine={false}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "1px solid #334155",
            borderRadius: "8px",
            fontSize: "12px",
            color: "#e2e8f0",
          }}
          formatter={(value: number) => [`${value.toFixed(1)}`, ""]}
        />
        <Legend
          wrapperStyle={{ fontSize: "11px", paddingTop: "12px" }}
          iconType="circle"
          iconSize={6}
        />
        {teams.map((team, i) => (
          <Radar
            key={team.team_id}
            name={team.team_name}
            dataKey={team.team_name}
            stroke={CHART_COLORS[i % CHART_COLORS.length]}
            fill={CHART_COLORS[i % CHART_COLORS.length]}
            fillOpacity={0.08}
            strokeWidth={2}
          />
        ))}
      </RadarChart>
    </ResponsiveContainer>
  );
}
