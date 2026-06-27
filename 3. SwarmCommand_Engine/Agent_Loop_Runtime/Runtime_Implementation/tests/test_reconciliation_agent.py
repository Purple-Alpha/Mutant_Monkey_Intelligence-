"""Phase 4 — ReconciliationAgent ensemble tests.

Three test classes per AGENTS.md §5 and
``Phase4_ReconciliationAgent_Contract.md`` §11:
  Class 1 — expected pass
  Class 2 — adversarial / break-it (P4-D4, P4-D6, P4-D8, §5 enum closure, §8)
  Class 3 — known-gap xfail (documented, with completion path)
"""

from __future__ import annotations

import inspect
from pathlib import Path
import pytest
from pydantic import ValidationError

from core.blackboard import (
    CanonicalEvidenceLedger,
    EvidenceLedgerEntry,
    EvidenceStage,
    EvidenceType,
    EnsembleOutcome,
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
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def evidence_ledger(tmp_path: Path) -> CanonicalEvidenceLedger:
    return CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")


@pytest.fixture
def verdict_ledger(tmp_path: Path) -> VerdictLedger:
    return VerdictLedger(tmp_path / "verdicts.jsonl")


def _entry(
    *,
    tenant_id: str = "tenant-a",
    email_id: str = "email-001",
    evidence_type: EvidenceType,
    details: dict,
    confidence: float,
    agent_id: str = "test_agent",
) -> EvidenceLedgerEntry:
    return EvidenceLedgerEntry(
        agent_id=agent_id,
        tenant_id=tenant_id,
        email_id=email_id,
        evidence_type=evidence_type,
        details=details,
        confidence=confidence,
        stage=EvidenceStage.ES2,
    )


def _seed(
    ledger: CanonicalEvidenceLedger,
    entries: list[EvidenceLedgerEntry],
) -> None:
    for entry in entries:
        ledger.append(entry)


def _make_agent(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
    *,
    cirt: CIRTRegistry | None = None,
) -> ReconciliationAgent:
    return ReconciliationAgent(evidence_ledger, verdict_ledger, cirt_registry=cirt)


def _high_risk_contributions(
    *,
    tenant_id: str = "tenant-a",
    email_id: str = "email-001",
) -> list[EvidenceLedgerEntry]:
    """Contributions tuned so R1/R2/R3 all cast HIGH_RISK (unanimous)."""

    return [
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.GEO_SIGNAL,
            details={
                "high_risk_region": True,
                "velocity_flag": True,
                "vpn_detected": False,
            },
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
                "ceo_impersonation_flag": False,
                "urgency_detected": True,
                "sentiment_score": 0.8,
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
            },
            confidence=0.9,
            agent_id="url_receptor",
        ),
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.ATTACHMENT_SIGNAL,
            details={
                "known_malicious_hash": True,
                "network_callback_detected": True,
            },
            confidence=0.95,
            agent_id="attachment_sandbox",
        ),
    ]


def _majority_contributions(
    *,
    tenant_id: str = "tenant-a",
    email_id: str = "email-001",
) -> list[EvidenceLedgerEntry]:
    """R1/R3 → HIGH_RISK; R2 → MEDIUM_RISK (2-of-3 majority HIGH)."""

    return [
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.GEO_SIGNAL,
            details={
                "high_risk_region": True,
                "velocity_flag": True,
                "vpn_detected": False,
            },
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
            },
            confidence=0.9,
            agent_id="sender_history_agent",
        ),
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.CONTENT_SIGNAL,
            details={
                "urgency_detected": True,
                "sentiment_score": 0.2,
            },
            confidence=0.55,
            agent_id="content_analyzer",
        ),
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.URL_SIGNAL,
            details={
                "malicious_url_detected": False,
                "reputation_score": 1.0,
            },
            confidence=0.95,
            agent_id="url_receptor",
        ),
    ]


