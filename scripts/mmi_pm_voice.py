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
from dataclasses import dataclass, field, replace
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
    "#61": "Authorize MMI_61_SCOREBOARD_SIGNED_UNBUILT_RECONCILE_ONLY.",
    "#62": "Authorize MMI_62_SCOREBOARD_SIGNED_UNBUILT_RECONCILE_ONLY.",
    "#63": "Authorize MMI_63_SCOREBOARD_SIGNED_UNBUILT_RECONCILE_ONLY.",
    "#64": "Authorize MMI_64_SCOREBOARD_SIGNED_UNBUILT_RECONCILE_ONLY.",
}
GATED_RECONCILE_YOU_DO = {
    "#52": "Authorize MMI_52_GATED_RECONCILE_ONLY.",
    "#61": "Authorize MMI_61_GATED_RECONCILE_ONLY.",
    "#62": "Authorize MMI_62_GATED_RECONCILE_ONLY.",
    "#63": "Authorize MMI_63_GATED_RECONCILE_ONLY.",
    "#64": "Authorize MMI_64_GATED_RECONCILE_ONLY.",
}

BUILDABLE_LIFECYCLE_PREFIXES = ("SIGNED_UNBUILT", "AWAITING_AUDIT")
BUILD_AUTHORIZATION_LIFECYCLE_PREFIXES = ("SIGNED_UNBUILT",)
AWAITING_AUDIT_LIFECYCLE_PREFIXES = ("AWAITING_AUDIT",)
CLOSED_LIFECYCLE_PREFIXES = ("GATED", "GOVERNED_AGENT", "INFRASTRUCTURE_BUILT")

ROSTER_CONTRACT_DRAFT = "Claude"
ROSTER_BUILD = "Cursor"
ROSTER_REVIEW = "Codex"
ROSTER_RESEARCH = "Gemini+ChatGPT"
ROSTER_MATT = "Matt"
ROSTER_MULTI_LANE_ADVISORY = (
    "Matt orchestrates; Claude + Gemini + ChatGPT per "
    "4. Product_Roadmap/MMI_Governance_Invariants_Testing_Advisory_Lane_Brief.md"
)

GOVERNANCE_FRAMEWORK_CONTRACTS: dict[str, str] = {
    "#105": (
        "4. Product_Roadmap/MMI_Governance_Invariants_Testing_Framework_Contract.md"
    ),
}
GOVERNANCE_SIGNED_CONTRACT_LIFECYCLE = "SIGNED_CONTRACT"

INVARIANTS_PROBE_REL = "scripts/mmi_authority_escalation_probe.py"
INVARIANTS_PROBE_TEST_REL = "tests/test_mmi_authority_escalation_probe.py"

RUBRIC_BINARY_CALIBRATION_AMENDMENT_REL = (
    "4. Product_Roadmap/Next_Action_Decision_Rubric_Binary_Calibration_Amendment_Deep_Dive.md"
)
RANKED_ACTIONS_REL = "mmi/MMI_RANKED_NEXT_ACTIONS.md"

CONTRACT_SIGNED_DECISION: dict[str, str] = {
    "#1": "MMI-DEC-102",
    "#3": "MMI-DEC-098",
}

CONTRACT_DRAFTS_ON_DISK: dict[str, str] = {
    "#1": "docs/mmi/contracts/001_swarm_commander_contract.md",
}

CONTRACT_REVIEW_DRAFTS_ON_DISK: dict[str, str] = {
    "#3": "docs/mmi/contracts/003_risk_triage_contract.md",
}

CONTRACT_DRAFT_GATE_GLOBS: dict[str, str] = {
    "#1": "mmi_01_contract_gate_*.md",
}

CONTRACT_REVIEW_GATE_GLOBS: dict[str, str] = {
    "#3": "mmi_03_contract_gate_*.md",
}

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
    feedstock_first: str = ""
    feedstock_first_name: str = ""
    feedstock_lane_type: str = ""
    gaps: list[str] = field(default_factory=list)
    ranked_rows: list = field(default_factory=list)


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
    evidence.ranked_rows = _load_ranked_rows(repo_root)

    scored, errors, _, _, feedstock_scored = estimator.analyze(repo_root)
    if errors:
        evidence.gaps.extend(errors)
    elif feedstock_scored and evidence.dispatcher_mode == "ALL_CLEAR":
        top = feedstock_scored[0]
        evidence.feedstock_first = top.entry.candidate_id
        evidence.feedstock_first_name = top.entry.name or top.scored.candidate.name
        evidence.feedstock_lane_type = top.entry.lane_type
    elif scored:
        evidence.scored_first = scored[0].candidate.candidate_id
        evidence.scored_first_name = scored[0].candidate.name
    elif feedstock_scored:
        top = feedstock_scored[0]
        evidence.feedstock_first = top.entry.candidate_id
        evidence.feedstock_first_name = top.entry.name or top.scored.candidate.name
        evidence.feedstock_lane_type = top.entry.lane_type

    return evidence


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _load_ranked_rows(repo_root: Path) -> list[dict[str, str]]:
    """Load persisted ranked lanes; compute in-memory if board file is absent."""
    ranked_path = repo_root / RANKED_ACTIONS_REL
    if ranked_path.is_file():
        rubric = _load_module("mmi_next_action_rubric", "mmi_next_action_rubric.py")
        rows = rubric.parse_ranked_markdown(_read_text(ranked_path))
        if rows:
            return rows
    rubric = _load_module("mmi_next_action_rubric", "mmi_next_action_rubric.py")
    scored = rubric.analyze(repo_root, limit=7)
    return [
        {
            "rank": str(index),
            "total": str(item.axes.total),
            "label": item.candidate.label,
        }
        for index, item in enumerate(scored, start=1)
    ]


