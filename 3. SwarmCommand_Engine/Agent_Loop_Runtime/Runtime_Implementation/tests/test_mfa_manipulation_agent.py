"""Evidence Stage 1 proof that the governed-agent contract holds on the
MFA-fatigue body-signal output (swarm agent #24 MFA Manipulation).

Authorized by the §11-SIGNED MFA Manipulation Agent Design Contract
(2026-06-08). These are the synthetic-fixture tests that constitute the Stage 1
evidence: known-bad fire, known-good no-fire, single-indicator firing,
HTML-only and subject-only surface handling, numeric one-time-code no-leak,
persistence, guardrails, registry-default exclusion, purity (no baseline write /
no network / no subprocess), and no score / raw-phrase / one-time-code /
body-subject leakage.
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
from core.orchestrator import mfa_manipulation_agent as mma
from core.orchestrator.mfa_manipulation_agent import (
    MFA_MANIPULATION_AGENT_ID,
    MFAManipulationAgent,
    digest_email,
)
from core.orchestrator.registry import build_default_registry
from core.orchestrator.routes import submit_email_inbound

_INGEST_AGENT_ID = "ingest_001"

# Closed MFA-manipulation indicator vocabulary the detector can emit. Used to
# assert facts-only output and no raw-phrase / one-time-code / score leakage.
_KNOWN_MFA_INDICATORS = frozenset(
    {
        "mfa_push_language",
        "verification_code_language",
    }
)

# Raw lure phrases / codes used in fixtures - must never leak into a contribution
# fact.
_RAW_LURE_PHRASES = (
    "tap approve",
    "approve the sign-in",
    "verification code",
    "your code is",
    "123456",
)


def _mfa_agent_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=MFA_MANIPULATION_AGENT_ID,
        display_name="MFA Manipulation Agent",
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
    return {e.agent_id: e for e in (_mfa_agent_entry(), _ingest_entry())}


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
        sender="it-security@vendor.example",
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


def _agent(route_ctx: RouteContext) -> MFAManipulationAgent:
    return MFAManipulationAgent(
        blackboard_root=route_ctx.blackboard_root,
        environment=Environment.PRODUCTION,
    )


def test_mfa_manipulation_agent_satisfies_agent_protocol(tmp_path):
    assert isinstance(_agent(_route_ctx(tmp_path)), Agent)


def test_known_bad_email_produces_both_indicator_facts_and_suspicious(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        subject="Action required",
        body_plain=(
            "We detected a sign-in attempt. Please tap approve on the prompt "
            "and enter the verification code we just sent to confirm it is you."
        ),
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert len(der.contributions) == 1
    contribution = der.contributions[0]
    assert contribution.agent_id == MFA_MANIPULATION_AGENT_ID
    assert contribution.layer == 2
    # Facts only, in detector order (mfa-push before verification-code);
    # no numeric score surfaced.
    assert contribution.observed_facts == (
        "mfa_push_language",
        "verification_code_language",
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


def test_mfa_push_language_only(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="Someone is trying to sign in. Approve the request on your phone to continue.",
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert der.contributions[0].observed_facts == ("mfa_push_language",)
    assert der.disposition == "suspicious"


def test_verification_code_language_only(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="Please read back your one-time passcode so we can finish verification.",
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert der.contributions[0].observed_facts == ("verification_code_language",)
    assert der.disposition == "suspicious"


def test_lure_in_html_only_is_detected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="Hello, see the message below.",
        body_html="<p>Please <strong>tap approve</strong> on your phone now.</p>",
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert der.contributions[0].observed_facts == ("mfa_push_language",)
    assert der.disposition == "suspicious"


def test_lure_in_subject_only_is_detected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        subject="Your verification code is waiting",
        body_plain="Regards, IT.",
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert der.contributions[0].observed_facts == ("verification_code_language",)
    assert der.disposition == "suspicious"


def test_numeric_one_time_code_does_not_leak_code_or_score(tmp_path):
    # A numeric "code: 123456" lure raises the detector's internal score
    # but the contribution still carries only the closed indicator names.
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="Your code is: 123456. Approve the sign-in to keep your account.",
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    facts = der.contributions[0].observed_facts
    assert facts == ("mfa_push_language", "verification_code_language")
    for fact in facts:
        assert "123456" not in fact
        assert not any(ch.isdigit() for ch in fact)


def test_contribution_persists_to_blackboard_and_reads_back(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="Approve the request on your phone to restore access.",
    )
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx)
    der = SwarmCommander(_registry()).run_case(context, [agent])

    write = agent.persist_contribution(route_ctx, context, der.contributions[0])
    assert write.record.record_type == RecordType.AGENT_CONTRIBUTION
    assert write.record.source_agent == MFA_MANIPULATION_AGENT_ID

    persisted = [
        r
        for r in read_records(write.path)
        if r.record_type == RecordType.AGENT_CONTRIBUTION
    ]
    assert len(persisted) == 1
    payload_back = AgentContributionPayload.model_validate(persisted[0].payload)
    assert payload_back.agent_id == MFA_MANIPULATION_AGENT_ID
    assert payload_back.case_id == context.case_id
    assert payload_back.inputs_digest == context.inputs_digest
    assert payload_back.observed_facts == ["mfa_push_language"]


def test_challenge_returns_none(tmp_path):
    assert _agent(_route_ctx(tmp_path)).challenge(()) is None


def test_missing_source_record_id_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    context = MissionContext(tenant_id="tenant_demo", inputs_digest="a" * 64)
    with pytest.raises(GovernanceError, match="source_record_id"):
        _agent(route_ctx).analyze(context)


def test_unknown_source_record_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    _seed_email(route_ctx, body_plain="tap approve")
    context = MissionContext(
        tenant_id="tenant_demo", inputs_digest="a" * 64, source_record_id=uuid4()
    )
    with pytest.raises(GovernanceError, match="not found"):
        _agent(route_ctx).analyze(context)


def test_source_record_of_wrong_type_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="tap approve",
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
        observed_facts=["mfa_push_language"],
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
        sender="it-security@vendor.example",
        recipient="ap@buyer.example",
        subject="your verification code",
        body_plain="tap approve",
    )
    assert digest_email(payload) == digest_email(payload)
    assert len(digest_email(payload)) == 64


def test_mfa_manipulation_not_in_default_registry(tmp_path):
    # Evidence Stage 1: explicitly excluded from production dispatch.
    assert MFA_MANIPULATION_AGENT_ID not in build_default_registry()


def test_contribution_carries_no_score_or_raw_phrase(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        subject="Your verification code is waiting",
        body_plain="Tap approve on the prompt; your code is: 123456.",
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    facts = der.contributions[0].observed_facts
    # Every emitted fact is a closed indicator name - no raw matched phrase,
    # one-time code, body substring, subject string, or numeric score crosses
    # into the contribution.
    assert all(fact in _KNOWN_MFA_INDICATORS for fact in facts)
    for fact in facts:
        for phrase in _RAW_LURE_PHRASES:
            assert phrase not in fact
        assert not any(ch.isdigit() for ch in fact)


def test_wrapper_does_no_baseline_network_or_subprocess(tmp_path, monkeypatch):
    """D8 purity: analyze() must not open sockets, spawn subprocesses, or write
    any baseline/memory store; it only calls the pure body-signal detector over
    the stored email text surfaces (body_plain, body_html, subject)."""

    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        subject="Your verification code is waiting",
        body_plain="Tap approve on the prompt.",
        body_html="<p>tap approve</p>",
    )

    def _no_network(*args, **kwargs):
        raise AssertionError("mfa manipulation wrapper must not open a socket")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("mfa manipulation wrapper must not spawn a subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)

    # Delegation spy: the wrapper must call the pure detector once with all three
    # text surfaces and derive its facts solely from that return value.
    calls: list[tuple] = []
    real_score = mma.score_mfa_fatigue

    def _spy(*texts):
        calls.append(texts)
        return real_score(*texts)

    monkeypatch.setattr(mma, "score_mfa_fatigue", _spy)

    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert calls == [
        ("Tap approve on the prompt.", "<p>tap approve</p>", "Your verification code is waiting")
    ]
    assert der.contributions[0].observed_facts == (
        "mfa_push_language",
        "verification_code_language",
    )
