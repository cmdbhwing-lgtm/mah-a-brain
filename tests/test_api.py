"""Tests for the Mah-a-Brain API endpoints."""

import pytest
from fastapi.testclient import TestClient

from main import app, DEFAULT_API_KEY


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_health(client: TestClient):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["version"] == "1.0.0"
    assert "cpu_percent" in body
    assert isinstance(body["ollama_available"], bool)
    assert isinstance(body["chroma_available"], bool)


def test_create_tenant(client: TestClient):
    resp = client.post("/api/tenants", json={"credits": 500})
    assert resp.status_code == 200
    body = resp.json()
    assert body["credits"] == 500
    assert body["api_key"].startswith("sk-mab-")


def test_get_credits(client: TestClient):
    resp = client.get(f"/api/tenants/{DEFAULT_API_KEY}/credits")
    assert resp.status_code == 200
    body = resp.json()
    assert body["credits"] > 0


def test_get_credits_unknown_key(client: TestClient):
    resp = client.get("/api/tenants/sk-nonexistent/credits")
    assert resp.status_code == 404


def test_chat_without_ollama(client: TestClient):
    """When Ollama is not installed the endpoint should still return 200
    with a helpful message rather than crashing."""
    resp = client.post("/api/chat", json={"prompt": "hello"})
    assert resp.status_code == 200
    body = resp.json()
    assert "response" in body


def test_cad_generate(client: TestClient):
    """CAD endpoint returns a structured response even when OpenSCAD is
    not installed (error message instead of crash)."""
    resp = client.post("/api/cad/generate")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in ("ok", "error")
    assert "job_id" in body


def test_memory_leach_without_chroma(client: TestClient):
    """If ChromaDB is available, leach should succeed; otherwise 503."""
    resp = client.post(
        "/api/memory/leach",
        json={"text": "test knowledge", "source_name": "unit-test"},
    )
    assert resp.status_code in (200, 503)


def test_memory_search_without_chroma(client: TestClient):
    resp = client.get("/api/memory/search", params={"query": "test"})
    assert resp.status_code in (200, 503)
