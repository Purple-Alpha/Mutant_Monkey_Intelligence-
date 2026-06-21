"""Evidence Stage 1 proof for swarm agent #52 Plain-English Explanation.

Authorized by the §11-SIGNED Plain-English Explanation Agent Design Contract
(2026-06-20). Synthetic tests prove deterministic rubric projection usage,
read-only purity, tenant isolation, missing-input refusal, per-line
traceability, registry-default exclusion, and no raw-source read / send /
Blackboard write / network / subprocess behavior at Stage 1.
"""

from __future__ import annotations

import inspect
import socket
import subprocess
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from core.blackboard import (
    BlackboardRecord,
    EmailAnalysisImpersonationAnalysis,
    EmailAnalysisPayload,
    EmailAnalysisRiskAnalysis,
    Environment,
    GovernanceError,
    RecordType,
    append_record,
)
from core.orchestrator import Agent, MissionContext, RouteContext
from core.orchestrator import plain_english_explanation_agent as pea
from core.orchestrator.plain_english_explanation_agent import (
    PLAIN_ENGLISH_EXPLANATION_AGENT_ID,
    PlainEnglishExplanationAgent,
    REFUSAL_ENVELOPE,
    attach_plain_english_explanation,
    explain_payload,
    format_insufficient_refusal,
)
from core.orchestrator.registry import build_default_registry
from core.orchestrator.routes import blackboard_path
from core.scoring.client_facing_rubric import project_client_facing_rubric

TENANT_A = "tenant_plain_english_a"
TENANT_B = "tenant_plain_english_b"

_LOCKED_AXIS_ORDER = (
    "sender_identity",
    "conversation_continuity",
    "vendor_payment_history",
    "document_integrity",
    "origin_timing",
)

_FORBIDDEN_LEAK_PATTERNS = (
    "Received:",
    "From:",
    "payment@",
    "compliant",
    "certified",
    "insurance policy",
)


@pytest.fixture(autouse=True)
def isolated_blackboard_root(tmp_path, monkeypatch):
    root = tmp_path / "workspace"
    root.mkdir()
    monkeypatch.chdir(root)


def _payload(
    *,
    tenant_marker: str = "a",
    risk_score: int = 50,
    recommended_action: str = "needs_review",
) -> EmailAnalysisPayload:
    return EmailAnalysisPayload(
        source_email_record_id=uuid4(),
        produced_at=datetime.now(timezone.utc),
        summary=None,
        action_items=[],
        risk_analysis=EmailAnalysisRiskAnalysis(
            risk_score=risk_score,
            risk_factors=[f"marker_{tenant_marker}"],
            phishing_signals=[],
            urgency_signals=[],
            financial_risk="medium",
            vendor_fraud_score=30,
            wire_transfer_anomaly_score=20,
            invoice_authenticity_score=None,
            behavioral_deviation_flags=[],
        ),
        impersonation_analysis=EmailAnalysisImpersonationAnalysis(
            impersonation_likelihood=20,
            suspicious_elements=[],
            sender_legitimacy_notes=None,
        ),
        recommended_action=recommended_action,
        forced_escalation_triggers=[],
    )


def _agent(analysis: EmailAnalysisPayload | None = None) -> PlainEnglishExplanationAgent:
    return PlainEnglishExplanationAgent(analysis=analysis)


def _context(
    *,
    tenant_id: str = TENANT_A,
    source_record_id=None,
) -> MissionContext:
    return MissionContext(
        tenant_id=tenant_id,
        inputs_digest="a" * 64,
        source_record_id=source_record_id,
    )


def test_plain_english_explanation_agent_satisfies_agent_protocol():
    assert isinstance(_agent(_payload()), Agent)


def test_known_payload_projects_five_axes_in_fixed_order():
    result = explain_payload(_payload())
    assert result.kind == "explanation"
    rubric = result.analysis.client_facing_rubric
    assert rubric is not None
    assert len(rubric.axes) == 5
    assert tuple(axis.axis_name for axis in rubric.axes) == _LOCKED_AXIS_ORDER


def test_why_this_score_respects_cap_and_has_no_leakage():
    result = explain_payload(_payload(risk_score=82))
    rubric = result.analysis.client_facing_rubric
    assert rubric is not None
    for axis in rubric.axes:
        assert len(axis.why_this_score) <= 160
        lowered = axis.why_this_score.lower()
        for pattern in _FORBIDDEN_LEAK_PATTERNS:
            assert pattern.lower() not in lowered


def test_wrapper_does_not_mutate_risk_score_or_recommended_action():
    original = _payload(risk_score=61, recommended_action="block")
    before_risk = original.risk_analysis.risk_score
    before_action = original.recommended_action
    updated = attach_plain_english_explanation(original)
    assert updated.risk_analysis.risk_score == before_risk
    assert updated.recommended_action == before_action
    assert original.client_facing_rubric is None


