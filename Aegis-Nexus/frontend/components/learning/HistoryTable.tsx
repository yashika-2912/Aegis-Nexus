import { Incident, LearningStat } from "@/types";

interface Props {
  incidents: Incident[];
  stats: LearningStat[];
}

export default function HistoryTable({ incidents, stats }: Props) {
  return (
    <div className="bg-nexus-panel border border-nexus-border rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Learning Engine</h3>

      {stats.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mb-4">
          {stats.map(s => (
            <div key={s.action} className="border border-nexus-border rounded p-2 text-xs">
              <p className="font-medium text-gray-300 truncate">{s.action}</p>
              <p className="text-nexus-green">{s.success_rate}% success</p>
              <p className="text-gray-500">avg {s.avg_recovery_ms}ms ({s.total} runs)</p>
            </div>
          ))}
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-gray-500 border-b border-nexus-border">
              <th className="text-left py-2 pr-2">Time</th>
              <th className="text-left py-2 pr-2">Type</th>
              <th className="text-left py-2 pr-2">Service</th>
              <th className="text-left py-2 pr-2">Action</th>
              <th className="text-left py-2 pr-2">Recovery</th>
              <th className="text-left py-2">Outcome</th>
            </tr>
          </thead>
          <tbody>
            {incidents.slice(0, 10).map(inc => (
              <tr key={inc.id} className="border-b border-nexus-border/50 text-gray-400">
                <td className="py-2 pr-2">{new Date(inc.triggered_at * 1000).toLocaleTimeString()}</td>
                <td className="py-2 pr-2">{inc.anomaly_type}</td>
                <td className="py-2 pr-2">{inc.affected_service}</td>
                <td className="py-2 pr-2">{inc.action_taken || "—"}</td>
                <td className="py-2 pr-2">{inc.recovery_time_ms ? `${inc.recovery_time_ms.toFixed(0)}ms` : "—"}</td>
                <td className={`py-2 ${inc.outcome === "success" ? "text-nexus-green" : inc.outcome === "failed" ? "text-nexus-red" : "text-gray-500"}`}>
                  {inc.outcome}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
