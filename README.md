# Mah-a-Brain

A deployable LLM agent with persistent memory, real-time telemetry, API-key billing, and CAD generation.

---

## Download & Install

### Step 1: Download

**Option A -- Download ZIP (easiest, no git needed):**

Go to **https://github.com/cmdbhwing-lgtm/mah-a-brain/archive/refs/heads/main.zip**, save the ZIP, and unzip it.

Or from terminal:

```bash
wget https://github.com/cmdbhwing-lgtm/mah-a-brain/archive/refs/heads/main.zip
unzip main.zip
cd mah-a-brain-main
```

**Option B -- Clone with git:**

```bash
git clone https://github.com/cmdbhwing-lgtm/mah-a-brain.git
cd mah-a-brain
```

**Option C -- One command (auto-installs everything):**

```bash
curl -fsSL https://raw.githubusercontent.com/cmdbhwing-lgtm/mah-a-brain/main/install.sh | bash
```

This detects your system and sets everything up. Skip to Step 3 if you use this.

### Step 2: Install & Run

Pick whichever method matches your setup:

**With Docker (recommended -- nothing else to install):**

```bash
docker compose up --build -d
```

Done. The server is running at `http://localhost:8080`.

**Without Docker (plain Python):**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

The server is running at `http://localhost:8080`.

### Step 3: Verify it works

Open your browser to **http://localhost:8080/docs** for the interactive API dashboard.

Or from terminal:

```bash
curl http://localhost:8080/api/health
```

You should see:

```json
{"status": "ok", "version": "1.0.0", "cpu_percent": 2.5, "ollama_available": false, "chroma_available": true, "memory_docs": 0}
```

### Step 4 (optional): Enable LLM chat

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

Restart the server. Now `/api/chat` will use the local LLM with memory-enhanced responses.

---

## 4 Ways to See Output

### 1. Browser Dashboard (visual UI)

Open **http://localhost:8080/dashboard** in any browser. You get:
- Live CPU and memory doc metrics
- Chat input box (type a prompt, see the AI reply)
- "Generate CAD" button with clickable download links
- Real-time telemetry log (WebSocket stream)

### 2. Swagger API Docs (interactive testing)

Open **http://localhost:8080/docs** -- click any endpoint, fill in parameters, hit "Execute", and see the JSON response.

### 3. CLI Tool (terminal output)

```bash
python3 cli.py health                          # system status
python3 cli.py chat "What is gravity?"         # chat with AI
python3 cli.py leach "Our product costs $5"    # feed knowledge
python3 cli.py search "product"                # search memory
python3 cli.py cad                             # generate CAD + get download link
python3 cli.py files                           # list all files with download URLs
python3 cli.py telemetry                       # live stream in terminal
```

Change the server address with `--base http://your-server:8080`.

### 4. curl / any HTTP client

```bash
curl http://localhost:8080/api/health
curl -X POST http://localhost:8080/api/chat -H "Content-Type: application/json" -d '{"prompt":"hello"}'
```

---

## What You Can Do

| Endpoint | What it does |
|---|---|
| `GET /api/health` | Check system status |
| `POST /api/chat` | Chat with local LLM (memory-enhanced) |
| `POST /api/memory/leach` | Feed knowledge into the AI's memory |
| `GET /api/memory/search?query=...` | Search stored memories |
| `POST /api/cad/generate` | Generate a 3D model (STL file) |
| `GET /api/cad/list` | List all generated CAD files with download links |
| `GET /api/cad/download/{job_id}` | Download a generated STL/SCAD file |
| `POST /api/tenants` | Create an API key with credits |
| `GET /api/tenants/{key}/credits` | Check remaining credits |
| `ws://localhost:8080/ws/telemetry` | Live CPU/memory/event stream |

Full interactive docs: **http://localhost:8080/docs**

---

## Examples

**Chat with the AI:**

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is quantum computing?"}'
```

**Feed it knowledge:**

```bash
curl -X POST http://localhost:8080/api/memory/leach \
  -H "Content-Type: application/json" \
  -d '{"text": "Our company sells red widgets for $5 each.", "source_name": "product-info"}'
```

**Generate a 3D model and download it:**

```bash
# Generate
curl -X POST http://localhost:8080/api/cad/generate

# The response includes a download_url. Use it:
curl -O http://localhost:8080/api/cad/download/cad_abc123
```

**List all generated files:**

```bash
curl http://localhost:8080/api/cad/list
```

---

## Configuration

Set these environment variables to customize behavior:

| Variable | Default | What it does |
|---|---|---|
| `LLM_MODEL` | `llama3.2` | Which Ollama model to use |
| `DATA_DIR` | `data` | Where databases are stored |
| `VAULT_CAD_DIR` | `vault/cad` | Where CAD files go |
| `VAULT_MEMORY_DIR` | `vault/memory` | Where ChromaDB stores memories |
| `VAULT_INGESTION_DIR` | `vault/ingestion` | Drop files here to trigger events |
| `CREDIT_COST` | `1.5` | Credits per authenticated API call |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Stopping / Restarting

**Docker:**

```bash
docker compose down          # stop
docker compose up -d         # restart
docker compose logs -f       # view logs
```

**Python:**

Press `Ctrl+C` to stop, then run `python3 main.py` again to restart.

---

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

---

## Project Structure

```
main.py              -- The entire backend (single file, ~500 lines)
requirements.txt     -- Python dependencies
Dockerfile           -- Container build
docker-compose.yml   -- One-command deployment
install.sh           -- Auto-detecting installer
tests/test_api.py    -- 10 integration tests
data/                -- Databases (auto-created)
vault/cad/           -- Generated 3D files (downloadable)
vault/memory/        -- AI memory storage
vault/ingestion/     -- File drop zone (watched for events)
```

## License

MIT