def _format_ranked_lane_lines(rows: list[dict[str, str]], limit: int = 5) -> list[str]:
    lines: list[str] = []
    for row in rows[:limit]:
        rank = row.get("rank", "?")
        total = row.get("total", "?")
        label = row.get("label", "unknown")
        lines.append(f"  {rank}. [{total}/10] {label}")
    return lines


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


def _is_rubric_binary_calibration_in_force(root: Path) -> bool:
    return _is_contract_signed(root, RUBRIC_BINARY_CALIBRATION_AMENDMENT_REL)


def _contract_review_draft_rel(candidate_id: str, root: Path) -> str | None:
    for mapping in (CONTRACT_DRAFTS_ON_DISK, CONTRACT_REVIEW_DRAFTS_ON_DISK):
        rel = mapping.get(candidate_id)
        if rel and (root / rel).is_file():
            return rel
    return None


def _contract_gate_clean(root: Path, candidate_id: str) -> str | None:
    """Return newest clean pre-build gate artifact path for a contract draft."""
    pattern = CONTRACT_DRAFT_GATE_GLOBS.get(
        candidate_id
    ) or CONTRACT_REVIEW_GATE_GLOBS.get(candidate_id)
    if not pattern:
        return None
    audit_dir = root / "audit_outputs"
    if not audit_dir.is_dir():
        return None
    matches = sorted(audit_dir.glob(pattern), reverse=True)
    for path in matches:
        content = _read_text(path)
        if not content:
            continue
        if "**Blocking deviations:** `0`" in content and "**Warnings:** `0`" in content:
            return path.relative_to(root).as_posix()
        if "GATE_SUMMARY: blocking=0 warnings=0" in content:
            return path.relative_to(root).as_posix()
    return None


def _governance_framework_lane_closed(root: Path, candidate_id: str) -> bool:
    """True when signed governance framework + Lane 1 probe are on disk (no PM nag)."""
    contract_rel = GOVERNANCE_FRAMEWORK_CONTRACTS.get(candidate_id)
    if not contract_rel:
        return False
    if not ((root / contract_rel).is_file() and _is_contract_signed(root, contract_rel)):
        return False
    if not (root / INVARIANTS_PROBE_REL).is_file():
        return False
    if not (root / INVARIANTS_PROBE_TEST_REL).is_file():
        return False
    return True


def _all_clear_hold_posture(evidence: VoiceEvidence, root: Path) -> bool:
    """ALL_CLEAR with no buildable rows; hold when only high-risk gaps or closed lanes."""
    if evidence.dispatcher_mode != "ALL_CLEAR":
        return False
    if evidence.buildable_count != 0:
        return False

    if evidence.feedstock_first:
        if evidence.feedstock_first in GOVERNANCE_FRAMEWORK_CONTRACTS:
            return _governance_framework_lane_closed(root, evidence.feedstock_first)
        return False

    relay = _relay_contract_candidate(evidence.menu_options)
    if relay is not None:
        if relay.candidate_id in HIGH_RISK_CANDIDATE_IDS:
            return True
        if relay.candidate_id in GOVERNANCE_FRAMEWORK_CONTRACTS:
            contract_rel = _contract_rel_for_candidate(relay.candidate_id)
            if contract_rel and (root / contract_rel).is_file():
                if not _is_contract_signed(root, contract_rel):
                    return False
            if _governance_framework_lane_closed(root, relay.candidate_id):
                return True
        return False

    if evidence.missing_contract_count > 0:
        blocked = [
            option
            for option in evidence.menu_options
            if option.buildability_status == "BLOCKED_MISSING_CONTRACT"
        ]
        if blocked and all(
            option.candidate_id in HIGH_RISK_CANDIDATE_IDS for option in blocked
        ):
            return True

    return True


