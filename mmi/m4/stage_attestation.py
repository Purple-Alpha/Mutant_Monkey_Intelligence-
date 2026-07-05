"""Stage ladder signed exits — verify_exit, lineage, EXIT_BINDS_H0 (§3.1, §17 Phase 4A)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping

from mmi.m4.key_custody import KeyCustodian

STAGE_ORDER: tuple[str, ...] = ("C-M4", "C2", "C3", "C4", "M4")
GENESIS_PARENT_HASH = "GENESIS"
ARTIFACT_SCHEMA_V = "2026-07-04a"

PROMOTING_STATUSES = frozenset({"HARNESS_READY", "CLEAN", "M4_MET"})
NON_PROMOTING_STATUSES = frozenset({"BLOCKED", "INDETERMINATE", "M4_NOT_MET"})


class StageAttestationError(ValueError):
    """Exit artifact invalid or lineage broken — fail-closed."""


@dataclass(frozen=True)
class StageExitArtifact:
    schema_v: str
    stage_id: str
    run_mode: str
    run_nonce: str
    d_mode_s: int
    chain_tip: str
    signed_h0: str
    parent_exit_hash: str
    status: str
    exit_signature: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> StageExitArtifact:
        return cls(
            schema_v=str(data["schema_v"]),
            stage_id=str(data["stage_id"]),
            run_mode=str(data["run_mode"]),
            run_nonce=str(data["run_nonce"]),
            d_mode_s=int(data["d_mode_s"]),
            chain_tip=str(data["chain_tip"]),
            signed_h0=str(data["signed_h0"]),
            parent_exit_hash=str(data["parent_exit_hash"]),
            status=str(data["status"]),
            exit_signature=str(data["exit_signature"]),
        )


def canonical_payload_bytes(payload: Mapping[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def unsigned_payload(artifact: StageExitArtifact) -> dict[str, object]:
    data = artifact.to_dict()
    data.pop("exit_signature", None)
    return data


def exit_artifact_hash(artifact: StageExitArtifact) -> str:
    return hashlib.sha256(canonical_payload_bytes(unsigned_payload(artifact))).hexdigest()


def sign_bytes(custodian: KeyCustodian, payload: Mapping[str, object]) -> str:
    return custodian.sign(canonical_payload_bytes(payload))


def verify_signature(custodian: KeyCustodian, artifact: StageExitArtifact) -> bool:
    return custodian.verify(canonical_payload_bytes(unsigned_payload(artifact)), artifact.exit_signature)


def emit_none(run_mode: str, status: str) -> None:
    return None


def sign_exit(
    *,
    stage_id: str,
    run_mode: str,
    run_nonce: str,
    d_mode_s: int,
    chain_tip: str,
    authority_h0: str,
    parent_exit_hash: str,
    status: str,
    custodian: KeyCustodian,
) -> StageExitArtifact | None:
    if status in NON_PROMOTING_STATUSES:
        emit_none(run_mode, status)
        return None
    if status not in PROMOTING_STATUSES:
        raise StageAttestationError(f"unknown terminal status for sign_exit: {status}")
    if stage_id != run_mode:
        raise StageAttestationError("stage_id must equal run_mode")
    if stage_id not in STAGE_ORDER:
        raise StageAttestationError(f"unknown stage_id: {stage_id}")

    idx = STAGE_ORDER.index(stage_id)
    if idx == 0:
        if parent_exit_hash != GENESIS_PARENT_HASH:
            raise StageAttestationError("C-M4 exit must have GENESIS parent_exit_hash")
    else:
        if parent_exit_hash == GENESIS_PARENT_HASH:
            raise StageAttestationError(f"{stage_id} exit cannot have GENESIS parent")

    unsigned = {
        "schema_v": ARTIFACT_SCHEMA_V,
        "stage_id": stage_id,
        "run_mode": run_mode,
        "run_nonce": run_nonce,
        "d_mode_s": d_mode_s,
        "chain_tip": chain_tip,
        "signed_h0": authority_h0,
        "parent_exit_hash": parent_exit_hash,
        "status": status,
    }
    signature = sign_bytes(custodian, unsigned)
    return StageExitArtifact(exit_signature=signature, **unsigned)


def save_exit(path: Path, artifact: StageExitArtifact) -> Path:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_exit(path: Path) -> StageExitArtifact:
    data = json.loads(path.read_text(encoding="utf-8"))
    return StageExitArtifact.from_dict(data)


def build_exit_index(directory: Path) -> dict[str, StageExitArtifact]:
    index: dict[str, StageExitArtifact] = {}
    if not directory.exists():
        return index
    for path in sorted(directory.glob("*.json")):
        artifact = load_exit(path)
        index[exit_artifact_hash(artifact)] = artifact
    return index


def lineage_root(
    artifact: StageExitArtifact,
    exit_index: Mapping[str, StageExitArtifact],
) -> str:
    current = artifact
    seen: set[str] = set()
    run_nonce: str | None = None
    while True:
        if run_nonce is None:
            run_nonce = current.run_nonce
        elif current.run_nonce != run_nonce:
            raise StageAttestationError("mixed run_nonce in lineage")
        current_hash = exit_artifact_hash(current)
        if current_hash in seen:
            raise StageAttestationError("lineage cycle detected")
        seen.add(current_hash)
        if current.parent_exit_hash == GENESIS_PARENT_HASH:
            if current.stage_id != STAGE_ORDER[0]:
                raise StageAttestationError("GENESIS parent must terminate at C-M4 root")
            return current.run_nonce
        parent = exit_index.get(current.parent_exit_hash)
        if parent is None:
            raise StageAttestationError(f"missing parent exit for hash {current.parent_exit_hash}")
        parent_idx = STAGE_ORDER.index(parent.stage_id)
        child_idx = STAGE_ORDER.index(current.stage_id)
        if child_idx != parent_idx + 1:
            raise StageAttestationError(
                f"mixed lineage: {parent.stage_id} cannot parent {current.stage_id}"
            )
        current = parent


def verify_exit(
    artifact: StageExitArtifact,
    custodian: KeyCustodian,
    *,
    exit_index: Mapping[str, StageExitArtifact] | None = None,
    current_authority_h0: str | None = None,
) -> None:
    if artifact.schema_v != ARTIFACT_SCHEMA_V:
        raise StageAttestationError(f"unsupported schema_v: {artifact.schema_v}")
    if artifact.stage_id != artifact.run_mode:
        raise StageAttestationError("stage_id/run_mode mismatch")
    if artifact.stage_id not in STAGE_ORDER:
        raise StageAttestationError(f"unknown stage_id: {artifact.stage_id}")
    if artifact.status not in PROMOTING_STATUSES:
        raise StageAttestationError(f"non-promoting status in exit artifact: {artifact.status}")
    if not verify_signature(custodian, artifact):
        raise StageAttestationError("exit_signature invalid (CANARY-023 path)")

    if current_authority_h0 is not None and artifact.signed_h0 != current_authority_h0:
        raise StageAttestationError("signed_h0 does not match current authority baseline (EXIT_BINDS_H0)")

    if exit_index is not None:
        lineage_root(artifact, exit_index)


def verify_exit_for_entry(
    prior_exit: StageExitArtifact,
    expected_prior_stage: str,
    custodian: KeyCustodian,
    current_authority_h0: str,
    exit_index: Mapping[str, StageExitArtifact],
) -> None:
    if prior_exit.stage_id != expected_prior_stage:
        raise StageAttestationError(
            f"prior exit stage mismatch: expected {expected_prior_stage}, got {prior_exit.stage_id}"
        )
    verify_exit(
        prior_exit,
        custodian,
        exit_index=exit_index,
        current_authority_h0=current_authority_h0,
    )
    lineage_root(prior_exit, exit_index)


def run_attestation_selftest(custodian: KeyCustodian) -> dict[str, object]:
    h0_a = "sha256:authority-h0-a"
    h0_b = "sha256:authority-h0-b"
    chain_tip = "sha256:chain-tip-001"
    nonce = "nonce-cm4-001"

    cm4 = sign_exit(
        stage_id="C-M4",
        run_mode="C-M4",
        run_nonce=nonce,
        d_mode_s=900,
        chain_tip=chain_tip,
        authority_h0=h0_a,
        parent_exit_hash=GENESIS_PARENT_HASH,
        status="HARNESS_READY",
        custodian=custodian,
    )
    assert cm4 is not None
    index = {exit_artifact_hash(cm4): cm4}

    verify_exit(cm4, custodian, exit_index=index, current_authority_h0=h0_a)

    cm4_parent_hash = exit_artifact_hash(cm4)
    c2 = sign_exit(
        stage_id="C2",
        run_mode="C2",
        run_nonce=nonce,
        d_mode_s=14400,
        chain_tip="sha256:chain-tip-002",
        authority_h0=h0_a,
        parent_exit_hash=cm4_parent_hash,
        status="CLEAN",
        custodian=custodian,
    )
    assert c2 is not None
    index[exit_artifact_hash(c2)] = c2
    verify_exit_for_entry(c2, "C2", custodian, h0_a, index)

    stale_failed = False
    try:
        verify_exit(cm4, custodian, exit_index=index, current_authority_h0=h0_b)
    except StageAttestationError:
        stale_failed = True

    mixed_failed = False
    other_cm4 = sign_exit(
        stage_id="C-M4",
        run_mode="C-M4",
        run_nonce="nonce-other-lineage",
        d_mode_s=900,
        chain_tip=chain_tip,
        authority_h0=h0_a,
        parent_exit_hash=GENESIS_PARENT_HASH,
        status="HARNESS_READY",
        custodian=custodian,
    )
    assert other_cm4 is not None
    bad_c2 = sign_exit(
        stage_id="C2",
        run_mode="C2",
        run_nonce="nonce-cm4-001",
        d_mode_s=14400,
        chain_tip="sha256:chain-tip-bad",
        authority_h0=h0_a,
        parent_exit_hash=exit_artifact_hash(other_cm4),
        status="CLEAN",
        custodian=custodian,
    )
    assert bad_c2 is not None
    mixed_index = {
        exit_artifact_hash(cm4): cm4,
        exit_artifact_hash(other_cm4): other_cm4,
        exit_artifact_hash(bad_c2): bad_c2,
    }
    try:
        verify_exit_for_entry(bad_c2, "C2", custodian, h0_a, mixed_index)
    except StageAttestationError:
        mixed_failed = True

    forged = StageExitArtifact(
        schema_v=ARTIFACT_SCHEMA_V,
        stage_id="C-M4",
        run_mode="C-M4",
        run_nonce="forged",
        d_mode_s=900,
        chain_tip=chain_tip,
        signed_h0=h0_a,
        parent_exit_hash=GENESIS_PARENT_HASH,
        status="HARNESS_READY",
        exit_signature="00" * 32,
    )
    forgery_failed = False
    try:
        verify_exit(forged, custodian)
    except StageAttestationError:
        forgery_failed = True

    none_result = sign_exit(
        stage_id="C-M4",
        run_mode="C-M4",
        run_nonce=nonce,
        d_mode_s=900,
        chain_tip=chain_tip,
        authority_h0=h0_a,
        parent_exit_hash=GENESIS_PARENT_HASH,
        status="BLOCKED",
        custodian=custodian,
    )

    return {
        "schema_v": ARTIFACT_SCHEMA_V,
        "stage_order": list(STAGE_ORDER),
        "cm4_sign_verify_ok": True,
        "c2_lineage_ok": True,
        "stale_h0_rejected": stale_failed,
        "mixed_lineage_rejected": mixed_failed,
        "forgery_rejected": forgery_failed,
        "non_promoting_emit_none": none_result is None,
        "lineage_root_nonce": lineage_root(c2, index),
    }
