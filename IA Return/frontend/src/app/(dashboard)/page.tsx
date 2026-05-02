"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  DollarSign, TrendingUp, Users, Zap, Target, BarChart3, Award, AlertTriangle,
} from "lucide-react";

import { analyticsApi, finopsApi, insightsApi } from "@/lib/api";
import { formatCurrency, formatNumber, formatPct } from "@/lib/utils";
import { TopBar } from "@/components/layout/TopBar";
import { KPICard } from "@/components/kpi/KPICard";
import { VelocityChart } from "@/components/charts/VelocityChart";
import { TeamRankingTable } from "@/components/executive/TeamRankingTable";
import { InsightCard } from "@/components/executive/InsightCard";
import { CostBreakdownChart } from "@/components/charts/CostBreakdownChart";

export default function ExecutiveOverviewPage() {
  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ["overview"],
    queryFn: analyticsApi.getOverview,
  });

  const { data: teamKPIs } = useQuery({
    queryKey: ["team-kpis"],
    queryFn: analyticsApi.getTeamKPIs,
  });

  const { data: velocityData } = useQuery({
    queryKey: ["velocity-ts"],
    queryFn: analyticsApi.getVelocityTimeseries,
  });

  const { data: rankings } = useQuery({
    queryKey: ["rankings"],
    queryFn: analyticsApi.getRankings,
  });

  const { data: insights } = useQuery({
    queryKey: ["insights"],
    queryFn: insightsApi.getStrategicInsights,
  });

  const { data: briefing } = useQuery({
    queryKey: ["exec-briefing"],
    queryFn: insightsApi.getExecutiveBriefing,
  });

  const { data: costBreakdown } = useQuery({
    queryKey: ["cost-breakdown"],
    queryFn: finopsApi.getCostBreakdown,
  });

  const topTeams = rankings?.rankings.slice(0, 8) ?? [];
  const topInsights = insights?.insights.slice(0, 4) ?? [];

  return (
    <div className="min-h-screen">
      <TopBar
        title="Executive Intelligence Center"
        subtitle="AI Generative Performance & FinOps Intelligence Framework"
      />

      <div className="p-6 space-y-6">
        {briefing && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-5 border-l-4 border-brand-500"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-[10px] text-brand-400 uppercase tracking-widest font-semibold mb-1">
                  Executive Briefing · Q1–Q4 2024
                </p>
                <h2 className="text-lg font-bold text-white mb-1">{briefing.headline}</h2>
                <p className="text-sm text-slate-400">{briefing.financial_summary}</p>
              </div>
              <div className="text-right flex-shrink-0 ml-6">
                <p className="text-[10px] text-slate-500 uppercase tracking-widest">AI Maturity</p>
                <p className="text-3xl font-bold text-gradient-brand">{briefing.ai_maturity_score.toFixed(0)}</p>
                <p className="text-[10px] text-slate-500">/ 100 score</p>
              </div>
            </div>
          </motion.div>
        )}

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Global AI ROI"
            value={overviewLoading ? "—" : `${overview?.global_roi_pct?.toFixed(0) ?? 0}%`}
            delta={overview?.global_roi_pct ? overview.global_roi_pct - 210 : undefined}
            deltaLabel="vs baseline"
            icon={<TrendingUp className="w-4 h-4" />}
            accentColor="brand"
            loading={overviewLoading}
            index={0}
          />
          <KPICard
            label="Estimated Annual Savings"
            value={overviewLoading ? "—" : formatCurrency(overview?.estimated_savings_usd ?? 0, true)}
            delta={22.4}
            deltaLabel="YoY"
            icon={<DollarSign className="w-4 h-4" />}
            accentColor="accent-emerald"
            loading={overviewLoading}
            index={1}
          />
          <KPICard
            label="Total AI Investment"
            value={overviewLoading ? "—" : formatCurrency(overview?.total_ai_cost_usd ?? 0, true)}
            delta={8.1}
            deltaLabel="MoM"
            icon={<Zap className="w-4 h-4" />}
            accentColor="accent-cyan"
            loading={overviewLoading}
            index={2}
          />
          <KPICard
            label="Tokens Consumed"
            value={overviewLoading ? "—" : formatNumber(overview?.total_tokens_consumed ?? 0)}
            delta={15.3}
            deltaLabel="vs last period"
            icon={<BarChart3 className="w-4 h-4" />}
            accentColor="accent-violet"
            loading={overviewLoading}
            index={3}
          />
          <KPICard
            label="Productivity Gain"
            value={overviewLoading ? "—" : `+${overview?.avg_productivity_gain_pct?.toFixed(1) ?? 0}%`}
            delta={overview?.avg_productivity_gain_pct}
            icon={<Target className="w-4 h-4" />}
            accentColor="brand"
            loading={overviewLoading}
            index={4}
          />
          <KPICard
            label="Quality Improvement"
            value={overviewLoading ? "—" : `+${overview?.avg_quality_improvement_pct?.toFixed(1) ?? 0}%`}
            delta={overview?.avg_quality_improvement_pct}
            icon={<Award className="w-4 h-4" />}
            accentColor="accent-emerald"
            loading={overviewLoading}
            index={5}
          />
          <KPICard
            label="AI Adoption Rate"
            value={overviewLoading ? "—" : `${overview?.global_ai_adoption_rate?.toFixed(0) ?? 0}%`}
            delta={12.5}
            deltaLabel="QoQ"
            icon={<Users className="w-4 h-4" />}
            accentColor="accent-cyan"
            loading={overviewLoading}
            index={6}
          />
          <KPICard
            label="Avg AOVI Score"
            value={overviewLoading ? "—" : `${overview?.avg_aovi_score?.toFixed(1) ?? 0}`}
            delta={7.2}
            deltaLabel="vs benchmark"
            icon={<Target className="w-4 h-4" />}
            accentColor="accent-amber"
            loading={overviewLoading}
            index={7}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 glass-card p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="section-header">Engineering Velocity Trends</h3>
                <p className="section-sub">Story points per engineer · Top 5 teams · 12-month view</p>
              </div>
            </div>
            {velocityData && <VelocityChart data={velocityData} topN={5} />}
          </div>

          <div className="glass-card p-5">
            <div className="mb-4">
              <h3 className="section-header">AI Cost Distribution</h3>
              <p className="section-sub">By request type · Current period</p>
            </div>
            {costBreakdown && <CostBreakdownChart data={costBreakdown} />}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          <div className="lg:col-span-3 glass-card p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="section-header">Team AOVI Rankings</h3>
                <p className="section-sub">AI Operational Value Index · All engineering teams</p>
              </div>
              <span className="text-[10px] text-brand-400 bg-brand-600/20 border border-brand-600/30 px-2 py-1 rounded-full">
                Proprietary Score
              </span>
            </div>
            {topTeams.length > 0 && <TeamRankingTable teams={topTeams} />}
          </div>

          <div className="lg:col-span-2 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="section-header">Strategic Insights</h3>
              {insights && (
                <span className="text-[10px] text-accent-rose bg-accent-rose/10 border border-accent-rose/20 px-2 py-1 rounded-full">
                  {insights.critical_count} Critical
                </span>
              )}
            </div>
            {topInsights.map((insight, i) => (
              <InsightCard key={insight.id} insight={insight} index={i} />
            ))}
            {insights && insights.total_insights > 4 && (
              <p className="text-xs text-slate-500 text-center pt-1">
                +{insights.total_insights - 4} more insights in Governance module
              </p>
            )}
          </div>
        </div>

        {briefing && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold text-accent-emerald mb-3 flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-accent-emerald" />
                Key Wins
              </h3>
              <ul className="space-y-2">
                {briefing.key_wins.map((win, i) => (
                  <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                    <span className="text-accent-emerald mt-0.5">✓</span>
                    {win}
                  </li>
                ))}
              </ul>
            </div>
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold text-accent-amber mb-3 flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-accent-amber" />
                Risks & Flags
              </h3>
              <ul className="space-y-2">
                {briefing.risks.map((risk, i) => (
                  <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                    <AlertTriangle className="w-3 h-3 text-accent-amber mt-0.5 flex-shrink-0" />
                    {risk}
                  </li>
                ))}
              </ul>
            </div>
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold text-brand-400 mb-3 flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-brand-400" />
                Strategic Recommendations
              </h3>
              <ul className="space-y-2">
                {briefing.recommendations.map((rec, i) => (
                  <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                    <span className="text-brand-400 mt-0.5">→</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
