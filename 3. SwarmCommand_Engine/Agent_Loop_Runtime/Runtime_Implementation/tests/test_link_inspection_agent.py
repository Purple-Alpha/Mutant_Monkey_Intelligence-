"""Evidence Stage 1 proof that the governed-agent contract holds on the
URL-obfuscation detector output (swarm agent #27 Link Inspection).

Authorized by the §11-SIGNED Link Inspection Agent Design Contract
(2026-06-08). These are the synthetic-fixture tests that constitute the Stage 1
evidence: known-bad fire, known-good no-fire, HTML-only surface, persistence,
guardrails, registry-default exclusion, and no score / raw-URL leakage.
"""

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
    validate_record_payload,
)
from core.blackboard.models import AgentContributionPayload, BlackboardRecord
from core.orchestrator import (
    Agent,
    MissionContext,
    RouteContext,
    SwarmCommander,
    submit_agent_contribution,
)
from core.orchestrator.link_inspection_agent import (
    LINK_INSPECTION_AGENT_ID,
    LinkInspectionAgent,
    digest_email,
)
from core.orchestrator.registry import build_default_registry
from core.orchestrator.routes import submit_email_inbound

_INGEST_AGENT_ID = "ingest_001"

# Closed URL-obfuscation indicator vocabulary the detector can emit. Used to
# assert facts-only output and no raw-URL/score leakage.
_KNOWN_URL_INDICATORS = frozenset(
    {
        "credential_bearing_url",
        "url_shortener_present",
        "punycode_url_present",
        "homoglyph_url_present",
        "suspicious_tld_present",
        "ip_address_url_present",
        "login_path_url_present",
    }
)

# Credential-bearing + shortener + login-path: a strong, multi-indicator bad URL.
_BAD_URL_BODY = "Please confirm here: http://user:pass@bit.ly/verify"
# Punycode + login-path link that appears only in the rendered HTML surface.
_HTML_ONLY_BAD = '<a href="http://xn--pple-43d.com/login">Apple ID</a>'


def _link_agent_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=LINK_INSPECTION_AGENT_ID,
        display_name="Link Inspection Agent",
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
    return {e.agent_id: e for e in (_link_agent_entry(), _ingest_entry())}


def _route_ctx(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard", registry=_registry())


def _seed_email(
    route_ctx: RouteContext,
    *,
    body_plain: str = "Please process the attached invoice.",
    body_html: str | None = None,
    tenant_id: str = "tenant_demo",
):
    payload = EmailInboundPayload(
        received_at=datetime.now(timezone.utc),
        sender="billing@vendor.example",
        recipient="ap@buyer.example",
        subject="Vendor invoice approval",
        body_plain=body_plain,
        body_html=body_html,
        headers={},
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


def _agent(route_ctx: RouteContext) -> LinkInspectionAgent:
    return LinkInspectionAgent(
        blackboard_root=route_ctx.blackboard_root,
        environment=Environment.PRODUCTION,
    )


def test_link_inspection_agent_satisfies_agent_protocol(tmp_path):
    assert isinstance(_agent(_route_ctx(tmp_path)), Agent)


def test_known_bad_url_produces_indicator_facts_and_suspicious(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(route_ctx, body_plain=_BAD_URL_BODY)
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert len(der.contributions) == 1
    contribution = der.contributions[0]
    assert contribution.agent_id == LINK_INSPECTION_AGENT_ID
    assert contribution.layer == 2
    # Facts only, in detector order; no numeric score surfaced.
    assert contribution.observed_facts == (
        "credential_bearing_url",
        "url_shortener_present",
        "login_path_url_present",
    )
    assert der.disposition == "suspicious"
    assert der.inputs_digest == digest_email(payload)
    assert len(der.inputs_digest) == 64


def test_known_good_email_with_no_urls_produces_empty_facts_and_clear(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx, body_plain="Thanks for the update, talk tomorrow."
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert der.contributions[0].observed_facts == ()
    assert der.disposition == "clear"


def test_html_only_suspicious_url_is_included(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="See the message below.",
        body_html=_HTML_ONLY_BAD,
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    facts = der.contributions[0].observed_facts
    # The detector reads body_html too, so the HTML-only link still fires.
    assert "punycode_url_present" in facts
    assert "login_path_url_present" in facts
    assert der.disposition == "suspicious"


def test_contribution_persists_to_blackboard_and_reads_back(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(route_ctx, body_plain=_BAD_URL_BODY)
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx)
    der = SwarmCommander(_registry()).run_case(context, [agent])

    write = agent.persist_contribution(route_ctx, context, der.contributions[0])
    assert write.record.record_type == RecordType.AGENT_CONTRIBUTION
    assert write.record.source_agent == LINK_INSPECTION_AGENT_ID

    persisted = [
        r
        for r in read_records(write.path)
        if r.record_type == RecordType.AGENT_CONTRIBUTION
    ]
    assert len(persisted) == 1
    payload_back = AgentContributionPayload.model_validate(persisted[0].payload)
    assert payload_back.agent_id == LINK_INSPECTION_AGENT_ID
    assert payload_back.case_id == context.case_id
    assert payload_back.inputs_digest == context.inputs_digest
    assert payload_back.observed_facts == [
        "credential_bearing_url",
        "url_shortener_present",
        "login_path_url_present",
    ]


def test_challenge_returns_none(tmp_path):
    assert _agent(_route_ctx(tmp_path)).challenge(()) is None


def test_missing_source_record_id_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    context = MissionContext(tenant_id="tenant_demo", inputs_digest="a" * 64)
    with pytest.raises(GovernanceError, match="source_record_id"):
        _agent(route_ctx).analyze(context)


def test_unknown_source_record_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    _seed_email(route_ctx, body_plain=_BAD_URL_BODY)
    context = MissionContext(
        tenant_id="tenant_demo", inputs_digest="a" * 64, source_record_id=uuid4()
    )
    with pytest.raises(GovernanceError, match="not found"):
        _agent(route_ctx).analyze(context)


def test_source_record_of_wrong_type_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(route_ctx, body_plain=_BAD_URL_BODY)
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
        observed_facts=["url_shortener_present"],
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
        subject="invoice",
        body_plain="hello http://bit.ly/login",
    )
    assert digest_email(payload) == digest_email(payload)
    assert len(digest_email(payload)) == 64


def test_link_inspection_not_in_default_registry(tmp_path):
    # Evidence Stage 1: explicitly excluded from production dispatch.
    assert LINK_INSPECTION_AGENT_ID not in build_default_registry()


def test_contribution_carries_no_score_or_raw_url(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(route_ctx, body_plain=_BAD_URL_BODY)
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    facts = der.contributions[0].observed_facts
    # Every emitted fact is a closed indicator name - no raw URL, host, query,
    # body snippet, or numeric score crosses into the contribution.
    assert all(fact in _KNOWN_URL_INDICATORS for fact in facts)
    for fact in facts:
        assert "http" not in fact
        assert "bit.ly" not in fact
        assert "@" not in fact
        assert "/" not in fact
        assert not any(ch.isdigit() for ch in fact)
