"""NorthStar Inbox Shield - Executive Impersonation detector.

Deterministic offline detector for claimed-executive-principal BEC patterns:
roster display-name match paired with identity-domain mismatch, free-mail, or
consumed look-alike cue, optionally corroborated by authority/secrecy/urgency
pressure and task-directive language in ``body_plain``.

Locked per ``4. Product_Roadmap/Executive_Impersonation_Detector_Deep_Dive.md``
(§11 SIGNED 2026-06-06 by Matt Nichol). v1 is pure, offline, default-off at
the scoring integration boundary, and never emits block/quarantine/deny verbs.

No DNS, org-chart sync, network calls, phone-number extraction, raw mailbox
body echo (>60 chars), or buyer-facing claims live here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, Iterable, Literal

from core.blackboard import (
    ExecutiveImpersonationAssessment,
    ExecutiveImpersonationFinding,
    LookalikeDomainAssessment,
)
from core.scoring.lookalike_domain_detector import extract_identity_domains

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

EXECUTIVE_IMPERSONATION_PATTERN_FLAG: Final[str] = "executive_impersonation_pattern"
"""``BehavioralDeviationFlag`` value the scoring agent (pass 2) appends to
``EmailAnalysisRiskAnalysis.behavioral_deviation_flags`` once when this
detector fires. Locked in §10.A Q7 of the Executive Impersonation spec."""


PrincipalRole = Literal["executive", "finance_authority", "owner", "other_authority"]

# ---------------------------------------------------------------------------
# §10.A Q6 curated consumer free-mail provider suffixes
# ---------------------------------------------------------------------------

_FREE_MAIL_SUFFIXES: Final[frozenset[str]] = frozenset(
    {
        "aol.com",
        "gmail.com",
        "googlemail.com",
        "gmx.com",
        "gmx.net",
        "hotmail.com",
        "icloud.com",
        "live.com",
        "mac.com",
        "me.com",
        "outlook.com",
        "pm.me",
        "proton.me",
        "protonmail.com",
        "yahoo.com",
        "yandex.com",
        "yandex.ru",
        "zoho.com",
    }
)

# ---------------------------------------------------------------------------
# §4.1 risk-floor lift bands (mirror Lookalike 25 / 70 / 85 discipline)
# ---------------------------------------------------------------------------

_LIFT_PROBABLE: Final[int] = 70
_LIFT_STRONG: Final[int] = 85

_SCORE_PROBABLE: Final[int] = 70
_SCORE_STRONG: Final[int] = 85

# ---------------------------------------------------------------------------
# Scan / input caps (mirror TOAD / Lookalike break-it posture)
# ---------------------------------------------------------------------------

_MAX_SCAN_CHARS: Final[int] = 200_000
_MAX_ROSTER_ENTRIES: Final[int] = 256
_MAX_NAME_FORMS_PER_ENTRY: Final[int] = 32
_MAX_AUTHORIZED_DOMAINS_PER_ENTRY: Final[int] = 64
_MAX_IDENTITY_DOMAINS: Final[int] = 8
_MAX_DOMAIN_CHARS: Final[int] = 253

# ---------------------------------------------------------------------------
# Name normalization (§10.A Q2)
# ---------------------------------------------------------------------------

_TITLES_AND_HONORIFICS: Final[re.Pattern[str]] = re.compile(
    r"\b(?:"
    r"mr|mrs|ms|miss|dr|prof|sir|madam|"
    r"ceo|cfo|coo|cto|owner|controller|president|"
    r"vp|vice\s+president|chief\s+\w+\s+officer"
    r")\b\.?",
    re.IGNORECASE,
)

_NON_ALNUM_RE: Final[re.Pattern[str]] = re.compile(r"[^\w\s]", re.UNICODE)
_WHITESPACE_RE: Final[re.Pattern[str]] = re.compile(r"\s+")

# ---------------------------------------------------------------------------
# §3 closed pressure categories (§10.A Q3 — sibling TOAD-style vocabulary)
# ---------------------------------------------------------------------------

_PRESSURE_CATEGORY_ORDER: Final[tuple[str, ...]] = (
    "authority",
    "secrecy",
    "urgency",
    "task_directive",
)

_PRESSURE_EVIDENCE: Final[dict[str, str]] = {
    "authority": (
        "executive authority framing detected in message body "
        "(sender claims decision-making or executive role to direct action)"
    ),
    "secrecy": (
        "secrecy or confidentiality pressure language detected in message body "
        "(instruction to limit disclosure or avoid looping others in)"
    ),
    "urgency": (
        "urgency or time-boxed directive language detected in message body "
        "(instruction to act before a short or fixed deadline)"
    ),
    "task_directive": (
        "high-risk financial or payment task directive detected in message body "
        "(wire, banking change, gift-card purchase, or urgent payment request)"
    ),
}

_IDENTITY_EVIDENCE: Final[dict[str, str]] = {
    "roster_name_domain_mismatch": (
        "claimed executive display name matches tenant roster but sending "
        "identity domain is not an authorized domain for that principal"
    ),
    "free_mail_executive_claim": (
        "claimed executive display name matches tenant roster but sender "
        "uses a consumer free-mail provider domain"
    ),
    "lookalike_domain_executive_claim": (
        "claimed executive display name matches tenant roster and sending "
        "domain resembles an authorized domain (consumed look-alike cue)"
    ),
}

_PATTERNS_AUTHORITY: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r"\bas\s+(?:the\s+)?(?:ceo|cfo|coo|cto|president|owner|controller|"
        r"managing\s+director|executive\s+director)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bi\s+am\s+(?:the\s+)?(?:ceo|cfo|coo|cto|president|owner|controller|"
        r"your\s+(?:ceo|cfo|boss|manager|supervisor))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:ceo|cfo|coo|cto|president|owner|controller)\s+(?:here|speaking)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:this\s+is|it\s+is)\s+(?:your\s+)?(?:ceo|cfo|president|owner)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:i\s+)?(?:need|require|expect)\s+you\s+to\s+(?:handle|take\s+care\s+of|"
        r"process|complete|approve|authorize)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:direct(?:ly)?\s+from|on\s+behalf\s+of)\s+(?:the\s+)?(?:ceo|cfo|"
        r"executive\s+(?:team|office|management))\b",
        re.IGNORECASE,
    ),
)

_PATTERNS_SECRECY: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r"\bkeep\s+(?:this|it)\s+(?:between\s+us|confidential|private|discreet)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:do\s+not|don'?t)\s+(?:share|discuss|mention|tell|loop\s+in|cc|copy)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:strictly\s+)?confidential\b[\s\S]{0,40}\b(?:do\s+not|don'?t)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:no\s+one|nobody)\s+(?:else\s+)?(?:needs\s+to|should|must)\s+know\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:discreet|discretion)\s+(?:is\s+)?(?:required|needed|appreciated)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:do\s+not|don'?t)\s+(?:loop|bring|involve)\s+(?:in\s+)?(?:finance|accounting|"
        r"legal|hr|it|anyone|anybody|others)\b",
        re.IGNORECASE,
    ),
)

_PATTERNS_URGENCY: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r"\b(?:before|by)\s+(?:the\s+)?(?:close\s+of\s+business|end\s+of\s+(?:day|business)|"
        r"eod|cob|today|tonight|this\s+(?:morning|afternoon|evening))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:right\s+now|immediately|asap|a\.?s\.?a\.?p\.?|urgent(?:ly)?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:time[- ]sensitive|deadline|within\s+\d+\s+(?:hours?|minutes?))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:need(?:ed)?|must\s+be\s+(?:done|completed|handled|processed))\s+"
        r"(?:today|now|immediately|before)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:handle|process|complete|send|wire|transfer)\s+(?:this\s+)?(?:today|now|"
        r"immediately|asap)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:in\s+a\s+meeting|tied\s+up|can'?t\s+(?:talk|call|discuss))\b"
        r"[\s\S]{0,60}\b(?:today|now|immediately|asap|before)\b",
        re.IGNORECASE,
    ),
)

_PATTERNS_TASK_DIRECTIVE: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(
        r"\b(?:wire|transfer|send)\s+(?:the\s+|me\s+)?(?:\$|usd\s+)?\d[\d,]*(?:\.\d{2})?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:wire|bank|ach|payment|transfer)\s+(?:transfer|details?|instructions?|"
        r"information|info)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:change|update|revise|modify)\s+(?:the\s+|our\s+)?(?:bank(?:ing)?|ach|wire|"
        r"payment|account|routing|deposit|payable)\s+(?:details?|instructions?|"
        r"information|info|number)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:purchase|buy|get)\s+(?:\d+\s+)?(?:gift\s+cards?|itunes|google\s+play|"
        r"apple\s+cards?|prepaid\s+cards?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:send|email|reply\s+with)\s+(?:the\s+)?(?:codes?|pin\s+codes?|serial\s+numbers?|"
        r"card\s+(?:numbers?|details?))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:release|approve|authorize|process|execute|complete)\s+(?:the\s+|this\s+)?"
        r"(?:payment|wire|transfer|invoice|vendor\s+payment)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:new|updated|revised|changed|corrected)\s+(?:bank(?:ing)?|ach|wire|payment|"
        r"account|routing)\s+(?:details?|instructions?|information|info)\b",
        re.IGNORECASE,
    ),
)

_PATTERNS_BY_CATEGORY: Final[dict[str, tuple[re.Pattern[str], ...]]] = {
    "authority": _PATTERNS_AUTHORITY,
    "secrecy": _PATTERNS_SECRECY,
    "urgency": _PATTERNS_URGENCY,
    "task_directive": _PATTERNS_TASK_DIRECTIVE,
}

_FINDING_TECHNIQUE_ORDER: Final[tuple[str, ...]] = (
    "roster_name_domain_mismatch",
    "free_mail_executive_claim",
    "lookalike_domain_executive_claim",
    "authority_pressure",
    "task_directive",
)


@dataclass(frozen=True)
class PrincipalRosterEntry:
    """One known-good principal row from the per-tenant roster (§10.A Q1)."""

    display_name_forms: tuple[str, ...]
    authorized_domains: tuple[str, ...]
    principal_role: PrincipalRole


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def detect_executive_impersonation(
    *,
    display_name: str,
    from_address: str,
    headers: dict[str, str] | None = None,
    body_plain: str = "",
    principal_roster: Iterable[PrincipalRosterEntry] = (),
    lookalike_assessment: LookalikeDomainAssessment | None = None,
) -> ExecutiveImpersonationAssessment:
    """Score claimed-executive impersonation evidence for an inbound message.

    Pure-function deterministic detector. Inputs are the sender display name,
    From / Reply-To identity domains (via ``extract_identity_domains``), a
    per-tenant principal roster, ``body_plain`` for pressure vocabulary, and an
    optional pre-computed :class:`~core.blackboard.LookalikeDomainAssessment`.

    Identity findings (roster match paired with domain mismatch, free-mail, or
    consumed look-alike cue) are **required** to fire; pressure and task-
    directive findings never fire the detector alone (§3.3 / §10.A Q4).

    Returns a frozen, validator-checked
    :class:`~core.blackboard.ExecutiveImpersonationAssessment`. Default-off
    wiring is enforced at the scoring integration boundary — this function
    always returns the assessment object only.
    """

    normalized_name = _normalize_display_name(display_name)
    roster = _normalize_roster(principal_roster)
    identity_domains = _normalize_identity_domains(
        extract_identity_domains(from_address=from_address, headers=headers)
    )
    lookalike_domains = _lookalike_offending_domains(lookalike_assessment)
    scan_region = (body_plain or "")[:_MAX_SCAN_CHARS]

    matched = _match_roster_principal(normalized_name, roster)
    if matched is None:
        return _empty_assessment()

    entry, _matched_form = matched
    if not identity_domains:
        return _empty_assessment()

    if _all_domains_authorized(identity_domains, entry.authorized_domains):
        return _empty_assessment()

    identity_findings = _collect_identity_findings(
        entry=entry,
        identity_domains=identity_domains,
        lookalike_domains=lookalike_domains,
    )
    if not identity_findings:
        return _empty_assessment()

    pressure_findings = _collect_pressure_findings(
        scan_region=scan_region,
        principal_role=entry.principal_role,
    )

    findings = _order_findings(identity_findings + pressure_findings)
    score, lift = _compute_score_and_lift(
        identity_findings=identity_findings,
        pressure_findings=pressure_findings,
    )

    return ExecutiveImpersonationAssessment(
        fired=True,
        executive_impersonation_score=score,
        findings=tuple(findings),
        recommended_risk_floor_lift=lift,
    )


# ---------------------------------------------------------------------------
# Roster / identity helpers
# ---------------------------------------------------------------------------


def _normalize_display_name(name: str) -> str:
    text = (name or "").casefold()
    text = _WHITESPACE_RE.sub(" ", text).strip()
    text = _TITLES_AND_HONORIFICS.sub(" ", text)
    text = _NON_ALNUM_RE.sub("", text)
    return _WHITESPACE_RE.sub(" ", text).strip()


def _normalize_roster(
    roster: Iterable[PrincipalRosterEntry],
) -> tuple[PrincipalRosterEntry, ...]:
    normalized: list[PrincipalRosterEntry] = []
    for index, entry in enumerate(roster):
        if index >= _MAX_ROSTER_ENTRIES:
            break
        name_forms = tuple(
            form
            for raw in entry.display_name_forms[:_MAX_NAME_FORMS_PER_ENTRY]
            if (form := _normalize_display_name(raw))
        )
        domains = _normalize_domain_set(
            entry.authorized_domains,
            cap=_MAX_AUTHORIZED_DOMAINS_PER_ENTRY,
        )
        if not name_forms or not domains:
            continue
        normalized.append(
            PrincipalRosterEntry(
                display_name_forms=name_forms,
                authorized_domains=domains,
                principal_role=entry.principal_role,
            )
        )
    return tuple(normalized)


def _match_roster_principal(
    normalized_name: str,
    roster: tuple[PrincipalRosterEntry, ...],
) -> tuple[PrincipalRosterEntry, str] | None:
    if not normalized_name:
        return None
    for entry in roster:
        for form in entry.display_name_forms:
            if normalized_name == form:
                return entry, form
    return None


def _normalize_identity_domains(domains: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    seen: set[str] = set()
    for domain in domains[:_MAX_IDENTITY_DOMAINS]:
        clean = _normalize_domain(domain)
        if clean and clean not in seen:
            seen.add(clean)
            normalized.append(clean)
    return tuple(normalized)


def _normalize_domain_set(domains: Iterable[str], *, cap: int) -> tuple[str, ...]:
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


def _all_domains_authorized(
    identity_domains: tuple[str, ...],
    authorized_domains: tuple[str, ...],
) -> bool:
    authorized = set(authorized_domains)
    return all(domain in authorized for domain in identity_domains)


def _lookalike_offending_domains(
    assessment: LookalikeDomainAssessment | None,
) -> frozenset[str]:
    if assessment is None or not assessment.fired:
        return frozenset()
    return frozenset(
        _normalize_domain(finding.offending_domain)
        for finding in assessment.findings
        if _normalize_domain(finding.offending_domain)
    )


def _is_free_mail_domain(domain: str) -> bool:
    normalized = _normalize_domain(domain)
    if not normalized:
        return False
    labels = normalized.split(".")
    for index in range(len(labels)):
        suffix = ".".join(labels[index:])
        if suffix in _FREE_MAIL_SUFFIXES:
            return True
    return False


def _collect_identity_findings(
    *,
    entry: PrincipalRosterEntry,
    identity_domains: tuple[str, ...],
    lookalike_domains: frozenset[str],
) -> list[ExecutiveImpersonationFinding]:
    findings: list[ExecutiveImpersonationFinding] = []
    seen_techniques: set[str] = set()
    authorized = set(entry.authorized_domains)

    for domain in identity_domains:
        if domain in authorized:
            continue

        if domain in lookalike_domains:
            technique = "lookalike_domain_executive_claim"
            relationship = "lookalike"
        elif _is_free_mail_domain(domain):
            technique = "free_mail_executive_claim"
            relationship = "free_provider"
        else:
            technique = "roster_name_domain_mismatch"
            relationship = "mismatch"

        if technique in seen_techniques:
            continue
        seen_techniques.add(technique)
        findings.append(
            _identity_finding(
                technique=technique,
                principal_role=entry.principal_role,
                domain_relationship=relationship,
            )
        )

    return findings


def _identity_finding(
    *,
    technique: str,
    principal_role: PrincipalRole,
    domain_relationship: str,
) -> ExecutiveImpersonationFinding:
    return ExecutiveImpersonationFinding(
        technique=technique,  # type: ignore[arg-type]
        claimed_principal_role=principal_role,
        domain_relationship=domain_relationship,  # type: ignore[arg-type]
        pressure_category="none",
        evidence=_IDENTITY_EVIDENCE[technique],
    )


# ---------------------------------------------------------------------------
# Pressure vocabulary
# ---------------------------------------------------------------------------


def _collect_pressure_findings(
    *,
    scan_region: str,
    principal_role: PrincipalRole,
) -> list[ExecutiveImpersonationFinding]:
    if not scan_region.strip():
        return []

    findings: list[ExecutiveImpersonationFinding] = []
    for category in _PRESSURE_CATEGORY_ORDER:
        patterns = _PATTERNS_BY_CATEGORY[category]
        if not any(pattern.search(scan_region) for pattern in patterns):
            continue

        if category == "task_directive":
            technique = "task_directive"
            pressure_category = "task_directive"
        else:
            technique = "authority_pressure"
            pressure_category = category

        findings.append(
            ExecutiveImpersonationFinding(
                technique=technique,  # type: ignore[arg-type]
                claimed_principal_role=principal_role,
                domain_relationship="not_applicable",
                pressure_category=pressure_category,  # type: ignore[arg-type]
                evidence=_PRESSURE_EVIDENCE[category],
            )
        )

    return findings


# ---------------------------------------------------------------------------
# Scoring (§3.3 / §10.A Q4)
# ---------------------------------------------------------------------------


def _compute_score_and_lift(
    *,
    identity_findings: list[ExecutiveImpersonationFinding],
    pressure_findings: list[ExecutiveImpersonationFinding],
) -> tuple[int, int]:
    if not identity_findings:
        return 0, 0

    pressure_categories = {
        finding.pressure_category
        for finding in pressure_findings
        if finding.pressure_category != "none"
    }
    has_corroborating_pressure = bool(
        pressure_categories.intersection({"authority", "secrecy", "urgency"})
    )
    has_task_directive = "task_directive" in pressure_categories

    if has_corroborating_pressure and has_task_directive:
        return _SCORE_STRONG, _LIFT_STRONG

    return _SCORE_PROBABLE, _LIFT_PROBABLE


def _order_findings(
    findings: list[ExecutiveImpersonationFinding],
) -> list[ExecutiveImpersonationFinding]:
    order_index = {
        technique: index for index, technique in enumerate(_FINDING_TECHNIQUE_ORDER)
    }

    def sort_key(finding: ExecutiveImpersonationFinding) -> tuple[int, str]:
        technique_rank = order_index.get(finding.technique, len(_FINDING_TECHNIQUE_ORDER))
        if finding.technique == "authority_pressure":
            return (technique_rank, finding.pressure_category)
        return (technique_rank, "")

    return sorted(findings, key=sort_key)


def _empty_assessment() -> ExecutiveImpersonationAssessment:
    return ExecutiveImpersonationAssessment(
        fired=False,
        executive_impersonation_score=0,
        findings=(),
        recommended_risk_floor_lift=0,
    )


__all__ = [
    "EXECUTIVE_IMPERSONATION_PATTERN_FLAG",
    "PrincipalRosterEntry",
    "detect_executive_impersonation",
]
