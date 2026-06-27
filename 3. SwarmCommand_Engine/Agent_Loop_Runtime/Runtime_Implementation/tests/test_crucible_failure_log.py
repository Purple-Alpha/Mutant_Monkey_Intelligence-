"""Crucible failure log tests — Blackboard-Mesh §6 test 8."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.blackboard import EvidenceBacker, EvidenceBackerVerdict
from core.crucible import (
    SCENARIO_OMISSION_AS_SAFETY,
    SCENARIO_ORPHAN_VERDICT_REF,
    CrucibleFailureLog,
    CrucibleHarness,
)


def test_crucible_run_appends_failure_log_with_backer_sha(tmp_path):
    workspace = tmp_path / "workspace"
    log_jsonl = tmp_path / "CRUCIBLE_FAILURE_LOG.jsonl"
    failure_log = CrucibleFailureLog(log_jsonl)

    harness = CrucibleHarness(workspace)
    entry = harness.run_scenario(
        SCENARIO_ORPHAN_VERDICT_REF,
        tenant_id="tenant_a",
        email_id="email_fault",
        failure_log=failure_log,
    )

    rows = failure_log.read_all()
    assert len(rows) == 1
    assert rows[0].crucible_run_id == entry.crucible_run_id
    assert rows[0].evidence_backer_report_sha == entry.evidence_backer_report_sha
    assert len(rows[0].evidence_backer_report_sha) == 64
    assert rows[0].failure_class.value == "orphan_verdict_ref"
    assert log_jsonl.with_suffix(".md").exists()


def test_orphan_scenario_produces_violation_backer_verdict(tmp_path):
    workspace = tmp_path / "workspace"
    harness = CrucibleHarness(workspace)
    harness.seed_scenario(
        SCENARIO_ORPHAN_VERDICT_REF,
        tenant_id="tenant_a",
        email_id="email_fault",
    )
    from core.blackboard import CanonicalEvidenceLedger, VerdictLedger

    report = EvidenceBacker(
        blackboard_paths=[],
        evidence_ledger=CanonicalEvidenceLedger(workspace / "evidence.jsonl"),
        verdict_ledger=VerdictLedger(workspace / "verdicts.jsonl"),
    ).verify(tenant_id="tenant_a", email_id="email_fault")
    assert report.verdict is EvidenceBackerVerdict.VIOLATION


def test_omission_scenario_produces_incomplete_backer_verdict(tmp_path):
    workspace = tmp_path / "workspace"
    harness = CrucibleHarness(workspace)
    harness.seed_scenario(
        SCENARIO_OMISSION_AS_SAFETY,
        tenant_id="tenant_a",
        email_id="email_sparse",
    )
    from core.blackboard import CanonicalEvidenceLedger, VerdictLedger

    report = EvidenceBacker(
        blackboard_paths=[],
        evidence_ledger=CanonicalEvidenceLedger(workspace / "evidence.jsonl"),
        verdict_ledger=VerdictLedger(workspace / "verdicts.jsonl"),
    ).verify(tenant_id="tenant_a", email_id="email_sparse")
    assert report.verdict is EvidenceBackerVerdict.INCOMPLETE


def test_failure_log_is_append_only(tmp_path):
    log_jsonl = tmp_path / "CRUCIBLE_FAILURE_LOG.jsonl"
    failure_log = CrucibleFailureLog(log_jsonl)
    harness = CrucibleHarness(tmp_path / "ws1")
    harness.run_scenario(
        SCENARIO_ORPHAN_VERDICT_REF,
        tenant_id="tenant_a",
        email_id="email_one",
        failure_log=failure_log,
    )
    harness2 = CrucibleHarness(tmp_path / "ws2")
    harness2.run_scenario(
        SCENARIO_OMISSION_AS_SAFETY,
        tenant_id="tenant_a",
        email_id="email_two",
        failure_log=failure_log,
    )
    assert len(failure_log.read_all()) == 2
