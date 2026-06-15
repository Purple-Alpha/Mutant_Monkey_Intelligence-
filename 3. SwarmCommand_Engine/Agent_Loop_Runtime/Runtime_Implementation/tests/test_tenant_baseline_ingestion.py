"""Tenant Baseline Ingestion tests (Gap 5, scoreboard row #97)."""

from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta, timezone

import pytest

from core.tenant_baseline_ingestion import (
    Approval,
    ActorType,
    BaselineAuditLog,
    BaselineStatus,
    CandidateStatus,
    ConfidenceInputs,
    DownstreamArtifact,
    EvidencePayload,
    PromotionDecision,
    PromotionRequest,
    RiskTier,
    RollbackOutcome,
    RollbackRejected,
    SnapshotCreationError,
    TenantBaselineIngestionPipeline,
    TenantBaselineStore,
    calculate_confidence_score,
)


TENANT = "tenant-a"


def _now() -> datetime:
    return datetime(2026, 6, 14, 12, 0, tzinfo=timezone.utc)


def _perfect_inputs(**overrides) -> ConfidenceInputs:
    values = {
        "evidence_completeness": 1.0,
        "observation_stability": 1.0,
        "historical_consistency": 1.0,
        "sample_size_weight": 1.0,
        "recency_weight": 1.0,
        "normalization_quality": 1.0,
        "cross_source_agreement": 1.0,
        "independent_lineage_factor": 1.0,
        "source_reliability": 1.0,
        "operator_policy_factor": 1.0,
        "anomaly_penalty": 0.0,
    }
    values.update(overrides)
    return ConfidenceInputs(**values)


def _evidence(
    *,
    risk_tier: RiskTier = RiskTier.LOW,
    baseline_key: str = "sender.known_good_domain",
    inputs: ConfidenceInputs | None = None,
    lineage_independence: bool = True,
    telemetry_lineage: tuple[str, ...] = ("mx-log-a", "mailbox-audit-b"),
    evidence_id: str = "ev-1",
) -> EvidencePayload:
    confidence_inputs = inputs or _perfect_inputs()
    return EvidencePayload(
        schema_version="gap5-v1",
        evidence_id=evidence_id,
        tenant_id=TENANT,
        observed_at=_now(),
        received_at=_now() + timedelta(seconds=1),
        source_component="sender_history_agent",
        source_instance_id="agent-instance-a",
        evidence_type="sender_signal",
        entity_type="sender",
        entity_id="sender@example.com",
        candidate_baseline_key=baseline_key,
        observed_state="observed",
        normalized_state="normalized",
        confidence_inputs=confidence_inputs,
        confidence_score=calculate_confidence_score(confidence_inputs, risk_tier),
        risk_tier=risk_tier,
        telemetry_signature="sha256:abc",
        retention_policy="90d",
        telemetry_lineage=telemetry_lineage,
        lineage_independence=lineage_independence,
    )


def _pipeline(*, fail_snapshot: bool = False):
    audit = BaselineAuditLog()
    store = TenantBaselineStore(fail_snapshot=fail_snapshot)
    return TenantBaselineIngestionPipeline(store=store, audit_log=audit), store, audit


def _request(evidence: EvidencePayload, **kwargs) -> PromotionRequest:
    return PromotionRequest(
        workflow_id=kwargs.pop("workflow_id", "wf-gap5"),
        requester_actor_id=kwargs.pop("requester_actor_id", "requester-a"),
        implementer_actor_id=kwargs.pop("implementer_actor_id", "implementer-a"),
        evidence=evidence,
        approvals=kwargs.pop("approvals", ()),
        manual_lineage_review=kwargs.pop("manual_lineage_review", False),
    )


def test_low_risk_strict_candidate_promotes_with_snapshot_and_audit():
    pipeline, store, audit = _pipeline()

    result = pipeline.submit(_request(_evidence()))

    assert result.decision is PromotionDecision.PROMOTED
    assert result.baseline_version is not None
    assert result.baseline_version.version == 1
    assert store.current(TENANT, "sender.known_good_domain").state == "normalized"
    assert audit.validate_chain()
    record = audit.entries()[-1]
    assert record.old_baseline_version is None
    assert record.new_baseline_version == 1
    assert record.evidence_ids == ("ev-1",)
    assert record.actor_id == "tenant_baseline_ingestion"


