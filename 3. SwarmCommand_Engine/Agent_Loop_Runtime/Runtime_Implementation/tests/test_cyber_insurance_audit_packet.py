from __future__ import annotations

import json
import sys
from pathlib import Path

RUNTIME_ROOT = Path(__file__).resolve().parents[1]
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from core.evidence_package import assemble_audit_packet, write_audit_packet


def _touched(tmp_path: Path) -> tuple[list[Path], list[Path], list[Path]]:
    reads = []
    for name in ("source_a.json", "source_b.json"):
        path = tmp_path / "src" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"name": name}), encoding="utf-8")
        reads.append(path)
    writes = []
    for name in ("record.json", "package.md"):
        path = tmp_path / "pkg" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"written {name}\n", encoding="utf-8")
        writes.append(path)
    contract = tmp_path / "VISION.md"
    contract.write_text("non-negotiables\n", encoding="utf-8")
    return reads, writes, [contract]


def test_packet_covers_every_touched_file(tmp_path):
    reads, writes, contracts = _touched(tmp_path)
    packet = assemble_audit_packet(
        package_id="pkg-1",
        read_files=reads,
        written_files=writes,
        contract_files=contracts,
        workspace_root=tmp_path,
    )

    assert packet.coverage_complete is True
    assert packet.missing_paths == ()
    assert packet.grok_submitted is False
    assert packet.file_count == 5
    roles = {item.path: item.role for item in packet.files}
    assert roles["src/source_a.json"] == "read"
    assert roles["pkg/record.json"] == "written"
    assert roles["VISION.md"] == "contract"
    assert all(item.sha256.startswith("sha256:") for item in packet.files)


def test_missing_touched_file_breaks_coverage(tmp_path):
    reads, writes, contracts = _touched(tmp_path)
    reads.append(tmp_path / "src" / "does_not_exist.json")

    packet = assemble_audit_packet(
        package_id="pkg-1",
        read_files=reads,
        written_files=writes,
        contract_files=contracts,
        workspace_root=tmp_path,
    )

    assert packet.coverage_complete is False
    assert "src/does_not_exist.json" in packet.missing_paths


def test_missing_contract_does_not_break_touched_coverage(tmp_path):
    reads, writes, _contracts = _touched(tmp_path)
    packet = assemble_audit_packet(
        package_id="pkg-1",
        read_files=reads,
        written_files=writes,
        contract_files=[tmp_path / "absent_spec.md"],
        workspace_root=tmp_path,
    )

    assert packet.coverage_complete is True
    assert packet.missing_contracts == ("absent_spec.md",)


def test_assembly_is_deterministic(tmp_path):
    reads, writes, contracts = _touched(tmp_path)
    first = assemble_audit_packet(
        package_id="pkg-1",
        read_files=reads,
        written_files=writes,
        contract_files=contracts,
        workspace_root=tmp_path,
    )
    second = assemble_audit_packet(
        package_id="pkg-1",
        read_files=list(reversed(reads)),
        written_files=list(reversed(writes)),
        contract_files=contracts,
        workspace_root=tmp_path,
    )

    assert first.packet_hash == second.packet_hash


def test_write_packet_emits_manifest_and_chunks(tmp_path):
    reads, writes, contracts = _touched(tmp_path)
    packet = assemble_audit_packet(
        package_id="pkg-1",
        read_files=reads,
        written_files=writes,
        contract_files=contracts,
        workspace_root=tmp_path,
    )
    audit_dir = tmp_path / "out" / "pkg-1__audit_packet"
    summary = write_audit_packet(packet, audit_dir=audit_dir, workspace_root=tmp_path)

    manifest = json.loads(summary["manifest_path"].read_text(encoding="utf-8"))
    assert manifest["coverage_complete"] is True
    assert manifest["grok_submitted"] is False
    assert manifest["file_count"] == 5
    assert len(manifest["content_chunks"]) >= 1
    for relative in manifest["content_chunks"]:
        assert (audit_dir / relative).exists()


def test_oversized_file_gets_its_own_chunk_without_trimming(tmp_path):
    reads, writes, contracts = _touched(tmp_path)
    big = tmp_path / "pkg" / "big.txt"
    big.write_text("x" * 5000, encoding="utf-8")
    writes.append(big)

    packet = assemble_audit_packet(
        package_id="pkg-1",
        read_files=reads,
        written_files=writes,
        contract_files=contracts,
        workspace_root=tmp_path,
    )
    audit_dir = tmp_path / "out" / "pkg-1__audit_packet"
    summary = write_audit_packet(
        packet, audit_dir=audit_dir, workspace_root=tmp_path, max_chunk_bytes=1000
    )

    combined = "".join(
        path.read_text(encoding="utf-8") for path in summary["content_chunk_paths"]
    )
    assert "x" * 5000 in combined
