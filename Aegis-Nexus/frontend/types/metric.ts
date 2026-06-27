import type { ServiceStatus } from "./service";

export interface MetricPoint {
  service_id: string;
  timestamp: string;
  cpu: number;
  memory: number;
  request_count: number;
  request_rate: number;
  error_rate: number;
  latency: number;
  status: ServiceStatus;
  available: boolean;
}

export interface MetricsResponse {
  latest: MetricPoint[];
  history: Record<string, MetricPoint[]>;
}
