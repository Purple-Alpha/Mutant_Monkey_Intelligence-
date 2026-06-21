# MMI PM Voice Layer — Owner Interface Contract

**Status:** §11 SIGNED 2026-06-20 by Matt Nichol. Mode A read-only build authorized for `scripts/mmi_pm_voice.py` only.

**Classification:** Governance contract · PM Voice Layer (single-voice reading-and-routing layer)

**Owner:** Matt Nichol

**Authority Domain:** Mutant Monkey Intelligence (MMI)

**Operator Authority:** Matt §11 sign-off required

**Authority repo:** `/home/socialarchitect/northstar` (Mutant Monkey Security)

**Build target (Mode A):** `scripts/mmi_pm_voice.py` (read-only, stdout only)

**Date:** 2026-06-20

**Implementation:** BLOCKED until Matt §11 sign-off + separate build authorization recorded in §11

---

## 1. What This Is

The PM Voice Layer is the **single thing Matt runs** for the daily owner answer. It reads existing MMI engines silently, collapses their outputs into one routed instruction, and speaks for them in one voice. It is a reading-and-routing layer — it replaces nothing, computes nothing of its own, and changes no engine.

Matt runs one command. He gets one answer: what needs him, why, who he hands it to, what to ignore, and what he does. Every line of that answer traces to a specific named engine.

---

## 2. The Problem It Solves

Matt currently runs multiple separate scripts (`mmi_dispatch.py`, `mmi_estimator.py`, `mmi_architect.py`, `mmi_superintendent.py`, `mmi_next_lane.py`, `mmi_crew_chain.py`, `mmi_pm_console.py`, `mmi_project_manager.py`) and reads multiple outputs to figure out one thing: what needs him next and who handles it. The engines are correct and must stay — they are the audit trail and the revision map. Reading all of them is the confusion.

Two things were missing:

1. **One voice** — a single output instead of many to interpret.
2. **Routing to a person** — every task has a who-handles-this answer (Claude / Cursor / Codex / Gemini+ChatGPT / Matt), applied by fixed roster lookup.

The PM Voice Layer adds exactly those two things and nothing else.

---

## 3. Hard Boundary — Faithful Relay Only

The PM Voice Layer is a **faithful relay**. Its single rule:

> Every line the PM speaks must trace to a specific engine's output. The PM adds nothing of its own except the fixed roster lookup (Section 5). It never re-computes, re-ranks, re-decides, or editorializes past what an engine said.

If the Estimator ranked `#52` first among buildable candidates, the PM reports that `#52` was ranked first **by the Estimator**. It does **not** independently select `#52` and present it as if the Estimator agreed. **Candidate surfacing is relayed from existing engine outputs (Estimator / next_lane / pm_console), not independently selected by PM Voice.**

The PM Voice Layer does **not**:

