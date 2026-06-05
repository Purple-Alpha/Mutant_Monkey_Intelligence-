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

CYCLE 5 — 2026-06-04T19:30Z
  OBSERVE: Queue §4 named "PDF render surface review / decision (IQ2 supply-chain surface)" as the next
           item, deferred pending an explicit operator decision because IQ2 adds a new
           cross-platform supply-chain/dependency surface (butterfly candidate). Spec-first check:
           IQ2 is already RESOLVED in the §11-signed impl spec (line 326 = "dedicated pinned PDF
           dependency"); line 342 says the concrete engine pin is refinable without a deep-dive re-sign.
           Open part = which concrete engine + whether to build now. Baseline 1122.
  DECISION (operator-authority, pre-scored engine options; Det/Supply/Fit/X-plat/Rev, 0-2 each):
    ReportLab (pure-Python, pip-only)   2 2 2 2 1  TOTAL 9  <- recommended
    WeasyPrint (HTML/CSS->PDF)          1 0 2 1 1  TOTAL 5
    wkhtmltopdf (binary)                1 0 2 1 1  TOTAL 5
    Pandoc+LaTeX                        1 0 2 1 1  TOTAL 5
                 ReportLab wins the exact dimension IQ2 flagged: no system binaries -> smallest
                 supply-chain surface to pin/test/audit; deterministic; cross-platform by default.
  SELECTED:      ReportLab pinned + build the minimal internal/synthetic renderer now (operator chose
                 "reportlab_build"). Stays inside the no-buyer-delivery Pass-1 envelope.
  EXPECTED:      New pdf_renderer.py: deterministic (reportlab invariant) internal PDF from manifest +
                 records; boundary statement verbatim/prominent (HC8); rendered/pdf_render.json sidecar
                 with pinned engine identity+version (HC6) and pdf_sha256; engine-pin fail-closed;
                 NOT auto-wired into generation (explicit separate step, like stage 9); no buyer delivery.
                 requirements.txt pins reportlab==4.2.5 + transitive pillow/chardet.
  EXECUTED AT:   2026-06-04T19:37Z
  AUDIT VERDICT: PASS — Grok gate clean 0/0
                 (audit_outputs/cyber_insurance_pdf_render_surface_20260604T193751Z.md); 1128 passed,
                 1 skipped; committed under STANDING.
  SURPRISES:     None. Build-layer call (stated): renderer is a separate explicit render_package_pdf()
                 rather than folded into generate_package_from_test_plan, to keep generation
                 deterministic/offline and PDF an opt-in internal step.

CYCLE 6 — 2026-06-04T22:35Z
  OBSERVE: Operator refreshed (slept), asked "what's on the agenda today?" GitHub current at 16f75ef;
           Codex consolidating the agent folder in parallel (separate repo). Cyber Insurance generator
           stages 8/9/10 + criterion-14 signature + PDF renderer all built/proven, synthetic-only.
           Private Test-Data Store spec is pre-§11 with 7 open §10 questions. Baseline 1128 green.
  OPTIONS + SCORES (Leverage / Risk / Evidence / FutureCost / Reversibility, 0-2 each):
    A Generate full synthetic package end-to-end + render the sample PDF (openable)   L1 R1 E2 FC2 Rv2  TOTAL 8
    B Private Test-Data Store: resolve the 7 open questions toward §11                 L2 R2 E1 FC1 Rv2  TOTAL 8
    C Real-customer-data controls Consequence Matrix now                              L2 R2 E1 FC0 Rv2  TOTAL 7
    D Wrap for the day                                                                L0 R0 E0 FC1 Rv2  TOTAL 3
  SELECTED:      ACTION B (operator-chosen; A was the agent recommendation via momentum-bias tiebreak,
                 operator overrode to B). C scored FC0 because the locked-machine option depends on the
                 agent substrate Codex is mid-cleanup on — premature to run C now.
  EXPECTED:      Bring all 7 operator-only §10 questions pre-scored with recommended defaults; operator
                 accepts/overrides; record resolutions into the spec (leave §11 unsigned).
  EXECUTED AT:   2026-06-04T22:40Z
  OUTCOME:       Operator accepted the six recommended defaults (Q1->D9 WSL2-primary-now/NAS-later,
                 Q2->D10 single-node ~250GB, Q4->D11 packets-indefinite/corpora-90d, Q5->D12
                 local-first+explicit-sync, Q6->D13 OS-keychain+gitignored-secrets, Q7->D14
                 strictly-test/lab-forever). For Q3 (mesh/sovereignty crux) operator triggered a
                 Consequence Matrix -> _Private_Test_Data_Store_Q3_Mesh_Consequence_Matrix.md
                 (A Tailscale / B WireGuard / C Headscale); operator initially leaned A, then overrode
                 to Option B (self-hosted WireGuard, full sovereignty — own sandbox/keys, no third-party
                 control plane, accepts the learning curve), promoted to spec D15. That resolved the
                 LAST open §10 question -> all seven now D9-D15. Operator then authored the §11 signature
                 ("Matt Nichol (zebra-comet) June 5th, 2026"); gate run on the signed slice clean
                 (1 warning: a stale Tailscale reference in the handshake, fixed). §11 SIGNED;
                 start-build still requires a separate explicit operator instruction.
  AUDIT VERDICT: N/A — pre-§11 spec/doc edits only, no code; gate fires at §11 sign-off per the spec.
  SURPRISES:     None. Six of seven questions were low-risk/reversible enough to accept-all; only the
                 sovereignty tradeoff (Q3) warranted the matrix, matching the spec's own §10 Q3 flag.

CYCLE 7 — 2026-06-05T01:24Z
  OBSERVE: Buyer-brand boundary re-signed + committed (07d297c, 7a028dc); Gemini briefing committed
           (815431d). Tree clean; 3 commits local-only ahead of GitHub (creds blocked through agent),
           local backup remote durable through 815431d. Cyber Insurance pipeline (stages 8/9/10 +
           criterion-14 + PDF renderer) built/proven synthetic-only. Real-customer-data controls
           decision still gated. Baseline 1128 green.
  OPTIONS + SCORES (Leverage / Risk / Evidence / FutureCost / Reversibility, 0-2 each):
    A Real-customer-data controls Consequence Matrix + scope boundary   L2 R2 E2 FC1 Rv2  TOTAL 9
    B Synthetic package done-state proof via operator-signature mech     L1 R1 E2 FC2 Rv2  TOTAL 8
    C Push 3 local commits to GitHub backup                              L1 R2 E2 FC2 Rv1  TOTAL 8
    D Start-build Private Test-Data Store v0 (MinIO + WireGuard)         L2 R1 E2 FC0 Rv1  TOTAL 6
    E Buyer PDF delivery scope decision                                  L2 R1 E1 FC0 Rv1  TOTAL 5
    F Wrap / do nothing                                                  L0 R0 E0 FC1 Rv2  TOTAL 3
  SELECTED:      Operator sequenced C then A: back up first, then run the controls decision.
  EXPECTED:      C: 3 commits land off-site. A: butterfly decision surfaced via Consequence Matrix;
                 operator selects a real-customer-data control path; scope boundary recorded.
  EXECUTED AT:   2026-06-05T01:24Z
  AUDIT VERDICT: PARTIAL (C) — GitHub push still credential-blocked through the agent; local `backup`
                 remote made durable through 815431d instead (off-site GitHub push remains an explicit
                 operator terminal step). PASS (A) — matrix run; operator chose Option B (locked-machine
                 local AI for real packages; Grok synthetic/test only). Doc/decision slice; gate fires
                 at commit per the standing doc-slice cadence.
  SURPRISES:     Operator flagged a real process failure: too many recommend-then-ask stops across the
                 session (Gemini-commit ask, milestone ask, matrix-outcome ask in quick succession),
                 violating AGENTS §3.1.9 + §3.2 (decisions chain; only milestone + genuine forks reach
                 the operator). Correction: STANDING extended to auto-commit gate-clean doc/spec-draft
                 slices; agent decides + rolls forward on ranked defaults; stops only for push, §11/§13
                 sign-off, scope/pricing/legal/identity, butterfly path changes, and non-negotiables.

CYCLE 8 — 2026-06-05T04:10Z
  OBSERVE: One-hour "cleanup then path forward" session. Drift cleanup done first: PROGRESS baseline
           header corrected 1072->1128 (verified by full suite run), tonight's decision-protocol /
           swarm-map / agent_concepts work logged across trackers (committed c3ec656). Matt's 70-agent
           blue-team swarm map captured (93822dd) and OPERATOR-ADOPTED as the Stage B/C architecture map,
           moved into the new agent_concepts/ design-dump folder (48a5ce5). Tree clean; baseline 1128.
  OPTIONS + SCORES (Leverage / Risk / Evidence / FutureCost / Reversibility, 0-2 each):
    A Production Evidence Store §10 -> §11 (resolve Q1-Q5, sign)        L2 R1 E2 FC1 Rv2  TOTAL 8
    B Spec the first swarm-map agent (spec-first deep-dive)             L2 R1 E2 FC1 Rv2  TOTAL 8
    C Real MSP pilot motion (operator-led; D10 market proof)           L2 R2 E1 FC1 Rv1  TOTAL 7
    D D9 local-AI calibration protocol design (no substrate yet)       L1 R1 E1 FC1 Rv2  TOTAL 6
    E §13/IQ3 revision (butterfly; authorize local-AI for real pkgs)   L2 R0 E1 FC0 Rv1  TOTAL 4 (premature)
    F Wrap / do nothing                                                L0 R0 E0 FC1 Rv2  TOTAL 3
  SELECTED:      ACTION B (operator-chosen). Within B, agent build-layer call: Lookalike Domain Detector
                 (swarm map #10) — self-contained, deterministic, no new network/supply-chain surface,
                 strengthens Stage A sender analysis, pairs with the Vendor Baseline Store, evidence-
                 producing. Honest flag carried to operator: C (a real pilot) is the highest-leverage
                 move overall but is operator-authority, not an agent build.
  EXPECTED:      One pre-§11 spec-first deep-dive for the chosen detector following the detector-spec
                 template (§0-§5 + §10 open questions + §11 placeholder); no runtime code; bounded
                 against existing detectors; gate clean; indexed.
  EXECUTED AT:   2026-06-05T04:10Z
  AUDIT VERDICT: PASS — Grok gate clean 0/0
                 (audit_outputs/lookalike_domain_detector_spec_draft_20260605T040950Z.md); doc-only,
                 no test delta (1128/1); committed fe4c3bd under STANDING.
  SURPRISES:     Scope grounding (spec-first): the existing url_obfuscation_detector already does
                 punycode/homoglyph for BODY URLs, and header_divergence_detector covers auth/routing —
                 but no detector scores the SENDING/identity domain vs known-good domains, which an
                 attacker-owned look-alike passes cleanly. So #10 is genuinely net-new + complementary;
                 D4 locks reuse of the existing homoglyph machinery so the two cannot drift apart.
