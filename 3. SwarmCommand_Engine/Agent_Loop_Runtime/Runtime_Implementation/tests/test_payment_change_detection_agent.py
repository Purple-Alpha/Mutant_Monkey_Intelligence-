"""Evidence Stage 1 proof that the governed-agent contract holds on the
Financial State Ledger / Delta Tripwire detector output (swarm agent #14
Payment Change Detection).

Authorized by the §11-SIGNED Payment Change Detection Agent Design Contract
(2026-06-08). These are the synthetic-fixture tests that constitute the Stage 1
evidence: new/known/expired states, check-before-ingest preservation, tenant
isolation, kill-switch inheritance, persistence, guardrails, registry-default
exclusion, no-network/subprocess behavior, and no risk-floor / raw-financial-
string / hash / redacted-display leakage.
"""

from __future__ import annotations

import inspect
import socket
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from core.blackboard import (
    AgentRegistryEntry,
    AgentRole,
    EmailAttachmentMeta,
    EmailInboundPayload,
    Environment,
    GovernanceError,
    RecordType,
    read_records,
)
from core.blackboard.models import AgentContributionPayload
from core.operator_state import KillSwitchEngaged, engage_kill_switch
from core.orchestrator import (
    Agent,
    MissionContext,
    RouteContext,
    SwarmCommander,
    submit_agent_contribution,
)
from core.orchestrator import payment_change_detection_agent as pcda
from core.orchestrator.payment_change_detection_agent import (
    PAYMENT_CHANGE_DETECTION_AGENT_ID,
    PaymentChangeDetectionAgent,
    digest_email,
)
from core.orchestrator.registry import build_default_registry
from core.orchestrator.routes import submit_email_inbound
from core.production_state import vendor_baseline as vb
from core.production_state.vendor_baseline.store import SIGNAL_TYPES
from core.scoring import financial_state_ledger as fsl

_INGEST_AGENT_ID = "ingest_001"
TENANT = "tenant_pay_change_demo"
VENDOR = "vendor.example"
NOW = datetime(2026, 6, 8, 12, 0, tzinfo=timezone.utc)

# A first-seen routing number in payment context; normalizes to 9 digits.
_ROUTING_BODY = "Please remit payment to our updated bank. Routing number: 021000021"
_ROUTING_VALUE = "021000021"

_ALLOWED_FACT_PREFIXES = frozenset(
    {
        "new_payment_destination_signal",
        "expired_payment_destination_signal",
        "payment_signal_type:",
        "payment_signal_extracted_count:",
        "payment_delta_finding_count:",
    }
)


@pytest.fixture(autouse=True)
def isolated_blackboard_root(tmp_path, monkeypatch):
    root = tmp_path / "workspace"
    root.mkdir()
    monkeypatch.chdir(root)


def _agent_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=PAYMENT_CHANGE_DETECTION_AGENT_ID,
        display_name="Payment Change Detection Agent",
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
    return {e.agent_id: e for e in (_agent_entry(), _ingest_entry())}


def _route_ctx() -> RouteContext:
    return RouteContext(blackboard_root=Path("blackboard"), registry=_registry())


def _seed_email(
    route_ctx: RouteContext,
    *,
    body_plain: str = "Please process the attached invoice.",
    attachments: list[EmailAttachmentMeta] | None = None,
    tenant_id: str = TENANT,
):
    payload = EmailInboundPayload(
        received_at=NOW,
        sender="billing@vendor.example",
        recipient="ap@buyer.example",
        subject="Vendor invoice approval",
        body_plain=body_plain,
        headers={},
        attachments=attachments or [],
    )
    result = submit_email_inbound(
        route_ctx,
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        source_agent=_INGEST_AGENT_ID,
        payload=payload,
    )
    return result.record.record_id, payload


def _mission_context(record_id, payload, *, tenant_id: str = TENANT) -> MissionContext:
    return MissionContext(
        tenant_id=tenant_id,
        inputs_digest=digest_email(payload),
        source_record_id=record_id,
    )


def _agent(
    route_ctx: RouteContext,
    *,
    vendor_domain: str = VENDOR,
    now: datetime = NOW,
) -> PaymentChangeDetectionAgent:
    return PaymentChangeDetectionAgent(
        blackboard_root=route_ctx.blackboard_root,
        vendor_domain=vendor_domain,
        now=now,
        environment=Environment.PRODUCTION,
    )


def _run(route_ctx: RouteContext, record_id, payload, *, tenant_id: str = TENANT):
    agent = _agent(route_ctx)
    return SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload, tenant_id=tenant_id),
        [agent],
    ), agent


