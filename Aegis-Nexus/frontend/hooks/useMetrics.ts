"use client";

import { useEffect, useState } from "react";

import { api } from "@/services/api";
import type { MetricsResponse } from "@/types/metric";

export function useMetrics() {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .metrics()
      .then(setMetrics)
      .finally(() => setLoading(false));
  }, []);

  return { metrics, loading };
}
