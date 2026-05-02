"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { analyticsApi, teamsApi } from "@/lib/api";
import { TopBar } from "@/components/layout/TopBar";
import { TeamRankingTable } from "@/components/executive/TeamRankingTable";
import { TeamRadarChart } from "@/components/charts/TeamRadarChart";
import { AOVIScore } from "@/components/kpi/AOVIScore";
import { formatCurrency, getTierColor, cn } from "@/lib/utils";
import { Search, ChevronDown } from "lucide-react";

const TIER_BADGES: Record<string, string> = {
  pioneer:  "bg-accent-cyan/10 text-accent-cyan border-accent-cyan/20",
  advanced: "bg-accent-emerald/10 text-accent-emerald border-accent-emerald/20",
  standard: "bg-brand-400/10 text-brand-400 border-brand-400/20",
  lagging:  "bg-accent-amber/10 text-accent-amber border-accent-amber/20",
};

export default function TeamsPage() {
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<string | null>(null);

  const { data: kpis } = useQuery({ queryKey: ["team-kpis"], queryFn: analyticsApi.getTeamKPIs });
  const { data: radar } = useQuery({ queryKey: ["radar"], queryFn: analyticsApi.getRadar });
  const { data: rankings } = useQuery({ queryKey: ["rankings"], queryFn: analyticsApi.getRankings });

  const teams = kpis?.teams ?? [];
  const filtered = teams.filter(t =>
    t.team_name.toLowerCase().includes(search.toLowerCase()) ||
    t.domain.toLowerCase().includes(search.toLowerCase())
  );

  const selectedTeam = selected ? teams.find(t => t.team_id === selected) : null;

  return (
    <div className="min-h-screen">
      <TopBar title="Team Intelligence" subtitle="Engineering teams · AOVI rankings · Performance benchmarks" />

      <div className="p-6 space-y-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {teams.slice(0, 4).map((team, i) => (
            <motion.div
              key={team.team_id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
              className={cn(
                "glass-card p-4 cursor-pointer transition-all duration-200",
                selected === team.team_id
                  ? "border-brand-500/50 shadow-glow-brand"
                  : "hover:border-slate-700"
              )}
              onClick={() => setSelected(selected === team.team_id ? null : team.team_id)}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="text-sm font-semibold text-white">{team.team_name}</p>
                  <p className="text-[10px] text-slate-500">{team.domain}</p>
                </div>
                <span className={cn(
                  "text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-full border",
                  TIER_BADGES["pioneer"] // placeholder
                )}>
                  {team.performance_tier?.split(" ")[0]}
                </span>
              </div>
              <AOVIScore
                score={team.aovi_score}
                rank={team.aovi_rank}
                tier={team.performance_tier}
                teamName={team.team_name}
                compact
              />
            </motion.div>
          ))}
        </div>

        <AnimatePresence>
          {selectedTeam && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="glass-card p-5 border-brand-600/30"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold text-white">{selectedTeam.team_name} — Deep Dive</h3>
                  <p className="text-sm text-slate-400">{selectedTeam.domain} · {selectedTeam.team_size} engineers</p>
                </div>
                <button onClick={() => setSelected(null)} className="text-slate-500 hover:text-white transition-colors">
                  ✕
                </button>
              </div>
              <div className="grid grid-cols-2 lg:grid-cols-6 gap-3 text-center">
                {[
                  { label: "Velocity",      value: selectedTeam.avg_velocity.toFixed(1) },
                  { label: "Quality",       value: `${selectedTeam.code_quality_score.toFixed(0)}/100` },
                  { label: "Test Coverage", value: `${selectedTeam.test_coverage_pct.toFixed(0)}%` },
                  { label: "AI Adoption",   value: `${selectedTeam.ai_adoption_rate.toFixed(0)}%` },
                  { label: "AI Cost",       value: formatCurrency(selectedTeam.ai_cost_usd, true) },
                  { label: "AOVI Score",    value: selectedTeam.aovi_score.toFixed(1) },
                ].map(m => (
                  <div key={m.label} className="glass-card p-3">
                    <p className="text-[10px] text-slate-500 uppercase tracking-widest">{m.label}</p>
                    <p className="text-lg font-bold text-white mt-1">{m.value}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 glass-card p-5">
            <div className="flex items-center gap-3 mb-4">
              <h3 className="section-header flex-1">All Teams · Full Rankings</h3>
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-slate-500" />
                <input
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Filter teams..."
                  className="bg-surface-800 border border-slate-700 rounded-lg pl-7 pr-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-brand-500 w-40"
                />
              </div>
            </div>
            {filtered.length > 0 && <TeamRankingTable teams={filtered} />}
          </div>

          <div className="glass-card p-5">
            <h3 className="section-header mb-1">Capability Radar</h3>
            <p className="section-sub mb-3">Top 3 teams · 6 dimensions</p>
            {radar && <TeamRadarChart data={radar} />}
          </div>
        </div>
      </div>
    </div>
  );
}