- Rank, score, or prioritize (Estimator's job — PM relays it).
- Blueprint or define done (Architect's job — PM relays it).
- Verify or judge working/not-working (Superintendent's job — PM relays it).
- Decide lifecycle/routing (dispatcher's job — PM relays it).
- Format Matt-facing summaries (Project Manager's job — PM may read it; PM Voice does not replace it).
- Select, authorize, approve, sign, or build anything (Matt's authority).
- Write to any engine, scoreboard, registry, state file, blueprint, or decision log.
- Populate `mmi/BLUEPRINT_OF_RECORD.md`.
- Run as a daemon, hook, or background process.
- Unlock AUTH-5 or enable registry-fed routing.
- Push.

It writes nothing. Read-only. Output to stdout only.

---

## 4. What It Reads (engines stay; PM Voice reads them)

The PM Voice Layer runs and reads existing engines silently. None are retired; all keep running, logging, and being separately inspectable.

| Engine | Invocation (repo-locked) | PM Voice reads |
|---|---|---|
| Dispatcher | `python3 scripts/mmi_dispatch.py --verify` (routing block via `MMI_CURRENT_STATE.md`) | `MODE`, queue posture |
| Estimator | `python3 scripts/mmi_estimator.py` | ranked buildable list, `BUILDABILITY_EXCLUSIONS`, `NO_BUILDABLE_CANDIDATES` |
| Architect | `python3 scripts/mmi_architect.py --candidate "<id>"` | blueprint / cannot-blueprint for relayed candidate only |
| Superintendent | `python3 scripts/mmi_superintendent.py --candidate "<id>"` | match/deviation for relayed built candidate only |
| Next lane menu | `python3 scripts/mmi_next_lane.py` | advisory menu rows (not authorization) |
| PM console | `python3 scripts/mmi_pm_console.py` | condensed NOW/NEXT/BLOCKED/ACTIVE_BLUEPRINT |
| Crew chain | `python3 scripts/mmi_crew_chain.py --candidate "<id>"` | detail command only; not required for default voice |
| Project Manager | `python3 scripts/mmi_project_manager.py --candidate "<id>"` | advisory PROCEED/REVISE/HOLD for relayed candidate only |
| Blueprint status | read `mmi/BLUEPRINT_OF_RECORD.md` | active plan status only; never populated |

**Candidate selection rule (Mode A):** When Architect / Superintendent / Project Manager / crew chain need a candidate id, PM Voice uses the **first buildable candidate from Estimator ranking** if any exist; otherwise the **first next_lane menu row** for missing-contract hold surfaces (relay only — not PM Voice selection). PM Voice never invents a candidate id.

**Relationship to `mmi_pm_console.py`:** PM console remains a separate condensed status command. PM Voice may read pm_console output or shared helpers; it does not retire pm_console.

---

## 5. The Roster (Matt-defined fixed lookup)

| Kind of next move | Hand it to |
|---|---|
| Draft / design a contract or spec | **Claude** |
| Build against a signed contract | **Cursor** |
| Review / verify / pre-build gate | **Codex** |
| Research / red-team / cross-check | **Gemini+ChatGPT** |
| Sign / authorize / final decision | **Matt** |

The PM Voice Layer maps engine-reported move type to roster name by table lookup only.

---

## 6. The One Output (Mode A envelope)

Allowed top-level envelope:

```text
MMI_PM_VOICE
```

Required fields:

```text
WHAT_NEEDS_MATT:
HAND_IT_TO:
WHY:
IGNORE_FOR_NOW:
YOU_DO:
SOURCE:
BOUNDARY:
```

`SOURCE` is mandatory — names which engine produced each claim.

When the pipeline is empty (ALL_CLEAR, no buildable candidates, NO_CURRENT_PLAN), PM Voice speaks plainly: nothing is signed/buildable; the move is contract drafting; roster lookup → **Claude**. It does not stop at raw status codes alone.

---

## 7. Revision Mode (optional flag; read-only)

When Matt requests revision (`--revision`), PM Voice enters read-only diagnostic mode reporting what can change, what cannot, and why — by pointing at the owning engine:

| Matt wants to change... | Owned by | Can it change? |
|---|---|---|
| What gets prioritized / ranked | Estimator (`mmi/MMI_ESTIMATOR_SCORING_CONTRACT.md`; weights locked MMI-DEC-039) | Yes — §11 amendment required |
| Buildability gates E12–E14 | Estimator amendment (`MMI-DEC-045`) | Yes — signed amendment path |
| What "done/flowing" means for a build | Architect / blueprint | Yes — re-author via Architect |
| Who handles a task type | Roster (Section 5) | Yes — Matt edits roster in contract |
| Lifecycle routing rules | Dispatcher doctrine | Yes — signed amendment path |
| Whether something is authorized | Matt only | Always Matt's |

Revision mode **reports** addresses and lock status; it performs no change.

---

## 8. Why the Engines Stay

The engines are retained, untouched, running, and separately inspectable. They are the audit trail and revision map. PM Voice never absorbs, replaces, or fuses them.

---

## 9. Falsifiable Acceptance Tests (T1–T10)

| Test | Pass condition |
|---|---|
| T1 | One command emits `MMI_PM_VOICE` default envelope |
| T2 | Every substantive line has engine receipt in `SOURCE` |
| T3 | Ranking/status matches engine output; no PM re-rank |
| T4 | `HAND_IT_TO` matches Section 5 roster lookup only |
| T5 | Empty pipeline → contract-draft direction routed to Claude |
| T6 | Zero writes to immutable paths (before/after digest) |
| T7 | No `mmi/BLUEPRINT_OF_RECORD.md` population |
| T8 | `--revision` read-only; no mutation |
| T9 | No forbidden self-applied authority tokens |
| T10 | All engines still run independently; PM Voice reads only |

---

## 10. What This Must Not Become

- Not a ninth decider voice.
- Not a replacement for engines.
- Not autonomous (no AUTH-5, no registry-fed routing).
- Not a writer.

---

## 11. Sign-off

**§11 SIGNED — Matt Nichol, June 20 2026.**

- [x] I approve this PM Voice Layer contract as written.
- [x] I separately authorize Mode A read-only build of `scripts/mmi_pm_voice.py`.

Confirmed: PM Voice is one voice that reads the engines and routes to the Matt-defined roster. It relays only — every line traces to a named engine; it adds nothing but the roster lookup. Candidate surfacing is relayed from existing engines, not independently selected by PM Voice.

Confirmed: the underlying engines stay intact as the audit trail and revision map.

Confirmed: this signature does **not** authorize writes to engines, scoreboard, registry, `MMI_CURRENT_STATE.md`, `mmi/BLUEPRINT_OF_RECORD.md` population, AUTH-5 unlock, or routing mutation.

Roster (Section 5) confirmed as written: **yes**

Matt Nichol