def _assert_allowed_facts_only(facts: tuple[str, ...]) -> None:
    for fact in facts:
        assert any(
            fact == prefix or fact.startswith(prefix)
            for prefix in _ALLOWED_FACT_PREFIXES
        ), f"unexpected fact emitted: {fact!r}"


def test_payment_change_agent_satisfies_agent_protocol():
    assert isinstance(_agent(_route_ctx()), Agent)


def test_first_seen_payment_signal_emits_new_indicator_and_persists():
    route_ctx = _route_ctx()
    record_id, payload = _seed_email(route_ctx, body_plain=_ROUTING_BODY)
    der, agent = _run(route_ctx, record_id, payload)
    context = _mission_context(record_id, payload)

    assert len(der.contributions) == 1
    contribution = der.contributions[0]
    assert contribution.agent_id == PAYMENT_CHANGE_DETECTION_AGENT_ID
    assert contribution.layer == 2
    facts = contribution.observed_facts
    assert "new_payment_destination_signal" in facts
    assert "payment_signal_type:routing_number" in facts
    assert "payment_delta_finding_count:1" in facts

    write = agent.persist_contribution(route_ctx, context, contribution)
    assert write.record.record_type == RecordType.AGENT_CONTRIBUTION
    assert write.record.source_agent == PAYMENT_CHANGE_DETECTION_AGENT_ID


def test_known_signal_emits_no_indicator_on_second_run():
    route_ctx = _route_ctx()
    record_id, payload = _seed_email(route_ctx, body_plain=_ROUTING_BODY)
    _run(route_ctx, record_id, payload)

    record_id2, payload2 = _seed_email(route_ctx, body_plain=_ROUTING_BODY)
    der, _ = _run(route_ctx, record_id2, payload2)

    facts = der.contributions[0].observed_facts
    assert "new_payment_destination_signal" not in facts
    assert "expired_payment_destination_signal" not in facts
    assert "payment_delta_finding_count:0" in facts


def test_expired_signal_emits_expired_indicator():
    route_ctx = _route_ctx()
    first_seen = NOW - timedelta(days=400)

    seed_id, seed_payload = _seed_email(route_ctx, body_plain=_ROUTING_BODY)
    SwarmCommander(_registry()).run_case(
        _mission_context(seed_id, seed_payload),
        [
            PaymentChangeDetectionAgent(
                blackboard_root=route_ctx.blackboard_root,
                vendor_domain=VENDOR,
                now=first_seen,
                environment=Environment.PRODUCTION,
            )
        ],
    )

    expired_id, expired_payload = _seed_email(route_ctx, body_plain=_ROUTING_BODY)
    der = SwarmCommander(_registry()).run_case(
        _mission_context(expired_id, expired_payload),
        [_agent(route_ctx, now=NOW)],
    )

    assert "expired_payment_destination_signal" in der.contributions[0].observed_facts


def test_check_signal_called_before_ingest_for_each_signal(monkeypatch):
    route_ctx = _route_ctx()
    body = (
        "Update payment details. Routing number: 021000021. "
        "Account number: 1234567890."
    )
    record_id, payload = _seed_email(route_ctx, body_plain=body)

    calls: list[tuple[str, str]] = []
    real_check = vb.check_signal
    real_ingest = vb.ingest_signal

    def spy_check(**kwargs):
        calls.append(("check", kwargs["raw_value"]))
        return real_check(**kwargs)

    def spy_ingest(**kwargs):
        calls.append(("ingest", kwargs["raw_value"]))
        return real_ingest(**kwargs)

    monkeypatch.setattr(vb, "check_signal", spy_check)
    monkeypatch.setattr(vb, "ingest_signal", spy_ingest)

    _run(route_ctx, record_id, payload)

    assert calls
    assert calls[0][0] == "check"
    for index, (action, value) in enumerate(calls):
        if action != "ingest":
            continue
        assert index > 0
        assert calls[index - 1] == ("check", value)


def test_duplicate_signal_across_sources_dedupes_baseline_calls(monkeypatch):
    route_ctx = _route_ctx()
    attachment = EmailAttachmentMeta(
        filename="invoice.pdf",
        content_type="application/pdf",
        attachment_class="invoice",
        extracted_text=f"Remit to routing number {_ROUTING_VALUE} for payment.",
    )
    record_id, payload = _seed_email(
        route_ctx,
        body_plain=_ROUTING_BODY,
        attachments=[attachment],
    )

    check_values: list[str] = []
    real_check = vb.check_signal

    def spy_check(**kwargs):
        check_values.append(kwargs["raw_value"])
        return real_check(**kwargs)

    monkeypatch.setattr(vb, "check_signal", spy_check)
    _run(route_ctx, record_id, payload)

    assert len(check_values) == 1


