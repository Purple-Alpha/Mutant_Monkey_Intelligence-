"""Mode A ledger gate tests — Blackboard-Mesh §6 infrastructure build bar (slice 1)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.blackboard import (
    CanonicalEvidenceLedger,
    EvidenceStage,
    EvidenceType,
    LedgerSchemaError,
    ReconciliationVerdict,
    Verdict,
    VerdictLedger,
    VerdictLedgerSchemaError,
)
from core.blackboard.mode_a_gate import (
    RECONCILIATION_WRITER_AGENT_ID,
    load_authority_shadow_tokens,
    validate_raw_evidence_dict,
)
from core.control_plane.semantic_filter import SemanticFilter


def _valid_evidence_dict(**overrides) -> dict:
    base = {
        "agent_id": "header_analysis",
        "tenant_id": "tenant_a",
        "email_id": "email_001",
        "evidence_type": "header_signal",
        "details": {"divergence": "from_vs_reply_to"},
        "confidence": 0.72,
        "stage": "ES1",
    }
    base.update(overrides)
    return base


def _minimal_verdict_dict() -> dict:
    return {
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
        "plain_english_chain": "observation only",
    }


def test_rejects_forbidden_top_level_key(tmp_path):
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    with pytest.raises(LedgerSchemaError, match="forbidden top-level"):
        ledger.append(_valid_evidence_dict(verdict="HIGH_RISK"))


def test_rejects_writer_metadata_keys(tmp_path):
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    with pytest.raises(LedgerSchemaError, match="writer metadata"):
        ledger.append(_valid_evidence_dict(entry_id="00000000-0000-0000-0000-000000000001"))


def test_rejects_authority_shadow_token_in_details(tmp_path):
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    with pytest.raises(LedgerSchemaError, match="authority-shadow"):
        ledger.append(
            _valid_evidence_dict(details={"note": "message is approved for release"})
        )


def test_benign_observation_payload_passes_mode_a_and_semantic_filter(tmp_path):
    payload = _valid_evidence_dict(
        details={"observed_facts": ["reply-to domain mismatch", "spf neutral"]}
    )
    validate_raw_evidence_dict(payload, shadow_tokens=load_authority_shadow_tokens())
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    ledger.append(payload)
    assert SemanticFilter().scan_value(payload) == ()


def test_non_reconciliation_agent_cannot_append_verdict(tmp_path):
    ledger = VerdictLedger(tmp_path / "verdicts.jsonl")
    with pytest.raises(VerdictLedgerSchemaError, match="reconciliation_agent_001"):
        ledger.append(
            _minimal_verdict_dict(),
            writer_agent_id="payroll_diversion_001",
        )


def test_reconciliation_agent_may_append_verdict(tmp_path):
    ledger = VerdictLedger(tmp_path / "verdicts.jsonl")
    written = ledger.append(
        _minimal_verdict_dict(),
        writer_agent_id=RECONCILIATION_WRITER_AGENT_ID,
    )
    assert isinstance(written, ReconciliationVerdict)
    assert written.verdict is Verdict.LOW_RISK


def test_verdict_rejects_shadow_token_in_plain_english_chain(tmp_path):
    ledger = VerdictLedger(tmp_path / "verdicts.jsonl")
    bad = _minimal_verdict_dict()
    bad["plain_english_chain"] = "case is approved for release"
    with pytest.raises(VerdictLedgerSchemaError, match="authority-shadow"):
        ledger.append(bad, writer_agent_id=RECONCILIATION_WRITER_AGENT_ID)


def test_cross_tenant_evidence_isolation(tmp_path):
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    ledger.append(_valid_evidence_dict(tenant_id="tenant_a", email_id="a1"))
    ledger.append(_valid_evidence_dict(tenant_id="tenant_b", email_id="b1"))
    assert {row.email_id for row in ledger.read_for_tenant("tenant_a")} == {"a1"}
    assert {row.email_id for row in ledger.read_for_tenant("tenant_b")} == {"b1"}


def test_rejected_write_logged_with_agent_id(tmp_path):
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    with pytest.raises(LedgerSchemaError):
        ledger.append(
            _valid_evidence_dict(
                agent_id="payroll_diversion_001",
                details={"status": "cleared for processing"},
            )
        )
    audit = json.loads(ledger.governance_audit_path.read_text(encoding="utf-8").strip())
    assert audit["event"] == "evidence_ledger_write_rejected"
    assert "payroll_diversion_001" in audit["reason"]


def test_shadow_token_config_is_version_pinned(tmp_path):
    config = tmp_path / "tokens.json"
    config.write_text(
        json.dumps({"version": "v1", "evidence_tokens": ["customshadow"]}),
        encoding="utf-8",
    )
    with pytest.raises(Exception, match="customshadow"):
        validate_raw_evidence_dict(
            _valid_evidence_dict(details={"x": "customshadow token seen"}),
            shadow_tokens=load_authority_shadow_tokens(config),
        )
