"""Production Swarm Loop prototype.

This module is Blue-only by design. It uses approved orchestrator routes to
write every stage to the Blackboard and sends only anonymized low-confidence
weakness reports to the sandbox.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.blackboard import (
    AuditStatus,
    AuditVerdictPayload,
    DetectionResultPayload,
    Environment,
    IngestEventPayload,
    RiskScorePayload,
    WeaknessReportPayload,
    WorkflowTriggerPayload,
)
from core.operator_state import KillSwitchEngaged, is_kill_switch_engaged
from core.orchestrator import (
    RouteContext,
    RouteResult,
    default_sandbox_tenant_for,
    submit_audit_verdict,
    submit_detection_result,
    submit_ingest_event,
    submit_risk_score,
    submit_weakness_report,
    trigger_workflow,
)
from core.drafting import (
    DailyDigestConfig,
    DailyDigestResult,
    run_daily_digest_cycle,
)
from core.production_state import (
    ProductionPolicyState,
    load_state,
    resolve_effective_parameters,
    state_path,
)
from core.scoring import (
    EmailRiskScoringConfig,
    EmailRiskScoringResult,
    run_email_risk_scoring_cycle,
)

from .alert_subscriber import (
    AlertSubscriberConfig,
    AlertSubscriptionResult,
    run_alert_subscriber_cycle,
)
from .policy_consumer import (
    PolicyConsumerConfig,
    PolicyConsumerResult,
    apply_pending_policies,
)
from .regression_detector import (
    RegressionDetectorConfig,
    RegressionDetectorResult,
    run_regression_detector_cycle,
)


@dataclass(frozen=True)
class ProductionSignal:
    source: str
    event_kind: str
    subject: str | None = None
    sender_domain: str | None = None
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    raw_ref: str | None = None


@dataclass(frozen=True)
class ProductionLoopConfig:
    detection_agent_id: str = "blue_detection_001"
    scoring_agent_id: str = "risk_scoring_001"
    orchestrator_agent_id: str = "orchestrator_001"
    audit_agent_id: str = "audit_001"
    risk_threshold: int = 70
    confidence_threshold: float = 0.70
    workflow_name: str = "monthly_training_assignment"
    apply_pending_policies_at_end_of_cycle: bool = True
    policy_consumer_config: PolicyConsumerConfig | None = None
    run_alert_subscriber_at_end_of_cycle: bool = True
    alert_subscriber_config: AlertSubscriberConfig | None = None
    run_regression_detector_at_end_of_cycle: bool = False
    regression_detector_config: RegressionDetectorConfig | None = None
    run_email_risk_scoring_at_end_of_cycle: bool = False
    email_risk_scoring_config: EmailRiskScoringConfig | None = None
    run_daily_digest_at_end_of_cycle: bool = False
    daily_digest_config: DailyDigestConfig | None = None


@dataclass(frozen=True)
class ProductionLoopResult:
    ingest: RouteResult
    detection: RouteResult
    risk_score: RouteResult
    workflow_trigger: RouteResult | None
    audit: RouteResult
    weakness_report: RouteResult | None
    active_policy_state: ProductionPolicyState
    policy_apply: PolicyConsumerResult | None
    alert_subscriber: AlertSubscriptionResult | None
    regression_detector: RegressionDetectorResult | None
    email_risk_scoring: EmailRiskScoringResult | None
    daily_digest: DailyDigestResult | None


def _coerce_int_parameter(value: object) -> int:
    """Coerce a ``ProductionPolicyState.parameters`` value to a clamped int.

    Phase 1.4 lift parameters are contracted as integers in 0..25 by the
    mutation engine + gate; this helper makes the production read site
    robust to a parameters dict that somehow carries a float, a numeric
    string, ``None``, or an out-of-range int. Non-numeric values resolve
    to 0 so a corrupt state file can never crash the production cycle.
    The 25 ceiling mirrors the engine's per-promotion contract.
    """

    try:
        as_int = int(value) if value is not None else 0
    except (TypeError, ValueError):
        return 0
    if as_int <= 0:
        return 0
    if as_int >= 25:
        return 25
    return as_int


def _detect(signal: ProductionSignal, policy_state: ProductionPolicyState) -> DetectionResultPayload:
    subject = (signal.subject or "").lower()
    sender_domain = (signal.sender_domain or "").lower()
    signals: list[str] = []

    if "invoice" in subject or "payment" in subject:
        signals.append("financial_lure_language")
    if "urgent" in subject or "immediate" in subject:
        signals.append("urgency_language")
    if sender_domain and sender_domain.endswith(".ru"):
        signals.append("risky_sender_tld")
    if sender_domain and "northstar" not in sender_domain and "client" not in sender_domain:
        signals.append("unknown_sender_domain")

    confidence_boost = 0.0
    raw_boost = policy_state.parameters.get("confidence_boost", 0.0)
    if isinstance(raw_boost, (int, float)):
        confidence_boost = max(0.0, min(0.5, float(raw_boost)))

    base = 0.35 + (0.18 * len(signals))
    confidence = min(base + confidence_boost, 0.95)
    label = "suspicious" if signals else "no_obvious_threat"

    return DetectionResultPayload(
        detection_label=label,
        confidence=confidence,
        signals=signals,
        explanation=(
            f"Deterministic prototype detector (policy_version={policy_state.active_version}, "
            f"confidence_boost={confidence_boost:.2f})."
        ),
    )


def _score(detection: DetectionResultPayload) -> RiskScorePayload:
    score = min(100, round(detection.confidence * 100) + (5 * len(detection.signals)))
    if score >= 80:
        risk_level = "high"
    elif score >= 50:
        risk_level = "medium"
    else:
        risk_level = "low"

    recommended_action = (
        "Trigger training workflow"
        if score >= 70
        else "Monitor and retain evidence"
    )

    return RiskScorePayload(
        score=score,
        risk_level=risk_level,
        factors=detection.signals,
        recommended_action=recommended_action,
    )


def _weakness_report(signal: ProductionSignal, detection: DetectionResultPayload) -> WeaknessReportPayload:
    subject_hint = "financial_lure" if signal.subject and "invoice" in signal.subject.lower() else "general_pattern"
    domain_hint = "sender_domain_present" if signal.sender_domain else "sender_domain_missing"
    return WeaknessReportPayload(
        weakness_kind="low_confidence_detection",
        anonymized_pattern=f"{subject_hint}:{domain_hint}:{detection.detection_label}",
        confidence_gap=round(1.0 - detection.confidence, 4),
        raw_tenant_data_removed=True,
    )


def run_production_cycle(
    context: RouteContext,
    *,
    tenant_id: str,
    signal: ProductionSignal,
    config: ProductionLoopConfig | None = None,
) -> ProductionLoopResult:
    """Run one Blue-only production cycle for one tenant signal."""

    config = config or ProductionLoopConfig()

    kill_switch_state = is_kill_switch_engaged(
        context.blackboard_root, scope="PRODUCTION"
    )
    if kill_switch_state is not None:
        raise KillSwitchEngaged(kill_switch_state)

    active_policy_state = load_state(state_path(context.blackboard_root, tenant_id))

    ingest = submit_ingest_event(
        context,
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=config.orchestrator_agent_id,
        payload=IngestEventPayload(
            source=signal.source,
            event_kind=signal.event_kind,
            subject=signal.subject,
            sender_domain=signal.sender_domain,
            received_at=signal.received_at,
            raw_ref=signal.raw_ref,
        ),
    )

    detection_payload = _detect(signal, active_policy_state)
    detection = submit_detection_result(
        context,
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=config.detection_agent_id,
        parent_record_id=ingest.record.record_id,
        payload=detection_payload,
    )

    risk_payload = _score(detection_payload)
    risk_score = submit_risk_score(
        context,
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=config.scoring_agent_id,
        parent_record_id=detection.record.record_id,
        payload=risk_payload,
    )

    workflow_trigger = None
    if risk_payload.score > config.risk_threshold:
        workflow_trigger = trigger_workflow(
            context,
            tenant_id=tenant_id,
            environment=Environment.PRODUCTION,
            source_agent=config.orchestrator_agent_id,
            parent_record_id=risk_score.record.record_id,
            payload=WorkflowTriggerPayload(
                workflow_name=config.workflow_name,
                reason=f"risk score {risk_payload.score} met threshold {config.risk_threshold}",
                priority="high" if risk_payload.risk_level == "high" else "normal",
            ),
        )

    audit = submit_audit_verdict(
        context,
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=config.audit_agent_id,
        parent_record_id=(workflow_trigger or risk_score).record.record_id,
        payload=AuditVerdictPayload(
            target_record_id=(workflow_trigger or risk_score).record.record_id,
            verdict=AuditStatus.APPROVED,
            findings=["production cycle records validated"],
            requires_human_review=False,
        ),
    )

    weakness_report = None
    if detection_payload.confidence < config.confidence_threshold:
        # Multi-tenant isolation spec (§§ 2, 4, 5) requires production
        # weakness reports to ship to the per-tenant sandbox so a second
        # tenant cannot read another tenant's failure signal out of a
        # shared sandbox bucket. The demo pair (``tenant_demo`` paired
        # with ``sandbox_default``) is preserved as the explicit
        # historical exception called out in the spec, matching the
        # AlertSubscriber and PolicyConsumer override pattern below.
        weakness_sandbox = (
            "sandbox_default"
            if tenant_id == "tenant_demo"
            else default_sandbox_tenant_for(tenant_id)
        )
        weakness_report = submit_weakness_report(
            context,
            source_agent=config.detection_agent_id,
            parent_record_id=detection.record.record_id,
            sandbox_tenant_id=weakness_sandbox,
            payload=_weakness_report(signal, detection_payload),
        )

    alert_subscriber_result: AlertSubscriptionResult | None = None
    if config.run_alert_subscriber_at_end_of_cycle:
        subscriber_config = config.alert_subscriber_config or AlertSubscriberConfig()
        if subscriber_config.production_tenant_id != tenant_id:
            # Cycle tenant override. Per the multi-tenant isolation spec
            # the sandbox tenant id is recomputed from the cycle tenant
            # via the helper so signed policy updates land in the
            # per-tenant sandbox (e.g. ``sandbox_acme_ca`` for
            # ``acme_ca``). Existing demo flows keep working because they
            # do not trigger this branch (the default config already
            # carries ``tenant_demo``).
            subscriber_config = AlertSubscriberConfig(
                production_tenant_id=tenant_id,
                sandbox_tenant_id=default_sandbox_tenant_for(tenant_id),
                alert_workflow_id=subscriber_config.alert_workflow_id,
                consumed_workflow_id=subscriber_config.consumed_workflow_id,
                alert_agent_id=subscriber_config.alert_agent_id,
                signing_key=subscriber_config.signing_key,
            )
        alert_subscriber_result = run_alert_subscriber_cycle(
            context,
            config=subscriber_config,
        )

    policy_apply: PolicyConsumerResult | None = None
    if config.apply_pending_policies_at_end_of_cycle:
        consumer_config = config.policy_consumer_config or PolicyConsumerConfig()
        if consumer_config.production_tenant_id != tenant_id:
            consumer_config = PolicyConsumerConfig(
                production_tenant_id=tenant_id,
                sandbox_tenant_id=default_sandbox_tenant_for(tenant_id),
                governance_agent_id=consumer_config.governance_agent_id,
                signing_key=consumer_config.signing_key,
            )
        policy_apply = apply_pending_policies(
            context,
            config=consumer_config,
        )

    regression_detector_result: RegressionDetectorResult | None = None
    if config.run_regression_detector_at_end_of_cycle:
        detector_config = config.regression_detector_config or RegressionDetectorConfig()
        if detector_config.production_tenant_id != tenant_id:
            detector_config = RegressionDetectorConfig(
                production_tenant_id=tenant_id,
                detector_agent_id=detector_config.detector_agent_id,
                minimum_samples=detector_config.minimum_samples,
                alert_ratio_threshold=detector_config.alert_ratio_threshold,
                risk_score_threshold=detector_config.risk_score_threshold,
                detection_confidence_threshold=detector_config.detection_confidence_threshold,
                checked_workflow_id=detector_config.checked_workflow_id,
            )
        regression_detector_result = run_regression_detector_cycle(
            context,
            config=detector_config,
        )

    email_risk_scoring_result: EmailRiskScoringResult | None = None
    if config.run_email_risk_scoring_at_end_of_cycle:
        if config.email_risk_scoring_config is None:
            raise ValueError(
                "run_email_risk_scoring_at_end_of_cycle=True requires "
                "ProductionLoopConfig.email_risk_scoring_config to provide an llm_client"
            )
        scoring_config = config.email_risk_scoring_config
        # Phase 2.1 (Month 6) — resolve effective tenant parameters from
        # code defaults -> signed policy state -> optional per-tenant
        # override. The override resolver ignores missing / invalid /
        # expired / paused / revoked override files and appends a local
        # audit event for operator review, so the production loop keeps
        # running on the signed policy baseline.
        effective_parameters = resolve_effective_parameters(
            blackboard_root=context.blackboard_root,
            tenant_id=tenant_id,
            policy_parameters=active_policy_state.parameters,
        )
        fraud_lift = _coerce_int_parameter(
            effective_parameters.get("fraud_risk_floor_lift", 0)
        )
        attachment_lift = _coerce_int_parameter(
            effective_parameters.get("attachment_risk_floor_lift", 0)
        )
        url_lift = _coerce_int_parameter(
            effective_parameters.get("url_obfuscation_floor_lift", 0)
        )
        needs_rebuild = (
            scoring_config.production_tenant_id != tenant_id
            or scoring_config.fraud_risk_floor_lift != fraud_lift
            or scoring_config.attachment_risk_floor_lift != attachment_lift
            or scoring_config.url_obfuscation_floor_lift != url_lift
        )
        if needs_rebuild:
            scoring_config = EmailRiskScoringConfig(
                llm_client=scoring_config.llm_client,
                production_tenant_id=tenant_id,
                scoring_agent_id=scoring_config.scoring_agent_id,
                marker_agent_id=scoring_config.marker_agent_id,
                marker_workflow_id=scoring_config.marker_workflow_id,
                max_summary_chars=scoring_config.max_summary_chars,
                max_action_items=scoring_config.max_action_items,
                enable_ransomware_precursor_overlay=(
                    scoring_config.enable_ransomware_precursor_overlay
                ),
                fraud_risk_floor_lift=fraud_lift,
                attachment_risk_floor_lift=attachment_lift,
                url_obfuscation_floor_lift=url_lift,
                # Preserve the operator-supplied client-facing rubric flag
                # through the production-loop rebuild path. Without this,
                # activation set on the incoming EmailRiskScoringConfig
                # silently reverts to the dataclass default (False) any time
                # tenant_id or the Phase 1.4 lifts force a rebuild —
                # i.e. on every real production cycle.
                enable_client_facing_rubric=(
                    scoring_config.enable_client_facing_rubric
                ),
            )
        email_risk_scoring_result = run_email_risk_scoring_cycle(
            context,
            config=scoring_config,
        )

    daily_digest_result: DailyDigestResult | None = None
    if config.run_daily_digest_at_end_of_cycle:
        if config.daily_digest_config is None:
            raise ValueError(
                "run_daily_digest_at_end_of_cycle=True requires "
                "ProductionLoopConfig.daily_digest_config to provide an llm_client"
            )
        digest_config = config.daily_digest_config
        if digest_config.production_tenant_id != tenant_id:
            digest_config = DailyDigestConfig(
                llm_client=digest_config.llm_client,
                production_tenant_id=tenant_id,
                drafting_agent_id=digest_config.drafting_agent_id,
                digest_date=digest_config.digest_date,
                digest_window_hours=digest_config.digest_window_hours,
                now_provider=digest_config.now_provider,
                send_workflow_name=digest_config.send_workflow_name,
                digest_workflow_id=digest_config.digest_workflow_id,
            )
        daily_digest_result = run_daily_digest_cycle(
            context,
            config=digest_config,
        )

    return ProductionLoopResult(
        ingest=ingest,
        detection=detection,
        risk_score=risk_score,
        workflow_trigger=workflow_trigger,
        audit=audit,
        weakness_report=weakness_report,
        active_policy_state=active_policy_state,
        policy_apply=policy_apply,
        alert_subscriber=alert_subscriber_result,
        regression_detector=regression_detector_result,
        email_risk_scoring=email_risk_scoring_result,
        daily_digest=daily_digest_result,
    )
