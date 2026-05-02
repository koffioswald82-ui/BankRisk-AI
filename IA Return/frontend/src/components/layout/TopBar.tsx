"use client";

import { Bell, RefreshCw, Calendar } from "lucide-react";
import { motion } from "framer-motion";

interface TopBarProps {
  title: string;
  subtitle?: string;
}

export function TopBar({ title, subtitle }: TopBarProps) {
  return (
    <header className="h-16 border-b border-slate-800/60 bg-surface-950/80 backdrop-blur-xl flex items-center justify-between px-6 sticky top-0 z-30">
      <div>
        <h1 className="text-base font-semibold text-white">{title}</h1>
        {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs text-slate-500 border border-slate-800 rounded-lg px-3 py-1.5">
          <Calendar className="w-3 h-3" />
          <span>Jan 2024 – Dec 2024</span>
        </div>

        <motion.button
          whileHover={{ rotate: 180 }}
          transition={{ duration: 0.3 }}
          className="w-8 h-8 rounded-lg border border-slate-800 flex items-center justify-center text-slate-500 hover:text-white hover:border-slate-600 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </motion.button>

        <div className="relative">
          <button className="w-8 h-8 rounded-lg border border-slate-800 flex items-center justify-center text-slate-500 hover:text-white hover:border-slate-600 transition-colors">
            <Bell className="w-3.5 h-3.5" />
          </button>
          <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-accent-rose text-[8px] font-bold text-white flex items-center justify-center">
            3
          </span>
        </div>

        <div className="flex items-center gap-2 border-l border-slate-800 pl-3">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-brand-500 to-accent-cyan flex items-center justify-center text-xs font-bold text-white">
            CIO
          </div>
          <div className="hidden sm:block">
            <p className="text-xs font-medium text-white leading-tight">Chief AI Officer</p>
            <p className="text-[10px] text-slate-600">Enterprise Division</p>
          </div>
        </div>
      </div>
    </header>
  );
}
