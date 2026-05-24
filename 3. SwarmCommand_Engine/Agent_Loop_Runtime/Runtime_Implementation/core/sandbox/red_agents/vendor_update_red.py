"""Phase 1.3 Red profile: Vendor-Update Pivot (``vendor_update_red_001``).

Generates "we changed our banking details" / "new remit-to address" /
thread-hijack / future-dated-invoice patterns from a sender that
otherwise looks like a known vendor. Cross-product produces 128
deterministic cases per battery (8 vendors × 4 patterns × 4 stylistic
variants), satisfying §11 decision 3.

Every case carries an explicit "new banking instructions" cue and a
mismatch between the apparent vendor name in the body and the sender
domain on at least the prefix/suffix/tld_swap variants. The
``reply_to_diverges_from_from`` flag is required when ``Reply-To``
points to a different namespace than ``From``.

See ``4. Product_Roadmap/Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md`` §1.
"""

from __future__ import annotations

from datetime import datetime, timezone

from core.blackboard import (
    BehavioralDeviationFlag,
    EmailAttachmentMeta,
    EmailInboundPayload,
    SyntheticEmailAttackCasePayload,
)

from ._seed_data import (
    DOLLAR_AMOUNTS,
    RECIPIENT_FINANCE,
    URGENCY_PHRASES,
    VENDOR_NAMES,
    VENDOR_UPDATE_PATTERN_KINDS,
    vendor_slug,
)

RED_PROFILE_ID = "vendor_update_red_001"
ARCHETYPE = "vendor_update_pivot"

# Restrict to first 8 vendors so the cross-product lands at 128 cases.
_VENDORS = VENDOR_NAMES[:8]
_VARIANTS = ("urgent", "calm", "with_attachment", "with_reply_to")

_BASELINE = datetime(2026, 6, 15, 10, 0, tzinfo=timezone.utc)


def _body_for_pattern(
    *, pattern: str, vendor: str, amount: int, urgency: str
) -> str:
    if pattern == "ach_routing_change":
        return (
            f"Hi finance team,\n\n"
            f"Heads up: we updated our ACH routing details effective {urgency}. "
            f"Please use the new account information for the ${amount:,} payment.\n\n"
            f"Thanks,\n{vendor} Accounts"
        )
    if pattern == "remit_to_address_change":
        return (
            f"Hello,\n\n"
            f"Our remit-to address has changed. Please send the ${amount:,} "
            f"payment to the new banking instructions on the attached file. "
            f"Confirmation needed {urgency}.\n\n"
            f"Best,\n{vendor} Billing"
        )
    if pattern == "thread_hijack_reply":
        return (
            f"Re: invoice follow-up\n\n"
            f"Hi,\n\n"
            f"Continuing our thread - we need to redirect the ${amount:,} "
            f"payment to our new bank. Process {urgency} please.\n\n"
            f"{vendor} AP"
        )
    if pattern == "future_dated_invoice":
        return (
            f"Hi,\n\n"
            f"Attached is the upcoming invoice for ${amount:,}. New bank "
            f"details apply effective next cycle - please update remit-to "
            f"{urgency}.\n\n"
            f"Regards,\n{vendor}"
        )
    raise ValueError(f"unknown pattern: {pattern!r}")


def _expected_flags_for_variant(
    *, pattern: str, variant: str
) -> tuple[BehavioralDeviationFlag, ...]:
    base: tuple[BehavioralDeviationFlag, ...] = (
        "new_banking_instructions",
        "first_time_sender_with_financial_ask",
    )
    if pattern == "thread_hijack_reply":
        base = base + ("out_of_band_pressure",)
    if variant == "with_reply_to":
        base = base + ("reply_to_diverges_from_from",)
    if variant == "urgent":
        base = base + ("urgency_paired_with_finance",)
    if pattern == "remit_to_address_change":
        base = base + ("mismatched_invoice_vendor_name",)
    return base


def generate_cases(
    *,
    seed: int = 0,
    count: int = 100,
) -> list[SyntheticEmailAttackCasePayload]:
    """Generate ``count`` deterministic vendor-update-pivot cases."""

    if count < 1:
        raise ValueError("count must be >= 1")

    cross_product: list[tuple[int, str, str, int]] = []
    for v_idx, vendor in enumerate(_VENDORS):
        for pattern in VENDOR_UPDATE_PATTERN_KINDS:
            for var_idx, variant in enumerate(_VARIANTS):
                amount = DOLLAR_AMOUNTS[(v_idx + var_idx) % len(DOLLAR_AMOUNTS)]
                cross_product.append((v_idx, pattern, variant, amount))

    if count > len(cross_product):
        raise ValueError(
            f"count {count} exceeds maximum cross-product size {len(cross_product)}"
        )

    cases: list[SyntheticEmailAttackCasePayload] = []
    for i in range(count):
        idx = (seed + i) % len(cross_product)
        v_idx, pattern, variant, amount = cross_product[idx]
        vendor = _VENDORS[v_idx]
        slug = vendor_slug(vendor)
        urgency = URGENCY_PHRASES[(v_idx + i) % len(URGENCY_PHRASES)]
        sender = f"ap@{slug}-billing.example"
        case_id = f"vendor-update-{slug}-{pattern}-{variant}-{i:03d}"

        headers: dict[str, str] = {}
        if variant == "with_reply_to":
            headers = {"Reply-To": f"finance-update-{i:03d}@notifications.test"}

        attachments: list[EmailAttachmentMeta] = []
        if variant == "with_attachment":
            attachments.append(
                EmailAttachmentMeta(
                    filename=f"updated_remit_to_{slug}.pdf",
                    content_type="application/pdf",
                    size_bytes=84_120 + i,
                    attachment_class="invoice",
                    extracted_text=(
                        f"{vendor} updated banking instructions. "
                        f"Please remit ${amount:,} to the new account."
                    ),
                )
            )

        inbound = EmailInboundPayload(
            received_at=_BASELINE,
            sender=sender,
            recipient=RECIPIENT_FINANCE,
            subject=f"{vendor} - updated banking instructions",
            body_plain=_body_for_pattern(
                pattern=pattern, vendor=vendor, amount=amount, urgency=urgency
            ),
            headers=headers,
            attachments=attachments,
        )

        cases.append(
            SyntheticEmailAttackCasePayload(
                case_id=case_id,
                red_profile_id=RED_PROFILE_ID,
                archetype=ARCHETYPE,
                attack_pattern=f"vendor_update:{pattern}:{variant}",
                inbound=inbound,
                case_tags=(),
                expected_min_risk_score=65,
                expected_recommended_actions=("needs_review", "block"),
                expected_behavioral_flags=_expected_flags_for_variant(
                    pattern=pattern, variant=variant
                ),
                expects_precursor_block=True,
            )
        )

    return cases


def case_universe_size() -> int:
    return len(_VENDORS) * len(VENDOR_UPDATE_PATTERN_KINDS) * len(_VARIANTS)


__all__ = [
    "ARCHETYPE",
    "RED_PROFILE_ID",
    "case_universe_size",
    "generate_cases",
]
