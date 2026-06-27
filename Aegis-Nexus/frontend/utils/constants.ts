export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://localhost:8010";

export const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8010/ws";

export const STATUS_COLORS = {
  Healthy: "text-emerald-300 bg-emerald-500/10 border-emerald-400/30",
  Warning: "text-amber-300 bg-amber-500/10 border-amber-400/30",
  Critical: "text-rose-300 bg-rose-500/10 border-rose-400/30",
} as const;
