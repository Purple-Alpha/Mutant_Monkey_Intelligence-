"""Phase 1 + Mode A gate — Canonical Evidence Ledger hardening."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field, ValidationError

from .mode_a_gate import (
    ModeAGateError,
    load_authority_shadow_tokens,
    validate_evidence_entry_semantics,
    validate_raw_evidence_dict,
)
from .models import StrictModel


CANONICAL_EVIDENCE_LEDGER_CONTRACT: dict[str, Any] = {
    "contract_path": (
        "4. Product_Roadmap/Phase1_Infrastructure_Agent_Design_Contract.md"
    ),
    "mode_a_contract_path": (
        "4. Product_Roadmap/Blackboard_Mesh_Governance_Foundation_Contract_Deep_Dive.md"
    ),
    "component": "§3 Component 1 — Canonical Evidence Ledger",
    "status": "§11 SIGNED 2026-06-09 (Matt Nichol); Mode A gate MMI-DEC-272",
    "authorizing_commit": "fe355da",
    "locked_decisions": ("P1-D1", "P1-D2", "P1-D3", "P1-D8", "BM-D1", "BM-D2", "BM-D3", "BM-D8"),
    "invariants": (
        "entries are immutable after write",
        "no delete operation exists",
        "tenant_id is mandatory on every write",
        "reads are filtered by tenant_id at query time and never span tenants",
        "schema validation fires before every write; malformed entries are "
        "rejected and logged to the governance audit trail",
        "Mode A structural + semantic gate fires before every write",
        "observe/record only — no detection, scoring, or AgentContribution",
    ),
}

EVIDENCE_LEDGER_SCHEMA_VERSION = "v1"


class EvidenceType(str, Enum):
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
    ES1 = "ES1"
    ES2 = "ES2"
    ES3 = "ES3"


class LedgerError(Exception):
    """Base error for canonical evidence ledger operations."""


class LedgerSchemaError(LedgerError):
    """Raised when a write is rejected because it fails schema validation."""


class EvidenceLedgerEntry(StrictModel):
    """Phase 1 §3 Component 1 write schema (exactly eight top-level fields)."""

    agent_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    email_id: str = Field(min_length=1)
    evidence_type: EvidenceType
    details: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    stage: EvidenceStage = EvidenceStage.ES1


class CanonicalEvidenceLedger:
    """Append-only evidence store with Mode A fail-closed gate at ``append``."""

    def __init__(
        self,
        ledger_path: Path,
        governance_audit_path: Path | None = None,
        shadow_token_config: Path | None = None,
    ) -> None:
        self.ledger_path = Path(ledger_path)
        self.governance_audit_path = (
            Path(governance_audit_path)
            if governance_audit_path is not None
            else self.ledger_path.with_suffix(self.ledger_path.suffix + ".rejected.jsonl")
        )
        self._shadow_tokens = load_authority_shadow_tokens(shadow_token_config)

    def append(self, entry: EvidenceLedgerEntry | dict[str, Any]) -> EvidenceLedgerEntry:
        attempted: Any = entry
        try:
            if isinstance(entry, dict):
                validate_raw_evidence_dict(entry, shadow_tokens=self._shadow_tokens)
                validated = EvidenceLedgerEntry.model_validate(entry)
            else:
                validate_evidence_entry_semantics(entry, shadow_tokens=self._shadow_tokens)
                validated = entry
        except ModeAGateError as exc:
            self._log_rejected_write(attempted, str(exc))
            raise LedgerSchemaError(str(exc)) from exc
        except ValidationError as exc:
            self._log_rejected_write(attempted, str(exc))
            raise LedgerSchemaError(
                "evidence ledger write rejected: schema validation failed"
            ) from exc

        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(validated.model_dump_json() + "\n")
        return validated

    def read_for_tenant(self, tenant_id: str) -> list[EvidenceLedgerEntry]:
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
        return len(self.read_for_tenant(tenant_id))

    def _log_rejected_write(self, attempted: Any, reason: str) -> None:
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
