from __future__ import annotations

from .base import BaseShadowWatcher
from .observation import CandidateAlarmFact, ShadowEmailEvent, ShadowWatcherKind, fact, inference


class VendorHistoryShadowWatcher(BaseShadowWatcher):
    WATCHER_ID = "vendor_history_shadow_watcher"
    KIND = ShadowWatcherKind.VENDOR_HISTORY

    def observe(self, event: ShadowEmailEvent):
        facts = []
        inferences = []
        alarms = []
        evidence_used = []

        if event.vendor_domain:
            facts.append(fact("vendor_domain", event.vendor_domain, "vendor_domain"))
            evidence_used.append("vendor_domain")

        facts.append(fact("vendor_known", event.vendor_known, "vendor_known"))
        facts.append(
            fact(
                "prior_vendor_interactions",
                event.prior_vendor_interactions,
                "prior_vendor_interactions",
            )
        )
        evidence_used.extend(("vendor_known", "prior_vendor_interactions"))

        if event.vendor_known:
            alarms.append(CandidateAlarmFact.VENDOR_KNOWN)
        else:
            alarms.append(CandidateAlarmFact.VENDOR_NEW_OR_THIN_HISTORY)
            inferences.append(
                inference("vendor_new_or_thin_history", "vendor history is absent or thin")
            )

        if event.verification_failures:
            facts.append(
                fact("verification_failures", event.verification_failures, "verification_failures")
            )
            alarms.append(CandidateAlarmFact.VERIFICATION_FAILURE_HISTORY)
            evidence_used.append("verification_failures")

        return self._record(
            event,
            observed_facts=tuple(facts),
            inferences=tuple(inferences),
            evidence_used=tuple(dict.fromkeys(evidence_used)),
            candidate_alarm_facts=tuple(dict.fromkeys(alarms)),
            confidence=0.7 if event.verification_failures else 0.45,
        )


__all__ = ["VendorHistoryShadowWatcher"]
