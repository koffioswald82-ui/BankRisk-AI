"use client";

import { useQuery } from "@tanstack/react-query";
import { finopsApi, analyticsApi } from "@/lib/api";
import { TopBar } from "@/components/layout/TopBar";
import { CostForecastChart } from "@/components/charts/CostForecastChart";
import { ROIScenariosChart } from "@/components/charts/ROIScenariosChart";
import { VelocityChart } from "@/components/charts/VelocityChart";
import { KPICard } from "@/components/kpi/KPICard";
import { formatCurrency, formatPct } from "@/lib/utils";
import { TrendingUp, DollarSign, Zap, Clock } from "lucide-react";

export default function ForecastingPage() {
  const { data: forecast } = useQuery({ queryKey: ["cost-forecast"], queryFn: finopsApi.getCostForecast });
  const { data: scenarios } = useQuery({ queryKey: ["roi-scenarios"], queryFn: finopsApi.getROIScenarios });
  const { data: monteCarlo } = useQuery({ queryKey: ["monte-carlo"], queryFn: finopsApi.getMonteCarlo });
  const { data: aiCostTS } = useQuery({ queryKey: ["ai-cost-ts"], queryFn: analyticsApi.getAICostTimeseries });
  const { data: tokenTS } = useQuery({ queryKey: ["token-ts"], queryFn: analyticsApi.getTokenTimeseries });

  const lastForecast = forecast?.filter(f => f.actual === null).slice(-1)[0];

  return (
    <div className="min-h-screen">
      <TopBar title="AI Forecasting" subtitle="Cost projections · Token consumption · Scenario modeling · Trend analysis" />

      <div className="p-6 space-y-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Projected Monthly Cost"
            value={formatCurrency(lastForecast?.forecast ?? 0, true)}
            icon={<DollarSign className="w-4 h-4" />}
            index={0}
          />
          <KPICard
            label="Realistic ROI (12m)"
            value={scenarios ? formatPct(scenarios.find(s => s.scenario_name === "realistic")?.roi_pct ?? 0) : "—"}
            icon={<TrendingUp className="w-4 h-4" />}
            index={1}
          />
          <KPICard
            label="Prob. Positive ROI"
            value={monteCarlo ? `${(monteCarlo.probability_positive_roi * 100).toFixed(0)}%` : "—"}
            icon={<Zap className="w-4 h-4" />}
            index={2}
          />
          <KPICard
            label="Forecast Horizon"
            value="6 months"
            icon={<Clock className="w-4 h-4" />}
            index={3}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-card p-5">
            <h3 className="section-header mb-1">AI Spend Forecast</h3>
            <p className="section-sub mb-4">Polynomial trend model · 95% CI bands · Monthly granularity</p>
            {forecast && <CostForecastChart data={forecast} />}
          </div>

          <div className="glass-card p-5">
            <h3 className="section-header mb-1">Token Consumption Trend</h3>
            <p className="section-sub mb-4">Total tokens (input + output) by team · 12 months</p>
            {tokenTS && <VelocityChart data={tokenTS} topN={5} />}
          </div>
        </div>

        <div className="glass-card p-5">
          <h3 className="section-header mb-1">3-Scenario ROI Projection</h3>
          <p className="section-sub mb-4">
            Probability-weighted scenarios: Pessimistic (20%) · Realistic (55%) · Optimistic (25%)
          </p>
          {scenarios && <ROIScenariosChart data={scenarios} />}
        </div>

        <div className="glass-card p-5">
          <h3 className="section-header mb-1">AI Cost Trend by Team</h3>
          <p className="section-sub mb-4">Monthly AI investment per team · 12 months</p>
          {aiCostTS && <VelocityChart data={aiCostTS} topN={6} />}
        </div>

        {monteCarlo && (
          <div className="glass-card p-5">
            <h3 className="section-header mb-4">Monte Carlo Risk Summary</h3>
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
              {[
                { label: "Simulations", value: monteCarlo.simulation_count.toLocaleString() },
                { label: "Mean ROI", value: formatPct(monteCarlo.mean_roi_pct) },
                { label: "Median ROI", value: formatPct(monteCarlo.median_roi_pct) },
                { label: "Std Deviation", value: `±${monteCarlo.std_deviation.toFixed(0)}%` },
                { label: "P(ROI > 0)", value: `${(monteCarlo.probability_positive_roi * 100).toFixed(1)}%` },
              ].map(m => (
                <div key={m.label} className="glass-card p-3 text-center">
                  <p className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">{m.label}</p>
                  <p className="text-lg font-bold text-white">{m.value}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
