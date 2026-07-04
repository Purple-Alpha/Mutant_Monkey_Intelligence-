# M4 Evolution Gate Spec — r2.3 Closeout (§13.1 hardening)

**Date:** 2026-07-03  
**Lane:** Cursor (file only)  
**Trigger:** Claude adversarial throw-back on r2.2 §13.1 (F1–F5) — advisory, not BUILDABLE/Codex verdict  
**Spec:** `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` → **r2.3**

---

## Verdict (Cursor)

Throw-back **accepted and filed**. r2.2 §13.1 mechanically closed B-R2-01 (`draft_ok` in `pass_conditions`) but did not meet research fidelity or Evidence Harvesting blocker doctrine. r2.3 replaces §13.1 and wires supporting FSM/canary/phasing changes.

**Not claimed:** BUILDABLE, PERFECT, M4 closed, Phase 11 buildable without Codex re-review on r2.3 delta.

---

## What changed (r2.2 → r2.3)

| Area | Change |
|---|---|
| §13.1 | Full rewrite: per-exploit `exploit_captures[]`, sanitizer gate, chain-inline append, scope honesty, replay bar |
| §3.1 FSM | `append_inline` on M4 PASS intervals; `draft_patch_evidence.min_viable` on M4 entry |
| §9 | **M4-CANARY-026** `draft_patch_contamination`; 26 IDs |
| §14 | T14 tightened; **T15** replay false-patch (PERFECT only) |
| §14.1 | T8 row updated for per-exploit + CANARY-026 |
| §17 | Phase 10 builds `draft_patch_evidence` + C4 dress rehearsal; Phase 11 = 48h only |
| Constants | `DRAFT_PATCH_SCHEMA_V`, `DRAFT_PATCH_SANITIZER_MODULE` |
| Footnote [C] | r2.3 grounding note |

---

## Claude findings → disposition

| ID | Disposition |
|---|---|
| F1 | **Closed in spec** — per-exploit list + `complete()` over all attempts |
| F2 | **Closed in spec** — mandatory sanitizer + CANARY-026 fail-closed |
| F3 | **Closed in spec** — honesty clause; replay = PERFECT tier (T15), not `M4_MET` |
| F4 | **Closed in spec** — inline chain append at credit time |
| F5 | **Noted** — C4 dress rehearsal recommended; not a pass gate |

---

## Build impact

- **Phases 0–10:** unchanged authorization posture (still staged on Matt auth + Codex Phase 0 diff CLEAN).
- **Phase 10 (new scope):** must deliver `draft_patch_evidence.min_viable` before Phase 11.
- **Phase 11:** entry no longer lists draft-patch as separate gate — inherited from Phase 10 exit.
- **Codex:** prior R2 BUILDABLE (STAGED) was against **r2.2**; r2.3 Phase 10/11 delta needs plan re-review before treating Phase 11 as buildable.

---

## Next steps (for Matt)

1. Review §13.1 r2.3 block in spec (replacement is on disk).
2. Relay r2.3 delta to Codex for STAGED re-review (Phase 10/11 scope).
3. Continue Phase 0 → Codex diff CLEAN → Phase 1 on existing auth.
4. No commit unless Matt says "Cursor commit."
