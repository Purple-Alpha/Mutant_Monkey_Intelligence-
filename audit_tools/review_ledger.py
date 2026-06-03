"""Operator-run score-sheet candidate review helper (Wave 3.1).

This helper is read-only. It lists, inspects, checks, drafts, and reports stale
candidate packets, but it never promotes, rejects, moves, deletes, rewrites, or
writes the canonical score sheet.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

try:  # pragma: no cover - exercised by subprocess/manual CLI use
    from audit_tools.score_sheet_review_scanner import (
        BLOCK,
        ScanFinding,
        format_findings,
        has_blocking_findings,
        scan_mapping,
    )
except ModuleNotFoundError:  # direct file execution from repo root or tests
    from score_sheet_review_scanner import (  # type: ignore
        BLOCK,
        ScanFinding,
        format_findings,
        has_blocking_findings,
        scan_mapping,
    )


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
CANDIDATE_DIR = WORKSPACE_ROOT / "audit_outputs" / "score_sheet_candidates"
STALE_THRESHOLD_DAYS = 60

SCHEMA_FIELDS = [
    "event_id",
    "event_date",
    "track",
    "event_type",
    "source_artifact",
    "test_or_check_name",
    "pass_fail",
    "failure_type",
    "finding_summary",
    "corrective_action",
    "retest_reference",
    "recorded_by",
    "notes",
]

CLOSED_TRACKS = {
    "testing_evidence",
    "email_security",
    "callback_phishing_toad",
    "vendor_payment_integrity",
    "cyber_insurance_evidence",
    "agent_runtime",
    "audit_gate",
    "ops_queue",
    "research_intake",
}


@dataclass(frozen=True)
class CandidatePacket:
    path: Path
    header: dict[str, object]
    rows: list[dict[str, object]]

    @property
    def packet_id(self) -> str:
        value = self.header.get("candidate_packet_id")
        return str(value or self.path.stem.removesuffix(".candidate"))


def _json_line(line: str, *, path: Path, line_number: int) -> dict[str, object]:
    try:
        value = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: malformed JSONL at line {line_number}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSONL line {line_number} must be an object")
    return value


def load_packet(packet_path: str | Path) -> CandidatePacket:
    path = Path(packet_path)
    if not path.is_absolute():
        path = WORKSPACE_ROOT / path
    if not path.exists():
        raise ValueError(f"candidate packet not found: {path}")
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise ValueError(f"{path}: empty candidate packet")

    header = _json_line(lines[0], path=path, line_number=1)
    if header.get("record_type") != "packet_header":
        raise ValueError(f"{path}: first line must be packet_header")
    rows = [_json_line(line, path=path, line_number=index) for index, line in enumerate(lines[1:], start=2)]
    for index, row in enumerate(rows, start=1):
        if row.get("record_type") != "candidate":
            raise ValueError(f"{path}: row {index} must have record_type=candidate")
    return CandidatePacket(path=path, header=header, rows=rows)


def unresolved_packets(candidate_dir: Path = CANDIDATE_DIR) -> list[Path]:
    if not candidate_dir.exists():
        return []
    packets = [
        path
        for path in candidate_dir.glob("*.candidate.jsonl")
        if path.is_file() and "promoted" not in path.parts and "rejected" not in path.parts
    ]
    return sorted(packets)


def _packet_summary(packet: CandidatePacket) -> str:
    emitted_at = str(packet.header.get("emitted_at", "unknown"))
    status = str(packet.header.get("promotion_status", "unknown"))
    return f"{_display_path(packet.path)} rows={len(packet.rows)} emitted_at={emitted_at} promotion_status={status}"


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE_ROOT))
    except ValueError:
        return str(path)


def _row_summary(row: dict[str, object], index: int) -> str:
    return (
        f"row={index} candidate_ref={row.get('candidate_ref', '')} "
        f"track={row.get('track', '')} pass_fail={row.get('pass_fail', '')} "
        f"failure_type={row.get('failure_type', '')}"
    )


def _canonical_event_id_finding(packet: CandidatePacket, row: dict[str, object], index: int) -> ScanFinding | None:
    event_id = row.get("event_id")
    if isinstance(event_id, str) and event_id.startswith("TE-"):
        return ScanFinding(
            severity=BLOCK,
            finding_class="event_id_laundering",
            path=str(packet.path),
            row_index=index,
            field="event_id",
            reason="canonical_event_id_present_before_operator_promotion",
            remediation="replace_with_null_until_operator_promotion",
        )
    return None


def _track_finding(packet: CandidatePacket, row: dict[str, object], index: int) -> ScanFinding | None:
    track = row.get("track")
    if not isinstance(track, str) or track not in CLOSED_TRACKS:
        return ScanFinding(
            severity="WARN",
            finding_class="track_taxonomy",
            path=str(packet.path),
            row_index=index,
            field="track",
            reason="track_not_in_closed_taxonomy",
            remediation="map_to_closed_wave0_track_before_promotion",
        )
    return None


def scan_packet(packet: CandidatePacket) -> list[ScanFinding]:
    findings: list[ScanFinding] = []
    for index, row in enumerate(packet.rows, start=1):
        findings.extend(scan_mapping(row, path=str(packet.path), row_index=index))
        event_id_finding = _canonical_event_id_finding(packet, row, index)
        if event_id_finding is not None:
            findings.append(event_id_finding)
        track_finding = _track_finding(packet, row, index)
        if track_finding is not None:
            findings.append(track_finding)
    return findings


def command_list(args: argparse.Namespace) -> int:
    packets = unresolved_packets(Path(args.candidate_dir))
    if not packets:
        print("No unresolved candidate packets.")
        return 0
    for path in packets:
        packet = load_packet(path)
        print(_packet_summary(packet))
    return 0


def command_inspect(args: argparse.Namespace) -> int:
    packet = load_packet(args.packet)
    print(_packet_summary(packet))
    print(f"packet_id={packet.packet_id}")
    print(f"emitter={packet.header.get('emitter', '')}")
    for index, row in enumerate(packet.rows, start=1):
        row_findings = scan_mapping(row, path=str(packet.path), row_index=index)
        status = "scan=BLOCK" if has_blocking_findings(row_findings) else "scan=OK"
        print(f"{_row_summary(row, index)} {status}")
    return 0


def _print_checklist() -> None:
    print("Wave 3 checklist:")
    print("1. Finding is real, not a tool artifact")
    print("2. failure_type is correct")
    print("3. No PII / secrets / raw payloads")
    print("4. track maps to closed taxonomy")
    print("5. finding_summary is accurate and complete")
    print("6. corrective_action / retest_reference filled or intentionally blank")
    print("7. event_id assigned at promotion only")
    print("8. operator identity and date recorded")


def command_check(args: argparse.Namespace) -> int:
    packet = load_packet(args.packet)
    findings = scan_packet(packet)
    _print_checklist()
    if findings:
        print(format_findings(findings))
    else:
        print("SCAN_OK")
    return 1 if has_blocking_findings(findings) else 0


def _draft_row(packet: CandidatePacket, row: dict[str, object]) -> dict[str, str]:
    candidate_ref = str(row.get("candidate_ref", ""))
    original_notes = str(row.get("notes", ""))
    notes_bits = [
        "DRAFT_NOT_CANONICAL",
        f"candidate_packet_id={packet.packet_id}",
    ]
    if candidate_ref:
        notes_bits.append(f"candidate_ref={candidate_ref}")
    notes_bits.append("archive_pointer_pending")
    if original_notes:
        notes_bits.append(f"operator_review_original_notes={original_notes}")

    return {
        "event_id": "OPERATOR_TO_ASSIGN",
        "event_date": "OPERATOR_TO_CONFIRM_YYYY-MM-DD",
        "track": str(row.get("track", "")),
        "event_type": str(row.get("event_type", "")),
        "source_artifact": str(row.get("source_artifact", "")),
        "test_or_check_name": str(row.get("test_or_check_name", "")),
        "pass_fail": str(row.get("pass_fail", "")),
        "failure_type": str(row.get("failure_type", "")),
        "finding_summary": str(row.get("finding_summary", "")),
        "corrective_action": str(row.get("corrective_action", "")),
        "retest_reference": str(row.get("retest_reference", "")),
        "recorded_by": "OPERATOR_TO_SET",
        "notes": " | ".join(notes_bits),
    }


def command_draft(args: argparse.Namespace) -> int:
    packet = load_packet(args.packet)
    row_number = args.row
    if row_number < 1 or row_number > len(packet.rows):
        raise ValueError(f"row must be between 1 and {len(packet.rows)}")
    row = packet.rows[row_number - 1]
    findings = scan_packet(CandidatePacket(path=packet.path, header=packet.header, rows=[row]))
    if has_blocking_findings(findings):
        print(format_findings(findings), file=sys.stderr)
        return 1

    draft = _draft_row(packet, row)
    print("\t".join(SCHEMA_FIELDS))
    print("\t".join(draft[field] for field in SCHEMA_FIELDS))
    return 0


def _parse_emitted_at(packet: CandidatePacket) -> datetime | None:
    emitted_at = packet.header.get("emitted_at")
    if not isinstance(emitted_at, str):
        return None
    try:
        return datetime.fromisoformat(emitted_at.replace("Z", "+00:00"))
    except ValueError:
        return None


def command_stale(args: argparse.Namespace) -> int:
    now = getattr(args, "now", None) or datetime.now(timezone.utc)
    stale_count = 0
    for path in unresolved_packets(Path(args.candidate_dir)):
        packet = load_packet(path)
        emitted_at = _parse_emitted_at(packet)
        if emitted_at is None:
            print(f"STALE_REVIEW_NEEDED {_display_path(path)} emitted_at=unknown")
            stale_count += 1
            continue
        age_days = (now - emitted_at).days
        if age_days > STALE_THRESHOLD_DAYS:
            print(
                f"STALE_REVIEW_NEEDED {_display_path(path)} "
                f"age_days={age_days} threshold_days={STALE_THRESHOLD_DAYS}"
            )
            stale_count += 1
    if stale_count == 0:
        print("No stale unresolved candidate packets.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review score-sheet candidate packets without promotion.")
    parser.add_argument("--candidate-dir", default=str(CANDIDATE_DIR))
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List unresolved candidate packets").set_defaults(func=command_list)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect one candidate packet")
    inspect_parser.add_argument("packet")
    inspect_parser.set_defaults(func=command_inspect)

    check_parser = subparsers.add_parser("check", help="Run checklist and scanner")
    check_parser.add_argument("packet")
    check_parser.set_defaults(func=command_check)

    draft_parser = subparsers.add_parser("draft", help="Emit non-canonical draft row to stdout")
    draft_parser.add_argument("packet")
    draft_parser.add_argument("--row", type=int, required=True)
    draft_parser.set_defaults(func=command_draft)

    stale_parser = subparsers.add_parser("stale", help="Report unresolved packets older than 60 days")
    stale_parser.set_defaults(func=command_stale)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as exc:
        print(f"review_ledger: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
