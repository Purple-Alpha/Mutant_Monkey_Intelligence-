# MMI Handoff Signal and PM Routing — Implementation Contract

**Document ID:** `MMI_HANDOFF_SIGNAL_AND_PM_ROUTING`

**Status:** §11 SIGNED 2026-06-21 by Matt Nichol. Lane **CLOSED** per MMI-DEC-051. Resolves gate blockers recorded in `audit_outputs/mmi_handoff_signal_pm_routing_20260621T053223Z.md` via operator §11 closeout (dispatch authorized build at `953e1bc`; signature records scope and closes lane).

**Authority Domain:** Mutant Monkey Intelligence (MMI)

**Operator Authority:** Matt Nichol

**Build commits:** `953e1bc` (handoff signal + PM routing Mode A); `ddb86bc` (handoff log awaiting-sign line)

---

## 0. Purpose

Append-only handoff signal loop so PM Voice surfaces the latest open in-flight task instead of generic empty-queue contract-draft text when work is awaiting Matt closeout, sign, or gate.

---

## 1. Scope signed and closed

### In scope (built and authorized)

- `mmi/MMI_HANDOFF_LOG.md` — append-only handoff records
- `scripts/mmi_handoff.py` — `--append` writer (one line per call; no edits/deletes)
- `scripts/mmi_pm_voice.py` — reads handoff log; emits `IN_FLIGHT`; routes `next_step` via roster lookup
- `tests/test_mmi_handoff.py` — T1–T7
- `tests/test_mmi_pm_voice.py` — handoff routing updates

### Out of scope (not authorized by this lane)

- Scoreboard / lifecycle mutation
- Registry / default dispatch
- Blueprint-of-Record population
- AUTH-5 unlock
- `#47` / `#48` changes
- Rebuild of handoff or PM Voice behavior beyond closeout/status text

---

## 2. Locked behavior

- Handoff log is append-only; PM Voice reads only; PM Voice never writes the log.
- Open handoff = latest line with state starting `DONE_AWAITING_`.
- Roster routing from `next_step`: draft→Claude; build→Cursor; review/gate→Codex; research→Gemini+ChatGPT; sign/close→Matt; no match→Matt.
- If no open handoff, PM Voice falls back to existing engine-based routing.

---

## 3. Gate resolution

Prior Grok gate (`mmi_handoff_signal_pm_routing_20260621T053223Z.md`) blocked because `MMI_PM_VOICE_LAYER_CONTRACT.md` text listed only `mmi_pm_voice.py`. Matt dispatch 2026-06-20 explicitly authorized the handoff loop build; this §11 signature and MMI-DEC-051 closeout record that authority and close the lane.

---

## §11 Sign-off

SIGNED and CLOSED. Matt approves the completed **HANDOFF_SIGNAL_AND_PM_ROUTING** lane. No further build, rebuild, or scope expansion without a new authorized lane.

> Matt Nichol June 21st 2026
