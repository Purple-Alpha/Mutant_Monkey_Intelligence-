"""Evidence Backer tests — Blackboard-Mesh §6 infrastructure build bar (slice 2)."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from core.blackboard import (
    CanonicalEvidenceLedger,
    EvidenceLedgerEntry,
    EvidenceStage,
    EvidenceType,
    Verdict,
    VerdictLedger,
)
from core.blackboard.evidence_backer import (
    EvidenceBacker,
    EvidenceBackerVerdict,
    evidence_ref,
)
from core.blackboard.mode_a_gate import RECONCILIATION_WRITER_AGENT_ID
from core.blackboard.models import (
    AgentContributionPayload,
    BlackboardRecord,
    EmailInboundPayload,
    Environment,
    RecordType,
)
from core.blackboard.storage import append_record


def _entry(**overrides) -> EvidenceLedgerEntry:
    base = dict(
        agent_id="header_analysis",
        tenant_id="tenant_a",
        email_id="email_001",
        evidence_type=EvidenceType.HEADER_SIGNAL,
        details={"signal": "reply_to_mismatch"},
        confidence=0.7,
        stage=EvidenceStage.ES1,
    )
    base.update(overrides)
    return EvidenceLedgerEntry(**base)


def _verdict(**overrides) -> dict:
    base = {
        "email_id": "email_001",
        "tenant_id": "tenant_a",
        "verdict": "LOW_RISK",
        "ensemble_outcome": "unanimous",
        "overall_confidence": 0.8,
        "r1_vote": "LOW_RISK",
        "r1_confidence": 0.8,
        "r2_vote": "LOW_RISK",
        "r2_confidence": 0.8,
        "r3_vote": "LOW_RISK",
        "r3_confidence": 0.8,
        "plain_english_chain": "observation chain only",
        "contributing_evidence": [],
    }
    base.update(overrides)
    return base


def _backer(tmp_path, *, decision_log: str = "MMI-DEC-000 | unrelated") -> EvidenceBacker:
    evidence = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    verdict = VerdictLedger(tmp_path / "verdicts.jsonl")
    blackboard = tmp_path / "production" / "tenant_a.jsonl"
    decision_path = tmp_path / "MMI_DECISION_LOG.md"
    decision_path.write_text(decision_log, encoding="utf-8")
    return EvidenceBacker(
        blackboard_paths=[blackboard],
        evidence_ledger=evidence,
        verdict_ledger=verdict,
        decision_log_path=decision_path,
    ), evidence, verdict, blackboard


def test_provable_chain(tmp_path):
    backer, evidence, verdict, blackboard = _backer(
        tmp_path, decision_log="MMI-DEC-100 | email_001 accepted"
    )
    first = evidence.append(_entry())
    second = evidence.append(
        _entry(agent_id="email_authentication", evidence_type=EvidenceType.AUTHENTICATION_SIGNAL)
    )
    verdict.append(
        _verdict(
            contributing_evidence=[evidence_ref(first), evidence_ref(second)],
        ),
        writer_agent_id=RECONCILIATION_WRITER_AGENT_ID,
    )
    append_record(
        blackboard,
        BlackboardRecord(
            tenant_id="tenant_a",
            environment=Environment.PRODUCTION,
            record_type=RecordType.EMAIL_INBOUND,
            source_agent="ingest_001",
            payload=EmailInboundPayload(
                received_at=datetime.now(timezone.utc),
                sender="a@example.com",
                recipient="b@example.com",
                body_plain="email_001 body",
            ).model_dump(mode="json"),
        ),
    )
    report = backer.verify(tenant_id="tenant_a", email_id="email_001")
    assert report.verdict is EvidenceBackerVerdict.PROVABLE


def test_violation_on_orphan_contributing_evidence_ref(tmp_path):
    backer, evidence, verdict, _ = _backer(tmp_path)
    evidence.append(_entry())
    verdict.append(
        _verdict(contributing_evidence=["header_signal:missing:email_001"]),
        writer_agent_id=RECONCILIATION_WRITER_AGENT_ID,
    )
    report = backer.verify(tenant_id="tenant_a", email_id="email_001")
    assert report.verdict is EvidenceBackerVerdict.VIOLATION
    assert any("orphan contributing_evidence" in item for item in report.findings)


def test_incomplete_when_human_gate_required_without_dec(tmp_path):
    backer, evidence, verdict, _ = _backer(tmp_path, decision_log="MMI-DEC-200 | other case")
    written = evidence.append(_entry())
    verdict.append(
        _verdict(
            verdict="HIGH_RISK",
            r1_vote="HIGH_RISK",
            r2_vote="HIGH_RISK",
            r3_vote="HIGH_RISK",
            contributing_evidence=[evidence_ref(written)],
        ),
        writer_agent_id=RECONCILIATION_WRITER_AGENT_ID,
    )
    report = backer.verify(tenant_id="tenant_a", email_id="email_001")
    assert report.verdict is EvidenceBackerVerdict.INCOMPLETE
    assert report.dec_record_found is False


def test_incomplete_on_omission_as_safety_sparse_evidence(tmp_path):
    backer, evidence, verdict, _ = _backer(tmp_path)
    written = evidence.append(_entry())
    verdict.append(
        _verdict(contributing_evidence=[evidence_ref(written)]),
        writer_agent_id=RECONCILIATION_WRITER_AGENT_ID,
    )
    report = backer.verify(tenant_id="tenant_a", email_id="email_001")
    assert report.verdict is EvidenceBackerVerdict.INCOMPLETE
    assert any("omission-as-safety" in item for item in report.findings)


def test_violation_on_cross_tenant_evidence_leak(tmp_path):
    backer, evidence, _, _ = _backer(tmp_path)
    evidence.append(_entry(tenant_id="tenant_b", email_id="email_001"))
    report = backer.verify(tenant_id="tenant_a", email_id="email_001")
    assert report.verdict is EvidenceBackerVerdict.VIOLATION
    assert any("cross-tenant leak" in item for item in report.findings)


def test_not_applicable_when_no_graph_nodes(tmp_path):
    backer, _, _, _ = _backer(tmp_path)
    report = backer.verify(tenant_id="tenant_a", email_id="missing")
    assert report.verdict is EvidenceBackerVerdict.NOT_APPLICABLE


def test_reads_agent_contribution_blackboard_path(tmp_path):
    backer, evidence, verdict, blackboard = _backer(tmp_path)
    written = evidence.append(_entry())
    verdict.append(
        _verdict(contributing_evidence=[evidence_ref(written)]),
        writer_agent_id=RECONCILIATION_WRITER_AGENT_ID,
    )
    append_record(
        blackboard,
        BlackboardRecord(
            tenant_id="tenant_a",
            environment=Environment.PRODUCTION,
            record_type=RecordType.AGENT_CONTRIBUTION,
            source_agent="header_analysis",
            payload=AgentContributionPayload(
                case_id=uuid4(),
                inputs_digest="digest-email_001",
                agent_id="header_analysis",
                layer=2,
                observed_facts=["reply_to mismatch"],
            ).model_dump(mode="json"),
        ),
    )
    report = backer.verify(tenant_id="tenant_a", email_id="email_001")
    assert report.contribution_count == 1
    assert report.verdict is EvidenceBackerVerdict.INCOMPLETE