def _contract_rel_for_candidate(candidate_id: str) -> str | None:
    rel = CONTRACT_DRAFTS_ON_DISK.get(candidate_id)
    if rel:
        return rel
    rel = CONTRACT_REVIEW_DRAFTS_ON_DISK.get(candidate_id)
    if rel:
        return rel
    rel = GOVERNANCE_FRAMEWORK_CONTRACTS.get(candidate_id)
    if rel:
        return rel
    estimator = _load_module("mmi_estimator", "mmi_estimator.py")
    return estimator.ARCHITECT_MANIFEST_CONTRACTS.get(candidate_id)


def _relay_buildable_option(evidence: VoiceEvidence) -> object | None:
    for option in evidence.menu_options:
        if option.buildability_status != "BUILDABLE":
            continue
        lifecycle = option.source_lifecycle or ""
        if not lifecycle.startswith(BUILD_AUTHORIZATION_LIFECYCLE_PREFIXES):
            continue
        return option
    if evidence.buildable_count > 0 and evidence.scored_first:
        for option in evidence.menu_options:
            if option.candidate_id != evidence.scored_first:
                continue
            lifecycle = option.source_lifecycle or ""
            if not lifecycle.startswith(BUILD_AUTHORIZATION_LIFECYCLE_PREFIXES):
                continue
            return option
    return None


def _relay_awaiting_audit_gated(evidence: VoiceEvidence) -> object | None:
    if evidence.dispatcher_mode != "AUDIT":
        return None
    for option in evidence.menu_options:
        lifecycle = option.source_lifecycle or ""
        if not lifecycle.startswith(AWAITING_AUDIT_LIFECYCLE_PREFIXES):
            continue
        if option.buildability_status == "BUILDABLE":
            return option
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
            if option.candidate_id in GOVERNANCE_FRAMEWORK_CONTRACTS:
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
        if option.candidate_id in GOVERNANCE_FRAMEWORK_CONTRACTS:
            continue
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
            if option.candidate_id in CONTRACT_REVIEW_DRAFTS_ON_DISK:
                continue
            if option.candidate_id in CONTRACT_DRAFTS_ON_DISK:
                continue
            return option
    return None


def _relay_signed_governance_framework(
    root: Path, evidence: VoiceEvidence
) -> dict[str, str] | None:
    if evidence.dispatcher_mode != "ALL_CLEAR":
        return None
    for candidate_id, contract_rel in GOVERNANCE_FRAMEWORK_CONTRACTS.items():
        if _governance_framework_lane_closed(root, candidate_id):
            continue
        if not ((root / contract_rel).is_file() and _is_contract_signed(root, contract_rel)):
            continue
        for option in evidence.menu_options:
            if option.candidate_id != candidate_id:
                continue
            lifecycle = option.source_lifecycle or ""
            if not lifecycle.startswith(GOVERNANCE_SIGNED_CONTRACT_LIFECYCLE):
                continue
            gov_evidence = replace(
                evidence,
                feedstock_first=candidate_id,
                feedstock_first_name=option.candidate_name,
            )
            return _compose_signed_invariants_framework_voice(gov_evidence, contract_rel)
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


def _ignore_lines(options: list, root: Path, feedstock_first: str = "") -> list[str]:
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
        if option.candidate_id == "#52" and option.buildability_status == "EXCLUDED_ALREADY_BUILT":
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
            if feedstock_first == option.candidate_id:
                continue
            draft_rel = _contract_review_draft_rel(option.candidate_id, root)
            if draft_rel:
                if _is_contract_signed(root, draft_rel):
                    add_line(
                        f"{option.candidate_id} {option.candidate_name} contract "
                        f"§11 SIGNED at {draft_rel} (MMI-DEC-098); not build / not "
                        f"SIGNED_UNBUILT."
                    )
                    continue
                add_line(
                    f"{option.candidate_id} {option.candidate_name} has "
                    f"{'contract DRAFT' if option.candidate_id in CONTRACT_DRAFTS_ON_DISK else 'CONTRACT_REVIEW draft'} "
                    f"on disk at {draft_rel} (DRAFT UNSIGNED); hold unless Matt chooses unpark."
                )
            else:
                add_line(
                    f"{option.candidate_id} {option.candidate_name} is a higher-risk "
                    f"control/risk candidate; hold unless Matt chooses it."
                )

    for mapping in (CONTRACT_DRAFTS_ON_DISK, CONTRACT_REVIEW_DRAFTS_ON_DISK):
        for candidate_id, draft_rel in mapping.items():
            if not _is_contract_signed(root, draft_rel):
                continue
            label = candidate_id
            for option in options:
                if option.candidate_id == candidate_id:
                    label = f"{option.candidate_id} {option.candidate_name}"
                    break
            decision = CONTRACT_SIGNED_DECISION.get(candidate_id, "MMI-DEC")
            add_line(
                f"{label} contract §11 SIGNED at {draft_rel} ({decision}); not build / not "
                f"SIGNED_UNBUILT."
            )

    for option in options:
        if option.candidate_id == "#105" and (
            (option.source_lifecycle or "").startswith(GOVERNANCE_SIGNED_CONTRACT_LIFECYCLE)
            or option.contract_status == "PRESENT"
        ):
            add_line(
                "#105 MMI Governance Invariants Testing Framework is SIGNED_CONTRACT "
                "+ Lane 1 probe complete (MMI-DEC-092); hold Lane 2+ unless Matt "
                "authorizes."
            )
            break

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

    return lines[:8]


