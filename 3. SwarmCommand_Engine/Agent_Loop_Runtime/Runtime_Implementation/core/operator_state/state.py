"""Operator-controlled kill-switch state for the runtime.

The kill switch is a SEPARATE surface from ``production_state`` (Guardrail
11's four mutable surfaces are unchanged). It is owned by the operator, not
by any agent, and no agent code path writes to it.

Persistence mirrors ``core/production_state/state.py``: a single frozen
dataclass, atomic ``.tmp`` + rename writes, and a strict disk-load that
rejects unauthorized fields. Defense-by-convention is sufficient for the
prototype: the engage / disengage write functions live in
``core.operator_state.gate`` and are not imported by any agent or loop
module. See ``Policy_Pipeline/operator-kill-switch.md`` for the full spec.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, TypeAlias

from core.blackboard import GovernanceError

KillSwitchScope: TypeAlias = Literal["NONE", "ALL", "PRODUCTION_ONLY", "SANDBOX_ONLY"]

_VALID_SCOPES: frozenset[str] = frozenset(
    {"NONE", "ALL", "PRODUCTION_ONLY", "SANDBOX_ONLY"}
)
_ALLOWED_FIELDS: frozenset[str] = frozenset(
    {"kill_switch_scope", "engaged_at", "engaged_by", "reason"}
)


@dataclass(frozen=True)
class OperatorControlState:
    """Frozen snapshot of the operator-controlled kill switch.

    All fields are optional. The default ``OperatorControlState()`` represents
    "no kill switch engaged" — every loop entry treats this as a green light.
    """

    kill_switch_scope: KillSwitchScope = "NONE"
    engaged_at: datetime | None = None
    engaged_by: str | None = None
    reason: str | None = None


class KillSwitchEngaged(RuntimeError):
    """Raised by every loop entry when the kill switch covers its scope.

    Carries the active ``OperatorControlState`` so the caller can log the
    scope, reason, and engaged-at timestamp without re-reading from disk.
    """

    def __init__(self, state: OperatorControlState) -> None:
        self.state = state
        engaged_at_iso = (
            state.engaged_at.isoformat() if state.engaged_at is not None else "None"
        )
        super().__init__(
            f"kill switch engaged (scope={state.kill_switch_scope}, "
            f"reason={state.reason}, engaged_by={state.engaged_by}, "
            f"engaged_at={engaged_at_iso})"
        )

    @property
    def scope(self) -> KillSwitchScope:
        return self.state.kill_switch_scope

    @property
    def reason(self) -> str | None:
        return self.state.reason

    @property
    def engaged_at(self) -> datetime | None:
        return self.state.engaged_at

    @property
    def engaged_by(self) -> str | None:
        return self.state.engaged_by


def operator_state_path(blackboard_root: Path) -> Path:
    """Return the on-disk path for the operator control state file."""

    return blackboard_root / "operator_state" / "operator.json"


def load_operator_state(path: Path) -> OperatorControlState:
    """Load the current operator control state.

    Returns the default ``OperatorControlState()`` if no state file exists.
    Mirrors the strict disk-load behaviour of
    ``core.production_state.state.load_state``: unauthorized fields, invalid
    scope literals, and wrong primitive types all raise ``GovernanceError``.
    """

    if not path.exists():
        return OperatorControlState()
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise GovernanceError("operator state file is not a JSON object")
    unknown = set(raw.keys()) - _ALLOWED_FIELDS
    if unknown:
        raise GovernanceError(
            f"operator state file contains unauthorized fields: {sorted(unknown)}"
        )

    scope = raw.get("kill_switch_scope", "NONE")
    if not isinstance(scope, str) or scope not in _VALID_SCOPES:
        raise GovernanceError(
            f"kill_switch_scope must be one of {sorted(_VALID_SCOPES)}, got {scope!r}"
        )

    engaged_at_raw = raw.get("engaged_at")
    engaged_at = _parse_optional_datetime(engaged_at_raw, field_name="engaged_at")

    engaged_by = raw.get("engaged_by")
    if engaged_by is not None and not isinstance(engaged_by, str):
        raise GovernanceError("engaged_by must be a string or null")

    reason = raw.get("reason")
    if reason is not None and not isinstance(reason, str):
        raise GovernanceError("reason must be a string or null")

    return OperatorControlState(
        kill_switch_scope=scope,  # type: ignore[arg-type]
        engaged_at=engaged_at,
        engaged_by=engaged_by,
        reason=reason,
    )


def save_operator_state(path: Path, state: OperatorControlState) -> None:
    """Atomically persist the operator control state.

    The write goes to a sibling ``.tmp`` file and is then renamed, identical
    to ``core.production_state.state.save_state``.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "kill_switch_scope": state.kill_switch_scope,
        "engaged_at": (
            state.engaged_at.isoformat() if state.engaged_at is not None else None
        ),
        "engaged_by": state.engaged_by,
        "reason": state.reason,
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, sort_keys=True, indent=2), encoding="utf-8")
    tmp.replace(path)


def _parse_optional_datetime(value: object, *, field_name: str) -> datetime | None:
    """Coerce a JSON-loaded value into a tz-aware datetime or ``None``.

    Accepts ``None``, empty string, or ISO-8601 string. Naive timestamps are
    treated as UTC, matching the runtime's "always UTC on disk" convention.
    """

    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise GovernanceError(f"{field_name} must be an ISO-8601 string or null")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise GovernanceError(
            f"{field_name} is not a valid ISO-8601 datetime: {value!r}"
        ) from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed
