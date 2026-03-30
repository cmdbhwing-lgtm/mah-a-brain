"""
Mah-a-Brain: A deployable LLM agent with persistent memory, telemetry,
API-key billing, file ingestion, and CAD generation.

Run with: uvicorn main:app --host 0.0.0.0 --port 8080
"""

import asyncio
import logging
import os
import secrets
import sqlite3
import subprocess
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import psutil
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from rich.console import Console
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
VAULT_CAD_DIR = Path(os.getenv("VAULT_CAD_DIR", "vault/cad"))
VAULT_MEMORY_DIR = Path(os.getenv("VAULT_MEMORY_DIR", "vault/memory"))
VAULT_INGESTION_DIR = Path(os.getenv("VAULT_INGESTION_DIR", "vault/ingestion"))
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
CREDIT_COST_PER_CALL = float(os.getenv("CREDIT_COST", "1.5"))
DEFAULT_API_KEY = "sk-mah-a-brain-default"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("mah-a-brain")
console = Console()

# ---------------------------------------------------------------------------
# Directory bootstrap
# ---------------------------------------------------------------------------

for directory in [DATA_DIR, VAULT_CAD_DIR, VAULT_MEMORY_DIR, VAULT_INGESTION_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Optional dependency detection
# ---------------------------------------------------------------------------

try:
    import ollama  # type: ignore[import-untyped]

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    import chromadb  # type: ignore[import-untyped]

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

# ---------------------------------------------------------------------------
# Database helpers (billing + interaction log)
# ---------------------------------------------------------------------------


def _get_billing_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DATA_DIR / "billing.db"), check_same_thread=False)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tenants "
        "(api_key TEXT PRIMARY KEY, credits REAL DEFAULT 1000, created_at TEXT, last_used TEXT)"
    )
    conn.execute(
        "INSERT OR IGNORE INTO tenants VALUES (?, ?, ?, ?)",
        (DEFAULT_API_KEY, 999_999, datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    return conn


def _get_interaction_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DATA_DIR / "interactions.db"), check_same_thread=False)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS interactions "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, prompt TEXT, response TEXT, tool TEXT)"
    )
    conn.commit()
    return conn


billing_db = _get_billing_db()
interaction_db = _get_interaction_db()

# ---------------------------------------------------------------------------
# ChromaDB persistent memory
# ---------------------------------------------------------------------------

memory_collection = None
if CHROMA_AVAILABLE:
    _chroma_client = chromadb.PersistentClient(path=str(VAULT_MEMORY_DIR))
    memory_collection = _chroma_client.get_or_create_collection(name="agent_memory")

# ---------------------------------------------------------------------------
# Auth / billing dependency
# ---------------------------------------------------------------------------


def verify_api_key(api_key: str = "") -> bool:
    """Verify the API key exists and has remaining credits, then debit."""
    if not api_key:
        return True  # unauthenticated endpoints pass through
    row = billing_db.execute("SELECT credits FROM tenants WHERE api_key=?", (api_key,)).fetchone()
    if not row or row[0] <= 0:
        raise HTTPException(status_code=401, detail="Invalid or exhausted API key")
    billing_db.execute(
        "UPDATE tenants SET credits = credits - ?, last_used = ? WHERE api_key=?",
        (CREDIT_COST_PER_CALL, datetime.now(timezone.utc).isoformat(), api_key),
    )
    billing_db.commit()
    return True


# ---------------------------------------------------------------------------
# WebSocket telemetry hub
# ---------------------------------------------------------------------------

active_websockets: list[WebSocket] = []


