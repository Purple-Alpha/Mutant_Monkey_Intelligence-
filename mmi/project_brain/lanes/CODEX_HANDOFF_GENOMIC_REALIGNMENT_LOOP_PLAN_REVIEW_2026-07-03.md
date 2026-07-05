# Codex Handoff — Genomic Realignment Loop PLAN REVIEW

**Task id:** `mmi-genomic-realignment-loop`  
**Assignee:** Codex (pre-build plan review)  
**Build auth:** NOT AUTHORIZED — spec closeout only  
**Spec:** `architecture/MMI_GENOMIC_REALIGNMENT_LOOP_SPEC_2026-07.md` (r2, PASS WITH REVISIONS)

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-genomic-realignment-loop
REVIEW TYPE: PRE-BUILD PLAN REVIEW
ASSIGNEE: Codex
AUTHORITY REPO: /mnt/c/Architectapp_clean

SPEC:
  mmi/project_brain/architecture/MMI_GENOMIC_REALIGNMENT_LOOP_SPEC_2026-07.md (r2)
  SIGN-OFF: PASS WITH REVISIONS (Claude Design, 2026-07-03)

UPSTREAM (BUILT + CLEAN — do not re-litigate):
  AGI §5 step 2: proof_gate_harness --console-bindings, console bindings spec r1
  AGI §5 step 3: mmi_control_envelope.py, control_envelope_harness CLEAN
  AGI §5 step 4: console_server.py, console_evidence_gate.py, console_server_harness CLEAN + Matt E2E

TARGET BUILD (NOT BUILT):
  ops/genomic_realignment_loop.py
  scripts/genomic_realignment_loop_harness.py
  tests/test_genomic_realignment_loop.py (expected)

DESIGN CALLS FOR CODEX RATIFICATION (footnote 1 + spec SIGN-OFF):
  (a) v1 terminal success = VALID_STAGED (in-episode SIGNED optional, not required)
  (b) ops/ placement vs scripts/ for orchestration module

POTENTIAL BUILD BLOCKERS TO CHECK:
  1. H14 episode binding — does proof_gate_summary.json today echo constraint_id + patch_context_digest?
     If not, spec footnote 5 says H14 fails closed — may need bindings extension BEFORE loop build.
  2. action_integrity_gate — does it expose validate() for genomic_constraint_v1 + registered capability check as spec assumes?
  3. Breach descriptor schema — spec §4 assumes EPISODE_ROOT/inbox input; define minimal v1 descriptor or flag as build-time deliverable.
  4. Constraint synthesis — spec allows typed declarative artifacts but does not define synth algorithm;
     v1 may need deterministic stub/template synth for harness T1 (flag if BUILDABLE only with explicit stub lane).
  5. ops/ directory may not exist — confirm create ops/ + import path convention.

REQUIRED OUTPUT: BUILDABLE | NOT BUILDABLE with numbered blockers

If NOT BUILDABLE: each blocker must name file/spec section and minimal fix (spec amendment vs upstream patch vs build package split).
If BUILDABLE: list ordered build slices (loop core → harness → tests) and any spec amendments bundled with build.
```

---

## After Codex BUILDABLE

Matt: `authorize build step 5 genomic loop` → Cursor implements → Codex diff review.

Update `MMI_PIPE_STAGING.json` → `genomic_realignment_loop_build: PENDING_CODEX_PLAN_REVIEW`.

---

## Codex plan review R1 (2026-07-03) — NOT BUILDABLE

| # | Blocker | Fix slice |
|---|---------|-----------|
| 1 | **H14** — `proof_gate_summary` lacks `constraint_id` + `patch_context_digest` | Extend bindings spec r1 → r2: genomic episode fields; `apply_console_bindings()` + loop passes `--constraint-id` / digest at invoke |
| 2 | **H8** — no `action_integrity_gate.validate()` for `genomic_constraint_v1` | New `chaos/genomic_constraint_validator.py` or extend action_integrity with closed enum + capability registry + anti-salami |
| 3 | **Harness T1** — no breach descriptor contract or deterministic synth stub | Add spec §4.5 breach descriptor + §4.6 v1 synth stub (template mapping harvest→constraint); harness fixtures |
| 4 | **ops/** placement | Not blocked — `ops/` exists; build plan must document chaos/scripts import bootstrap like harnesses |

**Re-review gate:** Codex BUILDABLE only after slices 1–3 are spec-defined (and slice 1–2 implemented if bundled as prerequisite package).

Matt research in progress on separate concept — step 5 build remains **NOT AUTHORIZED** until BUILDABLE + explicit build auth.
