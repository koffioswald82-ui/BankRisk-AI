"use client";

import { motion } from "framer-motion";
import { cn, getAOVIGradient, getPerformanceTierColor } from "@/lib/utils";

interface AOVIScoreProps {
  score: number;
  rank: number;
  tier: string;
  teamName: string;
  compact?: boolean;
}

export function AOVIScore({ score, rank, tier, teamName, compact = false }: AOVIScoreProps) {
  const gradient = getAOVIGradient(score);
  const tierColor = getPerformanceTierColor(tier);
  const circumference = 2 * Math.PI * 36;
  const progress = (score / 100) * circumference;

  if (compact) {
    return (
      <div className="flex items-center gap-3">
        <div className={cn("text-2xl font-bold bg-gradient-to-r bg-clip-text text-transparent", gradient)}>
          {score.toFixed(0)}
        </div>
        <div>
          <p className="text-xs text-slate-400">{teamName}</p>
          <p className={cn("text-xs font-semibold", tierColor)}>#{rank} · {tier}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-24 h-24">
        <svg className="w-24 h-24 -rotate-90" viewBox="0 0 80 80">
          <circle cx="40" cy="40" r="36" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="6" />
          <motion.circle
            cx="40" cy="40" r="36"
            fill="none"
            stroke="url(#aovi-gradient)"
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference - progress }}
            transition={{ duration: 1.2, ease: "easeOut" }}
          />
          <defs>
            <linearGradient id="aovi-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#6366f1" />
              <stop offset="100%" stopColor="#06b6d4" />
            </linearGradient>
          </defs>
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-bold text-white">{score.toFixed(0)}</span>
          <span className="text-[9px] text-slate-500 uppercase">AOVI</span>
        </div>
      </div>
      <p className={cn("text-xs font-semibold mt-2", tierColor)}>{tier}</p>
      <p className="text-[10px] text-slate-500">Rank #{rank}</p>
    </div>
  );
}
