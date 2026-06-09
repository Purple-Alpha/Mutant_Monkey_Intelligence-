"""Evidence Stage 1 proof that the governed-agent contract holds on the
callback-phishing body-language output (swarm agent #39 Language Pressure).

Authorized by the §11-SIGNED Language Pressure Agent Design Contract
(2026-06-08, the first agent selected by the LIVE Build Map). These are the
synthetic-fixture tests that constitute the Stage 1 evidence: known-bad fire,
known-good no-fire, per-category firing, multi-category deterministic order,
body_plain-only input boundary, persistence, guardrails, registry-default
exclusion, purity (no baseline write / no network / no subprocess), and no
risk-floor / category-explanation / raw-phrase / phone-number leakage.
"""

import socket
import subprocess
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from core.blackboard import (
    AgentRegistryEntry,
    AgentRole,
    EmailInboundPayload,
    Environment,
    GovernanceError,
    RecordType,
    read_records,
)
from core.blackboard.models import AgentContributionPayload
from core.orchestrator import (
    Agent,
    MissionContext,
    RouteContext,
    SwarmCommander,
    submit_agent_contribution,
)
from core.orchestrator import language_pressure_agent as lpa
from core.orchestrator.language_pressure_agent import (
    LANGUAGE_PRESSURE_AGENT_ID,
    LanguagePressureAgent,
    digest_email,
)
from core.orchestrator.registry import build_default_registry
from core.orchestrator.routes import submit_email_inbound

_INGEST_AGENT_ID = "ingest_001"

# Closed TOAD v1 category vocabulary the detector can emit. Used to assert
# facts-only output and no raw-phrase / risk-floor / explanation leakage.
_KNOWN_CATEGORIES = frozenset(
    {
        "call_now_pressure",
        "do_not_use_known_channel",
        "voice_only_finalize",
        "support_line_substitution",
        "payment_redirect_call",
    }
)

# Raw lure phrases / digits used in fixtures - must never leak into a fact.
_RAW_LURE_PHRASES = (
    "call us immediately",
    "do not use the number on file",
    "call to confirm the new ach details",
    "555-123-4567",
)


def _lp_agent_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=LANGUAGE_PRESSURE_AGENT_ID,
        display_name="Language Pressure Agent",
        role=AgentRole.DETECTION,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.AGENT_CONTRIBUTION},
        layer=2,
        authority_level=3,
        stage_allowed="stage_a",
    )


def _ingest_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=_INGEST_AGENT_ID,
        display_name="Ingest",
        role=AgentRole.DETECTION,
        allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
        allowed_write_types={RecordType.EMAIL_INBOUND},
    )


def _registry() -> dict[str, AgentRegistryEntry]:
    return {e.agent_id: e for e in (_lp_agent_entry(), _ingest_entry())}


