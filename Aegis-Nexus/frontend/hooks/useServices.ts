"use client";

import { useEffect, useState } from "react";

import { api } from "@/services/api";
import type { MonitoredService } from "@/types/service";

export function useServices() {
  const [services, setServices] = useState<MonitoredService[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .services()
      .then(setServices)
      .finally(() => setLoading(false));
  }, []);

  return { services, loading };
}
