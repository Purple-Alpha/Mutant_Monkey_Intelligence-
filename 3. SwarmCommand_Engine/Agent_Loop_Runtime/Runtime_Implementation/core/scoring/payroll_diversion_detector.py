"""Payroll diversion detector — employee payroll / direct-deposit observation only.

Detect-not-enact: emits closed payroll vocabulary per §3 of the #22 contract.
No verdict, suppression, approval, or risk conclusions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

# Closed observation vocabulary (§3).
PAYROLL_DIVERSION_PATTERN: Final[str] = "payroll_diversion_pattern"
DIRECT_DEPOSIT_CHANGE_REQUEST: Final[str] = "direct_deposit_change_request"
PAYROLL_VOCABULARY_SIGNAL: Final[str] = "payroll_vocabulary_signal"
PAYROLL_MAILBOX_TARGET: Final[str] = "payroll_mailbox_target"
EMPLOYEE_PAYROLL_CHANGE_REFERENCE_PREFIX: Final[str] = "employee_payroll_change_reference"
EMPLOYEE_PAYROLL_SIGNAL_TYPE_PREFIX: Final[str] = "employee_payroll_signal_type"
PAYROLL_TIMING_PRESSURE: Final[str] = "payroll_timing_pressure"
PAYROLL_DIVERSION_FINDING_COUNT_PREFIX: Final[str] = "payroll_diversion_finding_count"

_FORBIDDEN_VERDICT_TOKENS: Final[frozenset[str]] = frozenset(
    {
        "low_risk",
        "safe",
        "suppression_applied",
        "approval_recommended",
    }
)

_DD_VOCAB_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:direct[\s-]?deposit|payroll[\s-]?(?:update|change|redirect|instruction)|"
    r"update\s+(?:my|the|your)\s+(?:bank|account))\b",
    re.IGNORECASE,
)

_NEGATED_DD_WINDOW_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:not|no|isn'?t|is\s+not|never)[^.!?\n]{0,80}"
    r"(?:direct[\s-]?deposit|payroll[\s-]?(?:update|change|redirect))",
    re.IGNORECASE,
)

_PAYROLL_VOCAB_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:payroll|timesheet|pay\s+run|payroll\s+run|payroll\s+cutoff)\b",
    re.IGNORECASE,
)

_TIMING_PRESSURE_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:before\s+(?:the\s+)?(?:next\s+)?payroll|by\s+cutoff|today\s+before|"
    r"end\s+of\s+business|by\s+5\s*pm)\b",
    re.IGNORECASE,
)

_ROUTING_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:routing(?:\s+(?:number|no\.?))?|aba)\b",
    re.IGNORECASE,
)

_IBAN_RE: Final[re.Pattern[str]] = re.compile(r"\biban\b", re.IGNORECASE)

_ACCOUNT_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:account|acct)(?:\s*(?:number|no\.?|#))?\b",
    re.IGNORECASE,
)

_MAX_SCAN_CHARS: Final[int] = 200_000


@dataclass(frozen=True)
class PayrollDiversionAssessment:
    """Detector output — closed payroll vocabulary only."""

    payroll_diversion_pattern: bool = False
    direct_deposit_change_request: bool = False
    payroll_vocabulary_signal: bool = False
    payroll_mailbox_target: bool = False
    employee_payroll_change_references: tuple[str, ...] = ()
    employee_payroll_signal_types: tuple[str, ...] = ()
    payroll_timing_pressure: bool = False

    def observation_facts(self) -> tuple[str, ...]:
        facts: list[str] = []
        if self.payroll_diversion_pattern:
            facts.append(PAYROLL_DIVERSION_PATTERN)
        if self.direct_deposit_change_request:
            facts.append(DIRECT_DEPOSIT_CHANGE_REQUEST)
        if self.payroll_vocabulary_signal:
            facts.append(PAYROLL_VOCABULARY_SIGNAL)
        if self.payroll_mailbox_target:
            facts.append(PAYROLL_MAILBOX_TARGET)
        for token in self.employee_payroll_change_references:
            facts.append(
                f"{EMPLOYEE_PAYROLL_CHANGE_REFERENCE_PREFIX}:employee_ref:{token}"
            )
        for signal_type in self.employee_payroll_signal_types:
            facts.append(f"{EMPLOYEE_PAYROLL_SIGNAL_TYPE_PREFIX}:{signal_type}")
        if self.payroll_timing_pressure:
            facts.append(PAYROLL_TIMING_PRESSURE)
        finding_count = len(facts)
        if finding_count:
            facts.append(f"{PAYROLL_DIVERSION_FINDING_COUNT_PREFIX}:{finding_count}")
        for fact in facts:
            if any(token in fact.lower() for token in _FORBIDDEN_VERDICT_TOKENS):
                raise ValueError(f"forbidden verdict token in observation fact: {fact}")
        return tuple(facts)


def _bounded(text: str) -> str:
    return (text or "")[:_MAX_SCAN_CHARS]


def _employee_refs_in_text(
    text: str,
    employee_token_roster: tuple[str, ...],
) -> tuple[str, ...]:
    refs: list[str] = []
    bounded = _bounded(text)
    for token in employee_token_roster:
        cleaned = token.strip()
        if not cleaned:
            continue
        pattern = re.compile(rf"\b{re.escape(cleaned)}\b", re.IGNORECASE)
        if pattern.search(bounded):
            refs.append(cleaned)
    return tuple(refs)


def _signal_types_in_text(text: str) -> tuple[str, ...]:
    bounded = _bounded(text)
    signals: list[str] = []
    if _ROUTING_RE.search(bounded):
        signals.append("routing_number")
    if _ACCOUNT_RE.search(bounded):
        signals.append("account_number")
    if _IBAN_RE.search(bounded):
        signals.append("iban")
    return tuple(signals)


def detect_payroll_diversion(
    *,
    body_plain: str | None = None,
    subject: str | None = None,
    attachment_extracted_texts: tuple[str, ...] = (),
    recipient: str | None = None,
    payroll_mailbox_roster: tuple[str, ...] = (),
    employee_token_roster: tuple[str, ...] = (),
) -> PayrollDiversionAssessment:
    """Scan inbound material and return closed payroll observation facts."""

    combined_parts = [subject or "", body_plain or ""]
    combined_parts.extend(attachment_extracted_texts)
    combined = "\n".join(part for part in combined_parts if part)

    payroll_vocab = bool(_PAYROLL_VOCAB_RE.search(combined))
    timing_pressure = bool(_TIMING_PRESSURE_RE.search(combined))
    negated_dd = bool(_NEGATED_DD_WINDOW_RE.search(combined))
    dd_vocab = bool(_DD_VOCAB_RE.search(combined))
    direct_deposit_request = dd_vocab and not negated_dd

    mailbox_target = False
    if recipient and payroll_mailbox_roster:
        recipient_lower = recipient.lower()
        for mailbox in payroll_mailbox_roster:
            if mailbox.strip().lower() in recipient_lower:
                mailbox_target = True
                break

    employee_refs = _employee_refs_in_text(combined, employee_token_roster)
    signal_types = _signal_types_in_text(combined)

    corroborators = bool(employee_refs) or bool(signal_types) or mailbox_target
    pattern = direct_deposit_request and corroborators

    return PayrollDiversionAssessment(
        payroll_diversion_pattern=pattern,
        direct_deposit_change_request=direct_deposit_request,
        payroll_vocabulary_signal=payroll_vocab,
        payroll_mailbox_target=mailbox_target,
        employee_payroll_change_references=employee_refs,
        employee_payroll_signal_types=signal_types,
        payroll_timing_pressure=timing_pressure,
    )


__all__ = [
    "DIRECT_DEPOSIT_CHANGE_REQUEST",
    "EMPLOYEE_PAYROLL_CHANGE_REFERENCE_PREFIX",
    "EMPLOYEE_PAYROLL_SIGNAL_TYPE_PREFIX",
    "PAYROLL_DIVERSION_FINDING_COUNT_PREFIX",
    "PAYROLL_DIVERSION_PATTERN",
    "PAYROLL_MAILBOX_TARGET",
    "PAYROLL_TIMING_PRESSURE",
    "PAYROLL_VOCABULARY_SIGNAL",
    "PayrollDiversionAssessment",
    "detect_payroll_diversion",
]
