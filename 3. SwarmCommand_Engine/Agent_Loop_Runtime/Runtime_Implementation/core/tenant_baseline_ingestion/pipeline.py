"""Governed evidence-to-baseline promotion pipeline (Gap 5)."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from typing import Any, Mapping

from core.tenant_baseline_ingestion.audit import BaselineAuditLog
from core.tenant_baseline_ingestion.state import (
    RISK_TIER_CAPS,
    PROMOTION_THRESHOLDS,
    ActorType,
    ApprovalPolicy,
    AuditEventType,
    BaselineStatus,
    CandidateStatus,
    PromotionDecision,
    RiskTier,
    RollbackOutcome,
    approval_policy_for,
    is_permanent_lockout_key,
)

REQUIRED_EVIDENCE_FIELDS: frozenset[str] = frozenset(
    {
        "schema_version",
        "evidence_id",
        "tenant_id",
        "observed_at",
        "received_at",
        "source_component",
        "source_instance_id",
        "evidence_type",
        "entity_type",
        "entity_id",
        "candidate_baseline_key",
        "observed_state",
        "normalized_state",
        "confidence_inputs",
        "confidence_score",
        "risk_tier",
        "telemetry_signature",
        "retention_policy",
        "telemetry_lineage",
        "lineage_independence",
    }
)


class TenantBaselineIngestionError(Exception):
    """Base class for Gap 5 pipeline failures."""


class PromotionRejected(TenantBaselineIngestionError):
    """Raised when a candidate cannot promote."""


class SnapshotCreationError(TenantBaselineIngestionError):
    """Raised when immutable snapshot creation fails."""


class RollbackRejected(TenantBaselineIngestionError):
    """Raised when rollback/replay would exceed signed scope."""


@dataclass(frozen=True)
class ConfidenceInputs:
    evidence_completeness: float
    observation_stability: float
    historical_consistency: float
    sample_size_weight: float
    recency_weight: float
    normalization_quality: float
    cross_source_agreement: float
    independent_lineage_factor: float
    source_reliability: float
    operator_policy_factor: float = 1.0
    anomaly_penalty: float = 0.0

    def as_context(self) -> dict[str, float]:
        return {
            "evidence_completeness": self.evidence_completeness,
            "observation_stability": self.observation_stability,
            "historical_consistency": self.historical_consistency,
            "sample_size_weight": self.sample_size_weight,
            "recency_weight": self.recency_weight,
            "normalization_quality": self.normalization_quality,
            "cross_source_agreement": self.cross_source_agreement,
            "independent_lineage_factor": self.independent_lineage_factor,
            "source_reliability": self.source_reliability,
            "operator_policy_factor": self.operator_policy_factor,
            "anomaly_penalty": self.anomaly_penalty,
        }


@dataclass(frozen=True)
class EvidencePayload:
    schema_version: str
    evidence_id: str
    tenant_id: str
    observed_at: datetime
    received_at: datetime
    source_component: str
    source_instance_id: str
    evidence_type: str
    entity_type: str
    entity_id: str
    candidate_baseline_key: str
    observed_state: str
    normalized_state: str
    confidence_inputs: ConfidenceInputs
    confidence_score: float
    risk_tier: RiskTier
    telemetry_signature: str
    retention_policy: str
    telemetry_lineage: tuple[str, ...]
    lineage_independence: bool

    def __post_init__(self) -> None:
        if not isinstance(self.risk_tier, RiskTier):
            raise PromotionRejected("risk_tier must be a RiskTier")
        if not self.telemetry_lineage:
            raise PromotionRejected("incomplete_evidence_payload")
        if len(set(self.telemetry_lineage)) != len(self.telemetry_lineage):
            object.__setattr__(self, "lineage_independence", False)
            adjusted_inputs = replace(
                self.confidence_inputs, independent_lineage_factor=0.0
            )
            object.__setattr__(self, "confidence_inputs", adjusted_inputs)
            object.__setattr__(
                self,
                "confidence_score",
                calculate_confidence_score(adjusted_inputs, self.risk_tier),
            )

    def context(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "evidence_id": self.evidence_id,
            "tenant_id": self.tenant_id,
            "source_component": self.source_component,
            "source_instance_id": self.source_instance_id,
            "candidate_baseline_key": self.candidate_baseline_key,
            "confidence_score": self.confidence_score,
            "risk_tier": self.risk_tier.value,
            "telemetry_lineage": list(self.telemetry_lineage),
            "lineage_independence": self.lineage_independence,
            "confidence_inputs": self.confidence_inputs.as_context(),
        }


@dataclass(frozen=True)
class Approval:
    actor_id: str
    actor_type: ActorType = ActorType.OPERATOR


@dataclass(frozen=True)
class PromotionRequest:
    workflow_id: str
    requester_actor_id: str
    implementer_actor_id: str
    evidence: EvidencePayload
    approvals: tuple[Approval, ...] = ()
    manual_lineage_review: bool = False


@dataclass(frozen=True)
class BaselineVersion:
    tenant_id: str
    baseline_key: str
    version: int
    state: str
    evidence_ids: tuple[str, ...]
    activated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class BaselineSnapshot:
    tenant_id: str
    baseline_key: str
    version: int | None
    state: str | None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class PromotionResult:
    decision: PromotionDecision
    candidate_status: CandidateStatus
    reason_codes: tuple[str, ...]
    confidence_score: float
    baseline_version: BaselineVersion | None
    audit_signature: str


@dataclass(frozen=True)
class DownstreamArtifact:
    artifact_id: str
    artifact_type: str
    used_baseline_version: int
    observed_at: datetime
    outcome: RollbackOutcome | None = None


@dataclass(frozen=True)
class RollbackResult:
    baseline_status: BaselineStatus
    rollback_id: str
    outcomes: Mapping[str, RollbackOutcome]
    quarantined_candidates: tuple[str, ...]
    audit_signature: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "outcomes", MappingProxyType(dict(self.outcomes)))


@dataclass
class TenantBaselineStore:
    """In-memory tenant baseline store with immutable version snapshots."""

    fail_snapshot: bool = False
    _versions: dict[tuple[str, str], tuple[BaselineVersion, ...]] = field(
        default_factory=dict
    )
    _frozen_keys: set[tuple[str, str]] = field(default_factory=set)

    def current(self, tenant_id: str, baseline_key: str) -> BaselineVersion | None:
        versions = self._versions.get((tenant_id, baseline_key), ())
        return versions[-1] if versions else None

    def version(
        self, tenant_id: str, baseline_key: str, version: int
    ) -> BaselineVersion | None:
        versions = self._versions.get((tenant_id, baseline_key), ())
        for baseline in versions:
            if baseline.version == version:
                return baseline
        return None

    def snapshot(self, tenant_id: str, baseline_key: str) -> BaselineSnapshot:
        if self.fail_snapshot:
            raise SnapshotCreationError("snapshot_creation_failed")
        current = self.current(tenant_id, baseline_key)
        return BaselineSnapshot(
            tenant_id=tenant_id,
            baseline_key=baseline_key,
            version=current.version if current else None,
            state=current.state if current else None,
        )

    def promote(
        self,
        tenant_id: str,
        baseline_key: str,
        state: str,
        evidence_ids: tuple[str, ...],
    ) -> BaselineVersion:
        if (tenant_id, baseline_key) in self._frozen_keys:
            raise PromotionRejected("baseline_frozen_pending_reconciliation")
        current = self.current(tenant_id, baseline_key)
        version = 1 if current is None else current.version + 1
        baseline = BaselineVersion(
            tenant_id=tenant_id,
            baseline_key=baseline_key,
            version=version,
            state=state,
            evidence_ids=evidence_ids,
        )
        key = (tenant_id, baseline_key)
        self._versions[key] = self._versions.get(key, ()) + (baseline,)
        return baseline

    def freeze(self, tenant_id: str, baseline_key: str) -> None:
        self._frozen_keys.add((tenant_id, baseline_key))

    def is_frozen(self, tenant_id: str, baseline_key: str) -> bool:
        return (tenant_id, baseline_key) in self._frozen_keys


@dataclass
class TenantBaselineIngestionPipeline:
    store: TenantBaselineStore
    audit_log: BaselineAuditLog
    max_reconciliation_depth: int = 1
    ingestion_delay_buffer: timedelta = timedelta(minutes=5)

    def submit(self, request: PromotionRequest) -> PromotionResult:
        evidence = request.evidence
        locked_key = is_permanent_lockout_key(evidence.candidate_baseline_key)
        policy = approval_policy_for(evidence.risk_tier, locked_key)
        old_version = self.store.current(evidence.tenant_id, evidence.candidate_baseline_key)

        reason_codes = self._reason_codes(request, locked_key, policy)
        if reason_codes:
            reviewable = (
                "operator_review_required" in reason_codes
                or any(
                    code.startswith("auto_promotion_blocked:") for code in reason_codes
                )
            ) and not has_terminal_rejection(reason_codes)
            decision = (
                PromotionDecision.QUARANTINED
                if reviewable
                else PromotionDecision.REJECTED
            )
            return self._record_result(
                request=request,
                decision=decision,
                status=(
                    CandidateStatus.OPERATOR_REVIEW
                    if decision is PromotionDecision.QUARANTINED
                    else CandidateStatus.REJECTED
                ),
                reason_codes=tuple(reason_codes),
                policy=policy,
                old_version=old_version.version if old_version else None,
                new_version=None,
                baseline_version=None,
                event_type=(
                    AuditEventType.QUARANTINE
                    if decision is PromotionDecision.QUARANTINED
                    else AuditEventType.REJECTION
                ),
            )

        try:
            snapshot = self.store.snapshot(
                evidence.tenant_id, evidence.candidate_baseline_key
            )
        except SnapshotCreationError:
            return self._record_result(
                request=request,
                decision=PromotionDecision.REJECTED,
                status=CandidateStatus.REJECTED,
                reason_codes=("snapshot_creation_failed",),
                policy=policy,
                old_version=old_version.version if old_version else None,
                new_version=None,
                baseline_version=None,
                event_type=AuditEventType.REJECTION,
            )
        baseline = self.store.promote(
            evidence.tenant_id,
            evidence.candidate_baseline_key,
            evidence.normalized_state,
            (evidence.evidence_id,),
        )
        if snapshot.version != (old_version.version if old_version else None):
            raise PromotionRejected("snapshot_version_mismatch")
        return self._record_result(
            request=request,
            decision=PromotionDecision.PROMOTED,
            status=CandidateStatus.PROMOTED,
            reason_codes=("promoted",),
            policy=policy,
            old_version=snapshot.version,
            new_version=baseline.version,
            baseline_version=baseline,
            event_type=AuditEventType.PROMOTION,
        )

    def rollback(
        self,
        *,
        tenant_id: str,
        baseline_key: str,
        bad_baseline_version: int,
        actor_id: str,
        artifacts: tuple[DownstreamArtifact, ...],
        downstream_candidate_ids: tuple[str, ...] = (),
        depth: int = 1,
        now: datetime | None = None,
    ) -> RollbackResult:
        if depth > self.max_reconciliation_depth:
            raise RollbackRejected("cascade_depth_requires_dual_operator_approval")
        timestamp = now or datetime.now(timezone.utc)
        bad_version = self.store.version(tenant_id, baseline_key, bad_baseline_version)
        if bad_version is None:
            raise RollbackRejected("bad_baseline_version_not_found")
        self.store.freeze(tenant_id, baseline_key)
        current = self.store.current(tenant_id, baseline_key)
        window_start = bad_version.activated_at
        window_end = timestamp + self.ingestion_delay_buffer
        outcomes: dict[str, RollbackOutcome] = {}
        for artifact in artifacts:
            if (
                artifact.used_baseline_version == bad_baseline_version
                and window_start <= artifact.observed_at <= window_end
            ):
                outcomes[artifact.artifact_id] = (
                    artifact.outcome
                    or RollbackOutcome.CASE_REQUIRES_OPERATOR_REVIEW
                )
        for candidate_id in downstream_candidate_ids:
            outcomes[candidate_id] = RollbackOutcome.DOWNSTREAM_BASELINE_CANDIDATE_INVALIDATED

        record = self.audit_log.record(
            tenant_id=tenant_id,
            event_type=AuditEventType.ROLLBACK,
            actor_type=ActorType.OPERATOR,
            actor_id=actor_id,
            baseline_key=baseline_key,
            old_baseline_version=bad_baseline_version,
            new_baseline_version=current.version if current else None,
            evidence_ids=(),
            decision=PromotionDecision.ROLLED_BACK,
            promotion_reason_codes=("rollback_applied",),
            risk_tier=RiskTier.HIGH,
            approval_policy=ApprovalPolicy.DUAL_OPERATOR,
            request_context={
                "max_reconciliation_depth": self.max_reconciliation_depth,
                "window_start": window_start.isoformat(),
                "window_end": window_end.isoformat(),
                "replay_updates_active_baseline": False,
            },
            separation_of_duties={"rollback_actor": actor_id},
            rollback_status=BaselineStatus.FROZEN_PENDING_RECONCILIATION.value,
            rollback_blast_radius={
                "artifacts": list(outcomes),
                "downstream_candidates": list(downstream_candidate_ids),
            },
        )
        return RollbackResult(
            baseline_status=BaselineStatus.FROZEN_PENDING_RECONCILIATION,
            rollback_id=record.audit_event_id,
            outcomes=outcomes,
            quarantined_candidates=downstream_candidate_ids,
            audit_signature=record.audit_signature,
        )

    def _reason_codes(
        self,
        request: PromotionRequest,
        locked_key: bool,
        policy: ApprovalPolicy,
    ) -> list[str]:
        evidence = request.evidence
        reasons: list[str] = []
        invalid_payload_fields = invalid_evidence_payload_fields(evidence)
        if invalid_payload_fields:
            reasons.append("incomplete_evidence_payload")
        score = calculate_confidence_score(evidence.confidence_inputs, evidence.risk_tier)
        if abs(score - evidence.confidence_score) > 0.000001:
            reasons.append("confidence_score_not_reproducible")
        hard_gate = first_failed_hard_gate(evidence.confidence_inputs)
        if hard_gate:
            reasons.append(f"hard_gate_failed:{hard_gate}")
        approved_locked_key = locked_key and has_dual_operator_approval(request.approvals)
        if (
            evidence.confidence_score < PROMOTION_THRESHOLDS[evidence.risk_tier]
            and not (
                evidence.risk_tier is RiskTier.LOW
                and has_operator_approval(request.approvals)
            )
            and not approved_locked_key
        ):
            reasons.append("confidence_below_risk_threshold")
        if not evidence.lineage_independence and (
            not request.manual_lineage_review
            or not has_operator_approval(request.approvals)
        ):
            reasons.append("operator_review_required")
        if locked_key and not has_dual_operator_approval(request.approvals):
            reasons.append("permanent_lockout_key")
        sod_reason = separation_of_duties_failure(request, policy)
        if sod_reason:
            reasons.append(sod_reason)
        auto_fail = auto_promotion_failure(evidence)
        if policy is ApprovalPolicy.NONE_AUTO and auto_fail and not has_operator_approval(
            request.approvals
        ):
            reasons.append(auto_fail)
        return reasons

    def _record_result(
        self,
        *,
        request: PromotionRequest,
        decision: PromotionDecision,
        status: CandidateStatus,
        reason_codes: tuple[str, ...],
        policy: ApprovalPolicy,
        old_version: int | None,
        new_version: int | None,
        baseline_version: BaselineVersion | None,
        event_type: AuditEventType,
    ) -> PromotionResult:
        evidence = request.evidence
        record = self.audit_log.record(
            tenant_id=evidence.tenant_id,
            event_type=event_type,
            actor_type=ActorType.SYSTEM,
            actor_id="tenant_baseline_ingestion",
            baseline_key=evidence.candidate_baseline_key,
            old_baseline_version=old_version,
            new_baseline_version=new_version,
            evidence_ids=(evidence.evidence_id,),
            decision=decision,
            promotion_reason_codes=reason_codes,
            risk_tier=evidence.risk_tier,
            approval_policy=policy,
            request_context={
                "workflow_id": request.workflow_id,
                "requester_actor_id": request.requester_actor_id,
                "implementer_actor_id": request.implementer_actor_id,
                "evidence": evidence.context(),
            },
            separation_of_duties={
                "requester_actor_id": request.requester_actor_id,
                "implementer_actor_id": request.implementer_actor_id,
                "approver_actor_ids": [a.actor_id for a in request.approvals],
                "satisfied": "separation_of_duties_failed" not in reason_codes,
            },
            rollback_status="",
            rollback_blast_radius={},
        )
        return PromotionResult(
            decision=decision,
            candidate_status=status,
            reason_codes=reason_codes,
            confidence_score=evidence.confidence_score,
            baseline_version=baseline_version,
            audit_signature=record.audit_signature,
        )


def calculate_confidence_score(inputs: ConfidenceInputs, risk_tier: RiskTier) -> float:
    base_quality = (
        0.20 * inputs.evidence_completeness
        + 0.20 * inputs.observation_stability
        + 0.15 * inputs.historical_consistency
        + 0.15 * inputs.sample_size_weight
        + 0.10 * inputs.recency_weight
        + 0.20 * inputs.normalization_quality
    )
    lineage_adjusted_agreement = (
        inputs.cross_source_agreement * inputs.independent_lineage_factor
    )
    gate_multiplier = (
        inputs.source_reliability**2
        * lineage_adjusted_agreement**2
        * inputs.operator_policy_factor
        * (1 - inputs.anomaly_penalty)
    )
    return max(0.0, min(base_quality * gate_multiplier, RISK_TIER_CAPS[risk_tier]))


def first_failed_hard_gate(inputs: ConfidenceInputs) -> str:
    if inputs.source_reliability < 0.70:
        return "source_reliability"
    if inputs.cross_source_agreement * inputs.independent_lineage_factor < 0.70:
        return "lineage_adjusted_agreement"
    if inputs.evidence_completeness < 0.90:
        return "evidence_completeness"
    if inputs.normalization_quality < 0.90:
        return "normalization_quality"
    if inputs.anomaly_penalty > 0.20:
        return "anomaly_penalty"
    return ""


def separation_of_duties_failure(
    request: PromotionRequest, policy: ApprovalPolicy
) -> str:
    approvers = request.approvals
    for approver in approvers:
        if approver.actor_type is not ActorType.OPERATOR and not (
            policy is ApprovalPolicy.DUAL_OR_TENANT_ADMIN
            and approver.actor_type is ActorType.TENANT_ADMIN
        ):
            return "separation_of_duties_failed"
        if approver.actor_id in {
            request.requester_actor_id,
            request.implementer_actor_id,
            request.evidence.source_instance_id,
        }:
            return "separation_of_duties_failed"
    if policy is ApprovalPolicy.SINGLE_OPERATOR and not approvers:
        return "operator_review_required"
    if policy in {ApprovalPolicy.DUAL_OPERATOR, ApprovalPolicy.DUAL_OR_TENANT_ADMIN}:
        if policy is ApprovalPolicy.DUAL_OR_TENANT_ADMIN and has_tenant_admin_approval(
            approvers
        ):
            return ""
        if len(approvers) < 2:
            return "operator_review_required"
        if approvers[0].actor_id == approvers[1].actor_id:
            return "separation_of_duties_failed"
    return ""


def has_operator_approval(approvals: tuple[Approval, ...]) -> bool:
    return any(approval.actor_type is ActorType.OPERATOR for approval in approvals)


def has_dual_operator_approval(approvals: tuple[Approval, ...]) -> bool:
    operator_ids = [
        approval.actor_id
        for approval in approvals
        if approval.actor_type is ActorType.OPERATOR
    ]
    return len(set(operator_ids)) >= 2


def has_tenant_admin_approval(approvals: tuple[Approval, ...]) -> bool:
    return any(approval.actor_type is ActorType.TENANT_ADMIN for approval in approvals)


def has_terminal_rejection(reason_codes: tuple[str, ...] | list[str]) -> bool:
    return any(
        code == "incomplete_evidence_payload"
        or code == "permanent_lockout_key"
        or code == "separation_of_duties_failed"
        or code == "confidence_score_not_reproducible"
        or code.startswith("hard_gate_failed:")
        for code in reason_codes
    )


def auto_promotion_failure(evidence: EvidencePayload) -> str:
    inputs = evidence.confidence_inputs
    if evidence.risk_tier is not RiskTier.LOW:
        return "auto_promotion_blocked:risk_tier"
    if evidence.confidence_score < 0.95:
        return "auto_promotion_blocked:confidence_score"
    if inputs.source_reliability < 0.85:
        return "auto_promotion_blocked:source_reliability"
    if inputs.cross_source_agreement * inputs.independent_lineage_factor < 0.85:
        return "auto_promotion_blocked:lineage_adjusted_agreement"
    if inputs.independent_lineage_factor < 0.85:
        return "auto_promotion_blocked:independent_lineage_factor"
    if inputs.evidence_completeness < 0.95:
        return "auto_promotion_blocked:evidence_completeness"
    if inputs.normalization_quality < 0.95:
        return "auto_promotion_blocked:normalization_quality"
    if inputs.anomaly_penalty > 0.05:
        return "auto_promotion_blocked:anomaly_penalty"
    if is_permanent_lockout_key(evidence.candidate_baseline_key):
        return "auto_promotion_blocked:permanent_lockout_key"
    return ""


def invalid_evidence_payload_fields(evidence: EvidencePayload) -> tuple[str, ...]:
    invalid: list[str] = []
    string_fields = (
        "schema_version",
        "evidence_id",
        "tenant_id",
        "source_component",
        "source_instance_id",
        "evidence_type",
        "entity_type",
        "entity_id",
        "candidate_baseline_key",
        "observed_state",
        "normalized_state",
        "telemetry_signature",
        "retention_policy",
    )
    for field_name in string_fields:
        value = getattr(evidence, field_name)
        if not isinstance(value, str) or not value:
            invalid.append(field_name)
    if not isinstance(evidence.observed_at, datetime):
        invalid.append("observed_at")
    if not isinstance(evidence.received_at, datetime):
        invalid.append("received_at")
    if not evidence.telemetry_lineage:
        invalid.append("telemetry_lineage")
    return tuple(sorted(set(invalid)))


__all__ = [
    "REQUIRED_EVIDENCE_FIELDS",
    "TenantBaselineIngestionError",
    "PromotionRejected",
    "SnapshotCreationError",
    "RollbackRejected",
    "ConfidenceInputs",
    "EvidencePayload",
    "Approval",
    "PromotionRequest",
    "BaselineVersion",
    "BaselineSnapshot",
    "PromotionResult",
    "DownstreamArtifact",
    "RollbackResult",
    "TenantBaselineStore",
    "TenantBaselineIngestionPipeline",
    "calculate_confidence_score",
    "first_failed_hard_gate",
    "separation_of_duties_failure",
    "has_operator_approval",
    "has_dual_operator_approval",
    "has_tenant_admin_approval",
    "has_terminal_rejection",
    "auto_promotion_failure",
    "invalid_evidence_payload_fields",
]
