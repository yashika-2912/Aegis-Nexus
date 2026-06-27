import type { TimelineEvent } from "./event";
import type { MetricPoint } from "./metric";
import type { MonitoredService } from "./service";

export interface SystemHealth {
  system_health: number;
  healthy_services: number;
  warnings: number;
  critical: number;
  total_services: number;
}

export interface TelemetryUpdate {
  type: "telemetry.update";
  services: MonitoredService[];
  metrics: MetricPoint[];
  history: Record<string, MetricPoint[]>;
  health: SystemHealth;
  events: TimelineEvent[];
}
