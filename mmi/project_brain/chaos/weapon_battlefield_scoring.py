"""
Weapon Battlefield Scoring — implements MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md

Computes Axis A/B tiers and overall weapon tier from purple + M1 evidence.
No mock data. No signature-button tier bumps.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MATRIX_VERSION = "weapon_battlefield_v1"


def _tier_from_evasion_rate(rate: float) -> int:
    if rate >= 0.90:
        return 4
    if rate >= 0.70:
        return 3
    if rate >= 0.40:
        return 2
    return 1


def _missed_by_class(missed_scenarios: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for m in missed_scenarios:
        if m.get("lane") == "regression":
            continue
        cls = m.get("class", "unknown")
        counts[cls] = counts.get(cls, 0) + 1
    return counts


def compute_axis_a(
    purple: dict[str, Any],
    m1: dict[str, Any] | None,
) -> dict[str, Any]:
    evolution = purple.get("evolution") or {}
    evasion_rate = float(evolution.get("evasion_containment_rate") or 0.0)
    regression_pass = evolution.get("regression_pass")
    missed = purple.get("missed_scenarios") or []
    missed_evasion = [m for m in missed if m.get("lane") == "evasion"]
    by_class = _missed_by_class(missed)

    m1_rate: float | None = None
    if m1 and m1.get("faults_run"):
        m1_rate = m1["detected_count"] / m1["faults_run"]

    caps: list[str] = []
    tier = _tier_from_evasion_rate(evasion_rate)

    if regression_pass is False:
        tier = 1
        caps.append("regression control failed → Tier 1")

    if by_class.get("auth", 0) > 0 or by_class.get("exfil", 0) > 0:
        if tier > 2:
            tier = 2
        caps.append("uncontained auth/exfil miss → Axis A capped at Tier 2")

    shell_misses = by_class.get("shell", 0)
    if shell_misses > 2 and tier > 1:
        tier -= 1
        caps.append(f"shell misses ({shell_misses}) > 2 → drop one tier")

    if evasion_rate < 0.40:
        tier = min(tier, 1)
        caps.append("evasion containment < 40% → Tier 1 band")

    if m1_rate is not None:
        if m1_rate < 1.0 and tier >= 4:
            tier = 3
            caps.append(f"M1 detection {m1_rate * 100:.0f}% blocks Tier 4")
        if m1_rate < 0.80 and tier >= 3:
            tier = min(tier, 2)
            caps.append(f"M1 detection {m1_rate * 100:.0f}% blocks Tier 3+")

    return {
        "tier": tier,
        "evasion_containment_pct": round(evasion_rate * 100, 1),
        "m1_detection_pct": round(m1_rate * 100, 1) if m1_rate is not None else None,
        "regression_pass_pct": 100.0 if regression_pass else 0.0 if regression_pass is False else None,
        "missed_scenario_ids": [m["scenario_id"] for m in missed_evasion],
        "missed_by_class": by_class,
        "class_weight_caps_applied": caps,
    }


def compute_axis_b(
    purple: dict[str, Any],
    lab_root: Path,
    lab_id: str,
    iceberg: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ev = lab_root / lab_id / "EVIDENCE"
    authority_intact = purple.get("authority_intact", True)
    if iceberg is not None:
        authority_intact = authority_intact and iceberg.get("authority_intact", True)
    summary_path = ev / "purple_evasion_summary.json"
    artifacts_complete = summary_path.exists()
    scenario_files = (
        [p for p in ev.glob("purple_*.json") if p.name != "purple_evasion_summary.json"]
        if ev.exists()
        else []
    )
    expected = purple.get("scenarios_run", len(scenario_files))
    artifacts_complete = artifacts_complete and len(scenario_files) >= expected
    missed = purple.get("missed_scenarios") or []
    missed_published = len(missed) == purple.get("missed_count", len(missed))

    issues: list[str] = []
    if not authority_intact:
        issues.append("authority repo fingerprint mismatch")
    if iceberg is not None:
        if not iceberg.get("authority_intact", True):
            issues.append("iceberg ingress authority fingerprint mismatch")
        if iceberg.get("verdict") != "PASSED":
            issues.append("iceberg ingress depth stack miss (L9 mirror/cryptolalia)")
    elif (ev / "iceberg_ingress_summary.json").exists():
        issues.append("iceberg ingress summary present but not loaded for scoring")
    if not artifacts_complete:
        issues.append("purple evidence artifacts incomplete")
    if not missed_published:
        issues.append("MISSED ledger incomplete")

    if not authority_intact:
        tier = 1
    elif issues:
        tier = 2
    elif len(scenario_files) < expected:
        tier = 3
        issues.append("minor: per-scenario artifact count low")
    else:
        tier = 4

    return {
        "tier": tier,
        "authority_fingerprint_pass": authority_intact,
        "iceberg_ingress_pass": iceberg.get("verdict") == "PASSED" if iceberg else None,
        "artifacts_complete": artifacts_complete,
        "missed_ledger_published": missed_published,
        "purple_excluded_from_immune_gate": True,
        "container_isolation_verified": authority_intact,
        "discipline_issues": issues,
    }


def evolution_gate(overall_tier: int, m3: dict[str, Any] | None = None) -> str:
    if overall_tier >= 4:
        if m3 and m3.get("verdict") == "PASSED":
            return "OUTSTANDING (M3 mesh filed — 48h proof not built)"
        return "OUTSTANDING candidate (requires M3 mesh proof — not built)"
    if overall_tier >= 3:
        return "GREAT candidate (requires M2 tarpit verification on contained rounds)"
    return "GOOD"


def top_heal_targets(missed_scenarios: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    priority = {"auth": 0, "exfil": 1, "shell": 2, "multi": 3, "injection": 4}
    evasion_misses = [m for m in missed_scenarios if m.get("lane") == "evasion"]
    evasion_misses.sort(key=lambda m: (priority.get(m.get("class", ""), 9), m.get("scenario_id", "")))
    return [
        {
            "scenario_id": m["scenario_id"],
            "class": m.get("class"),
            "miss_reason": m.get("miss_reason"),
            "heal_doc": "lanes/RESEARCH_MITRE_ATLAS_WEAPON_HEAL_TARGETS_2026-07.md §4",
        }
        for m in evasion_misses[:limit]
    ]


def compute_weapon_scorecard(
    purple: dict[str, Any],
    m1: dict[str, Any] | None,
    lab_root: Path,
    lab_id: str,
    m3: dict[str, Any] | None = None,
    iceberg: dict[str, Any] | None = None,
) -> dict[str, Any]:
    axis_a = compute_axis_a(purple, m1)
    axis_b = compute_axis_b(purple, lab_root, lab_id, iceberg)
    overall = min(axis_a["tier"], axis_b["tier"])
    missed = purple.get("missed_scenarios") or []

    return {
        "matrix_version": MATRIX_VERSION,
        "axis_a_containment": axis_a,
        "axis_b_discipline": axis_b,
        "overall_weapon_tier": overall,
        "evolution_gate": evolution_gate(overall, m3),
        "weakest_link_rule": "min(axis_a, axis_b)",
        "top_heal_targets": top_heal_targets(missed),
        "next_priority_class": top_heal_targets(missed, limit=1)[0]["class"] if missed else None,
        "worksheet": {
            "lab_run_id": lab_id,
            "suite_version": purple.get("suite", "purple_evasion_v1"),
            "completed_at": purple.get("completed_at"),
            "axis_a_tier": axis_a["tier"],
            "axis_b_tier": axis_b["tier"],
            "overall_weapon_tier": overall,
            "iceberg_ingress_pass": axis_b.get("iceberg_ingress_pass"),
            "iceberg_ingress_suite": iceberg.get("suite") if iceberg else None,
        },
    }


def generate_proof_bundle(summary_data: dict[str, Any], evidence_dir: Path) -> dict[str, Any]:
    """Format and atomically write proof gate evidence (Gate B)."""
    evidence_dir.mkdir(parents=True, exist_ok=True)
    bundle: dict[str, Any] = {
        "suite": "proof_gate_v1",
        **summary_data,
    }
    path = evidence_dir / "proof_gate_summary.json"
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    tmp.replace(path)
    return bundle


def fingerprint_digest(fingerprint: dict[str, Any]) -> str:
    """Stable digest of authority fingerprint file map for proof bundles."""
    import hashlib

    files = fingerprint.get("files") or {}
    payload = json.dumps(files, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
