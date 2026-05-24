"""Append-only operator audit log for kill-switch engage / disengage events.

The operator audit log is the single source of truth for kill-switch events
(per resolved decision #1 in ``Policy_Pipeline/operator-kill-switch.md``).
Tenant Blackboards stay clean — operator actions do not pollute per-tenant
audit trails.

Storage: JSON Lines at ``blackboard_root/operator_state/operator.audit.jsonl``.
Same append-only contract as ``core/blackboard/storage.py``, but the records
are not Blackboard records (operators are not agents).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from core.blackboard import GovernanceError

from .state import KillSwitchScope, _VALID_SCOPES

OperatorAuditAction = Literal["engage", "disengage"]


@dataclass(frozen=True)
class OperatorAuditEntry:
    """One line in the operator audit log."""

    action: OperatorAuditAction
    scope: KillSwitchScope
    previous_scope: KillSwitchScope
    operator: str
    reason: str
    at: datetime


def operator_audit_log_path(blackboard_root: Path) -> Path:
    """Return the on-disk path for the operator audit log."""

    return blackboard_root / "operator_state" / "operator.audit.jsonl"


def append_operator_audit_entry(path: Path, entry: OperatorAuditEntry) -> None:
    """Append one operator audit entry as a JSON line.

    The parent directory is created if missing. The timestamp is serialized
    via ``isoformat()`` to preserve tzinfo (UTC by convention).
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "action": entry.action,
        "scope": entry.scope,
        "previous_scope": entry.previous_scope,
        "operator": entry.operator,
        "reason": entry.reason,
        "at": entry.at.isoformat(),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def read_operator_audit_log(path: Path) -> list[OperatorAuditEntry]:
    """Return every audit entry from ``path`` in file order (chronological).

    A missing file is treated as an empty log. Each line must be a JSON
    object with the locked schema; malformed lines raise ``GovernanceError``
    so silent log corruption never goes unnoticed.
    """

    if not path.exists():
        return []

    entries: list[OperatorAuditEntry] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            entries.append(_parse_audit_line(stripped, line_number=line_number))
    return entries


def _parse_audit_line(line: str, *, line_number: int) -> OperatorAuditEntry:
    try:
        raw = json.loads(line)
    except json.JSONDecodeError as exc:
        raise GovernanceError(
            f"operator audit log line {line_number} is not valid JSON"
        ) from exc
    if not isinstance(raw, dict):
        raise GovernanceError(
            f"operator audit log line {line_number} is not a JSON object"
        )

    action = raw.get("action")
    if action not in ("engage", "disengage"):
        raise GovernanceError(
            f"operator audit log line {line_number}: invalid action {action!r}"
        )

    scope = raw.get("scope")
    if not isinstance(scope, str) or scope not in _VALID_SCOPES:
        raise GovernanceError(
            f"operator audit log line {line_number}: invalid scope {scope!r}"
        )

    previous_scope = raw.get("previous_scope")
    if not isinstance(previous_scope, str) or previous_scope not in _VALID_SCOPES:
        raise GovernanceError(
            f"operator audit log line {line_number}: "
            f"invalid previous_scope {previous_scope!r}"
        )

    operator = raw.get("operator")
    if not isinstance(operator, str):
        raise GovernanceError(
            f"operator audit log line {line_number}: operator must be a string"
        )

    reason = raw.get("reason")
    if not isinstance(reason, str):
        raise GovernanceError(
            f"operator audit log line {line_number}: reason must be a string"
        )

    at_raw = raw.get("at")
    if not isinstance(at_raw, str):
        raise GovernanceError(
            f"operator audit log line {line_number}: at must be an ISO-8601 string"
        )
    try:
        at = datetime.fromisoformat(at_raw)
    except ValueError as exc:
        raise GovernanceError(
            f"operator audit log line {line_number}: "
            f"at is not a valid ISO-8601 datetime: {at_raw!r}"
        ) from exc
    if at.tzinfo is None:
        at = at.replace(tzinfo=timezone.utc)

    return OperatorAuditEntry(
        action=action,  # type: ignore[arg-type]
        scope=scope,  # type: ignore[arg-type]
        previous_scope=previous_scope,  # type: ignore[arg-type]
        operator=operator,
        reason=reason,
        at=at,
    )
