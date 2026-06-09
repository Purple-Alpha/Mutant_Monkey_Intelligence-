# Project Handshake
NorthStar + SwarmCommand Venture

```
═══════════════════════════════════════════════
CURRENT NEXT ACTION (as of edd44a6)
═══════════════════════════════════════════════
STATE: OPERATOR_LOCK (CYCLE 23 — #14 Payment Change Detection boundary contract DRAFTED, awaiting §11 signature)
TRACK: BREADTH
DEPTH GATE: CLOSED (real-data intake not open)

NEXT ACTION:
  BLOCKED ON §11 SIGNATURE — place Matt's signature on
  `4. Product_Roadmap/Payment_Change_Detection_Agent_Design_Contract_Deep_Dive.md`
  to authorize the Evidence Stage 1 (Synthetic) PaymentChangeDetectionAgent
  wrapper build + focused tests. No wrapper code lands until signed.

WHY LOCKED:
  Build Map BREADTH triage (CYCLE 23) found no remaining clean pure-detector
  wrap. #14 wraps the §11-signed `assess_financial_state_delta` detector, which
  mutates the per-tenant Vendor Baseline Store via check_signal -> ingest_signal
  (same stateful pattern as signed #31 PDF Fingerprint) — so it needs a boundary
  contract before it can become a governed agent. Draft gated clean 0/0 (edd44a6).

IF BLOCKED:
  Awaiting operator §11 signature only. #13/#16/#17/#20 remain stateful
  Vendor-Baseline/Financial-State-Ledger boundary candidates (separate contracts);
  #7/#15/#25/#37 remain RECLASSIFY; #32/#44 remain merged; depth gate CLOSED.

LAST UPDATED: edd44a6 2026-06-09
═══════════════════════════════════════════════
```

## Purpose
The "start here before doing work" file. Read it after `AGENTS.md` and `VISION.md`.
It tells a new session, in one screen: where we are now, the single next action, the
verification baseline, and what is uncommitted.

**HYGIENE RULE (added 2026-06-03 to stop new-chat drift):** keep this file SHORT and CURRENT.
"Current State" and "Current Next Step" are **REPLACED each session, never appended**. Superseded
detail moves to `PROJECT_HANDSHAKE_ARCHIVE_*.md`. If this file grows past ~one screen, rotate it.
The old append-style handshake (235 lines of stale "next step" bullets) is what caused new-chat
drift; do not recreate it.

## Current Active Build Track
Email fraud + inbox-layer MDR for SMBs via MSPs (Stage A). NorthStar Inbox Shield +
SwarmCommand Agent Loop Runtime + Fraud / Ransomware specialization.

## Current Development Surface
WSL2 Ubuntu at `/home/socialarchitect/northstar` (primary since 2026-06-01). The Windows path is
backup / reference only. If the two ever diverge, stop and reconcile by commit hash before editing.

