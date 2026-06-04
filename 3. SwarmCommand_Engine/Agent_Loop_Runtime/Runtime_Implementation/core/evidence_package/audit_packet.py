"""Audit-packet assembly for the Cyber Insurance Evidence Package generator.

Implements the section 8 ``auditpacket`` assembly stage and the section 10
audit-packet coverage rule of the signed implementation spec: collect every
file touched (read or written) during generation stages 1-7 into a
coverage-complete packet, hash each file, and bind the contract documents the
package is audited against.

Pass 1 assembles and persists the packet; it does NOT call Grok. There is no
live package audit, no Grok submission, and no done declaration in Pass 1
(`grok_submitted` is always ``False`` here).

The section 10 coverage rule is non-negotiable: AI-side scoping of the packet
is forbidden, and trimming reads to fit a size budget is forbidden. When the
assembled body is large it is chunked while preserving full coverage; an
oversized single file gets its own chunk rather than being dropped.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

# Chunk cap for the assembled packet body. Coverage always wins over size: a
# file larger than this cap is emitted in its own chunk, never truncated.
DEFAULT_MAX_CHUNK_BYTES = 180_000

PacketRole = Literal["read", "written", "contract"]


@dataclass(frozen=True)
class AuditPacketFile:
    """One file in the assembled packet, with its role and content hash."""

    path: str  # repo-relative POSIX path
    role: PacketRole
    sha256: str
    size_bytes: int


@dataclass(frozen=True)
class AssembledAuditPacket:
    """Coverage-complete set of touched + contract files for one package.

    ``coverage_complete`` reflects only the touched (read/written) files: a
    missing touched file is a section 10 ``missing_file_in_audit_packet`` miss.
    A missing contract path is tracked separately and does not, by itself,
    represent a coverage failure of the generated package.
    """

    package_id: str
    files: tuple[AuditPacketFile, ...]
    coverage_complete: bool
    missing_paths: tuple[str, ...]
    missing_contracts: tuple[str, ...]
    packet_hash: str
    grok_submitted: bool = False

    @property
    def file_count(self) -> int:
        return len(self.files)


def assemble_audit_packet(
    *,
    package_id: str,
    read_files: Sequence[Path],
    written_files: Sequence[Path],
    contract_files: Sequence[Path],
    workspace_root: Path,
) -> AssembledAuditPacket:
    """Assemble a coverage-complete audit packet from touched + contract files.

    ``read_files`` and ``written_files`` are the section 3 stage 1-7 touched
    files. ``contract_files`` are the documents the package is audited against.
    Any touched file absent from disk is a coverage miss and forces
    ``coverage_complete=False``.
    """

    entries: list[AuditPacketFile] = []
    missing: list[str] = []
    missing_contracts: list[str] = []
    seen: set[str] = set()

    def _add(path: Path, role: PacketRole, counts_for_coverage: bool) -> None:
        rel = _repo_relative(path, workspace_root)
        key = f"{role}:{rel}"
        if key in seen:
            return
        seen.add(key)
        if not path.exists() or not path.is_file():
            (missing if counts_for_coverage else missing_contracts).append(rel)
            return
        entries.append(
            AuditPacketFile(
                path=rel,
                role=role,
                sha256=f"sha256:{_file_sha256(path)}",
                size_bytes=path.stat().st_size,
            )
        )

    for path in read_files:
        _add(path, "read", True)
    for path in written_files:
        _add(path, "written", True)
    for path in contract_files:
        _add(path, "contract", False)

    ordered = tuple(sorted(entries, key=lambda item: (item.role, item.path)))
    coverage_complete = not missing
    digest = _packet_hash(package_id, ordered, tuple(sorted(missing)))
    return AssembledAuditPacket(
        package_id=package_id,
        files=ordered,
        coverage_complete=coverage_complete,
        missing_paths=tuple(sorted(missing)),
        missing_contracts=tuple(sorted(missing_contracts)),
        packet_hash=f"sha256:{digest}",
        grok_submitted=False,
    )


def write_audit_packet(
    packet: AssembledAuditPacket,
    *,
    audit_dir: Path,
    workspace_root: Path,
    max_chunk_bytes: int = DEFAULT_MAX_CHUNK_BYTES,
) -> dict[str, Any]:
    """Persist the packet: ``audit_packet.json`` manifest + chunked body.

    Returns a summary dict suitable for embedding in the package manifest.
    """

    if audit_dir.exists():
        shutil.rmtree(audit_dir)
    contents_dir = audit_dir / "contents"
    contents_dir.mkdir(parents=True, exist_ok=True)

    chunk_paths = _write_content_chunks(
        packet,
        contents_dir=contents_dir,
        workspace_root=workspace_root,
        max_chunk_bytes=max_chunk_bytes,
    )

    manifest = {
        "package_id": packet.package_id,
        "packet_hash": packet.packet_hash,
        "coverage_complete": packet.coverage_complete,
        "coverage_rule": (
            "section-10: every file touched (read or written) during stages 1-7 "
            "is in the packet; AI-side scoping forbidden; reads are never trimmed"
        ),
        "grok_submitted": packet.grok_submitted,
        "file_count": packet.file_count,
        "missing_paths": list(packet.missing_paths),
        "missing_contracts": list(packet.missing_contracts),
        "files": [
            {
                "path": item.path,
                "role": item.role,
                "sha256": item.sha256,
                "size_bytes": item.size_bytes,
            }
            for item in packet.files
        ],
        "content_chunks": [path.relative_to(audit_dir).as_posix() for path in chunk_paths],
    }
    manifest_path = audit_dir / "audit_packet.json"
    _atomic_write_json(manifest_path, manifest)
    return {
        "audit_dir": audit_dir,
        "manifest_path": manifest_path,
        "content_chunk_paths": tuple(chunk_paths),
        "packet_hash": packet.packet_hash,
        "coverage_complete": packet.coverage_complete,
        "file_count": packet.file_count,
    }


def _write_content_chunks(
    packet: AssembledAuditPacket,
    *,
    contents_dir: Path,
    workspace_root: Path,
    max_chunk_bytes: int,
) -> list[Path]:
    blocks: list[bytes] = []
    for item in packet.files:
        abs_path = workspace_root / item.path
        try:
            body = abs_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            body = ""
        header = f"===== BEGIN {item.role} {item.path} {item.sha256} {item.size_bytes}B =====\n"
        footer = f"\n===== END {item.path} =====\n"
        blocks.append((header + body + footer).encode("utf-8"))

    chunks: list[bytes] = []
    current = b""
    for block in blocks:
        if len(block) > max_chunk_bytes:
            if current:
                chunks.append(current)
                current = b""
            chunks.append(block)
            continue
        if current and len(current) + len(block) > max_chunk_bytes:
            chunks.append(current)
            current = b""
        current += block
    if current:
        chunks.append(current)

    chunk_paths: list[Path] = []
    for index, chunk in enumerate(chunks, start=1):
        path = contents_dir / f"part_{index:03d}.txt"
        _atomic_write_bytes(path, chunk)
        chunk_paths.append(path)
    return chunk_paths


def _packet_hash(
    package_id: str,
    files: Sequence[AuditPacketFile],
    missing: Sequence[str],
) -> str:
    payload = {
        "package_id": package_id,
        "files": [[item.role, item.path, item.sha256, item.size_bytes] for item in files],
        "missing": list(missing),
    }
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _atomic_write_bytes(path, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    with os.fdopen(temp_fd, "wb") as handle:
        handle.write(content)
    Path(temp_name).replace(path)


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_relative(path: Path, workspace_root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(workspace_root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()
