"""Reconciliation Verdict surface — Phase 4 (Layer 4).

Governing contract
------------------
``4. Product_Roadmap/Phase4_ReconciliationAgent_Contract.md`` — §11 SIGNED
2026-06-11 (Matt Nichol), commit ``d0cc849``. §13 relationship: "the verdict is
written to ``core/blackboard/`` (new verdict surface to be defined in build)."
This module is that surface.

What this is
------------
The ReconciliationAgent is the swarm's **only** verdict producer (P4-D5). A
verdict is **not** an ``EvidenceType`` — the Phase 1 ``CanonicalEvidenceLedger``
records detection *contributions* (no verdict field, P3-D1) and its
``EvidenceType`` enum is closed. So the verdict gets its own append-only,
tenant-isolated store here in ``core/blackboard/`` rather than corrupting the
signed Phase 1 evidence schema. Same append-only mechanics (P1-D2) and
tenant-isolation discipline (P1-D3/P4-D8) as the evidence ledger.

The ``Verdict`` enum is **closed** (§5). Schema validation rejects any value
outside the five members; ``StrictModel`` forbids extra fields. There is no
update or delete API — append-only holds structurally, not by convention.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field, ValidationError

from .models import StrictModel

VERDICT_LEDGER_SCHEMA_VERSION = "v1"


class Verdict(str, Enum):
    """Closed verdict enum (Phase 4 contract §5).

    No verdict value exists outside this set; schema validation rejects any
    other value at write time.
    """

    HIGH_RISK = "HIGH_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    LOW_RISK = "LOW_RISK"
    DELIVERY_PROBLEM = "DELIVERY_PROBLEM"
    ESCALATE = "ESCALATE"


class EnsembleOutcome(str, Enum):
    """How the three-voter ensemble resolved (§4)."""

    UNANIMOUS = "unanimous"
    MAJORITY = "majority"
    ESCALATE = "escalate"


class VerdictLedgerError(Exception):
    """Base error for verdict ledger operations."""


class VerdictLedgerSchemaError(VerdictLedgerError):
    """Raised when a verdict write is rejected by schema validation."""


class ReconciliationVerdict(StrictModel):
    """One ReconciliationAgent verdict (Phase 4 contract §7 schema).

    ``StrictModel`` forbids extra fields and the ``Verdict`` enum is closed, so
    a malformed verdict (unknown field, bad verdict value, out-of-range
    confidence, empty tenant) fails validation rather than landing on the
    ledger. The per-voter votes and confidences are persisted so the minority
    opinion is never discarded (§4). ``plain_english_chain`` is the
    operator-readable narrative required by §7 — not a raw signal dump.
    """

    verdict_id: UUID = Field(default_factory=uuid4)
    schema_version: str = VERDICT_LEDGER_SCHEMA_VERSION

    email_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    verdict: Verdict
    ensemble_outcome: EnsembleOutcome
    overall_confidence: float = Field(ge=0.0, le=1.0)

    r1_vote: Verdict
    r1_confidence: float = Field(ge=0.0, le=1.0)
    r2_vote: Verdict
    r2_confidence: float = Field(ge=0.0, le=1.0)
    r3_vote: Verdict
    r3_confidence: float = Field(ge=0.0, le=1.0)

    minority_opinion: str = ""
    contributing_evidence: list[str] = Field(default_factory=list)
    plain_english_chain: str = Field(min_length=1)
    cirt_individual: str = ""
    lockdown_applied: bool = False
    delivery_problem_path: bool = False
    zero_day_referred: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VerdictLedger:
    """Named, schema-enforced, tenant-isolated, append-only verdict store.

    Mirrors ``CanonicalEvidenceLedger``: backed by a JSONL file, exposes only
    ``append`` and ``read_for_tenant`` (no update/delete, P1-D2), and reads are
    filtered by ``tenant_id`` and never span tenants (P4-D8). The verdict is the
    sole verdict surface in the system (P4-D5).
    """

    def __init__(self, ledger_path: Path) -> None:
        self.ledger_path = Path(ledger_path)

    def append(
        self, verdict: ReconciliationVerdict | dict[str, Any]
    ) -> ReconciliationVerdict:
        """Validate and append one verdict. Append-only; never overwrites."""

        if isinstance(verdict, ReconciliationVerdict):
            validated = verdict
        else:
            try:
                validated = ReconciliationVerdict.model_validate(verdict)
            except ValidationError as exc:
                raise VerdictLedgerSchemaError(
                    "verdict write rejected: schema validation failed"
                ) from exc

        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(validated.model_dump_json() + "\n")
        return validated

    def read_for_tenant(self, tenant_id: str) -> list[ReconciliationVerdict]:
        """Return every verdict for ``tenant_id`` only (P4-D8 tenant isolation)."""

        if not tenant_id:
            raise VerdictLedgerError("tenant_id is required to read the verdict ledger")
        if not self.ledger_path.exists():
            return []

        verdicts: list[ReconciliationVerdict] = []
        with self.ledger_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = ReconciliationVerdict.model_validate_json(line)
                if record.tenant_id == tenant_id:
                    verdicts.append(record)
        return verdicts
