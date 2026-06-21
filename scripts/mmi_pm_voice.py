#!/usr/bin/env python3
"""MMI PM Voice Layer — Mode A read-only single-voice owner interface.

Reads existing MMI engines silently and emits one Matt-facing envelope.
Faithful relay only: every line traces to a named engine plus roster lookup.

Authority: mmi/MMI_PM_VOICE_LAYER_CONTRACT.md §11 signed 2026-06-20.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path

ENVELOPE_VOICE = "MMI_PM_VOICE"
ENVELOPE_INSUFFICIENT = "INPUTS_INSUFFICIENT_CANNOT_RENDER_PM_VOICE"

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
        "SELECTED",
    }
)

HIGH_RISK_CANDIDATE_IDS = frozenset({"#1", "#3"})
PREFERRED_CONTRACT_CANDIDATE = "#52"
PREFERRED_RECONCILE_CANDIDATE = "#52"
RECONCILE_YOU_DO = {
    "#52": "Authorize MMI_52_SIGNED_UNBUILT_RECONCILE_ONLY.",
}

BUILDABLE_LIFECYCLE_PREFIXES = ("SIGNED_UNBUILT", "AWAITING_AUDIT")
CLOSED_LIFECYCLE_PREFIXES = ("GATED", "GOVERNED_AGENT", "INFRASTRUCTURE_BUILT")

ROSTER_CONTRACT_DRAFT = "Claude"
ROSTER_BUILD = "Cursor"
ROSTER_REVIEW = "Codex"
ROSTER_RESEARCH = "Gemini+ChatGPT"
ROSTER_MATT = "Matt"

REVISION_ROWS = (
    (
        "What gets prioritized / ranked",
        "Estimator (mmi/MMI_ESTIMATOR_SCORING_CONTRACT.md; weights locked MMI-DEC-039)",
        "Yes — §11 amendment required",
    ),
    (
        "Buildability gates E12–E14",
        "Estimator amendment (MMI-DEC-045)",
        "Yes — signed amendment path",
    ),
    (
        "What done/flowing means for a build",
        "Architect / blueprint",
        "Yes — re-author via Architect",
    ),
    (
        "Who handles a task type",
        "Roster (contract Section 5)",
        "Yes — Matt edits roster in contract",
    ),
    (
        "Lifecycle routing rules",
        "Dispatcher doctrine",
        "Yes — signed amendment path",
    ),
    (
        "Whether something is authorized",
        "Matt only",
        "Always Matt's authority",
    ),
)


@dataclass
class VoiceEvidence:
    dispatcher_mode: str = "UNKNOWN"
    blueprint_status: str = "UNKNOWN"
    buildable_count: int = 0
    missing_contract_count: int = 0
    menu_options: list = field(default_factory=list)
    scored_first: str = ""
    scored_first_name: str = ""
    gaps: list[str] = field(default_factory=list)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parent


def _load_module(name: str, filename: str):
    script = _scripts_dir() / filename
    spec = importlib.util.spec_from_file_location(name, script)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def gather_evidence(repo_root: Path, menu_limit: int = 30) -> VoiceEvidence:
    evidence = VoiceEvidence()
    pm_console = _load_module("mmi_pm_console", "mmi_pm_console.py")
    next_lane = _load_module("mmi_next_lane", "mmi_next_lane.py")
    estimator = _load_module("mmi_estimator", "mmi_estimator.py")

    console_state = pm_console.gather_state(repo_root, menu_limit=menu_limit)
    evidence.dispatcher_mode = console_state.dispatcher_mode
    evidence.blueprint_status = console_state.blueprint_status
    evidence.buildable_count = console_state.buildable_count
    evidence.missing_contract_count = console_state.missing_contract_count
    evidence.gaps.extend(console_state.gaps)

    envelope, options, gaps = next_lane.build_menu(repo_root, menu_limit)
    evidence.menu_options = options
    evidence.gaps.extend(gaps)

    scored, errors, _, _ = estimator.analyze(repo_root)
    if errors:
        evidence.gaps.extend(errors)
    elif scored:
        evidence.scored_first = scored[0].candidate.candidate_id
        evidence.scored_first_name = scored[0].candidate.name

    return evidence


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _is_contract_signed(root: Path, contract_rel: str) -> bool:
    content = _read_text(root / contract_rel)
    if not content:
        return False
    for line in content.splitlines():
        if "**Status:**" not in line:
            continue
        if "UNSIGNED" in line or "DRAFT - unsigned" in line:
            continue
        if "SIGNED" in line:
            return True
    return False


def _contract_rel_for_candidate(candidate_id: str) -> str | None:
    estimator = _load_module("mmi_estimator", "mmi_estimator.py")
    return estimator.ARCHITECT_MANIFEST_CONTRACTS.get(candidate_id)


def _relay_buildable_option(evidence: VoiceEvidence) -> object | None:
    for option in evidence.menu_options:
        if option.buildability_status == "BUILDABLE":
            return option
    if evidence.buildable_count > 0 and evidence.scored_first:
        for option in evidence.menu_options:
            if option.candidate_id == evidence.scored_first:
                return option
    return None


def _relay_signed_unreconciled(root: Path, options: list) -> object | None:
    preferred = PREFERRED_RECONCILE_CANDIDATE
    contract_rel = _contract_rel_for_candidate(preferred)
    if contract_rel and (root / contract_rel).is_file() and _is_contract_signed(root, contract_rel):
        for option in options:
            if option.candidate_id != preferred:
                continue
            if option.contract_status != "PRESENT":
                continue
            lifecycle = option.source_lifecycle or ""
            if lifecycle.startswith(BUILDABLE_LIFECYCLE_PREFIXES):
                continue
            if any(lifecycle.startswith(prefix) for prefix in CLOSED_LIFECYCLE_PREFIXES):
                continue
            if option.buildability_status in {
                "EXCLUDED_NON_BUILDABLE_STATE",
                "BLOCKED_MISSING_CONTRACT",
            }:
                return option

    for option in options:
        if option.contract_status != "PRESENT":
            continue
        if option.buildability_status != "EXCLUDED_NON_BUILDABLE_STATE":
            continue
        lifecycle = option.source_lifecycle or ""
        if lifecycle.startswith(BUILDABLE_LIFECYCLE_PREFIXES):
            continue
        if any(lifecycle.startswith(prefix) for prefix in CLOSED_LIFECYCLE_PREFIXES):
            continue
        contract_rel = _contract_rel_for_candidate(option.candidate_id)
        if contract_rel and (root / contract_rel).is_file() and _is_contract_signed(
            root, contract_rel
        ):
            return option
    return None


def _relay_contract_candidate(options: list) -> object | None:
    for option in options:
        if (
            option.candidate_id == PREFERRED_CONTRACT_CANDIDATE
            and option.buildability_status == "BLOCKED_MISSING_CONTRACT"
        ):
            return option
    for option in options:
        if (
            option.candidate_id not in HIGH_RISK_CANDIDATE_IDS
            and option.buildability_status == "BLOCKED_MISSING_CONTRACT"
        ):
            return option
    for option in options:
        if option.buildability_status == "BLOCKED_MISSING_CONTRACT":
            return option
    return None


def _ignore_lines(options: list) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()

    def add_line(text: str) -> None:
        if text not in seen:
            seen.add(text)
            lines.append(text)

    for option in options:
        if option.candidate_id == "#47" and option.buildability_status == "EXCLUDED_ALREADY_BUILT":
            add_line(
                f"{option.candidate_id} {option.candidate_name} is already "
                f"{option.source_lifecycle}; no current action."
            )
            break

    for option in options:
        if (
            option.candidate_id in HIGH_RISK_CANDIDATE_IDS
            and option.buildability_status == "BLOCKED_MISSING_CONTRACT"
        ):
            add_line(
                f"{option.candidate_id} {option.candidate_name} is a higher-risk "
                f"control/risk candidate; hold unless Matt chooses it."
            )

    for option in options:
        if option.candidate_id in {"#72", "#73"} and option.buildability_status == "EXCLUDED_ALREADY_BUILT":
            add_line(
                f"{option.candidate_id} {option.candidate_name} is already "
                f"{option.source_lifecycle}; no current action."
            )

    for option in options:
        if option.buildability_status == "EXCLUDED_ALREADY_BUILT":
            if option.candidate_id in {"#47", "#72", "#73"}:
                continue
            add_line(
                f"{option.candidate_id} {option.candidate_name} is already "
                f"{option.source_lifecycle}; no current action."
            )

    return lines[:6]


def _source_line(evidence: VoiceEvidence, handoff: object | None = None) -> str:
    parts = [
        f"dispatcher: {evidence.dispatcher_mode} (MMI_CURRENT_STATE.md / dispatch verify posture)",
        (
            f"pm_console: {evidence.blueprint_status} buildable_count="
            f"{evidence.buildable_count}"
        ),
        (
            f"next_lane: missing_contract_count={evidence.missing_contract_count} "
            f"(relay from Estimator buildability exclusions / scored list)"
        ),
        "estimator: BUILDABILITY_EXCLUSIONS or SCORED_CANDIDATES relay",
    ]
    if evidence.scored_first:
        parts.append(
            f"estimator_rank_first: {evidence.scored_first} {evidence.scored_first_name}"
        )
    if handoff is not None:
        parts.append("handoff_log: mmi/MMI_HANDOFF_LOG.md")
    return "; ".join(parts)


def _route_next_step(next_step: str) -> str:
    lower = next_step.lower()
    if "draft" in lower:
        return ROSTER_CONTRACT_DRAFT
    if "build" in lower or "reconcile" in lower:
        return ROSTER_BUILD
    if "review" in lower or "gate" in lower:
        return ROSTER_REVIEW
    if "research" in lower:
        return ROSTER_RESEARCH
    if "sign" in lower or "close" in lower:
        return ROSTER_MATT
    return ROSTER_MATT


def _boundary_line() -> str:
    return "advisory only; Matt chooses; no autonomous selection; no AUTH-5"


def _ignore_block(evidence: VoiceEvidence) -> str:
    ignore_lines = _ignore_lines(evidence.menu_options)
    if ignore_lines:
        return "\n".join(f"- {line}" for line in ignore_lines)
    return "- No additional ignore lines relayed from engine menu."


def _compose_handoff_voice(evidence: VoiceEvidence, handoff) -> dict[str, str]:
    hand_it_to = _route_next_step(handoff.next_step)
    return {
        "WHAT_NEEDS_MATT": (
            f"Open handoff {handoff.task} is {handoff.state.replace('_', ' ').lower()}."
        ),
        "IN_FLIGHT": (
            f"task={handoff.task}; state={handoff.state}; by={handoff.by}; "
            f"next_step={handoff.next_step}"
        ),
        "HAND_IT_TO": hand_it_to,
        "YOU_DO": handoff.next_step,
        "WHY": (
            f"handoff_log latest open entry: task={handoff.task}; state={handoff.state}; "
            f"did={handoff.did}; evidence={handoff.evidence}"
        ),
        "IGNORE_FOR_NOW": _ignore_block(evidence),
        "SOURCE": _source_line(evidence, handoff=handoff),
        "BOUNDARY": _boundary_line(),
    }


def _compose_buildable_voice(evidence: VoiceEvidence, option) -> dict[str, str]:
    return {
        "WHAT_NEEDS_MATT": (
            f"Build lane authorization is needed for {option.candidate_id} "
            f"{option.candidate_name}."
        ),
        "IN_FLIGHT": "none",
        "HAND_IT_TO": ROSTER_BUILD,
        "YOU_DO": (
            f"Authorize build lane for {option.candidate_id} "
            f"{option.candidate_name}."
        ),
        "WHY": (
            f"next_lane/estimator relay: {option.candidate_id} is BUILDABLE with "
            f"source_lifecycle={option.source_lifecycle}; buildable_count="
            f"{evidence.buildable_count}."
        ),
        "IGNORE_FOR_NOW": _ignore_block(evidence),
        "SOURCE": _source_line(evidence),
        "BOUNDARY": _boundary_line(),
    }


def _compose_signed_unreconciled_voice(
    evidence: VoiceEvidence, option, contract_rel: str
) -> dict[str, str]:
    you_do = RECONCILE_YOU_DO.get(
        option.candidate_id,
        f"Authorize reconcile to SIGNED_UNBUILT for {option.candidate_id}.",
    )
    return {
        "WHAT_NEEDS_MATT": (
            f"Reconcile {option.candidate_id} {option.candidate_name} to "
            f"SIGNED_UNBUILT to open its build path."
        ),
        "IN_FLIGHT": "none",
        "HAND_IT_TO": ROSTER_BUILD,
        "YOU_DO": you_do,
        "WHY": (
            f"{option.candidate_id} contract is signed/on disk at {contract_rel}, "
            f"but lifecycle still shows {option.source_lifecycle} / not SIGNED_UNBUILT. "
            f"Reconcile is required before Architect/build lane."
        ),
        "IGNORE_FOR_NOW": _ignore_block(evidence),
        "SOURCE": _source_line(evidence),
        "BOUNDARY": _boundary_line(),
    }


def _compose_missing_contract_voice(
    evidence: VoiceEvidence, relay
) -> dict[str, str]:
    if relay:
        you_do = (
            f"Authorize contract draft lane for {relay.candidate_id} "
            f"{relay.candidate_name}."
        )
        what = (
            f"Contract draft lane is needed for {relay.candidate_id} "
            f"{relay.candidate_name}."
        )
        why = (
            f"next_lane relay: {relay.candidate_id} is "
            f"{relay.buildability_status} with contract_status="
            f"{relay.contract_status}."
        )
    else:
        you_do = "Authorize contract draft lane for the top missing-contract candidate."
        what = "Contract draft lane is needed for the top missing-contract candidate."
        why = (
            f"Dispatcher is {evidence.dispatcher_mode}. PM console reports "
            f"{evidence.blueprint_status}. buildable_count=0; "
            f"missing_contract_count={evidence.missing_contract_count}."
        )
    return {
        "WHAT_NEEDS_MATT": what,
        "IN_FLIGHT": "none",
        "HAND_IT_TO": ROSTER_CONTRACT_DRAFT,
        "YOU_DO": you_do,
        "WHY": why,
        "IGNORE_FOR_NOW": _ignore_block(evidence),
        "SOURCE": _source_line(evidence),
        "BOUNDARY": _boundary_line(),
    }


def _compose_fallback_voice(evidence: VoiceEvidence) -> dict[str, str]:
    if evidence.scored_first:
        you_do = (
            f"Run Estimator review for {evidence.scored_first} "
            f"{evidence.scored_first_name}, then authorize the next lane Matt selects."
        )
        what = (
            f"Next move requires Matt lane selection after Estimator-ranked "
            f"{evidence.scored_first} {evidence.scored_first_name}."
        )
        why = (
            f"Dispatcher is {evidence.dispatcher_mode}; no open handoff; "
            f"estimator_rank_first={evidence.scored_first}."
        )
        hand_it_to = ROSTER_MATT
    else:
        you_do = "Authorize the next MMI lane Matt selects, or run Estimator for candidate ranking."
        what = "Next lane selection is required to keep MMI moving."
        why = (
            f"Dispatcher is {evidence.dispatcher_mode}; PM console reports "
            f"{evidence.blueprint_status}; no open handoff relay."
        )
        hand_it_to = ROSTER_MATT
    return {
        "WHAT_NEEDS_MATT": what,
        "IN_FLIGHT": "none",
        "HAND_IT_TO": hand_it_to,
        "YOU_DO": you_do,
        "WHY": why,
        "IGNORE_FOR_NOW": _ignore_block(evidence),
        "SOURCE": _source_line(evidence),
        "BOUNDARY": _boundary_line(),
    }


def compose_voice(
    evidence: VoiceEvidence, handoff=None, repo_root: Path | None = None
) -> dict[str, str]:
    if handoff is not None:
        return _compose_handoff_voice(evidence, handoff)

    root = repo_root or _repo_root()

    buildable = _relay_buildable_option(evidence)
    if buildable is not None:
        return _compose_buildable_voice(evidence, buildable)

    unreconciled = _relay_signed_unreconciled(root, evidence.menu_options)
    if unreconciled is not None:
        contract_rel = _contract_rel_for_candidate(unreconciled.candidate_id) or ""
        return _compose_signed_unreconciled_voice(evidence, unreconciled, contract_rel)

    relay = _relay_contract_candidate(evidence.menu_options)
    if relay is not None or evidence.missing_contract_count > 0:
        return _compose_missing_contract_voice(evidence, relay)

    return _compose_fallback_voice(evidence)


def format_voice(fields: dict[str, str]) -> str:
    lines = [
        ENVELOPE_VOICE,
        f"WHAT_NEEDS_MATT:\n{fields['WHAT_NEEDS_MATT']}",
        f"IN_FLIGHT:\n{fields.get('IN_FLIGHT', 'none')}",
        f"HAND_IT_TO:\n{fields['HAND_IT_TO']}",
        f"YOU_DO:\n{fields['YOU_DO']}",
        f"WHY:\n{fields['WHY']}",
        f"IGNORE_FOR_NOW:\n{fields['IGNORE_FOR_NOW']}",
        f"SOURCE:\n{fields['SOURCE']}",
        f"BOUNDARY:\n{fields['BOUNDARY']}",
    ]
    return _validate_output("\n".join(lines) + "\n")


def format_revision() -> str:
    lines = [ENVELOPE_VOICE, "REVISION_MODE:", "read-only address map:"]
    for item, owner, can_change in REVISION_ROWS:
        lines.append(f"- change: {item}")
        lines.append(f"  owned_by: {owner}")
        lines.append(f"  can_change: {can_change}")
    lines.append(
        "BOUNDARY:\nrevision mode reports only; Matt directs changes through signed paths."
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
            raise RuntimeError("forbidden VERDICT line on PM voice output")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="MMI PM Voice Layer Mode A — read-only single owner voice (stdout only)."
    )
    parser.add_argument("--root", type=Path, default=None, help="Repository root")
    parser.add_argument(
        "--revision",
        action="store_true",
        help="Read-only revision address map",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=30,
        help="Max next_lane menu rows to read for relay",
    )
    args = parser.parse_args(argv)

    if args.revision:
        sys.stdout.write(format_revision())
        return 0

    repo_root = args.root.resolve() if args.root else _repo_root()
    evidence = gather_evidence(repo_root, menu_limit=max(1, args.limit))
    handoff_mod = _load_module("mmi_handoff", "mmi_handoff.py")
    handoff = handoff_mod.latest_open_handoff(repo_root)

    critical = [
        g
        for g in evidence.gaps
        if g.startswith("missing_dispatcher_state")
        or g.startswith("missing_or_unreadable")
    ]
    if critical and evidence.dispatcher_mode == "UNKNOWN":
        sys.stdout.write(format_insufficient(evidence.gaps))
        return 2

    sys.stdout.write(
        format_voice(compose_voice(evidence, handoff=handoff, repo_root=repo_root))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
