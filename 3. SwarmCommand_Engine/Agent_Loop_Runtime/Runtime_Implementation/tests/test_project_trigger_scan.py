"""Tests for the local read-only project trigger scanner."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.project_trigger_scan import (
    FORBIDDEN_AUTONOMOUS_ACTIONS,
    ScanResult,
    TriggerPacket,
    build_mission_envelope,
    run,
    scan,
)


def _fixed_now() -> datetime:
    return datetime(2026, 5, 22, 9, 30, 0, tzinfo=timezone.utc)


def _write_tracking(
    repo_root: Path,
    *,
    handshake_baseline: int | None,
    progress_baseline: int | None = None,
    include_master_index: bool = True,
    include_activity_log: bool = True,
    include_progress: bool = True,
    handshake_refs: list[str] | None = None,
    master_index_refs: list[str] | None = None,
    progress_status: str = "IN PROGRESS",
) -> None:
    refs = handshake_refs or []
    ref_lines = "\n".join(f"- `{ref}`" for ref in refs)
    handshake_body = f"# PROJECT_HANDSHAKE\n\n"
    if handshake_baseline is not None:
        handshake_body += f"Runtime baseline: {handshake_baseline} tests passing\n\n"
    if ref_lines:
        handshake_body += f"References:\n{ref_lines}\n"
    (repo_root / "PROJECT_HANDSHAKE.md").write_text(handshake_body, encoding="utf-8")

    if include_master_index:
        master_refs = master_index_refs or refs
        idx_lines = "\n".join(f"- `{ref}`" for ref in master_refs)
        (repo_root / "MASTER_INDEX.md").write_text(
            f"# MASTER_INDEX\n\nEntries:\n{idx_lines}\n",
            encoding="utf-8",
        )

    if include_activity_log:
        (repo_root / "PROJECT_ACTIVITY_LOG.md").write_text(
            "# PROJECT_ACTIVITY_LOG\n\nEntries omitted in fixture.\n",
            encoding="utf-8",
        )

    if include_progress:
        body = f"# PROGRESS\n\n## Active\n- {progress_status}: task A\n"
        if progress_baseline is not None:
            body += f"\nRuntime baseline (last verified): {progress_baseline} tests passing\n"
        (repo_root / "PROGRESS.md").write_text(body, encoding="utf-8")


def test_scan_emits_info_packet_when_tracking_is_clean(tmp_path: Path) -> None:
    _write_tracking(
        tmp_path,
        handshake_baseline=461,
        progress_baseline=461,
        handshake_refs=["4. Product_Roadmap/Tenant_Override_Operator_Runbook.md"],
        master_index_refs=["4. Product_Roadmap/Tenant_Override_Operator_Runbook.md"],
    )

    result = scan(
        repo_root=tmp_path,
        baseline_tests_expected=461,
        tenant_id="tenant_demo",
        now=_fixed_now(),
    )

    assert isinstance(result, ScanResult)
    assert result.baseline_tests_recorded == 461
    assert result.drift_findings == []
    assert len(result.packets) == 1
    only = result.packets[0]
    assert only.trigger_class == "scan_clean"
    assert only.severity == "info"
    assert only.requires_operator_approval is True


def test_scan_detects_baseline_drift(tmp_path: Path) -> None:
    _write_tracking(
        tmp_path,
        handshake_baseline=443,
        progress_baseline=443,
        handshake_refs=["4. Product_Roadmap/Tenant_Override_Operator_Runbook.md"],
        master_index_refs=["4. Product_Roadmap/Tenant_Override_Operator_Runbook.md"],
    )

    result = scan(
        repo_root=tmp_path,
        baseline_tests_expected=461,
        tenant_id="tenant_demo",
        now=_fixed_now(),
    )

    classes = [packet.trigger_class for packet in result.packets]
    assert "runtime_baseline_changed" in classes
    drift_packet = next(p for p in result.packets if p.trigger_class == "runtime_baseline_changed")
    assert drift_packet.severity == "training"
    assert drift_packet.recommended_loop == "one_hour_training"
    assert drift_packet.requires_operator_approval is True


def test_scan_flags_missing_progress_md(tmp_path: Path) -> None:
    _write_tracking(
        tmp_path,
        handshake_baseline=461,
        include_progress=False,
        handshake_refs=["4. Product_Roadmap/Tenant_Override_Operator_Runbook.md"],
        master_index_refs=["4. Product_Roadmap/Tenant_Override_Operator_Runbook.md"],
    )

    result = scan(
        repo_root=tmp_path,
        baseline_tests_expected=461,
        tenant_id="tenant_demo",
        now=_fixed_now(),
    )

    assert any("PROGRESS.md not found" in finding for finding in result.drift_findings)
    classes = [packet.trigger_class for packet in result.packets]
    assert "project_drift_detected" in classes


def test_scan_accepts_blocked_progress_task_as_current(tmp_path: Path) -> None:
    _write_tracking(
        tmp_path,
        handshake_baseline=470,
        progress_baseline=470,
        progress_status="⏸ BLOCKED (API budget gate)",
        handshake_refs=["4. Product_Roadmap/Tenant_Override_Operator_Runbook.md"],
        master_index_refs=["4. Product_Roadmap/Tenant_Override_Operator_Runbook.md"],
    )

    result = scan(
        repo_root=tmp_path,
        baseline_tests_expected=470,
        tenant_id="tenant_demo",
        now=_fixed_now(),
    )

    assert result.drift_findings == []
    assert [packet.trigger_class for packet in result.packets] == ["scan_clean"]


def test_scan_flags_handshake_reference_missing_from_index(tmp_path: Path) -> None:
    _write_tracking(
        tmp_path,
        handshake_baseline=461,
        progress_baseline=461,
        handshake_refs=[
            "4. Product_Roadmap/Tenant_Override_Operator_Runbook.md",
            "4. Product_Roadmap/Missing_From_Index.md",
        ],
        master_index_refs=[
            "4. Product_Roadmap/Tenant_Override_Operator_Runbook.md",
        ],
    )

    result = scan(
        repo_root=tmp_path,
        baseline_tests_expected=461,
        tenant_id="tenant_demo",
        now=_fixed_now(),
    )

    assert any(
        "Missing_From_Index.md" in finding for finding in result.drift_findings
    )
    drift_packets = [p for p in result.packets if p.trigger_class == "project_drift_detected"]
    assert drift_packets, "drift packet expected when handshake references unindexed runbook"
    drift_packet = drift_packets[0]
    assert drift_packet.severity == "review"
    assert drift_packet.requires_operator_approval is True


def test_scan_flags_missing_tracking_files(tmp_path: Path) -> None:
    result = scan(
        repo_root=tmp_path,
        baseline_tests_expected=461,
        tenant_id="tenant_demo",
        now=_fixed_now(),
    )

    assert "missing tracking file: PROJECT_HANDSHAKE.md" in result.drift_findings
    assert "missing tracking file: MASTER_INDEX.md" in result.drift_findings
    classes = [packet.trigger_class for packet in result.packets]
    assert "project_drift_detected" in classes


def test_packets_carry_full_forbidden_action_list(tmp_path: Path) -> None:
    _write_tracking(tmp_path, handshake_baseline=461, progress_baseline=461)
    result = scan(
        repo_root=tmp_path,
        baseline_tests_expected=461,
        tenant_id="tenant_demo",
        now=_fixed_now(),
    )
    for packet in result.packets:
        for forbidden in FORBIDDEN_AUTONOMOUS_ACTIONS:
            assert forbidden in packet.forbidden_actions
        assert packet.requires_operator_approval is True
        assert packet.evidence_record_ids == []


def test_mission_envelope_built_from_training_packets() -> None:
    packet = TriggerPacket(
        trigger_id="trigger_20260522_093000_001",
        trigger_class="runtime_baseline_changed",
        severity="training",
        tenant_id="tenant_demo",
        evidence_record_ids=[],
        changed_paths=["PROJECT_HANDSHAKE.md"],
        recommended_loop="one_hour_training",
        allowed_paths=["PROJECT_HANDSHAKE.md", "MASTER_INDEX.md"],
        forbidden_actions=list(FORBIDDEN_AUTONOMOUS_ACTIONS),
        requires_operator_approval=True,
        notes=["Baseline drift: expected=461 recorded=443"],
    )

    envelope = build_mission_envelope([packet], scanned_at=_fixed_now())

    assert envelope["mode"] == "training"
    assert envelope["trigger_source"] == "autonomous_trigger"
    assert envelope["max_duration_minutes"] == 60
    assert "PROJECT_HANDSHAKE.md" in envelope["allowed_paths"]
    assert "MASTER_INDEX.md" in envelope["allowed_paths"]
    assert "production_policy_apply" in envelope["requires_operator_approval_for"]
    assert "tenant_override_write" in envelope["requires_operator_approval_for"]
    assert "closeout_status_change" in envelope["requires_operator_approval_for"]
    assert envelope["forbidden_paths"]


def test_cli_writes_json_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write_tracking(tmp_path, handshake_baseline=461, progress_baseline=461)
    out_file = tmp_path / "scan.json"

    exit_code = run(
        [
            "--repo-root",
            str(tmp_path),
            "--baseline-tests",
            "461",
            "--out",
            str(out_file),
        ]
    )

    assert exit_code == 0
    assert out_file.exists()
    payload = json.loads(out_file.read_text(encoding="utf-8"))
    assert payload["baseline_tests_expected"] == 461
    assert payload["baseline_tests_recorded"] == 461
    assert payload["packets"], "at least one packet should always be emitted"
    captured = capsys.readouterr()
    assert payload["packets"][0]["trigger_id"] in captured.out


def test_cli_emits_mission_envelope_on_training_drift(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _write_tracking(
        tmp_path,
        handshake_baseline=443,
        progress_baseline=443,
    )
    mission_file = tmp_path / "mission.json"

    exit_code = run(
        [
            "--repo-root",
            str(tmp_path),
            "--baseline-tests",
            "461",
            "--with-mission-envelope",
            "--mission-out",
            str(mission_file),
        ]
    )

    assert exit_code == 0
    assert mission_file.exists()
    envelope = json.loads(mission_file.read_text(encoding="utf-8"))
    assert envelope["mode"] == "training"
    assert envelope["max_duration_minutes"] == 60
    captured = capsys.readouterr()
    assert "mission_envelope" in captured.out
