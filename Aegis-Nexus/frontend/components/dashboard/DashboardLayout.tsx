"use client";

import { motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";

import { CriticalServicesCard } from "@/components/cards/CriticalServicesCard";
import { HealthyServicesCard } from "@/components/cards/HealthyServicesCard";
import { SystemHealthCard } from "@/components/cards/SystemHealthCard";
import { WarningServicesCard } from "@/components/cards/WarningServicesCard";
import { CpuChart } from "@/components/charts/CpuChart";
import { LatencyChart } from "@/components/charts/LatencyChart";
import { MemoryChart } from "@/components/charts/MemoryChart";
import { RequestChart } from "@/components/charts/RequestChart";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { Loading } from "@/components/common/Loading";
import { ServiceCard } from "@/components/services/ServiceCard";
import { ServiceTable } from "@/components/services/ServiceTable";
import { EventTimeline } from "@/components/timeline/EventTimeline";
import { useMetrics } from "@/hooks/useMetrics";
import { useServices } from "@/hooks/useServices";
import { useSystemHealth } from "@/hooks/useSystemHealth";
import { useWebSocket } from "@/hooks/useWebSocket";
import type { MetricPoint } from "@/types/metric";
import type { ServiceStatus } from "@/types/service";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

export function DashboardLayout() {
  const { services: initialServices, loading: servicesLoading } = useServices();
  const { metrics: initialMetrics, loading: metricsLoading } = useMetrics();
  const { data, connected, error } = useWebSocket();
  const services = data?.services ?? initialServices;
  const metrics = data?.metrics ?? initialMetrics?.latest ?? [];
  const history = useMemo(
    () => data?.history ?? initialMetrics?.history ?? {},
    [data?.history, initialMetrics?.history],
  );
  const derivedHealth = useSystemHealth(metrics);
  const health = data?.health ?? derivedHealth;
  const events = data?.events ?? [];
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedId && services[0]) {
      setSelectedId(services[0].id);
    }
  }, [selectedId, services]);

  const selectedService = services.find((service) => service.id === selectedId) ?? services[0];
  const selectedMetric = metrics.find((metric) => metric.service_id === selectedService?.id);
  const selectedHistory = selectedService ? history[selectedService.id] ?? [] : [];
  const chartData = useMemo(() => mergeHistory(history), [history]);
  const loading = servicesLoading || metricsLoading;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="min-w-0 flex-1">
          <Header connected={connected} />
          <div className="space-y-5 p-4 md:p-5">
            {error ? <ErrorState message={error} /> : null}
            {loading && !data ? (
              <Loading />
            ) : services.length ? (
              <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
                <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  <SystemHealthCard value={health.system_health} />
                  <HealthyServicesCard healthy={health.healthy_services} total={health.total_services} />
                  <WarningServicesCard value={health.warnings} />
                  <CriticalServicesCard value={health.critical} />
                </section>

                <section className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
                  <div className="space-y-5">
                    <ServiceTable
                      services={services}
                      metrics={metrics}
                      selectedId={selectedService?.id ?? null}
                      onSelect={setSelectedId}
                    />
                    <div className="grid gap-4 xl:grid-cols-2">
                      <CpuChart data={chartData} />
                      <MemoryChart data={chartData} />
                      <RequestChart data={chartData} />
                      <LatencyChart data={chartData} />
                    </div>
                  </div>
                  <div className="space-y-5">
                    {selectedService ? (
                      <ServiceCard service={selectedService} metric={selectedMetric} history={selectedHistory} />
                    ) : null}
                    <EventTimeline events={events} />
                  </div>
                </section>
              </motion.div>
            ) : (
              <EmptyState label="No services are registered yet." />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

function mergeHistory(history: Record<string, MetricPoint[]>): MetricPoint[] {
  const byTime = new Map<string, MetricPoint[]>();
  Object.values(history).forEach((series) => {
    series.slice(-40).forEach((point) => {
      const bucket = point.timestamp.slice(0, 19);
      byTime.set(bucket, [...(byTime.get(bucket) ?? []), point]);
    });
  });
  return Array.from(byTime.entries())
    .map(([timestamp, points]) => ({
      service_id: "aggregate",
      timestamp,
      cpu: average(points.map((point) => point.cpu)),
      memory: average(points.map((point) => point.memory)),
      request_count: points.reduce((sum, point) => sum + point.request_count, 0),
      request_rate: points.reduce((sum, point) => sum + point.request_rate, 0),
      error_rate: average(points.map((point) => point.error_rate)),
      latency: average(points.map((point) => point.latency)),
      status: (points.some((point) => point.status === "Critical")
        ? "Critical"
        : points.some((point) => point.status === "Warning")
          ? "Warning"
          : "Healthy") as ServiceStatus,
      available: points.every((point) => point.available),
    }))
    .slice(-40);
}

function average(values: number[]): number {
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}
