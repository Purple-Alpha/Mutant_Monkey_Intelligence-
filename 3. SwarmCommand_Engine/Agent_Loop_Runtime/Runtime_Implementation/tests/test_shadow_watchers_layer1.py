"""Shadow Watcher Swarm Layer 1 tests.

Contract: ``Shadow_Watcher_Swarm_Contract.md`` §11 SIGNED, Layer 1 Watch Layer.
Three classes:
  Class 1 — expected pass
  Class 2 — adversarial boundaries
  Class 3 — known-gap xfails
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.orchestrator import AgentClass
from core.shadow_watchers import (
    AttachmentShadowWatcher,
    CandidateAlarmFact,
    GeoShadowWatcher,
    LanguageShadowWatcher,
    PaymentShadowWatcher,
    SenderShadowWatcher,
    ShadowAttachment,
    ShadowEmailEvent,
    ShadowObservationLog,
    ShadowObservationRecord,
    ShadowWatcherBoundaryError,
    ShadowWatcherKind,
    VendorHistoryShadowWatcher,
)

TENANT = "tenant_a"
EMAIL = "email_a"
SENTINEL = "SENTINEL_RAW_TEXT_SHADOW_WATCHER"


def _event() -> ShadowEmailEvent:
    return ShadowEmailEvent(
        tenant_id=TENANT,
        email_id=EMAIL,
        sender_domain="vendor.example",
        reply_to_domain="reply.example",
        payment_destinations=("bank-route-1",),
        invoice_template_id="invoice-template-a",
        body_text=f"Urgent and confidential request. {SENTINEL}",
        attachments=(
            ShadowAttachment(
                filename="invoice.pdf",
                sha256="a" * 64,
                extension=".pdf",
                pdf_fingerprint="pdf-fp-1",
            ),
        ),
        ip_country="RU",
        account_home_country="US",
        asn="AS64500",
        vendor_domain="vendor.example",
        vendor_known=False,
        prior_vendor_interactions=0,
        verification_failures=2,
    )


def _watchers(log: ShadowObservationLog):
    return (
        SenderShadowWatcher(log=log),
        PaymentShadowWatcher(log=log),
        LanguageShadowWatcher(log=log),
        AttachmentShadowWatcher(log=log),
        GeoShadowWatcher(log=log),
        VendorHistoryShadowWatcher(log=log),
    )


class TestShadowWatchersExpectedPass:
    def test_all_six_watchers_emit_structured_alarm_input(self):
        log = ShadowObservationLog()
        records = tuple(w.observe(_event()) for w in _watchers(log))

        assert len(records) == 6
        assert log.entries() == records
        assert {r.watcher_kind for r in records} == {
            ShadowWatcherKind.SENDER,
            ShadowWatcherKind.PAYMENT,
            ShadowWatcherKind.LANGUAGE,
            ShadowWatcherKind.ATTACHMENT,
            ShadowWatcherKind.GEO,
            ShadowWatcherKind.VENDOR_HISTORY,
        }
        assert all(r.tenant_id == TENANT and r.email_id == EMAIL for r in records)
        assert all(r.raw_text_present is False for r in records)
        assert all(r.confidence >= 0.0 for r in records)

    def test_candidate_alarm_facts_are_layer1_only(self):
        log = ShadowObservationLog()
        records = tuple(w.observe(_event()) for w in _watchers(log))
        facts = {fact for record in records for fact in record.candidate_alarm_facts}

        assert CandidateAlarmFact.REPLY_TO_DOMAIN_DRIFT in facts
        assert CandidateAlarmFact.PAYMENT_DESTINATION_PRESENT in facts
        assert CandidateAlarmFact.URGENCY_PRESSURE_LANGUAGE in facts
        assert CandidateAlarmFact.ATTACHMENT_HASH_PRESENT in facts
        assert CandidateAlarmFact.GEO_COUNTRY_DRIFT in facts
        assert CandidateAlarmFact.VERIFICATION_FAILURE_HISTORY in facts

    def test_raw_body_is_seen_but_not_emitted(self):
        record = LanguageShadowWatcher().observe(_event())
        dumped = record.model_dump_json()

        assert SENTINEL not in dumped
        assert "Urgent and confidential request" not in dumped
        assert "body_text:urgency_pattern" in dumped
        assert "body_text:secrecy_pattern" in dumped

    def test_append_only_log_has_no_update_or_delete_api(self):
        log = ShadowObservationLog()
        SenderShadowWatcher(log=log).observe(_event())

        assert len(log.entries()) == 1
        assert not hasattr(log, "delete")
        assert not hasattr(log, "update")
        assert not hasattr(log, "remove")


class TestShadowWatchersAdversarial:
    def test_q_class_no_tools_no_credentials(self):
        watcher = SenderShadowWatcher()

        assert watcher.agent_class is AgentClass.Q_CLASS
        assert watcher.tool_scope == frozenset()
        assert watcher.credentials == frozenset()

        with pytest.raises(ShadowWatcherBoundaryError, match="cannot request tools"):
            watcher.request_tool("canary")
        with pytest.raises(ShadowWatcherBoundaryError, match="cannot hold credentials"):
            watcher.add_credential("secret")

    def test_no_blackboard_no_block_no_verdict_no_recommendation(self):
        watcher = PaymentShadowWatcher()

        with pytest.raises(ShadowWatcherBoundaryError, match="do not write"):
            watcher.write_blackboard()
        with pytest.raises(ShadowWatcherBoundaryError, match="never block"):
            watcher.block_action()
        with pytest.raises(ShadowWatcherBoundaryError, match="never make final fraud"):
            watcher.make_final_fraud_claim()
        with pytest.raises(ShadowWatcherBoundaryError, match="no recommendations"):
            watcher.make_recommendation()

    def test_observation_schema_rejects_action_or_verdict_language(self):
        with pytest.raises(ValidationError):
            ShadowObservationRecord(
                watcher_id="bad",
                watcher_kind=ShadowWatcherKind.SENDER,
                tenant_id=TENANT,
                email_id=EMAIL,
                evidence_used=("recommended_action:block",),
                confidence=0.5,
            )

    def test_observation_schema_rejects_raw_text_marker(self):
        with pytest.raises(ValidationError, match="raw text"):
            ShadowObservationRecord(
                watcher_id="bad",
                watcher_kind=ShadowWatcherKind.LANGUAGE,
                tenant_id=TENANT,
                email_id=EMAIL,
                raw_text_present=True,
                confidence=0.5,
            )

    def test_no_external_or_active_surfaces_exist_on_watchers(self):
        watcher = AttachmentShadowWatcher()
        for forbidden in (
            "scan_infrastructure",
            "submit_abuse_report",
            "execute_attachment",
            "call_external_api",
            "identify_person",
        ):
            assert not hasattr(watcher, forbidden)


class TestShadowWatchersKnownGap:
    @pytest.mark.xfail(
        reason=(
            "Live mailbox integration is separately gated by Shadow Watcher §2/§10. "
            "Completion path: signed live-mailbox integration contract."
        ),
        strict=True,
    )
    def test_xfail_live_mailbox_integration(self):
        raise AssertionError("not implemented — live mailbox integration gated")

    @pytest.mark.xfail(
        reason=(
            "Payment-system integration is separately gated; Layer 1 observes only "
            "synthetic payment indicators. Completion path: signed payment integration contract."
        ),
        strict=True,
    )
    def test_xfail_live_payment_system_integration(self):
        raise AssertionError("not implemented — live payment integration gated")

    @pytest.mark.xfail(
        reason=(
            "External enrichment / active scanning is expressly not authorized by "
            "this Layer 1 build. Completion path: separate signed enrichment contract."
        ),
        strict=True,
    )
    def test_xfail_external_enrichment_or_active_scanning(self):
        raise AssertionError("not implemented — external enrichment gated")

    @pytest.mark.xfail(
        reason=(
            "Attachment execution/sandboxing beyond metadata observation is separately "
            "gated by §2/§10. Completion path: signed sandbox execution scope."
        ),
        strict=True,
    )
    def test_xfail_attachment_execution_sandboxing(self):
        raise AssertionError("not implemented — attachment execution gated")
