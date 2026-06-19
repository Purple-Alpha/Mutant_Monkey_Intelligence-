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

> Reconciliation note (2026-06-16): DEC-004 and DEC-005 were originally seeded as REVISE from a pre-acceptance snapshot. They are now reconciled to the committed scoreboard, where the #99 and #102 gate-scope re-runs landed clean (0/0) and Matt accepted all four adversarial suites, granting the parent hardening claims (#92 / #84 / #89 / #94).

```
MMI-DEC-001 | 2026-06-16 | #100 ReconciliationAgent Adversarial | audit_outputs/reconciliation_agent_adversarial_20260615T030712Z.md blocking=0 warnings=1 (LungState patch — disclosed) | ACCEPT | Evidence complete, warning reviewed and accepted; ReconciliationAgent #84 marked ADVERSARIALLY HARDENED via this row | None | None | Matt Nichol

MMI-DEC-002 | 2026-06-16 | #101 BRC Adversarial | audit_outputs/blast_radius_controller_adversarial_runtime_20260615T051019Z.md + gate_scope + tests — all blocking=0 warnings=0 | ACCEPT | Three clean Grok audits, all 47 BRC-ADV IDs covered; Blast Radius Controller #89 marked ADVERSARIALLY HARDENED via this row | None | None | Matt Nichol

MMI-DEC-003 | 2026-06-16 | Runtime Instrumentation | audit_outputs/runtime_instrumentation_20260615T034659Z.md blocking=0 warnings=0 20 files reviewed | ACCEPT | Clean Grok audit across all touched files | None | None | Matt Nichol

MMI-DEC-004 | 2026-06-16 | #99 Mode Controller Adversarial | clean gate-scope re-run audit_outputs/mode_controller_adversarial_gate_scope_20260616T032356Z.md blocking=0 warnings=0 (earlier 20260615T021703Z attempt blocked on working-tree hygiene only) + test slice audit_outputs/mode_controller_adversarial_20260615T021608Z.md blocking=0 warnings=0 | ACCEPT | Gate-scope re-gated clean with corrected manifest; all 50 MC-ADV IDs covered; Mode Controller #92 marked ADVERSARIALLY HARDENED via this row | None | None | Matt Nichol

MMI-DEC-005 | 2026-06-16 | #102 Safe-Stop Adversarial | clean gate-scope audit_outputs/safe_stop_adversarial_gate_scope_20260616T023345Z.md blocking=0 warnings=0 (earlier 20260616T022942Z attempt blocked on manifest coverage only) + test slice audit_outputs/safe_stop_adversarial_tests_20260616T023420Z.md blocking=0 warnings=0 | ACCEPT | Gate-scope re-gated clean; all 97 SS-ADV IDs covered; Safe-Stop State Machine #94 marked ADVERSARIALLY HARDENED via this row | None | None | Matt Nichol

MMI-DEC-006 | 2026-06-18 | MMI delegation restore | scripts/mmi_dispatch.py collect_delegation_tasks + MODE:DELEGATE; tests/test_mmi_dispatch_routing.py | ACCEPT | Passive ALL_CLEAR ("Matt names next target") replaced with evidence-scored delegation; TID reclassified EXTERNAL_LANE; worker-completion MMI-first rule documented | Stale handoff prose may lag until next session sync | Run mmi_dispatch.py --sync after commit | Matt Nichol (authorize patch)
```
