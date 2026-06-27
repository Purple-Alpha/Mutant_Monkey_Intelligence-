"""Evidence Backer — read-only proof layer (Blackboard-Mesh BM-D6).

Graph walk: EMAIL_INBOUND → contributions → evidence entries → challenge
results (if any) → verdict (if any) → human DEC / gate SHA.

Never decides, never enacts, never promotes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .canonical_ledger import CanonicalEvidenceLedger, EvidenceLedgerEntry
from .models import AgentContributionPayload, BlackboardRecord, EmailInboundPayload, RecordType
from .storage import read_records
from .verdict_ledger import ReconciliationVerdict, Verdict, VerdictLedger


class EvidenceBackerVerdict(str, Enum):
    PROVABLE = "PROVABLE"
    INCOMPLETE = "INCOMPLETE"
    VIOLATION = "VIOLATION"
    NOT_APPLICABLE = "NOT_APPLICABLE"


def evidence_ref(entry: EvidenceLedgerEntry) -> str:
    return f"{entry.evidence_type.value}:{entry.agent_id}:{entry.email_id}"


@dataclass
class EvidenceBackerReport:
    tenant_id: str
    email_id: str
    verdict: EvidenceBackerVerdict
    findings: list[str] = field(default_factory=list)
    email_inbound_count: int = 0
    contribution_count: int = 0
    evidence_count: int = 0
    challenge_count: int = 0
    verdict_count: int = 0
    dec_record_found: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "email_id": self.email_id,
            "verdict": self.verdict.value,
            "findings": list(self.findings),
            "graph": {
                "email_inbound": self.email_inbound_count,
                "contributions": self.contribution_count,
                "evidence_entries": self.evidence_count,
                "challenge_results": self.challenge_count,
                "verdicts": self.verdict_count,
            },
            "dec_record_found": self.dec_record_found,
        }

    def report_sha256(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class EvidenceBacker:
    """Read-only verifier across blackboard JSONL + canonical ledgers."""

    def __init__(
        self,
        *,
        blackboard_paths: list[Path] | None = None,
        evidence_ledger: CanonicalEvidenceLedger | None = None,
        verdict_ledger: VerdictLedger | None = None,
        decision_log_path: Path | None = None,
    ) -> None:
        self._blackboard_paths = list(blackboard_paths or [])
        self._evidence_ledger = evidence_ledger
        self._verdict_ledger = verdict_ledger
        self._decision_log_path = decision_log_path

    def _read_blackboard_records(self, tenant_id: str) -> list[BlackboardRecord]:
        records: list[BlackboardRecord] = []
        for path in self._blackboard_paths:
            for record in read_records(path):
                if record.tenant_id == tenant_id:
                    records.append(record)
        return records

    def _contributions_for_case(
        self, records: list[BlackboardRecord], email_id: str
    ) -> list[tuple[BlackboardRecord, AgentContributionPayload]]:
        matched: list[tuple[BlackboardRecord, AgentContributionPayload]] = []
        for record in records:
            if record.record_type is not RecordType.AGENT_CONTRIBUTION:
                continue
            payload = AgentContributionPayload.model_validate(record.payload)
            digest_hit = email_id in payload.inputs_digest
            if digest_hit or email_id in json.dumps(record.payload):
                matched.append((record, payload))
        return matched

    def _email_inbound_records(
        self, records: list[BlackboardRecord], email_id: str
    ) -> list[BlackboardRecord]:
        inbound: list[BlackboardRecord] = []
        for record in records:
            if record.record_type is not RecordType.EMAIL_INBOUND:
                continue
            EmailInboundPayload.model_validate(record.payload)
            blob = json.dumps(record.payload)
            if email_id in blob or email_id in str(record.record_id):
                inbound.append(record)
        return inbound

    def _decision_log_text(self) -> str:
        if self._decision_log_path is None or not self._decision_log_path.exists():
            return ""
        return self._decision_log_path.read_text(encoding="utf-8")

    def _human_gate_required(self, verdict: ReconciliationVerdict | None) -> bool:
        if verdict is None:
            return False
        return (
            verdict.verdict in {Verdict.HIGH_RISK, Verdict.ESCALATE}
            or verdict.ensemble_outcome.value == "escalate"
            or verdict.lockdown_applied
            or verdict.delivery_problem_path
        )

    def verify(self, *, tenant_id: str, email_id: str) -> EvidenceBackerReport:
        findings: list[str] = []
        blackboard_records = self._read_blackboard_records(tenant_id)
        inbound = self._email_inbound_records(blackboard_records, email_id)
        contributions = self._contributions_for_case(blackboard_records, email_id)
        challenges = [
            payload
            for _, payload in contributions
            if payload.challenge_result is not None
        ]

        evidence_entries: list[EvidenceLedgerEntry] = []
        cross_tenant_evidence: list[EvidenceLedgerEntry] = []
        if self._evidence_ledger is not None:
            evidence_entries = [
                entry
                for entry in self._evidence_ledger.read_for_tenant(tenant_id)
                if entry.email_id == email_id
            ]
            if self._evidence_ledger.ledger_path.exists():
                with self._evidence_ledger.ledger_path.open("r", encoding="utf-8") as handle:
                    for line in handle:
                        if not line.strip():
                            continue
                        entry = EvidenceLedgerEntry.model_validate_json(line)
                        if entry.email_id == email_id and entry.tenant_id != tenant_id:
                            cross_tenant_evidence.append(entry)

        verdicts: list[ReconciliationVerdict] = []
        if self._verdict_ledger is not None:
            verdicts = [
                verdict
                for verdict in self._verdict_ledger.read_for_tenant(tenant_id)
                if verdict.email_id == email_id
            ]

        for record in blackboard_records:
            if record.tenant_id != tenant_id:
                findings.append(
                    f"cross-tenant leak: record {record.record_id} tenant={record.tenant_id}"
                )

        for entry in cross_tenant_evidence:
            findings.append(
                f"cross-tenant leak: evidence ref {evidence_ref(entry)} tenant={entry.tenant_id}"
            )

        evidence_refs = {evidence_ref(entry) for entry in evidence_entries}
        verdict = verdicts[-1] if verdicts else None

        if verdict is not None:
            for ref in verdict.contributing_evidence:
                if ref not in evidence_refs:
                    findings.append(f"orphan contributing_evidence ref: {ref}")

        dec_text = self._decision_log_text()
        dec_found = bool(email_id in dec_text) if dec_text else False
        if self._human_gate_required(verdict) and not dec_found:
            findings.append(
                "human gate required for verdict outcome but no DEC record references this case"
            )

        if (
            verdict is not None
            and verdict.verdict is Verdict.LOW_RISK
            and len(evidence_entries) <= 1
        ):
            findings.append(
                "omission-as-safety gap: sparse evidence with LOW_RISK verdict"
            )

        has_graph = bool(
            evidence_entries or verdicts or inbound or contributions or cross_tenant_evidence
        )

        report = EvidenceBackerReport(
            tenant_id=tenant_id,
            email_id=email_id,
            verdict=EvidenceBackerVerdict.PROVABLE,
            findings=findings,
            email_inbound_count=len(inbound),
            contribution_count=len(contributions),
            evidence_count=len(evidence_entries),
            challenge_count=len(challenges),
            verdict_count=len(verdicts),
            dec_record_found=dec_found,
        )

        if not has_graph:
            report.verdict = EvidenceBackerVerdict.NOT_APPLICABLE
            report.findings.append("no graph nodes found for tenant/email pair")
            return report

        if any("cross-tenant leak" in item for item in findings):
            report.verdict = EvidenceBackerVerdict.VIOLATION
        elif any(item.startswith("orphan contributing_evidence") for item in findings):
            report.verdict = EvidenceBackerVerdict.VIOLATION
        elif any("human gate required" in item for item in findings):
            report.verdict = EvidenceBackerVerdict.INCOMPLETE
        elif any("omission-as-safety gap" in item for item in findings):
            report.verdict = EvidenceBackerVerdict.INCOMPLETE
        else:
            report.verdict = EvidenceBackerVerdict.PROVABLE

        return report
