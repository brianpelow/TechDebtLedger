"""Tests for debt data models."""

from techdebt.models.debt import DebtItem, DebtSummary, RoadmapItem, TodoItem, DependencyDebt


def test_debt_item_defaults() -> None:
    item = DebtItem(id="test-1", category="complexity", file_path="src/app.py",
                    description="High complexity function")
    assert item.severity == "medium"
    assert item.estimated_hours == 1.0


def test_debt_summary_defaults() -> None:
    summary = DebtSummary(scan_id="abc123", repo_name="test-repo", repo_path="/tmp/test")
    assert summary.total_items == 0
    assert summary.debt_score == 0


def test_roadmap_item_defaults() -> None:
    item = RoadmapItem(rank=1, category="complexity", description="Fix complex function",
                       file_path="src/app.py", severity="high", estimated_hours=4.0,
                       business_value="Reduces incident risk")
    assert item.recommended_sprint == 1


def test_todo_item() -> None:
    todo = TodoItem(file_path="src/app.py", line_number=42, tag="FIXME",
                    message="This needs to be refactored")
    assert todo.tag == "FIXME"
    assert todo.line_number == 42