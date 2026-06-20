#!/usr/bin/env python3
"""MMI Superintendent — Mode A read-only advisory match/deviation reporter.

Compares built work against the Architect blueprint and signed contract evidence.
Stdout only. Does not approve, authorize, promote, gate, route, assign, build,
or mutate lifecycle state.

Authority: Matt dispatch 2026-06-20 (MMI_SUPERINTENDENT_MODE_A_BUILD_ONLY).
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ENVELOPE_REPORT = "SUPERINTENDENT_REPORT"
ENVELOPE_INSUFFICIENT = "INPUTS_INSUFFICIENT_CANNOT_CHECK"

ADVISORY_MATCHES = "MATCHES_BLUEPRINT"
ADVISORY_DEVIATES = "DEVIATES_FROM_BLUEPRINT"
ADVISORY_INSUFFICIENT = "INPUTS_INSUFFICIENT"

FORBIDDEN_CONCLUSIONS = frozenset(
    {
        "APPROVED",
        "AUTHORIZED",
        "BUILD_AUTHORIZED",
        "PROMOTED",
        "GATED",
        "GOVERNED_AGENT",
        "COMPLETE",
        "VERIFIED",
        "PASS",
        "FAIL",
        "NEXT_DECIDED",
    }
)

CHECK_MATCH = "MATCH"
CHECK_DEVIATION = "DEVIATION"
CHECK_MISSING = "MISSING"
CHECK_NOT_CHECKED = "NOT_CHECKED"

UNITTEST_MODULE_RE = re.compile(r"unittest\s+([\w.]+)")
AUDIT_OUTPUT_RE = re.compile(r"audit_outputs/[\w._-]+\.md")
SCOREBOARD_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|")

BLEED_MARKERS: dict[str, tuple[str, ...]] = {
    "#47": (
        "Plain-English Explanation",
        "plain_english_explanation",
        "tests.test_client_facing_rubric",
        "client_facing_rubric.py",
        "selected_candidate: #52",
        "candidate_id: #52",
    ),
    "#52": (
        "case_timeline_agent",
        "Case Timeline",
        "test_case_timeline_agent",
        "selected_candidate: #47",
        "candidate_id: #47",
    ),
}

OTHER_CANDIDATE_IDS = ("#1", "#3", "#6", "#8", "#10", "#11", "#14", "#23", "#24")


@dataclass
class CheckResult:
    id: str
    expected: str
    observed: str
    status: str


@dataclass
class Analysis:
    candidate_id: str
    envelope: str
    advisory_result: str = ""
    contract_status: str = "MISSING"
    blueprint_status: str = "MISSING"
    implementation_files: list[tuple[str, str]] = field(default_factory=list)
    test_files: list[tuple[str, str]] = field(default_factory=list)
    gate_artifact: str = ""
    gate_artifact_status: str = "NOT_REFERENCED"
    checks: list[CheckResult] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_architect_module():
    script = Path(__file__).resolve().parent / "mmi_architect.py"
    spec = importlib.util.spec_from_file_location("mmi_architect", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_architect"] = module
    spec.loader.exec_module(module)
    return module


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _run_architect(repo_root: Path, candidate_id: str) -> tuple[int, str]:
    script = Path(__file__).resolve().parent / "mmi_architect.py"
    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--candidate",
            candidate_id,
            "--root",
            str(repo_root),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout


def _unittest_module_to_path(module: str) -> str:
    parts = module.split(".")
    if len(parts) < 2 or "tests" not in parts:
        return ""
    tests_idx = parts.index("tests")
    dir_parts = parts[:tests_idx]
    file_name = parts[-1] + ".py"
    if dir_parts and dir_parts[0].isdigit() and len(dir_parts) > 1:
        head = f"{dir_parts[0]}. {dir_parts[1]}"
        mid = "/".join(dir_parts[2:])
        base = head + (f"/{mid}" if mid else "")
    else:
        base = "/".join(dir_parts)
    return f"{base}/tests/{file_name}"


def _extract_file_exists_targets(conditions: list[str]) -> list[str]:
    targets: list[str] = []
    for cond in conditions:
        lower = cond.lower()
        if lower.startswith("file_exists:"):
            targets.append(cond.split(":", 1)[1].strip())
    return targets


def _extract_command_expect_targets(conditions: list[str]) -> list[str]:
    targets: list[str] = []
    for cond in conditions:
        lower = cond.lower()
        if not lower.startswith("command_expect:"):
            continue
        match = UNITTEST_MODULE_RE.search(cond)
        if not match:
            continue
        path = _unittest_module_to_path(match.group(1))
        if path:
            targets.append(path)
    return targets


def _scoreboard_row_text(scoreboard: str, agent_num: str) -> str:
    prefix = f"| {agent_num} |"
    for line in scoreboard.splitlines():
        if line.startswith(prefix):
            return line
    return ""


def _gate_artifacts_from_sources(contract_text: str, scoreboard_row: str) -> list[str]:
    artifacts: list[str] = []
    for text in (contract_text, scoreboard_row):
        for match in AUDIT_OUTPUT_RE.finditer(text):
            path = match.group(0)
            if path not in artifacts:
                artifacts.append(path)
    return artifacts


def _blueprint_conditions(blueprint: str) -> list[str]:
    conditions: list[str] = []
    in_section = False
    for line in blueprint.splitlines():
        if line.strip() == "section: 3 BUILD CONDITIONS":
            in_section = True
            continue
        if in_section and line.startswith("section:"):
            break
        if in_section and line.startswith("condition:"):
            payload = line.split(":", 1)[1].strip()
            if payload.startswith("CHECK:"):
                conditions.append(payload[6:].strip())
    return conditions


def _add_check(
    checks: list[CheckResult],
    id_: str,
    expected: str,
    observed: str,
    status: str,
) -> None:
    checks.append(
        CheckResult(id=id_, expected=expected, observed=observed, status=status)
    )


def analyze(repo_root: Path, candidate_id: str) -> Analysis:
    architect = _load_architect_module()
    result = Analysis(candidate_id=candidate_id, envelope=ENVELOPE_INSUFFICIENT)

    manifest = architect.CANDIDATE_MANIFEST.get(candidate_id)
    if manifest is None:
        result.gaps.append(f"unknown_candidate: {candidate_id}")
        result.advisory_result = ADVISORY_INSUFFICIENT
        return result

    contract_rel = manifest.agent_contract_rel
    contract_path = repo_root / contract_rel
    if contract_path.is_file():
        result.contract_status = "PRESENT"
        _add_check(
            result.checks,
            "contract_exists",
            contract_rel,
            "file present on disk",
            CHECK_MATCH,
        )
    else:
        result.contract_status = "MISSING"
        _add_check(
            result.checks,
            "contract_exists",
            contract_rel,
            "file missing on disk",
            CHECK_MISSING,
        )
        result.gaps.append(f"missing_contract: {contract_rel}")
        result.advisory_result = ADVISORY_INSUFFICIENT
        return result

    parsed = architect._parse_agent_contract(contract_path)
    if not parsed.build_conditions:
        _add_check(
            result.checks,
            "build_conditions_exist",
            "BUILD CONDITIONS with CHECK lines",
            "section missing or empty",
            CHECK_MISSING,
        )
        result.gaps.append("missing_build_conditions_section")
        result.advisory_result = ADVISORY_INSUFFICIENT
        return result

    _add_check(
        result.checks,
        "build_conditions_exist",
        "BUILD CONDITIONS with CHECK lines",
        f"{len(parsed.build_conditions)} CHECK lines parsed",
        CHECK_MATCH,
    )

    if parsed.flow:
        _add_check(
            result.checks,
            "flow_contract_exists",
            "FLOW CONTRACT table fields populated",
            f"{len(parsed.flow)} fields parsed",
            CHECK_MATCH,
        )
    else:
        _add_check(
            result.checks,
            "flow_contract_exists",
            "FLOW CONTRACT table fields populated",
            "FLOW CONTRACT missing or empty",
            CHECK_MISSING,
        )
        result.gaps.append("missing_flow_contract")

    code, blueprint = _run_architect(repo_root, candidate_id)
    if code == 0 and blueprint.startswith("BLUEPRINT"):
        result.blueprint_status = "PRESENT"
        _add_check(
            result.checks,
            "architect_blueprint",
            "Architect emits BLUEPRINT envelope",
            "BLUEPRINT envelope received",
            CHECK_MATCH,
        )
    else:
        result.blueprint_status = "MISSING"
        _add_check(
            result.checks,
            "architect_blueprint",
            "Architect emits BLUEPRINT envelope",
            "INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT or empty output",
            CHECK_MISSING,
        )
        result.gaps.append("architect_cannot_blueprint")
        result.advisory_result = ADVISORY_INSUFFICIENT
        return result

    if f"candidate_id: {candidate_id}" not in blueprint:
        _add_check(
            result.checks,
            "blueprint_candidate_id",
            f"candidate_id: {candidate_id}",
            "candidate_id mismatch or missing",
            CHECK_DEVIATION,
        )
    else:
        _add_check(
            result.checks,
            "blueprint_candidate_id",
            f"candidate_id: {candidate_id}",
            f"candidate_id: {candidate_id}",
            CHECK_MATCH,
        )

    bleed_hits = [
        marker
        for marker in BLEED_MARKERS.get(candidate_id, ())
        if marker in blueprint
    ]
    wrong_candidates = [
        other
        for other in OTHER_CANDIDATE_IDS
        if other != candidate_id and f"selected_candidate: {other}" in blueprint
    ]
    if bleed_hits or wrong_candidates:
        observed = ", ".join(bleed_hits + wrong_candidates)
        _add_check(
            result.checks,
            "blueprint_candidate_specific",
            "no cross-candidate bleed in blueprint",
            observed,
            CHECK_DEVIATION,
        )
    else:
        _add_check(
            result.checks,
            "blueprint_candidate_specific",
            "no cross-candidate bleed in blueprint",
            "no bleed markers detected",
            CHECK_MATCH,
        )

    blueprint_conds = _blueprint_conditions(blueprint)
    contract_set = {c.strip() for c in parsed.build_conditions}
    blueprint_set = {c.strip() for c in blueprint_conds}
    if contract_set == blueprint_set:
        _add_check(
            result.checks,
            "blueprint_build_conditions_align",
            "blueprint BUILD CONDITIONS match contract",
            "condition sets match",
            CHECK_MATCH,
        )
    else:
        _add_check(
            result.checks,
            "blueprint_build_conditions_align",
            "blueprint BUILD CONDITIONS match contract",
            "condition sets differ",
            CHECK_DEVIATION,
        )

    file_targets = _extract_file_exists_targets(parsed.build_conditions)
    impl_paths: list[str] = []
    test_paths: list[str] = []
    for rel in file_targets:
        path = repo_root / rel
        is_test = "/tests/" in rel.replace("\\", "/")
        status = "PRESENT" if path.is_file() else "MISSING"
        if is_test:
            test_paths.append((rel, status))
        else:
            impl_paths.append((rel, status))
        check_status = CHECK_MATCH if status == "PRESENT" else CHECK_MISSING
        _add_check(
            result.checks,
            f"file_exists:{rel}",
            rel,
            status.lower(),
            check_status,
        )

    result.implementation_files = impl_paths
    result.test_files = test_paths

    command_targets = _extract_command_expect_targets(parsed.build_conditions)
    for rel in command_targets:
        path = repo_root / rel
        status = "PRESENT" if path.is_file() else "MISSING"
        if rel not in {p for p, _ in test_paths}:
            result.test_files.append((rel, status))
        check_status = CHECK_MATCH if status == "PRESENT" else CHECK_MISSING
        _add_check(
            result.checks,
            f"test_command_target:{rel}",
            rel,
            status.lower(),
            check_status,
        )

    scoreboard_path = repo_root / "agent_concepts" / "Blue_Team_Swarm_70_Agent_Scoreboard.md"
    scoreboard = _read_text(scoreboard_path)
    agent_num = candidate_id.lstrip("#")
    scoreboard_row = _scoreboard_row_text(scoreboard, agent_num)
    gate_artifacts = _gate_artifacts_from_sources(parsed.text, scoreboard_row)
    if gate_artifacts:
        for artifact in gate_artifacts:
            path = repo_root / artifact
            status = "PRESENT" if path.is_file() else "MISSING"
            if not result.gate_artifact:
                result.gate_artifact = artifact
                result.gate_artifact_status = status
            check_status = CHECK_MATCH if status == "PRESENT" else CHECK_MISSING
            _add_check(
                result.checks,
                f"gate_artifact:{artifact}",
                artifact,
                status.lower(),
                check_status,
            )
    else:
        result.gate_artifact_status = "NOT_REFERENCED"
        _add_check(
            result.checks,
            "gate_artifact_referenced",
            "gate artifact path if referenced",
            "no gate artifact referenced in contract or scoreboard row",
            CHECK_NOT_CHECKED,
        )

    for semantic in parsed.build_conditions:
        lower = semantic.lower()
        if lower.startswith("format_exact:") or lower.startswith("consumer_named:"):
            _add_check(
                result.checks,
                f"semantic:{semantic[:40]}",
                semantic,
                "semantic check deferred in Mode A",
                CHECK_NOT_CHECKED,
            )

    _add_check(
        result.checks,
        "no_blueprint_of_record_write",
        "superintendent does not write BLUEPRINT_OF_RECORD",
        "Mode A stdout-only; no file writes",
        CHECK_NOT_CHECKED,
    )
    _add_check(
        result.checks,
        "no_lifecycle_mutation",
        "superintendent does not mutate scoreboard/registry/dispatcher",
        "Mode A stdout-only; no lifecycle writes",
        CHECK_NOT_CHECKED,
    )

    has_missing = any(c.status == CHECK_MISSING for c in result.checks)
    has_deviation = any(c.status == CHECK_DEVIATION for c in result.checks)
    if has_missing or has_deviation:
        result.envelope = ENVELOPE_REPORT
        result.advisory_result = ADVISORY_DEVIATES
    else:
        result.envelope = ENVELOPE_REPORT
        result.advisory_result = ADVISORY_MATCHES

    return result


def _summary_counts(checks: list[CheckResult]) -> tuple[int, int, int, int]:
    matches = sum(1 for c in checks if c.status == CHECK_MATCH)
    deviations = sum(1 for c in checks if c.status == CHECK_DEVIATION)
    missing = sum(1 for c in checks if c.status == CHECK_MISSING)
    not_checked = sum(1 for c in checks if c.status == CHECK_NOT_CHECKED)
    return matches, deviations, missing, not_checked


def format_insufficient(candidate_id: str, gaps: list[str]) -> str:
    lines = [
        ENVELOPE_INSUFFICIENT,
        f"candidate_id: {candidate_id}",
        "gaps:",
    ]
    for gap in gaps:
        lines.append(f"  - {gap}")
    lines.append(f"advisory_result: {ADVISORY_INSUFFICIENT}")
    return _validate_output("\n".join(lines) + "\n")


def format_report(analysis: Analysis) -> str:
    matches, deviations, missing, not_checked = _summary_counts(analysis.checks)
    lines = [
        ENVELOPE_REPORT,
        f"candidate_id: {analysis.candidate_id}",
        f"contract_status: {analysis.contract_status}",
        f"blueprint_status: {analysis.blueprint_status}",
        "implementation_files:",
    ]
    for rel, status in analysis.implementation_files:
        lines.append(f"  - path: {rel}")
        lines.append(f"    status: {status}")
    lines.append("test_files:")
    for rel, status in analysis.test_files:
        lines.append(f"  - path: {rel}")
        lines.append(f"    status: {status}")
    if analysis.gate_artifact:
        lines.append(f"gate_artifact: {analysis.gate_artifact}")
        lines.append(f"gate_artifact_status: {analysis.gate_artifact_status}")
    else:
        lines.append("gate_artifact:")
        lines.append(f"gate_artifact_status: {analysis.gate_artifact_status}")
    lines.append("checks:")
    for check in analysis.checks:
        lines.append(f"  - id: {check.id}")
        lines.append(f"    expected: {check.expected}")
        lines.append(f"    observed: {check.observed}")
        lines.append(f"    status: {check.status}")
    lines.extend(
        [
            "summary:",
            f"  matches: {matches}",
            f"  deviations: {deviations}",
            f"  missing: {missing}",
            f"  not_checked: {not_checked}",
            f"advisory_result: {analysis.advisory_result}",
        ]
    )
    return _validate_output("\n".join(lines) + "\n")


def _validate_output(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped in FORBIDDEN_CONCLUSIONS:
            raise RuntimeError(f"forbidden conclusion token on output line: {stripped}")
        if stripped.startswith("advisory_result:"):
            value = stripped.split(":", 1)[1].strip()
            if value in FORBIDDEN_CONCLUSIONS:
                raise RuntimeError(
                    f"forbidden advisory_result token: {value}"
                )
        if stripped.startswith("VERDICT:"):
            raise RuntimeError("forbidden VERDICT line on superintendent output")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="MMI Superintendent Mode A — advisory blueprint match reporter (stdout only)."
    )
    parser.add_argument(
        "--candidate",
        required=True,
        help='Candidate id (e.g. "#47")',
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: repo root)",
    )
    args = parser.parse_args(argv)

    repo_root = args.root.resolve() if args.root else _repo_root()
    candidate_id = args.candidate.strip()
    analysis = analyze(repo_root, candidate_id)

    if analysis.envelope == ENVELOPE_INSUFFICIENT:
        sys.stdout.write(format_insufficient(candidate_id, analysis.gaps))
        return 2

    sys.stdout.write(format_report(analysis))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
