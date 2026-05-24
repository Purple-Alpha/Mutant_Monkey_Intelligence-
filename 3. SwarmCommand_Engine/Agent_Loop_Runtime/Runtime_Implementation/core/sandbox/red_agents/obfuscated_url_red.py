"""Phase 1.3 Red profile: Obfuscated URL (``obfuscated_url_red_001``).

Generates emails carrying an obfuscated URL crossing URL kind × URL
path × body variant. Cross-product produces 108 deterministic cases
per battery (6 URL obfuscation kinds × 9 path fragments × 2 body
variants), satisfying §11 decision 3.

Every case is expected to trip the matching ``PrecursorIndicator``
from the ``url_obfuscation_detector`` plus, for paths that include
``/login`` / ``/signin`` / ``/account/login``, the
``login_path_url_present`` indicator as well.

See ``4. Product_Roadmap/Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md`` §1.
"""

from __future__ import annotations

from datetime import datetime, timezone

from core.blackboard import (
    EmailInboundPayload,
    PrecursorIndicator,
    SyntheticEmailAttackCasePayload,
)

from ._seed_data import (
    RECIPIENT_AP,
    URL_BODIES,
    URL_OBFUSCATION_KINDS,
    URL_PATH_FRAGMENTS,
)

RED_PROFILE_ID = "obfuscated_url_red_001"
ARCHETYPE = "obfuscated_url"

_INDICATOR_FOR_URL_KIND: dict[str, PrecursorIndicator] = {
    "punycode": "punycode_url_present",
    "homoglyph": "homoglyph_url_present",
    "shortener": "url_shortener_present",
    "credential_bearing": "credential_bearing_url",
    "suspicious_tld": "suspicious_tld_present",
    "ip_address": "ip_address_url_present",
}

_LOGIN_PATH_FRAGMENTS: frozenset[str] = frozenset(
    {"/login", "/signin", "/account/login", "/portal/login", "/sso/login"}
)

_BASELINE = datetime(2026, 8, 1, 11, 0, tzinfo=timezone.utc)


def generate_cases(
    *,
    seed: int = 0,
    count: int = 100,
) -> list[SyntheticEmailAttackCasePayload]:
    """Generate ``count`` deterministic obfuscated-URL cases."""

    if count < 1:
        raise ValueError("count must be >= 1")

    cross_product: list[tuple[str, str, str, str]] = []
    for url_kind, base_url in URL_OBFUSCATION_KINDS:
        for path in URL_PATH_FRAGMENTS:
            for body_fragment in URL_BODIES:
                cross_product.append((url_kind, base_url, path, body_fragment))

    if count > len(cross_product):
        raise ValueError(
            f"count {count} exceeds maximum cross-product size {len(cross_product)}"
        )

    cases: list[SyntheticEmailAttackCasePayload] = []
    for i in range(count):
        idx = (seed + i) % len(cross_product)
        url_kind, base_url, path, body_fragment = cross_product[idx]
        url = f"{base_url}{path}"
        sender = f"alerts-{i:03d}@notifications.example"
        case_id = f"obfuscated-url-{url_kind}-{path.strip('/').replace('/', '-')}-{i:03d}"

        body = (
            f"Hello,\n\n{body_fragment}\n\nUse this secure link to continue:\n"
            f"{url}\n\nThank you,\nSecurity Team"
        )
        inbound = EmailInboundPayload(
            received_at=_BASELINE,
            sender=sender,
            recipient=RECIPIENT_AP,
            subject="Action required: verify your account",
            body_plain=body,
        )

        indicators: list[PrecursorIndicator] = [_INDICATOR_FOR_URL_KIND[url_kind]]
        if path in _LOGIN_PATH_FRAGMENTS:
            indicators.append("login_path_url_present")

        cases.append(
            SyntheticEmailAttackCasePayload(
                case_id=case_id,
                red_profile_id=RED_PROFILE_ID,
                archetype=ARCHETYPE,
                attack_pattern=f"obfuscated_url:{url_kind}",
                inbound=inbound,
                case_tags=(),
                expected_min_risk_score=55,
                expected_recommended_actions=("needs_review", "block"),
                expected_behavioral_flags=(),
                expected_precursor_indicators=tuple(indicators),
                expects_precursor_block=True,
            )
        )

    return cases


def case_universe_size() -> int:
    return (
        len(URL_OBFUSCATION_KINDS) * len(URL_PATH_FRAGMENTS) * len(URL_BODIES)
    )


__all__ = [
    "ARCHETYPE",
    "RED_PROFILE_ID",
    "case_universe_size",
    "generate_cases",
]
