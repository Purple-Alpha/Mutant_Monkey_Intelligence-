from __future__ import annotations

from .base import BaseShadowWatcher
from .observation import CandidateAlarmFact, ShadowEmailEvent, ShadowWatcherKind, fact, inference


class GeoShadowWatcher(BaseShadowWatcher):
    WATCHER_ID = "geo_shadow_watcher"
    KIND = ShadowWatcherKind.GEO

    def observe(self, event: ShadowEmailEvent):
        facts = []
        inferences = []
        alarms = []
        evidence_used = []

        if event.ip_country:
            facts.append(fact("ip_country", event.ip_country, "ip_country"))
            evidence_used.append("ip_country")

        if event.account_home_country:
            facts.append(fact("account_home_country", event.account_home_country, "account_home_country"))
            evidence_used.append("account_home_country")

        if event.ip_country and event.account_home_country and event.ip_country != event.account_home_country:
            alarms.append(CandidateAlarmFact.GEO_COUNTRY_DRIFT)
            inferences.append(
                inference(
                    "geo_country_drift",
                    "sending country differs from account home country; alarm-input fact only",
                )
            )

        if event.asn:
            facts.append(fact("asn", event.asn, "asn"))
            alarms.append(CandidateAlarmFact.ASN_OBSERVED)
            evidence_used.append("asn")

        return self._record(
            event,
            observed_facts=tuple(facts),
            inferences=tuple(inferences),
            evidence_used=tuple(dict.fromkeys(evidence_used)),
            candidate_alarm_facts=tuple(alarms),
            confidence=0.7 if alarms else 0.15,
        )


__all__ = ["GeoShadowWatcher"]
