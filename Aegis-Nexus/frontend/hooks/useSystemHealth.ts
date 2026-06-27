"use client";

import { useMemo } from "react";

import type { MetricPoint } from "@/types/metric";
import { calculateSystemHealth } from "@/utils/healthCalculator";

export function useSystemHealth(metrics: MetricPoint[]) {
  return useMemo(() => calculateSystemHealth(metrics), [metrics]);
}
