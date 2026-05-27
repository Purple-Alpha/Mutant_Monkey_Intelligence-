from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Callable
from uuid import UUID

import pytest

from core.blackboard import (
    EmailAnalysisPayload,
    EmailInboundPayload,
    Environment,
    RecordType,
    read_records,
)
from core.orchestrator import RouteContext, submit_email_inbound
from core.orchestrator.routes import blackboard_path
from core.production import (
    ProductionLoopConfig,
    ProductionSignal,
    run_production_cycle,
)
from core.scoring import EmailRiskScoringConfig, run_email_risk_scoring_cycle
from core.scoring.email_risk_scoring_agent import (
    EMAIL_ANALYSIS_COMPLETE_WORKFLOW_ID,
    NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT,
)

TENANT = "tenant_demo"


def _context(tmp_path) -> RouteContext:
    return RouteContext(blackboard_root=tmp_path / "blackboard")


def _seed_inbound(
    context: RouteContext,
    *,
    subject: str = "Outstanding invoice",
    sender: str = "vendor@example.com",
    tenant_id: str = TENANT,
) -> UUID:
    payload = EmailInboundPayload(
        received_at=datetime(2026, 5, 20, 10, 0, tzinfo=timezone.utc),
        sender=sender,
        recipient="cfo@northstar.example",
        subject=subject,
        body_plain="Please pay the attached invoice today.",
        headers={"X-Spam-Score": "0.1"},
    )
    result = submit_email_inbound(
        context,
        tenant_id=tenant_id,
        environment=Environment.PRODUCTION,
        source_agent="orchestrator_001",
        payload=payload,
    )
    return result.record.record_id


def _valid_analysis_json(**overrides) -> str:
    payload = {
        "summary": "Vendor requested an immediate wire transfer.",
        "action_items": [
            {"task": "Confirm invoice with finance", "owner": "ops", "due_date": "2026-06-01"}
        ],
        "risk_analysis": {
            "risk_score": 72,
            "risk_factors": ["spoofed_sender_domain"],
            "phishing_signals": ["link_to_unknown_domain"],
            "urgency_signals": ["please_reply_today"],
            "financial_risk": "high",
            "vendor_fraud_score": 60,
            "wire_transfer_anomaly_score": 55,
            "invoice_authenticity_score": None,
            "behavioral_deviation_flags": [
                "first_time_sender_with_financial_ask",
                "urgency_paired_with_finance",
            ],
        },
        "impersonation_analysis": {
            "impersonation_likelihood": 30,
            "suspicious_elements": ["display_name_does_not_match_sender"],
            "sender_legitimacy_notes": "first contact from this domain",
        },
        "recommended_action": "needs_review",
    }
    payload.update(overrides)
    return json.dumps(payload)


def _canned_client(response: str) -> Callable[[str, str], str]:
    def _client(system_prompt: str, user_prompt: str) -> str:
        assert "NorthStar Inbox Shield" in system_prompt
        json.loads(user_prompt)  # the agent must send valid JSON in the user prompt
        return response

    return _client


def _production_records(context: RouteContext, tenant: str = TENANT):
    return read_records(blackboard_path(context.blackboard_root, Environment.PRODUCTION, tenant))


def test_scoring_agent_happy_path_writes_analysis_and_marker(tmp_path):
    context = _context(tmp_path)
    inbound_id = _seed_inbound(context)

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json()),
            production_tenant_id=TENANT,
        ),
    )

    assert result.analyzed == 1
    assert result.failed == 0
    assert result.skipped == 0
    assert result.successes[0].source_email_record_id == inbound_id

    records = _production_records(context)
    analyses = [r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS]
    assert len(analyses) == 1
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)
    assert parsed.source_email_record_id == inbound_id
    assert parsed.recommended_action == "needs_review"
    assert parsed.risk_analysis.risk_score == 72

    markers = [
        r
        for r in records
        if r.record_type == RecordType.AUDIT_VERDICT
        and r.workflow_id == EMAIL_ANALYSIS_COMPLETE_WORKFLOW_ID
    ]
    assert len(markers) == 1
    assert markers[0].parent_record_id == inbound_id


def test_scoring_agent_handles_invalid_json_with_failure_record(tmp_path):
    context = _context(tmp_path)
    inbound_id = _seed_inbound(context)

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client("this is not JSON {"),
            production_tenant_id=TENANT,
        ),
    )

    assert result.analyzed == 0
    assert result.failed == 1
    assert result.failures[0].failure_reason == "invalid_json"

    records = _production_records(context)
    failures = [r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS_FAILURE]
    assert len(failures) == 1
    assert failures[0].payload["raw_output"].startswith("this is not JSON")
    assert failures[0].payload["failure_reason"] == "invalid_json"
    assert failures[0].payload["source_email_record_id"] == str(inbound_id)

    markers = [
        r
        for r in records
        if r.record_type == RecordType.AUDIT_VERDICT
        and r.workflow_id == EMAIL_ANALYSIS_COMPLETE_WORKFLOW_ID
    ]
    assert len(markers) == 1
    assert markers[0].payload["requires_human_review"] is True


