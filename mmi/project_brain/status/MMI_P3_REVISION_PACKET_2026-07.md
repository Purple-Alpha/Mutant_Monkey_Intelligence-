# P3 Revision Packet — War Room Truth Surface Incomplete

**Date:** 2026-07-01  
**From:** Matt (Super) via Cursor PM  
**To:** Codex  
**Task:** `mmi-quality-slice-p3-war-room-truth`  
**Verdict:** **PASS ON EXECUTION, FAIL ON REQUIRED TRUTH SURFACE COMPLETENESS**  
**Closeout:** **NOT READY**

---

## Current status

| Check | Result |
|-------|--------|
| `py_compile` | PASS |
| `war_room.py --no-seed` | runs |
| Active task / owner / lane map / latest B2 push | visible |

---

## Blocking gaps before P3 closeout

1. War room does not show `build_authorization: NOT_AUTHORIZED` clearly enough.
2. `NEXT ACTION` incorrectly implies Codex should execute while build auth is not authorized.
3. War room does not show latest-good **restore-proven** archive separately from latest B2 mirror.
4. War room does not show restore-check status.
5. War room does not show OPSEC-4/5/9 as NOT_STARTED / known operator-risk.
6. War room does not show intel gate status / source-status summary.
7. War room does not show latest chaos level status.
8. War room does not show the key distinction: **latest B2 mirror ≠ restore-validated archive** unless restore-check passed.

---

## Required correction

**Update `mmi/war_room.py` display only.** No enforcement changes.

May read (read-only parsers):

- `mmi/project_brain/status/MMI_PIPE_STAGING.json`
- `mmi/project_brain/backup/MMI_LATEST_GOOD_ARCHIVE.md`
- `mmi/project_brain/status/MMI_LATEST_GOOD_ARCHIVE_VALIDATION_2026-07.md`
- `mmi/project_brain/status/MMI_BACKUP_PUSH_LOG.json`
- `mmi/project_brain/opsec/OPERATOR_OPSEC_CHECKLIST.md`
- `mmi/project_brain/chaos/MMI_CHAOS_L3-04_*.md`, `MMI_CHAOS_L3-06_*.md`, `MMI_CHAOS_LEVEL3_PLAN_2026-07.md`
- `scripts/mmi_verify.py` (invoke or parse intel-briefs status — read-only)

**Also fix `next_action` truth:** when `build_authorization` is `NOT_AUTHORIZED` and assignee is Codex, war room must **not** say Codex executes. Prefer fixing in `war_room.py` render layer or `command_center.next_action_for` if war room delegates there — display only, no enforcement.

---

## Expected display additions

```text
BUILD AUTH:        NOT_AUTHORIZED
NEXT ACTION:       Awaiting Matt build authorization for Codex.

LATEST B2 MIRROR:  mmi_backup_20260630_195144.tar.gz
RESTORE-PROVEN:    mmi_backup_20260630_163709.tar.gz
RESTORE-CHECK:     PASS for 163709

OPSEC KNOWN RISK:  OPSEC-4/5/9 NOT_STARTED
INTEL GATES:       P2 / G-INTEL active; live briefs clean
CHAOS:             L3-06 and L3-04 complete + mirrored; L3-05 paused; Level 4 prohibited

NOTE: Latest B2 mirror ≠ restore-validated archive unless restore-check passed.
      Seeded/pending ≠ build authorization.
```

---

## Source values (PM-confirmed)

| Field | Value |
|-------|--------|
| Latest B2 mirror | `mmi_backup_20260630_195144.tar.gz` (SHA `1a288271…`) |
| Restore-proven archive | `mmi_backup_20260630_163709.tar.gz` (SHA `49cf9e24…`) |
| Restore-check | PASS — see `MMI_LATEST_GOOD_ARCHIVE_VALIDATION_2026-07.md` |
| OPSEC-4/5/9 | NOT_STARTED (known operator-risk) |
| Intel | P1 H1 + P2 G-INTEL enforced at closeout; `intel-briefs` PASS on live briefs |
| Chaos | L3-06 PASS WITH REVISIONS; L3-04 PASS WITH REVISIONS; L3-05+ PAUSED; Level 4 PROHIBITED |

---

## Hard stops (unchanged)

- No P4
- No L3-05
- No OPSEC state changes
- No live intel changes
- No B2 mutation during build
- No enforcement changes — **display only**

---

## Closeout criteria (when revision complete)

```bash
python -m py_compile mmi/war_room.py mmi/command_center.py
python mmi/war_room.py --no-seed
```

Matt + Cursor PM verify all eight blocking gaps resolved before `complete_task.py` closeout.

---

## PM note

Task remains `pending` / `NOT_AUTHORIZED` until Matt separately authorizes build **or** confirms revision delivery under existing auth. Do not close P3 until truth surface is complete.
