"""Tests for TechDebtLedger FastAPI endpoints."""

import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from techdebt.api.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"


def test_scan_invalid_path() -> None:
    response = client.post("/scan", json={"repo_path": "/nonexistent/path", "name": "test"})
    assert response.status_code == 400


def test_scan_valid_path() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir + "/app.py").write_text("# TODO: fix this\ndef f(): pass\n")
        response = client.post("/scan", json={"repo_path": tmpdir, "name": "test-repo"})
        assert response.status_code == 200
        data = response.json()
        assert "scan_id" in data
        assert "debt_score" in data


def test_get_summary_not_found() -> None:
    response = client.get("/scan/nonexistent/summary")
    assert response.status_code == 404


def test_scan_and_get_summary() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir + "/app.py").write_text("# FIXME: urgent bug\n# TODO: cleanup\n")
        scan_response = client.post("/scan", json={"repo_path": tmpdir, "name": "test"})
        scan_id = scan_response.json()["scan_id"]

        summary_response = client.get(f"/scan/{scan_id}/summary")
        assert summary_response.status_code == 200
        data = summary_response.json()
        assert data["repo_name"] == "test"
        assert data["todo_count"] >= 2


def test_scan_and_get_roadmap() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir + "/app.py").write_text("# FIXME: fix me\n")
        scan_response = client.post("/scan", json={"repo_path": tmpdir, "name": "test"})
        scan_id = scan_response.json()["scan_id"]

        roadmap_response = client.get(f"/scan/{scan_id}/roadmap")
        assert roadmap_response.status_code == 200
        data = roadmap_response.json()
        assert "roadmap" in data