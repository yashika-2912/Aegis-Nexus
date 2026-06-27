"use client";

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { TelemetrySnapshot } from "@/types";

interface Props {
  telemetry: TelemetrySnapshot | null;
}

export default function LiveLineChart({ telemetry }: Props) {
  const services = telemetry ? Object.values(telemetry.services) : [];
  const maxLen = Math.max(...services.map(s => s.history?.length || 0), 1);

  const data = Array.from({ length: maxLen }, (_, i) => {
    const point: Record<string, number | string> = { index: i };
    services.forEach(s => {
      const h = s.history?.[i];
      if (h) {
        point[s.name] = h.latency_ms;
        point[`${s.name}_err`] = h.error_rate;
      }
    });
    return point;
  });

  const colors = ["#06b6d4", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"];

  return (
    <div className="bg-nexus-panel border border-nexus-border rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Live Latency (ms)</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <XAxis dataKey="index" stroke="#374151" tick={{ fontSize: 10 }} />
          <YAxis stroke="#374151" tick={{ fontSize: 10 }} />
          <Tooltip contentStyle={{ backgroundColor: "#111827", border: "1px solid #1f2937", fontSize: 12 }} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          {services.map((s, i) => (
            <Line key={s.name} type="monotone" dataKey={s.name} stroke={colors[i % colors.length]}
              dot={false} strokeWidth={2} isAnimationActive={false} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
