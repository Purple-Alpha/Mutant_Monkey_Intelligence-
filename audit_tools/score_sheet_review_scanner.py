"""Shared no-PII / no-secrets scanner for score-sheet review surfaces.

Wave 3.1 requires one shared scanner module imported by both
``review_ledger.py`` and the score-sheet safety hook. Findings deliberately do
not echo matched sensitive values.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ALLOWED_DOMAIN_SUFFIXES = (".example", ".test", ".invalid", ".localhost")
ALLOWED_PLACEHOLDERS = (
    "redacted",
    "example",
    "test-secret",
    "account_placeholder",
    "routing_placeholder",
    "iban_placeholder",
    "acme-industries-demo",
    "bluefin-marine-supplies-demo",
)

BLOCK = "BLOCK"
WARN = "WARN"

_PRIVATE_KEY_RE = re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY", re.I)
_SECRET_ASSIGNMENT_RE = re.compile(
    r"\b(?:XAI_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|GITHUB_TOKEN|"
    r"GH_TOKEN|API_KEY|SECRET|PASSWORD)\s*=\s*"
    r"(?!(?:test-secret|redacted|example|ACCOUNT_PLACEHOLDER|"
    r"ROUTING_PLACEHOLDER|IBAN_PLACEHOLDER)\b)[^\s'\"#]+",
    re.I,
)
_BEARER_RE = re.compile(r"\bbearer\s+[A-Za-z0-9._~+/=-]{16,}", re.I)
_GITHUB_TOKEN_RE = re.compile(r"\bgh[opsu]_[A-Za-z0-9_]{20,}\b")
_MODEL_TOKEN_RE = re.compile(r"\b(?:sk|xai|ant)-[A-Za-z0-9_-]{20,}\b", re.I)
_AUTH_HEADER_RE = re.compile(r"^\s*authorization\s*:", re.I | re.M)

_IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")
_SWIFT_RE = re.compile(r"\b[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b")
_ROUTING_LABELED_RE = re.compile(
    r"\b(?:routing|aba|transit)\s*(?:number|no\.?|#|:)?\s*\d{9}\b",
    re.I,
)
_ACCOUNT_LABELED_RE = re.compile(
    r"\b(?:account|acct)\s*(?:number|no\.?|#|:)?\s*\d{6,17}\b",
    re.I,
)
_PAYMENT_CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")

_RAW_HEADER_RE = re.compile(
    r"^\s*(?:Received|Authentication-Results|DKIM-Signature|Return-Path|"
    r"Message-ID|Content-Type|From|To|Subject)\s*:",
    re.I | re.M,
)
_LIVE_TOKEN_URL_RE = re.compile(
    r"https?://(?![^/\s]*\.example\b)[^\s?]+"
    r"\?[^\s]*(?:token|key|secret|auth|session|signature)=",
    re.I,
)
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
_PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\d)"
)
_COT_RE = re.compile(r"\b(?:chain_of_thought|hidden_reasoning|private_reasoning)\b", re.I)


@dataclass(frozen=True)
class ScanFinding:
    severity: str
    finding_class: str
    path: str
    field: str
    reason: str
    remediation: str
    line_number: int | None = None
    row_index: int | None = None

    def format(self) -> str:
        parts = [self.severity, self.finding_class, f"path={self.path}"]
        if self.line_number is not None:
            parts.append(f"line={self.line_number}")
        if self.row_index is not None:
            parts.append(f"row={self.row_index}")
        if self.field:
            parts.append(f"field={self.field}")
        parts.append(f"reason={self.reason}")
        parts.append(f"remediation={self.remediation}")
        return " ".join(parts)


def _contains_allowed_placeholder(value: str) -> bool:
    normalized = value.lower()
    return any(token in normalized for token in ALLOWED_PLACEHOLDERS)


def _is_allowed_email_domain(domain: str) -> bool:
    lowered = domain.lower()
    return lowered.endswith(ALLOWED_DOMAIN_SUFFIXES)


def _luhn_ok(candidate: str) -> bool:
    digits = [int(ch) for ch in re.sub(r"\D", "", candidate)]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def scan_text(
    value: object,
    *,
    path: str,
    field: str = "",
    line_number: int | None = None,
    row_index: int | None = None,
) -> list[ScanFinding]:
    """Scan one value and return findings without echoing matched content."""
    if not isinstance(value, str) or not value:
        return []
    if _contains_allowed_placeholder(value):
        return []

    findings: list[ScanFinding] = []

    def add(severity: str, finding_class: str, reason: str, remediation: str) -> None:
        findings.append(
            ScanFinding(
                severity=severity,
                finding_class=finding_class,
                path=path,
                line_number=line_number,
                row_index=row_index,
                field=field,
                reason=reason,
                remediation=remediation,
            )
        )

    if _PRIVATE_KEY_RE.search(value):
        add(BLOCK, "secret", "private_key_block", "remove_secret_or_replace_with_test_placeholder")
    if (
        _SECRET_ASSIGNMENT_RE.search(value)
        or _BEARER_RE.search(value)
        or _GITHUB_TOKEN_RE.search(value)
        or _MODEL_TOKEN_RE.search(value)
        or _AUTH_HEADER_RE.search(value)
    ):
        add(BLOCK, "secret", "credential_like_string", "replace_with_test-secret_or_redacted")
    if _ROUTING_LABELED_RE.search(value):
        add(BLOCK, "raw_financial_identifier", "routing_number", "replace_with_ROUTING_PLACEHOLDER")
    if _ACCOUNT_LABELED_RE.search(value):
        add(BLOCK, "raw_financial_identifier", "account_number", "replace_with_ACCOUNT_PLACEHOLDER")
    if _IBAN_RE.search(value):
        add(BLOCK, "raw_financial_identifier", "iban_like_string", "replace_with_IBAN_PLACEHOLDER")
    if _SWIFT_RE.search(value):
        add(BLOCK, "raw_financial_identifier", "swift_bic_like_string", "replace_with_redacted")
    if any(_luhn_ok(match.group(0)) for match in _PAYMENT_CARD_RE.finditer(value)):
        add(BLOCK, "raw_financial_identifier", "payment_card_like_number", "replace_with_redacted")
    if _RAW_HEADER_RE.search(value):
        add(BLOCK, "raw_payload_leakage", "raw_message_header_marker", "summarize_without_raw_header")
    if _LIVE_TOKEN_URL_RE.search(value):
        add(BLOCK, "raw_payload_leakage", "live_url_with_query_token", "replace_with_example_url")
    if _COT_RE.search(value):
        add(BLOCK, "chain_of_thought_leakage", "reasoning_label", "remove_private_reasoning_label")

    for match in _EMAIL_RE.finditer(value):
        if not _is_allowed_email_domain(match.group(1)):
            add(WARN, "pii_marker", "real_email_address", "replace_with_example_domain")
            break
    if _PHONE_RE.search(value):
        add(WARN, "pii_marker", "phone_like_string", "replace_with_known_channel_placeholder")

    return findings


def scan_mapping(row: dict[str, object], *, path: str, row_index: int | None = None) -> list[ScanFinding]:
    findings: list[ScanFinding] = []
    for field, value in row.items():
        findings.extend(scan_text(value, path=path, field=field, row_index=row_index))
    return findings


def scan_file(path: str | Path) -> list[ScanFinding]:
    scan_path = Path(path)
    try:
        text = scan_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [
            ScanFinding(
                severity=BLOCK,
                finding_class="raw_payload_leakage",
                path=str(scan_path),
                field="",
                reason="non_utf8_text_surface",
                remediation="do_not_stage_binary_or_non_utf8_score_sheet_surface",
            )
        ]

    findings: list[ScanFinding] = []
    if scan_path.suffix == ".jsonl":
        for index, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                findings.extend(
                    scan_text(line, path=str(scan_path), line_number=index, row_index=index)
                )
                continue
            if isinstance(obj, dict):
                findings.extend(scan_mapping(obj, path=str(scan_path), row_index=index))
            else:
                findings.extend(
                    scan_text(line, path=str(scan_path), line_number=index, row_index=index)
                )
        return findings

    for index, line in enumerate(text.splitlines(), start=1):
        findings.extend(scan_text(line, path=str(scan_path), line_number=index))
    return findings


def has_blocking_findings(findings: list[ScanFinding]) -> bool:
    return any(finding.severity == BLOCK for finding in findings)


def format_findings(findings: list[ScanFinding]) -> str:
    return "\n".join(finding.format() for finding in findings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan score-sheet review surfaces for unsafe content.")
    parser.add_argument("paths", nargs="+", help="Files to scan")
    args = parser.parse_args(argv)

    all_findings: list[ScanFinding] = []
    for raw_path in args.paths:
        all_findings.extend(scan_file(raw_path))

    if all_findings:
        print(format_findings(all_findings))
    return 1 if has_blocking_findings(all_findings) else 0


if __name__ == "__main__":
    sys.exit(main())
