"""MutationAuditTrail — Phase 5 (Layer 5), append-only mutation history.

Governing contract
------------------
``4. Product_Roadmap/Phase5_MutationEngine_Contract.md`` — §11 SIGNED 2026-06-12
(Matt Nichol) — P5-D6 (append-only audit trail) + §3 / §6.

Every proposed and deployed mutation is recorded here with timestamp, the
pipeline stage reached, the evidence chain, the signer (when sign-off happened),
and the outcome. Same append-only discipline as the Phase 1
``CanonicalEvidenceLedger`` (P1-D2): there is no update or delete API, so the
history holds structurally, not by convention.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field, ValidationError

from core.blackboard.models import StrictModel

MUTATION_AUDIT_SCHEMA_VERSION = "v1"


class MutationStage(str, Enum):
    """Ordered stages of the named Anomaly Detection Pipeline (contract §3.3.1).

    The first five are the gating stages a candidate walks in order; the last
    three are terminal outcomes recorded once a candidate reaches them.
    """

    # Gating stages (ordered)
    ANOMALY_FLAGGED = "anomaly_flagged"          # stage 1 — flagged, not acted on
    BASELINE_COMPARED = "baseline_compared"      # stage 2 — outlier vs variation
    THREE_SHOT_CONFIRMED = "three_shot_confirmed"  # stage 3 — distinct email+tenant
    VALIDATION_PASSED = "validation_passed"      # stage 4 — benign-stream FP check
    SIGNED_OFF = "signed_off"                    # stage 5 — operator signature
    # Terminal outcomes
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"
    REJECTED = "rejected"


class MutationAuditError(Exception):
    """Base error for mutation audit trail operations."""


class MutationAuditSchemaError(MutationAuditError):
    """Raised when an audit write is rejected by schema validation."""


class MutationAuditEntry(StrictModel):
    """One append-only mutation-history record (contract P5-D6)."""

    entry_id: UUID = Field(default_factory=uuid4)
    schema_version: str = MUTATION_AUDIT_SCHEMA_VERSION
    candidate_id: str = Field(min_length=1)
    # Scope of the mutation: a single tenant_id, or "sandbox"/"multi" for the
    # cross-tenant confirmation phase. Never empty.
    tenant_scope: str = Field(default="sandbox", min_length=1)
    stage: MutationStage
    detail: str = ""
    evidence_chain: list[str] = Field(default_factory=list)
    signer: str = ""  # populated only at SIGNED_OFF / DEPLOYED
    outcome: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MutationAuditTrail:
    """Append-only, JSONL-backed mutation history. No update/delete API."""

    def __init__(self, trail_path: Path) -> None:
        self.trail_path = Path(trail_path)

    def append(
        self, entry: MutationAuditEntry | dict[str, Any]
    ) -> MutationAuditEntry:
        """Validate and append one audit record. Append-only; never overwrites."""

        if isinstance(entry, MutationAuditEntry):
            validated = entry
        else:
            try:
                validated = MutationAuditEntry.model_validate(entry)
            except ValidationError as exc:
                raise MutationAuditSchemaError(
                    "mutation audit write rejected: schema validation failed"
                ) from exc

        self.trail_path.parent.mkdir(parents=True, exist_ok=True)
        with self.trail_path.open("a", encoding="utf-8") as handle:
            handle.write(validated.model_dump_json() + "\n")
        return validated

    def read_all(self) -> list[MutationAuditEntry]:
        if not self.trail_path.exists():
            return []
        entries: list[MutationAuditEntry] = []
        with self.trail_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    entries.append(MutationAuditEntry.model_validate_json(line))
        return entries

    def read_for_candidate(self, candidate_id: str) -> list[MutationAuditEntry]:
        return [e for e in self.read_all() if e.candidate_id == candidate_id]
