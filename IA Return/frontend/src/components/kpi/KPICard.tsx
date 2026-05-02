"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface KPICardProps {
  label: string;
  value: string;
  delta?: number;
  deltaLabel?: string;
  icon?: React.ReactNode;
  accentColor?: string;
  loading?: boolean;
  subtitle?: string;
  index?: number;
}

export function KPICard({
  label, value, delta, deltaLabel, icon, accentColor = "brand",
  loading, subtitle, index = 0,
}: KPICardProps) {
  const isPositive = delta !== undefined && delta > 0;
  const isNegative = delta !== undefined && delta < 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.06 }}
      className="glass-card-hover p-5 relative overflow-hidden group"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-brand-600/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl" />

      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <p className="kpi-label">{label}</p>
          {icon && (
            <div className={cn(
              "w-8 h-8 rounded-lg flex items-center justify-center",
              `bg-${accentColor}-500/10`
            )}>
              <div className={`text-${accentColor}-400`}>{icon}</div>
            </div>
          )}
        </div>

        {loading ? (
          <div className="space-y-2">
            <div className="h-8 w-32 bg-slate-800 rounded animate-pulse" />
            <div className="h-3 w-20 bg-slate-800 rounded animate-pulse" />
          </div>
        ) : (
          <>
            <p className="kpi-value mb-1">{value}</p>
            {subtitle && <p className="text-xs text-slate-500 mb-2">{subtitle}</p>}
            {delta !== undefined && (
              <div className={cn(
                "flex items-center gap-1 text-xs font-medium",
                isPositive ? "text-accent-emerald" : isNegative ? "text-accent-rose" : "text-slate-400"
              )}>
                {isPositive ? <TrendingUp className="w-3 h-3" /> :
                 isNegative ? <TrendingDown className="w-3 h-3" /> :
                 <Minus className="w-3 h-3" />}
                <span>
                  {isPositive ? "+" : ""}{delta.toFixed(1)}%
                  {deltaLabel && <span className="text-slate-500 ml-1">{deltaLabel}</span>}
                </span>
              </div>
            )}
          </>
        )}
      </div>

      <div className={cn(
        "absolute bottom-0 left-0 right-0 h-0.5",
        `bg-gradient-to-r from-transparent via-${accentColor}-500/40 to-transparent`
      )} />
    </motion.div>
  );
}