async def broadcast(message: str) -> None:
    """Send a message to every connected telemetry client."""
    dead: list[WebSocket] = []
    for ws in active_websockets:
        try:
            await ws.send_text(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        active_websockets.remove(ws)


# ---------------------------------------------------------------------------
# File-system watcher (ingestion directory)
# ---------------------------------------------------------------------------


class IngestionHandler(FileSystemEventHandler):
    """Watches the ingestion vault and broadcasts new file events."""

    def on_created(self, event):  # type: ignore[override]
        if event.is_directory:
            return
        msg = f"[ingestion] new file: {event.src_path}"
        logger.info(msg)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(broadcast(msg))
        except RuntimeError:
            pass


_observer: Optional[Observer] = None

# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(application: FastAPI):
    global _observer
    console.print("[bold cyan]Starting Mah-a-Brain agent...[/bold cyan]")
    _observer = Observer()
    _observer.schedule(IngestionHandler(), str(VAULT_INGESTION_DIR), recursive=True)
    _observer.start()
    logger.info("File observer started on %s", VAULT_INGESTION_DIR)
    yield
    if _observer:
        _observer.stop()
        _observer.join()
    console.print("[bold cyan]Mah-a-Brain agent stopped.[/bold cyan]")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Mah-a-Brain",
    version="1.0.0",
    description="Deployable LLM agent with persistent memory, telemetry, billing, and CAD generation.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8192)
    api_key: str = ""


class ChatResponse(BaseModel):
    response: str
    memory_enhanced: bool = False


class LeachRequest(BaseModel):
    text: str = Field(..., min_length=1)
    source_name: str = "unknown"
    api_key: str = ""


class CADResponse(BaseModel):
    status: str
    job_id: str = ""
    file: str = ""
    message: str = ""


class TenantCreate(BaseModel):
    credits: float = 1000.0


class HealthResponse(BaseModel):
    status: str
    version: str
    cpu_percent: float
    ollama_available: bool
    chroma_available: bool
    memory_docs: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return system health and capability status."""
    doc_count = 0
    if memory_collection is not None:
        doc_count = memory_collection.count()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        cpu_percent=psutil.cpu_percent(interval=0.1),
        ollama_available=OLLAMA_AVAILABLE,
        chroma_available=CHROMA_AVAILABLE,
        memory_docs=doc_count,
    )


# -- Chat with optional memory recall -----------------------------------------


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Chat with the local LLM. If ChromaDB is available, past interactions
    are recalled and injected as context (RAG-lite)."""
    if req.api_key:
        verify_api_key(req.api_key)

    if not OLLAMA_AVAILABLE:
        return ChatResponse(response="Ollama is not installed. Install it to enable LLM chat.")

    # Recall relevant memories
    context = ""
    memory_used = False
    if memory_collection is not None and memory_collection.count() > 0:
        results = memory_collection.query(query_texts=[req.prompt], n_results=3)
        if results["documents"] and results["documents"][0]:
            context = "\n".join(results["documents"][0])
            memory_used = True

    system_msg = "You are Mah-a-Brain, a helpful AI agent."
    if context:
        system_msg += f"\n\nRelevant past context:\n{context}"

    try:
        res = ollama.chat(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": req.prompt},
            ],
        )
        reply = res["message"]["content"]
    except Exception as exc:
        logger.error("LLM error: %s", exc)
        return ChatResponse(response=f"LLM error: {exc}")

    # Persist the interaction
    interaction_db.execute(
        "INSERT INTO interactions (ts, prompt, response, tool) VALUES (?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), req.prompt, reply, "ollama"),
    )
    interaction_db.commit()

    if memory_collection is not None:
        memory_collection.add(
            documents=[f"User: {req.prompt}\nAssistant: {reply}"],
            metadatas=[{"source": "chat", "ts": datetime.now(timezone.utc).isoformat()}],
            ids=[f"chat_{secrets.token_hex(6)}"],
        )

    await broadcast(f"[chat] prompt={req.prompt[:60]}...")
    return ChatResponse(response=reply, memory_enhanced=memory_used)


# -- Memory ingestion ----------------------------------------------------------


@app.post("/api/memory/leach")
async def leach_memory(req: LeachRequest) -> dict:
    """Feed text into the persistent memory vault."""
    if req.api_key:
        verify_api_key(req.api_key)

    if memory_collection is None:
        raise HTTPException(status_code=503, detail="ChromaDB not available")

    doc_id = f"leach_{secrets.token_hex(6)}"
    memory_collection.add(
        documents=[req.text],
        metadatas=[{"source": req.source_name, "ts": datetime.now(timezone.utc).isoformat()}],
        ids=[doc_id],
    )
    logger.info("Leached document %s from source %s", doc_id, req.source_name)
    await broadcast(f"[memory] leached {doc_id} from {req.source_name}")
    return {"status": "ok", "doc_id": doc_id, "source": req.source_name}


