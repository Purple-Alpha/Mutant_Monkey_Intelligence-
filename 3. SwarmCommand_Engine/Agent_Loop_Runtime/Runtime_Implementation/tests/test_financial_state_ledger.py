from __future__ import annotations

import inspect
import importlib.util
import sys
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from core.blackboard import (
    EmailAnalysisImpersonationAnalysis,
    EmailAnalysisPayload,
    EmailAnalysisRiskAnalysis,
    EmailAttachmentMeta,
    EmailInboundPayload,
    GovernanceError,
)
from core.operator_state import KillSwitchEngaged, engage_kill_switch
from core.production_state.vendor_baseline import (
    ingest_signal,
    tenant_database_path,
)
from core.scoring import financial_state_ledger as fsl
from core.scoring.email_risk_scoring_agent import _overlay_ransomware_precursor
from core.scoring.financial_state_ledger import (
    DeltaTripwireFinding,
    ExtractedFinancialSignal,
    FinancialStateLedgerAssessment,
    assess_financial_state_delta,
)


TENANT = "tenant_demo"
NOW = datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def isolated_blackboard_root(tmp_path, monkeypatch):
    root = tmp_path / "blackboard"
    root.mkdir()
    monkeypatch.chdir(root)


def _email(
    body: str,
    *,
    attachments: list[EmailAttachmentMeta] | None = None,
) -> EmailInboundPayload:
    return EmailInboundPayload(
        received_at=NOW,
        sender="ap@vendor.example",
        recipient="ap@northstar-customer.example",
        subject="Invoice payment update",
        body_plain=body,
        headers={},
        attachments=attachments or [],
    )


def _assess(body: str, *, tenant_id: str = TENANT) -> FinancialStateLedgerAssessment:
    return assess_financial_state_delta(
        tenant_id=tenant_id,
        vendor_domain="vendor.example",
        email=_email(body),
        now=NOW,
    )


def _analysis_payload(risk_score: int) -> EmailAnalysisPayload:
    return EmailAnalysisPayload(
        source_email_record_id=uuid4(),
        produced_at=NOW,
        summary="financial state ledger integration test",
        action_items=[],
        risk_analysis=EmailAnalysisRiskAnalysis(
            risk_score=risk_score,
            risk_factors=[],
            phishing_signals=[],
            urgency_signals=[],
            financial_risk="low",
            vendor_fraud_score=0,
            wire_transfer_anomaly_score=0,
            invoice_authenticity_score=None,
            behavioral_deviation_flags=[],
        ),
        impersonation_analysis=EmailAnalysisImpersonationAnalysis(
            impersonation_likelihood=0,
            suspicious_elements=[],
            sender_legitimacy_notes=None,
        ),
        recommended_action="safe",
    )


def test_public_api_surface_is_locked() -> None:
    assert set(fsl.__all__) == {
        "DeltaTripwireFinding",
        "ExtractedFinancialSignal",
        "FinancialSignalType",
        "FinancialStateLedgerAssessment",
        "SignalSource",
        "assess_financial_state_delta",
    }
    assert inspect.isfunction(assess_financial_state_delta)
    assert ExtractedFinancialSignal.__dataclass_params__.frozen
    assert DeltaTripwireFinding.__dataclass_params__.frozen
    assert FinancialStateLedgerAssessment.__dataclass_params__.frozen


def test_no_signal_path_writes_no_baseline_rows() -> None:
    assessment = _assess("Routine invoice attached. Standard terms apply.")

    assert assessment.findings == ()
    assert assessment.extracted_signals == ()
    assert assessment.recommended_risk_floor == 0
    assert assessment.recommended_action == "none"
    assert not assessment.requires_out_of_band_verification
    assert not tenant_database_path(TENANT).exists()


def test_first_seen_routing_number_creates_new_finding_after_check() -> None:
    assessment = _assess("Please remit by ACH. Routing number: 123-456-789.")

    assert len(assessment.findings) == 1
    finding = assessment.findings[0]
    assert finding.signal_type == "routing_number"
    assert finding.baseline_state == "new"
    assert finding.redacted_display == "***6789"
    assert finding.signal_hash
    assert assessment.recommended_risk_floor == 85
    assert assessment.recommended_action == "needs_review"
    assert assessment.requires_out_of_band_verification
    assert tenant_database_path(TENANT).exists()


def test_known_signal_path_emits_no_finding_and_refreshes_baseline() -> None:
    first = _assess("Please use routing number: 123456789.")
    second = assess_financial_state_delta(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        email=_email("Reminder: routing number: 123 456 789."),
        now=NOW + timedelta(days=1),
    )

    assert len(first.findings) == 1
    assert second.findings == ()
    assert second.recommended_risk_floor == 0
    assert second.recommended_action == "none"


