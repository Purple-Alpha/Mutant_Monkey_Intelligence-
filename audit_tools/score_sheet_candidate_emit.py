"""Score sheet candidate emitter (Wave 2, first emitter).

Implements the signed Wave 2 contract
(4. Product_Roadmap/Score_Sheet_Candidate_Emit_Implementation_Deep_Dive.md):

- Emits JSONL candidate packets under audit_outputs/score_sheet_candidates/.
- Dry-run by default: prints the packet, writes nothing.
- Scans every candidate-bound string for unsafe content and redacts unsafe fields.
- Never assigns a canonical event_id (always null at emission).
- recorded_by is always "tool_candidate".
- Never writes the canonical ledger, never promotes, never moves or deletes packets.
- Atomic write: temp file in the same directory, then os.replace.

This module is additive and isolated. It does not modify existing audit logic
and is not wired into pre_ship_audit.py.
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

CANDIDATE_DIR = Path("audit_outputs/score_sheet_candidates")

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

SCHEMA_FIELDS = [
    "event_id", "event_date", "track", "event_type", "source_artifact",
    "test_or_check_name", "pass_fail", "failure_type", "finding_summary",
    "corrective_action", "retest_reference", "recorded_by", "notes",
]

REDACTION_PLACEHOLDER = "[REDACTED_BY_CANDIDATE_EMITTER]"
RESERVED_EMAIL_SUFFIXES = (".example", ".test", ".invalid", ".localhost")
MAX_FIELD_LEN = 2000

_SECRET_RE = re.compile(r"(api[_-]?key|secret|password|authorization|bearer|sk-[A-Za-z0-9]|xox[a-z]-)", re.I)
_AUTH_HEADER_RE = re.compile(r"^\s*authorization\s*:|bearer\s+\S", re.I | re.M)
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
_PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\d)")
_PAYLOAD_MARKER_RE = re.compile(r"^\s*(from|to|subject|received|message-id|content-type)\s*:", re.I | re.M)


def scan_unsafe(value):
    """Return a list of reasons the value is unsafe. Empty list means safe."""
    if not isinstance(value, str):
        return []
    reasons = []
    if _SECRET_RE.search(value):
        reasons.append("secret-like term/value")
    if _AUTH_HEADER_RE.search(value):
        reasons.append("authorization header")
    for m in _EMAIL_RE.finditer(value):
        domain = m.group(1).lower()
        if not domain.endswith(RESERVED_EMAIL_SUFFIXES):
            reasons.append("real email address")
            break
    if _PHONE_RE.search(value):
        reasons.append("phone-like personal data")
    if _PAYLOAD_MARKER_RE.search(value):
        reasons.append("raw mailbox/message payload marker")
    if len(value) > MAX_FIELD_LEN:
        reasons.append("oversized raw text blob")
    return reasons


def _normalize_candidate(raw, packet_id, index):
    """Map a raw candidate dict to a safe, schema-complete candidate row."""
    row = {field: raw.get(field, "") for field in SCHEMA_FIELDS}
    row["event_id"] = None
    row["recorded_by"] = "tool_candidate"
    if not row.get("event_date"):
        row["event_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    notes = []
    for key in SCHEMA_FIELDS:
        reasons = scan_unsafe(row.get(key))
        if reasons:
            row[key] = REDACTION_PLACEHOLDER
            notes.append(key + ": " + ", ".join(sorted(set(reasons))))

    track = str(raw.get("track", "")).strip()
    row["track"] = track
    provisional = track not in CLOSED_TRACKS
    if provisional:
        notes.append("track '" + track + "' not in closed taxonomy; provisional, not promotable")

    if notes:
        base = "" if row.get("notes") in (None, "", REDACTION_PLACEHOLDER) else row["notes"]
        sep = " | " if base else ""
        row["notes"] = base + sep + "EMITTER NOTES: " + "; ".join(notes)

    ordered = {"record_type": "candidate", "candidate_ref": packet_id + "#" + str(index)}
    for field in SCHEMA_FIELDS:
        ordered[field] = row.get(field, "")
    if provisional:
        ordered["track_provisional"] = True
    return ordered


def build_packet(candidates, emitter="pre_ship_audit.py", short_context="run", source_run=None):
    """Build (packet_id, header_dict, [row_dicts]) for the given candidates."""
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%SZ")
    emitter_slug = re.sub(r"[^A-Za-z0-9_]+", "_", emitter).strip("_") or "emitter"
    ctx_slug = re.sub(r"[^A-Za-z0-9_]+", "_", short_context).strip("_") or "run"
    packet_id = ts + "_" + emitter_slug + "_" + ctx_slug
    header = {
        "record_type": "packet_header",
        "candidate_packet_id": packet_id,
        "emitter": emitter,
        "emitted_at": now.isoformat(),
        "status": "AI-drafted",
        "promotion_status": "not_reviewed",
        "source_run": source_run or {},
    }
    rows = [_normalize_candidate(c, packet_id, i + 1) for i, c in enumerate(candidates)]
    return packet_id, header, rows


def emit(candidates, emitter="pre_ship_audit.py", short_context="run",
         source_run=None, out_dir=CANDIDATE_DIR, dry_run=True):
    """Emit a candidate packet. Dry-run prints and writes nothing.

    Returns the written Path, or None for a dry-run or a no-op (no candidates).
    """
    if not candidates:
        return None

    packet_id, header, rows = build_packet(candidates, emitter, short_context, source_run)
    lines = [json.dumps(header, ensure_ascii=False)]
    lines += [json.dumps(r, ensure_ascii=False) for r in rows]
    content = "\n".join(lines) + "\n"

    if dry_run:
        sys.stdout.write("# DRY-RUN candidate packet (not written)\n")
        sys.stdout.write(content)
        return None

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    target = out_path / (packet_id + ".candidate.jsonl")

    fd, tmp = tempfile.mkstemp(dir=str(out_path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(tmp, target)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return target


def _demo():
    sample = [
        {
            "event_date": "2026-06-02",
            "track": "audit_gate",
            "event_type": "fail",
            "source_artifact": "audit_outputs/example_demo.md",
            "test_or_check_name": "demo_check",
            "pass_fail": "fail",
            "failure_type": "expectation_contract",
            "finding_summary": "Demo failing check for dry-run validation.",
            "corrective_action": "",
            "retest_reference": "",
            "notes": "",
        },
    ]
    emit(sample, emitter="pre_ship_audit.py", short_context="dry_run_demo", dry_run=True)


if __name__ == "__main__":
    _demo()
