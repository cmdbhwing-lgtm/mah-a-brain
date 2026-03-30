#!/usr/bin/env bash
# ----------------------------------------------------------
# Mah-a-Brain Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/cmdbhwing-lgtm/mah-a-brain/main/install.sh | bash
# ----------------------------------------------------------
set -euo pipefail

REPO="https://github.com/cmdbhwing-lgtm/mah-a-brain.git"
INSTALL_DIR="${MAB_INSTALL_DIR:-$HOME/mah-a-brain}"
PORT="${MAB_PORT:-8080}"

info()  { printf '\033[1;34m[INFO]\033[0m %s\n' "$*"; }
warn()  { printf '\033[1;33m[WARN]\033[0m %s\n' "$*"; }
error() { printf '\033[1;31m[ERROR]\033[0m %s\n' "$*"; exit 1; }

# ---- Detect platform ----
OS="$(uname -s)"
ARCH="$(uname -m)"
info "Detected: $OS $ARCH"

# ---- Check prerequisites ----
command -v git   >/dev/null 2>&1 || error "git is required. Install it first."
command -v python3 >/dev/null 2>&1 || error "python3 is required (3.9+)."

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
info "Python version: $PYTHON_VERSION"

# ---- Clone or update ----
if [ -d "$INSTALL_DIR" ]; then
    info "Updating existing installation at $INSTALL_DIR..."
    cd "$INSTALL_DIR"
    git pull --ff-only origin main || warn "Could not fast-forward; using existing code."
else
    info "Cloning repository to $INSTALL_DIR..."
    git clone "$REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# ---- Method selection ----
USE_DOCKER=false
if command -v docker >/dev/null 2>&1 && command -v docker compose >/dev/null 2>&1; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" = true ]; then
    info "Docker detected -- using containerized deployment."
    docker compose up --build -d
    info "Mah-a-Brain is running at http://localhost:$PORT"
    info "  Health check: curl http://localhost:$PORT/api/health"
    info "  Logs:         docker compose logs -f"
    info "  Stop:         docker compose down"
else
    info "Docker not found -- using Python virtual environment."

    # Create venv
    python3 -m venv .venv
    source .venv/bin/activate

    # Ensure pip
    python3 -m ensurepip --upgrade 2>/dev/null || true
    python3 -m pip install --upgrade pip

    # Install deps
    python3 -m pip install -r requirements.txt

    # Create data dirs
    mkdir -p data vault/cad vault/memory vault/ingestion

    info "Installation complete."
    info ""
    info "To start the server:"
    info "  cd $INSTALL_DIR"
    info "  source .venv/bin/activate"
    info "  uvicorn main:app --host 0.0.0.0 --port $PORT"
    info ""
    info "Health check: curl http://localhost:$PORT/api/health"

    # Optional: install Ollama
    if ! command -v ollama >/dev/null 2>&1; then
        warn "Ollama not found. For LLM chat, install it:"
        warn "  curl -fsSL https://ollama.com/install.sh | sh"
        warn "  ollama pull llama3.2"
    else
        info "Ollama detected. Pull a model if you haven't:"
        info "  ollama pull llama3.2"
    fi
fi

info "Done. Visit http://localhost:$PORT/docs for API documentation."