def test_tbi_inv_1_high_repetition_low_reliability_cannot_promote():
    pipeline, _, _ = _pipeline()
    inputs = _perfect_inputs(
        source_reliability=0.20,
        sample_size_weight=1.0,
    )

    result = pipeline.submit(_request(_evidence(inputs=inputs)))

    assert result.decision is PromotionDecision.REJECTED
    assert "hard_gate_failed:source_reliability" in result.reason_codes
    assert result.baseline_version is None


def test_tbi_inv_2_shared_upstream_source_forces_non_independent_lineage():
    evidence = _evidence(
        telemetry_lineage=("shared-mail-log", "shared-mail-log"),
        lineage_independence=True,
    )
    pipeline, _, _ = _pipeline()

    result = pipeline.submit(_request(evidence))

    assert evidence.lineage_independence is False
    assert evidence.confidence_inputs.independent_lineage_factor == 0.0
    assert result.decision is PromotionDecision.REJECTED
    assert "hard_gate_failed:lineage_adjusted_agreement" in result.reason_codes


@pytest.mark.parametrize(
    "baseline_key",
    [
        "vendor.payment_accounts.primary",
        "identity_provider.privileged_group_membership",
        "detector.alert_suppression_rule",
    ],
)
def test_tbi_inv_3_4_5_locked_keys_cannot_auto_promote(baseline_key):
    pipeline, _, _ = _pipeline()
    inputs = _perfect_inputs(operator_policy_factor=0.0)
    evidence = _evidence(
        baseline_key=baseline_key,
        risk_tier=RiskTier.HIGH,
        inputs=inputs,
    )

    result = pipeline.submit(_request(evidence))

    assert result.decision is PromotionDecision.REJECTED
    assert "permanent_lockout_key" in result.reason_codes
    assert result.baseline_version is None


def test_tbi_inv_6_requester_cannot_approve_own_change():
    pipeline, _, _ = _pipeline()
    evidence = _evidence(risk_tier=RiskTier.MEDIUM)

    result = pipeline.submit(
        _request(evidence, approvals=(Approval(actor_id="requester-a"),))
    )

    assert "separation_of_duties_failed" in result.reason_codes


def test_tbi_inv_7_same_actor_cannot_satisfy_dual_approval():
    pipeline, _, _ = _pipeline()
    evidence = _evidence(risk_tier=RiskTier.HIGH)

    result = pipeline.submit(
        _request(
            evidence,
            approvals=(Approval(actor_id="operator-a"), Approval(actor_id="operator-a")),
        )
    )

    assert "separation_of_duties_failed" in result.reason_codes


def test_high_risk_dual_distinct_approval_can_promote_when_not_locked():
    pipeline, _, _ = _pipeline()
    evidence = _evidence(risk_tier=RiskTier.HIGH, baseline_key="sender.geo_pattern")

    result = pipeline.submit(
        _request(
            evidence,
            approvals=(Approval(actor_id="operator-a"), Approval(actor_id="operator-b")),
        )
    )

    assert result.decision is PromotionDecision.PROMOTED


def test_tbi_inv_8_rollback_freezes_key_immediately():
    pipeline, store, _ = _pipeline()
    promoted = pipeline.submit(_request(_evidence()))

    rollback = pipeline.rollback(
        tenant_id=TENANT,
        baseline_key="sender.known_good_domain",
        bad_baseline_version=promoted.baseline_version.version,
        actor_id="operator-a",
        artifacts=(),
    )

    assert rollback.baseline_status is BaselineStatus.FROZEN_PENDING_RECONCILIATION
    assert store.is_frozen(TENANT, "sender.known_good_domain")


