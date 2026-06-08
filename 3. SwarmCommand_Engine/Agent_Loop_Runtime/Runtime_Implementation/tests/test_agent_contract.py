from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from core.orchestrator.agent_contract import (
    FINAL_REVIEW_AGENT_ID,
    Agent,
    AgentContribution,
    ChallengeResult,
    DecisionEvidenceRecord,
    DecisionTimestamps,
    MissionContext,
)


def _minimal_der(**overrides) -> DecisionEvidenceRecord:
    kwargs = dict(
        case_id=uuid4(),
        inputs_digest="d" * 64,
        disposition="suspicious",
        timestamps=DecisionTimestamps(detected_at=datetime.now(timezone.utc)),
    )
    kwargs.update(overrides)
    return DecisionEvidenceRecord(**kwargs)


def test_mission_context_constructs_with_defaults():
    ctx = MissionContext(tenant_id="tenant_demo", inputs_digest="a" * 64)
    assert ctx.case_id is not None
    assert ctx.created_at.tzinfo is not None


def test_detection_contribution_observed_facts_only():
    contribution = AgentContribution(
        agent_id="blue_detection_001",
        layer=2,
        observed_facts=("sender_domain_mismatch", "reply_to_diverges"),
    )
    assert contribution.layer == 2
    assert contribution.verification_source is None


def test_detection_layer_cannot_write_verification_field():
    with pytest.raises(ValidationError, match="layer-restricted contribution field"):
        AgentContribution(
            agent_id="blue_detection_001",
            layer=2,
            observed_facts=("x",),
            verification_source="previously_known_phone",
        )


def test_detection_layer_cannot_write_challenge_field():
    with pytest.raises(ValidationError, match="layer-restricted contribution field"):
        AgentContribution(
            agent_id="blue_detection_001",
            layer=2,
            challenge_result="confirmed",
        )


def test_verification_layer_may_write_verification_fields():
    contribution = AgentContribution(
        agent_id="known_good_contact_001",
        layer=3,
        verification_source="previously_known_phone",
        verification_outcome="confirmed",
    )
    assert contribution.verification_outcome == "confirmed"


def test_challenge_layer_may_write_challenge_fields():
    contribution = AgentContribution(
        agent_id="adversarial_test_001",
        layer=5,
        challenge_result="contradicted",
        challenge_rationale="Out-of-band callback contradicted the new bank detail.",
    )
    assert contribution.challenge_result == "contradicted"


def test_decision_evidence_record_constructs():
    der = DecisionEvidenceRecord(
        case_id=uuid4(),
        inputs_digest="b" * 64,
        contributions=(
            AgentContribution(
                agent_id="blue_detection_001", layer=2, observed_facts=("x",)
            ),
        ),
        challenge_pass=(
            ChallengeResult(
                agent_id="adversarial_test_001",
                challenge_outcome="confirmed",
                challenge_basis="Header divergence confirmed on second pass.",
            ),
        ),
        disposition="suspicious",
        timestamps=DecisionTimestamps(detected_at=datetime.now(timezone.utc)),
    )
    assert der.disposition == "suspicious"
    assert der.human_state == "not_required"
    # audit fields default empty; write-protection enforcement lands in slice 3.
    assert der.audit_record_id is None
    assert der.evidence_anchor is None


def test_decision_evidence_record_rejects_unknown_disposition():
    with pytest.raises(ValidationError):
        DecisionEvidenceRecord(
            case_id=uuid4(),
            inputs_digest="c" * 64,
            disposition="totally_safe",
            timestamps=DecisionTimestamps(detected_at=datetime.now(timezone.utc)),
        )


def test_audit_record_id_rejected_without_final_review_writer():
    # Assembler (Evidence Package Agent) trying to set the audit id fails.
    with pytest.raises(ValidationError, match="only be set by the Final Review Agent"):
        _minimal_der(
            audit_record_id="audit-123",
            audit_writer_agent_id="evidence_reporting_001",
        )


def test_audit_record_id_rejected_with_no_writer():
    with pytest.raises(ValidationError, match="only be set by the Final Review Agent"):
        _minimal_der(audit_record_id="audit-123")


def test_audit_record_id_allowed_for_final_review_agent():
    der = _minimal_der(
        audit_record_id="audit-123",
        audit_writer_agent_id=FINAL_REVIEW_AGENT_ID,
    )
    assert der.audit_record_id == "audit-123"


def test_evidence_anchor_must_match_package_hash_convention():
    with pytest.raises(ValidationError, match="package-hash convention"):
        _minimal_der(evidence_anchor="not-a-real-anchor")


def test_evidence_anchor_accepts_sha256_prefixed_digest():
    der = _minimal_der(evidence_anchor="sha256:" + "a" * 64)
    assert der.evidence_anchor.startswith("sha256:")


def test_agent_protocol_is_runtime_checkable():
    class _StubDetectionAgent:
        agent_id = "blue_detection_001"
        layer = 2
        authority_level = 1
        stage_allowed = "stage_a"
        autonomous_action_allowed = False

        def analyze(self, context: MissionContext) -> AgentContribution:
            return AgentContribution(agent_id=self.agent_id, layer=self.layer)

        def challenge(self, contributions: tuple[AgentContribution, ...]):
            return None

    assert isinstance(_StubDetectionAgent(), Agent)
