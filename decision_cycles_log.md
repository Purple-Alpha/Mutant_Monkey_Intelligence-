# Decision Cycles Log

Dedicated persistence surface for the **Next-Action Decision Rubric** (`4. Product_Roadmap/Next_Action_Decision_Rubric_Deep_Dive.md`, §11 SIGNED 2026-06-04). This artifact exists per locked decision **D15** (Q3 resolution) and is the Step 9 log target of the rubric's 10-step loop.

Each cycle records the Step 5 output (candidates + per-axis scores + totals), the operator-selected action (operator-decided, **not** rubric-ranked — D2 / failure mode vii), the pre-execution expected outcome (D7), the Step 8 audit verdict (PASS / PARTIAL / FAIL), and any surprises or mismatch notes (D6 calibration input).

**Calibration cadence (D16):** review mismatch entries at the 14-day Operating Doctrine retro, plus an earlier review whenever **≥3 consecutive PARTIAL or FAIL** verdicts occur.

A score is never a decision. The rubric ranks; Matt selects; reality audits.

## Entry schema

```
CYCLE <n> — <UTC timestamp>
  OBSERVE: <factual current state only>
  OPTIONS + SCORES (Leverage / Risk / Evidence / FutureCost / Reversibility, 0-2 each):
    ACTION 1   L_ R_ E_ FC_ Rv_   TOTAL _
    ACTION 2   L_ R_ E_ FC_ Rv_   TOTAL _
    (... 3-7 candidates; "do nothing" allowed, scored on the same axes per D19 ...)
  SELECTED:      ACTION N (operator-chosen, not rubric-ranked)
  EXPECTED:      <one-line expected outcome, captured BEFORE execution per D7>
  EXECUTED AT:   <timestamp>
  AUDIT VERDICT: PASS | PARTIAL | FAIL
  SURPRISES:     <free-text notes; empty if none>
```

---

CYCLE 1 — 2026-06-04T15:36Z
  OBSERVE: Next-Action Decision Rubric §11 SIGNED (uncommitted last night). Cyber Insurance
           generator Pass 1 committed + friction-free under §18.3; verification baseline green.
           Standing loose end: last night's signed slice (rubric, AGENTS guardrail, trackers,
           decision_cycles_log, SPARK) done + gate-clean but uncommitted. Parked: rename
           (Mutant Security, mutantsecurity.com available), private test-data store.
  OPTIONS + SCORES (Leverage / Risk / Evidence / FutureCost / Reversibility, 0-2 each):
    A Commit last night's signed slice (local)            L1 R2 E2 FC2 Rv2   TOTAL 9
    B Generator slice: package audit-packet assembly      L2 R1 E2 FC1 Rv2   TOTAL 8
    C Generator slice: done-declaration scaffolding        L2 R1 E1 FC1 Rv2   TOTAL 7
    D Draft private test-data store spec (MinIO/TrueNAS)   L2 R1 E1 FC1 Rv2   TOTAL 7
    E Name collision-smell pass (cyber-class scoped)       L1 R1 E1 FC1 Rv2   TOTAL 6
    F Do nothing / defer to queue                          L0 R0 E0 FC1 Rv2   TOTAL 3
  SELECTED:      ACTION B (operator-chosen, not rubric-ranked)
  EXPECTED:      Generator emits a durable, coverage-complete audit/audit_packet.json (+ chunked
                 contents) covering every read+written file from stages 1-7 with hashes and
                 contract refs, grok_submitted=false; manifest references it; gate 9 still passes;
                 new and existing focused tests stay green.
  EXECUTED AT:   2026-06-04T15:58Z
  AUDIT VERDICT: PASS
  SURPRISES:     (1) complete_gate HOOK_SCOPE_PREFIXES_ALWAYS does NOT include core/evidence_package/,
                 so --pre-commit mode would false-pass and normal mode audits the whole working tree
                 with no file scoping. Resolved by committing last night's already-clean slice first
                 (rubric candidate A, score 9), isolating today's code for a clean audit — A naturally
                 sequenced ahead of B. (2) Manifest relevant_contracts must be real, §11-signed file
                 paths; the §13-signed "what" deep-dive and VISION.md were rejected and removed.
                 Gate result: grok-4, 0 blocking / 0 warnings, comprehensive, packet 173,576 B
                 (audit_outputs/cyber_insurance_audit_packet_assembly_20260604T155835Z.md). Tests:
                 1095 passed, 1 skipped.

CYCLE 2 — 2026-06-04T16:56Z
  OBSERVE: Audit-packet slice done + committed (ec91074), gate-clean. Build loop now canonical
           (AGENTS §3.2); gate-scope hole fixed; STANDING commit cadence in force. Domain
           mutantmonkeysecurity.com registered (operator side). Tree clean; 6 commits local-only
           ahead of last push b18fa79. Baseline 1095 green.
  OPTIONS + SCORES (Leverage / Risk / Evidence / FutureCost / Reversibility, 0-2 each):
    A Done-declaration scaffolding (15 Done Criteria -> done_declaration.json)   L2 R1 E2 FC1 Rv2   TOTAL 8
    B Scope rebrand via Consequence Matrix (NorthStar -> Mutant Monkey Security) L1 R2 E2 FC1 Rv2   TOTAL 8
    D Push 6 local commits to remote/backup                                       L1 R2 E2 FC2 Rv1   TOTAL 8
    C Draft private test-data store spec (MinIO/TrueNAS)                          L2 R1 E1 FC1 Rv2   TOTAL 7
    E Wire stage 9 Grok package-audit                                             L2 R0 E0 FC1 Rv1   TOTAL 4 (boundary-blocked)
    F Do nothing / defer                                                          L0 R0 E0 FC1 Rv2   TOTAL 3
  SELECTED:      Operator set a full-day SEQUENCE: A -> B -> C -> D by 5pm, then E (Grok) as
                 capstone. E is gated on operator authorization to expand the signed Pass-1
                 boundary. This entry covers milestone A; B/C/D/E continue the same arc.
  EXPECTED (A):  Generator evaluates all 15 Done Criteria; Pass-1 package evaluates NOT done
                 (11/12/14/15 unmet), emits no done_declaration.json, records a done_evaluation
                 block in the manifest; gate clean; tests green.
  EXECUTED AT:   2026-06-04T17:22Z
  AUDIT VERDICT: PASS (A) — Grok gate clean 0/0, comprehensive
                 (audit_outputs/cyber_insurance_done_declaration_scaffolding_20260604T172209Z.md);
                 1105 passed, 1 skipped; auto-committed under STANDING (d75c3e7).
  SURPRISES:     None for A. Note: the loop ran clean this time — committing each slice as it
                 finished kept the tree isolated, so no mixed-tree dance was needed (the Cycle 1
                 surprise (1) is now structurally prevented by Fix B + STANDING).
