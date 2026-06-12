"""Phase 5 — Mutation Engine ensemble tests (Layer 5, scoreboard row #88).

Three test classes per component per AGENTS.md §5 and
``Phase5_MutationEngine_Contract.md`` §11:
  Class 1 — expected pass
  Class 2 — adversarial / break-it
  Class 3 — known-gap xfail (documented, with completion path)

Components under test (six):
  1. ThreeShotConfirmationTracker  (P5-D2)
  2. ValidationGate                (P5-D3, P5-D10)
  3. HumanSignOffGate              (P5-D4)
  4. RollbackMechanism             (P5-D5)
  5. ZeroDayCapture                (P5-D11)
  6. MutationEngineEnsemble        (P5-D9, §3.3.1 pipeline) + MutationAuditTrail
"""

from __future__ import annotations

from pathlib import Path

import pytest

from core.mutation import (
    AnomalyCandidate,
    Confirmation,
    ConfirmationError,
    HumanSignOffGate,
    MutationAuditTrail,
    MutationProposal,
    MutationStage,
    MutationEngineEnsemble,
    RollbackError,
    RollbackMechanism,
    SignOffError,
    ThreeShotConfirmationTracker,
    ValidationError,
    ValidationGate,
    ZeroDayCapture,
    ZeroDayCaptureError,
    ZeroDayReferral,
    ZERO_DAY_ROUTING_TARGET,
)
from core.operator_state.role_separation import (
    OPERATOR_IDENTITY,
    RoleSeparationController,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _clean_stream(rate: float = 0.01):
    """Benign stream that holds a flat FP rate every cycle."""

    return lambda candidate_id, cycle: rate


def _spiking_stream(base: float, spike: float, spike_cycle: int = 2):
    """Benign stream that spikes the FP rate on one cycle."""

    return lambda candidate_id, cycle: spike if cycle == spike_cycle else base


def _outlier_candidate(candidate_id: str = "cand_1", **overrides) -> AnomalyCandidate:
    params = dict(
        candidate_id=candidate_id,
        tenant_scope="sandbox",
        anomaly_summary="novel vendor-pivot fraud signature",
        observed_signal=10.0,
        baseline_mean=0.0,
        baseline_stddev=1.0,
        baseline_fp_rate=0.01,
        prior_state={"threshold": 0.5},
    )
    params.update(overrides)
    return AnomalyCandidate(**params)


def _three_independent(candidate_id: str = "cand_1") -> list[Confirmation]:
    return [
        Confirmation(candidate_id, "email_1", "tenant_a", "ev1"),
        Confirmation(candidate_id, "email_2", "tenant_b", "ev2"),
        Confirmation(candidate_id, "email_3", "tenant_c", "ev3"),
    ]


@pytest.fixture
def operator_controller() -> RoleSeparationController:
    return RoleSeparationController()


@pytest.fixture
def ensemble(tmp_path: Path, operator_controller: RoleSeparationController):
    trail = MutationAuditTrail(tmp_path / "mutation_audit.jsonl")
    sign_off = HumanSignOffGate(controller=operator_controller)
    return MutationEngineEnsemble(audit_trail=trail, sign_off_gate=sign_off)


# ===========================================================================
# Component 1 — ThreeShotConfirmationTracker (P5-D2)
# ===========================================================================


class TestThreeShotTrackerExpectedPass:
    def test_three_distinct_email_and_tenant_become_eligible(self):
        tracker = ThreeShotConfirmationTracker()
        counts = [tracker.record_confirmation(c) for c in _three_independent()]
        assert counts == [1, 2, 3]
        assert tracker.is_validation_eligible("cand_1") is True

    def test_eligibility_only_at_third_independent_hit(self):
        tracker = ThreeShotConfirmationTracker()
        c = _three_independent()
        tracker.record_confirmation(c[0])
        tracker.record_confirmation(c[1])
        assert tracker.is_validation_eligible("cand_1") is False
        tracker.record_confirmation(c[2])
        assert tracker.is_validation_eligible("cand_1") is True

    def test_evidence_chain_lists_advancing_confirmations(self):
        tracker = ThreeShotConfirmationTracker()
        for conf in _three_independent():
            tracker.record_confirmation(conf)
        chain = tracker.evidence_chain("cand_1")
        assert chain == [
            "email_1@tenant_a:ev1",
            "email_2@tenant_b:ev2",
            "email_3@tenant_c:ev3",
        ]


class TestThreeShotTrackerAdversarial:
    def test_repeated_email_id_does_not_advance(self):
        tracker = ThreeShotConfirmationTracker()
        tracker.record_confirmation(Confirmation("c", "email_1", "tenant_a"))
        # Same email_id, new tenant — must NOT advance (P5-D2).
        count = tracker.record_confirmation(Confirmation("c", "email_1", "tenant_b"))
        assert count == 1

    def test_same_tenant_replayed_never_reaches_three(self):
        tracker = ThreeShotConfirmationTracker()
        # One noisy tenant firing three distinct emails — one incident must not
        # mutate the swarm.
        for i in range(3):
            tracker.record_confirmation(
                Confirmation("c", f"email_{i}", "tenant_noisy")
            )
        assert tracker.independent_count("c") == 1
        assert tracker.is_validation_eligible("c") is False

    def test_missing_email_or_tenant_raises(self):
        tracker = ThreeShotConfirmationTracker()
        with pytest.raises(ConfirmationError):
            tracker.record_confirmation(Confirmation("c", "", "tenant_a"))
        with pytest.raises(ConfirmationError):
            tracker.record_confirmation(Confirmation("c", "email_1", ""))


class TestThreeShotTrackerKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Confirmation tracker is in-memory only — does not survive a process "
            "restart. Completion path: back with an append-only ledger surface in "
            "a signed persistence amendment."
        ),
        strict=True,
    )
    def test_xfail_confirmation_state_persists_across_restart(self):
        raise AssertionError("not implemented — persistence amendment required")


