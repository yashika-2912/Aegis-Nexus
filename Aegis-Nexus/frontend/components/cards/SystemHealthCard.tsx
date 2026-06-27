import { Activity } from "lucide-react";

export function SystemHealthCard({ value }: { value: number }) {
  return (
    <div className="rounded border border-slate-800 bg-slate-950 p-4">
      <div className="flex items-center justify-between text-slate-400">
        <span className="text-sm">System Health</span>
        <Activity className="h-4 w-4" />
      </div>
      <div className="mt-3 text-3xl font-semibold text-white">{value}%</div>
      <div className="mt-3 h-2 rounded bg-slate-800">
        <div className="h-2 rounded bg-cyan-400 transition-all" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}