def _source_line(
    evidence: VoiceEvidence, handoff: object | None = None, repo_root: Path | None = None
) -> str:
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
    if evidence.feedstock_first:
        parts.append(
            f"estimator_feedstock_first: {evidence.feedstock_first} "
            f"{evidence.feedstock_first_name} lane_type={evidence.feedstock_lane_type}"
        )
    if handoff is not None:
        parts.append("handoff_log: mmi/MMI_HANDOFF_LOG.md")
    root = repo_root or _repo_root()
    if _is_rubric_binary_calibration_in_force(root):
        parts.append(
            "rubric_calibration: MMI-DEC-095 §3.A in force (signed amendment on disk)"
        )
    return "; ".join(parts)


def _route_next_step(next_step: str) -> str:
    lower = next_step.lower()
    if "review" in lower or "gate" in lower:
        return ROSTER_REVIEW
    if "draft" in lower:
        return ROSTER_CONTRACT_DRAFT
    if "build" in lower or "reconcile" in lower:
        return ROSTER_BUILD
    if "research" in lower:
        return ROSTER_RESEARCH
    if "sign" in lower or "close" in lower:
        return ROSTER_MATT
    return ROSTER_MATT


def _boundary_line() -> str:
    return "advisory only; Matt chooses; no autonomous selection; no AUTH-5"


def _ignore_block(evidence: VoiceEvidence, repo_root: Path | None = None) -> str:
    root = repo_root or _repo_root()
    ignore_lines = _ignore_lines(
        evidence.menu_options, root, feedstock_first=evidence.feedstock_first
    )
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


def _compose_awaiting_audit_gated_voice(
    evidence: VoiceEvidence, option
) -> dict[str, str]:
    you_do = GATED_RECONCILE_YOU_DO.get(
        option.candidate_id,
        f"Authorize GATED reconcile for {option.candidate_id}.",
    )
    return {
        "WHAT_NEEDS_MATT": (
            f"GATED reconcile is needed for {option.candidate_id} "
            f"{option.candidate_name}."
        ),
        "IN_FLIGHT": "none",
        "HAND_IT_TO": ROSTER_BUILD,
        "YOU_DO": you_do,
        "WHY": (
            f"dispatcher: MODE:AUDIT; {option.candidate_id} is "
            f"{option.source_lifecycle}; superintendent must confirm Grok "
            f"completion gate 0/0 before GATED reconcile."
        ),
        "IGNORE_FOR_NOW": _ignore_block(evidence),
        "SOURCE": _source_line(evidence),
        "BOUNDARY": _boundary_line(),
    }


def _feedstock_hand_it_to(lane_type: str) -> str:
    if lane_type == "CONTRACT_DRAFT":
        return ROSTER_CONTRACT_DRAFT
    if lane_type == "CONTRACT_REVIEW":
        return ROSTER_REVIEW
    if lane_type == "ADVISORY_MULTI_LANE_DESIGN":
        return ROSTER_MULTI_LANE_ADVISORY
    if lane_type == "PROMOTION_REVIEW":
        return ROSTER_MATT
    if lane_type == "RESEARCH":
        return ROSTER_RESEARCH
    if lane_type == "REVISE":
        return ROSTER_REVIEW
    return ROSTER_MATT


