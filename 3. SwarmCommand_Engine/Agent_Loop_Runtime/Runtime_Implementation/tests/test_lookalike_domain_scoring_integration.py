"""Lookalike Domain Detector scoring-agent integration tests.

Pass 1 build slice for the §11-signed Lookalike Domain Detector. The pure
detector tests own technique coverage; these tests prove the runtime boundary:
default-off no-regression, explicit opt-in, From + Reply-To surface, max-merge
floor lift, existing behavioral flag append, attach-always when enabled, and
no autonomous action-word mutation.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Callable
from uuid import UUID

from core.blackboard import (
    EmailAnalysisPayload,
    EmailInboundPayload,
    Environment,
    RecordType,
    read_records,
)
from core.orchestrator import RouteContext, submit_email_inbound
from core.orchestrator.routes import blackboard_path
from core.scoring import EmailRiskScoringConfig, run_email_risk_scoring_cycle
from core.scoring.lookalike_domain_detector import LOOKALIKE_SENDER_DOMAIN_FLAG

TENANT = "tenant_demo"


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _seed_inbound(
    context: RouteContext,
    *,
    sender: str = "billing@harborllne.example",
    headers: dict[str, str] | None = None,
    tenant_id: str = TENANT,
) -> UUID:
    payload = EmailInboundPayload(
        received_at=datetime(2026, 6, 5, 12, 0, tzinfo=timezone.utc),
        sender=sender,
        recipient="ap@northstar-customer.example",
        subject="Invoice attached",
        body_plain="Please review the attached invoice.",
        headers=headers or {},
    )
    result = submit_email_inbound(
        context,
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        source_agent="orchestrator_001",
        payload=payload,
    )
    return result.record.record_id


def _valid_analysis_json(
    *,
    risk_score: int = 10,
    recommended_action: str = "safe",
    behavioral_deviation_flags: list[str] | None = None,
) -> str:
    payload = {
        "summary": "Vendor email under review.",
        "action_items": [],
        "risk_analysis": {
            "risk_score": risk_score,
            "risk_factors": [],
            "phishing_signals": [],
            "urgency_signals": [],
            "financial_risk": "low",
            "vendor_fraud_score": 10,
            "wire_transfer_anomaly_score": 10,
            "invoice_authenticity_score": None,
            "behavioral_deviation_flags": list(behavioral_deviation_flags or []),
        },
        "impersonation_analysis": {
            "impersonation_likelihood": 10,
            "suspicious_elements": [],
            "sender_legitimacy_notes": "first contact",
        },
        "recommended_action": recommended_action,
    }
    return json.dumps(payload)


def _canned_client(response: str) -> Callable[[str, str], str]:
    def _client(system_prompt: str, user_prompt: str) -> str:
        assert "NorthStar Inbox Shield" in system_prompt
        json.loads(user_prompt)
        return response

    return _client


def _analysis(context: RouteContext) -> EmailAnalysisPayload:
    records = [
        r
        for r in read_records(
            blackboard_path(context.blackboard_root, Environment.PRODUCTION, TENANT)
        )
        if r.record_type == RecordType.EMAIL_ANALYSIS
    ]
    assert len(records) == 1
    return EmailAnalysisPayload.model_validate(records[0].payload)


def test_default_off_no_lookalike_assessment_flag_or_lift(tmp_path) -> None:
    context = _context(tmp_path)
    _seed_inbound(context, sender="billing@harborllne.example")

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
            production_tenant_id=TENANT,
            lookalike_known_good_domains=("harborline.example",),
        ),
    )

    assert result.analyzed == 1
    parsed = _analysis(context)
    assert parsed.lookalike_domain_assessment is None
    assert LOOKALIKE_SENDER_DOMAIN_FLAG not in parsed.risk_analysis.behavioral_deviation_flags
    assert parsed.risk_analysis.risk_score == 10


def test_enabled_lookalike_from_domain_attaches_flag_and_floor_lift(tmp_path) -> None:
    context = _context(tmp_path)
    _seed_inbound(context, sender="billing@harborllne.example")

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=10)),
            production_tenant_id=TENANT,
            enable_lookalike_domain_detection=True,
            lookalike_known_good_domains=("harborline.example",),
        ),
    )

    assert result.analyzed == 1
    parsed = _analysis(context)
    assert parsed.lookalike_domain_assessment is not None
    assert parsed.lookalike_domain_assessment.fired is True
    assert parsed.lookalike_domain_assessment.recommended_risk_floor_lift == 85
    assert parsed.risk_analysis.risk_score == 85
    assert LOOKALIKE_SENDER_DOMAIN_FLAG in parsed.risk_analysis.behavioral_deviation_flags
    assert parsed.recommended_action == "safe", "Stage A detector must not rewrite action verbs"


def test_enabled_lookalike_reply_to_surface_fires(tmp_path) -> None:
    context = _context(tmp_path)
    _seed_inbound(
        context,
        sender="ap@trusted.example",
        headers={"Reply-To": "payments@harborllne.example"},
    )

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=25)),
            production_tenant_id=TENANT,
            enable_lookalike_domain_detection=True,
            lookalike_known_good_domains=("trusted.example", "harborline.example"),
        ),
    )

    parsed = _analysis(context)
    assert parsed.lookalike_domain_assessment is not None
    assert parsed.lookalike_domain_assessment.fired is True
    assert parsed.lookalike_domain_assessment.findings[0].offending_domain == "harborllne.example"
    assert parsed.risk_analysis.risk_score == 85


def test_enabled_without_known_good_set_attaches_non_fired_assessment(tmp_path) -> None:
    context = _context(tmp_path)
    _seed_inbound(context, sender="billing@harborllne.example")

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=33)),
            production_tenant_id=TENANT,
            enable_lookalike_domain_detection=True,
            lookalike_known_good_domains=(),
        ),
    )

    parsed = _analysis(context)
    assert parsed.lookalike_domain_assessment is not None
    assert parsed.lookalike_domain_assessment.fired is False
    assert parsed.risk_analysis.risk_score == 33
    assert LOOKALIKE_SENDER_DOMAIN_FLAG not in parsed.risk_analysis.behavioral_deviation_flags


def test_lookalike_floor_is_max_merge_not_lowering(tmp_path) -> None:
    context = _context(tmp_path)
    _seed_inbound(context, sender="billing@harborllne.example")

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_score=95)),
            production_tenant_id=TENANT,
            enable_lookalike_domain_detection=True,
            lookalike_known_good_domains=("harborline.example",),
        ),
    )

    parsed = _analysis(context)
    assert parsed.lookalike_domain_assessment is not None
    assert parsed.lookalike_domain_assessment.fired is True
    assert parsed.risk_analysis.risk_score == 95


def test_existing_lookalike_flag_is_not_duplicated(tmp_path) -> None:
    context = _context(tmp_path)
    _seed_inbound(context, sender="billing@harborllne.example")

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(
                _valid_analysis_json(
                    risk_score=10,
                    behavioral_deviation_flags=[LOOKALIKE_SENDER_DOMAIN_FLAG],
                )
            ),
            production_tenant_id=TENANT,
            enable_lookalike_domain_detection=True,
            lookalike_known_good_domains=("harborline.example",),
        ),
    )

    parsed = _analysis(context)
    assert parsed.risk_analysis.behavioral_deviation_flags.count(
        LOOKALIKE_SENDER_DOMAIN_FLAG
    ) == 1
