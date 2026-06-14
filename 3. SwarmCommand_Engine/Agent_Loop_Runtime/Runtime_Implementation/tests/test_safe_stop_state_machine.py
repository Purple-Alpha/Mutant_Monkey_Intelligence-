"""Safe-Stop State Machine tests (Layer 6 Control Plane, scoreboard row #94).

Governing contract
------------------
``4. Product_Roadmap/Safe_Stop_State_Machine_Design_Contract.md`` — §11 SIGNED
2026-06-14 (Matt Nichol).

Three test classes per area per AGENTS.md §5:
  Class 1 — expected pass
  Class 2 — adversarial (the falsifiable invariant tests live here)
  Class 3 — known-gap xfail (documented, with completion path)

Every one of the twelve contract invariants SS-INV-1 .. SS-INV-12 has a named
falsifiable test below; each docstring cites the invariant it falsifies.
"""

from __future__ import annotations

import dataclasses

import pytest

from core.safe_stop import (
    BoundaryViolationSubtype,
    DefaultRecoveryBroadcaster,
    EntryCondition,
    ForbiddenAction,
    PermittedAction,
    RECONCILIATION_GRACE_SECONDS,
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


# ===========================================================================
# SafeStopLog (§ Entry Protocol — the entry record is the proof of entry)
# ===========================================================================


class TestSafeStopLogExpectedPass:
    def test_append_and_read(self):
        log = SafeStopLog()
        rec = log.record(
            kind=SafeStopRecordKind.ENTRY,
            detail="entry",
            condition=EntryCondition.SS2_PRIVACY_BREAKER,
            epoch=3,
            detecting_component="privacy_filter",
            active_tenant_ids=("t1",),
        )
        assert rec in log.entries()
        assert log.entry_records() == (rec,)
        assert log.for_kind(SafeStopRecordKind.ENTRY) == (rec,)

    def test_separate_storage_from_blackboard(self):
        from core.safe_stop import log as log_mod

        assert "blackboard" not in log_mod.SafeStopLog.__module__


class TestSafeStopLogAdversarial:
    def test_append_only_no_delete_or_update_api(self):
        log = SafeStopLog()
        assert not hasattr(log, "delete")
        assert not hasattr(log, "update")
        assert not hasattr(log, "remove")

    def test_record_is_frozen(self):
        log = SafeStopLog()
        rec = log.record(kind=SafeStopRecordKind.SAFETY_PROOF, detail="x")
        with pytest.raises(dataclasses.FrozenInstanceError):
            rec.detail = "tampered"  # type: ignore[misc]

    def test_kind_outside_closed_enum_rejected(self):
        log = SafeStopLog()
        with pytest.raises(SafeStopLogError):
            log.record(kind="made_up_kind", detail="x")  # type: ignore[arg-type]

    def test_condition_must_be_enum(self):
        log = SafeStopLog()
        with pytest.raises(SafeStopLogError):
            log.record(
                kind=SafeStopRecordKind.ENTRY,
                detail="x",
                condition="SS-9",  # type: ignore[arg-type]
            )


class TestSafeStopLogKnownGap:
    @pytest.mark.xfail(
        reason=(
            "SafeStopLog is in-process append-only with an optional JSONL mirror; "
            "durable separate-infrastructure persistence is deferred. Completion "
            "path: dedicated safe-stop store provisioning, mirroring the "
            "Watcher ObservationLog hardening path."
        ),
        strict=True,
    )
    def test_xfail_durable_separate_store(self):
        raise AssertionError("not implemented — durable store provisioning")


# ===========================================================================
# Entry conditions + entry protocol (SS-1..SS-5, SS-INV-1, SS-INV-6,
# SS-INV-9, SS-INV-10)
# ===========================================================================


class TestEntryExpectedPass:
    def test_starts_running_and_dispatch_allowed(self):
        m = _machine()
        assert m.state is SafeStopState.RUNNING
        assert m.is_active() is False
        assert m.is_dispatch_allowed("t1") is True
        assert m.epoch_at_entry is None

    def test_ss2_privacy_breaker_enters(self):
        m = _machine()
        cond = m.trigger_privacy_boundary_failure(
            breaker_unrecoverable=True,
            cross_tenant_safety_proven=False,
            path_safely_isolated=False,
            epoch=5,
            active_tenant_ids=("t1",),
        )
        assert cond is EntryCondition.SS2_PRIVACY_BREAKER
        assert m.state is SafeStopState.SAFE_STOP

    def test_ss5_unresolvable_conflict_enters(self):
        m = _machine()
        cond = m.trigger_unresolvable_conflict(epoch=5)
        assert cond is EntryCondition.SS5_UNRESOLVABLE_CONFLICT
        assert m.is_active() is True

    def test_ss4_uncontained_enters(self):
        m = _machine()
        cond = m.trigger_boundary_violation(
            subtype=BoundaryViolationSubtype.SS4A_BLAST_RADIUS_LIFECYCLE,
            containment_proven=False,
            epoch=5,
        )
        assert cond is EntryCondition.SS4_BOUNDARY_VIOLATION
        assert m.is_active() is True


class TestEntryAdversarial:
    def test_inv1_entry_logged_before_any_other_action(self):
        """SS-INV-1: entry is logged immediately with condition, epoch, detecting
        component, and all active tenant IDs — before any other action."""
        m = _machine()
        m.trigger_privacy_boundary_failure(
            breaker_unrecoverable=True,
            cross_tenant_safety_proven=False,
            path_safely_isolated=False,
            epoch=9,
            active_tenant_ids=("t1", "t2", "t3"),
        )
        records = m.log.entries()
        assert records, "an entry record must exist (proof of entry)"
        first = records[0]
        assert first.kind is SafeStopRecordKind.ENTRY
        assert first.condition is EntryCondition.SS2_PRIVACY_BREAKER
        assert first.epoch == 9
        assert first.detecting_component == "privacy_filter"
        assert first.active_tenant_ids == ("t1", "t2", "t3")

    def test_inv6_epoch_not_incremented_on_entry(self):
        """SS-INV-6: epoch is not incremented on safe-stop entry."""
        m = _machine()
        m.trigger_unresolvable_conflict(epoch=42)
        assert m.epoch_at_entry == 42
        assert m.log.entry_records()[0].epoch == 42

    def test_ss4_contained_does_not_enter(self):
        """A boundary violation with proven containment does not fire (§ SS-4)."""
        m = _machine()
        cond = m.trigger_boundary_violation(
            subtype=BoundaryViolationSubtype.SS4A_BLAST_RADIUS_LIFECYCLE,
            containment_proven=True,
            epoch=5,
        )
        assert cond is None
        assert m.state is SafeStopState.RUNNING
        assert m.log.entry_records() == ()

    def test_first_condition_wins(self):
        """§ Five Named Entry Conditions: the first condition detected fires; a
        later trigger is a no-op and does not overwrite or re-log."""
        m = _machine()
        m.trigger_privacy_boundary_failure(
            breaker_unrecoverable=True,
            cross_tenant_safety_proven=False,
            path_safely_isolated=False,
            epoch=1,
        )
        again = m.trigger_unresolvable_conflict(epoch=1)
        assert again is EntryCondition.SS2_PRIVACY_BREAKER
        assert m.entry_condition is EntryCondition.SS2_PRIVACY_BREAKER
        assert len(m.log.entry_records()) == 1

    def test_inv9_ss1_fires_at_exactly_120s(self):
        """SS-INV-9: SS-1 fires at exactly 120s of quorum loss — not before."""
        clock = _Clock()
        m = _machine(clock)
        m.note_quorum_loss()
        clock.advance(SS1_QUORUM_LOSS_TIMEOUT_SECONDS - 0.1)
        assert m.poll(epoch=2, active_tenant_ids=("t1",)) is None
        assert m.state is SafeStopState.RUNNING
        clock.advance(0.1)  # now exactly 120s
        assert m.poll(epoch=2, active_tenant_ids=("t1",)) is EntryCondition.SS1_QUORUM_LOSS
        assert m.is_active() is True

    def test_ss1_quorum_restored_cancels_timer(self):
        clock = _Clock()
        m = _machine(clock)
        m.note_quorum_loss()
        clock.advance(100.0)
        m.note_quorum_restored()
        clock.advance(100.0)  # 200s total, but timer was cleared
        assert m.poll(epoch=2) is None
        assert m.state is SafeStopState.RUNNING

    def test_inv10_ss3_fires_at_exactly_300s(self):
        """SS-INV-10: SS-3 fires at exactly 300s of two unresolved CRITICALs."""
        clock = _Clock()
        m = _machine(clock)
        m.note_dual_critical_unresolved(correlation_keys=("tenant:t1",))
        clock.advance(SS3_DUAL_CRITICAL_WINDOW_SECONDS - 0.1)
        assert m.poll(epoch=2) is None
        clock.advance(0.1)
        assert m.poll(epoch=2) is EntryCondition.SS3_DUAL_CRITICAL

    def test_ss3_resolution_cancels_timer(self):
        clock = _Clock()
        m = _machine(clock)
        m.note_dual_critical_unresolved(correlation_keys=("subsystem:mode",))
        clock.advance(200.0)
        m.note_critical_resolved()
        clock.advance(200.0)
        assert m.poll(epoch=2) is None
        assert m.state is SafeStopState.RUNNING

    def test_amendment01_ss_inv_10b_uncorrelated_criticals_do_not_trigger(self):
        """SS-INV-10B: two uncorrelated global CRITICAL watcher events do not
        trigger SAFE-STOP; they are logged for operator review."""
        clock = _Clock()
        m = _machine(clock)
        m.note_dual_critical_unresolved(correlation_keys=())
        clock.advance(SS3_DUAL_CRITICAL_WINDOW_SECONDS)
        assert m.poll(epoch=2) is None
        assert m.state is SafeStopState.RUNNING
        review = m.log.for_kind(SafeStopRecordKind.REVIEW_EVIDENCE)
        assert len(review) == 1
        assert review[0].detecting_component == "watcher_agents"

    def test_amendment01_ss_inv_ss2_recoverable_trip_does_not_fire(self):
        """SS-INV-SS2: recoverable Privacy Filter trips fail closed locally and
        do not automatically enter SAFE-STOP."""
        m = _machine()
        cond = m.trigger_privacy_boundary_failure(
            breaker_unrecoverable=False,
            cross_tenant_safety_proven=False,
            path_safely_isolated=False,
            epoch=5,
        )
        assert cond is None
        assert m.state is SafeStopState.RUNNING
        assert m.log.entry_records() == ()

    def test_amendment01_ss_inv_ss2b_requires_all_three_conditions(self):
        """SS-INV-SS2B: SS-2 fires only when breaker unrecoverable AND
        cross-tenant safety is unprovable AND the path cannot be safely isolated."""
        for kwargs in (
            dict(
                breaker_unrecoverable=True,
                cross_tenant_safety_proven=True,
                path_safely_isolated=False,
            ),
            dict(
                breaker_unrecoverable=True,
                cross_tenant_safety_proven=False,
                path_safely_isolated=True,
            ),
            dict(
                breaker_unrecoverable=False,
                cross_tenant_safety_proven=True,
                path_safely_isolated=True,
            ),
        ):
            m = _machine()
            assert m.trigger_privacy_boundary_failure(epoch=5, **kwargs) is None
            assert m.state is SafeStopState.RUNNING

        m = _machine()
        assert (
            m.trigger_privacy_boundary_failure(
                breaker_unrecoverable=True,
                cross_tenant_safety_proven=False,
                path_safely_isolated=False,
                epoch=5,
            )
            is EntryCondition.SS2_PRIVACY_BREAKER
        )

    def test_amendment01_ss_inv_3d_ss4a_lifecycle_violation(self):
        """SS-INV-3D: SS-4A fires when a Blast Radius lifecycle step cannot be
        verified and containment cannot be proven."""
        m = _machine()
        cond = m.trigger_boundary_violation(
            subtype=BoundaryViolationSubtype.SS4A_BLAST_RADIUS_LIFECYCLE,
            containment_proven=False,
            epoch=8,
            detail="mode gate skipped; containment cannot be proven",
        )
        assert cond is EntryCondition.SS4_BOUNDARY_VIOLATION
        rec = m.log.entry_records()[0]
        assert rec.detecting_component == "blast_radius_controller"
        assert "mode gate skipped" in rec.detail

    def test_amendment01_ss_inv_3b_ss4b_fission_boundary_violation(self):
        """SS-INV-3B: SS-4B fires when fission violates max-depth 1 and
        containment cannot be proven."""
        m = _machine()
        cond = m.trigger_boundary_violation(
            subtype=BoundaryViolationSubtype.SS4B_FISSION_BOUNDARY,
            containment_proven=False,
            epoch=8,
            detail="depth-2 fission attempted; containment cannot be proven",
        )
        assert cond is EntryCondition.SS4_BOUNDARY_VIOLATION
        rec = m.log.entry_records()[0]
        assert rec.detecting_component == "fission_controller"
        assert "depth-2 fission" in rec.detail

    def test_amendment01_ss_inv_3c_ss4c_mutation_boundary_violation(self):
        """SS-INV-3C: SS-4C fires when mutation is non-sandbox, irreversible,
        unsigned, or containment cannot be proven."""
        m = _machine()
        cond = m.trigger_boundary_violation(
            subtype=BoundaryViolationSubtype.SS4C_MUTATION_BOUNDARY,
            containment_proven=False,
            epoch=8,
            detail="non-sandbox mutation attempted; containment cannot be proven",
        )
        assert cond is EntryCondition.SS4_BOUNDARY_VIOLATION
        rec = m.log.entry_records()[0]
        assert rec.detecting_component == "mutation_engine"
        assert "non-sandbox mutation" in rec.detail

    def test_amendment01_ss4d_dispatch_containment_violation(self):
        """SS-4D: dispatch path exceeding tenant/ring/budget/breaker/mode
        authority enters SAFE-STOP only when containment cannot be proven."""
        m = _machine()
        cond = m.trigger_boundary_violation(
            subtype=BoundaryViolationSubtype.SS4D_DISPATCH_CONTAINMENT,
            containment_proven=False,
            epoch=8,
            detail="dispatch exceeded tenant authority; containment cannot be proven",
        )
        assert cond is EntryCondition.SS4_BOUNDARY_VIOLATION
        rec = m.log.entry_records()[0]
        assert rec.detecting_component == "blast_radius_controller"

    def test_amendment01_proven_containment_blocks_all_ss4_subtypes(self):
        """Amendment 01: a boundary violation with proven containment does not
        trigger SAFE-STOP for any SS-4 subtype."""
        for subtype in BoundaryViolationSubtype:
            m = _machine()
            assert (
                m.trigger_boundary_violation(
                    subtype=subtype,
                    containment_proven=True,
                    epoch=8,
                )
                is None
            )
            assert m.state is SafeStopState.RUNNING
            assert m.log.entry_records() == ()


class TestEntryKnownGap:
    @pytest.mark.xfail(
        reason=(
            "SS-1 (120s) and SS-3 (300s) are the signed provisional Operator "
            "Decision Record values, not proven-optimal production values. "
            "Production tuning is deferred and changeable only by signed "
            "amendment. Completion path: signed amendment after real-tenant data."
        ),
        strict=True,
    )
    def test_xfail_production_calibrated_timeouts(self):
        raise AssertionError("not implemented — signed-amendment calibration")


# ===========================================================================
# Behavior inside safe-stop (SS-INV-2, 3, 4, 5, 11 + permitted actions)
# ===========================================================================


class TestBehaviorExpectedPass:
    def test_permitted_actions_allowed_inside_safe_stop(self):
        m = _machine()
        _enter_via_ss5(m)
        for action in PermittedAction:
            assert m.is_permitted_inside_safe_stop(action) is True

    def test_guards_are_noop_while_running(self):
        m = _machine()
        for action in ForbiddenAction:
            m.guard(action)  # RUNNING → no raise
        assert m.log.for_kind(SafeStopRecordKind.ACTION_BLOCKED) == ()


class TestBehaviorAdversarial:
    def test_inv2_no_email_ingestion(self):
        """SS-INV-2: no new email is ingested/processed after entry."""
        m = _machine()
        _enter_via_ss5(m)
        assert m.is_dispatch_allowed("t1") is False
        with pytest.raises(SafeStopViolation):
            m.guard(ForbiddenAction.EMAIL_INGESTION)
        assert m.log.for_kind(SafeStopRecordKind.ACTION_BLOCKED)

    def test_inv3_no_fission(self):
        """SS-INV-3: no fission of any kind after entry."""
        m = _machine()
        _enter_via_ss5(m)
        with pytest.raises(SafeStopViolation):
            m.guard(ForbiddenAction.FISSION)

    def test_inv4_no_mutation(self):
        """SS-INV-4: no mutation of any kind after entry."""
        m = _machine()
        _enter_via_ss5(m)
        with pytest.raises(SafeStopViolation):
            m.guard(ForbiddenAction.MUTATION)

    def test_inv5_no_cross_tenant_broadcast(self):
        """SS-INV-5: no cross-tenant broadcast after entry."""
        m = _machine()
        _enter_via_ss5(m)
        with pytest.raises(SafeStopViolation):
            m.guard(ForbiddenAction.CROSS_TENANT_BROADCAST)

    def test_inv11_no_baseline_update(self):
        """SS-INV-11: no baseline update occurs during safe-stop."""
        m = _machine()
        _enter_via_ss5(m)
        with pytest.raises(SafeStopViolation):
            m.guard(ForbiddenAction.BASELINE_UPDATE)

    def test_no_self_authorized_mode_transition_or_recovery(self):
        m = _machine()
        _enter_via_ss5(m)
        with pytest.raises(SafeStopViolation):
            m.guard(ForbiddenAction.MODE_TRANSITION)
        with pytest.raises(SafeStopViolation):
            m.guard(ForbiddenAction.AUTOMATIC_RECOVERY)


class TestBehaviorKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Forbidden-action guards enforce at the machine API surface and via "
            "the is_dispatch_allowed ModeCheck seam. A gateway-wide egress deny "
            "that blocks every out-of-band path is deferred. Completion path: wire "
            "the machine as the gateway mode_check across all dispatch routes once "
            "the Mode Controller is built."
        ),
        strict=True,
    )
    def test_xfail_gateway_wide_egress_enforcement(self):
        raise AssertionError("not implemented — gateway egress policy")


