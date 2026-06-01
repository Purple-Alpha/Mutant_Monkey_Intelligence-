"""Vendor Payment Integrity break-it tests.

Adversarial coverage for the already-built Vendor Payment Integrity evidence
path (Financial State Ledger + Vendor Baseline Store + scoring overlay +
daily digest) under the operator-locked Alert-fatigue doctrine and the §11
SIGNED specs:

- 4. Product_Roadmap/Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md
- 4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md
- 4. Product_Roadmap/Tiered_Detection_Intensity_Deep_Dive.md
- 4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md
- CURRENT_STATE_MAP.md Alert-fatigue doctrine

These tests probe scope boundaries within the signed specs. They do not
introduce new detector behaviour, new product surfaces, or new D-decisions.
"""

from __future__ import annotations

import inspect
from dataclasses import asdict
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from core.blackboard import (
    EmailAnalysisImpersonationAnalysis,
    EmailAnalysisPayload,
    EmailAnalysisRiskAnalysis,
    EmailInboundPayload,
)
from core.drafting import daily_digest_agent
from core.production_state.vendor_baseline import (
    ingest_signal,
    tenant_database_path,
)
from core.scoring.email_risk_scoring_agent import _overlay_ransomware_precursor
from core.scoring.financial_state_ledger import (
    DeltaTripwireFinding,
    FinancialStateLedgerAssessment,
    assess_financial_state_delta,
)


