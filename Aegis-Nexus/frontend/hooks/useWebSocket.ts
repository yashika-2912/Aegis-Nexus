"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AgentStep, Incident, LearningStat, TelemetrySnapshot } from "@/types";
import type { TelemetryUpdate } from "@/types/websocket";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8010/ws";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

export function useWebSocket() {
  const [connected, setConnected] = useState(false);
  const [telemetry, setTelemetry] = useState<TelemetrySnapshot | null>(null);
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [pipelineActive, setPipelineActive] = useState(false);
  const [recovery, setRecovery] = useState<Record<string, unknown> | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [data, setData] = useState<TelemetryUpdate | null>(null);
  const [learningStats, setLearningStats] = useState<LearningStat[]>([]);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchIncidents = useCallback(async () => {
    try {
      const r = await fetch(`${API_URL}/api/incidents`);
      const d = await r.json();
      setIncidents(d.incidents || []);
    } catch { /* ignore */ }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const r = await fetch(`${API_URL}/api/learning/stats`);
      const d = await r.json();
      setLearningStats(d.stats || []);
    } catch { /* ignore */ }
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      setError(null);
    };
    ws.onclose = () => {
      setConnected(false);
      reconnectRef.current = setTimeout(connect, 2000);
    };
    ws.onerror = () => {
      setError("WebSocket connection failed.");
      ws.close();
    };

    ws.onmessage = (evt) => {
      try {
        const raw = JSON.parse(evt.data) as unknown;
        if (typeof raw !== "object" || raw === null || !("type" in raw)) return;

        const msg = raw as { type: string; payload?: unknown };
        if (msg.type === "telemetry.update") {
          setData(raw as TelemetryUpdate);
        } else if (msg.type === "telemetry" && typeof msg.payload === "object" && msg.payload !== null) {
          setTelemetry(msg.payload as TelemetrySnapshot);
        } else if (msg.type === "pipeline_event" && typeof msg.payload === "object" && msg.payload !== null) {
          const step = msg.payload as { type: string; agent?: string; step?: AgentStep };
          if (step.type === "agent_start") {
            setPipelineActive(true);
          } else if (step.type === "agent_step" && step.step) {
            setAgentSteps((prev) => [...prev.filter((s) => s.agent !== step.step!.agent), step.step!]);
          } else if (step.type === "pipeline_complete") {
            setPipelineActive(false);
            void fetchIncidents();
            void fetchStats();
          }
        } else if (msg.type === "anomaly_detected") {
          setPipelineActive(true);
        } else if (msg.type === "recovery" && typeof msg.payload === "object" && msg.payload !== null) {
          setRecovery(msg.payload as Record<string, unknown>);
          setPipelineActive(false);
          void fetchIncidents();
          void fetchStats();
        } else if (msg.type === "reset") {
          setAgentSteps([]);
          setRecovery(null);
          setPipelineActive(false);
        }
      } catch {
        setError("Invalid WebSocket message.");
      }
    };
  }, [fetchIncidents, fetchStats]);

  useEffect(() => {
    connect();
    fetchIncidents();
    fetchStats();
    const ping = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "ping" }));
      }
    }, 30000);
    return () => {
      clearInterval(ping);
      if (reconnectRef.current) {
        clearTimeout(reconnectRef.current);
      }
      wsRef.current?.close();
    };
  }, [connect, fetchIncidents, fetchStats]);

  const executeHeal = async () => {
    const r = await fetch(`${API_URL}/api/heal/execute`, { method: "POST" });
    const data = await r.json();
    if (!data.error) setRecovery(data);
    void fetchIncidents();
    void fetchStats();
    return data;
  };

  const reanalyze = async (anomaly?: string, service?: string) => {
    setAgentSteps([]);
    const r = await fetch(`${API_URL}/api/incidents/reanalyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ anomaly_type: anomaly, affected_service: service }),
    });
    return r.json();
  };

  const resetAll = async () => {
    await fetch(`${API_URL}/api/reset`, { method: "POST" });
    setAgentSteps([]);
    setRecovery(null);
    fetchIncidents();
    fetchStats();
  };

  return {
    connected,
    telemetry,
    agentSteps,
    pipelineActive,
    recovery,
    incidents,
    learningStats,
    executeHeal,
    reanalyze,
    resetAll,
    fetchIncidents,
    fetchStats,
    data,
    error,
  };
}
