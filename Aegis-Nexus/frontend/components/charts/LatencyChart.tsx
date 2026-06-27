"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { MetricPoint } from "@/types/metric";
import { timeLabel } from "@/utils/formatters";

export function LatencyChart({ data }: { data: MetricPoint[] }) {
  return (
    <div className="h-64 rounded border border-slate-800 bg-slate-950 p-4">
      <h3 className="mb-3 text-sm font-semibold text-white">Latency Trends</h3>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={data}>
          <XAxis dataKey="timestamp" tickFormatter={timeLabel} stroke="#64748b" tick={{ fontSize: 11 }} />
          <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
          <Tooltip contentStyle={{ background: "#020617", border: "1px solid #1e293b" }} />
          <Line type="monotone" dataKey="latency" stroke="#f59e0b" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
