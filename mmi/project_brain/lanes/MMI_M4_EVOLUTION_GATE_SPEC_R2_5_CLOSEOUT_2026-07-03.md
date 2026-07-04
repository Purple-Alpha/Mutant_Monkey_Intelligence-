# M4 Evolution Gate Spec — r2.5 Closeout (Matt ruling)

**Date:** 2026-07-03  
**Lane:** Cursor  
**Trigger:** Matt — no shortcuts; full matrix bar for `M4_MET`  
**Spec:** `architecture/MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` → **r2.5**  
**Decision:** `lanes/MMI_MATT_RULING_M4_NO_SHORTCUTS_2026-07-03.md`

---

## Summary

r2.4 Finding C resolved by **Matt ruling**, not agent policy:

- **Rejected:** `M4_MET` as lesser milestone / capture-only finish / Option 1
- **Adopted:** replay-verified doctrine draft patch required for `M4_MET` (matrix pass-line #7)
- **Retained:** r2.3–r2.4 hardening (per-exploit, sanitizer, inline attempt log, terminology)

---

## Mechanical changes (r2.4 → r2.5)

| Area | Change |
|------|--------|
| Constants | `M4_REPLAY_REMEDIATION_REQUIRED`; `DRAFT_PATCH_SCHEMA_V` → `2026-07-03d` |
| FSM `draft_ok` | `complete()` **AND** `replay_complete()` |
| §13.1.4–13.1.6 | Replay required for `M4_MET`; Matt ruling recorded |
| T15 | `M4_NOT_MET`, not PERFECT-only |
| Summary | `perfect_gate_remaining: []` iff `M4_MET` |
| Terminal table | `M4_MET` = matrix-aligned, not "candidacy only" |

---

## Also in this commit

- Phase 0 H-L8-001: dynamic import bypass fix + tests (Codex NOT CLEAN → fix)
- r2.3/r2.4 closeout memos (historical)

**Not claimed:** BUILDABLE, PERFECT, M4 closed, Phase 1 auth, GATED
