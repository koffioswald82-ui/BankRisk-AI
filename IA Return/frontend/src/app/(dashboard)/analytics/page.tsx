"use client";

import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";
import { TopBar } from "@/components/layout/TopBar";
import { VelocityChart } from "@/components/charts/VelocityChart";
import { TeamHeatmap } from "@/components/charts/TeamHeatmap";
import { TeamRadarChart } from "@/components/charts/TeamRadarChart";
import { KPICard } from "@/components/kpi/KPICard";
import { AOVIScore } from "@/components/kpi/AOVIScore";
import { formatCurrency } from "@/lib/utils";
import { Activity, GitBranch, Bug, Layers } from "lucide-react";

export default function AnalyticsPage() {
  const { data: teamKPIs } = useQuery({ queryKey: ["team-kpis"], queryFn: analyticsApi.getTeamKPIs });
  const { data: velocityData } = useQuery({ queryKey: ["velocity-ts"], queryFn: analyticsApi.getVelocityTimeseries });
  const { data: qualityData } = useQuery({ queryKey: ["quality-ts"], queryFn: analyticsApi.getQualityTimeseries });
  const { data: heatmap } = useQuery({ queryKey: ["heatmap"], queryFn: analyticsApi.getHeatmap });
  const { data: radar } = useQuery({ queryKey: ["radar"], queryFn: analyticsApi.getRadar });
  const { data: rankings } = useQuery({ queryKey: ["rankings"], queryFn: analyticsApi.getRankings });

  const teams = teamKPIs?.teams ?? [];
  const avgVelocity = teams.length ? teams.reduce((s, t) => s + t.avg_velocity, 0) / teams.length : 0;
  const avgQuality = teams.length ? teams.reduce((s, t) => s + t.code_quality_score, 0) / teams.length : 0;
  const avgCoverage = teams.length ? teams.reduce((s, t) => s + t.test_coverage_pct, 0) / teams.length : 0;
  const totalCommits = teams.reduce((s, t) => s + t.commits_count, 0);

  return (
    <div className="min-h-screen">
      <TopBar title="Analytics Engine" subtitle="Engineering KPIs · Productivity · Quality · Velocity" />

      <div className="p-6 space-y-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard label="Avg Velocity" value={avgVelocity.toFixed(1)} icon={<Activity className="w-4 h-4" />} delta={14.2} index={0} />
          <KPICard label="Code Quality Score" value={`${avgQuality.toFixed(0)}/100`} icon={<Layers className="w-4 h-4" />} delta={8.5} index={1} />
          <KPICard label="Test Coverage" value={`${avgCoverage.toFixed(0)}%`} icon={<GitBranch className="w-4 h-4" />} delta={6.1} index={2} />
          <KPICard label="Total Commits" value={totalCommits.toLocaleString()} icon={<Bug className="w-4 h-4" />} delta={22.7} index={3} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-card p-5">
            <h3 className="section-header mb-1">Velocity Trend</h3>
            <p className="section-sub mb-4">Sprint velocity per engineer · 12 months</p>
            {velocityData && <VelocityChart data={velocityData} topN={6} />}
          </div>
          <div className="glass-card p-5">
            <h3 className="section-header mb-1">Code Quality Trend</h3>
            <p className="section-sub mb-4">Quality score (0–100) by team · 12 months</p>
            {qualityData && <VelocityChart data={qualityData} topN={6} />}
          </div>
        </div>

        <div className="glass-card p-5">
          <h3 className="section-header mb-1">KPI Performance Heatmap</h3>
          <p className="section-sub mb-5">Multi-metric comparison · All teams</p>
          {heatmap && <TeamHeatmap data={heatmap} />}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-card p-5">
            <h3 className="section-header mb-1">Team Capability Radar</h3>
            <p className="section-sub mb-4">Multi-dimensional performance · Top 3 teams</p>
            {radar && <TeamRadarChart data={radar} />}
          </div>

          <div className="glass-card p-5">
            <h3 className="section-header mb-1">AOVI Scoreboard</h3>
            <p className="section-sub mb-4">AI Operational Value Index · All teams ranked</p>
            <div className="grid grid-cols-2 gap-3">
              {(rankings?.rankings ?? []).slice(0, 6).map(team => (
                <div key={team.team_id} className="glass-card p-3 flex items-center gap-3">
                  <AOVIScore
                    score={team.aovi_score}
                    rank={team.aovi_rank}
                    tier={team.performance_tier}
                    teamName={team.team_name}
                    compact
                  />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
