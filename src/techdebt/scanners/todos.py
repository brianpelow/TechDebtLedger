"""TODO/FIXME/HACK annotation scanner."""

from __future__ import annotations

import re
from pathlib import Path
from techdebt.models.debt import TodoItem, DebtItem

TODO_PATTERN = re.compile(
    r'#\s*(TODO|FIXME|HACK|XXX|BUG|DEBT|NOQA)[\s:]*(.+)',
    re.IGNORECASE,
)

SEVERITY_MAP = {
    "FIXME": "high",
    "BUG": "high",
    "DEBT": "high",
    "HACK": "medium",
    "XXX": "medium",
    "TODO": "low",
    "NOQA": "low",
}

EXTENSIONS = {".py", ".ts", ".js", ".go", ".java", ".cs", ".rb"}


def scan_todos(repo_path: Path, max_files: int = 200) -> list[TodoItem]:
    """Scan source files for annotated debt comments."""
    todos = []
    files = [
        f for f in repo_path.rglob("*")
        if f.is_file()
        and f.suffix in EXTENSIONS
        and ".git" not in f.parts
        and ".venv" not in f.parts
        and "node_modules" not in f.parts
    ][:max_files]

    for file_path in files:
        try:
            lines = file_path.read_text(errors="ignore").splitlines()
            for i, line in enumerate(lines, 1):
                match = TODO_PATTERN.search(line)
                if match:
                    todos.append(TodoItem(
                        file_path=str(file_path.relative_to(repo_path)),
                        line_number=i,
                        tag=match.group(1).upper(),
                        message=match.group(2).strip()[:200],
                    ))
        except Exception:
            pass

    return todos


def todos_to_debt_items(todos: list[TodoItem]) -> list[DebtItem]:
    """Convert TODO items to debt items."""
    items = []
    for i, t in enumerate(todos):
        severity = SEVERITY_MAP.get(t.tag, "low")
        items.append(DebtItem(
            id=f"todo-{i}",
            category="annotated_debt",
            file_path=t.file_path,
            line_number=t.line_number,
            description=f"{t.tag}: {t.message}",
            severity=severity,
            estimated_hours=1.0 if severity == "high" else 0.5,
            snippet=f"Line {t.line_number}: {t.tag}: {t.message}",
        ))
    return items