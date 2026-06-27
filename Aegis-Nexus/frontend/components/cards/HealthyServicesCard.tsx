import { CheckCircle2 } from "lucide-react";

export function HealthyServicesCard({ healthy, total }: { healthy: number; total: number }) {
  return (
    <div className="rounded border border-slate-800 bg-slate-950 p-4">
      <div className="flex items-center justify-between text-slate-400">
        <span className="text-sm">Healthy Services</span>
        <CheckCircle2 className="h-4 w-4 text-emerald-300" />
      </div>
      <div className="mt-3 text-3xl font-semibold text-white">
        {healthy}/{total}
      </div>
      <p className="mt-2 text-xs text-slate-500">Currently inside operating thresholds</p>
    </div>
  );
}