def test_scoring_agent_handles_out_of_range_risk_score(tmp_path):
    context = _context(tmp_path)
    _seed_inbound(context)

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(risk_analysis={
                "risk_score": 150,
                "risk_factors": [],
                "phishing_signals": [],
                "urgency_signals": [],
                "financial_risk": "low",
                "vendor_fraud_score": 0,
                "wire_transfer_anomaly_score": 0,
                "invoice_authenticity_score": None,
                "behavioral_deviation_flags": [],
            })),
            production_tenant_id=TENANT,
        ),
    )

    assert result.failed == 1
    assert result.failures[0].failure_reason in {"out_of_range", "schema_mismatch"}


def test_scoring_agent_handles_invalid_enum(tmp_path):
    context = _context(tmp_path)
    _seed_inbound(context)

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json(recommended_action="quarantine")),
            production_tenant_id=TENANT,
        ),
    )

    assert result.failed == 1
    assert result.failures[0].failure_reason in {"invalid_enum", "schema_mismatch"}


def test_scoring_agent_is_idempotent_per_source_email(tmp_path):
    context = _context(tmp_path)
    _seed_inbound(context)
    config = EmailRiskScoringConfig(
        llm_client=_canned_client(_valid_analysis_json()),
        production_tenant_id=TENANT,
    )

    first = run_email_risk_scoring_cycle(context, config=config)
    second = run_email_risk_scoring_cycle(context, config=config)

    assert first.analyzed == 1
    assert second.analyzed == 0
    assert second.skipped == 1

    analyses = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_ANALYSIS
    ]
    assert len(analyses) == 1


def test_scoring_agent_processes_multiple_inbound_in_one_cycle(tmp_path):
    context = _context(tmp_path)
    _seed_inbound(context, subject="Email A")
    _seed_inbound(context, subject="Email B")

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json()),
            production_tenant_id=TENANT,
        ),
    )

    assert result.analyzed == 2
    analyses = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_ANALYSIS
    ]
    assert len(analyses) == 2


def test_production_loop_does_not_run_scoring_by_default(tmp_path):
    context = _context(tmp_path)
    _seed_inbound(context)

    result = run_production_cycle(
        context,
        tenant_id=TENANT,
        signal=ProductionSignal(source="mailbox", event_kind="email_received"),
    )

    assert result.email_risk_scoring is None

    records = _production_records(context)
    assert all(r.record_type != RecordType.EMAIL_ANALYSIS for r in records)
    assert all(
        not (
            r.record_type == RecordType.AUDIT_VERDICT
            and r.workflow_id == EMAIL_ANALYSIS_COMPLETE_WORKFLOW_ID
        )
        for r in records
    )


def test_production_loop_runs_scoring_when_opted_in(tmp_path):
    context = _context(tmp_path)
    _seed_inbound(context)

    result = run_production_cycle(
        context,
        tenant_id=TENANT,
        signal=ProductionSignal(source="mailbox", event_kind="email_received"),
        config=ProductionLoopConfig(
            run_email_risk_scoring_at_end_of_cycle=True,
            email_risk_scoring_config=EmailRiskScoringConfig(
                llm_client=_canned_client(_valid_analysis_json()),
                production_tenant_id=TENANT,
            ),
        ),
    )

    assert result.email_risk_scoring is not None
    assert result.email_risk_scoring.analyzed == 1


def test_production_loop_flag_without_config_raises(tmp_path):
    context = _context(tmp_path)
    _seed_inbound(context)

    with pytest.raises(ValueError, match="email_risk_scoring_config"):
        run_production_cycle(
            context,
            tenant_id=TENANT,
            signal=ProductionSignal(source="mailbox", event_kind="email_received"),
            config=ProductionLoopConfig(
                run_email_risk_scoring_at_end_of_cycle=True,
                email_risk_scoring_config=None,
            ),
        )


