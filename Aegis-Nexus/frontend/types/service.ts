export type ServiceStatus = "Healthy" | "Warning" | "Critical";

export interface Dependency {
  id: string;
  name: string;
  status: ServiceStatus;
}

export interface MonitoredService {
  id: string;
  name: string;
  kind: "frontend" | "api" | "worker" | "database";
  description: string;
  owner: string;
  status: ServiceStatus;
  available: boolean;
  dependencies: Dependency[];
}
