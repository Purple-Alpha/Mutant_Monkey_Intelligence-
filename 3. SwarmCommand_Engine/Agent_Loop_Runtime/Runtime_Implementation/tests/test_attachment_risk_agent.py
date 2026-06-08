"""Evidence Stage 1 proof that the governed-agent contract holds on the static
attachment-classifier output (swarm agent #30 Attachment Risk).

Authorized by the §11-SIGNED Attachment Risk Agent Design Contract
(2026-06-08). These are the synthetic-fixture tests that constitute the Stage 1
evidence: known-bad fire, known-good no-fire, multi-attachment aggregation,
persistence, guardrails, registry-default exclusion, static-only (no
network/subprocess) behavior, and no score / raw attachment-metadata leakage.
"""

import socket
import subprocess
from datetime import datetime, timezone
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
from core.orchestrator import attachment_risk_agent as ara
from core.orchestrator.attachment_risk_agent import (
    ATTACHMENT_RISK_AGENT_ID,
    AttachmentRiskAgent,
    digest_email,
)
from core.orchestrator.registry import build_default_registry
from core.orchestrator.routes import submit_email_inbound

_INGEST_AGENT_ID = "ingest_001"

# Closed attachment-risk indicator vocabulary the detector can emit. Used to
# assert facts-only output and no raw-metadata/score leakage.
_KNOWN_ATTACHMENT_INDICATORS = frozenset(
    {
        "double_extension_attachment",
        "executable_attachment",
        "iso_or_disk_image_attachment",
        "macro_enabled_office_document",
        "html_smuggling_attachment",
        "encrypted_archive_attachment",
    }
)


