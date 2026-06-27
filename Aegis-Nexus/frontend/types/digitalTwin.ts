export type TwinStatus = "Healthy" | "Warning" | "Critical" | "Affected" | "Down";
export type TwinServiceType = "Gateway" | "Microservice" | "Database" | "Queue" | "Cache";

export interface TwinNode {
  id: string;
  name: string;
  type: TwinServiceType;
  status: TwinStatus;
  health: number;
  last_updated: string;
}

export interface TwinEdge {
  id: string;
  source: string;
  target: string;
  relationship: "DEPENDS_ON";
}

export interface TwinGraph {
  nodes: TwinNode[];
  edges: TwinEdge[];
}

export interface ImpactAnalysis {
  failure_origin: string;
  affected_services: string[];
  blast_radius: number;
  critical_path: string[];
  suggested_root_cause: string;
  graph: TwinGraph;
}
