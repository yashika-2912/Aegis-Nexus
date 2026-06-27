"use client";

import type { MetricPoint } from "@/types/metric";
import type { MonitoredService } from "@/types/service";
import { compactNumber, milliseconds, percentage } from "@/utils/formatters";
import { ServiceStatusBadge } from "./ServiceStatusBadge";

interface Props {
  services: MonitoredService[];
  metrics: MetricPoint[];
  selectedId: string | null;
  onSelect: (serviceId: string) => void;
}

export function ServiceTable({ services, metrics, selectedId, onSelect }: Props) {
  const latestByService = new Map(metrics.map((metric) => [metric.service_id, metric]));

  return (
    <div className="overflow-hidden rounded border border-slate-800 bg-slate-950">
      <div className="border-b border-slate-800 px-4 py-3">
        <h2 className="text-sm font-semibold text-white">Service Health Grid</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead className="bg-slate-900/70 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Service</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">CPU</th>
              <th className="px-4 py-3">Memory</th>
              <th className="px-4 py-3">Requests</th>
              <th className="px-4 py-3">Latency</th>
              <th className="px-4 py-3">Error Rate</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {services.map((service) => {
              const metric = latestByService.get(service.id);
              return (
                <tr
                  key={service.id}
                  onClick={() => onSelect(service.id)}
                  className={`cursor-pointer transition hover:bg-slate-900 ${
                    selectedId === service.id ? "bg-cyan-500/10" : ""
                  }`}
                >
                  <td className="px-4 py-3">
                    <div className="font-medium text-white">{service.name}</div>
                    <div className="text-xs text-slate-500">{service.owner}</div>
                  </td>
                  <td className="px-4 py-3"><ServiceStatusBadge status={service.status} /></td>
                  <td className="px-4 py-3 text-slate-300">{metric ? percentage(metric.cpu) : "--"}</td>
                  <td className="px-4 py-3 text-slate-300">{metric ? percentage(metric.memory) : "--"}</td>
                  <td className="px-4 py-3 text-slate-300">{metric ? compactNumber(metric.request_count) : "--"}</td>
                  <td className="px-4 py-3 text-slate-300">{metric ? milliseconds(metric.latency) : "--"}</td>
                  <td className="px-4 py-3 text-slate-300">{metric ? `${metric.error_rate.toFixed(2)}%` : "--"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
