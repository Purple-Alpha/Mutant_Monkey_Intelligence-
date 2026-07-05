# Codex Handoff — Genomic Realignment Loop PLAN REVIEW (R2)

**Task id:** `mmi-genomic-realignment-loop`  
**Assignee:** Codex (pre-build plan review — re-run)  
**Build auth:** Prereqs BUILT — main loop NOT AUTHORIZED until BUILDABLE  
**Spec:** `architecture/MMI_GENOMIC_REALIGNMENT_LOOP_SPEC_2026-07.md` (r2)

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-genomic-realignment-loop
REVIEW TYPE: PRE-BUILD PLAN REVIEW (R2 — post prereqs)
ASSIGNEE: Codex
AUTHORITY REPO: /mnt/c/Architectapp_clean

SPEC:
  mmi/project_brain/architecture/MMI_GENOMIC_REALIGNMENT_LOOP_SPEC_2026-07.md (r2)
  mmi/project_brain/architecture/MMI_PROOF_GATE_CONSOLE_BINDINGS_SPEC_2026-07.md (r2 §3.6)

PREREQS BUILT (Codex R1 blockers addressed):
  Slice 1 — H14 episode binding:
    - mmi_canonical_digest.patch_context_tree_digest()
    - proof_gate_harness --constraint-id --episode-id --patch-context-digest
    - apply_console_bindings() emits genomic_episode on summary
    - tests/test_proof_gate_console_bindings.py::test_apply_console_bindings_genomic_episode

  Slice 2 — H8 genomic_constraint_v1 validator:
    - chaos/genomic_constraint_validator.py (validate_genomic_constraint, compute_constraint_id)
    - tests/test_genomic_constraint_validator.py (T5/T7 class cases)

  Slice 3 — T1 breach descriptor + deterministic synth stub:
    - genomic spec §4.5 breach_descriptor_v1 + §4.6 synth stub
    - chaos/genomic_constraint_synth.py (validate_breach_descriptor, synthesize_constraint_v1)

CURSOR VERIFICATION:
  pytest tests/test_genomic_constraint_validator.py tests/test_proof_gate_console_bindings.py -v

STILL NOT BUILT (await BUILDABLE):
  ops/genomic_realignment_loop.py
  scripts/genomic_realignment_loop_harness.py

REQUIRED OUTPUT: BUILDABLE | NOT BUILDABLE with numbered blockers
```

---

## R1 blockers — resolution record

| # | R1 blocker | R2 resolution |
|---|------------|---------------|
| 1 | H14 no constraint_id/patch_context_digest on summary | bindings r2 §3.6 + harness flags + test |
| 2 | H8 no validate() for genomic_constraint_v1 | genomic_constraint_validator.py + tests |
| 3 | T1 no breach descriptor / synth stub | §4.5/§4.6 + genomic_constraint_synth.py |
| 4 | ops/ placement | ops/ exists; import bootstrap deferred to loop build handoff |

---

## After Codex BUILDABLE

Matt: `authorize build step 5 genomic loop` → Cursor implements loop + harness → Codex diff review.

---

## Codex verdict (2026-07-03)

**BUILDABLE**

Verification: `pytest tests/test_genomic_constraint_validator.py tests/test_proof_gate_console_bindings.py -v` → **16 passed**

R1 blockers closed:
1. H14 — Gate B surface: `--constraint-id`, `--episode-id`, `--patch-context-digest`; `genomic_episode` on summary; `patch_context_tree_digest()`
2. H8 — `genomic_constraint_validator.py` (types, capabilities, fragments, executable fields, constraint ID recompute)
3. T1 — `breach_descriptor_v1` + deterministic `synthesize_constraint_v1()` stub
4. `ops/` — exists; import bootstrap deferred to loop/harness build (scripts/chaos path pattern)

No remaining pre-build blockers.
