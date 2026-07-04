"""H-L8-001 structural import ban for the M4 package."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

CANARY_METADATA_LAYER_IMPORT = re.compile(
    r"^\s*(?:import\s+.*canary_metadata_layer|from\s+.*canary_metadata_layer)",
    re.MULTILINE,
)
# Fail-closed: block dynamic import paths to L8 on the same line (H-L8-001 Phase 0).
DYNAMIC_IMPORT_MECHANISM = re.compile(
    r"(?:importlib(?:\.\w+)*\.import_module|__import__|\bimport_module\b)"
)
MMI_L8_SYMBOL = re.compile(r"\bmmi\.l8(?:\.|\b)")


@dataclass
class ImportBanViolation:
    path: str
    line_no: int
    rule: str
    line: str


@dataclass
class ImportBanScanResult:
    package_root: str
    files_scanned: int
    violations: list[ImportBanViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.violations


def _canary_metadata_layer_coupling(line: str) -> bool:
    if "canary_metadata_layer" not in line:
        return False
    if CANARY_METADATA_LAYER_IMPORT.search(line):
        return True
    return bool(DYNAMIC_IMPORT_MECHANISM.search(line))


def _scan_file(path: Path, package_root: Path) -> list[ImportBanViolation]:
    rel = path.relative_to(package_root).as_posix()
    text = path.read_text(encoding="utf-8")
    hits: list[ImportBanViolation] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if _canary_metadata_layer_coupling(line):
            hits.append(
                ImportBanViolation(
                    path=rel,
                    line_no=idx,
                    rule="H-L8-001-canary_metadata_layer",
                    line=line.strip(),
                )
            )
        if MMI_L8_SYMBOL.search(line):
            hits.append(
                ImportBanViolation(
                    path=rel,
                    line_no=idx,
                    rule="H-L8-001-mmi_l8_symbol",
                    line=line.strip(),
                )
            )
    return hits


def scan_m4_package(authority_root: Path) -> ImportBanScanResult:
    """Scan `mmi/m4/` for forbidden L8 coupling."""
    package_root = authority_root / "mmi" / "m4"
    if not package_root.is_dir():
        return ImportBanScanResult(
            package_root=package_root.as_posix(),
            files_scanned=0,
            violations=[
                ImportBanViolation(
                    path="mmi/m4",
                    line_no=0,
                    rule="H-L8-001-package_missing",
                    line="package root not found",
                )
            ],
        )

    violations: list[ImportBanViolation] = []
    files_scanned = 0
    for path in sorted(package_root.rglob("*.py")):
        files_scanned += 1
        violations.extend(_scan_file(path, package_root))

    return ImportBanScanResult(
        package_root=package_root.as_posix(),
        files_scanned=files_scanned,
        violations=violations,
    )