@app.get("/api/memory/search")
async def search_memory(query: str, n: int = 5) -> dict:
    """Search the persistent memory vault."""
    if memory_collection is None:
        raise HTTPException(status_code=503, detail="ChromaDB not available")
    results = memory_collection.query(query_texts=[query], n_results=n)
    return {"results": results["documents"], "metadatas": results["metadatas"]}


# -- CAD generation (OpenSCAD) -------------------------------------------------


@app.post("/api/cad/generate", response_model=CADResponse)
async def generate_cad(api_key: str = "") -> CADResponse:
    """Generate a sample interlocking-brick STL via OpenSCAD."""
    if api_key:
        verify_api_key(api_key)

    job_id = f"cad_{secrets.token_hex(6)}"
    scad_code = (
        "difference() {\n"
        "  cube([200, 100, 40]);\n"
        "  translate([20, 20, 10]) cube([160, 60, 20]);\n"
        "  translate([0, 0, 40]) cube([30, 30, 10]);\n"
        "  translate([170, 0, 40]) cube([30, 30, 10]);\n"
        "  translate([0, 70, 40]) cube([30, 30, 10]);\n"
        "  translate([170, 70, 40]) cube([30, 30, 10]);\n"
        "}\n"
    )
    scad_path = VAULT_CAD_DIR / f"{job_id}.scad"
    stl_path = VAULT_CAD_DIR / f"{job_id}.stl"

    scad_path.write_text(scad_code)

    try:
        subprocess.run(
            ["openscad", "-o", str(stl_path), str(scad_path)],
            check=True,
            timeout=30,
            capture_output=True,
        )
    except FileNotFoundError:
        return CADResponse(status="error", job_id=job_id, message="OpenSCAD is not installed on this system")
    except subprocess.TimeoutExpired:
        return CADResponse(status="error", job_id=job_id, message="OpenSCAD timed out")
    except subprocess.CalledProcessError as exc:
        return CADResponse(status="error", job_id=job_id, message=f"OpenSCAD failed: {exc.stderr.decode()}")

    await broadcast(f"[cad] generated {job_id}")
    return CADResponse(status="ok", job_id=job_id, file=str(stl_path), message="STL generated")


# -- Tenant management ---------------------------------------------------------


@app.post("/api/tenants")
async def create_tenant(body: TenantCreate) -> dict:
    """Create a new API key with the given credit balance."""
    key = f"sk-mab-{secrets.token_hex(16)}"
    billing_db.execute(
        "INSERT INTO tenants VALUES (?, ?, ?, ?)",
        (key, body.credits, datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()),
    )
    billing_db.commit()
    return {"api_key": key, "credits": body.credits}


@app.get("/api/tenants/{api_key}/credits")
async def get_credits(api_key: str) -> dict:
    """Check remaining credits for an API key."""
    row = billing_db.execute("SELECT credits FROM tenants WHERE api_key=?", (api_key,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"api_key": api_key, "credits": row[0]}


# -- WebSocket telemetry -------------------------------------------------------


@app.websocket("/ws/telemetry")
async def telemetry_websocket(ws: WebSocket) -> None:
    """Stream live telemetry (CPU, memory docs, heartbeat) to connected clients."""
    await ws.accept()
    active_websockets.append(ws)
    logger.info("Telemetry client connected (%d total)", len(active_websockets))
    try:
        while True:
            await asyncio.sleep(3)
            doc_count = memory_collection.count() if memory_collection else 0
            await ws.send_text(
                f"[telemetry] cpu={psutil.cpu_percent():.1f}% "
                f"mem_docs={doc_count} "
                f"ts={datetime.now(timezone.utc).isoformat()}"
            )
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        if ws in active_websockets:
            active_websockets.remove(ws)
        logger.info("Telemetry client disconnected (%d remaining)", len(active_websockets))


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
