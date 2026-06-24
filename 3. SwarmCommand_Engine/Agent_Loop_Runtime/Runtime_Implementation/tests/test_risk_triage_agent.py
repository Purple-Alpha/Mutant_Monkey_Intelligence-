"""Evidence Stage 1 proof for swarm agent #3 Risk Triage.

Authorized by the §11-SIGNED Risk Triage contract
(docs/mmi/contracts/003_risk_triage_contract.md) and Matt build authorization
(MMI-DEC-115). Synthetic tests prove AUTH-4 score-only telemetry, strict
allowlist output, provenance validation, routing-key rejection, deterministic
replay, registry exclusion, and purity guards.
"""

from __future__ import annotations

import inspect
import socket
import subprocess
import uuid

import pytest

from core.blackboard.models import GovernanceError
from core.command import (
    SCORING_POLICY_VERSION,
    DetectorEvidenceRecord,
    RiskTriageAgent,
    RiskTriageInput,
    assert_telemetry_auth4_compliant,
    score_case,
    telemetry_to_observed_facts,
)
from core.command.risk_triage_agent import (
    REFUSAL_POLICY,
    REFUSAL_PROVENANCE,
    REFUSAL_ROUTING_KEY,
    RiskScoreTelemetry,
    SourceProvenance,
)
from core.orchestrator import Agent, MissionContext
from core.orchestrator.registry import build_default_registry


def _record(
    *,
    detector_id: str = "credential_phishing_001",
    tags: tuple[str, ...] = ("credential_phishing",),
    extra_fields: frozenset[str] = frozenset(),
) -> DetectorEvidenceRecord:
    return DetectorEvidenceRecord(
        detector_id=detector_id,
        detector_contract_version="mmi_det_v1",
        evidence_ref="evidence:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        emitted_at="2026-06-23T00:00:00Z",
        signal_tags=tags,
        extra_fields=extra_fields,
    )


def _payload(
    *,
    outputs: tuple[DetectorEvidenceRecord, ...] = (_record(),),
    policy: str = SCORING_POLICY_VERSION,
) -> RiskTriageInput:
    return RiskTriageInput(
        message_id="msg-risk-triage-001",
        tenant_id="tenant_risk_triage",
        detector_outputs=outputs,
        scoring_policy_version=policy,
    )


def _context() -> MissionContext:
    return MissionContext(tenant_id="tenant_risk_triage", inputs_digest="b" * 64)


def test_risk_triage_agent_carries_auth4_metadata():
    agent = RiskTriageAgent()
    assert isinstance(agent, Agent)
    assert agent.agent_id == "risk_triage_001"
    assert agent.layer == 1
    assert agent.autonomous_action_allowed is False
    assert agent.scoring_policy_version == SCORING_POLICY_VERSION
    assert inspect.ismethod(agent.score)
    assert agent.challenge(()) is None


def test_score_case_emits_allowlisted_telemetry():
    result = score_case(_payload())
    assert result.kind == "success"
    telemetry = result.telemetry
    assert telemetry is not None
    assert telemetry.aggregate_risk_score == 70.0
    assert telemetry.axis_scores["impersonation"] == 70.0
    assert telemetry.scoring_policy_version == SCORING_POLICY_VERSION
    assert len(telemetry.source_provenance) == 1


def test_vendor_payment_signal_maps_to_vendor_fraud_axis():
    result = score_case(
        _payload(outputs=(_record(tags=("payment_change_detection",)),))
    )
    assert result.telemetry is not None
    assert result.telemetry.axis_scores["vendor_fraud"] == 72.0
    assert result.telemetry.aggregate_risk_score == 72.0


def test_refuse_routing_key_in_detector_record():
    result = score_case(
        _payload(outputs=(_record(extra_fields=frozenset({"dispatch"})),))
    )
    assert result.kind == "refusal"
    assert result.refusal == REFUSAL_ROUTING_KEY


