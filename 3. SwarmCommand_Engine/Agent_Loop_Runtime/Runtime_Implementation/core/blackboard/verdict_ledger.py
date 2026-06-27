"""Reconciliation Verdict surface — Phase 4 (Layer 4) with Mode A writer allowlist."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field, ValidationError

from .mode_a_gate import (
    RECONCILIATION_WRITER_AGENT_ID,
    ModeAGateError,
    assert_verdict_writer_allowed,
    load_authority_shadow_tokens,
    load_verdict_narrative_shadow_tokens,
    validate_verdict_semantics,
)
from .models import StrictModel

VERDICT_LEDGER_SCHEMA_VERSION = "v1"


class Verdict(str, Enum):
    HIGH_RISK = "HIGH_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    LOW_RISK = "LOW_RISK"
    DELIVERY_PROBLEM = "DELIVERY_PROBLEM"
    ESCALATE = "ESCALATE"


class EnsembleOutcome(str, Enum):
    UNANIMOUS = "unanimous"
    MAJORITY = "majority"
    ESCALATE = "escalate"


class VerdictLedgerError(Exception):
    """Base error for verdict ledger operations."""


class VerdictLedgerSchemaError(VerdictLedgerError):
    """Raised when a verdict write is rejected by schema validation."""


class ReconciliationVerdict(StrictModel):
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
    """Append-only verdict store; only ``reconciliation_agent_001`` may write (BM-D4)."""

    def __init__(self, ledger_path: Path, shadow_token_config: Path | None = None) -> None:
        self.ledger_path = Path(ledger_path)
        self._shadow_tokens = load_verdict_narrative_shadow_tokens(shadow_token_config)

    def append(
        self,
        verdict: ReconciliationVerdict | dict[str, Any],
        *,
        writer_agent_id: str,
    ) -> ReconciliationVerdict:
        try:
            assert_verdict_writer_allowed(writer_agent_id)
        except ModeAGateError as exc:
            raise VerdictLedgerSchemaError(str(exc)) from exc

        if isinstance(verdict, ReconciliationVerdict):
            validated = verdict
        else:
            try:
                validated = ReconciliationVerdict.model_validate(verdict)
            except ValidationError as exc:
                raise VerdictLedgerSchemaError(
                    "verdict write rejected: schema validation failed"
                ) from exc

        try:
            validate_verdict_semantics(validated, shadow_tokens=self._shadow_tokens)
        except ModeAGateError as exc:
            raise VerdictLedgerSchemaError(str(exc)) from exc

        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(validated.model_dump_json() + "\n")
        return validated

    def read_for_tenant(self, tenant_id: str) -> list[ReconciliationVerdict]:
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


__all__ = [
    "RECONCILIATION_WRITER_AGENT_ID",
    "EnsembleOutcome",
    "ReconciliationVerdict",
    "Verdict",
    "VerdictLedger",
    "VerdictLedgerError",
    "VerdictLedgerSchemaError",
]
