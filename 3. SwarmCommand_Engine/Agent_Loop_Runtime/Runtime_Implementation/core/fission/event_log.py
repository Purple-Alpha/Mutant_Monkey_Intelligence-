"""FissionEventLog — shared append-only fission history.

Governing contracts
-------------------
``4. Product_Roadmap/Load_Fission_Contract_v2.md`` — §13 SIGNED 2026-06-13
(Matt Nichol) — LF2-D7; v1 history under ``Load_Fission_Contract.md``.

``4. Product_Roadmap/Specialisation_Fission_Contract.md`` — §11 SIGNED
2026-06-12 (Matt Nichol) — SF-D8.

This is the shared event log that the advisory ordering note requires to land
under the lower-risk Load Fission build first. It is append-only and has no
update/delete API. Load Fission writes spawn / exhale / rejection records now;
Specialisation Fission will reuse the same schema later for sign-off decisions
and net-new-type records.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class FissionTrigger(str, Enum):
    LOAD = "load"
    SPECIALISATION = "specialisation"


class FissionEventType(str, Enum):
    SPAWN = "spawn"
    EXHALE = "exhale"
    REJECTED = "rejected"
    PROPOSED_EVIDENCE = "proposed_evidence"
    SIGN_OFF = "sign_off"


@dataclass(frozen=True)
class FissionEvent:
    """One immutable fission event."""

    event_type: FissionEventType
    trigger_type: FissionTrigger
    triggering_watcher: str
    threat_level: str
    parent_id: str
    parent_type: str
    child_ids: tuple[str, ...] = ()
    schema_id: str = ""
    namespace: str = ""
    detail: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FissionEventLog:
    """Append-only fission log. No update/delete API by design."""

    _events: list[FissionEvent] = field(default_factory=list)

    def append(self, event: FissionEvent) -> FissionEvent:
        self._events.append(event)
        return event

    def record(
        self,
        *,
        event_type: FissionEventType,
        trigger_type: FissionTrigger,
        triggering_watcher: str,
        threat_level: str,
        parent_id: str,
        parent_type: str,
        child_ids: tuple[str, ...] = (),
        schema_id: str = "",
        namespace: str = "",
        detail: str = "",
    ) -> FissionEvent:
        return self.append(
            FissionEvent(
                event_type=event_type,
                trigger_type=trigger_type,
                triggering_watcher=triggering_watcher,
                threat_level=threat_level,
                parent_id=parent_id,
                parent_type=parent_type,
                child_ids=child_ids,
                schema_id=schema_id,
                namespace=namespace,
                detail=detail,
            )
        )

    def entries(self) -> tuple[FissionEvent, ...]:
        return tuple(self._events)

    def for_type(self, event_type: FissionEventType) -> tuple[FissionEvent, ...]:
        return tuple(e for e in self._events if e.event_type is event_type)


__all__ = [
    "FissionTrigger",
    "FissionEventType",
    "FissionEvent",
    "FissionEventLog",
]
