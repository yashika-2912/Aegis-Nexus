import { AGENT_COLORS, AgentStep } from "@/types";

interface Props {
  steps: AgentStep[];
  active: boolean;
}

const ORDER = ["Sentinel", "Sherlock", "Oracle", "Healer"];

export default function AgentReasoningPanel({ steps, active }: Props) {
  const sorted = ORDER.map(name => steps.find(s => s.agent === name)).filter(Boolean) as AgentStep[];

  return (
    <div className="bg-nexus-panel border border-nexus-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">AI Agent Pipeline</h3>
        {active && <span className="text-xs text-nexus-accent agent-glow px-2 py-1 rounded bg-cyan-950">Running...</span>}
      </div>
      {sorted.length === 0 ? (
        <p className="text-gray-600 text-sm">Waiting for anomaly detection...</p>
      ) : (
        <div className="space-y-3">
          {sorted.map(step => (
            <div key={step.agent} className="border border-nexus-border rounded-lg p-3"
              style={{ borderLeftColor: AGENT_COLORS[step.agent], borderLeftWidth: 3 }}>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-semibold text-sm" style={{ color: AGENT_COLORS[step.agent] }}>{step.agent}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${step.status === "complete" ? "bg-green-900 text-green-400" : "bg-yellow-900 text-yellow-400"}`}>
                  {step.status}
                </span>
              </div>
              <p className="text-sm text-gray-400 leading-relaxed">{step.output}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
