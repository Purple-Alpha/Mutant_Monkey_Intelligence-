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
```