def test_production_loop_forces_tenant_id_on_custom_scoring_config(tmp_path):
    context = _context(tmp_path)
    _seed_inbound(context)

    custom = EmailRiskScoringConfig(
        llm_client=_canned_client(_valid_analysis_json()),
        production_tenant_id="wrong_tenant_overridden",
    )

    result = run_production_cycle(
        context,
        tenant_id=TENANT,
        signal=ProductionSignal(source="mailbox", event_kind="email_received"),
        config=ProductionLoopConfig(
            run_email_risk_scoring_at_end_of_cycle=True,
            email_risk_scoring_config=custom,
        ),
    )

    assert result.email_risk_scoring is not None
    assert result.email_risk_scoring.analyzed == 1

    wrong_tenant_records = read_records(
        blackboard_path(
            context.blackboard_root, Environment.PRODUCTION, "wrong_tenant_overridden"
        )
    )
    assert wrong_tenant_records == []
    assert any(
        r.record_type == RecordType.EMAIL_ANALYSIS for r in _production_records(context)
    )


# ---------------------------------------------------------------------------
# Month 2 — Phase 1.1 Vendor / Invoice Fraud Detection.
# Tests below pin the locked NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT against
# the deep dive's specialization pillars, prove the four new scoring
# dimensions round-trip end-to-end through the agent, and exercise the
# worked examples from §3 of the deep dive against deterministic fakes.
# ---------------------------------------------------------------------------


def test_scoring_prompt_is_locked_to_fraud_specialization_pillars():
    prompt = NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT

    assert "PROMPT NOT YET LOCKED" not in prompt
    assert "TODO" not in prompt
    assert "human-layer fraud defense" in prompt
    assert "ransomware precursor defense" in prompt
    assert "Fraud starts in the inbox." in prompt
    assert "stop the attack before it becomes an incident." in prompt
    # The four new scoring dimensions must be named in the prompt so the LLM
    # cannot accidentally drop them from its output.
    assert "vendor_fraud_score" in prompt
    assert "wire_transfer_anomaly_score" in prompt
    assert "invoice_authenticity_score" in prompt
    assert "behavioral_deviation_flags" in prompt
    # All BehavioralDeviationFlag values must be present in the
    # controlled-enum block so the LLM never invents a freeform flag.
    for flag in (
        "new_banking_instructions",
        "out_of_band_pressure",
        "unusual_dollar_amount",
        "lookalike_sender_domain",
        "reply_to_diverges_from_from",
        "mismatched_invoice_vendor_name",
        "first_time_sender_with_financial_ask",
        "urgency_paired_with_finance",
        "unusual_unicode_obfuscation",
    ):
        assert flag in prompt


def test_scoring_prompt_embeds_four_worked_examples_with_distinct_labels():
    prompt = NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT
    assert "Example 1 \u2014 High-confidence vendor invoice fraud" in prompt
    assert "Example 2 \u2014 Executive impersonation wire pressure" in prompt
    assert "Example 3 \u2014 Legitimate vendor invoice" in prompt
    assert "Example 4 \u2014 Ambiguous needs_review" in prompt


def test_scoring_prompt_embeds_recovery_pass_examples_5_and_6():
    """Recovery pass adds two surgical worked examples (Examples 5 and 6).

    Example 5 teaches thread-hijack scoring (fake In-Reply-To headers +
    "Re:" subject with no quoted history + "as discussed" phrasing) so the
    FPR-protection "matching-domain stays safe" clause cannot over-route
    these to ``safe``. Example 6 teaches future-dated / past-due invoice
    scoring so the date-anomaly authenticity case lands in the right band.
    Both examples come from the 2026-05-21 live-eval recovery diagnostic.
    """
    prompt = NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT
    assert "Example 5 \u2014 Thread-hijack vendor invoice" in prompt
    assert "fake thread context" in prompt
    assert "In-Reply-To and References pointing at" in prompt
    assert "thread-hijack fraud pattern" in prompt
    assert "Example 6 \u2014 Future-dated invoice" in prompt
    assert "Invoice date 2026-07-30. Payment due 2026-06-15" in prompt
    assert "date-anomaly authenticity case" in prompt


def test_scoring_prompt_embeds_final_recovery_example_7_unicode_hyphen_sender():
    """Final recovery pass adds Example 7 (Unicode-hyphen lookalike sender domain).

    Anchored to the 2026-05-21 final-recovery diagnostic on ``ls-001`` where
    grok-4 failed to emit ``lookalike_sender_domain`` because the previous
    rubric only mentioned punycode / homoglyph and did not call out Unicode
    hyphen variants (U+2010, U+2011, U+2212) in the sender domain. The
    example also clarifies that a non-ASCII recipient domain does not
    legitimise a non-ASCII sender domain.
    """
    prompt = NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT
    assert "Example 7 \u2014 Unicode-hyphen lookalike sender domain" in prompt
    assert "U+2011" in prompt
    assert "non-breaking hyphen" in prompt
    assert "lookalike sender attack" in prompt
    assert "evaluated independently" in prompt


