"""ModeTransitionLog — append-only, immutable mode-transition history.

Governing contract
------------------
``4. Product_Roadmap/Mode_Controller_Contract.md`` — §14 SIGNED 2026-06-13
(Matt Nichol) — MC-D9 / §7 ("Homeostasis index manipulation" / audit).

Every mode transition is a security-critical event (MC-D9). Each record carries
exactly the fields the contract names: timestamp, previous mode, new mode, epoch
before, epoch after, trigger condition, and which observers agreed. The store
has no update or delete API — immutability holds structurally, the same
discipline as the control-plane ``ControlPlaneAuditTrail`` and the Safe-Stop
``SafeStopLog``. The log makes no decisions and authorizes nothing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from core.mode_controller.state import Mode, ObserverSource


class ModeRecordKind(str, Enum):
    """Closed set of mode-controller record kinds."""

    TRANSITION = "transition"
    LOCAL_FALLBACK = "local_fallback"
    EPOCH_FORGE_REJECTED = "epoch_forge_rejected"
    QUORUM_DENIED = "quorum_denied"
    FLAPPING_DENIED = "flapping_denied"
    RECONCILIATION_TIMEOUT = "reconciliation_timeout"
    HOMEOSTASIS_ALERT = "homeostasis_alert"


class ModeLogError(Exception):
    """Raised on a malformed mode-transition log write (fail-safe)."""


@dataclass(frozen=True)
class ModeTransitionRecord:
    """One append-only, immutable mode record (MC-D9).

    A TRANSITION record carries every field the audit requirement names; other
    kinds reuse the same immutable shape, populating fields where meaningful.
    """

    kind: ModeRecordKind
    detail: str
    previous_mode: Mode | None = None
    new_mode: Mode | None = None
    epoch_before: int | None = None
    epoch_after: int | None = None
    trigger: str = ""
    observers_agreed: tuple[ObserverSource, ...] = ()
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ModeTransitionLog:
    """Append-only, immutable mode-transition store — no update/delete API.

    Optionally mirrors to a JSONL file for durability; the in-process list is
    itself append-only.
    """

    jsonl_path: Path | None = None
    _records: list[ModeTransitionRecord] = field(default_factory=list)

    def record(
        self,
        *,
        kind: ModeRecordKind,
        detail: str,
        previous_mode: Mode | None = None,
        new_mode: Mode | None = None,
        epoch_before: int | None = None,
        epoch_after: int | None = None,
        trigger: str = "",
        observers_agreed: tuple[ObserverSource, ...] = (),
    ) -> ModeTransitionRecord:
        if not isinstance(kind, ModeRecordKind):
            raise ModeLogError("kind must be a closed-enum ModeRecordKind")
        if previous_mode is not None and not isinstance(previous_mode, Mode):
            raise ModeLogError("previous_mode must be a closed-enum Mode")
        if new_mode is not None and not isinstance(new_mode, Mode):
            raise ModeLogError("new_mode must be a closed-enum Mode")

        entry = ModeTransitionRecord(
            kind=kind,
            detail=detail,
            previous_mode=previous_mode,
            new_mode=new_mode,
            epoch_before=epoch_before,
            epoch_after=epoch_after,
            trigger=trigger,
            observers_agreed=tuple(observers_agreed),
        )
        self._records.append(entry)
        if self.jsonl_path is not None:
            self._append_jsonl(entry)
        return entry

    def _append_jsonl(self, entry: ModeTransitionRecord) -> None:
        path = Path(self.jsonl_path)  # type: ignore[arg-type]
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "kind": entry.kind.value,
                        "detail": entry.detail,
                        "previous_mode": (
                            entry.previous_mode.value if entry.previous_mode else None
                        ),
                        "new_mode": entry.new_mode.value if entry.new_mode else None,
                        "epoch_before": entry.epoch_before,
                        "epoch_after": entry.epoch_after,
                        "trigger": entry.trigger,
                        "observers_agreed": [o.value for o in entry.observers_agreed],
                        "timestamp": entry.timestamp.isoformat(),
                    }
                )
                + "\n"
            )

    def entries(self) -> tuple[ModeTransitionRecord, ...]:
        return tuple(self._records)

    def for_kind(self, kind: ModeRecordKind) -> tuple[ModeTransitionRecord, ...]:
        return tuple(e for e in self._records if e.kind is kind)

    def transitions(self) -> tuple[ModeTransitionRecord, ...]:
        return self.for_kind(ModeRecordKind.TRANSITION)


__all__ = [
    "ModeRecordKind",
    "ModeLogError",
    "ModeTransitionRecord",
    "ModeTransitionLog",
]
