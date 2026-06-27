export interface ServiceState {
  name: string;
  status: string;
  error_rate: number;
  avg_latency_ms: number;
  p95_latency_ms: number;
  total_requests: number;
  error_count: number;
  logs: string[];
  history: { timestamp: number; latency_ms: number; error_rate: number; status: number }[];
}

export interface AgentStep {
  agent: string;
  status: string;
  output: string;
  timestamp: number;
  metadata?: Record<string, unknown>;
}

export interface Incident {
  id: number;
  triggered_at: number;
  resolved_at?: number;
  anomaly_type: string;
  affected_service: string;
  root_cause: string;
  action_taken: string;
  recovery_time_ms?: number;
  outcome: string;
  failed_requests: number;
  failed_checkouts: number;
  severity: string;
  agent_outputs: Record<string, string>;
}

export interface TelemetrySnapshot {
  services: Record<string, ServiceState>;
  graph: { nodes: { id: string; label: string; status: string; criticality: string }[]; edges: { source: string; target: string }[] };
  incident_window: {
    active: boolean;
    failed_requests: number;
    failed_checkouts: number;
    anomaly_type: string;
    affected_service: string;
  };
  pipeline_state: boolean;
  timestamp: number;
}

export interface LearningStat {
  action: string;
  total: number;
  success_rate: number;
  avg_recovery_ms: number;
}

export const STATUS_COLORS: Record<string, string> = {
  healthy: "#10b981",
  warning: "#f59e0b",
  degraded: "#f97316",
  critical: "#ef4444",
  down: "#6b7280",
};

export const AGENT_COLORS: Record<string, string> = {
  Sentinel: "#06b6d4",
  Sherlock: "#8b5cf6",
  Oracle: "#f59e0b",
  Healer: "#10b981",
};