def test_tbi_inv_9_replay_cannot_recursively_promote():
    pipeline, _, _ = _pipeline()
    promoted = pipeline.submit(_request(_evidence()))
    artifact = DownstreamArtifact(
        artifact_id="case-1",
        artifact_type="case",
        used_baseline_version=promoted.baseline_version.version,
        observed_at=promoted.baseline_version.activated_at,
        outcome=RollbackOutcome.CASE_REQUIRES_OPERATOR_REVIEW,
    )

    rollback = pipeline.rollback(
        tenant_id=TENANT,
        baseline_key="sender.known_good_domain",
        bad_baseline_version=promoted.baseline_version.version,
        actor_id="operator-a",
        artifacts=(artifact,),
    )

    assert rollback.outcomes["case-1"] is RollbackOutcome.CASE_REQUIRES_OPERATOR_REVIEW
    assert pipeline.store.current(TENANT, "sender.known_good_domain").version == 1


def test_tbi_inv_10_in_window_candidates_are_quarantined():
    pipeline, _, _ = _pipeline()
    promoted = pipeline.submit(_request(_evidence()))

    rollback = pipeline.rollback(
        tenant_id=TENANT,
        baseline_key="sender.known_good_domain",
        bad_baseline_version=promoted.baseline_version.version,
        actor_id="operator-a",
        artifacts=(),
        downstream_candidate_ids=("candidate-1", "candidate-2"),
    )

    assert rollback.quarantined_candidates == ("candidate-1", "candidate-2")
    assert rollback.outcomes["candidate-1"] is (
        RollbackOutcome.DOWNSTREAM_BASELINE_CANDIDATE_INVALIDATED
    )


def test_tbi_inv_11_audit_record_includes_both_baseline_versions():
    pipeline, _, audit = _pipeline()

    pipeline.submit(_request(_evidence()))

    record = audit.entries()[-1]
    assert record.old_baseline_version is None
    assert record.new_baseline_version == 1


def test_tbi_inv_12_audit_record_includes_evidence_ids_and_approval_identities():
    pipeline, _, audit = _pipeline()
    evidence = _evidence(risk_tier=RiskTier.MEDIUM)

    pipeline.submit(_request(evidence, approvals=(Approval(actor_id="operator-a"),)))

    record = audit.entries()[-1]
    assert record.evidence_ids == ("ev-1",)
    assert record.separation_of_duties["approver_actor_ids"] == ["operator-a"]


def test_tbi_inv_13_rollback_produces_outcomes_for_all_in_window_artifacts():
    pipeline, _, _ = _pipeline()
    promoted = pipeline.submit(_request(_evidence()))
    artifacts = (
        DownstreamArtifact(
            artifact_id="alert-1",
            artifact_type="alert",
            used_baseline_version=1,
            observed_at=promoted.baseline_version.activated_at,
        ),
        DownstreamArtifact(
            artifact_id="report-1",
            artifact_type="report",
            used_baseline_version=1,
            observed_at=promoted.baseline_version.activated_at,
            outcome=RollbackOutcome.REPORT_REQUIRES_AMENDMENT,
        ),
    )

    rollback = pipeline.rollback(
        tenant_id=TENANT,
        baseline_key="sender.known_good_domain",
        bad_baseline_version=1,
        actor_id="operator-a",
        artifacts=artifacts,
    )

    assert set(rollback.outcomes) == {"alert-1", "report-1"}
    assert rollback.outcomes["report-1"] is RollbackOutcome.REPORT_REQUIRES_AMENDMENT


def test_tbi_inv_14_snapshot_failure_blocks_promotion_and_writes_audit_record():
    pipeline, _, audit = _pipeline(fail_snapshot=True)

    result = pipeline.submit(_request(_evidence()))

    assert result.decision is PromotionDecision.REJECTED
    assert result.baseline_version is None
    assert "snapshot_creation_failed" in result.reason_codes
    assert audit.entries()[-1].new_baseline_version is None
    assert audit.validate_chain()


def test_codex_incomplete_required_payload_fields_reject_and_audit():
    pipeline, _, audit = _pipeline()
    evidence = _evidence(evidence_id="", baseline_key="", telemetry_lineage=("src-a",))

    result = pipeline.submit(_request(evidence))

    assert result.decision is PromotionDecision.REJECTED
    assert "incomplete_evidence_payload" in result.reason_codes
    assert result.baseline_version is None
    assert audit.entries()[-1].promotion_reason_codes[0] == "incomplete_evidence_payload"


