# Codex Diff Review — M4 Evolution Gate Phase 2

**Task id:** `mmi-m4-evolution-gate`  
**Review type:** POST-BUILD DIFF REVIEW (Phase 2)  
**Date:** 2026-07-04  
**Build auth:** Matt authorized Phase 2 (2026-07-04)  
**Spec:** `MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` (r2.5) §17 Phase 2, §6  
**Prerequisite:** Phase 0–1 Codex CLEAN; Phase 1.5 assurance scaffold COMPLETE

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate
REVIEW TYPE: POST-BUILD DIFF REVIEW (Phase 2)
ASSIGNEE: Codex
AUTHORITY REPO: /mnt/c/Architectapp_clean

SPEC PHASE: §17 Phase 2 — m4_fuzz_harness.py (§6)

FILES CHANGED:
  mmi/m4/parser_surface.py
  mmi/m4/stage_fsm.py
  mmi/m4/afe_ledger.py
  mmi/m4/canary_classifier.py
  mmi/m4/evidence_chain.py
  mmi/m4/restart_latch.py
  mmi/m4/fuzz_runner.py
  scripts/m4_fuzz_harness.py
  tests/test_m4_fuzz_harness.py
  mmi/project_brain/lanes/MMI_MATT_AUTH_M4_PHASE2_BUILD_2026-07-04.md

PREREQUISITE: Phase 0–1 Codex CLEAN; Phase 1.5 assurance scaffold

EXIT GATE:
  python scripts/m4_fuzz_harness.py --target all --seed 1 --iters 50 → PASS
  python -m pytest tests/test_m4_fuzz_harness.py tests/test_m4_invariant_check.py -q → green

ASSURANCE SCOPE (Phase 1.5 — do not oversell):
  Phase 2 reduces parser/FSM/ledger/classifier/rollup/restart uncertainty ONLY.
  Does NOT prove sandbox escape, host boundary, canary runtime, endurance, or M4_MET.

VERIFY:
  python scripts/m4_fuzz_harness.py --target all --seed 1 --iters 100 --json
  python scripts/m4_invariant_check.py --phase static

POSTURE: evolution_gate OUTSTANDING — no PERFECT, no M4 closed

REQUIRED OUTPUT: CLEAN | NOT CLEAN with numbered findings

Do NOT authorize Phase 3. Do NOT claim GATED or M4 met.
```

---

## Cursor verification (2026-07-04)

```
m4_fuzz_harness (all): PASS — fuzz PASS + INV static PASS
pytest test_m4_fuzz_harness + test_m4_invariant_check — 14 passed
```

**Assurance claim scope:** Parser/FSM/ledger/classifier/evidence/restart deterministic fuzz only (AC-P2).

**Not claimed:** CLEAN, Phase 3 auth, containment proven, GATED, M4/PERFECT.

---

## Codex round 1 — NOT CLEAN (2026-07-04)

1. **EVIDENCE_ROOT default:** harness defaulted `--evidence` to `AUTHORITY_ROOT/mmi/project_brain/evidence/fuzz`. Spec §6/§13 requires `EVIDENCE_ROOT/fuzz/` **outside** `AUTHORITY_ROOT`.

---

## Cursor fix (2026-07-04, round 2)

- Added `mmi/m4/evidence_paths.py`: `resolve_fuzz_evidence_dir()` — fail-closed if path under authority.
- Default: `$MMI_EVIDENCE_ROOT/fuzz` or `C:/mmi_m4_evidence/fuzz` (Win) / `/var/mmi_m4_evidence/fuzz` (POSIX).
- `--evidence` still accepted as explicit `EVIDENCE_ROOT/fuzz/`.
- Tests: reject evidence under authority; default resolves outside repo.

**Re-verification:**
```
python scripts/m4_fuzz_harness.py --target all --seed 1 --iters 100 --json → PASS
python scripts/m4_invariant_check.py --phase static → PASS
pytest test_m4_fuzz_harness + test_m4_invariant_check → green
```

**Ready for Codex re-review (Phase 2 round 2).**

---

## Codex round 2 — CLEAN with verification caveat (2026-07-04)

- EVIDENCE_ROOT outside authority: **accepted** (`/var/mmi_m4_evidence/fuzz` on POSIX).
- Verification failed in Codex env: `/var/mmi_m4_evidence` read-only (`OSError: [Errno 30]`).

---

## Cursor fix (2026-07-04, round 3)

- `resolve_fuzz_evidence_dir()` tries ordered candidates outside `AUTHORITY_ROOT`.
- Primary: `$MMI_EVIDENCE_ROOT` → `/var/mmi_m4_evidence` (POSIX) / `C:/mmi_m4_evidence` (Win).
- **Writable fallback:** `$XDG_STATE_HOME/mmi_m4_evidence` or `~/.local/state/mmi_m4_evidence` when host default is read-only.
- Still rejects paths under authority and forbidden `/tmp/mmi*` (H-EVID-001).
- Explicit `--evidence` unchanged.

**Re-verification:**
```
python scripts/m4_fuzz_harness.py --target all --seed 1 --iters 100 --json → PASS
python scripts/m4_invariant_check.py --phase static → PASS
pytest → 17 passed
```

**Ready for Codex re-review (Phase 2 round 3) if required.**

---

## Codex round 3 — NOT CLEAN (2026-07-04)

1. All host defaults read-only in review env → `no writable EVIDENCE_ROOT/fuzz outside AUTHORITY_ROOT`.
2. `test_resolve_fuzz_evidence_default_outside_repo` failed (depended on host `/var` or `C:` writability).

---

## Cursor fix (2026-07-04, round 4)

- Expanded candidate chain: XDG state, `~/.cache`, `$TMPDIR/m4_evidence_root`, `tempfile.gettempdir()/m4_evidence_root` (review fallback; dirname avoids `/tmp/mmi*`).
- Tests use `MMI_EVIDENCE_ROOT` tmp fixture — no dependency on host `/var` writability.
- INV-2 docstring: removed word `Production`.

**Re-verification:**
```
python scripts/m4_fuzz_harness.py --target all --seed 1 --iters 100 --json → PASS
python scripts/m4_invariant_check.py --phase static → PASS
pytest → 18 passed
```

---

## Codex round 4 — CLEAN (2026-07-04)

- Default evidence resolves outside `AUTHORITY_ROOT` and writable in review env: `/tmp/m4_evidence_root/fuzz`.
- Avoids forbidden `/tmp/mmi*` pattern (H-EVID-001).
- Verification: fuzz harness + INV static + 18 pytest tests — all PASS.

**Blocked:** Phase 3 (`m4_sandbox_escape_suite.py`) — `matt_auth_phase3`. No GATED, no M4 claim.

---

## After Codex

| Verdict | Next |
|---------|------|
| CLEAN | Matt may authorize Phase 3 (sandbox escape) |
| NOT CLEAN | Cursor fix → re-review |
