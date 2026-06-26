# Operator Console Runbook

Use this when Matt asks, "what do I do next?"

## Normal Command

```bash
python3 scripts/mmi_pm_voice.py
```

Expected shape:

```text
MMI_OPERATOR_CONSOLE
status: ACTION
task: short task name
for: worker name
score: n/10
```

## Full Detail Commands

Use these only when the short answer is not enough:

```bash
python3 scripts/mmi_pm_voice.py --verbose
python3 scripts/mmi_pm_voice.py --lanes
python3 scripts/mmi_dispatch.py --route-detail
```

## How To Read The Score

- `8-10`: do this next unless Matt has a better business priority
- `4-7`: useful, but compare against the active milestone
- `1-3`: weak; backlog or promotion cleanup unless Matt explicitly chooses it
- `n/a`: no buildable task

## If The Console Shows Only A Weak Task

Check the active milestone:

```bash
cat mmi/project_brain/mission/milestone_map.md
cat mmi/project_brain/status/active_task.md
```

Then either:

- pick a stronger milestone task, or
- explicitly accept the weak task as cleanup

## Guardrails

- The console is advisory only.
- A score is not authorization.
- Matt still signs contracts and authorizes production wiring.
- Cursor should not build without signed authority.
- Promotion review is not a rebuild.

