import { useState, useEffect, useRef, useCallback } from "react";

const WS_URL =
  (window.location.protocol === "https:" ? "wss://" : "ws://") +
  window.location.host +
  "/ws/metrics";

/**
 * Custom hook that maintains a live WebSocket connection to the backend
 * metrics stream, with automatic reconnection.
 */
export function useMetrics() {
  const [metrics, setMetrics] = useState(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      // Send periodic pings to keep connection alive
      ws._pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) ws.send("ping");
      }, 15_000);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (!data.pong) {
          setMetrics(data);
        }
      } catch {
        // ignore non-JSON frames
      }
    };

    ws.onclose = () => {
      setConnected(false);
      clearInterval(ws._pingInterval);
      // Reconnect after 3 seconds
      reconnectTimer.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimer.current);
      if (wsRef.current) {
        clearInterval(wsRef.current._pingInterval);
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { metrics, connected };
}

/**
 * Fallback: poll /api/status via REST if WebSocket is unavailable.
 */
export function useMetricsPolling(intervalMs = 3000) {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    let active = true;
    const poll = async () => {
      try {
        const res = await fetch("/api/status");
        if (res.ok && active) {
          setMetrics(await res.json());
        }
      } catch {
        // Swallow
      }
    };
    poll();
    const id = setInterval(poll, intervalMs);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, [intervalMs]);

  return metrics;
}
