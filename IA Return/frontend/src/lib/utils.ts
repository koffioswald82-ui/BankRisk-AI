import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number, compact = false): string {
  if (compact && value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (compact && value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatNumber(value: number, decimals = 1): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toFixed(decimals);
}

export function formatPct(value: number): string {
  return `${value >= 0 ? "+" : ""}${value.toFixed(1)}%`;
}

export function getTierColor(tier: string): string {
  const map: Record<string, string> = {
    pioneer: "text-accent-cyan",
    advanced: "text-accent-emerald",
    standard: "text-brand-400",
    lagging: "text-accent-amber",
  };
  return map[tier] ?? "text-gray-400";
}

export function getPerformanceTierColor(tier: string): string {
  const map: Record<string, string> = {
    Elite: "text-accent-cyan",
    "High Performer": "text-accent-emerald",
    Standard: "text-brand-400",
    "Needs Improvement": "text-accent-amber",
    Critical: "text-accent-rose",
  };
  return map[tier] ?? "text-gray-400";
}

export function getSeverityColor(severity: string): string {
  const map: Record<string, string> = {
    critical: "text-accent-rose border-accent-rose/30 bg-accent-rose/10",
    high: "text-accent-amber border-accent-amber/30 bg-accent-amber/10",
    medium: "text-brand-400 border-brand-400/30 bg-brand-400/10",
    low: "text-gray-400 border-gray-400/30 bg-gray-400/10",
    info: "text-accent-cyan border-accent-cyan/30 bg-accent-cyan/10",
  };
  return map[severity] ?? "text-gray-400";
}

export function getAOVIGradient(score: number): string {
  if (score >= 85) return "from-accent-cyan to-brand-500";
  if (score >= 70) return "from-accent-emerald to-brand-500";
  if (score >= 50) return "from-brand-400 to-brand-600";
  if (score >= 30) return "from-accent-amber to-orange-600";
  return "from-accent-rose to-red-700";
}

export const CHART_COLORS = [
  "#6366f1", "#06b6d4", "#10b981", "#f59e0b",
  "#f43f5e", "#8b5cf6", "#ec4899", "#14b8a6",
  "#84cc16", "#fb923c", "#a78bfa", "#34d399",
];
