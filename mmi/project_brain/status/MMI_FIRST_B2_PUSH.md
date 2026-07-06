# MMI First B2 Cold Push

Date: 2026-06-28  
Authority: Matt (Super)  
Status: **OPERATIONAL**

---

## Approved stack

| Piece | Value |
|-------|--------|
| Provider | Backblaze B2 |
| Operator | rclone (WSL) |
| Remote | `matt:` |
| Bucket path | `mmi-cold-storage/archives/` |
| Policy | Local-first; cloud = cold mirror only |

Matt authorized automated push after first manual success.

---

## First manual push (2026-06-28)

```bash
python scripts/mmi_cold_backup.py --archive /tmp/mmi_backup.tar.gz
rclone copy /tmp/mmi_backup.tar.gz matt:mmi-cold-storage/archives/ --checksum -v
```

Result: `41519` bytes transferred, file visible on B2.

---

## Automated push (recommended)

One command — local archive + checksum push + verify + log:

```bash
cd /mnt/c/MMI
python scripts/mmi_cold_backup.py --backup-and-push
```

Optional custom path:

```bash
python scripts/mmi_cold_backup.py --archive /tmp/mmi_backup.tar.gz --push matt:mmi-cold-storage/archives/
```

Push existing archive only:

```bash
python scripts/mmi_cold_backup.py --push-archive /tmp/mmi_backup.tar.gz --push matt:mmi-cold-storage/archives/
```

Push log: `mmi/project_brain/status/MMI_BACKUP_PUSH_LOG.json`

---

## Safety guardrails

- No upload without `--push` or `--backup-and-push`
- Allowed remotes: `matt:` and `matt-crypt:` only
- `rclone --checksum` by default
- Post-push size verification on remote
- Never mutates `tasks.json`
- rclone credentials stay in `~/.config/rclone/rclone.conf` only

---

## Not yet implemented

- `matt-crypt` encrypted remote (recommended before scaling sensitive archives)
- Scheduled/cron backup (still on-demand by design)