# ---------------------------------------------------------------------------
# Month 2 recall patch — targeted subcategory rubric refinements.
# These tests pin the recall patch text against the three weak areas Matt
# called out after the first calibrated Grok run: banking-instruction floor,
# sender-domain obfuscation emission, and invoice/PDF-only-banking lean.
# They also pin the false-positive protection guardrails that exist
# specifically to preserve the 0% legit-FPR result.
# ---------------------------------------------------------------------------


def test_scoring_prompt_includes_month_2_recall_patch_header():
    prompt = NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT
    assert "Month 2 recall patch" in prompt


def test_recall_patch_pins_banking_instruction_floor_clause():
    prompt = NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT
    assert "Banking-instruction strength" in prompt
    assert "new ACH details" in prompt
    assert "updated remit-to address" in prompt
    assert "appear only inside an attached PDF" in prompt
    assert "vendor_fraud_score must reach at least 60" in prompt
    assert "vendor_fraud_score must still reach at least 45" in prompt
    assert 'Emit "new_banking_instructions"' in prompt


def test_recall_patch_pins_sender_domain_obfuscation_clause():
    prompt = NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT
    assert "Sender-domain obfuscation" in prompt
    assert "punycode prefixes such as \"xn--\"" in prompt
    assert "homoglyph substitutions" in prompt
    assert "near-variant of a vendor or brand name" in prompt
    assert "additionally emit \"unusual_unicode_obfuscation\"" in prompt
    assert "Do not emit \"lookalike_sender_domain\" purely because the sender is unknown" in prompt


def test_recall_patch_pins_invoice_authenticity_clause():
    prompt = NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT
    assert "Invoice authenticity & PDF-only banking changes" in prompt
    assert "invoice_authenticity_score must fall in the 0-40 band" in prompt
    assert "vendor different from the sender's domain" in prompt
    assert "banking destination details" in prompt
    assert "future-dated invoice" in prompt
    assert "Emit \"mismatched_invoice_vendor_name\"" in prompt


def test_recall_patch_pins_false_positive_protection_guardrails():
    prompt = NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT
    assert "False-positive protection" in prompt
    assert "preserve the 0% legit-FPR target" in prompt
    assert "must remain \"safe\"" in prompt
    assert "banking details unchanged from last invoice" in prompt
    assert "first-time or unknown sender alone is not enough" in prompt
    assert "no payment ask, no banking detail, and no invoice attachment" in prompt
    assert "polite reminder" in prompt
    assert "newsletter must keep recommended_action at \"safe\"" in prompt


def test_phase_1_5_vendor_invoice_recall_floor_is_pinned():
    prompt = NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT
    assert "Phase 1.5 vendor-invoice recall floor" in prompt
    assert "first invoice after onboarding" in prompt
    assert "use the remittance instructions on the attached PDF" in prompt
    assert 'emit "first_time_sender_with_financial_ask"' in prompt
    assert "risk_score=60" in prompt
    assert "vendor_fraud_score=55" in prompt
    assert "wire_transfer_anomaly_score=35" in prompt
    assert "invoice_authenticity_score no higher than 55" in prompt
    assert "high-value emergency invoice" in prompt
    assert 'emit both "unusual_dollar_amount" and "urgency_paired_with_finance"' in prompt
    assert "risk_score=75" in prompt
    assert "vendor_fraud_score=70" in prompt
    assert "wire_transfer_anomaly_score=45" in prompt
    assert "fake thread-continuity invoice" in prompt
    assert "vendor_fraud_score at least 60" in prompt


def test_scoring_agent_passes_locked_prompt_to_llm_client(tmp_path):
    context = _context(tmp_path)
    _seed_inbound(context)
    captured: dict[str, str] = {}

    def _capturing_client(system_prompt: str, user_prompt: str) -> str:
        captured["system_prompt"] = system_prompt
        captured["user_prompt"] = user_prompt
        return _valid_analysis_json()

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_capturing_client,
            production_tenant_id=TENANT,
        ),
    )

    assert captured["system_prompt"] == NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT


