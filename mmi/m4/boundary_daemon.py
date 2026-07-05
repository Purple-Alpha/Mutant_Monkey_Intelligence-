"""Boundary daemon skeleton — manifest arm/refuse + heartbeat (§17 Phase 4C).

Go target: ``host_boundary/mmi_boundary_daemon/``. This Python skeleton implements
the same contract for dev/CI when Go is not installed on the build host.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from mmi.m4.authority_seal import (
    AuthorityManifest,
    AuthoritySealError,
    SignedPolicyManifest,
    build_enforcement_manifest,
    daemon_may_arm,
    verify_policy_manifest,
)
from mmi.m4.key_custody import KeyCustodian, create_custodian

DAEMON_SCHEMA_V = "2026-07-04a"
BOUNDARY_DEADMAN_GAP_S = 30


class BoundaryDaemonError(RuntimeError):
    """Daemon refused to arm or health check failed."""


@dataclass
class DaemonHeartbeat:
    schema_v: str
    daemon: str
    armed: bool
    last_heartbeat_utc: str
    manifest_hash: str
    reason: str
    boundary_deadman_gap_s: int = BOUNDARY_DEADMAN_GAP_S

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def load_policy_manifest(path: Path) -> SignedPolicyManifest:
    data = json.loads(path.read_text(encoding="utf-8"))
    return SignedPolicyManifest.from_dict(data)


def load_authority_manifest(path: Path) -> AuthorityManifest:
    from mmi.m4.authority_seal import load_authority_manifest as _load

    return _load(path)


def try_arm_from_files(
    policy_path: Path,
    authority_manifest_path: Path,
    custodian: KeyCustodian,
) -> tuple[bool, str, str]:
    policy = load_policy_manifest(policy_path)
    authority_manifest = load_authority_manifest(authority_manifest_path)
    ok, reason = daemon_may_arm(policy, custodian, authority_manifest)
    return ok, policy.manifest_hash, reason


def try_arm_live(
    policy_path: Path,
    authority_root: Path,
    custodian: KeyCustodian | None = None,
) -> tuple[bool, str, str]:
    custodian = custodian or create_custodian()
    policy = load_policy_manifest(policy_path)
    current = build_enforcement_manifest(authority_root)
    ok, reason = daemon_may_arm(policy, custodian, current)
    return ok, policy.manifest_hash, reason


def write_heartbeat(evidence_dir: Path, armed: bool, manifest_hash: str, reason: str) -> DaemonHeartbeat:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    hb = DaemonHeartbeat(
        schema_v=DAEMON_SCHEMA_V,
        daemon="mmi_boundary_daemon_py_skeleton",
        armed=armed,
        last_heartbeat_utc=datetime.now(timezone.utc).isoformat(),
        manifest_hash=manifest_hash,
        reason=reason,
    )
    path = evidence_dir / "daemon_heartbeat.json"
    path.write_text(json.dumps(hb.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return hb


def append_daemon_event(evidence_dir: Path, event: Mapping[str, object]) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    line = json.dumps(dict(event), sort_keys=True, separators=(",", ":"))
    with (evidence_dir / "daemon.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def run_daemon_selftest(
    evidence_dir: Path,
    policy_path: Path,
    authority_manifest_path: Path,
    *,
    custodian: KeyCustodian | None = None,
) -> dict[str, object]:
    custodian = custodian or create_custodian(evidence_boundary_dir=evidence_dir)
    armed, manifest_hash, reason = try_arm_from_files(
        policy_path, authority_manifest_path, custodian
    )
    hb = write_heartbeat(evidence_dir, armed, manifest_hash, reason)
    append_daemon_event(
        evidence_dir,
        {
            "event": "arm_attempt",
            "armed": armed,
            "reason": reason,
            "manifest_hash": manifest_hash,
            "ts": hb.last_heartbeat_utc,
        },
    )

    bad_refused = False
    policy = load_policy_manifest(policy_path)
    authority_manifest = load_authority_manifest(authority_manifest_path)
    try:
        verify_policy_manifest(policy, custodian, current_manifest=authority_manifest)
        tampered_path = evidence_dir / "tampered_policy.json"
        tampered = json.loads(policy_path.read_text(encoding="utf-8"))
        tampered["manifest_hash"] = "sha256:deadbeef"
        tampered_path.write_text(json.dumps(tampered, indent=2) + "\n", encoding="utf-8")
        bad_ok, _, _ = try_arm_from_files(tampered_path, authority_manifest_path, custodian)
        bad_refused = not bad_ok
    except AuthoritySealError:
        bad_refused = True

    heartbeat_visible = (evidence_dir / "daemon_heartbeat.json").exists()
    log_visible = (evidence_dir / "daemon.jsonl").exists()

    return {
        "schema_v": DAEMON_SCHEMA_V,
        "armed_on_valid_policy": armed,
        "arm_reason": reason,
        "bad_manifest_refused": bad_refused,
        "heartbeat_visible": heartbeat_visible,
        "daemon_log_visible": log_visible,
        "boundary_deadman_gap_s": BOUNDARY_DEADMAN_GAP_S,
    }
