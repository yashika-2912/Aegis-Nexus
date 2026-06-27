"use client";

import { Database, Network, Server } from "lucide-react";

import type { MetricPoint } from "@/types/metric";
import type { MonitoredService } from "@/types/service";
import { compactNumber, milliseconds, percentage } from "@/utils/formatters";
import { ServiceStatusBadge } from "./ServiceStatusBadge";

interface Props {
  service: MonitoredService;
  metric?: MetricPoint;
  history: MetricPoint[];
}

export function ServiceCard({ service, metric, history }: Props) {
  const Icon = service.kind === "database" ? Database : service.kind === "frontend" ? Network : Server;
  const logs = history.slice(-4).reverse();

  return (
    <aside className="rounded border border-slate-800 bg-slate-950 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Icon className="h-4 w-4 text-cyan-300" />
            <h2 className="text-sm font-semibold text-white">{service.name}</h2>
          </div>
          <p className="mt-2 text-xs leading-5 text-slate-400">{service.description}</p>
        </div>
        <ServiceStatusBadge status={service.status} />
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
        <Stat label="CPU" value={metric ? percentage(metric.cpu) : "--"} />
        <Stat label="Memory" value={metric ? percentage(metric.memory) : "--"} />
        <Stat label="Latency" value={metric ? milliseconds(metric.latency) : "--"} />
        <Stat label="Request Rate" value={metric ? `${Math.round(metric.request_rate)}/s` : "--"} />
        <Stat label="Error Rate" value={metric ? `${metric.error_rate.toFixed(2)}%` : "--"} />
        <Stat label="Requests" value={metric ? compactNumber(metric.request_count) : "--"} />
      </div>

      <div className="mt-5">
        <h3 className="text-xs font-semibold uppercase text-slate-500">Dependencies</h3>
        <div className="mt-2 space-y-2">
          {service.dependencies.length ? (
            service.dependencies.map((dependency) => (
              <div key={dependency.id} className="flex items-center justify-between rounded bg-slate-900 px-3 py-2 text-xs">
                <span className="text-slate-300">{dependency.name}</span>
                <ServiceStatusBadge status={dependency.status} />
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-500">No downstream dependencies</p>
          )}
        </div>
      </div>

      <div className="mt-5">
        <h3 className="text-xs font-semibold uppercase text-slate-500">Recent Logs</h3>
        <div className="mt-2 space-y-2">
          {logs.map((point) => (
            <p key={point.timestamp} className="rounded bg-slate-900 px-3 py-2 text-xs text-slate-400">
              [{new Date(point.timestamp).toLocaleTimeString()}] telemetry exported:
              CPU {point.cpu.toFixed(0)}%, latency {point.latency.toFixed(0)}ms
            </p>
          ))}
        </div>
      </div>
    </aside>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-slate-800 bg-slate-900/60 p-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-1 text-base font-semibold text-white">{value}</div>
    </div>
  );
}
