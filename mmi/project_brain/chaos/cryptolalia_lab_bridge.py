"""
Cryptolalia lab bridge — wire iceberg gate mirror diverts to mirror cells.

Chaos-lab only. Never touches authority repo paths.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mirror_dimension_router import MirrorDimensionRouter


def serialize_divert_payload(
    *,
    sender_id: str,
    error: str,
    detail: Any,
    payload: Any,
    layer_result: dict[str, Any],
) -> str:
    """Evidence blob for mirror cell raw_payload.txt."""
    return json.dumps(
        {
            "sender_id": sender_id,
            "mirror_error": error,
            "mirror_detail": detail,
            "payload": payload,
            "layer_result": layer_result,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def route_gate_divert_to_mirror(
    router: MirrorDimensionRouter,
    sender_id: str,
    *,
    error: str,
    detail: Any,
    payload: Any,
    layer_result: dict[str, Any],
) -> dict[str, Any]:
    """Emit cryptolalia for an iceberg MirrorDimensionDivert verdict."""
    raw = serialize_divert_payload(
        sender_id=sender_id,
        error=error,
        detail=detail,
        payload=payload,
        layer_result=layer_result,
    )
    return router.route_iceberg_divert(
        sender_id,
        raw,
        layer_error=error,
        layer_detail=detail,
        layer_result=layer_result,
    )


def mirror_router_for_lab(mirror_root: Path, canary_key: str | None = None) -> MirrorDimensionRouter:
    mirror_root.mkdir(parents=True, exist_ok=True)
    key = canary_key or "CANARY-MMI-CHAOS-LAB-NOT-REAL"
    return MirrorDimensionRouter(mirror_root, canary_key=key)


__all__ = [
    "mirror_router_for_lab",
    "route_gate_divert_to_mirror",
    "serialize_divert_payload",
]
