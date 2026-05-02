"use client";

import { motion } from "framer-motion";
import type { HeatmapCell } from "@/types";
import { cn } from "@/lib/utils";

interface TeamHeatmapProps {
  data: HeatmapCell[];
}

function getHeatColor(normalized: number): string {
  if (normalized >= 0.8) return "bg-accent-cyan/70 text-white";
  if (normalized >= 0.6) return "bg-brand-500/60 text-white";
  if (normalized >= 0.4) return "bg-brand-700/50 text-slate-200";
  if (normalized >= 0.2) return "bg-accent-amber/30 text-slate-300";
  return "bg-accent-rose/30 text-slate-400";
}

export function TeamHeatmap({ data }: TeamHeatmapProps) {
  if (!data?.length) return null;

  const teams = [...new Set(data.map(d => d.team))];
  const metrics = [...new Set(data.map(d => d.metric))];

  const getValue = (team: string, metric: string) =>
    data.find(d => d.team === team && d.metric === metric);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr>
            <th className="text-left text-slate-500 font-medium pb-3 pr-4 w-32">Team</th>
            {metrics.map(m => (
              <th key={m} className="text-center text-slate-500 font-medium pb-3 px-1 min-w-[80px]">
                {m}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="space-y-1">
          {teams.map((team, ti) => (
            <tr key={team}>
              <td className="text-slate-300 font-medium pr-4 py-1 text-xs">{team}</td>
              {metrics.map((metric, mi) => {
                const cell = getValue(team, metric);
                if (!cell) return <td key={metric} className="px-1 py-1" />;
                return (
                  <td key={metric} className="px-1 py-1">
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: (ti * metrics.length + mi) * 0.01 }}
                      title={`${cell.value.toFixed(2)}`}
                      className={cn(
                        "h-8 rounded flex items-center justify-center font-mono font-semibold text-[10px]",
                        getHeatColor(cell.normalized)
                      )}
                    >
                      {cell.value.toFixed(0)}
                    </motion.div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