def test_wrapper_source_does_not_read_email_inbound_records():
    source = inspect.getsource(pea)
    for forbidden in (
        "RecordType.EMAIL_INBOUND",
        "EmailInboundPayload",
        "submit_email_inbound",
    ):
        assert forbidden not in source


def test_wrapper_source_has_no_send_or_transmit_path():
    source = inspect.getsource(pea.PlainEnglishExplanationAgent)
    lowered = source.lower()
    assert "smtp" not in lowered
    assert "sendmail" not in lowered
    assert "transmit" not in lowered


def test_stage1_performs_no_blackboard_writes(tmp_path):
    root = tmp_path / "blackboard"
    env_dir = root / Environment.PRODUCTION.value
    env_dir.mkdir(parents=True)
    path = env_dir / f"{TENANT_A}.jsonl"
    path.write_text("", encoding="utf-8")
    before = path.read_text(encoding="utf-8")
    agent = _agent(_payload())
    result = agent.explain_for_mission(_context())
    assert result.kind == "explanation"
    assert path.read_text(encoding="utf-8") == before


def test_tenant_isolation_on_direct_payloads():
    payload_a = _payload(tenant_marker="tenant_a_only")
    payload_b = _payload(tenant_marker="tenant_b_only")
    result_a = explain_payload(payload_a)
    result_b = explain_payload(payload_b)
    assert result_a.analysis.risk_analysis.risk_factors != result_b.analysis.risk_analysis.risk_factors


def test_plain_english_explanation_not_in_default_registry():
    assert PLAIN_ENGLISH_EXPLANATION_AGENT_ID not in build_default_registry()


def test_wrapper_does_no_network_or_subprocess(monkeypatch):
    def _no_network(*args, **kwargs):
        raise AssertionError("plain english wrapper must not open network sockets")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("plain english wrapper must not spawn subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)
    result = _agent(_payload()).explain_for_mission(_context())
    assert result.kind == "explanation"


def test_missing_source_record_id_emits_refusal_without_rubric():
    result = _agent().explain_for_mission(_context(source_record_id=None))
    assert result.kind == "refusal"
    assert REFUSAL_ENVELOPE in result.refusal
    assert "source_record_id" in result.refusal
    assert "missing_fields:" in result.refusal
    assert result.analysis is None


def test_per_line_traceability_matches_direct_mapper_output():
    payload = _payload(risk_score=77)
    expected = project_client_facing_rubric(payload)
    result = explain_payload(payload)
    actual = result.analysis.client_facing_rubric
    assert actual is not None
    assert actual.model_dump() == expected.model_dump()


def test_missing_analysis_sub_object_emits_refusal():
    broken = EmailAnalysisPayload.model_construct(
        source_email_record_id=uuid4(),
        produced_at=datetime.now(timezone.utc),
        action_items=[],
        risk_analysis=None,
        impersonation_analysis=EmailAnalysisImpersonationAnalysis(
            impersonation_likelihood=0,
            suspicious_elements=[],
            sender_legitimacy_notes=None,
        ),
        recommended_action="safe",
        forced_escalation_triggers=[],
    )
    result = explain_payload(broken)
    assert result.kind == "refusal"
    assert "risk_analysis" in result.missing_fields


def test_blackboard_read_path_projects_explanation(tmp_path):
    root = tmp_path / "blackboard"
    record_id = uuid4()
    payload = _payload()
    record = BlackboardRecord(
        record_id=record_id,
        tenant_id=TENANT_A,
        environment=Environment.PRODUCTION,
        record_type=RecordType.EMAIL_ANALYSIS,
        source_agent="email_risk_scoring_001",
        payload=payload.model_dump(mode="json"),
    )
    path = blackboard_path(root, Environment.PRODUCTION, TENANT_A)
    path.parent.mkdir(parents=True, exist_ok=True)
    append_record(path, record)
    route_ctx = RouteContext(blackboard_root=root, registry={})
    agent = PlainEnglishExplanationAgent(
        route_context=route_ctx, environment=Environment.PRODUCTION
    )
    result = agent.explain_for_mission(
        _context(tenant_id=TENANT_A, source_record_id=record_id)
    )
    assert result.kind == "explanation"
    assert result.analysis.client_facing_rubric is not None


def test_analyze_raises_on_refusal():
    agent = _agent()
    with pytest.raises(GovernanceError, match=REFUSAL_ENVELOPE):
        agent.analyze(_context(source_record_id=None))


def test_refusal_formatter_matches_contract_shape():
    text = format_insufficient_refusal(("source_record_id",))
    assert text.startswith(f"{REFUSAL_ENVELOPE}\n")
    assert "- source_record_id" in text
    assert "no AUTH-5" in text
