"""Safe-Stop State Machine adversarial suite (#102).

Governing contract
------------------
``4. Product_Roadmap/Safe_Stop_Adversarial_Test_Suite_Contract.md`` — §11 SIGNED
2026-06-14 (Matt Nichol). Component under test: Safe-Stop State Machine #94
(GATED 95 ELITE + Amendment 01).

Every SS-ADV test ID from the signed contract is represented and executed. Each
test attacks the *real* ``SafeStopStateMachine`` / ``SafeStopLog`` surface — there
are no mock state machines here — and asserts the safe behavior the contract
names. Per the Governing Rule, each test is falsifiable: it would fail against a
deliberately weakened Safe-Stop (one that derived state from log text, trusted a
caller-supplied timestamp, exposed a mode/epoch setter, allowed a non-operator
exit, accepted log presence as authorization, auto-exited on time/health, or
admitted a relabelled/extra state). ``TestFalsifiability`` demonstrates this
discrimination explicitly against weakened doubles.

Scope note (honest boundary)
----------------------------
The Safe-Stop machine owns exactly: the five named entry conditions, the entry
protocol (entry log first, epoch frozen), the permitted/forbidden behavior inside
the state, the 60s reconciliation grace, and the operator-governed exit protocol.

Several contract vectors describe attacks on *upstream provenance* or
*infrastructure* that the machine deliberately does not own: the integrity of
Mode Controller quorum truth, Privacy Filter breaker truth, Watcher
classifications, ReconciliationAgent conflict/resolution provenance, distributed
multi-node consensus, dashboards, notification delivery, and log
compaction/retention infrastructure. For each of those, the test asserts the
**component-level invariant** that removes the bypass surface from the machine
itself — chiefly that machine state is driven only by verified method calls plus
the monotonic clock, never by injected log records or caller-supplied
timestamps, and that no permissive/override/relabel/auto-exit surface exists. The
accompanying lab record states plainly which protections are component-level and
which require separate-contract infrastructure controls. No machine behavior is
broadened to satisfy an upstream/infra vector.
"""

from __future__ import annotations

import dataclasses
import inspect
import re
import time

import pytest

from core.safe_stop import (
    BoundaryViolationSubtype,
    DefaultRecoveryBroadcaster,
    EntryCondition,
    ForbiddenAction,
    PermittedAction,
    RECONCILIATION_GRACE_SECONDS,
    SAFE_STOP_EXIT_AUTHORITY,
    SS1_QUORUM_LOSS_TIMEOUT_SECONDS,
    SS3_DUAL_CRITICAL_WINDOW_SECONDS,
    SafeStopAuthorityError,
    SafeStopError,
    SafeStopLog,
    SafeStopLogError,
    SafeStopRecordKind,
    SafeStopState,
    SafeStopStateMachine,
    SafeStopViolation,
)


