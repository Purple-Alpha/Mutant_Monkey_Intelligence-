#!/usr/bin/env python3
"""MMI Crew Chain — Mode A read-only terminal runner.

Runs or summarizes the crew role chain in order: Dispatcher state, Estimator,
Architect, Superintendent, Project Manager, then a Matt-facing advisory summary.
Stdout only. Does not authorize, route, build, promote, or mutate state.

Authority: Matt dispatch (MMI_CREW_CHAIN_TERMINAL_RUNNER_MODE_A_BUILD_ONLY).
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ENVELOPE_REPORT = "MMI_CREW_CHAIN_REPORT"
ENVELOPE_INSUFFICIENT = "INPUTS_INSUFFICIENT_CANNOT_RUN_CHAIN"

FORBIDDEN_CONCLUSIONS = frozenset(
    {
        "AUTHORIZED",
        "APPROVED",
        "BUILD_AUTHORIZED",
        "PROMOTED",
        "GOVERNED_AGENT",
        "COMPLETE",
        "VERIFIED",
        "NEXT_DECIDED",
        "AUTONOMOUSLY_SELECTED",
    }
)

CHAIN_SECTIONS = (
    "section: 1 DISPATCHER",
    "section: 2 ESTIMATOR",
    "section: 3 ARCHITECT",
    "section: 4 SUPERINTENDENT",
    "section: 5 PROJECT_MANAGER",
    "section: 6 MATT_ADVISORY_SUMMARY",
)


@dataclass
class ChainResult:
    candidate_id: str
    envelope: str = ENVELOPE_INSUFFICIENT
    dispatcher_mode: str = "UNKNOWN"
    authorized_task: str = ""
    estimator_status: str = "UNKNOWN"
    architect_status: str = "MISSING"
    architect_envelope: str = ""
    superintendent_status: str = "MISSING"
    superintendent_envelope: str = ""
    project_manager_status: str = "MISSING"
    project_manager_envelope: str = ""
    lifecycle_state: str = "UNKNOWN"
    gate_status: str = "NOT_REFERENCED"
    gate_artifact: str = ""
    boundary_status: str = ""
    advisory_summary: str = ""
    matt_action_required: str = ""
    gaps: list[str] = field(default_factory=list)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parent


def _load_architect_module():
    script = _scripts_dir() / "mmi_architect.py"
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


def _extract_line_value(text: str, key: str) -> str:
    for line in text.splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    return ""


def _parse_routing_block(state_text: str) -> tuple[str, str]:
    mode = "UNKNOWN"
    authorized_task = ""
    for line in state_text.splitlines():
        if not line.strip():
            break
        if line.startswith("MODE:"):
            mode = line.split(":", 1)[1].strip()
        elif line.startswith("AUTHORIZED_TASK:"):
            authorized_task = line.split(":", 1)[1].strip()
    return mode, authorized_task


def _run_script(script_name: str, repo_root: Path, args: list[str]) -> tuple[int, str]:
    script = _scripts_dir() / script_name
    proc = subprocess.run(
        [sys.executable, str(script), *args, "--root", str(repo_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout


def _run_script_no_root(script_name: str, args: list[str]) -> tuple[int, str]:
    script = _scripts_dir() / script_name
    proc = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout


def _strip_ticks(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        return value.strip("`").strip()
    return value


def _lifecycle_token(lifecycle_state: str) -> str:
    text = lifecycle_state.split("(")[0].strip()
    return _strip_ticks(text)


def _estimator_candidate_status(estimator_output: str, candidate_id: str) -> str:
    if estimator_output.startswith("STATE_INCOMPLETE_CANNOT_SCORE"):
        return "STATE_INCOMPLETE_CANNOT_SCORE"
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
    if f"candidate_id: {candidate_id}" in estimator_output:
        return "FOUND_IN_ESTIMATOR_OUTPUT"
    return "NOT_FOUND_IN_ESTIMATOR_OUTPUT"


def _build_advisory_summary(result: ChainResult) -> str:
    lifecycle = _lifecycle_token(result.lifecycle_state)
    parts: list[str] = [f"{result.candidate_id} is {lifecycle} Mode A."]
    if result.gate_status == "CLEAN":
        parts.append("The completion gate is clean.")
    elif result.gate_status != "NOT_REFERENCED":
        parts.append(f"Gate status is {result.gate_status}.")
    if result.superintendent_status == "MATCHES_BLUEPRINT":
        parts.append("Superintendent matched the build to the blueprint.")
    elif result.superintendent_status:
        parts.append(f"Superintendent status is {result.superintendent_status}.")
    if result.project_manager_status == "PROCEED_FOR_MATT_REVIEW":
        parts.append("Project Manager says PROCEED_FOR_MATT_REVIEW.")
    elif result.project_manager_status:
        parts.append(f"Project Manager status is {result.project_manager_status}.")
    parts.append("No autonomous next action is taken.")
    return " ".join(parts)


def analyze(repo_root: Path, candidate_id: str) -> ChainResult:
    architect_mod = _load_architect_module()
    result = ChainResult(candidate_id=candidate_id)

    if architect_mod.CANDIDATE_MANIFEST.get(candidate_id) is None:
        result.gaps.append(f"unknown_candidate: {candidate_id}")
        return result

    state_text = _read_text(repo_root / "MMI_CURRENT_STATE.md")
    if state_text.strip():
        result.dispatcher_mode, result.authorized_task = _parse_routing_block(state_text)
    else:
        result.gaps.append("missing_dispatcher_state: MMI_CURRENT_STATE.md")

    est_code, est_out = _run_script_no_root("mmi_estimator.py", [])
    if est_out.strip():
        result.estimator_status = _estimator_candidate_status(est_out, candidate_id)
    else:
        result.estimator_status = "UNAVAILABLE"
        result.gaps.append("estimator_output_unavailable")

    arch_code, arch_out = _run_script(
        "mmi_architect.py", repo_root, ["--candidate", candidate_id]
    )
    if arch_code == 0 and arch_out.startswith("BLUEPRINT"):
        result.architect_status = "BLUEPRINT"
        result.architect_envelope = "BLUEPRINT"
    elif arch_out.startswith("INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT"):
        result.architect_status = "INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT"
        result.architect_envelope = "INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT"
        result.gaps.append("architect_cannot_blueprint")
    else:
        result.architect_status = "MISSING"
        result.gaps.append("architect_output_missing")

    sup_code, sup_out = _run_script(
        "mmi_superintendent.py", repo_root, ["--candidate", candidate_id]
    )
    if sup_out.startswith("SUPERINTENDENT_REPORT"):
        result.superintendent_envelope = "SUPERINTENDENT_REPORT"
        advisory = _extract_line_value(sup_out, "advisory_result")
        result.superintendent_status = advisory or "SUPERINTENDENT_REPORT"
        result.gate_artifact = _extract_line_value(sup_out, "gate_artifact")
    elif sup_out.startswith("INPUTS_INSUFFICIENT_CANNOT_CHECK"):
        result.superintendent_status = "INPUTS_INSUFFICIENT_CANNOT_CHECK"
        result.superintendent_envelope = "INPUTS_INSUFFICIENT_CANNOT_CHECK"
        result.gaps.append("superintendent_cannot_check")
    else:
        result.superintendent_status = "MISSING"
        result.gaps.append("superintendent_output_missing")

    pm_code, pm_out = _run_script(
        "mmi_project_manager.py", repo_root, ["--candidate", candidate_id]
    )
    if pm_out.startswith("PROJECT_MANAGER_REPORT"):
        result.project_manager_envelope = "PROJECT_MANAGER_REPORT"
        result.project_manager_status = _extract_line_value(pm_out, "advisory_result")
        result.lifecycle_state = _extract_line_value(pm_out, "lifecycle_state")
        result.gate_status = _extract_line_value(pm_out, "gate_status")
        if not result.gate_artifact:
            result.gate_artifact = _extract_line_value(pm_out, "gate_artifact")
        result.boundary_status = _extract_line_value(pm_out, "boundary_status")
        result.matt_action_required = _extract_line_value(pm_out, "matt_action_required")
    elif pm_out.startswith("INPUTS_INSUFFICIENT_CANNOT_SUMMARIZE"):
        result.project_manager_envelope = "INPUTS_INSUFFICIENT_CANNOT_SUMMARIZE"
        result.project_manager_status = "INPUTS_INSUFFICIENT_CANNOT_SUMMARIZE"
        result.gaps.append("project_manager_cannot_summarize")
    else:
        result.project_manager_status = "MISSING"
        result.gaps.append("project_manager_output_missing")

    if result.gaps and (
        "unknown_candidate" in result.gaps
        or "architect_cannot_blueprint" in result.gaps
        or "superintendent_cannot_check" in result.gaps
        or "project_manager_cannot_summarize" in result.gaps
    ):
        return result

    result.envelope = ENVELOPE_REPORT
    result.boundary_status = (
        result.boundary_status or "no autonomous action; Matt remains authority"
    )
    if "no autonomous" not in result.boundary_status.lower():
        result.boundary_status = (
            f"{result.boundary_status}; no autonomous action; Matt remains authority"
        )
    result.advisory_summary = _build_advisory_summary(result)
    if not result.matt_action_required:
        result.matt_action_required = (
            "Matt remains authority; crew output is advisory only."
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
    return _validate_output("\n".join(lines) + "\n")


def format_report(result: ChainResult, plain: bool = False) -> str:
    if plain:
        lines = [
            ENVELOPE_REPORT,
            f"candidate_id: {result.candidate_id}",
            f"dispatcher_mode: {result.dispatcher_mode}",
            f"estimator_status: {result.estimator_status}",
            f"architect_status: {result.architect_status}",
            f"superintendent_status: {result.superintendent_status}",
            f"project_manager_status: {result.project_manager_status}",
            f"gate_status: {result.gate_status}",
            f"boundary_status: {result.boundary_status}",
            f"advisory_summary: {result.advisory_summary}",
            f"matt_action_required: {result.matt_action_required}",
        ]
        return _validate_output("\n".join(lines) + "\n")

    lines = [
        ENVELOPE_REPORT,
        f"candidate_id: {result.candidate_id}",
        "---",
        CHAIN_SECTIONS[0],
        f"dispatcher_mode: {result.dispatcher_mode}",
        f"authorized_task: {result.authorized_task}",
        "---",
        CHAIN_SECTIONS[1],
        f"crew_status: {result.estimator_status}",
        "---",
        CHAIN_SECTIONS[2],
        f"crew_status: {result.architect_status}",
        f"envelope: {result.architect_envelope or result.architect_status}",
        "---",
        CHAIN_SECTIONS[3],
        f"crew_status: {result.superintendent_status}",
        f"envelope: {result.superintendent_envelope or result.superintendent_status}",
    ]
    if result.gate_artifact:
        lines.append(f"gate_artifact: {result.gate_artifact}")
    lines.extend(
        [
            "---",
            CHAIN_SECTIONS[4],
            f"crew_status: {result.project_manager_status}",
            f"envelope: {result.project_manager_envelope or result.project_manager_status}",
            f"source_lifecycle: {_lifecycle_token(result.lifecycle_state)}",
            f"gate_status: {result.gate_status}",
            "---",
            CHAIN_SECTIONS[5],
            f"advisory_summary: {result.advisory_summary}",
            f"matt_action_required: {result.matt_action_required}",
            "boundary_status: no autonomous action; Matt remains authority",
            f"pm_boundary_detail: {result.boundary_status}",
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
                raise RuntimeError(f"forbidden advisory_result token: {value}")
        if stripped.startswith("VERDICT:"):
            raise RuntimeError("forbidden VERDICT line on crew chain output")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="MMI Crew Chain Mode A — read-only terminal runner (stdout only)."
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
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Compact output without section headers",
    )
    args = parser.parse_args(argv)

    repo_root = args.root.resolve() if args.root else _repo_root()
    candidate_id = args.candidate.strip()
    result = analyze(repo_root, candidate_id)

    if result.envelope == ENVELOPE_INSUFFICIENT:
        sys.stdout.write(format_insufficient(candidate_id, result.gaps))
        return 2

    sys.stdout.write(format_report(result, plain=args.plain))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
