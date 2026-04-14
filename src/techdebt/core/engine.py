"""Tech debt aggregation and scoring engine."""

from __future__ import annotations

import uuid
from pathlib import Path

from techdebt.models.debt import DebtItem, DebtSummary, RoadmapItem
from techdebt.scanners.complexity import scan_complexity, complexity_to_debt_items
from techdebt.scanners.todos import scan_todos, todos_to_debt_items
from techdebt.scanners.dependencies import scan_dependencies, dependencies_to_debt_items

SEVERITY_WEIGHTS = {"critical": 40, "high": 20, "medium": 8, "low": 2}
SEVERITY_HOURS = {"critical": 8.0, "high": 4.0, "medium": 2.0, "low": 0.5}

BUSINESS_VALUE = {
    "complexity": "Reduces incident blast radius and improves onboarding speed",
    "annotated_debt": "Addresses known issues before they become incidents",
    "dependency": "Reduces CVE exposure and maintains supportability",
}


def scan_repo(repo_path: Path, repo_name: str, config: object) -> tuple[str, list[DebtItem], DebtSummary]:
    """Run all scanners against a repository and return debt inventory."""
    scan_id = str(uuid.uuid4())[:8]

    complexity_hotspots = scan_complexity(
        repo_path,
        threshold=getattr(config, "complexity_threshold", 10),
        max_files=getattr(config, "max_files", 200),
    )
    todos = scan_todos(repo_path, max_files=getattr(config, "max_files", 200))
    deps = scan_dependencies(repo_path)

    items: list[DebtItem] = []
    items.extend(complexity_to_debt_items(complexity_hotspots))
    items.extend(todos_to_debt_items(todos))
    items.extend(dependencies_to_debt_items(deps))

    summary = _compute_summary(scan_id, repo_name, str(repo_path), items,
                                len(complexity_hotspots), len(todos), len(deps))
    return scan_id, items, summary


def _compute_summary(
    scan_id: str,
    repo_name: str,
    repo_path: str,
    items: list[DebtItem],
    hotspot_count: int,
    todo_count: int,
    dep_count: int,
) -> DebtSummary:
    critical = sum(1 for i in items if i.severity == "critical")
    high = sum(1 for i in items if i.severity == "high")
    medium = sum(1 for i in items if i.severity == "medium")
    low = sum(1 for i in items if i.severity == "low")

    raw_score = sum(SEVERITY_WEIGHTS.get(i.severity, 2) for i in items)
    debt_score = min(100, raw_score)

    total_hours = sum(i.estimated_hours for i in items)

    return DebtSummary(
        scan_id=scan_id,
        repo_name=repo_name,
        repo_path=repo_path,
        total_items=len(items),
        critical_items=critical,
        high_items=high,
        medium_items=medium,
        low_items=low,
        debt_score=debt_score,
        estimated_remediation_hours=round(total_hours, 1),
        complexity_hotspots=hotspot_count,
        todo_count=todo_count,
        stale_dependencies=dep_count,
    )


def build_roadmap(items: list[DebtItem], max_items: int = 20) -> list[RoadmapItem]:
    """Build a prioritized tech debt payoff roadmap."""
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_items = sorted(items, key=lambda x: (severity_order.get(x.severity, 3), -x.estimated_hours))

    roadmap = []
    sprint = 1
    sprint_hours = 0.0
    sprint_capacity = 16.0

    for rank, item in enumerate(sorted_items[:max_items], 1):
        if sprint_hours + item.estimated_hours > sprint_capacity:
            sprint += 1
            sprint_hours = 0.0

        sprint_hours += item.estimated_hours
        roadmap.append(RoadmapItem(
            rank=rank,
            category=item.category,
            description=item.description,
            file_path=item.file_path,
            severity=item.severity,
            estimated_hours=item.estimated_hours,
            business_value=BUSINESS_VALUE.get(item.category, "Improves codebase maintainability"),
            recommended_sprint=sprint,
        ))

    return roadmap