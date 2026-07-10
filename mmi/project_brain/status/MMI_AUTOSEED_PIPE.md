# MMI Auto-Seed Pipe

Last updated: 2026-07-01

## Problem (fixed)

The queue went **DRY** after every task completion because `keep_task_queue_warm.py` only knew bootstrap tasks and a one-time hold. Nothing seeded the next bounded step automatically.

## Pipeline warm rule (2026-07)

**No silent DRY.** After every closeout, Cursor PM must seed the next Matt-approved pending task **or** record an explicit DRY reason. See **`mmi/project_brain/status/MMI_PIPELINE_WARM_RULE_2026-07.md`**.

Staging record: **`mmi/project_brain/status/MMI_PIPE_STAGING.json`** (updated by warmer on seed/peek).

Seeded tasks default to `build_authorization: NOT_AUTHORIZED` — seeding is not build authorization.

## How it works now

1. **`mmi/task_pipeline.json`** — ordered list of MMI tasks (source of truth for what comes next)
2. **`scripts/reload_mmi_pipes.py`** — calls warmer; auto-seeds first incomplete pipeline entry when dry
3. **`scripts/complete_task.py`** — mark done + auto-seed in one command (for Codex/agents)

## Commands

```bash
cd /mnt/c/MMI

# After any task completion — auto-seeds next pipeline task
python scripts/complete_task.py TASK_ID --by "Codex" --summary "..." --output path/to/output --report-card path/to/report_card.md

# Or reload only
python scripts/reload_mmi_pipes.py

# Preview next seed without writing
python scripts/keep_task_queue_warm.py --peek
```

## Adding future work

Append **one** new entry to `mmi/task_pipeline.json`, then run `reload_mmi_pipes.py`. Do not hand-edit `tasks.json` for seeding unless completing a task.

When the pipeline tail (`mmi-pipeline-refresh`) completes, Cursor PM extends `task_pipeline.json` with the next Matt-approved task.

## Still DRY?

- Pipeline exhausted and tail not completed → run reload after PM updates pipeline file
- Active task stuck in `paused` on a pipeline id → resolve or skip in pipeline file
- Matt hold on `mmi-await-matt-phase2` paused → intentional HOLD (legacy)
