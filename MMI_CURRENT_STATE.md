MODE: DELEGATE
AUTHORIZED_TASK: Build Threat Intelligence Daemon (external lane)
OPERATOR_NAMES_TARGET: Matt
MMI_ASSIGNS_LANE: YES
LANE_ESCALATION_TO_MATT: only on authority/scope/live-data/material-risk fork
BUILD_AUTHORIZATION_IMPLIED: YES — delegated from repo evidence
CURRENT_PROJECT_TRUTH: Northstar control-plane queue: 0 SIGNED_UNBUILT, 0 AWAITING_AUDIT, 33 GATED rows; 4 untracked roadmap draft(s) in git status
TASK_SCOREBOARD: Build Threat Intelligence Daemon (external lane) [EXTERNAL_LANE score=68]
NEXT_DELEGATED_TASK: Build Threat Intelligence Daemon (external lane)
ASSIGNED_WORKER: Cursor
ASSIGNED_TO: Cursor
WHY_THIS_TASK: Contract is signed and scoped to an external repo lane — not a Northstar scoreboard row; delegate build to external surface
TASK_SCORE: 68
LOWER_SCORE_ALTERNATIVES: (none)
SOURCE_EVIDENCE: 4. Product_Roadmap/Threat_Intelligence_Daemon_Design_Contract.md §11 signed; external root /home/socialarchitect/mutant_monkey_intel/
REQUIRED_UPDATE_AFTER_COMPLETION: MMI first after any worker completion: append evidence to the relevant MMI record (intake/gate/decision log as applicable), update MMI_CURRENT_STATE.md LAST_COMPLETED prose, run python3 scripts/mmi_dispatch.py --sync, commit routing-authority files, then python3 scripts/mmi_dispatch.py --verify
NEXT_PROMPT_GOES_TO: Cursor
BLOCKED_UNTIL: Cursor completes delegated task and MMI update
OPERATOR_ACTION_REQUIRED: NO
CANDIDATES_NOT_AUTHORIZATION: YES — lower-scored alternatives are context only; delegation is evidence-based
CANDIDATES: [EXTERNAL] Build Threat Intelligence Daemon (external lane) | Classification: EXTERNAL_LANE | Score: 68 | Source: 4. Product_Roadmap/Threat_Intelligence_Daemon_Design_Contract.md §11 signed; external root /home/socialarchitect/mutant_monkey_intel/ | Worker: Cursor | Matt action: NO
NEXT_GATE: worker completion → MMI update first → --verify PASS

AUTHORITY NOTE (2026-06-16): The routing block above is derived by scripts/mmi_dispatch.py
  and must remain as emitted. MODE: BUILD means the scoreboard has a visible SIGNED_UNBUILT
  next item (#103 first); it does NOT mean Matt has authorized Cursor to begin implementation.
  Matt must still explicitly name the build target. Rows #103/#104 state lifecycle tracking is
  not build authorization. `BUILD_AUTHORIZATION_IMPLIED` in the routing block is mechanical
  sequencer language, not operator build authorization. Current source-of-truth authority for
  component/gate status is mmi/MMI_GATE_REGISTRY.md and mmi/MMI_DECISION_LOG.md; consistency
  is verified by `python3 scripts/mmi_dispatch.py --verify`. Prose below is human context;
  anything marked SUPERSEDED is historical only and is NOT routing authority.

LAST_COMPLETED: Parked roadmap draft intake classification (INTAKE-2026-06-18-004) —
  four parallel-session untracked files classified PARK/NOT_AUTHORIZED; evidence in
  mmi/PARKED_DRAFT_CLASSIFICATIONS.md + mmi/MMI_INTAKE_RECORDS.md; files remain ?? in
  git by design until Matt authorizes promotion. Prior: Specialisation Fission v2 #104 GATED.

REVIEW_ACCEPTED_ITEMS:
  - Mode Controller Adversarial #99 evidence accepted June 15th 2026; #92 marked ADVERSARIALLY HARDENED
  - ReconciliationAgent Adversarial #100 evidence accepted June 15th 2026 with disclosed LungState guard warning; #84 marked ADVERSARIALLY HARDENED
  - Blast Radius Controller Adversarial #101 evidence accepted June 15th 2026; #89 marked ADVERSARIALLY HARDENED
  - Runtime Instrumentation telemetry output accepted June 15th 2026
  - Safe-Stop Adversarial #102 evidence accepted June 15th 2026; #94 marked ADVERSARIALLY HARDENED

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
