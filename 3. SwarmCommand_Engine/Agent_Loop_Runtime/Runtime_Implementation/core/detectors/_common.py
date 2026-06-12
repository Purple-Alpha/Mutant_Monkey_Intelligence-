"""Shared detection-swarm primitives — Phase 3 (Layer 1).

Governing contract: ``Phase3_Detection_Swarm_Agent_Design_Contract.md`` (§11
SIGNED 2026-06-10, ``c522292``) + Amendment 1 (§11 SIGNED 2026-06-11, ``56e8b33``).

This module holds the inbound-email input model every detector reads from and the
single helper that writes a structured evidence contribution to the Phase 1
``CanonicalEvidenceLedger``. Centralizing the write keeps P3-D1 (structured
contribution only, no verdict field), P3-D2 (evidence-type closure), and P3-D5
(``tenant_id`` on every write) enforced in one place rather than re-implemented
six times. It lives inside the contract's ``core/detectors/`` namespace (P3-D9);
no new ``core/`` namespace is created (Amendment §E).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from core.blackboard import (
    CanonicalEvidenceLedger,
    EvidenceLedgerEntry,
    EvidenceStage,
    EvidenceType,
)


class DetectionError(Exception):
    """Raised on a detector boundary violation or malformed input (fails safe)."""


class AttachmentInput(BaseModel):
    """One inbound attachment descriptor (cloud-side metadata only, P3-D4).

    The sandbox never receives raw client bytes here — it receives the
    already-extracted metadata (filename, hash, extension) produced cloud-side.
    """

    model_config = ConfigDict(extra="forbid")

    filename: str = ""
    sha256: str = ""
    extension: str = ""


class EmailContext(BaseModel):
    """Normalized inbound-email view a detector inspects (cloud-side, P3-D4).

    ``extra="forbid"`` so a smuggled/unknown field fails at construction — the
    "malformed input returns a safe error not a crash" adversarial requirement
    (§5 Class 2) is satisfied at the model boundary. Every field except the two
    identity anchors has a safe default so a partial email is analyzable, not a
    crash.
    """

    model_config = ConfigDict(extra="forbid")

    email_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)

    from_domain: str | None = None
    sending_ip: str | None = None
    ip_country: str | None = None
    account_home_country: str | None = None

    subject: str = ""
    body: str = ""
    urls: tuple[str, ...] = ()
    attachments: tuple[AttachmentInput, ...] = ()
    image_count: int = Field(default=0, ge=0)


def require_email(email: object) -> EmailContext:
    """Return ``email`` if it is an ``EmailContext``, else raise ``DetectionError``.

    Detectors call this first so a wrong-typed input is a safe, named error at the
    boundary (§5 Class 2) rather than an ``AttributeError`` deeper in the agent.
    """

    if not isinstance(email, EmailContext):
        raise DetectionError(
            "detector input must be an EmailContext; got " f"{type(email).__name__}"
        )
    return email


def write_contribution(
    ledger: CanonicalEvidenceLedger,
    *,
    agent_id: str,
    tenant_id: str,
    email_id: str,
    evidence_type: EvidenceType,
    details: dict,
    confidence: float,
    stage: EvidenceStage = EvidenceStage.ES2,
) -> EvidenceLedgerEntry:
    """Build and append one evidence contribution (tenant-isolated, append-only).

    The ``evidence_type`` is supplied by the calling agent as a fixed class
    constant — there is no path for a detector to write outside its assigned type
    (P3-D2). No ``verdict`` field exists on ``EvidenceLedgerEntry`` (P3-D1); a
    detector that tried to smuggle one would fail ``StrictModel`` validation.
    ``tenant_id`` is mandatory (P3-D5). Stage defaults to ES2 (P3-D8: adversarial
    synthetic build target).
    """

    entry = EvidenceLedgerEntry(
        agent_id=agent_id,
        tenant_id=tenant_id,
        email_id=email_id,
        evidence_type=evidence_type,
        details=details,
        confidence=confidence,
        stage=stage,
    )
    return ledger.append(entry)