def test_scoring_agent_persists_high_vendor_fraud_dimensions_end_to_end(tmp_path):
    """Worked Example 1 (deep dive §3) — vendor invoice fraud must round-trip."""
    context = _context(tmp_path)
    _seed_inbound(context, subject="URGENT: Invoice 4471 - payment due today")

    response = _valid_analysis_json(
        risk_analysis={
            "risk_score": 88,
            "risk_factors": ["new_banking_instructions", "lookalike_sender_domain"],
            "phishing_signals": ["lookalike_sender_domain"],
            "urgency_signals": ["payment_today"],
            "financial_risk": "high",
            "vendor_fraud_score": 88,
            "wire_transfer_anomaly_score": 72,
            "invoice_authenticity_score": 25,
            "behavioral_deviation_flags": [
                "new_banking_instructions",
                "urgency_paired_with_finance",
                "lookalike_sender_domain",
            ],
        },
        recommended_action="block",
    )

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(response),
            production_tenant_id=TENANT,
        ),
    )

    analyses = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_ANALYSIS
    ]
    assert len(analyses) == 1
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)
    assert parsed.recommended_action == "block"
    assert parsed.risk_analysis.vendor_fraud_score == 88
    assert parsed.risk_analysis.wire_transfer_anomaly_score == 72
    assert parsed.risk_analysis.invoice_authenticity_score == 25
    assert "new_banking_instructions" in parsed.risk_analysis.behavioral_deviation_flags


def test_scoring_agent_persists_executive_impersonation_dimensions_end_to_end(tmp_path):
    """Worked Example 2 (deep dive §3) — executive impersonation wire pressure."""
    context = _context(tmp_path)
    _seed_inbound(
        context,
        subject="Quick wire - can't talk now",
        sender="sarahchen.cfo@gmail.com",
    )

    response = _valid_analysis_json(
        risk_analysis={
            "risk_score": 94,
            "risk_factors": ["executive_impersonation", "out_of_band_pressure"],
            "phishing_signals": ["freemail_sender_for_executive_action"],
            "urgency_signals": ["by_4pm_today"],
            "financial_risk": "high",
            "vendor_fraud_score": 35,
            "wire_transfer_anomaly_score": 95,
            "invoice_authenticity_score": None,
            "behavioral_deviation_flags": [
                "out_of_band_pressure",
                "urgency_paired_with_finance",
                "first_time_sender_with_financial_ask",
            ],
        },
        recommended_action="block",
    )

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(response),
            production_tenant_id=TENANT,
        ),
    )

    analyses = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_ANALYSIS
    ]
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)
    assert parsed.risk_analysis.wire_transfer_anomaly_score == 95
    assert parsed.risk_analysis.invoice_authenticity_score is None
    assert "out_of_band_pressure" in parsed.risk_analysis.behavioral_deviation_flags


def test_scoring_agent_persists_legitimate_vendor_dimensions_end_to_end(tmp_path):
    """Worked Example 3 (deep dive §3) — legit vendor invoice negative case."""
    context = _context(tmp_path)
    _seed_inbound(
        context,
        subject="Invoice 4471 - May parts order",
        sender="ap@acmemanufacturing.com",
    )

    response = _valid_analysis_json(
        risk_analysis={
            "risk_score": 8,
            "risk_factors": [],
            "phishing_signals": [],
            "urgency_signals": [],
            "financial_risk": "low",
            "vendor_fraud_score": 5,
            "wire_transfer_anomaly_score": 3,
            "invoice_authenticity_score": 85,
            "behavioral_deviation_flags": [],
        },
        recommended_action="safe",
    )

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(response),
            production_tenant_id=TENANT,
        ),
    )

    analyses = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_ANALYSIS
    ]
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)
    assert parsed.recommended_action == "safe"
    assert parsed.risk_analysis.invoice_authenticity_score == 85
    assert parsed.risk_analysis.behavioral_deviation_flags == []


def test_scoring_agent_persists_ambiguous_needs_review_dimensions_end_to_end(tmp_path):
    """Worked Example 4 (deep dive §3) — ambiguous needs_review."""
    context = _context(tmp_path)
    _seed_inbound(context, subject="Invoice for April work")

    response = _valid_analysis_json(
        risk_analysis={
            "risk_score": 55,
            "risk_factors": ["new_banking_instructions"],
            "phishing_signals": ["new_banking_instructions"],
            "urgency_signals": [],
            "financial_risk": "medium",
            "vendor_fraud_score": 55,
            "wire_transfer_anomaly_score": 50,
            "invoice_authenticity_score": 45,
            "behavioral_deviation_flags": ["new_banking_instructions"],
        },
        recommended_action="needs_review",
    )

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(response),
            production_tenant_id=TENANT,
        ),
    )

    analyses = [
        r for r in _production_records(context) if r.record_type == RecordType.EMAIL_ANALYSIS
    ]
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)
    assert parsed.recommended_action == "needs_review"
    assert parsed.risk_analysis.vendor_fraud_score == 55
    assert parsed.risk_analysis.invoice_authenticity_score == 45


