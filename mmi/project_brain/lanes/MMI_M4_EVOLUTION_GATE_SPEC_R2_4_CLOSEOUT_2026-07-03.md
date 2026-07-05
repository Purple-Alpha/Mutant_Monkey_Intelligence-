# M4 Evolution Gate Spec — r2.4 Closeout (§13.1 A/B/C)

**Date:** 2026-07-03  
**Lane:** Cursor (file only)  
**Trigger:** Claude r2.3 grounded review — residuals A/B/C (advisory, not bless)  
**Spec:** `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` → **r2.4**  
**Supersedes:** r2.3 §13.1 wording for A/B; r2.3 closeout remains historical

---

## Disposition

| Finding | Action |
|---------|--------|
| **A** — `draft_patch_sha256` misnames capture bytes | **Filed:** `sanitized_capture_sha256`; §13.1.0 terminology table; sidecar `exploit_capture_record.json`; `draft_patch_sha256` reserved for PERFECT remediation only |
| **B** — coverage only as honest as interval-close log | **Filed:** inline `exploit_attempt` chain links at issue time; FSM hook; `complete()` vs chain; **T16** |
| **C** — `M4_MET` vs matrix PERFECT | **Flagged only:** `perfect_gate_remaining` on M4 summary; §13.1.6 Matt/research ruling — **not coded** into `pass_conditions` |

**Not claimed:** BUILDABLE, PERFECT, M4 closed, Phase 11 spec-complete until Matt rules C.

---

## Matt decision required (Finding C)

Choose one and record in staging / research:

1. **`M4_MET` = lesser milestone** — current spec; replay required separately for PERFECT (`perfect_gate_remaining: ["replay_remediation"]`).
2. **`M4_MET` must require replay** — move §13.1.5 into `draft_ok` / `pass_conditions` (aligns matrix §1.3 #7 with terminal status).

Until ruled, build Phase 10 on §13.1.1–13.1.3; do not treat 48h `M4_MET` as matrix PERFECT.

---

## Wiring delta (r2.3 → r2.4)

| Item | r2.4 |
|------|------|
| FSM | `exploit_attempt_log.attach` + `attempt_hook` during `INTERVAL_RUN`; `append_inline(chain, i)` without interval summary |
| Schema | `DRAFT_PATCH_SCHEMA_V` → `"2026-07-03c"` |
| Summary | `perfect_gate_remaining` required on M4 FINAL when replay unproven |
| Falsifiers | **T16** attempt-log laundering |
| CANARY-026 | signal source `exploit_capture.verify` |

---

## Next steps

1. Matt: rule on Finding C (option 1 vs 2).
2. Codex: re-review r2.4 Phase 10/11 delta when ready.
3. Phase 0: Codex diff re-review after dynamic-import fix (separate track).
4. No commit unless Matt says "Cursor commit."
