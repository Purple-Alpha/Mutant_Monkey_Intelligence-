"""Mode Controller tests (Layer 6 Control Plane, scoreboard row #92).

Governing contract
------------------
``4. Product_Roadmap/Mode_Controller_Contract.md`` — §14 SIGNED 2026-06-13
(Matt Nichol).

Three test classes per AGENTS.md §5 / contract §8:
  Class 1 — expected pass
  Class 2 — adversarial (the falsifiable decision tests live here)
  Class 3 — known-gap xfail (documented, with completion path)

Each adversarial test cites the locked decision (MC-D*) or §7 failure mode it
falsifies.
"""

from __future__ import annotations

import dataclasses

import pytest

from core.mode_controller import (
    AgentInfluenceError,
    EpochError,
    FlappingError,
    Heartbeat,
    HOMEOSTASIS_WARNING_THRESHOLD,
    HomeostasisBand,
    HomeostasisError,
    HomeostasisLayer,
    MIN_DWELL_SECONDS,
    MODE_HEARTBEAT_TIMEOUT_SECONDS,
    Mode,
    ModeController,
    ModeRecordKind,
    ModeTransitionLog,
    ObserverSource,
    ObserverVote,
    QuorumError,
    RecoveryError,
    TenantModeView,
    TransitionError,
    compute_homeostasis_index,
)


