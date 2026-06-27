import { Database, Layers3, Server, Workflow } from "lucide-react";

import type { TwinEdge, TwinNode } from "@/types/digitalTwin";

export function NodeDetailsPanel({
  node,
  nodes,
  edges,
}: {
  node: TwinNode | null;
  nodes: TwinNode[];
  edges: TwinEdge[];
}) {
  if (!node) {
    return <Panel title="Node Details">Select a service node to inspect dependencies and dependents.</Panel>;
  }

  const dependencies = edges
    .filter((edge) => edge.source === node.id)
    .map((edge) => nodes.find((item) => item.id === edge.target)?.name)
    .filter(Boolean);
  const dependents = edges
    .filter((edge) => edge.target === node.id)
    .map((edge) => nodes.find((item) => item.id === edge.source)?.name)
    .filter(Boolean);
  const Icon = node.type === "Database" ? Database : node.type === "Gateway" ? Workflow : node.type === "Cache" ? Layers3 : Server;

  return (
    <Panel title="Node Details">
      <div className="flex items-center gap-3">
        <Icon className="h-5 w-5 text-cyan-300" />
        <div>
          <div className="font-semibold text-white">{node.name}</div>
          <div className="text-xs text-slate-500">{node.type}</div>
        </div>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3">
        <Stat label="Status" value={node.status} />
        <Stat label="Health" value={`${node.health}%`} />
      </div>
      <List title="Dependencies" values={dependencies} empty="No downstream dependencies" />
      <List title="Dependents" values={dependents} empty="No upstream dependents" />
      <div className="mt-4 text-xs text-slate-500">Last updated: {new Date(node.last_updated).toLocaleString()}</div>
    </Panel>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded border border-slate-800 bg-slate-950 p-4 text-sm text-slate-400">
      <h2 className="mb-4 text-sm font-semibold text-white">{title}</h2>
      {children}
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-slate-800 bg-slate-900/70 p-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-1 font-semibold text-white">{value}</div>
    </div>
  );
}

function List({ title, values, empty }: { title: string; values: (string | undefined)[]; empty: string }) {
  return (
    <div className="mt-4">
      <h3 className="text-xs font-semibold uppercase text-slate-500">{title}</h3>
      <div className="mt-2 space-y-2">
        {values.length ? (
          values.map((value) => (
            <div key={value} className="rounded bg-slate-900 px-3 py-2 text-xs text-slate-300">
              {value}
            </div>
          ))
        ) : (
          <p className="text-xs text-slate-500">{empty}</p>
        )}
      </div>
    </div>
  );
}