def _compose_signed_swarm_commander_contract_voice(
    evidence: VoiceEvidence, contract_rel: str, repo_root: Path
) -> dict[str, str]:
    gate_rel = _contract_gate_clean(repo_root, "#1") or ""
    gate_note = f" gate {gate_rel}" if gate_rel else ""
    ranked = evidence.ranked_rows or _load_ranked_rows(repo_root)
    ranked_lines = _format_ranked_lane_lines(ranked, limit=3)
    ranked_block = "\n".join(ranked_lines) if ranked_lines else ""
    return {
        "WHAT_NEEDS_MATT": (
            "#1 Swarm Commander contract §11 signed; select next ranked lane "
            "(buildable_count=0)."
        ),
        "IN_FLIGHT": (
            f"#1 contract §11 SIGNED at {contract_rel} (MMI-DEC-102);"
            f"{gate_note}; not build / not SIGNED_UNBUILT."
        ),
        "HAND_IT_TO": ROSTER_MATT,
        "YOU_DO": (
            f"Ranked lanes (Matt selects one):\n{ranked_block}\n"
            f"Board: {RANKED_ACTIONS_REL}. Maintain drift defense: pytest "
            f"{INVARIANTS_PROBE_TEST_REL} after any scripts/mmi_*.py change."
        ),
        "WHY": (
            f"§11 signed at {contract_rel}; pre-build gate 0/0 (MMI-DEC-101); "
            f"BOR hold-only feedstock; missing_contract_count="
            f"{evidence.missing_contract_count}."
        ),
        "IGNORE_FOR_NOW": _ignore_block(evidence, repo_root=repo_root),
        "SOURCE": _source_line(evidence, repo_root=repo_root),
        "BOUNDARY": _boundary_line(),
    }


def _compose_signed_risk_triage_contract_voice(
    evidence: VoiceEvidence, contract_rel: str, repo_root: Path
) -> dict[str, str]:
    gate_rel = _contract_gate_clean(repo_root, "#3") or ""
    gate_note = f" gate {gate_rel}" if gate_rel else ""
    ranked = evidence.ranked_rows or _load_ranked_rows(repo_root)
    ranked_lines = _format_ranked_lane_lines(ranked, limit=3)
    ranked_block = "\n".join(ranked_lines) if ranked_lines else ""
    return {
        "WHAT_NEEDS_MATT": (
            "#3 Risk Triage contract §11 signed; select next ranked lane "
            "(buildable_count=0)."
        ),
        "IN_FLIGHT": (
            f"#3 contract §11 SIGNED at {contract_rel} (MMI-DEC-098);"
            f"{gate_note}; not build / not SIGNED_UNBUILT."
        ),
        "HAND_IT_TO": ROSTER_MATT,
        "YOU_DO": (
            f"Ranked lanes (Matt selects one):\n{ranked_block}\n"
            f"Board: {RANKED_ACTIONS_REL}. Maintain drift defense: pytest "
            f"{INVARIANTS_PROBE_TEST_REL} after any scripts/mmi_*.py change."
        ),
        "WHY": (
            f"§11 signed at {contract_rel}; pre-build gate 0/0 (MMI-DEC-097); "
            f"BOR hold-only feedstock; missing_contract_count="
            f"{evidence.missing_contract_count}."
        ),
        "IGNORE_FOR_NOW": _ignore_block(evidence, repo_root=repo_root),
        "SOURCE": _source_line(evidence, repo_root=repo_root),
        "BOUNDARY": _boundary_line(),
    }


def _compose_unsigned_contract_draft_voice(
    evidence: VoiceEvidence, contract_rel: str
) -> dict[str, str]:
    candidate_id = evidence.feedstock_first
    candidate_name = evidence.feedstock_first_name
    return {
        "WHAT_NEEDS_MATT": (
            f"Pre-build gate review is needed for {candidate_id} {candidate_name} "
            f"contract draft."
        ),
        "IN_FLIGHT": f"Contract draft on disk at {contract_rel}; §11 UNSIGNED.",
        "HAND_IT_TO": ROSTER_REVIEW,
        "YOU_DO": (
            f"Run Grok pre-build gate review on {candidate_id} "
            f"{candidate_name} contract draft at {contract_rel}."
        ),
        "WHY": (
            f"contract draft on disk at {contract_rel}; §11 UNSIGNED; "
            f"estimator feedstock rank {candidate_id}; MMI-DEC-099 unpark; "
            f"MMI-DEC-100 draft placement."
        ),
        "IGNORE_FOR_NOW": _ignore_block(evidence),
        "SOURCE": _source_line(evidence),
        "BOUNDARY": _boundary_line(),
    }


def _compose_gate_clean_contract_draft_voice(
    evidence: VoiceEvidence,
    contract_rel: str,
    gate_rel: str,
    repo_root: Path,
) -> dict[str, str]:
    candidate_id = evidence.feedstock_first
    candidate_name = evidence.feedstock_first_name
    return {
        "WHAT_NEEDS_MATT": (
            f"Optional Matt §11 signature on {candidate_id} {candidate_name} "
            f"contract draft when ready."
        ),
        "IN_FLIGHT": (
            f"Pre-build gate clean 0/0 at {gate_rel}; contract still UNSIGNED."
        ),
        "HAND_IT_TO": ROSTER_MATT,
        "YOU_DO": (
            f"Matt §11 sign {candidate_id} {candidate_name} at {contract_rel} "
            f"when ready. Gate evidence: {gate_rel}. No build authorization; "
            f"no SIGNED_UNBUILT reconcile; no scoreboard promotion implied."
        ),
        "WHY": (
            f"pre-build gate 0/0 at {gate_rel}; contract draft at {contract_rel}; "
            f"estimator feedstock rank {candidate_id}; MMI-DEC-099 unpark; "
            f"MMI-DEC-101 gate record."
        ),
        "IGNORE_FOR_NOW": _ignore_block(evidence, repo_root=repo_root),
        "SOURCE": _source_line(evidence, repo_root=repo_root),
        "BOUNDARY": _boundary_line(),
    }


