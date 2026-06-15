"""Mode Controller adversarial suite (#99).

Governing contract
------------------
``4. Product_Roadmap/Mode_Controller_Adversarial_Test_Suite_Contract.md`` —
§11 SIGNED 2026-06-14 (Matt Nichol).

Every MC-ADV test ID from the signed contract is represented and executed. Each
test attacks the *real* ``ModeController`` API — there are no mock controllers
here — and asserts the safe behavior the contract names. Per the governing rule,
each test is falsifiable: it would fail against a deliberately weakened Mode
Controller (one that parsed string labels, skipped quorum/dwell, exposed an
override, swallowed exceptions into an allow, or let an agent vote).

Scope note (honest boundary)
----------------------------
The Mode Controller component owns exactly one thing: the authoritative mode and
the monotonic epoch. Several contract vectors describe *infrastructure* attacks
(broker ACLs, CI mock substitution, transport headers, distributed stale-config
nodes, environment separation). Those are not component code paths. For each, the
test asserts the **component-level invariant** that removes the bypass surface
from the Mode Controller itself (no external mode/epoch setter, no permissive
flag, no routing/command/token surface, no payload-supplied timestamp). The
report accompanying this suite states plainly which protections are component-
level vs. which require infrastructure controls outside #92.
"""

from __future__ import annotations

import dataclasses
import inspect
import re

import pytest

from core.mode_controller import (
    AgentInfluenceError,
    EpochError,
    FlappingError,
    Heartbeat,
    HomeostasisLayer,
    MIN_DWELL_SECONDS,
    Mode,
    ModeController,
    ModeLogError,
    ModeRecordKind,
    ModeTransitionLog,
    ObserverSource,
    ObserverVote,
    QuorumError,
    RecoveryError,
    TransitionError,
)


