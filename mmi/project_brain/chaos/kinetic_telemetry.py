"""
Kinetic Warfare telemetry — slot map + AFE ledger from chaos lab mirror state.

STATUS: CONCEPT — local chaos lab console only
See: architecture/MMI_KINETIC_WARFARE_DASHBOARD_SPEC_2026-07.md
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AIR_LOCK_SLOTS = 700
BASELINE_GREEN = 70  # Inhale baseline workers (Addendum 04)
ATTACKER_USD_PER_1K_TOKENS = 0.015
LOCAL_USD_PER_COMPUTE_CYCLE = 0.00001

from weapon_battlefield_scoring import compute_weapon_scorecard


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def scan_mirror_cells(mirror_root: Path) -> list[dict[str, Any]]:
    cells_dir = mirror_root / "cells"
    if not cells_dir.exists():
        return []
    out: list[dict[str, Any]] = []
    for cell in sorted(cells_dir.iterdir()):
        if not cell.is_dir():
            continue
        record = _read_json(cell / "route_record.json") or {}
        crypto_path = cell / "cryptolalia_stream.txt"
        raw_path = cell / "raw_payload.txt"
        crypto_bytes = crypto_path.stat().st_size if crypto_path.exists() else 0
        raw_bytes = raw_path.stat().st_size if raw_path.exists() else 0
        agent_id = record.get("agent_id") or cell.name
        out.append(
            {
                "agent_id": agent_id,
                "cell": cell.as_posix(),
                "critic_hits": (record.get("critic") or {}).get("critic_hits", []),
                "cryptolalia_bytes": crypto_bytes or record.get("cryptolalia_bytes", 0),
                "raw_payload_bytes": raw_bytes,
                "routed_at": record.get("routed_at"),
                "payload_sha256": record.get("payload_sha256"),
            }
        )
    return out


def build_slot_map(contained_count: int) -> dict[str, Any]:
    """
    700 Air-Lock slots: 1–70 green baseline, 71+ red for contained, remainder grey.
    """
    red_count = min(contained_count, AIR_LOCK_SLOTS - BASELINE_GREEN)
    grey_count = AIR_LOCK_SLOTS - BASELINE_GREEN - red_count
    red_indices = list(range(BASELINE_GREEN + 1, BASELINE_GREEN + 1 + red_count))
    return {
        "total": AIR_LOCK_SLOTS,
        "green": BASELINE_GREEN,
        "green_range": [1, BASELINE_GREEN],
        "red": red_count,
        "red_indices": red_indices,
        "grey": grey_count,
        "grey_range": [BASELINE_GREEN + red_count + 1, AIR_LOCK_SLOTS] if grey_count else [],
    }


def compute_afe(cells: list[dict[str, Any]]) -> dict[str, Any]:
    cryptolalia_total = sum(c.get("cryptolalia_bytes", 0) for c in cells)
    raw_total = sum(c.get("raw_payload_bytes", 0) for c in cells)
    # Attacker must chew through cryptolalia + reasoning on raw — token est ~ bytes/4
    attacker_tokens = (cryptolalia_total + raw_total) // 4
    local_cycles = len(cells) * 2 + 1  # route + tarpit gen per cell
    attacker_usd = (attacker_tokens / 1000) * ATTACKER_USD_PER_1K_TOKENS
    local_usd = local_cycles * LOCAL_USD_PER_COMPUTE_CYCLE
    ratio = attacker_usd / max(local_usd, 0.0001)
    return {
        "attacker_tokens_est": attacker_tokens,
        "cryptolalia_bytes_total": cryptolalia_total,
        "raw_payload_bytes_total": raw_total,
        "attacker_loss_usd": round(attacker_usd, 2),
        "local_cost_usd": round(local_usd, 4),
        "asymmetric_ratio": f"1:{round(ratio, 1)}",
        "local_compute_cycles": local_cycles,
    }


def map_red_agents(slot_map: dict[str, Any], cells: list[dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for idx, cell in zip(slot_map.get("red_indices", []), cells):
        mapping[str(idx)] = cell.get("agent_id", "unknown")
    return mapping


def _is_purple_lab_cell(agent_id: str) -> bool:
    return agent_id.startswith("purple_")


def build_pending_patches(cells: list[dict[str, Any]], mirror_root: Path) -> dict[str, Any]:
    adversary: list[dict[str, Any]] = []
    purple_lab: list[dict[str, Any]] = []
    for cell in cells:
        agent_id = cell["agent_id"]
        cell_path = Path(cell["cell"])
        sanitized_path = cell_path / "sanitized_payload.txt"
        preview = ""
        if sanitized_path.exists():
            preview = sanitized_path.read_text(encoding="utf-8")[:500]
        is_purple = _is_purple_lab_cell(agent_id)
        entry = {
            "agent_id": agent_id,
            "sanitized_preview": preview,
            "critic_hits": cell.get("critic_hits", []),
            "purple_lab": is_purple,
            "status": (
                "PURPLE_LAB_TEST — NOT FOR IMMUNIZATION"
                if is_purple
                else "PENDING_MATT_SIGNATURE"
            ),
        }
        if is_purple:
            purple_lab.append(entry)
        else:
            adversary.append(entry)
    return {"adversary": adversary, "purple_lab": purple_lab}


def load_m1_summary(lab_root: Path, lab_id: str) -> dict[str, Any] | None:
    ev = lab_root / lab_id / "EVIDENCE"
    path = ev / "smash_all_summary.json"
    if path.exists():
        return _read_json(path)
    detections = sorted(ev.glob("detect_*.json")) if ev.exists() else []
    if not detections:
        return None
    detected = 0
    missed: list[str] = []
    for p in detections:
        row = _read_json(p) or {}
        if row.get("detected"):
            detected += 1
        elif row.get("missed"):
            missed.append(row.get("fault", p.stem))
    return {
        "lab_id": lab_id,
        "faults_run": len(detections),
        "detected_count": detected,
        "missed_count": len(missed),
        "missed_faults": missed,
    }


def load_purple_summary(lab_root: Path, lab_id: str) -> dict[str, Any] | None:
    path = lab_root / lab_id / "EVIDENCE" / "purple_evasion_summary.json"
    return _read_json(path)


def load_m3_summary(lab_root: Path, lab_id: str) -> dict[str, Any] | None:
    ev = lab_root / lab_id / "EVIDENCE"
    for name in ("m3_mesh_summary.json", "mesh_smash_m3.json"):
        path = ev / name
        if path.exists():
            return _read_json(path)
    return None


def load_iceberg_summary(lab_root: Path, lab_id: str) -> dict[str, Any] | None:
    ev = lab_root / lab_id / "EVIDENCE"
    for name in ("iceberg_ingress_summary.json", "iceberg_mirror_smash.json"):
        path = ev / name
        if path.exists():
            return _read_json(path)
    return None


def load_action_integrity_summary(lab_root: Path, lab_id: str) -> dict[str, Any] | None:
    ev = lab_root / lab_id / "EVIDENCE"
    path = ev / "action_integrity_summary.json"
    if path.exists():
        return _read_json(path)
    return None


def build_battlefield_scorecard(lab_root: Path, lab_id: str) -> dict[str, Any]:
    purple = load_purple_summary(lab_root, lab_id)
    m1 = load_m1_summary(lab_root, lab_id)
    m3 = load_m3_summary(lab_root, lab_id)
    iceberg = load_iceberg_summary(lab_root, lab_id)

    if not purple:
        return {
            "available": False,
            "message": "Run: python3 scripts/chaos_lab_provisioner.py purple-evasion --lab-id " + lab_id,
            "m1_regression": m1,
            "m3_mesh": m3,
            "evolution": {"stage": "UNTESTED", "honest": False, "blockers": ["Purple evasion suite not run"]},
        }

    loss = purple.get("defender_loss_if_misses_hit_authority", {})
    evolution = purple.get("evolution", {})
    weapon = compute_weapon_scorecard(purple, m1, lab_root, lab_id, m3, iceberg)
    return {
        "available": True,
        "doctrine": purple.get("doctrine"),
        "scenarios_run": purple.get("scenarios_run", 0),
        "contained_count": purple.get("contained_count", 0),
        "missed_count": purple.get("missed_count", 0),
        "evasion_missed_count": purple.get("evasion_missed_count", 0),
        "containment_matrix": purple.get("containment_matrix", {}),
        "missed_scenarios": purple.get("missed_scenarios", []),
        "defender_loss": loss,
        "evolution": evolution,
        "weapon": weapon,
        "m1_regression": m1,
        "m3_mesh": m3,
        "completed_at": purple.get("completed_at"),
        "suite": purple.get("suite"),
    }


def build_telemetry(lab_root: Path, lab_id: str, authority_root: Path | None = None) -> dict[str, Any]:
    mirror_root = lab_root / lab_id / "MIRROR"
    index = _read_json(mirror_root / "contained_cells.json") or {}
    cells = scan_mirror_cells(mirror_root)
    if not cells and index:
        for agent_id, meta in index.items():
            cells.append(
                {
                    "agent_id": agent_id,
                    "cell": meta.get("cell", ""),
                    "critic_hits": meta.get("critic_hits", []),
                    "cryptolalia_bytes": 0,
                    "raw_payload_bytes": 0,
                    "routed_at": meta.get("routed_at"),
                }
            )

    adversary_cells = [c for c in cells if not _is_purple_lab_cell(c.get("agent_id", ""))]
    patch_groups = build_pending_patches(cells, mirror_root)

    slot_map = build_slot_map(len(adversary_cells))
    slot_map["red_agents"] = map_red_agents(slot_map, adversary_cells)
    afe = compute_afe(adversary_cells)

    scorecard = build_battlefield_scorecard(lab_root, lab_id)
    action_integrity = load_action_integrity_summary(lab_root, lab_id)
    afe_conditional = {
        **afe,
        "conditional_on_mirror_hit": True,
        "note": "Win-side AFE only — see scorecard.defender_loss for miss-side economics",
    }

    return {
        "timestamp": time.time(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lab_id": lab_id,
        "mirror_root": mirror_root.as_posix(),
        "slots": slot_map,
        "afe": afe_conditional,
        "scorecard": scorecard,
        "action_integrity": action_integrity,
        "contained_cells": index,
        "cell_details": cells,
        "pending_patches": patch_groups["adversary"],
        "purple_lab_cells": patch_groups["purple_lab"],
        "authority_root": authority_root.as_posix() if authority_root else None,
    }