def _attachment_agent_entry() -> AgentRegistryEntry:
    return AgentRegistryEntry(
        agent_id=ATTACHMENT_RISK_AGENT_ID,
        display_name="Attachment Risk Agent",
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
    return {e.agent_id: e for e in (_attachment_agent_entry(), _ingest_entry())}


def _route_ctx(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard", registry=_registry())


def _seed_email(
    route_ctx: RouteContext,
    *,
    attachments: list[EmailAttachmentMeta] | None = None,
    tenant_id: str = "tenant_demo",
):
    payload = EmailInboundPayload(
        received_at=datetime.now(timezone.utc),
        sender="billing@vendor.example",
        recipient="ap@buyer.example",
        subject="Vendor invoice approval",
        body_plain="Please process the attached invoice.",
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


def _mission_context(record_id, payload, *, tenant_id: str = "tenant_demo") -> MissionContext:
    return MissionContext(
        tenant_id=tenant_id,
        inputs_digest=digest_email(payload),
        source_record_id=record_id,
    )


def _agent(route_ctx: RouteContext) -> AttachmentRiskAgent:
    return AttachmentRiskAgent(
        blackboard_root=route_ctx.blackboard_root,
        environment=Environment.PRODUCTION,
    )


def test_attachment_risk_agent_satisfies_agent_protocol(tmp_path):
    assert isinstance(_agent(_route_ctx(tmp_path)), Agent)


def test_known_bad_attachment_produces_indicator_facts_and_suspicious(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        attachments=[EmailAttachmentMeta(filename="invoice.pdf.exe")],
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert len(der.contributions) == 1
    contribution = der.contributions[0]
    assert contribution.agent_id == ATTACHMENT_RISK_AGENT_ID
    assert contribution.layer == 2
    # Facts only, in detector order; no numeric score / classification surfaced.
    assert contribution.observed_facts == (
        "double_extension_attachment",
        "executable_attachment",
    )
    assert der.disposition == "suspicious"
    assert der.inputs_digest == digest_email(payload)
    assert len(der.inputs_digest) == 64


def test_known_good_email_with_no_dangerous_attachment_is_clear(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        attachments=[EmailAttachmentMeta(filename="invoice_march.pdf")],
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    # Routine invoice attachment carries a low detector score but no indicator.
    assert der.contributions[0].observed_facts == ()
    assert der.disposition == "clear"


def test_email_with_no_attachments_is_clear(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(route_ctx, attachments=[])
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert der.contributions[0].observed_facts == ()
    assert der.disposition == "clear"


def test_multiple_attachments_aggregate_in_source_order_with_dedupe(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        attachments=[
            EmailAttachmentMeta(filename="report_q1.docm"),       # macro
            EmailAttachmentMeta(filename="quarterly_summary.pdf"),  # benign
            EmailAttachmentMeta(filename="image.iso"),            # disk image
            EmailAttachmentMeta(filename="second_macro.xlsm"),    # macro (dedupe)
        ],
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    # Source-order aggregation, deduped: macro first (from the .docm), then the
    # disk image; the second macro file adds no duplicate fact.
    assert der.contributions[0].observed_facts == (
        "macro_enabled_office_document",
        "iso_or_disk_image_attachment",
    )
    assert der.disposition == "suspicious"


def test_contribution_persists_to_blackboard_and_reads_back(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        attachments=[EmailAttachmentMeta(filename="invoice.pdf.exe")],
    )
    context = _mission_context(record_id, payload)
    agent = _agent(route_ctx)
    der = SwarmCommander(_registry()).run_case(context, [agent])

    write = agent.persist_contribution(route_ctx, context, der.contributions[0])
    assert write.record.record_type == RecordType.AGENT_CONTRIBUTION
    assert write.record.source_agent == ATTACHMENT_RISK_AGENT_ID

    persisted = [
        r
        for r in read_records(write.path)
        if r.record_type == RecordType.AGENT_CONTRIBUTION
    ]
    assert len(persisted) == 1
    payload_back = AgentContributionPayload.model_validate(persisted[0].payload)
    assert payload_back.agent_id == ATTACHMENT_RISK_AGENT_ID
    assert payload_back.case_id == context.case_id
    assert payload_back.inputs_digest == context.inputs_digest
    assert payload_back.observed_facts == [
        "double_extension_attachment",
        "executable_attachment",
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
    _seed_email(route_ctx, attachments=[EmailAttachmentMeta(filename="invoice.pdf.exe")])
    context = MissionContext(
        tenant_id="tenant_demo", inputs_digest="a" * 64, source_record_id=uuid4()
    )
    with pytest.raises(GovernanceError, match="not found"):
        _agent(route_ctx).analyze(context)


def test_source_record_of_wrong_type_is_rejected(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        attachments=[EmailAttachmentMeta(filename="invoice.pdf.exe")],
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
        observed_facts=["executable_attachment"],
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
        body_plain="hello",
        attachments=[EmailAttachmentMeta(filename="invoice.pdf.exe")],
    )
    assert digest_email(payload) == digest_email(payload)
    assert len(digest_email(payload)) == 64


def test_attachment_risk_not_in_default_registry(tmp_path):
    # Evidence Stage 1: explicitly excluded from production dispatch.
    assert ATTACHMENT_RISK_AGENT_ID not in build_default_registry()


def test_contribution_carries_no_score_classification_or_raw_filename(tmp_path):
    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        attachments=[EmailAttachmentMeta(filename="invoice.pdf.exe")],
    )
    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    facts = der.contributions[0].observed_facts
    # Every emitted fact is a closed indicator name - no raw filename, hash,
    # MIME, classification, or numeric score crosses into the contribution.
    assert all(fact in _KNOWN_ATTACHMENT_INDICATORS for fact in facts)
    for fact in facts:
        assert "invoice" not in fact
        assert ".exe" not in fact
        assert ".pdf" not in fact
        assert not any(ch.isdigit() for ch in fact)


def test_wrapper_does_no_network_or_subprocess(tmp_path, monkeypatch):
    """D8 static-only: analyze() must not open sockets or spawn subprocesses;
    it only calls the static metadata detector over stored attachment data."""

    route_ctx = _route_ctx(tmp_path)
    record_id, payload = _seed_email(
        route_ctx,
        attachments=[EmailAttachmentMeta(filename="invoice.pdf.exe")],
    )

    def _no_network(*args, **kwargs):
        raise AssertionError("attachment risk wrapper must not open a socket")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("attachment risk wrapper must not spawn a subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)

    # Delegation spy: the wrapper must call the static detector once per
    # attachment and derive its facts solely from that return value.
    calls: list[str] = []
    real_score = ara.score_attachment_risk

    def _spy(meta):
        calls.append(meta.filename)
        return real_score(meta)

    monkeypatch.setattr(ara, "score_attachment_risk", _spy)

    der = SwarmCommander(_registry()).run_case(
        _mission_context(record_id, payload), [_agent(route_ctx)]
    )

    assert calls == ["invoice.pdf.exe"]
    assert der.contributions[0].observed_facts == (
        "double_extension_attachment",
        "executable_attachment",
    )
