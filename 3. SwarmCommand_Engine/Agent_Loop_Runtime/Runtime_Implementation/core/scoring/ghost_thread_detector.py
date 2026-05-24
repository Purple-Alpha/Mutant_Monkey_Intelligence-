"""NorthStar Inbox Shield — Ghost-thread detector.

Pure-function deterministic detector for fake email-thread continuity. A
ghost thread is an inbound email whose subject claims to be part of an
existing conversation (``Re:``, ``Fwd:`` prefixes) but whose RFC 5322
threading headers (``In-Reply-To:``, ``References:``) are missing or
empty — i.e. there is no actual prior message on the wire that this email
is replying to.

Why it matters for fraud:

Ghost threading is one of the highest-conversion BEC patterns. An attacker
crafts an email titled ``Re: Vendor invoice approval`` and sends it cold
into a bookkeeper's inbox. The recipient skim-reads the subject, assumes
this is part of a thread they participated in earlier, and treats the
payment-change request inside as a known follow-up. Modern mail clients
visually group messages by ``In-Reply-To`` / ``References`` headers, not
by subject line — so the absence of those headers is the deterministic
giveaway, even when the subject is convincingly threaded.

What this detector does NOT do (v0 scope):

- Does not parse the body for "following up as discussed" / "per our
  previous email" language without quoted history. That is a body-signal
  detector and lives separately.
- Does not validate the ``Message-ID`` referenced by ``In-Reply-To``
  against the recipient's mailbox. That requires per-tenant state.
- Does not detect ghost-fwd patterns where forwarding headers are
  manufactured. v0 trusts ``References:`` if present.

The function is pure: no I/O, no network, no LLM call. Safe to run
unconditionally on every scored email; emails with no Re:/Fwd: prefix
or with valid threading headers get a score of 0.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping


_THREADING_SUBJECT_RE = re.compile(
    r"^\s*(?:re|fw|fwd)\s*(?:\[\d+\])?\s*:",
    re.IGNORECASE,
)

# Score band tuned so:
# - Ghost-thread alone lands in needs_review territory (>= 50) but well
#   below auto-block (>= 80). Subject-line spoofing alone is rarely
#   sufficient evidence to refuse a real vendor email; we want a human or
#   an LLM signal to confirm.
# - Lower than Reply-To divergence (65) because legitimate broken mail
#   clients do still occasionally drop threading headers when forwarding
#   through web interfaces.
_SCORE_GHOST_THREAD = 55


@dataclass(frozen=True)
class GhostThreadAssessment:
    """One email's worth of ghost-thread findings.

    ``score`` is 0–100. Higher means stronger ghost-thread signal.
    ``indicators`` is a tuple of human-readable strings naming the detected
    pattern. Currently always either empty or ``("ghost_thread_subject",)``;
    future versions may add body-signal indicators.
    """

    score: int
    indicators: tuple[str, ...]


def score_ghost_thread(
    *,
    subject: str | None,
    headers: Mapping[str, str] | None = None,
) -> GhostThreadAssessment:
    """Detect ghost-thread continuity in an inbound email.

    A ghost thread fires when BOTH of the following are true:

    1. The subject begins with a threading prefix (``Re:``, ``Fwd:``,
       ``Fw:``, with optional whitespace and optional bracketed counter
       like ``Re[2]:``). Subjects without a threading prefix never fire
       this detector regardless of header state.
    2. Neither the ``In-Reply-To`` header nor the ``References`` header
       carries a non-empty value. Both headers are looked up
       case-insensitively to match RFC 5322 semantics. Whitespace-only
       values count as empty.

    Inputs:

    - ``subject``: ``EmailInboundPayload.subject``. Optional — a ``None``
      or empty subject can never threading-prefix-match, so the detector
      returns 0 immediately.
    - ``headers``: ``EmailInboundPayload.headers``. May be empty or
      ``None``.

    Returns a ``GhostThreadAssessment``.
    """

    if not subject or not _has_threading_prefix(subject):
        return GhostThreadAssessment(score=0, indicators=())

    if _has_non_empty_threading_header(headers):
        return GhostThreadAssessment(score=0, indicators=())

    return GhostThreadAssessment(
        score=_SCORE_GHOST_THREAD,
        indicators=("ghost_thread_subject",),
    )


def _has_threading_prefix(subject: str) -> bool:
    return _THREADING_SUBJECT_RE.match(subject) is not None


def _has_non_empty_threading_header(headers: Mapping[str, str] | None) -> bool:
    if not headers:
        return False

    for key, value in headers.items():
        if key.lower() in ("in-reply-to", "references"):
            if value and value.strip():
                return True
    return False
