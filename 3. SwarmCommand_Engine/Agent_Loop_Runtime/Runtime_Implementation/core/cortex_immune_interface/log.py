"""Append-only Cortex / Immune Interface boundary log.

Governing contract
------------------
``4. Product_Roadmap/Cortex_Immune_Interface_Design_Contract.md`` — §11
SIGNED 2026-06-14 (Matt Nichol).

Records are boundary facts only. The log authorizes nothing and exposes no
update/delete API.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from core.cortex_immune_interface.state import (
    HandoffPoint,
    HiddenChannelType,
    InterfaceDecision,
    Organ,
)


class InterfaceRecordKind(str, Enum):
    CORTEX_TO_IMMUNE = "cortex_to_immune"
    IMMUNE_TO_CORTEX = "immune_to_cortex"
    BASELINE_UPDATE = "baseline_update"
    SAFE_STOP_STATE = "safe_stop_state"
    HIDDEN_CHANNEL = "hidden_channel"
    SIGNAL_BLOCKED = "signal_blocked"


class InterfaceLogError(Exception):
    """Raised on malformed interface log writes."""


@dataclass(frozen=True)
class InterfaceRecord:
    kind: InterfaceRecordKind
    decision: InterfaceDecision
    detail: str
    source_organ: Organ
    target_organ: Organ
    workflow_id: str
    tenant_id: str = ""
    source: str = ""
    target: str = ""
    handoff_point: HandoffPoint | None = None
    hidden_channel_type: HiddenChannelType | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CortexImmuneInterfaceLog:
    """Append-only interface audit store; no update/delete API."""

    jsonl_path: Path | None = None
    _records: list[InterfaceRecord] = field(default_factory=list)

    def record(
        self,
        *,
        kind: InterfaceRecordKind,
        decision: InterfaceDecision,
        detail: str,
        source_organ: Organ,
        target_organ: Organ,
        workflow_id: str,
        tenant_id: str = "",
        source: str = "",
        target: str = "",
        handoff_point: HandoffPoint | None = None,
        hidden_channel_type: HiddenChannelType | None = None,
    ) -> InterfaceRecord:
        if not isinstance(kind, InterfaceRecordKind):
            raise InterfaceLogError("kind must be an InterfaceRecordKind")
        if not isinstance(decision, InterfaceDecision):
            raise InterfaceLogError("decision must be an InterfaceDecision")
        if not isinstance(source_organ, Organ) or not isinstance(target_organ, Organ):
            raise InterfaceLogError("source_organ and target_organ must be Organ values")
        if handoff_point is not None and not isinstance(handoff_point, HandoffPoint):
            raise InterfaceLogError("handoff_point must be a HandoffPoint")
        if hidden_channel_type is not None and not isinstance(
            hidden_channel_type, HiddenChannelType
        ):
            raise InterfaceLogError("hidden_channel_type must be a HiddenChannelType")

        entry = InterfaceRecord(
            kind=kind,
            decision=decision,
            detail=detail,
            source_organ=source_organ,
            target_organ=target_organ,
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            source=source,
            target=target,
            handoff_point=handoff_point,
            hidden_channel_type=hidden_channel_type,
        )
        if self.jsonl_path is not None:
            self._append_jsonl(entry)
        self._records.append(entry)
        return entry

    def _append_jsonl(self, entry: InterfaceRecord) -> None:
        path = Path(self.jsonl_path)  # type: ignore[arg-type]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "kind": entry.kind.value,
                        "decision": entry.decision.value,
                        "detail": entry.detail,
                        "source_organ": entry.source_organ.value,
                        "target_organ": entry.target_organ.value,
                        "workflow_id": entry.workflow_id,
                        "tenant_id": entry.tenant_id,
                        "source": entry.source,
                        "target": entry.target,
                        "handoff_point": (
                            entry.handoff_point.value if entry.handoff_point else None
                        ),
                        "hidden_channel_type": (
                            entry.hidden_channel_type.value
                            if entry.hidden_channel_type
                            else None
                        ),
                        "timestamp": entry.timestamp.isoformat(),
                    }
                )
                + "\n"
            )

    def entries(self) -> tuple[InterfaceRecord, ...]:
        return tuple(self._records)

    def for_kind(self, kind: InterfaceRecordKind) -> tuple[InterfaceRecord, ...]:
        return tuple(e for e in self._records if e.kind is kind)


__all__ = [
    "InterfaceRecordKind",
    "InterfaceLogError",
    "InterfaceRecord",
    "CortexImmuneInterfaceLog",
]
