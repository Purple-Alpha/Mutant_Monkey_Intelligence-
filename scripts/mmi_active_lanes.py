#!/usr/bin/env python3
"""MMI Active Lane Console — Mode A read-only five-lane operator feed.

Surfaces one active item per lane (RESEARCH, DESIGN, BUILD, AUDIT, REVISE)
from existing MMI evidence. Does not authorize, route, assign, or mutate state.

Authority: operator-facing decision surface only (MMI_ACTIVE_LANE_CONSOLE_MODE_A).
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ENVELOPE = "MMI ACTIVE LANES"

LANES = ("RESEARCH", "DESIGN", "BUILD", "AUDIT", "REVISE")

LANE_STATES = frozenset(
    {
        "LANE_EMPTY",
        "EVIDENCE_MISSING",
        "EVIDENCE_PRESENT",
        "READY_FOR_REVIEW",
        "READY_FOR_OPERATOR_DECISION",
        "AUTHORIZED",
        "IN_PROGRESS",
        "COMPLETED",
        "BLOCKED",
        "PARKED",
        "SUPERSEDED",
        "FORBIDDEN",
    }
)

DEFAULT_AUTHORITY = "OPERATOR_REQUIRED"
BUILD_FORBIDDEN = "BUILD_FORBIDDEN_UNTIL_SIGNED"

EVIDENCE_PATHS = (
    "MMI_CURRENT_STATE.md",
    "mmi/MMI_HEALTH_STATE.md",
    "mmi/MMI_DECISION_LOG.md",
    "mmi/MMI_GATE_REGISTRY.md",
    "mmi/MMI_REPO_SURFACE_REGISTRY.md",
    "mmi/MMI_AUTONOMOUS_BRAIN_STAGE1_GAPS.md",
    "mmi/MMI_RANKED_NEXT_ACTIONS.md",
    "mmi/research/MMI_MESH_HARDENING_RESEARCH_CLOSEOUT_MMI-DEC-131.md",
    "docs/mmi/contracts/004_immune_federation_mesh_contract.md",
    "mmi/concepts/MMI_IMMUNE_FEDERATION_MESH_HARDENING_ADDENDUM.md",
)

MESH_CLOSEOUT_REL = "mmi/research/MMI_MESH_HARDENING_RESEARCH_CLOSEOUT_MMI-DEC-131.md"
MESH_CONTRACT_REL = "docs/mmi/contracts/004_immune_federation_mesh_contract.md"
MESH_ADDENDUM_REL = "mmi/concepts/MMI_IMMUNE_FEDERATION_MESH_HARDENING_ADDENDUM.md"
DECISION_LOG_REL = "mmi/MMI_DECISION_LOG.md"
CURRENT_STATE_REL = "MMI_CURRENT_STATE.md"
SCOREBOARD_REL = "agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md"

FORBIDDEN_NEXT_PATTERNS = (
    re.compile(r"\bauto[- ]?run build\b", re.I),
    re.compile(r"\bbuild after research evidence\b", re.I),
    re.compile(r"\bautonomous(ly)?\s+(build|route|select)\b", re.I),
)


@dataclass(frozen=True)
class LaneView:
    lane: str
    active: str
    state: str
    evidence: str
    next_action: str
    actor: str
    authority: str
    pugh: str = "+"
    risk_alert: str = ""


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _read_text(root: Path, rel: str) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except OSError:
        return ""


def _file_exists(root: Path, rel: str) -> bool:
    return (root / rel).is_file()


def _decision_present(log: str, decision_id: str) -> bool:
    return bool(re.search(rf"^{re.escape(decision_id)}\s*\|", log, re.M))


def _parse_dispatcher_counts(state: str) -> dict[str, int]:
    counts = {"SIGNED_UNBUILT": 0, "AWAITING_AUDIT": 0, "GATED": 0}
    match = re.search(
        r"(\d+)\s+SIGNED_UNBUILT,\s+(\d+)\s+AWAITING_AUDIT,\s+(\d+)\s+GATED",
        state,
    )
    if match:
        counts["SIGNED_UNBUILT"] = int(match.group(1))
        counts["AWAITING_AUDIT"] = int(match.group(2))
        counts["GATED"] = int(match.group(3))
    return counts


def _scoreboard_status(line: str) -> str:
    if not line.startswith("|"):
        return ""
    cells = [c.strip() for c in line.split("|")]
    if len(cells) < 4:
        return ""
    return cells[3]


def _scoreboard_name(line: str) -> tuple[str, str]:
    if not line.startswith("|"):
        return "", ""
    cells = [c.strip() for c in line.split("|")]
    if len(cells) < 3:
        return "", ""
    return cells[1].strip(), cells[2].strip()


def _signed_unbuilt_rows(scoreboard: str) -> list[str]:
    rows: list[str] = []
    for line in scoreboard.splitlines():
        status = _scoreboard_status(line)
        if not status.startswith("`SIGNED_UNBUILT") and not status.startswith("SIGNED_UNBUILT"):
            continue
        agent_id, name = _scoreboard_name(line)
        if agent_id.isdigit():
            rows.append(f"#{agent_id} {name}")
    return rows


def _awaiting_audit_rows(scoreboard: str) -> list[str]:
    rows: list[str] = []
    for line in scoreboard.splitlines():
        status = _scoreboard_status(line)
        if not status.startswith("`AWAITING_AUDIT") and not status.startswith("AWAITING_AUDIT"):
            continue
        agent_id, name = _scoreboard_name(line)
        if agent_id.isdigit():
            rows.append(f"#{agent_id} {name}")
    return rows


def _mesh_contract_signed(contract: str) -> bool:
    return "§11 SIGNED" in contract or "SIGNED 2026" in contract


def _mesh_contract_build_blocked(contract: str) -> bool:
    upper = contract.upper()
    return "NOT BUILD AUTHORIZED" in upper or "IMPLEMENTATION:** **BLOCKED" in contract


def _classify_pugh(next_action: str, lane: str) -> tuple[str, str]:
    for pattern in FORBIDDEN_NEXT_PATTERNS:
        if pattern.search(next_action):
            return "-", "RISK_ALERT: violates no-autonomous-build doctrine"
    if lane == "BUILD" and re.search(r"\b(build|implement)\b", next_action, re.I):
        if "forbidden" not in next_action.lower() and "no build" not in next_action.lower():
            return "-", "RISK_ALERT: build lane requires explicit operator authorization"
    maintenance = (
        "lane_board_sync",
        "ranked lane board",
        "mmi_dispatch --sync",
        "refresh handshake",
    )
    lowered = next_action.lower()
    if any(token in lowered for token in maintenance):
        return "0", ""
    return "+", ""


def _resolve_research_lane(root: Path, log: str) -> LaneView:
    closeout_exists = _file_exists(root, MESH_CLOSEOUT_REL)
    dec131 = _decision_present(log, "MMI-DEC-131")
    if closeout_exists and dec131:
        return LaneView(
            lane="RESEARCH",
            active="a05 Mesh hardening closeout → MMI-DEC-131",
            state="COMPLETED",
            evidence=(
                "Research closeout memo on disk; MMI-DEC-131 filed; "
                "findings transferred; mesh shares threat shape never tenant truth"
            ),
            next_action=(
                "Decide whether mesh hardening inputs advance to DESIGN review "
                "or remain PARKED_RESEARCH"
            ),
            actor="Matt",
            authority=DEFAULT_AUTHORITY,
        )
    if closeout_exists or dec131:
        return LaneView(
            lane="RESEARCH",
            active="Mesh hardening research closeout (partial evidence)",
            state="EVIDENCE_PRESENT",
            evidence="Partial research closeout evidence on disk",
            next_action="Supply missing research closeout record or decision log entry",
            actor="Matt / research worker",
            authority=DEFAULT_AUTHORITY,
        )
    gaps = _read_text(root, "mmi/MMI_AUTONOMOUS_BRAIN_STAGE1_GAPS.md")
    if gaps.strip():
        return LaneView(
            lane="RESEARCH",
            active="Stage 1 brain research gaps register",
            state="EVIDENCE_PRESENT",
            evidence="mmi/MMI_AUTONOMOUS_BRAIN_STAGE1_GAPS.md present",
            next_action="Review open research gap and file closeout memo",
            actor="Gemini / ChatGPT / research worker",
            authority=DEFAULT_AUTHORITY,
        )
    return LaneView(
        lane="RESEARCH",
        active="None",
        state="EVIDENCE_MISSING",
        evidence="missing",
        next_action="No research barrier identified from on-disk evidence",
        actor="None",
        authority=DEFAULT_AUTHORITY,
    )


def _resolve_design_lane(root: Path, log: str) -> LaneView:
    contract = _read_text(root, MESH_CONTRACT_REL)
    addendum = _read_text(root, MESH_ADDENDUM_REL)
    contract_exists = _file_exists(root, MESH_CONTRACT_REL)
    addendum_exists = _file_exists(root, MESH_ADDENDUM_REL)
    dec134 = _decision_present(log, "MMI-DEC-134")
    dec140 = _decision_present(log, "MMI-DEC-140")

    if contract_exists and (dec134 or dec140 or _mesh_contract_signed(contract)):
        blocked = _mesh_contract_build_blocked(contract)
        state = "READY_FOR_REVIEW"
        if blocked:
            authority = DEFAULT_AUTHORITY
            next_action = (
                "Review Immune Federation Mesh contract addendum "
                "(Guardrail 11, HMAC, replay/TTL, anti-poisoning); no build"
            )
        else:
            authority = DEFAULT_AUTHORITY
            next_action = "Review mesh architecture contract before any build authorization"
        evidence_parts = []
        if contract_exists:
            evidence_parts.append(MESH_CONTRACT_REL)
        if addendum_exists:
            evidence_parts.append("hardening addendum drafted")
        if dec140:
            evidence_parts.append("MMI-DEC-140 §11 signed")
        elif dec134:
            evidence_parts.append("MMI-DEC-134 contract draft filed")
        return LaneView(
            lane="DESIGN",
            active="Immune Federation Mesh / Pneumatic Lung hardening",
            state=state,
            evidence="; ".join(evidence_parts) or "contract draft on disk",
            next_action=next_action,
            actor="Matt / design worker",
            authority=authority,
        )

    if addendum_exists:
        return LaneView(
            lane="DESIGN",
            active="Immune Federation Mesh hardening addendum (concept)",
            state="EVIDENCE_PRESENT",
            evidence=MESH_ADDENDUM_REL,
            next_action="Promote hardening addendum to contract review draft when ready",
            actor="Claude / design worker",
            authority=DEFAULT_AUTHORITY,
        )

    return LaneView(
        lane="DESIGN",
        active="None",
        state="LANE_EMPTY",
        evidence="missing",
        next_action="No design contract candidate identified from on-disk evidence",
        actor="None",
        authority=DEFAULT_AUTHORITY,
    )


def _resolve_build_lane(root: Path) -> LaneView:
    state_text = _read_text(root, CURRENT_STATE_REL)
    scoreboard = _read_text(root, SCOREBOARD_REL)
    counts = _parse_dispatcher_counts(state_text)
    signed_rows = _signed_unbuilt_rows(scoreboard)

    if counts["SIGNED_UNBUILT"] > 0 and signed_rows:
        active = signed_rows[0]
        if len(signed_rows) > 1:
            active = f"{active} (+{len(signed_rows) - 1} more SIGNED_UNBUILT)"
        return LaneView(
            lane="BUILD",
            active=active,
            state="READY_FOR_OPERATOR_DECISION",
            evidence=(
                f"MMI_CURRENT_STATE: {counts['SIGNED_UNBUILT']} SIGNED_UNBUILT; "
                "§11 signed row present — separate build authorization still required"
            ),
            next_action="Matt must explicitly authorize build lane; no autonomous execution",
            actor="Matt",
            authority=DEFAULT_AUTHORITY,
        )

    if counts["AWAITING_AUDIT"] > 0:
        audit_rows = _awaiting_audit_rows(scoreboard)
        active = audit_rows[0] if audit_rows else "AWAITING_AUDIT row(s)"
        return LaneView(
            lane="BUILD",
            active="None (implementation held)",
            state="BLOCKED",
            evidence=(
                f"{counts['AWAITING_AUDIT']} AWAITING_AUDIT — build complete; "
                f"audit gate pending on {active}"
            ),
            next_action="No build action — completion gate before further implementation",
            actor="None",
            authority=BUILD_FORBIDDEN,
        )

    return LaneView(
        lane="BUILD",
        active="None",
        state="BLOCKED",
        evidence="No signed build contract in active SIGNED_UNBUILT queue",
        next_action="No build action",
        actor="None",
        authority=BUILD_FORBIDDEN,
    )


def _resolve_audit_lane(root: Path, log: str) -> LaneView:
    scoreboard = _read_text(root, SCOREBOARD_REL)
    awaiting = _awaiting_audit_rows(scoreboard)
    closeout = _read_text(root, MESH_CLOSEOUT_REL)

    if awaiting:
        return LaneView(
            lane="AUDIT",
            active=f"Completion gate — {awaiting[0]}",
            state="READY_FOR_REVIEW",
            evidence=f"Scoreboard AWAITING_AUDIT row; {len(awaiting)} pending",
            next_action=f"Run completion gate review for {awaiting[0]}",
            actor="Gemini / Grok / Codex",
            authority=DEFAULT_AUTHORITY,
        )

    if closeout and _decision_present(log, "MMI-DEC-131"):
        return LaneView(
            lane="AUDIT",
            active="Mesh anti-poisoning / replay / HMAC controls",
            state="READY_FOR_REVIEW",
            evidence=(
                "MMI-DEC-131 closeout + mesh hardening memo identify required audit surfaces"
            ),
            next_action="Create adversarial review checklist for mesh hardening controls",
            actor="Gemini / ChatGPT / security reviewer",
            authority=DEFAULT_AUTHORITY,
        )

    gate_registry = _read_text(root, "mmi/MMI_GATE_REGISTRY.md")
    if gate_registry.strip():
        return LaneView(
            lane="AUDIT",
            active="MMI gate registry standing review",
            state="EVIDENCE_PRESENT",
            evidence="mmi/MMI_GATE_REGISTRY.md present",
            next_action="Review next open gate from registry when operator selects",
            actor="Matt / security reviewer",
            authority=DEFAULT_AUTHORITY,
        )

    return LaneView(
        lane="AUDIT",
        active="None",
        state="LANE_EMPTY",
        evidence="missing",
        next_action="No audit surface identified from on-disk evidence",
        actor="None",
        authority=DEFAULT_AUTHORITY,
    )


def _resolve_revise_lane(root: Path) -> LaneView:
    return LaneView(
        lane="REVISE",
        active="Operator feed default",
        state="COMPLETED",
        evidence=(
            "PM Voice default is active-lane console; legacy governance envelope "
            "available via --verbose only"
        ),
        next_action=(
            "Retire ranked-board-first workflows; use plain `mmi_pm_voice.py` "
            "for five-lane feed"
        ),
        actor="Matt",
        authority=DEFAULT_AUTHORITY,
    )


def _apply_pugh(view: LaneView) -> LaneView:
    pugh, risk = _classify_pugh(view.next_action, view.lane)
    if pugh == "-" and not view.risk_alert:
        state = "FORBIDDEN"
        authority = "FORBIDDEN"
    elif pugh == "0":
        state = view.state if view.state != "LANE_EMPTY" else "PARKED"
    else:
        state = view.state
        authority = view.authority
    return LaneView(
        lane=view.lane,
        active=view.active,
        state=state,
        evidence=view.evidence,
        next_action=view.next_action,
        actor=view.actor,
        authority=authority,
        pugh=pugh,
        risk_alert=risk,
    )


def gather_lanes(root: Path | None = None) -> list[LaneView]:
    repo = root or _repo_root()
    log = _read_text(repo, DECISION_LOG_REL)
    raw = [
        _resolve_research_lane(repo, log),
        _resolve_design_lane(repo, log),
        _resolve_build_lane(repo),
        _resolve_audit_lane(repo, log),
        _resolve_revise_lane(repo),
    ]
    filtered: list[LaneView] = []
    for view in raw:
        adjusted = _apply_pugh(view)
        if adjusted.pugh == "0":
            filtered.append(
                LaneView(
                    lane=adjusted.lane,
                    active="Backlog (maintenance — hidden from default feed)",
                    state="PARKED",
                    evidence=adjusted.evidence,
                    next_action="See ranked board / sync scripts if needed",
                    actor="None",
                    authority=DEFAULT_AUTHORITY,
                    pugh="0",
                )
            )
        else:
            filtered.append(adjusted)
    return filtered


def format_lane(view: LaneView) -> str:
    lines = [
        f"[{view.lane}]",
        f"Active: {view.active}",
        f"State: {view.state}",
        f"Evidence: {view.evidence}",
        f"Next: {view.next_action}",
        f"Actor: {view.actor}",
        f"Authority: {view.authority}",
    ]
    if view.risk_alert:
        lines.append(f"Alert: {view.risk_alert}")
    return "\n".join(lines)


def format_console(lanes: list[LaneView]) -> str:
    parts = [ENVELOPE, ""]
    for view in lanes:
        parts.append(format_lane(view))
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="MMI Active Lane Console Mode A — read-only five-lane feed (stdout only)."
    )
    parser.add_argument("--root", type=Path, default=None, help="Repository root")
    args = parser.parse_args(argv)
    repo = args.root.resolve() if args.root else _repo_root()
    sys.stdout.write(format_console(gather_lanes(repo)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
