"""Tech debt data models."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class DebtItem(BaseModel):
    """A single tech debt item."""

    id: str
    category: str
    file_path: str
    line_number: int = 0
    description: str
    severity: str = Field("medium", description="low/medium/high/critical")
    estimated_hours: float = Field(1.0, description="Estimated remediation hours")
    snippet: str = ""


class ComplexityHotspot(BaseModel):
    """A file with high cyclomatic complexity."""

    file_path: str
    complexity_score: int
    function_count: int
    avg_function_length: float
    long_functions: list[str] = Field(default_factory=list)


class TodoItem(BaseModel):
    """An annotated debt item from source comments."""

    file_path: str
    line_number: int
    tag: str
    message: str
    author: str = ""


class DependencyDebt(BaseModel):
    """An outdated dependency."""

    name: str
    current_version: str
    latest_version: str = ""
    age_days: int = 0
    has_known_cve: bool = False
    severity: str = "low"


class DebtSummary(BaseModel):
    """Summary of tech debt for a repository."""

    scan_id: str
    repo_name: str
    repo_path: str
    total_items: int = 0
    critical_items: int = 0
    high_items: int = 0
    medium_items: int = 0
    low_items: int = 0
    debt_score: int = Field(0, description="0-100 debt score, higher = more debt")
    estimated_remediation_hours: float = 0.0
    complexity_hotspots: int = 0
    todo_count: int = 0
    stale_dependencies: int = 0
    narrative: Optional[str] = None


class RoadmapItem(BaseModel):
    """A prioritized tech debt payoff item."""

    rank: int
    category: str
    description: str
    file_path: str
    severity: str
    estimated_hours: float
    business_value: str
    recommended_sprint: int = 1