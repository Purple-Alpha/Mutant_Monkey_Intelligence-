# Codex Diff Review — M4 Evolution Gate Phase 3

**Task id:** `mmi-m4-evolution-gate`  
**Review type:** POST-BUILD DIFF REVIEW (Phase 3)  
**Date:** 2026-07-04  
**Build auth:** Matt Phase 3 build authorization  
**Spec:** `MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` (r2.5) §17 Phase 3, §7  
**Prerequisite:** Phase 0–2 Codex CLEAN

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate
REVIEW TYPE: POST-BUILD DIFF REVIEW (Phase 3)
ASSIGNEE: Codex
AUTHORITY REPO: /mnt/c/MMI

SPEC PHASE: §17 Phase 3 — m4_sandbox_escape_suite.py (§7)

FILES CHANGED:
  mmi/m4/sandbox_escape.py
  mmi/m4/evidence_paths.py (resolve_sandbox_evidence_dir)
  mmi/m4/invariants.py (INV-2 exempt §7 vector fixtures)
  scripts/m4_sandbox_escape_suite.py
  tests/test_m4_sandbox_escape_suite.py
  mmi/project_brain/lanes/MMI_MATT_AUTH_M4_PHASE3_BUILD_2026-07-04.md

PREREQUISITE: Phase 2 Codex CLEAN

EXIT GATE:
  python scripts/m4_sandbox_escape_suite.py → PASS (all modules DENY/contained)
  python scripts/m4_invariant_check.py --phase static → PASS
  python -m pytest tests/test_m4_sandbox_escape_suite.py tests/test_m4_fuzz_harness.py tests/test_m4_invariant_check.py -q → green

ASSURANCE SCOPE: Phase 3 policy model only — not live WFP/minifilter (Phase 4).

VERIFY:
  python scripts/m4_sandbox_escape_suite.py --json
  python scripts/m4_invariant_check.py --phase static

POSTURE: evolution_gate OUTSTANDING — no PERFECT, no M4 closed

REQUIRED OUTPUT: CLEAN | NOT CLEAN with numbered findings

Do NOT authorize Phase 4. Do NOT claim GATED or M4 met.
```

---

## Cursor verification (2026-07-04)

```
m4_sandbox_escape_suite --json → PASS (SE-FS..SE-KEY DENY/CONTAINED)
m4_invariant_check --phase static → PASS
pytest (sandbox + fuzz + invariant) → 23 passed
```

**Not claimed:** CLEAN (until Codex), Phase 4 auth, GATED, M4/PERFECT.

**Assurance scope:** SE-FS..SE-KEY modular DENY/contained under Phase 3 policy model — not host boundary runtime (Phase 4).

---

## Codex — CLEAN (2026-07-04)

- Policy-model sandbox escape suite accepted; all seven §7 modules DENY or CONTAINED.
- Evidence outside `AUTHORITY_ROOT` at `/tmp/m4_evidence_root/sandbox`.
- Verification: suite + INV static + 23 pytest tests — all PASS.

**Blocked:** Phase 4 (host boundary / TCB) — `matt_auth_phase4`. No GATED, no M4 claim.

---

## After Codex

| Verdict | Next |
|---------|------|
| CLEAN | Matt may authorize Phase 4 (host boundary) |
| NOT CLEAN | Cursor fix → re-review |
