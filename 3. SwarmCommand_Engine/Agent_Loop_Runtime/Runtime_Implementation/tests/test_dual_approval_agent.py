"""Evidence Stage 1 proof for swarm agent #19 Dual-Approval."""

from __future__ import annotations

import inspect
import socket
import subprocess
from pathlib import Path
from uuid import uuid4

import pytest

from core.blackboard import GovernanceError
from core.orchestrator import MissionContext
from core.orchestrator.dual_approval_agent import (
    DUAL_APPROVAL_AGENT_ID,
    DualApprovalAgent,
    digest_packet,
)
from core.orchestrator.registry import build_default_registry
from core.workflows.vendor_payment_verification import (
    SCHEMA_VERSION,
    VPVPaymentRequest,
    VPVEvidencePacket,
    VPVReproducibility,
    run_vendor_payment_verification,
)

TENANT = "tenant_dual_approval_demo"
FINDING_ID = "vendor_payment:case-019"


def _packet(*, risk_verdict: str, oob_confirmation: str = "absent") -> VPVEvidencePacket:
    request = VPVPaymentRequest(
        tenant_id=TENANT,
        finding_id=FINDING_ID,
        sender="billing@vendor.example",
        headers={},
        body_plain="body",
        subject="subject",
        known_good_domains=("vendor.example",),
    )
    packet = run_vendor_payment_verification(request)
    return VPVEvidencePacket(
        schema_version=packet.schema_version,
        tenant_id=packet.tenant_id,
        finding_id=packet.finding_id,
        sender_auth=packet.sender_auth,
        domain_similarity=packet.domain_similarity,
        thread_integrity=packet.thread_integrity,
        banking_delta=packet.banking_delta,
        vendor_known=packet.vendor_known,
        payment_pattern_anomaly=packet.payment_pattern_anomaly,
        oob_confirmation=oob_confirmation,
        urgency_markers=packet.urgency_markers,
        risk_verdict=risk_verdict,
        reproducibility=packet.reproducibility,
    )


def _context(*, tenant_id: str = TENANT) -> MissionContext:
    return MissionContext(
        tenant_id=tenant_id,
        case_id=uuid4(),
        source_record_id=uuid4(),
        inputs_digest="digest",
    )


def test_high_packet_raises_dual_approval_required():
    agent = DualApprovalAgent(_packet(risk_verdict="HIGH"))
    contribution = agent.analyze(_context())
    assert "dual_approval_required" in contribution.observed_facts
    assert contribution.verification_outcome == "unable_to_verify"
    assert contribution.layer == 3
    assert contribution.agent_id == DUAL_APPROVAL_AGENT_ID


def test_elevated_packet_raises_by_default():
    agent = DualApprovalAgent(_packet(risk_verdict="ELEVATED"))
    contribution = agent.analyze(_context())
    assert "dual_approval_required" in contribution.observed_facts


def test_elevated_carve_out_can_skip_raise():
    agent = DualApprovalAgent(_packet(risk_verdict="ELEVATED"), elevated_raises=False)
    contribution = agent.analyze(_context())
    assert "dual_approval_not_applicable" in contribution.observed_facts
    assert contribution.verification_outcome == "confirmed"


def test_clear_packet_emits_not_applicable():
    agent = DualApprovalAgent(_packet(risk_verdict="CLEAR", oob_confirmation="present"))
    contribution = agent.analyze(_context())
    assert "dual_approval_not_applicable" in contribution.observed_facts
    assert contribution.verification_outcome == "confirmed"


def test_schema_mismatch_fails_closed():
    packet = _packet(risk_verdict="CLEAR")
    bad = VPVEvidencePacket(
        schema_version="vpv_evidence_packet_v0",
        tenant_id=packet.tenant_id,
        finding_id=packet.finding_id,
        sender_auth=packet.sender_auth,
        domain_similarity=packet.domain_similarity,
        thread_integrity=packet.thread_integrity,
        banking_delta=packet.banking_delta,
        vendor_known=packet.vendor_known,
        payment_pattern_anomaly=packet.payment_pattern_anomaly,
        oob_confirmation=packet.oob_confirmation,
        urgency_markers=packet.urgency_markers,
        risk_verdict=packet.risk_verdict,
        reproducibility=packet.reproducibility,
    )
    agent = DualApprovalAgent(bad)
    with pytest.raises(GovernanceError):
        agent.analyze(_context())


def test_missing_packet_fails_closed():
    agent = DualApprovalAgent(None)
    with pytest.raises(GovernanceError):
        agent.analyze(_context())


def test_tenant_mismatch_rejected():
    agent = DualApprovalAgent(_packet(risk_verdict="HIGH"))
    with pytest.raises(GovernanceError):
        agent.analyze(_context(tenant_id="other-tenant"))


def test_no_raw_financial_or_body_leakage_in_facts():
    agent = DualApprovalAgent(_packet(risk_verdict="HIGH"))
    contribution = agent.analyze(_context())
    joined = " ".join(contribution.observed_facts)
    assert "@" not in joined
    assert "invoice" not in joined.lower()
    assert "account" not in joined.lower()


def test_not_in_default_registry():
    registry = build_default_registry()
    assert DUAL_APPROVAL_AGENT_ID not in registry


def test_challenge_is_none():
    agent = DualApprovalAgent(_packet(risk_verdict="HIGH"))
    contribution = agent.analyze(_context())
    assert agent.challenge((contribution,)) is None


def test_digest_packet_stable():
    packet = _packet(risk_verdict="HIGH")
    assert digest_packet(packet) == digest_packet(packet)


def test_no_network_or_subprocess_in_wrapper():
    source = Path(__file__).parents[1] / "core/orchestrator/dual_approval_agent.py"
    text = source.read_text(encoding="utf-8")
    assert "socket" not in text
    assert "subprocess" not in text
    assert "requests" not in text
    assert "score_email_authentication" not in text

    with pytest.MonkeyPatch.context() as mp:
        def _blocked(*_args, **_kwargs):
            raise AssertionError("network call attempted")

        mp.setattr(socket, "socket", _blocked)
        DualApprovalAgent(_packet(risk_verdict="HIGH")).analyze(_context())

    assert "subprocess" not in inspect.getsource(DualApprovalAgent)
