"""CollectiveImmuneSystemLog — append-only coordination history.

Governing contract
------------------
``4. Product_Roadmap/Collective_Immune_System_Design_Contract.md`` — §11
SIGNED 2026-06-14 (Matt Nichol) — Cross-Component Evidence Handoff Rules and
CIS-INV-6 / CIS-INV-10 / CIS-INV-11.

Every handoff and level transition is logged before the coordination action is
returned to the caller. If this log cannot write, the coordinator fails closed
and the handoff is aborted.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from core.collective_immune_system.state import CISComponent, EscalationLevel


class CISRecordKind(str, Enum):
    """Closed set of CIS coordination record kinds."""

    LEVEL_TRANSITION = "level_transition"
    HANDOFF = "handoff"
    HANDOFF_BLOCKED = "handoff_blocked"
    ACTION_BLOCKED = "action_blocked"
    COMPONENT_NOTIFICATION = "component_notification"
    MUTATION_SUSPENDED = "mutation_suspended"
    SAFE_STOP_HANDOFF = "safe_stop_handoff"


class CISLogError(Exception):
    """Raised when a CIS log write cannot be completed."""


@dataclass(frozen=True)
class CISRecord:
    """One immutable CIS coordination record."""

    kind: CISRecordKind
    detail: str
    level: EscalationLevel
    workflow_id: str
    source: CISComponent | None = None
    target: CISComponent | None = None
    tenant_scope: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CollectiveImmuneSystemLog:
    """Append-only, immutable CIS coordination store — no update/delete API."""

    jsonl_path: Path | None = None
    failing: bool = False
    _records: list[CISRecord] = field(default_factory=list)

    def record(
        self,
        *,
        kind: CISRecordKind,
        detail: str,
        level: EscalationLevel,
        workflow_id: str,
        source: CISComponent | None = None,
        target: CISComponent | None = None,
        tenant_scope: tuple[str, ...] = (),
        evidence_refs: tuple[str, ...] = (),
    ) -> CISRecord:
        if self.failing:
            raise CISLogError(
                f"CIS log write failed for workflow {workflow_id!r}; fail closed"
            )
        if not isinstance(kind, CISRecordKind):
            raise CISLogError("kind must be a closed-enum CISRecordKind")
        if not isinstance(level, EscalationLevel):
            raise CISLogError("level must be a closed-enum EscalationLevel")
        if source is not None and not isinstance(source, CISComponent):
            raise CISLogError("source must be a closed-enum CISComponent")
        if target is not None and not isinstance(target, CISComponent):
            raise CISLogError("target must be a closed-enum CISComponent")

        entry = CISRecord(
            kind=kind,
            detail=detail,
            level=level,
            workflow_id=workflow_id,
            source=source,
            target=target,
            tenant_scope=tuple(tenant_scope),
            evidence_refs=tuple(evidence_refs),
        )
        if self.jsonl_path is not None:
            self._append_jsonl(entry)
        self._records.append(entry)
        return entry

    def _append_jsonl(self, entry: CISRecord) -> None:
        path = Path(self.jsonl_path)  # type: ignore[arg-type]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "kind": entry.kind.value,
                        "detail": entry.detail,
                        "level": entry.level.value,
                        "workflow_id": entry.workflow_id,
                        "source": entry.source.value if entry.source else None,
                        "target": entry.target.value if entry.target else None,
                        "tenant_scope": list(entry.tenant_scope),
                        "evidence_refs": list(entry.evidence_refs),
                        "timestamp": entry.timestamp.isoformat(),
                    }
                )
                + "\n"
            )

    def entries(self) -> tuple[CISRecord, ...]:
        return tuple(self._records)

    def for_kind(self, kind: CISRecordKind) -> tuple[CISRecord, ...]:
        return tuple(e for e in self._records if e.kind is kind)


__all__ = [
    "CISRecordKind",
    "CISLogError",
    "CISRecord",
    "CollectiveImmuneSystemLog",
]
