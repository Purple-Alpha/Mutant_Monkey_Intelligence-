"""Hash-chained fingerprint ledger for console evidence gate (V15)."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

LEDGER_VERSION = "fingerprint_ledger_v1"
DEFAULT_LEDGER_PATH = Path("/tmp/mmi_console_server/state/fingerprint_ledger.jsonl")
GENESIS_RUN_ID = "GENESIS"
GENESIS_SOURCE = "genesis_seed"
ALLOWED_ROOT = Path("/tmp/mmi_console_server/state")
ALLOWED_TMP_PREFIX = Path("/tmp")


class FingerprintLedgerError(Exception):
    pass


def _assert_ledger_path(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ALLOWED_TMP_PREFIX.resolve())
    except ValueError as exc:
        raise FingerprintLedgerError(
            f"ledger path must be under /tmp: {resolved.as_posix()}"
        ) from exc
    return resolved


def _genesis_prev_hash() -> str:
    return "0" * 64


def _line_hash(line_bytes: bytes) -> str:
    return hashlib.sha256(line_bytes).hexdigest()


def _read_lines(path: Path) -> list[bytes]:
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return []
    return [part.encode("utf-8") for part in raw.splitlines() if part.strip()]


def ledger_tail(path: Path = DEFAULT_LEDGER_PATH) -> dict[str, Any] | None:
    path = _assert_ledger_path(path)
    lines = _read_lines(path)
    if not lines:
        return None
    return json.loads(lines[-1].decode("utf-8"))


def ledger_contains(digest: str, path: Path = DEFAULT_LEDGER_PATH) -> bool:
    path = _assert_ledger_path(path)
    if not path.exists():
        return False
    for line in _read_lines(path):
        entry = json.loads(line.decode("utf-8"))
        if entry.get("fingerprint_digest") == digest:
            return True
    return False


def append_known_good(
    run_id: str,
    fingerprint_digest: str,
    source: str,
    written_at_ms: int,
    *,
    path: Path = DEFAULT_LEDGER_PATH,
) -> dict[str, Any]:
    path = _assert_ledger_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = _read_lines(path)
    prev_line_hash = _line_hash(lines[-1]) if lines else _genesis_prev_hash()

    entry: dict[str, Any] = {
        "ledger_version": LEDGER_VERSION,
        "run_id": run_id,
        "fingerprint_digest": fingerprint_digest,
        "source": source,
        "written_at_ms": written_at_ms,
        "prev_entry_hash": prev_line_hash,
    }
    line_bytes = (json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")

    fd, tmp_name = tempfile.mkstemp(prefix=".fingerprint_ledger.", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            for existing in lines:
                handle.write(existing + b"\n")
            handle.write(line_bytes)
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

    return entry


def verify_chain(path: Path = DEFAULT_LEDGER_PATH) -> bool:
    path = _assert_ledger_path(path)
    lines = _read_lines(path)
    prev = _genesis_prev_hash()
    for line in lines:
        entry = json.loads(line.decode("utf-8"))
        if entry.get("prev_entry_hash") != prev:
            return False
        prev = _line_hash(line)
    return True
