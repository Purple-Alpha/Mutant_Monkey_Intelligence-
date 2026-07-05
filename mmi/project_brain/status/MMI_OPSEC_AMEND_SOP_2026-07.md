# MMI OPSEC Amend SOP — G-OPSEC-1

**Purpose:** Human-gated checklist amendment process for `OPERATOR_OPSEC_CHECKLIST.md`.
**Status:** Active SOP for P6.

## Rule

`OPSEC-4`, `OPSEC-5`, and `OPSEC-9` must not be marked `DONE` unless Matt has real evidence in `last_done` and `verify_method`.

Worksheet, dry-run, and template evidence are not enough to promote a row to `DONE`.

## Workflow

1. Copy `mmi/project_brain/opsec/OPERATOR_OPSEC_CHECKLIST.md` to a draft/staged path.
2. Matt manually edits the draft row only when real evidence exists.
3. Run:

```bash
python3 scripts/mmi_verify.py opsec-amend-check path/to/draft_checklist.md
```

4. If the result is `BLOCK_AMEND`, do not replace the live checklist.
5. If the result is `ALLOW_AMEND`, Matt may manually apply the reviewed change.

## Hard Stops

- No file watcher.
- No automatic checklist writes.
- No worksheet-to-DONE promotion.
- No fabricated `last_done`.
- No OPSEC-4/5/9 state changes without Matt evidence.

## Expected Fault Behavior

The helper must block the L3-06 false-DONE class:

```bash
python3 scripts/mmi_verify.py opsec-amend-check \
  mmi/project_brain/chaos/fixtures/v3/L3-06/FAULT/opsec/OPERATOR_OPSEC_CHECKLIST.md
```

Expected: `BLOCK_AMEND`.
