"""Phase 1.3 Red profile: Fake Invoice (``fake_invoice_red_001``).

Generates invoice-flavoured synthetic emails crossing vendor name ×
sender-domain variant × urgency tier. The cross-product produces 100
deterministic cases per battery (10 vendors × 5 domain variants ×
2 urgency tiers), satisfying §11 decision 3.

Every case carries an attached invoice payload, a "new banking
instructions" cue, and a synthesized invoice number. The expected
behavioral flags depend on the domain variant (lookalike variants
expect ``lookalike_sender_domain``; the matching-legit variant does
not), keeping the failure-mode taxonomy exercise-able when Blue
fails to surface the correct subset.

See ``4. Product_Roadmap/Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md`` §1.
"""

from __future__ import annotations

from datetime import datetime, timezone

from core.blackboard import (
    BehavioralDeviationFlag,
    EmailAttachmentMeta,
    EmailInboundPayload,
    Phase13CaseTag,
    SyntheticEmailAttackCasePayload,
)

from ._seed_data import (
    DOLLAR_AMOUNTS,
    RECIPIENT_AP,
    SENDER_DOMAIN_VARIANT_KINDS,
    URGENCY_PHRASES,
    VENDOR_NAMES,
    build_sender_domain,
    vendor_slug,
)

RED_PROFILE_ID = "fake_invoice_red_001"
ARCHETYPE = "fake_invoice"

# Deterministic timestamp baseline so every case in a battery has a
# stable received_at relative to its index. Avoids datetime.now() so
# generator output is byte-deterministic per Decision 3.
_BASELINE = datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)


def _expected_flags_for_variant(kind: str) -> tuple[BehavioralDeviationFlag, ...]:
    """Behavioral flags every case of a given variant kind must surface.

    Kept as the **minimum required** subset (the eval-harness behavioural
    flag contract is "required flags present, extras allowed", per the
    Month 2 Bucket A calibration).
    """

    base: tuple[BehavioralDeviationFlag, ...] = (
        "first_time_sender_with_financial_ask",
        "new_banking_instructions",
        "urgency_paired_with_finance",
    )
    if kind == "matching_legit":
        # Domain looks legit; lookalike flag is not required for this
        # variant, only the other three.
        return base
    return base + ("lookalike_sender_domain",)


def _expected_unusual_amount(amount: int) -> bool:
    return amount >= 25_000


def generate_cases(
    *,
    seed: int = 0,
    count: int = 100,
) -> list[SyntheticEmailAttackCasePayload]:
    """Generate ``count`` deterministic fake-invoice cases.

    ``seed`` rotates the deterministic cross-product start so different
    seeds produce different orderings of the same case universe. The
    full cross-product has 100 unique cases (10 vendors × 5 variants ×
    2 urgency tiers); ``count`` caps the returned slice from there.
    """

    if count < 1:
        raise ValueError("count must be >= 1")

    cross_product: list[tuple[int, str, int, str, int]] = []
    for v_idx, vendor in enumerate(VENDOR_NAMES):
        for k_idx, kind in enumerate(SENDER_DOMAIN_VARIANT_KINDS):
            for u_idx in range(2):  # two urgency tiers per vendor+variant
                amount = DOLLAR_AMOUNTS[(v_idx + k_idx + u_idx) % len(DOLLAR_AMOUNTS)]
                cross_product.append((v_idx, kind, u_idx, vendor, amount))

    if count > len(cross_product):
        raise ValueError(
            f"count {count} exceeds maximum cross-product size {len(cross_product)}"
        )

    cases: list[SyntheticEmailAttackCasePayload] = []
    for i in range(count):
        idx = (seed + i) % len(cross_product)
        v_idx, kind, u_idx, vendor, amount = cross_product[idx]
        slug = vendor_slug(vendor)
        domain = build_sender_domain(slug, kind)
        urgency = URGENCY_PHRASES[u_idx % len(URGENCY_PHRASES)]
        invoice_no = f"{(v_idx * 1000) + (u_idx * 100) + idx:05d}"
        sender = f"billing@{domain}"
        case_id = f"fake-invoice-{slug}-{kind}-{u_idx}-{i:03d}"

        body = (
            f"Hello,\n\n"
            f"This is our first invoice after onboarding. Please process "
            f"invoice {invoice_no} for ${amount:,} {urgency}. Use the new "
            f"remittance instructions on the attached PDF.\n\n"
            f"Regards,\n{vendor} Billing"
        )
        attachment = EmailAttachmentMeta(
            filename=f"invoice_{invoice_no}.pdf",
            content_type="application/pdf",
            size_bytes=119_233 + idx,
            attachment_class="invoice",
            extracted_text=(
                f"{vendor} invoice {invoice_no}. Total due ${amount:,}. "
                f"Please remit to the account details on this page."
            ),
        )

        flags = _expected_flags_for_variant(kind)
        if _expected_unusual_amount(amount):
            flags = flags + ("unusual_dollar_amount",)

        inbound = EmailInboundPayload(
            received_at=_BASELINE,
            sender=sender,
            recipient=RECIPIENT_AP,
            subject=f"Invoice {invoice_no} - remittance details attached",
            body_plain=body,
            attachments=[attachment],
        )

        cases.append(
            SyntheticEmailAttackCasePayload(
                case_id=case_id,
                red_profile_id=RED_PROFILE_ID,
                archetype=ARCHETYPE,
                attack_pattern=f"fake_invoice:{kind}",
                inbound=inbound,
                case_tags=(),
                expected_min_risk_score=60,
                expected_recommended_actions=("needs_review", "block"),
                expected_behavioral_flags=flags,
                expects_precursor_block=True,
            )
        )

    return cases


def case_universe_size() -> int:
    """Total unique cases in the deterministic cross-product."""

    return len(VENDOR_NAMES) * len(SENDER_DOMAIN_VARIANT_KINDS) * 2


__all__ = [
    "ARCHETYPE",
    "RED_PROFILE_ID",
    "case_universe_size",
    "generate_cases",
]