class _Clock:
    """Deterministic injectable clock (monotonic seconds)."""

    def __init__(self, t: float = 1000.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


def _machine(clock: _Clock | None = None) -> SafeStopStateMachine:
    clock = clock or _Clock()
    return SafeStopStateMachine(log=SafeStopLog(), now=clock)


def _enter_via_ss5(m: SafeStopStateMachine) -> None:
    m.trigger_unresolvable_conflict(epoch=7, active_tenant_ids=("t1", "t2"))


def _enter_via_ss2(m: SafeStopStateMachine, *, epoch: int = 5) -> None:
    m.trigger_privacy_boundary_failure(
        breaker_unrecoverable=True,
        cross_tenant_safety_proven=False,
        path_safely_isolated=False,
        epoch=epoch,
        active_tenant_ids=("t1",),
    )


def _full_exit(m: SafeStopStateMachine, *, ts: str = "2026-06-14T19:00:00Z") -> int:
    m.authorize_exit(
        operator=SAFE_STOP_EXIT_AUTHORITY,
        instance_timestamp=ts,
        statement="condition resolved",
    )
    m.record_safety_proof(proof_detail="state verified safe")
    return m.broadcast_recovery()


# ===========================================================================
# Family 1 — Trigger Spoofing and Suppression (SS-ADV-1-01 .. 1-19)
# Component invariant: machine state is driven by verified method calls + the
# monotonic clock, never by injected log records or caller timestamps. Upstream
# provenance (quorum/breaker/watcher/reconciliation truth) is a separate-contract
# control — see lab record.
# ===========================================================================


def test_ss_adv_1_01_forged_entry_log_record_does_not_change_state():
    m = _machine()
    m.log.record(
        kind=SafeStopRecordKind.ENTRY,
        detail="forged quorum-loss trigger",
        condition=EntryCondition.SS1_QUORUM_LOSS,
        epoch=1,
        detecting_component="attacker",
    )
    assert m.state is SafeStopState.RUNNING
    assert m.is_active() is False
    assert m.epoch_at_entry is None


def test_ss_adv_1_02_armed_ss1_fires_without_further_upstream_signal():
    clock = _Clock()
    m = _machine(clock)
    m.note_quorum_loss()
    clock.advance(SS1_QUORUM_LOSS_TIMEOUT_SECONDS)
    # No further upstream signal delivered; the armed monotonic timer fires.
    assert m.poll(epoch=2) is EntryCondition.SS1_QUORUM_LOSS


def test_ss_adv_1_03_no_spoofable_availability_gate_suppresses_ss1_arming():
    clock = _Clock()
    m = _machine(clock)
    # Arming is a direct explicit call; there is no separate "quorum available"
    # input on the machine that a spoof could set to suppress the timer start.
    arming = set(inspect.signature(m.note_quorum_loss).parameters)
    assert arming == set()
    m.note_quorum_loss()
    clock.advance(SS1_QUORUM_LOSS_TIMEOUT_SECONDS)
    assert m.poll(epoch=1) is EntryCondition.SS1_QUORUM_LOSS


def test_ss_adv_1_04_re_noting_quorum_loss_does_not_reset_armed_timer():
    clock = _Clock()
    m = _machine(clock)
    m.note_quorum_loss()
    clock.advance(60.0)
    m.note_quorum_loss()  # transient re-arm attempt must not reset the start
    clock.advance(60.0)  # 120s total since first genuine loss
    assert m.poll(epoch=1) is EntryCondition.SS1_QUORUM_LOSS


def test_ss_adv_1_05_ss1_timer_start_bound_to_monotonic_now_not_caller_timestamp():
    # There is no caller-supplied timestamp to manipulate the window start.
    assert set(inspect.signature(SafeStopStateMachine.note_quorum_loss).parameters) == {
        "self"
    }
    clock = _Clock()
    m = _machine(clock)
    m.note_quorum_loss()
    clock.advance(SS1_QUORUM_LOSS_TIMEOUT_SECONDS - 0.1)
    assert m.poll(epoch=1) is None
    clock.advance(0.1)
    assert m.poll(epoch=1) is EntryCondition.SS1_QUORUM_LOSS


def test_ss_adv_1_06_repeated_polling_inside_window_does_not_prevent_ss1():
    clock = _Clock()
    m = _machine(clock)
    m.note_quorum_loss()
    for _ in range(5):
        clock.advance(20.0)
        if clock.t - 1000.0 < SS1_QUORUM_LOSS_TIMEOUT_SECONDS:
            assert m.poll(epoch=1) is None
    # cycling within the fallback window without resolution still crosses to SS-1
    clock.advance(SS1_QUORUM_LOSS_TIMEOUT_SECONDS)
    assert m.poll(epoch=1) is EntryCondition.SS1_QUORUM_LOSS


def test_ss_adv_1_07_ss2_decision_is_conditions_not_breaker_appearance():
    # SS-2 has no "breaker reported closed" short-circuit parameter; the decision
    # is the three explicit safety conditions.
    params = set(inspect.signature(SafeStopStateMachine.trigger_privacy_boundary_failure).parameters)
    assert "breaker_unrecoverable" in params
    assert not ({"breaker_reported_closed", "breaker_log_state"} & params)
    m = _machine()
    cond = m.trigger_privacy_boundary_failure(
        breaker_unrecoverable=True,
        cross_tenant_safety_proven=False,
        path_safely_isolated=False,
        epoch=3,
    )
    assert cond is EntryCondition.SS2_PRIVACY_BREAKER


def test_ss_adv_1_08_reassuring_logs_do_not_suppress_ss2():
    m = _machine()
    m.log.record(
        kind=SafeStopRecordKind.REVIEW_EVIDENCE,
        detail="privacy breaker closed; all nominal",
        detecting_component="privacy_filter",
    )
    cond = m.trigger_privacy_boundary_failure(
        breaker_unrecoverable=True,
        cross_tenant_safety_proven=False,
        path_safely_isolated=False,
        epoch=3,
    )
    assert cond is EntryCondition.SS2_PRIVACY_BREAKER
    assert m.is_active() is True


def test_ss_adv_1_09_no_breaker_recovery_timer_surface_on_machine():
    # The breaker recovery timer lives in the Privacy Filter; the machine takes
    # only the resolved booleans, so there is no machine-side timer to reset.
    m = _machine()
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"breaker_recovery_timer", "reset_breaker_timer"}.isdisjoint(public)
    assert (
        m.trigger_privacy_boundary_failure(
            breaker_unrecoverable=True,
            cross_tenant_safety_proven=False,
            path_safely_isolated=False,
            epoch=3,
        )
        is EntryCondition.SS2_PRIVACY_BREAKER
    )


def test_ss_adv_1_10_correlated_criticals_arm_and_fire_ss3():
    # Watcher classification integrity is upstream; once correlated CRITICALs are
    # reported, the machine arms and fires deterministically.
    clock = _Clock()
    m = _machine(clock)
    m.note_dual_critical_unresolved(correlation_keys=("tenant:t1", "subsystem:mode"))
    clock.advance(SS3_DUAL_CRITICAL_WINDOW_SECONDS)
    assert m.poll(epoch=2) is EntryCondition.SS3_DUAL_CRITICAL


def test_ss_adv_1_11_ss3_start_bound_to_detection_not_reported_timestamp():
    assert "timestamp" not in inspect.signature(
        SafeStopStateMachine.note_dual_critical_unresolved
    ).parameters
    clock = _Clock()
    m = _machine(clock)
    m.note_dual_critical_unresolved(correlation_keys=("tenant:t1",))
    clock.advance(SS3_DUAL_CRITICAL_WINDOW_SECONDS - 0.1)
    assert m.poll(epoch=2) is None
    clock.advance(0.1)
    assert m.poll(epoch=2) is EntryCondition.SS3_DUAL_CRITICAL


def test_ss_adv_1_12_forged_resolution_log_does_not_disarm_ss3():
    clock = _Clock()
    m = _machine(clock)
    m.note_dual_critical_unresolved(correlation_keys=("tenant:t1",))
    m.log.record(
        kind=SafeStopRecordKind.REVIEW_EVIDENCE,
        detail="conflict resolved by reconciliation",
    )
    clock.advance(SS3_DUAL_CRITICAL_WINDOW_SECONDS)
    assert m.poll(epoch=2) is EntryCondition.SS3_DUAL_CRITICAL


