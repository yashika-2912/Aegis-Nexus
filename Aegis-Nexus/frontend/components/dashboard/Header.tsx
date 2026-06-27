import { RadioTower } from "lucide-react";

export function Header({ connected }: { connected: boolean }) {
  return (
    <header className="flex flex-col gap-3 border-b border-slate-800 bg-slate-950/80 px-5 py-4 backdrop-blur md:flex-row md:items-center md:justify-between">
      <div>
        <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Aegis Nexus Phase 1</p>
        <h1 className="mt-1 text-2xl font-semibold text-white">Real-Time Infrastructure Monitoring</h1>
      </div>
      <div className="flex items-center gap-2 rounded border border-slate-800 bg-slate-900 px-3 py-2 text-sm text-slate-300">
        <RadioTower className={`h-4 w-4 ${connected ? "text-emerald-300" : "text-rose-300"}`} />
        {connected ? "Live telemetry connected" : "Waiting for telemetry"}
      </div>
    </header>
  );
}