def test_refuse_missing_provenance():
    bad = DetectorEvidenceRecord(
        detector_id="",
        detector_contract_version="mmi_det_v1",
        evidence_ref="evidence:bad",
        emitted_at="2026-06-23T00:00:00Z",
    )
    result = score_case(_payload(outputs=(bad,)))
    assert result.kind == "success"
    assert result.telemetry is not None
    assert result.telemetry.aggregate_risk_score == 0.0
    assert "INPUT_PROVENANCE_MISSING" in result.telemetry.scoring_reason_codes


def test_refuse_wrong_policy_version():
    result = score_case(_payload(policy="mmi_rt_v0"))
    assert result.kind == "refusal"
    assert result.refusal == REFUSAL_POLICY


def test_deterministic_replay_same_inputs():
    payload = _payload(outputs=(_record(tags=("ghost_thread", "payment_change_detection")),))
    first = score_case(payload)
    second = score_case(payload)
    assert first.telemetry is not None
    assert second.telemetry is not None
    assert first.telemetry.aggregate_risk_score == second.telemetry.aggregate_risk_score
    assert first.telemetry.axis_scores == second.telemetry.axis_scores


def test_assert_telemetry_auth4_rejects_unknown_axis():
    telemetry = RiskScoreTelemetry(
        message_id="msg-1",
        tenant_id="tenant-1",
        aggregate_risk_score=1.0,
        axis_scores={"unknown_axis": 1.0},
        scoring_reason_codes=(),
        scoring_policy_version=SCORING_POLICY_VERSION,
        source_provenance=(),
    )
    with pytest.raises(GovernanceError, match="closed policy set"):
        assert_telemetry_auth4_compliant(telemetry)


def test_observed_facts_use_closed_triage_prefixes_only():
    result = score_case(_payload())
    assert result.telemetry is not None
    facts = telemetry_to_observed_facts(result.telemetry)
    assert all(fact.startswith("triage_") for fact in facts)
    joined = "\n".join(facts)
    for forbidden in ("recommended_action", "route_to", "dispatch", "plain_english"):
        assert forbidden not in joined


def test_analyze_maps_telemetry_to_layer1_contribution():
    agent = RiskTriageAgent(
        detector_outputs=(_record(tags=("payment_change_detection",)),),
        message_id="msg-analyze-001",
    )
    contribution = agent.analyze(_context())
    assert contribution.agent_id == "risk_triage_001"
    assert contribution.layer == 1
    assert "triage_aggregate_risk_score:72.0000" in contribution.observed_facts


def test_not_in_build_default_registry():
    registry = build_default_registry()
    assert "risk_triage_001" not in registry


def test_purity_guard_no_network_or_subprocess(monkeypatch):
    def _no_network(*args, **kwargs):
        raise AssertionError("RiskTriageAgent must not open network sockets")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("RiskTriageAgent must not spawn subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)

    agent = RiskTriageAgent(detector_outputs=(_record(),))
    agent.analyze(_context())
    source = inspect.getsource(RiskTriageAgent)
    assert "socket" not in source
    assert "subprocess" not in source


def test_score_wrapper_enforces_auth4_probe():
    agent = RiskTriageAgent()
    result = agent.score(_payload())
    assert result.telemetry is not None
    assert_telemetry_auth4_compliant(result.telemetry)


def test_provenance_chain_present_on_output():
    result = score_case(_payload())
    assert result.telemetry is not None
    assert result.telemetry.source_provenance == (
        SourceProvenance(
            detector_id="credential_phishing_001",
            detector_contract_version="mmi_det_v1",
            evidence_ref="evidence:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        ),
    )


def test_analyze_refuses_on_routing_key():
    agent = RiskTriageAgent(
        detector_outputs=(_record(extra_fields=frozenset({"route_to"})),)
    )
    with pytest.raises(ValueError, match=REFUSAL_ROUTING_KEY):
        agent.analyze(_context())


def test_wrapper_source_excludes_routing_and_narrative():
    source = inspect.getsource(RiskTriageAgent)
    assert "recommended_action" not in source
    assert "plain_english_summary" not in source
    assert "route_to" not in inspect.getsource(RiskTriageAgent.score)