## Verification Baseline
**1387 tests passing, 1 skipped, 4 xfailed** (verified 2026-06-08, after CYCLE 22 #11 Known-Good Contact `KnownGoodContactAgent` landed at Evidence Stage 1 Synthetic — first Layer 3 Verification agent; +20 from prior 1367 baseline) from
`3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation`.

## Current State (latest reconcile 2026-06-08)
- **LAYER 5 AGGREGATE CHALLENGE PASS + FIRST CHALLENGE AGENT LANDED (2026-06-08).** Section 2 of the signed Layer 5 Aggregate Challenge Pass spec is wired (`Agent.challenge()` now takes the aggregate `AgentContribution` tuple; the Commander invokes challenge agents once per case over the aggregate set). The first Layer 5 Challenge agent — the **Aggregate Corroboration Agent** — is §11-signed, built, gated clean, and committed at **Evidence Stage 1 (Synthetic)**: facts-only, not in `build_default_registry`, no production dispatch, no autonomy; three-class test suite (expected-pass / adversarial / known-gap xfail KG-001 + KG-002). Two governance rules added to `AGENTS.md`: **§2.1.1.B** operator sign-off scope, and **§3.1 rule 11 + §12 failure mode** banning "cheap" as a decision criterion (best-in-class only). Baseline 1247 / 1 skipped / 4 xfailed.
- **OPERATOR #1 TARGET (2026-06-07): the full 70-agent blue-team swarm.** Matt declared the complete 70-agent swarm (the ten-team / six-layer map in `agent_concepts/`) his number-one target — the terminal goal the rest of the project exists to reach, and **not to be reduced** ("we are not discussing less than"; not the 14-agent V1 subset, not a trimmed version). Nothing else is sacrificed to get there: the disciplined spec-first -> gate -> sign path continues unchanged, now aimed at the swarm, with the cyber-insurance / evidence / revenue work as the instrumental track that funds and proves the project on the way. **Next-session first action:** build the consolidated **70-agent swarm scoreboard** — one tracker listing all 70 agents with build status *verified against current code* (done / partial / not-started), dependency/build order, and a per-agent "done = a governed agent, not just a detector function" definition — reconciling the 70-agent SPARK (`agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md`) and the 6-layer Design Tree (`agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`) into that single scoreboard. The deliberate VISION.md top-level re-ranking wording is intentionally deferred to a fresh session (path-setting framing change, not a late-night edit).
- **Butterfly Hard-Stop ADOPTED (2026-06-07; Option A).** AGENTS.md gains **§7.1 Butterfly Hard-Stop Protocol**: on a path-setting (revenue / architecture / legal-insurance / trust / product-identity / signed-spec-substance / autonomy / projected-outcome) trigger, the agent STOPs the irreversible action, names the trigger, pre-scores options on the unmodified Next-Action Decision Rubric, drafts the Consequence Matrix unasked, and lists external questions; the stop lifts only when independent intel is in hand and Matt records the decision. `Consequence_Matrix_Process.md` flipped from opt-in to **mandatory-on-trigger** (§2/§3/§6). Guards: anti-paralysis (stop is on building not thinking; has a completion criterion) + anti-over-trigger (Bin-1 reversible work never trips it). "Product identity" defined. The decision was itself run through the protocol — two independent external overviews converged on A and confirmed the rubric axes (`leverage / risk_reduction / evidence_strength / future_cost / reversibility`); a reviewer's RICE/WSJF rescale was declined as calibration drift; the rubric was NOT modified. D9 plan got two lean review refinements (baseline source-version/immutability; §3 coverage precondition).
- **Environment (2026-06-06): git freeze cleared; Linux-native committed.** The git "freeze" (no-exit-status commands forcing manual relays) is dead — verified by running git directly in the Linux terminal. The Windows copy is now **cold-backup-only; editing it is abandoned.** Linux (`/home/socialarchitect/northstar`) is the sole development surface. The freeze is logged as environment friction (not a lane-structure failure) and is excluded from the 2026-06-09 lane-trial review. See `PROJECT_ACTIVITY_LOG.md` and `CURRENT_STATE_MAP.md` Development-surface entry.
- **Mutant Monkey package-auditor D9 calibration plan DRAFTED + §9 RESOLVED (2026-06-06; committed `581b7f3`, §9 resolution `add8938`).** `4. Product_Roadmap/Mutant_Monkey_Package_Auditor_D9_Calibration_Plan.md` operationalizes the D9 gate (brief §6 + controls D9): synthetic-only corpus (known-good / planted-defect / refuse), three conjunctive requirements, a six-row planted-defect catalog mapped to expected blocking findings + contract refs, a 100% conjunctive pass bar (false pass = dangerous miss), a calibration-run record schema, and re-calibration triggers. §9 resolved as a **lean-first / evidence-triggered hybrid** (§9.A): frozen `baseline_reference.json`, 15-20 hand-curated fixtures + evidence-driven expansion, exact-match hard failure (no diff engine), plaintext `audit_outputs/` artifact with `git_commit` + `baseline_sha256`. §9.B backstops: escaped-defect promotion + human-reviewable artifacts active; mutation testing deferred until the calibration runner exists. §9.C escalation triggers added. Synthetic/test only; no signed-spec edit, no infrastructure, no real data; a `calibration_pass` still needs controls D7 + substrate + explicit operator activation. Gate clean 0/0 (draft `..._012634Z.md`, §9 `..._022102Z.md`).
- **Agent Design Contract #10/#21 metadata retrofit COMPLETE (2026-06-06; committed `cc63fca`).** `Lookalike_Domain_Detector_Deep_Dive.md` (#10) and `Executive_Impersonation_Detector_Deep_Dive.md` (#21) now carry Agent Design Contract Wrapper blocks declaring layer, authority, Stage posture, two-pass role, Decision Evidence Record contribution, promotion/demotion, tests/audit dependencies, and Build Authorization boundaries. This was metadata-only under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0: detector contracts, scoring bands/floors, default-off posture, input surfaces, data-minimization rules, rubric linkage, code, runtime behavior, buyer-facing claims, and push state remain unchanged. Gate clean 0/0: `audit_outputs/agent_design_contract_retrofit_10_21_20260607_20260607T011044Z.md`.
- **Cyber Insurance Evidence Package deep-dive: §13 SIGNED** (Matt; operating entity name TBD, project rename parked) and **§13 buyer-brand boundary revision RE-SIGNED 2026-06-05** with Matt-authored wording: "Approved by Matt Nichol, Sovereign Operator." D1-D11 locked. **D10 is OVERRIDDEN, not met** — signed operator override; basis is ad-hoc confirmation signal, not validated market proof. The §2 required boundary statement now names **Mutant Monkey Inbox Shield** on buyer-facing package surfaces; "NorthStar Inbox Shield" remains the internal codename per rebrand Option B.
- **Cyber Insurance Evidence Package IMPLEMENTATION spec: §11 SIGNED 2026-06-03** by Matt Nichol (Zebra-Comit), authored in-chat and committed (`4308b22`). Build-layer §3-§16 locked (IQ1-IQ7 + §13 pins: Grok-4 / temp 0 / dedicated PDF toolchain / `vf-001`+legit pair). Signed-spec slice Grok audit is **clean: 0 blocking / 0 warnings** (`audit_outputs/cyber_insurance_section11_spec_signature_slice_20260603_20260604T001901Z.md`). Signing did not authorize code beyond the later operator-selected runner-first milestone.
- **§14 test-plan runner-first milestone: EXECUTED / PASS** (live `grok-4`, 2026-06-04T00:49Z). Evidence under `audit_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/`; `run_summary.md` and `verdict.json` show all seven §14.4 conditions passed, all nine §7 gates passed, and zero drift incidents. This is internal test evidence only, not buyer-facing output or D10 market proof.
- **Cyber Insurance gate library + generator Pass 1: COMMITTED** (Markdown-first, internal only). Gate library `db32cd5` (fresh Grok gate clean); generator + CLI `ff0f41e` via `complete_gate.py --operator-override` (the §11-signed implementation spec is a no-code document; Matt explicitly authorized generator Pass-1 start-build, internal scope, 2026-06-04 — recorded in `PROJECT_ACTIVITY_LOG.md`; warning-level drift incident logged). `core/evidence_package/` gate/generator surface + `scripts/cyber_insurance_package_generate.py` produce a deterministic Markdown bundle under `audit_outputs/cyber_insurance_packages/` from the §14 artifacts. Focused tests: **16 passed**; live CLI all nine gates passed. No PDF, no Grok package audit, no package done declaration, no buyer-facing release.
- **Wave 3.1 score-sheet review ledger helper:** implemented, Grok-clean, committed (`audit_tools/review_ledger.py` + scanner + hook + tests).
- **Doc rotation done (2026-06-03):** `PROJECT_ACTIVITY_LOG.md`, `PROGRESS.md`, `MASTER_INDEX.md`, and this handshake were trimmed to active heads with verbatim archives, to fit the audit-gate packet cap (200KB / 50KB per file).
- **AGENTS.md §3.1 Decision Presentation Rule added:** decisions arrive pre-scored (ranking, why, consequence, recommended default) routed through the existing rubric engines; no bare unscored menus.
- **Project rename away from "NorthStar": PARKED.** Collisions found (Zebra, Axion, cyan AG, etc.); no name chosen; needs a real USPTO + registrar clearance pass.

- **Cyber Insurance implementation spec §18 amendment: SIGNED 2026-06-04** (Matt, Zebra-Comit; committed `3aec44b`; pre+post-signature gate audits clean). Declares `core/evidence_package/` the authorized generator code home; in-scope generator code now commits clean through the gate with **no `--operator-override` and no per-commit signature**. Operator signature is required only for §18.4 architectural changes (locked decisions, boundary, scope, external claims). The independent Grok audit stays in force.

- **Next-Action Decision Rubric: §11 SIGNED 2026-06-04** (Matt, Zebra-Comet). All 7 §10 questions locked as D13–D19; gate audit clean (grok-4, 0 blocking / 0 warnings, `audit_outputs/next_action_decision_rubric_signoff_20260604T062334Z.md`). `decision_cycles_log.md` created (D15). The rubric is now the live tactical decision engine: it ranks candidates on 5 axes; Matt selects; cycles log to `decision_cycles_log.md`.
- **AGENTS.md decision-calibration guardrail added 2026-06-04:** §3.1.2 now grades escalation by substance + reversibility (not "touches a signed file"); §3.1.8 + §12 "trivia-escalation / decision-inversion" failure mode added. Fixes the inversion of heavy-guardrailing trivia (e.g. an internal name change) while dumping real decisions raw.

## Current Next Step — TODAY'S MILESTONE LIST (persisted; READ this, don't ask)
**This list is the answer to "what's next." It lives here on disk, not in chat, and is regenerated at the end of every build cycle so the question never has to be re-asked.** **Candidate source:** `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (Build Sequencer header + actionable-now rows). **Engine:** the §11-signed Next-Action Decision Rubric (D13-rev §12 SIGNED 2026-06-08 — LIVE). Scored 0-2 per axis, max 10. The rubric ranks; **Matt selects** (D2). Queue is **retired** (historical only).

**OBSERVE (true current state):** #1 target = the full 70-agent governed swarm (not reducible). Spine built + gated: DER/shared interface, Stage A Commander case loop, Layer 5 *aggregate* challenge pass (Section 2 rewire), and 4 detector agents promoted to `GOVERNED_AGENT` at Evidence Stage 1 Synthetic (#6 Header, #6A Email Auth, #8 Ghost Thread, #10 Lookalike). Newest slice: the first Layer 5 *Challenge* agent — the Aggregate Corroboration Agent — built/gated/committed at Evidence Stage 1. Baseline 1247 / 1 skipped / 4 xfailed.

**Critical-path truth (the map must keep this visible):** TWO axes. (1) *Breadth* — wrapping detector functions into governed agents at Stage 1 — is **UNBLOCKED**; it is the live runway toward "70 governed agents" (~26 detector functions exist as candidates; ~22 are net-new). (2) *Depth* — maturing any agent past Evidence Stage 1 (Stage 2 Supervised / Stage 3 Production) — needs **real-data intake**, gated behind the signed-but-unstarted Production Evidence Store + real-data controls + a separate operator authorization. Stage B autonomy agents (e.g. #38 Containment) are gated behind a separate signed Stage B authorization. Breadth moves now; depth is a butterfly/operator decision.

**Ranked candidates (rubric output — Matt picks one; selection logs to `decision_cycles_log.md` per D15):**

```
ACTION A — Wrap the next existing detector into a governed agent (Stage 1, synthetic) via the proven
           analyze->contribution->challenge path (candidates: #7 Sender Identity, #18 Callback
           Verification, #27 Link Inspection, #30 Attachment Risk)
  Leverage:      1
  Risk:          1
  Evidence:      2
  Future Cost:   1
  Reversibility: 2
  TOTAL:         7

ACTION B — Build the second Layer 5 Challenge agent (cross-arbitration between challenge agents;
           closes the Aggregate Corroboration Agent's KG-002 known-gap xfail)
  Leverage:      1
  Risk:          1
  Evidence:      2
  Future Cost:   1
  Reversibility: 2
  TOTAL:         7

ACTION C — Build the dictating "what's next" map: elevate the 70-agent scoreboard into a
           dependency-aware, self-maintaining critical-path engine that every slice updates, so
           "what's next" is always READ here, never asked (governance design -> routes to Claude
           per AGENTS §2.1.2)
  Leverage:      2
  Risk:          2
  Evidence:      2
  Future Cost:   2
  Reversibility: 2
  TOTAL:         10

ACTION D — Open the real-data intake path (unblocks ALL Evidence Stage 2+ promotions; butterfly /
           operator-authority; gated behind Production Evidence Store infra + controls activation)
  Leverage:      2
  Risk:          0
  Evidence:      1
  Future Cost:   0
  Reversibility: 0
  TOTAL:         3

ACTION E — Do nothing this cycle (reference baseline)
  Leverage:      0
  Risk:          1
  Evidence:      0
  Future Cost:   1
  Reversibility: 2
  TOTAL:         4
```

SELECTED: **ACTION C** (Matt, 2026-06-08) — **COMPLETE.** Option B adopted and LIVE: queue retired; scoreboard = Build Sequencer; rubric D13-rev §12 SIGNED 2026-06-08 ("Matt Nichol June 8th 2026"). Build Loop Steps 0.5/6.5 in force.

SELECTED NEXT: **CYCLE 15 — #24 MFA Manipulation COMPLETE for Evidence Stage 1** (Build Sequencer clean-breadth path; rubric 10, 2026-06-08). Matt §11-signed the contract ("Matt Nichol June 8th 2026", commit `fec6ee7`); built `MFAManipulationAgent` (`core/orchestrator/mfa_manipulation_agent.py`, commit `09c5425`) wrapping immutable pure `score_mfa_fatigue` — facts-only closed indicators (`mfa_push_language`, `verification_code_language`) from body_plain/body_html/subject, no score/raw-code leakage, not in default registry. 18 focused tests cover all 14 §6 requirements. #24 is now `GOVERNED_AGENT` at Evidence Stage 1; breadth runway **8**. Runtime baseline **1310 passing** (1292 + 18). **No lock open.** Next clean pure-detector breadth candidate per the Build Sequencer: **#25 Session Theft** (`prompt_injection_detector.py`); #31 PDF Fingerprint and #11 Known-Good Contact remain stateful/Layer-3 boundary-contract problems; or a Stage 2 promotion for #23/#24/#27/#30 once ≥3 real samples + a signed promotion record exist.

**Operator scheduling is NOT an agent agenda item (per AGENTS §3, 2026-06-07).** Do not raise, prep for, or re-surface any of Matt's appointments/meetings unless Matt raises it first. The anchor card at `1. Business_Operations/Client_Documents/Todd_Tuesday_MSP_Call_Anchor_Card.md` exists as Matt's own personal notes; it is finished and is not a build deliverable.

**Standing #1 build target: the full 70-agent swarm** (see the #1-target bullet in Current State) — the terminal goal the rest of the project serves.

**70-agent scoreboard v1 BUILT (2026-06-07, committed `d832b3c`, updated through current spine slices):** `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` reconciles the SPARK 70-agent inventory + 6-layer Design Tree against the live runtime. Execution-lane verified status remains conservative: real code does not become `GOVERNED_AGENT` until the layer-specific promotion bar is cleared. The spine now has the DER/shared interface, Stage A Commander case loop, Header Divergence real-detector wrapper proof, Layer 5 challenge pass, and second-detector Ghost Thread wrapper proof. **#6 Header Analysis and #8 Ghost Thread are now `GOVERNED_AGENT` at Evidence Stage 1 (Synthetic) — both per-agent Agent Design Contracts were §11-signed 2026-06-07 (#6 `8f0a89f`, #8 `275475b`). #8 was renamed from "Reply-To Mismatch" to "Ghost Thread Agent" on the scoreboard (§10 Q1): Reply-To divergence is #6's signal; #8 detects fake thread continuity only.** No agent build is authorized by the scoreboard (Rule 4); the per-agent Rubric -> spec -> gate -> sign path still governs each promotion.

**Multi-model lane structure remains on a 3-day TRIAL (opened 2026-06-06, review 2026-06-09)** and the git-freeze relays are excluded as environment friction, not lane failure. The #10/#21 metadata-only retrofit is now complete. Next milestone options remaining from the current scored set: Local-AI audit substrate planning (spec-only; score 7), Mutant Monkey package-auditor D9 calibration plan (score 7), promote another swarm-map agent build slice (score 5), or stop/wrap (score 4). Pick exactly one next cycle; no code/build/runtime work is authorized by the retrofit.


**Agent Design Contract Template §11 SIGNED + BANKED (2026-06-06)** by Matt Nichol ("Matt Nichol June 6th 2026", placed verbatim). Spec: `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`. Turns the adopted 6-layer agentic evidence swarm into a required template for future promoted agents. §10.A locks defaults: enforce before §10 resolution; immediate metadata-only #10/#21 retrofit after sign-off; Stage A detectors default Level 3 Specialist; seven-field decision evidence record; promotion/demotion spec-only in v1; pure detectors may declare Pass 1 only until the Two-Pass spec signs; v2 design tree canonical / v1 map inventory-only. **Operator-directed hardening folded into the signed text:** §7.0 immutability boundary — the signed detector contract is immutable; a retrofit adds governance fields to a wrapper only and is NOT permission to touch detection logic; and Q7 settles the v1 map as inventory-only (not a competing design source, not to be relitigated). Gate clean 0/0 (`audit_outputs/Agent Design Contract Template §11 sign-off_20260606T220951Z.md`); committed as signed-spec slice `d5decc0`, followed by AGENTS/tracker/lane handoff slices through `be6d8df`. Pushed to GitHub + backup. The immediate #10/#21 metadata-only retrofit is now executed in `cc63fca`; no runtime enforcement, code, new agent behavior, default-on change, rubric change, or buyer-facing claim is authorized.

**Production Evidence Store §11 SIGNED + BANKED (2026-06-05).** §10.A locks all five questions (Q1 same host / isolated MinIO instance; Q2 per-tenant credentials day one; Q3 indefinite-until-explicit-delete for evidence-bearing classes; Q4 operator off-site media only; Q5 read-only-from-locked-machine + egress-deny v1). Committed in four gate-clean slices and pushed to GitHub + backup through `4145dc2`. Locks the contract only — no infrastructure, no real-customer-data handling, until a separate explicit start-build instruction.

**Session opening 2026-06-06:** set today's milestone list, then pick one. Recommended next: **Local-AI audit substrate planning (spec-only)** — advances the real-customer-data path (Dax/NorthStar local auditor per controls D6/D11) with no infrastructure and no real data. Alternatives: promote another swarm-map agent build slice; draft the Mutant Monkey package-auditor D9 calibration plan; §13/IQ3 revision prep. Todd/MSP parked until Tuesday.

**Real-customer-data controls remain signed but not operationally started:** controls spec §11 signed (`e77f85c`), D11 package-audit brief authored (`6026deb`), Lookalike Domain Detector build slice banked (`13f3cb1`/`0ceb582`). No real-customer-data handling, §13/IQ3 revision, local-AI substrate, production evidence store infrastructure, or buyer delivery starts without separate operator authorization. Todd/MSP motion parked until Tuesday by operator instruction.

## Commit Cadence (operator §4 decision, 2026-06-04; EXTENDED 2026-06-05)
**STANDING authorization in force, extended per operator instruction 2026-06-05.** Any gate-clean, fully-green slice is committed + logged automatically with no per-step prompt — this now covers in-scope code (`core/evidence_package/`) AND doc / log / spec-draft / matrix slices. Decisions chain (AGENTS §3.1.9, §3.2); the agent decides on ranked defaults and rolls forward. **Only these still stop and reach Matt, never auto-proceeding:** pushes to remote; §11/§13 sign-offs; scope / pricing / legal-trademark / external-identity changes; butterfly path-setting decisions; the seven VISION non-negotiables; and any change to the substance of a signed spec's locked decisions. Pushes are never inferred.

## Git State
Branch `safety/queue-drift-cleanup-20260528`. Local-only ahead of `github`/`backup` (both last known at `be6d8df`) by the handshake refresh, git-freeze decision slice, and #10/#21 retrofit slice; latest completed work before this tracker refresh is `cc63fca`. This is normal local-first state, not drift. The **git "freeze" is cleared** (verified 2026-06-06: `git status -sb` and `git log --oneline -3` run directly in the Linux terminal returned clean, exit code 0, no hang, no relay). Pushes remain explicit operator actions; use the Linux integrated terminal for authenticated GitHub pushes. STANDING governs gate-clean local commits; pushes remain explicit. Run `git status -sb` to confirm the live state at session start.

**Commit discipline (learned 2026-06-05 from an avoidable mess):** ALWAYS run `complete_gate.py` (or `--pre-commit` with only the intended slice staged) and see "clean" BEFORE `git commit` — never commit first and gate after. NEVER `git reset` past the last pushed commit (`git log --oneline -5` shows the `github/`+`backup/` ref; do not soft-reset below it). If a packet is `too_large` (200KB cap), split into smaller staged slices and gate each — do not commit the oversized packet anyway.

## Decision Routing (trial, 2026-06-05)
`DECISION_PROTOCOL.md` is in TRIAL (committed `6a83bfc`, not yet adopted into AGENTS.md authority). The agent operates under it now: Bin 1 (technical/reversible) = agent decides silently, never asks; Bin 2 (operator-authority/irreversible/money/identity/legal/real-data/buyer-delivery/butterfly/non-negotiable) = always reaches Matt with each option's positives, negatives, consequence, recommendation, and why-on-demand. Every session opens by setting a daily milestone list; every decision traces to it. The agent challenges any instruction (including Matt's) that collides with signed specs / the seven non-negotiables / forbidden language / butterfly triggers, before building. On any conflict AGENTS.md wins until Matt formally adopts the protocol.

## Required Files to Check Before Work
Follow the `AGENTS.md` §1 session-start read order first. Core governance files:
`MASTER_INDEX.md`, `PROJECT_HANDSHAKE.md`, `PROJECT_GUARDRAILS.md`, `PROJECT_ACTIVITY_LOG.md`,
`CURRENT_STATE_MAP.md`, `PROGRESS.md`, `PROJECT_BUILD_AND_AUDIT_QUEUE.md`.
(The exhaustive per-file checklist was archived 2026-06-03 to `PROJECT_HANDSHAKE_ARCHIVE_2026-06-03.md`;
use `MASTER_INDEX.md` as the live map of all artifacts.)

## Required Files to Update After Work
- `PROJECT_ACTIVITY_LOG.md` (new entry)
- `PROJECT_HANDSHAKE.md` — **replace** Current State + Current Next Step (do not append)
- `MASTER_INDEX.md` if a new major artifact is added

## Resume Rule
"Where do we keep going from?" -> read this file's **Current State** + **Current Next Step**,
then the latest `PROJECT_ACTIVITY_LOG.md` entry. That is the resume point.

## Current Owner
Matt

## Last Updated
2026-06-06 - D9 calibration plan §9 resolved as a lean-first / evidence-triggered hybrid and committed
`add8938` (frozen baseline_reference.json; 15-20 hand-curated fixtures; exact-match hard failure;
plaintext audit_outputs artifact; backstops with mutation testing deferred until the runner exists;
escalation triggers). Doc-only, synthetic-only; gate clean 0/0. No open §9 questions remain.

2026-06-06 - Mutant Monkey package-auditor D9 calibration plan drafted and committed `581b7f3`
(synthetic-only operational plan; operationalizes brief §6 + controls D9; no signed-spec edit, no infra,
no real data; gate clean 0/0).

2026-06-06 - #10/#21 Agent Design Contract metadata-only retrofit executed and committed `cc63fca`.
Lookalike Domain Detector and Executive Impersonation Detector now have wrapper governance fields only;
signed detector contracts and runtime behavior remain unchanged. Gate clean 0/0:
`audit_outputs/agent_design_contract_retrofit_10_21_20260607_20260607T011044Z.md`.

2026-06-06 - Git freeze cleared (verified by direct Linux terminal `git status -sb` + `git log --oneline -3`,
clean / exit 0). Linux-native commitment recorded; Windows copy demoted to cold-backup-only (editing abandoned).
Freeze logged as environment friction, excluded from the 2026-06-09 lane-trial review. Git State corrected to
show local `e9d9d95` `[ahead 1]` of `github`/`backup` (`be6d8df`); prior "both remotes resolve to be6d8df" text was stale.

2026-06-06 - 3-day lane-structure trial opened and banked through `be6d8df`: execution vs advisory
lanes, git-step rule, 4-phase Design -> Logic -> Audit -> Execute pipeline, away rule, and war-room
substrate parked. Trial review date: 2026-06-09. GitHub + backup both resolve to `be6d8df`.

2026-06-06 - Partner-lanes (model-strengths) contract added to `AGENTS.md` §2.1: Matt decides /
Grok audits / Codex builds / Claude designs+governs, each with strengths, guardrails, and lane, plus
shared cross-lane rules. Banked and pushed as part of the `be6d8df` remote-aligned state.

2026-06-06 - Agent Design Contract Template §11 SIGNED + BANKED by Matt Nichol at
`4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (with operator-directed §7.0 detector-contract
immutability boundary + Q7 v1-map-inventory-only confirmation folded into the signed text). Canonical design
adoption banked through `01e12ee`; signed-spec and tracker/lane slices banked through `be6d8df`. No code,
runtime enforcement, retrofits, or new agent behavior authorized.
