#!/usr/bin/env python3
"""MMI Mission Map — chain-of-command stage position engine (stdout only).

Reads mmi/MMI_CHAIN_OF_COMMAND_MISSION_MAP.yaml, evaluates repo state against
stage START/END markers and waypoint complete_when clauses, and emits the
current stage plus next executable waypoint for PMV relay.

Does not write files, authorize build, or mutate scoreboard/BOR/registry.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ENVELOPE = "MISSION_MAP_POSITION"
ENVELOPE_INCOMPLETE = "MISSION_MAP_INPUTS_INCOMPLETE"
MAP_REL = "mmi/MMI_CHAIN_OF_COMMAND_MISSION_MAP.yaml"
DECISION_LOG_REL = "mmi/MMI_DECISION_LOG.md"
CURRENT_STATE_REL = "MMI_CURRENT_STATE.md"

FORBIDDEN_TOKENS = frozenset(
    {
        "AUTHORIZED",
        "BUILD_AUTHORIZED",
        "AUTONOMOUSLY_SELECTED",
        "SELECTED",
        "NEXT_DECIDED",
        "PROMOTED",
        "GOVERNED_AGENT",
    }
)


@dataclass
class WaypointView:
    waypoint_id: str
    label: str
    hand_to: str
    you_do: str
    requires_matt_escalation: bool = False


@dataclass
class MissionMapPosition:
    active: bool
    stage_id: str = ""
    stage_name: str = ""
    stage_start_label: str = ""
    stage_end_label: str = ""
    completed_waypoints: list[WaypointView] = field(default_factory=list)
    next_waypoint: WaypointView | None = None
    upcoming_waypoints: list[WaypointView] = field(default_factory=list)
    all_stages_complete: bool = False
    reason: str = ""


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _load_map(root: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML required for mission map engine")
    path = root / MAP_REL
    if not path.is_file():
        raise FileNotFoundError(MAP_REL)
    data = yaml.safe_load(_read_text(path))
    if not isinstance(data, dict):
        raise ValueError(f"{MAP_REL} must be a mapping")
    return data


def _last_completed_block(root: Path) -> str:
    state = _read_text(root / CURRENT_STATE_REL)
    capture = False
    lines: list[str] = []
    for line in state.splitlines():
        if line.startswith("LAST_COMPLETED:"):
            capture = True
            lines.append(line.replace("LAST_COMPLETED:", "").strip())
            continue
        if capture:
            if line.startswith("PRIOR") or line.startswith("REVIEW_"):
                break
            if line.strip():
                lines.append(line.strip())
    return " ".join(lines)


def _eval_condition(condition: dict, root: Path, cache: dict[str, str]) -> bool:
    if not isinstance(condition, dict):
        return False
    kind = condition.get("type", "")
    if kind == "all_of":
        nested = condition.get("conditions") or []
        return all(_eval_condition(item, root, cache) for item in nested)
    if kind == "any_of":
        nested = condition.get("conditions") or []
        return any(_eval_condition(item, root, cache) for item in nested)
    if kind == "decision_log_contains":
        if "decision_log" not in cache:
            cache["decision_log"] = _read_text(root / DECISION_LOG_REL)
        pattern = str(condition.get("pattern", ""))
        if not pattern:
            return False
        prefix = f"{pattern} |"
        for line in cache["decision_log"].splitlines():
            if line.startswith(prefix):
                return True
        return False
    if kind == "last_completed_contains":
        pattern = str(condition.get("pattern", ""))
        return bool(pattern) and pattern in _last_completed_block(root)
    if kind == "file_exists":
        rel = str(condition.get("path", ""))
        return bool(rel) and (root / rel).is_file()
    if kind == "file_contains":
        rel = str(condition.get("path", ""))
        pattern = str(condition.get("pattern", ""))
        if not rel or not pattern:
            return False
        if rel not in cache:
            cache[rel] = _read_text(root / rel)
        return pattern in cache[rel]
    return False


def _eval_conditions(conditions: list | None, root: Path, cache: dict[str, str]) -> bool:
    if not conditions:
        return True
    return all(_eval_condition(item, root, cache) for item in conditions)


def _waypoint_view(raw: dict) -> WaypointView:
    return WaypointView(
        waypoint_id=str(raw.get("id", "")),
        label=str(raw.get("label", "")),
        hand_to=str(raw.get("hand_to", "Matt")),
        you_do=str(raw.get("you_do", "")).strip(),
        requires_matt_escalation=bool(raw.get("requires_matt_escalation", False)),
    )


def analyze(root: Path | None = None) -> MissionMapPosition:
    root = root or _repo_root()
    cache: dict[str, str] = {}
    try:
        data = _load_map(root)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        return MissionMapPosition(active=False, reason=str(exc))

    stages = data.get("stages") or []
    if not stages:
        return MissionMapPosition(active=False, reason="no stages in mission map")

    for stage in stages:
        if not isinstance(stage, dict):
            continue
        start_ok = _eval_conditions(
            (stage.get("start") or {}).get("complete_when"), root, cache
        )
        if not start_ok:
            continue
        end_ok = _eval_conditions(
            (stage.get("end") or {}).get("complete_when"), root, cache
        )
        if end_ok:
            continue

        stage_id = str(stage.get("id", ""))
        stage_name = str(stage.get("name", stage_id))
        start_label = str((stage.get("start") or {}).get("label", ""))
        end_label = str((stage.get("end") or {}).get("label", ""))
        raw_waypoints = stage.get("waypoints") or []

        completed: list[WaypointView] = []
        next_wp: WaypointView | None = None
        upcoming: list[WaypointView] = []
        seen_next = False
        for raw in raw_waypoints:
            if not isinstance(raw, dict):
                continue
            view = _waypoint_view(raw)
            if _eval_conditions(raw.get("complete_when"), root, cache):
                completed.append(view)
                continue
            if not seen_next:
                next_wp = view
                seen_next = True
            else:
                upcoming.append(view)

        if next_wp is None and not raw_waypoints:
            return MissionMapPosition(
                active=True,
                stage_id=stage_id,
                stage_name=stage_name,
                stage_start_label=start_label,
                stage_end_label=end_label,
                completed_waypoints=completed,
                reason="stage has no waypoints; awaiting stage end marker",
            )

        return MissionMapPosition(
            active=True,
            stage_id=stage_id,
            stage_name=stage_name,
            stage_start_label=start_label,
            stage_end_label=end_label,
            completed_waypoints=completed,
            next_waypoint=next_wp,
            upcoming_waypoints=upcoming,
            reason="active stage with pending waypoint"
            if next_wp
            else "stage waypoints complete; awaiting stage end marker",
        )

    return MissionMapPosition(
        active=True,
        all_stages_complete=True,
        reason="all stages complete per map markers",
    )


def _forbidden_scan(text: str) -> list[str]:
    upper = text.upper()
    return sorted(token for token in FORBIDDEN_TOKENS if token in upper)


def render_stdout(position: MissionMapPosition, root: Path) -> str:
    lines = [ENVELOPE]
    if not position.active:
        lines = [ENVELOPE_INCOMPLETE, f"reason: {position.reason}"]
        return "\n".join(lines) + "\n"

    if position.all_stages_complete:
        lines.extend(
            [
                "status: ALL_STAGES_COMPLETE",
                f"reason: {position.reason}",
                f"map: {MAP_REL}",
            ]
        )
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            f"stage_id: {position.stage_id}",
            f"stage_name: {position.stage_name}",
            f"stage_start: {position.stage_start_label}",
            f"stage_end: {position.stage_end_label}",
            f"completed_waypoints: {len(position.completed_waypoints)}",
        ]
    )
    if position.next_waypoint:
        wp = position.next_waypoint
        lines.extend(
            [
                "next_waypoint:",
                f"  id: {wp.waypoint_id}",
                f"  label: {wp.label}",
                f"  hand_to: {wp.hand_to}",
                f"  requires_matt_escalation: {str(wp.requires_matt_escalation).lower()}",
                f"  you_do: {wp.you_do}",
            ]
        )
    else:
        lines.append("next_waypoint: (none — awaiting stage end marker)")
    if position.upcoming_waypoints:
        lines.append("upcoming_waypoints:")
        for item in position.upcoming_waypoints[:5]:
            lines.append(f"  - {item.waypoint_id}: {item.label}")
    lines.append(f"map: {MAP_REL}")
    lines.append(f"git_head: {_git_head(root)}")
    body = "\n".join(lines) + "\n"
    hits = _forbidden_scan(body)
    if hits:
        raise RuntimeError(f"forbidden tokens in mission map output: {', '.join(hits)}")
    return body


def _git_head(root: Path) -> str:
    head = root / ".git" / "HEAD"
    if not head.is_file():
        return "unknown"
    ref = _read_text(head).strip()
    if ref.startswith("ref:"):
        ref_path = root / ".git" / ref.split(":", 1)[1].strip()
        if ref_path.is_file():
            return _read_text(ref_path).strip()[:12]
    return ref[:12] if ref else "unknown"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MMI chain-of-command mission map")
    parser.add_argument(
        "--position",
        action="store_true",
        help="Emit MISSION_MAP_POSITION envelope (default)",
    )
    args = parser.parse_args(argv)
    root = _repo_root()
    position = analyze(root)
    sys.stdout.write(render_stdout(position, root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
