export interface Team {
  id: string;
  name: string;
  domain: string;
  size: number;
  department: string;
  lead_engineer: string;
  ai_adoption_tier: "pioneer" | "advanced" | "standard" | "lagging";
  budget_usd: number;
  engineer_count?: number;
  total_ai_cost_usd?: number;
}

export interface TeamKPI {
  team_id: string;
  team_name: string;
  domain: string;
  team_size: number;
  avg_velocity: number;
  story_points_delivered: number;
  avg_dev_time_hours: number;
  commits_count: number;
  prs_merged: number;
  prs_rejected: number;
  bug_rate: number;
  test_coverage_pct: number;
  code_quality_score: number;
  documentation_coverage_pct: number;
  deployment_frequency: number;
  change_failure_rate: number;
  lead_time_hours: number;
  mttr_hours: number;
  incidents_count: number;
  ai_adoption_rate: number;
  tokens_consumed: number;
  total_ai_requests: number;
  ai_cost_usd: number;
  cost_per_engineer: number;
  critical_bugs: number;
  productivity_index: number;
  quality_index: number;
  velocity_index: number;
  aovi_score: number;
  aovi_rank: number;
  performance_tier: "Elite" | "High Performer" | "Standard" | "Needs Improvement" | "Critical";
}

export interface PlatformOverview {
  total_teams: number;
  total_engineers: number;
  total_ai_cost_usd: number;
  total_tokens_consumed: number;
  avg_productivity_gain_pct: number;
  avg_quality_improvement_pct: number;
  global_ai_adoption_rate: number;
  estimated_savings_usd: number;
  global_roi_pct: number;
  avg_aovi_score: number;
  period_start: string;
  period_end: string;
}

export interface TimeSeriesPoint {
  period: string;
  value: number;
  label?: string;
}

export interface TeamTrend {
  team_id: string;
  team_name: string;
  series: TimeSeriesPoint[];
}

export interface HeatmapCell {
  team: string;
  metric: string;
  value: number;
  normalized: number;
}

export interface RadarPoint {
  metric: string;
  value: number;
  fullMark: number;
}

export interface TeamRadar {
  team_id: string;
  team_name: string;
  data: RadarPoint[];
}

export interface ROIScenario {
  scenario_name: string;
  label: string;
  roi_pct: number;
  net_benefit_usd: number;
  break_even_months: number;
  cumulative_savings_12m: number;
  probability: number;
}

export interface ForecastPoint {
  period: string;
  actual: number | null;
  forecast: number;
  lower_bound: number;
  upper_bound: number;
}

export interface CostBreakdown {
  category: string;
  amount_usd: number;
  percentage: number;
  trend_pct: number;
}

export interface MonteCarloResult {
  simulation_count: number;
  mean_roi_pct: number;
  median_roi_pct: number;
  std_deviation: number;
  p10_roi_pct: number;
  p50_roi_pct: number;
  p90_roi_pct: number;
  probability_positive_roi: number;
  distribution: number[];
}

export interface FinOpsSnapshot {
  total_annual_savings_usd: number;
  productivity_savings_usd: number;
  quality_savings_usd: number;
  documentation_savings_usd: number;
  total_ai_cost_usd: number;
  net_benefit_usd: number;
  roi_pct: number;
  break_even_months: number;
}

export interface StrategicInsight {
  id: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  category: string;
  title: string;
  description: string;
  team_name?: string;
  metric_value?: number;
  benchmark_value?: number;
  delta_pct?: number;
  recommended_action: string;
  estimated_impact_usd?: number;
  confidence_score: number;
  generated_at: string;
}

export interface InsightsSummary {
  total_insights: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  total_opportunity_usd: number;
  insights: StrategicInsight[];
}

export interface ExecutiveBriefing {
  headline: string;
  period: string;
  key_wins: string[];
  risks: string[];
  recommendations: string[];
  financial_summary: string;
  ai_maturity_score: number;
}

export interface FinOpsRecommendation {
  id: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  category: string;
  title: string;
  description: string;
  estimated_savings_usd: number;
  implementation_effort: string;
  impact_score: number;
}
