MODE: BUILD
AUTHORIZED_TASK: Build Callback Verification
OPERATOR_NAMES_TARGET: Matt
MMI_ASSIGNS_LANE: YES
LANE_ESCALATION_TO_MATT: only on authority/scope/live-data/material-risk fork
BUILD_AUTHORIZATION_IMPLIED: YES — §11 signed on scoreboard SIGNED_UNBUILT row
PROJECT_IDENTITY: Mutant Monkey Security
MMI_BRAIN: Mutant Monkey Intelligence (MMI)
AUTHORITY_REPO: Mutant Monkey Security authority repo (legacy path /home/socialarchitect/northstar)
ASSIGNED_TO: Cursor → Codex → Cursor
PRE_BUILD_REVIEW: Codex
NEXT_PROMPT_GOES_TO: Cursor (draft plan) → Codex (review) → Cursor (build)
BLOCKED_UNTIL: Codex clears build plan; then implementation + tests complete
OPERATOR_ACTION_REQUIRED: NO
NEXT_GATE: Codex review → Cursor build → gate 0/0 + health score 85+ + hash reported

AUTHORITY NOTE (2026-06-16): The routing block above is derived by scripts/mmi_dispatch.py
  and must remain as emitted. MODE: BUILD means the scoreboard has a visible SIGNED_UNBUILT
  next item (#103 first); it does NOT mean Matt has authorized Cursor to begin implementation.
  Matt must still explicitly name the build target. Rows #103/#104 state lifecycle tracking is
  not build authorization. `BUILD_AUTHORIZATION_IMPLIED` in the routing block is mechanical
  sequencer language, not operator build authorization. Current source-of-truth authority for
  component/gate status is mmi/MMI_GATE_REGISTRY.md and mmi/MMI_DECISION_LOG.md; consistency
  is verified by `python3 scripts/mmi_dispatch.py --verify`. Prose below is human context;
  anything marked SUPERSEDED is historical only and is NOT routing authority.

LAST_COMPLETED: #18 Callback Verification build + AWAITING_AUDIT (MMI-DEC-194)
  (`CallbackVerificationAgent` wrapper + 22 tests; read-only callback-OOB posture;
  completion gate pending; rank-2 #49 on deck).

PRIOR_LAST_COMPLETED: #18 Callback Verification Agent Design Contract §11 signed (MMI-DEC-193)
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

