from __future__ import annotations

from pathlib import Path


def test_vendor_baseline_sqlite_connections_stay_inside_isolation_manager():
    runtime_root = Path(__file__).resolve().parents[1]
    offenders: list[str] = []
    allowed_paths = {
        "core/production_state/vendor_baseline/isolation.py",
        "tests/test_vendor_baseline_store.py",
        "tests/test_vendor_baseline_isolation_boundary.py",
    }
    ignored_dirs = {".git", ".pytest_cache", "__pycache__"}
    for path in runtime_root.rglob("*.py"):
        if any(part in ignored_dirs for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        if "sqlite3.connect" not in text:
            continue
        normalized = path.relative_to(runtime_root).as_posix()
        if normalized not in allowed_paths:
            offenders.append(normalized)

    assert offenders == []

