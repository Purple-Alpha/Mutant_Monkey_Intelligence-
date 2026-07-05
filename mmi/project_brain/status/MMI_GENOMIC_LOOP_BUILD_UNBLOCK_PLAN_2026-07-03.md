# Genomic Loop — Build Unblock Plan (Codex R1)

**Date:** 2026-07-03  
**Authority:** Matt (Super)  
**Status:** NOT BUILDABLE — prerequisites required before `ops/genomic_realignment_loop.py`  
**Spec:** `architecture/MMI_GENOMIC_REALIGNMENT_LOOP_SPEC_2026-07.md` (r2)

---

## Codex verdict

Plan review **NOT BUILDABLE** — three real blockers, one non-blocker (ops/ exists).

---

## Slice 1 — H14 episode binding in Gate B summary

**Gap:** `apply_console_bindings()` emits suite/run/timestamp/patch/proof digests/rollback/budget only. No `constraint_id` or `patch_context_digest`.

**Fix (minimal):**

1. Amend `MMI_PROOF_GATE_CONSOLE_BINDINGS_SPEC_2026-07.md` → r2 section **§3.6 Genomic episode binding (H14)**:
   - Optional when `--genomic-episode` flag set (or when summary caller supplies fields)
   - `genomic_episode.constraint_id` — string, required for genomic loop invocations
   - `genomic_episode.patch_context_digest` — 64-char hex sha256 of patch context tree
   - `genomic_episode.episode_id` — optional audit cross-ref

2. `proof_gate_harness.py`:
   - CLI: `--constraint-id`, `--patch-context-digest`, `--episode-id` (optional)
   - `apply_console_bindings()` copies into summary when present

3. Loop PRESENTING check (H14) reads these fields from summary — no loop-side invention.

**Tests:** extend `tests/test_proof_gate_console_bindings.py` — summary includes binding fields when flags passed.

**Lane:** Cursor implement after Matt `authorize build genomic prereqs slice 1` OR bundle with slice 2.

---

## Slice 2 — H8 `genomic_constraint_v1` validator

**Gap:** `action_integrity_gate.py` is payment-action suite only — no validate() for constraint artifacts.

**Fix (minimal — avoid polluting payment suite):**

New module `chaos/genomic_constraint_validator.py`:

```text
validate_genomic_constraint(artifact: dict) -> tuple[str, list[str]]
  # returns ("VALID"|"REJECTED", reasons[])
```

Enforces spec §4.1:
- `artifact_version == genomic_constraint_v1`
- `constraint_type` ∈ ALLOWED_CONSTRAINT_TYPES
- `constraint_completeness == complete_single_bundle`
- `constraint_body` declarative only (denylist executable keys)
- `target` ∈ REGISTERED_CAPABILITIES registry (v1: explicit frozenset, extensible)
- size ≤ MAX_CONSTRAINT_BYTES
- `constraint_id` recompute match

**Tests:** `tests/test_genomic_constraint_validator.py` — T5/T7(b) cases from genomic spec.

**Lane:** Cursor implement; no change to payment action_integrity suite.

---

## Slice 3 — Breach descriptor + deterministic synth stub

**Gap:** Harness T1 needs fabricated breach input and honest happy-path synthesis.

**Fix (spec appendix — no ML):**

Add to genomic spec **§4.5 Breach descriptor v1** (`breach_descriptor_v1.json`):

```json
{
  "descriptor_version": "breach_descriptor_v1",
  "incident_id": "inc-<unique>",
  "critic_node": "<id>",
  "exploit_id": "<purple scenario id>",
  "mirror_agent_id": "<agent>",
  "payload": "<hostile payload string for route_to_mirror>"
}
```

Add **§4.6 v1 synthesis stub** (deterministic template):

```text
synthesize_constraint_v1(harvest, breach_descriptor) -> genomic_constraint_v1
  Maps harvest.exploit_class → constraint_type from fixed table:
    e.g. action_exfil → action_deny, rate_burst → rate_limit
  target from REGISTERED_CAPABILITIES lookup on exploit_id
  NO LLM; same harvest → same artifact (harness reproducibility)
```

Harness fixtures under `/tmp/mmi_genomic_loop/harness/fixtures/`.

**Lane:** Claude spec appendix OR Cursor adds §4.5/§4.6 to spec file → Codex re-review slice 3 only.

---

## Slice 4 — ops/ import bootstrap (build plan only)

**Not blocked.** Document in build handoff:

```python
# ops/genomic_realignment_loop.py bootstrap (mirror console_server / harness)
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "mmi/project_brain/chaos"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
```

Note: `ops/` contains legacy Social Architect agents — **new file must not import ops/run.py or council paths**. MMI hard stop.

---

## Re-review sequence

```text
1. Slice 1 + 2 implement + pytest  →  Codex plan re-review (bindings + validator)
2. Slice 3 spec appendix filed       →  Codex BUILDABLE on full step 5 package
3. Matt authorize build step 5       →  Cursor loop + harness + tests
4. Codex diff review                 →  CLEAN
```

---

## Parked while Matt researches

Step 5 main loop build stays **NOT AUTHORIZED**. Prereq slices can proceed independently when Matt returns.

Do not claim PERFECT / Phase 3 / evolution gate closed.
