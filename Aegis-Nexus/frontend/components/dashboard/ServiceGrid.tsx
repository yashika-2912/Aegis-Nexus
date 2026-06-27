import { STATUS_COLORS, TelemetrySnapshot } from "@/types";

interface Props {
  telemetry: TelemetrySnapshot | null;
}

export default function ServiceGrid({ telemetry }: Props) {
  const services = telemetry ? Object.values(telemetry.services) : [];

  return (
    <div className="bg-nexus-panel border border-nexus-border rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Service Grid</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {services.map(s => {
          const color = STATUS_COLORS[s.status] || STATUS_COLORS.healthy;
          return (
            <div key={s.name} className="border border-nexus-border rounded-lg p-3" style={{ borderLeftColor: color, borderLeftWidth: 3 }}>
              <div className="flex justify-between items-center">
                <span className="font-medium text-sm">{s.name}</span>
                <span className="text-xs px-2 py-0.5 rounded-full capitalize" style={{ backgroundColor: color + "22", color }}>
                  {s.status}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2 mt-2 text-xs text-gray-500">
                <div>Err: {s.error_rate.toFixed(1)}%</div>
                <div>Avg: {s.avg_latency_ms.toFixed(0)}ms</div>
                <div>P95: {s.p95_latency_ms.toFixed(0)}ms</div>
              </div>
              {s.logs.length > 0 && (
                <p className="mt-2 text-xs text-gray-600 truncate">{s.logs[s.logs.length - 1]}</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
