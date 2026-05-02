"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard, TrendingUp, DollarSign, Users,
  Shield, BarChart3, Zap, ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/",           label: "Executive Overview", icon: LayoutDashboard, badge: null },
  { href: "/analytics",  label: "Analytics Engine",   icon: BarChart3,        badge: null },
  { href: "/finops",     label: "FinOps Intelligence", icon: DollarSign,      badge: "NEW" },
  { href: "/teams",      label: "Team Intelligence",  icon: Users,            badge: null },
  { href: "/forecasting",label: "AI Forecasting",     icon: TrendingUp,      badge: null },
  { href: "/governance", label: "AI Governance",      icon: Shield,          badge: null },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-surface-950 border-r border-slate-800/60 z-40 flex flex-col">
      <div className="p-6 border-b border-slate-800/60">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-accent-cyan flex items-center justify-center shadow-glow-brand">
            <Zap className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-white leading-tight">AI FinOps</p>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest">Intelligence Platform</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-1">
        <p className="text-[10px] font-semibold text-slate-600 uppercase tracking-widest px-3 pt-2 pb-1">
          Platform
        </p>
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href}>
              <motion.div
                whileHover={{ x: 2 }}
                className={cn(
                  "flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer",
                  active
                    ? "text-white bg-brand-600/20 border border-brand-600/30"
                    : "text-slate-400 hover:text-white hover:bg-surface-800"
                )}
              >
                <div className="flex items-center gap-3">
                  <Icon className={cn("w-4 h-4", active ? "text-brand-400" : "text-slate-500")} />
                  <span>{item.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  {item.badge && (
                    <span className="text-[9px] font-bold text-accent-cyan bg-accent-cyan/10 border border-accent-cyan/20 px-1.5 py-0.5 rounded-full">
                      {item.badge}
                    </span>
                  )}
                  {active && <ChevronRight className="w-3 h-3 text-brand-400" />}
                </div>
              </motion.div>
            </Link>
          );
        })}
      </div>

      <div className="p-4 border-t border-slate-800/60">
        <div className="glass-card p-3 space-y-1">
          <p className="text-[10px] text-slate-500 uppercase tracking-widest">Platform Status</p>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-accent-emerald animate-pulse-slow" />
            <span className="text-xs text-slate-300">All Systems Operational</span>
          </div>
          <p className="text-[10px] text-slate-600">v1.0.0 · 12 teams · 96 engineers</p>
        </div>
      </div>
    </aside>
  );
}
