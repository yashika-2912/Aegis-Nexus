import { AlertTriangle } from "lucide-react";

export function WarningServicesCard({ value }: { value: number }) {
  return (
    <div className="rounded border border-slate-800 bg-slate-950 p-4">
      <div className="flex items-center justify-between text-slate-400">
        <span className="text-sm">Active Warnings</span>
        <AlertTriangle className="h-4 w-4 text-amber-300" />
      </div>
      <div className="mt-3 text-3xl font-semibold text-white">{value}</div>
      <p className="mt-2 text-xs text-slate-500">CPU, latency, or error threshold crossings</p>
    </div>
  );
}
