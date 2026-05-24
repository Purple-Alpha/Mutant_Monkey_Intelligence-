"""Phase 1.3 Red profile: Malicious Attachment (``malicious_attachment_red_001``).

Generates emails carrying a payload-style attachment crossing
attachment kind × sender variant × body variant. Cross-product
produces 112 deterministic cases per battery (7 attachment kinds ×
8 sender variants × 2 body variants), satisfying §11 decision 3.

Every case is expected to trip at least one deterministic precursor
indicator from the ``attachment_classifier`` detector
(``executable_attachment``, ``iso_or_disk_image_attachment``,
``macro_enabled_office_document``, ``double_extension_attachment``,
``encrypted_archive_attachment``, ``html_smuggling_attachment``). The
expected ``PrecursorIndicator`` tuple per case pins which indicator
the per-case Blue evaluation must see; failing to emit the indicator
produces a ``missing_precursor_indicator`` failure mode with the
specific indicator name in ``Phase13FailureDetail.dynamic_detail``.

See ``4. Product_Roadmap/Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md`` §1.
"""

from __future__ import annotations

from datetime import datetime, timezone

from core.blackboard import (
    EmailAttachmentMeta,
    EmailInboundPayload,
    PrecursorIndicator,
    SyntheticEmailAttackCasePayload,
)

from ._seed_data import (
    MALICIOUS_ATTACHMENT_BODIES,
    MALICIOUS_ATTACHMENT_KINDS,
    RECIPIENT_OPS,
)

RED_PROFILE_ID = "malicious_attachment_red_001"
ARCHETYPE = "malicious_attachment"

# Sender variants synthesizing different sandbox-safe sender hosts.
_SENDER_VARIANTS: tuple[str, ...] = (
    "delivery-notify.example",
    "ops-team.example",
    "alerts-hub.test",
    "logistics-portal.example",
    "shipping-updates.test",
    "secure-docs.example",
    "vendor-portal.example",
    "purchase-orders.test",
)


# Map attachment kind -> the single PrecursorIndicator the
# ``attachment_classifier`` detector emits for it (one-to-one).
_INDICATOR_FOR_KIND: dict[str, PrecursorIndicator] = {
    "executable": "executable_attachment",
    "iso_image": "iso_or_disk_image_attachment",
    "macro_office": "macro_enabled_office_document",
    "double_extension": "double_extension_attachment",
    "encrypted_archive": "encrypted_archive_attachment",
    "html_smuggling": "html_smuggling_attachment",
    "vhd_image": "iso_or_disk_image_attachment",
}

_BASELINE = datetime(2026, 7, 1, 14, 0, tzinfo=timezone.utc)


def generate_cases(
    *,
    seed: int = 0,
    count: int = 100,
) -> list[SyntheticEmailAttackCasePayload]:
    """Generate ``count`` deterministic malicious-attachment cases."""

    if count < 1:
        raise ValueError("count must be >= 1")

    cross_product: list[tuple[int, tuple[str, str, str, str], str, str]] = []
    for k_idx, kind_tuple in enumerate(MALICIOUS_ATTACHMENT_KINDS):
        for s_idx, sender_host in enumerate(_SENDER_VARIANTS):
            for b_idx, body_fragment in enumerate(MALICIOUS_ATTACHMENT_BODIES):
                cross_product.append((k_idx, kind_tuple, sender_host, body_fragment))

    if count > len(cross_product):
        raise ValueError(
            f"count {count} exceeds maximum cross-product size {len(cross_product)}"
        )

    cases: list[SyntheticEmailAttackCasePayload] = []
    for i in range(count):
        idx = (seed + i) % len(cross_product)
        k_idx, (kind, filename, content_type, attachment_class), sender_host, body_fragment = (
            cross_product[idx]
        )

        sender = f"notifications@{sender_host}"
        case_id = f"malicious-attachment-{kind}-{k_idx}-{i:03d}"
        attachment = EmailAttachmentMeta(
            filename=filename,
            content_type=content_type,
            size_bytes=72_400 + i,
            attachment_class=attachment_class,  # type: ignore[arg-type]
        )
        body = (
            f"Hello,\n\n{body_fragment} The attached file ({filename}) "
            f"contains the latest documents.\n\n"
            f"Best,\nOperations"
        )

        inbound = EmailInboundPayload(
            received_at=_BASELINE,
            sender=sender,
            recipient=RECIPIENT_OPS,
            subject="Documents attached for your review",
            body_plain=body,
            attachments=[attachment],
        )

        cases.append(
            SyntheticEmailAttackCasePayload(
                case_id=case_id,
                red_profile_id=RED_PROFILE_ID,
                archetype=ARCHETYPE,
                attack_pattern=f"malicious_attachment:{kind}",
                inbound=inbound,
                case_tags=(),
                expected_min_risk_score=70,
                expected_recommended_actions=("needs_review", "block"),
                expected_behavioral_flags=(),
                expected_precursor_indicators=(_INDICATOR_FOR_KIND[kind],),
                expects_precursor_block=True,
            )
        )

    return cases


def case_universe_size() -> int:
    return (
        len(MALICIOUS_ATTACHMENT_KINDS)
        * len(_SENDER_VARIANTS)
        * len(MALICIOUS_ATTACHMENT_BODIES)
    )


__all__ = [
    "ARCHETYPE",
    "RED_PROFILE_ID",
    "case_universe_size",
    "generate_cases",
]
