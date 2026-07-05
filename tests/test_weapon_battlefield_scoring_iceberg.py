from __future__ import annotations

from pathlib import Path

from weapon_battlefield_scoring import compute_weapon_scorecard


def _purple() -> dict:
    return {
        "suite": "purple_evasion_v1",
        "scenarios_run": 12,
        "missed_count": 0,
        "missed_scenarios": [],
        "authority_intact": True,
        "evolution": {
            "evasion_containment_rate": 1.0,
            "regression_pass": True,
        },
        "completed_at": "2026-07-02T00:00:00+00:00",
    }


def test_iceberg_fail_caps_axis_b(tmp_path: Path) -> None:
    lab_root = tmp_path / "lab"
    lab_id = "ice_fail"
    ev = lab_root / lab_id / "EVIDENCE"
    ev.mkdir(parents=True)
    (ev / "purple_evasion_summary.json").write_text("{}", encoding="utf-8")
    for i in range(12):
        (ev / f"purple_scenario_{i}.json").write_text("{}", encoding="utf-8")

    iceberg = {"verdict": "FAILED", "authority_intact": True, "suite": "iceberg_ingress_v1"}
    scorecard = compute_weapon_scorecard(_purple(), None, lab_root, lab_id, None, iceberg)
    assert scorecard["axis_b_discipline"]["tier"] == 2
    assert scorecard["overall_weapon_tier"] == 2


def test_iceberg_pass_allows_axis_b_tier4(tmp_path: Path) -> None:
    lab_root = tmp_path / "lab"
    lab_id = "ice_pass"
    ev = lab_root / lab_id / "EVIDENCE"
    ev.mkdir(parents=True)
    (ev / "purple_evasion_summary.json").write_text("{}", encoding="utf-8")
    for i in range(12):
        (ev / f"purple_scenario_{i}.json").write_text("{}", encoding="utf-8")

    m1 = {"faults_run": 5, "detected_count": 5}
    iceberg = {"verdict": "PASSED", "authority_intact": True, "suite": "iceberg_ingress_v1"}
    scorecard = compute_weapon_scorecard(_purple(), m1, lab_root, lab_id, None, iceberg)
    assert scorecard["axis_b_discipline"]["tier"] == 4
    assert scorecard["axis_b_discipline"]["iceberg_ingress_pass"] is True
