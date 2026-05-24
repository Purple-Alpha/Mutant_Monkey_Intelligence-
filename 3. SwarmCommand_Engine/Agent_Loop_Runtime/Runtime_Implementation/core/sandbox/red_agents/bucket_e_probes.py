"""Phase 1.3 Bucket E mirror cases (``bucket_e_regression_probe``).

Matt's 2026-05-21 §11 decision 5: surface the four Month 2 Bucket E
honest gaps (``vf-002``, ``vf-005``, ``ei-005``, ``wt-004``) inside
the Phase 1.3 Red battery so Month 5 mutation work has a typed,
seeded place to target them.

Each mirror case is tagged ``bucket_e_regression_probe`` so weakness
reports and downstream consumers can filter and prioritise them
without crawling the JSONL by hand. The mirrors are intentionally
**not** included in the main Red profile cross-products: profile
generators stay byte-deterministic in their own right, and the
mirror set is short and operator-curated.

Distribution across archetypes:
- ``vf-002`` (first-time-sender + invoice + remit-to in attachment) ->
  ``fake_invoice``
- ``vf-005`` (large-dollar emergency invoice + urgency) ->
  ``fake_invoice``
- ``ei-005`` (CFO impersonation w/ Reply-To divergence) ->
  ``vendor_update_pivot``
- ``wt-004`` (terse wire-deposit ask w/ no specifics) ->
  ``vendor_update_pivot``
"""

from __future__ import annotations

from datetime import datetime, timezone

from core.blackboard import (
    EmailAttachmentMeta,
    EmailInboundPayload,
    SyntheticEmailAttackCasePayload,
)

_BASELINE = datetime(2026, 6, 15, 10, 5, tzinfo=timezone.utc)


def generate_bucket_e_probes() -> list[SyntheticEmailAttackCasePayload]:
    """Return the four typed Bucket E mirror cases.

    Each case carries ``case_tags=("bucket_e_regression_probe",)``
    plus the per-archetype expectations the original Bucket E case
    held. The expectations are intentionally tight (matching the
    original gate-pass rows) so failures clearly indicate continuing
    Blue gaps for those patterns.
    """

    return [
        # vf-002 mirror: first-time vendor invoice with new remittance in PDF
        SyntheticEmailAttackCasePayload(
            case_id="bucket-e-vf-002-mirror",
            red_profile_id="fake_invoice_red_001",
            archetype="fake_invoice",
            attack_pattern="fake_invoice:bucket_e_vf_002_mirror",
            inbound=EmailInboundPayload(
                received_at=_BASELINE,
                sender="billing@trusted-vendor-payments.example",
                recipient="ap@northstar-customer.example",
                subject="Invoice 8821 - remittance details attached",
                body_plain=(
                    "Good morning,\n\n"
                    "We are sending our first invoice after onboarding. Please use the "
                    "remittance instructions on the attached PDF for this payment.\n\n"
                    "Regards,\nTrusted Vendor Billing"
                ),
                attachments=[
                    EmailAttachmentMeta(
                        filename="invoice_8821.pdf",
                        content_type="application/pdf",
                        size_bytes=119_233,
                        attachment_class="invoice",
                        extracted_text=(
                            "Trusted Vendor invoice 8821. Total due $18,240. "
                            "Please remit to the account details on this page."
                        ),
                    )
                ],
            ),
            case_tags=("bucket_e_regression_probe",),
            expected_min_risk_score=60,
            expected_recommended_actions=("needs_review", "block"),
            expected_behavioral_flags=("first_time_sender_with_financial_ask",),
            expects_precursor_block=True,
        ),
        # vf-005 mirror: large-dollar emergency invoice w/ urgency
        SyntheticEmailAttackCasePayload(
            case_id="bucket-e-vf-005-mirror",
            red_profile_id="fake_invoice_red_001",
            archetype="fake_invoice",
            attack_pattern="fake_invoice:bucket_e_vf_005_mirror",
            inbound=EmailInboundPayload(
                received_at=_BASELINE,
                sender="emergency-parts@pacific-logistics.example",
                recipient="ap@northstar-customer.example",
                subject="High-value emergency parts invoice - approve before EOD",
                body_plain=(
                    "Hi finance,\n\n"
                    "This invoice is larger than our usual monthly order because it "
                    "covers emergency replacement parts. Please approve the attached "
                    "$96,400 invoice before end of day so the shipment is not delayed.\n\n"
                    "Regards,\nPacific Logistics"
                ),
                attachments=[
                    EmailAttachmentMeta(
                        filename="emergency_parts_invoice_96400.pdf",
                        content_type="application/pdf",
                        size_bytes=184_220,
                        attachment_class="invoice",
                        extracted_text=(
                            "Pacific Logistics emergency parts invoice. Total due $96,400. "
                            "Approval requested before end of day."
                        ),
                    )
                ],
            ),
            case_tags=("bucket_e_regression_probe",),
            expected_min_risk_score=75,
            expected_recommended_actions=("needs_review", "block"),
            expected_behavioral_flags=(
                "unusual_dollar_amount",
                "urgency_paired_with_finance",
            ),
            expects_precursor_block=True,
        ),
        # ei-005 mirror: CFO impersonation w/ Reply-To divergence
        SyntheticEmailAttackCasePayload(
            case_id="bucket-e-ei-005-mirror",
            red_profile_id="vendor_update_red_001",
            archetype="vendor_update_pivot",
            attack_pattern="vendor_update_pivot:bucket_e_ei_005_mirror",
            inbound=EmailInboundPayload(
                received_at=_BASELINE,
                sender="cfo@northstar-customer.example",
                recipient="finance@northstar-customer.example",
                subject="Vendor payment approval",
                body_plain=(
                    "Approved - send the funds for the vendor payment today and "
                    "confirm by reply."
                ),
                headers={
                    "Reply-To": "cfo.finance.approvals@gmail.example",
                    "Return-Path": "bounce@mailer.example",
                },
            ),
            case_tags=("bucket_e_regression_probe",),
            expected_min_risk_score=80,
            expected_recommended_actions=("block",),
            expected_behavioral_flags=(
                "reply_to_diverges_from_from",
                "urgency_paired_with_finance",
            ),
            expects_precursor_block=True,
        ),
        # wt-004 mirror: terse wire-deposit ask
        SyntheticEmailAttackCasePayload(
            case_id="bucket-e-wt-004-mirror",
            red_profile_id="vendor_update_red_001",
            archetype="vendor_update_pivot",
            attack_pattern="vendor_update_pivot:bucket_e_wt_004_mirror",
            inbound=EmailInboundPayload(
                received_at=_BASELINE,
                sender="deposits@project-partner.example",
                recipient="finance@northstar-customer.example",
                subject="Deposit wire this week",
                body_plain=(
                    "Can you wire the $18,000 project deposit this week? We can "
                    "send final routing details once you confirm the payment window."
                ),
            ),
            case_tags=("bucket_e_regression_probe",),
            expected_min_risk_score=45,
            expected_max_risk_score=75,
            expected_recommended_actions=("needs_review",),
            expected_behavioral_flags=(),
            expects_precursor_block=True,
        ),
    ]


__all__ = ["generate_bucket_e_probes"]
