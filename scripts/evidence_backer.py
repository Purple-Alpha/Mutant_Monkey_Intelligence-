#!/usr/bin/env python3
"""CLI for the read-only Evidence Backer verifier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = REPO_ROOT / "3. SwarmCommand_Engine" / "Agent_Loop_Runtime" / "Runtime_Implementation"
DEMO_DIR = RUNTIME_DIR / "demo_outputs" / "evidence_backer_cli_demo"
DEMO_TENANT_ID = "tenant_a"
DEMO_EMAIL_ID = "email_001"

sys.path.insert(0, str(RUNTIME_DIR))

from core.blackboard import (  # noqa: E402
    CanonicalEvidenceLedger,
    EvidenceBacker,
    EvidenceBackerVerdict,
    VerdictLedger,
)
from core.blackboard.models import Environment  # noqa: E402
from core.orchestrator.routes import blackboard_path  # noqa: E402


def _demo_paths() -> tuple[Path, Path, Path]:
    return (
        DEMO_DIR / "blackboard",
        DEMO_DIR / "evidence.jsonl",
        DEMO_DIR / "verdicts.jsonl",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only Evidence Backer verifier")
    parser.add_argument(
        "--demo",
        action="store_true",
        help=(
            "Use bundled demo fixture "
            f"({DEMO_TENANT_ID}/{DEMO_EMAIL_ID} under demo_outputs/evidence_backer_cli_demo)"
        ),
    )
    parser.add_argument("--tenant-id", default=None)
    parser.add_argument("--email-id", default=None)
    parser.add_argument("--blackboard-root", type=Path, default=None)
    parser.add_argument("--evidence-ledger", type=Path, default=None)
    parser.add_argument("--verdict-ledger", type=Path, default=None)
    parser.add_argument(
        "--decision-log",
        type=Path,
        default=REPO_ROOT / "mmi" / "MMI_DECISION_LOG.md",
    )
    parser.add_argument("--format", choices=("json", "text"), default="text")
    return parser.parse_args()


def _resolve_inputs(args: argparse.Namespace) -> tuple[str, str, Path, Path, Path]:
    if args.demo:
        tenant_id = DEMO_TENANT_ID
        email_id = DEMO_EMAIL_ID
        blackboard_root, evidence_path, verdict_path = _demo_paths()
    else:
        if not args.tenant_id or not args.email_id:
            raise SystemExit(
                "error: --tenant-id and --email-id are required unless --demo is set"
            )
        tenant_id = args.tenant_id
        email_id = args.email_id
        blackboard_root = args.blackboard_root or (DEMO_DIR / "blackboard")
        evidence_path = args.evidence_ledger or (DEMO_DIR / "evidence.jsonl")
        verdict_path = args.verdict_ledger or (DEMO_DIR / "verdicts.jsonl")
        if args.blackboard_root is None and args.evidence_ledger is None and args.verdict_ledger is None:
            print(
                "hint: no paths supplied; defaulting to demo_outputs/evidence_backer_cli_demo "
                f"({DEMO_TENANT_ID}/{DEMO_EMAIL_ID}). Use --demo explicitly or pass ledger paths.",
                file=sys.stderr,
            )
    return tenant_id, email_id, blackboard_root, evidence_path, verdict_path


def main() -> int:
    args = _parse_args()
    tenant_id, email_id, blackboard_root, evidence_path, verdict_path = _resolve_inputs(args)

    blackboard_paths: list[Path] = []
    for environment in Environment:
        candidate = blackboard_path(blackboard_root, environment, tenant_id)
        if candidate.exists():
            blackboard_paths.append(candidate)

    if args.format == "text":
        print(f"paths: blackboard_root={blackboard_root}", file=sys.stderr)
        print(f"paths: evidence_ledger={evidence_path}", file=sys.stderr)
        print(f"paths: verdict_ledger={verdict_path}", file=sys.stderr)
        if blackboard_paths:
            print(f"paths: blackboard_jsonl={blackboard_paths[0]}", file=sys.stderr)
        else:
            print("paths: blackboard_jsonl=(none found)", file=sys.stderr)

    backer = EvidenceBacker(
        blackboard_paths=blackboard_paths,
        evidence_ledger=CanonicalEvidenceLedger(evidence_path),
        verdict_ledger=VerdictLedger(verdict_path),
        decision_log_path=args.decision_log,
    )
    report = backer.verify(tenant_id=tenant_id, email_id=email_id)

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

        if report.verdict is EvidenceBackerVerdict.NOT_APPLICABLE:
            print(
                "\nhint: seed the bundled demo with "
                "`python3 scripts/seed_evidence_backer_demo.py` then run "
                "`python3 scripts/evidence_backer.py --demo`",
                file=sys.stderr,
            )

    return 0 if report.verdict is not EvidenceBackerVerdict.VIOLATION else 2


if __name__ == "__main__":
    raise SystemExit(main())
