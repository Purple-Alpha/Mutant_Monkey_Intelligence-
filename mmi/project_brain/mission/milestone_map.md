# MMI Milestone Map

This file defines what the project is building toward. The dispatcher and PM
voice should prefer work that advances the active milestone.

For operator-facing direction sheets see `short_term_goals.md` and
`long_term_goals.md` in this folder.

## Active Milestone

`M1_CONTROL_PLANE_RESTORED`

Goal: Matt can run one command and see the current task, owner, score, lane, and
reason without reading a wall of governance text.

Done when:

- `python3 scripts/mmi_pm_voice.py` gives one clear operator action
- every surfaced task has a lane, owner, score, and milestone
- weak `1/10` actions do not become the main recommendation unless no stronger
  milestone work exists or Matt explicitly chooses them
- drift checks still protect authority, contracts, and scoreboard state

## Milestones

### M1_CONTROL_PLANE_RESTORED

Restore the operator brain: short console, real queue truth, milestone-aware
ranking, and plain handoff text.

Primary lanes: `DRIFT_CHECK`, `CONTRACT`, `PROMOTION`, `AUDIT`

Preferred owners:

- `Codex`: control-plane review, critique, tests, routing safety
- `Cursor`: implementation when a scoped code change is authorized
- `Matt`: authority decisions and final authorization

### M2_CONTRACT_QUEUE_CLEAN

Make sure contract drafts, signed contracts, GATED rows, and promotion targets
are not mixed together.

Primary lanes: `CONTRACT`, `PRE_BUILD_REVIEW`, `PROMOTION`

### M3_BUILD_PIPELINE_STABLE

Only build from signed authority. Keep implementation, tests, and evidence tied
to the correct contract.

Primary lanes: `BUILD`, `TEST`, `DRIFT_CHECK`

### M4_GOVERNED_RUNTIME_SPINE

Promote the right GATED components into governed runtime only after promotion
review.

Primary lanes: `PROMOTION`, `AUDIT`, `BUILD`

### M5_DEMO_REVENUE_ASSET

Produce a usable demo or revenue-facing proof that stays inside security and
authority boundaries.

Primary lanes: `DESIGN`, `BUILD`, `AUDIT`, `REVENUE_DEMO`

## Ranking Rule

When the queue is empty or only shows low-score promotion leftovers, use the
active milestone to pull stronger work. A task that advances the active
milestone should outrank a generic `1/10` backlog item.

