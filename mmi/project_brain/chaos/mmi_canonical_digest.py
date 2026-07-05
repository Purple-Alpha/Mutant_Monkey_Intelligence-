"""Canonical JSON digest helper for console / Gate B bindings."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json_bytes(obj: dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_object_digest(obj: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def file_sha256_hex(path) -> str:
    import hashlib
    from pathlib import Path

    data = Path(path).read_bytes()
    return hashlib.sha256(data).hexdigest()


def patch_context_tree_digest(root) -> str:
    """Deterministic sha256 over sorted relative path + file digest entries."""
    from pathlib import Path

    base = Path(root).resolve()
    if not base.exists():
        return hashlib.sha256(b"").hexdigest()
    lines: list[str] = []
    for item in sorted(base.rglob("*")):
        if item.is_file():
            rel = item.relative_to(base).as_posix()
            lines.append(f"{rel}:{file_sha256_hex(item)}")
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
