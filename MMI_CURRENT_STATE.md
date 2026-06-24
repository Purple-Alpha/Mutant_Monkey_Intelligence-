MODE: ALL_CLEAR
AUTHORIZED_TASK: No delegable tasks in routing queue
OPERATOR_NAMES_TARGET: Matt
MMI_ASSIGNS_LANE: YES
LANE_ESCALATION_TO_MATT: only on authority/scope/live-data/material-risk fork
BUILD_AUTHORIZATION_IMPLIED: NO
CURRENT_PROJECT_TRUTH: Mutant Monkey Security authority-repo control-plane queue: 0 SIGNED_UNBUILT, 0 AWAITING_AUDIT, 42 GATED rows; 0 untracked roadmap draft(s) in git status; legacy path /home/socialarchitect/northstar
WHY_QUEUE_IS_EMPTY: 0 SIGNED_UNBUILT scoreboard rows; 0 AWAITING_AUDIT rows; parked roadmap drafts already classified (PARK — not delegable); no off-scoreboard signed authority-repo contracts; external lanes complete or unsigned; no specific research target beyond generic placeholder
ASSIGNED_TO: Matt
NEXT_PROMPT_GOES_TO: Matt
OPERATOR_ACTION_REQUIRED: YES — supply next evidence or run Estimator for read-only candidate ranking
CANDIDATES_NOT_AUTHORIZATION: YES — Estimator ranks candidates; output is not authorization, selection, or routing authority
REQUIRED_UPDATE_AFTER_COMPLETION: MMI first after any worker completion: append evidence to the relevant MMI record (intake/gate/decision log as applicable), update MMI_CURRENT_STATE.md LAST_COMPLETED prose, run python3 scripts/mmi_dispatch.py --sync, commit routing-authority files, then python3 scripts/mmi_dispatch.py --verify
NEXT_GATE: new signed contract, scoreboard row, intake evidence, or operator-selected next action
TASK_SCOREBOARD: (empty — queue has no delegable tasks)

AUTHORITY NOTE (2026-06-16): The routing block above is derived by scripts/mmi_dispatch.py
  and must remain as emitted. MODE: BUILD means the scoreboard has a visible SIGNED_UNBUILT
  next item (#103 first); it does NOT mean Matt has authorized Cursor to begin implementation.
  Matt must still explicitly name the build target. Rows #103/#104 state lifecycle tracking is
  not build authorization. `BUILD_AUTHORIZATION_IMPLIED` in the routing block is mechanical
  sequencer language, not operator build authorization. Current source-of-truth authority for
  component/gate status is mmi/MMI_GATE_REGISTRY.md and mmi/MMI_DECISION_LOG.md; consistency
  is verified by `python3 scripts/mmi_dispatch.py --verify`. Prose below is human context;
  anything marked SUPERSEDED is historical only and is NOT routing authority.

LAST_COMPLETED: #1 routing-policy annex §6 wiring completion gate clean 0/0 (MMI-DEC-123)
  (`audit_outputs/swarm_commander_routing_policy_annex_wiring_20260624T022634Z.md`;
  wiring MMI-DEC-122; 27 focused tests; **not** GOVERNED_AGENT promotion).

PRIOR_LAST_COMPLETED: #1 routing-policy annex §6 wired in SwarmCommanderAgent (MMI-DEC-122)
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

