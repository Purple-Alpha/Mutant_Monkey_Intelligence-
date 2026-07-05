# MMI Deployer Queue Check

Last updated: 2026-07-01

## Verdict

**PASS** — Local deployer commands emit MMI-only active work with task id, score, and assignee. Active task routes to **Codex** (not Cursor PM by default). Non-MMI tasks remain paused or completed.

## Active task (2026-07-01)

| Field | Value |
|-------|--------|
| Task | `mmi-quality-slice-p1-closeout-gate` |
| Assignee | **Codex** |
| Tier | Backbone / runtime support |
| Build auth | **NOT_AUTHORIZED** (see `tasks.json`) |
| Cursor PM role | Route/monitor/closeout hygiene only |

Live `next_task.py`:

```text
TASK: mmi-quality-slice-p1-closeout-gate
SCORE: 88
GOES TO: Codex (Backbone / runtime support)
```

See `MMI_ACTIVE_TASK_ROUTING_P1_2026-07.md` and `MMI_LANE_ROUTING.md` § Active task routing — P1.

**Warning:** `task_runner.py` prints `EXECUTING:` for any pending task — Cursor PM must **not** use it to auto-run Codex-assigned backbone work.

## Commands Checked

| Command | Role | Result |
|---|---|---|
| `python3 scripts/next_task.py` | Primary next-task reader | PASS |
| `python3 scripts/keep_task_queue_warm.py` | Queue seeder when dry | PASS |
| `python3 task_runner.py` | Local task monitor / auto-runner | PASS (format); see notes |

## `next_task.py` — PASS

Verified output fields:

- `TASK` — task id
- `SCORE` — numeric priority
- `GOES TO` — assignee and tier
- `WORK` — full instruction

Live run (2026-06-28):

```
TASK: mmi-queue-deployer-check
SCORE: 92
GOES TO: Cursor PM (Project Manager)
WORK: PROJECT: MMI. Verify the local deployer and next-task command only emit MMI tasks ...
```

Selection logic: first task in `tasks.json` whose status is in `{pending, queued, todo, in-progress, in_progress}`. No score-based sort.

## `task_runner.py` — PASS (format)

For each pending task, prints:

```
NEXT TASK: <id> | SCORE: <score> | GOES TO: <assignee>
EXECUTING: <instruction>
```

Uses `scripts.keep_task_queue_warm.seed_if_dry()` when no pending tasks exist, so the pipe stays loaded with MMI backlog seeds.

**Note:** `task_runner.py` auto-marks tasks completed without `completed_by`, `result_summary`, or `output_files`. Cursor PM should use the manual completion protocol in `tasks.json` when finishing PM tasks by hand.

## `keep_task_queue_warm.py` — PASS

Fixed backlog (all MMI, all Cursor PM):

| id | score | status in queue |
|---|---|---|
| `mmi-active-scope-lock` | 100 | completed |
| `mmi-queue-deployer-check` | 92 | pending (this check) |
| `mmi-next-work-packet` | 85 | not yet seeded |

Fallback seed (only when entire queue is finished): instruction is `PROJECT: MMI` and output is `MMI_NEXT_SAFE_TASK.md`. Id prefix `phase1-next-safe-increment-*` is legacy naming only; content is MMI-only.

## Pipe status (2026-07-01)

**Rule:** `mmi/project_brain/status/MMI_PIPELINE_WARM_RULE_2026-07.md` — no silent DRY.

**Current:** `LOADED` — `mmi-promote-latest-good-stub-110548` | **Matt** | manual stub update  
**Restore-check `110548`:** PASS | **validate-promotion:** ALLOWED  
**Last B2 mirror:** `mmi_backup_20260701_104504.tar.gz` (P1–P5)  
**Last B2 mirror:** `mmi_backup_20260701_103517.tar.gz` (P1–P4)  
**Restore-proven:** `mmi_backup_20260630_163709.tar.gz`  
**Last B2 mirror:** `mmi_backup_20260630_195144.tar.gz` (P1 + P2 gates + tests)  
**Last B2 mirror:** `mmi_backup_20260630_194435.tar.gz` (P1 gate + tests)

Staging file: `mmi/project_brain/status/MMI_PIPE_STAGING.json`


| id | status | MMI? | Surfaced? |
|---|---|---|---|
| `1` (legacy website/DAX) | completed | no | no |
| `phase1-stability-audit` | paused | no | no |
| `mmi-active-scope-lock` | completed | yes | no |
| `mmi-queue-deployer-check` | pending | yes | **yes — current active** |

`phase1-stability-audit` is correctly paused with score_reason noting MMI-only scope. It will not be emitted unless status is changed back to pending.

## Guardrails (do not relax)

1. Keep non-MMI tasks (`phase1-stability-audit`, legacy DAX/Trades entries) in `paused` or `completed` status — never `pending`.
2. Do not run legacy seeders (`strategist.py`) that write open-ended tasks into `tasks.json`.
3. `next_task.py` does not filter by project name; queue curation is the guardrail.
4. `ops/council_daemon.py` uses Supabase `task_queue`, not local wiring — out of scope for local MMI deployer check unless Matt reactivates that lane.

## Conclusion

Local deployer path is locked to MMI for active work. Social Architect Phase 1, DAX, and Trades are not reactivated. Next seeded task after this check: `mmi-next-work-packet`.

## Follow-up (2026-06-28)

Codex reported deployer script syntax check **PASS**. Cursor PM verified:

```
python3 -m py_compile scripts/next_task.py scripts/keep_task_queue_warm.py task_runner.py
→ SYNTAX OK
```
