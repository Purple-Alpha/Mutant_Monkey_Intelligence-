"""Canonical Evidence Ledger — Phase 1 Infrastructure, Component 1.

Governing contract
------------------
``4. Product_Roadmap/Phase1_Infrastructure_Agent_Design_Contract.md`` —
§11 SIGNED 2026-06-09 (Matt Nichol), commit ``fe355da`` — §3 Component 1.
Locked decisions enforced here:

- **P1-D1** Canonical evidence ledger path is ``core/blackboard/``. This module
  lives inside that namespace; no parallel namespace is created for this
  surface.
- **P1-D2** Every entry is append-only. No agent may modify or delete a prior
  entry. The ledger is a fact accumulator, not a mutable state store — so this
  class deliberately exposes **no** update/delete API.
- **P1-D3** Tenant isolation is enforced at the ledger level, not assumed.
  ``tenant_id`` is mandatory on every write; reads are filtered by ``tenant_id``
  at query time and never span tenants.
- **P1-D8** No detection surface. This component observes and records; it does
  not detect, score, flag, or produce ``AgentContribution`` objects of its own.

Relationship to existing surfaces
----------------------------------
This formalises ``core/blackboard/`` as the single append-only evidence store
all agents write contributions to. It does **not** replace the legacy
``BlackboardRecord`` envelope or ``storage.py`` JSONL adapter that the 13
currently governed agents already use; it is the named, schema-enforced,
tenant-isolated facade the Phase 1 contract governs, layered on the same
append-only JSONL mechanics. New evidence types require a signed amendment to
the contract before use (see ``EvidenceType``).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field, ValidationError

from .models import StrictModel


# Governing-contract metadata. Read-only provenance so any consumer (or audit)
# can resolve which signed decision authorizes this surface without leaving the
# code. Not behaviour — documentation that travels with the module.
CANONICAL_EVIDENCE_LEDGER_CONTRACT: dict[str, Any] = {
    "contract_path": (
        "4. Product_Roadmap/Phase1_Infrastructure_Agent_Design_Contract.md"
    ),
    "component": "§3 Component 1 — Canonical Evidence Ledger",
    "status": "§11 SIGNED 2026-06-09 (Matt Nichol)",
    "authorizing_commit": "fe355da",
    "locked_decisions": ("P1-D1", "P1-D2", "P1-D3", "P1-D8"),
    "invariants": (
        "entries are immutable after write",
        "no delete operation exists",
        "tenant_id is mandatory on every write",
        "reads are filtered by tenant_id at query time and never span tenants",
        "schema validation fires before every write; malformed entries are "
        "rejected and logged to the governance audit trail",
        "observe/record only — no detection, scoring, or AgentContribution",
    ),
}

# Schema version for the on-disk evidence entry. A future v2 is a deliberate,
# audit-visible upgrade via a signed contract amendment, never a silent change.
EVIDENCE_LEDGER_SCHEMA_VERSION = "v1"


class EvidenceType(str, Enum):
    """Closed enum of evidence types (signed contract §3 Component 1).

    New evidence types require a signed amendment to the Phase 1 Infrastructure
    contract before use. The strict ``extra``/enum validation rejects any value
    outside this set at write time.
    """

    HEADER_SIGNAL = "header_signal"
    AUTHENTICATION_SIGNAL = "authentication_signal"
    THREAD_SIGNAL = "thread_signal"
    GEO_SIGNAL = "geo_signal"
    CONTENT_SIGNAL = "content_signal"
    URL_SIGNAL = "url_signal"
    ATTACHMENT_SIGNAL = "attachment_signal"
    IMAGE_SIGNAL = "image_signal"
    SENDER_SIGNAL = "sender_signal"
    KNOWLEDGE_SIGNAL = "knowledge_signal"


class EvidenceStage(str, Enum):
    """Evidence Stage maturity marker (ES1 Synthetic / ES2 Supervised / ES3 Production)."""

    ES1 = "ES1"
    ES2 = "ES2"
    ES3 = "ES3"


class LedgerError(Exception):
    """Base error for canonical evidence ledger operations."""


class LedgerSchemaError(LedgerError):
    """Raised when a write is rejected because it fails schema validation."""


class EvidenceLedgerEntry(StrictModel):
    """One append-only evidence contribution (signed contract §3 Component 1 schema).

    Fields are exactly the signed write schema (``agent_id``, ``tenant_id``,
    ``email_id``, ``evidence_type``, ``details``, ``confidence``, ``timestamp``,
    ``stage``) plus an immutable ``entry_id`` identity anchor — the same role
    ``record_id`` plays on ``BlackboardRecord``. ``StrictModel`` forbids extra
    fields, so a malformed write (unknown field, bad enum, out-of-range
    confidence, empty ``tenant_id``) fails validation rather than landing on the
    ledger.
    """

    entry_id: UUID = Field(default_factory=uuid4)
    schema_version: str = EVIDENCE_LEDGER_SCHEMA_VERSION
    agent_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    email_id: str = Field(min_length=1)
    evidence_type: EvidenceType
    details: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    stage: EvidenceStage = EvidenceStage.ES1


class CanonicalEvidenceLedger:
    """Named, schema-enforced, tenant-isolated, append-only evidence store.

    Backed by a JSONL file (same append-only mechanics as ``storage.py``).
    Exposes only ``append`` and ``read_for_tenant`` — there is intentionally no
    update or delete method, so P1-D2 (append-only) holds structurally, not by
    convention.

    A ``governance_audit_path`` (defaults to ``<ledger>.rejected.jsonl`` beside
    the ledger) receives an append-only record of every rejected write, per the
    §3 invariant "malformed entries are rejected and logged to the governance
    audit trail".
    """

    def __init__(
        self,
        ledger_path: Path,
        governance_audit_path: Path | None = None,
    ) -> None:
        self.ledger_path = Path(ledger_path)
        self.governance_audit_path = (
            Path(governance_audit_path)
            if governance_audit_path is not None
            else self.ledger_path.with_suffix(self.ledger_path.suffix + ".rejected.jsonl")
        )

    def append(self, entry: EvidenceLedgerEntry | dict[str, Any]) -> EvidenceLedgerEntry:
        """Validate and append one evidence entry. Append-only; never overwrites.

        Accepts a validated ``EvidenceLedgerEntry`` or a raw ``dict``. A raw dict
        is validated first; on failure the attempted write is logged to the
        governance audit trail and ``LedgerSchemaError`` is raised — the bad
        entry never reaches the ledger.
        """

        if isinstance(entry, EvidenceLedgerEntry):
            validated = entry
        else:
            try:
                validated = EvidenceLedgerEntry.model_validate(entry)
            except ValidationError as exc:
                self._log_rejected_write(entry, str(exc))
                raise LedgerSchemaError(
                    "evidence ledger write rejected: schema validation failed"
                ) from exc

        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(validated.model_dump_json() + "\n")
        return validated

    def read_for_tenant(self, tenant_id: str) -> list[EvidenceLedgerEntry]:
        """Return every entry for ``tenant_id`` only (P1-D3 tenant isolation).

        Reading a tenant that has written nothing returns an empty list, not an
        error. There is no cross-tenant read path on this class.
        """

        if not tenant_id:
            raise LedgerError("tenant_id is required to read the evidence ledger")
        if not self.ledger_path.exists():
            return []

        entries: list[EvidenceLedgerEntry] = []
        with self.ledger_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = EvidenceLedgerEntry.model_validate_json(line)
                if record.tenant_id == tenant_id:
                    entries.append(record)
        return entries

    def count_for_tenant(self, tenant_id: str) -> int:
        """Count entries visible to ``tenant_id`` (tenant-isolated, read-only)."""

        return len(self.read_for_tenant(tenant_id))

    def _log_rejected_write(self, attempted: Any, reason: str) -> None:
        """Append a rejection record to the governance audit trail (append-only)."""

        self.governance_audit_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            attempted_repr: Any = json.loads(json.dumps(attempted, default=str))
        except (TypeError, ValueError):
            attempted_repr = repr(attempted)
        record = {
            "event": "evidence_ledger_write_rejected",
            "rejected_at": datetime.now(timezone.utc).isoformat(),
            "ledger_path": str(self.ledger_path),
            "reason": reason,
            "attempted": attempted_repr,
        }
        with self.governance_audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
