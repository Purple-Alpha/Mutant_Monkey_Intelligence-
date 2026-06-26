# Active Task

This file records what the project brain believes is active right now. It should
match the short operator console.

## Current State

status: `ACTION`

task: `Restore milestone-aware operator routing so weak 1/10 backlog work does not become the default next build`

for: `Codex`

score: `8/10`

milestone: `M1_CONTROL_PLANE_RESTORED`

lane: `DRIFT_CHECK`

## Why This Is Active

The current console can show a clean short answer, but when the formal queue is
empty it can still surface weak promotion leftovers like `1/10`. The missing
piece is a project brain/milestone layer that tells the dispatcher what the
project is building toward.

## Done When

- project brain files exist in `mmi/project_brain/`
- active milestone is documented
- lanes are documented
- next implementation step is clear: wire active milestone into scoring output

## Closeout

MMI-DEC-220 records the operator-console and project-brain restoration. This
task stays active until dispatch verify is clean and the ranked lane board no
longer makes the weak `1/10` backlog item look like the main project direction.
This is advisory only and does not authorize build, promotion, signing,
production wiring, or AUTH-5.