def test_attachment_extracted_text_path_works():
    route_ctx = _route_ctx()
    attachment = EmailAttachmentMeta(
        filename="invoice.pdf",
        content_type="application/pdf",
        attachment_class="invoice",
        extracted_text="New payment instructions. Routing number: 021000021",
    )
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="See attached for updated remittance.",
        attachments=[attachment],
    )
    der, _ = _run(route_ctx, record_id, payload)

    assert "new_payment_destination_signal" in der.contributions[0].observed_facts


def test_no_financial_signal_emits_no_indicator_and_writes_no_baseline(monkeypatch):
    route_ctx = _route_ctx()
    record_id, payload = _seed_email(
        route_ctx,
        body_plain="Thanks for your email. Talk soon.",
    )

    ingests: list[str] = []
    real_ingest = vb.ingest_signal

    def spy_ingest(**kwargs):
        ingests.append(kwargs["raw_value"])
        return real_ingest(**kwargs)

    monkeypatch.setattr(vb, "ingest_signal", spy_ingest)
    der, _ = _run(route_ctx, record_id, payload)

    assert der.contributions[0].observed_facts == (
        "payment_signal_extracted_count:0",
        "payment_delta_finding_count:0",
    )
    assert ingests == []


def test_missing_source_record_id_is_rejected():
    route_ctx = _route_ctx()
    context = MissionContext(tenant_id=TENANT, inputs_digest="a" * 64)
    with pytest.raises(GovernanceError, match="source_record_id"):
        _agent(route_ctx).analyze(context)


def test_unknown_source_record_is_rejected():
    route_ctx = _route_ctx()
    _seed_email(route_ctx, body_plain=_ROUTING_BODY)
    context = MissionContext(
        tenant_id=TENANT,
        inputs_digest="a" * 64,
        source_record_id=uuid4(),
    )
    with pytest.raises(GovernanceError, match="not found"):
        _agent(route_ctx).analyze(context)


def test_source_record_of_wrong_type_is_rejected():
    route_ctx = _route_ctx()
    record_id, payload = _seed_email(route_ctx, body_plain=_ROUTING_BODY)
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx)
    der = SwarmCommander(_registry()).run_case(context, [agent])
    contribution_write = agent.persist_contribution(
        route_ctx, context, der.contributions[0]
    )

    misdirected = MissionContext(
        tenant_id=TENANT,
        inputs_digest="a" * 64,
        source_record_id=contribution_write.record.record_id,
    )
    with pytest.raises(GovernanceError, match="not an email_inbound record"):
        agent.analyze(misdirected)


def test_invalid_vendor_domain_fails_closed():
    route_ctx = _route_ctx()
    record_id, payload = _seed_email(route_ctx, body_plain=_ROUTING_BODY)
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx, vendor_domain=" Vendor.example")
    with pytest.raises(GovernanceError, match="vendor_domain"):
        agent.analyze(context)


def test_naive_now_fails_closed():
    route_ctx = _route_ctx()
    record_id, payload = _seed_email(route_ctx, body_plain=_ROUTING_BODY)
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx, now=datetime(2026, 6, 8, 12, 0))
    with pytest.raises(GovernanceError, match="timezone-aware"):
        agent.analyze(context)


def test_tenant_isolation_keeps_baselines_separate():
    route_ctx = _route_ctx()
    tenant_a = "tenant_pay_a"
    tenant_b = "tenant_pay_b"

    record_a, payload_a = _seed_email(route_ctx, body_plain=_ROUTING_BODY, tenant_id=tenant_a)
    der_a, _ = _run(route_ctx, record_a, payload_a, tenant_id=tenant_a)
    assert "new_payment_destination_signal" in der_a.contributions[0].observed_facts

    record_b, payload_b = _seed_email(route_ctx, body_plain=_ROUTING_BODY, tenant_id=tenant_b)
    der_b, _ = _run(route_ctx, record_b, payload_b, tenant_id=tenant_b)
    assert "new_payment_destination_signal" in der_b.contributions[0].observed_facts


def test_kill_switch_inheritance_blocks_baseline_access():
    engage_kill_switch(
        Path("."),
        scope="PRODUCTION_ONLY",
        reason="halt payment change baseline",
        operator="matt",
    )
    route_ctx = _route_ctx()
    record_id, payload = _seed_email(route_ctx, body_plain=_ROUTING_BODY)
    with pytest.raises(KillSwitchEngaged):
        _agent(route_ctx).analyze(_mission_context(record_id, payload))


