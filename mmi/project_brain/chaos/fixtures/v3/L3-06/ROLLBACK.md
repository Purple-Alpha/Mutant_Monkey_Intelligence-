# L3-06 Rollback — Staged OPSEC false-DONE

**Scenario:** L3-06  
**Live authority:** **Never modified**

## Rollback procedure

1. **Do not** apply `FAULT/opsec/OPERATOR_OPSEC_CHECKLIST.md` to live path.
2. Confirm live checklist SHA256 matches `EVIDENCE/pre_check.json` → `post_check_live_unchanged.json`.
3. Retain `FAULT/` as intentional staged fault evidence (not deleted).
4. `BEFORE/` remains known-good copy snapshot from pre-test live state.

## Abort condition triggered?

**No** — live `mmi/project_brain/opsec/OPERATOR_OPSEC_CHECKLIST.md` was not written.
