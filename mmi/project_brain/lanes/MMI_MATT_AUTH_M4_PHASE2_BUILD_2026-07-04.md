# Matt Build Authorization — M4 Evolution Gate Phase 2

**Date:** 2026-07-04  
**Authority:** Matt (explicit: "authorize Phase 2")  
**Task:** `mmi-m4-evolution-gate`  
**Spec:** `MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` (r2.5) §17 Phase 2, §6  
**Prerequisite:** Phase 0–1 Codex CLEAN; Phase 1.5 assurance scaffold COMPLETE

---

## Authorized

**Phase 2:** `m4_fuzz_harness.py` — deterministic fuzz of §6 targets

| File | Role |
|------|------|
| `mmi/m4/parser_surface.py` | Strict JSON/manifest/canary-rule parsing |
| `mmi/m4/stage_fsm.py` | `run_stage` transition table |
| `mmi/m4/afe_ledger.py` | Monotonic attributed AFE ledger |
| `mmi/m4/canary_classifier.py` | Threshold classifier (fail-closed) |
| `mmi/m4/evidence_chain.py` | Append-only hash chain verify |
| `mmi/m4/restart_latch.py` | Crash/resume fail-closed latch |
| `mmi/m4/fuzz_runner.py` | Seeded mutation engine |
| `scripts/m4_fuzz_harness.py` | CLI gate |
| `tests/test_m4_fuzz_harness.py` | Regression + negative tests |

**Exit gate:** `python scripts/m4_fuzz_harness.py --target all --seed 1 --iters 100` → PASS; pytest green.

**Assurance scope (Phase 1.5):** Parser/FSM/ledger/classifier/rollup/restart uncertainty only — not containment, boundary, or endurance.

**Not authorized:** Phase 3+, Phase 11, 48h, PERFECT, GATED, M4 closed.

---

## Posture

`evolution_gate`: OUTSTANDING  
`perfect_claim`: false (pinned)  
**Blocked until:** Codex Phase 2 diff review CLEAN before Phase 3 auth.
