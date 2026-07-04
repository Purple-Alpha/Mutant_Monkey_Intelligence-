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
AUTHORITY REPO: /mnt/c/Architectapp_clean

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