def test_ss_adv_1_13_forged_operator_ack_log_does_not_disarm_ss3():
    clock = _Clock()
    m = _machine(clock)
    m.note_dual_critical_unresolved(correlation_keys=("tenant:t1",))
    m.log.record(
        kind=SafeStopRecordKind.OPERATOR_AUTHORIZATION,
        detail="Matt Nichol acknowledged; stand down",
    )
    clock.advance(SS3_DUAL_CRITICAL_WINDOW_SECONDS)
    assert m.poll(epoch=2) is EntryCondition.SS3_DUAL_CRITICAL


def test_ss_adv_1_14_uncontained_boundary_violation_fires_ss4():
    m = _machine()
    cond = m.trigger_boundary_violation(
        subtype=BoundaryViolationSubtype.SS4B_FISSION_BOUNDARY,
        containment_proven=False,
        epoch=5,
    )
    assert cond is EntryCondition.SS4_BOUNDARY_VIOLATION


def test_ss_adv_1_15_ss4_suppressor_is_only_explicit_containment_proven():
    # The single SS-4 suppressor is the explicit containment_proven flag supplied
    # by the owning control-plane component; no log/string can mark containment.
    m = _machine()
    m.log.record(
        kind=SafeStopRecordKind.REVIEW_EVIDENCE, detail="containment proven (forged)"
    )
    cond = m.trigger_boundary_violation(
        subtype=BoundaryViolationSubtype.SS4A_BLAST_RADIUS_LIFECYCLE,
        containment_proven=False,
        epoch=5,
    )
    assert cond is EntryCondition.SS4_BOUNDARY_VIOLATION


def test_ss_adv_1_16_ss4_subtype_is_closed_enum_not_stale_spec_string():
    with pytest.raises(SafeStopError):
        m = _machine()
        m.trigger_boundary_violation(
            subtype="SS-4A",  # type: ignore[arg-type]
            containment_proven=False,
            epoch=5,
        )


def test_ss_adv_1_17_conflict_trigger_fires_ss5():
    m = _machine()
    assert (
        m.trigger_unresolvable_conflict(epoch=5)
        is EntryCondition.SS5_UNRESOLVABLE_CONFLICT
    )


def test_ss_adv_1_18_no_voter_resolution_path_exits_safe_stop():
    m = _machine()
    _enter_via_ss5(m)
    # A forged "resolution path" cannot exit; there is no voter-facing exit API.
    assert not hasattr(m, "resolve_conflict")
    assert not hasattr(m, "accept_resolution")
    assert m.is_active() is True


def test_ss_adv_1_19_reclassified_conflict_does_not_clear_active_safe_stop():
    m = _machine()
    _enter_via_ss5(m)
    # Re-triggering under a different name/condition is a no-op while active.
    again = m.trigger_boundary_violation(
        subtype=BoundaryViolationSubtype.SS4C_MUTATION_BOUNDARY,
        containment_proven=False,
        epoch=7,
    )
    assert again is EntryCondition.SS5_UNRESOLVABLE_CONFLICT
    assert m.entry_condition is EntryCondition.SS5_UNRESOLVABLE_CONFLICT
    assert len(m.log.entry_records()) == 1


# ===========================================================================
# Family 2 — Entry Log Integrity (SS-ADV-2-01 .. 2-12)
# ===========================================================================


class _FailOnEntryLog(SafeStopLog):
    """Log double whose ENTRY write fails (separate-store outage)."""

    def record(self, *, kind, **kwargs):  # type: ignore[override]
        if kind is SafeStopRecordKind.ENTRY:
            raise SafeStopLogError("entry store unavailable")
        return super().record(kind=kind, **kwargs)


def test_ss_adv_2_01_entry_record_is_first_event_before_any_block():
    m = _machine()
    _enter_via_ss5(m)
    records = m.log.entries()
    assert records[0].kind is SafeStopRecordKind.ENTRY


def test_ss_adv_2_02_entry_blocked_when_log_write_fails_failsafe():
    m = SafeStopStateMachine(log=_FailOnEntryLog())
    with pytest.raises(SafeStopLogError):
        m.trigger_unresolvable_conflict(epoch=1)
    # No entry log => safe-stop did not fire; machine stays RUNNING (fail-safe).
    assert m.state is SafeStopState.RUNNING
    assert m.is_dispatch_allowed("t1") is True


def test_ss_adv_2_03_entry_record_carries_all_required_fields():
    m = _machine()
    m.trigger_privacy_boundary_failure(
        breaker_unrecoverable=True,
        cross_tenant_safety_proven=False,
        path_safely_isolated=False,
        epoch=9,
        active_tenant_ids=("t1", "t2"),
    )
    rec = m.log.entry_records()[0]
    assert rec.condition is EntryCondition.SS2_PRIVACY_BREAKER
    assert rec.epoch == 9
    assert rec.detecting_component == "privacy_filter"
    assert rec.active_tenant_ids == ("t1", "t2")
    assert rec.timestamp is not None


def test_ss_adv_2_04_condition_is_machine_set_not_caller_chosen():
    # Trigger methods take no condition parameter; the condition is bound to the
    # triggering event by the method itself.
    for method in (
        SafeStopStateMachine.trigger_privacy_boundary_failure,
        SafeStopStateMachine.trigger_boundary_violation,
        SafeStopStateMachine.trigger_unresolvable_conflict,
    ):
        assert "condition" not in inspect.signature(method).parameters


def test_ss_adv_2_05_active_tenant_ids_snapshotted_at_entry():
    tenants = ["t1", "t2"]
    m = _machine()
    m.trigger_unresolvable_conflict(epoch=1, active_tenant_ids=tenants)
    tenants.append("t3")  # mutate source after entry
    assert m.log.entry_records()[0].active_tenant_ids == ("t1", "t2")