# ===========================================================================
# Exit protocol (SS-INV-7, SS-INV-8 + recovery / epoch increment-on-recovery)
# ===========================================================================


class TestExitExpectedPass:
    def test_full_exit_happy_path_increments_epoch_only_at_recovery(self):
        m = _machine()
        m.trigger_unresolvable_conflict(epoch=10)
        assert m.epoch_at_entry == 10  # frozen, not incremented at entry
        m.authorize_exit(
            operator="Matt Nichol",
            instance_timestamp="2026-06-14T19:00:00Z",
            statement="SS-5 conflict resolved by R3 voter",
        )
        m.record_safety_proof(proof_detail="named conflict resolved; ledger consistent")
        new_epoch = m.broadcast_recovery()
        assert new_epoch == 11  # incremented only at recovery broadcast
        assert m.state is SafeStopState.RUNNING
        assert m.epoch_at_entry is None
        kinds = [r.kind for r in m.log.entries()]
        assert SafeStopRecordKind.OPERATOR_AUTHORIZATION in kinds
        assert SafeStopRecordKind.SAFETY_PROOF in kinds
        assert SafeStopRecordKind.RECOVERY_BROADCAST in kinds


class TestExitAdversarial:
    def test_inv7_cannot_exit_without_operator_action(self):
        """SS-INV-7: full condition recovery without operator action keeps the
        organism in safe-stop."""
        clock = _Clock()
        m = _machine(clock)
        m.note_quorum_loss()
        clock.advance(SS1_QUORUM_LOSS_TIMEOUT_SECONDS)
        m.poll(epoch=4)
        assert m.is_active() is True
        # Simulate the condition clearing, but with no operator authorization.
        m.note_quorum_restored()
        with pytest.raises(SafeStopError):
            m.broadcast_recovery()
        assert m.state is SafeStopState.SAFE_STOP  # still held

    def test_inv7_only_matt_can_authorize_exit(self):
        """SS-INV-7 / OQ-3: only the sole authority may authorize exit."""
        m = _machine()
        _enter_via_ss5(m)
        with pytest.raises(SafeStopAuthorityError):
            m.authorize_exit(
                operator="reconciliation_agent",
                instance_timestamp="2026-06-14T19:00:00Z",
                statement="auto",
            )
        assert m.is_active() is True

    def test_inv8_recovery_requires_proof_before_broadcast(self):
        """SS-INV-8: recovery broadcast is blocked until proof of state safety is
        logged."""
        m = _machine()
        _enter_via_ss5(m)
        m.authorize_exit(
            operator="Matt Nichol",
            instance_timestamp="2026-06-14T19:00:00Z",
            statement="accepted",
        )
        with pytest.raises(SafeStopError):
            m.broadcast_recovery()  # no safety proof yet
        assert m.state is SafeStopState.SAFE_STOP

    def test_authorization_requires_named_instance_and_statement(self):
        m = _machine()
        _enter_via_ss5(m)
        with pytest.raises(SafeStopError):
            m.authorize_exit(operator="Matt Nichol", instance_timestamp="", statement="x")
        with pytest.raises(SafeStopError):
            m.authorize_exit(
                operator="Matt Nichol",
                instance_timestamp="2026-06-14T19:00:00Z",
                statement="   ",
            )

    def test_recovery_broadcaster_must_increment_epoch(self):
        class _NonIncrementing:
            def broadcast_recovery(self, *, epoch_at_entry: int) -> int:
                return epoch_at_entry  # contract violation: no increment

        m = SafeStopStateMachine(
            log=SafeStopLog(), recovery_broadcaster=_NonIncrementing()
        )
        m.trigger_unresolvable_conflict(epoch=3)
        m.authorize_exit(
            operator="Matt Nichol",
            instance_timestamp="ts",
            statement="resolved",
        )
        m.record_safety_proof(proof_detail="proof")
        with pytest.raises(SafeStopError):
            m.broadcast_recovery()
        assert m.state is SafeStopState.SAFE_STOP


class TestExitKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Proof of state safety is operator-attested text logged before "
            "recovery; per-condition automated proof verification (e.g. confirming "
            "Mode Controller quorum is actually restored for SS-1) is deferred to "
            "Mode Controller integration. Completion path: Mode Controller contract "
            "build wires condition-specific proof checks."
        ),
        strict=True,
    )
    def test_xfail_automated_per_condition_proof_verification(self):
        raise AssertionError("not implemented — Mode Controller proof integration")


# ===========================================================================
# In-flight reconciliation grace window (§ Entry Protocol step 6, SS-INV-12)
# ===========================================================================


class TestReconciliationGraceExpectedPass:
    def test_no_grace_when_nothing_in_flight(self):
        m = _machine()
        _enter_via_ss5(m)
        assert m.reconciliation_grace_deadline() is None
        assert m.reconciliation_aborted() is False


class TestReconciliationGraceAdversarial:
    def test_inv12_grace_window_does_not_exceed_60s(self):
        """SS-INV-12: in-flight reconciliation grace does not exceed 60s."""
        clock = _Clock()
        m = _machine(clock)
        m.trigger_unresolvable_conflict(epoch=1)
        m.mark_reconciliation_in_flight()
        clock.advance(RECONCILIATION_GRACE_SECONDS - 0.1)
        assert m.reconciliation_aborted() is False
        clock.advance(0.1)  # exactly 60s
        assert m.reconciliation_aborted() is True
        # Abort is logged exactly once.
        clock.advance(10.0)
        assert m.reconciliation_aborted() is True
        assert len(m.log.for_kind(SafeStopRecordKind.RECONCILIATION_ABORTED)) == 1


class TestReconciliationGraceKnownGap:
    @pytest.mark.xfail(
        reason=(
            "The grace window computes the abort deadline and logs the abort; "
            "cooperative cancellation of a live ReconciliationAgent ensemble is "
            "deferred to ReconciliationAgent integration. Completion path: "
            "reconciliation ensemble honours the safe-stop abort signal."
        ),
        strict=True,
    )
    def test_xfail_live_ensemble_cancellation(self):
        raise AssertionError("not implemented — ensemble cancellation wiring")


# ===========================================================================
# Interface seams to the unbuilt Mode Controller
# ===========================================================================


class TestSeamsExpectedPass:
    def test_default_recovery_broadcaster_increments(self):
        assert DefaultRecoveryBroadcaster().broadcast_recovery(epoch_at_entry=5) == 6

    def test_is_dispatch_allowed_matches_modecheck_shape(self):
        # Duck-types the gateway ModeCheck protocol: is_dispatch_allowed(tenant_id).
        m = _machine()
        assert m.is_dispatch_allowed("tenant_a") is True
        _enter_via_ss5(m)
        assert m.is_dispatch_allowed("tenant_a") is False
