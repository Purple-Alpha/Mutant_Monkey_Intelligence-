"""Synthetic crucible harness — Phoenix / Iterative Crucible Mode v1."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.blackboard import (
    CanonicalEvidenceLedger,
    EvidenceBacker,
    EvidenceBackerVerdict,
    EvidenceLedgerEntry,
    EvidenceStage,
    EvidenceType,
    VerdictLedger,
)
from core.blackboard.evidence_backer import evidence_ref
from core.blackboard.mode_a_gate import RECONCILIATION_WRITER_AGENT_ID

from .failure_log import (
    CrucibleFailureLog,
    CrucibleFailureLogEntry,
    FailureClass,
    PhoenixAction,
)

SCENARIO_ORPHAN_VERDICT_REF = "orphan_verdict_ref"
SCENARIO_OMISSION_AS_SAFETY = "omission_as_safety"
SCENARIO_LEADER_SILENCE = "leader_silence_scenario"

SYNTHETIC_SCENARIOS = (
    SCENARIO_ORPHAN_VERDICT_REF,
    SCENARIO_OMISSION_AS_SAFETY,
    SCENARIO_LEADER_SILENCE,
)


@dataclass(frozen=True)
class ScenarioSpec:
    failure_class: FailureClass
    agents_involved: tuple[str, ...]
    governance_rule_id: str
    phoenix_action: PhoenixAction


SCENARIO_SPECS: dict[str, ScenarioSpec] = {
    SCENARIO_ORPHAN_VERDICT_REF: ScenarioSpec(
        failure_class=FailureClass.ORPHAN_VERDICT_REF,
        agents_involved=("reconciliation_agent_001", "header_analysis"),
        governance_rule_id="BM-D8",
        phoenix_action=PhoenixAction.SCHEMA_TIGHTEN,
    ),
    SCENARIO_OMISSION_AS_SAFETY: ScenarioSpec(
        failure_class=FailureClass.OMISSION_AS_SAFETY,
        agents_involved=("reconciliation_agent_001",),
        governance_rule_id="vector-1-omission-as-safety",
        phoenix_action=PhoenixAction.CONTRACT_AMEND,
    ),
    SCENARIO_LEADER_SILENCE: ScenarioSpec(
        failure_class=FailureClass.LEADER_SILENCE_SCENARIO,
        agents_involved=("swarm_commander_001", "mission_context_001"),
        governance_rule_id="BM-D7",
        phoenix_action=PhoenixAction.TEST_ADD,
    ),
}


class CrucibleHarness:
    """Run synthetic fault fixtures and record Evidence Backer discoveries."""

    def __init__(self, workspace: Path) -> None:
        self.workspace = Path(workspace)
        self.evidence_path = self.workspace / "evidence.jsonl"
        self.verdict_path = self.workspace / "verdicts.jsonl"

    def _seed_orphan_verdict_ref(self, tenant_id: str, email_id: str) -> None:
        evidence = CanonicalEvidenceLedger(self.evidence_path)
        verdict = VerdictLedger(self.verdict_path)
        written = evidence.append(
            EvidenceLedgerEntry(
                agent_id="header_analysis",
                tenant_id=tenant_id,
                email_id=email_id,
                evidence_type=EvidenceType.HEADER_SIGNAL,
                details={"signal": "synthetic_orphan_fixture"},
                confidence=0.7,
                stage=EvidenceStage.ES1,
            )
        )
        verdict.append(
            {
                "email_id": email_id,
                "tenant_id": tenant_id,
                "verdict": "LOW_RISK",
                "ensemble_outcome": "unanimous",
                "overall_confidence": 0.8,
                "r1_vote": "LOW_RISK",
                "r1_confidence": 0.8,
                "r2_vote": "LOW_RISK",
                "r2_confidence": 0.8,
                "r3_vote": "LOW_RISK",
                "r3_confidence": 0.8,
                "plain_english_chain": "synthetic orphan verdict reference fixture",
                "contributing_evidence": [
                    evidence_ref(written),
                    "header_signal:missing_agent:orphan",
                ],
            },
            writer_agent_id=RECONCILIATION_WRITER_AGENT_ID,
        )

    def _seed_omission_as_safety(self, tenant_id: str, email_id: str) -> None:
        evidence = CanonicalEvidenceLedger(self.evidence_path)
        verdict = VerdictLedger(self.verdict_path)
        written = evidence.append(
            EvidenceLedgerEntry(
                agent_id="header_analysis",
                tenant_id=tenant_id,
                email_id=email_id,
                evidence_type=EvidenceType.HEADER_SIGNAL,
                details={"signal": "sparse_fixture"},
                confidence=0.6,
                stage=EvidenceStage.ES1,
            )
        )
        verdict.append(
            {
                "email_id": email_id,
                "tenant_id": tenant_id,
                "verdict": "LOW_RISK",
                "ensemble_outcome": "unanimous",
                "overall_confidence": 0.8,
                "r1_vote": "LOW_RISK",
                "r1_confidence": 0.8,
                "r2_vote": "LOW_RISK",
                "r2_confidence": 0.8,
                "r3_vote": "LOW_RISK",
                "r3_confidence": 0.8,
                "plain_english_chain": "sparse evidence omission fixture",
                "contributing_evidence": [evidence_ref(written)],
            },
            writer_agent_id=RECONCILIATION_WRITER_AGENT_ID,
        )

    def _seed_leader_silence(self, tenant_id: str, email_id: str) -> None:
        # Synthetic scenario marker only — no production commander kill.
        _ = (tenant_id, email_id)

    def seed_scenario(self, scenario: str, *, tenant_id: str, email_id: str) -> None:
        if scenario == SCENARIO_ORPHAN_VERDICT_REF:
            self._seed_orphan_verdict_ref(tenant_id, email_id)
        elif scenario == SCENARIO_OMISSION_AS_SAFETY:
            self._seed_omission_as_safety(tenant_id, email_id)
        elif scenario == SCENARIO_LEADER_SILENCE:
            self._seed_leader_silence(tenant_id, email_id)
        else:
            raise ValueError(f"unknown crucible scenario: {scenario}")

    def run_scenario(
        self,
        scenario: str,
        *,
        tenant_id: str,
        email_id: str,
        failure_log: CrucibleFailureLog,
        decision_log_path: Path | None = None,
    ) -> CrucibleFailureLogEntry:
        if scenario not in SCENARIO_SPECS:
            raise ValueError(f"unknown crucible scenario: {scenario}")

        self.workspace.mkdir(parents=True, exist_ok=True)
        for path in (self.evidence_path, self.verdict_path):
            if path.exists():
                path.unlink()

        self.seed_scenario(scenario, tenant_id=tenant_id, email_id=email_id)
        spec = SCENARIO_SPECS[scenario]

        backer = EvidenceBacker(
            blackboard_paths=[],
            evidence_ledger=CanonicalEvidenceLedger(self.evidence_path),
            verdict_ledger=VerdictLedger(self.verdict_path),
            decision_log_path=decision_log_path,
        )
        report = backer.verify(tenant_id=tenant_id, email_id=email_id)

        if scenario == SCENARIO_LEADER_SILENCE and report.verdict is EvidenceBackerVerdict.NOT_APPLICABLE:
            report_verdict = EvidenceBackerVerdict.INCOMPLETE.value
            report_sha = report.report_sha256()
        else:
            report_verdict = report.verdict.value
            report_sha = report.report_sha256()

        if report.verdict is EvidenceBackerVerdict.PROVABLE and scenario != SCENARIO_LEADER_SILENCE:
            raise RuntimeError(
                f"scenario {scenario} expected non-PROVABLE Evidence Backer verdict, got PROVABLE"
            )

        entry = CrucibleFailureLogEntry(
            failure_class=spec.failure_class,
            agents_involved=list(spec.agents_involved),
            evidence_backer_report_sha=report_sha,
            governance_rule_id=spec.governance_rule_id,
            phoenix_action=spec.phoenix_action,
            tenant_id=tenant_id,
            email_id=email_id,
            evidence_backer_verdict=report_verdict,
        )
        return failure_log.append(entry)
