# Blackboard Data Model
Concept Draft

## Implementation Spec
See `python-blackboard-models.md` for the first Python/Pydantic implementation target Manus should build.

## Record Envelope
Every Blackboard record should use a consistent envelope.

```json
{
  "record_id": "uuid",
  "tenant_id": "tenant_or_sandbox_id",
  "environment": "production|sandbox",
  "record_type": "detection_result",
  "source_agent": "agent_id",
  "workflow_id": "workflow_id",
  "parent_record_id": "uuid_or_null",
  "hop_count": 0,
  "created_at": "iso8601",
  "schema_version": "v1",
  "payload": {},
  "audit": {
    "status": "pending|approved|rejected|quarantined",
    "auditor": "agent_or_human_id",
    "signed": false
  }
}
```

## Core Record Types
- `ingest_event`
- `detection_result`
- `risk_score`
- `workflow_trigger`
- `audit_verdict`
- `weakness_report`
- `synthetic_attack_case`
- `mutant_evaluation`
- `policy_update`

## Future Record Types
- `training_assignment`
- `draft_output`

## Environment Rules
- Production records may generate anonymized sandbox weakness reports.
- Sandbox records may generate policy update candidates.
- Sandbox records must not contain raw tenant data.
- Policy updates must be signed before production review.
