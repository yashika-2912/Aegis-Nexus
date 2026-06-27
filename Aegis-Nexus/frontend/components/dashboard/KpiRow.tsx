import { TelemetrySnapshot } from "@/types";

interface Props {
  telemetry: TelemetrySnapshot | null;
  connected: boolean;
}

export default function KpiRow({ telemetry, connected }: Props) {
  const services = telemetry ? Object.values(telemetry.services) : [];
  const totalReqs = services.reduce((s, v) => s + v.total_requests, 0);
  const totalErrors = services.reduce((s, v) => s + v.error_count, 0);
  const avgLatency = services.length
    ? services.reduce((s, v) => s + v.avg_latency_ms, 0) / services.length
    : 0;
  const errorRate = totalReqs ? (totalErrors / totalReqs * 100) : 0;
  const healthyCount = services.filter(s => s.status === "healthy").length;

  const kpis = [
    { label: "Services Healthy", value: `${healthyCount}/${services.length || 5}`, color: healthyCount === 5 ? "text-nexus-green" : "text-nexus-yellow" },
    { label: "Total Requests", value: totalReqs.toLocaleString(), color: "text-nexus-accent" },
    { label: "Error Rate", value: `${errorRate.toFixed(1)}%`, color: errorRate > 10 ? "text-nexus-red" : "text-nexus-green" },
    { label: "Avg Latency", value: `${avgLatency.toFixed(0)}ms`, color: avgLatency > 300 ? "text-nexus-yellow" : "text-nexus-accent" },
    { label: "WS Status", value: connected ? "Live" : "Reconnecting", color: connected ? "text-nexus-green" : "text-nexus-red" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
      {kpis.map(k => (
        <div key={k.label} className="bg-nexus-panel border border-nexus-border rounded-lg p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wider">{k.label}</p>
          <p className={`text-2xl font-bold mt-1 ${k.color}`}>{k.value}</p>
        </div>
      ))}
    </div>
  );
}
