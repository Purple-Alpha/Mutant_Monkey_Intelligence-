# MMI Latest-Good Archive Validation — 2026-07

**Task:** H3 closeout validation (Matt-authorized)  
**Executor:** Cursor PM  
**Date:** 2026-07-01  
**Target archive:** `mmi_backup_20260630_163709.tar.gz`  
**Authority stub:** `mmi/project_brain/backup/MMI_LATEST_GOOD_ARCHIVE.md`

---

## Sign-off

**PASS**

Tar spot-check and full isolated `--restore-check` both passed for `163709`. Archive extracts cleanly; restored scratch tree satisfies `mmi_cold_backup.py` restore-check logic (required files, valid `tasks.json`, Python syntax on restore-critical scripts). Level 3 chaos planning is **eligible for scoping** — not authorized to start without separate Matt authorization.

---

## Step 1 — Tar spot-check

| Check | Result |
|-------|--------|
| Archive located | **PASS** — `/tmp/mmi_backup_20260630_163709.tar.gz` (local WSL) |
| SHA256 vs H3 stub | **PASS** — `49cf9e247a08320f619f452237fbd0d233371339d1a1a778f067c87d3ef2a21b` |
| Archive bytes | **PASS** — 193,971 (matches push log) |
| `tar -tzf` readable | **PASS** — 101 member paths listed without error |
| Push log tail match | **PASS** — `MMI_BACKUP_PUSH_LOG.json` last entry |

### Required high-signal paths (10/10 present)

| Path | In archive |
|------|------------|
| `mmi/project_brain/backup/MMI_LATEST_GOOD_ARCHIVE.md` | Yes |
| `scripts/mmi_verify.py` | Yes |
| `mmi/project_brain/chaos/MMI_CHAOS_HARDENING_H1-H3_2026-07.md` | Yes |
| `mmi/project_brain/chaos/MMI_CHAOS_SANDBOX_V2_2026-07.md` | Yes |
| `mmi/project_brain/chaos/MMI_CHAOS_TABLETOP_V1_2026-07.md` | Yes |
| `mmi/project_brain/intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md` | Yes |
| `mmi/project_brain/intel/briefs/INTEL_polymorphic-ransomware-delivery_2026-07.md` | Yes |
| `mmi/project_brain/opsec/OPERATOR_OPSEC_CHECKLIST.md` | Yes |
| `tasks.json` | Yes |
| `mmi/task_pipeline.json` | Yes |

---

## Step 2 — Full isolated restore-check

**Executed:** 2026-07-01 (WSL)  
**Scratch:** `/tmp/mmi_restore_validate_163709` (removed after run)

| Check | Result |
|-------|--------|
| Pre-extract SHA256 | **PASS** — matches expected |
| `tar -xzf` extraction | **PASS** — no errors |
| `--restore-check` status | **PASS** — `errors: []` |
| Live tree overwritten | **No** |
| B2 mutated during check | **No** |
| OPSEC-4/5/9 changed | **No** |

### Commands run

```bash
SCRATCH=/tmp/mmi_restore_validate_163709
rm -rf "$SCRATCH" && mkdir -p "$SCRATCH"
tar -xzf /tmp/mmi_backup_20260630_163709.tar.gz -C "$SCRATCH"
cd /mnt/c/MMI
python3 scripts/mmi_cold_backup.py --restore-check "$SCRATCH"
rm -rf "$SCRATCH"
```

### Restore-check output

```json
{
  "restore_root": "/tmp/mmi_restore_validate_163709",
  "status": "PASS",
  "errors": []
}
```

### What restore-check validated

- Required files present (`tasks.json`, scope/policy docs, core scripts)
- `tasks.json` parses as JSON list
- Python syntax on: `command_center.py`, `next_task.py`, `reload_mmi_pipes.py`, `keep_task_queue_warm.py`, `complete_task.py`, `mmi_verify.py`, `mmi_cold_backup.py`

**Note:** Prior proof on `mmi_backup_20260629_203555.tar.gz` (`MMI_RESTORE_CHECK_WAR_ROOM_PROOF_2026-06.md`) does not substitute for this run.

---

## Hard stops honored

