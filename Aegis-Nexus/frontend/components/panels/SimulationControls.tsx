import { RotateCcw, ServerCrash, TriangleAlert } from "lucide-react";

export function SimulationControls({
  onPaymentDbFailure,
  onPaymentServiceFailure,
  onReset,
}: {
  onPaymentDbFailure: () => void;
  onPaymentServiceFailure: () => void;
  onReset: () => void;
}) {
  return (
    <section className="rounded border border-slate-800 bg-slate-950 p-4">
      <h2 className="text-sm font-semibold text-white">Simulation Controls</h2>
      <div className="mt-4 grid gap-3">
        <button
          onClick={onPaymentDbFailure}
          className="flex items-center justify-center gap-2 rounded bg-rose-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-rose-500"
        >
          <ServerCrash className="h-4 w-4" />
          Simulate Payment DB Failure
        </button>
        <button
          onClick={onPaymentServiceFailure}
          className="flex items-center justify-center gap-2 rounded bg-orange-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-orange-500"
        >
          <TriangleAlert className="h-4 w-4" />
          Simulate Payment Service Failure
        </button>
        <button
          onClick={onReset}
          className="flex items-center justify-center gap-2 rounded border border-slate-700 px-3 py-2 text-sm font-semibold text-slate-200 transition hover:bg-slate-900"
        >
          <RotateCcw className="h-4 w-4" />
          Reset Simulation
        </button>
      </div>
    </section>
  );
}
