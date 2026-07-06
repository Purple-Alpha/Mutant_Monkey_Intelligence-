# MMI Cold-Storage Backup Spec

Last updated: 2026-06-28T18:32:59-07:00  
Authority: Matt (Super)  
Owner: Codex (Backbone / runtime support)  
Source task: `mmi-backup-cold-storage-spec`

---

## Purpose

Define the first MMI cold-storage backup layer.

MMI remains local-first. The Mini PC workspace is the source of truth for `tasks.json`, `mmi/project_brain/`, execution, and the local command center. Cloud is allowed only as a redundant mirror for recovery.

This spec does not create a hosted database, live cloud queue, hosted runtime, or NorthStar bridge.

---

## Policy Summary

Source: `mmi/project_brain/architecture/MMI_LOCAL_CLOUD_POLICY.md`

| Decision | Rule |
|---|---|
| Source of truth | Local files in `C:\MMI` / `/mnt/c/MMI` |
| Queue state | Local `tasks.json` only |
| Project brain | Local `mmi/project_brain/` only |
| Cloud role | Cold mirror only |
| Allowed backup routes | Private git remote or encrypted file sync |
| Hosted DB / live queue | Not allowed |
| NorthStar relationship | Isolated; no bridge, copy, or dependency |

---

## Backup Scope

### Required backup set

Back up these files/directories:

| Path | Reason |
|---|---|
| `tasks.json` | Local queue source of truth |
| `mmi/project_brain/` | Mission, architecture, lane, and status memory |
| `CODEX.md` | Current Codex scope override |
| `AGENTS.md` | Contains top-level MMI override notice |
| `scripts/next_task.py` | Queue inspection command |
| `scripts/reload_mmi_pipes.py` | Pipe reload/status command |
| `scripts/keep_task_queue_warm.py` | Queue warmer/hold behavior |
| `scripts/mmi_cold_backup.py` | Local cold backup helper |
| `mmi/command_center.py` | Local command center runtime |

### Optional backup set

Back up only if Matt asks:

| Path | Reason |
|---|---|
| `logs/` | May contain useful execution evidence, but can be noisy |
| `docs/` | Mixed legacy content; not required for MMI source of truth |
| root handoff files | Legacy-heavy; only include if needed for recovery history |

### Explicitly excluded

Do not back up as part of the MMI cold-storage layer:

| Path / system | Reason |
|---|---|
| `web/` | Social Architect lane, not active MMI |
| `ops/run.py` and Social Architect operator files | Not part of MMI runtime |
| `node_modules/`, build outputs, caches | Rebuildable/noisy |
| API key files, tokens, secrets | Do not mirror secrets into cold storage |
| `/home/socialarchitect/northstar` | Separate project; no bridge |
| hosted database state | Not allowed by local-first policy |

---

## Backup Modes

### Mode A: Private git remote

Use a private remote as a cold mirror of the allowed backup set.

Properties:

- Local repo remains source of truth.
- Push is manual or scheduled from the Mini PC.
- Remote is not a task runner.
- Remote is not used by agents as live state.
- Restore is `git clone` or `git fetch` into a clean local directory.

Use when:

- Matt wants simple version history and remote redundancy.
- The backup target can safely store non-secret MMI files.

### Mode B: Encrypted file sync

Use an encrypted archive or encrypted sync target containing only the allowed backup set.

Properties:

- Local repo remains source of truth.
- Cloud provider sees encrypted data only.
- Restore requires the encryption key/passphrase.
- No live queue or cloud runtime exists.

Use when:

- Matt wants cold storage but does not want readable MMI files in a remote.
- Backup target is a generic cloud drive or object bucket.

---

## Minimal Backup Manifest

The first backup script should maintain a plain manifest so restores can be verified.

Suggested future path:

`mmi/project_brain/status/MMI_BACKUP_MANIFEST.json`

Suggested shape:

```json
{
  "created_at": "2026-06-28T18:32:59-07:00",
  "source_root": "/mnt/c/MMI",
  "mode": "dry-run",
  "files": [
    {
      "path": "tasks.json",
      "sha256": "<hash>",
      "bytes": 12345
    }
  ]
}
```

