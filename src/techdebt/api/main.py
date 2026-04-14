"""FastAPI application for TechDebtLedger."""

from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from techdebt.core.config import DebtConfig
from techdebt.core.engine import scan_repo, build_roadmap
from techdebt.core.narrator import generate_debt_narrative
from techdebt.models.debt import DebtSummary, RoadmapItem

app = FastAPI(
    title="TechDebtLedger",
    description="Automated tech debt tracking for regulated industries",
    version="0.1.0",
)

config = DebtConfig.from_env()
_scan_store: dict[str, tuple[list, DebtSummary]] = {}


class ScanRequest(BaseModel):
    repo_path: str
    name: str = ""


class HealthResponse(BaseModel):
    status: str
    version: str
    industry: str


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0", industry=config.industry)


@app.post("/scan")
def scan_repository(request: ScanRequest) -> dict:
    repo_path = Path(request.repo_path)
    if not repo_path.exists():
        raise HTTPException(status_code=400, detail=f"Path not found: {request.repo_path}")

    repo_name = request.name or repo_path.name
    scan_id, items, summary = scan_repo(repo_path, repo_name, config)
    _scan_store[scan_id] = (items, summary)

    return {
        "scan_id": scan_id,
        "repo": repo_name,
        "total_items": summary.total_items,
        "debt_score": summary.debt_score,
        "message": f"Scan complete. Use /scan/{scan_id}/summary for full results.",
    }


@app.get("/scan/{scan_id}/summary")
def get_summary(scan_id: str) -> DebtSummary:
    if scan_id not in _scan_store:
        raise HTTPException(status_code=404, detail=f"Scan not found: {scan_id}")
    _, summary = _scan_store[scan_id]
    return summary


@app.get("/scan/{scan_id}/roadmap")
def get_roadmap(scan_id: str) -> dict:
    if scan_id not in _scan_store:
        raise HTTPException(status_code=404, detail=f"Scan not found: {scan_id}")
    items, summary = _scan_store[scan_id]
    roadmap = build_roadmap(items)
    return {
        "scan_id": scan_id,
        "repo": summary.repo_name,
        "total_sprints": max((r.recommended_sprint for r in roadmap), default=0),
        "roadmap": [r.model_dump() for r in roadmap],
    }


@app.get("/scan/{scan_id}/hotspots")
def get_hotspots(scan_id: str) -> dict:
    if scan_id not in _scan_store:
        raise HTTPException(status_code=404, detail=f"Scan not found: {scan_id}")
    items, summary = _scan_store[scan_id]
    hotspots = [i for i in items if i.category == "complexity"]
    return {
        "scan_id": scan_id,
        "count": len(hotspots),
        "hotspots": [h.model_dump() for h in hotspots[:20]],
    }


@app.get("/scan/{scan_id}/todos")
def get_todos(scan_id: str) -> dict:
    if scan_id not in _scan_store:
        raise HTTPException(status_code=404, detail=f"Scan not found: {scan_id}")
    items, summary = _scan_store[scan_id]
    todos = [i for i in items if i.category == "annotated_debt"]
    return {
        "scan_id": scan_id,
        "count": len(todos),
        "todos": [t.model_dump() for t in todos[:50]],
    }


@app.get("/scan/{scan_id}/narrative")
def get_narrative(scan_id: str) -> dict:
    if scan_id not in _scan_store:
        raise HTTPException(status_code=404, detail=f"Scan not found: {scan_id}")
    items, summary = _scan_store[scan_id]
    narrative = generate_debt_narrative(summary, industry=config.industry)
    return {
        "scan_id": scan_id,
        "repo": summary.repo_name,
        "debt_score": summary.debt_score,
        "narrative": narrative,
    }


def run() -> None:
    import uvicorn
    uvicorn.run("techdebt.api.main:app", host=config.host, port=config.port, reload=False)


if __name__ == "__main__":
    run()