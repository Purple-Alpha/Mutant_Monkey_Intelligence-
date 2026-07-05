"""Deterministic v1 synthesis stub — harvest + breach descriptor → genomic_constraint_v1."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from genomic_constraint_validator import compute_constraint_id
from mmi_canonical_digest import canonical_object_digest

DESCRIPTOR_VERSION = "breach_descriptor_v1"

EXPLOIT_TO_CONSTRAINT_TYPE: dict[str, str] = {
    "purple_exfil_proc_environ": "action_deny",
    "purple_control_m2_regression": "route_isolate",
    "mesh-smash": "schema_tighten",
    "default": "action_deny",
}

EXPLOIT_TO_TARGET: dict[str, str] = {
    "purple_exfil_proc_environ": "agent.exec.shell",
    "purple_control_m2_regression": "agent.route.external",
    "mesh-smash": "agent.prompt.inject",
    "default": "agent.route.external",
}


def validate_breach_descriptor(descriptor: dict[str, Any]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if descriptor.get("descriptor_version") != DESCRIPTOR_VERSION:
        reasons.append("DESCRIPTOR_VERSION_MISMATCH")
    for field in ("incident_id", "critic_node", "exploit_id", "mirror_agent_id", "payload"):
        if not descriptor.get(field):
            reasons.append(f"MISSING_{field.upper()}")
    return ("VALID" if not reasons else "REJECTED", reasons)


def harvest_digest(harvest: dict[str, Any]) -> str:
    return canonical_object_digest(harvest)


def synthesize_constraint_v1(
    harvest: dict[str, Any],
    breach_descriptor: dict[str, Any],
    *,
    episode_id: str,
    synth_attempt: int = 1,
    mirror_containment_root: str = "/tmp/mmi_mirror_dimension/",
) -> dict[str, Any]:
    verdict, reasons = validate_breach_descriptor(breach_descriptor)
    if verdict != "VALID":
        raise ValueError(f"invalid breach descriptor: {reasons}")

    exploit_id = str(breach_descriptor["exploit_id"])
    constraint_type = EXPLOIT_TO_CONSTRAINT_TYPE.get(
        exploit_id, EXPLOIT_TO_CONSTRAINT_TYPE["default"]
    )
    target = EXPLOIT_TO_TARGET.get(exploit_id, EXPLOIT_TO_TARGET["default"])

    artifact: dict[str, Any] = {
        "artifact_version": "genomic_constraint_v1",
        "episode_id": episode_id,
        "incident_id": breach_descriptor["incident_id"],
        "created_at_ms": int(harvest.get("harvested_at_ms") or 1_782_200_000_000),
        "breach_ref": {
            "critic_node": breach_descriptor["critic_node"],
            "exploit_id": exploit_id,
            "mirror_agent_id": breach_descriptor["mirror_agent_id"],
            "mirror_containment_root": mirror_containment_root,
        },
        "constraint_type": constraint_type,
        "constraint_completeness": "complete_single_bundle",
        "constraint_body": {
            "target": target,
            "rule": "deny" if constraint_type == "action_deny" else "isolate",
            "params": {"exploit_id_hash": hashlib.sha256(exploit_id.encode()).hexdigest()[:16]},
        },
        "provenance": {
            "harvest_digest": harvest_digest(harvest),
            "synth_attempt": synth_attempt,
        },
    }
    artifact["constraint_id"] = compute_constraint_id(artifact)
    return artifact


def write_constraint_artifact(artifact: dict[str, Any], patch_context_dir) -> None:
    from pathlib import Path

    root = Path(patch_context_dir)
    root.mkdir(parents=True, exist_ok=True)
    (root / "genomic_constraint.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    proof_context = {
        "fix_id": artifact["incident_id"],
        "patch_content": f"--- genomic constraint {artifact['constraint_id']}\n+++ bound\n",
        "constraint_id": artifact["constraint_id"],
        "episode_id": artifact["episode_id"],
    }
    (root / "proof_context.json").write_text(json.dumps(proof_context, indent=2), encoding="utf-8")
