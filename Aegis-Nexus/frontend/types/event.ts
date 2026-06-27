export type TimelineEventType =
  | "SERVICE_STARTED"
  | "THRESHOLD_CROSSED"
  | "RECOVERY"
  | "SERVICE_UNAVAILABLE"
  | "TELEMETRY";

export interface TimelineEvent {
  id: string;
  service_id: string;
  service_name: string;
  type: TimelineEventType;
  severity: "info" | "success" | "warning" | "critical";
  message: string;
  timestamp: string;
}
