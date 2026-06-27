"use client";

import { useMemo } from "react";
import ReactFlow, { Background, Controls, MarkerType } from "reactflow";
import "reactflow/dist/style.css";
import { STATUS_COLORS, TelemetrySnapshot } from "@/types";

interface Props {
  telemetry: TelemetrySnapshot | null;
}

const POSITIONS: Record<string, { x: number; y: number }> = {
  "api-gateway": { x: 250, y: 0 },
  "user-service": { x: 0, y: 150 },
  "product-service": { x: 170, y: 150 },
  "order-service": { x: 340, y: 150 },
  "payment-service": { x: 510, y: 150 },
};

export default function DependencyGraph({ telemetry }: Props) {
  const graph = telemetry?.graph;

  const { nodes, edges } = useMemo(() => {
    if (!graph) return { nodes: [], edges: [] };
    const nodes = graph.nodes.map(n => {
      const color = STATUS_COLORS[n.status] || STATUS_COLORS.healthy;
      return {
        id: n.id,
        data: { label: n.label },
        position: POSITIONS[n.id] || { x: 0, y: 0 },
        style: {
          background: color + "22",
          border: `2px solid ${color}`,
          borderRadius: 8,
          padding: "8px 16px",
          fontSize: 12,
          color: "#e5e7eb",
          fontWeight: 600,
        },
      };
    });
    const edges = graph.edges.map(e => ({
      id: `${e.source}-${e.target}`,
      source: e.source,
      target: e.target,
      animated: telemetry?.incident_window?.affected_service === e.source,
      style: { stroke: "#374151" },
      markerEnd: { type: MarkerType.ArrowClosed, color: "#374151" },
    }));
    return { nodes, edges };
  }, [graph, telemetry]);

  return (
    <div className="bg-nexus-panel border border-nexus-border rounded-lg p-4 h-[280px]">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">Dependency Graph</h3>
      <ReactFlow nodes={nodes} edges={edges} fitView proOptions={{ hideAttribution: true }}
        nodesDraggable={false} nodesConnectable={false} elementsSelectable={false}>
        <Background color="#1f2937" gap={16} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
