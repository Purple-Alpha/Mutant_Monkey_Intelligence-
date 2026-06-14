"""SafeStopLog — append-only, immutable safe-stop record store.

Governing contract
------------------
``4. Product_Roadmap/Safe_Stop_State_Machine_Design_Contract.md`` — §11 SIGNED
2026-06-14 (Matt Nichol) — § Entry Protocol + § Testable Invariants.

The **entry record is the proof of entry** (§ Entry Protocol): "If no entry log
exists, safe-stop did not fire correctly." The log therefore lives in its own
storage with no update or delete API — immutability holds structurally, the same
discipline as the Watcher ``ObservationLog`` and the Phase 5 ``MutationAuditTrail``.

Records are facts only: what happened, when, under which condition. The log makes
no decisions and authorizes nothing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from core.safe_stop.state import EntryCondition


class SafeStopRecordKind(str, Enum):
    """Closed set of safe-stop record kinds. No kind outside this set."""

    ENTRY = "entry"
    ACTION_BLOCKED = "action_blocked"
    SAFETY_PROOF = "safety_proof"
    OPERATOR_AUTHORIZATION = "operator_authorization"
    RECOVERY_BROADCAST = "recovery_broadcast"
    RECONCILIATION_ABORTED = "reconciliation_aborted"


class SafeStopLogError(Exception):
    """Raised on a malformed safe-stop log write (fail-safe)."""


@dataclass(frozen=True)
class SafeStopRecord:
    """One append-only, immutable safe-stop record (§ Entry Protocol).

    An ENTRY record carries every field the entry protocol requires: condition
    name, timestamp, epoch at entry (never incremented), detecting component, and
    all active tenant IDs at the moment of entry. Other kinds reuse the same
    immutable shape; condition/epoch are populated where meaningful.
    """

    kind: SafeStopRecordKind
    detail: str
    condition: EntryCondition | None = None
    epoch: int | None = None
    detecting_component: str = ""
    active_tenant_ids: tuple[str, ...] = ()
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SafeStopLog:
    """Append-only, immutable safe-stop store — its own storage, no update/delete.

    Optionally mirrors to a JSONL file for durability, but the in-process list is
    itself append-only.
    """

    jsonl_path: Path | None = None
    _records: list[SafeStopRecord] = field(default_factory=list)

    def record(
        self,
        *,
        kind: SafeStopRecordKind,
        detail: str,
        condition: EntryCondition | None = None,
        epoch: int | None = None,
        detecting_component: str = "",
        active_tenant_ids: tuple[str, ...] = (),
    ) -> SafeStopRecord:
        if not isinstance(kind, SafeStopRecordKind):
            raise SafeStopLogError("kind must be a closed-enum SafeStopRecordKind")
        if condition is not None and not isinstance(condition, EntryCondition):
            raise SafeStopLogError("condition must be a closed-enum EntryCondition")

        entry = SafeStopRecord(
            kind=kind,
            detail=detail,
            condition=condition,
            epoch=epoch,
            detecting_component=detecting_component,
            active_tenant_ids=tuple(active_tenant_ids),
        )
        self._records.append(entry)
        if self.jsonl_path is not None:
            self._append_jsonl(entry)
        return entry

    def _append_jsonl(self, entry: SafeStopRecord) -> None:
        path = Path(self.jsonl_path)  # type: ignore[arg-type]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "kind": entry.kind.value,
                        "detail": entry.detail,
                        "condition": (
                            entry.condition.value if entry.condition else None
                        ),
                        "epoch": entry.epoch,
                        "detecting_component": entry.detecting_component,
                        "active_tenant_ids": list(entry.active_tenant_ids),
                        "timestamp": entry.timestamp.isoformat(),
                    }
                )
                + "\n"
            )

    def entries(self) -> tuple[SafeStopRecord, ...]:
        return tuple(self._records)

    def for_kind(self, kind: SafeStopRecordKind) -> tuple[SafeStopRecord, ...]:
        return tuple(e for e in self._records if e.kind is kind)

    def entry_records(self) -> tuple[SafeStopRecord, ...]:
        """ENTRY records only — the proof-of-entry view (§ Entry Protocol)."""

        return self.for_kind(SafeStopRecordKind.ENTRY)


__all__ = [
    "SafeStopRecordKind",
    "SafeStopLogError",
    "SafeStopRecord",
    "SafeStopLog",
]
