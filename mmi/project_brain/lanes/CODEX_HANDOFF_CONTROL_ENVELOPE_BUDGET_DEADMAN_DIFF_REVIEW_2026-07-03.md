# Codex Handoff — Control Envelope Budget + Dead-Man DIFF REVIEW

**Task id:** `mmi-control-envelope-budget-deadman-build`  
**Assignee:** Codex (post-build diff review)  
**Build auth:** Implemented per Codex BUILDABLE checklist (Matt relayed BUILDABLE)

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-control-envelope-budget-deadman-build
REVIEW TYPE: POST-BUILD DIFF REVIEW
ASSIGNEE: Codex
SPEC: mmi/project_brain/architecture/MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md (REV A)

FILES CHANGED:
  - mmi/project_brain/chaos/mmi_control_envelope.py (extended)
  - scripts/control_envelope_harness.py (new)
  - tests/test_control_envelope.py (new)

TEST EVIDENCE:
  pytest tests/test_control_envelope.py — 10/10 PASS
  python3 scripts/control_envelope_harness.py --scenario all — overall_gate_status CLEAN, authority files intact

VERIFY AGAINST SPEC:
  - enforce_boundary v0 unchanged
  - record_heartbeat() has no ack argument
  - pre_iteration_gate honors STOP_LATCH first
  - monotonic lifetime_spend seal + cross-witness
  - sticky latch; human-only ack/resume/window-reset helpers
  - no kinetic_telemetry import
  - evidence/state outside authority repo

OPEN RESIDUALS (expected — do not fail review if still documented):
  - Root-level consistent forge (host boundary non-goal)
  - Ack file permission isolation (deployment prerequisite)
  - Cap defaults 500k/5M pending Matt economic sign-off

REQUIRED OUTPUT:
  Verdict: CLEAN | NOT CLEAN
  If NOT CLEAN: numbered blockers with file:line references
```

---

## Build summary (Cursor)

| Item | Status |
|------|--------|
| `mmi_control_envelope.py` extended | Done — budget, dead-man, pre_iteration_gate, human-only helpers |
| `control_envelope_harness.py` | Done — T1/T2/T3 + all |
| `tests/test_control_envelope.py` | Done — 14 tests |
| Harness smoke | CLEAN (all scenarios) |
| Authority repo writes during harness | None (files fingerprint intact) |

## Codex R1 fixes (2026-07-03)

| Blocker | Fix |
|---------|-----|
| `_test_now_ms` on production constructor | Removed from `__init__`. Test/harness use `MMIControlEnvelope.for_testing(now_ms=...)` + `set_test_clock_ms()` only |
| `check_budget()` fail-open on deleted ledger | `_run_established()` + missing/corrupt ledger → `LEDGER_FAULT` SUSPENDED |
| T3 restart-loop not tested | `test_t3_restart_loop` + harness `restart_loop_halt` / `restart_loop_boundary_ok` |

**Re-verify:** pytest 14/14 PASS · harness `--scenario all` CLEAN · authority_intact true
