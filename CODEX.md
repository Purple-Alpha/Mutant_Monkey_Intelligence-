# Codex Scope Override

## Active Project

The active project is MMI only.

Repo root:

- Windows: `C:\MMI`
- WSL: `/mnt/c/MMI`

Do not infer active scope from legacy repo-root files. This repository still contains old Social Architect material, but current work is controlled by the MMI project brain.

## Authority Order

For MMI work, follow these files before any root-level handoff, role, or swarm document:

1. `mmi/project_brain/status/MMI_MMS_CUSTODY_MAINTENANCE_2026-07.md`
2. `mmi/project_brain/status/MMI_ACTIVE_SCOPE.md`
3. `mmi/project_brain/status/MMI_BUILD_AND_PRESERVATION_AUTHORITY_LAWS_20260707.md`
4. `mmi/project_brain/status/MMI_PHASE2_START.md`
5. `mmi/project_brain/architecture/MMI_PHASE2_MVP_ARCHITECTURE.md`
6. `mmi/project_brain/status/MMI_LANE_ROUTING.md`
7. `tasks.json`

If those files conflict with `AGENTS.md`, `CLAUDE.md`, `CURRENT_PROJECT_HANDOFF.md`, `PROGRESS.md`, `HANDSHAKE_LEDGER.md`, `ops/run.py`, or `web/`, the MMI project-brain files win.

## Required Task Completion (mandatory)

After finishing any MMI task, **always** run one of these from repo root:

```bash
cd /mnt/c/MMI
python3 scripts/complete_task.py TASK_ID --by "Codex" --summary "..." --output path/to/output --report-card path/to/report_card.md
```

Or if you already edited `tasks.json` manually:

```bash
python3 scripts/reload_mmi_pipes.py
```

**Never** stop after marking a task completed without running one of the above. Otherwise the pipe goes DRY until someone reloads.

Pipeline source of truth for what comes next: `mmi/task_pipeline.json`

## Cold backup push (Matt approved 2026-06-28)

After meaningful changes to brain or `tasks.json`:

```bash
cd /mnt/c/MMI
python scripts/mmi_cold_backup.py --backup-and-push
```

See `mmi/project_brain/status/MMI_FIRST_B2_PUSH.md`.

## Required Startup Check

Before doing MMI work, run:

```bash
cd /mnt/c/MMI
python3 scripts/reload_mmi_pipes.py
python3 scripts/next_task.py
```

If the task is not MMI-prefixed or does not start with `PROJECT: MMI.`, stop and report the mismatch.

## Current Hard Stops

- MMI only.
- Maintenance freeze is active: no product feature work until the custody-maintenance ledger closes and Matt explicitly lifts the freeze.
- Cursor has no current PM or repository-control authority. Historical Cursor records remain evidence of prior work only.
- Do not run `npm`.
- Do not run `ops/run.py`.
- Do not edit `web/`.
- Do not route active work to Social Architect Phase 1, DAX, Trades, SAGE, MAVEN, or HAVEN unless Matt explicitly reactivates that lane.
- Do not use `/home/socialarchitect/northstar` for this task queue.

## Mandatory Authority Laws - 2026-07-07

All agents must read and obey mmi/project_brain/status/MMI_BUILD_AND_PRESERVATION_AUTHORITY_LAWS_20260707.md before selecting a next lane, committing/pushing, proposing build work, running audits, or closing a session.

Key binding points:

- Evidence decides the next lane; Matt is not asked to choose when rubric evidence decides.
- Every next lane must name the primary model, secondary review model, execution operator, forbidden tools, and ownership reason.
- Daily backup, commit, push, and remote-head verification are preservation law, not optional hygiene.
- No build, execution, cleanup, delete, reset, force-push, kernel/minifilter/IOCTL testing, or restore-check script execution without explicit Matt authorization.
- Accepted artifacts must be committed and pushed, or explicitly listed as intentionally untracked/quarantine. No silent loose files.
