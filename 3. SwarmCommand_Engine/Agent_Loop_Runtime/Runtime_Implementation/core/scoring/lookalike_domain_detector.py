"""Deterministic sending-domain lookalike detector.

Locked by ``4. Product_Roadmap/Lookalike_Domain_Detector_Deep_Dive.md``
(§11 SIGNED 2026-06-05). v1 is pure, offline, default-off at the scoring
integration boundary, and compares message identity domains against a
provided tenant known-good domain set.

No DNS, WHOIS, network calls, global brand seeds, body-URL scoring, canonical
ledger writes, or buyer-facing claims live here.
"""

from __future__ import annotations

import re
from email.utils import parseaddr
from typing import Final, Iterable

from core.blackboard import LookalikeDomainAssessment, LookalikeDomainFinding
from core.precursor.url_obfuscation_detector import CYRILLIC_LOOKALIKES

LOOKALIKE_SENDER_DOMAIN_FLAG: Final[str] = "lookalike_sender_domain"

_MAX_IDENTITY_DOMAINS: Final[int] = 8
_MAX_KNOWN_GOOD_DOMAINS: Final[int] = 256
_MAX_DOMAIN_CHARS: Final[int] = 253

_COMMON_MULTI_PART_SUFFIXES: Final[frozenset[str]] = frozenset(
    {
        "co.uk",
        "com.au",
        "com.br",
        "com.mx",
        "co.nz",
        "co.jp",
        "co.in",
        "com.sg",
    }
)

_GENERIC_COMBOSQUAT_TOKENS: Final[frozenset[str]] = frozenset(
    {
        "admin",
        "billing",
        "finance",
        "invoice",
        "invoices",
        "mail",
        "pay",
        "payment",
        "payments",
        "secure",
        "security",
        "support",
        "vendor",
    }
)

_CONFUSABLES: Final[dict[str, str]] = {
    "0": "o",
    "1": "l",
    "3": "e",
    "5": "s",
    "7": "t",
    "а": "a",
    "А": "a",
    "В": "b",
    "с": "c",
    "С": "c",
    "е": "e",
    "Е": "e",
    "Н": "h",
    "К": "k",
    "М": "m",
    "о": "o",
    "О": "o",
    "р": "p",
    "Р": "p",
    "Т": "t",
    "х": "x",
    "Х": "x",
    "у": "y",
    "У": "y",
    "−": "-",
    "‐": "-",
    "‑": "-",
    "‒": "-",
    "–": "-",
    "—": "-",
}

_DOMAIN_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"[a-z0-9-]+")


def detect_lookalike_domains(
    *,
    from_address: str,
    headers: dict[str, str] | None = None,
    known_good_domains: Iterable[str],
) -> LookalikeDomainAssessment:
    """Compare From / Reply-To identity domains to known-good tenant domains.

    ``known_good_domains`` is an explicit input so this detector stays pure and
    does not read tenant state. Integration code is responsible for sourcing
    that set from the Vendor Baseline Store or an equivalent signed path.
    """

    identity_domains = _identity_domains(from_address=from_address, headers=headers or {})
    known_good = _normalize_domain_set(known_good_domains, cap=_MAX_KNOWN_GOOD_DOMAINS)
    if not identity_domains or not known_good:
        return _empty_assessment()

    findings: list[LookalikeDomainFinding] = []
    seen: set[tuple[str, str, str]] = set()

    for offending_domain in identity_domains[:_MAX_IDENTITY_DOMAINS]:
        if offending_domain in known_good:
            continue
        for trusted_domain in known_good:
            for finding in _find_domain_matches(offending_domain, trusted_domain):
                key = (finding.technique, finding.offending_domain, finding.matched_known_good)
                if key in seen:
                    continue
                seen.add(key)
                findings.append(finding)

    if not findings:
        return _empty_assessment()

    score = max(_score_for_technique(f.technique, f.distance) for f in findings)
    return LookalikeDomainAssessment(
        fired=True,
        lookalike_domain_score=score,
        findings=tuple(findings),
        recommended_risk_floor_lift=_floor_for_score(score),
    )


