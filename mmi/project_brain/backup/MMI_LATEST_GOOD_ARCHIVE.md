# MMI Latest Good Archive — Operator Restore Reference

**Purpose:** Single read-only pointer to the **latest verified cold-mirror archive** for restore under pressure.  
**Authority:** Matt (Super) — updated after Matt-authorized B2 push with PASS.  
**Task:** `mmi-chaos-hardening-h1-h3` (H3)  
**Do not edit manually unless recording a new Matt-authorized push.**

---

## Latest good archive (use this for restore reference)

| Field | Value |
|-------|--------|
| **Archive name** | `mmi_backup_20260701_110548.tar.gz` |
| **SHA256** | `5f6203e04f357127e4923793bb522ed32981a123d23e16f40f43b92e736e81df` |
| **Archive date/time (UTC)** | 2026-07-01T18:05:48Z (`MMI_BACKUP_PUSH_LOG.json` tail) |
| **Local build path (WSL)** | `/tmp/mmi_backup_20260701_110548.tar.gz` (ephemeral — use B2 for authoritative copy) |
| **Remote path** | `matt:mmi-cold-storage/archives/mmi_backup_20260701_110548.tar.gz` |
| **Push status** | PASS |
| **Local/remote bytes** | 271,612 (match) |
| **Restore-check status** | **PASS** — isolated `--restore-check` on this archive passed |
| **Safe as latest-good restore reference?** | **YES** |

---

## Manifest notes (high-signal paths in this archive)

- `mmi/project_brain/status/MMI_LATEST_GOOD_ARCHIVE_VALIDATION_2026-07.md`
- `mmi/project_brain/chaos/MMI_CHAOS_HARDENING_H1-H3_2026-07.md`
- `scripts/mmi_verify.py`
- `mmi/project_brain/backup/MMI_LATEST_GOOD_ARCHIVE.md`
- `mmi/project_brain/chaos/MMI_CHAOS_SANDBOX_V2_2026-07.md`
- `mmi/project_brain/chaos/MMI_CHAOS_TABLETOP_V1_2026-07.md`
- `mmi/project_brain/chaos/fixtures/v2/` (Level 2 sandbox fixtures)
- `mmi/project_brain/lanes/REDDIT_VENDOR_EMAIL_ROUTINE_INTAKE_2026-07.md`
- `mmi/project_brain/intel/briefs/` (both filed briefs, MIXED)
- `mmi/project_brain/opsec/OPERATOR_OPSEC_CHECKLIST.md`
- `tasks.json`, `mmi/task_pipeline.json`

Full file list: `mmi/project_brain/status/MMI_BACKUP_PUSH_LOG.json` — last entry.

---

## Under pressure — operator steps

1. Read **Archive name** and **SHA256** from this file (not from memory).  
2. Confirm push log tail matches before restore.  
3. Restore to an **isolated directory** first (`scripts/mmi_cold_backup.py --restore-check` pattern).  
4. Do not overwrite live tree until restore validated.

---

## Supersedes

| Archive | SHA256 (prefix) | Notes |
|---------|-----------------|-------|
| `mmi_backup_20260630_163310.tar.gz` | `ee17d618…` | H1–H3 hardening pre–intel-brief glob fix |
| `mmi_backup_20260630_163150.tar.gz` | `ebb22f191…` | H1–H3 hardening (missing `mmi_verify.py` on allowlist) |
| `mmi_backup_20260630_162815.tar.gz` | `d9db5f207c…` | Level 2 sandbox closeout (pre–H1–H3) |
| `mmi_backup_20260630_162035.tar.gz` | `f262e3e7…` | Pre–Level 2 sandbox closeout |
| `mmi_backup_20260630_154854.tar.gz` | `f1762050…` | Pre–chaos sandbox artifacts |

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | H3 stub — initial pointer to `mmi_backup_20260630_162815.tar.gz` |
| 1.1 | 2026-07-01 | Post–H1–H3 B2 push — `mmi_backup_20260630_163150.tar.gz` |
| 1.2 | 2026-07-01 | Allowlist fix — `163235` includes `scripts/mmi_verify.py` |
| 1.3 | 2026-07-01 | Final hardening mirror — `163310` |
| 1.4 | 2026-07-01 | Closeout mirror — `163709` (multi-path `intel-brief` + final task summary) |
| 1.5 | 2026-07-01 | Restore-check PASS recorded — see `status/MMI_LATEST_GOOD_ARCHIVE_VALIDATION_2026-07.md` |
| 1.6 | 2026-07-01 | Matt Option A promotion closeout — `110548` confirmed latest-good; weapon Phase 1 harness seeded |
