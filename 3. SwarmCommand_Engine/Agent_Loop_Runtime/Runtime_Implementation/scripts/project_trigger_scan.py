"""Local read-only project trigger scanner.

Implements the v1 of the autonomous trigger layer specified at
``3. SwarmCommand_Engine/Agent_Loop_Runtime/Autonomous_Triggers/autonomous-defensive-triggers.md``.

The scanner is intentionally **read-only and offline**:

* It compares the current repo against a small set of expected anchors
  (tracking docs, baseline test count, runbook references).
* It emits one or more trigger packets in the locked schema.
* It can optionally emit a one-hour mission envelope per
  ``Autonomous_Workflows/one-hour-agent-training-loop.md``.
* It writes **nothing** to ``production_state``, tenant overrides, the
  Blackboard, the policy pipeline, or any external system.
* All emitted packets carry ``mode = "training"`` and
  ``requires_operator_approval = true``.

Invoke from ``Runtime_Implementation/``::

    python -m scripts.project_trigger_scan --baseline-tests 461

The default behavior prints results to stdout. ``--out`` writes the
trigger packets to a JSON file for review or downstream consumption.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_HANDSHAKE = "PROJECT_HANDSHAKE.md"
DEFAULT_PROGRESS = "PROGRESS.md"
DEFAULT_ACTIVITY_LOG = "PROJECT_ACTIVITY_LOG.md"
DEFAULT_MASTER_INDEX = "MASTER_INDEX.md"

FORBIDDEN_AUTONOMOUS_ACTIONS = (
    "production_policy_apply",
    "tenant_override_write",
    "rollback_request",
    "client_facing_send",
    "external_network_call",
)

TriggerSeverity = str  # one of: info|review|training|urgent_review|halt_recommended

_TRACKING_BASELINE_REGEX = re.compile(
    r"(?P<count>\d{2,5})\s*(?:tests?\s+passing|/\s*(?P=count)\s+pytest)",
    re.IGNORECASE,
)
_ACCEPTED_PROGRESS_MARKERS = (
    "in progress",
    "blocked",
    "api budget gate",
    "approval",
)


@dataclass(frozen=True)
class TriggerPacket:
    trigger_id: str
    trigger_class: str
    severity: TriggerSeverity
    tenant_id: str
    evidence_record_ids: list[str]
    changed_paths: list[str]
    recommended_loop: str
    allowed_paths: list[str]
    forbidden_actions: list[str]
    requires_operator_approval: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trigger_id": self.trigger_id,
            "trigger_class": self.trigger_class,
            "severity": self.severity,
            "tenant_id": self.tenant_id,
            "evidence_record_ids": list(self.evidence_record_ids),
            "changed_paths": list(self.changed_paths),
            "recommended_loop": self.recommended_loop,
            "allowed_paths": list(self.allowed_paths),
            "forbidden_actions": list(self.forbidden_actions),
            "requires_operator_approval": self.requires_operator_approval,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class ScanResult:
    scanned_at: datetime
    repo_root: Path
    baseline_tests_expected: int | None
    baseline_tests_recorded: int | None
    packets: list[TriggerPacket]
    drift_findings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "scanned_at": self.scanned_at.isoformat(),
            "repo_root": str(self.repo_root),
            "baseline_tests_expected": self.baseline_tests_expected,
            "baseline_tests_recorded": self.baseline_tests_recorded,
            "drift_findings": list(self.drift_findings),
            "packets": [packet.to_dict() for packet in self.packets],
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project_trigger_scan",
        description=(
            "Local read-only project trigger scanner. Detects baseline / "
            "tracking drift and emits training-mode trigger packets. "
            "Never writes to production_state, overrides, or external systems."
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=DEFAULT_REPO_ROOT,
        help="Workspace root (defaults to the resolved venture root).",
    )
    parser.add_argument(
        "--baseline-tests",
        type=int,
        default=None,
        help=(
            "Expected current pytest baseline. If provided, the scanner "
            "compares it against the number recorded in PROJECT_HANDSHAKE / "
            "PROGRESS and emits a runtime_baseline_changed packet on drift."
        ),
    )
    parser.add_argument(
        "--tenant-id",
        type=str,
        default="tenant_demo",
        help="Tenant id stamped on emitted packets (default: tenant_demo).",
    )
    parser.add_argument(
        "--with-mission-envelope",
        action="store_true",
        help=(
            "When a training-eligible trigger is emitted, also write a one-hour "
            "mission envelope per Autonomous_Workflows/one-hour-agent-training-loop.md."
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional file path to write the JSON scan result.",
    )
    parser.add_argument(
        "--mission-out",
        type=Path,
        default=None,
        help=(
            "Optional file path to write the one-hour mission envelope "
            "(requires --with-mission-envelope and at least one training packet)."
        ),
    )
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = scan(
        repo_root=args.repo_root,
        baseline_tests_expected=args.baseline_tests,
        tenant_id=args.tenant_id,
    )
    payload = result.to_dict()
    print(json.dumps(payload, indent=2, sort_keys=True))

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if args.with_mission_envelope:
        training_packets = [
            packet
            for packet in result.packets
            if packet.severity in {"training", "urgent_review"}
        ]
        if training_packets:
            envelope = build_mission_envelope(
                training_packets,
                scanned_at=result.scanned_at,
            )
            print(json.dumps({"mission_envelope": envelope}, indent=2, sort_keys=True))
            if args.mission_out is not None:
                args.mission_out.parent.mkdir(parents=True, exist_ok=True)
                args.mission_out.write_text(
                    json.dumps(envelope, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
    return 0


def scan(
    *,
    repo_root: Path,
    baseline_tests_expected: int | None = None,
    tenant_id: str = "tenant_demo",
    now: datetime | None = None,
) -> ScanResult:
    """Run all v1 scan profiles and return a structured result.

    The scan is read-only and offline. It reads handshake / progress /
    activity-log / master-index files only.
    """

    scanned_at = now or datetime.now(timezone.utc)
    drift_findings: list[str] = []
    packets: list[TriggerPacket] = []

    handshake_path = repo_root / DEFAULT_HANDSHAKE
    progress_path = repo_root / DEFAULT_PROGRESS
    activity_log_path = repo_root / DEFAULT_ACTIVITY_LOG
    master_index_path = repo_root / DEFAULT_MASTER_INDEX

    for required in (handshake_path, master_index_path):
        if not required.exists():
            drift_findings.append(f"missing tracking file: {required.name}")

    handshake_text = _read_text_safe(handshake_path)
    progress_text = _read_text_safe(progress_path)
    activity_text = _read_text_safe(activity_log_path)
    master_index_text = _read_text_safe(master_index_path)

    baseline_recorded = _extract_baseline_count(
        sources=[handshake_text, progress_text, activity_text],
    )

    packet_counter = 1

    if baseline_tests_expected is not None and baseline_recorded is not None:
        if baseline_tests_expected != baseline_recorded:
            packets.append(
                _emit_packet(
                    packet_counter,
                    scanned_at=scanned_at,
                    trigger_class="runtime_baseline_changed",
                    severity="training",
                    tenant_id=tenant_id,
                    changed_paths=[
                        str(handshake_path.relative_to(repo_root)),
                        str(progress_path.relative_to(repo_root))
                        if progress_text
                        else "",
                    ],
                    notes=[
                        (
                            f"Baseline drift: expected={baseline_tests_expected} "
                            f"recorded={baseline_recorded}"
                        ),
                        "Verify pytest and reconcile tracking text.",
                    ],
                    allowed_paths=[
                        "PROJECT_HANDSHAKE.md",
                        "PROJECT_ACTIVITY_LOG.md",
                        "PROGRESS.md",
                        "MASTER_INDEX.md",
                    ],
                )
            )
            packet_counter += 1

    if progress_text:
        if not _progress_has_active_or_gated_task(progress_text):
            drift_findings.append(
                "PROGRESS.md has no active, blocked, or approval-gated task marker; tracker may be stale."
            )
    else:
        drift_findings.append(
            "PROGRESS.md not found; tracker should exist per operator rule."
        )

    if handshake_text and master_index_text:
        for snippet in _candidate_runbook_references(handshake_text):
            basename = snippet.rsplit("/", 1)[-1] if snippet else ""
            if not basename:
                continue
            if basename not in master_index_text and snippet not in master_index_text:
                drift_findings.append(
                    f"handshake references {snippet!r} but MASTER_INDEX has no entry"
                )

    if drift_findings:
        packets.append(
            _emit_packet(
                packet_counter,
                scanned_at=scanned_at,
                trigger_class="project_drift_detected",
                severity="review",
                tenant_id=tenant_id,
                changed_paths=[str(p.relative_to(repo_root)) for p in (
                    handshake_path,
                    master_index_path,
                    activity_log_path,
                    progress_path,
                ) if p.exists()],
                notes=drift_findings,
                allowed_paths=[
                    "PROJECT_HANDSHAKE.md",
                    "PROJECT_ACTIVITY_LOG.md",
                    "PROGRESS.md",
                    "MASTER_INDEX.md",
                ],
            )
        )
        packet_counter += 1

    if not packets:
        packets.append(
            _emit_packet(
                packet_counter,
                scanned_at=scanned_at,
                trigger_class="scan_clean",
                severity="info",
                tenant_id=tenant_id,
                changed_paths=[],
                notes=[
                    "No drift or baseline mismatch detected.",
                    "Trigger emitted in info severity for observability.",
                ],
                allowed_paths=[],
            )
        )

    return ScanResult(
        scanned_at=scanned_at,
        repo_root=repo_root.resolve(),
        baseline_tests_expected=baseline_tests_expected,
        baseline_tests_recorded=baseline_recorded,
        packets=packets,
        drift_findings=drift_findings,
    )


def build_mission_envelope(
    packets: list[TriggerPacket],
    *,
    scanned_at: datetime,
) -> dict[str, Any]:
    """Build a one-hour training mission envelope from training packets.

    The envelope follows the §5 schema in
    ``Autonomous_Workflows/one-hour-agent-training-loop.md``. It is the
    operator-reviewable artifact that a human can approve before any
    actual one-hour training loop is started.
    """

    session_id = (
        "one_hour_training_"
        + scanned_at.strftime("%Y%m%d_%H%M")
    )
    allowed_paths: list[str] = []
    objectives: list[str] = []
    for packet in packets:
        objectives.append(
            f"[{packet.trigger_class}] " + "; ".join(packet.notes or [packet.trigger_class])
        )
        for path in packet.allowed_paths:
            if path and path not in allowed_paths:
                allowed_paths.append(path)
    return {
        "session_id": session_id,
        "mode": "training",
        "trigger_source": "autonomous_trigger",
        "objective": " | ".join(objectives) if objectives else "training loop",
        "allowed_paths": allowed_paths,
        "forbidden_paths": [
            "core/policy/",
            "core/production_state/gate.py",
            "core/production_state/tenant_overrides.py",
        ],
        "definition_of_done": [
            "Verify pytest summary if baseline changed.",
            "Reconcile tracking text (handshake / progress / activity log / index).",
            "Produce audit findings.",
            "Recommend operator actions; do not apply production changes.",
        ],
        "max_duration_minutes": 60,
        "requires_operator_approval_for": list(FORBIDDEN_AUTONOMOUS_ACTIONS) + [
            "closeout_status_change",
        ],
    }


def _emit_packet(
    counter: int,
    *,
    scanned_at: datetime,
    trigger_class: str,
    severity: TriggerSeverity,
    tenant_id: str,
    changed_paths: list[str],
    notes: list[str],
    allowed_paths: list[str],
) -> TriggerPacket:
    timestamp_id = scanned_at.strftime("%Y%m%d_%H%M%S")
    return TriggerPacket(
        trigger_id=f"trigger_{timestamp_id}_{counter:03d}",
        trigger_class=trigger_class,
        severity=severity,
        tenant_id=tenant_id,
        evidence_record_ids=[],
        changed_paths=[path for path in changed_paths if path],
        recommended_loop="one_hour_training" if severity in {"training", "urgent_review"} else "audit_summary",
        allowed_paths=allowed_paths,
        forbidden_actions=list(FORBIDDEN_AUTONOMOUS_ACTIONS),
        requires_operator_approval=True,
        notes=notes,
    )


def _read_text_safe(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _extract_baseline_count(*, sources: list[str]) -> int | None:
    """Pull the most-recent baseline test count from tracking text.

    Scans for patterns like ``443 tests passing`` or ``461 / 461 pytest``.
    Returns ``None`` if no match is found in any source.
    """

    for source in sources:
        if not source:
            continue
        match = _TRACKING_BASELINE_REGEX.search(source)
        if match:
            try:
                return int(match.group("count"))
            except (ValueError, IndexError):
                continue
    return None


def _progress_has_active_or_gated_task(progress_text: str) -> bool:
    lowered = progress_text.lower()
    return any(marker in lowered for marker in _ACCEPTED_PROGRESS_MARKERS)


def _candidate_runbook_references(handshake_text: str) -> list[str]:
    """Return runbook / readiness doc names mentioned in the handshake text.

    Used to spot a handshake-vs-index drift without parsing the whole file.
    """

    candidates: list[str] = []
    for token in re.findall(r"`([^`\n]+?\.md)`", handshake_text):
        token = token.strip()
        if "/" in token and token not in candidates:
            candidates.append(token)
    return candidates[:30]


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "FORBIDDEN_AUTONOMOUS_ACTIONS",
    "ScanResult",
    "TriggerPacket",
    "build_mission_envelope",
    "build_parser",
    "run",
    "scan",
]
