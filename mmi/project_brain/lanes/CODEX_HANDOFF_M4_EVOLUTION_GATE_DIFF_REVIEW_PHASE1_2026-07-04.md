# Codex Diff Review — M4 Evolution Gate Phase 1

**Task id:** `mmi-m4-evolution-gate`  
**Review type:** POST-BUILD DIFF REVIEW (Phase 1)  
**Date:** 2026-07-04  
**Build auth:** Matt authorized Phase 1 (2026-07-04)  
**Spec:** `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` (r2.5) §17 Phase 1, §5

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate
REVIEW TYPE: POST-BUILD DIFF REVIEW (Phase 1)
ASSIGNEE: Codex
AUTHORITY REPO: /mnt/c/Architectapp_clean

SPEC PHASE: §17 Phase 1 — m4_invariant_check.py + INV-1..7 static (§5)

FILES CHANGED:
  mmi/m4/invariants.py
  scripts/m4_invariant_check.py
  tests/test_m4_invariant_check.py
  mmi/project_brain/lanes/MMI_MATT_AUTH_M4_PHASE1_BUILD_2026-07-04.md

PREREQUISITE: Phase 0 import ban (H-L8-001) — Codex re-review may still be in flight

EXIT GATE: python scripts/m4_invariant_check.py --phase static → PASS (all INV-1..7)
            python -m pytest tests/test_m4_invariant_check.py -q → green

VERIFY:
  python scripts/m4_invariant_check.py --phase static --json
  python scripts/m4_invariant_check.py --phase live --json   (expect stub NOT PASS — Phase 4+)

POSTURE: evolution_gate OUTSTANDING — no PERFECT, no M4 closed

REQUIRED OUTPUT: CLEAN | NOT CLEAN with numbered findings

Do NOT authorize Phase 2. Do NOT claim GATED or M4 met.
```

---

## Cursor verification (2026-07-04)

```
m4_invariant_check (static): PASS — INV-1..7 all PASS
pytest tests/test_m4_invariant_check.py — 3 passed
```

**Not claimed:** CLEAN, Phase 2 auth, GATED, M4/PERFECT.

**Prerequisite:** Phase 0 Codex diff review — **CLEAN** (2026-07-04)

---

## Codex round 1 — NOT CLEAN (2026-07-04)

1. **INV-1 gap:** same-line regex only; multi-line `AUTHORITY_ROOT → target → write_text(...)` bypassed.
2. **Test gap:** no INV-1 negative coverage for indirect/multi-line authority writes.

---

## Cursor fix (2026-07-04, round 2)

**INV-1:** Replaced line-regex with AST taint analysis (`_ast_inv1_violations`):
- Tracks authority path expressions (`Path("...Architectapp_clean")`, `AUTHORITY_ROOT` name markers).
- Propagates taint through assignments across lines and scopes.
- Seeds module-level taint into function bodies (`_seed_module_taint`).
- Flags mutating calls (`.write_text`, `.write_bytes`, `open(...,"w")`, `shutil.copy`, etc.) on tainted handles.
- Self-scan exempt: `mmi/m4/invariants.py` via `_is_checker_source`.

**Tests added** (`tests/test_m4_invariant_check.py`):
- `test_inv1_fails_multiline_indirect_authority_write` — 3-line assign chain in `mmi/m4/bad.py`
- `test_inv1_fails_module_scope_indirect_write_via_alias` — module `ROOT` alias → function-scope write

**Re-verification (2026-07-04):**
```
python scripts/m4_invariant_check.py --phase static → PASS (INV-1..7)
python -m pytest tests/test_m4_invariant_check.py -q → 5 passed
```

**Ready for Codex re-review (Phase 1 round 2).**

---

## Codex round 2 — CLEAN (2026-07-04)

- INV-1 AST taint tracking accepted (indirect aliases, function-scope writes).
- Negative tests cover previously missed multi-line/alias paths.
- Static gate + 5 pytest tests verified.

**Blocked:** Phase 2 (`m4_fuzz_harness.py`) — Matt auth required. No GATED, no PERFECT.

---

## After Codex

| Verdict | Next |
|---------|------|
| CLEAN | Matt may authorize Phase 2 (fuzz harness) |
| NOT CLEAN | Cursor fix → re-review |

**Note:** Phase 0 Codex re-review is a separate packet — both can be open.
