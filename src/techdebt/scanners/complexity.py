"""Cyclomatic complexity scanner."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from techdebt.models.debt import ComplexityHotspot, DebtItem


def scan_complexity(repo_path: Path, threshold: int = 10, max_files: int = 200) -> list[ComplexityHotspot]:
    """Scan Python files for cyclomatic complexity hotspots."""
    hotspots = []
    py_files = [f for f in repo_path.rglob("*.py")
                if ".venv" not in f.parts and ".git" not in f.parts][:max_files]

    for file_path in py_files:
        try:
            source = file_path.read_text(errors="ignore")
            tree = ast.parse(source)
            functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

            if not functions:
                continue

            scores = []
            long_fns = []
            for fn in functions:
                score = _cyclomatic_complexity(fn)
                scores.append(score)
                if score >= threshold:
                    long_fns.append(f"{fn.name} (complexity={score})")

            avg_score = sum(scores) / len(scores)
            max_score = max(scores)

            if max_score >= threshold:
                hotspots.append(ComplexityHotspot(
                    file_path=str(file_path.relative_to(repo_path)),
                    complexity_score=max_score,
                    function_count=len(functions),
                    avg_function_length=round(avg_score, 1),
                    long_functions=long_fns[:5],
                ))
        except Exception:
            pass

    return sorted(hotspots, key=lambda h: h.complexity_score, reverse=True)


def complexity_to_debt_items(hotspots: list[ComplexityHotspot]) -> list[DebtItem]:
    """Convert complexity hotspots to debt items."""
    items = []
    for i, h in enumerate(hotspots):
        severity = "critical" if h.complexity_score >= 20 else "high" if h.complexity_score >= 15 else "medium"
        items.append(DebtItem(
            id=f"complexity-{i}",
            category="complexity",
            file_path=h.file_path,
            line_number=0,
            description=f"High complexity (score={h.complexity_score}): {', '.join(h.long_functions[:2])}",
            severity=severity,
            estimated_hours=round(h.complexity_score * 0.5, 1),
        ))
    return items


def _cyclomatic_complexity(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Estimate cyclomatic complexity of a function."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                               ast.With, ast.Assert, ast.comprehension)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity