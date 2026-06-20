#!/usr/bin/env python3
"""Tier 2C Mode A — read-only contradiction / stale-state report (stdout only).

Does not execute, import, or call the MMI dispatcher. Does not write files.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ENVELOPE_FINDINGS = "REPORT_ONLY_FINDINGS"
ENVELOPE_NONE = "NO_REPORTABLE_FINDINGS"
ENVELOPE_REVIEW = "REVIEW_REQUIRED"

FORBIDDEN_TOOL_VERDICTS = frozenset(
    {
        "PASS",
        "FAIL",
        "BLOCK",
        "APPROVED",
        "VERIFIED",
        "COMPLETE",
        "BUILD_AUTHORIZED",
        "SIGNED",
        "PROMOTED",
        "SELECTED",
        "DELEGATED",
        "GATED",
        "ACCEPT",
        "REJECT",
        "NEXT_TASK",
        "RECOMMENDED",
        "AUTHORIZED",
    }
)

REVIEW_SEVERITIES = frozenset({"REVIEW", "HIGH_REVIEW", "CRITICAL_REVIEW"})

HEX40 = re.compile(r"[0-9a-fA-F]{40}")

LEGACY_TERMS = (
    re.compile(r"Swarm Command Center", re.IGNORECASE),
    re.compile(r"SwarmCommand(?!\s*Engine)", re.IGNORECASE),
    re.compile(r"\bNorthStar\b", re.IGNORECASE),
)

HISTORICAL_MARKERS = (
    "historical",
    "superseded",
    "retrospective",
    "legacy filesystem path",
    "legacy path",
    "prior:",
    "citation only",
    "built-artifact",
)

BUILD_AUTH_PHRASES = (
    "build authorization",
    "authorize",
    "build auth",
    "explicit build",
)


@dataclass
class EvidenceRef:
    path: str
    ref: str


@dataclass
class Finding:
    category: str
    severity: str
    summary: str
    evidence: list[EvidenceRef] = field(default_factory=list)
    note: str = ""


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _yaml_load_no_comments(text: str) -> dict | list | None:
    if yaml is None:
        return None
    lines = [line for line in text.splitlines() if not line.strip().startswith("#")]
    try:
        return yaml.safe_load("\n".join(lines))
    except yaml.YAMLError:
        return None


def _decision_ids(text: str) -> set[str]:
    return set(re.findall(r"MMI-DEC-\d+", text))


def _intake_ids(text: str) -> set[str]:
    return set(re.findall(r"INTAKE-\d{4}-\d{2}-\d{2}-\d{3}", text))


def _git_object_exists(root: Path, commit: str) -> bool:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "cat-file", "-t", commit],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        return proc.returncode == 0 and proc.stdout.strip() in {"commit", "tag"}
    except (OSError, subprocess.SubprocessError):
        return False


def _is_historical_context(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in HISTORICAL_MARKERS)


def _legacy_in_active_text(text: str, path_label: str) -> bool:
    if _is_historical_context(text):
        return False
    if re.search(r"/northstar", text, re.IGNORECASE) or "legacy filesystem path" in text.lower():
        return False
    for pattern in LEGACY_TERMS:
        if pattern.search(text):
            if pattern.pattern == r"\bNorthStar\b" and "Mutant Monkey" in text:
                continue
            return True
    return False


def _has_closeout_evidence(status_evidence: list) -> bool:
    if not status_evidence:
        return False
    types = {item.get("type") for item in status_evidence if isinstance(item, dict)}
    has_commit = "commit" in types
    has_closeout = "mmi_decision" in types or "worker_packet" in types
    return has_commit and has_closeout


def _is_retrospective_complete(task: dict) -> bool:
    for entry in task.get("transition_log") or []:
        if not isinstance(entry, dict):
            continue
        ref = str(entry.get("evidence_ref", ""))
        if entry.get("from") == "BUILT_NEEDS_REVIEW" and entry.get("to") == "COMPLETE":
            if "retrospective" in ref.lower() or "historical" in ref.lower():
                return True
    notes = str(task.get("notes", ""))
    if _is_historical_context(notes):
        return True
    return False


def _collect_commit_hashes(blob: str) -> set[str]:
    return set(m.group(0).lower() for m in HEX40.finditer(blob))


def _signed_contract_paths(root: Path) -> list[Path]:
    mmi = root / "mmi"
    if not mmi.is_dir():
        return []
    paths = []
    for path in mmi.glob("*CONTRACT*.md"):
        text = _read_text(path)
        if "§11 SIGNED" in text or "**Status:** §11 SIGNED" in text:
            paths.append(path)
    return paths


def _registry_task_refs(registry: dict) -> set[str]:
    refs: set[str] = set()
    for task in registry.get("tasks") or []:
        if not isinstance(task, dict):
            continue
        refs.add(str(task.get("title", "")))
        refs.add(str(task.get("task_or_contract_ref", "")))
        for blob in (task.get("source_evidence") or []):
            refs.add(str(blob))
    return refs


def analyze(root: Path) -> tuple[list[Finding], list[str]]:
    """Return findings and parse errors (non-empty => exit 2)."""
    errors: list[str] = []
    findings: list[Finding] = []
    fid = 0

    def add(category: str, severity: str, summary: str, path: str, ref: str, note: str = "") -> None:
        nonlocal fid
        fid += 1
        findings.append(
            Finding(
                category=category,
                severity=severity,
                summary=summary,
                evidence=[EvidenceRef(path=path, ref=ref)],
                note=note,
            )
        )

    registry_path = root / "mmi" / "MMI_TASK_REGISTRY.yaml"
    registry_text = _read_text(registry_path)
    registry = _yaml_load_no_comments(registry_text) if registry_text else None
    if registry_text and registry is None:
        errors.append(f"REGISTRY_PARSE_ERROR: {registry_path}")

    decision_path = root / "mmi" / "MMI_DECISION_LOG.md"
    decision_text = _read_text(decision_path)
    decision_ids = _decision_ids(decision_text)

    intake_path = root / "mmi" / "MMI_INTAKE_RECORDS.md"
    intake_text = _read_text(intake_path)
    intake_ids = _intake_ids(intake_text)

    state_path = root / "MMI_CURRENT_STATE.md"
    state_text = _read_text(state_path)

    if isinstance(registry, dict):
        if registry.get("dispatcher_reads") is not False:
            add(
                "DISPATCHER_REGISTRY_BOUNDARY_RISK",
                "CRITICAL_REVIEW",
                "Registry envelope dispatcher_reads is not false",
                str(registry_path),
                "dispatcher_reads",
            )
        if registry.get("autonomous_selection") is not False:
            add(
                "DISPATCHER_REGISTRY_BOUNDARY_RISK",
                "CRITICAL_REVIEW",
                "Registry envelope autonomous_selection is not false",
                str(registry_path),
                "autonomous_selection",
            )
        if registry.get("maintained_by") != "human":
            add(
                "DISPATCHER_REGISTRY_BOUNDARY_RISK",
                "CRITICAL_REVIEW",
                "Registry envelope maintained_by is not human",
                str(registry_path),
                "maintained_by",
            )

        for task in registry.get("tasks") or []:
            if not isinstance(task, dict):
                continue
            task_id = str(task.get("task_id", "unknown"))
            status = str(task.get("status", ""))
            status_evidence = task.get("status_evidence") or []

            if status == "COMPLETE" and not _has_closeout_evidence(status_evidence):
                if not _is_retrospective_complete(task):
                    add(
                        "COMPLETE_WITHOUT_CLOSEOUT_EVIDENCE",
                        "HIGH_REVIEW",
                        f"Task {task_id} is COMPLETE without commit + closeout evidence",
                        str(registry_path),
                        f"task_id={task_id}",
                    )

            if status == "BUILD_AUTHORIZED":
                ok = False
                for ev in status_evidence:
                    if not isinstance(ev, dict):
                        continue
                    ev_type = ev.get("type")
                    if ev_type in ("mmi_decision", "operator_instruction"):
                        note = str(ev.get("note", "")).lower()
                        ref = str(ev.get("ref", "")).lower()
                        if any(p in note or p in ref for p in BUILD_AUTH_PHRASES) or ev_type == "mmi_decision":
                            ok = True
                if not ok:
                    add(
                        "BUILD_AUTHORIZED_WITHOUT_MATT_AUTH",
                        "CRITICAL_REVIEW",
                        f"Task {task_id} is BUILD_AUTHORIZED without explicit authorization evidence",
                        str(registry_path),
                        f"task_id={task_id}",
                    )

            for ev in status_evidence:
                if not isinstance(ev, dict):
                    continue
                ref = str(ev.get("ref", ""))
                if ref.startswith("MMI-DEC-") and ref not in decision_ids:
                    add(
                        "REGISTRY_DECISION_LOG_MISMATCH",
                        "HIGH_REVIEW",
                        f"Task {task_id} cites missing decision {ref}",
                        str(registry_path),
                        ref,
                    )
                if ref.startswith("INTAKE-") and ref not in intake_ids:
                    add(
                        "REGISTRY_INTAKE_RECORD_MISMATCH",
                        "HIGH_REVIEW",
                        f"Task {task_id} cites missing intake {ref}",
                        str(registry_path),
                        ref,
                    )
                if ev.get("type") == "commit":
                    commit = ref.lower()
                    if HEX40.fullmatch(commit) and not _git_object_exists(root, commit):
                        add(
                            "STALE_COMMIT_REFERENCE",
                            "HIGH_REVIEW",
                            f"Task {task_id} cites commit that does not resolve in git",
                            str(registry_path),
                            commit,
                        )

            blob = str(task)
            if "DO_NOT_USE" in blob and "do-not-use" not in blob.lower():
                if status not in ("DO_NOT_USE", "SUPERSEDED", "REJECTED"):
                    for other in registry.get("tasks") or []:
                        if other is task:
                            continue
                        other_id = str(other.get("task_id", ""))
                        other_blob = str(other)
                        if "DO_NOT_USE" in other_blob and other_id in blob:
                            if not _is_historical_context(blob):
                                add(
                                    "DO_NOT_USE_REFERENCED_AS_AUTHORITY",
                                    "HIGH_REVIEW",
                                    f"Task {task_id} may cite DO_NOT_USE scope as live authority",
                                    str(registry_path),
                                    f"task_id={task_id}",
                                )

            notes = str(task.get("notes", ""))
            if notes and _legacy_in_active_text(notes, "registry notes"):
                add(
                    "LEGACY_NAMING_DRIFT",
                    "REVIEW",
                    f"Legacy naming in registry notes for {task_id}",
                    str(registry_path),
                    f"task_id={task_id}",
                )

    # E-01 signed contracts without registry row (INFO advisory)
    if isinstance(registry, dict):
        task_refs = _registry_task_refs(registry)
        for contract_path in _signed_contract_paths(root):
            rel = contract_path.relative_to(root).as_posix()
            name = contract_path.name
            if rel not in task_refs and name not in task_refs:
                if "TIER2C" not in name.upper():  # Tier 2C may not have registry row yet
                    add(
                        "SIGNED_CONTRACT_WITHOUT_REGISTRY_ROW",
                        "INFO",
                        f"Signed contract {rel} has no matching registry row (INFO advisory)",
                        rel,
                        "§11 SIGNED",
                        "Not a defect unless signed rule requires registry row",
                    )

    # C-04 style: decision ACCEPT with build artifacts vs registry status
    if isinstance(registry, dict) and decision_text:
        for line in decision_text.splitlines():
            if not line.startswith("MMI-DEC-"):
                continue
            if "ACCEPT" not in line:
                continue
            dec_id = line.split("|", 1)[0].strip()
            lower = line.lower()
            if "build" not in lower and "mode a" not in lower:
                continue
            for task in registry.get("tasks") or []:
                if not isinstance(task, dict):
                    continue
                ev_blob = str(task.get("status_evidence", ""))
                if dec_id in ev_blob:
                    status = str(task.get("status", ""))
                    if status in ("SIGNED_CONTRACT", "DRAFT_CONTRACT", "CANDIDATE"):
                        add(
                            "BUILD_COMMIT_WITHOUT_REGISTRY_UPDATE",
                            "REVIEW",
                            f"Decision {dec_id} ACCEPT but registry task remains {status}",
                            str(registry_path),
                            f"task_id={task.get('task_id')}",
                        )

    # Naming drift in LAST_COMPLETED
    if state_text:
        last_idx = state_text.find("LAST_COMPLETED:")
        if last_idx != -1:
            section = state_text[last_idx:last_idx + 800]
            if _legacy_in_active_text(section, "LAST_COMPLETED"):
                add(
                    "LEGACY_NAMING_DRIFT",
                    "REVIEW",
                    "Legacy naming in MMI_CURRENT_STATE.md LAST_COMPLETED prose",
                    "MMI_CURRENT_STATE.md",
                    "LAST_COMPLETED",
                )

    # Intake references missing decisions
    for intake_id in _intake_ids(intake_text):
        block_start = intake_text.find(intake_id)
        if block_start == -1:
            continue
        block = intake_text[block_start:block_start + 500]
        for dec in _decision_ids(block):
            if dec not in decision_ids:
                add(
                    "REGISTRY_INTAKE_RECORD_MISMATCH",
                    "HIGH_REVIEW",
                    f"Intake {intake_id} references missing decision {dec}",
                    "mmi/MMI_INTAKE_RECORDS.md",
                    intake_id,
                )

    return findings, errors


def _format_finding(index: int, finding: Finding) -> list[str]:
    lines = [
        f"finding_id: T2C-F-{index}",
        f"category: {finding.category}",
        f"severity: {finding.severity}",
        f"summary: {finding.summary}",
    ]
    if finding.evidence:
        lines.append("evidence:")
        for ev in finding.evidence:
            lines.append(f"  - path: {ev.path}")
            lines.append(f"    ref: {ev.ref}")
    if finding.note:
        lines.append(f"note: {finding.note}")
    return lines


def format_report(findings: list[Finding]) -> str:
    envelope_lines: list[str] = []
    if not findings:
        envelope_lines.append(ENVELOPE_NONE)
    else:
        envelope_lines.append(ENVELOPE_FINDINGS)
        if any(f.severity in REVIEW_SEVERITIES for f in findings):
            envelope_lines.append(ENVELOPE_REVIEW)
        for idx, finding in enumerate(findings, start=1):
            envelope_lines.extend(_format_finding(idx, finding))

    for line in envelope_lines:
        stripped = line.strip()
        if stripped in FORBIDDEN_TOOL_VERDICTS:
            raise RuntimeError(f"forbidden tool verdict on envelope line: {stripped}")
        if stripped.startswith("VERDICT:"):
            raise RuntimeError("forbidden VERDICT line on envelope output")

    return "\n".join(envelope_lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Tier 2C Mode A read-only contradiction/stale-state report (stdout only)."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root containing MMI governance files (default: repo root)",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve() if args.root else _repo_root()
    findings, errors = analyze(root)
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 2

    sys.stdout.write(format_report(findings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