def _all_disagree_contributions(
    *,
    tenant_id: str = "tenant-a",
    email_id: str = "email-001",
) -> list[EvidenceLedgerEntry]:
    """R1 LOW, R2 HIGH, R3 MEDIUM — all three distinct → ESCALATE."""

    return [
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.SENDER_SIGNAL,
            details={"known_contact": True, "prior_interaction_count": 2},
            confidence=0.2,
            agent_id="sender_history_agent",
        ),
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.GEO_SIGNAL,
            details={
                "high_risk_region": False,
                "velocity_flag": False,
                "sender_history_match": True,
            },
            confidence=0.2,
            agent_id="geo_velocity_agent",
        ),
        _entry(
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_type=EvidenceType.CONTENT_SIGNAL,
            details={
                "bec_pattern_match": True,
                "wire_transfer_request": True,
                "sentiment_score": 0.1,
            },
            confidence=0.95,
            agent_id="content_analyzer",
        ),
    ]


# ---------------------------------------------------------------------------
# Class 1 — Expected pass (contract §11)
# ---------------------------------------------------------------------------


def test_voters_cast_verdict_and_confidence_in_range(
    evidence_ledger: CanonicalEvidenceLedger,
):
    contributions = _high_risk_contributions()
    for voter in (
        R1SignalWeightVoter(),
        R2PatternMatchVoter(),
        R3ConflictResolutionVoter(),
    ):
        vote = voter.vote(contributions)
        assert vote.verdict in (Verdict.HIGH_RISK, Verdict.MEDIUM_RISK, Verdict.LOW_RISK)
        assert 0.0 <= vote.confidence <= 1.0


def test_unanimous_high_risk_outcome(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
):
    _seed(evidence_ledger, _high_risk_contributions())
    agent = _make_agent(evidence_ledger, verdict_ledger)
    result = agent.analyze(tenant_id="tenant-a", email_id="email-001")

    assert result.verdict is Verdict.HIGH_RISK
    assert result.ensemble_outcome is EnsembleOutcome.UNANIMOUS
    assert result.minority_opinion == ""
    assert result.plain_english_chain


def test_majority_outcome_logs_minority(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
):
    _seed(evidence_ledger, _majority_contributions())
    agent = _make_agent(evidence_ledger, verdict_ledger)
    result = agent.analyze(tenant_id="tenant-a", email_id="email-001")

    assert result.ensemble_outcome is EnsembleOutcome.MAJORITY
    assert result.verdict is Verdict.HIGH_RISK
    assert "R2" in result.minority_opinion
    assert result.minority_opinion


def test_all_disagree_escalates_no_verdict(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
):
    _seed(evidence_ledger, _all_disagree_contributions())
    cirt = CIRTRegistry()
    cirt.bind(tenant_id="tenant-a", actor_id="todd")
    agent = _make_agent(evidence_ledger, verdict_ledger, cirt=cirt)
    result = agent.analyze(tenant_id="tenant-a", email_id="email-001")

    assert result.ensemble_outcome is EnsembleOutcome.ESCALATE
    assert result.verdict is Verdict.ESCALATE
    assert result.cirt_individual == "todd"
    assert "R1" in result.minority_opinion
    assert "R2" in result.minority_opinion
    assert "R3" in result.minority_opinion


def test_verdict_written_tenant_isolated_with_plain_english_chain(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
):
    _seed(evidence_ledger, _high_risk_contributions())
    agent = _make_agent(evidence_ledger, verdict_ledger)
    result = agent.analyze(tenant_id="tenant-a", email_id="email-001")

    stored = verdict_ledger.read_for_tenant("tenant-a")
    assert len(stored) == 1
    assert stored[0].verdict_id == result.verdict_id
    assert stored[0].tenant_id == "tenant-a"
    assert len(stored[0].plain_english_chain) > 20
    assert stored[0].contributing_evidence


def test_spam_signal_only_routes_delivery_problem(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
):
    _seed(
        evidence_ledger,
        [
            _entry(
                evidence_type=EvidenceType.IMAGE_SIGNAL,
                details={
                    "spam_signal_only": True,
                    "bulk_content_flag": True,
                    "ai_generated_detected": False,
                },
                confidence=0.6,
                agent_id="image_classifier",
            )
        ],
    )
    agent = _make_agent(evidence_ledger, verdict_ledger)
    result = agent.analyze(tenant_id="tenant-a", email_id="email-001")

    assert result.verdict is Verdict.DELIVERY_PROBLEM
    assert result.delivery_problem_path is True