def test_scoring_agent_rejects_unknown_behavioral_deviation_flag_from_llm(tmp_path):
    """Defense in depth: even if the LLM ignores the prompt's enum list and
    invents a freeform flag, the schema's Literal forbids it. The agent
    surfaces the failure through its existing schema_mismatch path."""
    context = _context(tmp_path)
    _seed_inbound(context)

    response = _valid_analysis_json(
        risk_analysis={
            "risk_score": 50,
            "risk_factors": [],
            "phishing_signals": [],
            "urgency_signals": [],
            "financial_risk": "medium",
            "vendor_fraud_score": 40,
            "wire_transfer_anomaly_score": 30,
            "invoice_authenticity_score": None,
            "behavioral_deviation_flags": ["invented_freeform_flag"],
        },
    )

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(response),
            production_tenant_id=TENANT,
        ),
    )

    assert result.analyzed == 0
    assert result.failed == 1
    assert result.failures[0].failure_reason in {"schema_mismatch", "invalid_enum"}


def test_scoring_agent_rejects_out_of_range_vendor_fraud_score(tmp_path):
    context = _context(tmp_path)
    _seed_inbound(context)

    response = _valid_analysis_json(
        risk_analysis={
            "risk_score": 50,
            "risk_factors": [],
            "phishing_signals": [],
            "urgency_signals": [],
            "financial_risk": "medium",
            "vendor_fraud_score": 150,
            "wire_transfer_anomaly_score": 30,
            "invoice_authenticity_score": None,
            "behavioral_deviation_flags": [],
        },
    )

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(response),
            production_tenant_id=TENANT,
        ),
    )

    assert result.failed == 1
    assert result.failures[0].failure_reason in {"out_of_range", "schema_mismatch"}


def test_scoring_agent_persists_unicode_obfuscation_flag_for_coastal_marine_case(
    tmp_path,
):
    """Coastal-marine eval-grid case: Unicode hyphen in sender domain plus
    zero-width space in filename now has a locked behavioral flag.
    """
    context = _context(tmp_path)
    _seed_inbound(
        context,
        subject="Invoice attached",
        sender="billing@coastal\u2011marine.ca",
    )

    response = _valid_analysis_json(
        risk_analysis={
            "risk_score": 78,
            "risk_factors": [
                "lookalike_sender_domain",
                "zero_width_space_in_attachment_filename",
                "empty_body_attachment_only_delivery",
            ],
            "phishing_signals": [
                "lookalike_sender_domain",
                "unicode_obfuscation_in_attachment_filename",
            ],
            "urgency_signals": [],
            "financial_risk": "high",
            "vendor_fraud_score": 72,
            "wire_transfer_anomaly_score": 25,
            "invoice_authenticity_score": None,
            "behavioral_deviation_flags": [
                "lookalike_sender_domain",
                "first_time_sender_with_financial_ask",
                "unusual_unicode_obfuscation",
            ],
        },
        recommended_action="needs_review",
    )

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(response),
            production_tenant_id=TENANT,
        ),
    )

    analyses = [
        r
        for r in _production_records(context)
        if r.record_type == RecordType.EMAIL_ANALYSIS
    ]
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)
    assert "unusual_unicode_obfuscation" in (
        parsed.risk_analysis.behavioral_deviation_flags
    )
    assert parsed.risk_analysis.vendor_fraud_score == 72


# --- Client-facing 5-axis rubric wiring (§11 SIGNED 2026-05-25) -----------


def test_client_facing_rubric_is_unattached_by_default(tmp_path):
    """Default ``EmailRiskScoringConfig.enable_client_facing_rubric=False``
    leaves ``EmailAnalysisPayload.client_facing_rubric`` at ``None`` so the
    activation gate (spec §9 step 5) holds: no client-facing surface ships
    until an operator explicitly flips the flag.
    """
    context = _context(tmp_path)
    _seed_inbound(context)

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json()),
            production_tenant_id=TENANT,
        ),
    )

    analyses = [
        r
        for r in _production_records(context)
        if r.record_type == RecordType.EMAIL_ANALYSIS
    ]
    assert len(analyses) == 1
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)
    assert parsed.client_facing_rubric is None


def test_client_facing_rubric_attaches_when_flag_enabled(tmp_path):
    """When ``enable_client_facing_rubric=True``, the production cycle writes
    an ``EmailAnalysisPayload`` whose ``client_facing_rubric`` is populated
    with exactly five axes in the spec §3 / D14 fixed order, and the existing
    ``recommended_action`` and ``risk_score`` fields are unchanged (D5 / §8.14
    kill-switch invariant).
    """
    context = _context(tmp_path)
    _seed_inbound(context)

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json()),
            production_tenant_id=TENANT,
            enable_client_facing_rubric=True,
        ),
    )

    analyses = [
        r
        for r in _production_records(context)
        if r.record_type == RecordType.EMAIL_ANALYSIS
    ]
    assert len(analyses) == 1
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)

    rubric = parsed.client_facing_rubric
    assert rubric is not None
    assert rubric.rubric_version == "v1"
    assert len(rubric.axes) == 5
    assert tuple(a.axis_name for a in rubric.axes) == (
        "sender_identity",
        "conversation_continuity",
        "vendor_payment_history",
        "document_integrity",
        "origin_timing",
    )
    assert 0 <= rubric.axis_total <= 10

    # Lift-only invariant: the rubric attach must not move the internal
    # scoring numbers or the recommended action.
    assert parsed.risk_analysis.risk_score == 72
    assert parsed.recommended_action == "needs_review"