class _Clock:
    """Deterministic injectable clock (monotonic seconds)."""

    def __init__(self, t: float = 1000.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


def _controller(clock: _Clock | None = None) -> ModeController:
    clock = clock or _Clock()
    return ModeController(log=ModeTransitionLog(), now=clock)


def _quorum() -> list[ObserverVote]:
    return [
        ObserverVote(ObserverSource.WATCHER, "w1"),
        ObserverVote(ObserverSource.BREAKER, "b1"),
    ]


def _all_layers(value: float) -> dict[HomeostasisLayer, float]:
    return {layer: value for layer in HomeostasisLayer}


def _step(m: ModeController, clock: _Clock, new_mode: Mode, trigger: str = "test") -> int:
    """Advance past the dwell window and perform a quorum-backed transition."""

    clock.advance(MIN_DWELL_SECONDS[m.mode.value] + 1.0)
    return m.request_transition(new_mode, observers=_quorum(), trigger=trigger)


# ---------------------------------------------------------------------------
# Class 1 — expected pass
# ---------------------------------------------------------------------------


def test_transitions_fire_through_all_four_states():
    clock = _Clock()
    m = _controller(clock)
    assert m.mode is Mode.NORMAL

    _step(m, clock, Mode.DEGRADED)
    assert m.mode is Mode.DEGRADED
    _step(m, clock, Mode.ISOLATED)
    assert m.mode is Mode.ISOLATED
    _step(m, clock, Mode.RECOVERING)
    assert m.mode is Mode.RECOVERING
    m.validate_recovery(observers=_quorum())
    _step(m, clock, Mode.NORMAL)
    assert m.mode is Mode.NORMAL


def test_epoch_increments_on_each_transition():
    clock = _Clock()
    m = _controller(clock)
    assert m.epoch == 0
    assert _step(m, clock, Mode.DEGRADED) == 1
    assert m.epoch == 1
    assert _step(m, clock, Mode.ISOLATED) == 2
    assert _step(m, clock, Mode.RECOVERING) == 3
    assert m.epoch == 3


def test_highest_epoch_wins_on_resolution_and_adoption():
    # MC-D3: highest epoch wins, always.
    assert ModeController.resolve_epoch(5, 3) == 5
    assert ModeController.resolve_epoch(3, 5) == 5

    tenant = TenantModeView(now=_Clock(), known_mode_epoch=2, current_mode=Mode.NORMAL)
    adopted = tenant.on_heartbeat(Heartbeat(mode=Mode.DEGRADED, epoch=7, timestamp=0.0))
    assert adopted is True
    assert tenant.known_mode_epoch == 7
    assert tenant.current_mode is Mode.DEGRADED


def test_heartbeat_timeout_triggers_local_isolated_without_epoch_increment():
    clock = _Clock()
    tenant = TenantModeView(now=clock, known_mode_epoch=4, current_mode=Mode.NORMAL)
    clock.advance(MODE_HEARTBEAT_TIMEOUT_SECONDS + 1.0)
    assert tenant.check_heartbeat_timeout() is True
    assert tenant.current_mode is Mode.ISOLATED
    assert tenant.local_fallback_active is True
    assert tenant.known_mode_epoch == 4  # MC-D6: no epoch increment on local fallback


def test_recovering_blocks_cross_tenant_sharing_until_validated():
    clock = _Clock()
    m = _controller(clock)
    _step(m, clock, Mode.DEGRADED)
    _step(m, clock, Mode.ISOLATED)
    _step(m, clock, Mode.RECOVERING)

    assert m.cross_tenant_operation_allowed("tenant-a") is False
    m.record_recovering_upload(tenant_id="tenant-a")  # uploads permitted in RECOVERING

    m.validate_recovery(observers=_quorum())
    _step(m, clock, Mode.NORMAL)
    assert m.cross_tenant_operation_allowed("tenant-a") is True


def test_homeostasis_index_computes_from_all_eight_layers():
    reading = compute_homeostasis_index(_all_layers(80.0))
    assert reading.score == pytest.approx(80.0)
    assert reading.band is HomeostasisBand.HEALTHY
    assert len(reading.layer_scores) == 8
    assert {layer for layer, _ in reading.layer_scores} == set(HomeostasisLayer)


def test_anti_flapping_blocks_transition_before_minimum_dwell():
    clock = _Clock()
    m = _controller(clock)
    _step(m, clock, Mode.DEGRADED)  # advances past dwell, now in DEGRADED
    # Immediate second transition, no dwell elapsed.
    with pytest.raises(FlappingError):
        m.request_transition(Mode.ISOLATED, observers=_quorum(), trigger="rapid")
    assert m.mode is Mode.DEGRADED


def test_every_transition_is_audited_append_only():
    # MC-D9: every transition logged with the required fields.
    clock = _Clock()
    log = ModeTransitionLog()
    m = ModeController(log=log, now=clock)
    _step(m, clock, Mode.DEGRADED, trigger="sustained_load")
    transitions = log.transitions()
    assert len(transitions) == 1
    rec = transitions[0]
    assert rec.previous_mode is Mode.NORMAL
    assert rec.new_mode is Mode.DEGRADED
    assert rec.epoch_before == 0 and rec.epoch_after == 1
    assert rec.trigger == "sustained_load"
    assert set(rec.observers_agreed) == {ObserverSource.WATCHER, ObserverSource.BREAKER}
    # Append-only: no update/delete API, and records are frozen.
    assert not hasattr(log, "delete")
    assert not hasattr(log, "update")
    with pytest.raises(dataclasses.FrozenInstanceError):
        rec.new_mode = Mode.ISOLATED  # type: ignore[misc]


def test_mode_check_seam_allows_local_dispatch_in_every_mode():
    clock = _Clock()
    m = _controller(clock)
    for target in (Mode.DEGRADED, Mode.ISOLATED, Mode.RECOVERING):
        assert m.is_dispatch_allowed("tenant-a") is True
        _step(m, clock, target)
    assert m.is_dispatch_allowed("tenant-a") is True  # RECOVERING


def test_recovery_broadcaster_seam_increments_epoch_and_returns_to_normal():
    clock = _Clock()
    m = _controller(clock)
    _step(m, clock, Mode.DEGRADED)
    _step(m, clock, Mode.ISOLATED)
    epoch_before = m.epoch
    new_epoch = m.broadcast_recovery(epoch_at_entry=epoch_before)
    assert new_epoch > epoch_before
    assert m.mode is Mode.NORMAL
    assert m.epoch == new_epoch


# ---------------------------------------------------------------------------
# Class 2 — adversarial (falsifiable decision tests)
# ---------------------------------------------------------------------------


def test_single_observer_cannot_force_transition():
    """Falsifies MC-D4: a single observer must not force a system-wide transition."""

    clock = _Clock()
    m = _controller(clock)
    clock.advance(MIN_DWELL_SECONDS[m.mode.value] + 1.0)
    with pytest.raises(QuorumError):
        m.request_transition(
            Mode.DEGRADED,
            observers=[ObserverVote(ObserverSource.WATCHER, "only-one")],
            trigger="single",
        )
    assert m.mode is Mode.NORMAL


def test_duplicate_source_does_not_satisfy_quorum():
    """Falsifies MC-D4: 'independent' observers — same source twice is one voice."""

    clock = _Clock()
    m = _controller(clock)
    clock.advance(MIN_DWELL_SECONDS[m.mode.value] + 1.0)
    with pytest.raises(QuorumError):
        m.request_transition(
            Mode.DEGRADED,
            observers=[
                ObserverVote(ObserverSource.WATCHER, "w1"),
                ObserverVote(ObserverSource.WATCHER, "w2"),
            ],
            trigger="dup",
        )
    assert m.mode is Mode.NORMAL


def test_agent_cannot_influence_mode():
    """Falsifies MC-D5: mode is not a surface agents can trigger."""

    clock = _Clock()
    log = ModeTransitionLog()
    m = ModeController(log=log, now=clock)
    clock.advance(MIN_DWELL_SECONDS[m.mode.value] + 1.0)
    with pytest.raises(AgentInfluenceError):
        m.request_transition(
            Mode.DEGRADED,
            observers=[
                ObserverVote(ObserverSource.WATCHER, "w1"),
                ObserverVote(ObserverSource.AGENT, "evil-agent"),
            ],
            trigger="agent",
        )
    assert m.mode is Mode.NORMAL
    assert len(log.for_kind(ModeRecordKind.QUORUM_DENIED)) == 1


def test_epoch_cannot_be_forged_or_decremented():
    """Falsifies MC-D2 / §7: epoch is controller-owned, monotonic, un-forgeable."""

    clock = _Clock()
    log = ModeTransitionLog()
    m = ModeController(log=log, now=clock)
    _step(m, clock, Mode.DEGRADED)
    assert m.epoch == 1
    with pytest.raises(EpochError):
        m.reject_epoch_forge(claimed_epoch=999, source="malicious")
    assert m.epoch == 1
    assert len(log.for_kind(ModeRecordKind.EPOCH_FORGE_REJECTED)) == 1
    # Resolution never decreases the epoch.
    assert ModeController.resolve_epoch(1, 0) == 1
    # A lower incoming epoch is ignored by tenants.
    tenant = TenantModeView(now=_Clock(), known_mode_epoch=5)
    assert tenant.on_heartbeat(Heartbeat(Mode.ISOLATED, 3, 0.0)) is False
    assert tenant.known_mode_epoch == 5


def test_flapping_rule_holds_under_rapid_trigger_attempts():
    """Falsifies MC-D8: rapid triggers cannot oscillate the mode."""

    clock = _Clock()
    m = _controller(clock)
    _step(m, clock, Mode.DEGRADED)
    for _ in range(5):
        with pytest.raises(FlappingError):
            m.request_transition(Mode.ISOLATED, observers=_quorum(), trigger="flap")
        clock.advance(0.5)
    assert m.mode is Mode.DEGRADED  # stabilised, never oscillated


def test_local_isolated_fallback_does_not_increment_epoch():
    """Falsifies MC-D6: local fallback must not touch the epoch."""

    clock = _Clock()
    tenant = TenantModeView(now=clock, known_mode_epoch=9, current_mode=Mode.NORMAL)
    clock.advance(MODE_HEARTBEAT_TIMEOUT_SECONDS + 5.0)
    tenant.check_heartbeat_timeout()
    assert tenant.current_mode is Mode.ISOLATED
    assert tenant.known_mode_epoch == 9


def test_recovering_cannot_be_bypassed_to_normal_without_validation():
    """Falsifies §3 / MC-D7: RECOVERING -> NORMAL requires validation."""

    clock = _Clock()
    m = _controller(clock)
    _step(m, clock, Mode.DEGRADED)
    _step(m, clock, Mode.ISOLATED)
    _step(m, clock, Mode.RECOVERING)
    clock.advance(MIN_DWELL_SECONDS[m.mode.value] + 1.0)
    with pytest.raises(RecoveryError):
        m.request_transition(Mode.NORMAL, observers=_quorum(), trigger="bypass")
    assert m.mode is Mode.RECOVERING


def test_homeostasis_index_cannot_be_manipulated_via_reported_state():
    """Falsifies §7: a CRITICAL index alone (one observer) never moves the mode."""

    clock = _Clock()
    m = _controller(clock)
    reading = m.ingest_homeostasis(_all_layers(10.0))  # deeply CRITICAL
    assert reading.critical is True
    assert m.mode is Mode.NORMAL  # index did not force a transition on its own
    # No agent-reported channel exists: an unknown/extra layer is rejected.
    with pytest.raises(HomeostasisError):
        compute_homeostasis_index({**_all_layers(80.0), "agent_reported": 100.0})  # type: ignore[dict-item]
    with pytest.raises(HomeostasisError):
        compute_homeostasis_index({HomeostasisLayer.CORTICAL: 80.0})  # missing layers


def test_disallowed_transition_is_rejected():
    """Falsifies §3: only defined transitions are permitted."""

    clock = _Clock()
    m = _controller(clock)
    clock.advance(MIN_DWELL_SECONDS[m.mode.value] + 1.0)
    with pytest.raises(TransitionError):
        m.request_transition(Mode.RECOVERING, observers=_quorum(), trigger="illegal")
    assert m.mode is Mode.NORMAL


def test_reconciliation_window_is_time_bounded():
    """Falsifies §7: RECOVERING that never completes escalates to the operator."""

    clock = _Clock()
    log = ModeTransitionLog()
    m = ModeController(log=log, now=clock)
    _step(m, clock, Mode.DEGRADED)
    _step(m, clock, Mode.ISOLATED)
    _step(m, clock, Mode.RECOVERING)
    assert m.reconciliation_timed_out() is False
    clock.advance(m.reconciliation_window + 1.0)
    assert m.reconciliation_timed_out() is True
    assert len(log.for_kind(ModeRecordKind.RECONCILIATION_TIMEOUT)) == 1


# ---------------------------------------------------------------------------
# Class 3 — known-gap xfail (documented; completion path named)
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason="Specific consensus technology deferred — cloud provider not selected; "
    "completion path: Lung contract (§1 out of scope).",
)
def test_specific_consensus_technology_implemented():
    assert hasattr(ModeController, "consensus_backend")


@pytest.mark.xfail(
    strict=True,
    reason="Cross-region mode coordination deferred — infrastructure selection "
    "pending; completion path: Lung contract (§1 out of scope).",
)
def test_cross_region_mode_coordination_implemented():
    assert hasattr(ModeController, "coordinate_cross_region")


@pytest.mark.xfail(
    strict=True,
    reason="Real tenant baseline calibration of Homeostasis thresholds deferred — "
    "requires production tenant data; completion path: signed amendment after "
    "first tenant onboarded (§8 Class 3).",
)
def test_homeostasis_thresholds_calibrated_from_tenant_data():
    # Provisional contract-drafting value until calibrated against real data.
    assert HOMEOSTASIS_WARNING_THRESHOLD != 70.0
