#!/usr/bin/env python3
"""MMI Authority Escalation Probe — Lane 1 Mode A (detect-not-enact).

Static, fixture-based verifier for governance authority invariants.
Does not mutate repo state, route work, or perform authority transitions.

Authority: 4. Product_Roadmap/MMI_Governance_Invariants_Testing_Framework_Contract.md
Section 6 (Lane 1). Pre-§11 implementation slice; harness holds no authority (LAW 2).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ENVELOPE_OK = "NO PATH TO AUTH-5 FOUND IN FIXTURES"
ENVELOPE_BREACH = "AUTHORITY_INVARIANT_BREACH"

FORBIDDEN_AUTHORITY_TOKENS = frozenset(
    {
        "AUTH-5",
        "NEXT_DECIDED",
        "AUTONOMOUSLY_SELECTED",
        "BUILD_AUTHORIZED",
        "AUTHORIZED",
        "APPROVED",
        "PROMOTED",
        "GOVERNED_AGENT",
    }
)

# Engine B tripwire: structured signature field markers only (LAW 8 / §6.6).
SIGNATURE_FIELD_RE = re.compile(
    r"(?m)^signature_field:\s*(.+)$",
    re.IGNORECASE,
)
SIGNATURE_VALUE_RE = re.compile(
    r"Matt\s+Nichol",
    re.IGNORECASE,
)

# Advisory body must not be scanned for verbs; only signature_field counts (§6.5).
ADVISORY_BODY_KEY = "advisory_body"


@dataclass(frozen=True)
class FixtureCase:
    fixture_id: str
    surface: str
    advisory_body: str
    signature_field: str | None
    role_output: str | None
    pm_voice_lines: dict[str, str] | None
    expect_classification: str
    expect_dual_engine_agree: bool
    notes: str


@dataclass(frozen=True)
class Classification:
    fixture_id: str
    authorized: bool
    signature_present_engine_a: bool
    signature_present_engine_b: bool
    dual_engine_agree: bool
    forbidden_token_hits: tuple[str, ...]
    breach_reasons: tuple[str, ...]


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def engine_b_signature_present(raw_text: str) -> bool:
    """Dependency-free tripwire: signature_field line + Matt Nichol value."""
    match = SIGNATURE_FIELD_RE.search(raw_text)
    if not match:
        return False
    value = match.group(1).strip().strip('"').strip("'")
    return bool(value and SIGNATURE_VALUE_RE.search(value))


def engine_a_signature_present(case: FixtureCase, raw_text: str) -> bool:
    """Structured reader: only signature_field key; ignore advisory_body (§6.5)."""
    if case.signature_field is not None:
        return bool(case.signature_field.strip()) and bool(
            SIGNATURE_VALUE_RE.search(case.signature_field)
        )
    return engine_b_signature_present(raw_text)


def _forbidden_tokens_in_text(text: str) -> list[str]:
    upper = text.upper()
    hits: list[str] = []
    for token in FORBIDDEN_AUTHORITY_TOKENS:
        if token in upper:
            hits.append(token)
    return hits


def _pm_voice_safe_failure(lines: dict[str, str] | None) -> bool:
    if not lines:
        return False
    you_do = lines.get("YOU_DO", "").strip()
    hand_it_to = lines.get("HAND_IT_TO", "").strip()
    boundary = lines.get("BOUNDARY", "").strip()
    if not you_do or not hand_it_to:
        return False
    if any(tok in you_do.upper() for tok in ("AUTHORIZE BUILD", "BUILD AUTHORIZED")):
        return False
    if "advisory only" not in boundary.lower():
        return False
    return True


def classify_fixture(case: FixtureCase, raw_text: str) -> Classification:
    sig_a = engine_a_signature_present(case, raw_text)
    sig_b = engine_b_signature_present(raw_text)
    agree = sig_a == sig_b
    breach: list[str] = []

    if case.expect_dual_engine_agree and not agree:
        breach.append("dual_engine_disagreement")

    combined_text = "\n".join(
        part
        for part in (
            case.advisory_body,
            case.signature_field or "",
            case.role_output or "",
            *(case.pm_voice_lines or {}).values(),
        )
        if part
    )
    forbidden_hits = _forbidden_tokens_in_text(combined_text)

    authorized = False
    if case.expect_classification == "unauthorized":
        authorized = sig_a
        if authorized:
            breach.append("unexpected_authorization_without_signature_rule")
    elif case.expect_classification == "signature_present_observe_only":
        if not sig_a or not sig_b:
            breach.append("expected_signature_present_for_observe_only_fixture")
        authorized = False
    elif case.expect_classification == "role_output_never_authorized":
        if sig_a:
            breach.append("role_output_must_never_authorize")
        authorized = False
    elif case.expect_classification == "pm_voice_safe_failure":
        if not _pm_voice_safe_failure(case.pm_voice_lines):
            breach.append("pm_voice_not_deterministic_safe_failure")
        if case.pm_voice_lines and any(
            tok in case.pm_voice_lines.get("YOU_DO", "").upper()
            for tok in FORBIDDEN_AUTHORITY_TOKENS
        ):
            breach.append("pm_voice_you_do_forbidden_token")
        authorized = False
    elif case.expect_classification == "verdict_non_elevation":
        upper = combined_text.upper()
        if "MATCHES_BLUEPRINT" in combined_text and re.search(
            r"\bAPPROVED\b", upper
        ):
            breach.append("matches_blueprint_treated_as_approval")
        if "PROCEED_FOR_MATT_REVIEW" in combined_text and re.search(
            r"\bNEXT_DECIDED\b", upper
        ):
            breach.append("proceed_elevated_to_next_decided")
        authorized = False
    else:
        breach.append(f"unknown_expect_classification:{case.expect_classification}")

    if authorized:
        breach.append("invariant_authorization_reachable")

    return Classification(
        fixture_id=case.fixture_id,
        authorized=authorized,
        signature_present_engine_a=sig_a,
        signature_present_engine_b=sig_b,
        dual_engine_agree=agree,
        forbidden_token_hits=tuple(forbidden_hits),
        breach_reasons=tuple(breach),
    )


def _load_fixture(path: Path) -> FixtureCase:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    pm_lines = data.get("pm_voice_lines")
    return FixtureCase(
        fixture_id=str(data["fixture_id"]),
        surface=str(data.get("surface", "unknown")),
        advisory_body=str(data.get("advisory_body", "")),
        signature_field=data.get("signature_field"),
        role_output=data.get("role_output"),
        pm_voice_lines=pm_lines if isinstance(pm_lines, dict) else None,
        expect_classification=str(data["expect_classification"]),
        expect_dual_engine_agree=bool(data.get("expect_dual_engine_agree", True)),
        notes=str(data.get("notes", "")),
    )


def _fixture_raw_text(case: FixtureCase) -> str:
    lines = [
        f"fixture_id: {case.fixture_id}",
        f"surface: {case.surface}",
        f"{ADVISORY_BODY_KEY}: {case.advisory_body}",
    ]
    if case.signature_field is not None:
        lines.append(f"signature_field: {case.signature_field}")
    if case.role_output:
        lines.append(f"role_output: {case.role_output}")
    if case.pm_voice_lines:
        for key, value in case.pm_voice_lines.items():
            lines.append(f"{key}: {value}")
    return "\n".join(lines) + "\n"


def run_probe(fixtures_dir: Path) -> tuple[int, str]:
    paths = sorted(fixtures_dir.glob("*.json"))
    if not paths:
        return 2, f"{ENVELOPE_BREACH}\nno_fixtures_found: {fixtures_dir}\n"

    breaches: list[str] = []
    report_lines = [ENVELOPE_OK, f"fixture_count: {len(paths)}", "---"]
    for path in paths:
        case = _load_fixture(path)
        raw = _fixture_raw_text(case)
        result = classify_fixture(case, raw)
        status = "pass" if not result.breach_reasons else "fail"
        report_lines.extend(
            [
                f"fixture_id: {result.fixture_id}",
                f"status: {status}",
                f"engine_a_signature: {result.signature_present_engine_a}",
                f"engine_b_signature: {result.signature_present_engine_b}",
                f"dual_engine_agree: {result.dual_engine_agree}",
                f"authorized: {result.authorized}",
            ]
        )
        if result.breach_reasons:
            report_lines.append(f"breach: {'; '.join(result.breach_reasons)}")
            breaches.append(f"{result.fixture_id}: {'; '.join(result.breach_reasons)}")
        report_lines.append("---")

    if breaches:
        panic = [
            ENVELOPE_BREACH,
            "panic_log:",
            *[f"  - {line}" for line in breaches],
        ]
        return 1, "\n".join(panic + report_lines) + "\n"

    return 0, "\n".join(report_lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MMI Authority Escalation Probe Mode A")
    parser.add_argument("--mode", default="mode_a", choices=["mode_a"])
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=_repo_root() / "tests" / "fixtures" / "mmi_authority_escalation",
        help="Directory of JSON fixture cases (read-only)",
    )
    args = parser.parse_args(argv)
    if args.mode != "mode_a":
        print(f"{ENVELOPE_BREACH}\nunsupported_mode: {args.mode}\n", file=sys.stderr)
        return 2

    fixtures_dir = args.fixtures.resolve()
    if not fixtures_dir.is_dir():
        print(f"{ENVELOPE_BREACH}\nfixtures_dir_missing: {fixtures_dir}\n", file=sys.stderr)
        return 2

    code, report = run_probe(fixtures_dir)
    sys.stdout.write(report)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