def test_client_facing_rubric_projection_failure_marks_unavailable_and_audits(
    tmp_path, monkeypatch
):
    """D12 failure posture: projection failures must not silently look like
    the flag was disabled. Internal analysis still emits, the rubric payload
    is marked unavailable, and the normal audit marker records the failure.
    """
    context = _context(tmp_path)
    _seed_inbound(context)

    def _boom(_payload):
        raise RuntimeError("synthetic projection failure")

    monkeypatch.setattr(
        "core.scoring.email_risk_scoring_agent.project_client_facing_rubric",
        _boom,
    )

    result = run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(_valid_analysis_json()),
            production_tenant_id=TENANT,
            enable_client_facing_rubric=True,
        ),
    )

    assert result.analyzed == 1
    records = _production_records(context)
    analyses = [
        r for r in records if r.record_type == RecordType.EMAIL_ANALYSIS
    ]
    assert len(analyses) == 1
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)

    rubric = parsed.client_facing_rubric
    assert rubric is not None
    assert rubric.rubric_status == "unavailable"
    assert rubric.axis_total == 0
    assert rubric.axes == ()
    assert rubric.rubric_consistency_override is True
    assert rubric.rubric_consistency_reason is not None
    assert "projection unavailable" in rubric.rubric_consistency_reason
    assert len(rubric.rubric_consistency_reason) <= 220

    markers = [
        r
        for r in records
        if r.record_type == RecordType.AUDIT_VERDICT
        and r.workflow_id == EMAIL_ANALYSIS_COMPLETE_WORKFLOW_ID
    ]
    assert len(markers) == 1
    assert any(
        "client_facing_rubric=unavailable" in finding
        for finding in markers[0].payload["findings"]
    )


