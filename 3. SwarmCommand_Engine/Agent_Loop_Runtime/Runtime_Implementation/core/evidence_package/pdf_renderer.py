"""Cyber Insurance Evidence Package PDF render surface (spec §9, HC6 / HC8).

IQ2 of the §11-signed implementation spec resolved the render toolchain to a
dedicated pinned PDF dependency. The concrete engine pinned here is ReportLab:
pure-Python, no system binaries, chosen to minimize the new cross-platform
supply-chain surface the spec flagged as the IQ2 watch-item.

Scope boundary for this build: an explicit, internal/synthetic-only render
step. It is NOT auto-wired into ``generate_package_from_test_plan`` (generation
stays deterministic and offline), and it produces no buyer-facing delivery. The
standing Pass-1 authorization excludes buyer PDF delivery; nothing here changes
that.

Determinism (HC6): rendering uses ReportLab's ``invariant`` mode so two runs
against the same package produce byte-identical PDFs. The engine identity and
version are pinned and recorded in a ``rendered/pdf_render.json`` sidecar; a
render requested against a different engine identity fails closed.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from .gates import BOUNDARY_STATEMENT

RENDER_ENGINE_IDENTITY = "reportlab"
INTERNAL_FOOTER = "Internal synthetic package - not for buyer delivery."

_RECORD_STAGES: tuple[str, ...] = (
    "detection",
    "verification",
    "evidence",
    "audit_trail",
    "outcome_documentation",
)


def render_engine_version() -> str:
    """Return the pinned PDF engine version (recorded in the sidecar, HC6)."""

    import reportlab

    return reportlab.Version


@dataclass(frozen=True)
class PdfRenderResult:
    pdf_path: Path
    sidecar_path: Path
    engine_identity: str
    engine_version: str
    pdf_sha256: str
    boundary_statement_present: bool
    page_count: int


def render_package_pdf(
    package_dir: Path,
    *,
    expected_engine_identity: str = RENDER_ENGINE_IDENTITY,
    boundary_statement: str = BOUNDARY_STATEMENT,
) -> PdfRenderResult:
    """Render a deterministic internal PDF for one generated package.

    Reads ``manifest.json`` and the structured records, draws the buyer-facing
    surfaces (boundary statement verbatim and prominent, package metadata,
    evidence-records table, determinism pins), and writes ``rendered/package.pdf``
    plus a ``rendered/pdf_render.json`` sidecar (HC6 toolchain identity).
    """

    if expected_engine_identity != RENDER_ENGINE_IDENTITY:
        # HC6 fail-closed: the pinned engine identity must match.
        raise ValueError(
            "PDF render engine identity mismatch: "
            f"expected {RENDER_ENGINE_IDENTITY!r}, requested {expected_engine_identity!r}"
        )
    if not boundary_statement.strip():
        # §2 / HC8: the boundary statement is mandatory and unedited.
        raise ValueError("boundary_statement must not be empty")

    package_dir = Path(package_dir).resolve()
    manifest_path = package_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"package manifest missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = _load_records(package_dir)

    pdf_bytes, page_count = _build_pdf_bytes(manifest, records, boundary_statement)

    rendered_dir = package_dir / "rendered"
    rendered_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = rendered_dir / "package.pdf"
    _atomic_write_bytes(pdf_path, pdf_bytes)

    pdf_sha = sha256(pdf_bytes).hexdigest()
    engine_version = render_engine_version()
    sidecar = {
        "package_id": manifest.get("package_id"),
        "engine_identity": RENDER_ENGINE_IDENTITY,
        "engine_version": engine_version,
        "engine_pinned": True,
        "deterministic_mode": "reportlab-invariant",
        "pdf_sha256": f"sha256:{pdf_sha}",
        "page_count": page_count,
        "boundary_statement": boundary_statement,
        "buyer_delivery": False,
    }
    sidecar_path = rendered_dir / "pdf_render.json"
    _atomic_write_text(sidecar_path, json.dumps(sidecar, indent=2, sort_keys=True) + "\n")

    return PdfRenderResult(
        pdf_path=pdf_path,
        sidecar_path=sidecar_path,
        engine_identity=RENDER_ENGINE_IDENTITY,
        engine_version=engine_version,
        pdf_sha256=f"sha256:{pdf_sha}",
        boundary_statement_present=True,
        page_count=page_count,
    )


def _build_pdf_bytes(
    manifest: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
    boundary_statement: str,
) -> tuple[bytes, int]:
    import io

    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas

    page_width, page_height = LETTER
    left = 54.0
    right = page_width - 54.0
    top = page_height - 54.0
    bottom = 54.0
    body_width = right - left

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=LETTER, invariant=1)
    pdf.setTitle("Cyber Insurance Evidence Package")
    pdf.setSubject("Internal synthetic evidence package")

    state = {"y": top}

    def footer() -> None:
        pdf.setFont("Helvetica-Oblique", 8)
        pdf.drawString(left, bottom - 18, INTERNAL_FOOTER)
        pdf.drawRightString(right, bottom - 18, f"Page {pdf.getPageNumber()}")

    def new_page() -> None:
        footer()
        pdf.showPage()
        state["y"] = top

    def ensure_space(needed: float) -> None:
        if state["y"] - needed < bottom:
            new_page()

    def write_line(text: str, font: str, size: float, gap: float, indent: float = 0.0) -> None:
        for chunk in _wrap(text, font, size, body_width - indent, stringWidth):
            ensure_space(size + gap)
            pdf.setFont(font, size)
            pdf.drawString(left + indent, state["y"], chunk)
            state["y"] -= size + gap

    def spacer(height: float) -> None:
        ensure_space(height)
        state["y"] -= height

    write_line("Cyber Insurance Evidence Package", "Helvetica-Bold", 18, 8)
    spacer(4)
    write_line(f"Package ID: {manifest.get('package_id', 'n/a')}", "Helvetica", 10, 3)
    write_line(f"Tenant: {manifest.get('tenant_id', 'n/a')}", "Helvetica", 10, 3)
    write_line(f"Generated at: {manifest.get('generated_at', 'n/a')}", "Helvetica", 10, 3)
    write_line(f"Trigger: {manifest.get('trigger', 'n/a')}", "Helvetica", 10, 3)
    spacer(10)

    write_line("Scope Boundary", "Helvetica-Bold", 12, 6)
    for chunk in _wrap(boundary_statement, "Helvetica", 10, body_width - 12, stringWidth):
        ensure_space(10 + 4)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(left + 12, state["y"], chunk)
        state["y"] -= 10 + 4
    spacer(10)

    write_line("Evidence Records", "Helvetica-Bold", 12, 6)
    if records:
        write_line("Record | Category | Source | Result", "Helvetica-Bold", 9, 4)
        for record in records:
            row = (
                f"{record.get('record_id', '?')} | "
                f"{record.get('evidence_category', '?')} | "
                f"{record.get('source_artifact_path', '?')} | "
                f"{record.get('result', '?')}"
            )
            write_line(row, "Helvetica", 9, 4)
    else:
        write_line("No structured records found in package.", "Helvetica", 9, 4)
    spacer(10)

    write_line("Determinism Pins", "Helvetica-Bold", 12, 6)
    write_line(
        f"Model: {manifest.get('model_identity', 'n/a')} "
        f"(temperature {manifest.get('model_temperature', 'n/a')})",
        "Helvetica",
        10,
        3,
    )
    write_line(
        f"Render toolchain: {manifest.get('render_toolchain', 'n/a')} | "
        f"PDF engine: {RENDER_ENGINE_IDENTITY} {render_engine_version()}",
        "Helvetica",
        10,
        3,
    )
    write_line(f"Package hash: {manifest.get('package_hash', 'n/a')}", "Helvetica", 9, 3)

    footer()
    page_count = pdf.getPageNumber()
    pdf.save()
    return buffer.getvalue(), page_count


def _wrap(text: str, font: str, size: float, max_width: float, width_of) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if width_of(candidate, font, size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _load_records(package_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    records_dir = package_dir / "records"
    for stage in _RECORD_STAGES:
        path = records_dir / f"{stage}.json"
        if path.exists():
            records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    with os.fdopen(temp_fd, "wb") as handle:
        handle.write(payload)
    Path(temp_name).replace(path)


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    with os.fdopen(temp_fd, "w", encoding="utf-8") as handle:
        handle.write(content)
    Path(temp_name).replace(path)
