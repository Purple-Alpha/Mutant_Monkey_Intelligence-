#!/usr/bin/env python3
"""MMI PM Console — Mode A read-only simplified status view (stdout only).

Summarizes current MMI state for Matt: what is happening, what is next,
what is blocked, and active blueprint status. Does not select, authorize,
build, promote, or mutate state.

Authority: Matt dispatch (MMI_PM_CONSOLE_AND_ACTIVE_BLUEPRINT_STATUS_MODE_A_BUILD_ONLY).
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ENVELOPE_CONSOLE = "MMI_PM_CONSOLE"
ENVELOPE_INSUFFICIENT = "INPUTS_INSUFFICIENT_CANNOT_RENDER_PM_CONSOLE"

BLUEPRINT_PATH_REL = "mmi/BLUEPRINT_OF_RECORD.md"

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

PLAN_STATUS_RE = re.compile(
    r"plan_status\s*:\s*(CURRENT_PLAN|DRAFT_PLAN|SUPERSEDED_PLAN)",
    re.IGNORECASE,
)


@dataclass
class ConsoleState:
    dispatcher_mode: str = "UNKNOWN"
    buildable_count: int = 0
    menu_envelope: str = ""
    top_options: list = field(default_factory=list)
    missing_contract_count: int = 0
    already_built_count: int = 0
    blueprint_status: str = "BLUEPRINT_FILE_MISSING"
    blueprint_detail: str = ""
    gaps: list[str] = field(default_factory=list)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parent


def _load_next_lane_module():
    script = _scripts_dir() / "mmi_next_lane.py"
    spec = importlib.util.spec_from_file_location("mmi_next_lane", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_next_lane"] = module
    spec.loader.exec_module(module)
    return module


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _parse_routing_mode(state_text: str) -> str:
    for line in state_text.splitlines():
        if not line.strip():
            break
        if line.startswith("MODE:"):
            return line.split(":", 1)[1].strip()
    return "UNKNOWN"


def _parse_blueprint_status(blueprint_text: str, file_exists: bool) -> tuple[str, str]:
    if not file_exists:
        return "BLUEPRINT_FILE_MISSING", "mmi/BLUEPRINT_OF_RECORD.md not found on disk."

    lower = blueprint_text.lower()
    statuses = [m.group(1).upper() for m in PLAN_STATUS_RE.finditer(blueprint_text)]
    current_count = sum(1 for s in statuses if s == "CURRENT_PLAN")
    draft_count = sum(1 for s in statuses if s == "DRAFT_PLAN")

    if current_count > 1:
        return (
            "MULTIPLE_CURRENT_PLANS_VIOLATION",
            f"Found {current_count} CURRENT_PLAN markers in {BLUEPRINT_PATH_REL}.",
        )
    if current_count == 1:
        return (
            "CURRENT_PLAN_PRESENT",
            "A CURRENT_PLAN block is present in mmi/BLUEPRINT_OF_RECORD.md.",
        )
    if draft_count > 0:
        return (
            "DRAFT_PLAN_PRESENT_NOT_ACTIVE",
            "DRAFT_PLAN present but no CURRENT_PLAN is active.",
        )
    if "not populated" in lower or "population deferred" in lower:
        return (
            "NO_CURRENT_PLAN",
            "Placeholder shell only; no CURRENT_PLAN content is active.",
        )
    return (
        "NO_CURRENT_PLAN",
        "No CURRENT_PLAN marker found in mmi/BLUEPRINT_OF_RECORD.md.",
    )


def _option_note(option) -> str:
    if option.recommended_matt_action == "HOLD_MISSING_CONTRACT":
        return "candidate requires signed contract before buildability"
    if option.recommended_matt_action == "HOLD_ALREADY_BUILT":
        return "already built or gated; hold unless Matt directs rework"
    if option.recommended_matt_action == "AUTHORIZE_ARCHITECT_BLUEPRINT":
        return "buildable; Matt authorization needed before blueprint lane"
    if option.recommended_matt_action == "REVIEW_REQUIRED":
        return "awaiting audit review"
    return option.reason_summary.split(".")[0]


def gather_state(repo_root: Path, menu_limit: int = 10) -> ConsoleState:
    state = ConsoleState()
    state_path = repo_root / "MMI_CURRENT_STATE.md"
    state_text = _read_text(state_path)
    if not state_text.strip():
        state.gaps.append("missing_dispatcher_state: MMI_CURRENT_STATE.md")
    else:
        state.dispatcher_mode = _parse_routing_mode(state_text)

    blueprint_path = repo_root / BLUEPRINT_PATH_REL
    blueprint_text = _read_text(blueprint_path)
    status, detail = _parse_blueprint_status(blueprint_text, blueprint_path.is_file())
    state.blueprint_status = status
    state.blueprint_detail = detail

    try:
        next_lane = _load_next_lane_module()
        envelope, options, gaps = next_lane.build_menu(repo_root, menu_limit)
        state.menu_envelope = envelope
        if gaps:
            state.gaps.extend(gaps)
        else:
            state.buildable_count = sum(
                1 for o in options if o.buildability_status == "BUILDABLE"
            )
            state.missing_contract_count = sum(
                1 for o in options if o.buildability_status == "BLOCKED_MISSING_CONTRACT"
            )
            state.already_built_count = sum(
                1 for o in options if o.buildability_status == "EXCLUDED_ALREADY_BUILT"
            )
            state.top_options = options[:3]
    except Exception as exc:  # pragma: no cover - surfaced as gap
        state.gaps.append(f"next_lane_failed: {exc}")

    return state


def _now_line(state: ConsoleState) -> str:
    if state.dispatcher_mode == "ALL_CLEAR":
        return "No active build in progress. Dispatcher is ALL_CLEAR."
    return f"Dispatcher mode is {state.dispatcher_mode}. No autonomous routing."


def _next_line(state: ConsoleState) -> str:
    if state.buildable_count == 0:
        return "No buildable candidates are currently available."
    return f"{state.buildable_count} buildable candidate(s) available for Matt review."


def _blocked_line(state: ConsoleState) -> str:
    if state.missing_contract_count:
        return (
            "Top candidates are blocked because signed Agent Design Contracts "
            "are missing."
        )
    if state.already_built_count and not state.missing_contract_count:
        return "Candidates are mostly already built or gated; no open build lane."
    if state.gaps:
        return "Blocked state could not be fully derived; see gaps in details mode."
    return "No dominant blocker identified in current menu snapshot."


def _matt_decision_line(state: ConsoleState) -> str:
    if state.buildable_count > 0:
        return (
            "Choose one buildable candidate for Matt-authorized blueprint or build lane, "
            "or hold."
        )
    if state.missing_contract_count:
        return "Choose one missing-contract candidate for contract drafting, or hold."
    return "Hold, or run detail commands to inspect a specific candidate."


def _active_blueprint_line(state: ConsoleState) -> str:
    base = f"{state.blueprint_status}: {state.blueprint_detail}"
    if state.blueprint_status == "NO_CURRENT_PLAN":
        base += (
            " Nothing is currently in the active build pipe. "
            "If candidates are blocked by missing contracts, the next real action "
            "is contract drafting."
        )
    return base


def _detail_commands() -> str:
    return (
        "python3 scripts/mmi_next_lane.py\n"
        "python3 scripts/mmi_crew_chain.py --candidate \"#47\""
    )


def format_console(state: ConsoleState, plain: bool = False, details: bool = False) -> str:
    lines = [ENVELOPE_CONSOLE]
    if plain:
        lines.extend(
            [
                f"NOW: {_now_line(state)}",
                f"NEXT: {_next_line(state)}",
                f"BLOCKED: {_blocked_line(state)}",
                f"MATT_DECISION: {_matt_decision_line(state)}",
                f"ACTIVE_BLUEPRINT: {_active_blueprint_line(state)}",
            ]
        )
    else:
        lines.extend(
            [
                "NOW:",
                f"  {_now_line(state)}",
                "NEXT:",
                f"  {_next_line(state)}",
                "BLOCKED:",
                f"  {_blocked_line(state)}",
                "MATT_DECISION:",
                f"  {_matt_decision_line(state)}",
                "ACTIVE_BLUEPRINT:",
                f"  {_active_blueprint_line(state)}",
            ]
        )

    if state.top_options:
        lines.append("TOP_DECISION_OPTIONS:")
        for index, option in enumerate(state.top_options, start=1):
            note = _option_note(option)
            lines.append(
                f"  {index}. {option.candidate_id} {option.candidate_name} — "
                f"{option.recommended_matt_action} — {note}"
            )

    if plain:
        lines.append(f"DETAIL_COMMANDS: {_detail_commands().replace(chr(10), ' | ')}")
    else:
        lines.append("DETAIL_COMMANDS:")
        for cmd in _detail_commands().splitlines():
            lines.append(f"  {cmd}")

    if details:
        lines.append("---")
        lines.append("details:")
        lines.append(f"  dispatcher_mode: {state.dispatcher_mode}")
        lines.append(f"  menu_envelope: {state.menu_envelope}")
        lines.append(f"  buildable_count: {state.buildable_count}")
        lines.append(
            f"  missing_contract_count: {state.missing_contract_count}"
        )
        lines.append(f"  already_built_count: {state.already_built_count}")
        lines.append(f"  blueprint_status: {state.blueprint_status}")
        if state.gaps:
            lines.append("  gaps:")
            for gap in state.gaps:
                lines.append(f"    - {gap}")
        lines.append("  detail_commands:")
        for cmd in _detail_commands().splitlines():
            lines.append(f"    {cmd}")
        lines.append("  next_lane_command: python3 scripts/mmi_next_lane.py --limit 10")
        lines.append(
            "  crew_chain_example: python3 scripts/mmi_crew_chain.py --candidate \"#47\""
        )

    return _validate_output("\n".join(lines) + "\n")


def format_insufficient(gaps: list[str]) -> str:
    lines = [ENVELOPE_INSUFFICIENT, "gaps:"]
    for gap in gaps:
        lines.append(f"  - {gap}")
    return _validate_output("\n".join(lines) + "\n")


def _validate_output(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped in FORBIDDEN_CONCLUSIONS:
            raise RuntimeError(f"forbidden conclusion token: {stripped}")
        if stripped.startswith("VERDICT:"):
            raise RuntimeError("forbidden VERDICT line on PM console output")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="MMI PM Console Mode A — simplified read-only status (stdout only)."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: repo root)",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Include extended context blocks",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Single-line section values",
    )
    args = parser.parse_args(argv)

    repo_root = args.root.resolve() if args.root else _repo_root()
    state = gather_state(repo_root, menu_limit=10)

    if any(g.startswith("missing_dispatcher_state") for g in state.gaps):
        sys.stdout.write(format_insufficient(state.gaps))
        return 2

    sys.stdout.write(format_console(state, plain=args.plain, details=args.details))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