TENANT = "tenant_break_it_demo"
NOW = datetime(2026, 5, 31, 22, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def isolated_blackboard_root(tmp_path, monkeypatch):
    root = tmp_path / "blackboard"
    root.mkdir()
    monkeypatch.chdir(root)


def _email(body: str) -> EmailInboundPayload:
    return EmailInboundPayload(
        received_at=NOW,
        sender="ap@vendor.example",
        recipient="ap@northstar-customer.example",
        subject="Invoice payment update",
        body_plain=body,
        headers={},
        attachments=[],
    )


def _analysis_payload(risk_score: int) -> EmailAnalysisPayload:
    return EmailAnalysisPayload(
        source_email_record_id=uuid4(),
        produced_at=NOW,
        summary="vendor payment integrity break-it baseline",
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


def test_multiple_new_payment_signals_recommend_review_never_block() -> None:
    """Pattern 1: a vendor-payment change recommends review, not block.

    Even with three different first-seen payment signals stacking inside a
    single email, the FSL spec D9 / D11 boundary must hold: floor stays at
    85 (not summed), recommended_action stays exactly ``needs_review``, and
    the assessment never produces any block/quarantine action verb. The
    detector's job is to surface for human review; auto-block remains an
    explicit operator-only / connector-only Stage B+ surface.
    """

    assessment = assess_financial_state_delta(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        email=_email(
            "ACH update for outstanding invoices. "
            "Routing number: 123456789. "
            "Account number: 00044556677. "
            "Please remit through our new billing portal "
            "https://pay.vendor-portal.example/remit."
        ),
        now=NOW,
    )

    finding_types = {finding.signal_type for finding in assessment.findings}
    assert finding_types == {
        "routing_number",
        "account_number",
        "payment_portal_url",
    }
    assert len(assessment.findings) == 3
    assert assessment.recommended_risk_floor == 85
    assert assessment.recommended_action == "needs_review"
    assert assessment.requires_out_of_band_verification is True

    forbidden_action_tokens = {
        "block",
        "blocked",
        "quarantine",
        "quarantined",
        "deny",
        "denied",
        "reject",
        "rejected",
        "auto_block",
        "auto_quarantine",
    }
    assessment_dump = str(asdict(assessment)).lower()
    for token in forbidden_action_tokens:
        assert (
            f"'recommended_action': '{token}'" not in assessment_dump
        ), (
            f"FSL spec D11 violated: recommended_action contained {token!r}; "
            "detector must never auto-block, only recommend review."
        )


def test_no_raw_financial_values_leak_across_full_signal_set() -> None:
    """Pattern 2: raw account/routing/IBAN/SWIFT/URL token values do not
    leak into returned findings or any caller-readable surface.

    FSL spec D13 + Vendor Baseline Store spec D2 require hash-only storage
    and redacted display. This adversarial probe stacks every supported
    signal type in one email with credentials/tokens, then walks the full
    assessment via ``asdict`` and asserts none of the raw forms appear.
    """

    raw_routing = "987654321"
    raw_account = "00099887766"
    raw_iban_spaced = "GB82 WEST 1234 5698 7654 32"
    raw_iban_packed = "GB82WEST12345698765432"
    raw_swift = "DEUT DE FF 500"
    raw_swift_packed = "DEUTDEFF500"
    raw_url = (
        "https://Billing.Vendor-Portal.example/pay?token=supersecret&sid=abc"
    )

    assessment = assess_financial_state_delta(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        email=_email(
            "Updated remittance details. "
            f"Routing number: {raw_routing}. "
            f"Account number: {raw_account}. "
            f"IBAN: {raw_iban_spaced}. "
            f"SWIFT: {raw_swift}. "
            f"Pay through {raw_url}."
        ),
        now=NOW,
    )

    dumped = str(asdict(assessment))

    forbidden_raw_substrings = (
        raw_routing,
        raw_account,
        raw_account.lstrip("0"),
        raw_iban_spaced,
        raw_iban_packed,
        raw_swift,
        raw_swift_packed,
        raw_url,
        "token=supersecret",
        "supersecret",
        "sid=abc",
    )
    for raw in forbidden_raw_substrings:
        assert raw not in dumped, (
            "FSL spec D13 / Vendor Baseline Store spec D2 violated: "
            f"raw financial substring {raw!r} leaked into assessment dump."
        )

    findings_by_type = {
        finding.signal_type: finding for finding in assessment.findings
    }
    assert "routing_number" in findings_by_type
    assert "account_number" in findings_by_type
    assert "iban" in findings_by_type
    assert "swift_bic_code" in findings_by_type
    assert "payment_portal_url" in findings_by_type

    routing = findings_by_type["routing_number"]
    account = findings_by_type["account_number"]
    iban = findings_by_type["iban"]
    swift = findings_by_type["swift_bic_code"]
    portal = findings_by_type["payment_portal_url"]
    assert routing.redacted_display == "***4321"
    assert account.redacted_display == "***7766"
    assert iban.redacted_display.startswith("GB82") and iban.redacted_display.endswith("5432")
    assert "..." in iban.redacted_display
    assert swift.redacted_display.endswith("...")
    assert portal.redacted_display == "billing.vendor-portal.example"


def test_payment_context_without_labelled_identifier_does_not_trigger() -> None:
    """Pattern 3: benign vendor-payment language does not trigger findings.

    Per FSL spec §3 extraction rules, every financial signal requires a
    labelled identifier near payment language; bare 10-digit reference
    numbers and benign ``pay / remit / invoice / billing`` prose must not
    produce findings or open a Vendor Baseline Store row. This protects the
    Alert-fatigue doctrine surface: routine vendor mail must stay quiet.
    """

    assessment = assess_financial_state_delta(
        tenant_id=TENANT,
        vendor_domain="vendor.example",
        email=_email(
            "Hi team, just confirming this month's invoice payment is being "
            "processed on schedule. We will remit on Friday as usual. "
            "Reference 1234567890 for your records; no banking changes on "
            "our side. Billing summary attached on the next invoice cycle."
        ),
        now=NOW,
    )

    assert assessment.extracted_signals == ()
    assert assessment.findings == ()
    assert assessment.recommended_risk_floor == 0
    assert assessment.recommended_action == "none"
    assert assessment.requires_out_of_band_verification is False
    assert not tenant_database_path(TENANT).exists(), (
        "Benign payment-context language must not open a Vendor Baseline "
        "Store row; doing so would leak signal into the per-tenant DB and "
        "produce noise without a labelled financial identifier."
    )


def test_multi_finding_overlay_max_merges_and_preserves_higher_existing_risk() -> None:
    """Pattern 4: multiple FSL signals max-merge upward without lowering an
    already-higher LLM risk_score.

    Tiered Detection Intensity D11 lift-only invariant and FSL spec D9
    require: the recommended risk floor (85) lifts the LLM score when LLM
    < 85, but never lowers an LLM score that is already higher. Stacking
    three findings inside one assessment does NOT change this — the floor
    is 85 per assessment, not 85 per finding.
    """

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
                recommended_verification="x",
            ),
            DeltaTripwireFinding(
                signal_type="account_number",
                baseline_state="new",
                redacted_display="***6677",
                source="body_plain",
                signal_hash="b" * 64,
                recommended_verification="x",
            ),
            DeltaTripwireFinding(
                signal_type="payment_portal_url",
                baseline_state="new",
                redacted_display="pay.vendor.example",
                source="body_plain",
                signal_hash="c" * 64,
                recommended_verification="x",
            ),
        ),
        recommended_risk_floor=85,
        recommended_action="needs_review",
        requires_out_of_band_verification=True,
    )

    cases = [
        (10, 85),
        (50, 85),
        (84, 85),
        (85, 85),
        (86, 86),
        (95, 95),
        (100, 100),
    ]
    for llm_risk, expected_final in cases:
        result = _overlay_ransomware_precursor(
            _analysis_payload(llm_risk),
            _email("Routine vendor body."),
            financial_state_ledger_assessment=assessment,
        )
        assert result.risk_analysis.risk_score == expected_final, (
            f"FSL multi-finding max-merge invariant violated: LLM risk "
            f"{llm_risk} produced final {result.risk_analysis.risk_score}, "
            f"expected {expected_final}. Floor must lift up, never down, "
            "and multiple findings must not stack additively."
        )