def _compose_gate_clean_contract_review_voice(
    evidence: VoiceEvidence,
    contract_rel: str,
    gate_rel: str,
    repo_root: Path,
) -> dict[str, str]:
    candidate_id = evidence.feedstock_first
    candidate_name = evidence.feedstock_first_name
    return {
        "WHAT_NEEDS_MATT": (
            f"Optional Matt §11 signature on {candidate_id} {candidate_name} "
            f"contract review draft when ready."
        ),
        "IN_FLIGHT": (
            f"Pre-build gate clean 0/0 at {gate_rel}; contract still UNSIGNED."
        ),
        "HAND_IT_TO": ROSTER_MATT,
        "YOU_DO": (
            f"Matt §11 sign {candidate_id} {candidate_name} at {contract_rel} "
            f"when ready. Gate evidence: {gate_rel}. No build authorization; "
            f"no SIGNED_UNBUILT reconcile; no scoreboard promotion implied."
        ),
        "WHY": (
            f"pre-build gate 0/0 at {gate_rel}; contract review draft at "
            f"{contract_rel}; estimator feedstock rank {candidate_id}; "
            f"MMI-DEC-096 unpark."
        ),
        "IGNORE_FOR_NOW": _ignore_block(evidence, repo_root=repo_root),
        "SOURCE": _source_line(evidence, repo_root=repo_root),
        "BOUNDARY": _boundary_line(),
    }


def _compose_unsigned_contract_review_voice(
    evidence: VoiceEvidence, contract_rel: str
) -> dict[str, str]:
    candidate_id = evidence.feedstock_first
    candidate_name = evidence.feedstock_first_name
    if candidate_id == "#105":
        return {
            "WHAT_NEEDS_MATT": (
                f"Pre-build gate review is needed for {candidate_id} {candidate_name} "
                f"invariants framework contract."
            ),
            "IN_FLIGHT": (
                f"Lane 1 probe shipped ({INVARIANTS_PROBE_REL}; "
                f"pytest {INVARIANTS_PROBE_TEST_REL}); contract still UNSIGNED."
            ),
            "HAND_IT_TO": ROSTER_REVIEW,
            "YOU_DO": (
                f"Run Grok pre-build gate review on {candidate_id} "
                f"{candidate_name} at {contract_rel}; optional Matt §11 when ready. "
                f"Maintain drift defense: pytest {INVARIANTS_PROBE_TEST_REL} after "
                f"any scripts/mmi_*.py change."
            ),
            "WHY": (
                f"unsigned invariants contract on disk at {contract_rel}; "
                f"Lane 1 Mode A probe complete (MMI-DEC-082/083); "
                f"estimator feedstock rank {candidate_id}; gate before §11 per contract §16."
            ),
            "IGNORE_FOR_NOW": _ignore_block(evidence),
            "SOURCE": _source_line(evidence),
            "BOUNDARY": _boundary_line(),
        }
    return {
        "WHAT_NEEDS_MATT": (
            f"Pre-build gate review is needed for {candidate_id} {candidate_name} "
            f"contract review draft."
        ),
        "IN_FLIGHT": "none",
        "HAND_IT_TO": ROSTER_REVIEW,
        "YOU_DO": (
            f"Run Grok pre-build gate review on {candidate_id} "
            f"{candidate_name} contract review draft at {contract_rel}."
        ),
        "WHY": (
            f"contract review draft on disk at {contract_rel}; §11 UNSIGNED; "
            f"estimator feedstock rank {candidate_id}; gate before §11 per contract."
        ),
        "IGNORE_FOR_NOW": _ignore_block(evidence),
        "SOURCE": _source_line(evidence),
        "BOUNDARY": _boundary_line(),
    }


