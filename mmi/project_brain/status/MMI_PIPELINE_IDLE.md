# MMI Pipeline Idle

Date: 2026-06-28  
Authority: Matt (Super)  
Recorded by: Cursor PM

---

## Status

**Phase-2 core pipeline is caught up.** All Codex increments through cold-backup script are complete.

| Increment | Task | Status |
|-----------|------|--------|
| 1 | Command-center spec | completed |
| 2 | `mmi/command_center.py` | completed |
| 3 | Backup spec | completed |
| 4 | `scripts/mmi_cold_backup.py` | completed |

---

## Why DRY appeared

Codex marked `mmi-cold-backup-script` completed in `tasks.json` but **did not run** `complete_task.py` or `reload_mmi_pipes.py`. The next pipeline step was not seeded until reload ran.

**Fixed:** `CODEX.md` now requires completion + reload. `mmi/command_center.py` auto-seeds from pipeline on every run.

---

## Next seeded work (no Matt approval needed)

~~`mmi-first-backup-run`~~ — **completed 2026-06-29.** See `MMI_FIRST_BACKUP_RUN.md` and `MMI_BACKUP_MANIFEST.json`.

---

## Current pipe

**DRY** — all pipeline entries complete. Append the next task to `mmi/task_pipeline.json`, then run `python mmi/command_center.py` (auto-seeds).

| Decision | Notes |
|----------|-------|
| Cloud backup provider | Private git remote vs encrypted sync — cold mirror only per `MMI_LOCAL_CLOUD_POLICY.md` |
| Next product feature | Beyond command center + local backup tooling |

Matt does **not** need to design architecture. Pick provider when ready; Cursor PM will append one pipeline entry.

---

## Operator commands

```bash
cd /mnt/c/Architectapp_clean
python mmi/command_center.py          # auto-seeds if dry
python scripts/reload_mmi_pipes.py    # same seed logic
python scripts/keep_task_queue_warm.py --peek
```