def test_codex_rollback_window_uses_bad_version_activation_not_current_version():
    pipeline, _, _ = _pipeline()
    first = pipeline.submit(
        _request(_evidence(evidence_id="ev-1", baseline_key="sender.pattern"))
    )
    second = pipeline.submit(
        _request(_evidence(evidence_id="ev-2", baseline_key="sender.pattern"))
    )
    artifact = DownstreamArtifact(
        artifact_id="alert-from-v1",
        artifact_type="alert",
        used_baseline_version=first.baseline_version.version,
        observed_at=first.baseline_version.activated_at,
        outcome=RollbackOutcome.ALERT_SHOULD_HAVE_FIRED,
    )

    rollback = pipeline.rollback(
        tenant_id=TENANT,
        baseline_key="sender.pattern",
        bad_baseline_version=first.baseline_version.version,
        actor_id="operator-a",
        artifacts=(artifact,),
    )

    assert second.baseline_version.version == 2
    assert rollback.outcomes["alert-from-v1"] is RollbackOutcome.ALERT_SHOULD_HAVE_FIRED


def test_codex_manual_lineage_review_requires_operator_approval():
    pipeline, _, _ = _pipeline()
    evidence = _evidence(lineage_independence=False)

    result = pipeline.submit(_request(evidence, manual_lineage_review=True))

    assert result.candidate_status is CandidateStatus.OPERATOR_REVIEW
    assert "operator_review_required" in result.reason_codes


def test_codex_non_operator_approver_is_rejected():
    pipeline, _, _ = _pipeline()
    evidence = _evidence(risk_tier=RiskTier.MEDIUM)

    result = pipeline.submit(
        _request(
            evidence,
            approvals=(Approval(actor_id="agent-approver", actor_type=ActorType.AGENT),),
        )
    )

    assert result.decision is PromotionDecision.REJECTED
    assert "separation_of_duties_failed" in result.reason_codes


def test_codex_locked_key_manual_promotion_allowed_with_dual_operator_approval():
    pipeline, _, _ = _pipeline()
    inputs = _perfect_inputs(operator_policy_factor=0.0)
    evidence = _evidence(
        baseline_key="vendor.payment_accounts.primary",
        risk_tier=RiskTier.HIGH,
        inputs=inputs,
    )

    result = pipeline.submit(
        _request(
            evidence,
            approvals=(Approval(actor_id="operator-a"), Approval(actor_id="operator-b")),
        )
    )

    assert result.decision is PromotionDecision.PROMOTED


def test_codex_rollback_window_includes_ingestion_delay_buffer():
    pipeline, _, _ = _pipeline()
    promoted = pipeline.submit(_request(_evidence(baseline_key="sender.buffered")))
    rollback_time = promoted.baseline_version.activated_at + timedelta(minutes=1)
    delayed_artifact = DownstreamArtifact(
        artifact_id="delayed-alert",
        artifact_type="alert",
        used_baseline_version=promoted.baseline_version.version,
        observed_at=rollback_time + timedelta(minutes=4),
        outcome=RollbackOutcome.ALERT_WAS_INCORRECTLY_SUPPRESSED,
    )

    rollback = pipeline.rollback(
        tenant_id=TENANT,
        baseline_key="sender.buffered",
        bad_baseline_version=promoted.baseline_version.version,
        actor_id="operator-a",
        artifacts=(delayed_artifact,),
        now=rollback_time,
    )

    assert rollback.outcomes["delayed-alert"] is (
        RollbackOutcome.ALERT_WAS_INCORRECTLY_SUPPRESSED
    )


