from __future__ import annotations

from .base import BaseShadowWatcher
from .observation import CandidateAlarmFact, ShadowEmailEvent, ShadowWatcherKind, fact, inference


class SenderShadowWatcher(BaseShadowWatcher):
    WATCHER_ID = "sender_shadow_watcher"
    KIND = ShadowWatcherKind.SENDER

    def observe(self, event: ShadowEmailEvent):
        facts = []
        inferences = []
        alarms = []
        evidence_used = []

        if event.sender_domain:
            facts.append(fact("sender_domain", event.sender_domain, "sender_domain"))
            alarms.append(CandidateAlarmFact.SENDER_DOMAIN_OBSERVED)
            evidence_used.append("sender_domain")

        if event.reply_to_domain:
            facts.append(fact("reply_to_domain", event.reply_to_domain, "reply_to_domain"))
            evidence_used.append("reply_to_domain")
            if event.sender_domain and event.reply_to_domain != event.sender_domain:
                alarms.append(CandidateAlarmFact.REPLY_TO_DOMAIN_DRIFT)
                inferences.append(
                    inference(
                        "reply_to_domain_drift",
                        "reply-to domain differs from sender domain; alarm-input fact only",
                    )
                )

        return self._record(
            event,
            observed_facts=tuple(facts),
            inferences=tuple(inferences),
            evidence_used=tuple(evidence_used),
            candidate_alarm_facts=tuple(alarms),
            confidence=0.7 if alarms else 0.2,
        )


__all__ = ["SenderShadowWatcher"]