def test_client_facing_rubric_isolation_across_two_tenants(tmp_path):
    """§8.13 gate test (Tenant isolation: no cross-tenant rubric evidence leak).

    Drives two distinct production scoring cycles for ``tenant_a`` and
    ``tenant_b`` on the same blackboard root, both with
    ``enable_client_facing_rubric=True``. Asserts each tenant's blackboard
    contains exactly its own ``EMAIL_ANALYSIS`` record with its own rubric,
    and asserts the other tenant's inbound id never appears in either
    tenant's record stream. This is the integration-level proof for §8.13;
    structural mapper purity is covered separately in
    ``test_mapper_is_pure_no_payload_mutation``.
    """
    context = _context(tmp_path)
    tenant_a = "tenant_a"
    tenant_b = "tenant_b"

    inbound_a = _seed_inbound(
        context,
        subject="ACME wire request",
        sender="billing-a@vendor-a.example",
        tenant_id=tenant_a,
    )
    inbound_b = _seed_inbound(
        context,
        subject="Beta credentials reset",
        sender="security-b@idp-b.example",
        tenant_id=tenant_b,
    )

    # Distinct canned responses so we can prove each tenant's rubric came
    # from its own inbound's analysis, not crossed over.
    response_a = _valid_analysis_json(
        risk_analysis={
            "risk_score": 81,
            "risk_factors": ["spoofed_sender_domain_a"],
            "phishing_signals": [],
            "urgency_signals": ["please_reply_today"],
            "financial_risk": "high",
            "vendor_fraud_score": 70,
            "wire_transfer_anomaly_score": 65,
            "invoice_authenticity_score": None,
            "behavioral_deviation_flags": ["new_banking_instructions"],
        },
        recommended_action="block",
    )
    response_b = _valid_analysis_json(
        risk_analysis={
            "risk_score": 33,
            "risk_factors": ["credential_reset_pattern_b"],
            "phishing_signals": [],
            "urgency_signals": [],
            "financial_risk": "medium",
            "vendor_fraud_score": 20,
            "wire_transfer_anomaly_score": 15,
            "invoice_authenticity_score": None,
            "behavioral_deviation_flags": [],
        },
        impersonation_analysis={
            "impersonation_likelihood": 25,
            "suspicious_elements": [],
            "sender_legitimacy_notes": "moderate signal only",
        },
        recommended_action="needs_review",
    )

    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(response_a),
            production_tenant_id=tenant_a,
            enable_client_facing_rubric=True,
        ),
    )
    run_email_risk_scoring_cycle(
        context,
        config=EmailRiskScoringConfig(
            llm_client=_canned_client(response_b),
            production_tenant_id=tenant_b,
            enable_client_facing_rubric=True,
        ),
    )

    records_a = _production_records(context, tenant=tenant_a)
    records_b = _production_records(context, tenant=tenant_b)

    analyses_a = [r for r in records_a if r.record_type == RecordType.EMAIL_ANALYSIS]
    analyses_b = [r for r in records_b if r.record_type == RecordType.EMAIL_ANALYSIS]
    assert len(analyses_a) == 1
    assert len(analyses_b) == 1

    parsed_a = EmailAnalysisPayload.model_validate(analyses_a[0].payload)
    parsed_b = EmailAnalysisPayload.model_validate(analyses_b[0].payload)

    # Each tenant's analysis points at its own inbound id only.
    assert parsed_a.source_email_record_id == inbound_a
    assert parsed_b.source_email_record_id == inbound_b

    # Each tenant carries its own distinct internal scoring numbers, proving
    # we are looking at independent analyses, not a shared object.
    assert parsed_a.risk_analysis.risk_score == 81
    assert parsed_b.risk_analysis.risk_score == 33
    assert parsed_a.recommended_action == "block"
    assert parsed_b.recommended_action == "needs_review"

    # Rubric is attached for both, but each rubric must reflect its own
    # tenant's evidence — not the other tenant's.
    assert parsed_a.client_facing_rubric is not None
    assert parsed_b.client_facing_rubric is not None
    assert parsed_a.client_facing_rubric.rubric_status == "available"
    assert parsed_b.client_facing_rubric.rubric_status == "available"

    # tenant_a is high-risk (band 75-100, axis_total 7-10).
    assert 7 <= parsed_a.client_facing_rubric.axis_total <= 10
    # tenant_b is moderate-low (band 25-49, axis_total 2-5).
    assert 2 <= parsed_b.client_facing_rubric.axis_total <= 5

    # Hard isolation assertions: no record on tenant_a's blackboard
    # references tenant_b's inbound id (or vice versa) in any of the
    # cross-record fields the rubric path could touch.
    serialized_a = json.dumps([r.payload for r in records_a])
    serialized_b = json.dumps([r.payload for r in records_b])
    assert str(inbound_b) not in serialized_a, (
        "tenant_a's blackboard leaked tenant_b's inbound id"
    )
    assert str(inbound_a) not in serialized_b, (
        "tenant_b's blackboard leaked tenant_a's inbound id"
    )
    # And no record on either side carries the *other* tenant's tenant_id
    # field at the record level.
    assert all(r.tenant_id == tenant_a for r in records_a)
    assert all(r.tenant_id == tenant_b for r in records_b)


def test_production_loop_preserves_client_facing_rubric_flag_through_rebuild(tmp_path):
    """Activation regression: ``ProductionLoopConfig`` rebuilds the
    ``EmailRiskScoringConfig`` whenever the cycle tenant or any of the
    Phase 1.4 lifts force one. Without explicit preservation, the
    operator-supplied ``enable_client_facing_rubric=True`` would silently
    revert to the dataclass default (False) on every real production cycle.
    This test forces the rebuild branch via a mismatched tenant id and
    asserts the persisted analysis record carries the rubric.
    """
    context = _context(tmp_path)
    _seed_inbound(context)

    custom = EmailRiskScoringConfig(
        llm_client=_canned_client(_valid_analysis_json()),
        production_tenant_id="wrong_tenant_overridden",
        enable_client_facing_rubric=True,
    )

    from core.production import ProductionLoopConfig, ProductionSignal, run_production_cycle

    result = run_production_cycle(
        context,
        tenant_id=TENANT,
        signal=ProductionSignal(source="mailbox", event_kind="email_received"),
        config=ProductionLoopConfig(
            run_email_risk_scoring_at_end_of_cycle=True,
            email_risk_scoring_config=custom,
        ),
    )

    assert result.email_risk_scoring is not None
    assert result.email_risk_scoring.analyzed == 1

    analyses = [
        r
        for r in _production_records(context)
        if r.record_type == RecordType.EMAIL_ANALYSIS
    ]
    assert len(analyses) == 1
    parsed = EmailAnalysisPayload.model_validate(analyses[0].payload)
    assert parsed.client_facing_rubric is not None, (
        "production-loop rebuild dropped the enable_client_facing_rubric flag"
    )
    assert len(parsed.client_facing_rubric.axes) == 5