def test_codex_persisted_audit_chain_continues_after_restart(tmp_path):
    audit_path = tmp_path / "baseline_audit.jsonl"
    first_audit = BaselineAuditLog(jsonl_path=audit_path)
    first_pipeline = TenantBaselineIngestionPipeline(
        store=TenantBaselineStore(), audit_log=first_audit
    )
    first_pipeline.submit(_request(_evidence(evidence_id="ev-1")))
    first_signature = first_audit.entries()[-1].audit_signature

    second_audit = BaselineAuditLog(jsonl_path=audit_path)
    second_pipeline = TenantBaselineIngestionPipeline(
        store=TenantBaselineStore(), audit_log=second_audit
    )
    second_pipeline.submit(_request(_evidence(evidence_id="ev-2")))

    assert len(second_audit.entries()) == 2
    assert second_audit.entries()[-1].previous_audit_signature == first_signature
    assert second_audit.validate_chain()


def test_codex_rollback_missing_baseline_version_rejected_before_freeze():
    pipeline, store, _ = _pipeline()
    pipeline.submit(_request(_evidence()))

    with pytest.raises(RollbackRejected, match="not_found"):
        pipeline.rollback(
            tenant_id=TENANT,
            baseline_key="sender.known_good_domain",
            bad_baseline_version=99,
            actor_id="operator-a",
            artifacts=(),
        )

    assert not store.is_frozen(TENANT, "sender.known_good_domain")


def test_codex_low_risk_auto_promotion_miss_routes_to_operator_review():
    pipeline, _, _ = _pipeline()
    inputs = _perfect_inputs(evidence_completeness=0.94)
    evidence = _evidence(inputs=inputs)

    result = pipeline.submit(_request(evidence))

    assert result.decision is PromotionDecision.QUARANTINED
    assert result.candidate_status is CandidateStatus.OPERATOR_REVIEW
    assert any(code.startswith("auto_promotion_blocked:") for code in result.reason_codes)


def test_codex_operator_approval_clears_low_risk_auto_only_miss():
    pipeline, _, _ = _pipeline()
    inputs = _perfect_inputs(evidence_completeness=0.94)
    evidence = _evidence(inputs=inputs)

    result = pipeline.submit(
        _request(evidence, approvals=(Approval(actor_id="operator-a"),))
    )

    assert result.decision is PromotionDecision.PROMOTED


def test_codex_tenant_admin_can_approve_critical_risk_path():
    pipeline, _, _ = _pipeline()
    evidence = _evidence(risk_tier=RiskTier.CRITICAL, baseline_key="sender.critical")

    result = pipeline.submit(
        _request(
            evidence,
            approvals=(
                Approval(actor_id="tenant-admin-a", actor_type=ActorType.TENANT_ADMIN),
            ),
        )
    )

    assert result.decision is PromotionDecision.PROMOTED


def test_codex_none_required_identifier_is_rejected_and_audited():
    pipeline, _, audit = _pipeline()
    evidence = _evidence()
    object.__setattr__(evidence, "tenant_id", None)

    result = pipeline.submit(_request(evidence))

    assert result.decision is PromotionDecision.REJECTED
    assert "incomplete_evidence_payload" in result.reason_codes
    assert audit.entries()[-1].tenant_id is None


def test_tbi_inv_15_broken_audit_chain_is_detectable():
    pipeline, _, audit = _pipeline()
    pipeline.submit(_request(_evidence()))
    original = audit.entries()[0]
    tampered = dataclasses.replace(original, baseline_key="tampered")
    audit._records[0] = tampered

    assert audit.validate_chain() is False


def test_replay_beyond_depth_one_requires_dual_operator_scope():
    pipeline, _, _ = _pipeline()

    with pytest.raises(RollbackRejected):
        pipeline.rollback(
            tenant_id=TENANT,
            baseline_key="sender.known_good_domain",
            bad_baseline_version=1,
            actor_id="operator-a",
            artifacts=(),
            depth=2,
        )


@pytest.mark.xfail(
    reason=(
        "Durable cross-process baseline storage is deferred; this build enforces "
        "the signed lifecycle in an in-memory testable store without replacing "
        "the existing vendor baseline SQLite surface."
    ),
    strict=True,
)
def test_xfail_durable_cross_process_baseline_store():
    raise AssertionError("deferred to persistence hardening contract")
