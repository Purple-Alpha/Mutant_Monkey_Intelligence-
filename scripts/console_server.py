#!/usr/bin/env python3
"""
MMI Console Server — Ed25519 evidence-signoff gate (AGI §5 step 4).

Verify-only server: binds loopback, never loads private keys.
See: architecture/MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

_WSL_AUTHORITY = Path("/mnt/c/Architectapp_clean")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _resolve_authority(config: Any | None = None) -> Path:
    if config is not None and getattr(config, "authority_root", None) is not None:
        return Path(config.authority_root)
    env_root = os.environ.get("MMI_AUTHORITY_ROOT")
    if env_root:
        return Path(env_root)
    if _WSL_AUTHORITY.exists():
        return _WSL_AUTHORITY
    return _repo_root()


DEFAULT_AUTHORITY = _resolve_authority()


def _ensure_chaos_import(authority: Path) -> None:
    chaos = authority / "mmi/project_brain/chaos"
    if chaos.exists() and str(chaos) not in sys.path:
        sys.path.insert(0, str(chaos))


def create_app(config=None):
    from console_evidence_gate import (  # type: ignore
        CONSOLE_BIND,
        CONSOLE_PORT,
        GateConfig,
        append_audit_line,
        review_bundle,
        sign_bundle,
        validate_bundle,
    )

    cfg = config or GateConfig()
    authority = _resolve_authority(cfg)
    _ensure_chaos_import(authority)

    try:
        from fastapi import Body, FastAPI
        from starlette.responses import JSONResponse
    except ImportError as exc:
        raise SystemExit(f"fastapi required: {exc}") from exc

    app = FastAPI(title="MMI Console Evidence Gate")

    @app.get("/api/v1/health")
    async def health_endpoint():
        return {
            "service": "mmi_console_evidence_gate",
            "bind": CONSOLE_BIND,
            "port": CONSOLE_PORT,
            "endpoints": [
                "GET /api/v1/health",
                "POST /api/v1/evidence-bundle/validate",
                "GET /api/v1/evidence-bundle/{bundle_id}",
                "POST /api/v1/evidence-bundle/sign",
            ],
            "note": "No web UI at /. Use API routes or console_sign_client.py",
        }

    @app.post("/api/v1/evidence-bundle/validate")
    async def validate_endpoint(body: dict[str, Any] = Body(...)):
        client = CONSOLE_BIND
        result = validate_bundle(body, cfg)
        append_audit_line(
            cfg,
            "VALIDATE",
            {
                "bundle_id": result.bundle_id,
                "verdict": result.verdict,
                "reasons": result.reasons,
                "client": client,
                "sign_seq": None,
                "manifest_hash": result.manifest_hash_preview,
            },
        )
        payload = {
            "verdict": result.verdict,
            "reasons": result.reasons,
            "bundle_id": result.bundle_id,
            "manifest_preview": result.manifest_preview,
            "manifest_hash_preview": result.manifest_hash_preview,
        }
        status = 200 if result.verdict == "VALID" else 422
        return JSONResponse(payload, status_code=status)

    @app.get("/api/v1/evidence-bundle/{bundle_id}")
    async def review_endpoint(bundle_id: str):
        data = review_bundle(bundle_id, cfg)
        if data is None:
            return JSONResponse({"error": "not found"}, status_code=404)
        return data

    @app.post("/api/v1/evidence-bundle/sign")
    async def sign_endpoint(body: dict[str, Any] = Body(...)):
        client = CONSOLE_BIND
        verdict, reasons, record = sign_bundle(body, cfg, client=client)
        if verdict != "ACCEPTED":
            append_audit_line(
                cfg,
                "SIGN",
                {
                    "bundle_id": body.get("bundle_id"),
                    "verdict": "REJECTED",
                    "reasons": reasons,
                    "client": client,
                    "sign_seq": body.get("sign_seq"),
                    "manifest_hash": body.get("manifest_hash"),
                },
            )
            return JSONResponse({"verdict": "REJECTED", "reasons": reasons}, status_code=422)
        return JSONResponse({"verdict": "ACCEPTED", "record": record})

    return app


def main() -> int:
    parser = argparse.ArgumentParser(description="MMI Console Evidence Gate")
    parser.add_argument(
        "--host",
        default=None,
        help="ignored except loopback; only 127.0.0.1 permitted (spec CONSOLE_BIND)",
    )
    parser.add_argument("--port", type=int, default=8767)
    parser.add_argument("--authority", type=Path, default=DEFAULT_AUTHORITY)
    args = parser.parse_args()

    if not args.authority.exists():
        print(f"authority not found: {args.authority}", file=sys.stderr)
        return 2

    _ensure_chaos_import(args.authority)
    from console_evidence_gate import CONSOLE_BIND, CONSOLE_PORT, GateConfig  # type: ignore

    if args.host is not None and args.host not in (CONSOLE_BIND, "localhost"):
        print(
            f"refusing bind host {args.host!r}: console server must bind {CONSOLE_BIND} only",
            file=sys.stderr,
        )
        return 2

    host = CONSOLE_BIND
    port = args.port if args.port != 8767 else CONSOLE_PORT

    try:
        import uvicorn
    except ImportError:
        print("uvicorn required", file=sys.stderr)
        return 2

    app = create_app(GateConfig(authority_root=args.authority))
    print(f"[console] http://{host}:{port}/")
    uvicorn.run(app, host=host, port=port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
