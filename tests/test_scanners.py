"""Tests for debt scanners."""

import tempfile
from pathlib import Path
from techdebt.scanners.complexity import scan_complexity, complexity_to_debt_items
from techdebt.scanners.todos import scan_todos, todos_to_debt_items
from techdebt.scanners.dependencies import scan_dependencies, dependencies_to_debt_items


def test_complexity_scan_empty_dir() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        hotspots = scan_complexity(Path(tmpdir))
        assert hotspots == []


def test_complexity_scan_detects_complex_function() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "complex.py"
        path.write_text("""
def very_complex(x):
    if x > 0:
        if x > 10:
            if x > 100:
                for i in range(x):
                    if i % 2 == 0:
                        while i > 0:
                            if i > 5:
                                i -= 1
                            else:
                                break
    return x
""")
        hotspots = scan_complexity(Path(tmpdir), threshold=5)
        assert len(hotspots) > 0
        assert hotspots[0].complexity_score >= 5


def test_todos_scan_empty_dir() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        todos = scan_todos(Path(tmpdir))
        assert todos == []


def test_todos_scan_detects_annotations() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "service.py"
        path.write_text("""
def process():
    # TODO: refactor this function
    # FIXME: handle edge case for negative values
    # HACK: temporary workaround for issue #123
    pass
""")
        todos = scan_todos(Path(tmpdir))
        assert len(todos) == 3
        tags = {t.tag for t in todos}
        assert "TODO" in tags
        assert "FIXME" in tags
        assert "HACK" in tags


def test_todos_to_debt_items() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "service.py"
        path.write_text("# FIXME: critical bug here\n")
        todos = scan_todos(Path(tmpdir))
        items = todos_to_debt_items(todos)
        assert len(items) > 0
        assert items[0].category == "annotated_debt"
        assert items[0].severity == "high"


def test_dependency_scan_empty_dir() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        deps = scan_dependencies(Path(tmpdir))
        assert deps == []


def test_complexity_to_debt_items() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "complex.py"
        path.write_text("""
def f(x):
    if x: 
        if x > 1:
            if x > 2:
                for i in range(x):
                    if i: pass
    return x
""")
        hotspots = scan_complexity(Path(tmpdir), threshold=3)
        if hotspots:
            items = complexity_to_debt_items(hotspots)
            assert len(items) > 0
            assert items[0].category == "complexity"