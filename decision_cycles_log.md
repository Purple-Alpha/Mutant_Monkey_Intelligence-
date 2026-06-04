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
  ----- continuation: milestones B/C/D/E of the same operator-set arc -----
  B (rebrand):   Flagged as a butterfly decision; ran the Consequence Matrix
                 (_Rebrand_to_Mutant_Monkey_Security_Consequence_Matrix.md). Operator chose Option B
                 (external brand + domain now; NorthStar/SwarmCommand stay internal codenames;
                 trademark clearance in parallel; deep rename deferred). Committed 729a964.
  C (test store):Drafted Private_Test_Data_Store_Deep_Dive.md (pre-§11, D1-D8, 7 open questions).
                 Committed 7cf4361.
  D (push):      Local backup remote durable (f59f54c). GitHub initially blocked (no creds in shell);
                 operator pushed from own terminal -> github b18fa79..f59f54c. Off-site durable.
  E (stage 9):   SURPRISE/correction: I mislabeled E as "blocked by a signed boundary." The §11-signed
                 impl spec §10 in fact REQUIRES the Grok audit (Done Criteria 11/12) — the deferral was
                 the operator's 2026-06-04 Pass-1 scope call, not a signed prohibition. Missed signal:
                 characterized a boundary without quoting the artifact. Rule that catches it: spec-first
                 (quote the signed text before labeling a constraint). Ran the Consequence Matrix
                 (_Stage9_Grok_Package_Audit_Consequence_Matrix.md); operator authorized Option B
                 conditioned on an honest on-the-merits assessment (it IS warranted — required stage).
                 Built package_auditor.py as a separate explicit injectable-client step; generation
                 untouched/offline. Grok gate CLEAN 0/0
                 (audit_outputs/cyber_insurance_stage9_package_auditor_20260604T175758Z.md); 1114
                 passed, 1 skipped; committed 264a340. Second gate surprise: the matrix doc was caught
                 as a manifest coverage gap (Pass-1-wiring-bug guard working) — added to the manifest
                 and re-ran clean.

CYCLE 3 — 2026-06-04T19:00Z
  OBSERVE: Day arc A-E complete + pushed off-site (github 7d4b3c1). Cyber Insurance generator has
           stages 8/9/10 wired (synthetic-only), each unit-tested in isolation but not yet proven to
           chain. Drift surfaced: uncommitted handshake git-state edit; stale queue §4 ("13 commits
           unpushed; do not push"). Baseline 1114 green.
  OPTIONS + SCORES (Leverage / Risk / Evidence / FutureCost / Reversibility, 0-2 each):
    C End-to-end pipeline integration test (8->9->10, synthetic, no network)   L1 R2 E2 FC2 Rv2  TOTAL 9
    A Criterion 14: operator package-signature mechanism                        L2 R1 E2 FC1 Rv2  TOTAL 8
    D Resolve 7 §10 questions in private test-data store spec, toward §11       L1 R1 E1 FC1 Rv2  TOTAL 6
    E Apply Option-B external brand to non-signed client-facing surfaces        L1 R1 E1 FC1 Rv2  TOTAL 6
    B PDF render surface (IQ2 supply-chain review needed first)                 L2 R0 E1 FC0 Rv1  TOTAL 4
    F Wrap / do nothing                                                         L0 R0 E0 FC1 Rv2  TOTAL 3
  SELECTED:      ACTION C (operator-chosen).
  EXPECTED:      One durable test exercising generation -> stage 8 packet -> stage 9 audit (fake clean
                 client) -> stage 10 done-eval; asserts not-done after generation (gaps 11/12/14/15),
                 stage 9 closes 11/12 with zero drift, still not-done without operator signature (14),
                 and signature + test-plan evidence flips to done + writes done_declaration.json.
  EXECUTED AT:   2026-06-04T19:08Z
  AUDIT VERDICT: PASS — Grok gate clean 0/0
                 (audit_outputs/cyber_insurance_pipeline_integration_20260604T190819Z.md); 1116 passed,
                 1 skipped; committed ab9846a under STANDING.
  SURPRISES:     None. Handshake git-state correction committed first (cef-style tracker hygiene) to
                 isolate the test slice for a clean gate; queue §4 refreshed in the same Log step.

CYCLE 4 — 2026-06-04T19:18Z
  OBSERVE: Queue §4 named criterion 14 (operator package-signature mechanism) as the next generator
           slice after Cycle 3. Generator stages 8/9/10 are wired and proven to chain; remaining
           "done" gap is a way to capture Matt-authored package sign-off as evidence. Baseline 1116.
  SELECTED:      Criterion 14 operator package-signature mechanism (operator direct instruction:
                 "alright lets do it").
  EXPECTED:      Build the mechanism only: record Matt-supplied wording + scope acknowledgment as a
                 signed_by_operator evidence record with timestamp and reviewed rendered artifact path;
                 no AI-authored sign-off text, no proxy signature. The evidence id satisfies criterion
                 14 when passed to the done evaluator; malformed/missing records fail closed.
  EXECUTED AT:   2026-06-04T19:20Z
  AUDIT VERDICT: PASS — Grok gate clean 0/0
                 (audit_outputs/cyber_insurance_operator_signature_mechanism_20260604T192050Z.md);
                 1122 passed, 1 skipped; committed a65babf under STANDING.
  SURPRISES:     None. Pipeline integration was updated to use the real signature mechanism instead of
                 a placeholder evidence id, keeping the end-to-end proof honest.
