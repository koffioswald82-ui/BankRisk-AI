import axios from "axios";
import type {
  PlatformOverview, TeamKPI, TeamTrend, HeatmapCell, TeamRadar,
  ROIScenario, ForecastPoint, CostBreakdown, MonteCarloResult,
  FinOpsSnapshot, InsightsSummary, ExecutiveBriefing, FinOpsRecommendation, Team,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

export const analyticsApi = {
  getOverview: () => client.get<PlatformOverview>("/analytics/overview").then(r => r.data),
  getTeamKPIs: () => client.get<{ teams: TeamKPI[]; total: number }>("/analytics/teams/kpis").then(r => r.data),
  getTeamKPI: (id: string) => client.get<TeamKPI>(`/analytics/teams/${id}/kpis`).then(r => r.data),
  getRankings: () => client.get<{ rankings: TeamKPI[] }>("/analytics/rankings").then(r => r.data),
  getVelocityTimeseries: () => client.get<TeamTrend[]>("/analytics/timeseries/velocity").then(r => r.data),
  getQualityTimeseries: () => client.get<TeamTrend[]>("/analytics/timeseries/quality").then(r => r.data),
  getAICostTimeseries: () => client.get<TeamTrend[]>("/analytics/timeseries/ai-cost").then(r => r.data),
  getTokenTimeseries: () => client.get<TeamTrend[]>("/analytics/timeseries/tokens").then(r => r.data),
  getHeatmap: () => client.get<HeatmapCell[]>("/analytics/heatmap").then(r => r.data),
  getRadar: () => client.get<TeamRadar[]>("/analytics/radar").then(r => r.data),
};

export const finopsApi = {
  getSnapshot: () => client.get<FinOpsSnapshot>("/finops/snapshot").then(r => r.data),
  getROIScenarios: () => client.get<ROIScenario[]>("/finops/roi/scenarios").then(r => r.data),
  getMonteCarlo: () => client.get<MonteCarloResult>("/finops/montecarlo").then(r => r.data),
  getCostForecast: () => client.get<ForecastPoint[]>("/finops/forecast/costs").then(r => r.data),
  getCostBreakdown: () => client.get<CostBreakdown[]>("/finops/cost-breakdown").then(r => r.data),
  getRecommendations: () => client.get<FinOpsRecommendation[]>("/finops/recommendations").then(r => r.data),
};

export const insightsApi = {
  getStrategicInsights: () => client.get<InsightsSummary>("/insights/strategic").then(r => r.data),
  getExecutiveBriefing: () => client.get<ExecutiveBriefing>("/insights/executive-briefing").then(r => r.data),
};

export const teamsApi = {
  getTeams: () => client.get<{ teams: Team[]; total: number }>("/teams/").then(r => r.data),
  getTeamEngineers: (id: string) => client.get(`/teams/${id}/engineers`).then(r => r.data),
  getTeamSprints: (id: string) => client.get(`/teams/${id}/sprints`).then(r => r.data),
};
