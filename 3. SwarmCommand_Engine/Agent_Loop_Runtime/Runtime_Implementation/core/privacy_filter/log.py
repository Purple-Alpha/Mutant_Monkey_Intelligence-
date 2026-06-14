"""PrivacyFilterAuditLog — append-only, immutable filter-operation audit (stage 5).

Governing contract
------------------
``4. Product_Roadmap/Privacy_Filter_Contract.md`` — §15 SIGNED 2026-06-14
(Matt Nichol) — §3.5 + PF-D7 + PF-D9.

The audit record is **pipeline stage 5, not an afterthought** (PF-D7): an
operation that cannot be audited does not complete. Every operation — permitted
or blocked — is recorded with the same rigor (PF-D9). The trail is the evidence
that the no-raw-identifier invariant held on every operation (§3.5). No update,
no delete — immutability holds structurally, as with the control-plane and
safe-stop logs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from core.privacy_filter.state import BlockReason, BroadcastDecision, EntityKind


class AuditWriteError(Exception):
    """Raised when an audit record cannot be written — pipeline fails closed."""


@dataclass(frozen=True)
class PrivacyAuditRecord:
    """One immutable filter-operation record (§3.5 required fields)."""

    workflow_id: str
    input_ref: str  # hash of the input item, not the item itself (§3.5)
    tenant_id: str
    entry_timestamp: datetime
    exit_timestamp: datetime
    entity_findings: tuple[EntityKind, ...]
    policy_applied: str
    transformation_applied: tuple[str, ...]
    validation_passed: bool
    decision: BroadcastDecision
    block_reason: BlockReason | None = None


@dataclass
class PrivacyFilterAuditLog:
    """Append-only, immutable audit store — no update/delete API (§3.5).

    Optionally mirrors to a JSONL file (correlated by ``workflow_id``); the
    in-process list is itself append-only. A ``failing`` flag exists only so
    tests can simulate an audit-write failure (PF-D7: no broadcast without an
    audit record).
    """

    jsonl_path: Path | None = None
    failing: bool = False
    _records: list[PrivacyAuditRecord] = field(default_factory=list)

    def record(self, entry: PrivacyAuditRecord) -> PrivacyAuditRecord:
        if self.failing:
            raise AuditWriteError(
                f"audit write failed for workflow {entry.workflow_id!r}; fail closed"
            )
        self._records.append(entry)
        if self.jsonl_path is not None:
            self._append_jsonl(entry)
        return entry

    def _append_jsonl(self, entry: PrivacyAuditRecord) -> None:
        path = Path(self.jsonl_path)  # type: ignore[arg-type]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "workflow_id": entry.workflow_id,
                        "input_ref": entry.input_ref,
                        "tenant_id": entry.tenant_id,
                        "entry_timestamp": entry.entry_timestamp.isoformat(),
                        "exit_timestamp": entry.exit_timestamp.isoformat(),
                        "entity_findings": [e.value for e in entry.entity_findings],
                        "policy_applied": entry.policy_applied,
                        "transformation_applied": list(entry.transformation_applied),
                        "validation_passed": entry.validation_passed,
                        "decision": entry.decision.value,
                        "block_reason": (
                            entry.block_reason.value if entry.block_reason else None
                        ),
                    }
                )
                + "\n"
            )

    def entries(self) -> tuple[PrivacyAuditRecord, ...]:
        return tuple(self._records)

    def for_workflow(self, workflow_id: str) -> tuple[PrivacyAuditRecord, ...]:
        return tuple(e for e in self._records if e.workflow_id == workflow_id)

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)


__all__ = ["AuditWriteError", "PrivacyAuditRecord", "PrivacyFilterAuditLog"]
