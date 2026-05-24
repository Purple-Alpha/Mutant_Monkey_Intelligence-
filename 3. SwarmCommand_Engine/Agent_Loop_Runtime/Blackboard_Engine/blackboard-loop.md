# Blackboard Loop
Shared Memory Engine

## Purpose
The Blackboard is the central nervous system of the swarm. It synchronizes agent work through append-only structured records, triggers, locks, and vector memory updates.

## Loop

```text
while True:
    accept writes from agents append-only
    fire triggers when layer data is complete
    lock rows during audits
    update vector memory with new patterns
```

## Properties
- Append-only
- Event-driven
- Lock-controlled
- Dual-layer: structured records and vector memory
- Immutable audit trail
- Tenant-aware

## Write Types
- Detection result
- Risk score
- Workflow trigger
- Draft output
- Audit verdict
- Weakness report
- Synthetic attack case
- Mutant evaluation
- Policy update

## Trigger Examples
- When detection result is complete, trigger scoring.
- When risk score exceeds threshold, trigger workflow planning.
- When report draft is complete, trigger audit.
- When confidence is low, trigger sandbox weakness report.
- When sandbox mutant is approved, trigger policy update review.

## Locking Rules
- Audit locks prevent edits during validation.
- Production records are immutable.
- Sandbox experiments must reference source weakness IDs.
- Promotion records require signed approval.
