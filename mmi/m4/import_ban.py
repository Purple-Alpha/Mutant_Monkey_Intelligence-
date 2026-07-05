"""H-L8-001 structural import ban for the M4 package."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

CANARY_METADATA_LAYER_IMPORT = re.compile(
    r"^\s*(?:import\s+.*canary_metadata_layer|from\s+.*canary_metadata_layer)",
    re.MULTILINE,
)
DYNAMIC_IMPORT_MECHANISM = re.compile(
    r"(?:importlib(?:\.\w+)*\.import_module|__import__|\bimport_module\b)"
)
MMI_L8_SYMBOL = re.compile(r"\bmmi\.l8(?:\.|\b)")
CANARY_MODULE_MARKER = "canary_metadata_layer"
CHECKER_EXEMPT = frozenset({"import_ban.py"})


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


def _line_at(text: str, line_no: int) -> str:
    lines = text.splitlines()
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1].strip()
    return ""


def _ast_canary_violations(path: Path, rel: str, text: str) -> list[ImportBanViolation]:
    if path.name in CHECKER_EXEMPT:
        return []
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return []

    hits: list[ImportBanViolation] = []
    seen: set[tuple[int, str]] = set()

    def add(line_no: int, rule: str, detail: str) -> None:
        key = (line_no, rule)
        if key in seen:
            return
        seen.add(key)
        hits.append(
            ImportBanViolation(
                path=rel,
                line_no=line_no,
                rule=rule,
                line=_line_at(text, line_no) or detail,
            )
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if CANARY_MODULE_MARKER in node.value:
                add(
                    node.lineno,
                    "H-L8-001-canary_metadata_layer",
                    "string literal references canary_metadata_layer",
                )

    return hits


def _line_canary_violations(rel: str, text: str) -> list[ImportBanViolation]:
    if rel.split("/")[-1] in CHECKER_EXEMPT:
        return []
    hits: list[ImportBanViolation] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if CANARY_METADATA_LAYER_IMPORT.search(line):
            hits.append(
                ImportBanViolation(
                    path=rel,
                    line_no=idx,
                    rule="H-L8-001-canary_metadata_layer",
                    line=line.strip(),
                )
            )
        elif CANARY_MODULE_MARKER in line and DYNAMIC_IMPORT_MECHANISM.search(line):
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


def _scan_file(path: Path, package_root: Path) -> list[ImportBanViolation]:
    rel = path.relative_to(package_root).as_posix()
    text = path.read_text(encoding="utf-8")
    hits = _line_canary_violations(rel, text)
    hits.extend(_ast_canary_violations(path, rel, text))
    # De-dupe same line+rule
    seen: set[tuple[str, int, str]] = set()
    unique: list[ImportBanViolation] = []
    for hit in hits:
        key = (hit.rule, hit.line_no, hit.line)
        if key in seen:
            continue
        seen.add(key)
        unique.append(hit)
    return unique


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
