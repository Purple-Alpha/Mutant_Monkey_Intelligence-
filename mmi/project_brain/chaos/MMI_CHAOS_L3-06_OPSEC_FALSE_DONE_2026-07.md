# MMI Chaos Level 3 — L3-06 OPSEC False-DONE (Staged)

**Task:** `mmi-chaos-l3-06-opsec-false-done`  
**Scenario:** L3-06 from `MMI_CHAOS_LEVEL3_PLAN_2026-07.md`  
**Date:** 2026-07-01  
**Executor:** Cursor PM  
**Authority:** Matt — L3-06 only (not batch Level 3)

---

## Sign-off

**PASS WITH REVISIONS**

Staged checklist fault **detected** (4 violations). Live OPSEC-4/5/9 remain **`NOT_STARTED`**. Live checklist SHA256 **unchanged**.

**Revision caveat:** Detection uses new read-only `scripts/mmi_verify.py opsec-checklist` — not yet a mandatory operator workflow gate. Dual-read with `OPSEC_HUMAN_GATE_DRILL_2026-06-30.md` remains operator responsibility.

---

## Fixture path

```text
mmi/project_brain/chaos/fixtures/v3/L3-06/
├── BEFORE/opsec/OPERATOR_OPSEC_CHECKLIST.md   # known-good copy from live
├── FAULT/opsec/OPERATOR_OPSEC_CHECKLIST.md    # false-DONE injection
├── EVIDENCE/
│   ├── pre_check.json
│   ├── detection_output.json
│   └── post_check_live_unchanged.json
├── ROLLBACK.md
├── _setup_fixture.py
└── _post_check.py
```

---

## Injected fault (FAULT copy only)

| Item | Staged state | Why false |
|------|--------------|-----------|
| OPSEC-4 | `DONE`, empty `last_done` | Worksheet-only verify — no habit evidence |
| OPSEC-5 | `DONE`, `2026-06-30`, dry-run verify | Worksheet §6 dry-run insufficient alone per checklist |
| OPSEC-9 | `DONE`, `2026-06-30`, worksheet dry-run | No real decision-log habit evidence |

Live checklist was **not** modified.

---

## Live checklist pre-check

From `EVIDENCE/pre_check.json`:

| Item | State |
|------|--------|
| OPSEC-4 | `NOT_STARTED` |
| OPSEC-5 | `NOT_STARTED` |
| OPSEC-9 | `NOT_STARTED` |

Live SHA256 (pre): `fbdab2d504acef91d2578b4468dcb3f489c7920269f58cc985c060ba9d68aab2`

---

## Detection command / result

```bash
python3 scripts/mmi_verify.py opsec-checklist \
  mmi/project_brain/chaos/fixtures/v3/L3-06/FAULT/opsec/OPERATOR_OPSEC_CHECKLIST.md \
  --live-compare --expect-fault
```

| Field | Result |
|-------|--------|
| `fault_detected` | **true** |
| `live_unchanged_ok` | **true** |
| Exit code | **0** (expect-fault mode) |

### Violations detected

| Item | Reason |
|------|--------|
| OPSEC-4 | DONE without last_done |
| OPSEC-4 | DONE with worksheet-only verify_method |
| OPSEC-5 | DONE with dry-run-only verify_method |
| OPSEC-9 | DONE with dry-run-only verify_method |

Full JSON: `fixtures/v3/L3-06/EVIDENCE/detection_output.json`

Live truth at detection time:

```json
{
  "OPSEC-4": "NOT_STARTED",
  "OPSEC-5": "NOT_STARTED",
  "OPSEC-9": "NOT_STARTED"
}
```

---

## Rollback / cleanup

| Check | Result |
|-------|--------|
| Live file written? | **No** |
| Rollback required on live? | **No** — FAULT retained as evidence |
| Live SHA256 post | `fbdab2d504acef91d2578b4468dcb3f489c7920269f58cc985c060ba9d68aab2` |
| Matches pre? | **Yes** |

See `fixtures/v3/L3-06/ROLLBACK.md` and `EVIDENCE/post_check_live_unchanged.json`.

---

## Hard stops honored

| Stop | Result |
|------|--------|
| Live OPSEC checklist mutated | **NO** |
| OPSEC-4/5/9 state changed on live | **NO** |
| Other Level 3 scenarios run | **NO** |
| Batch Level 3 | **NO** |
| B2 mutated | **NO** |
| Level 4 | **NOT STARTED** |
| Malware / SOAR / EDR | **NO** |

---

## Tooling added (read-only)

`scripts/mmi_verify.py opsec-checklist PATH [--live-compare] [--expect-fault]`

Maps to Level 2 T06 detection logic, extended for full checklist rows and OPSEC-9.

---

## Next

- Matt review + optional B2 mirror of L3-06 evidence (separate auth)
- Next Level 3 test: **L3-04 only** when separately authorized — not batch

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | First Level 3 execution — L3-06 staged only — PASS WITH REVISIONS |
