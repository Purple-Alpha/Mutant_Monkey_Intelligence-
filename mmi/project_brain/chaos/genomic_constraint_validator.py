"""Validate genomic_constraint_v1 artifacts (AGI §5 step 5 prereq — H8)."""

from __future__ import annotations

import json
from typing import Any

from mmi_canonical_digest import canonical_object_digest

ARTIFACT_VERSION = "genomic_constraint_v1"
MAX_CONSTRAINT_BYTES = 65536
ALLOWED_CONSTRAINT_TYPES = frozenset(
    {"rate_limit", "action_deny", "schema_tighten", "route_isolate", "param_clamp"}
)
REGISTERED_CAPABILITIES = frozenset(
    {
        "agent.route.external",
        "agent.exec.shell",
        "agent.file.write",
        "agent.prompt.inject",
        "mesh.ipc.send",
    }
)
EXECUTABLE_FIELD_DENYLIST = frozenset(
    {"code", "eval", "exec", "script", "shell", "python", "bash", "powershell", "javascript"}
)


def compute_constraint_id(artifact: dict[str, Any]) -> str:
    body = {k: v for k, v in artifact.items() if k != "constraint_id"}
    digest = canonical_object_digest(body)
    return f"grc-{digest[:16]}"


def validate_genomic_constraint(artifact: dict[str, Any]) -> tuple[str, list[str]]:
    reasons: list[str] = []

    if artifact.get("artifact_version") != ARTIFACT_VERSION:
        reasons.append("ARTIFACT_VERSION_MISMATCH")

    if artifact.get("constraint_completeness") != "complete_single_bundle":
        reasons.append("INCOMPLETE_BUNDLE")

    ctype = artifact.get("constraint_type")
    if ctype not in ALLOWED_CONSTRAINT_TYPES:
        reasons.append("ARTIFACT_SCHEMA_FAIL")

    body = artifact.get("constraint_body")
    if not isinstance(body, dict):
        reasons.append("ARTIFACT_SCHEMA_FAIL")
        return "REJECTED", reasons

    target = body.get("target")
    if not isinstance(target, str) or target not in REGISTERED_CAPABILITIES:
        reasons.append("CAPABILITY_UNREGISTERED")

    for key in body:
        if key.lower() in EXECUTABLE_FIELD_DENYLIST:
            reasons.append("EXECUTABLE_FIELD_DENIED")

    params = body.get("params")
    if params is not None:
        if not isinstance(params, dict):
            reasons.append("ARTIFACT_SCHEMA_FAIL")
        else:
            for k, v in params.items():
                if k.lower() in EXECUTABLE_FIELD_DENYLIST:
                    reasons.append("EXECUTABLE_FIELD_DENIED")
                if isinstance(v, float):
                    reasons.append("FLOAT_NOT_ALLOWED")

    try:
        serialized = json.dumps(artifact, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError):
        reasons.append("ARTIFACT_SCHEMA_FAIL")
        serialized = ""
    if len(serialized.encode("utf-8")) > MAX_CONSTRAINT_BYTES:
        reasons.append("ARTIFACT_TOO_LARGE")

    expected_id = compute_constraint_id(artifact)
    if artifact.get("constraint_id") != expected_id:
        reasons.append("CONSTRAINT_ID_MISMATCH")

    return ("VALID" if not reasons else "REJECTED", reasons)
