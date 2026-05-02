"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { finopsApi } from "@/lib/api";
import { TopBar } from "@/components/layout/TopBar";
import { KPICard } from "@/components/kpi/KPICard";
import { ROIScenariosChart } from "@/components/charts/ROIScenariosChart";
import { CostForecastChart } from "@/components/charts/CostForecastChart";
import { CostBreakdownChart } from "@/components/charts/CostBreakdownChart";
import { formatCurrency, formatPct, cn } from "@/lib/utils";
import { DollarSign, TrendingUp, Target, Zap, CheckCircle, Clock, ChevronRight } from "lucide-react";

export default function FinOpsPage() {
  const { data: snapshot } = useQuery({ queryKey: ["finops-snapshot"], queryFn: finopsApi.getSnapshot });
  const { data: scenarios } = useQuery({ queryKey: ["roi-scenarios"], queryFn: finopsApi.getROIScenarios });
  const { data: monteCarlo } = useQuery({ queryKey: ["monte-carlo"], queryFn: finopsApi.getMonteCarlo });
  const { data: forecast } = useQuery({ queryKey: ["cost-forecast"], queryFn: finopsApi.getCostForecast });
  const { data: breakdown } = useQuery({ queryKey: ["cost-breakdown"], queryFn: finopsApi.getCostBreakdown });
  const { data: recommendations } = useQuery({ queryKey: ["finops-recs"], queryFn: finopsApi.getRecommendations });

  const effortColor = (e: string) =>
    e === "Low" ? "text-accent-emerald" : e === "Medium" ? "text-accent-amber" : "text-accent-rose";

  return (
    <div className="min-h-screen">
      <TopBar title="FinOps Intelligence" subtitle="ROI Modeling · Cost Optimization · Scenario Analysis · Forecasting" />

      <div className="p-6 space-y-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Annual Savings"
            value={formatCurrency(snapshot?.total_annual_savings_usd ?? 0, true)}
            delta={22.4}
            icon={<DollarSign className="w-4 h-4" />}
            index={0}
          />
          <KPICard
            label="Net ROI"
            value={snapshot ? formatPct(snapshot.roi_pct) : "—"}
            delta={snapshot?.roi_pct}
            icon={<TrendingUp className="w-4 h-4" />}
            index={1}
          />
          <KPICard
            label="Break-Even"
            value={snapshot ? `${snapshot.break_even_months.toFixed(1)} mo` : "—"}
            icon={<Target className="w-4 h-4" />}
            index={2}
          />
          <KPICard
            label="Total AI Spend"
            value={formatCurrency(snapshot?.total_ai_cost_usd ?? 0, true)}
            delta={8.1}
            icon={<Zap className="w-4 h-4" />}
            index={3}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-card p-5">
            <h3 className="section-header mb-1">ROI Scenario Analysis</h3>
            <p className="section-sub mb-4">Pessimistic · Realistic · Optimistic projections over 12 months</p>
            {scenarios && <ROIScenariosChart data={scenarios} />}
          </div>

          <div className="glass-card p-5">
            <h3 className="section-header mb-1">Monte Carlo Simulation</h3>
            <p className="section-sub mb-4">
              {monteCarlo?.simulation_count?.toLocaleString() ?? "5,000"} simulations · ROI probability distribution
            </p>
            {monteCarlo && (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { label: "P10 (Bear)", value: monteCarlo.p10_roi_pct, color: "text-accent-rose" },
                    { label: "P50 (Base)", value: monteCarlo.p50_roi_pct, color: "text-brand-400" },
                    { label: "P90 (Bull)", value: monteCarlo.p90_roi_pct, color: "text-accent-emerald" },
                  ].map(s => (
                    <div key={s.label} className="glass-card p-3 text-center">
                      <p className="text-[10px] text-slate-500 mb-1">{s.label}</p>
                      <p className={`text-xl font-bold ${s.color}`}>{s.value.toFixed(0)}%</p>
                    </div>
                  ))}
                </div>

                <div className="glass-card p-4">
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-sm text-slate-300">Probability of Positive ROI</span>
                    <span className="text-lg font-bold text-accent-emerald">
                      {(monteCarlo.probability_positive_roi * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <motion.div
                      className="h-2 rounded-full bg-gradient-to-r from-brand-500 to-accent-emerald"
                      initial={{ width: 0 }}
                      animate={{ width: `${monteCarlo.probability_positive_roi * 100}%` }}
                      transition={{ duration: 1.2, ease: "easeOut" }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-slate-600 mt-1">
                    <span>Mean ROI: {monteCarlo.mean_roi_pct.toFixed(0)}%</span>
                    <span>Std Dev: ±{monteCarlo.std_deviation.toFixed(0)}%</span>
                  </div>
                </div>

                <div className="flex items-end gap-0.5 h-16">
                  {monteCarlo.distribution.slice(0, 60).map((v, i) => {
                    const height = Math.max(2, Math.min(100, ((v + 100) / 400) * 100));
                    return (
                      <div
                        key={i}
                        className="flex-1 rounded-t"
                        style={{
                          height: `${height}%`,
                          backgroundColor: v > 0 ? "#6366f1" : "#f43f5e",
                          opacity: 0.6,
                        }}
                      />
                    );
                  })}
                </div>
                <p className="text-[10px] text-slate-600 text-center">ROI distribution histogram</p>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 glass-card p-5">
            <h3 className="section-header mb-1">AI Cost Forecast</h3>
            <p className="section-sub mb-4">Trend analysis with 95% confidence interval · 6-month projection</p>
            {forecast && <CostForecastChart data={forecast} />}
          </div>

          <div className="glass-card p-5">
            <h3 className="section-header mb-1">Cost Breakdown</h3>
            <p className="section-sub mb-4">By use-case category</p>
            {breakdown && <CostBreakdownChart data={breakdown} />}
          </div>
        </div>

        {snapshot && (
          <div className="glass-card p-5">
            <h3 className="section-header mb-4">Savings Attribution</h3>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {[
                { label: "Productivity Gains", value: snapshot.productivity_savings_usd, pct: snapshot.productivity_savings_usd / snapshot.total_annual_savings_usd * 100, color: "from-brand-500 to-brand-700" },
                { label: "Quality & Incident Reduction", value: snapshot.quality_savings_usd, pct: snapshot.quality_savings_usd / snapshot.total_annual_savings_usd * 100, color: "from-accent-emerald to-green-700" },
                { label: "Documentation Automation", value: snapshot.documentation_savings_usd, pct: snapshot.documentation_savings_usd / snapshot.total_annual_savings_usd * 100, color: "from-accent-cyan to-blue-600" },
              ].map((item) => (
                <div key={item.label} className="glass-card p-4">
                  <p className="text-xs text-slate-400 mb-1">{item.label}</p>
                  <p className="text-2xl font-bold text-white mb-2">{formatCurrency(item.value, true)}</p>
                  <div className="w-full bg-slate-800 rounded-full h-1.5">
                    <motion.div
                      className={`h-1.5 rounded-full bg-gradient-to-r ${item.color}`}
                      initial={{ width: 0 }}
                      animate={{ width: `${item.pct}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                    />
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1">{item.pct.toFixed(0)}% of total savings</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {recommendations && recommendations.length > 0 && (
          <div className="glass-card p-5">
            <h3 className="section-header mb-4">FinOps Optimization Recommendations</h3>
            <div className="space-y-3">
              {recommendations.map((rec, i) => (
                <motion.div
                  key={rec.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.06 }}
                  className="glass-card p-4 flex items-start gap-4"
                >
                  <div className={cn(
                    "w-2 h-full min-h-[40px] rounded-full flex-shrink-0",
                    rec.priority === "HIGH" ? "bg-accent-rose" :
                    rec.priority === "MEDIUM" ? "bg-accent-amber" : "bg-accent-emerald"
                  )} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <p className="text-sm font-semibold text-white">{rec.title}</p>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className="text-xs font-bold text-accent-emerald">
                          {formatCurrency(rec.estimated_savings_usd, true)}/yr
                        </span>
                      </div>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 mb-2">{rec.description}</p>
                    <div className="flex items-center gap-3">
                      <span className={cn("text-[10px] font-medium", effortColor(rec.implementation_effort))}>
                        {rec.implementation_effort} effort
                      </span>
                      <span className="text-[10px] text-slate-600">·</span>
                      <span className="text-[10px] text-slate-500">
                        Impact score: {(rec.impact_score * 100).toFixed(0)}/100
                      </span>
                      <span className="text-[10px] text-slate-500 bg-slate-800 px-2 py-0.5 rounded-full">
                        {rec.category}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