# ===========================================================================
# Component 2 — ValidationGate (P5-D3, P5-D10)
# ===========================================================================


class TestValidationGateExpectedPass:
    def test_clean_benign_stream_passes(self):
        gate = ValidationGate()
        result = gate.validate(
            "cand_1", baseline_fp_rate=0.01, benign_stream=_clean_stream(0.01)
        )
        assert result.passed is True
        assert result.max_delta == pytest.approx(0.0)
        assert result.cycles == gate.cycles

    def test_improvement_passes(self):
        gate = ValidationGate()
        result = gate.validate(
            "cand_1", baseline_fp_rate=0.05, benign_stream=_clean_stream(0.02)
        )
        assert result.passed is True
        assert result.max_delta < 0


class TestValidationGateAdversarial:
    def test_single_cycle_spike_rejects(self):
        gate = ValidationGate()
        result = gate.validate(
            "cand_1",
            baseline_fp_rate=0.01,
            benign_stream=_spiking_stream(0.01, 0.5),
        )
        assert result.passed is False
        assert "REJECTED" in result.reason

    def test_out_of_range_rate_raises(self):
        gate = ValidationGate()
        with pytest.raises(ValidationError):
            gate.validate(
                "cand_1",
                baseline_fp_rate=0.01,
                benign_stream=lambda c, i: 1.5,
            )

    def test_non_numeric_rate_raises(self):
        gate = ValidationGate()
        with pytest.raises(ValidationError):
            gate.validate(
                "cand_1",
                baseline_fp_rate=0.01,
                benign_stream=lambda c, i: "low",
            )

    def test_zero_cycles_rejected_at_construction(self):
        with pytest.raises(ValidationError):
            ValidationGate(cycles=0)


class TestValidationGateKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Benign stream is caller-supplied — the gate cannot detect an "
            "adversarially curated 'benign' stream that hides real FP risk. "
            "Completion path: signed benign-corpus provenance amendment."
        ),
        strict=True,
    )
    def test_xfail_benign_stream_provenance_enforced(self):
        raise AssertionError("not implemented — benign-corpus provenance amendment")


# ===========================================================================
# Component 3 — HumanSignOffGate (P5-D4)
# ===========================================================================


class TestSignOffGateExpectedPass:
    def test_operator_sign_off_records(self, operator_controller):
        gate = HumanSignOffGate(controller=operator_controller)
        proposal = MutationProposal("cand_1", "sandbox", "clean")
        record = gate.sign_off(proposal, actor_id=OPERATOR_IDENTITY)
        assert record.signer_id == OPERATOR_IDENTITY
        assert gate.is_signed_off("cand_1") is True
        assert gate.require_sign_off("cand_1").signer_id == OPERATOR_IDENTITY


class TestSignOffGateAdversarial:
    def test_non_operator_actor_denied(self, operator_controller):
        gate = HumanSignOffGate(controller=operator_controller)
        proposal = MutationProposal("cand_1", "sandbox", "clean")
        with pytest.raises(SignOffError):
            gate.sign_off(proposal, actor_id="tenant_admin_42")

    def test_empty_actor_denied(self, operator_controller):
        gate = HumanSignOffGate(controller=operator_controller)
        proposal = MutationProposal("cand_1", "sandbox", "clean")
        with pytest.raises(SignOffError):
            gate.sign_off(proposal, actor_id="")

    def test_require_sign_off_without_signature_raises(self, operator_controller):
        gate = HumanSignOffGate(controller=operator_controller)
        with pytest.raises(SignOffError):
            gate.require_sign_off("never_signed")


class TestSignOffGateKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Sign-off trust is an in-process identity string, not a cryptographic "
            "signature. Completion path: wire DEPLOY_MUTATION sign-off to the "
            "Ed25519 signing surface in a signed amendment."
        ),
        strict=True,
    )
    def test_xfail_cryptographic_sign_off(self):
        raise AssertionError("not implemented — cryptographic sign-off amendment")


# ===========================================================================
# Component 4 — RollbackMechanism (P5-D5)
# ===========================================================================


class TestRollbackExpectedPass:
    def test_revert_restores_prior_state(self):
        rb = RollbackMechanism()
        rb.record_deployment(
            candidate_id="c",
            tenant_scope="sandbox",
            prior_state={"threshold": 0.5},
            baseline_fp_rate=0.01,
        )
        outcome = rb.revert("c")
        assert outcome.restored_state == {"threshold": 0.5}
        assert outcome.automatic is False
        assert rb.is_active("c") is False


class TestRollbackAdversarial:
    def test_fp_spike_auto_reverts(self):
        rb = RollbackMechanism()
        rb.record_deployment(
            candidate_id="c",
            tenant_scope="sandbox",
            prior_state={"threshold": 0.5},
            baseline_fp_rate=0.01,
        )
        outcome = rb.observe_false_positive_rate("c", observed_fp_rate=0.5)
        assert outcome is not None
        assert outcome.automatic is True
        assert rb.is_active("c") is False

    def test_prior_state_is_defensively_copied(self):
        rb = RollbackMechanism()
        mutable = {"threshold": 0.5}
        rb.record_deployment(
            candidate_id="c",
            tenant_scope="sandbox",
            prior_state=mutable,
            baseline_fp_rate=0.01,
        )
        mutable["threshold"] = 9.9  # tamper after recording
        outcome = rb.revert("c")
        assert outcome.restored_state == {"threshold": 0.5}

    def test_revert_unknown_candidate_raises(self):
        rb = RollbackMechanism()
        with pytest.raises(RollbackError):
            rb.revert("never_deployed")

    def test_small_fp_drift_does_not_trigger(self):
        rb = RollbackMechanism()
        rb.record_deployment(
            candidate_id="c",
            tenant_scope="sandbox",
            prior_state={},
            baseline_fp_rate=0.01,
        )
        assert rb.observe_false_positive_rate("c", observed_fp_rate=0.02) is None
        assert rb.is_active("c") is True


class TestRollbackKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Rollback restores the recorded prior-state dict but does not re-sign "
            "the restored policy through the signing surface. Completion path: "
            "rollback-resigning amendment."
        ),
        strict=True,
    )
    def test_xfail_rollback_resigns_restored_policy(self):
        raise AssertionError("not implemented — rollback re-signing amendment")


# ===========================================================================
# Component 5 — ZeroDayCapture (P5-D11)
# ===========================================================================


class TestZeroDayCaptureExpectedPass:
    def test_referral_routes_to_matt_only(self):
        zd = ZeroDayCapture()
        proposal = zd.capture(
            ZeroDayReferral("zd_1", "email_x", "tenant_q", "novel packer")
        )
        assert proposal.routed_to == ZERO_DAY_ROUTING_TARGET == OPERATOR_IDENTITY
        assert proposal.novelty_summary == "novel packer"
        assert len(proposal.referrals) == 1


class TestZeroDayCaptureAdversarial:
    def test_routes_to_matt_regardless_of_tenant(self):
        zd = ZeroDayCapture()
        proposal = zd.capture(
            ZeroDayReferral("zd_1", "email_x", "hostile_tenant", "novel")
        )
        # No tenant operator can redirect a zero-day proposal to themselves.
        assert proposal.routed_to == OPERATOR_IDENTITY

    def test_missing_fields_raise(self):
        zd = ZeroDayCapture()
        with pytest.raises(ZeroDayCaptureError):
            zd.capture(ZeroDayReferral("zd_1", "", "tenant_q", "x"))
        with pytest.raises(ZeroDayCaptureError):
            zd.capture(ZeroDayReferral("zd_1", "email_x", "", "x"))

    def test_proposal_for_unknown_raises(self):
        zd = ZeroDayCapture()
        with pytest.raises(ZeroDayCaptureError):
            zd.proposal_for("never_captured")


class TestZeroDayCaptureKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Zero-day proposals are packaged for Matt only but not yet pushed to a "
            "live notification channel. Completion path: notification-routing "
            "amendment after onboarding surface exists."
        ),
        strict=True,
    )
    def test_xfail_zero_day_notification_delivery(self):
        raise AssertionError("not implemented — notification-routing amendment")


# ===========================================================================
# Component 6 — MutationEngineEnsemble (P5-D9, §3.3.1) + MutationAuditTrail
# ===========================================================================


class TestEnsembleExpectedPass:
    def test_full_pipeline_then_deploy(self, ensemble):
        candidate = _outlier_candidate()
        for conf in _three_independent():
            ensemble.record_confirmation(conf)
        result = ensemble.run_pipeline(candidate, benign_stream=_clean_stream(0.01))
        assert result.stamped is True
        assert result.rejected is False
        assert result.stage_reached is MutationStage.VALIDATION_PASSED

        ensemble.sign_off_gate.sign_off(
            MutationProposal(candidate.candidate_id, "sandbox", "clean"),
            actor_id=OPERATOR_IDENTITY,
        )
        ensemble.deploy(candidate, actor_id=OPERATOR_IDENTITY)

        stages = [e.stage for e in ensemble.audit_trail.read_for_candidate("cand_1")]
        assert MutationStage.ANOMALY_FLAGGED in stages
        assert MutationStage.THREE_SHOT_CONFIRMED in stages
        assert MutationStage.VALIDATION_PASSED in stages
        assert MutationStage.DEPLOYED in stages

    def test_audit_trail_records_signer_on_deploy(self, ensemble):
        candidate = _outlier_candidate()
        for conf in _three_independent():
            ensemble.record_confirmation(conf)
        ensemble.run_pipeline(candidate, benign_stream=_clean_stream(0.01))
        ensemble.sign_off_gate.sign_off(
            MutationProposal(candidate.candidate_id, "sandbox", "clean"),
            actor_id=OPERATOR_IDENTITY,
        )
        ensemble.deploy(candidate, actor_id=OPERATOR_IDENTITY)
        deployed = [
            e
            for e in ensemble.audit_trail.read_for_candidate("cand_1")
            if e.stage is MutationStage.DEPLOYED
        ]
        assert deployed and deployed[0].signer == OPERATOR_IDENTITY


