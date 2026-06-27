import type { ImpactAnalysis, TwinGraph, TwinNode } from "@/types/digitalTwin";
import { API_BASE_URL } from "@/utils/constants";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/digital-twin${path}`, {
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!response.ok) {
    throw new Error(`Digital Twin request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const digitalTwinApi = {
  services: () => request<TwinNode[]>("/services"),
  graph: () => request<TwinGraph>("/graph"),
  simulateFailure: (serviceId: string) =>
    request<ImpactAnalysis>("/simulate/failure", {
      method: "POST",
      body: JSON.stringify({ service_id: serviceId }),
    }),
  reset: () => request<TwinGraph>("/reset", { method: "POST" }),
};
