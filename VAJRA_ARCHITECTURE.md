# Vajra God Mode Exocortex -- System Architecture

```
=======================================================================
  VAJRA GOD MODE EXOCORTEX - SYSTEM ARCHITECTURE
=======================================================================
  USER: Samrat
  STYLE: Mac OS X (Glassmorphism), Event-Driven, Autonomous AI

  [ TIER 1: FRONTEND - MAC OS X EXOCORTEX ]
  (Next.js / React + Vite + Tailwind + Framer Motion)
  |
  |-->  Glassmorphism UI (Draggable Windows, Dock, Control Center)
  |-->  Neural Graph Dashboard (Visualizes active background agents)
  `-->  WebSockets Client (Receives live telemetry & upgrade prompts)
        |
  [ WSS / REST API ]  <-->  (Bi-directional Real-Time Data Flow)
        |
  [ TIER 2: BACKEND - THE API GATEWAY ]
  (FastAPI + Python Asyncio)
  |
  |-->  /api/health         (Health check + platform info)
  |-->  /api/status         (CPU / GPU / RAM / Disk / Network metrics)
  |-->  /api/execute        (Command echo endpoint -- future execution)
  |-->  /api/sync/device    (Ingestion endpoint for Smartphone payloads) [L2+]
  `-->  WebSocket Manager   (Broadcasts Leecher logs & System alerts)
        |
  [ TIER 3: AUTONOMY & NEURAL WIRING ]
  (Background Daemons + Task Queues)
  |
  |-->  [Mega Pattern Leecher]  (Python Watchdog)              [Level 2]
  |     `-->  Continuously monitors local directories & sync folders
  |     `-->  Categorizes and indexes data silently without UI lag
  |
  |-->  [Neural Sleep Cycle]  (APScheduler / Celery)           [Level 3]
  |     `-->  Tracks user activity heuristics
  |     `-->  1 AM - 6 AM: Enters "Deep Sleep" (Halts heavy GPU tasks)
  |     `-->  Wakes up with a UI spike animation upon user login
  |
  `-->  [God-Mode Upgrade Engine]  (Subprocess + Git)          [Level 3]
        `-->  Polls for system upgrades
        `-->  Triggers native-looking UI Modal for God Mode permission
        `-->  Executes git pull && docker-compose build safely

  [ TIER 4: THE MEMORY VAULT ]
  |
  |-->  PostgreSQL / SQLite  (Task states, Leecher logs, Settings)
  `-->  Local File System    (Raw Smartphone Dumps & Extracted Patterns)

  [ TIER 5: COMMERCIAL LAYER ]                                [Level 4]
  |
  |-->  Tenant API Gateway  (/v1/chat/completions -- OpenAI-compatible)
  |-->  Token Metering & Billing  (PostgreSQL tenant_usage table)
  |-->  GPU Queue Saver  (Celery + Redis sequential processing)
  |-->  Client Dashboard  (Light-themed Next.js for tenants)
  `-->  God Mode Oversight  (MRR panel, Kill Switch)

  [ TIER 6: MEGATRON DISTRIBUTED CLUSTER ]                    [Level 5]
  |
  |-->  Industrial Mega Leecher  (.STEP/.STL/.IGES/.NC parser)
  |-->  Headless CAD/CFD Engine  (OpenSCAD + OpenFOAM in containers)
  |-->  G-Code & CAM Generator  (CNC-ready toolpath generation)
  |-->  Cluster Orchestration  (K8s / Ray.io / Celery + RabbitMQ)
  `-->  3D Viewport  (react-three-fiber for in-browser CAD viewing)
=======================================================================
```

## Current Implementation: Level 1 (Foundation)

This repository implements Level 1 of the Vajra Exocortex:

- **Backend**: FastAPI server with real system metrics (CPU, GPU, RAM, Disk, Network),
  WebSocket live telemetry stream, and an echo command endpoint.
- **Frontend**: React (Vite) + Tailwind CSS + Framer Motion with macOS-style
  Glassmorphism design, animated metric rings, per-core CPU charts, a bottom dock,
  and a terminal view.
- **Infrastructure**: Multi-stage Dockerfile (Node build + Python runtime),
  docker-compose for local development.

## Execution Protocol

1. **Level 1** (this PR): Foundation UI + API + live metrics
2. **Level 2**: Add Mega Pattern Leecher (watchdog), WebSocket crawler feed, draggable windows
3. **Level 3**: Neural Sleep Cycle, God Mode Upgrade Engine, Celery/Redis task queue
4. **Level 4**: Multi-tenant SaaS layer, API key management, token billing
5. **Level 5**: Distributed cluster, CAD/CFD simulation, 3D viewport
