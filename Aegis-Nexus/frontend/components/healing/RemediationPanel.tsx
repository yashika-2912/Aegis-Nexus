interface Props {
  onExecute: () => void;
  onReanalyze: () => void;
  onReset: () => void;
  recovery: Record<string, unknown> | null;
  executing?: boolean;
}

export default function RemediationPanel({ onExecute, onReanalyze, onReset, recovery, executing }: Props) {
  const before = recovery?.before as Record<string, unknown> | undefined;
  const after = recovery?.after as Record<string, unknown> | undefined;

  return (
    <div className="bg-nexus-panel border border-nexus-border rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Remediation</h3>
      <div className="flex flex-wrap gap-2 mb-4">
        <button onClick={onExecute} disabled={executing}
          className="px-4 py-2 bg-nexus-green text-black font-semibold text-sm rounded-lg hover:brightness-110 disabled:opacity-50">
          Execute Healer Action
        </button>
        <button onClick={onReanalyze}
          className="px-4 py-2 bg-nexus-purple text-white text-sm rounded-lg hover:brightness-110">
          Force Re-analyze
        </button>
        <button onClick={onReset}
          className="px-4 py-2 border border-nexus-border text-gray-400 text-sm rounded-lg hover:bg-nexus-border">
          Reset All
        </button>
      </div>
      {recovery && (
        <div className="space-y-2 text-sm">
          <div className="flex gap-4">
            <div className="flex-1 p-2 bg-red-950/30 border border-red-900 rounded">
              <p className="text-xs text-red-400 mb-1">Before</p>
              <p>Status: {String(before?.status_code ?? "—")}</p>
              <p>Latency: {String(before?.latency_ms ?? "—")}ms</p>
            </div>
            <div className="flex-1 p-2 bg-green-950/30 border border-green-900 rounded">
              <p className="text-xs text-green-400 mb-1">After</p>
              <p>Status: {String(after?.status_code ?? "—")}</p>
              <p>Latency: {String(after?.latency_ms ?? "—")}ms</p>
            </div>
          </div>
          <p className="text-gray-500">
            Outcome: <span className={recovery.outcome === "success" ? "text-nexus-green" : "text-nexus-red"}>{String(recovery.outcome)}</span>
            {" "}— Recovery: {String(recovery.recovery_time_ms ?? "—")}ms
          </p>
        </div>
      )}
    </div>
  );
}
