# Next Target Evidence Board

This file exists so Matt does not have to pick the next build blind.

## Naming

Old term: `chain of command`

Current terms:

- `project brain`: the living project memory and milestone map
- `PM Voice`: the short operator console
- `dispatcher`: the queue truth checker
- `mission map`: historical stage map; useful context, not enough by itself

The old chain-of-command idea is now split across the project brain, PM Voice,
dispatcher, and mission map.

## Current Evidence Snapshot

Source commands:

```bash
python3 scripts/mmi_pm_voice.py
python3 scripts/mmi_dispatch.py --route-detail
python3 scripts/mmi_estimator.py
python3 scripts/mmi_next_action_rubric.py --limit 12
```

Findings:

- PM Voice asks Matt to pick a next project-brain milestone target.
- Dispatcher reports `ALL_CLEAR`.
- Dispatcher reports `0 SIGNED_UNBUILT` rows.
- Dispatcher reports `0 AWAITING_AUDIT` rows.
- Estimator reports `NO_BUILDABLE_CANDIDATES`.
- Estimator excludes `#10 Lookalike Domain` because it is already `GATED`.
- Estimator excludes `#21 Executive Impersonation` because it is already `GATED`.
- Estimator excludes `#105 MMI Governance Invariants Testing Framework` because it is `SIGNED_CONTRACT`, not a build lane; Lane 2+ is held.
- Current live rubric only surfaces weak/admin actions:
  - admin lane board sync: `5/10`
  - promotion `#10`: `1/10`
  - promotion `#21`: `1/10`
  - hold: `3/10`

## Important Drift Finding

The historical mission map still references old BOR feedstock language such as
`#71 Token Usage Tracker` as rank-1. That is stale for current routing because
the live scoreboard/decision log now show `#71` as already governed and the
dispatcher reports no buildable candidates.

This means Matt should not be asked to pick from the old mission-map text alone.
The next target needs a fresh evidence-backed candidate board.

## Evidence-Based Options

### Option A: Repair next-target evidence board

Owner: `Codex`

Lane: `DRIFT_CHECK`

Score: `8/10`

Why:

- Prevents blind operator picks.
- Reconciles stale mission-map language against live dispatcher/estimator truth.
- Gives Matt a short ranked choice set with evidence.

Boundary:

- Advisory only.
- No build authorization.
- No scoreboard lifecycle mutation without separate authorization.

### Option B: Promotion cleanup for #10 or #21

Owner: `Matt`

Lane: `PROMOTION`

Score: `1/10`

Why:

- Both are GATED and have clean gates.
- Promotion review is available if Matt explicitly wants cleanup.

Why weak:

- Current rubric gives each only `1/10`.
- Promotion does not create a new build target.
- Promotion is not the same as production dispatch.

### Option C: Start next Build Sequencer Q5 step 4 selection

Owner: `Codex`

Lane: `DESIGN`

Score: `7/10`

Why:

- Build Sequencer says Q5 step 4 is wrapping existing detector functions into
  governed agents by evidence value.
- This is likely the next real build direction, but it needs a candidate review
  before Cursor gets implementation.

Boundary:

- Codex can prepare the candidate evidence packet.
- Matt must authorize the selected target.
- Cursor should only build after signed authority and scoped implementation.

## Recommended Next Action

Use Option A first:

```text
task: Reconcile project-brain next-target evidence against dispatcher, estimator, scoreboard, and mission map
for: Codex
score: 8/10
```

Done when Matt sees a short ranked list of 2-4 next targets with evidence and
can choose without guessing.