def _compose_signed_invariants_framework_voice(
    evidence: VoiceEvidence, contract_rel: str
) -> dict[str, str]:
    return {
        "WHAT_NEEDS_MATT": (
            "#105 MMI Governance Invariants Testing Framework is §11 signed; "
            "Lane 1 authorized and on disk; hold Lane 2+ until separate authorization."
        ),
        "IN_FLIGHT": (
            f"Lane 1 probe shipped ({INVARIANTS_PROBE_REL}; "
            f"pytest {INVARIANTS_PROBE_TEST_REL}); contract §11 SIGNED (MMI-DEC-092)."
        ),
        "HAND_IT_TO": ROSTER_MATT,
        "YOU_DO": (
            f"Hold Lane 2+ closed; maintain drift defense: pytest "
            f"{INVARIANTS_PROBE_TEST_REL} after any scripts/mmi_*.py change. "
            f"No redraft; no pre-build gate rerun on {contract_rel}."
        ),
        "WHY": (
            f"§11 signed at {contract_rel}; pre-build gate 0/0 (MMI-DEC-091); "
            f"scoreboard SIGNED_CONTRACT (MMI-DEC-092); estimator feedstock rank #105."
        ),
        "IGNORE_FOR_NOW": _ignore_block(evidence),
        "SOURCE": _source_line(evidence),
        "BOUNDARY": _boundary_line(),
    }


