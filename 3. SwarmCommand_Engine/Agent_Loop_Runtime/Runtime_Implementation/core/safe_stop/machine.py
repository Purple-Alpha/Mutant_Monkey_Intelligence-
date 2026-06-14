"""SafeStopStateMachine — Layer 6 Control Plane, scoreboard row #94.

Governing contract
------------------
``4. Product_Roadmap/Safe_Stop_State_Machine_Design_Contract.md`` — §11 SIGNED
2026-06-14 (Matt Nichol).

Safe-stop is the organism's proof that it prefers bounded, logged,
operator-governed shutdown over silent corruption or uncontrolled behavior. This
machine owns the five named entry conditions, the entry protocol, the
permitted/forbidden behavior inside the state, and the exit protocol — and
nothing else (§ Out of Scope / § Non-Authorizations).

Interface seams (the separate, unbuilt Mode Controller owns these):
  - ``is_dispatch_allowed`` satisfies the gateway ``ModeCheck`` protocol so the
    Blast Radius Controller halts new dispatch while in safe-stop, without this
    machine owning mode transitions or quorum.
  - ``RecoveryBroadcaster`` is the Mode Controller's recovery-broadcast path
    (§ Exit Protocol step 3). Epoch is incremented **only** there, never here.
    ``DefaultRecoveryBroadcaster`` is a placeholder until the Mode Controller
    contract is built — analogous to the gateway's ``AllowAllModeCheck``.

Out of scope (must never appear here): automatic recovery, diagnosis/root-cause,
new agent types, Homeostasis Engine, CIS authorization, network isolation,
verdicting, or CIRT role definition.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Iterable, Protocol, runtime_checkable

from core.safe_stop.log import SafeStopLog, SafeStopRecordKind
from core.safe_stop.state import (
    RECONCILIATION_GRACE_SECONDS,
    SAFE_STOP_EXIT_AUTHORITY,
    SS1_QUORUM_LOSS_TIMEOUT_SECONDS,
    SS3_DUAL_CRITICAL_WINDOW_SECONDS,
    EntryCondition,
    ForbiddenAction,
    PermittedAction,
    SafeStopState,
)


class SafeStopError(Exception):
    """Raised on an invalid safe-stop operation (fail-safe)."""


class SafeStopViolation(SafeStopError):
    """Raised when a forbidden action is attempted inside safe-stop."""


class SafeStopAuthorityError(SafeStopError):
    """Raised when a non-operator attempts to exit safe-stop (OQ-3)."""


@runtime_checkable
class RecoveryBroadcaster(Protocol):
    """Mode Controller recovery-broadcast seam (§ Exit Protocol step 3, BRC-D10).

    Returns the new epoch after the standard Mode Controller recovery broadcast.
    The returned epoch must be strictly greater than ``epoch_at_entry`` — epoch
    is incremented only on recovery (Doctrine Invariant 1).
    """

    def broadcast_recovery(self, *, epoch_at_entry: int) -> int:
        ...


class DefaultRecoveryBroadcaster:
    """Placeholder recovery broadcaster until the Mode Controller is built.

    Increments the epoch by one to represent the Mode Controller broadcast. This
    machine never increments epoch itself — it delegates to this seam.
    """

    def broadcast_recovery(self, *, epoch_at_entry: int) -> int:  # noqa: D401
        return epoch_at_entry + 1


# The permitted set never includes a forbidden action — they are disjoint by
# construction (§ Behavior Inside Safe-Stop).
PERMITTED_INSIDE_SAFE_STOP: frozenset[PermittedAction] = frozenset(PermittedAction)


@dataclass
class SafeStopStateMachine:
    """The Safe-Stop State Machine (row #94).

    The clock is injectable (``now`` returning monotonic seconds) so the SS-1 /
    SS-3 timers and the reconciliation grace window are deterministic under test.
    """

    log: SafeStopLog
    now: Callable[[], float] = time.monotonic
    exit_authority: str = SAFE_STOP_EXIT_AUTHORITY
    recovery_broadcaster: RecoveryBroadcaster = field(
        default_factory=DefaultRecoveryBroadcaster
    )

    _state: SafeStopState = SafeStopState.RUNNING
    _entry_condition: EntryCondition | None = None
    _epoch_at_entry: int | None = None
    _entry_time: float | None = None
    _reconciliation_in_flight: bool = False
    _reconciliation_abort_logged: bool = False
    _operator_authorized: bool = False
    _safety_proof_logged: bool = False

    # Timer arming state for the two timed conditions.
    _quorum_loss_started_at: float | None = None
    _dual_critical_started_at: float | None = None

    # --- inspection ---------------------------------------------------------

    @property
    def state(self) -> SafeStopState:
        return self._state

    @property
    def entry_condition(self) -> EntryCondition | None:
        return self._entry_condition

    @property
    def epoch_at_entry(self) -> int | None:
        """Frozen epoch captured at entry; ``None`` while RUNNING (SS-INV-6)."""

        return self._epoch_at_entry

    def is_active(self) -> bool:
        return self._state is SafeStopState.SAFE_STOP

    # --- SS-1 timer (Mode Controller quorum loss) ---------------------------

    def note_quorum_loss(self) -> None:
        """Start the SS-1 timer when quorum drops below threshold (idempotent)."""

        if self._state is SafeStopState.RUNNING and self._quorum_loss_started_at is None:
            self._quorum_loss_started_at = self.now()

    def note_quorum_restored(self) -> None:
        """Quorum recovered within the window — disarm the SS-1 timer."""

        self._quorum_loss_started_at = None

    # --- SS-3 timer (two simultaneous CRITICAL watcher events) --------------

    def note_dual_critical_unresolved(self) -> None:
        """Start the SS-3 timer when the second CRITICAL event is logged."""

        if self._state is SafeStopState.RUNNING and self._dual_critical_started_at is None:
            self._dual_critical_started_at = self.now()

    def note_critical_resolved(self) -> None:
        """A resolution path closed the dual-CRITICAL state — disarm SS-3.

        Any one of the contract's resolution paths is sufficient (reconciliation
        closes both, re-classification below CRITICAL, containment to ISOLATED, or
        explicit operator acknowledgment). This machine only needs to know the
        unresolved state ended.
        """

        self._dual_critical_started_at = None

    # --- timed-condition poll -----------------------------------------------

    def poll(
        self,
        *,
        epoch: int,
        active_tenant_ids: Iterable[str] = (),
    ) -> EntryCondition | None:
        """Fire SS-1 / SS-3 when their armed timer reaches the contract timeout.

        SS-1 fires at exactly ``SS1_QUORUM_LOSS_TIMEOUT_SECONDS`` (SS-INV-9);
        SS-3 at exactly ``SS3_DUAL_CRITICAL_WINDOW_SECONDS`` (SS-INV-10).
        """

        if self._state is SafeStopState.SAFE_STOP:
            return self._entry_condition

        if self._quorum_loss_started_at is not None:
            elapsed = self.now() - self._quorum_loss_started_at
            if elapsed >= SS1_QUORUM_LOSS_TIMEOUT_SECONDS:
                return self._enter(
                    EntryCondition.SS1_QUORUM_LOSS,
                    detail=(
                        f"Mode Controller quorum unavailable for "
                        f"{elapsed:.0f}s (>= {SS1_QUORUM_LOSS_TIMEOUT_SECONDS:.0f}s)"
                    ),
                    detecting_component="mode_controller",
                    epoch=epoch,
                    active_tenant_ids=active_tenant_ids,
                )

        if self._dual_critical_started_at is not None:
            elapsed = self.now() - self._dual_critical_started_at
            if elapsed >= SS3_DUAL_CRITICAL_WINDOW_SECONDS:
                return self._enter(
                    EntryCondition.SS3_DUAL_CRITICAL,
                    detail=(
                        f"two simultaneous CRITICAL watcher events unresolved for "
                        f"{elapsed:.0f}s (>= {SS3_DUAL_CRITICAL_WINDOW_SECONDS:.0f}s)"
                    ),
                    detecting_component="watcher_agents",
                    epoch=epoch,
                    active_tenant_ids=active_tenant_ids,
                )

        return None

    # --- immediate (state-based) conditions ---------------------------------

    def trigger_privacy_breaker_unrecoverable(
        self,
        *,
        epoch: int,
        active_tenant_ids: Iterable[str] = (),
        detail: str = "",
    ) -> EntryCondition | None:
        """SS-2: Privacy Filter independent breaker is unrecoverably OPEN."""

        return self._enter(
            EntryCondition.SS2_PRIVACY_BREAKER,
            detail=detail or "privacy filter breaker unrecoverable",
            detecting_component="privacy_filter",
            epoch=epoch,
            active_tenant_ids=active_tenant_ids,
        )

    def trigger_boundary_violation(
        self,
        *,
        contained: bool,
        epoch: int,
        active_tenant_ids: Iterable[str] = (),
        detail: str = "",
    ) -> EntryCondition | None:
        """SS-4: signed-boundary violation with unproven containment.

        A boundary violation **with proven containment does not trigger
        safe-stop** (§ SS-4) — only the uncontained case fires.
        """

        if contained:
            return None
        return self._enter(
            EntryCondition.SS4_BOUNDARY_VIOLATION,
            detail=detail or "signed boundary violation; containment not proven",
            detecting_component="blast_radius_controller",
            epoch=epoch,
            active_tenant_ids=active_tenant_ids,
        )

    def trigger_unresolvable_conflict(
        self,
        *,
        epoch: int,
        active_tenant_ids: Iterable[str] = (),
        detail: str = "",
    ) -> EntryCondition | None:
        """SS-5: ReconciliationAgent surfaces an unresolvable named conflict.

        ReconciliationAgent does not self-authorize safe-stop — the conflict
        state is the trigger (§ SS-5).
        """

        return self._enter(
            EntryCondition.SS5_UNRESOLVABLE_CONFLICT,
            detail=detail or "unresolvable named evidence conflict",
            detecting_component="reconciliation_agent",
            epoch=epoch,
            active_tenant_ids=active_tenant_ids,
        )

    # --- entry protocol ------------------------------------------------------

    def _enter(
        self,
        condition: EntryCondition,
        *,
        detail: str,
        detecting_component: str,
        epoch: int,
        active_tenant_ids: Iterable[str],
        reconciliation_in_flight: bool = False,
    ) -> EntryCondition:
        """Execute the entry protocol. The first condition detected wins; a later
        trigger while already in safe-stop is a no-op that returns the active
        condition (§ Five Named Entry Conditions: "the first condition detected
        fires the entry protocol").
        """

        if self._state is SafeStopState.SAFE_STOP:
            assert self._entry_condition is not None
            return self._entry_condition

        # SS-INV-1: the entry record is written immediately, BEFORE any halt
        # action. This is the first side effect of entering safe-stop.
        self.log.record(
            kind=SafeStopRecordKind.ENTRY,
            detail=detail,
            condition=condition,
            epoch=epoch,
            detecting_component=detecting_component,
            active_tenant_ids=tuple(active_tenant_ids),
        )

        # SS-INV-6: epoch is frozen at entry and NOT incremented.
        self._epoch_at_entry = epoch
        self._entry_condition = condition
        self._entry_time = self.now()
        self._reconciliation_in_flight = reconciliation_in_flight
        self._reconciliation_abort_logged = False
        # Exit gates are closed on entry; recovery requires operator + proof.
        self._operator_authorized = False
        self._safety_proof_logged = False
        self._state = SafeStopState.SAFE_STOP
        return condition

    def mark_reconciliation_in_flight(self) -> None:
        """Record that a reconciliation ensemble was deliberating at entry, so the
        60s grace window (§ Entry Protocol step 6 / SS-INV-12) applies.
        """

        if self._state is SafeStopState.SAFE_STOP:
            self._reconciliation_in_flight = True

    # --- behavior inside safe-stop ------------------------------------------

    def is_dispatch_allowed(self, tenant_id: str) -> bool:
        """Gateway ``ModeCheck`` seam: no new dispatch while in safe-stop.

        This is how SS-INV-2/3/4/5 are enforced at the Blast Radius Controller —
        the gateway only *reads* this; a single agent can never flip it.
        """

        return not self.is_active()

    def is_forbidden(self, action: ForbiddenAction) -> bool:
        """True when ``action`` is forbidden right now (i.e. while in safe-stop)."""

        return self.is_active()

    def guard(self, action: ForbiddenAction, *, detail: str = "") -> None:
        """Raise ``SafeStopViolation`` (and log the blocked attempt) if a forbidden
        action is attempted inside safe-stop. A no-op while RUNNING.
        """

        if not isinstance(action, ForbiddenAction):
            raise SafeStopError("action must be a ForbiddenAction")
        if not self.is_active():
            return
        self.log.record(
            kind=SafeStopRecordKind.ACTION_BLOCKED,
            detail=f"{action.value} blocked in safe-stop: {detail}".rstrip(": "),
            condition=self._entry_condition,
            epoch=self._epoch_at_entry,
        )
        raise SafeStopViolation(
            f"{action.value!r} is forbidden inside safe-stop "
            f"(entry condition {self._entry_condition.value if self._entry_condition else '?'})"
        )

    @staticmethod
    def is_permitted_inside_safe_stop(action: PermittedAction) -> bool:
        return action in PERMITTED_INSIDE_SAFE_STOP

    # --- reconciliation grace window (§ Entry Protocol step 6) --------------

    def reconciliation_grace_deadline(self) -> float | None:
        if self._entry_time is None or not self._reconciliation_in_flight:
            return None
        return self._entry_time + RECONCILIATION_GRACE_SECONDS

    def reconciliation_aborted(self) -> bool:
        """SS-INV-12: in-flight reconciliation does not exceed 60s after entry."""

        deadline = self.reconciliation_grace_deadline()
        if deadline is None:
            return False
        if self.now() >= deadline:
            if not self._reconciliation_abort_logged:
                self.log.record(
                    kind=SafeStopRecordKind.RECONCILIATION_ABORTED,
                    detail=(
                        f"in-flight reconciliation aborted at "
                        f"{RECONCILIATION_GRACE_SECONDS:.0f}s grace deadline"
                    ),
                    condition=self._entry_condition,
                    epoch=self._epoch_at_entry,
                )
                self._reconciliation_abort_logged = True
            return True
        return False

    # --- exit protocol -------------------------------------------------------

    def authorize_exit(
        self, *, operator: str, instance_timestamp: str, statement: str
    ) -> None:
        """Exit protocol step 1 — operator action.

        Authorization must be named to the specific safe-stop instance and carry a
        statement that the condition is resolved or accepted. Only the contract's
        sole authority may authorize (OQ-3: Matt Nichol only).
        """

        if self._state is not SafeStopState.SAFE_STOP:
            raise SafeStopError("authorize_exit requires the machine to be in safe-stop")
        if operator != self.exit_authority:
            raise SafeStopAuthorityError(
                f"{operator!r} cannot exit safe-stop; sole authority is "
                f"{self.exit_authority!r} (OQ-3)"
            )
        if not instance_timestamp.strip():
            raise SafeStopError("authorization must name the safe-stop instance")
        if not statement.strip():
            raise SafeStopError(
                "authorization must state the condition is resolved or accepted"
            )
        self._operator_authorized = True
        self.log.record(
            kind=SafeStopRecordKind.OPERATOR_AUTHORIZATION,
            detail=(
                f"{operator} authorized exit for instance {instance_timestamp}: "
                f"{statement}"
            ),
            condition=self._entry_condition,
            epoch=self._epoch_at_entry,
        )

    def record_safety_proof(self, *, proof_detail: str) -> None:
        """Exit protocol step 2 — proof of state safety, logged before recovery."""

        if self._state is not SafeStopState.SAFE_STOP:
            raise SafeStopError("record_safety_proof requires safe-stop")
        if not proof_detail.strip():
            raise SafeStopError("proof of state safety detail is required")
        self._safety_proof_logged = True
        self.log.record(
            kind=SafeStopRecordKind.SAFETY_PROOF,
            detail=proof_detail,
            condition=self._entry_condition,
            epoch=self._epoch_at_entry,
        )

    def broadcast_recovery(self) -> int:
        """Exit protocol step 3 + 4 — recovery broadcast, then resume.

        Blocks unless the operator has authorized exit (SS-INV-7) and proof of
        state safety has been logged (SS-INV-8). Epoch is incremented only here,
        via the Mode Controller seam.
        """

        if self._state is not SafeStopState.SAFE_STOP:
            raise SafeStopError("broadcast_recovery requires safe-stop")
        if not self._operator_authorized:
            raise SafeStopError(
                "safe-stop exit requires explicit operator authorization (SS-INV-7)"
            )
        if not self._safety_proof_logged:
            raise SafeStopError(
                "recovery broadcast requires proof of state safety first (SS-INV-8)"
            )

        assert self._epoch_at_entry is not None
        new_epoch = self.recovery_broadcaster.broadcast_recovery(
            epoch_at_entry=self._epoch_at_entry
        )
        if new_epoch <= self._epoch_at_entry:
            raise SafeStopError(
                "recovery broadcast must increment the epoch (Doctrine Invariant 1)"
            )
        self.log.record(
            kind=SafeStopRecordKind.RECOVERY_BROADCAST,
            detail=f"recovery broadcast; epoch {self._epoch_at_entry} -> {new_epoch}",
            condition=self._entry_condition,
            epoch=new_epoch,
        )

        # Step 4 — resume under existing signed-contract constraints.
        self._state = SafeStopState.RUNNING
        self._entry_condition = None
        self._epoch_at_entry = None
        self._entry_time = None
        self._reconciliation_in_flight = False
        self._reconciliation_abort_logged = False
        self._operator_authorized = False
        self._safety_proof_logged = False
        self._quorum_loss_started_at = None
        self._dual_critical_started_at = None
        return new_epoch


__all__ = [
    "SafeStopError",
    "SafeStopViolation",
    "SafeStopAuthorityError",
    "RecoveryBroadcaster",
    "DefaultRecoveryBroadcaster",
    "PERMITTED_INSIDE_SAFE_STOP",
    "SafeStopStateMachine",
]
