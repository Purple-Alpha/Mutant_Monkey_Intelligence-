MODE: AUDIT
AUTHORIZED_TASK: Run completion gate for Geo-Context
ASSIGNED_TO: completion gate auditor (complete_gate.py)
NEXT_PROMPT_GOES_TO: Cursor stages the build, runs the gate, then commits
OPERATOR_ACTION_REQUIRED: NO  (completion gate activation is standing; no per-run permission)
RUN: python3 audit_tools/complete_gate.py --pre-commit --task geo_context --claim "Geo-Context build implemented + tested; ready for audit"
MANIFEST: audit_outputs/pending/geo_context.manifest.json (MISSING - create before gate)
BLOCKED_UNTIL: complete_gate.py reports blocking=0 (0/0) AND build committed
NEXT_GATE: flip scoreboard row AWAITING_AUDIT -> GATED after clean audit + commit

AUTHORITY NOTE (2026-06-16): The routing block above is derived by scripts/mmi_dispatch.py
  and must remain as emitted. MODE: BUILD means the scoreboard has a visible SIGNED_UNBUILT
  next item (#103 first); it does NOT mean Matt has authorized Cursor to begin implementation.
  Matt must still explicitly name the build target. Rows #103/#104 state lifecycle tracking is
  not build authorization. `BUILD_AUTHORIZATION_IMPLIED` in the routing block is mechanical
  sequencer language, not operator build authorization. Current source-of-truth authority for
  component/gate status is mmi/MMI_GATE_REGISTRY.md and mmi/MMI_DECISION_LOG.md; consistency
  is verified by `python3 scripts/mmi_dispatch.py --verify`. Prose below is human context;
  anything marked SUPERSEDED is historical only and is NOT routing authority.

LAST_COMPLETED: #70 FinalReviewAgent ES1 build (MMI-DEC-248)
  (`core/orchestrator/final_review_agent.py`; `final_review_001`; FR-DER + FR-GOV;
  build `aa38ca3`; 15 focused tests; scoreboard #70 `AWAITING_AUDIT`;
  **not** GATED; **not** GOVERNED_AGENT; **not** production dispatch).

PRIOR_LAST_COMPLETED: #70 Final Review contract §11 + superintendent merge (MMI-DEC-244/247)
  (`4. Product_Roadmap/Final_Review_Agent_Design_Contract_Deep_Dive.md`; Matt Nichol June 26th 2026;
  scoreboard #70 `SIGNED_UNBUILT` / `NEEDS_BUILD_AUTH`; #10 promotion renumbered MMI-DEC-245;
  active task -> #43 Geo-Context research; **not** build authorization).

PRIOR_LAST_COMPLETED: #70 Final Review pre-build gate (MMI-DEC-243)
  (`4. Product_Roadmap/Final_Review_Agent_Design_Contract_Deep_Dive.md`; 0 blocking / 2 warnings;
  `logs/complete_gate_report.json`; Codex SIGNABLE; **not** §11 signed; **not** build authorization).

PRIOR_LAST_COMPLETED: #70 Final Review Slice B contract DRAFT placement (MMI-DEC-242)
  (`4. Product_Roadmap/Final_Review_Agent_Design_Contract_Deep_Dive.md`; Step 00 31/31;
  Slice A gates remain separate infra; FR-DER + FR-GOV modes; DRAFT pre-§11;
  **not** build authorization; **not** §11 signed).

PRIOR_LAST_COMPLETED: #70 Final Review boundary review (MMI-DEC-240)
  (`mmi/project_brain/status/final_review_70_boundary.md`; Slice A satisfied by
  `audit_tools/complete_gate.py` + `core/evidence_package/package_auditor.py`;
  Slice B unbuilt — `FINAL_REVIEW_AGENT_ID` schema hook only; scoreboard #70
  `NEEDS_BUILD_AUTH` -> `NEEDS_SIGNED_CONTRACT`; MMI-DEC-222 depth queue complete MMI-DEC-241;
  **not** build authorization; **not** §11; **not** production dispatch).

PRIOR_LAST_COMPLETED: #19 Dual-Approval GOVERNED_AGENT (MMI-DEC-238)
  (`core/workflows/vendor_payment_verification.py` + `core/orchestrator/dual_approval_agent.py`;
  MMI-DEC-234 build `0b78503`; 21 focused tests; completion gate 0 blocking / 1 warning —
  `audit_outputs/dual_approval_20260626T212610Z.md`; scoreboard #19 `AWAITING_AUDIT` -> `GATED`;
  **not GOVERNED_AGENT**; **not** production dispatch; **not** AUTH-5).

PRIOR_LAST_COMPLETED: VPV + #19 Dual-Approval §11 signatures (MMI-DEC-231/232)
  (`4. Product_Roadmap/Vendor_Payment_Verification_Workflow_Design_Contract_Deep_Dive.md`;
  `4. Product_Roadmap/Dual_Approval_Agent_Design_Contract_Deep_Dive.md`;
  Matt §11 signed `Matt Nichol June 25th 2026`;
  #19 scoreboard `SPEC_ONLY` -> `SIGNED_UNBUILT` / `NEEDS_BUILD_AUTH`;
  **not** build authorization; **not** GATED; **not** production dispatch; **not** AUTH-5).

PRIOR_LAST_COMPLETED: #19 Dual-Approval contract draft placement (MMI-DEC-224)
  (`4. Product_Roadmap/Dual_Approval_Agent_Design_Contract_Deep_Dive.md`;
  DRAFT pre-§11; #19 contract lane advanced from Claude draft placement to
  Codex pre-build gate review; **not** §11; **not** build authorization;
  **not** scoreboard lifecycle change; **not** production dispatch; **not**
  AUTH-5).

PRIOR: Matt selected project-brain target order (MMI-DEC-222)
  (`mmi/project_brain/status/active_task.md`;
  `mmi/project_brain/status/next_target_evidence.md`; selected order is #19
  Dual-Approval contract lane, then #66 Drift Watch re-triage, then #70 Final
  Review boundary/design; #43 Geo-Context held for more research/design; **not**
  build authorization; **not** §11; **not** scoreboard lifecycle change; **not**
  AUTH-5).

CURRENT_RESEARCH_BRANCH: Purple Translation Layer + Agentic Swarm Command Center
  + Adversarial Resilience Harness research/design captured
  (MMI-DEC-223 / MMI-DEC-226 / MMI-DEC-227)
  (`mmi/project_brain/architecture/purple_translation_layer.md`; Blue/Purple
  defensive-first; Unified Fact Schema draft; orchestrator/sub-agent research;
  lab-only breaker-harness concept; high-liability active response, deception,
  exploit, and scanning concepts parked behind separate legal/safety authority;
  related #43/#70; **not** build authorization; **not** active probing;
  **not** production dispatch; **not** AUTH-5).

PRIOR: Project brain next-target evidence reconciliation (MMI-DEC-221)
  (`mmi/project_brain/status/next_target_evidence.md`; reconciled dispatcher
  ALL_CLEAR, Estimator NO_BUILDABLE_CANDIDATES, scoreboard status, mission-map
  drift, and runtime evidence; recommended #19 Dual-Approval contract lane as
  strongest next target; **not** build authorization; **not** §11; **not**
  scoreboard lifecycle change; **not** AUTH-5).

PRIOR: Project brain milestone-aware operator routing restored (MMI-DEC-220)
  (`mmi/project_brain/`; `scripts/mmi_pm_voice.py`; `tests/test_mmi_pm_voice.py`;
  default PM Voice now surfaces the active milestone task over weak `1/10` backlog
  fallback when stronger project-brain evidence exists; advisory only; **not** build
  authorization; **not** scoreboard lifecycle change; **not** AUTH-5).

PRIOR: #50 Evidence Strength Mode A wrapper build (MMI-DEC-207)
  (Matt operator pick over #19/#21/#43 tie; Estimator 17.00; Layer 4 Evidence successor to #49;
  source `Email_Security_Testing_Evidence_Framework_Deep_Dive.md`; **not** §11; **not** build).

PRIOR: #50 Evidence Strength Gemini pre-build gate 0/0 (MMI-DEC-205)
  (contract `f1f0164`; Gemini pre-build gate 0/0; **not** build at sign).
  (§11 contract MMI-DEC-102; annex §6 wired MMI-DEC-122; 27 tests; completion gate
  0 blocking / 1 warning; breadth runway 16 -> 17; **not** production dispatch /
  **not** default registry).

PRIOR: #65 Correction Evidence GATED closeout (MMI-DEC-165/166)
  (`audit_outputs/correction_evidence_20260624T223220Z.md` 0 blocking / 1 warning;
  Gemini; **not GOVERNED_AGENT**).

PRIOR: #65 Correction Evidence build + AWAITING_AUDIT (MMI-DEC-163/164)
  (`CorrectionEvidenceAgent` wrapper + 19 tests).

PRIOR: Stage C c01 — Operator Lung Dial promotion gate (MMI-DEC-141 · PARK)
  (MMI-DEC-133 prerequisites not met; spec not promoted).

PRIOR: Stage B END — federation economics + mesh contract fork (MMI-DEC-140)
  (`mmi/research/MMI_BRAIN_IMMUNE_LUNG_PREREQ_AUDIT_MMI-DEC-133.md`;
  Lung production BLOCKED; tenant calibration + Playhouse + signed Load Multiplier
  contract remain open).

PRIOR: Stage A end — platform credibility closeout (MMI-DEC-130)
  (`mmi/research/MMI_STAGE_A_PLATFORM_CREDIBILITY_CLOSEOUT_MMI-DEC-130.md`;
  GATED stack + docs posture; Todd intake historical — not end gate;
  re-staged to Stage B federation-first per MMI-DEC-135).

PRIOR: Mission map re-stage — federation-first Stage B (MMI-DEC-135)
  (`mmi/research/MMI_MESH_HARDENING_RESEARCH_CLOSEOUT_MMI-DEC-131.md`;
  hardening addendum research register; pricing/copy caps/consent/protobuf closed;
  **advisory only** — no mesh production code).

PRIOR: Stage A a04 — MSP pilot motion intake Todd / CMIT (MMI-DEC-129 VERIFY)
  (`mmi/MMI_CHAIN_OF_COMMAND_MISSION_MAP.yaml`; `scripts/mmi_mission_map.py`;
  `mmi/MMI_MISSION_MAP.md` v2; PMV ALL_CLEAR relay to mission map).

PRIOR: Swarm organism concept capture — federation mesh + Lung dials (MMI-DEC-125)
  (`mmi_rp_v1` hints; RoutePolicyAudit metadata).

PRIOR: #3 Risk Triage GATED (MMI-DEC-116); Command spine #1–#3 GATED at wrapper layer.

REVIEW_ACCEPTED_ITEMS:
  - Mode Controller Adversarial #99 evidence accepted June 15th 2026; #92 marked ADVERSARIALLY HARDENED
  - ReconciliationAgent Adversarial #100 evidence accepted June 15th 2026 with disclosed LungState guard warning; #84 marked ADVERSARIALLY HARDENED
  - Blast Radius Controller Adversarial #101 evidence accepted June 15th 2026; #89 marked ADVERSARIALLY HARDENED
  - Runtime Instrumentation telemetry output accepted June 15th 2026
  - Threat Intelligence Daemon external lane build verified 2026-06-18 (EXTERNAL_LANE COMPLETE; not authority-repo scoreboard)

ADVERSARIAL QUEUE STATUS:
  #99  Mode Controller Adversarial      GATED (Matt accepted June 15th 2026; #92 hardened claim granted)
  #100 ReconciliationAgent Adversarial  GATED (Matt accepted June 15th 2026; #84 hardened claim granted)
  #101 BRC Adversarial                  GATED (Matt accepted June 15th 2026; #89 hardened claim granted)
  #102 Safe-Stop Adversarial            GATED (Matt accepted June 15th 2026; #94 hardened claim granted)

INSTRUMENTATION STATUS:
  Runtime_Instrumentation_Runbook.md signed June 16 2026
  Runtime instrumentation Grok output accepted June 15th 2026

PARKED DRAFTS (untracked, parallel-session; CLASSIFIED 2026-06-18 — NOT promoted):
  4. Product_Roadmap/Builder_Radar_Concept_Doc.md — PARKED_DRAFT / CONCEPT_ADVISORY / PARK
  4. Product_Roadmap/Honeypot_Deception_Concept_Doc.md — PARKED_DRAFT / LEGAL_GATE / PARK
  4. Product_Roadmap/Mutant_Monkey_Radar_Concept_Doc.md — PARKED_DRAFT / CONCEPT_ADVISORY / PARK
  4. Product_Roadmap/Purple_Team_Attacker_Cost_Doctrine.md — PARKED_DRAFT / DOCTRINE_ADVISORY / PARK
  Registry: mmi/PARKED_DRAFT_CLASSIFICATIONS.md

## Active Project Identity Guard

Active project identity: **Mutant Monkey Security**.

Central project brain: **Mutant Monkey Intelligence (MMI)**.

Legacy filesystem path: `/home/socialarchitect/northstar`.

The word `northstar` may appear as a legacy folder path, commit history, or historical reference only. It must not be used as the current active project identity.

Separate app repo surfaces such as `/home/socialarchitect/projects/Architectapp_clean` or `/mnt/c/Architectapp_clean` are not the governed MMI / swarm runtime authority surface.

For governed MMI / swarm runtime work, use:

- Project: Mutant Monkey Security
- Brain: Mutant Monkey Intelligence / MMI
- Authority repo path: `/home/socialarchitect/northstar`

#48 Verification Outcome Agent belongs only in:

`/home/socialarchitect/northstar/core/orchestrator/verification_outcome_agent.py`

Do not build governed MMI / swarm runtime artifacts in Architectapp.
