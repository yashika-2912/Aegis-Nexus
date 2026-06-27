"use client";

import { useState } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import KpiRow from "@/components/dashboard/KpiRow";
import ServiceGrid from "@/components/dashboard/ServiceGrid";
import LiveLineChart from "@/components/charts/LiveLineChart";
import DependencyGraph from "@/components/graph/DependencyGraph";
import AgentReasoningPanel from "@/components/incidents/AgentReasoningPanel";
import BusinessImpactCard from "@/components/impact/BusinessImpactCard";
import RemediationPanel from "@/components/healing/RemediationPanel";
import HistoryTable from "@/components/learning/HistoryTable";

export default function NexusDashboard() {
  const {
    connected, telemetry, agentSteps, pipelineActive, recovery,
    incidents, learningStats, executeHeal, reanalyze, resetAll,
  } = useWebSocket();
  const [executing, setExecuting] = useState(false);

  const handleExecute = async () => {
    setExecuting(true);
    try { await executeHeal(); } finally { setExecuting(false); }
  };

  const sherlockOut = agentSteps.find(s => s.agent === "Sherlock")?.output;

  return (
    <div className="min-h-screen p-4 md:p-6 space-y-4">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            <span className="text-nexus-accent">Aegis</span> Nexus
          </h1>
          <p className="text-sm text-gray-500">Autonomous SRE Command Center — monitoring Aegis Shop</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${connected ? "bg-nexus-green" : "bg-nexus-red animate-pulse"}`} />
          <span className="text-xs text-gray-500">{connected ? "Connected" : "Reconnecting..."}</span>
        </div>
      </header>

      <KpiRow telemetry={telemetry} connected={connected} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          <LiveLineChart telemetry={telemetry} />
          <DependencyGraph telemetry={telemetry} />
          <ServiceGrid telemetry={telemetry} />
        </div>
        <div className="space-y-4">
          <AgentReasoningPanel steps={agentSteps} active={pipelineActive} />
          <BusinessImpactCard telemetry={telemetry} agentOutput={sherlockOut} />
          <RemediationPanel
            onExecute={handleExecute}
            onReanalyze={() => reanalyze()}
            onReset={resetAll}
            recovery={recovery}
            executing={executing}
          />
        </div>
      </div>

      <HistoryTable incidents={incidents} stats={learningStats} />
    </div>
  );
}
