# MMI Pipeline Warm Rule — 2026-07

**Date:** 2026-07-01  
**Authority:** Matt (Super)  
**Maintained by:** Cursor PM  
**Status:** **Active doctrine** — no silent DRY

---

## Problem

```text
Task completes → pipe goes DRY → Matt reconstructs next step from memory
```

That is operator friction, not streamlining. MMI must stay **staged and ready** without stealing build authority.

---

## Target model

```text
Task completes → MMI proposes next eligible task → Matt approves or rejects → queue stays warm
```

**Not:** autonomous execution · auto-build · Cursor absorbing non-PM lanes

**Yes:** always-ready next-task staging with explicit assignee, scope, and `build_authorization`

```text
Bad:   Pipeline DRY and Matt must remember what's next
Good:  DRY only when Matt intentionally parks all lanes
Great: Always a proposed next task OR an explicit DRY reason on record
```

---

## Standing rule (mandatory)

After **every** task closeout, Cursor PM must **either**:

1. **Seed** the next Matt-approved pending task in `tasks.json` with:
   - correct `assignee` (lane owner — not default Cursor)
   - `build_authorization: NOT_AUTHORIZED` (unless Matt already authorized build)
   - `routing_note` when assignee ≠ Cursor PM  
   **or**

2. **Record** an explicit DRY reason, e.g.:
   - `INTENTIONAL_PAUSE_BY_MATT`
   - `PIPELINE_EXHAUSTED_AWAITING_PM_EXTEND`
   - `BLOCKED_ON_MATT_DECISION`

**No silent DRY.**

Staging record: `mmi/project_brain/status/MMI_PIPE_STAGING.json` (updated by `keep_task_queue_warm.py` / closeout seed path).

---

## Authority distinctions (non-negotiable)

| State | Meaning |
|-------|---------|
| `pending` / seeded | Task is **proposed** and queue-ready |
| `build_authorization: NOT_AUTHORIZED` | **No code changes** — not permission to build |
| `build_authorization: AUTHORIZED_BY_MATT_<date>` | Assigned lane may implement **that task only** |
| `assignee: Codex` | Cursor PM **routes** — does not implement by default |
| `completed_by: Codex` | Backbone lane executed; Cursor PM verifies closeout hygiene |

```text
Seeding ≠ build authorization
Pending ≠ execution
Assignee controls routing
Matt remains final authority
```

---

## Pipe display semantics

| `MMI_PIPE_STAGING.json` `pipe` | Meaning |
|-------------------------------|---------|
| `LOADED` | Active pending task exists |
| `READY` | Next candidate staged (see `next_task`) |
| `DRY` | No pending task — **`reason` required** |

Example **READY**:

```json
{
  "pipe": "LOADED",
  "reason": "active pending task",
  "active_task_id": "mmi-p1-closeout-gate-tests",
  "assignee": "Codex",
  "build_authorization": "NOT_AUTHORIZED"
}
```

Example **explicit DRY**:

```json
{
  "pipe": "DRY",
  "reason": "INTENTIONAL_PAUSE_BY_MATT",
  "next_candidate": null
}
```

---

## Cursor PM closeout checklist

After `complete_task.py` (any lane):

1. Confirm `closeout_verification` recorded when applicable (P1+ gates).
2. Run seed path (`seed_if_dry` via `complete_task` or `reload_mmi_pipes.py`).
3. If seed fails → write/update `MMI_PIPE_STAGING.json` with explicit `reason`.
4. If assignee ≠ Cursor PM → prepare handoff; **do not implement**.
5. Extend `mmi/task_pipeline.json` when tail consumed — before pipe goes silent.

---

## Current staged next task (2026-07-01)

| Field | Value |
|-------|--------|
| Pipe | **LOADED** |
| Active task | `mmi-promote-latest-good-stub-110548` (Matt manual) |
| Restore-check | `110548` **PASS** |
| Promotion helper | **ALLOWED** |
| Last B2 | `mmi_backup_20260701_110548.tar.gz` |

---

## Hard stops (unchanged)

- MMI only · local-first · advisory-only
- No NorthStar bridge · no Social Architect swarm hierarchy
- No SOAR/EDR/auto-containment
- Level 3 paused until separately authorized
- OPSEC-4/5/9 state changes only with Matt habit evidence

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | No silent DRY rule + P1 tests task staged |
