# Python Blackboard Models
Implementation Spec for Manus

## Purpose
This file defines the first build target for the NorthStar Agent Loop Runtime: the Python data models that every agent, orchestrator, auditor, and future storage adapter will use when writing to the Blackboard.

## Recommended First Implementation
Use **Pydantic v2** models.

Reason:
- Runtime validation is built in.
- JSON serialization is straightforward.
- Enums make record types and permissions explicit.
- The models can later back SQLite, Postgres, event streams, or APIs.

## Build Order
1. Record enums
2. Audit model
3. Blackboard record envelope
4. Payload models for first record types
5. Agent registry models
6. Governance validation helpers
7. Append-only JSONL storage adapter

---

# 1. Record Enums

```python
from enum import Enum


class Environment(str, Enum):
    PRODUCTION = "production"
    SANDBOX = "sandbox"


class RecordType(str, Enum):
    INGEST_EVENT = "ingest_event"
    DETECTION_RESULT = "detection_result"
    RISK_SCORE = "risk_score"
    WORKFLOW_TRIGGER = "workflow_trigger"
    AUDIT_VERDICT = "audit_verdict"
    WEAKNESS_REPORT = "weakness_report"
    SYNTHETIC_ATTACK_CASE = "synthetic_attack_case"
    MUTANT_EVALUATION = "mutant_evaluation"
    POLICY_UPDATE = "policy_update"


class AuditStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    QUARANTINED = "quarantined"


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    DETECTION = "detection"
    SCORING = "scoring"
    WORKFLOW = "workflow"
    DRAFTING = "drafting"
    AUDIT = "audit"
    RED = "red"
    BLUE = "blue"
    GOVERNANCE = "governance"
```

---

# 2. Audit Model

```python
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class AuditMeta(BaseModel):
    status: AuditStatus = AuditStatus.PENDING
    auditor: str | None = None
    signed: bool = False
    signature_id: str | None = None
    reviewed_at: datetime | None = None
    notes: str | None = None
```

## Audit Rules
- New records start as `pending`.
- Quarantined records must not trigger downstream workflows.
- Policy updates require `signed = True` before production review.
- Production records are never edited after write.

---

# 3. Blackboard Record Envelope

```python
from typing import Any
from uuid import UUID, uuid4


class BlackboardRecord(BaseModel):
    record_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    environment: Environment
    record_type: RecordType
    source_agent: str
    workflow_id: str | None = None
    parent_record_id: UUID | None = None
    hop_count: int = Field(default=0, ge=0, le=10)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: str = "v1"
    payload: dict[str, Any]
    audit: AuditMeta = Field(default_factory=AuditMeta)
```

## Envelope Rules
- Every agent write must use this envelope.
- `tenant_id` is required, including sandbox tenants.
- `environment` must be either `production` or `sandbox`.
- `hop_count` cannot exceed 10.
- `payload` must later validate against the specific `record_type`.

---

# 4. First Payload Models

## Ingest Event

```python
class IngestEventPayload(BaseModel):
    source: str
    event_kind: str
    subject: str | None = None
    sender_domain: str | None = None
    received_at: datetime
    raw_ref: str | None = None
```

## Detection Result

```python
class DetectionResultPayload(BaseModel):
    detection_label: str
    confidence: float = Field(ge=0.0, le=1.0)
    signals: list[str] = Field(default_factory=list)
    explanation: str | None = None
```

## Risk Score

```python
class RiskScorePayload(BaseModel):
    score: int = Field(ge=0, le=100)
    risk_level: str
    factors: list[str] = Field(default_factory=list)
    recommended_action: str | None = None
```

## Workflow Trigger

```python
class WorkflowTriggerPayload(BaseModel):
    workflow_name: str
    reason: str
    priority: str = "normal"
    target_agent_role: AgentRole | None = None
```

## Audit Verdict

```python
class AuditVerdictPayload(BaseModel):
    target_record_id: UUID
    verdict: AuditStatus
    findings: list[str] = Field(default_factory=list)
    requires_human_review: bool = False
```

## Weakness Report

```python
class WeaknessReportPayload(BaseModel):
    weakness_kind: str
    anonymized_pattern: str
    confidence_gap: float = Field(ge=0.0, le=1.0)
    source_record_ids: list[UUID] = Field(default_factory=list)
    raw_tenant_data_removed: bool = True
```

## Synthetic Attack Case

```python
class SyntheticAttackCasePayload(BaseModel):
    attack_kind: str
    generated_from_weakness_id: UUID
    synthetic_subject: str
    synthetic_sender_domain: str
    expected_detection_signals: list[str] = Field(default_factory=list)
    raw_tenant_data_removed: bool = True
```

## Mutant Evaluation

```python
class MutantEvaluationPayload(BaseModel):
    baseline_agent_id: str
    candidate_agent_id: str | None = None
    source_attack_case_id: UUID
    blue_detected: bool
    baseline_confidence: float = Field(ge=0.0, le=1.0)
    failure_modes: list[str] = Field(default_factory=list)
    mutation_recommended: bool = False
```

