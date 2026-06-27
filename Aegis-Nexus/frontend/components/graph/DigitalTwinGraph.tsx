"use client";

import type { MouseEvent } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Edge,
  type Node,
} from "reactflow";
import "reactflow/dist/style.css";

import type { TwinGraph, TwinNode } from "@/types/digitalTwin";
import { DigitalTwinNode } from "./DigitalTwinNode";

const nodeTypes = { digitalTwin: DigitalTwinNode };

const positions: Record<string, { x: number; y: number }> = {
  "api-gateway": { x: 420, y: 20 },
  "user-service": { x: 120, y: 210 },
  "order-service": { x: 420, y: 210 },
  "payment-service": { x: 720, y: 210 },
  "payment-db": { x: 720, y: 430 },
  "order-db": { x: 420, y: 430 },
  "redis-cache": { x: 120, y: 430 },
  "event-queue": { x: 420, y: 620 },
};

export function DigitalTwinGraph({
  graph,
  selectedId,
  onSelect,
}: {
  graph: TwinGraph;
  selectedId: string | null;
  onSelect: (node: TwinNode) => void;
}) {
  const nodes: Node<TwinNode>[] = graph.nodes.map((node) => ({
    id: node.id,
    type: "digitalTwin",
    position: positions[node.id] ?? { x: 0, y: 0 },
    data: node,
    selected: node.id === selectedId,
  }));

  const edges: Edge[] = graph.edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    animated: isImpactedEdge(edge.source, edge.target, graph),
    label: edge.relationship,
    style: {
      stroke: isImpactedEdge(edge.source, edge.target, graph) ? "#fb923c" : "#475569",
      strokeWidth: isImpactedEdge(edge.source, edge.target, graph) ? 2.5 : 1.5,
    },
  }));

  const handleNodeClick = (_event: MouseEvent, node: Node<TwinNode>) => onSelect(node.data);

  return (
    <div className="h-[680px] min-h-[520px] overflow-hidden rounded border border-slate-800 bg-slate-950">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodeClick={handleNodeClick}
        fitView
        minZoom={0.35}
      >
        <MiniMap pannable zoomable nodeStrokeWidth={3} />
        <Controls />
        <Background color="#1e293b" gap={22} />
      </ReactFlow>
    </div>
  );
}

function isImpactedEdge(source: string, target: string, graph: TwinGraph): boolean {
  const sourceNode = graph.nodes.find((node) => node.id === source);
  const targetNode = graph.nodes.find((node) => node.id === target);
  return Boolean(
    sourceNode &&
      targetNode &&
      ["Affected", "Down"].includes(sourceNode.status) &&
      ["Affected", "Down"].includes(targetNode.status),
  );
}
