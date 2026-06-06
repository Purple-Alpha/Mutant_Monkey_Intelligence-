"""Lookalike Domain Detector pure-function tests.

Locked by ``4. Product_Roadmap/Lookalike_Domain_Detector_Deep_Dive.md``
(§11 SIGNED 2026-06-05). These tests cover D1-D9 at the detector boundary:
pure offline operation, exact-match allowlist, conservative edit-distance
thresholds, homoglyph / punycode handling, tenant-local combosquat tokens,
TLD swap, subdomain spoof, From + Reply-To identity surface, and crash
resistance.
"""

from __future__ import annotations

from core.scoring.lookalike_domain_detector import (
    detect_lookalike_domains,
    extract_identity_domains,
)


def test_exact_match_known_good_short_circuits_to_zero() -> None:
    assessment = detect_lookalike_domains(
        from_address="Accounts Payable <ap@harborline.example>",
        known_good_domains=("harborline.example",),
    )

    assert assessment.fired is False
    assert assessment.lookalike_domain_score == 0
    assert assessment.findings == ()
    assert assessment.recommended_risk_floor_lift == 0


def test_typosquat_distance_one_is_strong_lookalike() -> None:
    assessment = detect_lookalike_domains(
        from_address="billing@harborllne.example",
        known_good_domains=("harborline.example",),
    )

    assert assessment.fired is True
    assert assessment.lookalike_domain_score == 85
    assert assessment.recommended_risk_floor_lift == 85
    assert assessment.findings[0].technique == "typosquat"
    assert assessment.findings[0].distance == 1


def test_long_domain_distance_two_is_probable_not_strong() -> None:
    assessment = detect_lookalike_domains(
        from_address="billing@northcoast-parzz.example",
        known_good_domains=("northcoast-parts.example",),
    )

    assert assessment.fired is True
    assert assessment.lookalike_domain_score == 70
    assert assessment.recommended_risk_floor_lift == 70
    assert any(f.technique == "typosquat" and f.distance == 2 for f in assessment.findings)


def test_short_domain_distance_two_does_not_fire() -> None:
    assessment = detect_lookalike_domains(
        from_address="ap@abxy.example",
        known_good_domains=("abcd.example",),
    )

    assert assessment.fired is False


def test_homoglyph_normalizes_to_known_good_domain() -> None:
    # First "p" and "a" are Cyrillic lookalikes.
    assessment = detect_lookalike_domains(
        from_address="security@раypal.example",
        known_good_domains=("paypal.example",),
    )

    assert assessment.fired is True
    assert any(f.technique == "homoglyph" for f in assessment.findings)
    assert assessment.recommended_risk_floor_lift == 85


def test_punycode_decoding_surfaces_lookalike_without_network() -> None:
    punycode_domain = "раypal.example".encode("idna").decode("ascii")

    assessment = detect_lookalike_domains(
        from_address=f"security@{punycode_domain}",
        known_good_domains=("paypal.example",),
    )

    assert assessment.fired is True
    assert any(f.technique == "punycode" for f in assessment.findings)
    assert assessment.recommended_risk_floor_lift == 85


def test_combosquat_uses_tenant_known_good_token_only() -> None:
    assessment = detect_lookalike_domains(
        from_address="billing@harborline-secure.example",
        known_good_domains=("harborline.example",),
    )

    assert assessment.fired is True
    assert any(f.technique == "combosquat" for f in assessment.findings)
    assert assessment.recommended_risk_floor_lift == 70


def test_generic_short_tokens_do_not_create_global_brand_seed_behavior() -> None:
    assessment = detect_lookalike_domains(
        from_address="billing@secure-payments.example",
        known_good_domains=("pay.example", "secure.example"),
    )

    assert assessment.fired is False


def test_tld_swap_same_second_level_label_fires() -> None:
    assessment = detect_lookalike_domains(
        from_address="billing@harborline.co",
        known_good_domains=("harborline.com",),
    )

    assert assessment.fired is True
    assert any(f.technique == "tld_swap" for f in assessment.findings)
    assert assessment.recommended_risk_floor_lift == 70


def test_subdomain_spoof_fires_when_known_good_domain_is_under_attacker_parent() -> None:
    assessment = detect_lookalike_domains(
        from_address="billing@harborline.example.attacker.test",
        known_good_domains=("harborline.example",),
    )

    assert assessment.fired is True
    assert any(f.technique == "subdomain_spoof" for f in assessment.findings)
    assert assessment.recommended_risk_floor_lift == 85


def test_reply_to_domain_is_in_v1_identity_surface() -> None:
    domains = extract_identity_domains(
        from_address="ap@trusted.example",
        headers={"Reply-To": "payments@harborllne.example"},
    )

    assert domains == ("trusted.example", "harborllne.example")

    assessment = detect_lookalike_domains(
        from_address="ap@trusted.example",
        headers={"Reply-To": "payments@harborllne.example"},
        known_good_domains=("trusted.example", "harborline.example"),
    )

    assert assessment.fired is True
    assert assessment.findings[0].offending_domain == "harborllne.example"


def test_pathological_inputs_fail_closed_without_exception() -> None:
    assessment = detect_lookalike_domains(
        from_address="not an address \x00 \u200b" * 1000,
        headers={"Reply-To": "also-not-a-domain \n " * 1000},
        known_good_domains=("harborline.example",) * 300,
    )

    assert assessment.fired is False
