"""NorthStar Inbox Shield — From / Reply-To / Return-Path divergence detector.

Pure-function deterministic detector for one of the strongest single-signal
BEC (Business Email Compromise) indicators: the sender's identity headers
do not line up.

Three header pairs are inspected:

- ``From:`` vs ``Reply-To:`` — a reply would route to a different domain than
  the apparent sender. Classic vendor-impersonation pattern: attacker spoofs
  a real vendor's address but routes the conversation to an attacker-controlled
  reply mailbox.
- ``From:`` vs ``Return-Path:`` — bounces would route to a different domain.
  Legitimate ESPs (Mailchimp, SendGrid, Constant Contact, etc.) frequently
  produce this kind of divergence on purpose, so the score for this signal
  alone is moderate, not high. Combined with a Reply-To divergence it is a
  much stronger BEC indicator.
- ``From:`` vs ``Sender:`` — RFC 5322 ``Sender:`` header set to a different
  identity than ``From:``. This is the lowest-confidence divergence signal
  (legitimate mailing-list software does this) and only contributes when the
  domains differ at the root.

Domain comparison is done on the **root domain** (eTLD+1 heuristic — last
two labels of the domain, lowercased). ``mail.vendor.com`` vs ``vendor.com``
does NOT count as divergence (legit subdomain). ``vendor.com`` vs
``vendor.co`` does count (different TLDs — classic homograph attack pattern).

The function is pure: no I/O, no network, no LLM call. Safe to run
unconditionally on every scored email; emails with no headers or no
divergence get a score of 0 and an empty indicator tuple.

This detector intentionally does NOT mutate ``EmailAnalysisRiskAnalysis``
or write to ``behavioral_deviation_flags``. It produces a deterministic
score that is consumed by ``core/scoring/email_risk_scoring_agent.py``
and merged into ``recommended_risk_floor`` alongside the ransomware
precursor sub-scores. The lift-only invariant is preserved end-to-end.
"""

from __future__ import annotations

from dataclasses import dataclass
from email.utils import parseaddr
from typing import Mapping


# Score band for each individual divergence kind. Tuned so that:
# - Reply-To divergence alone is enough to push a benign-looking email into
#   the "needs_review" band (>= 50) but not auto-block (>= 80).
# - Return-Path divergence alone is moderate, because legitimate ESPs
#   commonly produce it (e.g. Mailchimp bounces to bounce@<esp-domain>).
# - Sender header divergence alone is the lowest-confidence signal.
# - When multiple divergences fire together, the score is the max of the
#   individual scores plus a small combination bump, capped at 90 so the
#   detector alone cannot force the risk_score to 100.
_SCORE_REPLY_TO_DIVERGENCE = 65
_SCORE_RETURN_PATH_DIVERGENCE = 45
_SCORE_SENDER_HEADER_DIVERGENCE = 35
_COMBINATION_BUMP = 10
_MAX_SCORE = 90


@dataclass(frozen=True)
class HeaderDivergenceAssessment:
    """One email's worth of From / Reply-To / Return-Path divergence findings.

    ``score`` is 0–100. Higher means more divergence signal.

    ``indicators`` is a tuple of human-readable strings naming each detected
    divergence, deduplicated and source-order stable. Values are drawn from
    the closed set:

    - ``"from_reply_to_divergence"``
    - ``"from_return_path_divergence"``
    - ``"from_sender_header_divergence"``

    These are intentionally NOT added to the schema-versioned
    ``PrecursorIndicator`` literal because divergence is a sender-identity
    signal, not a ransomware-precursor signal. The scoring agent's overlay
    uses the score; downstream consumers that need the named flags can
    inspect the assessment object directly.
    """

    score: int
    indicators: tuple[str, ...]