def test_expired_signal_path_returns_expired_finding_and_refreshes_row() -> None:
    ingest_signal(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value="123456789",
        now=NOW - timedelta(days=91),
    )

    assessment = _assess("Please use routing number: 123456789.")

    assert len(assessment.findings) == 1
    assert assessment.findings[0].baseline_state == "expired"
    assert assessment.recommended_risk_floor == 85

    refreshed = assess_financial_state_delta(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        email=_email("Routing number: 123456789."),
        now=NOW + timedelta(days=1),
    )
    assert refreshed.findings == ()


def test_check_before_ingest_ordering_is_enforced(monkeypatch) -> None:
    calls: list[str] = []

    def fake_check_signal(**kwargs):
        calls.append(f"check:{kwargs['signal_type']}")
        return SimpleNamespace(state="new", record=None)

    def fake_ingest_signal(**kwargs):
        calls.append(f"ingest:{kwargs['signal_type']}")
        return SimpleNamespace(signal_hash="a" * 64)

    monkeypatch.setattr(fsl.vendor_baseline, "check_signal", fake_check_signal)
    monkeypatch.setattr(fsl.vendor_baseline, "ingest_signal", fake_ingest_signal)

    assessment = _assess("Routing number: 123456789.")

    assert assessment.findings[0].signal_hash == "a" * 64
    assert calls == ["check:routing_number", "ingest:routing_number"]


def test_attachment_text_path_records_filename_and_index() -> None:
    attachment = EmailAttachmentMeta(
        filename="invoice.pdf",
        content_type="application/pdf",
        extracted_text="Remit to account number: 000-001234567.",
    )
    assessment = assess_financial_state_delta(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        email=_email("Please process attached invoice.", attachments=[attachment]),
        now=NOW,
    )

    finding = assessment.findings[0]
    assert finding.signal_type == "account_number"
    assert finding.source == "attachment_extracted_text"
    assert finding.attachment_filename == "invoice.pdf"
    assert finding.attachment_index == 0


def test_body_and_attachment_dedupe_keeps_sources_but_one_finding() -> None:
    attachment = EmailAttachmentMeta(
        filename="invoice.pdf",
        extracted_text="Routing number: 123456789.",
    )
    assessment = assess_financial_state_delta(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        email=_email("Routing number: 123-456-789.", attachments=[attachment]),
        now=NOW,
    )

    assert [signal.source for signal in assessment.extracted_signals] == [
        "body_plain",
        "attachment_extracted_text",
    ]
    assert len(assessment.findings) == 1
    assert assessment.recommended_risk_floor == 85


def test_payment_portal_host_extraction_uses_host_only_redaction() -> None:
    assessment = _assess(
        "Please remit through our payment portal: "
        "https://Pay.Vendor-Portal.example/invoice/123?token=secret."
    )

    finding = assessment.findings[0]
    assert finding.signal_type == "payment_portal_url"
    assert finding.redacted_display == "pay.vendor-portal.example"
    assert "token=secret" not in str(assessment)


def test_unlabelled_numbers_are_suppressed() -> None:
    assessment = _assess(
        "Invoice 123456789 is attached. Reference 987654321 is due Friday."
    )

    assert assessment.extracted_signals == ()
    assert assessment.findings == ()
    assert not tenant_database_path(TENANT).exists()


def test_malformed_candidates_are_suppressed_without_crashing() -> None:
    assessment = _assess(
        "Routing number: 12345. SWIFT: BAD. IBAN: X. Account number: ---."
    )

    assert assessment.extracted_signals == ()
    assert assessment.findings == ()


def test_multiple_signal_types_return_one_finding_per_new_signal_type() -> None:
    assessment = _assess(
        "ACH update. Routing number: 123456789. "
        "Account number: 00044556677. "
        "Pay through billing portal https://pay.vendor.example/remit."
    )

    assert {finding.signal_type for finding in assessment.findings} == {
        "routing_number",
        "account_number",
        "payment_portal_url",
    }
    assert len(assessment.findings) == 3
    assert assessment.recommended_risk_floor == 85


def test_no_raw_value_leakage_in_repr_or_dict() -> None:
    raw_account = "00044556677"
    raw_iban = "GB82 WEST 1234 5698 7654 32"
    assessment = _assess(
        f"Account number: {raw_account}. IBAN: {raw_iban}."
    )

    dumped = str(asdict(assessment))
    assert raw_account not in dumped
    assert "44556677" not in dumped
    assert "GB82WEST12345698765432" not in dumped
    assert raw_iban not in dumped