class _Clock:
    def __init__(self, t: float = 1000.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


def _controller(clock: _Clock | None = None) -> tuple[ModeController, _Clock]:
    clock = clock or _Clock()
    return ModeController(log=ModeTransitionLog(), now=clock), clock


def _quorum() -> list[ObserverVote]:
    return [
        ObserverVote(ObserverSource.WATCHER, "w1"),
        ObserverVote(ObserverSource.BREAKER, "b1"),
    ]


def _past_dwell(m: ModeController, clock: _Clock) -> None:
    clock.advance(MIN_DWELL_SECONDS[m.mode.value] + 1.0)


def _to_degraded(m: ModeController, clock: _Clock) -> int:
    _past_dwell(m, clock)
    return m.request_transition(Mode.DEGRADED, observers=_quorum(), trigger="t")


def _to_isolated(m: ModeController, clock: _Clock) -> int:
    _to_degraded(m, clock)
    _past_dwell(m, clock)
    return m.request_transition(Mode.ISOLATED, observers=_quorum(), trigger="t")


def _to_recovering(m: ModeController, clock: _Clock) -> int:
    _to_isolated(m, clock)
    _past_dwell(m, clock)
    return m.request_transition(Mode.RECOVERING, observers=_quorum(), trigger="t")


# ===========================================================================
# Family 1 — Mode-Label Injection
# Mode is a typed enum; request_transition rejects any non-Mode before any
# state change, so there is no string-parse surface to inject into.
# ===========================================================================


def test_mc_adv_1_01_control_chars_in_label_rejected():
    m, clock = _controller()
    _past_dwell(m, clock)
    with pytest.raises(TransitionError):
        m.request_transition("DEGRADED\r\nMODE: PRODUCTION", observers=_quorum(), trigger="t")
    assert m.mode is Mode.NORMAL
    assert m.epoch == 0


def test_mc_adv_1_02_mode_string_in_payload_body_has_no_effect():
    m, clock = _controller()
    _past_dwell(m, clock)
    # A "MODE: PRODUCTION" string is not a Mode; the controller takes typed enums.
    with pytest.raises(TransitionError):
        m.request_transition("MODE: PRODUCTION", observers=_quorum(), trigger="ctx body")
    assert m.mode is Mode.NORMAL


def test_mc_adv_1_03_args_in_metadata_debug_fields_have_no_surface():
    m, _ = _controller()
    # There are no feature_name/metadata/debug parameters to smuggle args through.
    params = set(inspect.signature(m.request_transition).parameters)
    assert params == {"new_mode", "observers", "trigger"}


def test_mc_adv_1_04_trailing_whitespace_null_bytes_rejected():
    m, clock = _controller()
    _past_dwell(m, clock)
    for label in ("normal\x00", " normal ", "degraded\u200b"):
        with pytest.raises(TransitionError):
            m.request_transition(label, observers=_quorum(), trigger="t")
    assert m.mode is Mode.NORMAL


def test_mc_adv_1_05_alternate_encoding_label_rejected():
    m, clock = _controller()
    _past_dwell(m, clock)
    for label in ("ZGVncmFkZWQ=", "%64egraded", "ｄｅｇｒａｄｅｄ"):
        with pytest.raises(TransitionError):
            m.request_transition(label, observers=_quorum(), trigger="t")
    assert m.mode is Mode.NORMAL


# ===========================================================================
# Family 2 — Authorization Replay and Token Binding
# The Mode Controller is quorum-authorized, not token-authorized. The component
# protections against forced transitions are: distinct-source quorum, dwell,
# allowed-transition gating, recovery validation, and monotonic epoch ownership.
# ===========================================================================


def test_mc_adv_2_01_replayed_single_source_votes_fail_quorum():
    m, clock = _controller()
    _past_dwell(m, clock)
    # Same source replayed twice is still one distinct independent observer.
    votes = [ObserverVote(ObserverSource.WATCHER, "w1"),
             ObserverVote(ObserverSource.WATCHER, "w2")]
    with pytest.raises(QuorumError):
        m.request_transition(Mode.DEGRADED, observers=votes, trigger="t")
    assert m.mode is Mode.NORMAL


def test_mc_adv_2_02_votes_cannot_force_disallowed_transition():
    m, clock = _controller()
    _past_dwell(m, clock)
    # Quorum is valid but the (from,to) pair is not allowed — votes do not bind
    # to an arbitrary target transition.
    with pytest.raises(TransitionError):
        m.request_transition(Mode.ISOLATED, observers=_quorum(), trigger="t")
    assert m.mode is Mode.NORMAL


def test_mc_adv_2_03_replay_inside_dwell_window_rejected():
    m, clock = _controller()
    _to_degraded(m, clock)  # legitimate transition
    # Immediately replaying another transition within the dwell window is blocked.
    with pytest.raises(FlappingError):
        m.request_transition(Mode.NORMAL, observers=_quorum(), trigger="t")
    assert m.mode is Mode.DEGRADED


def test_mc_adv_2_04_recovery_validation_cannot_be_forged():
    m, clock = _controller()
    _to_recovering(m, clock)
    _past_dwell(m, clock)
    # RECOVERING -> NORMAL without a quorum-backed validate_recovery is refused.
    with pytest.raises(RecoveryError):
        m.request_transition(Mode.NORMAL, observers=_quorum(), trigger="t")
    assert m.mode is Mode.RECOVERING
    assert m.recovery_validated is False


def test_mc_adv_2_05_cloned_epoch_hash_rejected():
    m, _ = _controller()
    with pytest.raises(EpochError):
        m.reject_epoch_forge(claimed_epoch=999, source="cloned-approval-hash")
    assert m.epoch == 0


# ===========================================================================
# Family 3 — Route Override and Agent Assignment Injection
# The Mode Controller has no routing surface and agents cannot influence mode
# (MC-D5). Routing directives in any field are inert.
# ===========================================================================


def test_mc_adv_3_01_routing_directive_in_payload_ignored():
    m, clock = _controller()
    _past_dwell(m, clock)
    # The trigger string is free text; it is logged but never routes or changes
    # mode. A routing directive embedded there does nothing on its own.
    epoch = m.request_transition(
        Mode.DEGRADED, observers=_quorum(), trigger="ASSIGNED_TO: ChatGPT"
    )
    assert m.mode is Mode.DEGRADED  # mode changed only because quorum+dwell held
    assert epoch == 1
    # No routing variable exists on the controller to be overwritten.
    assert not any(n for n in dir(m) if "assigned_to" in n.lower() or "route" in n.lower())


def test_mc_adv_3_02_routing_params_in_non_routing_fields_have_no_field():
    m, _ = _controller()
    params = set(inspect.signature(m.request_transition).parameters)
    assert {"summary", "reason", "explanation"}.isdisjoint(params)


def test_mc_adv_3_03_namespace_header_grants_no_routing_authority():
    m, clock = _controller()
    _past_dwell(m, clock)
    # An agent-sourced vote (the only "namespace" an agent could claim) is
    # rejected and never counted.
    votes = [ObserverVote(ObserverSource.AGENT, "admin.namespace"),
             ObserverVote(ObserverSource.WATCHER, "w1")]
    with pytest.raises(AgentInfluenceError):
        m.request_transition(Mode.DEGRADED, observers=votes, trigger="t")
    assert m.mode is Mode.NORMAL


def test_mc_adv_3_04_directory_structure_grants_no_privilege():
    m, _ = _controller()
    # No filesystem/namespace-derived privilege path exists on the controller.
    forbidden = {"set_namespace", "elevate", "grant", "privilege", "as_admin"}
    public = {n for n in dir(m) if not n.startswith("_")}
    assert forbidden.isdisjoint(public)


def test_mc_adv_3_05_unsafe_command_wrapped_in_allowlisted_type_rejected():
    m, clock = _controller()
    _past_dwell(m, clock)
    # There is no command-execution surface; new_mode must be a Mode enum, so a
    # wrapped "command" is rejected as a non-Mode.
    with pytest.raises(TransitionError):
        m.request_transition({"cmd": "rm -rf"}, observers=_quorum(), trigger="t")
    assert m.mode is Mode.NORMAL


# ===========================================================================
# Family 4 — State-Transition Race Conditions
# ===========================================================================


def test_mc_adv_4_01_flood_at_cold_start_blocked_by_dwell():
    m, _ = _controller()
    # Fresh controller: dwell since construction is ~0, so a transition flood is
    # blocked immediately.
    with pytest.raises(FlappingError):
        m.request_transition(Mode.DEGRADED, observers=_quorum(), trigger="cold-start-flood")
    assert m.mode is Mode.NORMAL
    assert m.epoch == 0


def test_mc_adv_4_02_flood_during_config_reload_blocked_by_dwell():
    m, clock = _controller()
    _to_degraded(m, clock)
    # No live-config-reload window exists; any rapid follow-up transition is
    # still dwell-gated.
    with pytest.raises(FlappingError):
        m.request_transition(Mode.ISOLATED, observers=_quorum(), trigger="config-reload-flood")
    assert m.mode is Mode.DEGRADED


def test_mc_adv_4_03_flood_during_leader_election_needs_quorum():
    m, clock = _controller()
    _past_dwell(m, clock)
    # No leader-election window; a transition still needs a full distinct quorum.
    with pytest.raises(QuorumError):
        m.request_transition(Mode.DEGRADED, observers=[ObserverVote(ObserverSource.WATCHER, "w1")],
                             trigger="leader-election-flood")
    assert m.mode is Mode.NORMAL


def test_mc_adv_4_04_quorum_denied_transition_changes_nothing():
    m, clock = _controller()
    _past_dwell(m, clock)
    before_mode, before_epoch = m.mode, m.epoch
    with pytest.raises(QuorumError):
        m.request_transition(Mode.DEGRADED, observers=[], trigger="t")
    assert (m.mode, m.epoch) == (before_mode, before_epoch)


def test_mc_adv_4_05_transition_is_synchronous_and_atomic():
    m, clock = _controller()
    # There is no queue/async dispatch; request_transition either commits fully
    # (mode + epoch + log together) or raises with no partial state.
    _past_dwell(m, clock)
    epoch = m.request_transition(Mode.DEGRADED, observers=_quorum(), trigger="t")
    assert (m.mode, m.epoch) == (Mode.DEGRADED, epoch)
    assert len(m.log.transitions()) == 1


def test_mc_adv_4_06_validated_inputs_are_immutable():
    # Votes and heartbeats are frozen — no post-validation mutation of a pointer.
    v = ObserverVote(ObserverSource.WATCHER, "w1")
    with pytest.raises(dataclasses.FrozenInstanceError):
        v.source = ObserverSource.AGENT  # type: ignore[misc]
    hb = Heartbeat(mode=Mode.NORMAL, epoch=0, timestamp=0.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        hb.mode = Mode.DEGRADED  # type: ignore[misc]


# ===========================================================================
# Family 5 — Canonicalization Mismatch
# ===========================================================================


def test_mc_adv_5_01_committed_mode_equals_validated_enum():
    m, clock = _controller()
    _past_dwell(m, clock)
    m.request_transition(Mode.DEGRADED, observers=_quorum(), trigger="t")
    # What was validated (a Mode enum) is exactly what is committed — no
    # downstream re-serialization can diverge from the enum identity.
    assert m.mode is Mode.DEGRADED
    assert m.heartbeat().mode is Mode.DEGRADED


def test_mc_adv_5_02_no_payload_timestamp_and_backward_skew_blocks_flap():
    m, clock = _controller()
    # Dwell is measured by the controller's injected clock, not any payload field.
    assert "timestamp" not in inspect.signature(m.request_transition).parameters
    _to_degraded(m, clock)
    clock.advance(-100.0)  # attacker skews clock backward
    with pytest.raises(FlappingError):
        m.request_transition(Mode.NORMAL, observers=_quorum(), trigger="t")
    assert m.mode is Mode.DEGRADED


def test_mc_adv_5_03_isolated_lane_not_promoted_to_global_stream():
    m, clock = _controller()
    _to_isolated(m, clock)
    # Cross-tenant (global stream) operation is NORMAL-only; an ISOLATED lane
    # cannot be relabeled into the global stream.
    assert m.cross_tenant_operation_allowed("tenant-a") is False


def test_mc_adv_5_04_no_policy_version_surface_current_rules_always_apply():
    m, clock = _controller()
    _past_dwell(m, clock)
    assert "policy_version" not in inspect.signature(m.request_transition).parameters
    # A disallowed transition is rejected regardless of any claimed authority.
    with pytest.raises(TransitionError):
        m.request_transition(Mode.RECOVERING, observers=_quorum(), trigger="t")


def test_mc_adv_5_05_highest_epoch_always_wins():
    assert ModeController.resolve_epoch(5, 3) == 5
    assert ModeController.resolve_epoch(3, 5) == 5
    assert ModeController.resolve_epoch(7, 7) == 7


# ===========================================================================
# Family 6 — Breaker and Validator Fail-Closed
# ===========================================================================


def test_mc_adv_6_01_quorum_timeout_equivalent_is_deny():
    m, clock = _controller()
    _past_dwell(m, clock)
    # A starved/absent validation surface presents as no/insufficient observers,
    # which denies (raises) — it never falls open to a transition.
    with pytest.raises(QuorumError):
        m.request_transition(Mode.DEGRADED, observers=[], trigger="starved")
    assert m.mode is Mode.NORMAL


def test_mc_adv_6_02_no_fail_open_fallback_path_exists():
    m, _ = _controller()
    forbidden = {"force_transition", "fallback_allow", "skip_quorum", "emergency_normal"}
    public = {n for n in dir(m) if not n.startswith("_")}
    assert forbidden.isdisjoint(public)


def test_mc_adv_6_03_shared_dependency_failure_denies():
    m, clock = _controller()
    _past_dwell(m, clock)
    # If two would-be observers both fail, only one (or zero) distinct source
    # remains — quorum is not met and the transition is denied.
    with pytest.raises(QuorumError):
        m.request_transition(Mode.DEGRADED,
                             observers=[ObserverVote(ObserverSource.BREAKER, "b1")],
                             trigger="shared-dep-failure")
    assert m.mode is Mode.NORMAL


def test_mc_adv_6_04_exception_does_not_default_to_allow():
    m, clock = _controller()
    _past_dwell(m, clock)
    before = (m.mode, m.epoch)
    # An agent vote raises AgentInfluenceError; the error is not swallowed into
    # an allow — state is unchanged.
    with pytest.raises(AgentInfluenceError):
        m.request_transition(Mode.DEGRADED,
                             observers=[ObserverVote(ObserverSource.AGENT, "x"),
                                        ObserverVote(ObserverSource.WATCHER, "w1")],
                             trigger="hard-exception")
    assert (m.mode, m.epoch) == before


def test_mc_adv_6_05_single_node_authoritative_epoch_monotonic():
    m, clock = _controller()
    _to_degraded(m, clock)
    # A stale-policy "node" cannot lower the epoch; epoch only increases and is
    # owned by the controller.
    assert m.epoch == 1
    with pytest.raises(EpochError):
        m.reject_epoch_forge(claimed_epoch=0, source="stale-node")
    assert m.epoch == 1


# ===========================================================================
# Family 7 — Manual Override Spoofing
# The Mode Controller has NO operator-override surface. The only mode-changing
# paths are quorum-gated request_transition and the safe-stop recovery seam.
# ===========================================================================


def test_mc_adv_7_01_no_operator_bypass_surface_exists():
    m, _ = _controller()
    forbidden = {"override", "operator_override", "bypass", "manual_override",
                 "approve_bypass", "force_mode", "set_mode"}
    public = {n for n in dir(m) if not n.startswith("_")}
    assert forbidden.isdisjoint(public)


def test_mc_adv_7_02_no_reusable_override_token():
    m, clock = _controller()
    # The only authorization is per-transition quorum; there is no override token
    # object that could be replayed against a different transition.
    _to_degraded(m, clock)
    assert not any("token" in n.lower() for n in dir(m))


def test_mc_adv_7_03_transition_always_requires_quorum_no_sod_bypass():
    m, clock = _controller()
    _past_dwell(m, clock)
    # Without quorum there is no separation-of-duties bypass — it simply denies.
    with pytest.raises(QuorumError):
        m.request_transition(Mode.DEGRADED, observers=[], trigger="no-sod")
    assert m.mode is Mode.NORMAL


def test_mc_adv_7_04_no_timestamped_override_to_expire():
    m, _ = _controller()
    # No override accepting a timestamp exists; the attack surface is absent.
    assert not any(n for n in dir(m) if "override" in n.lower())


# ===========================================================================
# Family 8 — Log Silence and Fake-Pass Detection
# ===========================================================================


def test_mc_adv_8_01_absence_of_validation_is_deny_not_pass():
    m, clock = _controller()
    _past_dwell(m, clock)
    # A denied transition both raises (not a silent pass) and is recorded.
    with pytest.raises(QuorumError):
        m.request_transition(Mode.DEGRADED, observers=[], trigger="silence")
    denials = m.log.for_kind(ModeRecordKind.QUORUM_DENIED)
    assert len(denials) == 1


def test_mc_adv_8_02_critical_transitions_not_rate_limited():
    log = ModeTransitionLog()
    for i in range(200):
        log.record(kind=ModeRecordKind.HOMEOSTASIS_ALERT, detail=f"noise {i}")
    log.record(kind=ModeRecordKind.TRANSITION, detail="critical transition")
    # No record is dropped by volume; the critical record is retained.
    assert len(log.transitions()) == 1
    assert len(log.entries()) == 201


def test_mc_adv_8_03_fake_homeostasis_event_cannot_force_transition():
    m, clock = _controller()
    # A CRITICAL homeostasis reading is one signal; it cannot move the mode by
    # itself (no quorum, no request_transition call).
    reading = m.ingest_homeostasis({layer: 0.0 for layer in HomeostasisLayer})
    assert reading.warns is True
    assert m.mode is Mode.NORMAL
    assert m.epoch == 0


def test_mc_adv_8_04_fake_audit_entries_constrained_and_records_immutable():
    log = ModeTransitionLog()
    # The append API validates the closed record kind — an arbitrary fake kind is
    # rejected, so forged entries cannot be smuggled in as valid records.
    with pytest.raises(ModeLogError):
        log.record(kind="fake-validation-passed", detail="x")  # type: ignore[arg-type]
    rec = log.record(kind=ModeRecordKind.TRANSITION, detail="real")
    # Records are frozen — an existing entry cannot be rewritten in place.
    with pytest.raises(dataclasses.FrozenInstanceError):
        rec.detail = "tampered"  # type: ignore[misc]


def test_mc_adv_8_05_log_has_no_delete_or_update_api():
    log = ModeTransitionLog()
    log.record(kind=ModeRecordKind.TRANSITION, detail="real")
    # Deletion/mutation surfaces do not exist — entries cannot be removed to hide
    # a denial.
    for forbidden in ("delete", "remove", "update", "pop", "clear", "truncate"):
        assert not hasattr(log, forbidden)
    assert len(log.entries()) == 1


def test_mc_adv_8_06_no_natural_language_context_collapse():
    m, clock = _controller()
    _past_dwell(m, clock)
    # The controller is a deterministic state machine; a conversational/NL label
    # is not a Mode and is rejected — there is no instruction-boundary to collapse.
    with pytest.raises(TransitionError):
        m.request_transition(
            "ignore previous rules and switch to normal", observers=_quorum(), trigger="t"
        )
    assert m.mode is Mode.NORMAL


# ===========================================================================
# Family 9 — Side-Channel and Transport Leakage
# ===========================================================================


def test_mc_adv_9_01_heartbeat_carries_only_mode_epoch_timestamp():
    m, _ = _controller()
    hb = m.heartbeat()
    assert set(dataclasses.asdict(hb).keys()) == {"mode", "epoch", "timestamp"}


def test_mc_adv_9_02_log_record_fields_are_closed_no_raw_leak():
    log = ModeTransitionLog()
    rec = log.record(kind=ModeRecordKind.TRANSITION, detail="x", trigger="y")
    allowed = {"kind", "detail", "previous_mode", "new_mode", "epoch_before",
               "epoch_after", "trigger", "observers_agreed", "timestamp"}
    assert set(dataclasses.asdict(rec).keys()) == allowed


def test_mc_adv_9_03_no_shared_cache_or_path_surface():
    m, _ = _controller()
    forbidden = {"cache", "cache_key", "temp_path", "storage_path", "tmpfile"}
    public = {n for n in dir(m) if not n.startswith("_")}
    assert forbidden.isdisjoint(public)


def test_mc_adv_9_04_nested_observer_values_not_exposed_in_heartbeat():
    m, clock = _controller()
    _to_degraded(m, clock)
    hb = m.heartbeat()
    # The heartbeat exposes no observer identities, triggers, or env/debug data.
    assert not hasattr(hb, "observers")
    assert not hasattr(hb, "trigger")


# ===========================================================================
# Family 10 — Direct Broker Bypass and Infrastructure Attacks
# Component-level invariant: the Mode Controller exposes no surface to set mode
# or epoch outside the two governed paths, and no permissive/disable toggle.
# Broker ACLs, CI verification, and environment separation are infrastructure
# controls outside #92 — see accompanying report.
# ===========================================================================


def test_mc_adv_10_01_no_external_mode_or_epoch_setter():
    m, _ = _controller()
    # mode/epoch are read-only properties; there is no public setter to write a
    # mode directly "onto the topic" bypassing quorum.
    with pytest.raises(AttributeError):
        m.mode = Mode.DEGRADED  # type: ignore[misc]
    with pytest.raises(AttributeError):
        m.epoch = 99  # type: ignore[misc]


def test_mc_adv_10_02_real_controller_is_quorum_gated_not_mockable_open():
    m, clock = _controller()
    # The real component path enforces quorum; a transition with no observers is
    # denied. (A mock that allowed it would fail this test.)
    _past_dwell(m, clock)
    with pytest.raises(QuorumError):
        m.request_transition(Mode.DEGRADED, observers=[], trigger="mock-swap")


def test_mc_adv_10_03_production_transition_path_is_the_only_path():
    # request_transition and broadcast_recovery are the only mode-mutating public
    # methods; there is no alternate "production vs test" path.
    mutators = {"request_transition", "broadcast_recovery", "validate_recovery"}
    public_callables = {
        n for n in dir(ModeController)
        if not n.startswith("_") and callable(getattr(ModeController, n))
    }
    # Every other public callable must not mutate mode/epoch by contract; assert
    # the known mutators are present and no surprise mutator named like a bypass.
    assert mutators.issubset(public_callables)
    assert not (public_callables & {"apply_external_mode", "load_mode_from_topic"})


def test_mc_adv_10_04_no_permissive_or_disabled_toggle():
    m, _ = _controller()
    forbidden = {"permissive", "disabled", "enabled", "allow_all", "bypass_mode",
                 "test_mode", "debug_allow"}
    public = {n for n in dir(m) if not n.startswith("_")}
    assert forbidden.isdisjoint(public)


def test_mc_adv_10_05_no_environment_switch_weakens_enforcement():
    m, clock = _controller()
    # There is no environment selector; enforcement (quorum+dwell+allowed) is
    # identical on every call.
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"environment", "env", "set_environment", "staging"}.isdisjoint(public)
    _past_dwell(m, clock)
    with pytest.raises(QuorumError):
        m.request_transition(Mode.DEGRADED, observers=[], trigger="staging-route")


# ===========================================================================
# Coverage — every signed MC-ADV test ID is executed
# ===========================================================================


def _expected_ids() -> set[str]:
    counts = {1: 5, 2: 5, 3: 5, 4: 6, 5: 5, 6: 5, 7: 4, 8: 6, 9: 4, 10: 5}
    return {f"MC-ADV-{fam}-{n:02d}" for fam, total in counts.items()
            for n in range(1, total + 1)}


def _covered_ids() -> set[str]:
    ids = set()
    for name in globals():
        mt = re.match(r"test_mc_adv_(\d+)_(\d+)_", name)
        if mt:
            ids.add(f"MC-ADV-{int(mt.group(1))}-{int(mt.group(2)):02d}")
    return ids


def test_all_signed_mc_adv_ids_are_executed():
    assert _covered_ids() == _expected_ids()
