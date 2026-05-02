"use client";

import { AlertTriangle, RefreshCw } from "lucide-react";

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({
  message = "Failed to load data. Is the backend running?",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-12 h-12 rounded-full bg-accent-rose/10 flex items-center justify-center mb-4">
        <AlertTriangle className="w-6 h-6 text-accent-rose" />
      </div>
      <p className="text-sm font-medium text-white mb-1">Data Unavailable</p>
      <p className="text-xs text-slate-500 max-w-xs mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 text-xs text-brand-400 hover:text-brand-300 transition-colors"
        >
          <RefreshCw className="w-3 h-3" /> Retry
        </button>
      )}
    </div>
  );
}
