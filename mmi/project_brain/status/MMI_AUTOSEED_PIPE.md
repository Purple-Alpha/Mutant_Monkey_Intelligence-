# MMI Auto-Seed Pipe

Last updated: 2026-06-28

## Problem (fixed)

The queue went **DRY** after every task completion because `keep_task_queue_warm.py` only knew bootstrap tasks and a one-time hold. Nothing seeded the next bounded step automatically.

## How it works now

1. **`mmi/task_pipeline.json`** — ordered list of MMI tasks (source of truth for what comes next)
2. **`scripts/reload_mmi_pipes.py`** — calls warmer; auto-seeds first incomplete pipeline entry when dry
3. **`scripts/complete_task.py`** — mark done + auto-seed in one command (for Codex/agents)

## Commands

```bash
cd /mnt/c/Architectapp_clean

# After any task completion — auto-seeds next pipeline task
python scripts/complete_task.py TASK_ID --by "Codex" --summary "..." --output path/to/output

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