def extract_identity_domains(
    *,
    from_address: str,
    headers: dict[str, str] | None = None,
) -> tuple[str, ...]:
    """Public helper used by tests and future integration code."""

    return tuple(_identity_domains(from_address=from_address, headers=headers or {}))


def _identity_domains(*, from_address: str, headers: dict[str, str]) -> list[str]:
    candidates = [from_address]
    for key, value in headers.items():
        if key.lower() == "reply-to":
            candidates.append(value)
    domains: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        normalized = _normalize_domain(_extract_domain(candidate))
        if normalized and normalized not in seen:
            seen.add(normalized)
            domains.append(normalized)
    return domains


def _find_domain_matches(
    offending_domain: str,
    trusted_domain: str,
) -> tuple[LookalikeDomainFinding, ...]:
    findings: list[LookalikeDomainFinding] = []
    offending_decoded = _decode_idna(offending_domain)
    trusted_decoded = _decode_idna(trusted_domain)
    offending_registered = _registrable_domain(offending_decoded)
    trusted_registered = _registrable_domain(trusted_decoded)
    offending_sld = _sld(offending_registered)
    trusted_sld = _sld(trusted_registered)

    if not offending_sld or not trusted_sld:
        return ()

    if "xn--" in offending_domain or offending_decoded != offending_domain:
        decoded_match = _find_domain_matches(offending_decoded, trusted_domain)
        if decoded_match:
            findings.append(
                _finding(
                    "punycode",
                    offending_domain,
                    trusted_domain,
                    "punycode identity domain decodes near known-good domain",
                )
            )

    if _has_confusable(offending_decoded):
        normalized_offending = _normalize_confusables(offending_decoded)
        if _registrable_domain(normalized_offending) == trusted_registered:
            findings.append(
                _finding(
                    "homoglyph",
                    offending_domain,
                    trusted_domain,
                    "confusable characters normalize to known-good domain",
                )
            )

    distance = _damerau_levenshtein(offending_sld, trusted_sld)
    if 0 < distance <= _distance_threshold(len(trusted_sld)):
        findings.append(
            _finding(
                "typosquat",
                offending_domain,
                trusted_domain,
                "bounded edit distance to known-good domain",
                distance=distance,
            )
        )

    if offending_sld == trusted_sld and offending_registered != trusted_registered:
        findings.append(
            _finding(
                "tld_swap",
                offending_domain,
                trusted_domain,
                "same second-level label with different TLD",
            )
        )

    if _is_subdomain_spoof(offending_decoded, trusted_registered):
        findings.append(
            _finding(
                "subdomain_spoof",
                offending_domain,
                trusted_domain,
                "known-good domain appears under attacker-controlled parent",
            )
        )

    if _is_combosquat(offending_sld, trusted_sld):
        findings.append(
            _finding(
                "combosquat",
                offending_domain,
                trusted_domain,
                "known-good token embedded in non-known-good domain",
            )
        )

    return tuple(findings)


def _extract_domain(value: str | None) -> str:
    if not value:
        return ""
    _, address = parseaddr(value)
    candidate = address or value
    if "@" in candidate:
        candidate = candidate.rsplit("@", 1)[1]
    return candidate.strip().strip("<>[](),;")


def _normalize_domain_set(
    domains: Iterable[str],
    *,
    cap: int,
) -> tuple[str, ...]:
    normalized: list[str] = []
    seen: set[str] = set()
    for domain in domains:
        clean = _normalize_domain(domain)
        if not clean or clean in seen:
            continue
        seen.add(clean)
        normalized.append(clean)
        if len(normalized) >= cap:
            break
    return tuple(normalized)


def _normalize_domain(domain: str) -> str:
    cleaned = domain.strip().strip(".").lower()
    if not cleaned or len(cleaned) > _MAX_DOMAIN_CHARS:
        return ""
    if any(char.isspace() for char in cleaned):
        return ""
    if "/" in cleaned or "\\" in cleaned or ".." in cleaned:
        return ""
    return cleaned


