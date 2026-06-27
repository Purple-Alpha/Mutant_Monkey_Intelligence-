#!/usr/bin/env python3
"""CLI for synthetic crucible harness (Iterative Crucible Mode v1)."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = REPO_ROOT / "3. SwarmCommand_Engine" / "Agent_Loop_Runtime" / "Runtime_Implementation"
CRUCIBLE_DIR = REPO_ROOT / "mmi" / "crucible"
DEFAULT_LOG_JSONL = CRUCIBLE_DIR / "CRUCIBLE_FAILURE_LOG.jsonl"

sys.path.insert(0, str(RUNTIME_DIR))

from core.crucible import (  # noqa: E402
    SCENARIO_ORPHAN_VERDICT_REF,
    SYNTHETIC_SCENARIOS,
    CrucibleFailureLog,
    CrucibleHarness,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic crucible harness")
    parser.add_argument(
        "--scenario",
        choices=SYNTHETIC_SCENARIOS,
        default=SCENARIO_ORPHAN_VERDICT_REF,
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run default orphan_verdict_ref scenario into mmi/crucible log",
    )
    parser.add_argument("--tenant-id", default="tenant_crucible")
    parser.add_argument("--email-id", default="email_crucible_001")
    parser.add_argument("--failure-log", type=Path, default=DEFAULT_LOG_JSONL)
    parser.add_argument(
        "--decision-log",
        type=Path,
        default=REPO_ROOT / "mmi" / "MMI_DECISION_LOG.md",
    )
    parser.add_argument("--format", choices=("json", "text"), default="text")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    scenario = SCENARIO_ORPHAN_VERDICT_REF if args.demo else args.scenario
    tenant_id = "tenant_crucible" if args.demo else args.tenant_id
    email_id = "email_crucible_001" if args.demo else args.email_id
    log_path = DEFAULT_LOG_JSONL if args.demo else args.failure_log

    failure_log = CrucibleFailureLog(
        log_path,
        markdown_path=log_path.with_suffix(".md"),
    )

    with tempfile.TemporaryDirectory(prefix="crucible_") as tmp:
        harness = CrucibleHarness(Path(tmp))
        entry = harness.run_scenario(
            scenario,
            tenant_id=tenant_id,
            email_id=email_id,
            failure_log=failure_log,
            decision_log_path=args.decision_log,
        )

    if args.format == "json":
        print(json.dumps(entry.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        print(f"crucible_run_id: {entry.crucible_run_id}")
        print(f"failure_class: {entry.failure_class.value}")
        print(f"evidence_backer_report_sha: {entry.evidence_backer_report_sha}")
        print(f"evidence_backer_verdict: {entry.evidence_backer_verdict}")
        print(f"governance_rule_id: {entry.governance_rule_id}")
        print(f"phoenix_action: {entry.phoenix_action.value}")
        print(f"log_jsonl: {log_path}")
        print(f"log_markdown: {log_path.with_suffix('.md')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
