# Codex Handoff — P2 Intel Closeout Gate

**Date:** 2026-07-01  
**From:** Cursor PM (relay from Matt)  
**To:** Codex  
**Task:** `mmi-quality-slice-p2-intel-closeout-gate`  
**Build authorization:** `AUTHORIZED_BY_MATT_2026-07-01`

---

## Objective

Implement P2 / G-INTEL-1 so the H2 intel brief headline/source-status check becomes a **required closeout/acceptance gate** for intel-brief tasks.

---

## Required behavior

1. Intel brief tasks must run H2 validation before closeout when output files include `mmi/project_brain/intel/briefs/INTEL_*.md`
2. Gate blocks closeout if §1/headline/operator-facing sections contain global/vendor statistic laundering
3. Gate passes current live briefs
4. Gate fails `mmi/project_brain/chaos/fixtures/v3/L3-04/FAULT/intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md`
5. Gate does not ban properly quarantined global/vendor stats in claims tables or disclosure sections
6. Gate result recorded in `closeout_verification`

---

## Files you may touch

- `scripts/complete_task.py`
- `scripts/mmi_verify.py` (only if needed)
- `tests/test_intel_closeout_gate.py` (new)
- Closeout/routing docs as needed

**Inputs to read:** `tests/test_complete_task_gate.py`, quality redesign P2 slice, L3-04 chaos report.

---

## Required tests

| Case | Expected |
|------|----------|
| Clean live/sample intel brief | PASS |
| Injected §1 laundering brief | FAIL |
| Quarantined claims-table global/vendor stat | PASS |
| H2 fail at closeout | `tasks.json` unchanged |
| H2 pass at closeout | H2 in `closeout_verification` |

---

## Hard stops

No P3 · no L3-05 · no new intel brief · no live brief edits · no OPSEC-4/5/9 · no B2 during build · no Level 4

---

## Closeout

```bash
python scripts/complete_task.py mmi-quality-slice-p2-intel-closeout-gate \
  --by "Codex" \
  --summary "..." \
  --output <changed files>
```

PASS WITH REVISIONS acceptable if intel closeout gate works but war-room display integration incomplete.

---

## PM verification commands (for reference)

```bash
python -m py_compile scripts/complete_task.py scripts/mmi_verify.py
python -m pytest tests/test_complete_task_gate.py
python -m pytest tests/test_intel_closeout_gate.py
python scripts/mmi_verify.py intel-briefs
python scripts/mmi_verify.py intel-brief mmi/project_brain/chaos/fixtures/v3/L3-04/FAULT/intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md
```
