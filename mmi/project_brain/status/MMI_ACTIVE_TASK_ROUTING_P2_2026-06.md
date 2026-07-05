# MMI Active Task Routing — P2 Intel Closeout Gate

**Last updated:** 2026-06-30  
**Authority:** Matt (Super)  
**Task:** `mmi-quality-slice-p2-intel-closeout-gate` — **COMPLETE** (Codex)

---

## Verdict

**CLOSED** — G-INTEL-1 delivered and PM-verified. See `MMI_CLOSEOUT_P2_2026-07.md`.

---

## Objective

Implement P2 / G-INTEL-1: H2 intel brief headline/source-status check becomes a **required closeout/acceptance gate** for intel-brief tasks — not optional read-only detection.

```text
Before: H2 catches laundering when run
After:  G-INTEL blocks laundering before intel closeout/acceptance
```

---

## Inputs

- `scripts/mmi_verify.py`
- `scripts/complete_task.py`
- `tests/test_complete_task_gate.py`
- `mmi/project_brain/architecture/MMI_QUALITY_ELEVATION_REDESIGN_2026-07.md`
- `mmi/project_brain/chaos/MMI_CHAOS_L3-04_INTEL_HEADLINE_LAUNDERING_2026-07.md`

---

## Scope (Codex may)

- Update `scripts/complete_task.py`
- Update `scripts/mmi_verify.py` only if needed for gate integration
- Add `tests/test_intel_closeout_gate.py`
- Update task closeout/routing documentation

---

## Required behavior

- Intel brief tasks run H2 before closeout when outputs include `mmi/project_brain/intel/briefs/INTEL_*.md`
- Block closeout if §1/headline/operator-facing sections contain global/vendor statistic laundering
- Pass current live briefs
- Fail known bad L3-04 FAULT fixture
- Do not ban properly quarantined global/vendor stats in claims tables or disclosure sections
- Record gate result in `closeout_verification`

---

## Required tests

- Clean live/sample intel brief passes
- Injected §1 laundering brief fails
- Quarantined claims-table global/vendor stat passes
- Closeout blocked before `tasks.json` write when H2 fails
- Closeout records H2 verification when H2 passes

---

## Hard stops

- No P3 implementation
- No L3-05
- No new intel brief
- No live intel brief content mutation
- No OPSEC-4/5/9 state changes
- No B2 mutation during build
- No Level 4

---

## PM spot-check (after Codex delivery)

```bash
python -m py_compile scripts/complete_task.py scripts/mmi_verify.py
python -m pytest tests/test_complete_task_gate.py
python -m pytest tests/test_intel_closeout_gate.py
python scripts/mmi_verify.py intel-briefs
python scripts/mmi_verify.py intel-brief mmi/project_brain/chaos/fixtures/v3/L3-04/FAULT/intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md
```

Expected:

```text
live briefs: PASS
L3-04 FAULT: FAIL
P2 closeout gate tests: PASS
```

**PASS WITH REVISIONS** acceptable if P2 enforced for intel closeout but not yet in every war-room display.

---

## References

- `mmi/project_brain/status/MMI_CODEX_HANDOFF_P2_2026-07.md` — relay packet
- `mmi/project_brain/architecture/MMI_QUALITY_ELEVATION_REDESIGN_2026-07.md` — Slice P2
- `mmi/project_brain/status/MMI_B2_MIRROR_P1_TESTS_2026-06.md` — preceding snapshot
