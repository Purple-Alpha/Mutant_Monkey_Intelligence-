"""Tests for payroll diversion detector — contract §6 ES1 bar."""

from core.scoring.payroll_diversion_detector import (
    DIRECT_DEPOSIT_CHANGE_REQUEST,
    EMPLOYEE_PAYROLL_SIGNAL_TYPE_PREFIX,
    PAYROLL_DIVERSION_PATTERN,
    PAYROLL_MAILBOX_TARGET,
    PAYROLL_VOCABULARY_SIGNAL,
    detect_payroll_diversion,
)

EI002_BODY = (
    "Please update the direct deposit for Jordan Lee before the next payroll run. "
    "I am tied up all morning so do not call; just reply when it is handled.\n\nCEO"
)

LH002_BODY = (
    "Payroll cutoff dates for June are attached. Please submit timesheets by the "
    "published deadlines. This is not a direct-deposit change request."
)


def test_ei002_emits_pattern_and_supporting_facts():
    assessment = detect_payroll_diversion(
        subject="Payroll update before next run",
        body_plain=EI002_BODY,
        recipient="payroll@northstar-customer.example",
        payroll_mailbox_roster=("payroll@",),
        employee_token_roster=("jordan_lee",),
    )
    facts = assessment.observation_facts()
    assert PAYROLL_DIVERSION_PATTERN in facts
    assert DIRECT_DEPOSIT_CHANGE_REQUEST in facts
    assert PAYROLL_MAILBOX_TARGET in facts
    assert PAYROLL_VOCABULARY_SIGNAL in facts
    assert "payment_signal_type" not in " ".join(facts)


def test_lh002_does_not_emit_pattern():
    assessment = detect_payroll_diversion(body_plain=LH002_BODY)
    facts = assessment.observation_facts()
    assert PAYROLL_DIVERSION_PATTERN not in facts
    assert DIRECT_DEPOSIT_CHANGE_REQUEST not in facts
    assert PAYROLL_VOCABULARY_SIGNAL in facts


def test_payroll_vocabulary_without_corroborator_emits_no_pattern():
    assessment = detect_payroll_diversion(
        body_plain="Payroll cutoff dates are attached for June."
    )
    facts = assessment.observation_facts()
    assert PAYROLL_VOCABULARY_SIGNAL in facts
    assert PAYROLL_DIVERSION_PATTERN not in facts


def test_employee_token_roster_emits_reference_without_display_name():
    assessment = detect_payroll_diversion(
        body_plain="Please update direct deposit for jordan_lee before payroll.",
        employee_token_roster=("jordan_lee",),
    )
    facts = assessment.observation_facts()
    assert any("employee_ref:jordan_lee" in fact for fact in facts)
    assert "Jordan Lee" not in facts


def test_banking_detail_emits_employee_signal_types_only():
    assessment = detect_payroll_diversion(
        body_plain=(
            "Update direct deposit routing number 021000021 and account number 12345."
        ),
        recipient="payroll@customer.example",
        payroll_mailbox_roster=("payroll@",),
    )
    facts = assessment.observation_facts()
    assert f"{EMPLOYEE_PAYROLL_SIGNAL_TYPE_PREFIX}:routing_number" in facts
    assert f"{EMPLOYEE_PAYROLL_SIGNAL_TYPE_PREFIX}:account_number" in facts
    assert "payment_signal_type" not in " ".join(facts)


def test_no_financial_signal_emits_no_pattern():
    assessment = detect_payroll_diversion(
        body_plain="Please review the attached payroll calendar.",
        recipient="payroll@customer.example",
        payroll_mailbox_roster=("payroll@",),
    )
    facts = assessment.observation_facts()
    assert PAYROLL_DIVERSION_PATTERN not in facts
