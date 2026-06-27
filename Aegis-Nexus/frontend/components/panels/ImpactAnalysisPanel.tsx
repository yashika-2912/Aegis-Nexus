import { GitBranch, Radar, Route } from "lucide-react";

import type { ImpactAnalysis } from "@/types/digitalTwin";

export function ImpactAnalysisPanel({ analysis }: { analysis: ImpactAnalysis | null }) {
  return (
    <section className="rounded border border-slate-800 bg-slate-950 p-4">
      <h2 className="text-sm font-semibold text-white">Impact Analysis</h2>
      {analysis ? (
        <div className="mt-4 space-y-4 text-sm">
          <Insight icon={<Radar className="h-4 w-4" />} label="Failure Origin" value={analysis.failure_origin} />
          <Insight icon={<GitBranch className="h-4 w-4" />} label="Blast Radius" value={`${analysis.blast_radius} services`} />
          <div>
            <div className="text-xs font-semibold uppercase text-slate-500">Affected Services</div>
            <div className="mt-2 flex flex-wrap gap-2">
              {analysis.affected_services.map((service) => (
                <span key={service} className="rounded border border-orange-300/30 bg-orange-500/10 px-2 py-1 text-xs text-orange-200">
                  {service}
                </span>
              ))}
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase text-slate-500">
              <Route className="h-4 w-4" />
              Critical Path
            </div>
            <p className="mt-2 text-sm text-slate-200">{analysis.critical_path.join(" -> ")}</p>
          </div>
          <p className="rounded border border-slate-800 bg-slate-900 p-3 text-sm text-slate-300">
            {analysis.suggested_root_cause}
          </p>
        </div>
      ) : (
        <p className="mt-4 text-sm leading-6 text-slate-400">
          Run a failure simulation to calculate affected services, blast radius, and the critical dependency path.
        </p>
      )}
    </section>
  );
}

function Insight({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-3 rounded border border-slate-800 bg-slate-900/70 p-3">
      <div className="text-cyan-300">{icon}</div>
      <div>
        <div className="text-xs text-slate-500">{label}</div>
        <div className="font-semibold text-white">{value}</div>
      </div>
    </div>
  );
}
