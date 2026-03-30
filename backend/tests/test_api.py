"""Tests for the Vajra Base Engine API."""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "operational"
    assert "uptime_seconds" in data
    assert "engine" in data


def test_status_endpoint():
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "cpu" in data
    assert "memory" in data
    assert "disk" in data
    assert "network" in data
    assert "timestamp" in data
    # Validate CPU sub-fields
    assert "usage_pct" in data["cpu"]
    assert "cores_logical" in data["cpu"]
    # Validate memory sub-fields
    assert "total_gb" in data["memory"]
    assert "usage_pct" in data["memory"]


def test_execute_endpoint():
    resp = client.post("/api/execute", json={"command": "hello world"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["received"] == "hello world"
    assert "Vajra" in data["echo"]
    assert data["status"] == "queued"


def test_execute_empty_command():
    resp = client.post("/api/execute", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["received"] == ""


def test_websocket_metrics():
    with client.websocket_connect("/ws/metrics") as ws:
        ws.send_text("ping")
        data = ws.receive_json()
        assert data.get("pong") is True
