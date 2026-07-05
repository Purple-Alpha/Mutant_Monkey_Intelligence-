# Matt Build Authorization — M4 Evolution Gate Phase 1

**Date:** 2026-07-04  
**Authority:** Matt (explicit: "authorize the next build step")  
**Task:** `mmi-m4-evolution-gate`  
**Spec:** `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` (r2.5) §17 Phase 1

---

## Authorized

**Phase 1:** `m4_invariant_check.py` + INV-1..7 static suite (§5)

**Parallel:** Codex Phase 0 diff re-review may complete independently; Phase 1 build proceeds on Matt auth.

**Not authorized:** Phase 2+ fuzz, Phase 11, 48h, PERFECT, GATED, M4 closed.

---

## Phase 1 deliverables (Cursor)

| File | Role |
|------|------|
| `mmi/m4/invariants.py` | INV-1..7 static checks |
| `scripts/m4_invariant_check.py` | CLI `--phase static\|live` |
| `tests/test_m4_invariant_check.py` | Regression tests |

**Exit gate:** `python scripts/m4_invariant_check.py --phase static` → PASS; pytest green.

**Blocked until:** Codex Phase 1 diff review CLEAN before Phase 2 auth.

---

## Posture

`evolution_gate`: OUTSTANDING  
`perfect_claim`: false (pinned)  
Phase 0: Codex re-review in flight
