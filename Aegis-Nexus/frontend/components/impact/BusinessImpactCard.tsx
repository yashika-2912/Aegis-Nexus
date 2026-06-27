import { TelemetrySnapshot } from "@/types";

interface Props {
  telemetry: TelemetrySnapshot | null;
  agentOutput?: string;
}

export default function BusinessImpactCard({ telemetry, agentOutput }: Props) {
  const iw = telemetry?.incident_window;
  const failedReqs = iw?.failed_requests || 0;
  const failedCheckouts = iw?.failed_checkouts || 0;
  const affectedUsers = Math.round(failedReqs * 3.5);
  const revenueAtRisk = (failedCheckouts * 149.99).toFixed(2);

  let priority = "P4";
  if (iw?.anomaly_type === "5xx_spike" && failedCheckouts > 5) priority = "P1";
  else if (iw?.anomaly_type === "5xx_spike") priority = "P2";
  else if (iw?.anomaly_type === "404_spike" && failedReqs > 10) priority = "P2";
  else if (iw?.active) priority = "P3";

  const slaRisk = ["P1", "P2"].includes(priority) && failedCheckouts > 0;

  return (
    <div className="bg-nexus-panel border border-nexus-border rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Business Impact</h3>
      <div className="grid grid-cols-2 gap-3 mb-3">
        <div>
          <p className="text-xs text-gray-500">Affected Users (est.)</p>
          <p className="text-xl font-bold text-nexus-accent">{affectedUsers}</p>
          <p className="text-xs text-gray-600">×3.5 multiplier on {failedReqs} failed reqs</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Revenue at Risk</p>
          <p className="text-xl font-bold text-nexus-red">${revenueAtRisk}</p>
          <p className="text-xs text-gray-600">{failedCheckouts} failed checkouts × $149.99</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Priority</p>
          <p className={`text-xl font-bold ${priority === "P1" ? "text-nexus-red" : priority === "P2" ? "text-nexus-yellow" : "text-gray-300"}`}>{priority}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">SLA Risk</p>
          <p className={`text-xl font-bold ${slaRisk ? "text-nexus-red" : "text-nexus-green"}`}>{slaRisk ? "YES" : "No"}</p>
        </div>
      </div>
      {agentOutput && (
        <p className="text-sm text-gray-400 border-t border-nexus-border pt-3 italic">{agentOutput}</p>
      )}
    </div>
  );
}
