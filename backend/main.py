"""
Vajra God Mode Exocortex - Backend Engine
Level 1: Foundation API with live system metrics and WebSocket telemetry.
"""
from __future__ import annotations

import asyncio
import logging
import platform
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger("vajra")


# ---------------------------------------------------------------------------
# WebSocket connection manager
# ---------------------------------------------------------------------------
class ConnectionManager:
    """Manages active WebSocket connections for live metric broadcasting."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active_connections.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        try:
            self.active_connections.remove(ws)
        except ValueError:
            pass  # Already removed by broadcast cleanup

    async def broadcast(self, data: Dict[str, Any]) -> None:
        stale: List[WebSocket] = []
        for conn in self.active_connections:
            try:
                await conn.send_json(data)
            except Exception:
                stale.append(conn)
        for conn in stale:
            try:
                self.active_connections.remove(conn)
            except ValueError:
                pass


manager = ConnectionManager()

# Background task handle
_metrics_task: Optional[asyncio.Task] = None


async def _broadcast_metrics_loop() -> None:
    """Push system metrics to all connected WebSocket clients every 2s."""
    while True:
        try:
            payload = _collect_system_metrics()
            await manager.broadcast(payload)
        except asyncio.CancelledError:
            raise  # Let cancellation propagate
        except Exception:
            logger.exception("Error in metrics broadcast loop")
        await asyncio.sleep(2)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _metrics_task
    _metrics_task = asyncio.create_task(_broadcast_metrics_loop())
    yield
    if _metrics_task:
        _metrics_task.cancel()
        try:
            await _metrics_task
        except asyncio.CancelledError:
            pass


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Vajra Base Engine",
    description="Level 1 Foundation API - System metrics, health, and command execution.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _collect_system_metrics() -> Dict[str, Any]:
    cpu_freq = psutil.cpu_freq()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()

    # Attempt GPU info (nvidia-smi) -- graceful fallback
    gpu_info: Optional[Dict[str, Any]] = None
    try:
        import subprocess

        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = [p.strip() for p in result.stdout.strip().split(",")]
            if len(parts) >= 5:
                gpu_info = {
                    "name": parts[0],
                    "utilization_pct": float(parts[1]),
                    "memory_used_mb": float(parts[2]),
                    "memory_total_mb": float(parts[3]),
                    "temperature_c": float(parts[4]),
                }
    except Exception:
        pass

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu": {
            "usage_pct": psutil.cpu_percent(interval=0),
            "per_core_pct": psutil.cpu_percent(interval=0, percpu=True),
            "freq_mhz": cpu_freq.current if cpu_freq else None,
            "cores_physical": psutil.cpu_count(logical=False),
            "cores_logical": psutil.cpu_count(logical=True),
        },
        "memory": {
            "total_gb": round(mem.total / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "usage_pct": mem.percent,
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "usage_pct": disk.percent,
        },
        "network": {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
        },
        "gpu": gpu_info,
    }


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health():
    """Basic health check."""
    return {
        "status": "operational",
        "engine": "Vajra Base Engine v0.1.0",
        "uptime_seconds": round(time.time() - psutil.boot_time(), 1),
        "platform": platform.platform(),
        "python": platform.python_version(),
    }


@app.get("/api/status")
async def system_status():
    """Return a full snapshot of current system metrics."""
    return _collect_system_metrics()


@app.post("/api/execute")
async def execute_command(payload: Dict[str, Any]):
    """
    Echo-style command endpoint.
    Accepts {"command": "..."} and returns a structured response.
    In future levels this will route to actual execution engines.
    """
    command = payload.get("command", "")
    return {
        "received": command,
        "echo": f"[Vajra] Command acknowledged: {command}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "queued",
    }


# ---------------------------------------------------------------------------
# WebSocket endpoint -- live metrics stream
# ---------------------------------------------------------------------------
@app.websocket("/ws/metrics")
async def ws_metrics(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            # Keep connection alive; optionally receive client pings
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_json({"pong": True})
    except (WebSocketDisconnect, RuntimeError, ConnectionResetError):
        pass
    finally:
        manager.disconnect(ws)


# ---------------------------------------------------------------------------
# Serve frontend static build (production)
# ---------------------------------------------------------------------------
_frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="static")
