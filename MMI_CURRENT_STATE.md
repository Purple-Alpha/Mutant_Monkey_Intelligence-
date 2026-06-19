MODE: PROJECT_DIRECTION_RESEARCH
AUTHORIZED_TASK: Score repo-grounded project directions; recommend best next direction
OPERATOR_NAMES_TARGET: Matt
MMI_ASSIGNS_LANE: YES
LANE_ESCALATION_TO_MATT: only on authority/scope/live-data/material-risk fork
BUILD_AUTHORIZATION_IMPLIED: YES — top direction has signed contract or explicit build path
CURRENT_PROJECT_TRUTH: Northstar control-plane queue: 0 SIGNED_UNBUILT, 0 AWAITING_AUDIT, 33 GATED rows; 4 untracked roadmap draft(s) in git status
WHY_QUEUE_IS_EMPTY: 0 SIGNED_UNBUILT scoreboard rows; 0 AWAITING_AUDIT rows; parked roadmap drafts already classified (PARK — not delegable); no off-scoreboard signed Northstar contracts; external lanes complete or unsigned; no specific research target beyond generic placeholder
DIRECTION_SCOREBOARD: Build #48 Verification Outcome Agent (Stage 1 Synthetic wrapper) [total=19 axes: revenue_market=2,product_foundation=2,security_evidence=2,dependency_unlock=2,drift_reduction=2,build_readiness=2,risk_ambiguity=2,owner_time=2,mmi_alignment=2,demo_customer=1] || Build second Layer 5 Challenge agent (cross-arbitration; closes KG-002) [total=13 axes: revenue_market=1,product_foundation=2,security_evidence=2,dependency_unlock=1,drift_reduction=1,build_readiness=1,risk_ambiguity=1,owner_time=1,mmi_alignment=2,demo_customer=1] || Stage 1 breadth — wrap #52 Plain-English Explanation detector [total=13 axes: revenue_market=2,product_foundation=1,security_evidence=1,dependency_unlock=1,drift_reduction=1,build_readiness=1,risk_ambiguity=2,owner_time=1,mmi_alignment=1,demo_customer=2] || Stabilize — hold new builds; verify and document only [total=9 axes: revenue_market=0,product_foundation=0,security_evidence=1,dependency_unlock=0,drift_reduction=1,build_readiness=2,risk_ambiguity=2,owner_time=2,mmi_alignment=1,demo_customer=0] || Real-data intake path (Evidence Stage 2 promotion) [total=6 axes: revenue_market=1,product_foundation=1,security_evidence=1,dependency_unlock=0,drift_reduction=0,build_readiness=0,risk_ambiguity=1,owner_time=0,mmi_alignment=1,demo_customer=1] || Promote parked roadmap concept drafts to tracked build [total=0 axes: revenue_market=0,product_foundation=0,security_evidence=0,dependency_unlock=0,drift_reduction=0,build_readiness=0,risk_ambiguity=0,owner_time=0,mmi_alignment=0,demo_customer=0]
RECOMMENDED_DIRECTION: Build #48 Verification Outcome Agent (Stage 1 Synthetic wrapper)
RECOMMENDED_NEXT_ACTION: Reconcile scoreboard #48 to SIGNED_UNBUILT, then Cursor build plan -> Codex pre-build review -> implement VerificationOutcomeAgent + focused tests -> gate 0/0
ASSIGNED_WORKER_OR_LANE: Cursor -> Codex -> Cursor
WHY_THIS_DIRECTION: Build Sequencer CYCLE 25 UNBLOCK; §11-signed boundary contract; read-only Layer 3 projection over two_channel_confirmation; unblocks #47 Case Timeline and vendor-payment verification frontier
DECISION_SCORE: 19/20 (revenue_market=2,product_foundation=2,security_evidence=2,dependency_unlock=2,drift_reduction=2,build_readiness=2,risk_ambiguity=2,owner_time=2,mmi_alignment=2,demo_customer=1)
LOWER_SCORE_ALTERNATIVES: Build second Layer 5 Challenge agent (cross-arbitration; closes KG-002) (score=13) || Stage 1 breadth — wrap #52 Plain-English Explanation detector (score=13) || Stabilize — hold new builds; verify and document only (score=9) || Real-data intake path (Evidence Stage 2 promotion) (score=6) || Promote parked roadmap concept drafts to tracked build (score=0)
SCORE_RUBRIC: MMI project-direction rubric: 0-2 per axis, max total 20. 0=negligible, 1=moderate, 2=strong. risk_ambiguity and owner_time are inverse penalties (2=low risk/burden). Recommendation ranks directions; Matt selects.
SOURCE_EVIDENCE: 4. Product_Roadmap/Verification_Outcome_Agent_Design_Contract_Deep_Dive.md (§11 SIGNED); agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md #48/#47; PROJECT_HANDSHAKE.md; decision_cycles_log.md CYCLE 25; scoreboard row #48 still SPEC_ONLY/UNSIGNED — drift vs signed contract
OWNER_DECISION_NEEDED: YES — confirm this direction; contract §11 already signed; scoreboard reconcile + build start need operator acknowledgment
REQUIRED_UPDATE_AFTER_COMPLETION: MMI first after any worker completion: append evidence to the relevant MMI record (intake/gate/decision log as applicable), update MMI_CURRENT_STATE.md LAST_COMPLETED prose, run python3 scripts/mmi_dispatch.py --sync, commit routing-authority files, then python3 scripts/mmi_dispatch.py --verify
ASSIGNED_TO: Matt (direction selection) -> Cursor -> Codex -> Cursor
NEXT_PROMPT_GOES_TO: Matt confirms direction, then Cursor
OPERATOR_ACTION_REQUIRED: YES — Matt selects among scored directions (recommendation is not authorization)
CANDIDATES_NOT_AUTHORIZATION: YES — scored directions rank options; Matt selects; lower scores are context only
CANDIDATES: Build #48 Verification Outcome Agent (Stage 1 Synthetic wrapper) [total=19 axes: revenue_market=2,product_foundation=2,security_evidence=2,dependency_unlock=2,drift_reduction=2,build_readiness=2,risk_ambiguity=2,owner_time=2,mmi_alignment=2,demo_customer=1] || Build second Layer 5 Challenge agent (cross-arbitration; closes KG-002) [total=13 axes: revenue_market=1,product_foundation=2,security_evidence=2,dependency_unlock=1,drift_reduction=1,build_readiness=1,risk_ambiguity=1,owner_time=1,mmi_alignment=2,demo_customer=1] || Stage 1 breadth — wrap #52 Plain-English Explanation detector [total=13 axes: revenue_market=2,product_foundation=1,security_evidence=1,dependency_unlock=1,drift_reduction=1,build_readiness=1,risk_ambiguity=2,owner_time=1,mmi_alignment=1,demo_customer=2] || Stabilize — hold new builds; verify and document only [total=9 axes: revenue_market=0,product_foundation=0,security_evidence=1,dependency_unlock=0,drift_reduction=1,build_readiness=2,risk_ambiguity=2,owner_time=2,mmi_alignment=1,demo_customer=0] || Real-data intake path (Evidence Stage 2 promotion) [total=6 axes: revenue_market=1,product_foundation=1,security_evidence=1,dependency_unlock=0,drift_reduction=0,build_readiness=0,risk_ambiguity=1,owner_time=0,mmi_alignment=1,demo_customer=1] || Promote parked roadmap concept drafts to tracked build [total=0 axes: revenue_market=0,product_foundation=0,security_evidence=0,dependency_unlock=0,drift_reduction=0,build_readiness=0,risk_ambiguity=0,owner_time=0,mmi_alignment=0,demo_customer=0]
NEXT_GATE: Matt confirms direction -> delegate build/design lane -> worker completion -> MMI update -> --verify PASS
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

