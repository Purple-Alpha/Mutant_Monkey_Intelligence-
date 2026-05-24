"""NorthStar Inbox Shield — Phase 1.2 sandbox-safe attachment classifier.

Static, **non-executing** classifier that turns the metadata on an
``EmailAttachmentMeta`` (filename, content type, size, optional sha256, optional
``body_bytes`` from the ingest hook) into a refined ``attachment_class`` plus a
0–100 ransomware ``attachment_risk_score`` and the list of
``PrecursorIndicator`` values it justifies.

Hard guardrail from Phase 1.2 deep dive §3 and the 12-month roadmap Month 3
risk/dependency note: **attachment inspection must stay sandbox-safe — under
no circumstances does the inspector execute attachment content. Static
analysis only.**

This module is the Phase 1.2 implementation of:
- the ``AttachmentInspector`` callable contract declared at
  ``core/ingest/email_ingest_agent.py`` (so it plugs into the existing
  Month 1.5 ingest hook); and
- a separate ``score_attachment_risk`` function used by the precursor overlay
  (``core/precursor/analysis.py``) at scoring time.

Both entry points are deterministic and pure: same inputs -> same outputs,
no I/O, no subprocess, no exec, no eval.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from core.blackboard import (
    AttachmentClass,
    EmailAttachmentMeta,
    PrecursorIndicator,
)

# Filename extensions that strongly indicate a directly-executable or
# script-bearing payload. Kept conservative; expanding this set requires a
# documented justification because it directly raises ``attachment_risk_score``.
EXECUTABLE_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".exe",
        ".scr",
        ".bat",
        ".cmd",
        ".com",
        ".cpl",
        ".msi",
        ".msp",
        ".ps1",
        ".vbs",
        ".vbe",
        ".js",
        ".jse",
        ".wsf",
        ".wsh",
        ".hta",
        ".jar",
        ".lnk",
        ".pif",
    }
)

# Macro-enabled Office formats. Document formats that cannot carry macros
# (``.docx``, ``.xlsx``, ``.pptx``) are intentionally excluded.
MACRO_OFFICE_EXTENSIONS: frozenset[str] = frozenset(
    {".docm", ".xlsm", ".xlsb", ".pptm", ".dotm", ".xltm", ".potm"}
)

# Container formats commonly used to bypass mark-of-the-web checks. ISO/IMG
# in particular has been a dominant ransomware initial-access vector since
# 2022 (Qakbot, IcedID, etc.).
DISK_IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {".iso", ".img", ".vhd", ".vhdx"}
)

ARCHIVE_EXTENSIONS: frozenset[str] = frozenset(
    {".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz", ".tgz"}
)

HTML_SMUGGLING_EXTENSIONS: frozenset[str] = frozenset({".html", ".htm", ".svg"})

# Filename token that is a near-universal sign of "encrypted archive — open with
# this password" social engineering. Detected as a substring (case-insensitive)
# on the filename, not the body, because the filename naming convention is
# itself the signal.
ENCRYPTED_ARCHIVE_HINT = re.compile(
    r"(?i)(invoice|payment|remittance|statement|wire|aging)[-_ ]?(protected|secure|encrypted|password)"
)


@dataclass(frozen=True)
class AttachmentRiskAssessment:
    """One attachment's deterministic ransomware-precursor risk assessment.

    ``classification`` is the refined ``AttachmentClass`` the classifier picked
    (may differ from ``meta.attachment_class`` if the input was ``"unknown"``).
    ``risk_score`` is the per-attachment 0–100 score before aggregation.
    ``indicators`` is the list of ``PrecursorIndicator`` values this attachment
    contributed. The overlay layer aggregates per-email max across attachments.
    """

    classification: AttachmentClass
    risk_score: int
    indicators: tuple[PrecursorIndicator, ...]


def attachment_inspector(
    body_bytes: bytes | None, meta: EmailAttachmentMeta
) -> EmailAttachmentMeta:
    """``AttachmentInspector`` implementation for the ingest hook.

    Refines ``attachment_class`` when the inbound dict left it at ``"unknown"``
    (or another non-specific value the connector could not determine). Never
    rewrites a classifier-friendly value the connector already chose
    confidently (caller intent wins).

    Does not touch ``extracted_text`` (that requires format-aware parsing not
    in Phase 1.2 scope) or ``sha256`` (handled by the existing
    ``sha256_attachment_inspector`` reference implementation in
    ``core/ingest/email_ingest_agent.py``).

    Returned ``EmailAttachmentMeta`` is always re-validated by the ingest
    layer; this function returns a ``model_copy`` so the original is never
    mutated.
    """

    if meta.attachment_class != "unknown":
        return meta

    refined = _refine_attachment_class(meta)
    if refined == "unknown":
        return meta
    return meta.model_copy(update={"attachment_class": refined})


def classify_attachment(meta: EmailAttachmentMeta) -> AttachmentClass:
    """Return the refined ``AttachmentClass`` for one attachment.

    Pure function over ``EmailAttachmentMeta``; safe to call from any layer.
    """

    if meta.attachment_class != "unknown":
        return meta.attachment_class
    return _refine_attachment_class(meta)


def score_attachment_risk(meta: EmailAttachmentMeta) -> AttachmentRiskAssessment:
    """Score one attachment's ransomware-precursor risk.

    Score bands:
    - ``0-20``: routine business attachment (invoice / payment request / unknown
      benign).
    - ``21-50``: container or archive that COULD carry a payload but has no
      explicit malicious indicator on its own.
    - ``51-80``: macro-enabled Office document, encrypted-archive social-
      engineering filename pattern, or HTML-smuggling-capable file.
    - ``81-100``: directly executable filename, ISO / IMG disk image, or
      double-extension filename (e.g. ``invoice.pdf.exe``).

    Indicator emission is one-to-one with the bands above. ``risk_score`` is
    the **max** of the matched-band contributions, never additive across bands
    on the same attachment; aggregation across attachments happens one layer
    up in the overlay.
    """

    classification = classify_attachment(meta)
    filename_lower = (meta.filename or "").lower()
    indicators: list[PrecursorIndicator] = []
    score = 0

    if _has_double_extension(filename_lower):
        indicators.append("double_extension_attachment")
        score = max(score, 90)

    if _has_extension(filename_lower, EXECUTABLE_EXTENSIONS):
        indicators.append("executable_attachment")
        score = max(score, 85)
        classification = "executable_doc"

    if _has_extension(filename_lower, DISK_IMAGE_EXTENSIONS):
        indicators.append("iso_or_disk_image_attachment")
        score = max(score, 85)
        classification = "payload_carrier"

    if _has_extension(filename_lower, MACRO_OFFICE_EXTENSIONS):
        indicators.append("macro_enabled_office_document")
        score = max(score, 65)
        classification = "payload_carrier"

    if _has_extension(filename_lower, HTML_SMUGGLING_EXTENSIONS):
        indicators.append("html_smuggling_attachment")
        score = max(score, 60)
        if classification == "unknown":
            classification = "payload_carrier"

    if _has_extension(filename_lower, ARCHIVE_EXTENSIONS) and (
        ENCRYPTED_ARCHIVE_HINT.search(filename_lower) is not None
    ):
        indicators.append("encrypted_archive_attachment")
        score = max(score, 65)
        classification = "payload_carrier"

    if classification == "credential_lure" and score == 0:
        score = 40

    if classification in ("invoice", "payment_request") and score == 0:
        score = 10

    return AttachmentRiskAssessment(
        classification=classification,
        risk_score=min(score, 100),
        indicators=tuple(indicators),
    )


def _refine_attachment_class(meta: EmailAttachmentMeta) -> AttachmentClass:
    filename_lower = (meta.filename or "").lower()
    if _has_extension(filename_lower, EXECUTABLE_EXTENSIONS):
        return "executable_doc"
    if _has_extension(filename_lower, DISK_IMAGE_EXTENSIONS):
        return "payload_carrier"
    if _has_extension(filename_lower, MACRO_OFFICE_EXTENSIONS):
        return "payload_carrier"
    if _has_extension(filename_lower, HTML_SMUGGLING_EXTENSIONS):
        return "payload_carrier"
    if (
        _has_extension(filename_lower, ARCHIVE_EXTENSIONS)
        and ENCRYPTED_ARCHIVE_HINT.search(filename_lower) is not None
    ):
        return "payload_carrier"
    return "unknown"


def _has_extension(filename_lower: str, extensions: Iterable[str]) -> bool:
    return any(filename_lower.endswith(ext) for ext in extensions)


def _has_double_extension(filename_lower: str) -> bool:
    """True when the filename ends with a dangerous extension preceded by a
    safe-looking one (e.g. ``invoice.pdf.exe``, ``statement.docx.scr``).

    Filenames with three or more dot segments where the LAST is in
    ``EXECUTABLE_EXTENSIONS`` and the SECOND-TO-LAST starts with a letter
    (i.e. looks like a real extension, not a version number) count as a
    double-extension pattern.
    """

    if "." not in filename_lower:
        return False
    parts = filename_lower.rsplit(".", 2)
    if len(parts) < 3:
        return False
    second_last_segment, last_segment = parts[1], parts[2]
    if not second_last_segment.isalpha():
        return False
    return f".{last_segment}" in EXECUTABLE_EXTENSIONS
