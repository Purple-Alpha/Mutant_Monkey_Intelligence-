"""Crucible failure log — append-only synthetic discovery record (BM-D7)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field

from core.blackboard.models import StrictModel


class FailureClass(str, Enum):
    ORPHAN_VERDICT_REF = "orphan_verdict_ref"
    OMISSION_AS_SAFETY = "omission_as_safety"
    EVIDENCE_POISON = "evidence_poison"
    CROSS_TENANT_LEAK = "cross_tenant_leak"
    LEADER_SILENCE_SCENARIO = "leader_silence_scenario"


class PhoenixAction(str, Enum):
    CONTRACT_AMEND = "contract_amend"
    TEST_ADD = "test_add"
    SCHEMA_TIGHTEN = "schema_tighten"


class CrucibleFailureLogEntry(StrictModel):
    crucible_run_id: UUID = Field(default_factory=uuid4)
    failure_class: FailureClass
    agents_involved: list[str] = Field(default_factory=list)
    evidence_backer_report_sha: str = Field(min_length=64, max_length=64)
    governance_rule_id: str = Field(min_length=1)
    phoenix_action: PhoenixAction
    tenant_id: str = Field(min_length=1)
    email_id: str = Field(min_length=1)
    evidence_backer_verdict: str = Field(min_length=1)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CrucibleFailureLog:
    """Append-only JSONL log with optional markdown mirror."""

    def __init__(
        self,
        jsonl_path: Path,
        markdown_path: Path | None = None,
    ) -> None:
        self.jsonl_path = Path(jsonl_path)
        self.markdown_path = (
            Path(markdown_path)
            if markdown_path is not None
            else self.jsonl_path.with_suffix(".md")
        )

    def ensure_initialized(self) -> None:
        self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.markdown_path.exists():
            self.markdown_path.write_text(
                "# CRUCIBLE_FAILURE_LOG\n\n"
                "Append-only synthetic crucible failure discoveries "
                "(Iterative Crucible Mode / Phoenix).\n\n"
                f"Machine entries: `{self.jsonl_path.name}`\n\n",
                encoding="utf-8",
            )

    def append(self, entry: CrucibleFailureLogEntry) -> CrucibleFailureLogEntry:
        self.ensure_initialized()
        with self.jsonl_path.open("a", encoding="utf-8") as handle:
            handle.write(entry.model_dump_json() + "\n")
        with self.markdown_path.open("a", encoding="utf-8") as handle:
            handle.write(
                f"## {entry.crucible_run_id} — {entry.failure_class.value}\n\n"
                f"- recorded_at: {entry.recorded_at.isoformat()}\n"
                f"- tenant_id: {entry.tenant_id}\n"
                f"- email_id: {entry.email_id}\n"
                f"- agents_involved: {', '.join(entry.agents_involved)}\n"
                f"- evidence_backer_verdict: {entry.evidence_backer_verdict}\n"
                f"- evidence_backer_report_sha: `{entry.evidence_backer_report_sha}`\n"
                f"- governance_rule_id: {entry.governance_rule_id}\n"
                f"- phoenix_action: {entry.phoenix_action.value}\n\n"
            )
        return entry

    def read_all(self) -> list[CrucibleFailureLogEntry]:
        if not self.jsonl_path.exists():
            return []
        entries: list[CrucibleFailureLogEntry] = []
        with self.jsonl_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    entries.append(CrucibleFailureLogEntry.model_validate_json(line))
        return entries