The manifest is for verification only. It must not become a queue, database, or source of truth.

---

## Restore Drill

Run this drill before trusting any backup path.

1. Create a clean restore directory outside the active workspace.
2. Restore only the required backup set.
3. Confirm these files exist:
   - `tasks.json`
   - `mmi/project_brain/status/MMI_ACTIVE_SCOPE.md`
   - `mmi/project_brain/architecture/MMI_LOCAL_CLOUD_POLICY.md`
   - `mmi/command_center.py`
   - `scripts/next_task.py`
   - `scripts/reload_mmi_pipes.py`
   - `scripts/mmi_cold_backup.py`
4. Run JSON validation:
   ```bash
   python3 -m json.tool tasks.json >/tmp/mmi_restore_tasks_check.out
   ```
5. Run syntax checks:
   ```bash
   python3 -m py_compile mmi/command_center.py scripts/next_task.py scripts/reload_mmi_pipes.py scripts/keep_task_queue_warm.py scripts/mmi_cold_backup.py
   ```
6. Run the command center from the restored directory:
   ```bash
   python3 mmi/command_center.py
   ```
7. Confirm the panel reports one of:
   - `LOADED` with an MMI task
   - `HOLD`
   - `DRY`
   - `BLOCKED` only if the restored queue really has a malformed/non-MMI active task
8. Confirm no restored process calls cloud services, hosted DBs, `npm`, `web/`, `ops/run.py`, or NorthStar.

Restore success means the local command center and queue inspection tools can read the restored local files without cloud participation.

---

## Minimal Local Script Outline

Suggested future file:

`scripts/mmi_cold_backup.py`

The first implementation should be local and conservative.

### Supported commands

```bash
python3 scripts/mmi_cold_backup.py --dry-run
python3 scripts/mmi_cold_backup.py --manifest
python3 scripts/mmi_cold_backup.py --archive /tmp/mmi_backup.tar.gz
python3 scripts/mmi_cold_backup.py --restore-check /path/to/restored/MMI
```

### Responsibilities

| Function | Responsibility |
|---|---|
| `backup_paths()` | Return the required allowlist |
| `excluded_paths()` | Return explicit denylist patterns |
| `walk_backup_set(root)` | Collect allowed files only |
| `sha256_file(path)` | Hash files for manifest |
| `build_manifest(files)` | Emit verification metadata |
| `write_archive(files, output)` | Create local archive |
| `restore_check(path)` | Validate restored files and syntax |
| `main()` | Parse flags and run one action |

### Guardrails

The script must:

- default to `--dry-run` style behavior unless an output path is provided
- never mutate `tasks.json`
- never create or change active tasks
- never upload by itself in the first version
- never include secrets
- never read NorthStar
- never call hosted DBs or cloud APIs

Cloud push/sync, if ever added, must be a separate Matt-authorized task.

---

## Verification Commands

Run from repo root:

```bash
cd /mnt/c/MMI
python3 mmi/command_center.py
python3 -m json.tool tasks.json >/tmp/tasks_json_check.out
```

Future script verification:

```bash
python3 scripts/mmi_cold_backup.py --dry-run
python3 scripts/mmi_cold_backup.py --manifest
python3 scripts/mmi_cold_backup.py --restore-check /tmp/mmi_restore_test
```

---

## Hard Stops

- No hosted DB.
- No live cloud queue.
- No cloud runtime.
- No NorthStar bridge.
- No `npm`.
- No `web/`.
- No `ops/run.py`.
- No secrets in backup.
- No cloud upload until Matt explicitly approves provider, destination, and encryption posture.

---

## Next Bounded Task Recommendation

After Matt reviews this spec, the next Codex task can be:

`mmi-cold-backup-script`

Required output:

`scripts/mmi_cold_backup.py`

Scope:

Implement only local dry-run, manifest, archive creation, and restore-check behavior. Do not upload to cloud.
