#!/usr/bin/env python3
"""Step 00 — deterministic Agent Design Contract §3 block validator.

Parses ``4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`` §3
for the canonical field list, then verifies a contract file contains every
required label with a non-empty value inside the Agent Design Contract block.

Exit 0 when complete; exit 1 when fields are missing (hard halt before
``complete_gate.py`` spends auditor tokens on structural incompleteness).

Stdout only for machine-readable JSON (--json) or human summary (default).
No file writes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EXIT_OK = 0
EXIT_INCOMPLETE = 1
EXIT_ERROR = 2

TEMPLATE_REL = "4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md"
EXCEPTION_MARKER = "INFRASTRUCTURE_TEMPLATE_EXCEPTION_SIGNED"

FIELD_ALIASES: dict[str, str] = {
    "component name": "agent name",
}

BLOCK_HEADINGS = (
    "## agent design contract block",
    "## agent design contract",
)

INNER_BLOCK_HEADINGS = frozenset(
    {
        "## agent design contract",
    }
)

TABLE_ROW = re.compile(r"^\|\s*(?P<label>[^|]+?)\s*\|\s*(?P<value>[^|]*?)\s*\|")
LABELED_LINE = re.compile(r"^(?P<label>[A-Za-z0-9][^:\n]{0,120}?):\s*(?P<value>.+)?\s*$")


@dataclass(frozen=True)
class ValidationResult:
    path: str
    required_count: int
    found_count: int
    missing_fields: tuple[str, ...]
    exception_validated: bool
    passed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_fields_found": self.found_count,
            "contract_fields_required": self.required_count,
            "exception_validated": self.exception_validated,
            "missing_fields": list(self.missing_fields),
            "passed": self.passed,
            "path": self.path,
        }


def _repo_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in (here, *here.parents):
        if (parent / TEMPLATE_REL).is_file():
            return parent
    raise FileNotFoundError(f"could not locate repo root containing {TEMPLATE_REL}")


def _normalize_label(label: str) -> str:
    text = label.strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = text.rstrip(":")
    return FIELD_ALIASES.get(text, text)


def load_required_fields(template_path: Path) -> tuple[str, ...]:
    text = template_path.read_text(encoding="utf-8")
    match = re.search(r"```text\s*\n## Agent Design Contract\s*\n(.*?)```", text, re.S)
    if not match:
        raise ValueError(f"§3 fenced block not found in {template_path}")
    fields: list[str] = []
    for raw in match.group(1).splitlines():
        line = raw.strip()
        if not line or line.startswith("##"):
            continue
        if line.endswith(":"):
            fields.append(line[:-1].strip())
    if not fields:
        raise ValueError("no required fields parsed from template §3 block")
    return tuple(fields)


def _find_block(text: str) -> str:
    lines = text.splitlines()
    start_idx: int | None = None
    for idx, line in enumerate(lines):
        norm = line.strip().lower()
        if norm in BLOCK_HEADINGS:
            start_idx = idx
            break
    if start_idx is None:
        return ""

    body: list[str] = []
    for line in lines[start_idx + 1 :]:
        stripped = line.strip()
        if stripped == "---":
            break
        if (
            stripped.startswith("## ")
            and stripped.lower() not in INNER_BLOCK_HEADINGS
            and body
        ):
            break
        body.append(line)
    return "\n".join(body)


def _parse_fields(block: str) -> dict[str, str]:
    found: dict[str, str] = {}
    in_table = False
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("|") and "field" in line.lower() and "value" in line.lower():
            in_table = True
            continue
        if line.startswith("|---"):
            in_table = True
            continue
        if in_table:
            row = TABLE_ROW.match(line)
            if row:
                label = _normalize_label(row.group("label"))
                value = row.group("value").strip()
                if label and value and label not in {"field", "---"}:
                    found[label] = value
                continue
        labeled = LABELED_LINE.match(line)
        if labeled:
            label = _normalize_label(labeled.group("label"))
            value = (labeled.group("value") or "").strip()
            if label:
                found[label] = value
    return found


def _has_signed_infra_exception(text: str) -> bool:
    if EXCEPTION_MARKER not in text:
        return False
    return bool(re.search(r"§11\.?A?\s+.*SIGNED|Matt Nichol.*20\d{2}", text, re.I))


def validate_contract(path: Path, required_fields: tuple[str, ...]) -> ValidationResult:
    text = path.read_text(encoding="utf-8")
    block = _find_block(text)
    parsed = _parse_fields(block)
    exception = _has_signed_infra_exception(text)

    missing: list[str] = []
    for field in required_fields:
        key = _normalize_label(field)
        value = parsed.get(key, "").strip()
        if not value or value.upper() in {"TBD", "TODO", "—", "-"}:
            missing.append(field)

    found_count = len(required_fields) - len(missing)
    passed = exception or not missing
    return ValidationResult(
        path=str(path),
        required_count=len(required_fields),
        found_count=found_count if not exception else len(required_fields),
        missing_fields=tuple(missing),
        exception_validated=exception,
        passed=passed,
    )


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Step 00 validator — count Agent Design Contract §3 fields before "
            "complete_gate.py."
        ),
    )
    parser.add_argument(
        "contract_path",
        help="Path to Agent Design Contract Deep Dive markdown file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON on stdout.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (auto-detected from script location by default).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    try:
        root = _repo_root(args.repo_root)
        template_path = root / TEMPLATE_REL
        required = load_required_fields(template_path)
        contract_path = Path(args.contract_path)
        if not contract_path.is_absolute():
            contract_path = root / contract_path
        if not contract_path.is_file():
            print(f"validate_agent_contract_block: file not found: {contract_path}", file=sys.stderr)
            return EXIT_ERROR
        result = validate_contract(contract_path, required)
    except (OSError, ValueError) as exc:
        print(f"validate_agent_contract_block: {exc}", file=sys.stderr)
        return EXIT_ERROR

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    elif result.passed:
        if result.exception_validated:
            print(
                f"PASS (signed infrastructure template exception): "
                f"{result.path}"
            )
        else:
            print(
                f"PASS: {result.found_count}/{result.required_count} "
                f"template §3 fields present — {result.path}"
            )
    else:
        print(
            f"FAIL: {result.found_count}/{result.required_count} "
            f"template §3 fields — missing: {', '.join(result.missing_fields)}",
            file=sys.stderr,
        )

    return EXIT_OK if result.passed else EXIT_INCOMPLETE


if __name__ == "__main__":
    raise SystemExit(main())