LAST_COMPLETED: Threat Intelligence Daemon external lane — verified against
  §11-signed `Threat_Intelligence_Daemon_Design_Contract.md` at
  `/home/socialarchitect/mutant_monkey_intel/`; layout + tiering + notification +
  Northstar write guard present; `test_monkey_intel_daemon.py` 11 passed (offline
  TI-INV suite); registry `mmi/EXTERNAL_LANE_STATUS.md` marked COMPLETE; lab record
  `lab_records/2026-06-18_threat_intelligence_daemon_external_lane.md`. Prior:
  parked draft intake INTAKE-2026-06-18-004.

REVIEW_ACCEPTED_ITEMS:
  - Mode Controller Adversarial #99 evidence accepted June 15th 2026; #92 marked ADVERSARIALLY HARDENED
  - ReconciliationAgent Adversarial #100 evidence accepted June 15th 2026 with disclosed LungState guard warning; #84 marked ADVERSARIALLY HARDENED
  - Blast Radius Controller Adversarial #101 evidence accepted June 15th 2026; #89 marked ADVERSARIALLY HARDENED
  - Runtime Instrumentation telemetry output accepted June 15th 2026
  - Threat Intelligence Daemon external lane build verified 2026-06-18 (EXTERNAL_LANE COMPLETE; not Northstar scoreboard)

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