def test_daily_digest_agent_does_not_import_financial_state_ledger_directly() -> None:
    """Pattern 5: the daily digest agent does not emit per-email FSL alerts.

    Pins the CURRENT_STATE_MAP.md Alert-fatigue doctrine in code: Stage A
    is decision-support and evidence (batched into one digest per tenant
    per day), not a per-email FSL alert stream. The digest consumes the
    already-overlaid ``risk_score`` and ``behavioral_deviation_flags`` from
    the scoring agent; it does not call into ``financial_state_ledger``
    directly, and it does not import the FSL assessment dataclass.
    """

    source = inspect.getsource(daily_digest_agent)
    assert "from core.scoring.financial_state_ledger" not in source, (
        "Alert-fatigue doctrine violated: daily_digest_agent must not "
        "import financial_state_ledger directly. FSL evidence reaches the "
        "digest via the already-overlaid risk_score on EmailAnalysisPayload."
    )
    assert "FinancialStateLedgerAssessment" not in source
    assert "assess_financial_state_delta" not in source
    assert "DeltaTripwireFinding" not in source

    digest_module_namespace = vars(daily_digest_agent)
    assert "FinancialStateLedgerAssessment" not in digest_module_namespace
    assert "assess_financial_state_delta" not in digest_module_namespace


def test_per_tenant_salt_yields_different_hashes_and_no_raw_value_on_disk() -> None:
    """Pattern 6: tenant isolation and hash-only storage hold under an
    adversarial-looking shared raw value.

    Vendor Baseline Store spec D2 + D5 + D6 require: per-tenant salted
    SHA-256 hashing, physical per-tenant SQLite files, and no raw value on
    disk. Ingesting the same raw routing number for two tenants must
    produce two different ``signal_hash`` values (proves the per-tenant
    salt actually changes the hash) and neither tenant's on-disk database
    bytes may contain the raw routing number.
    """

    raw_routing = "555444333"

    record_a = ingest_signal(
        tenant_id="tenant_break_it_a",
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value=raw_routing,
        now=NOW,
    )
    record_b = ingest_signal(
        tenant_id="tenant_break_it_b",
        vendor_domain="vendor.example",
        signal_type="routing_number",
        raw_value=raw_routing,
        now=NOW,
    )

    assert record_a.signal_hash != record_b.signal_hash, (
        "Vendor Baseline Store spec D5 violated: identical raw routing "
        "numbers ingested for two tenants produced identical hashes. "
        "Per-tenant HKDF-derived salt is not changing the hash output."
    )
    assert len(record_a.signal_hash) == 64
    assert len(record_b.signal_hash) == 64

    path_a = tenant_database_path("tenant_break_it_a")
    path_b = tenant_database_path("tenant_break_it_b")
    assert path_a != path_b
    assert path_a.exists()
    assert path_b.exists()

    bytes_a = path_a.read_bytes()
    bytes_b = path_b.read_bytes()
    raw_bytes = raw_routing.encode("ascii")
    assert raw_bytes not in bytes_a, (
        "Vendor Baseline Store spec D2 violated: raw routing number "
        f"{raw_routing!r} found inside tenant_a's on-disk SQLite bytes."
    )
    assert raw_bytes not in bytes_b, (
        "Vendor Baseline Store spec D2 violated: raw routing number "
        f"{raw_routing!r} found inside tenant_b's on-disk SQLite bytes."
    )