def score_header_divergence(
    *,
    sender: str,
    headers: Mapping[str, str] | None = None,
) -> HeaderDivergenceAssessment:
    """Detect From / Reply-To / Return-Path / Sender header divergence.

    Inputs:

    - ``sender``: the parsed ``From:`` address as carried by
      ``EmailInboundPayload.sender``. Can be a bare address
      (``vendor@example.com``) or an RFC 5322 display-name form
      (``"Vendor Billing <vendor@example.com>"``). Empty / unparseable
      values disable the detector for that email (score 0).
    - ``headers``: the raw header dict from
      ``EmailInboundPayload.headers``. May be empty or ``None``. Header
      lookup is case-insensitive — ``Reply-To`` and ``reply-to`` are
      equivalent.

    Returns a ``HeaderDivergenceAssessment``. The score is bounded above
    by ``_MAX_SCORE`` (90) by design: a deterministic divergence detector
    should never single-handedly force a final ``risk_score`` of 100 —
    that decision belongs to the LLM scoring path or to combined
    multi-signal evidence.
    """

    from_domain = _root_domain(_extract_address_domain(sender))
    if not from_domain:
        return HeaderDivergenceAssessment(score=0, indicators=())

    header_lookup = _case_insensitive_headers(headers or {})

    reply_to_addr = header_lookup.get("reply-to", "")
    return_path_addr = header_lookup.get("return-path", "")
    sender_header_addr = header_lookup.get("sender", "")

    reply_to_domain = _root_domain(_extract_address_domain(reply_to_addr))
    return_path_domain = _root_domain(_extract_address_domain(return_path_addr))
    sender_header_domain = _root_domain(_extract_address_domain(sender_header_addr))

    indicators: list[str] = []
    contributions: list[int] = []

    if reply_to_domain and reply_to_domain != from_domain:
        indicators.append("from_reply_to_divergence")
        contributions.append(_SCORE_REPLY_TO_DIVERGENCE)

    if return_path_domain and return_path_domain != from_domain:
        indicators.append("from_return_path_divergence")
        contributions.append(_SCORE_RETURN_PATH_DIVERGENCE)

    if sender_header_domain and sender_header_domain != from_domain:
        indicators.append("from_sender_header_divergence")
        contributions.append(_SCORE_SENDER_HEADER_DIVERGENCE)

    if not contributions:
        return HeaderDivergenceAssessment(score=0, indicators=())

    base = max(contributions)
    bonus = _COMBINATION_BUMP if len(contributions) > 1 else 0
    score = min(_MAX_SCORE, base + bonus)

    return HeaderDivergenceAssessment(score=score, indicators=tuple(indicators))


def _extract_address_domain(value: str) -> str:
    """Pull the domain portion out of a header value.

    Accepts bare addresses (``vendor@example.com``) and RFC 5322 display-name
    forms (``"Vendor <vendor@example.com>"``). Return-Path values commonly
    appear as ``<vendor@example.com>`` — also handled. Returns ``""`` for
    empty / unparseable values rather than raising.
    """

    if not value:
        return ""

    _, address = parseaddr(value)
    if not address or "@" not in address:
        return ""

    domain = address.rsplit("@", 1)[1].strip().lower()
    if not domain:
        return ""

    return domain


def _root_domain(domain: str) -> str:
    """Reduce a domain to its eTLD+1 root for comparison.

    Heuristic: take the last two labels. ``mail.vendor.com`` -> ``vendor.com``.
    ``vendor.co.uk`` -> ``co.uk`` (a known limitation — for v0 SMB scope this
    is acceptable; an MSP-hosted vendor at ``.co.uk`` will still compare
    correctly to itself, and the false-divergence risk is symmetric for
    legitimate and attacker domains).

    Returns ``""`` if the input is empty or has no usable structure.
    """

    if not domain:
        return ""

    parts = [p for p in domain.strip().lower().split(".") if p]
    if len(parts) <= 2:
        return ".".join(parts)
    return ".".join(parts[-2:])


def _case_insensitive_headers(headers: Mapping[str, str]) -> Mapping[str, str]:
    """Build a lowercase-keyed view of the header dict.

    RFC 5322 header field names are case-insensitive. A real-world MTA-stored
    header dict may use any casing (``Reply-To``, ``reply-to``, ``REPLY-TO``).
    """

    return {key.lower(): value for key, value in headers.items()}
