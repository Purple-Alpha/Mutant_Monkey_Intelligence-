from __future__ import annotations

from .base import BaseShadowWatcher
from .observation import CandidateAlarmFact, ShadowEmailEvent, ShadowWatcherKind, fact, inference

_URGENCY_TERMS = ("urgent", "today", "immediately", "asap", "right away")
_SECRECY_TERMS = ("confidential", "secret", "do not tell", "keep this between us")


class LanguageShadowWatcher(BaseShadowWatcher):
    WATCHER_ID = "language_shadow_watcher"
    KIND = ShadowWatcherKind.LANGUAGE

    def observe(self, event: ShadowEmailEvent):
        text = event.body_text.lower()
        urgency_hits = tuple(term for term in _URGENCY_TERMS if term in text)
        secrecy_hits = tuple(term for term in _SECRECY_TERMS if term in text)

        facts = []
        inferences = []
        alarms = []
        evidence_used = []

        if urgency_hits:
            facts.append(fact("urgency_term_count", len(urgency_hits), "body_text"))
            alarms.append(CandidateAlarmFact.URGENCY_PRESSURE_LANGUAGE)
            evidence_used.append("body_text:urgency_pattern")
            inferences.append(
                inference("urgency_pressure", "urgency-pattern terms are present; alarm-input only")
            )

        if secrecy_hits:
            facts.append(fact("secrecy_term_count", len(secrecy_hits), "body_text"))
            alarms.append(CandidateAlarmFact.SECRECY_PRESSURE_LANGUAGE)
            evidence_used.append("body_text:secrecy_pattern")
            inferences.append(
                inference("secrecy_pressure", "secrecy-pattern terms are present; alarm-input only")
            )

        return self._record(
            event,
            observed_facts=tuple(facts),
            inferences=tuple(inferences),
            evidence_used=tuple(evidence_used),
            candidate_alarm_facts=tuple(alarms),
            confidence=0.6 if alarms else 0.1,
        )


__all__ = ["LanguageShadowWatcher"]