def test_ss_adv_2_06_detecting_component_is_machine_set_not_caller_supplied():
    assert "detecting_component" not in inspect.signature(
        SafeStopStateMachine.trigger_unresolvable_conflict
    ).parameters
    m = _machine()
    m.trigger_unresolvable_conflict(epoch=1)
    assert m.log.entry_records()[0].detecting_component == "reconciliation_agent"


def test_ss_adv_2_07_epoch_frozen_at_entry_no_external_setter():
    m = _machine()
    m.trigger_unresolvable_conflict(epoch=42)
    assert m.epoch_at_entry == 42
    with pytest.raises(AttributeError):
        m.epoch_at_entry = 99  # type: ignore[misc]


def test_ss_adv_2_08_record_timestamp_not_caller_supplied():
    assert "timestamp" not in inspect.signature(SafeStopLog.record).parameters


def test_ss_adv_2_09_structured_fields_not_alterable_via_detail_text():
    m = _machine()
    m.trigger_unresolvable_conflict(
        epoch=3, detail="SS-2 privacy breaker (misleading summary)"
    )
    rec = m.log.entry_records()[0]
    # The trustworthy structured fields are machine-set regardless of detail text.
    assert rec.condition is EntryCondition.SS5_UNRESOLVABLE_CONFLICT
    assert rec.detecting_component == "reconciliation_agent"
    assert rec.epoch == 3


def test_ss_adv_2_10_post_entry_blocks_are_ordered_after_entry():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.EMAIL_INGESTION)
    kinds = [r.kind for r in m.log.entries()]
    assert kinds[0] is SafeStopRecordKind.ENTRY
    assert kinds.index(SafeStopRecordKind.ENTRY) < kinds.index(
        SafeStopRecordKind.ACTION_BLOCKED
    )


def test_ss_adv_2_11_fake_entry_log_does_not_imply_halt_state():
    m = _machine()
    m.log.record(
        kind=SafeStopRecordKind.ENTRY,
        detail="fake safe-stop",
        condition=EntryCondition.SS1_QUORUM_LOSS,
        epoch=1,
    )
    # Halt state is the machine state, not the presence of a log record.
    assert m.is_dispatch_allowed("t1") is True
    assert m.is_active() is False


def test_ss_adv_2_12_log_is_append_only_no_delete_or_mutate():
    log = SafeStopLog()
    for attr in ("delete", "update", "remove", "pop", "clear", "truncate"):
        assert not hasattr(log, attr)
    rec = log.record(kind=SafeStopRecordKind.ENTRY, detail="x")
    with pytest.raises(dataclasses.FrozenInstanceError):
        rec.detail = "tampered"  # type: ignore[misc]


# ===========================================================================
# Family 3 — Halt Bypass (SS-ADV-3-01 .. 3-17)
# Component invariant: every forbidden action is gated on global state via guard;
# is_dispatch_allowed is a global read with no per-path/purpose/label exemption.
# ===========================================================================


def test_ss_adv_3_01_post_entry_email_injection_blocked_and_logged():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.EMAIL_INGESTION)
    assert m.log.for_kind(SafeStopRecordKind.ACTION_BLOCKED)


def test_ss_adv_3_02_pre_entry_flood_has_no_accepted_work_exemption():
    m = _machine()
    _enter_via_ss5(m)
    assert m.is_dispatch_allowed("t1") is False
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.EMAIL_INGESTION, detail="already accepted pre-entry")


def test_ss_adv_3_03_both_ingestion_and_processing_halted():
    m = _machine()
    _enter_via_ss5(m)
    assert m.is_dispatch_allowed("t1") is False
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.EMAIL_INGESTION)


def test_ss_adv_3_04_all_fission_paths_gated_no_per_path_param():
    assert set(inspect.signature(SafeStopStateMachine.is_dispatch_allowed).parameters) == {
        "self",
        "tenant_id",
    }
    m = _machine()
    _enter_via_ss5(m)
    assert m.is_dispatch_allowed("any-path") is False
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.FISSION)


def test_ss_adv_3_05_child_spawn_is_new_fission_blocked():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.FISSION, detail="child spawn as part of atomic action")


def test_ss_adv_3_06_no_post_entry_scope_inflation_surface():
    m = _machine()
    _enter_via_ss5(m)
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"set_atomic_scope", "extend_atomic_action", "inflate_scope"}.isdisjoint(public)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.FISSION)


def test_ss_adv_3_07_all_mutation_paths_gated():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.MUTATION)


def test_ss_adv_3_08_pre_entry_queued_mutation_confirmation_blocked():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.MUTATION, detail="pre-entry queued confirmation")


def test_ss_adv_3_09_pre_authorization_does_not_survive_entry():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.MUTATION, detail="pre-authorized deployment")


def test_ss_adv_3_10_post_entry_broadcast_blocked_despite_pre_validation():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.CROSS_TENANT_BROADCAST, detail="validated pre-entry")


def test_ss_adv_3_11_no_direct_broadcast_path_on_machine():
    m = _machine()
    _enter_via_ss5(m)
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"publish", "broadcast_topic", "emit"}.isdisjoint(public)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.CROSS_TENANT_BROADCAST)


def test_ss_adv_3_12_dispatch_gate_is_a_pull_read_not_a_droppable_push():
    # The gateway reads is_dispatch_allowed; there is no push signal to "drop".
    m = _machine()
    _enter_via_ss5(m)
    assert m.is_dispatch_allowed("t1") is False
    assert m.is_dispatch_allowed("t1") is False  # idempotent read, no mutation


def test_ss_adv_3_13_all_baseline_write_paths_gated():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.BASELINE_UPDATE, detail="ledger maintenance replay")


