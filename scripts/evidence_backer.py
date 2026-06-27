#!/usr/bin/env python3
"""CLI for the read-only Evidence Backer verifier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = REPO_ROOT / "3. SwarmCommand_Engine" / "Agent_Loop_Runtime" / "Runtime_Implementation"
sys.path.insert(0, str(RUNTIME_DIR))

from core.blackboard import CanonicalEvidenceLedger, VerdictLedger  # noqa: E402
from core.blackboard.evidence_backer import EvidenceBacker  # noqa: E402
from core.blackboard.models import Environment  # noqa: E402
from core.orchestrator.routes import blackboard_path  # noqa: E402


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only Evidence Backer verifier")
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--email-id", required=True)
    parser.add_argument(
        "--blackboard-root",
        type=Path,
        default=RUNTIME_DIR / "demo_outputs" / "blackboard",
    )
    parser.add_argument(
        "--evidence-ledger",
        type=Path,
        default=None,
        help="Path to canonical evidence JSONL (default: <blackboard-root>/evidence.jsonl)",
    )
    parser.add_argument(
        "--verdict-ledger",
        type=Path,
        default=None,
        help="Path to verdict JSONL (default: <blackboard-root>/verdicts.jsonl)",
    )
    parser.add_argument(
        "--decision-log",
        type=Path,
        default=REPO_ROOT / "mmi" / "MMI_DECISION_LOG.md",
    )
    parser.add_argument("--format", choices=("json", "text"), default="text")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    blackboard_root: Path = args.blackboard_root
    evidence_path = args.evidence_ledger or (blackboard_root / "evidence.jsonl")
    verdict_path = args.verdict_ledger or (blackboard_root / "verdicts.jsonl")

    blackboard_paths: list[Path] = []
    for environment in Environment:
        candidate = blackboard_path(blackboard_root, environment, args.tenant_id)
        if candidate.exists():
            blackboard_paths.append(candidate)

    backer = EvidenceBacker(
        blackboard_paths=blackboard_paths,
        evidence_ledger=CanonicalEvidenceLedger(evidence_path),
        verdict_ledger=VerdictLedger(verdict_path),
        decision_log_path=args.decision_log,
    )
    report = backer.verify(tenant_id=args.tenant_id, email_id=args.email_id)

    if args.format == "json":
        payload = report.to_dict()
        payload["report_sha256"] = report.report_sha256()
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"Evidence Backer verdict: {report.verdict.value}")
        print(f"tenant_id: {report.tenant_id}")
        print(f"email_id: {report.email_id}")
        print(f"report_sha256: {report.report_sha256()}")
        print(
            "graph: "
            f"inbound={report.email_inbound_count} "
            f"contributions={report.contribution_count} "
            f"evidence={report.evidence_count} "
            f"challenges={report.challenge_count} "
            f"verdicts={report.verdict_count}"
        )
        if report.findings:
            print("findings:")
            for item in report.findings:
                print(f"  - {item}")

    return 0 if report.verdict is not EvidenceBackerVerdict.VIOLATION else 2


if __name__ == "__main__":
    raise SystemExit(main())
