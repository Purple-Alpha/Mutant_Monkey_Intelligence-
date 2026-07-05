# MMI Restore Drill — 2026-06

**Drill ID:** `mmi-restore-drill-quarterly`  
**Executed:** 2026-06-30  
**Executor:** Cursor PM  
**Authority:** Phase 6 drill A7 gap (`DRILL_WORKSHEET_2026-06-30.md`); CCCS ITSAP.40.004 — recovery tested in isolated environment (no production `mmi/` mutation)

---

## Objective

Validate that the latest known-good B2 cold archive restores into a repo-shaped tree and passes `scripts/mmi_cold_backup.py --restore-check`.

---

## Archive Used

| Field | Value |
|-------|-------|
| File | `mmi_backup_20260629_190227.tar.gz` |
| Local path (WSL) | `/tmp/mmi_backup_20260629_190227.tar.gz` |
| Archive bytes | 73,193 |
| Archive SHA-256 | `db9d0e84b7e4ed3af574c78c6c663154ae78691fb4989e3538590d9378e66e07` |
| Push log entry | `MMI_BACKUP_PUSH_LOG.json` — `2026-06-30T02:02:27Z` PASS |
| B2 remote | `matt:mmi-cold-storage/archives/` |

---

## Isolated Restore Procedure

1. Created scratch directory (outside git tracking): `C:\Architectapp_clean\_restore_drill_scratch\`
2. Extracted archive into scratch (WSL tar, no live tree touched):
   ```bash
   tar -xzf /tmp/mmi_backup_20260629_190227.tar.gz -C /mnt/c/Architectapp_clean/_restore_drill_scratch
   ```
3. Ran restore validation:
   ```bash
   python scripts/mmi_cold_backup.py --restore-check C:\Architectapp_clean\_restore_drill_scratch
   ```

### Terminal output (`--restore-check`)

```json
{
  "restore_root": "C:/Architectapp_clean/_restore_drill_scratch",
  "status": "PASS",
  "errors": []
}
```

---

## Artifact Verification (scratch tree)

| Artifact | Restored | Notes |
|----------|----------|-------|
| `tasks.json` | Yes | 34,673 bytes (matches push log) |
| `mmi/command_center.py` | Yes | Present; syntax check passed |
| `mmi/project_brain/**/*.md` | Yes | 35 markdown files restored |
| `scripts/mmi_cold_backup.py` | Yes | Present; syntax check passed |
| `scripts/next_task.py` | Yes | Present |
| `scripts/reload_mmi_pipes.py` | Yes | Present |
| `scripts/keep_task_queue_warm.py` | Yes | Present |
| `scripts/complete_task.py` | Yes | Present |
| `mmi/war_room.py` | **No** | Not in `BACKUP_ALLOWLIST` at backup time (2026-06-29); live file exists (7,889 bytes) but was shipped after last push |

---

## Verdict

| Check | Result |
|-------|--------|
| `--restore-check` | **PASS** |
| Required files per `RESTORE_REQUIRED_FILES` | All present |
| Python syntax compile | All checked files pass |
| `tasks.json` schema | Valid list |
| A7 gap (restore path tested) | **CLOSED** for this quarter |

---

## Follow-Up (non-blocking)

1. ~~Add `mmi/war_room.py` to `BACKUP_ALLOWLIST`~~ — **done** (`mmi-war-room-backup-allowlist-patch`, 2026-06-30). Run `--backup-and-push` so war room ships on next cold mirror; restore drill still required to prove recovery.
2. Add `_restore_drill_scratch/` to `.gitignore` if recurring drills use the same path.

---

## Cleanup

Scratch folder destroyed after validation (`Remove-Item -Recurse -Force _restore_drill_scratch`).

---

## Pipeline Context (same session)

- `mmi-intel-brief-template`: dependency patched — `RESEARCH_EVALUATOR_PASS_2026-06.md` replaced with `RESEARCH_VERIFICATION_2026-06.md`; status `ready` (unblocked, not active).
- `mmi-restore-drill-quarterly`: executed and closed by this evidence file.