def _compose_feedstock_voice(evidence: VoiceEvidence) -> dict[str, str]:
    candidate_id = evidence.feedstock_first
    candidate_name = evidence.feedstock_first_name
    lane_type = evidence.feedstock_lane_type
    hand_it_to = _feedstock_hand_it_to(lane_type)
    why_extra = ""
    if lane_type == "CONTRACT_DRAFT":
        you_do = (
            f"Authorize contract draft lane for {candidate_id} {candidate_name}."
        )
        what = f"Contract draft lane is needed for {candidate_id} {candidate_name}."
        if candidate_id == "#1":
            why_extra = "; MMI-DEC-099 unpark"
    elif lane_type == "ADVISORY_MULTI_LANE_DESIGN":
        you_do = (
            f"Optional multi-lane invariants contract advisory review for {candidate_id} "
            f"{candidate_name} per "
            f"4. Product_Roadmap/MMI_Governance_Invariants_Testing_Advisory_Lane_Brief.md "
            f"if Matt wants external review; Lane 1 probe already shipped — "
            f"pytest {INVARIANTS_PROBE_TEST_REL} is the drift-defense default."
        )
        what = (
            f"Optional governance invariants framework external review for "
            f"{candidate_id} {candidate_name}; regular lane restored — not required."
        )
    elif lane_type == "CONTRACT_REVIEW":
        you_do = (
            f"Review unsigned invariants framework contract for {candidate_id} "
            f"{candidate_name}; run Grok pre-build gate when Matt chooses §11 path."
        )
        what = (
            f"Invariants framework contract review is available for "
            f"{candidate_id} {candidate_name}."
        )
    elif lane_type == "PROMOTION_REVIEW":
        you_do = (
            f"Authorize GOVERNED_AGENT promotion review for {candidate_id} "
            f"{candidate_name}."
        )
        what = (
            f"Promotion review is needed for {candidate_id} {candidate_name}."
        )
    else:
        you_do = f"Authorize {lane_type} lane for {candidate_id} {candidate_name}."
        what = f"{lane_type} lane is needed for {candidate_id} {candidate_name}."
    return {
        "WHAT_NEEDS_MATT": what,
        "IN_FLIGHT": "none",
        "HAND_IT_TO": hand_it_to,
        "YOU_DO": you_do,
        "WHY": (
            f"estimator feedstock rank from BOR CURRENT_PLAN: {candidate_id} "
            f"lane_type={lane_type}; dispatcher={evidence.dispatcher_mode}; "
            f"buildable_count={evidence.buildable_count}{why_extra}."
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


def _compose_all_clear_hold_voice(
    evidence: VoiceEvidence, repo_root: Path
) -> dict[str, str]:
    why = (
        f"dispatcher={evidence.dispatcher_mode}; buildable_count="
        f"{evidence.buildable_count}; missing_contract_count="
        f"{evidence.missing_contract_count}; BOR hold-only feedstock; "
        f"#105 SIGNED_CONTRACT + Lane 1 probe complete (MMI-DEC-092)."
    )
    if (repo_root / CONTRACT_REVIEW_DRAFTS_ON_DISK["#3"]).is_file() and _is_contract_signed(
        repo_root, CONTRACT_REVIEW_DRAFTS_ON_DISK["#3"]
    ):
        why += " #3 contract §11 SIGNED (MMI-DEC-098); not build."
    if (repo_root / CONTRACT_DRAFTS_ON_DISK["#1"]).is_file() and _is_contract_signed(
        repo_root, CONTRACT_DRAFTS_ON_DISK["#1"]
    ):
        why += " #1 contract §11 SIGNED (MMI-DEC-102); not build."
    if _is_rubric_binary_calibration_in_force(repo_root):
        why += (
            " Next-Action Rubric §3.A binary calibration in force "
            "(MMI-DEC-095)."
        )

    ranked = evidence.ranked_rows or _load_ranked_rows(repo_root)
    ranked_lines = _format_ranked_lane_lines(ranked)
    top = ranked[0] if ranked else None
    top_label = top.get("label", "Hold ALL_CLEAR") if top else "Hold ALL_CLEAR"
    top_total = top.get("total", "?") if top else "?"

    you_do_parts = [
        "Select one ranked lane (rubric ranks; Matt selects; not authorization):",
        *ranked_lines,
        f"Persisted board: {RANKED_ACTIONS_REL} — refresh with "
        f"`python3 scripts/mmi_lane_board_sync.py` after repo changes.",
        f"Maintain drift defense: pytest {INVARIANTS_PROBE_TEST_REL} after any "
        f"scripts/mmi_*.py change.",
    ]

    return {
        "WHAT_NEEDS_MATT": (
            f"Select one ranked lane — top [{top_total}/10]: {top_label}. "
            f"Dispatcher ALL_CLEAR; buildable_count=0."
        ),
        "IN_FLIGHT": "none",
        "HAND_IT_TO": ROSTER_MATT,
        "YOU_DO": "\n".join(you_do_parts),
        "WHY": why,
        "IGNORE_FOR_NOW": _ignore_block(evidence, repo_root=repo_root),
        "SOURCE": _source_line(evidence, repo_root=repo_root)
        + f"; ranked_board: {RANKED_ACTIONS_REL}",
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

    awaiting_audit = _relay_awaiting_audit_gated(evidence)
    if awaiting_audit is not None:
        return _compose_awaiting_audit_gated_voice(evidence, awaiting_audit)

    buildable = _relay_buildable_option(evidence)
    if buildable is not None:
        return _compose_buildable_voice(evidence, buildable)

    governance_voice = _relay_signed_governance_framework(root, evidence)
    if governance_voice is not None:
        return governance_voice

    if evidence.feedstock_first and evidence.dispatcher_mode == "ALL_CLEAR":
        if not (
            evidence.feedstock_first in GOVERNANCE_FRAMEWORK_CONTRACTS
            and _governance_framework_lane_closed(root, evidence.feedstock_first)
        ):
            contract_rel = _contract_rel_for_candidate(evidence.feedstock_first)
            if contract_rel and (root / contract_rel).is_file():
                if not _is_contract_signed(root, contract_rel):
                    gate_rel = _contract_gate_clean(root, evidence.feedstock_first)
                    if gate_rel:
                        if evidence.feedstock_lane_type == "CONTRACT_DRAFT":
                            return _compose_gate_clean_contract_draft_voice(
                                evidence, contract_rel, gate_rel, root
                            )
                        return _compose_gate_clean_contract_review_voice(
                            evidence, contract_rel, gate_rel, root
                        )
                    if evidence.feedstock_lane_type == "CONTRACT_DRAFT":
                        return _compose_unsigned_contract_draft_voice(
                            evidence, contract_rel
                        )
                    return _compose_unsigned_contract_review_voice(
                        evidence, contract_rel
                    )
                if (
                    evidence.feedstock_first == "#1"
                    and _is_contract_signed(root, contract_rel)
                ):
                    return _compose_signed_swarm_commander_contract_voice(
                        evidence, contract_rel, root
                    )
                if (
                    evidence.feedstock_first == "#3"
                    and _is_contract_signed(root, contract_rel)
                ):
                    return _compose_signed_risk_triage_contract_voice(
                        evidence, contract_rel, root
                    )
                if (
                    evidence.feedstock_first == "#105"
                    and not _governance_framework_lane_closed(root, "#105")
                ):
                    return _compose_signed_invariants_framework_voice(
                        evidence, contract_rel
                    )
            return _compose_feedstock_voice(evidence)

    unreconciled = _relay_signed_unreconciled(root, evidence.menu_options)
    if unreconciled is not None:
        contract_rel = _contract_rel_for_candidate(unreconciled.candidate_id) or ""
        return _compose_signed_unreconciled_voice(evidence, unreconciled, contract_rel)

    if not _all_clear_hold_posture(evidence, root):
        relay = _relay_contract_candidate(evidence.menu_options)
        if relay is not None:
            contract_rel = _contract_rel_for_candidate(relay.candidate_id)
            if (
                contract_rel
                and (root / contract_rel).is_file()
                and not _is_contract_signed(root, contract_rel)
            ):
                relay_evidence = replace(
                    evidence,
                    feedstock_first=relay.candidate_id,
                    feedstock_first_name=relay.candidate_name,
                )
                return _compose_unsigned_contract_review_voice(
                    relay_evidence, contract_rel
                )
        if relay is not None or evidence.missing_contract_count > 0:
            return _compose_missing_contract_voice(evidence, relay)

    if _all_clear_hold_posture(evidence, root):
        return _compose_all_clear_hold_voice(evidence, root)

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
