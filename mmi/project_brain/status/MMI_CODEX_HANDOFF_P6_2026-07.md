# Codex Handoff — P6 OPSEC Amend Helper

**Date:** 2026-07-01  
**From:** Cursor PM (relay from Matt)  
**To:** Codex  
**Task:** `mmi-quality-slice-p6-opsec-amend-helper`  
**Build authorization:** `AUTHORIZED_BY_MATT_2026-07-01`

---

## Objective

Implement P6 / **G-OPSEC-1** — helper + documented SOP so `mmi_verify.py opsec-checklist` runs **before** Matt manually amends `OPERATOR_OPSEC_CHECKLIST.md`.

---

## Required behavior

1. Document human-gated amend workflow (Matt edits checklist; system does not auto-promote)
2. Helper runs `opsec-checklist` validation before amend (or blocks/gates the amend path with clear output)
3. Detect L3-06 class false-DONE patterns (DONE without evidence, stale `last_done`, etc.)
4. **Never** auto-write OPSEC rows to DONE

---

## Inputs

- `scripts/mmi_verify.py` (`opsec-checklist` subcommand)
- `mmi/project_brain/opsec/OPERATOR_OPSEC_CHECKLIST.md`
- `mmi/project_brain/chaos/MMI_CHAOS_L3-06_OPSEC_FALSE_DONE_2026-07.md`
- `mmi/project_brain/chaos/fixtures/v3/L3-06/`

Example fault check:

```bash
python3 scripts/mmi_verify.py opsec-checklist \
  --live-compare mmi/project_brain/chaos/fixtures/v3/L3-06/FAULT/opsec/OPERATOR_OPSEC_CHECKLIST.md \
  --expect-fault
```

---

## Hard stops

No P7 · no L3-05 · no OPSEC state fabrication · no B2 delete/overwrite · no live intel edits · no worksheet auto-promotion

---

## Closeout

```bash
python scripts/complete_task.py mmi-quality-slice-p6-opsec-amend-helper \
  --by "Codex" --summary "..." --output <paths>
```

PASS WITH REVISIONS acceptable if SOP + helper work but war-room integration incomplete.

---

## PM verification (reference)

```bash
python3 -m py_compile <changed files>
python3 -m unittest <new tests>   # WSL canonical
python3 scripts/mmi_verify.py opsec-checklist <L3-06 paths>
```
