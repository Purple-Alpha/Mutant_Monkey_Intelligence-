from __future__ import annotations

from .base import BaseShadowWatcher
from .observation import CandidateAlarmFact, ShadowEmailEvent, ShadowWatcherKind, fact


class PaymentShadowWatcher(BaseShadowWatcher):
    WATCHER_ID = "payment_shadow_watcher"
    KIND = ShadowWatcherKind.PAYMENT

    def observe(self, event: ShadowEmailEvent):
        facts = []
        alarms = []
        evidence_used = []

        for index, destination in enumerate(event.payment_destinations):
            facts.append(fact(f"payment_destination_{index}", destination, "payment_destinations"))
        if event.payment_destinations:
            alarms.append(CandidateAlarmFact.PAYMENT_DESTINATION_PRESENT)
            evidence_used.append("payment_destinations")

        if event.invoice_template_id:
            facts.append(fact("invoice_template_id", event.invoice_template_id, "invoice_template_id"))
            alarms.append(CandidateAlarmFact.INVOICE_TEMPLATE_PRESENT)
            evidence_used.append("invoice_template_id")

        return self._record(
            event,
            observed_facts=tuple(facts),
            inferences=(),
            evidence_used=tuple(evidence_used),
            candidate_alarm_facts=tuple(alarms),
            confidence=0.65 if alarms else 0.15,
        )


__all__ = ["PaymentShadowWatcher"]
