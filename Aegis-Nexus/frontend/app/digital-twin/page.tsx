"use client";

import { useMemo, useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { Loading } from "@/components/common/Loading";
import { Header } from "@/components/dashboard/Header";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { DigitalTwinGraph } from "@/components/graph/DigitalTwinGraph";
import { ImpactAnalysisPanel } from "@/components/panels/ImpactAnalysisPanel";
import { NodeDetailsPanel } from "@/components/panels/NodeDetailsPanel";
import { SimulationControls } from "@/components/panels/SimulationControls";
import { useDigitalTwin } from "@/hooks/useDigitalTwin";
import type { TwinNode } from "@/types/digitalTwin";

export default function DigitalTwinPage() {
  const { graph, analysis, loading, error, simulateFailure, reset } = useDigitalTwin();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selectedNode = useMemo(
    () => graph?.nodes.find((node) => node.id === selectedId) ?? graph?.nodes[0] ?? null,
    [graph?.nodes, selectedId],
  );

  const handleSelect = (node: TwinNode) => setSelectedId(node.id);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="min-w-0 flex-1">
          <Header connected={Boolean(graph)} />
          <div className="space-y-5 p-4 md:p-5">
            <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-orange-300">Phase 2</p>
                <h1 className="text-2xl font-semibold text-white">Enterprise Digital Twin</h1>
                <p className="mt-1 text-sm text-slate-400">Dependency graph, failure propagation, and blast-radius analysis.</p>
              </div>
            </div>
            {error ? <ErrorState message={error} /> : null}
            {loading || !graph ? (
              <Loading />
            ) : (
              <section className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
                <DigitalTwinGraph graph={graph} selectedId={selectedNode?.id ?? null} onSelect={handleSelect} />
                <div className="space-y-5">
                  <SimulationControls
                    onPaymentDbFailure={() => void simulateFailure("payment-db")}
                    onPaymentServiceFailure={() => void simulateFailure("payment-service")}
                    onReset={() => void reset()}
                  />
                  <ImpactAnalysisPanel analysis={analysis} />
                  <NodeDetailsPanel node={selectedNode} nodes={graph.nodes} edges={graph.edges} />
                </div>
              </section>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
