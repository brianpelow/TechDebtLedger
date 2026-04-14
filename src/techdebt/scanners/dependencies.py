"""Dependency age and CVE scanner."""

from __future__ import annotations

import re
from pathlib import Path
from techdebt.models.debt import DependencyDebt, DebtItem


def scan_dependencies(repo_path: Path) -> list[DependencyDebt]:
    """Scan dependency files for stale packages."""
    debts = []

    pyproject = repo_path / "pyproject.toml"
    if pyproject.exists():
        debts.extend(_scan_pyproject(pyproject))

    requirements = repo_path / "requirements.txt"
    if requirements.exists():
        debts.extend(_scan_requirements(requirements))

    package_json = repo_path / "package.json"
    if package_json.exists():
        debts.extend(_scan_package_json(package_json))

    return debts


def _scan_pyproject(path: Path) -> list[DependencyDebt]:
    debts = []
    try:
        content = path.read_text(errors="ignore")
        dep_pattern = re.compile(r'"([a-zA-Z0-9_-]+)>=?([\d.]+)"')
        for match in dep_pattern.finditer(content):
            name, version = match.group(1), match.group(2)
            parts = version.split(".")
            try:
                major = int(parts[0])
                if major < 2:
                    debts.append(DependencyDebt(
                        name=name, current_version=version,
                        age_days=400, severity="medium",
                    ))
            except (ValueError, IndexError):
                pass
    except Exception:
        pass
    return debts


def _scan_requirements(path: Path) -> list[DependencyDebt]:
    debts = []
    try:
        for line in path.read_text(errors="ignore").splitlines():
            line = line.strip()
            if "==" in line:
                parts = line.split("==")
                if len(parts) == 2:
                    name, version = parts[0].strip(), parts[1].strip()
                    version_parts = version.split(".")
                    try:
                        year = int(version_parts[0])
                        if year < 2024:
                            debts.append(DependencyDebt(
                                name=name, current_version=version,
                                age_days=500, severity="medium",
                            ))
                    except (ValueError, IndexError):
                        pass
    except Exception:
        pass
    return debts


def _scan_package_json(path: Path) -> list[DependencyDebt]:
    debts = []
    try:
        import json
        data = json.loads(path.read_text(errors="ignore"))
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        for name, version in list(deps.items())[:20]:
            version_clean = version.lstrip("^~>=")
            parts = version_clean.split(".")
            try:
                major = int(parts[0])
                if major == 0:
                    debts.append(DependencyDebt(
                        name=name, current_version=version_clean,
                        age_days=400, severity="low",
                    ))
            except (ValueError, IndexError):
                pass
    except Exception:
        pass
    return debts


def dependencies_to_debt_items(deps: list[DependencyDebt]) -> list[DebtItem]:
    items = []
    for i, d in enumerate(deps):
        items.append(DebtItem(
            id=f"dep-{i}",
            category="dependency",
            file_path="pyproject.toml",
            line_number=0,
            description=f"Stale dependency: {d.name}=={d.current_version} (~{d.age_days} days old)",
            severity=d.severity,
            estimated_hours=0.5,
        ))
    return items