class TestEnsembleAdversarial:
    def test_within_variation_filtered_at_stage_two(self, ensemble):
        candidate = _outlier_candidate(observed_signal=1.0)  # 1σ — not an outlier
        for conf in _three_independent():
            ensemble.record_confirmation(conf)
        result = ensemble.run_pipeline(candidate, benign_stream=_clean_stream(0.01))
        assert result.stamped is False
        assert result.stage_reached is MutationStage.BASELINE_COMPARED

    def test_insufficient_confirmations_not_stamped(self, ensemble):
        candidate = _outlier_candidate()
        ensemble.record_confirmation(Confirmation("cand_1", "e1", "t1"))
        result = ensemble.run_pipeline(candidate, benign_stream=_clean_stream(0.01))
        assert result.stamped is False
        assert "awaiting confirmation" in result.reason

    def test_validation_failure_rejects(self, ensemble):
        candidate = _outlier_candidate()
        for conf in _three_independent():
            ensemble.record_confirmation(conf)
        result = ensemble.run_pipeline(
            candidate, benign_stream=_spiking_stream(0.01, 0.5)
        )
        assert result.rejected is True
        assert result.stage_reached is MutationStage.REJECTED

    def test_deploy_without_sign_off_refused(self, ensemble):
        candidate = _outlier_candidate()
        for conf in _three_independent():
            ensemble.record_confirmation(conf)
        ensemble.run_pipeline(candidate, benign_stream=_clean_stream(0.01))
        with pytest.raises(SignOffError):
            ensemble.deploy(candidate, actor_id=OPERATOR_IDENTITY)

    def test_post_deploy_spike_auto_rolls_back(self, ensemble):
        candidate = _outlier_candidate()
        for conf in _three_independent():
            ensemble.record_confirmation(conf)
        ensemble.run_pipeline(candidate, benign_stream=_clean_stream(0.01))
        ensemble.sign_off_gate.sign_off(
            MutationProposal(candidate.candidate_id, "sandbox", "clean"),
            actor_id=OPERATOR_IDENTITY,
        )
        ensemble.deploy(candidate, actor_id=OPERATOR_IDENTITY)
        outcome = ensemble.observe_post_deploy_fp(candidate, observed_fp_rate=0.9)
        assert outcome is not None and outcome.automatic is True
        rolled = [
            e
            for e in ensemble.audit_trail.read_for_candidate("cand_1")
            if e.stage is MutationStage.ROLLED_BACK
        ]
        assert rolled

    def test_audit_trail_is_append_only(self, ensemble):
        # Structural append-only: no update/delete surface (P5-D6).
        assert not hasattr(ensemble.audit_trail, "update")
        assert not hasattr(ensemble.audit_trail, "delete")


class TestEnsembleKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Pipeline stages 6-7 (conservative threshold-lock cycle accounting and "
            "the amendment path) are governance disciplines enforced by signed "
            "amendment, not yet enforced in code. Completion path: post-launch "
            "threshold-locking amendment from real-tenant data (P5-D10)."
        ),
        strict=True,
    )
    def test_xfail_threshold_lock_and_amendment_path_enforced_in_code(self):
        raise AssertionError("not implemented — threshold-lock amendment (P5-D10)")
