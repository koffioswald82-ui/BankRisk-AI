import { useQuery } from "@tanstack/react-query";
import { analyticsApi, finopsApi, insightsApi } from "@/lib/api";

export function useOverview() {
  return useQuery({ queryKey: ["overview"], queryFn: analyticsApi.getOverview });
}

export function useTeamKPIs() {
  return useQuery({ queryKey: ["team-kpis"], queryFn: analyticsApi.getTeamKPIs });
}

export function useRankings() {
  return useQuery({ queryKey: ["rankings"], queryFn: analyticsApi.getRankings });
}

export function useHeatmap() {
  return useQuery({ queryKey: ["heatmap"], queryFn: analyticsApi.getHeatmap });
}

export function useRadar() {
  return useQuery({ queryKey: ["radar"], queryFn: analyticsApi.getRadar });
}

export function useVelocityTimeseries() {
  return useQuery({ queryKey: ["velocity-ts"], queryFn: analyticsApi.getVelocityTimeseries });
}

export function useQualityTimeseries() {
  return useQuery({ queryKey: ["quality-ts"], queryFn: analyticsApi.getQualityTimeseries });
}

export function useAICostTimeseries() {
  return useQuery({ queryKey: ["ai-cost-ts"], queryFn: analyticsApi.getAICostTimeseries });
}

export function useFinOpsSnapshot() {
  return useQuery({ queryKey: ["finops-snapshot"], queryFn: finopsApi.getSnapshot });
}

export function useROIScenarios() {
  return useQuery({ queryKey: ["roi-scenarios"], queryFn: finopsApi.getROIScenarios });
}

export function useMonteCarlo() {
  return useQuery({ queryKey: ["monte-carlo"], queryFn: finopsApi.getMonteCarlo });
}

export function useCostForecast() {
  return useQuery({ queryKey: ["cost-forecast"], queryFn: finopsApi.getCostForecast });
}

export function useCostBreakdown() {
  return useQuery({ queryKey: ["cost-breakdown"], queryFn: finopsApi.getCostBreakdown });
}

export function useStrategicInsights() {
  return useQuery({ queryKey: ["insights"], queryFn: insightsApi.getStrategicInsights });
}

export function useExecutiveBriefing() {
  return useQuery({ queryKey: ["exec-briefing"], queryFn: insightsApi.getExecutiveBriefing });
}
