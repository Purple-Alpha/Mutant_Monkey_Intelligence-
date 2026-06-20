#!/usr/bin/env python3
"""MMI Project Manager — Mode A read-only Matt-facing decision summary.

Consumes dispatcher state, scoreboard lifecycle, Estimator, Architect, and
Superintendent outputs. Emits advisory PROCEED / REVISE / HOLD labels only.
Stdout only. Does not authorize, route, assign, build, promote, or mutate state.

Authority: Matt dispatch 2026-06-20 (MMI_PROJECT_MANAGER_MODE_A_BUILD_ONLY).
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ENVELOPE_REPORT = "PROJECT_MANAGER_REPORT"
ENVELOPE_INSUFFICIENT = "INPUTS_INSUFFICIENT_CANNOT_SUMMARIZE"

ADVISORY_PROCEED = "PROCEED_FOR_MATT_REVIEW"
ADVISORY_REVISE = "REVISE_BEFORE_MATT_REVIEW"
ADVISORY_HOLD = "HOLD_FOR_MISSING_INPUTS"

FORBIDDEN_CONCLUSIONS = frozenset(
    {
        "AUTHORIZED",
        "APPROVED",
        "BUILD_AUTHORIZED",
        "PROMOTED",
        "GATED",
        "GOVERNED_AGENT",
        "COMPLETE",
        "VERIFIED",
        "PASS",
        "FAIL",
        "NEXT_DECIDED",
        "AUTONOMOUSLY_SELECTED",
    }
)

LIFECYCLE_CLOSED = frozenset({"GATED", "GOVERNED_AGENT", "INFRASTRUCTURE_BUILT"})
BLOCKING_COUNT_RE = re.compile(
    r"blocking\s*(?:deviations)?\s*[:=]\s*`?(\d+)`?",
    re.IGNORECASE,
)
GATE_SUMMARY_RE = re.compile(r"GATE_SUMMARY:\s*blocking=(\d+)", re.IGNORECASE)
AUDIT_OUTPUT_RE = re.compile(r"audit_outputs/[\w._-]+\.md")


@dataclass
class Analysis:
    candidate_id: str
    envelope: str = ENVELOPE_INSUFFICIENT
    lifecycle_state: str = "UNKNOWN"
    dispatcher_mode: str = "UNKNOWN"
    estimator_status: str = "UNKNOWN"
    architect_status: str = "MISSING"
    superintendent_status: str = "MISSING"
    gate_status: str = "NOT_REFERENCED"
    gate_artifact: str = ""
    boundary_status: str = ""
    decision_summary: str = ""
    advisory_result: str = ADVISORY_HOLD
    matt_action_required: str = ""
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


def _run_script(script_name: str, repo_root: Path, args: list[str]) -> tuple[int, str]:
    script = Path(__file__).resolve().parent / script_name
    proc = subprocess.run(
        [sys.executable, str(script), *args, "--root", str(repo_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout


def _extract_line_value(text: str, key: str) -> str:
    for line in text.splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    return ""


def _parse_routing_mode(state_text: str) -> str:
    for line in state_text.splitlines():
        if not line.strip():
            break
        if line.startswith("MODE:"):
            return line.split(":", 1)[1].strip()
    return "UNKNOWN"


def _strip_ticks(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        return value.strip("`").strip()
    return value


def _runtime_status_token(cell: str) -> str:
    cell = _strip_ticks(cell.strip())
    for prefix in (
        "GOVERNED_AGENT",
        "GATED",
        "INFRASTRUCTURE_BUILT",
        "SIGNED_UNBUILT",
        "AWAITING_AUDIT",
        "DETECTOR_FUNCTION",
        "SPEC_ONLY",
        "NOT_STARTED",
    ):
        if cell.startswith(prefix):
            return prefix
    return cell.split()[0] if cell else "UNKNOWN"


def _scoreboard_row(scoreboard: str, agent_num: str) -> tuple[str, str]:
    prefix = f"| {agent_num} |"
    for line in scoreboard.splitlines():
        if line.startswith(prefix):
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if len(parts) >= 3:
                return line, parts[2]
    return "", ""


def _estimator_candidate_status(estimator_output: str, candidate_id: str) -> str:
    if estimator_output.startswith("STATE_INCOMPLETE_CANNOT_SCORE"):
        return "STATE_INCOMPLETE_CANNOT_SCORE"
    if estimator_output.startswith("NO_BUILDABLE_CANDIDATES"):
        return "NO_BUILDABLE_CANDIDATES"
    blocks = estimator_output.split("---")
    for block in blocks:
        if _extract_line_value(block, "candidate_id") == candidate_id:
            reason = _extract_line_value(block, "reason")
            prefix = _extract_line_value(block, "runtime_status_prefix")
            if reason and prefix:
                return f"{reason} (source_lifecycle: {prefix})"
            if reason:
                return reason
            return "FOUND_IN_ESTIMATOR_OUTPUT"
    if estimator_output.startswith("SCORED_CANDIDATES"):
        if f"candidate_id: {candidate_id}" in estimator_output:
            return "SCORED_BUILDABLE"
        return "NOT_IN_SCORED_LIST"
    return "NOT_FOUND_IN_ESTIMATOR_OUTPUT"


def _gate_blocking_count(gate_text: str) -> int | None:
    for pattern in (GATE_SUMMARY_RE, BLOCKING_COUNT_RE):
        match = pattern.search(gate_text)
        if match:
            return int(match.group(1))
    return None


def _boundary_notes(lifecycle_token: str, status_cell: str, code_evidence: str) -> str:
    notes: list[str] = []
    if lifecycle_token == "GOVERNED_AGENT":
        notes.append("source_lifecycle is GOVERNED_AGENT")
    else:
        notes.append("not GOVERNED_AGENT")
    lower = (status_cell + " " + code_evidence).lower()
    if "production dispatch" in lower and "no production" not in lower:
        notes.append("production dispatch referenced")
    else:
        notes.append("no production dispatch")
    if "build_default_registry" in lower or "default registry" in lower:
        if "not in" in lower or "not in `build_default_registry`" in lower:
            notes.append("not in default registry")
        else:
            notes.append("default registry reference present")
    else:
        notes.append("not in default registry")
    notes.append("no autonomous routing")
    notes.append("AUTH-5 blocked")
    return "; ".join(notes)


def analyze(repo_root: Path, candidate_id: str) -> Analysis:
    architect_mod = _load_architect_module()
    result = Analysis(candidate_id=candidate_id)

    manifest = architect_mod.CANDIDATE_MANIFEST.get(candidate_id)
    if manifest is None:
        result.gaps.append(f"unknown_candidate: {candidate_id}")
        result.advisory_result = ADVISORY_HOLD
        return result

    state_path = repo_root / "MMI_CURRENT_STATE.md"
    state_text = _read_text(state_path)
    if state_text.strip():
        result.dispatcher_mode = _parse_routing_mode(state_text)
    else:
        result.gaps.append("missing_dispatcher_state: MMI_CURRENT_STATE.md")
        result.dispatcher_mode = "UNAVAILABLE"

    scoreboard_path = repo_root / "agent_concepts" / "Blue_Team_Swarm_70_Agent_Scoreboard.md"
    scoreboard = _read_text(scoreboard_path)
    agent_num = candidate_id.lstrip("#")
    row_line, status_cell = _scoreboard_row(scoreboard, agent_num)
    code_evidence = ""
    if not row_line:
        result.gaps.append(f"missing_scoreboard_row: {candidate_id}")
        result.lifecycle_state = "UNREADABLE"
    else:
        token = _runtime_status_token(status_cell)
        result.lifecycle_state = f"{token} (scoreboard source)"
        parts = [p.strip() for p in row_line.strip().strip("|").split("|")]
        code_evidence = parts[3] if len(parts) > 3 else ""
        result.boundary_status = _boundary_notes(
            token, _strip_ticks(status_cell), code_evidence
        )

    est_code, est_out = _run_script("mmi_estimator.py", repo_root, [])
    if est_code == 0 or est_out.strip():
        result.estimator_status = _estimator_candidate_status(est_out, candidate_id)
    else:
        result.estimator_status = "UNAVAILABLE"
        result.gaps.append("estimator_output_unavailable")

    arch_code, arch_out = _run_script(
        "mmi_architect.py", repo_root, ["--candidate", candidate_id]
    )
    if arch_code == 0 and arch_out.startswith("BLUEPRINT"):
        result.architect_status = "BLUEPRINT"
    elif arch_out.startswith("INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT"):
        result.architect_status = "INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT"
        result.gaps.append("architect_cannot_blueprint")
    else:
        result.architect_status = "MISSING"
        result.gaps.append("architect_output_missing")

    sup_code, sup_out = _run_script(
        "mmi_superintendent.py", repo_root, ["--candidate", candidate_id]
    )
    if sup_out.startswith("SUPERINTENDENT_REPORT"):
        advisory = _extract_line_value(sup_out, "advisory_result")
        result.superintendent_status = advisory or "SUPERINTENDENT_REPORT"
        gate_artifact = _extract_line_value(sup_out, "gate_artifact")
        gate_status_field = _extract_line_value(sup_out, "gate_artifact_status")
        if gate_artifact:
            result.gate_artifact = gate_artifact
    elif sup_out.startswith("INPUTS_INSUFFICIENT_CANNOT_CHECK"):
        result.superintendent_status = "INPUTS_INSUFFICIENT_CANNOT_CHECK"
        result.gaps.append("superintendent_cannot_check")
    else:
        result.superintendent_status = "MISSING"
        result.gaps.append("superintendent_output_missing")

    lifecycle_token = _runtime_status_token(status_cell) if status_cell else "UNKNOWN"
    gate_refs: list[str] = []
    if result.gate_artifact:
        gate_refs.append(result.gate_artifact)
    for text in (row_line, status_cell, code_evidence if row_line else ""):
        for match in AUDIT_OUTPUT_RE.finditer(text):
            path = match.group(0)
            if path not in gate_refs:
                gate_refs.append(path)
    if gate_refs and not result.gate_artifact:
        result.gate_artifact = gate_refs[0]

    if result.gate_artifact:
        gate_path = repo_root / result.gate_artifact
        if not gate_path.is_file():
            result.gate_status = "MISSING"
            result.gaps.append(f"missing_gate_artifact: {result.gate_artifact}")
        else:
            gate_text = _read_text(gate_path)
            blockers = _gate_blocking_count(gate_text)
            if blockers is None:
                result.gate_status = "PRESENT_UNPARSED"
            elif blockers == 0:
                result.gate_status = "CLEAN"
            else:
                result.gate_status = f"BLOCKERS_{blockers}"
                result.gaps.append(f"gate_has_blockers: {blockers}")
    elif lifecycle_token in LIFECYCLE_CLOSED:
        result.gate_status = "MISSING_FOR_CLOSED_LIFECYCLE"
        result.gaps.append("gate_artifact_missing_for_closed_lifecycle")
    else:
        result.gate_status = "NOT_REFERENCED"

    bleed_deviation = (
        "id: blueprint_candidate_specific" in sup_out
        and "status: DEVIATION" in sup_out
    )

    hold_gaps = (
        "architect_cannot_blueprint" in result.gaps
        or "superintendent_cannot_check" in result.gaps
        or "missing_scoreboard_row" in result.gaps
        or result.dispatcher_mode in ("UNKNOWN", "UNAVAILABLE")
        or result.gate_status == "MISSING_FOR_CLOSED_LIFECYCLE"
        or (
            lifecycle_token in LIFECYCLE_CLOSED
            and result.gate_status == "MISSING"
        )
    )
    if hold_gaps:
        result.envelope = (
            ENVELOPE_INSUFFICIENT if not row_line else ENVELOPE_REPORT
        )
        result.advisory_result = ADVISORY_HOLD
        result.decision_summary = (
            f"{candidate_id} evidence is incomplete for Matt-facing summary. "
            f"Gaps: {', '.join(result.gaps)}."
        )
        result.matt_action_required = (
            "Matt should supply missing evidence or run the missing crew role "
            "before treating this as ready for review."
        )
    elif (
        result.superintendent_status == "DEVIATES_FROM_BLUEPRINT"
        or bleed_deviation
        or result.gate_status.startswith("BLOCKERS_")
    ):
        result.envelope = ENVELOPE_REPORT
        result.advisory_result = ADVISORY_REVISE
        result.decision_summary = (
            f"{candidate_id} has crew evidence mismatch or gate blockers. "
            f"Superintendent={result.superintendent_status}; "
            f"gate_status={result.gate_status}."
        )
        result.matt_action_required = (
            "Matt should review deviations before any promotion or new lane."
        )
    elif (
        result.architect_status == "BLUEPRINT"
        and result.superintendent_status == "MATCHES_BLUEPRINT"
        and lifecycle_token != "UNKNOWN"
        and result.dispatcher_mode != "UNAVAILABLE"
        and (
            result.gate_status in ("CLEAN", "NOT_REFERENCED", "PRESENT_UNPARSED")
            or (
                lifecycle_token in LIFECYCLE_CLOSED
                and result.gate_status == "CLEAN"
            )
        )
        and lifecycle_token != "GOVERNED_AGENT"
    ):
        result.envelope = ENVELOPE_REPORT
        result.advisory_result = ADVISORY_PROCEED
        gate_note = (
            f"completion gate clean at {result.gate_artifact}"
            if result.gate_status == "CLEAN" and result.gate_artifact
            else f"gate_status={result.gate_status}"
        )
        result.decision_summary = (
            f"{candidate_id} is {lifecycle_token} Mode A, {gate_note}, "
            f"Superintendent matched build to blueprint, dispatcher is "
            f"{result.dispatcher_mode}. No autonomous next action is taken. "
            f"Matt may choose either to hold, consider governed-agent promotion "
            f"later, or ask MMI for next lane discovery."
        )
        if lifecycle_token == "GATED":
            result.matt_action_required = (
                "No further action is required unless Matt wants GOVERNED_AGENT "
                "promotion or another lane."
            )
        else:
            result.matt_action_required = (
                "Matt review only; PM does not authorize build or promotion."
            )
    else:
        result.envelope = ENVELOPE_REPORT
        result.advisory_result = ADVISORY_HOLD
        result.decision_summary = (
            f"{candidate_id} crew evidence is present but not aligned for proceed. "
            f"architect={result.architect_status}; "
            f"superintendent={result.superintendent_status}; "
            f"lifecycle={result.lifecycle_state}."
        )
        result.matt_action_required = (
            "Matt should resolve missing or conflicting evidence before proceed."
        )

    if not result.boundary_status and status_cell:
        parts = [p.strip() for p in row_line.strip().strip("|").split("|")]
        code_evidence = parts[3] if len(parts) > 3 else ""
        result.boundary_status = _boundary_notes(
            _runtime_status_token(status_cell), status_cell, code_evidence
        )

    return result


def format_insufficient(candidate_id: str, gaps: list[str]) -> str:
    lines = [
        ENVELOPE_INSUFFICIENT,
        f"candidate_id: {candidate_id}",
        "gaps:",
    ]
    for gap in gaps:
        lines.append(f"  - {gap}")
    lines.append(f"advisory_result: {ADVISORY_HOLD}")
    return _validate_output("\n".join(lines) + "\n")


def format_report(analysis: Analysis) -> str:
    lines = [
        ENVELOPE_REPORT,
        f"candidate_id: {analysis.candidate_id}",
        f"lifecycle_state: {analysis.lifecycle_state}",
        f"dispatcher_mode: {analysis.dispatcher_mode}",
        f"estimator_status: {analysis.estimator_status}",
        f"architect_status: {analysis.architect_status}",
        f"superintendent_status: {analysis.superintendent_status}",
        f"gate_status: {analysis.gate_status}",
        f"boundary_status: {analysis.boundary_status}",
        f"decision_summary: {analysis.decision_summary}",
        f"advisory_result: {analysis.advisory_result}",
        f"matt_action_required: {analysis.matt_action_required}",
    ]
    if analysis.gate_artifact:
        lines.insert(8, f"gate_artifact: {analysis.gate_artifact}")
    return _validate_output("\n".join(lines) + "\n")


def _validate_output(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped in FORBIDDEN_CONCLUSIONS:
            raise RuntimeError(f"forbidden conclusion token on output line: {stripped}")
        if stripped.startswith("advisory_result:"):
            value = stripped.split(":", 1)[1].strip()
            if value in FORBIDDEN_CONCLUSIONS:
                raise RuntimeError(f"forbidden advisory_result token: {value}")
        if stripped.startswith("VERDICT:"):
            raise RuntimeError("forbidden VERDICT line on project manager output")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="MMI Project Manager Mode A — advisory Matt-facing summary (stdout only)."
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

    if analysis.envelope == ENVELOPE_INSUFFICIENT and not analysis.decision_summary:
        sys.stdout.write(format_insufficient(candidate_id, analysis.gaps))
        return 2

    sys.stdout.write(format_report(analysis))
    if analysis.advisory_result == ADVISORY_HOLD and analysis.envelope == ENVELOPE_INSUFFICIENT:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
