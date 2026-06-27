"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { MetricPoint } from "@/types/metric";
import { timeLabel } from "@/utils/formatters";

export function RequestChart({ data }: { data: MetricPoint[] }) {
  return (
    <div className="h-64 rounded border border-slate-800 bg-slate-950 p-4">
      <h3 className="mb-3 text-sm font-semibold text-white">Request Throughput</h3>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data}>
          <XAxis dataKey="timestamp" tickFormatter={timeLabel} stroke="#64748b" tick={{ fontSize: 11 }} />
          <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
          <Tooltip contentStyle={{ background: "#020617", border: "1px solid #1e293b" }} />
          <Bar dataKey="request_rate" fill="#a78bfa" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
