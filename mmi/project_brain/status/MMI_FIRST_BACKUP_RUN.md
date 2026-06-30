# MMI First Backup Run

Date: 2026-06-29  
Authority: Matt (Super)  
Recorded by: Cursor PM  
Task: `mmi-first-backup-run`

---

## Command

```bash
cd /mnt/c/Architectapp_clean
python scripts/mmi_cold_backup.py --manifest
```

Manifest saved to: `mmi/project_brain/status/MMI_BACKUP_MANIFEST.json`

---

## Result

| Field | Value |
|-------|-------|
| Mode | `manifest` |
| Source root | `C:/Architectapp_clean` |
| Files in backup set | **31** |
| Cloud upload | **None** |
| `tasks.json` mutated | **No** |

---

## Key files verified in manifest

| Path | Purpose |
|------|---------|
| `tasks.json` | Local queue source of truth |
| `mmi/command_center.py` | Command center |
| `mmi/project_brain/` | Project brain (mission, architecture, status) |
| `scripts/mmi_cold_backup.py` | Backup helper |
| `scripts/reload_mmi_pipes.py` | Pipe reload + auto-seed |
| `scripts/keep_task_queue_warm.py` | Pipeline warmer |
| `CODEX.md` | Codex scope override |

---

## Exclusions (confirmed)

- No `web/`, `ops/run.py`, secrets, or NorthStar paths in manifest
- No cloud API calls during manifest generation

---

## Optional next steps (Matt approval)

| Step | Command | Requires |
|------|---------|----------|
| Local archive | `python scripts/mmi_cold_backup.py --archive /tmp/mmi_backup.tar.gz` | Output path only |
| Restore drill | `python scripts/mmi_cold_backup.py --restore-check /path/to/restored` | Restored copy |
| Cloud cold mirror | Not run yet | Matt picks provider per `MMI_LOCAL_CLOUD_POLICY.md` |

---

## Status

First local manifest run **PASS**. MMI cold-backup layer is operational on the Mini PC.