def test_zero_day_referred_without_changing_verdict(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
):
    _seed(
        evidence_ledger,
        [
            _entry(
                evidence_type=EvidenceType.ATTACHMENT_SIGNAL,
                details={
                    "zero_day_candidate": True,
                    "attachment_present": True,
                    "known_malicious_hash": False,
                },
                confidence=0.75,
                agent_id="attachment_sandbox",
            ),
            _entry(
                evidence_type=EvidenceType.SENDER_SIGNAL,
                details={"known_contact": True, "prior_interaction_count": 5},
                confidence=0.6,
                agent_id="sender_history_agent",
            ),
        ],
    )
    agent = _make_agent(evidence_ledger, verdict_ledger)
    result = agent.analyze(tenant_id="tenant-a", email_id="email-001")

    assert result.zero_day_referred is True
    assert result.verdict is not Verdict.HIGH_RISK


def test_lockdown_medium_plus_deep_breath_becomes_high_risk(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
):
    # Single fraud indicator → R2 MEDIUM; R1/R3 also moderate → majority MEDIUM.
    _seed(
        evidence_ledger,
        [
            _entry(
                evidence_type=EvidenceType.CONTENT_SIGNAL,
                details={"urgency_detected": True, "sentiment_score": 0.5},
                confidence=0.55,
                agent_id="content_analyzer",
            ),
            _entry(
                evidence_type=EvidenceType.SENDER_SIGNAL,
                details={"known_contact": True, "prior_interaction_count": 3},
                confidence=0.6,
                agent_id="sender_history_agent",
            ),
        ],
    )
    agent = _make_agent(evidence_ledger, verdict_ledger)
    result = agent.analyze(
        tenant_id="tenant-a",
        email_id="email-001",
        lung_state=LungState.DEEP_BREATH,
    )

    assert result.lockdown_applied is True
    assert result.verdict is Verdict.HIGH_RISK


# ---------------------------------------------------------------------------
# Class 2 — Adversarial (contract §11)
# ---------------------------------------------------------------------------


def test_voter_independence_no_cross_vote_parameter():
    """P4-D6: voters cannot see one another's votes before casting."""

    for voter_cls in (
        R1SignalWeightVoter,
        R2PatternMatchVoter,
        R3ConflictResolutionVoter,
    ):
        sig = inspect.signature(voter_cls.vote)
        assert list(sig.parameters.keys()) == ["self", "contributions"]


def test_verdict_outside_closed_enum_rejected():
    with pytest.raises(ValidationError):
        ReconciliationVerdict(
            email_id="e1",
            tenant_id="tenant-a",
            verdict="NOT_A_VERDICT",  # type: ignore[arg-type]
            ensemble_outcome=EnsembleOutcome.UNANIMOUS,
            overall_confidence=0.5,
            r1_vote=Verdict.LOW_RISK,
            r1_confidence=0.5,
            r2_vote=Verdict.LOW_RISK,
            r2_confidence=0.5,
            r3_vote=Verdict.LOW_RISK,
            r3_confidence=0.5,
            plain_english_chain="test",
        )


def test_all_disagree_cannot_silently_emit_non_escalate_verdict(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
):
    _seed(evidence_ledger, _all_disagree_contributions())
    agent = _make_agent(evidence_ledger, verdict_ledger)
    result = agent.analyze(tenant_id="tenant-a", email_id="email-001")

    assert result.ensemble_outcome is EnsembleOutcome.ESCALATE
    assert result.verdict is Verdict.ESCALATE
    assert result.verdict not in (Verdict.HIGH_RISK, Verdict.MEDIUM_RISK, Verdict.LOW_RISK)


def test_cross_tenant_read_blocked(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
):
    _seed(evidence_ledger, _high_risk_contributions(tenant_id="tenant-a"))
    agent = _make_agent(evidence_ledger, verdict_ledger)

    with pytest.raises(ReconciliationError, match="no Layer 1 contributions"):
        agent.analyze(tenant_id="tenant-b", email_id="email-001")

    assert verdict_ledger.read_for_tenant("tenant-b") == []


def test_cross_tenant_verdict_write_isolated(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
):
    _seed(evidence_ledger, _high_risk_contributions(tenant_id="tenant-a"))
    agent = _make_agent(evidence_ledger, verdict_ledger)
    agent.analyze(tenant_id="tenant-a", email_id="email-001")

    assert len(verdict_ledger.read_for_tenant("tenant-a")) == 1
    assert len(verdict_ledger.read_for_tenant("tenant-b")) == 0


