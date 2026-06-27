#!/usr/bin/env python3
"""Seed bundled Evidence Backer CLI demo fixture (tenant_a / email_001)."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = REPO_ROOT / "3. SwarmCommand_Engine" / "Agent_Loop_Runtime" / "Runtime_Implementation"
sys.path.insert(0, str(RUNTIME_DIR))

from core.blackboard import (  # noqa: E402
    CanonicalEvidenceLedger,
    EvidenceLedgerEntry,
    EvidenceStage,
    EvidenceType,
    VerdictLedger,
)
from core.blackboard.evidence_backer import evidence_ref  # noqa: E402
from core.blackboard.mode_a_gate import RECONCILIATION_WRITER_AGENT_ID  # noqa: E402
from core.blackboard.models import (  # noqa: E402
    AgentContributionPayload,
    BlackboardRecord,
    EmailInboundPayload,
    Environment,
    RecordType,
)
from core.blackboard.storage import append_record  # noqa: E402
from core.orchestrator.routes import blackboard_path  # noqa: E402

DEMO_DIR = RUNTIME_DIR / "demo_outputs" / "evidence_backer_cli_demo"
TENANT_ID = "tenant_a"
EMAIL_ID = "email_001"
CASE_ID = UUID("11111111-2222-4333-8444-555555555501")


def main() -> None:
    blackboard_root = DEMO_DIR / "blackboard"
    evidence_path = DEMO_DIR / "evidence.jsonl"
    verdict_path = DEMO_DIR / "verdicts.jsonl"

    for path in (evidence_path, verdict_path):
        if path.exists():
            path.unlink()
    bb_path = blackboard_path(blackboard_root, Environment.PRODUCTION, TENANT_ID)
    if bb_path.exists():
        bb_path.unlink()

    evidence = CanonicalEvidenceLedger(evidence_path)
    verdict = VerdictLedger(verdict_path)

    first = evidence.append(
        EvidenceLedgerEntry(
            agent_id="header_analysis",
            tenant_id=TENANT_ID,
            email_id=EMAIL_ID,
            evidence_type=EvidenceType.HEADER_SIGNAL,
            details={"signal": "reply_to_mismatch"},
            confidence=0.72,
            stage=EvidenceStage.ES1,
        )
    )
    second = evidence.append(
        EvidenceLedgerEntry(
            agent_id="email_authentication",
            tenant_id=TENANT_ID,
            email_id=EMAIL_ID,
            evidence_type=EvidenceType.AUTHENTICATION_SIGNAL,
            details={"spf": "neutral"},
            confidence=0.65,
            stage=EvidenceStage.ES1,
        )
    )
    verdict.append(
        {
            "email_id": EMAIL_ID,
            "tenant_id": TENANT_ID,
            "verdict": "LOW_RISK",
            "ensemble_outcome": "unanimous",
            "overall_confidence": 0.8,
            "r1_vote": "LOW_RISK",
            "r1_confidence": 0.8,
            "r2_vote": "LOW_RISK",
            "r2_confidence": 0.8,
            "r3_vote": "LOW_RISK",
            "r3_confidence": 0.8,
            "plain_english_chain": "Two independent observation signals; no enactment language.",
            "contributing_evidence": [evidence_ref(first), evidence_ref(second)],
        },
        writer_agent_id=RECONCILIATION_WRITER_AGENT_ID,
    )

    append_record(
        bb_path,
        BlackboardRecord(
            tenant_id=TENANT_ID,
            environment=Environment.PRODUCTION,
            record_type=RecordType.EMAIL_INBOUND,
            source_agent="ingest_001",
            payload=EmailInboundPayload(
                received_at=datetime.now(timezone.utc),
                sender="payroll@example.com",
                recipient="hr@example.com",
                body_plain=f"synthetic inbound case {EMAIL_ID}",
            ).model_dump(mode="json"),
        ),
    )
    append_record(
        bb_path,
        BlackboardRecord(
            tenant_id=TENANT_ID,
            environment=Environment.PRODUCTION,
            record_type=RecordType.AGENT_CONTRIBUTION,
            source_agent="header_analysis",
            payload=AgentContributionPayload(
                case_id=CASE_ID,
                inputs_digest=f"digest-{EMAIL_ID}",
                agent_id="header_analysis",
                layer=2,
                observed_facts=["reply_to domain mismatch"],
            ).model_dump(mode="json"),
        ),
    )

    print(f"seeded {DEMO_DIR}")
    print(f"  blackboard: {bb_path}")
    print(f"  evidence:   {evidence_path}")
    print(f"  verdict:    {verdict_path}")
    print("run: python3 scripts/evidence_backer.py --demo")


if __name__ == "__main__":
    main()
