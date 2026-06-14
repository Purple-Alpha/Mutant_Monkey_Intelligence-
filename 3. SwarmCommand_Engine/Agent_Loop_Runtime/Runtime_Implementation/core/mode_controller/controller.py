"""ModeController — the authoritative operating mode + epoch of the swarm.

Governing contract
------------------
``4. Product_Roadmap/Mode_Controller_Contract.md`` — §14 SIGNED 2026-06-13
(Matt Nichol). Scoreboard row #92 (Layer 6 Control Plane).

This component owns exactly one thing: the authoritative operating mode and the
monotonic ``mode_epoch`` (MC-D1, MC-D2). It is the only component that may
increment the epoch (MC-D2); the highest epoch always wins (MC-D3). Transitions
require a quorum of independent control-plane observers (MC-D4); agents can
neither see, request, nor influence mode changes (MC-D5); minimum dwell time
prevents flapping (MC-D8); and every transition is an append-only audit record
(MC-D9).

Resilience (MC-D11) — the four required plans:
  * Compartment: this module owns only mode + epoch and holds no business logic;
    halting dispatch is the Safe-Stop machine's job, not this one's.
  * Redundancy: tenants keep a local mode view and fall back to ISOLATED on
    heartbeat loss without the controller (``TenantModeView``, MC-D6).
  * Degradation: DEGRADED and ISOLATED are graceful, bounded degraded states in
    which local operation always continues (§3).
  * Recovery: RECOVERING + the epoch-incrementing recovery broadcast bring the
    organism back to NORMAL only after validation (MC-D7).

Interface seams this controller satisfies for already-built components:
  * ``ModeCheck`` (Blast Radius gateway, BRC-D10): ``is_dispatch_allowed`` —
    local dispatch continues in every mode by design, so this returns True; the
    meaningful gate is ``cross_tenant_operation_allowed`` (NORMAL only, §3).
  * ``RecoveryBroadcaster`` (Safe-Stop exit protocol step 3): ``broadcast_recovery``
    is the single epoch-incrementing recovery path the Safe-Stop machine calls.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Iterable

from core.mode_controller.homeostasis import (
    HomeostasisReading,
    compute_homeostasis_index,
)
from core.mode_controller.log import ModeRecordKind, ModeTransitionLog
from core.mode_controller.state import (
    ALLOWED_TRANSITIONS,
    HOMEOSTASIS_CRITICAL_THRESHOLD,
    MIN_DWELL_SECONDS,
    MODE_HEARTBEAT_TIMEOUT_SECONDS,
    QUORUM_ELIGIBLE_SOURCES,
    QUORUM_MIN_OBSERVERS,
    RECONCILIATION_WINDOW_SECONDS,
    HomeostasisLayer,
    Mode,
    ObserverSource,
)


class ModeControllerError(Exception):
    """Base class for mode-controller failures (fail-safe)."""


class QuorumError(ModeControllerError):
    """Raised when a transition lacks the required independent-observer quorum."""


class AgentInfluenceError(ModeControllerError):
    """Raised when an agent-sourced vote is presented (MC-D5)."""


class FlappingError(ModeControllerError):
    """Raised when a transition is attempted before minimum dwell time (MC-D8)."""


class TransitionError(ModeControllerError):
    """Raised when a (from, to) mode pair is not an allowed transition (§3)."""


class RecoveryError(ModeControllerError):
    """Raised when RECOVERING is bypassed to NORMAL without validation (§3, MC-D7)."""


class EpochError(ModeControllerError):
    """Raised on an attempt to forge or decrement the epoch (MC-D2, §7)."""


@dataclass(frozen=True)
class ObserverVote:
    """One observer's agreement toward a quorum (MC-D4).

    ``source`` identifies the independent control-plane subsystem; ``observer_id``
    distinguishes instances. Agent-sourced votes are rejected, never counted.
    """

    source: ObserverSource
    observer_id: str = ""


@dataclass(frozen=True)
class Heartbeat:
    """The mode + epoch broadcast tenants adopt (§4)."""

    mode: Mode
    epoch: int
    timestamp: float


@dataclass
class ModeController:
    """The autonomic nervous system: authoritative mode + epoch (row #92).

    The clock is injectable (``now`` returning monotonic seconds) so dwell,
    heartbeat-timeout, and reconciliation-window logic is deterministic in tests.
    """

    log: ModeTransitionLog
    now: Callable[[], float] = time.monotonic
    quorum_min: int = QUORUM_MIN_OBSERVERS
    heartbeat_timeout: float = MODE_HEARTBEAT_TIMEOUT_SECONDS
    reconciliation_window: float = RECONCILIATION_WINDOW_SECONDS

    _mode: Mode = Mode.NORMAL
    _epoch: int = 0
    _mode_entered_at: float = field(default=0.0)
    _recovery_validated: bool = False
    _reconciliation_started_at: float | None = None
    _initialised: bool = False

    def __post_init__(self) -> None:
        if not self._initialised:
            self._mode_entered_at = self.now()
            self._initialised = True

    # --- inspection ---------------------------------------------------------

    @property
    def mode(self) -> Mode:
        return self._mode

    @property
    def epoch(self) -> int:
        return self._epoch

    @property
    def recovery_validated(self) -> bool:
        return self._recovery_validated

    def heartbeat(self) -> Heartbeat:
        """The current authoritative mode + epoch, for broadcast to tenants (§4)."""

        return Heartbeat(mode=self._mode, epoch=self._epoch, timestamp=self.now())

    # --- quorum + dwell guards ---------------------------------------------

    def _check_quorum(
        self, votes: Iterable[ObserverVote], *, trigger: str
    ) -> tuple[ObserverSource, ...]:
        votes = tuple(votes)
        # MC-D5: an agent can never influence mode — reject + log, do not count.
        if any(v.source is ObserverSource.AGENT for v in votes):
            self.log.record(
                kind=ModeRecordKind.QUORUM_DENIED,
                detail="agent-sourced vote rejected; agents cannot influence mode",
                trigger=trigger,
            )
            raise AgentInfluenceError("agent-sourced vote is not eligible for quorum")

        eligible = {v.source for v in votes if v.source in QUORUM_ELIGIBLE_SOURCES}
        if len(eligible) < self.quorum_min:
            self.log.record(
                kind=ModeRecordKind.QUORUM_DENIED,
                detail=(
                    f"quorum not met: {len(eligible)} distinct independent "
                    f"observer(s) < required {self.quorum_min}"
                ),
                trigger=trigger,
            )
            raise QuorumError(
                f"quorum requires >= {self.quorum_min} distinct independent "
                f"observers; got {len(eligible)}"
            )
        return tuple(sorted(eligible, key=lambda s: s.value))

    def _check_dwell(self, *, trigger: str) -> None:
        dwell = MIN_DWELL_SECONDS[self._mode.value]
        elapsed = self.now() - self._mode_entered_at
        if elapsed < dwell:
            self.log.record(
                kind=ModeRecordKind.FLAPPING_DENIED,
                detail=(
                    f"min dwell not met in {self._mode.value}: {elapsed:.1f}s "
                    f"< {dwell:.1f}s"
                ),
                previous_mode=self._mode,
                trigger=trigger,
            )
            raise FlappingError(
                f"minimum dwell time not met in {self._mode.value} "
                f"({elapsed:.1f}s < {dwell:.1f}s)"
            )

    # --- the one transition path -------------------------------------------

    def request_transition(
        self,
        new_mode: Mode,
        *,
        observers: Iterable[ObserverVote],
        trigger: str,
    ) -> int:
        """Quorum-gated, anti-flap, audited mode transition. Returns new epoch.

        This is the only public path that changes the authoritative mode and is
        the only place (besides ``broadcast_recovery``) the epoch is incremented.
        """

        if not isinstance(new_mode, Mode):
            raise TransitionError("new_mode must be a Mode")

        if (self._mode, new_mode) not in ALLOWED_TRANSITIONS:
            raise TransitionError(
                f"{self._mode.value} -> {new_mode.value} is not an allowed transition"
            )

        # RECOVERING -> NORMAL cannot be reached without validation (MC-D7, §3).
        if (
            self._mode is Mode.RECOVERING
            and new_mode is Mode.NORMAL
            and not self._recovery_validated
        ):
            self.log.record(
                kind=ModeRecordKind.QUORUM_DENIED,
                detail="RECOVERING -> NORMAL blocked: recovery not yet validated",
                previous_mode=self._mode,
                new_mode=new_mode,
                trigger=trigger,
            )
            raise RecoveryError(
                "RECOVERING cannot transition to NORMAL until recovery is validated"
            )

        agreed = self._check_quorum(observers, trigger=trigger)
        self._check_dwell(trigger=trigger)

        return self._commit_transition(new_mode, trigger=trigger, observers=agreed)

    def _commit_transition(
        self,
        new_mode: Mode,
        *,
        trigger: str,
        observers: tuple[ObserverSource, ...],
    ) -> int:
        epoch_before = self._epoch
        self._epoch += 1  # MC-D2: only the controller increments the epoch.
        previous = self._mode
        self._mode = new_mode
        self._mode_entered_at = self.now()

        if new_mode is Mode.RECOVERING:
            self._recovery_validated = False
            self._reconciliation_started_at = self.now()
        elif new_mode is Mode.NORMAL:
            self._recovery_validated = False
            self._reconciliation_started_at = None

        self.log.record(
            kind=ModeRecordKind.TRANSITION,
            detail=f"{previous.value} -> {new_mode.value}",
            previous_mode=previous,
            new_mode=new_mode,
            epoch_before=epoch_before,
            epoch_after=self._epoch,
            trigger=trigger,
            observers_agreed=observers,
        )
        return self._epoch

    # --- RECOVERING reconciliation (MC-D7, §3) ------------------------------

    def validate_recovery(self, *, observers: Iterable[ObserverVote]) -> None:
        """Validate organism state across tenants so RECOVERING may reach NORMAL.

        Requires a quorum — recovery is never declared by a single observer.
        """

        if self._mode is not Mode.RECOVERING:
            raise RecoveryError("validate_recovery is only valid in RECOVERING")
        self._check_quorum(observers, trigger="recovery_validation")
        self._recovery_validated = True

    def cross_tenant_operation_allowed(self, tenant_id: str = "") -> bool:
        """Cross-tenant operations are permitted in NORMAL only (§3, MC-D7).

        In RECOVERING, no *new* cross-tenant sharing is allowed until validation
        completes and the controller increments to the NORMAL epoch.
        """

        return self._mode is Mode.NORMAL

    def record_recovering_upload(self, *, tenant_id: str, detail: str = "") -> None:
        """Tenants may upload pattern hashes + anomaly counts only in RECOVERING (MC-D7)."""

        if self._mode is not Mode.RECOVERING:
            raise RecoveryError(
                "RECOVERING-only uploads are not permitted outside RECOVERING"
            )

    def reconciliation_timed_out(self) -> bool:
        """True if RECOVERING has exceeded its bounded window (operator escalation, §7)."""

        if self._mode is not Mode.RECOVERING or self._reconciliation_started_at is None:
            return False
        elapsed = self.now() - self._reconciliation_started_at
        if elapsed >= self.reconciliation_window:
            self.log.record(
                kind=ModeRecordKind.RECONCILIATION_TIMEOUT,
                detail=(
                    f"RECOVERING exceeded {self.reconciliation_window:.0f}s "
                    f"({elapsed:.0f}s); operator escalation required"
                ),
                previous_mode=self._mode,
                trigger="reconciliation_window",
            )
            return True
        return False

    # --- Global Homeostasis Index (§5, MC-D10) ------------------------------

    def ingest_homeostasis(
        self, layer_scores: dict[HomeostasisLayer, float]
    ) -> HomeostasisReading:
        """Compute the index from objective layers and log a band alert.

        Computing the index never changes the mode by itself — a CRITICAL index
        is one observer's signal, and a single observer can never force a
        transition (MC-D4). The control plane must still gather quorum and call
        ``request_transition``. This keeps the index un-manipulable: there is no
        path by which a reported score moves the mode on its own.
        """

        reading = compute_homeostasis_index(layer_scores)
        if reading.warns:
            self.log.record(
                kind=ModeRecordKind.HOMEOSTASIS_ALERT,
                detail=(
                    f"homeostasis index {reading.score:.1f} band={reading.band.value} "
                    f"(critical<{HOMEOSTASIS_CRITICAL_THRESHOLD:.0f})"
                ),
                previous_mode=self._mode,
                trigger="homeostasis_index",
            )
        return reading

    # --- epoch resolution + forge guard (MC-D2, MC-D3, §7) ------------------

    @staticmethod
    def resolve_epoch(local_epoch: int, incoming_epoch: int) -> int:
        """Highest epoch wins, always, no exceptions (MC-D3)."""

        return max(local_epoch, incoming_epoch)

    def reject_epoch_forge(self, *, claimed_epoch: int, source: str) -> int:
        """Record and refuse any attempt to set/decrement the epoch externally.

        There is deliberately no public epoch setter; this method exists so a
        forge/decrement attempt fails loudly and is logged (§7). The authoritative
        epoch is returned unchanged — it never decreases.
        """

        self.log.record(
            kind=ModeRecordKind.EPOCH_FORGE_REJECTED,
            detail=(
                f"rejected epoch forge from {source}: claimed {claimed_epoch}, "
                f"authoritative {self._epoch} (epoch is controller-owned, monotonic)"
            ),
            trigger="epoch_forge",
        )
        raise EpochError(
            "epoch is owned by the Mode Controller and cannot be set externally"
        )

    # --- ModeCheck seam (gateway BRC-D10) -----------------------------------

    def is_dispatch_allowed(self, tenant_id: str) -> bool:
        """Local dispatch continues in every mode by design (§3).

        The Mode Controller never halts local dispatch — "everything keeps
        working, just no network effect" (ISOLATED). Halting dispatch is the
        Safe-Stop machine's responsibility, not this one's (compartment, MC-D11).
        """

        return True

    # --- RecoveryBroadcaster seam (Safe-Stop exit protocol step 3) ----------

    def broadcast_recovery(self, *, epoch_at_entry: int) -> int:
        """Increment the epoch and broadcast recovery after a safe-stop event.

        This is the single epoch-incrementing recovery path the Safe-Stop machine
        calls on exit (operator authorization + state-safety proof already
        happened upstream in the Safe-Stop exit protocol). The returned epoch is
        strictly greater than both the authoritative and the entry epoch
        (MC-D2/MC-D3; Safe-Stop Doctrine Invariant 1).
        """

        previous = self._mode
        epoch_before = self._epoch
        self._epoch = self.resolve_epoch(self._epoch, epoch_at_entry) + 1
        self._mode = Mode.NORMAL
        self._mode_entered_at = self.now()
        self._recovery_validated = False
        self._reconciliation_started_at = None
        self.log.record(
            kind=ModeRecordKind.TRANSITION,
            detail=f"safe-stop recovery broadcast: {previous.value} -> normal",
            previous_mode=previous,
            new_mode=Mode.NORMAL,
            epoch_before=epoch_before,
            epoch_after=self._epoch,
            trigger="safe_stop_recovery_broadcast",
        )
        return self._epoch


@dataclass
class TenantModeView:
    """Tenant-side mode state and epoch-adoption rules (§4).

    Tenants adopt a strictly-higher incoming epoch, fall back to a local ISOLATED
    on heartbeat timeout *without* incrementing the epoch (MC-D6), and rejoin when
    the controller broadcasts a higher recovery epoch.
    """

    now: Callable[[], float] = time.monotonic
    heartbeat_timeout: float = MODE_HEARTBEAT_TIMEOUT_SECONDS

    current_mode: Mode = Mode.NORMAL
    known_mode_epoch: int = 0
    last_mode_heartbeat_ts: float = field(default=0.0)
    local_fallback_active: bool = False
    _initialised: bool = False

    def __post_init__(self) -> None:
        if not self._initialised:
            self.last_mode_heartbeat_ts = self.now()
            self._initialised = True

    def on_heartbeat(self, heartbeat: Heartbeat) -> bool:
        """Adopt mode + epoch iff incoming epoch is strictly higher (§4, MC-D3).

        Returns True if adopted. A non-higher epoch is ignored (the epoch never
        moves backward), and adoption clears any local fallback.
        """

        self.last_mode_heartbeat_ts = self.now()
        if heartbeat.epoch > self.known_mode_epoch:
            self.current_mode = heartbeat.mode
            self.known_mode_epoch = heartbeat.epoch
            self.local_fallback_active = False
            return True
        return False

    def check_heartbeat_timeout(self) -> bool:
        """On timeout, switch to local ISOLATED without incrementing epoch (MC-D6).

        Returns True if the local fallback was (or remains) engaged this check.
        """

        elapsed = self.now() - self.last_mode_heartbeat_ts
        if elapsed >= self.heartbeat_timeout:
            self.current_mode = Mode.ISOLATED
            self.local_fallback_active = True
            return True
        return False


__all__ = [
    "ModeControllerError",
    "QuorumError",
    "AgentInfluenceError",
    "FlappingError",
    "TransitionError",
    "RecoveryError",
    "EpochError",
    "ObserverVote",
    "Heartbeat",
    "ModeController",
    "TenantModeView",
]
