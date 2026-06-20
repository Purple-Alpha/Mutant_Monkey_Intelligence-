#!/usr/bin/env python3
"""MMI Architect — Mode A read-only blueprint emitter (stdout only).

Blueprints exactly one operator-selected candidate from a fixed manifest and
recorded on-disk source contracts. Does not write files, score, select, or
authorize builds.

Authority: ``mmi/MMI_ARCHITECT_BLUEPRINT_CONTRACT.md`` Mode A (Matt dispatch
2026-06-20). Does not import or call the MMI dispatcher, task registry,
or scoreboard writers.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ENVELOPE_BLUEPRINT = "BLUEPRINT"
ENVELOPE_INSUFFICIENT = "INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT"

FORBIDDEN_TOOL_VERDICTS = frozenset(
    {
        "SELECTED",
        "AUTHORIZED",
        "APPROVED",
        "RECOMMENDED",
        "BUILD_AUTHORIZED",
        "COMPLETE",
        "SIGNED",
        "VERIFIED",
        "PASS",
        "FAIL",
        "PROMOTED",
        "NEXT_DECIDED",
    }
)

VAGUE_WORDS = frozenset(
    {
        "works well",
        "good",
        "clean",
        "reasonable",
        "robust",
        "appropriate",
        "properly",
    }
)

RESEARCH_PATH_RE = re.compile(r"mmi/research/", re.IGNORECASE)
TABLE_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")
CHECK_LINE_RE = re.compile(r"^\s*-\s*CHECK:\s*(.+)\s*$", re.MULTILINE)
OUT_OF_SCOPE_HEADER_RE = re.compile(
    r"(?:^|\n)#{1,3}\s*Out of scope[^\n]*\n(.*?)(?=\n#{1,3}\s|\Z)",
    re.IGNORECASE | re.DOTALL,
)
FLOW_SECTION_RE = re.compile(
    r"##\s*FLOW CONTRACT\s*\n(.*?)(?=\n##\s|\Z)",
    re.IGNORECASE | re.DOTALL,
)
BUILD_CONDITIONS_RE = re.compile(
    r"##\s*BUILD CONDITIONS\s*\n(.*?)(?=\n##\s|\Z)",
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class CandidateManifest:
    candidate_id: str
    name: str
    agent_contract_rel: str
    artifact_basis_rel: tuple[str, ...]


CANDIDATE_MANIFEST: dict[str, CandidateManifest] = {
    "#47": CandidateManifest(
        candidate_id="#47",
        name="Case Timeline",
        agent_contract_rel=(
            "4. Product_Roadmap/Case_Timeline_Agent_Design_Contract_Deep_Dive.md"
        ),
        artifact_basis_rel=(
            "4. Product_Roadmap/Verification_Outcome_Agent_Design_Contract_Deep_Dive.md",
            (
                "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
                "core/orchestrator/agent_contract.py"
            ),
            (
                "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
                "core/orchestrator/verification_outcome_agent.py"
            ),
        ),
    ),
    "#52": CandidateManifest(
        candidate_id="#52",
        name="Plain-English Explanation",
        agent_contract_rel=(
            "4. Product_Roadmap/Plain_English_Explanation_Agent_Design_Contract_Deep_Dive.md"
        ),
        artifact_basis_rel=(
            "4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md",
            (
                "3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/"
                "core/scoring/client_facing_rubric.py"
            ),
        ),
    ),
}

FLOW_FIELDS = (
    "output_location",
    "output_format",
    "downstream_consumer",
    "consumer_usage",
)


@dataclass
class ParsedContract:
    path: Path
    text: str
    flow: dict[str, str] = field(default_factory=dict)
    out_of_scope: list[str] = field(default_factory=list)
    build_conditions: list[str] = field(default_factory=list)
    research_authority_paths: list[str] = field(default_factory=list)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _strip_ticks(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        return value.strip("`")
    return value


def _parse_table_fields(section: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in section.splitlines():
        match = TABLE_ROW_RE.match(line.strip())
        if not match:
            continue
        key = match.group(1).strip().lower().replace(" ", "_")
        val = _strip_ticks(match.group(2).strip())
        if key in ("field", "---") or not val:
            continue
        fields[key] = val
    return fields


def _parse_out_of_scope(text: str) -> list[str]:
    match = OUT_OF_SCOPE_HEADER_RE.search(text)
    if not match:
        return []
    items: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif stripped.startswith("* "):
            items.append(stripped[2:].strip())
    return [item for item in items if item]


def _parse_build_conditions(text: str) -> list[str]:
    match = BUILD_CONDITIONS_RE.search(text)
    if not match:
        return []
    return [m.group(1).strip() for m in CHECK_LINE_RE.finditer(match.group(1))]


def _research_authority_hits(text: str, source_label: str) -> list[str]:
    hits: list[str] = []
    if not RESEARCH_PATH_RE.search(text):
        return hits
    for line in text.splitlines():
        if not RESEARCH_PATH_RE.search(line):
            continue
        lower = line.lower()
        if "excluded" in lower or "not authority" in lower or "ignore" in lower:
            continue
        if any(
            token in lower
            for token in (
                "authority",
                "source-of-truth",
                "source of truth",
                "check:",
                "required",
                "downstream",
                "output_location",
                "consumer",
            )
        ):
            hits.append(f"{source_label}: {line.strip()}")
    return hits


def _parse_agent_contract(path: Path) -> ParsedContract:
    text = _read_text(path)
    parsed = ParsedContract(path=path, text=text)
    flow_match = FLOW_SECTION_RE.search(text)
    if flow_match:
        parsed.flow = _parse_table_fields(flow_match.group(1))
    parsed.out_of_scope = _parse_out_of_scope(text)
    parsed.build_conditions = _parse_build_conditions(text)
    parsed.research_authority_paths = _research_authority_hits(
        text, str(path.as_posix())
    )
    return parsed


def _validate_flow(flow: dict[str, str]) -> list[str]:
    gaps: list[str] = []
    for key in FLOW_FIELDS:
        if not flow.get(key, "").strip():
            gaps.append(f"missing_flow_contract_field: {key}")
    return gaps


def _validate_build_conditions(conditions: list[str]) -> list[str]:
    gaps: list[str] = []
    if not conditions:
        gaps.append("missing_build_conditions_section")
        return gaps
    for cond in conditions:
        lower = cond.lower()
        if not (
            lower.startswith("file_exists:")
            or lower.startswith("field_present:")
            or lower.startswith("command_expect:")
            or lower.startswith("path_exact:")
            or lower.startswith("format_exact:")
            or lower.startswith("consumer_named:")
        ):
            gaps.append(f"non_checkable_build_condition: {cond}")
            continue
        for vague in VAGUE_WORDS:
            if vague in lower:
                gaps.append(f"vague_build_condition: {cond}")
    return gaps


def analyze(root: Path, candidate_id: str) -> tuple[str, list[str], str]:
    """Return (envelope, gaps, blueprint_text). blueprint_text empty if insufficient."""
    gaps: list[str] = []
    manifest = CANDIDATE_MANIFEST.get(candidate_id)
    if manifest is None:
        gaps.append(f"unknown_candidate: {candidate_id}")
        return ENVELOPE_INSUFFICIENT, gaps, ""

    contract_path = root / manifest.agent_contract_rel
    if not contract_path.is_file():
        gaps.append(f"missing_source: {manifest.agent_contract_rel}")

    for rel in manifest.artifact_basis_rel:
        basis_path = root / rel
        if not basis_path.is_file():
            gaps.append(f"missing_artifact_basis: {rel}")

    if gaps:
        return ENVELOPE_INSUFFICIENT, gaps, ""

    parsed = _parse_agent_contract(contract_path)
    if not parsed.text.strip():
        gaps.append(f"unreadable_source: {manifest.agent_contract_rel}")
        return ENVELOPE_INSUFFICIENT, gaps, ""

    gaps.extend(_validate_flow(parsed.flow))
    if not parsed.out_of_scope:
        gaps.append("missing_out_of_scope_source")
    gaps.extend(_validate_build_conditions(parsed.build_conditions))
    gaps.extend(
        f"research_note_authority_forbidden: {hit}"
        for hit in parsed.research_authority_paths
    )

    for rel in manifest.artifact_basis_rel:
        basis_text = _read_text(root / rel)
        for hit in _research_authority_hits(basis_text, rel):
            gaps.append(f"research_note_authority_forbidden: {hit}")

    if gaps:
        return ENVELOPE_INSUFFICIENT, gaps, ""

    blueprint = _format_blueprint(root, manifest, parsed)
    return ENVELOPE_BLUEPRINT, [], blueprint


def _format_blueprint(
    root: Path, manifest: CandidateManifest, parsed: ParsedContract
) -> str:
    lines = [
        ENVELOPE_BLUEPRINT,
        f"candidate_id: {manifest.candidate_id}",
        f"name: {manifest.name}",
        "---",
        "section: 1 CANDIDATE",
        f"selected_candidate: {manifest.candidate_id}",
        f"selected_name: {manifest.name}",
        "---",
        "section: 2 SOURCE MANIFEST",
        f"agent_contract: {manifest.agent_contract_rel}",
    ]
    for rel in manifest.artifact_basis_rel:
        lines.append(f"artifact_basis: {rel}")
    lines.extend(
        [
            "---",
            "section: 3 BUILD CONDITIONS",
        ]
    )
    for cond in parsed.build_conditions:
        lines.append(f"condition: CHECK:{cond}")
    lines.extend(
        [
            "---",
            "section: 4 FLOW CONTRACT",
            f"output_location: {parsed.flow['output_location']}",
            f"output_format: {parsed.flow['output_format']}",
            f"downstream_consumer: {parsed.flow['downstream_consumer']}",
            f"consumer_usage: {parsed.flow['consumer_usage']}",
            "---",
            "section: 5 OUT OF SCOPE",
        ]
    )
    for item in parsed.out_of_scope:
        lines.append(f"boundary: {item}")
    lines.extend(
        [
            "---",
            "section: 6 EVIDENCE REQUIREMENTS",
            (
                "requirement: WORKER_COMPLETION_PACKET with task_or_contract_ref, "
                "files_changed, exact_commit_hash, scope_confirmation, "
                "tests_gates_run, deviations_from_contract, verify_output, "
                "git_status_short"
            ),
            f"requirement: CHECK:file_exists:{manifest.agent_contract_rel}",
        ]
    )
    for cond in parsed.build_conditions:
        lines.append(f"requirement: CHECK:{cond}")
    lines.extend(
        [
            "---",
            f"source_contract_path: {manifest.agent_contract_rel}",
        ]
    )
    return _validate_output("\n".join(lines) + "\n")


def format_insufficient(candidate_id: str, gaps: list[str]) -> str:
    lines = [ENVELOPE_INSUFFICIENT, f"candidate_id: {candidate_id}", "gaps:"]
    for gap in gaps:
        lines.append(f"  - {gap}")
    return _validate_output("\n".join(lines) + "\n")


def _validate_output(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped in FORBIDDEN_TOOL_VERDICTS:
            raise RuntimeError(f"forbidden tool verdict on output line: {stripped}")
        if stripped.startswith("VERDICT:"):
            raise RuntimeError("forbidden VERDICT line on architect output")
        if not stripped.startswith("condition:") and not stripped.startswith(
            "requirement:"
        ):
            lower = stripped.lower()
            for vague in VAGUE_WORDS:
                if re.search(rf"\b{re.escape(vague)}\b", lower):
                    raise RuntimeError(f"vague language on output line: {stripped}")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="MMI Architect Mode A — read-only blueprint emitter (stdout only)."
    )
    parser.add_argument(
        "--candidate",
        required=True,
        help='Selected candidate id only (e.g. "#52")',
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: repo root)",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve() if args.root else _repo_root()
    envelope, gaps, blueprint = analyze(root, args.candidate.strip())
    if envelope == ENVELOPE_BLUEPRINT:
        sys.stdout.write(blueprint)
        return 0

    sys.stdout.write(format_insufficient(args.candidate.strip(), gaps))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
