# MMI Recovery Proof Requirements

**Status:** HARD CONTROL — documentation only  
**Date:** 2026-07-04  
**Related:** RR-M4-009, Ceiling 5, AGI Pillar 3

**Forbidden claims:** "survival is enough," "recovery is implied by uptime."

---

## Thesis

A system that only survives is **less mature** than one that proves **safe failure, evidence preservation, and refusal to promote after unresolved failure**. Recovery must be first-class — not deferred to post-M4.

---

## Minimum recovery proofs (required before Ceiling 5 claims)

| ID | Proof | Falsifier |
| -- | ----- | --------- |
| RP-01 | Clone destruction after assault | Clone persists with hostile state |
| RP-02 | Boundary reset after breach attempt | Stale boundary rules remain |
| RP-03 | Credential rotation after incident | Compromised creds still trusted |
| RP-04 | Failed-run quarantine | Failed run continues without isolation |
| RP-05 | Rollback to known-good hash | Rollback incomplete or unverifiable |
| RP-06 | Evidence preserved after failure | Chain lost or truncated on failure |
| RP-07 | Dead-man trigger on boundary loss | Run continues without boundary |
| RP-08 | Post-failure no-promotion | Stage promoted after CRITICAL/BLOCKED |

---

## M4 ladder status

| Proof | §17 owner | Status |
| ----- | --------- | ------ |
| RP-01..RP-08 | Partially AGI Pillar 3; not fully wired to M4 exit gates | **OPEN** |

---

## Assurance row requirement

Any phase claiming "fail-closed" must list which recovery proofs it does **not** yet satisfy in residual risk.

**Not claimed:** recovery proven, self-healing safe, M4_MET.