def _decode_idna(domain: str) -> str:
    labels: list[str] = []
    for label in domain.split("."):
        try:
            labels.append(label.encode("ascii").decode("idna").lower())
        except (UnicodeError, ValueError):
            labels.append(label.lower())
    return ".".join(labels)


def _registrable_domain(domain: str) -> str:
    labels = [label for label in domain.split(".") if label]
    if len(labels) <= 2:
        return ".".join(labels)
    suffix2 = ".".join(labels[-2:])
    if suffix2 in _COMMON_MULTI_PART_SUFFIXES and len(labels) >= 3:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def _sld(registrable_domain: str) -> str:
    parts = registrable_domain.split(".")
    if len(parts) < 2:
        return ""
    return parts[0]


def _has_confusable(domain: str) -> bool:
    return any(char in CYRILLIC_LOOKALIKES or char in _CONFUSABLES for char in domain)


def _normalize_confusables(value: str) -> str:
    return "".join(_CONFUSABLES.get(char, char) for char in value)


def _distance_threshold(sld_length: int) -> int:
    if sld_length < 5:
        return 1
    if sld_length <= 9:
        return 1
    return 2


def _is_subdomain_spoof(offending_domain: str, trusted_domain: str) -> bool:
    return offending_domain.endswith("." + trusted_domain) is False and (
        "." + trusted_domain + "." in "." + offending_domain + "."
        or offending_domain.startswith(trusted_domain + ".")
    )


def _is_combosquat(offending_sld: str, trusted_sld: str) -> bool:
    tokens = _tokens_for_combosquat(trusted_sld)
    return any(token in offending_sld and offending_sld != token for token in tokens)


def _tokens_for_combosquat(trusted_sld: str) -> tuple[str, ...]:
    tokens = [
        token
        for token in _DOMAIN_TOKEN_RE.findall(trusted_sld)
        if len(token) >= 5 and token not in _GENERIC_COMBOSQUAT_TOKENS
    ]
    compact = trusted_sld.replace("-", "")
    if len(compact) >= 5 and compact not in _GENERIC_COMBOSQUAT_TOKENS:
        tokens.append(compact)
    return tuple(dict.fromkeys(tokens))


def _score_for_technique(technique: str, distance: int | None) -> int:
    if technique in {"homoglyph", "punycode", "subdomain_spoof"}:
        return 85
    if technique == "typosquat":
        return 85 if distance is not None and distance <= 1 else 70
    if technique in {"combosquat", "tld_swap"}:
        return 70
    return 25


def _floor_for_score(score: int) -> int:
    if score >= 85:
        return 85
    if score >= 50:
        return 70
    return min(score, 25)


def _finding(
    technique: str,
    offending_domain: str,
    trusted_domain: str,
    evidence: str,
    *,
    distance: int | None = None,
) -> LookalikeDomainFinding:
    return LookalikeDomainFinding(
        technique=technique,  # type: ignore[arg-type]
        offending_domain=offending_domain,
        matched_known_good=trusted_domain,
        distance=distance,
        evidence=evidence,
    )


def _damerau_levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    rows = len(a) + 1
    cols = len(b) + 1
    dist = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        dist[i][0] = i
    for j in range(cols):
        dist[0][j] = j

    for i in range(1, rows):
        for j in range(1, cols):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dist[i][j] = min(
                dist[i - 1][j] + 1,
                dist[i][j - 1] + 1,
                dist[i - 1][j - 1] + cost,
            )
            if (
                i > 1
                and j > 1
                and a[i - 1] == b[j - 2]
                and a[i - 2] == b[j - 1]
            ):
                dist[i][j] = min(dist[i][j], dist[i - 2][j - 2] + 1)
    return dist[-1][-1]


def _empty_assessment() -> LookalikeDomainAssessment:
    return LookalikeDomainAssessment(
        fired=False,
        lookalike_domain_score=0,
        findings=(),
        recommended_risk_floor_lift=0,
    )


__all__ = [
    "LOOKALIKE_SENDER_DOMAIN_FLAG",
    "detect_lookalike_domains",
    "extract_identity_domains",
]
