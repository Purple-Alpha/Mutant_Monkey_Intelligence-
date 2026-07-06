# Codex Diff Review — M4 Evolution Gate Phase 0

**Task id:** `mmi-m4-evolution-gate`  
**Review type:** POST-BUILD DIFF REVIEW (Phase 0)  
**Date:** 2026-07-03  
**Build auth:** Matt authorized staged build (Phase 0)  
**Spec:** `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` (r2.2) §17 Phase 0

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate
REVIEW TYPE: POST-BUILD DIFF REVIEW (Phase 0)
ASSIGNEE: Codex
AUTHORITY REPO: /mnt/c/MMI

SPEC PHASE: §17 Phase 0 — m4_import_ban_test.py (H-L8-001), mmi/m4/ scaffold

FILES CHANGED:
  mmi/__init__.py
  mmi/m4/__init__.py
  mmi/m4/import_ban.py
  scripts/m4_import_ban_test.py
  tests/test_m4_import_ban.py

EXIT GATE: 0 L8 imports in mmi/m4/*; scan passes; pytest green

POSTURE: evolution_gate OUTSTANDING — no PERFECT, no M4 closed, Phase 11 still gated

REQUIRED OUTPUT: CLEAN | NOT CLEAN with numbered findings

Do NOT authorize Phase 1. Do NOT claim GATED or M4 met.
```

---

## After Codex

| Verdict | Next |
|---------|------|
| CLEAN | Matt may authorize Phase 1 (invariant suite) or continue staged build |
| NOT CLEAN | Cursor fix → re-review |

---

## Codex verdict (2026-07-03) — NOT CLEAN

1. **Dynamic import bypass:** `import_ban.py` only matched static `import`/`from` lines; `importlib.import_module("chaos.canary_metadata_layer")` and `__import__(...)` passed.
2. **Missing regression tests** for dynamic import paths.

---

## Cursor fix (2026-07-03) — ready for re-review

| Finding | Fix |
|---------|-----|
| Dynamic import bypass | `_canary_metadata_layer_coupling()`: static import **or** same-line `importlib` / `__import__` / `import_module` + `canary_metadata_layer` |
| Test gap | `test_dynamic_canary_metadata_layer_import_fails` (parametrized: `import_module`, `__import__`, `getattr(importlib, ...)`) |

**Verification (Cursor):**
- `python scripts/m4_import_ban_test.py --json` → `passed: true`
- `python -m pytest tests/test_m4_import_ban.py -q` → **6 passed**

**Not claimed:** CLEAN, Phase 1 auth, GATED, M4/PERFECT.

---

## Codex re-review (2026-07-04) — paste this

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate
REVIEW TYPE: POST-BUILD DIFF REVIEW (Phase 0) — RE-REVIEW
ASSIGNEE: Codex
AUTHORITY REPO: /mnt/c/MMI

CONTEXT: Prior review NOT CLEAN (2 findings). Cursor fixed both. This is re-review only — not a new build phase.

PRIOR FINDINGS (must verify closed):
  1. Dynamic import bypass — importlib/__import__/import_module + canary_metadata_layer on same line
  2. Missing regression tests for dynamic import paths

FILES CHANGED (since first review):
  mmi/m4/import_ban.py          — _canary_metadata_layer_coupling(), DYNAMIC_IMPORT_MECHANISM regex
  tests/test_m4_import_ban.py   — test_dynamic_canary_metadata_layer_import_fails (3 parametrized cases)

COMMITS (branch mmi-phase2-commit):
  999789e — M4 evolution gate r2.5: full matrix bar, Phase 0 import ban, Matt ruling
  (Phase 0 files in this commit)

SPEC: architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md (r2.5) §17 Phase 0, H-L8-001

EXIT GATE: 0 L8 coupling in mmi/m4/*; dynamic import bypass closed; pytest green

VERIFY ON DISK:
  python scripts/m4_import_ban_test.py --json
  python -m pytest tests/test_m4_import_ban.py -q

POSTURE: evolution_gate OUTSTANDING — no PERFECT, no M4 closed, Phase 11 gated on §13.1

REQUIRED OUTPUT: CLEAN | NOT CLEAN with numbered findings

Do NOT authorize Phase 1. Do NOT claim GATED or M4 met.

OPTIONAL NOTE (out of Phase 0 scope): split-line indirection (MOD="..." then import_module(MOD)) still passes — flag only if you want fail-closed on that before Phase 1.
```

---

## Codex re-review round 2 (2026-07-04) — NOT CLEAN → fixed

**Codex findings:**
1. Split-line / aliased dynamic import (`LAYER = "..."; import_module(LAYER)`)
2. Missing tests for split/aliased cases

**Cursor fix:**
- AST scan: any string literal containing `canary_metadata_layer` in `mmi/m4/*.py` → FAIL (except `import_ban.py`)
- Tests: `test_split_or_aliased_dynamic_import_fails` + benign json import passes
- Reworded `mmi/m4/__init__.py` docstring (removed literal substring)

**Paste for Codex re-review round 2:**

```
REVIEW TYPE: POST-BUILD DIFF REVIEW (Phase 0) — RE-REVIEW ROUND 2
AUTHORITY REPO: /mnt/c/MMI
FILES: mmi/m4/import_ban.py, mmi/m4/__init__.py, tests/test_m4_import_ban.py
VERIFY: python scripts/m4_import_ban_test.py --json && pytest tests/test_m4_import_ban.py -q
Must fail: LAYER="chaos.canary_metadata_layer"; importlib.import_module(LAYER)
Must fail: split-line assign + import_module variable/concat
OUTPUT: CLEAN | NOT CLEAN
```

**Verification:** import ban PASS (3 files); pytest **10 passed**

**Not claimed:** CLEAN, GATED, M4/PERFECT.

**After CLEAN:** Phase 1 already built on Matt auth — run Phase 1 Codex diff packet next.

---

## Codex verdict (2026-07-04) — CLEAN (round 2)

1. Split-line / aliased dynamic import bypass — **closed** (AST string-literal detection)
2. Regression tests — **closed** (split-line, aliased, same-line, benign cases)

**Verification (Codex):** import ban PASS; pytest 10 passed

**Next:** Codex Phase 1 diff review (`CODEX_HANDOFF_M4_EVOLUTION_GATE_DIFF_REVIEW_PHASE1_2026-07-04.md`)
