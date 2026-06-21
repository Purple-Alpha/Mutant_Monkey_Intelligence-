# MMI PM Voice Always Routes — Completion Contract

**Document ID:** `MMI_PM_VOICE_ALWAYS_ROUTES`

**Status:** §11 SIGNED 2026-06-21 by Matt Nichol. Awaiting operator closeout after build verification.

**Amends:** `mmi/MMI_PM_VOICE_LAYER_CONTRACT.md` (§11 signed 2026-06-20); `mmi/MMI_HANDOFF_SIGNAL_AND_PM_ROUTING_CONTRACT.md` (closed MMI-DEC-051)

**Authority Domain:** Mutant Monkey Intelligence (MMI)

**Operator Authority:** Matt Nichol

**Build target (Mode A):** `scripts/mmi_pm_voice.py` routing completion + `scripts/mmi_handoff.py` state extensions (read path only for PM Voice)

---

## 0. Purpose

PM Voice must always route one next move with one named handler and one concrete `YOU_DO` line. No nameless dead-ends when engine evidence exists.

---

## 1. Routing priority (locked)

1. OPEN_HANDOFF — latest open `DONE_AWAITING_*` from `mmi/MMI_HANDOFF_LOG.md`
2. BUILDABLE_CANDIDATE — next_lane/estimator BUILDABLE relay → Cursor
3. SIGNED_UNRECONCILED_CANDIDATE — signed contract on disk, lifecycle not SIGNED_UNBUILT → Cursor reconcile
4. MISSING_CONTRACT_CANDIDATE — top missing-contract candidate → Claude contract draft
5. FALLBACK — concrete Matt or Estimator-review action when no higher branch matches

---

## 2. Scope

### In scope

- PM Voice routing priority and envelope (`IN_FLIGHT: none` when no open handoff)
- Signed-unreconciled detection (live: `#52` → `MMI_52_SIGNED_UNBUILT_RECONCILE_ONLY`)
- Handoff open states: `DONE_AWAITING_REVIEW`, `DONE_AWAITING_MATT`
- Tests T1–T10 in `tests/test_mmi_pm_voice.py`

### Out of scope

- Scoreboard / lifecycle mutation (except closeout text in separate lanes)
- Registry / default dispatch
- Blueprint-of-Record population
- AUTH-5 unlock
- Push

---

## §11 Sign-off

SIGNED. Matt authorizes PM Voice always-routes Mode A completion for read-only routing layer + handoff read path.

> Matt Nichol June 21st 2026
