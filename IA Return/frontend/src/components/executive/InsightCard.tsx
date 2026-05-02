"use client";

import { motion } from "framer-motion";
import { AlertTriangle, TrendingUp, Shield, Zap, Info, ChevronRight } from "lucide-react";
import { cn, getSeverityColor, formatCurrency } from "@/lib/utils";
import type { StrategicInsight } from "@/types";

const SEVERITY_ICONS = {
  critical: AlertTriangle,
  high: AlertTriangle,
  medium: TrendingUp,
  low: Shield,
  info: Info,
};

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  cost_anomaly: Zap,
  performance_gap: TrendingUp,
  ai_optimization: Zap,
  quality_risk: Shield,
  velocity_insight: TrendingUp,
  finops: Zap,
  governance: Shield,
};

interface InsightCardProps {
  insight: StrategicInsight;
  index?: number;
}

export function InsightCard({ insight, index = 0 }: InsightCardProps) {
  const colorClass = getSeverityColor(insight.severity);
  const SeverityIcon = SEVERITY_ICONS[insight.severity] ?? Info;
  const CategoryIcon = CATEGORY_ICONS[insight.category] ?? Info;

  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.35, delay: index * 0.05 }}
      className={cn("glass-card p-4 border", colorClass)}
    >
      <div className="flex items-start gap-3">
        <div className={cn("w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0", colorClass)}>
          <SeverityIcon className="w-4 h-4" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <p className="text-sm font-semibold text-white leading-tight">{insight.title}</p>
            <span className={cn("text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-full border flex-shrink-0", colorClass)}>
              {insight.severity}
            </span>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed mb-3">{insight.description}</p>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {insight.team_name && (
                <span className="text-[10px] text-slate-500 bg-slate-800 px-2 py-0.5 rounded-full">
                  {insight.team_name}
                </span>
              )}
              {insight.estimated_impact_usd && insight.estimated_impact_usd > 0 && (
                <span className="text-[10px] text-accent-emerald bg-accent-emerald/10 px-2 py-0.5 rounded-full">
                  {formatCurrency(insight.estimated_impact_usd, true)} opportunity
                </span>
              )}
            </div>
            <span className="text-[10px] text-slate-600">
              {(insight.confidence_score * 100).toFixed(0)}% confidence
            </span>
          </div>

          <div className="mt-3 pt-3 border-t border-slate-800/60 flex items-center gap-2 text-xs text-slate-500">
            <ChevronRight className="w-3 h-3 text-brand-500" />
            <span className="text-brand-400">{insight.recommended_action}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
