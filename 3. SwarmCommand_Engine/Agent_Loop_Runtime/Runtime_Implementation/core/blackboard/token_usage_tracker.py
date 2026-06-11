"""Token Usage Tracker — Phase 1 Infrastructure, Component 3.

Governing contract
------------------
``4. Product_Roadmap/Phase1_Infrastructure_Agent_Design_Contract.md`` —
§11 SIGNED 2026-06-09 (Matt Nichol), commit ``fe355da`` — §3 Component 3.
Locked decisions:

- **P1-D5** Records: tenant_id, agent_id, model_id, token_count, timestamp,
  action_type (+ session_id per §3 schema). Read-only reporting surface only.
  No agent may read another tenant's token data.
- **P1-D6** This is a ledger, not a decision surface. It informs the Playhouse
  cost-attribution dashboard. It does NOT gate, block, or modify any agent's
  operation — so this class deliberately exposes no allow/block/gate method.
- **P1-D8** Observe/record only — no detection, scoring, or AgentContribution.

Net-new component (scoreboard row #71). Append-only and tenant-isolated with the
same discipline as the Canonical Evidence Ledger (Component 1). Lives inside the
existing ``core/blackboard/`` namespace (P1-D1); no new namespace created.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field, ValidationError

from .models import StrictModel


TOKEN_USAGE_TRACKER_CONTRACT: dict[str, Any] = {
    "contract_path": (
        "4. Product_Roadmap/Phase1_Infrastructure_Agent_Design_Contract.md"
    ),
    "component": "§3 Component 3 — Token Usage Tracker",
    "status": "§11 SIGNED 2026-06-09 (Matt Nichol)",
    "authorizing_commit": "fe355da",
    "scoreboard_row": "#71",
    "locked_decisions": ("P1-D5", "P1-D6", "P1-D8"),
    "invariants": (
        "append-only; no modification after write",
        "tenant isolation identical to the evidence ledger",
        "reporting only — never gates, blocks, or modifies any agent operation",
        "aggregate queries available to the Playhouse cost-attribution dashboard, "
        "per tenant",
    ),
}

TOKEN_USAGE_SCHEMA_VERSION = "v1"


class TokenActionType(str, Enum):
    """Closed action-type enum (§3 Component 3 record schema)."""

    DETECTION = "detection"
    VERIFICATION = "verification"
    RECONCILIATION = "reconciliation"
    MUTATION = "mutation"
    AUDIT = "audit"


class TokenUsageError(Exception):
    """Base error for token usage tracker operations."""


class TokenUsageSchemaError(TokenUsageError):
    """Raised when a usage record is rejected because it fails validation."""


class TokenUsageRecord(StrictModel):
    """One append-only token-usage record (§3 Component 3 schema).

    Carries the signed fields plus an immutable ``record_id`` identity anchor.
    ``StrictModel`` forbids extra fields and validates types/ranges, so a
    malformed write fails rather than landing on the ledger.
    """

    record_id: UUID = Field(default_factory=uuid4)
    schema_version: str = TOKEN_USAGE_SCHEMA_VERSION
    tenant_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    token_count: int = Field(ge=0)
    action_type: TokenActionType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: str = Field(min_length=1)


class TenantTokenUsageSummary(StrictModel):
    """Read-only per-tenant aggregate for the Playhouse cost-attribution dashboard.

    Batch aggregate over the ledger (P1-D6 reporting surface). Totals are broken
    out by agent, by model, and by action type so the dashboard can attribute
    cost without re-reading raw rows.
    """

    tenant_id: str
    record_count: int
    total_tokens: int
    tokens_by_agent: dict[str, int]
    tokens_by_model: dict[str, int]
    tokens_by_action_type: dict[str, int]


class TokenUsageTracker:
    """Append-only, tenant-isolated, reporting-only token-usage ledger.

    Exposes ``record`` (write), ``read_for_tenant`` and ``aggregate_for_tenant``
    (tenant-scoped reads). There is intentionally no update/delete method
    (append-only, P1-D5) and no allow/block/gate method (reporting only, P1-D6).
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

    def record(self, entry: TokenUsageRecord | dict[str, Any]) -> TokenUsageRecord:
        """Validate and append one usage record. Append-only; never overwrites."""

        if isinstance(entry, TokenUsageRecord):
            validated = entry
        else:
            try:
                validated = TokenUsageRecord.model_validate(entry)
            except ValidationError as exc:
                self._log_rejected_write(entry, str(exc))
                raise TokenUsageSchemaError(
                    "token usage write rejected: schema validation failed"
                ) from exc

        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(validated.model_dump_json() + "\n")
        return validated

    def read_for_tenant(self, tenant_id: str) -> list[TokenUsageRecord]:
        """Return every record for ``tenant_id`` only (P1-D5 tenant isolation).

        A tenant with no records returns an empty list, not an error. There is
        no cross-tenant read path.
        """

        if not tenant_id:
            raise TokenUsageError("tenant_id is required to read token usage")
        if not self.ledger_path.exists():
            return []

        records: list[TokenUsageRecord] = []
        with self.ledger_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = TokenUsageRecord.model_validate_json(line)
                if record.tenant_id == tenant_id:
                    records.append(record)
        return records

    def aggregate_for_tenant(self, tenant_id: str) -> TenantTokenUsageSummary:
        """Batch per-tenant aggregate for the Playhouse cost dashboard (read-only)."""

        records = self.read_for_tenant(tenant_id)
        by_agent: Counter[str] = Counter()
        by_model: Counter[str] = Counter()
        by_action: Counter[str] = Counter()
        total = 0
        for record in records:
            total += record.token_count
            by_agent[record.agent_id] += record.token_count
            by_model[record.model_id] += record.token_count
            by_action[record.action_type.value] += record.token_count
        return TenantTokenUsageSummary(
            tenant_id=tenant_id,
            record_count=len(records),
            total_tokens=total,
            tokens_by_agent=dict(by_agent),
            tokens_by_model=dict(by_model),
            tokens_by_action_type=dict(by_action),
        )

    def _log_rejected_write(self, attempted: Any, reason: str) -> None:
        """Append a rejection record to the governance audit trail (append-only)."""

        self.governance_audit_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            attempted_repr: Any = json.loads(json.dumps(attempted, default=str))
        except (TypeError, ValueError):
            attempted_repr = repr(attempted)
        record = {
            "event": "token_usage_write_rejected",
            "rejected_at": datetime.now(timezone.utc).isoformat(),
            "ledger_path": str(self.ledger_path),
            "reason": reason,
            "attempted": attempted_repr,
        }
        with self.governance_audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
