# MMI Blueprint of Record — Governance Contract

**Status:** DRAFT — UNSIGNED

**Classification:** Governance contract · Blueprint of Record population and revision

**Owner:** Matt Nichol

**Authority Domain:** Mutant Monkey Intelligence (MMI)

**Operator Authority:** Matt §11 sign-off required

**Authority repo:** `/home/socialarchitect/northstar` (Mutant Monkey Security)

**Parent model:** Five-role crew operating model (Estimator / Architect / Superintendent / PM / Blueprint of Record)

**Date:** 2026-06-20

---

## 1. Purpose

This contract governs **population and revision** of `mmi/BLUEPRINT_OF_RECORD.md` — the shared structural reference for the five-role crew. It defines what may be written, who may authorize writes, version discipline, and falsifiable violations.

The Blueprint-of-record is **advisory and revisable**. It records traceable structural intent for a **real Matt-authorized candidate for blueprint population**. It does **not** authorize build, routing, lifecycle promotion, or authority transfer.

---

## 2. Scope

### In scope

- Governance rules for `mmi/BLUEPRINT_OF_RECORD.md` content, population lanes, and revision discipline
- Relationship between Architect stdout `BLUEPRINT` output and on-disk Blueprint-of-record
- Falsifiable checks for population violations
- Version / plan-status rules (`CURRENT_PLAN`, `SUPERSEDED_PLAN`, `DRAFT_PLAN`)

### Out of scope

- Building or authorizing `scripts/mmi_architect.py` (see `mmi/MMI_ARCHITECT_BLUEPRINT_CONTRACT.md`)
- Estimator, Superintendent, or Project Manager tool builds
- Dispatcher routing, registry-fed routing, scoreboard writes, lifecycle mutation
- AUTH-5 autonomous selection or routing
- Signing or populating `mmi/BLUEPRINT_OF_RECORD.md` in this contract lane

---

## 3. Locked design decisions

| ID | Decision |
|---|---|
| G-D1 | **No build from blueprint alone:** population does not authorize implementation, tests, gates, or promotion |
| G-D2 | **No authority transfer:** population does not make Estimator rank, dispatcher mode, Architect stdout, Superintendent match, PM proceed label, or gate pass into authorization |
| G-D3 | **Architect produces content only:** The Architect produces blueprint content. Writing that content into `mmi/BLUEPRINT_OF_RECORD.md` requires a separate Matt-authorized population lane. The Architect does **not** gain direct write authority from this contract |
| G-D4 | **Matt-authorized candidate only:** population targets a **real Matt-authorized candidate for blueprint population**. Estimator ranking is **not** selection. Dispatcher `MODE: BUILD` / `MODE: AUDIT` / `MODE: ALL_CLEAR` is **not** population authorization |
| G-D5 | **One current plan:** the Blueprint-of-record may contain only one `CURRENT_PLAN` at a time. Older plans must be marked `SUPERSEDED_PLAN`, not deleted |
| G-D6 | **Traceable revision:** Matt may direct or approve revisions. Normal population/revision should route through Architect so the artifact remains traceable and checkable. This contract constrains MMI roles, not Matt's ultimate authority |
| G-D7 | **Registry-fed routing FORBIDDEN; AUTH-5 BLOCKED** |

---

## 4. Population and write rules

### 4.1 What counts as population

**Architect output to stdout is not population.** Population means writing or replacing content in `mmi/BLUEPRINT_OF_RECORD.md`, and requires a separate Matt-authorized population lane.

Population lanes must record `population_authorization` (operator lane name, decision id, or explicit Matt instruction reference).

### 4.2 What population does not authorize

Population does **not** authorize:

- Build implementation or test edits
- Scoreboard or registry mutation
- Dispatcher route assignment
- Marking `GATED`, `GOVERNED_AGENT`, or `COMPLETE`
- AUTH-5 unlock
- Default registry or production dispatch wiring
- Treating PM `PROCEED_FOR_MATT_REVIEW` as authorization

### 4.3 No autonomous population

No agent may populate or revise `BLUEPRINT_OF_RECORD.md` because Estimator ranked a candidate, dispatcher entered `BUILD` / `AUDIT`, Architect emitted `BLUEPRINT`, Superintendent emitted `MATCHES_BLUEPRINT`, Project Manager emitted `PROCEED_FOR_MATT_REVIEW`, or a gate passed. Population still requires separate Matt authorization.

### 4.4 Role boundaries (preserved)

- **No build.**
- **No population** without separate Matt-authorized lane.
- **No authority transfer.**
- **No scoreboard write.**
- **No registry write.**
- **No dispatcher route.**
- **No AUTH-5.**
- **No registry-fed routing.**
- Blueprint remains **advisory and revisable.**

---

## 5. Governance rules

