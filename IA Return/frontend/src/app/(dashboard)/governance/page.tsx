"use client";

import { useQuery } from "@tanstack/react-query";
import { insightsApi } from "@/lib/api";
import { TopBar } from "@/components/layout/TopBar";
import { InsightCard } from "@/components/executive/InsightCard";
import { KPICard } from "@/components/kpi/KPICard";
import { formatCurrency, cn } from "@/lib/utils";
import { Shield, AlertTriangle, TrendingUp, Info } from "lucide-react";
import { motion } from "framer-motion";

const SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"] as const;

export default function GovernancePage() {
  const { data: insights } = useQuery({
    queryKey: ["insights"],
    queryFn: insightsApi.getStrategicInsights,
  });

  const allInsights = insights?.insights ?? [];

  return (
    <div className="min-h-screen">
      <TopBar title="AI Governance" subtitle="Strategic insights · Risk detection · Compliance · Optimization alerts" />

      <div className="p-6 space-y-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Total Insights"
            value={`${insights?.total_insights ?? 0}`}
            icon={<Info className="w-4 h-4" />}
            index={0}
          />
          <KPICard
            label="Critical Issues"
            value={`${insights?.critical_count ?? 0}`}
            icon={<AlertTriangle className="w-4 h-4" />}
            accentColor="accent-rose"
            index={1}
          />
          <KPICard
            label="High Priority"
            value={`${insights?.high_count ?? 0}`}
            icon={<AlertTriangle className="w-4 h-4" />}
            accentColor="accent-amber"
            index={2}
          />
          <KPICard
            label="Total Opportunity"
            value={formatCurrency(insights?.total_opportunity_usd ?? 0, true)}
            icon={<TrendingUp className="w-4 h-4" />}
            accentColor="accent-emerald"
            index={3}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="glass-card p-5">
            <h3 className="section-header mb-4">Severity Breakdown</h3>
            {SEVERITY_ORDER.map((sev) => {
              const count = allInsights.filter(i => i.severity === sev).length;
              const pct = allInsights.length ? (count / allInsights.length) * 100 : 0;
              const colors: Record<string, string> = {
                critical: "bg-accent-rose",
                high: "bg-accent-amber",
                medium: "bg-brand-500",
                low: "bg-slate-500",
                info: "bg-accent-cyan",
              };
              return (
                <div key={sev} className="mb-3">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400 capitalize">{sev}</span>
                    <span className="text-slate-300 font-medium">{count}</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1.5">
                    <motion.div
                      className={`h-1.5 rounded-full ${colors[sev]}`}
                      initial={{ width: 0 }}
                      animate={{ width: `${pct}%` }}
                      transition={{ duration: 0.8, ease: "easeOut" }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="lg:col-span-3 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="section-header">All Strategic Insights</h3>
              <div className="flex gap-2">
                {SEVERITY_ORDER.slice(0, 3).map(sev => (
                  <span key={sev} className="text-[9px] text-slate-500 bg-slate-800 px-2 py-1 rounded-full capitalize">
                    {sev}: {allInsights.filter(i => i.severity === sev).length}
                  </span>
                ))}
              </div>
            </div>
            {allInsights.map((insight, i) => (
              <InsightCard key={insight.id} insight={insight} index={i} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
