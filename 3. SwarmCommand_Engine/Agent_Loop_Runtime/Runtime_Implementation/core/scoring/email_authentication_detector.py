"""NorthStar Inbox Shield - email authentication header detector.

Parses upstream gateway ``Authentication-Results`` headers for SPF, DKIM, and
DMARC results. The detector is pure: no DNS lookups, no crypto verification,
no I/O, and no network calls. Mail gateways such as Microsoft, Google,
Proofpoint, and Mimecast already perform the protocol checks before delivery;
this detector ingests their result as one deterministic scoring signal.

Important boundary: authentication pass does not mean an email is safe. A
phisher can pass SPF/DKIM/DMARC from a lookalike domain they control. This
detector can only raise risk on failures or missing/unknown posture; it never
lowers risk on pass.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from email.utils import parseaddr
from typing import Mapping


_RESULT_RE = re.compile(
    r"\b(?P<mechanism>spf|dkim|dmarc)\s*=\s*(?P<result>[A-Za-z][A-Za-z0-9_-]*)",
    re.IGNORECASE,
)

_VALID_RESULTS = {
    "pass",
    "fail",
    "softfail",
    "neutral",
    "none",
    "temperror",
    "permerror",
    "policy",
    "bestguesspass",
}

_RESULT_NORMALIZATION = {
    "bestguesspass": "pass",
}

_SCORE_DKIM_FAIL = 45
_SCORE_SPF_FAIL = 45
_SCORE_SPF_SOFTFAIL = 35
_SCORE_DKIM_NONE = 20
_SCORE_DMARC_FAIL = 75
_SCORE_DMARC_NONE = 20
_SCORE_TEMPERROR = 25
_SCORE_PERMERROR = 35
_COMBINATION_BUMP = 10
_MAX_SCORE = 90


@dataclass(frozen=True)
class EmailAuthenticationAssessment:
    """One email's SPF/DKIM/DMARC gateway-authentication assessment."""

    score: int
    from_domain: str
    spf_result: str | None
    dkim_result: str | None
    dmarc_result: str | None
    indicators: tuple[str, ...]


def score_email_authentication(
    *,
    sender: str,
    headers: Mapping[str, str] | None = None,
) -> EmailAuthenticationAssessment:
    """Parse Authentication-Results and produce a lift-only score.

    Missing headers return score 0. Explicit failures/unknown posture lift risk
    but do not mutate payloads directly.
    """

    from_domain = _extract_address_domain(sender)
    auth_results = _authentication_results_header(headers or {})
    parsed_results = _parse_authentication_results(auth_results)

    indicators: list[str] = []
    contributions: list[int] = []

    spf = parsed_results.get("spf")
    dkim = parsed_results.get("dkim")
    dmarc = parsed_results.get("dmarc")

    _add_indicator(
        indicators,
        contributions,
        "spf_fail",
        _SCORE_SPF_FAIL,
        spf == "fail",
    )
    _add_indicator(
        indicators,
        contributions,
        "spf_softfail",
        _SCORE_SPF_SOFTFAIL,
        spf == "softfail",
    )
    _add_indicator(
        indicators,
        contributions,
        "spf_permerror",
        _SCORE_PERMERROR,
        spf == "permerror",
    )
    _add_indicator(
        indicators,
        contributions,
        "spf_temperror",
        _SCORE_TEMPERROR,
        spf == "temperror",
    )
    _add_indicator(
        indicators,
        contributions,
        "dkim_fail",
        _SCORE_DKIM_FAIL,
        dkim == "fail",
    )
    _add_indicator(
        indicators,
        contributions,
        "dkim_none",
        _SCORE_DKIM_NONE,
        dkim == "none",
    )
    _add_indicator(
        indicators,
        contributions,
        "dkim_permerror",
        _SCORE_PERMERROR,
        dkim == "permerror",
    )
    _add_indicator(
        indicators,
        contributions,
        "dmarc_fail",
        _SCORE_DMARC_FAIL,
        dmarc == "fail",
    )
    _add_indicator(
        indicators,
        contributions,
        "dmarc_none",
        _SCORE_DMARC_NONE,
        dmarc == "none",
    )
    _add_indicator(
        indicators,
        contributions,
        "dmarc_permerror",
        _SCORE_PERMERROR,
        dmarc == "permerror",
    )
    _add_indicator(
        indicators,
        contributions,
        "dmarc_temperror",
        _SCORE_TEMPERROR,
        dmarc == "temperror",
    )

    score = 0
    if contributions:
        score = min(
            _MAX_SCORE,
            max(contributions) + (_COMBINATION_BUMP if len(contributions) > 1 else 0),
        )

    return EmailAuthenticationAssessment(
        score=score,
        from_domain=from_domain,
        spf_result=spf,
        dkim_result=dkim,
        dmarc_result=dmarc,
        indicators=tuple(indicators),
    )


def _add_indicator(
    indicators: list[str],
    contributions: list[int],
    indicator: str,
    score: int,
    condition: bool,
) -> None:
    if condition:
        indicators.append(indicator)
        contributions.append(score)


def _authentication_results_header(headers: Mapping[str, str]) -> str:
    for key, value in headers.items():
        if key.lower() == "authentication-results":
            return value or ""
    return ""


def _parse_authentication_results(header_value: str) -> dict[str, str]:
    if not header_value:
        return {}

    results: dict[str, str] = {}
    for match in _RESULT_RE.finditer(header_value):
        mechanism = match.group("mechanism").lower()
        result = match.group("result").lower()
        result = _RESULT_NORMALIZATION.get(result, result)
        if result in _VALID_RESULTS:
            results[mechanism] = result
    return results


def _extract_address_domain(value: str) -> str:
    if not value:
        return ""
    _, address = parseaddr(value)
    if not address or "@" not in address:
        return ""
    return address.rsplit("@", 1)[1].strip().lower()


__all__ = [
    "EmailAuthenticationAssessment",
    "score_email_authentication",
]
