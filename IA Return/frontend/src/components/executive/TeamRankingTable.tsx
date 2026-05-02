"use client";

import { motion } from "framer-motion";
import { cn, formatCurrency, getPerformanceTierColor, getAOVIGradient } from "@/lib/utils";
import type { TeamKPI } from "@/types";

interface TeamRankingTableProps {
  teams: TeamKPI[];
}

export function TeamRankingTable({ teams }: TeamRankingTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-slate-800">
            <th className="text-left text-slate-500 font-medium pb-3 pr-4">#</th>
            <th className="text-left text-slate-500 font-medium pb-3 pr-4">Team</th>
            <th className="text-right text-slate-500 font-medium pb-3 pr-4">AOVI</th>
            <th className="text-right text-slate-500 font-medium pb-3 pr-4">Velocity</th>
            <th className="text-right text-slate-500 font-medium pb-3 pr-4">Quality</th>
            <th className="text-right text-slate-500 font-medium pb-3 pr-4">AI Adoption</th>
            <th className="text-right text-slate-500 font-medium pb-3 pr-4">AI Cost</th>
            <th className="text-left text-slate-500 font-medium pb-3">Tier</th>
          </tr>
        </thead>
        <tbody>
          {teams.map((team, i) => (
            <motion.tr
              key={team.team_id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
              className="border-b border-slate-800/40 hover:bg-surface-800/30 transition-colors"
            >
              <td className="py-3 pr-4">
                <span className={cn(
                  "w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold",
                  i === 0 ? "bg-accent-amber/20 text-accent-amber" :
                  i === 1 ? "bg-slate-500/20 text-slate-400" :
                  i === 2 ? "bg-orange-700/20 text-orange-500" :
                  "bg-slate-800 text-slate-600"
                )}>
                  {i + 1}
                </span>
              </td>
              <td className="py-3 pr-4">
                <div>
                  <p className="text-slate-200 font-medium">{team.team_name}</p>
                  <p className="text-slate-600 text-[10px]">{team.domain} · {team.team_size} engineers</p>
                </div>
              </td>
              <td className="py-3 pr-4 text-right">
                <span className={cn(
                  "font-bold text-sm bg-gradient-to-r bg-clip-text text-transparent",
                  getAOVIGradient(team.aovi_score)
                )}>
                  {team.aovi_score.toFixed(1)}
                </span>
              </td>
              <td className="py-3 pr-4 text-right text-slate-300">{team.avg_velocity.toFixed(1)}</td>
              <td className="py-3 pr-4 text-right text-slate-300">{team.code_quality_score.toFixed(0)}</td>
              <td className="py-3 pr-4 text-right">
                <div className="flex items-center justify-end gap-2">
                  <div className="w-16 bg-slate-800 rounded-full h-1.5">
                    <div
                      className="h-1.5 rounded-full bg-gradient-to-r from-brand-500 to-accent-cyan"
                      style={{ width: `${team.ai_adoption_rate}%` }}
                    />
                  </div>
                  <span className="text-slate-300 w-8 text-right">{team.ai_adoption_rate.toFixed(0)}%</span>
                </div>
              </td>
              <td className="py-3 pr-4 text-right text-slate-300">{formatCurrency(team.ai_cost_usd, true)}</td>
              <td className="py-3">
                <span className={cn("font-semibold text-[10px]", getPerformanceTierColor(team.performance_tier))}>
                  {team.performance_tier}
                </span>
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
