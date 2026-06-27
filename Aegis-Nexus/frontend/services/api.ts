import type { MetricsResponse } from "@/types/metric";
import type { MonitoredService } from "@/types/service";
import type { SystemHealth } from "@/types/websocket";
import { API_BASE_URL } from "@/utils/constants";
import { endpoints } from "./endpoints";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  services: () => getJson<MonitoredService[]>(endpoints.services),
  metrics: () => getJson<MetricsResponse>(endpoints.metrics),
  health: () => getJson<SystemHealth & { status: string }>(endpoints.health),
};