def test_contribution_persists_to_blackboard_and_reads_back():
    route_ctx = _route_ctx()
    record_id, payload = _seed_email(route_ctx, body_plain=_ROUTING_BODY)
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx)
    der = SwarmCommander(_registry()).run_case(context, [agent])

    write = agent.persist_contribution(route_ctx, context, der.contributions[0])
    persisted = [
        r
        for r in read_records(write.path)
        if r.record_type == RecordType.AGENT_CONTRIBUTION
    ]
    assert len(persisted) == 1
    payload_back = AgentContributionPayload.model_validate(persisted[0].payload)
    assert payload_back.agent_id == PAYMENT_CHANGE_DETECTION_AGENT_ID
    assert payload_back.case_id == context.case_id
    assert payload_back.inputs_digest == context.inputs_digest
    assert "new_payment_destination_signal" in payload_back.observed_facts


def test_challenge_returns_none():
    assert _agent(_route_ctx()).challenge(()) is None


def test_unauthorized_agent_cannot_write_contribution():
    route_ctx = _route_ctx()
    payload = AgentContributionPayload(
        case_id=uuid4(),
        inputs_digest="a" * 64,
        agent_id=_INGEST_AGENT_ID,
        layer=2,
        observed_facts=["new_payment_destination_signal"],
    )
    with pytest.raises(GovernanceError, match="cannot write this record type"):
        submit_agent_contribution(
            route_ctx,
            tenant_id=TENANT,
            environment=Environment.PRODUCTION,
            source_agent=_INGEST_AGENT_ID,
            payload=payload,
        )


def test_digest_email_is_deterministic():
    payload = EmailInboundPayload(
        received_at=NOW,
        sender="billing@vendor.example",
        recipient="ap@buyer.example",
        subject="invoice",
        body_plain=_ROUTING_BODY,
        attachments=[],
    )
    assert digest_email(payload) == digest_email(payload)
    assert len(digest_email(payload)) == 64


def test_payment_change_not_in_default_registry():
    assert PAYMENT_CHANGE_DETECTION_AGENT_ID not in build_default_registry()


def test_contribution_emits_no_risk_floor_raw_value_hash_or_redacted_display():
    route_ctx = _route_ctx()
    record_id, payload = _seed_email(route_ctx, body_plain=_ROUTING_BODY)
    der, _ = _run(route_ctx, record_id, payload)
    facts = der.contributions[0].observed_facts
    _assert_allowed_facts_only(facts)
    joined = " ".join(facts).lower()
    assert _ROUTING_VALUE not in joined
    assert "***0021" not in joined
    assert "recommended_risk_floor" not in joined
    assert "needs_review" not in joined
    assert "requires_out_of_band_verification" not in joined
    assert "sha256" not in joined


def test_wrapper_performs_no_network_or_subprocess(monkeypatch):
    route_ctx = _route_ctx()
    record_id, payload = _seed_email(route_ctx, body_plain=_ROUTING_BODY)

    def _no_network(*args, **kwargs):
        raise AssertionError("payment change wrapper must not open a socket")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("payment change wrapper must not spawn a subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)

    calls: list[str] = []
    real_assess = pcda.assess_financial_state_delta

    def spy_assess(**kwargs):
        calls.append("assess")
        return real_assess(**kwargs)

    agent = PaymentChangeDetectionAgent(
        blackboard_root=route_ctx.blackboard_root,
        vendor_domain=VENDOR,
        now=NOW,
        environment=Environment.PRODUCTION,
        assessor=spy_assess,
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload),
        [agent],
    )

    assert calls == ["assess"]
    assert "new_payment_destination_signal" in der.contributions[0].observed_facts

    source = inspect.getsource(pcda.PaymentChangeDetectionAgent).lower()
    for forbidden in ("subprocess", "socket", "requests", "urllib"):
        assert forbidden not in source


def test_wrapper_does_not_change_detector_store_or_scoring_behavior():
    wrapper_source = inspect.getsource(pcda.PaymentChangeDetectionAgent)
    assert "ingest_signal" not in wrapper_source
    assert "check_signal" not in wrapper_source
    assert "recommended_risk_floor" not in wrapper_source
    assert "recommended_action" not in wrapper_source

    for signal_type in (
        "routing_number",
        "swift_bic_code",
        "iban",
        "account_number",
        "payment_portal_url",
    ):
        assert signal_type in SIGNAL_TYPES
    assert len(SIGNAL_TYPES) == 7

    detector_source = inspect.getsource(fsl.assess_financial_state_delta)
    assert "check_signal" in detector_source
    assert "ingest_signal" in detector_source