def test_verification_wording_is_pinned() -> None:
    assessment = _assess("Routing number: 123456789.")

    wording = assessment.findings[0].recommended_verification
    assert "Verify through a previously-known vendor channel before payment" in wording
    assert "Do not use phone numbers, links, or payment instructions from this email" in wording


@pytest.mark.parametrize(
    "vendor_domain",
    ["Vendor.Example", " vendor.example", "vendor.example ", "vendor/example", "", ".vendor", "vendor.", "vendor..example"],
)
def test_vendor_domain_validation_rejects_unsafe_values(vendor_domain: str) -> None:
    with pytest.raises(GovernanceError):
        assess_financial_state_delta(
            tenant_id=TENANT,
            vendor_domain=vendor_domain,
            email=_email("Routing number: 123456789."),
            now=NOW,
        )


def test_kill_switch_is_inherited_from_vendor_baseline_store(tmp_path) -> None:
    engage_kill_switch(
        Path("."),
        scope="PRODUCTION_ONLY",
        reason="halt financial baseline",
        operator="matt",
    )

    with pytest.raises(KillSwitchEngaged):
        _assess("Routing number: 123456789.")

    assert not tenant_database_path(TENANT).exists()


def test_tenant_isolation_keeps_same_signal_new_for_second_tenant() -> None:
    tenant_a_first = _assess("Routing number: 123456789.", tenant_id="tenant_a")
    tenant_b_first = _assess("Routing number: 123456789.", tenant_id="tenant_b")
    tenant_a_second = assess_financial_state_delta(
        tenant_id="tenant_a",
        vendor_domain="vendor.example",
        email=_email("Routing number: 123456789."),
        now=NOW + timedelta(days=1),
    )

    assert tenant_a_first.findings[0].baseline_state == "new"
    assert tenant_b_first.findings[0].baseline_state == "new"
    assert tenant_a_second.findings == ()


def test_detector_does_not_write_blackboard_directly() -> None:
    source = inspect.getsource(fsl)
    assert "submit_" not in source
    assert "RouteContext" not in source
    assert "core.orchestrator" not in source


def test_detector_opens_no_new_persistent_state_surface() -> None:
    source = inspect.getsource(fsl)
    assert "sqlite3" not in source
    assert "open(" not in source
    assert "write_text" not in source
    assert "json.dump" not in source


def test_scoring_overlay_can_max_merge_financial_state_floor() -> None:
    assessment = FinancialStateLedgerAssessment(
        vendor_domain="vendor.example",
        extracted_signals=(),
        findings=(
            DeltaTripwireFinding(
                signal_type="routing_number",
                baseline_state="new",
                redacted_display="***6789",
                source="body_plain",
                signal_hash="a" * 64,
                recommended_verification="Verify through a previously-known vendor channel before payment.",
            ),
        ),
        recommended_risk_floor=85,
        recommended_action="needs_review",
        requires_out_of_band_verification=True,
    )
    lifted = _overlay_ransomware_precursor(
        _analysis_payload(10),
        _email("Routine body."),
        financial_state_ledger_assessment=assessment,
    )
    preserved = _overlay_ransomware_precursor(
        _analysis_payload(95),
        _email("Routine body."),
        financial_state_ledger_assessment=assessment,
    )

    assert lifted.risk_analysis.risk_score == 85
    assert preserved.risk_analysis.risk_score == 95


def test_digest_fields_are_client_readable_without_raw_financial_details() -> None:
    assessment = _assess("Please pay using account number: 00044556677.")
    finding = assessment.findings[0]

    line = (
        f"Financial Delta Tripwire: {finding.baseline_state} "
        f"{finding.signal_type} {finding.redacted_display} from "
        f"{assessment.vendor_domain}. {finding.recommended_verification}"
    )
    assert "vendor.example" in line
    assert "account_number" in line
    assert "***6677" in line
    assert "00044556677" not in line


def test_grok_audit_runner_has_financial_state_ledger_target() -> None:
    workspace_root = Path(__file__).resolve().parents[4]
    runner_path = workspace_root / "audit_tools" / "grok_audit_runner.py"
    spec = importlib.util.spec_from_file_location("grok_audit_runner", runner_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    package = module.AUDIT_PACKAGES["financial_state_ledger"]
    assert package.name == "financial_state_ledger"
    included_paths = {entry.relative_path for entry in package.files}
    assert (
        "4. Product_Roadmap/Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md"
        in included_paths
    )
    assert (
        "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
        "core/scoring/financial_state_ledger.py"
        in included_paths
    )
    assert (
        "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
        "tests/test_financial_state_ledger.py"
        in included_paths
    )