def test_r1_isolated_from_sophistication_rubric_parameter():
    """P4-D4: R1 vote() accepts only contributions — no rubric/Lung/human input."""

    sig = inspect.signature(R1SignalWeightVoter.vote)
    assert list(sig.parameters.keys()) == ["self", "contributions"]


def test_malformed_empty_contribution_set_safe_error(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
):
    agent = _make_agent(evidence_ledger, verdict_ledger)
    with pytest.raises(ReconciliationError, match="no Layer 1 contributions"):
        agent.analyze(tenant_id="tenant-a", email_id="missing-email")


def test_spam_signal_only_must_not_route_high_risk(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
):
    _seed(
        evidence_ledger,
        [
            _entry(
                evidence_type=EvidenceType.IMAGE_SIGNAL,
                details={"spam_signal_only": True, "bulk_content_flag": True},
                confidence=0.9,
                agent_id="image_classifier",
            ),
            *_high_risk_contributions(),
        ],
    )
    agent = _make_agent(evidence_ledger, verdict_ledger)
    result = agent.analyze(tenant_id="tenant-a", email_id="email-001")

    assert result.verdict is Verdict.DELIVERY_PROBLEM
    assert result.verdict is not Verdict.HIGH_RISK


def test_zero_day_does_not_alter_verdict(
    evidence_ledger: CanonicalEvidenceLedger,
    verdict_ledger: VerdictLedger,
):
    low_only = [
        _entry(
            evidence_type=EvidenceType.SENDER_SIGNAL,
            details={"known_contact": True, "prior_interaction_count": 2},
            confidence=0.55,
            agent_id="sender_history_agent",
        ),
        _entry(
            evidence_type=EvidenceType.ATTACHMENT_SIGNAL,
            details={"zero_day_candidate": True, "attachment_present": True},
            confidence=0.75,
            agent_id="attachment_sandbox",
        ),
    ]
    _seed(evidence_ledger, low_only)
    agent = _make_agent(evidence_ledger, verdict_ledger)
    result = agent.analyze(tenant_id="tenant-a", email_id="email-001")

    assert result.zero_day_referred is True
    # Without zero-day the verdict would be the same — zero-day is recorded only.
    _seed(evidence_ledger, low_only[:1])
    agent2 = ReconciliationAgent(
        evidence_ledger, VerdictLedger(verdict_ledger.ledger_path.parent / "v2.jsonl")
    )
    result2 = agent2.analyze(tenant_id="tenant-a", email_id="email-001")
    assert result.verdict == result2.verdict


def test_verdict_ledger_rejects_extra_fields():
    with pytest.raises(VerdictLedgerSchemaError):
        VerdictLedger(Path("/tmp/unused-verdict.jsonl")).append(
            {
                "email_id": "e1",
                "tenant_id": "tenant-a",
                "verdict": "HIGH_RISK",
                "ensemble_outcome": "unanimous",
                "overall_confidence": 0.9,
                "r1_vote": "HIGH_RISK",
                "r1_confidence": 0.9,
                "r2_vote": "HIGH_RISK",
                "r2_confidence": 0.9,
                "r3_vote": "HIGH_RISK",
                "r3_confidence": 0.9,
                "plain_english_chain": "test",
                "smuggled_field": True,
            },
            writer_agent_id="reconciliation_agent_001",
        )


# ---------------------------------------------------------------------------
# Class 3 — Known-gap xfail (contract §11)
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    reason=(
        "Real-tenant verdict calibration — deferred. Equal weights at launch; "
        "weight tuning needs real data + signed amendment (§6). "
        "Completion path: post-onboarding amendment."
    ),
    strict=True,
)
def test_xfail_real_tenant_verdict_calibration():
    raise AssertionError("not implemented — post-onboarding signed amendment required")


@pytest.mark.xfail(
    reason=(
        "Lung live integration — deferred. Lung is a separate unbuilt contract. "
        "Completion path: after Lung contract."
    ),
    strict=True,
)
def test_xfail_lung_live_integration():
    raise AssertionError("not implemented — Lung contract required")


@pytest.mark.xfail(
    reason=(
        "CIRT freeze-authority live wiring — deferred. Operator-state/onboarding "
        "surface. Completion path: onboarding integration."
    ),
    strict=True,
)
def test_xfail_cirt_freeze_authority_live_wiring():
    raise AssertionError("not implemented — onboarding integration required")
