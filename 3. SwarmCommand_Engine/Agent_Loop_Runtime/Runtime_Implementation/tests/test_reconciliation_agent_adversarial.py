"""ReconciliationAgent adversarial suite (#100).

Governing contract
------------------
``4. Product_Roadmap/ReconciliationAgent_Adversarial_Test_Suite_Contract.md``
- §11 SIGNED 2026-06-14 (Matt Nichol).

Every RA-ADV test ID from the signed contract is represented and executed. The
tests target the real ReconciliationAgent, CanonicalEvidenceLedger, VerdictLedger,
and voter classes. Where a signed attack names an integration boundary that is
not implemented inside the Phase 4 component (live Lung transport, CIRT delivery
monitoring, CI health scoring, audit-output flood monitoring), the test asserts
the component-level invariant and the gate manifest records the remaining
infrastructure control as out of scope for #100.
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path
from typing import Iterable

import pytest
from pydantic import ValidationError

from core.blackboard import (
    CanonicalEvidenceLedger,
    EnsembleOutcome,
    EvidenceLedgerEntry,
    EvidenceStage,
    EvidenceType,
    LedgerSchemaError,
    ReconciliationVerdict,
    Verdict,
    VerdictLedger,
    VerdictLedgerSchemaError,
)
from core.operator_state import CIRTRegistry
from core.reconciliation import (
    LungState,
    R1SignalWeightVoter,
    R2PatternMatchVoter,
    R3ConflictResolutionVoter,
    ReconciliationAgent,
    ReconciliationError,
    VoterVote,
)


TENANT = "tenant-a"
OTHER_TENANT = "tenant-b"
EMAIL = "email-001"


def _entry(
    *,
    tenant_id: str = TENANT,
    email_id: str = EMAIL,
    evidence_type: EvidenceType = EvidenceType.CONTENT_SIGNAL,
    details: dict | None = None,
    confidence: float = 0.6,
    agent_id: str = "adversarial_test_agent",
) -> EvidenceLedgerEntry:
    return EvidenceLedgerEntry(
        agent_id=agent_id,
        tenant_id=tenant_id,
        email_id=email_id,
        evidence_type=evidence_type,
        details=details or {},
        confidence=confidence,
        stage=EvidenceStage.ES2,
    )


def _seed(ledger: CanonicalEvidenceLedger, entries: Iterable[EvidenceLedgerEntry]) -> None:
    for entry in entries:
        ledger.append(entry)


def _ledgers(tmp_path: Path) -> tuple[CanonicalEvidenceLedger, VerdictLedger]:
    return (
        CanonicalEvidenceLedger(tmp_path / "evidence.jsonl"),
        VerdictLedger(tmp_path / "verdicts.jsonl"),
    )


def _agent(
    evidence: CanonicalEvidenceLedger,
    verdicts: VerdictLedger,
    *,
    cirt: CIRTRegistry | None = None,
) -> ReconciliationAgent:
    return ReconciliationAgent(evidence, verdicts, cirt_registry=cirt)


def _high_risk_entries(
    *,
    tenant_id: str = TENANT,
    email_id: str = EMAIL,
    extra_details: dict | None = None,
) -> list[EvidenceLedgerEntry]:
    extra = extra_details or {}
    return [
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.GEO_SIGNAL,
            details={"high_risk_region": True, "velocity_flag": True, **extra},
            confidence=0.9,
            agent_id="geo_velocity_agent",
        ),
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.SENDER_SIGNAL,
            details={
                "known_contact": True,
                "established_vendor": True,
                "prior_interaction_count": 40,
                **extra,
            },
            confidence=0.9,
            agent_id="sender_history_agent",
        ),
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.CONTENT_SIGNAL,
            details={
                "bec_pattern_match": True,
                "wire_transfer_request": True,
                "urgency_detected": True,
                "sentiment_score": 0.9,
                **extra,
            },
            confidence=0.95,
            agent_id="content_analyzer",
        ),
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.URL_SIGNAL,
            details={
                "malicious_url_detected": True,
                "credential_harvest_flag": True,
                "reputation_score": 1.0,
                **extra,
            },
            confidence=0.9,
            agent_id="url_receptor",
        ),
    ]


def _medium_entries(*, tenant_id: str = TENANT, email_id: str = EMAIL) -> list[EvidenceLedgerEntry]:
    return [
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.CONTENT_SIGNAL,
            details={"urgency_detected": True, "sentiment_score": 0.5},
            confidence=0.55,
            agent_id="content_analyzer",
        ),
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.SENDER_SIGNAL,
            details={"known_contact": True, "prior_interaction_count": 3},
            confidence=0.6,
            agent_id="sender_history_agent",
        ),
    ]


def _all_disagree_entries() -> list[EvidenceLedgerEntry]:
    return [
        _entry(
            evidence_type=EvidenceType.SENDER_SIGNAL,
            details={"known_contact": True, "prior_interaction_count": 2},
            confidence=0.2,
            agent_id="sender_history_agent",
        ),
        _entry(
            evidence_type=EvidenceType.GEO_SIGNAL,
            details={"high_risk_region": False, "velocity_flag": False},
            confidence=0.2,
            agent_id="geo_velocity_agent",
        ),
        _entry(
            evidence_type=EvidenceType.CONTENT_SIGNAL,
            details={"bec_pattern_match": True, "wire_transfer_request": True},
            confidence=0.95,
            agent_id="content_analyzer",
        ),
    ]


def _base_verdict_dict(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "email_id": EMAIL,
        "tenant_id": TENANT,
        "verdict": "HIGH_RISK",
        "ensemble_outcome": "unanimous",
        "overall_confidence": 0.9,
        "r1_vote": "HIGH_RISK",
        "r1_confidence": 0.9,
        "r2_vote": "HIGH_RISK",
        "r2_confidence": 0.9,
        "r3_vote": "HIGH_RISK",
        "r3_confidence": 0.9,
        "plain_english_chain": "verified evidence chain",
    }
    data.update(overrides)
    return data


class _StaticVoter:
    def __init__(self, vote: VoterVote) -> None:
        self._vote = vote

    def vote(self, contributions: list[EvidenceLedgerEntry]) -> VoterVote:
        return self._vote


def _vote(voter_id: str, verdict: Verdict, confidence: float = 0.8) -> VoterVote:
    return VoterVote(voter_id, verdict, confidence, f"{voter_id} static adversarial vote")


# ---------------------------------------------------------------------------
# Family 1 - Blackboard Trust Boundary
# ---------------------------------------------------------------------------


def test_ra_adv_1_01_fake_layer1_contribution_rejected(tmp_path: Path):
    evidence, _ = _ledgers(tmp_path)
    with pytest.raises(LedgerSchemaError):
        evidence.append(
            {
                "agent_id": "",
                "tenant_id": TENANT,
                "email_id": EMAIL,
                "evidence_type": "fake_detection_agent",
                "details": {"bec_pattern_match": True},
                "confidence": 0.99,
                "stage": "ES2",
            }
        )
    assert evidence.read_for_tenant(TENANT) == []


def test_ra_adv_1_02_malformed_or_missing_contributions_safe_error(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    agent = _agent(evidence, verdicts)
    with pytest.raises(ReconciliationError, match="no Layer 1 contributions"):
        agent.analyze(tenant_id=TENANT, email_id=EMAIL)
    assert verdicts.read_for_tenant(TENANT) == []


def test_ra_adv_1_03_zero_day_identifier_does_not_suppress_primary_verdict(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    entries = _high_risk_entries(extra_details={"zero_day_candidate": True})
    _seed(evidence, entries)
    result = _agent(evidence, verdicts).analyze(tenant_id=TENANT, email_id=EMAIL)
    assert result.zero_day_referred is True
    assert result.verdict is Verdict.HIGH_RISK


def test_ra_adv_1_04_spam_only_layout_cannot_hide_fraud_pattern(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(
        evidence,
        [
            _entry(
                evidence_type=EvidenceType.IMAGE_SIGNAL,
                details={"spam_signal_only": True, "bulk_content_flag": True},
                confidence=0.6,
                agent_id="image_classifier",
            ),
            *_high_risk_entries(),
        ],
    )
    result = _agent(evidence, verdicts).analyze(tenant_id=TENANT, email_id=EMAIL)
    assert result.delivery_problem_path is True
    assert result.verdict is Verdict.DELIVERY_PROBLEM
    assert result.zero_day_referred is False
    assert "delivery problem" in result.plain_english_chain.lower()


def test_ra_adv_1_05_pattern_poisoning_flag_does_not_disable_r2(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(
        evidence,
        _high_risk_entries(
            extra_details={
                "layer0_profile_override": "disable_bec_wire_fraud",
                "known_profile_poisoned": True,
            }
        ),
    )
    result = _agent(evidence, verdicts).analyze(tenant_id=TENANT, email_id=EMAIL)
    assert result.r2_vote is Verdict.HIGH_RISK
    assert result.verdict is Verdict.HIGH_RISK


# ---------------------------------------------------------------------------
# Family 2 - Tenant Isolation and Join-Key Collision
# ---------------------------------------------------------------------------


def test_ra_adv_2_01_cross_tenant_contribution_rejected_by_query_boundary(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(evidence, _high_risk_entries(tenant_id=OTHER_TENANT))
    with pytest.raises(ReconciliationError):
        _agent(evidence, verdicts).analyze(tenant_id=TENANT, email_id=EMAIL)
    assert verdicts.read_for_tenant(TENANT) == []


def test_ra_adv_2_02_sender_domain_join_key_cannot_merge_tenants(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(
        evidence,
        [
            *_high_risk_entries(tenant_id=OTHER_TENANT, extra_details={"sender_domain": "same.example"}),
            _entry(
                tenant_id=TENANT,
                evidence_type=EvidenceType.SENDER_SIGNAL,
                details={"sender_domain": "same.example", "known_contact": True},
                confidence=0.2,
            ),
        ],
    )
    result = _agent(evidence, verdicts).analyze(tenant_id=TENANT, email_id=EMAIL)
    assert result.tenant_id == TENANT
    assert all(OTHER_TENANT not in ref for ref in result.contributing_evidence)
    assert len(verdicts.read_for_tenant(OTHER_TENANT)) == 0


def test_ra_adv_2_03_serialization_boundary_rejects_tenant_swap(tmp_path: Path):
    _, verdicts = _ledgers(tmp_path)
    verdicts.append(_base_verdict_dict(tenant_id=TENANT))
    swapped = _base_verdict_dict(tenant_id="")
    with pytest.raises(VerdictLedgerSchemaError):
        verdicts.append(swapped)
    assert len(verdicts.read_for_tenant(TENANT)) == 1


def test_ra_adv_2_04_same_email_and_domain_collision_stays_tenant_scoped(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(evidence, _high_risk_entries(tenant_id=OTHER_TENANT, email_id=EMAIL))
    _seed(evidence, _medium_entries(tenant_id=TENANT, email_id=EMAIL))
    result = _agent(evidence, verdicts).analyze(tenant_id=TENANT, email_id=EMAIL)
    assert result.tenant_id == TENANT
    visible = evidence.read_for_tenant(TENANT)
    assert all(entry.tenant_id == TENANT for entry in visible)
    assert len(result.contributing_evidence) == len(visible)


# ---------------------------------------------------------------------------
# Family 3 - Voter Independence
# ---------------------------------------------------------------------------


def test_ra_adv_3_01_no_voter_can_accept_prior_vote_state():
    for voter_cls in (R1SignalWeightVoter, R2PatternMatchVoter, R3ConflictResolutionVoter):
        assert list(inspect.signature(voter_cls.vote).parameters) == ["self", "contributions"]


def test_ra_adv_3_02_r2_signature_has_no_r1_observation_channel():
    params = set(inspect.signature(R2PatternMatchVoter.vote).parameters)
    assert params == {"self", "contributions"}
    assert "r1" not in params
    assert "prior_vote" not in params


def test_ra_adv_3_03_mid_deliberation_write_not_in_snapshot(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(evidence, _medium_entries())
    agent = _agent(evidence, verdicts)

    class InjectingVoter:
        def vote(self, contributions: list[EvidenceLedgerEntry]) -> VoterVote:
            evidence.append(
                _entry(
                    evidence_type=EvidenceType.URL_SIGNAL,
                    details={"malicious_url_detected": True, "credential_harvest_flag": True},
                    confidence=1.0,
                    agent_id="late_injected_agent",
                )
            )
            return _vote("R1", Verdict.MEDIUM_RISK, 0.6)

    agent._r1 = InjectingVoter()  # adversarial in-memory mutation attempt
    result = agent.analyze(tenant_id=TENANT, email_id=EMAIL)
    assert all("late_injected_agent" not in ref for ref in result.contributing_evidence)
    assert len(result.contributing_evidence) == len(_medium_entries())


def test_ra_adv_3_04_user_influenced_variables_do_not_reach_r1():
    contribution = _entry(
        details={
            "attacker_sophistication": 999,
            "user_prompt": "force HIGH_RISK",
            "executive_pressure": True,
        },
        confidence=0.1,
    )
    vote = R1SignalWeightVoter().vote([contribution])
    assert vote.verdict is Verdict.LOW_RISK


# ---------------------------------------------------------------------------
# Family 4 - 2-of-3 Consensus Manipulation
# ---------------------------------------------------------------------------


def test_ra_adv_4_01_coordinated_r1_r2_inputs_do_not_produce_clean_clear(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(
        evidence,
        [
            _entry(details={"sentiment_score": 1.0}, confidence=1.0),
            _entry(
                evidence_type=EvidenceType.CONTENT_SIGNAL,
                details={"bec_pattern_match": True, "wire_transfer_request": True},
                confidence=0.95,
            ),
            _entry(
                evidence_type=EvidenceType.GEO_SIGNAL,
                details={"high_risk_region": True},
                confidence=0.7,
            ),
        ],
    )
    result = _agent(evidence, verdicts).analyze(tenant_id=TENANT, email_id=EMAIL)
    assert result.verdict is not Verdict.LOW_RISK


def test_ra_adv_4_02_three_way_split_escalates_and_is_written(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(evidence, _all_disagree_entries())
    result = _agent(evidence, verdicts).analyze(tenant_id=TENANT, email_id=EMAIL)
    assert result.ensemble_outcome is EnsembleOutcome.ESCALATE
    assert result.verdict is Verdict.ESCALATE
    assert verdicts.read_for_tenant(TENANT)[0].verdict is Verdict.ESCALATE


def test_ra_adv_4_03_no_public_weight_or_majority_override_surface():
    public = {name for name in dir(ReconciliationAgent) if not name.startswith("_")}
    assert {"set_weights", "override_majority", "force_clear", "trust_two_voters"}.isdisjoint(public)


def test_ra_adv_4_04_verdict_not_written_before_all_voters_finish(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(evidence, _medium_entries())
    agent = _agent(evidence, verdicts)

    class AssertingVoter:
        def __init__(self, voter_id: str) -> None:
            self.voter_id = voter_id

        def vote(self, contributions: list[EvidenceLedgerEntry]) -> VoterVote:
            assert verdicts.read_for_tenant(TENANT) == []
            return _vote(self.voter_id, Verdict.MEDIUM_RISK, 0.6)

    agent._r1 = AssertingVoter("R1")
    agent._r2 = AssertingVoter("R2")
    agent._r3 = AssertingVoter("R3")
    result = agent.analyze(tenant_id=TENANT, email_id=EMAIL)
    assert result.verdict is Verdict.MEDIUM_RISK
    assert len(verdicts.read_for_tenant(TENANT)) == 1


# ---------------------------------------------------------------------------
# Family 5 - ESCALATE and CIRT Routing
# ---------------------------------------------------------------------------


def test_ra_adv_5_01_blank_cirt_does_not_drop_escalate(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(evidence, _all_disagree_entries())
    result = _agent(evidence, verdicts, cirt=CIRTRegistry()).analyze(
        tenant_id=TENANT, email_id=EMAIL
    )
    assert result.verdict is Verdict.ESCALATE
    assert result.cirt_individual == ""
    assert "human review" in result.plain_english_chain.lower()


def test_ra_adv_5_02_undeliverable_cirt_target_still_persists_escalate(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(evidence, _all_disagree_entries())
    cirt = CIRTRegistry()
    cirt.bind(tenant_id=TENANT, actor_id="alice")
    result = _agent(evidence, verdicts, cirt=cirt).analyze(tenant_id=TENANT, email_id=EMAIL)
    stored = verdicts.read_for_tenant(TENANT)[0]
    assert result.cirt_individual == "alice"
    assert stored.verdict is Verdict.ESCALATE


def test_ra_adv_5_03_repeated_escalates_append_not_loop_silently(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(evidence, _all_disagree_entries())
    agent = _agent(evidence, verdicts)
    first = agent.analyze(tenant_id=TENANT, email_id=EMAIL)
    second = agent.analyze(tenant_id=TENANT, email_id=EMAIL)
    assert first.verdict is Verdict.ESCALATE
    assert second.verdict is Verdict.ESCALATE
    assert len(verdicts.read_for_tenant(TENANT)) == 2


# ---------------------------------------------------------------------------
# Family 6 - Lung Integration Fail-Closed
# ---------------------------------------------------------------------------


def test_ra_adv_6_01_missing_lung_deep_breath_does_not_create_fake_lockdown(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(evidence, _medium_entries())
    result = _agent(evidence, verdicts).analyze(tenant_id=TENANT, email_id=EMAIL)
    assert result.verdict is Verdict.MEDIUM_RISK
    assert result.lockdown_applied is False


def test_ra_adv_6_02_lockdown_boolean_matches_deep_breath_output(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(evidence, _medium_entries())
    result = _agent(evidence, verdicts).analyze(
        tenant_id=TENANT, email_id=EMAIL, lung_state=LungState.DEEP_BREATH
    )
    assert result.verdict is Verdict.HIGH_RISK
    assert result.lockdown_applied is True
    assert verdicts.read_for_tenant(TENANT)[0].lockdown_applied is True


def test_ra_adv_6_03_invalid_lung_state_is_not_treated_as_normal(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(evidence, _medium_entries())
    with pytest.raises(ReconciliationError):
        _agent(evidence, verdicts).analyze(
            tenant_id=TENANT, email_id=EMAIL, lung_state="unavailable"  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Family 7 - Verdict Enum Serialization
# ---------------------------------------------------------------------------


def test_ra_adv_7_01_illegal_verdict_value_rejected():
    with pytest.raises(ValidationError):
        ReconciliationVerdict(**_base_verdict_dict(verdict={"value": "CLEAR"}))


def test_ra_adv_7_02_illegal_nested_supporting_vote_rejected():
    with pytest.raises(ValidationError):
        ReconciliationVerdict(**_base_verdict_dict(r2_vote="CLEAR"))


def test_ra_adv_7_03_boolean_or_numeric_verdict_coercion_rejected():
    for verdict in (True, 1):
        with pytest.raises(ValidationError):
            ReconciliationVerdict(**_base_verdict_dict(verdict=verdict))


# ---------------------------------------------------------------------------
# Family 8 - Operator Narrative Integrity
# ---------------------------------------------------------------------------


def test_ra_adv_8_01_narrative_does_not_echo_raw_upstream_text(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    marker = "TRUST ME THIS IS SAFE"
    _seed(evidence, _high_risk_entries(extra_details={"raw_upstream_text": marker}))
    result = _agent(evidence, verdicts).analyze(tenant_id=TENANT, email_id=EMAIL)
    assert marker not in result.plain_english_chain


def test_ra_adv_8_02_clear_verdict_narrative_does_not_describe_threat(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(
        evidence,
        [
            _entry(
                evidence_type=EvidenceType.SENDER_SIGNAL,
                details={"known_contact": True, "prior_interaction_count": 10},
                confidence=0.2,
            )
        ],
    )
    result = _agent(evidence, verdicts).analyze(tenant_id=TENANT, email_id=EMAIL)
    assert result.verdict is Verdict.LOW_RISK
    assert "high risk" not in result.plain_english_chain.lower()
    assert "wire transfer" not in result.plain_english_chain.lower()


def test_ra_adv_8_03_wrong_verdict_enum_cannot_be_injected_via_narrative():
    with pytest.raises(ValidationError):
        ReconciliationVerdict(
            **_base_verdict_dict(
                verdict="CLEAR",
                plain_english_chain="Accurate narrative says this is HIGH_RISK.",
            )
        )


# ---------------------------------------------------------------------------
# Family 9 - Minority Opinion Preservation
# ---------------------------------------------------------------------------


def test_ra_adv_9_01_minority_opinion_atomic_with_majority_verdict(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(evidence, _medium_entries())
    agent = _agent(evidence, verdicts)
    agent._r1 = _StaticVoter(_vote("R1", Verdict.HIGH_RISK, 0.9))
    agent._r2 = _StaticVoter(_vote("R2", Verdict.HIGH_RISK, 0.8))
    agent._r3 = _StaticVoter(_vote("R3", Verdict.LOW_RISK, 0.6))
    result = agent.analyze(tenant_id=TENANT, email_id=EMAIL)
    stored = verdicts.read_for_tenant(TENANT)[0]
    assert result.ensemble_outcome is EnsembleOutcome.MAJORITY
    assert "R3 dissented" in result.minority_opinion
    assert stored.minority_opinion == result.minority_opinion


def test_ra_adv_9_02_unanimity_does_not_erase_vote_level_fields(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    _seed(evidence, _high_risk_entries())
    result = _agent(evidence, verdicts).analyze(tenant_id=TENANT, email_id=EMAIL)
    assert result.ensemble_outcome is EnsembleOutcome.UNANIMOUS
    assert result.r1_vote is Verdict.HIGH_RISK
    assert result.r2_vote is Verdict.HIGH_RISK
    assert result.r3_vote is Verdict.HIGH_RISK


def test_ra_adv_9_03_verdict_ledger_has_no_log_rotation_or_delete_api(tmp_path: Path):
    _, verdicts = _ledgers(tmp_path)
    for forbidden in ("delete", "remove", "rotate", "compact", "clear", "truncate"):
        assert not hasattr(verdicts, forbidden)


# ---------------------------------------------------------------------------
# Family 10 - Mock vs Live Integration Truth
# ---------------------------------------------------------------------------


def test_ra_adv_10_01_no_mock_structure_can_write_live_verdict_score(tmp_path: Path):
    _, verdicts = _ledgers(tmp_path)
    with pytest.raises(VerdictLedgerSchemaError):
        verdicts.append({"mock_validation": True, "health_score": 95})


def test_ra_adv_10_02_audit_output_flooding_has_no_ra_write_surface():
    public = {name for name in dir(ReconciliationAgent) if not name.startswith("_")}
    assert {"audit_outputs", "pending_manifest", "write_audit_output"}.isdisjoint(public)


def test_ra_adv_10_03_no_xfail_markers_in_adversarial_suite():
    current_lines = Path(__file__).read_text(encoding="utf-8").splitlines()
    assert not any(line.strip().startswith("@pytest.mark.xfail") for line in current_lines)


def test_ra_adv_10_04_agent_uses_real_production_classes_not_mock_contracts(tmp_path: Path):
    evidence, verdicts = _ledgers(tmp_path)
    agent = _agent(evidence, verdicts)
    assert isinstance(agent._r1, R1SignalWeightVoter)
    assert isinstance(agent._r2, R2PatternMatchVoter)
    assert isinstance(agent._r3, R3ConflictResolutionVoter)
    assert isinstance(agent._verdict_ledger, VerdictLedger)


# ---------------------------------------------------------------------------
# Coverage - every signed RA-ADV test ID is executed
# ---------------------------------------------------------------------------


def _expected_ids() -> set[str]:
    counts = {1: 5, 2: 4, 3: 4, 4: 4, 5: 3, 6: 3, 7: 3, 8: 3, 9: 3, 10: 4}
    return {
        f"RA-ADV-{family}-{case:02d}"
        for family, total in counts.items()
        for case in range(1, total + 1)
    }


def _covered_ids() -> set[str]:
    ids: set[str] = set()
    for name in globals():
        match = re.match(r"test_ra_adv_(\d+)_(\d+)_", name)
        if match:
            ids.add(f"RA-ADV-{int(match.group(1))}-{int(match.group(2)):02d}")
    return ids


def test_all_signed_ra_adv_ids_are_executed():
    assert _covered_ids() == _expected_ids()