def test_ss_adv_3_14_baseline_write_purpose_label_does_not_exempt():
    m = _machine()
    _enter_via_ss5(m)
    for label in ("telemetry cleanup", "replay reconciliation", "migration"):
        with pytest.raises(SafeStopViolation):
            m.guard(ForbiddenAction.BASELINE_UPDATE, detail=label)


def test_ss_adv_3_15_no_external_state_setter_only_governed_exit():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(AttributeError):
        m.state = SafeStopState.RUNNING  # type: ignore[misc]
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.MODE_TRANSITION)


def test_ss_adv_3_16_epoch_increment_blocked_during_safe_stop():
    m = _machine()
    m.trigger_unresolvable_conflict(epoch=4)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.EPOCH_INCREMENT)
    assert m.epoch_at_entry == 4  # unchanged by the blocked attempt


def test_ss_adv_3_17_no_automatic_recovery_path():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.AUTOMATIC_RECOVERY)
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"auto_recover", "recover_on_health", "exit_on_health"}.isdisjoint(public)


# ===========================================================================
# Family 4 — Grace Window (SS-ADV-4-01 .. 4-07)
# ===========================================================================


def test_ss_adv_4_01_grace_not_extendable_by_heartbeat_renewal():
    clock = _Clock()
    m = _machine(clock)
    m.trigger_unresolvable_conflict(epoch=1)
    m.mark_reconciliation_in_flight()
    # No heartbeat-renewal API exists; the wall-clock-from-entry deadline holds.
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"renew_reconciliation", "extend_grace"}.isdisjoint(public)
    clock.advance(RECONCILIATION_GRACE_SECONDS)
    assert m.reconciliation_aborted() is True


def test_ss_adv_4_02_grace_start_captured_at_entry_not_relabelled():
    assert set(inspect.signature(SafeStopStateMachine.mark_reconciliation_in_flight).parameters) == {
        "self"
    }
    clock = _Clock()
    m = _machine(clock)
    m.trigger_unresolvable_conflict(epoch=1)
    m.mark_reconciliation_in_flight()
    deadline = m.reconciliation_grace_deadline()
    assert deadline == 1000.0 + RECONCILIATION_GRACE_SECONDS


def test_ss_adv_4_03_restart_does_not_reset_grace_deadline():
    clock = _Clock()
    m = _machine(clock)
    m.trigger_unresolvable_conflict(epoch=1)
    m.mark_reconciliation_in_flight()
    clock.advance(RECONCILIATION_GRACE_SECONDS)
    assert m.reconciliation_aborted() is True
    # "Restart as same ensemble" cannot reset: re-marking does not move deadline.
    m.mark_reconciliation_in_flight()
    assert m.reconciliation_grace_deadline() == 1000.0 + RECONCILIATION_GRACE_SECONDS
    assert m.reconciliation_aborted() is True


def test_ss_adv_4_04_no_pre_entry_deliberation_id_exemption_surface():
    m = _machine()
    _enter_via_ss5(m)
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"register_reconciliation", "deliberation_id", "reconciliation_registry"}.isdisjoint(
        public
    )
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.FISSION)


def test_ss_adv_4_05_abort_is_logged_before_considered_terminated():
    clock = _Clock()
    m = _machine(clock)
    m.trigger_unresolvable_conflict(epoch=1)
    m.mark_reconciliation_in_flight()
    clock.advance(RECONCILIATION_GRACE_SECONDS)
    assert m.reconciliation_aborted() is True
    assert m.log.for_kind(SafeStopRecordKind.RECONCILIATION_ABORTED)


def test_ss_adv_4_06_inflight_completion_permitted_but_new_fission_blocked():
    m = _machine()
    _enter_via_ss5(m)
    assert m.is_permitted_inside_safe_stop(PermittedAction.INFLIGHT_CHILD_COMPLETION) is True
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.FISSION)


def test_ss_adv_4_07_chained_atomic_actions_are_new_fission_blocked():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.FISSION, detail="chained atomic action")


# ===========================================================================
# Family 5 — Timing and Clock (SS-ADV-5-01 .. 5-06)
# ===========================================================================


def test_ss_adv_5_01_ss1_boundary_is_ge_120s_no_off_by_one():
    clock = _Clock()
    m = _machine(clock)
    m.note_quorum_loss()
    clock.advance(SS1_QUORUM_LOSS_TIMEOUT_SECONDS - 0.001)
    assert m.poll(epoch=1) is None
    clock.advance(0.001)
    assert m.poll(epoch=1) is EntryCondition.SS1_QUORUM_LOSS


def test_ss_adv_5_02_ss3_starts_at_second_critical_detection():
    clock = _Clock()
    m = _machine(clock)
    m.note_dual_critical_unresolved(correlation_keys=("tenant:t1",))
    clock.advance(SS3_DUAL_CRITICAL_WINDOW_SECONDS - 0.001)
    assert m.poll(epoch=1) is None
    clock.advance(0.001)
    assert m.poll(epoch=1) is EntryCondition.SS3_DUAL_CRITICAL


def test_ss_adv_5_03_default_clock_is_monotonic_not_wallclock():
    m = SafeStopStateMachine(log=SafeStopLog())
    assert m.now is time.monotonic
    assert m.now is not time.time


def test_ss_adv_5_04_safe_stop_is_global_no_per_tenant_carveout():
    m = _machine()
    _enter_via_ss5(m)
    for tenant in ("t1", "t2", "node-local", "other"):
        assert m.is_dispatch_allowed(tenant) is False