def _route_ctx(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard", registry=_registry())


def _seed_email(
    route_ctx: RouteContext,
    *,
    subject: str | None = "Vendor invoice approval",
    body_plain: str = "Please process the attached invoice.",
    body_html: str | None = None,
    tenant_id: str = "tenant_demo",
):
    payload = EmailInboundPayload(
        received_at=datetime.now(timezone.utc),
        sender="billing@vendor.example",
        recipient="ap@buyer.example",
        subject=subject,
        body_plain=body_plain,
        body_html=body_html,
        headers={},
        attachments=[],
    )
    result = submit_email_inbound(
        route_ctx,
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=_INGEST_AGENT_ID,
        payload=payload,
    )
    return result.record.record_id, payload


def _mission_context(record_id, payload, *, tenant_id: str = "tenant_demo") -> MissionContext:
    return MissionContext(
        tenant_id=tenant_id,
        inputs_digest=digest_email(payload),
        source_record_id=record_id,
    )


def _agent(route_ctx: RouteContext) -> LanguagePressureAgent:
    return LanguagePressureAgent(
        blackboard_root=route_ctx.blackboard_root,
        environment=Environment.PRODUCTION,
    )


def test_language_pressure_agent_satisfies_agent_protocol(tmp_path):
    assert isinstance(_agent(_route_ctx(tmp_path)), Agent)


def test_known_bad_email_produces_category_facts_in_order_and_suspicious(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        subject="Action required",
        body_plain=(
            "Call us immediately to resolve this. Do not use the number on file. "
            "Call to confirm the new ACH details."
        ),
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert len(der.contributions) == 1
    contribution = der.contributions[0]
    assert contribution.agent_id == LANGUAGE_PRESSURE_AGENT_ID
    assert contribution.layer == 2
    # Facts only, in fixed detector category order (call_now_pressure ->
    # do_not_use_known_channel -> payment_redirect_call); no risk-floor lift.
    assert contribution.observed_facts == (
        "call_now_pressure",
        "do_not_use_known_channel",
        "payment_redirect_call",
    )
    assert der.disposition == "suspicious"
    assert der.inputs_digest == digest_email(payload)
    assert len(der.inputs_digest) == 64


def test_known_good_business_email_is_clear(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        subject="Re: Q1 invoice schedule",
        body_plain="Thanks for the update - please confirm the meeting time for Thursday.",
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert der.contributions[0].observed_facts == ()
    assert der.disposition == "clear"


def test_call_now_pressure_only(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="Call us immediately to keep your account active.",
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert der.contributions[0].observed_facts == ("call_now_pressure",)
    assert der.disposition == "suspicious"


def test_voice_only_finalize_only(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="We cannot complete this over email; please phone us to finalize.",
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert der.contributions[0].observed_facts == ("voice_only_finalize",)
    assert der.disposition == "suspicious"


def test_support_line_substitution_only(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="Please call our updated support line to continue.",
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert der.contributions[0].observed_facts == ("support_line_substitution",)
    assert der.disposition == "suspicious"


def test_multi_category_dedupes_and_orders(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    # Two call_now_pressure phrasings plus one voice_only_finalize: the category
    # appears once (dedupe by construction) and order follows _CATEGORY_ORDER.
    record_id, payload = _seed_email(
        route_ctx,
        body_plain=(
            "Call us immediately. Do not delay - call now. "
            "We cannot complete this over email."
        ),
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert der.contributions[0].observed_facts == (
        "call_now_pressure",
        "voice_only_finalize",
    )


def test_lure_only_in_html_or_subject_is_not_read(tmp_path):
    # D4 / D14: the signed TOAD v1 detector reads body_plain only; lure language
    # placed only in body_html or subject must not produce a Stage 1 fact.
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        subject="Please call our updated support line",
        body_plain="Thanks, talk soon.",
        body_html="<p>Call us immediately. Do not use the number on file.</p>",
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert der.contributions[0].observed_facts == ()
    assert der.disposition == "clear"


def test_contribution_persists_to_blackboard_and_reads_back(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="Call us immediately to keep your account active.",
    )
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx)
    der = SwarmCommander(_registry()).run_case(context, [agent])

    write = agent.persist_contribution(route_ctx, context, der.contributions[0])
    assert write.record.record_type == RecordType.AGENT_CONTRIBUTION
    assert write.record.source_agent == LANGUAGE_PRESSURE_AGENT_ID

    persisted = [
        r
        for r in read_records(write.path)
        if r.record_type == RecordType.AGENT_CONTRIBUTION
    ]
    assert len(persisted) == 1
    payload_back = AgentContributionPayload.model_validate(persisted[0].payload)
    assert payload_back.agent_id == LANGUAGE_PRESSURE_AGENT_ID
    assert payload_back.case_id == context.case_id
    assert payload_back.inputs_digest == context.inputs_digest
    assert payload_back.observed_facts == ["call_now_pressure"]


def test_challenge_returns_none(tmp_path):
    assert _agent(_route_ctx(tmp_path)).challenge(()) is None


def test_missing_source_record_id_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    context = MissionContext(tenant_id="tenant_demo", inputs_digest="a" * 64)
    with pytest.raises(GovernanceError, match="source_record_id"):
        _agent(route_ctx).analyze(context)


def test_unknown_source_record_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    _seed_email(route_ctx, body_plain="call us immediately")
    context = MissionContext(
        tenant_id="tenant_demo", inputs_digest="a" * 64, source_record_id=uuid4()
    )
    with pytest.raises(GovernanceError, match="not found"):
        _agent(route_ctx).analyze(context)


def test_source_record_of_wrong_type_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="call us immediately",
    )
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx)
    der = SwarmCommander(_registry()).run_case(context, [agent])
    contribution_write = agent.persist_contribution(route_ctx, context, der.contributions[0])

    misdirected = MissionContext(
        tenant_id="tenant_demo",
        inputs_digest="a" * 64,
        source_record_id=contribution_write.record.record_id,
    )
    with pytest.raises(GovernanceError, match="not an email_inbound record"):
        agent.analyze(misdirected)


def test_unauthorized_agent_cannot_write_contribution(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    payload = AgentContributionPayload(
        case_id=uuid4(),
        inputs_digest="a" * 64,
        agent_id=_INGEST_AGENT_ID,
        layer=2,
        observed_facts=["call_now_pressure"],
    )
    with pytest.raises(GovernanceError, match="cannot write this record type"):
        submit_agent_contribution(
            route_ctx,
            tenant_id="tenant_demo",
            environment=Environment.PRODUCTION,
            source_agent=_INGEST_AGENT_ID,
            payload=payload,
        )


def test_digest_email_is_deterministic():
    payload = EmailInboundPayload(
        received_at=datetime(2026, 6, 8, tzinfo=timezone.utc),
        sender="billing@vendor.example",
        recipient="ap@buyer.example",
        subject="call our updated support line",
        body_plain="call us immediately",
    )
    assert digest_email(payload) == digest_email(payload)
    assert len(digest_email(payload)) == 64


def test_language_pressure_not_in_default_registry(tmp_path):
    # Evidence Stage 1: explicitly excluded from production dispatch.
    assert LANGUAGE_PRESSURE_AGENT_ID not in build_default_registry()


def test_contribution_carries_no_score_phrase_or_phone_number(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        subject="Action required",
        body_plain=(
            "Call us immediately at 555-123-4567. Do not use the number on file. "
            "Call to confirm the new ACH details."
        ),
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    facts = der.contributions[0].observed_facts
    # Every emitted fact is a closed category name - no risk-floor lift, no
    # category explanation, no raw matched phrase, no phone-number digit, and no
    # body substring crosses into the contribution.
    assert all(fact in _KNOWN_CATEGORIES for fact in facts)
    for fact in facts:
        for phrase in _RAW_LURE_PHRASES:
            assert phrase not in fact.lower()
        assert not any(ch.isdigit() for ch in fact)


def test_wrapper_does_no_baseline_network_or_subprocess(tmp_path, monkeypatch):
    """D8 purity: analyze() must not open sockets, spawn subprocesses, or write
    any baseline/memory store; it only calls the pure callback-phishing detector
    over the stored body_plain text surface (TOAD v1 D14 boundary)."""

    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        subject="Action required",
        body_plain="Call us immediately. Do not use the number on file.",
        body_html="<p>ignored html</p>",
    )

    def _no_network(*args, **kwargs):
        raise AssertionError("language pressure wrapper must not open a socket")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("language pressure wrapper must not spawn a subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)

    # Delegation spy: the wrapper must call the pure detector once with the
    # body_plain surface only and derive its facts solely from that return value.
    calls: list[str] = []
    real_detect = lpa.detect_callback_phishing

    def _spy(*, body_plain):
        calls.append(body_plain)
        return real_detect(body_plain=body_plain)

    monkeypatch.setattr(lpa, "detect_callback_phishing", _spy)

    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert calls == ["Call us immediately. Do not use the number on file."]
    assert der.contributions[0].observed_facts == (
        "call_now_pressure",
        "do_not_use_known_channel",
    )
