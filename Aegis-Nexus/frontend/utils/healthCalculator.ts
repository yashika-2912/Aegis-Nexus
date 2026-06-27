import type { MetricPoint } from "@/types/metric";
import type { SystemHealth } from "@/types/websocket";

export function calculateSystemHealth(metrics: MetricPoint[]): SystemHealth {
  const total = metrics.length;
  const healthy = metrics.filter((metric) => metric.status === "Healthy").length;
  const warnings = metrics.filter((metric) => metric.status === "Warning").length;
  const critical = metrics.filter((metric) => metric.status === "Critical").length;
  const score = metrics.reduce((sum, metric) => {
    if (metric.status === "Healthy") return sum + 100;
    if (metric.status === "Warning") return sum + 55;
    return sum;
  }, 0);

  return {
    system_health: total ? Math.round(score / total) : 0,
    healthy_services: healthy,
    warnings,
    critical,
    total_services: total,
  };
}
