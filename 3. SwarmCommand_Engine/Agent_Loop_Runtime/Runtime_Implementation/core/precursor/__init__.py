"""NorthStar Inbox Shield — Phase 1.2 ransomware precursor detection.

This module collects the deterministic ransomware-precursor detectors landed
under Month 3 of the 12-month specialization roadmap. The detectors
explicitly do NOT execute attachment content or fetch URLs — everything is
static analysis over the inbound email metadata and body text.

Public surface:

- ``score_attachment_risk(meta) -> AttachmentRiskAssessment`` and
  ``classify_attachment(meta) -> AttachmentClass`` for per-attachment
  scoring (``attachment_classifier``).
- ``attachment_inspector(body_bytes, meta) -> EmailAttachmentMeta`` for use
  as the ingest-path ``AttachmentInspector`` callable.
- ``extract_urls(text)`` and
  ``score_url_obfuscation(*texts) -> UrlRiskAssessment`` for URL parsing /
  obfuscation scoring (``url_obfuscation_detector``).
- ``score_credential_harvesting(*texts)`` and
  ``score_mfa_fatigue(*texts)`` for body-language signal scoring
  (``body_signal_detector``).
- ``build_precursor_overlay(payload) -> PrecursorOverlay`` for the unified
  per-email overlay the scoring agent consumes (``analysis``).

The schema types (``EmailAnalysisRansomwarePrecursorAnalysis``,
``PrecursorIndicator``) live in ``core/blackboard/models.py`` and are
re-exported from ``core.blackboard`` directly.
"""

from .analysis import PrecursorOverlay, build_precursor_overlay
from .attachment_classifier import (
    AttachmentRiskAssessment,
    attachment_inspector,
    classify_attachment,
    score_attachment_risk,
)
from .body_signal_detector import (
    BodySignalAssessment,
    score_credential_harvesting,
    score_mfa_fatigue,
)
from .url_obfuscation_detector import (
    UrlRiskAssessment,
    extract_urls,
    score_url_obfuscation,
)

__all__ = [
    "AttachmentRiskAssessment",
    "BodySignalAssessment",
    "PrecursorOverlay",
    "UrlRiskAssessment",
    "attachment_inspector",
    "build_precursor_overlay",
    "classify_attachment",
    "extract_urls",
    "score_attachment_risk",
    "score_credential_harvesting",
    "score_mfa_fatigue",
    "score_url_obfuscation",
]
