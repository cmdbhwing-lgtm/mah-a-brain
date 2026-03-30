# Mah-a-Brain

A deployable LLM agent with persistent memory, real-time telemetry, API-key billing, file ingestion watching, and CAD generation.

## Features

| Feature | Description |
|---|---|
| **LLM Chat** | Local inference via [Ollama](https://ollama.com) (configurable model) |
| **Persistent Memory** | ChromaDB vector store -- the agent recalls past interactions automatically |
| **Memory Ingestion** | POST text to `/api/memory/leach` to feed domain knowledge |
| **Real-time Telemetry** | WebSocket at `/ws/telemetry` streams CPU, memory doc count, heartbeats |
| **File Watcher** | Drops into `vault/ingestion/` are broadcast to all telemetry clients |
| **API-key Billing** | Create tenants, assign credits, auto-debit per call |
| **CAD Generation** | OpenSCAD-based STL generation from parametric SCAD code |
| **Docker Ready** | Single `docker compose up` to run everything |

## Quick Start

### Option A: Docker (recommended)

```bash
docker compose up --build -d
```

The API is available at `http://localhost:8080`. Persistent data lives in `./data` and `./vault` on the host.

### Option B: Local Python

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Optional: Install Ollama for LLM support

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

## API Reference

### Health

```
GET /api/health
```

Returns system status, CPU usage, and feature availability flags.

### Chat

```
POST /api/chat
Content-Type: application/json

{"prompt": "Explain quantum computing", "api_key": ""}
```

If ChromaDB is loaded, past interactions are recalled and injected as context (RAG-lite). The `api_key` field is optional; when provided, credits are debited.

### Memory

```
POST /api/memory/leach
{"text": "Domain-specific knowledge...", "source_name": "manual"}

GET /api/memory/search?query=quantum&n=5
```

### CAD Generation

```
POST /api/cad/generate?api_key=
```

Generates an interlocking-brick `.stl` file via OpenSCAD and stores it in `vault/cad/`.

### Tenants / Billing

```
POST /api/tenants          -- create a new API key
GET  /api/tenants/{key}/credits  -- check remaining credits
```

### Telemetry WebSocket

```
ws://localhost:8080/ws/telemetry
```

Streams periodic CPU usage, memory document count, and event notifications (file ingestion, chat, CAD jobs).

## Configuration

All settings are controlled via environment variables:

| Variable | Default | Description |
|---|---|---|
| `LLM_MODEL` | `llama3.2` | Ollama model name |
| `DATA_DIR` | `data` | SQLite database directory |
| `VAULT_CAD_DIR` | `vault/cad` | CAD output directory |
| `VAULT_MEMORY_DIR` | `vault/memory` | ChromaDB persistence directory |
| `VAULT_INGESTION_DIR` | `vault/ingestion` | Watched directory for file drops |
| `CREDIT_COST` | `1.5` | Credits debited per authenticated API call |
| `LOG_LEVEL` | `INFO` | Python logging level |

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Architecture

```
main.py              -- FastAPI application (single-file for simplicity)
requirements.txt     -- Python dependencies
Dockerfile           -- Container image with OpenSCAD
docker-compose.yml   -- One-command deployment
tests/test_api.py    -- API integration tests
data/                -- SQLite databases (billing, interactions)
vault/cad/           -- Generated SCAD/STL files
vault/memory/        -- ChromaDB persistent storage
vault/ingestion/     -- Drop files here; watcher broadcasts events
```

## License

MIT
