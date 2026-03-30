# Mah-a-Brain

A deployable LLM agent with persistent memory, real-time telemetry, API-key billing, file ingestion watching, and CAD generation with downloadable file links.

## Features

| Feature | Description |
|---|---|
| **LLM Chat** | Local inference via [Ollama](https://ollama.com) with configurable model and RAG-enhanced context |
| **Persistent Memory** | ChromaDB vector store -- the agent recalls past interactions automatically |
| **Memory Ingestion** | Feed domain knowledge via `/api/memory/leach` |
| **Real-time Telemetry** | WebSocket at `/ws/telemetry` streams CPU, memory doc count, heartbeats |
| **File Watcher** | Files dropped into `vault/ingestion/` are broadcast to all telemetry clients |
| **API-key Billing** | Create tenants, assign credits, auto-debit per call |
| **CAD Generation** | OpenSCAD-based STL generation with **downloadable file links** |
| **CAD File Browser** | List and download all generated CAD files via `/api/cad/list` |
| **Docker Ready** | Single `docker compose up` to run everything |

---

## Installation

### Method 1: One-Line Installer (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/cmdbhwing-lgtm/mah-a-brain/main/install.sh | bash
```

This auto-detects your environment:
- If **Docker** is available, it builds and runs a container.
- Otherwise, it creates a **Python virtual environment** and installs dependencies.

You can customize the install location and port:

```bash
MAB_INSTALL_DIR=/opt/mah-a-brain MAB_PORT=9090 bash install.sh
```

### Method 2: Docker Compose

```bash
git clone https://github.com/cmdbhwing-lgtm/mah-a-brain.git
cd mah-a-brain
docker compose up --build -d
```

Data persists in `./data` and `./vault` on the host. To stop: `docker compose down`.

### Method 3: Docker (standalone)

```bash
git clone https://github.com/cmdbhwing-lgtm/mah-a-brain.git
cd mah-a-brain
docker build -t mah-a-brain .
docker run -d -p 8080:8080 -v $(pwd)/data:/app/data -v $(pwd)/vault:/app/vault mah-a-brain
```

### Method 4: Python Virtual Environment

```bash
git clone https://github.com/cmdbhwing-lgtm/mah-a-brain.git
cd mah-a-brain
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p data vault/cad vault/memory vault/ingestion
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Method 5: pip install (system-wide)

```bash
git clone https://github.com/cmdbhwing-lgtm/mah-a-brain.git
cd mah-a-brain
pip install -r requirements.txt
python main.py
```

### Optional: Enable LLM Support

Install Ollama for local LLM inference:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

---

## API Reference

Once running, full interactive docs are available at `http://localhost:8080/docs` (Swagger UI).

### Health

```
GET /api/health
```

Returns system status, CPU usage, and feature availability flags.

### Chat (with memory recall)

```
POST /api/chat
Content-Type: application/json

{"prompt": "Explain quantum computing", "api_key": ""}
```

If ChromaDB is loaded, past interactions are recalled and injected as context. The `api_key` field is optional; when provided, credits are debited.

### Memory

```
POST /api/memory/leach
{"text": "Domain-specific knowledge...", "source_name": "manual"}

GET /api/memory/search?query=quantum&n=5
```

### CAD Generation with Download Links

```
POST /api/cad/generate?api_key=
```

Returns a response with a `download_url` field:

```json
{
  "status": "ok",
  "job_id": "cad_a1b2c3d4e5f6",
  "file": "vault/cad/cad_a1b2c3d4e5f6.stl",
  "message": "STL generated",
  "download_url": "/api/cad/download/cad_a1b2c3d4e5f6"
}
```

**Download a file:**

```
GET /api/cad/download/{job_id}
```

Returns the STL file as a binary download. Falls back to SCAD if STL was not generated.

**List all generated files:**

```
GET /api/cad/list
```

Returns all CAD files with download links:

```json
{
  "files": [
    {"job_id": "cad_a1b2c3", "filename": "cad_a1b2c3.stl", "size_bytes": 4096, "download_url": "/api/cad/download/cad_a1b2c3"}
  ],
  "count": 1
}
```

### Tenants / Billing

```
POST /api/tenants          -- create a new API key
GET  /api/tenants/{key}/credits  -- check remaining credits
```

### Telemetry WebSocket

```
ws://localhost:8080/ws/telemetry
```

Streams periodic CPU usage, memory document count, and event notifications.

---

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

---

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

---

## Architecture

```
main.py              -- FastAPI application (single-file for simplicity)
requirements.txt     -- Python dependencies
Dockerfile           -- Container image with OpenSCAD
docker-compose.yml   -- One-command deployment
install.sh           -- Auto-detecting installer script
tests/test_api.py    -- API integration tests
data/                -- SQLite databases (billing, interactions)
vault/cad/           -- Generated SCAD/STL files (downloadable)
vault/memory/        -- ChromaDB persistent storage
vault/ingestion/     -- Drop files here; watcher broadcasts events
```

## License

MIT
