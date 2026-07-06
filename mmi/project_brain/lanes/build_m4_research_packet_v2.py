#!/usr/bin/env python3
"""Build M4 research packet v2 ZIP for ChatGPT upload."""

from __future__ import annotations

import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(r"C:\MMI")
OUT = Path(r"C:\Users\mattn\AppData\Local\Temp\m4_research_packet_v2")
ZIP = Path(r"C:\Users\mattn\AppData\Local\Temp\m4_research_packet_v2_2026-07-03.zip")
ZIP_REPO = REPO / "mmi/project_brain/lanes/m4_research_packet_v2_2026-07-03.zip"

EXCLUDE_DIRS = {
    ".git",
    "venv",
    ".venv",
    ".venv_kinetic",
    "node_modules",
    ".pytest_cache",
    "__pycache__",
    ".tmp.driveupload",
}

PATTERN = re.compile(
    r"M4|PERFECT|host boundary|host-boundary|canary|48h|genomic|"
    r"evolution gate|Gate C|AFE|evolution_gate|destructive evolution",
    re.I,
)

MANDATORY = [
    "tasks.json",
    "AGENTS.md",
    "mmi/project_brain/status",
    "mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_2026-07.md",
    "mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_RELAY_PORTABLE_2026-07-03.md",
    "mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md",
    "mmi/project_brain/lanes/CHATGPT_MMI_LANE_INTEGRATION_2026-07-03.md",
    "mmi/project_brain/architecture/MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md",
    "mmi/project_brain/chaos/MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md",
    "mmi/project_brain/architecture/MMI_AGI_EVOLUTION_PATHWAY.md",
    "mmi/project_brain/lanes/RESEARCH_host_boundary_wsl_windows_2026-06.md",
]

CODE = [
    "scripts/genomic_realignment_loop_harness.py",
    "scripts/control_envelope_harness.py",
    "scripts/email_lanes_harness.py",
    "scripts/console_server_harness.py",
    "scripts/proof_gate_harness.py",
    "scripts/phase1_stability_harness.py",
    "scripts/chaos_lab_provisioner.py",
    "ops/genomic_realignment_loop.py",
    "tests/test_genomic_realignment_loop.py",
    "tests/test_genomic_constraint_validator.py",
    "tests/test_metadata_ingress_gate.py",
    "tests/test_control_envelope.py",
    "tests/test_console_server.py",
    "mmi/project_brain/chaos/mmi_control_envelope.py",
    "mmi/project_brain/chaos/console_evidence_gate.py",
    "mmi/project_brain/chaos/canary_metadata_layer.py",
    "mmi/project_brain/chaos/metadata_ingress_gate.py",
    "mmi/project_brain/chaos/mirror_dimension_router.py",
    "mmi/project_brain/chaos/weapon_battlefield_scoring.py",
    "mmi/project_brain/chaos/purple_evasion_suite.py",
    "mmi/project_brain/chaos/genomic_constraint_validator.py",
    "mmi/project_brain/chaos/genomic_constraint_synth.py",
]

GREP_ROOTS = ["mmi", "scripts", "tests", "ops"]


def excluded(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def copy_into_staging(rel: str, collected: set[str]) -> None:
    src = REPO / rel.replace("/", "\\")
    if not src.exists() or excluded(src):
        return
    if src.is_dir():
        for item in src.rglob("*"):
            if item.is_file() and not excluded(item.relative_to(REPO)):
                r = item.relative_to(REPO).as_posix()
                if r in collected:
                    continue
                dest = OUT / r
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
                collected.add(r)
    else:
        r = src.relative_to(REPO).as_posix()
        if r in collected:
            return
        dest = OUT / r
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        collected.add(r)


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    collected: set[str] = set()
    for rel in MANDATORY + CODE:
        copy_into_staging(rel, collected)

    for root_name in GREP_ROOTS:
        root = REPO / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".md", ".json", ".py"}:
                continue
            rel = path.relative_to(REPO)
            if excluded(rel):
                continue
            r = rel.as_posix()
            if r in collected:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if PATTERN.search(text):
                copy_into_staging(r, collected)

    manifest = OUT / "M4_RESEARCH_PACKET_V2_MANIFEST.md"
    manifest.write_text(
        "\n".join(
            [
                "# M4 Research Packet v2 Manifest",
                "",
                f"**Built:** {datetime.now(timezone.utc).isoformat()}",
                "**Authority repo:** C:\\MMI",
                "**Task:** mmi-m4-evolution-gate-research-v2",
                "**Authorization:** RESEARCH PACKET V2 ONLY",
                "",
                "## Upload to ChatGPT",
                "",
                "Attach the `.zip` file directly. Do NOT paste terminal zip output.",
                "",
                "## Read first",
                "",
                "1. mmi/project_brain/lanes/RESEARCH_M4_EVOLUTION_GATE_2026-07.md",
                "2. mmi/project_brain/chaos/MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md (M4)",
                "3. mmi/project_brain/architecture/MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md (section 6)",
                "4. mmi/project_brain/status/MMI_PIPE_STAGING.json",
                "5. tasks.json",
                "",
                "## Deliverable",
                "",
                "Revise RESEARCH_M4_EVOLUTION_GATE_FINDINGS_2026-07.md — remove [UNVERIFIED] where read.",
                "No PERFECT claim. No build auth. No spec auth.",
                "",
                f"**File count:** {len(collected) + 1}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(OUT.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(OUT.parent).as_posix())

    ZIP_REPO.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ZIP, ZIP_REPO)

    print(f"ZIP={ZIP}")
    print(f"ZIP_REPO={ZIP_REPO}")
    print(f"FILES={len(collected) + 1}")
    print(f"BYTES={ZIP.stat().st_size}")


if __name__ == "__main__":
    main()
