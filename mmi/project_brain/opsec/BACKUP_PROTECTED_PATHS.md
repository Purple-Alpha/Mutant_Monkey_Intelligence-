# MMI Backup Protected Paths — Human Review Artifact

Date: 2026-06-30  
Authority: Matt (Super) — Canadian operator  
Artifact ID: `OPSEC-BACKUP-PATHS`  
Status: **DRAFT — documentation only.** Defines protected backup scope for human review; does not enforce, block, or mutate live systems.  
Lane: Security Intel / OpSec  
Linked brief: `intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md`  
Linked checklist items: `OPSEC-3`, `OPSEC-6`, `OPSEC-7`, `OPSEC-8` in `opsec/OPERATOR_OPSEC_CHECKLIST.md`

```yaml
control_plane_status: ADVISORY_ONLY
automation_status: NONE
review_mode: HUMAN_REVIEW_ONLY
enforcement_status: NONE
```

---

## 0. Purpose

This artifact documents which backup paths MMI treats as **protected scope** for operator review during incident triage, drill planning, and post-incident review (PIR). It answers: *what should exist in a cold backup, who may write or delete it, and what evidence proves a restore path is real.*

MMI can **surface linked OPSEC checks for human review**. This file does not automatically block deletion, isolate hosts, or trigger mitigation workflows.

---

## 1. Protected backup scope (local-first MMI)

Paths and objects included in the MMI cold-backup allowlist per `scripts/mmi_cold_backup.py` `BACKUP_ALLOWLIST`:

| Scope | Path / object | Role |
|-------|---------------|------|
| Task queue | `tasks.json` | Operator task state |
| Project brain | `mmi/project_brain/` | Intel, opsec, architecture, status |
| Pipeline | `mmi/task_pipeline.json` | Seeded task definitions |
| Authority docs | `AGENTS.md`, `CODEX.md` | Lane routing |
| MMI scripts | `scripts/next_task.py`, `scripts/reload_mmi_pipes.py`, `scripts/keep_task_queue_warm.py`, `scripts/complete_task.py`, `scripts/mmi_cold_backup.py` | Local-first tooling |
| Command center | `mmi/command_center.py` | Read-only CLI |
| War room | `mmi/war_room.py` | Read-only orient panel (monitor 2) |

**Allowlist patch (2026-06-30):** `mmi/war_room.py` added to `BACKUP_ALLOWLIST` via `mmi-war-room-backup-allowlist-patch`.

**Recoverability proof (2026-06-30):** Archive `mmi_backup_20260629_203555.tar.gz` pushed PASS to B2; isolated `--restore-check` PASS with `war_room.py` recovered (see `status/MMI_RESTORE_CHECK_WAR_ROOM_PROOF_2026-06.md`). `OPSEC-8` quarterly operator drill still separate.

**Cold mirror destination:** B2 via `matt:mmi-cold-storage/archives/` — push log at `mmi/project_brain/status/MMI_BACKUP_PUSH_LOG.json`.

---

## 2. Tools allowed to write / sync / delete

| Tool / actor | Allowed action | Human confirmation required |
|--------------|----------------|----------------------------|
| Matt (operator) | Run `python scripts/mmi_cold_backup.py --backup-and-push` | Yes — explicit command |
| Matt (operator) | Run restore drill to scratch folder (`--restore-check` on extracted tree) | Yes — isolated path only |
| `rclone` (Matt-initiated) | Copy archive to B2 cold path | Yes — only via backup script or explicit Matt command |
| Any process / agent | Delete or overwrite protected paths outside backup rotation | **No — treat as suspicious; human triage required** |
| MMI CLI (`command_center.py`, `war_room.py`) | Read-only display | N/A — no write authority |

No script in this repo is authorized to auto-delete backups, auto-purge B2 objects, or auto-rotate archives without Matt running the command.

---

## 3. Normal backup rotation vs suspicious deletion

| Signal | Likely normal | Likely suspicious — human review |
|--------|---------------|----------------------------------|
| New `mmi_backup_YYYYMMDD_HHMMSS.tar.gz` in B2 archives | Scheduled or Matt-initiated cold push | N/A if push log shows PASS |
| Local `/tmp/mmi_backup_*.tar.gz` overwritten | New backup run on same host | Unexpected if Matt did not run backup |
| `MMI_BACKUP_PUSH_LOG.json` new PASS entry | Documented push | Missing log entry after apparent push |
| Files under `mmi/project_brain/` deleted locally | Matt editing project brain | Mass deletion, encryption, or ransom note |
| B2 login / API key use | Matt cold push | Unknown session; correlate with `OPSEC-3` MFA check |
| Restore drill scratch folder removed after PASS | Expected cleanup per drill SOP | Deletion of only known-good archive with no replacement |

**Operator action:** open decision log (`OPSEC-9`), cross-check `intel/WAR_ROOM_SCORING_MATRIX_v2.md` §8 P1 backup/recovery signals, surface `OPSEC-6` / `OPSEC-7` / `OPSEC-8` for manual review. Do not assume MMI detected the event automatically.

---

## 4. Restore-drill evidence required

A protected backup path is **operationally unverified** until:

1. **OPSEC-8** — quarterly full restore drill: extract archive to isolated scratch, run `--restore-check`, open sample files, log in `intel/drills/`.
2. **OPSEC-7** — weekly integrity spot-check on most recent archive.
3. Drill worksheet references: `intel/drills/DRILL_2026-06-30_phase6_sim/`, `status/MMI_RESTORE_DRILL_2026-06.md` (one PASS on record; `OPSEC-8` `last_done` still blank until Matt fills).

An unrestored backup is an assumption, not a control (`MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md`).

---

## 5. B2 / rclone considerations

- **Local-first:** source of truth remains `C:\MMI` / `/mnt/c/MMI`; B2 is cold mirror only.
- **Credentials:** `rclone.conf` is denylisted from backup archives — never expect credentials inside a restore bundle.
- **Verification:** compare `archive_sha256` in push log to local archive before trusting remote copy.
- **Destructive remote actions** (delete remote archive, reconfigure remote): Matt-only; log decision if done during incident response.

---

## 6. MITRE techniques this artifact supports review for

Documentation links only — **not** proof that mitigation is implemented.

| Technique | Name | Review focus in this artifact |
|-----------|------|-------------------------------|
| T1486 | Data Encrypted for Impact | Offline/immutable copy exists outside encrypted host |
| T1490 | Inhibit System Recovery | Backup deletion / recovery inhibition — protected paths + B2 account |

Primary source: [MITRE ATT&CK](https://attack.mitre.org/) — technique IDs checked 2026-06-30.

---

## 7. Hard stops

- No runtime enforcement, auto-containment, endpoint agents, or live telemetry.
- No automatic checklist dispatch — operator opens linked `OPSEC-<n>` items manually.
- Mapping a MITRE technique to this artifact does not mean the control is `DONE`.
- Global vendor stats about backup targeting are not Canadian facts — see brief limitations.
- This artifact does not modify `scripts/mmi_cold_backup.py` `BACKUP_ALLOWLIST` at runtime.

---

## 8. Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-30 | Initial DRAFT — `mmi-wire-mitigation-refs`; human-review-only protected path scope |
