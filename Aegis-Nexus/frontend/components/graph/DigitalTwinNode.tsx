import { Handle, Position, type NodeProps } from "reactflow";

import type { TwinNode } from "@/types/digitalTwin";

const statusClasses = {
  Healthy: "border-emerald-400/50 bg-emerald-950/80 text-emerald-100",
  Warning: "border-amber-300/60 bg-amber-950/80 text-amber-100",
  Critical: "border-red-400/60 bg-red-950/80 text-red-100",
  Affected: "border-orange-300/70 bg-orange-950/80 text-orange-100",
  Down: "border-rose-500 bg-rose-950 text-rose-50",
};

export function DigitalTwinNode({ data }: NodeProps<TwinNode>) {
  return (
    <div className={`w-48 rounded border px-3 py-3 shadow-lg shadow-black/30 ${statusClasses[data.status]}`}>
      <Handle type="target" position={Position.Top} className="!bg-slate-300" />
      <div className="text-sm font-semibold">{data.name}</div>
      <div className="mt-1 flex items-center justify-between text-[11px]">
        <span>{data.type}</span>
        <span>{data.health}%</span>
      </div>
      <div className="mt-2 h-1.5 rounded bg-black/30">
        <div className="h-1.5 rounded bg-current transition-all" style={{ width: `${data.health}%` }} />
      </div>
      <div className="mt-2 text-[11px] uppercase">{data.status}</div>
      <Handle type="source" position={Position.Bottom} className="!bg-slate-300" />
    </div>
  );
}
