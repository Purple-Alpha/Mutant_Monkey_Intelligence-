from __future__ import annotations

from .base import BaseShadowWatcher
from .observation import CandidateAlarmFact, ShadowEmailEvent, ShadowWatcherKind, fact


class AttachmentShadowWatcher(BaseShadowWatcher):
    WATCHER_ID = "attachment_shadow_watcher"
    KIND = ShadowWatcherKind.ATTACHMENT

    def observe(self, event: ShadowEmailEvent):
        facts = []
        alarms = []
        evidence_used = []

        for index, attachment in enumerate(event.attachments):
            if attachment.sha256:
                facts.append(fact(f"attachment_hash_{index}", attachment.sha256, "attachments.sha256"))
                alarms.append(CandidateAlarmFact.ATTACHMENT_HASH_PRESENT)
            if attachment.pdf_fingerprint:
                facts.append(
                    fact(
                        f"pdf_fingerprint_{index}",
                        attachment.pdf_fingerprint,
                        "attachments.pdf_fingerprint",
                    )
                )
                alarms.append(CandidateAlarmFact.PDF_FINGERPRINT_PRESENT)

        if event.attachments:
            evidence_used.append("attachments:metadata_only")

        return self._record(
            event,
            observed_facts=tuple(facts),
            inferences=(),
            evidence_used=tuple(evidence_used),
            candidate_alarm_facts=tuple(dict.fromkeys(alarms)),
            confidence=0.65 if alarms else 0.1,
        )


__all__ = ["AttachmentShadowWatcher"]