- Live tree not overwritten
- B2 not mutated during restore-check (B2 push of this validation note authorized separately after PASS)
- Level 3 not started
- OPSEC-4/5/9 not changed

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | Tar spot-check PASS — 10/10 required paths |
| 1.1 | 2026-07-01 | Full isolated `--restore-check` PASS on `163709` — sign-off upgraded to PASS |

---

## B2 mirror (post-validation)

| Field | Value |
|-------|--------|
| Archive | `mmi_backup_20260630_164111.tar.gz` |
| SHA256 | `456d38e3730fba9a48adf76192d7faa311c8170ccfde3848fb0e6406eb0cb2a4` |
| Bytes | 195,998 |
| Push status | PASS |
| Remote | `matt:mmi-cold-storage/archives/` |
| Purpose | Mirrors this validation note + updated H3 stub restore-check status |

**Note:** Restore-check proof above applies to **`163709` tarball** extraction. `164111` adds documentation only; full `--restore-check` was not re-run on `164111` (non-material delta).

---

## Appendix — `mmi_backup_20260701_110548.tar.gz` (P1–P8 quality ladder)

**Authorized by:** Matt — Option A post-P8 queue decision (2026-07-01)  
**Executor:** Cursor PM  
**SHA256:** `5f6203e04f357127e4923793bb522ed32981a123d23e16f40f43b92e736e81df`  
**Bytes:** 271,612

### Sign-off

**PASS** — isolated `--restore-check` on `mmi_backup_20260701_110548.tar.gz` (scratch `/tmp/mmi_restore_validate_110548`).

### Restore-check

| Check | Result |
|-------|--------|
| SHA256 vs B2 mirror record | **PASS** |
| `tar -tzf` | **PASS** |
| `--restore-check` | **PASS** — `errors: []` |
| Live tree overwritten | **No** |
| B2 mutated during check | **No** |

```bash
SCRATCH=/tmp/mmi_restore_validate_110548
rm -rf "$SCRATCH" && mkdir -p "$SCRATCH"
tar -xzf /tmp/mmi_backup_20260701_110548.tar.gz -C "$SCRATCH"
python3 scripts/mmi_cold_backup.py --restore-check "$SCRATCH"
```

Promotion helper: run `python3 scripts/mmi_cold_backup.py --validate-promotion mmi_backup_20260701_110548.tar.gz` after this section is saved — expect **ALLOWED**. Matt manually updates `MMI_LATEST_GOOD_ARCHIVE.md` (human-gated; P5).

---

## Appendix — `mmi_backup_20260713_092718.tar.gz` (custody maintenance)

**Authorized by:** Matt — MMI/MMS maintenance program MNT-005 and MNT-008
**Executor:** Codex
**Date:** 2026-07-13
**SHA256:** `470b23f58343ae54d225b36c948d725c54110bead0e08be9afbb37a31ca3ec0c`
**Bytes:** 8,247,595

### Sign-off

**PASS — BOUNDED ALLOWLIST RESTORE CHECK**

The archive extracted into a new isolated temporary directory and the repository-defined `--restore-check` returned `PASS` with an empty error list. The live tree was not overwritten. The scratch directory remains present because cleanup was not authorized.

| Check | Result |
|---|---|
| Local archive SHA-256 | **PASS** |
| Backblaze bytes and SHA-256 | **PASS** |
| Sidecar SHA-256 | **PASS** |
| Isolated extraction | **PASS** |
| Required restore files | **PASS** |
| `tasks.json` JSON-list validation | **PASS** |
| Restore-critical Python syntax compilation | **PASS** |
| `--restore-check` errors | `[]` |
| Live tree overwritten | **No** |
| Scratch cleanup performed | **No** |
| Quarantined `evidence/` proven recoverable | **No — excluded from archive** |
| Loose MMS candidate data proven recoverable | **No — outside archive boundary** |

```bash
tar -xzf mmi/project_brain/backup/mmi_backup_20260713_092718.tar.gz \
  -C /tmp/mmi_restore_check_20260713_F8uWW7
python3 scripts/mmi_cold_backup.py \
  --restore-check /tmp/mmi_restore_check_20260713_F8uWW7
```

```json
{
  "restore_root": "/tmp/mmi_restore_check_20260713_F8uWW7",
  "status": "PASS",
  "errors": []
}
```

This PASS supports recovery of the standard allowlisted MMI control package only. It does not authorize latest-good promotion, account deletion, data deletion, cleanup, or product-work resumption.