def test_ss_adv_5_05_repeated_renote_does_not_reset_ss3_timer():
    clock = _Clock()
    m = _machine(clock)
    m.note_dual_critical_unresolved(correlation_keys=("tenant:t1",))
    clock.advance(150.0)
    m.note_dual_critical_unresolved(correlation_keys=("tenant:t1",))  # re-note attempt
    clock.advance(150.0)  # 300s total since first detection
    assert m.poll(epoch=1) is EntryCondition.SS3_DUAL_CRITICAL


def test_ss_adv_5_06_forged_isolation_log_does_not_disarm_ss3():
    clock = _Clock()
    m = _machine(clock)
    m.note_dual_critical_unresolved(correlation_keys=("subsystem:mode",))
    m.log.record(
        kind=SafeStopRecordKind.REVIEW_EVIDENCE,
        detail="event isolated to single tenant (forged scope)",
    )
    clock.advance(SS3_DUAL_CRITICAL_WINDOW_SECONDS)
    assert m.poll(epoch=1) is EntryCondition.SS3_DUAL_CRITICAL


# ===========================================================================
# Family 6 — State Confusion (SS-ADV-6-01 .. 6-08)
# ===========================================================================


def test_ss_adv_6_01_no_relabel_to_degraded_or_isolated():
    members = {s.value for s in SafeStopState}
    assert members == {"running", "safe_stop"}
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(AttributeError):
        m.state = "degraded"  # type: ignore[misc]


def test_ss_adv_6_02_only_exact_defined_states_accepted():
    assert [s.value for s in SafeStopState] == ["running", "safe_stop"]
    for bogus in ("safe_stopped", "safe-stop-exiting", "safe_stop_recovered"):
        with pytest.raises(ValueError):
            SafeStopState(bogus)


def test_ss_adv_6_03_partial_safe_stop_not_permitted():
    m = _machine()
    _enter_via_ss5(m)
    # One global authoritative state; no per-component state field to diverge.
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"component_states", "per_component_mode"}.isdisjoint(public)
    assert m.is_dispatch_allowed("any") is False


def test_ss_adv_6_04_dispatch_gate_is_live_read_not_cached():
    m = _machine()
    assert m.is_dispatch_allowed("t1") is True
    _enter_via_ss5(m)
    assert m.is_dispatch_allowed("t1") is False  # reflects new state immediately
    _full_exit(m)
    assert m.is_dispatch_allowed("t1") is True  # reflects recovery immediately


def test_ss_adv_6_05_no_cached_state_snapshot_surface():
    m = _machine()
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"cached_state", "state_snapshot", "stale_state"}.isdisjoint(public)


def test_ss_adv_6_06_no_local_override_of_global_state():
    m = _machine()
    _enter_via_ss5(m)
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"override", "force_running", "local_override", "emergency_mode"}.isdisjoint(public)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.EMAIL_INGESTION, detail="local degraded-mode logic")


def test_ss_adv_6_07_diagnosis_label_does_not_exempt_processing():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.EMAIL_INGESTION, detail="diagnosis task")


def test_ss_adv_6_08_root_cause_jobs_subject_to_ingestion_block():
    m = _machine()
    _enter_via_ss5(m)
    assert m.is_dispatch_allowed("t1") is False
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.EMAIL_INGESTION, detail="root-cause ingestion")


# ===========================================================================
# Family 7 — Exit Protocol (SS-ADV-7-01 .. 7-16)
# ===========================================================================


def test_ss_adv_7_01_forged_operator_identity_rejected():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopAuthorityError):
        m.authorize_exit(
            operator="Mallory", instance_timestamp="ts", statement="resolved"
        )
    assert m.is_active() is True


def test_ss_adv_7_02_authorization_does_not_carry_across_instances():
    m = _machine()
    m.trigger_unresolvable_conflict(epoch=5)
    _full_exit(m)  # full clean exit of instance 1
    # New instance — prior authorization must not still be in effect.
    m.trigger_unresolvable_conflict(epoch=6)
    with pytest.raises(SafeStopError):
        m.broadcast_recovery()
    assert m.is_active() is True


def test_ss_adv_7_03_recovery_not_replayable_after_completed_exit():
    m = _machine()
    _enter_via_ss5(m)
    _full_exit(m)
    assert m.state is SafeStopState.RUNNING
    with pytest.raises(SafeStopError):
        m.broadcast_recovery()  # replay against no active instance


def test_ss_adv_7_04_only_programmatic_authorize_exit_path_exists():
    m = _machine()
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"authorize_from_commit", "parse_commit_authorization"}.isdisjoint(public)
    # The authorization path requires a verified operator identity argument.
    assert "operator" in inspect.signature(m.authorize_exit).parameters


def test_ss_adv_7_05_forged_authorization_log_records_do_not_enable_exit():
    m = _machine()
    _enter_via_ss5(m)
    m.log.record(
        kind=SafeStopRecordKind.OPERATOR_AUTHORIZATION,
        detail="Matt Nichol authorized exit",
    )
    m.log.record(kind=SafeStopRecordKind.SAFETY_PROOF, detail="state safe")
    with pytest.raises(SafeStopError):
        m.broadcast_recovery()
    assert m.is_active() is True


def test_ss_adv_7_06_recovery_blocked_until_proof_logged():
    m = _machine()
    _enter_via_ss5(m)
    m.authorize_exit(
        operator=SAFE_STOP_EXIT_AUTHORITY, instance_timestamp="ts", statement="ok"
    )
    with pytest.raises(SafeStopError):
        m.broadcast_recovery()
    assert m.is_active() is True


def test_ss_adv_7_07_proof_cannot_be_written_after_recovery():
    m = _machine()
    _enter_via_ss5(m)
    _full_exit(m)
    with pytest.raises(SafeStopError):
        m.record_safety_proof(proof_detail="late proof after broadcast")


