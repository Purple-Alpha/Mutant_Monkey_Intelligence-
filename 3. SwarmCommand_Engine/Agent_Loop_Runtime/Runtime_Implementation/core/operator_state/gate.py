"""Operator kill-switch gate: engage, disengage, and halt-on-entry check.

This module is intentionally **not imported** by any agent or loop module
(per spec ``Policy_Pipeline/operator-kill-switch.md``). The engage /
disengage functions are intended for CLI / REPL / future operator-dashboard
use. The read helper ``is_kill_switch_engaged`` is the only function loop
entry points import, via ``core.operator_state``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from .audit import (
    OperatorAuditEntry,
    append_operator_audit_entry,
    operator_audit_log_path,
)
from .state import (
    KillSwitchEngaged,
    KillSwitchScope,
    OperatorControlState,
    load_operator_state,
    operator_state_path,
    save_operator_state,
)

EngageScope = Literal["ALL", "PRODUCTION_ONLY", "SANDBOX_ONLY"]
LoopScope = Literal["PRODUCTION", "SANDBOX"]


def engage_kill_switch(
    blackboard_root: Path,
    *,
    scope: KillSwitchScope,
    reason: str,
    operator: str,
) -> OperatorControlState:
    """Engage the operator kill switch for ``scope``.

    Writes the new ``OperatorControlState`` to ``operator.json`` atomically
    and appends one ``engage`` entry to ``operator.audit.jsonl``. Returns
    the new state.

    Raises ``ValueError`` for empty ``reason``, empty ``operator``, or a
    ``scope`` of ``"NONE"`` (use ``disengage_kill_switch`` instead).
    """

    if scope == "NONE":
        raise ValueError("cannot engage kill switch with scope NONE")
    if scope not in ("ALL", "PRODUCTION_ONLY", "SANDBOX_ONLY"):
        raise ValueError(
            "scope must be one of {'ALL', 'PRODUCTION_ONLY', 'SANDBOX_ONLY'}, "
            f"got {scope!r}"
        )
    if not reason.strip():
        raise ValueError("reason must not be empty")
    if not operator.strip():
        raise ValueError("operator must not be empty")

    state_path = operator_state_path(blackboard_root)
    previous = load_operator_state(state_path)

    now = datetime.now(timezone.utc)
    new_state = OperatorControlState(
        kill_switch_scope=scope,
        engaged_at=now,
        engaged_by=operator,
        reason=reason,
    )
    save_operator_state(state_path, new_state)
    append_operator_audit_entry(
        operator_audit_log_path(blackboard_root),
        OperatorAuditEntry(
            action="engage",
            scope=scope,
            previous_scope=previous.kill_switch_scope,
            operator=operator,
            reason=reason,
            at=now,
        ),
    )
    return new_state


def disengage_kill_switch(
    blackboard_root: Path,
    *,
    reason: str,
    operator: str,
) -> OperatorControlState:
    """Disengage the operator kill switch.

    Always records the disengage action in the audit log, even when the
    previous state was already ``NONE`` — per the spec's "operator intent
    recorded" rule (behavior contract: "Disengage when already disengaged
    -> state unchanged; one disengage audit record written anyway").

    Raises ``ValueError`` for empty ``reason`` or empty ``operator``.
    """

    if not reason.strip():
        raise ValueError("reason must not be empty")
    if not operator.strip():
        raise ValueError("operator must not be empty")

    state_path = operator_state_path(blackboard_root)
    previous = load_operator_state(state_path)

    now = datetime.now(timezone.utc)
    new_state = OperatorControlState()
    save_operator_state(state_path, new_state)
    append_operator_audit_entry(
        operator_audit_log_path(blackboard_root),
        OperatorAuditEntry(
            action="disengage",
            scope="NONE",
            previous_scope=previous.kill_switch_scope,
            operator=operator,
            reason=reason,
            at=now,
        ),
    )
    return new_state


def is_kill_switch_engaged(
    blackboard_root: Path,
    *,
    scope: LoopScope,
) -> OperatorControlState | None:
    """Return the active state iff a kill switch covers ``scope``, else ``None``.

    Production-side loops pass ``scope="PRODUCTION"`` and see the state when
    ``kill_switch_scope`` is ``ALL`` or ``PRODUCTION_ONLY``. Sandbox-side
    loops pass ``scope="SANDBOX"`` and see the state when ``kill_switch_scope``
    is ``ALL`` or ``SANDBOX_ONLY``. The default state (``NONE``) and the
    cross-domain scope return ``None`` so the loop proceeds normally.

    Cheap and side-effect-free: one JSON read of the on-disk operator state.
    Safe to call at the top of every loop entry on every tick.
    """

    state = load_operator_state(operator_state_path(blackboard_root))
    if scope == "PRODUCTION":
        if state.kill_switch_scope in ("ALL", "PRODUCTION_ONLY"):
            return state
        return None
    if scope == "SANDBOX":
        if state.kill_switch_scope in ("ALL", "SANDBOX_ONLY"):
            return state
        return None
    raise ValueError(
        f"scope must be 'PRODUCTION' or 'SANDBOX', got {scope!r}"
    )


def _check_or_raise(blackboard_root: Path, *, scope: LoopScope) -> None:
    """Raise ``KillSwitchEngaged`` if the switch covers ``scope``.

    Tiny convenience used at the top of every loop entry. Kept private; loop
    modules call ``is_kill_switch_engaged`` + raise directly to keep the
    stack trace at the right level.
    """

    state = is_kill_switch_engaged(blackboard_root, scope=scope)
    if state is not None:
        raise KillSwitchEngaged(state)
