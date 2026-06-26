"""Executive Impersonation Detector pure-function tests."""

from __future__ import annotations

from core.scoring.executive_impersonation_detector import (
    EXECUTIVE_IMPERSONATION_PATTERN_FLAG,
    PrincipalRosterEntry,
    detect_executive_impersonation,
)
from core.scoring.lookalike_domain_detector import detect_lookalike_domains


def _cfo_roster() -> tuple[PrincipalRosterEntry, ...]:
    return (
        PrincipalRosterEntry(
            display_name_forms=("Sarah Chen", "S. Chen"),
            authorized_domains=("northstar-customer.example",),
            principal_role="finance_authority",
        ),
    )


def test_empty_roster_short_circuits_to_zero() -> None:
    assessment = detect_executive_impersonation(
        display_name="Sarah Chen",
        from_address="sarahchen.cfo@gmail.com",
        body_plain="Wire funds today.",
        principal_roster=(),
    )
    assert assessment.fired is False
    assert assessment.executive_impersonation_score == 0
    assert assessment.findings == ()
    assert assessment.recommended_risk_floor_lift == 0


def test_authorized_domain_executive_does_not_fire() -> None:
    assessment = detect_executive_impersonation(
        display_name="Sarah Chen",
        from_address="sarahchen@northstar-customer.example",
        body_plain="Please approve the vendor payment today.",
        principal_roster=_cfo_roster(),
    )
    assert assessment.fired is False


def test_free_mail_executive_claim_fires_probable() -> None:
    assessment = detect_executive_impersonation(
        display_name="Sarah Chen",
        from_address="sarahchen.cfo@gmail.com",
        body_plain="Handle this payment before close of business.",
        principal_roster=_cfo_roster(),
    )
    assert assessment.fired is True
    assert assessment.executive_impersonation_score == 70
    assert assessment.recommended_risk_floor_lift == 70
    assert any(f.technique == "free_mail_executive_claim" for f in assessment.findings)


def test_domain_mismatch_fires_probable() -> None:
    assessment = detect_executive_impersonation(
        display_name="Sarah Chen",
        from_address="sarahchen@evil-vendor.example",
        body_plain="Please review this vendor request when you have a moment.",
        principal_roster=_cfo_roster(),
    )
    assert assessment.fired is True
    assert assessment.recommended_risk_floor_lift == 70
    assert any(f.technique == "roster_name_domain_mismatch" for f in assessment.findings)


def test_pressure_only_without_identity_match_does_not_fire() -> None:
    assessment = detect_executive_impersonation(
        display_name="Random Vendor",
        from_address="vendor@evil-vendor.example",
        body_plain="Wire $50,000 before close of business. Keep this confidential.",
        principal_roster=_cfo_roster(),
    )
    assert assessment.fired is False


def test_strong_band_requires_pressure_and_task_directive() -> None:
    assessment = detect_executive_impersonation(
        display_name="Sarah Chen",
        from_address="sarahchen.cfo@gmail.com",
        body_plain=(
            "As the CFO I need you to wire $42,000 today. "
            "Keep this between us. Do not loop in finance."
        ),
        principal_roster=_cfo_roster(),
    )
    assert assessment.fired is True
    assert assessment.executive_impersonation_score == 85
    assert assessment.recommended_risk_floor_lift == 85


def test_lookalike_cue_consumed_for_executive_claim() -> None:
    lookalike = detect_lookalike_domains(
        from_address="Sarah Chen <sarahchen@northstar-customer-support.example>",
        known_good_domains=("northstar-customer.example",),
    )
    assessment = detect_executive_impersonation(
        display_name="Sarah Chen",
        from_address="Sarah Chen <sarahchen@northstar-customer-support.example>",
        body_plain="Approve payment before end of day.",
        principal_roster=_cfo_roster(),
        lookalike_assessment=lookalike,
    )
    assert assessment.fired is True
    assert any(f.technique == "lookalike_domain_executive_claim" for f in assessment.findings)


def test_pattern_flag_constant() -> None:
    assert EXECUTIVE_IMPERSONATION_PATTERN_FLAG == "executive_impersonation_pattern"