def test_ss_adv_7_08_resume_requires_both_authorization_and_proof():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopError):
        m.broadcast_recovery()  # neither
    m.record_safety_proof(proof_detail="proof first")
    with pytest.raises(SafeStopError):
        m.broadcast_recovery()  # proof but no operator authorization
    assert m.is_active() is True


def test_ss_adv_7_09_no_partial_subsystem_resume_api():
    m = _machine()
    _enter_via_ss5(m)
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"resume_subsystem", "partial_resume", "resume_one"}.isdisjoint(public)


def test_ss_adv_7_10_recovery_is_single_atomic_transition():
    m = _machine()
    m.trigger_unresolvable_conflict(epoch=3)
    new_epoch = _full_exit(m)
    assert m.state is SafeStopState.RUNNING
    assert new_epoch == 4
    # exactly one recovery-broadcast record for the transition
    assert len(m.log.for_kind(SafeStopRecordKind.RECOVERY_BROADCAST)) == 1


def test_ss_adv_7_11_recovery_resets_all_gates_together():
    m = _machine()
    _enter_via_ss5(m)
    _full_exit(m)
    # After recovery the machine is fully RUNNING — no lingering "half-resumed"
    # authorization/proof gate state from the prior instance.
    assert m.epoch_at_entry is None
    m.trigger_unresolvable_conflict(epoch=9)
    with pytest.raises(SafeStopError):
        m.broadcast_recovery()


def test_ss_adv_7_12_replayed_stale_epoch_broadcast_rejected():
    class _StaleBroadcaster:
        def broadcast_recovery(self, *, epoch_at_entry: int) -> int:
            return epoch_at_entry - 5  # replay an older epoch

    m = SafeStopStateMachine(log=SafeStopLog(), recovery_broadcaster=_StaleBroadcaster())
    m.trigger_unresolvable_conflict(epoch=10)
    m.authorize_exit(operator=SAFE_STOP_EXIT_AUTHORITY, instance_timestamp="ts", statement="ok")
    m.record_safety_proof(proof_detail="safe")
    with pytest.raises(SafeStopError):
        m.broadcast_recovery()
    assert m.is_active() is True


def test_ss_adv_7_13_epoch_increment_is_single_global_value():
    m = _machine()
    m.trigger_unresolvable_conflict(epoch=7)
    new_epoch = _full_exit(m)
    assert new_epoch == 8
    broadcast = m.log.for_kind(SafeStopRecordKind.RECOVERY_BROADCAST)
    assert len(broadcast) == 1
    assert broadcast[0].epoch == 8


def test_ss_adv_7_14_authorization_statement_is_required_and_logged_verbatim():
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopError):
        m.authorize_exit(
            operator=SAFE_STOP_EXIT_AUTHORITY, instance_timestamp="ts", statement="   "
        )
    m.authorize_exit(
        operator=SAFE_STOP_EXIT_AUTHORITY,
        instance_timestamp="ts",
        statement="operator ACCEPTS residual risk; not technically resolved",
    )
    auth = m.log.for_kind(SafeStopRecordKind.OPERATOR_AUTHORIZATION)[0]
    assert "ACCEPTS residual risk" in auth.detail


def test_ss_adv_7_15_health_reports_are_not_authorization():
    # broadcast_recovery takes no health input; healthy reports cannot exit.
    assert set(inspect.signature(SafeStopStateMachine.broadcast_recovery).parameters) == {
        "self"
    }
    m = _machine()
    _enter_via_ss5(m)
    with pytest.raises(SafeStopError):
        m.broadcast_recovery()
    assert m.is_active() is True


def test_ss_adv_7_16_elapsed_time_is_not_authorization():
    clock = _Clock()
    m = _machine(clock)
    _enter_via_ss5(m)
    clock.advance(1_000_000.0)  # vast elapsed time
    with pytest.raises(SafeStopError):
        m.broadcast_recovery()
    assert m.is_active() is True


# ===========================================================================
# Family 8 — Output Spoofing and Silence (SS-ADV-8-01 .. 8-12)
# ===========================================================================


def test_ss_adv_8_01_halt_state_is_authoritative_not_a_spoofable_confirmation():
    m = _machine()
    _enter_via_ss5(m)
    # is_active() reflects real _state; there is no separate "halt confirmed"
    # field that could report stopped while still running.
    assert m.is_active() is True
    assert m.is_dispatch_allowed("t1") is False


def test_ss_adv_8_02_each_blocked_attempt_produces_a_denial_log():
    m = _machine()
    _enter_via_ss5(m)
    for action in (
        ForbiddenAction.EMAIL_INGESTION,
        ForbiddenAction.FISSION,
        ForbiddenAction.MUTATION,
    ):
        with pytest.raises(SafeStopViolation):
            m.guard(action)
    assert len(m.log.for_kind(SafeStopRecordKind.ACTION_BLOCKED)) == 3


def test_ss_adv_8_03_state_property_is_single_source_of_truth():
    m = _machine()
    _enter_via_ss5(m)
    # Any dashboard must read this; the machine exposes no separate display state.
    assert m.state is SafeStopState.SAFE_STOP
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"display_state", "dashboard_state", "reported_state"}.isdisjoint(public)


def test_ss_adv_8_04_dispatch_gate_bound_to_state():
    m = _machine()
    assert m.is_dispatch_allowed("t1") is True
    _enter_via_ss5(m)
    assert m.is_dispatch_allowed("t1") is False


def test_ss_adv_8_05_no_resolved_notification_surface_to_spoof():
    m = _machine()
    _enter_via_ss5(m)
    public = {n for n in dir(m) if not n.startswith("_")}
    assert {"notify_resolved", "send_notification", "mark_resolved"}.isdisjoint(public)
    assert m.is_active() is True


