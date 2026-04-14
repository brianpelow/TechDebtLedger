"""Tests for the debt scoring engine."""

import tempfile
from pathlib import Path
from techdebt.core.config import DebtConfig
from techdebt.core.engine import scan_repo, build_roadmap
from techdebt.models.debt import DebtItem


def test_scan_repo_empty_dir() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        config = DebtConfig()
        scan_id, items, summary = scan_repo(Path(tmpdir), "test-repo", config)
        assert scan_id
        assert summary.repo_name == "test-repo"
        assert summary.debt_score >= 0


def test_scan_repo_with_todos() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / "app.py").write_text("# TODO: fix this\n# FIXME: and this\n")
        config = DebtConfig()
        scan_id, items, summary = scan_repo(path, "test-repo", config)
        assert summary.todo_count >= 2


def test_build_roadmap_empty() -> None:
    roadmap = build_roadmap([])
    assert roadmap == []


def test_build_roadmap_prioritizes_critical() -> None:
    items = [
        DebtItem(id="1", category="complexity", file_path="a.py",
                 description="low item", severity="low", estimated_hours=0.5),
        DebtItem(id="2", category="annotated_debt", file_path="b.py",
                 description="critical item", severity="critical", estimated_hours=8.0),
        DebtItem(id="3", category="dependency", file_path="c.py",
                 description="high item", severity="high", estimated_hours=4.0),
    ]
    roadmap = build_roadmap(items)
    assert roadmap[0].severity == "critical"
    assert roadmap[1].severity == "high"


def test_build_roadmap_assigns_sprints() -> None:
    items = [
        DebtItem(id=str(i), category="complexity", file_path="a.py",
                 description=f"item {i}", severity="high", estimated_hours=6.0)
        for i in range(5)
    ]
    roadmap = build_roadmap(items)
    assert max(r.recommended_sprint for r in roadmap) >= 2