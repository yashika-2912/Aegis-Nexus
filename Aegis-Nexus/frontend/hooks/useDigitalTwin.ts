"use client";

import { useCallback, useEffect, useState } from "react";

import { digitalTwinApi } from "@/services/digitalTwinApi";
import type { ImpactAnalysis, TwinGraph } from "@/types/digitalTwin";

export function useDigitalTwin() {
  const [graph, setGraph] = useState<TwinGraph | null>(null);
  const [analysis, setAnalysis] = useState<ImpactAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadGraph = useCallback(async () => {
    setLoading(true);
    try {
      setGraph(await digitalTwinApi.graph());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load graph");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadGraph();
  }, [loadGraph]);

  const simulateFailure = async (serviceId: string) => {
    const result = await digitalTwinApi.simulateFailure(serviceId);
    setAnalysis(result);
    setGraph(result.graph);
  };

  const reset = async () => {
    const result = await digitalTwinApi.reset();
    setGraph(result);
    setAnalysis(null);
  };

  return { graph, analysis, loading, error, simulateFailure, reset, reload: loadGraph };
}