| Rule | Requirement |
|---|---|
| R1 | Population requires explicit `population_authorization` recorded in the artifact |
| R2 | Only one `CURRENT_PLAN` per Blueprint-of-record file at any time |
| R3 | Superseded plans remain on disk as `SUPERSEDED_PLAN`; no silent deletion of prior plans |
| R4 | Every populated plan cites `source_contract` and `architect_blueprint_source` trace paths |
| R5 | **No self-applied authority conclusions.** A populated blueprint must not use `AUTHORIZED`, `BUILD_AUTHORIZED`, `SELECTED`, `COMPLETE`, `VERIFIED`, `PROMOTED`, `GOVERNED_AGENT`, `GATED`, `NEXT_DECIDED`, or similar terms as self-applied conclusions. It may cite signed source contracts, lifecycle rows, or gate artifacts as evidence |
| R6 | `non_authority_disclaimer` is mandatory on every populated plan |
| R7 | Estimator rank order, dispatcher mode, crew stdout envelopes, and gate artifacts may be cited as **evidence only** — never as population authorization |

---

## 6. Blueprint File Format / Version Rules

A populated Blueprint-of-record plan block must include:

| Field | Requirement |
|---|---|
| `candidate_id` | Matt-authorized candidate id (e.g. `#47`) |
| `candidate_name` | Human-readable name from manifest or contract |
| `source_contract` | Path to signed agent design contract on disk |
| `architect_blueprint_source` | Trace to Architect stdout capture, commit, or lane record — not implicit from stdout alone |
| `version_id` | Unique plan version identifier |
| `plan_status` | One of `CURRENT_PLAN` / `SUPERSEDED_PLAN` / `DRAFT_PLAN` |
| `population_authorization` | Matt-authorized lane name, MMI-DEC id, or explicit operator instruction reference |
| `created_at` | Timestamp or commit hash for population event |
| `supersedes` | Prior `version_id` when replacing a plan; empty when first plan |
| `revision_reason` | Why this plan version exists |
| `non_authority_disclaimer` | Statement that the plan is advisory and not build/route/promotion authority |
| `revision_history` | Ordered list of prior `version_id` values with brief reason |

**One-current-plan rule:** The Blueprint-of-record may contain only one `CURRENT_PLAN` at a time. Older plans must be marked `SUPERSEDED_PLAN`, not deleted.

---

## 7. Falsifiable checks

| Check | Violation |
|---|---|
| C1 | Population without recorded `population_authorization` |
| C2 | Population triggers build, scoreboard write, registry write, or dispatcher route change |
| C3 | Population claims AUTH-5 unlock or registry-fed routing |
| C4 | Populated plan missing `source_contract` or `architect_blueprint_source` |
| C5 | Populated plan missing `non_authority_disclaimer` |
| C6 | Self-applied forbidden authority conclusions in plan body (R5) |
| C7 | Prior `CURRENT_PLAN` deleted instead of marked `SUPERSEDED_PLAN` |
| C8 | More than one `CURRENT_PLAN` is a violation |
| C9 | Population without `population_authorization` is a violation |
| C10 | Architect stdout `BLUEPRINT` being treated as file population is a violation |
| C11 | Population triggered by Estimator, dispatcher, Architect, Superintendent, Project Manager, or gate output without separate Matt authorization is a violation |
| C12 | A populated blueprint missing `version_id`, `source_contract`, or `non_authority_disclaimer` is a violation |

---

## 8. Relationship to crew roles

| Role | May | May not |
|---|---|---|
| Estimator | Rank candidates; cite scoreboard evidence | Select candidate; authorize population |
| Architect | Emit stdout `BLUEPRINT` for Matt-selected candidate | Write `mmi/BLUEPRINT_OF_RECORD.md` under this contract |
| Superintendent | Advisory match/deviation report | Authorize population or promotion |
| Project Manager | Advisory `PROCEED_FOR_MATT_REVIEW` / `REVISE` / `HOLD` labels | Authorize population or routing |
| Matt | Direct, approve, or §11-sign population lanes | — |

---

## 9. Current artifact state

`mmi/BLUEPRINT_OF_RECORD.md` exists as a **placeholder** (§11 signed adoption shell). **Content population deferred.** This governance contract does not authorize population.

---

## 10. Open questions

- OQ1: Exact population lane naming convention for `population_authorization` field
- OQ2: Whether `DRAFT_PLAN` blocks coexist with `CURRENT_PLAN` during Matt review
- OQ3: Retention policy for `SUPERSEDED_PLAN` blocks beyond one-current-plan minimum

---

## 11. Sign-off

**§11 UNSIGNED — placeholder for Matt Nichol.**

- Governance contract only; does not authorize population
- Does not grant Architect direct write authority to `mmi/BLUEPRINT_OF_RECORD.md`
- Does not authorize build, routing, lifecycle promotion, or AUTH-5
