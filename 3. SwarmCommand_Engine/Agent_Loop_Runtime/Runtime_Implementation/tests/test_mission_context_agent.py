"""Evidence Stage 1 proof for swarm agent #2 Mission Context.

Authorized by the §11-SIGNED Mission Context contract
(docs/mmi/contracts/002_mission_context_contract.md) and Matt build
authorization (MMI-DEC-108). Synthetic tests prove MC-AUTH classify-only
output, closed vocabularies, provenance validation, routing-key rejection,
deterministic replay, registry exclusion, and purity guards.
"""

from __future__ import annotations

import inspect
import socket
import subprocess
import uuid

import pytest

from core.command import (
    CLASSIFICATION_POLICY_VERSION,
    MissionClassificationInput,
    MissionContextAgent,
    classify_case,
    format_classification,
)
from core.command.mission_context_agent import (
    REFUSAL_PROVENANCE,
    REFUSAL_ROUTING_KEY,
    classification_to_observed_facts,
)
from core.orchestrator import Agent, MissionContext
from core.orchestrator.registry import build_default_registry


def _record_id() -> uuid.UUID:
    return uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")


def _payload(
    *,
    refs: tuple[str, ...] = ("credential_phishing",),
    digest: str = "a" * 64,
    forbidden: tuple[str, ...] = (),
) -> MissionClassificationInput:
    return MissionClassificationInput(
        tenant_id="tenant_mission_context",
        inputs_digest=digest,
        source_record_id=_record_id(),
        classification_policy_version=CLASSIFICATION_POLICY_VERSION,
        detector_summary_refs=refs,
        forbidden_keys_present=forbidden,
    )


def _context(*, refs_agent: MissionContextAgent | None = None) -> MissionContext:
    agent = refs_agent or MissionContextAgent(detector_summary_refs=("credential_phishing",))
    _ = agent
    return MissionContext(
        tenant_id="tenant_mission_context",
        inputs_digest="a" * 64,
        source_record_id=_record_id(),
    )


def test_mission_context_agent_satisfies_agent_protocol():
    agent = MissionContextAgent()
    assert isinstance(agent, Agent)
    assert agent.layer == 1
    assert agent.autonomous_action_allowed is False
    assert inspect.ismethod(agent.classify)
    assert inspect.ismethod(agent.analyze)
    assert agent.challenge(()) is None


def test_classify_phishing_from_credential_ref():
    result = classify_case(_payload(refs=("credential_phishing",)))
    assert result.kind == "success"
    item = result.classification
    assert item is not None
    assert item.case_type == "phishing"
    assert item.review_depth == "standard"
    assert "credential_phishing" in item.required_evidence


def test_classify_vendor_payment_from_payment_change_ref():
    result = classify_case(_payload(refs=("payment_change_detection",)))
    assert result.classification is not None
    assert result.classification.case_type == "vendor_payment_fraud"


def test_unknown_case_type_when_no_refs():
    result = classify_case(_payload(refs=()))
    assert result.classification is not None
    assert result.classification.case_type == "unknown"
    assert result.classification.review_depth == "human_required"


def test_refuse_missing_provenance_digest():
    result = classify_case(_payload(digest="not-a-sha256"))
    assert result.kind == "refusal"
    assert result.refusal == REFUSAL_PROVENANCE


def test_refuse_routing_key_in_inbound():
    result = classify_case(_payload(forbidden=("dispatch",)))
    assert result.kind == "refusal"
    assert result.refusal == REFUSAL_ROUTING_KEY


def test_deterministic_replay_same_inputs():
    payload = _payload(refs=("ghost_thread",))
    first = classify_case(payload)
    second = classify_case(payload)
    assert first.classification is not None
    assert second.classification is not None
    assert first.classification.case_type == second.classification.case_type
    assert first.classification.review_depth == second.classification.review_depth
    assert first.classification.required_evidence == second.classification.required_evidence


def test_observed_facts_use_closed_prefixes_only():
    result = classify_case(_payload(refs=("evidence_package",)))
    assert result.classification is not None
    facts = classification_to_observed_facts(result.classification)
    assert all(fact.startswith("classification_") for fact in facts)
    joined = "\n".join(facts)
    for forbidden in ("dispatch", "aggregate_risk_score", "disposition", "agents"):
        assert forbidden not in joined


def test_analyze_maps_classification_to_layer1_contribution():
    agent = MissionContextAgent(detector_summary_refs=("payment_change_detection",))
    contribution = agent.analyze(_context())
    assert contribution.agent_id == "mission_context_001"
    assert contribution.layer == 1
    assert "classification_case_type:vendor_payment_fraud" in contribution.observed_facts


def test_analyze_refuses_without_source_record_id():
    agent = MissionContextAgent()
    context = MissionContext(tenant_id="tenant_mission_context", inputs_digest="b" * 64)
    with pytest.raises(ValueError):
        agent.analyze(context)


def test_format_classification_is_machine_readable():
    result = classify_case(_payload(refs=("attachment_risk",)))
    assert result.classification is not None
    text = format_classification(result.classification)
    assert "case_type=ransomware_precursor" in text
    assert "review_depth=enhanced" in text


def test_not_in_build_default_registry():
    registry = build_default_registry()
    assert "mission_context_001" not in registry


def test_purity_guard_no_network_or_subprocess(monkeypatch):
    def _no_network(*args, **kwargs):
        raise AssertionError("MissionContextAgent must not open network sockets")

    def _no_subprocess(*args, **kwargs):
        raise AssertionError("MissionContextAgent must not spawn subprocess")

    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(subprocess, "Popen", _no_subprocess)
    monkeypatch.setattr(subprocess, "run", _no_subprocess)

    agent = MissionContextAgent(detector_summary_refs=("credential_phishing",))
    agent.analyze(_context())
    source = inspect.getsource(MissionContextAgent)
    assert "socket" not in source
    assert "subprocess" not in source


def test_policy_version_echoed_on_output():
    result = classify_case(_payload())
    assert result.classification is not None
    assert (
        result.classification.classification_policy_version
        == CLASSIFICATION_POLICY_VERSION
    )


def test_ransomware_precursor_gets_enhanced_depth():
    result = classify_case(_payload(refs=("attachment_risk",)))
    assert result.classification is not None
    assert result.classification.review_depth == "enhanced"


def test_cyber_insurance_evidence_manifest():
    result = classify_case(_payload(refs=("evidence_package",)))
    assert result.classification is not None
    assert result.classification.case_type == "cyber_insurance_evidence"
    assert "evidence_package" in result.classification.required_evidence
