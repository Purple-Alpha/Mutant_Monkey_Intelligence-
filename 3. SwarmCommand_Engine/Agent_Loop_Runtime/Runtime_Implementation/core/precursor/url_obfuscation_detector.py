"""NorthStar Inbox Shield — Phase 1.2 URL obfuscation detector.

Pure-function URL parser. Given the body text (plain + optional HTML) of an
``EmailInboundPayload``, returns a 0–100 ``url_obfuscation_score`` plus the
``PrecursorIndicator`` values that justify it.

Detects, per the 12-month roadmap Month 3 deliverables list:
- homoglyphs / Cyrillic look-alikes in the host portion;
- IDN tricks (punycode ``xn--`` prefix);
- URL shorteners (bit.ly, tinyurl.com, t.co, ow.ly, is.gd, buff.ly, rb.gy, etc.);
- credential-bearing URLs (``user:password@host`` syntax);
- suspicious TLDs (`.zip`, `.mov`, `.tk`, `.top`, `.gq`, `.cf`, `.ml`, `.ga`);
- IP-address hosts and ``http://`` instead of ``https://`` on financial URLs;
- known phishing-kit URL-path patterns (``/login``, ``/signin``, ``/verify``,
  ``/auth``, ``/account/secure``).

No network calls. No DNS resolution. No fetching the URL. Everything is
inferred from the URL string alone.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from core.blackboard import PrecursorIndicator

# URL regex tuned to common email body / HTML rendering. Captures ``http``,
# ``https``, and bare-``www`` hosts. Greedy enough to grab real-world URLs that
# include ``=``, ``&``, ``%``, etc., but stops at common terminators
# (whitespace, closing brackets / parens / quotes, end-of-string).
URL_PATTERN = re.compile(
    r"(?i)\b(?:https?://|www\.)[^\s<>()\"\'\\]+",
)

URL_SHORTENER_HOSTS: frozenset[str] = frozenset(
    {
        "bit.ly",
        "tinyurl.com",
        "t.co",
        "ow.ly",
        "is.gd",
        "buff.ly",
        "rb.gy",
        "goo.gl",
        "shorturl.at",
        "cutt.ly",
        "tiny.cc",
        "rebrand.ly",
        "lnkd.in",
    }
)

# Suspicious TLDs per common-abuse-list research (Spamhaus / Cloudflare data).
# Kept tight — adding to this set requires documented rationale because
# legitimate businesses on these TLDs would otherwise FPR-regress.
SUSPICIOUS_TLDS: frozenset[str] = frozenset(
    {
        "zip",
        "mov",
        "tk",
        "top",
        "gq",
        "cf",
        "ml",
        "ga",
        "country",
        "kim",
        "click",
        "loan",
        "work",
    }
)

# Path tokens common in phishing kits' credential-harvest landing pages.
LOGIN_PATH_TOKENS: frozenset[str] = frozenset(
    {"login", "signin", "sign-in", "verify", "auth", "secure", "account"}
)

# IPv4 host pattern.
IPV4_HOST = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")

# Cyrillic letters that visually resemble Latin letters and are the most
# common homoglyph attack vector on ASCII brand names.
CYRILLIC_LOOKALIKES: frozenset[str] = frozenset(
    "абсеорхуАВСЕНКМОРТХУ"
)


@dataclass(frozen=True)
class UrlRiskAssessment:
    """Aggregate URL-obfuscation score for one email body.

    ``score`` is 0–100. ``indicators`` lists the ``PrecursorIndicator`` values
    that fired across all extracted URLs (deduplicated, order-stable). The
    overlay layer hands these straight into the
    ``EmailAnalysisRansomwarePrecursorAnalysis.precursor_indicators`` list.
    """

    score: int
    indicators: tuple[PrecursorIndicator, ...]


def extract_urls(text: str | None) -> list[str]:
    """Extract URLs from email body text.

    Returns matches in source order. Caller-supplied ``None`` is treated as
    empty string (returns ``[]``) so we never raise on missing body.
    """

    if not text:
        return []
    return URL_PATTERN.findall(text)


def score_url_obfuscation(*texts: str | None) -> UrlRiskAssessment:
    """Score URL-obfuscation risk across one or more body texts.

    Pass ``body_plain`` and optionally ``body_html`` (or any other rendered
    surface). All inputs are concatenated for URL extraction; per-URL
    indicators are deduplicated, and the aggregate ``score`` is the **max**
    of per-URL contributions (so the worst URL drives the email's risk,
    not the count of URLs).

    Pure function: no network, no DNS, no I/O.
    """

    combined = "\n".join(t for t in texts if t)
    urls = extract_urls(combined)
    if not urls:
        return UrlRiskAssessment(score=0, indicators=())

    aggregate_indicators: list[PrecursorIndicator] = []
    aggregate_score = 0
    seen_indicators: set[PrecursorIndicator] = set()

    for url in urls:
        per_url = _score_single_url(url)
        aggregate_score = max(aggregate_score, per_url.score)
        for indicator in per_url.indicators:
            if indicator in seen_indicators:
                continue
            seen_indicators.add(indicator)
            aggregate_indicators.append(indicator)

    return UrlRiskAssessment(
        score=min(aggregate_score, 100),
        indicators=tuple(aggregate_indicators),
    )


def _score_single_url(url: str) -> UrlRiskAssessment:
    indicators: list[PrecursorIndicator] = []
    score = 0

    parsed = _safe_urlparse(url)
    if parsed is None:
        return UrlRiskAssessment(score=0, indicators=())

    host = (parsed.hostname or "").lower()
    path = (parsed.path or "").lower()

    if parsed.username is not None or "@" in (parsed.netloc or ""):
        indicators.append("credential_bearing_url")
        score = max(score, 80)

    if host in URL_SHORTENER_HOSTS:
        indicators.append("url_shortener_present")
        score = max(score, 50)

    if "xn--" in host:
        indicators.append("punycode_url_present")
        score = max(score, 75)

    if _has_cyrillic_homoglyph(host):
        indicators.append("homoglyph_url_present")
        score = max(score, 75)

    tld = host.rsplit(".", 1)[-1] if "." in host else ""
    if tld in SUSPICIOUS_TLDS:
        indicators.append("suspicious_tld_present")
        score = max(score, 60)

    if IPV4_HOST.match(host or "") is not None:
        indicators.append("ip_address_url_present")
        score = max(score, 70)

    if any(token in path for token in LOGIN_PATH_TOKENS):
        indicators.append("login_path_url_present")
        score = max(score, 50)

    return UrlRiskAssessment(score=score, indicators=tuple(indicators))


def _safe_urlparse(url: str):  # type: ignore[no-untyped-def]
    """Wrap ``urllib.parse.urlparse`` to never raise and to normalise
    schemeless ``www.`` URLs into something ``urlparse`` understands.
    """

    if url.lower().startswith("www."):
        url = "http://" + url
    try:
        return urlparse(url)
    except ValueError:
        return None


def _has_cyrillic_homoglyph(host: str) -> bool:
    return any(ch in CYRILLIC_LOOKALIKES for ch in host)
