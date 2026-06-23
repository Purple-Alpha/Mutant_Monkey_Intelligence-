MODE: AUDIT
AUTHORIZED_TASK: Run Grok completion gate for Mission Context Agent
ASSIGNED_TO: Grok (negative-feedback auditor)
NEXT_PROMPT_GOES_TO: Cursor stages the build, runs the gate, then commits
OPERATOR_ACTION_REQUIRED: NO  (Grok activation is standing; no per-run permission)
RUN: python3 audit_tools/complete_gate.py --pre-commit --task mission_context_agent --claim "Mission Context Agent build implemented + tested; ready for audit"
MANIFEST: audit_outputs/pending/mission_context_agent.manifest.json (present)
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

LAST_COMPLETED: #2 Mission Context build + AWAITING_AUDIT reconcile
  (MMI-DEC-108; Matt authorized #2 build; `MissionContextAgent` + 16 tests; pre-build gate MMI-DEC-107; **not GATED** until completion gate 0/0; **not GOVERNED_AGENT**; **not** AUTH-5).

PRIOR_LAST_COMPLETED: #2 Mission Context pre-build gate clean 0/0
  (MMI-DEC-107; `mmi_02_contract_gate_20260623T033955Z.md`; SIGNED_UNBUILT reconcile MMI-DEC-106).

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

