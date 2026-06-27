"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { MetricPoint } from "@/types/metric";
import { timeLabel } from "@/utils/formatters";

export function CpuChart({ data }: { data: MetricPoint[] }) {
  return (
    <ChartShell title="CPU Trends">
      <LineChart data={data}>
        <XAxis dataKey="timestamp" tickFormatter={timeLabel} stroke="#64748b" tick={{ fontSize: 11 }} />
        <YAxis domain={[0, 100]} stroke="#64748b" tick={{ fontSize: 11 }} />
        <Tooltip contentStyle={{ background: "#020617", border: "1px solid #1e293b" }} />
        <Line type="monotone" dataKey="cpu" stroke="#22d3ee" strokeWidth={2} dot={false} />
      </LineChart>
    </ChartShell>
  );
}

export function ChartShell({ title, children }: { title: string; children: React.ReactElement }) {
  return (
    <div className="h-64 rounded border border-slate-800 bg-slate-950 p-4">
      <h3 className="mb-3 text-sm font-semibold text-white">{title}</h3>
      <ResponsiveContainer width="100%" height="85%">{children}</ResponsiveContainer>
    </div>
  );
}
