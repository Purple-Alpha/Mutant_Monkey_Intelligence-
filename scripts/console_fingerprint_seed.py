#!/usr/bin/env python3
"""Seed GENESIS fingerprint ledger entry for console evidence gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

DEFAULT_AUTHORITY = Path("/mnt/c/Architectapp_clean")


def _ensure_imports(authority: Path) -> None:
    chaos = authority / "mmi/project_brain/chaos"
    scripts = authority / "scripts"
    for p in (chaos, scripts):
        if p.exists() and str(p) not in sys.path:
            sys.path.insert(0, str(p))


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed GENESIS fingerprint ledger entry")
    parser.add_argument("--authority", type=Path, default=DEFAULT_AUTHORITY)
    parser.add_argument(
        "--fingerprint-digest",
        help="64-hex digest; default = sha256 of phase1 stability summary or authority fingerprint",
    )
    parser.add_argument("--written-at-ms", type=int, default=None)
    args = parser.parse_args()

    if not args.authority.exists():
        print(json.dumps({"error": f"authority not found: {args.authority}"}), file=sys.stderr)
        return 2

    _ensure_imports(args.authority)
    from console_fingerprint_ledger import (  # type: ignore
        GENESIS_RUN_ID,
        GENESIS_SOURCE,
        append_known_good,
        ledger_contains,
    )

    digest = args.fingerprint_digest
    if not digest:
        from chaos_lab_provisioner import authority_fingerprint  # type: ignore
        from weapon_battlefield_scoring import fingerprint_digest  # type: ignore

        digest = fingerprint_digest(authority_fingerprint(args.authority))

    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        print(json.dumps({"error": "fingerprint-digest must be 64 lowercase hex chars"}), file=sys.stderr)
        return 2

    if ledger_contains(digest):
        print(json.dumps({"verdict": "ALREADY_SEEDED", "fingerprint_digest": digest}))
        return 0

    import time

    written_at_ms = args.written_at_ms if args.written_at_ms is not None else int(time.time() * 1000)
    entry = append_known_good(GENESIS_RUN_ID, digest, GENESIS_SOURCE, written_at_ms)
    print(json.dumps({"verdict": "SEEDED", "entry": entry}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
