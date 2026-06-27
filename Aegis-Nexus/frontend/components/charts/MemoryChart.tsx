"use client";

import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { MetricPoint } from "@/types/metric";
import { timeLabel } from "@/utils/formatters";

export function MemoryChart({ data }: { data: MetricPoint[] }) {
  return (
    <div className="h-64 rounded border border-slate-800 bg-slate-950 p-4">
      <h3 className="mb-3 text-sm font-semibold text-white">Memory Trends</h3>
      <ResponsiveContainer width="100%" height="85%">
        <AreaChart data={data}>
          <XAxis dataKey="timestamp" tickFormatter={timeLabel} stroke="#64748b" tick={{ fontSize: 11 }} />
          <YAxis domain={[0, 100]} stroke="#64748b" tick={{ fontSize: 11 }} />
          <Tooltip contentStyle={{ background: "#020617", border: "1px solid #1e293b" }} />
          <Area type="monotone" dataKey="memory" stroke="#34d399" fill="#064e3b" fillOpacity={0.35} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
