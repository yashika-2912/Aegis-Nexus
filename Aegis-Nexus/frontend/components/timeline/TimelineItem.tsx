import { CircleCheck, Info, TriangleAlert, Zap } from "lucide-react";

import type { TimelineEvent } from "@/types/event";
import { timeLabel } from "@/utils/formatters";

export function TimelineItem({ event }: { event: TimelineEvent }) {
  const Icon =
    event.severity === "success"
      ? CircleCheck
      : event.severity === "warning"
        ? TriangleAlert
        : event.severity === "critical"
          ? Zap
          : Info;
  const color =
    event.severity === "success"
      ? "text-emerald-300"
      : event.severity === "warning"
        ? "text-amber-300"
        : event.severity === "critical"
          ? "text-rose-300"
          : "text-cyan-300";

  return (
    <div className="flex gap-3 rounded border border-slate-800 bg-slate-900/50 p-3">
      <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${color}`} />
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-white">{event.service_name}</span>
          <span className="text-[11px] uppercase text-slate-500">{event.type.replaceAll("_", " ")}</span>
          <span className="text-[11px] text-slate-600">{timeLabel(event.timestamp)}</span>
        </div>
        <p className="mt-1 text-xs leading-5 text-slate-400">{event.message}</p>
      </div>
    </div>
  );
}