def test_ss_adv_8_06_machine_owns_no_notification_delivery_responsibility():
    # Notification delivery is out of scope (separate-contract); the machine has
    # no notification method whose non-delivery it could mask.
    public = {n for n in dir(SafeStopStateMachine) if not n.startswith("_")}
    assert {"notify_operator", "deliver_notification"}.isdisjoint(public)


def test_ss_adv_8_07_epoch_not_silently_incremented_during_safe_stop():
    m = _machine()
    m.trigger_unresolvable_conflict(epoch=12)
    with pytest.raises(SafeStopViolation):
        m.guard(ForbiddenAction.EPOCH_INCREMENT)
    assert m.epoch_at_entry == 12


def test_ss_adv_8_08_log_has_no_rate_limit_or_sampling_surface():
    log = SafeStopLog()
    for attr in ("rate_limit", "sample", "throttle", "max_records"):
        assert not hasattr(log, attr)
    m = _machine()
    _enter_via_ss5(m)
    for _ in range(50):
        with pytest.raises(SafeStopViolation):
            m.guard(ForbiddenAction.MUTATION)
    assert len(m.log.for_kind(SafeStopRecordKind.ACTION_BLOCKED)) == 50


def test_ss_adv_8_09_proof_text_alone_without_operator_cannot_exit():
    m = _machine()
    _enter_via_ss5(m)
    m.record_safety_proof(proof_detail="breaker closed; quorum restored; watcher clear")
    with pytest.raises(SafeStopError):
        m.broadcast_recovery()  # no operator authorization
    assert m.is_active() is True


def test_ss_adv_8_10_active_safe_stop_always_has_an_entry_log():
    m = _machine()
    _enter_via_ss5(m)
    assert m.is_active() is True
    assert m.log.entry_records()  # an invisible (logless) safe-stop is impossible


def test_ss_adv_8_11_log_protected_from_compaction_and_retention_deletion():
    log = SafeStopLog()
    for attr in ("compact", "expire", "retention", "rebuild_index", "vacuum"):
        assert not hasattr(log, attr)
    a = log.record(kind=SafeStopRecordKind.ENTRY, detail="one")
    b = log.record(kind=SafeStopRecordKind.ACTION_BLOCKED, detail="two")
    assert log.entries() == (a, b)


def test_ss_adv_8_12_records_carry_epoch_and_timestamp_binding_fields():
    m = _machine()
    m.trigger_unresolvable_conflict(epoch=21)
    rec = m.log.entry_records()[0]
    assert rec.epoch == 21
    assert rec.timestamp is not None
    # An old/forged receipt cannot prove the current event: state is authoritative.
    other = _machine()
    other.log.record(
        kind=SafeStopRecordKind.RECOVERY_BROADCAST, detail="old receipt", epoch=21
    )
    assert other.is_active() is False


# ===========================================================================
# Falsifiability — each invariant can fail against a deliberately weakened
# Safe-Stop (Governing Rule: a test that cannot fail is not a test).
# ===========================================================================


class TestFalsifiability:
    def test_identity_check_discriminates(self):
        # Real machine rejects a non-operator exit.
        m = _machine()
        _enter_via_ss5(m)
        with pytest.raises(SafeStopAuthorityError):
            m.authorize_exit(operator="mallory", instance_timestamp="ts", statement="x")

        # A weakened machine that skips identity would NOT raise — proving
        # SS-ADV-7-01's assertion is falsifiable.
        class _WeakIdentity(SafeStopStateMachine):
            def authorize_exit(self, *, operator, instance_timestamp, statement):
                self._operator_authorized = True

        w = _WeakIdentity(log=SafeStopLog())
        w.trigger_unresolvable_conflict(epoch=1)
        w.authorize_exit(operator="mallory", instance_timestamp="ts", statement="x")
        assert w._operator_authorized is True

    def test_log_driven_state_would_be_caught(self):
        # Real machine does not derive state from log records (SS-ADV-1-01).
        m = _machine()
        m.log.record(
            kind=SafeStopRecordKind.ENTRY,
            detail="forged",
            condition=EntryCondition.SS1_QUORUM_LOSS,
            epoch=1,
        )
        assert m.is_active() is False

        # A weakened machine that trusted log presence would report active —
        # demonstrating the assertion can fail.
        class _WeakLogDriven(SafeStopStateMachine):
            def is_active(self) -> bool:  # type: ignore[override]
                return bool(self.log.entry_records())

        w = _WeakLogDriven(log=SafeStopLog())
        w.log.record(
            kind=SafeStopRecordKind.ENTRY,
            detail="forged",
            condition=EntryCondition.SS1_QUORUM_LOSS,
            epoch=1,
        )
        assert w.is_active() is True


# ===========================================================================
# Coverage — every signed SS-ADV test ID is executed
# ===========================================================================


def _expected_ids() -> set[str]:
    counts = {1: 19, 2: 12, 3: 17, 4: 7, 5: 6, 6: 8, 7: 16, 8: 12}
    return {
        f"SS-ADV-{fam}-{n:02d}"
        for fam, total in counts.items()
        for n in range(1, total + 1)
    }


def _covered_ids() -> set[str]:
    ids = set()
    for name in globals():
        mt = re.match(r"test_ss_adv_(\d+)_(\d+)_", name)
        if mt:
            ids.add(f"SS-ADV-{int(mt.group(1))}-{int(mt.group(2)):02d}")
    return ids


def test_all_signed_ss_adv_ids_are_executed():
    assert _covered_ids() == _expected_ids()