## Policy Update

```python
class PolicyUpdatePayload(BaseModel):
    policy_name: str
    change_summary: str
    sandbox_evidence_ids: list[UUID] = Field(default_factory=list)
    rollout_scope: str = "manual_review"
    rollback_plan: str
```

---

# 5. Agent Registry Model

```python
class AgentRegistryEntry(BaseModel):
    agent_id: str
    display_name: str
    role: AgentRole
    allowed_environments: set[Environment]
    allowed_write_types: set[RecordType]
    can_mutate: bool = False
    can_access_production_data: bool = False
    max_hops: int = Field(default=10, ge=1, le=10)
```

## Registry Rules
- Red agents are sandbox-only.
- Mutation-capable agents are sandbox-only.
- Production agents cannot mutate.
- Agents can write only approved record types.
- Agents that access production data cannot write Red records.

## Example Registry Entries

```python
DETECTION_AGENT = AgentRegistryEntry(
    agent_id="blue_detection_001",
    display_name="Blue Detection Agent 001",
    role=AgentRole.DETECTION,
    allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
    allowed_write_types={RecordType.DETECTION_RESULT, RecordType.WEAKNESS_REPORT},
    can_mutate=False,
    can_access_production_data=True,
)

RED_AGENT = AgentRegistryEntry(
    agent_id="red_sandbox_001",
    display_name="Sandbox Red Agent 001",
    role=AgentRole.RED,
    allowed_environments={Environment.SANDBOX},
    allowed_write_types={RecordType.INGEST_EVENT},
    can_mutate=False,
    can_access_production_data=False,
)

GOVERNANCE_AGENT = AgentRegistryEntry(
    agent_id="governance_001",
    display_name="Governance Constitution Agent",
    role=AgentRole.GOVERNANCE,
    allowed_environments={Environment.PRODUCTION, Environment.SANDBOX},
    allowed_write_types={RecordType.AUDIT_VERDICT, RecordType.POLICY_UPDATE},
    can_mutate=False,
    can_access_production_data=True,
)
```

---

# 6. Governance Validation Helpers

## Required Checks
- Schema is valid.
- Agent exists in registry.
- Agent may write to target environment.
- Agent may write the requested record type.
- Hop count is less than or equal to 10.
- Red agents cannot write production records.
- Mutation-capable agents cannot operate in production.
- Policy updates must be sandbox-derived and signed before production review.
- Weakness reports must confirm tenant data was removed.

## Pseudocode

```python
def validate_record_against_registry(
    record: BlackboardRecord,
    agent: AgentRegistryEntry,
) -> None:
    if record.environment not in agent.allowed_environments:
        raise ValueError("Agent cannot write to this environment")

    if record.record_type not in agent.allowed_write_types:
        raise ValueError("Agent cannot write this record type")

    if agent.role == AgentRole.RED and record.environment == Environment.PRODUCTION:
        raise ValueError("Red agents cannot access production")

    if agent.can_mutate and record.environment == Environment.PRODUCTION:
        raise ValueError("Mutation is sandbox-only")

    if record.hop_count > agent.max_hops:
        raise ValueError("Hop count exceeded")
```

---

# 7. Append-Only Storage Model

## First Storage Choice
Start with JSONL.

Reason:
- Simple to inspect.
- Easy to append.
- Easy to replay.
- No database migration needed for the first prototype.

## File Layout

```text
/data/blackboard/
  production/
    tenant_a.jsonl
    tenant_b.jsonl
  sandbox/
    sandbox_default.jsonl
```

## Append Rule
Records are only appended. Existing lines are never edited.

## Write Pseudocode

```python
import json
from pathlib import Path


def append_record(path: Path, record: BlackboardRecord) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(record.model_dump_json() + "\n")
```

## Read Pseudocode

```python
def read_records(path: Path) -> list[BlackboardRecord]:
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(BlackboardRecord.model_validate_json(line))
    return records
```

## Future Storage Upgrade
Move to SQLite or Postgres after:
- Record types stabilize.
- Query needs are clear.
- Audit and replay requirements are tested.

---

# 8. Manus Implementation Checklist

- [ ] Create `core/blackboard/models.py`.
- [ ] Add enums.
- [ ] Add `AuditMeta`.
- [ ] Add `BlackboardRecord`.
- [ ] Add first payload models.
- [ ] Add `AgentRegistryEntry`.
- [ ] Add validation helper.
- [ ] Add JSONL append/read adapter.
- [ ] Add unit tests for valid writes.
- [ ] Add unit tests for rejected Red production writes.
- [ ] Add unit tests for rejected unauthorized record types.
- [ ] Add unit tests for hop count quarantine.
- [ ] Add sandbox loop tests for synthetic attack cases and mutant evaluations.

## Definition of Done
The first implementation is done when a test can:
1. Create a valid production detection record.
2. Append it to JSONL.
3. Read it back.
4. Reject a Red agent writing to production.
5. Reject a production mutation attempt.
6. Reject hop count greater than 10.
