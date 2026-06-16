# MMI_DECISION_LOG.md — Official Decision History

**Authority:** Matt Nichol — authorized June 16 2026

Every important decision is recorded here with its evidence. This is the project's decision memory.

---

## Decision record template

```
Decision ID:
Date:
Component:
Input evidence:
Decision:
Reason:
Risks:
Required follow-up:
Approved by:
```

---

## Decision log

```
MMI-DEC-001 | 2026-06-16 | #100 ReconciliationAgent Adversarial | audit_outputs/reconciliation_agent_adversarial_20260615T030712Z.md blocking=0 warnings=1 (LungState patch — previously accepted) | ACCEPT | Evidence complete, warning already reviewed and accepted | None | None | Matt Nichol

MMI-DEC-002 | 2026-06-16 | #101 BRC Adversarial | audit_outputs/blast_radius_controller_adversarial_runtime_20260615T051019Z.md + gate_scope + tests — all blocking=0 warnings=0 | ACCEPT | Three clean Grok audits, all 47 BRC-ADV IDs covered | None | None | Matt Nichol

MMI-DEC-003 | 2026-06-16 | Runtime Instrumentation | audit_outputs/runtime_instrumentation_20260615T034659Z.md blocking=0 warnings=0 20 files reviewed | ACCEPT | Clean Grok audit across all touched files | None | None | Matt Nichol

MMI-DEC-004 | 2026-06-16 | #99 Mode Controller Adversarial | audit_outputs/mode_controller_adversarial_gate_scope_20260615T021703Z.md blocking=2 warnings=1 | REVISE | Gate scope has manifest coverage gap and path mismatch — re-run required | Gate scope re-run with correct manifest | None | Pending Matt

MMI-DEC-005 | 2026-06-16 | #102 Safe-Stop Adversarial | audit_outputs/safe_stop_adversarial_gate_scope_20260616T022942Z.md blocking=2 warnings=1 | REVISE | Gate scope manifest omits touched files — re-run required | Gate scope re-run with correct manifest | None | Pending Matt
```
