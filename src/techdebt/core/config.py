"""Configuration for TechDebtLedger."""

from __future__ import annotations

import os
from pydantic import BaseModel, Field


class DebtConfig(BaseModel):
    """Runtime configuration for TechDebtLedger."""

    industry: str = Field("fintech", description="Industry context")
    complexity_threshold: int = Field(10, description="Cyclomatic complexity threshold")
    dependency_age_days: int = Field(365, description="Days before dependency considered stale")
    max_files: int = Field(200, description="Max files to scan per repo")
    host: str = Field("0.0.0.0", description="API server host")
    port: int = Field(8000, description="API server port")

    @classmethod
    def from_env(cls) -> "DebtConfig":
        return cls(
            industry=os.environ.get("DEBT_INDUSTRY", "fintech"),
        )