"""Nightly agent — self-scan TechDebtLedger against its own codebase."""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

REPO_ROOT = Path(__file__).parent.parent


def self_scan() -> None:
    """Scan this repo and save the debt report."""
    from techdebt.core.config import DebtConfig
    from techdebt.core.engine import scan_repo, build_roadmap

    config = DebtConfig()
    scan_id, items, summary = scan_repo(REPO_ROOT, "TechDebtLedger", config)

    roadmap = build_roadmap(items, max_items=10)

    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "date": date.today().isoformat(),
        "scan_id": scan_id,
        "debt_score": summary.debt_score,
        "total_items": summary.total_items,
        "critical": summary.critical_items,
        "high": summary.high_items,
        "medium": summary.medium_items,
        "low": summary.low_items,
        "estimated_hours": summary.estimated_remediation_hours,
        "top_roadmap_items": [r.model_dump() for r in roadmap[:5]],
    }

    out = REPO_ROOT / "docs" / "self-debt-report.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"[agent] Self-scan complete — debt score: {summary.debt_score}/100 -> {out}")


def refresh_changelog() -> None:
    changelog = REPO_ROOT / "CHANGELOG.md"
    if not changelog.exists():
        return
    today = date.today().isoformat()
    content = changelog.read_text()
    if today not in content:
        content = content.replace("## [Unreleased]", f"## [Unreleased]\n\n_Last checked: {today}_", 1)
        changelog.write_text(content)
    print("[agent] Refreshed CHANGELOG timestamp")


if __name__ == "__main__":
    print(f"[agent] Starting nightly self-scan - {date.today().isoformat()}")
    self_scan()
    refresh_changelog()
    print("[agent] Done.")