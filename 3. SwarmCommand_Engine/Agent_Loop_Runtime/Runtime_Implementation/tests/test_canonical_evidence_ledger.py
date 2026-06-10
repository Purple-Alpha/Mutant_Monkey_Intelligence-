"""Phase 1 Infrastructure — Component 1 (Canonical Evidence Ledger) tests.

Three test classes per AGENTS.md §5 and Phase1_Infrastructure_Agent_Design_Contract §5:
  Class 1 — expected pass
  Class 2 — adversarial / break-it
  Class 3 — known-gap xfail (documented, with completion path)
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from core.blackboard import (
    CANONICAL_EVIDENCE_LEDGER_CONTRACT,
    CanonicalEvidenceLedger,
    EvidenceLedgerEntry,
    EvidenceStage,
    EvidenceType,
    LedgerError,
    LedgerSchemaError,
)


def _entry(**overrides) -> EvidenceLedgerEntry:
    base = dict(
        agent_id="header_analysis",
        tenant_id="tenant_a",
        email_id="email_001",
        evidence_type=EvidenceType.HEADER_SIGNAL,
        details={"divergence": "from_vs_reply_to"},
        confidence=0.72,
        stage=EvidenceStage.ES1,
    )
    base.update(overrides)
    return EvidenceLedgerEntry(**base)


# ---------------------------------------------------------------------------
# Class 1 — Expected pass
# ---------------------------------------------------------------------------


def test_valid_entry_writes_and_reads_back(tmp_path):
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    written = ledger.append(_entry())
    rows = ledger.read_for_tenant("tenant_a")
    assert len(rows) == 1
    assert rows[0].entry_id == written.entry_id
    assert rows[0].evidence_type is EvidenceType.HEADER_SIGNAL
    assert rows[0].agent_id == "header_analysis"


def test_append_accepts_validated_dict(tmp_path):
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    ledger.append(
        {
            "agent_id": "email_authentication",
            "tenant_id": "tenant_a",
            "email_id": "email_002",
            "evidence_type": "authentication_signal",
            "details": {"spf": "pass"},
            "confidence": 0.5,
            "stage": "ES1",
        }
    )
    rows = ledger.read_for_tenant("tenant_a")
    assert len(rows) == 1
    assert rows[0].evidence_type is EvidenceType.AUTHENTICATION_SIGNAL


def test_tenant_isolation_confirmed(tmp_path):
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    ledger.append(_entry(tenant_id="tenant_a", email_id="a1"))
    ledger.append(_entry(tenant_id="tenant_b", email_id="b1"))
    ledger.append(_entry(tenant_id="tenant_a", email_id="a2"))

    a_rows = ledger.read_for_tenant("tenant_a")
    b_rows = ledger.read_for_tenant("tenant_b")
    assert {r.email_id for r in a_rows} == {"a1", "a2"}
    assert {r.email_id for r in b_rows} == {"b1"}
    assert all(r.tenant_id == "tenant_a" for r in a_rows)
    assert all(r.tenant_id == "tenant_b" for r in b_rows)


def test_contract_metadata_is_present(tmp_path):
    # Governing-contract provenance travels with the module (§3 Component 1).
    assert "Phase1_Infrastructure_Agent_Design_Contract.md" in (
        CANONICAL_EVIDENCE_LEDGER_CONTRACT["contract_path"]
    )
    assert CANONICAL_EVIDENCE_LEDGER_CONTRACT["authorizing_commit"] == "fe355da"
    assert "P1-D2" in CANONICAL_EVIDENCE_LEDGER_CONTRACT["locked_decisions"]


# ---------------------------------------------------------------------------
# Class 2 — Adversarial / break-it
# ---------------------------------------------------------------------------


def test_no_modify_or_delete_api_exists(tmp_path):
    # P1-D2 append-only is structural: there is no mutate/delete surface at all.
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    for forbidden in ("update", "delete", "modify", "remove", "overwrite", "edit"):
        assert not hasattr(ledger, forbidden), f"append-only violated: {forbidden}"


def test_append_never_overwrites_a_prior_entry(tmp_path):
    # "Modifying" an entry can only ever produce a second appended line; the
    # original line is left byte-for-byte intact (immutable after write).
    path = tmp_path / "evidence.jsonl"
    ledger = CanonicalEvidenceLedger(path)
    first = ledger.append(_entry(email_id="e1", confidence=0.1))
    after_first = path.read_text(encoding="utf-8")

    second = ledger.append(_entry(email_id="e1", confidence=0.9))
    after_second = path.read_text(encoding="utf-8")

    assert after_second.startswith(after_first)  # original line untouched
    assert after_second.count("\n") == 2
    assert first.entry_id != second.entry_id


def test_write_without_tenant_id_is_rejected_and_logged(tmp_path):
    path = tmp_path / "evidence.jsonl"
    ledger = CanonicalEvidenceLedger(path)
    bad = {
        "agent_id": "header_analysis",
        "tenant_id": "",  # empty -> violates min_length=1
        "email_id": "email_x",
        "evidence_type": "header_signal",
        "confidence": 0.5,
    }
    with pytest.raises(LedgerSchemaError):
        ledger.append(bad)
    # Nothing landed on the ledger; the rejection was logged to the audit trail.
    assert not path.exists() or path.read_text(encoding="utf-8").strip() == ""
    audit = ledger.governance_audit_path.read_text(encoding="utf-8")
    assert "evidence_ledger_write_rejected" in audit


def test_unknown_evidence_type_is_rejected(tmp_path):
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    with pytest.raises(LedgerSchemaError):
        ledger.append(
            {
                "agent_id": "header_analysis",
                "tenant_id": "tenant_a",
                "email_id": "email_x",
                "evidence_type": "totally_made_up_signal",
                "confidence": 0.5,
            }
        )


def test_out_of_range_confidence_is_rejected(tmp_path):
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    with pytest.raises(LedgerSchemaError):
        ledger.append(
            {
                "agent_id": "header_analysis",
                "tenant_id": "tenant_a",
                "email_id": "email_x",
                "evidence_type": "header_signal",
                "confidence": 1.7,
            }
        )


def test_extra_field_is_rejected(tmp_path):
    # StrictModel(extra="forbid") rejects smuggled fields.
    with pytest.raises(ValidationError):
        EvidenceLedgerEntry(
            agent_id="header_analysis",
            tenant_id="tenant_a",
            email_id="email_x",
            evidence_type=EvidenceType.HEADER_SIGNAL,
            confidence=0.5,
            not_a_real_field="x",
        )


def test_cross_tenant_read_returns_empty_not_error(tmp_path):
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    ledger.append(_entry(tenant_id="tenant_a"))
    # A tenant with no entries gets [] back, never another tenant's data.
    assert ledger.read_for_tenant("tenant_c") == []
    assert ledger.count_for_tenant("tenant_c") == 0


def test_empty_tenant_id_read_raises(tmp_path):
    ledger = CanonicalEvidenceLedger(tmp_path / "evidence.jsonl")
    with pytest.raises(LedgerError):
        ledger.read_for_tenant("")


# ---------------------------------------------------------------------------
# Class 3 — Known-gap xfail (documented; completion path in the contract §5)
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    reason=(
        "Distributed consistency under concurrent writes is ES1 synthetic only; "
        "not tested until the real-data gate opens. Requires production "
        "infrastructure (file-locking / append serialization across processes). "
        "Completion path: Stage 2 infrastructure contract."
    ),
    strict=True,
)
def test_concurrent_multiprocess_write_consistency(tmp_path):
    # ES1 single-process append is correct; multi-process append ordering and
    # durability guarantees are out of scope until the Stage 2 contract. This
    # xfail intentionally fails to keep the gap visible (strict=True).
    raise AssertionError(
        "concurrent multi-process write consistency not implemented at ES1"
    )
