import type { TelemetryUpdate } from "@/types/websocket";
import { WS_URL } from "@/utils/constants";

export function connectTelemetrySocket(onUpdate: (update: TelemetryUpdate) => void): WebSocket {
  const socket = new WebSocket(WS_URL);
  socket.onmessage = (event) => {
    const payload = JSON.parse(event.data) as TelemetryUpdate;
    if (payload.type === "telemetry.update") {
      onUpdate(payload);
    }
  };
  socket.onopen = () => socket.send("connected");
  return socket;
}
