# Codex Handoff — P5 H3 Promotion Helper

**Date:** 2026-07-01  
**From:** Cursor PM (relay from Matt)  
**To:** Codex  
**Task:** `mmi-quality-slice-p5-h3-promotion-helper`  
**Build authorization:** `AUTHORIZED_BY_MATT_2026-07-01`

---

## Objective

Implement P5 — read-only **H3 promotion helper** that validates restore-check / manifest evidence **before** Matt manually updates `MMI_LATEST_GOOD_ARCHIVE.md`.

---

## Required behavior

1. Read-only validate an archive candidate (restore-check pattern, manifest, SHA evidence)
2. Report whether promotion to latest-good is **allowed** vs **blocked** (no restore-check PASS → blocked)
3. **Do not** auto-write or auto-promote `MMI_LATEST_GOOD_ARCHIVE.md`
4. Document human-gated promotion steps for Matt

---

## Inputs

- `scripts/mmi_cold_backup.py` (`--restore-check`, push log fields from P4)
- `mmi/project_brain/backup/MMI_LATEST_GOOD_ARCHIVE.md`
- `mmi/project_brain/status/MMI_LATEST_GOOD_ARCHIVE_VALIDATION_2026-07.md`
- `mmi/project_brain/status/MMI_BACKUP_PUSH_LOG.json`

---

## Hard stops

No P6 · no L3-05 · no OPSEC mutation · no B2 delete/overwrite · no live intel edits · no auto-promotion

---

## Closeout

```bash
python scripts/complete_task.py mmi-quality-slice-p5-h3-promotion-helper \
  --by "Codex" --summary "..." --output <script and test paths>
```

PASS WITH REVISIONS acceptable if helper validates and documents workflow but does not yet integrate into war room display.

---

## PM verification (reference)

```bash
python3 -m py_compile <changed files>
python3 -m unittest <new tests>   # WSL canonical for isolated/fake fixtures
```
