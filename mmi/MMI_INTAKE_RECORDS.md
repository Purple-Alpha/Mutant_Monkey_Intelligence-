# MMI_INTAKE_RECORDS.md — Task Intake Log

**Authority:** Matt Nichol — authorized June 16 2026

Every incoming task gets an intake record **before** it is routed. This prevents random work from becoming invisible work.

---

## Intake record template

```
Intake ID:
Date/time:
Source:
Requested task:
Affected component:
Current phase:
Assigned reviewer/model:
Authority status:
Required evidence:
Decision needed:
Routing outcome:
Matt approval required: yes/no
```

---

## Running log

```
INTAKE-2026-06-16-001
Component: MMI Center
Request: Build MMI governance folder and files
Assigned to: Cursor
Authority: Build only — files defined by Claude design session June 16 2026
Matt approval required: Yes — review after build

INTAKE-2026-06-16-002
Component: MMI dispatcher / routing doctrine
Request: Classify session history on lane-selection doctrine becoming executable
Source: Cursor/Matt MMI routing-status history (evidence only)
Classification: NEEDS_MMI_REVIEW / BUILT_NEEDS_VERIFICATION
Record: mmi/history_intake/MMI_DISPATCHER_ROUTING_DOCTRINE_INTAKE.md
Golden candidate: "Matt names the authorized target; MMI assigns the lane."
Matt approval required: Yes — review golden doctrine; authorize commit of dispatcher/routing changes

INTAKE-2026-06-16-003
Component: MMI chat/session history intake cleanup
Request: Finish MMI_CHATGPT_HISTORY_INTAKE_AND_CLASSIFICATION — index folder, repo intake,
  Windows master pointer, Claude/Cursor quarantine intake; revert local dispatcher experiments
Source: Repo artifacts + Windows master + pasted Claude/Cursor session material
Classification: documentation/classification only — no dispatcher/routing/automation changes
Records: mmi/history_intake/README.md,
  mmi/history_intake/MMI_CHATGPT_HISTORY_INTAKE.md,
  mmi/history_intake/MMI_CHATGPT_HISTORY_MASTER_INDEX.md,
  mmi/history_intake/MMI_CLAUDE_CURSOR_HISTORY_INTAKE.md
Matt approval required: No for intake commit; yes before any promotion out of NEEDS_MMI_REVIEW

INTAKE-PHASE-CLOSED-2026-06-16
Component: MMI history intake phase closure
Status: INTAKE PHASE CLOSED
Pushed commits: ccd96f4 (dispatcher routing doctrine intake), 3b4b999 (history intake cleanup)
Remote branch: github/safety/queue-drift-cleanup-20260528
Classification summary:
  - SUPPORTED_BY_REPO — intake files committed and pushed
  - NEEDS_MMI_REVIEW — golden doctrine captured inside intake (not promoted)
  - BUILT_NEEDS_VERIFICATION — dispatcher/routing upgrade claims remain unaccepted
  - PARKED_DRAFT — four untracked roadmap concept docs (untouched)
Dispatcher/routing files: CLEAN (no local changes)
Handshake / scoreboard: UNTOUCHED
Authority bleed: PREVENTED (intake separated from dispatcher implementation)
Origin rejection: remote-drift / Windows-surface warning only — not in scope for this lane
No next phase authorized: no build, research, design, dispatcher implementation,
  routing alignment patch, or automation

INTAKE-2026-06-18-004
Component: Parked roadmap drafts (parallel-session untracked)
Request: Classify parked roadmap drafts (4 files) — MMI DELEGATE score=72
Source: git status ?? in 4. Product_Roadmap/; MODE: DELEGATE 2026-06-18
Assigned to: Cursor (intake lane)
Authority: Classification only — no git add, no promotion, no build
Classification summary (record: mmi/PARKED_DRAFT_CLASSIFICATIONS.md):
  - Builder_Radar_Concept_Doc.md → PARKED_DRAFT / CONCEPT_ADVISORY → PARK
  - Honeypot_Deception_Concept_Doc.md → PARKED_DRAFT / CONCEPT_ADVISORY / LEGAL_GATE → PARK
  - Mutant_Monkey_Radar_Concept_Doc.md → PARKED_DRAFT / CONCEPT_ADVISORY → PARK
  - Purple_Team_Attacker_Cost_Doctrine.md → PARKED_DRAFT / DOCTRINE_ADVISORY → PARK
Routing outcome: NOT_AUTHORIZED for build or scoreboard; remain untracked until Matt promotes
Matt approval required: YES before any file is git-tracked, contracted, or built

INTAKE-2026-06-18-005
Component: Threat Intelligence Daemon (external lane)
Request: Build delegated external lane per MODE:DELEGATE TASK_SCORE=68
Source: 4. Product_Roadmap/Threat_Intelligence_Daemon_Design_Contract.md §11 signed
Assigned to: Cursor
Authority: External build at /home/socialarchitect/mutant_monkey_intel/ only — TI-R2 Northstar isolation
Classification: EXTERNAL_LANE COMPLETE — not a Northstar scoreboard row
Evidence: lab_records/2026-06-18_threat_intelligence_daemon_external_lane.md;
  mmi/EXTERNAL_LANE_STATUS.md; test_monkey_intel_daemon.py (11 passed)
Tests: 11 passed offline (TI-INV-2/3/4/5/6/7/8/9/10/11 + layout)
Matt approval required: NO for build verification; YES before intel enters Northstar build loop

INTAKE-2026-06-18-006
Component: #48 Verification Outcome Agent (scoreboard lifecycle)
Request: Reconcile scoreboard row per MMI PROJECT_DIRECTION_RESEARCH recommendation (54df32e)
Source: 4. Product_Roadmap/Verification_Outcome_Agent_Design_Contract_Deep_Dive.md
  **Status:** §11 SIGNED 2026-06-08 by Matt Nichol (draft 8e2b787; signature f34cc4f)
  §11 Lockdown Signature: Matt Nichol June 8th 2026
Assigned to: Cursor (scoreboard reconcile only — no build)
Authority: Lifecycle visibility only; contract §11 is build authority
Classification: SCOREBOARD_RECONCILE — SPEC_ONLY/NEEDS_SIGNED_CONTRACT -> SIGNED_UNBUILT
Evidence: agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md #48 row updated;
  no core/orchestrator/verification_outcome_agent.py (wrapper not built)
Routing outcome: MODE:BUILD eligible via get_signed_unbuilt()
Matt approval required: YES before wrapper build starts (separate authorization)

INTAKE-2026-06-19-001
Component: #48 Verification Outcome Agent (build complete)
Request: Commit build + advance scoreboard to AWAITING_AUDIT per #48_BUILD_COMMIT_AND_SCOREBOARD_AUDIT_LANE
Source: 4. Product_Roadmap/Verification_Outcome_Agent_Design_Contract_Deep_Dive.md (§11 SIGNED f34cc4f)
Build commit: e1afc56
Evidence: core/orchestrator/verification_outcome_agent.py; tests/test_verification_outcome_agent.py (21 passed)
Classification: BUILT_AWAITING_AUDIT — scoreboard #48 lifecycle advance
Routing outcome: MODE:AUDIT via get_awaiting_audit()
Gate manifest: audit_outputs/pending/verification_outcome.manifest.json
Matt approval required: NO for audit lane routing; YES for GATED promotion after gate

INTAKE-2026-06-19-002
Component: #48 Verification Outcome Agent (Grok gate + GATED)
Request: Run Grok completion gate on clean worktree; flip scoreboard AWAITING_AUDIT -> GATED
Source: audit_outputs/verification_outcome_20260619T032930Z.md (Grok 0/0 comprehensive)
Build commit: e1afc56
Gate evidence: blocking=0 warnings=0; packet hash 3c576411377255e6e473cc2f9afe68844169e7b0fdb16acfbc1d36cce990f43d
Classification: GATED — scoreboard #48 lifecycle advance post-audit
Routing outcome: exit MODE:AUDIT; next promotion GATED -> GOVERNED_AGENT on operator authorization
Matt approval required: NO for gate run (standing Grok activation); promotion to GOVERNED_AGENT is separate

INTAKE-2026-06-19-003
Component: #48 Verification Outcome Agent (GOVERNED_AGENT promotion)
Request: MMI_48_GOVERNED_AGENT_PROMOTION_REVIEW — complete lifecycle if repo evidence supports it
Source: scoreboard Q4 L3 bar; contract §6/§7; build e1afc56; gate verification_outcome_20260619T032930Z.md
Evidence: 21 focused tests; DER chain via SwarmCommander.run_case; health score 87 seeded
Classification: GOVERNED_AGENT — scoreboard #48 lifecycle promotion at Evidence Stage 1
Routing outcome: breadth runway 13 -> 14; #47 DEPENDS_ON:#48 satisfied for re-triage only
Matt approval required: YES — operator authorized MMI_48_GOVERNED_AGENT_PROMOTION_REVIEW only
