from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

RUNTIME_ROOT = Path(__file__).resolve().parents[1]
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.evidence_package import (
    audit_package,
    build_audit_payload,
    parse_audit_output,
)
from core.evidence_package.package_auditor import PackageAuditError

FIXED_NOW = datetime(2026, 6, 4, 18, 30, 0, tzinfo=timezone.utc)


def _write_packet(tmp_path: Path) -> Path:
    """Create a minimal persisted audit packet (manifest + one chunk)."""
    audit_dir = tmp_path / "pkg__audit_packet"
    contents = audit_dir / "contents"
    contents.mkdir(parents=True)
    (contents / "chunk_0001.txt").write_text("rendered claim: boundary statement\n", encoding="utf-8")
    manifest = {
        "package_id": "pkg-1",
        "packet_hash": "sha256:abc123",
        "coverage_complete": True,
        "content_chunks": ["contents/chunk_0001.txt"],
        "files": [{"path": "rendered/package.md", "role": "written"}],
    }
    (audit_dir / "audit_packet.json").write_text(json.dumps(manifest), encoding="utf-8")
    return audit_dir


def _contract(tmp_path: Path) -> Path:
    contract = tmp_path / "contract.md"
    contract.write_text("VISION non-negotiables\n", encoding="utf-8")
    return contract


def test_build_payload_includes_manifest_chunks_and_contracts(tmp_path):
    audit_dir = _write_packet(tmp_path)
    payload = build_audit_payload(audit_packet_dir=audit_dir, contract_files=[_contract(tmp_path)])

    assert "AUDIT PACKET MANIFEST" in payload
    assert "sha256:abc123" in payload
    assert "rendered claim: boundary statement" in payload
    assert "VISION non-negotiables" in payload


def test_build_payload_raises_when_packet_missing(tmp_path):
    with pytest.raises(PackageAuditError):
        build_audit_payload(audit_packet_dir=tmp_path / "nope", contract_files=[])


def test_parse_clean_output():
    blocking, warning, deviations = parse_audit_output("looks fine\nGATE_SUMMARY: blocking=0 warnings=0\n")
    assert blocking == 0 and warning == 0
    assert deviations == ()


def test_parse_output_with_deviations():
    content = (
        "BLOCKING: boundary statement was edited\n"
        "WARNING: vendor name not redacted\n"
        "GATE_SUMMARY: blocking=1 warnings=1\n"
    )
    blocking, warning, deviations = parse_audit_output(content)
    assert blocking == 1 and warning == 1
    severities = {d.severity for d in deviations}
    assert severities == {"blocking", "warning"}


def test_parse_output_missing_summary_raises():
    with pytest.raises(PackageAuditError):
        parse_audit_output("no verdict line here")


def test_parse_output_multiple_summaries_raises():
    with pytest.raises(PackageAuditError):
        parse_audit_output("GATE_SUMMARY: blocking=0 warnings=0\nGATE_SUMMARY: blocking=1 warnings=0\n")


def test_audit_clean_package_writes_no_drift(tmp_path):
    audit_dir = _write_packet(tmp_path)
    package_dir = tmp_path / "pkg"
    package_dir.mkdir()
    captured = {}

    def fake_client(payload: str) -> str:
        captured["payload"] = payload
        return "GATE_SUMMARY: blocking=0 warnings=0\n"

    result = audit_package(
        package_id="pkg-1",
        tenant_id="t-1",
        package_dir=package_dir,
        audit_packet_dir=audit_dir,
        contract_files=[_contract(tmp_path)],
        grok_client=fake_client,
        audit_outputs_dir=tmp_path / "audit_outputs",
        now=FIXED_NOW,
    )

    assert result.clean is True
    assert result.blocking_count == 0 and result.warning_count == 0
    assert result.drift_incident_paths == ()
    assert Path(result.grok_output_path).exists()
    assert result.packet_hash == "sha256:abc123"
    # The packet content actually reached the client.
    assert "rendered claim" in captured["payload"]


def test_audit_with_deviations_writes_drift_incidents(tmp_path):
    audit_dir = _write_packet(tmp_path)
    package_dir = tmp_path / "pkg"
    package_dir.mkdir()

    def fake_client(payload: str) -> str:
        return (
            "BLOCKING: boundary statement edited\n"
            "WARNING: stale evidence\n"
            "GATE_SUMMARY: blocking=1 warnings=1\n"
        )

    result = audit_package(
        package_id="pkg-1",
        tenant_id="t-1",
        package_dir=package_dir,
        audit_packet_dir=audit_dir,
        contract_files=[_contract(tmp_path)],
        grok_client=fake_client,
        audit_outputs_dir=tmp_path / "audit_outputs",
        now=FIXED_NOW,
    )

    assert result.clean is False
    assert len(result.drift_incident_paths) == 2
    incident = json.loads(Path(result.drift_incident_paths[0]).read_text(encoding="utf-8"))
    assert incident["source"] == "grok_package_audit"
    assert incident["status"] == "open"
    assert incident["severity"] in {"blocking", "warning"}
    assert incident["operator_resolution_note"] is None


def test_audit_empty_grok_output_raises(tmp_path):
    audit_dir = _write_packet(tmp_path)
    package_dir = tmp_path / "pkg"
    package_dir.mkdir()

    with pytest.raises(PackageAuditError):
        audit_package(
            package_id="pkg-1",
            tenant_id="t-1",
            package_dir=package_dir,
            audit_packet_dir=audit_dir,
            contract_files=[],
            grok_client=lambda _payload: "   ",
            audit_outputs_dir=tmp_path / "audit_outputs",
            now=FIXED_NOW,
        )
