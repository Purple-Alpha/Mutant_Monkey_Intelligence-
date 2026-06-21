#!/usr/bin/env python3
"""MMI Next Lane — Mode A read-only decision menu (stdout only).

Shows Matt-facing candidate options from Estimator buildability evidence.
Does not select, authorize, route, assign, build, promote, or mutate state.

Authority: Matt dispatch (MMI_NEXT_LANE_DECISION_MENU_MODE_A_BUILD_ONLY).
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

ENVELOPE_MENU = "MMI_NEXT_LANE_DECISION_MENU"
ENVELOPE_NO_BUILDABLE = "NO_BUILDABLE_CANDIDATES"
ENVELOPE_INSUFFICIENT = "INPUTS_INSUFFICIENT_CANNOT_BUILD_MENU"

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

REASON_PRIORITY = {
    "BLOCKED_MISSING_CONTRACT": 0,
    "EXCLUDED_NON_BUILDABLE_STATE": 1,
    "EXCLUDED_ALREADY_BUILT": 2,
}

ACTION_FROM_REASON = {
    "EXCLUDED_ALREADY_BUILT": "HOLD_ALREADY_BUILT",
    "BLOCKED_MISSING_CONTRACT": "HOLD_MISSING_CONTRACT",
    "EXCLUDED_NON_BUILDABLE_STATE": "HOLD_NOT_BUILDABLE",
}


@dataclass
class MenuOption:
    candidate_id: str
    candidate_name: str
    source_lifecycle: str
    buildability_status: str
    contract_status: str
    reason_summary: str
    recommended_matt_action: str
    sort_rank: float = 0.0
    exclusion_rank: int = 99


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_estimator_module():
    script = Path(__file__).resolve().parent / "mmi_estimator.py"
    spec = importlib.util.spec_from_file_location("mmi_estimator", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mmi_estimator"] = module
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


def _contract_status(cand, root: Path, estimator_mod) -> str:
    contract_rel = estimator_mod._resolve_agent_design_contract(cand)
    if contract_rel and (root / contract_rel).is_file():
        return "PRESENT"
    if contract_rel:
        return "MISSING"
    return "UNKNOWN"


def _menu_from_scored(item, root: Path, estimator_mod) -> MenuOption:
    cand = item.candidate
    lifecycle = cand.runtime_status or "UNKNOWN"
    contract_status = _contract_status(cand, root, estimator_mod)
    if lifecycle == "SIGNED_UNBUILT":
        action = "AUTHORIZE_ARCHITECT_BLUEPRINT"
        summary = (
            "Candidate appears buildable and requires Matt authorization "
            "before Architect blueprint or build lane."
        )
    elif lifecycle == "AWAITING_AUDIT":
        action = "REVIEW_REQUIRED"
        summary = "Candidate awaiting audit; Matt review required before further lane."
    else:
        action = "AUTHORIZE_BUILD_ONLY"
        summary = (
            "Candidate appears buildable; Matt authorization required before any next lane."
        )
    return MenuOption(
        candidate_id=cand.candidate_id,
        candidate_name=cand.name,
        source_lifecycle=lifecycle,
        buildability_status="BUILDABLE",
        contract_status=contract_status,
        reason_summary=summary,
        recommended_matt_action=action,
        sort_rank=-item.total_measured_score,
        exclusion_rank=-1,
    )


def _menu_from_exclusion(exclusion, root: Path, estimator_mod) -> MenuOption:
    cand = exclusion.candidate
    reason = exclusion.reason
    action = ACTION_FROM_REASON.get(reason, "HOLD_NOT_BUILDABLE")
    contract_rel = exclusion.missing_contract or estimator_mod._resolve_agent_design_contract(
        cand
    )
    if contract_rel and (root / contract_rel).is_file():
        contract_status = "PRESENT"
    elif reason == "BLOCKED_MISSING_CONTRACT" or exclusion.missing_contract:
        contract_status = "MISSING"
    else:
        contract_status = _contract_status(cand, root, estimator_mod)

    summaries = {
        "HOLD_ALREADY_BUILT": (
            "Candidate lifecycle is closed or already built; hold unless Matt "
            "directs promotion or rework."
        ),
        "HOLD_MISSING_CONTRACT": (
            "Signed Agent Design Contract missing on disk; hold until contract lane completes."
        ),
        "HOLD_NOT_BUILDABLE": (
            "Candidate not in a buildable lifecycle state for current breadth runway."
        ),
    }
    return MenuOption(
        candidate_id=cand.candidate_id,
        candidate_name=cand.name,
        source_lifecycle=exclusion.runtime_status_prefix,
        buildability_status=reason,
        contract_status=contract_status,
        reason_summary=summaries.get(action, summaries["HOLD_NOT_BUILDABLE"]),
        recommended_matt_action=action,
        sort_rank=0.0,
        exclusion_rank=REASON_PRIORITY.get(reason, 99),
    )


def build_menu(repo_root: Path, limit: int) -> tuple[str, list[MenuOption], list[str]]:
    estimator_mod = _load_estimator_module()
    scored, errors, _, exclusions, _ = estimator_mod.analyze(repo_root)
    if errors:
        return ENVELOPE_INSUFFICIENT, [], errors

    options: list[MenuOption] = []
    for item in scored:
        options.append(_menu_from_scored(item, repo_root, estimator_mod))

    exclusion_options = [
        _menu_from_exclusion(ex, repo_root, estimator_mod) for ex in exclusions
    ]
    exclusion_options.sort(
        key=lambda o: (o.exclusion_rank, o.candidate_id)
    )
    options.extend(exclusion_options)

    if not options:
        return ENVELOPE_NO_BUILDABLE, [], []

    options.sort(key=lambda o: (o.exclusion_rank, o.sort_rank, o.candidate_id))
    limited = options[:limit]
    return ENVELOPE_MENU, limited, []


def format_insufficient(gaps: list[str]) -> str:
    lines = [ENVELOPE_INSUFFICIENT, "gaps:"]
    for gap in gaps:
        lines.append(f"  - {gap}")
    lines.extend(
        [
            "authority_note: This is a decision menu only. MMI does not choose the next lane.",
            "authority_note: Matt remains authority. No autonomous routing or AUTH-5.",
        ]
    )
    return _validate_output("\n".join(lines) + "\n")


def format_no_buildable(dispatcher_mode: str) -> str:
    lines = [
        ENVELOPE_NO_BUILDABLE,
        f"dispatcher_mode: {dispatcher_mode}",
        "authority_boundary: advisory only; Matt chooses; no autonomous selection",
        "authority_note: This is a decision menu only. MMI does not choose the next lane.",
        "authority_note: Matt remains authority. No autonomous routing or AUTH-5.",
    ]
    return _validate_output("\n".join(lines) + "\n")


def format_menu(
    dispatcher_mode: str,
    options: list[MenuOption],
    plain: bool = False,
) -> str:
    buildable_count = sum(1 for o in options if o.buildability_status == "BUILDABLE")
    lines = [
        ENVELOPE_MENU,
        f"dispatcher_mode: {dispatcher_mode}",
        "authority_boundary: advisory only; Matt chooses; no autonomous selection",
        f"buildable_count: {buildable_count}",
        "authority_note: This is a decision menu only. MMI does not choose the next lane.",
        "authority_note: Matt remains authority. No autonomous routing or AUTH-5.",
    ]
    for index, option in enumerate(options, start=1):
        if plain:
            lines.append(
                f"option {index}: {option.candidate_id} {option.candidate_name} "
                f"{option.buildability_status} {option.recommended_matt_action}"
            )
            continue
        lines.append(f"option: {index}")
        lines.append(f"candidate_id: {option.candidate_id}")
        lines.append(f"candidate_name: {option.candidate_name}")
        lines.append(f"source_lifecycle: {option.source_lifecycle}")
        lines.append(f"buildability_status: {option.buildability_status}")
        lines.append(f"contract_status: {option.contract_status}")
        lines.append(f"recommended_matt_action: {option.recommended_matt_action}")
        lines.append(f"reason_summary: {option.reason_summary}")
        lines.append("---")
    if lines[-1] == "---":
        lines.pop()
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
            raise RuntimeError("forbidden VERDICT line on next lane output")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="MMI Next Lane Mode A — read-only decision menu (stdout only)."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum menu options to show (default: 10)",
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
        help="Compact one-line-per-option output",
    )
    args = parser.parse_args(argv)

    repo_root = args.root.resolve() if args.root else _repo_root()
    limit = max(1, args.limit)
    state_text = _read_text(repo_root / "MMI_CURRENT_STATE.md")
    dispatcher_mode = _parse_routing_mode(state_text) if state_text.strip() else "UNKNOWN"

    envelope, options, gaps = build_menu(repo_root, limit)

    if envelope == ENVELOPE_INSUFFICIENT:
        sys.stdout.write(format_insufficient(gaps))
        return 2
    if envelope == ENVELOPE_NO_BUILDABLE:
        sys.stdout.write(format_no_buildable(dispatcher_mode))
        return 0

    sys.stdout.write(format_menu(dispatcher_mode, options, plain=args.plain))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
