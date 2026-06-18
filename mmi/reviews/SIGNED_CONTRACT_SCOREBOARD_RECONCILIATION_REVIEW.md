# Signed Contract / Scoreboard Reconciliation Review

**Review ID:** `SIGNED_CONTRACT_SCOREBOARD_RECONCILIATION_REVIEW`  
**Date:** 2026-06-16  
**Authority:** Review-only lane — Matt authorized classification review, not build or scoreboard edits  
**Branch reviewed:** `safety/queue-drift-cleanup-20260528` @ `f0d2554`  
**Trigger:** MMI ALL_CLEAR surfaced three build-looking candidates, all labeled `NEEDS_SCOREBOARD_ROW` / `NOT_AUTHORIZED` (`MMI_CURRENT_STATE.md`, `scripts/mmi_dispatch.py` `HANDOFF_WAITING_BUILD_CONTRACTS`)

---

## Scope and guardrails

| Allowed | Not authorized by this review |
|---|---|
| Read contracts, scoreboard, handoff, drift detector, dispatcher logic | Build any candidate |
| Classify each candidate against MMI doctrine | Edit scoreboard rows |
| Recommend whether Matt must authorize scoreboard reconciliation | Edit dispatcher, routing rules, or authority matrix |
| Record doctrine tensions for operator follow-up | Promote concepts or wire runtime/automation |

**Final rule:** This review does **not** authorize build or scoreboard edits.

---

## Executive summary

| Candidate | Contract signed? | Scoreboard row (filename match)? | D2 alias match? | Recommended classification | Matt scoreboard reconciliation required? | Build implied |
|---|---|---|---|---|---|---|
| Load Fission v2 | YES (§13, 2026-06-13) | NO — #90 is `GATED` under v1 contract only | YES — alias `"Load Fission"` | **NEEDS_SCOREBOARD_ROW** | **YES** | **NO** |
| Specialisation Fission v2 | YES (§18, 2026-06-13) | NO — #91 is `GATED` under v1 contract only | YES — alias `"Specialisation Fission"` | **NEEDS_SCOREBOARD_ROW** | **YES** | **NO** |
| Threat Intelligence Daemon | YES (§11, 2026-06-14) | N/A — intentionally external to Northstar | Exempt (`_D2_EXEMPTIONS`) | **NEEDS_MMI_REVIEW** (Northstar `SIGNED_UNBUILT`: **DO_NOT_USE**) | **YES** — external-lane doctrine, not a missing Northstar row | **NO** (Northstar build queue) |

**Doctrine tension (important):** `scripts/detect_drift.py` D2 treats the two Fission v2 contracts as scoreboard-covered via historical agent-name aliases and treats Threat Intelligence as a documented exemption. `scripts/mmi_dispatch.py` uses a stricter rule: the **contract filename** must appear on a scoreboard row with a lifecycle status. That is why D2 reports clean while MMI still surfaces all three as off-scoreboard drift. Reconciliation should align operator intent with one of these models — not assume D2 clean means MMI build-ready.

---

## Candidate 1 — Load Fission v2

### Source file

`4. Product_Roadmap/Load_Fission_Contract_v2.md`

### Evidence of signature / §11 / approval

| Field | Evidence |
|---|---|
| Header status | `SIGNED — Matt Nichol June 13th 2026` |
| Authority line | `Signed by Matt Nichol June 13th 2026 (§13) — build authorization granted per this contract's scope` |
| Signature block | §13 — `Signed: Matt Nichol`, `Date: June 13th 2026` |
| Implementation gate | §12 — signed implementation authorized; lists LF2-D1..LF2-D12, governance artifacts, Class 2 adversarial tests, ELITE 85+, gate 0/0 |

Contract text explicitly states signing does **not** change scoreboard rows, deploy code, or rewrite historical gate records.

### Whether it is still current

**YES — current authoritative contract for Load Fission scope.**

- Supersedes `4. Product_Roadmap/Load_Fission_Contract.md` effective on signing (2026-06-13).
- v1 contract remains in repo as historical reference; D2 skips v1 when v2 sibling exists.
- Runtime code under `core/fission/load.py` still cites v1 contract (`Load_Fission_Contract.md`, §11 SIGNED 2026-06-12) — implementation predates v2; v2 adds material scope (governed ingestion pipeline, Canadian legal alignment, underwriter checklist, Class 2 adversarial suite, LF2-D10 policy-as-code, fission fallback mode, etc.).

### Whether it conflicts with newer MMI doctrine

**No authority conflict; lifecycle classification gap only.**

- Aligns with Operator Decision 1: off-scoreboard signed contracts must not read as build-ready; `NEEDS_SCOREBOARD_ROW` is correct MMI surfacing.
- Aligns with Operator Decision 2: contract-level Matt signature ≠ MMI `BUILD_AUTHORIZATION_IMPLIED: NO` until Matt names target and scoreboard reflects lifecycle.
- Scoreboard #90 `GATED` records the **v1 build closure** (2026-06-12). v2 is an **incremental upgrade/amendment build**, not a duplicate greenfield row — not `SUPERSEDED` in the sense of "do not build."

### Whether it has a scoreboard row

| Check | Result |
|---|---|
| Filename `Load_Fission_Contract_v2.md` on any scoreboard row | **NO** |
| Related row #90 Load Fission Controller | `GATED` — references §11-signed **v1** Load Fission contract (2026-06-12) |
| `detect_drift.py` alias `"Load Fission"` | Matches #90 — D2 considers contract covered |
| `mmi_dispatch.py` `_contract_scoreboard_build_state` | `off_scoreboard` (filename not in row text) |
| `SIGNED_UNBUILT` row for v2 | **MISSING** |

Also listed in `MMI_THREAD_HANDOFF.md` §Signed Contracts Waiting For Build: "Load Fission v2 — SIGNED, supersedes #90".

### Recommended classification

**Primary: `NEEDS_SCOREBOARD_ROW`**

Matt should authorize a **new scoreboard lifecycle row** (or an explicitly documented amendment row) that:

1. References `Load_Fission_Contract_v2.md` by filename.
2. Starts at `SIGNED_UNBUILT` for the v2 delta scope (or another documented lifecycle state Matt chooses).
3. Does **not** rewrite or downgrade historical #90 `GATED` v1 closure.

**Not recommended:**

| Label | Why not |
|---|---|
| `SIGNED_UNBUILT` (without Matt action) | No row exists yet — cannot self-promote |
| `SUPERSEDED` | v2 supersedes v1 **contract text**, not the fact that v1 was built and gated |
| `PARKED_DRAFT` | Fully signed build contract |
| `DO_NOT_USE` | Active signed authority for v2 scope |

### Whether Matt must authorize scoreboard reconciliation

**YES.**

Operator must decide row shape: new `#` row vs amendment notation on #90, and whether v2 work is `SIGNED_UNBUILT` → build → audit → re-gate #90 or a sibling row.

### Whether build is implied

**NO** (for MMI routing).

Contract §12 grants implementation authorization **within contract scope**, but MMI doctrine (Decisions 1–2, dispatcher `BUILD_AUTHORIZATION_IMPLIED: NO`) requires Matt to name target **and** scoreboard reconciliation before the dispatcher may treat this as a normal BUILD-queue item.

---

## Candidate 2 — Specialisation Fission v2

### Source file

`4. Product_Roadmap/Specialisation_Fission_Contract_v2.md`

### Evidence of signature / §11 / approval

| Field | Evidence |
|---|---|
| Header status | `SIGNED — Matt Nichol June 13th 2026` |
| Authority line | `Signed by Matt Nichol June 13th 2026 (§18) — build authorization granted per this contract's scope` |
| Signature block | §18 — `Signed: Matt Nichol`, `Date: June 13th 2026` |
| Implementation gate | §17 — signed implementation authorized; incorporates Load Fission v2 controls; Purple Team pairing table; eight adversarial tests; ELITE 85+, gate 0/0 |
| Cross-reference | §2 — all locked decisions from `Load_Fission_Contract_v2.md` apply |

### Whether it is still current

**YES — current authoritative contract for Specialisation Fission scope.**

- Supersedes `4. Product_Roadmap/Specialisation_Fission_Contract.md` effective 2026-06-13.
- Runtime `core/fission/specialisation.py` cites v1 contract (2026-06-12 build).
- v2 adds/locks Purple Team doctrine, net-new type governance, and expanded adversarial/implementation gates beyond the gated v1 implementation.

### Whether it conflicts with newer MMI doctrine

**No authority conflict; same lifecycle gap as Load Fission v2.**

- Companion docs (`Purple_Team_Attacker_Cost_Doctrine.md`, `Honeypot_Deception_Concept_Doc.md`) reference v2 as companion — consistent, not conflicting.
- Ordering note in scoreboard: Load Fission shared wiring landed first under v1; v2 reconciliation should preserve that sequencing intent if both rows are opened.

### Whether it has a scoreboard row

| Check | Result |
|---|---|
| Filename `Specialisation_Fission_Contract_v2.md` on any scoreboard row | **NO** |
| Related row #91 Specialisation Fission Controller | `GATED` — references §11-signed **v1** contract (2026-06-12) |
| `detect_drift.py` alias `"Specialisation Fission"` | Matches #91 — D2 considers contract covered |
| `mmi_dispatch.py` | `off_scoreboard` |
| `SIGNED_UNBUILT` row for v2 | **MISSING** |

Listed in `MMI_THREAD_HANDOFF.md`: "Specialisation Fission v2 — SIGNED, supersedes #91".

### Recommended classification

**Primary: `NEEDS_SCOREBOARD_ROW`**

Same reconciliation pattern as Load Fission v2: new lifecycle row referencing v2 filename, preserving #91 historical `GATED` v1 closure.

**Not recommended:** `SUPERSEDED`, `PARKED_DRAFT`, or self-assigned `SIGNED_UNBUILT`.

### Whether Matt must authorize scoreboard reconciliation

**YES.**

Likely paired decision with Load Fission v2 (shared `FissionEventLog`, advisory ordering, Purple Team pairing dependencies).

### Whether build is implied

**NO** (for MMI routing). Same reasoning as Candidate 1.

---

## Candidate 3 — Threat Intelligence Daemon

### Source file

`4. Product_Roadmap/Threat_Intelligence_Daemon_Design_Contract.md`  
(Concept source: `4. Product_Roadmap/Threat_Intelligence_Daemon_Concept_Doc.md`)

### Evidence of signature / §11 / approval

| Field | Evidence |
|---|---|
| Header status | `SIGNED — §11 authorized for build` |
| Date | June 14 2026 |
| Authority | `Matt Nichol — sole signing authority` |
| §11 Signature block | `Signed: Matt Nichol`, `Date: June 14th 2026` |
| Scope declaration | `Separate governed lane — completely independent of Northstar repo and build system` |
| Build target path | `/home/socialarchitect/mutant_monkey_intel/` (explicitly **not** `/home/socialarchitect/northstar/`) |

### Whether it is still current

**YES — signed design contract is current**, but **operational status is ambiguous across artifacts:**

| Artifact | Claim |
|---|---|
| `MMI_THREAD_HANDOFF.md` | "Signed Contracts Waiting For Build" — build to `mutant_monkey_intel/` |
| `scripts/detect_drift.py` `_D2_EXEMPTIONS` | "external component built under `/home/socialarchitect/mutant_monkey_intel/`; tracked as provisionally complete pending independent review/gate" |
| Filesystem (2026-06-16 review) | `mutant_monkey_intel/` exists with `monkey_intel_daemon.py`, `config/`, `store/`, `logs/daemon.log` — **external build appears present** |
| Northstar scoreboard | No row (by design) |
| `lab_records/2026-06-14_project_drift_detector_lab_record.md` RT-3 | D2 exemption documented; external lane acknowledged |

**Conclusion:** Contract is current; **build/waiting-list status is stale or split across lanes** — needs Matt/MMI doctrine clarification, not a Northstar `SIGNED_UNBUILT` row.

### Whether it conflicts with newer MMI doctrine

**Lane-model tension — not a contract invalidation.**

- Operator Decision 1 example lists Threat Intelligence as `NEEDS_SCOREBOARD_ROW` / missing `SIGNED_UNBUILT` — that example assumes Northstar scoreboard tracking.
- Drift detector RT-3 (2026-06-14) explicitly **exempted** this contract from D2 because it is external.
- Contract §Scope and TI-INV-2 require **no writes to Northstar repo** — placing this on the Blue Team Swarm scoreboard as a normal control-plane `SIGNED_UNBUILT` row would misrepresent architecture.

**Recommended doctrine resolution:** External signed components need an **external tracking model** (separate gate record, handoff status update, or permanent D2/MMI exemption sync) — not forced into Northstar scoreboard lifecycle.

### Whether it has a scoreboard row

| Check | Result |
|---|---|
| Row in `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` | **NO** (intentional) |
| `SIGNED_UNBUILT` on Northstar scoreboard | **N/A — DO_NOT_USE for Northstar row** |
| `detect_drift.py` | **Documented exemption** |
| `mmi_dispatch.py` `HANDOFF_WAITING_BUILD_CONTRACTS` | Still listed → surfaces as `NEEDS_SCOREBOARD_ROW` |
| External implementation path | Present on disk under `mutant_monkey_intel/` |

### Recommended classification

**Primary: `NEEDS_MMI_REVIEW`**

Matt should decide:

1. **Remove or reclassify** Threat Intelligence in `HANDOFF_WAITING_BUILD_CONTRACTS` / handoff "waiting for build" list if external build is provisionally complete.
2. **Define external gate tracking** (independent review/gate per D2 exemption text) without a Northstar scoreboard row.
3. **Sync MMI surfacing** with D2 exemption so ALL_CLEAR does not imply Northstar BUILD drift for an external lane.

**Secondary label for Northstar scoreboard specifically: `DO_NOT_USE`**

Do not add this contract as a Northstar `SIGNED_UNBUILT` control-plane row — contract and TI-INV-2 forbid that model.

**Not recommended:**

| Label | Why not |
|---|---|
| `NEEDS_SCOREBOARD_ROW` (Northstar) | Misaligns with D2 exemption and contract external-scope clause |
| `PARKED_DRAFT` | Signed §11 build contract |
| `SUPERSEDED` | No successor contract |

### Whether Matt must authorize scoreboard reconciliation

**YES — but reconciliation type is external-lane doctrine, not a missing Northstar row.**

Matt must authorize how MMI/handoff/drift/dispatcher represent:

- external build completion state,
- provisional gate pending independent review,
- and whether `HANDOFF_WAITING_BUILD_CONTRACTS` should retain this entry.

### Whether build is implied

**NO** for Northstar MMI BUILD routing.

External build may already exist; any further work (external gate, operational hardening, Matt review of `mutant_monkey_intel/`) is **outside this review's authorization** and outside the Northstar dispatcher BUILD queue.

---

## Cross-cutting findings

### 1. Handoff waiting list vs scoreboard lifecycle

`MMI_THREAD_HANDOFF.md` §Signed Contracts Waiting For Build predates dispatcher Decision 1 enforcement. All three entries are correctly surfaced by MMI as drift, but only the Fission v2 pair should resolve via **new Northstar scoreboard rows**. Threat Intelligence should resolve via **external-lane doctrine**, not scoreboard row addition.

### 2. D2 alias vs MMI filename strictness

For Fission v2, D2 alias matching `#90`/`#91` `GATED` rows can create a **false "reconciled" signal** while MMI correctly reports `NEEDS_SCOREBOARD_ROW`. Future operator decision (not in this review): tighten D2 aliases for `_v2` contracts, or add explicit v2 rows so both tools agree.

### 3. Runtime citation drift

`core/fission/load.py`, `specialisation.py`, `event_log.py`, and tests still cite v1 contract paths. Expected until v2 build is authorized and completed; not a reason to downgrade v2 contract currency.

### 4. Sequencing hint

Scoreboard narrative built Load (#90) before Specialisation (#91) under v1. If Matt authorizes v2 rows, preserve that ordering unless explicitly overridden.

---

## Recommended operator next steps (Matt authorization required)

| Step | Action | Authorizes build? | Authorizes scoreboard edit? |
|---|---|---|---|
| A | Approve scoreboard reconciliation plan for Load Fission v2 (`NEEDS_SCOREBOARD_ROW` → new row) | NO | Requires separate explicit authorization |
| B | Approve scoreboard reconciliation plan for Specialisation Fission v2 (likely paired with A) | NO | Requires separate explicit authorization |
| C | Decide Threat Intelligence external-lane tracking; update handoff/dispatcher exemption alignment | NO | NO (Northstar scoreboard) |
| D | After A–C, Matt may name a build target in a new authorized round | Only then | Only if row edits separately authorized |

---

## Review closure

| Item | Status |
|---|---|
| Three ALL_CLEAR drift candidates reviewed | **COMPLETE** |
| Scoreboard edited | **NOT DONE** (out of scope) |
| Dispatcher edited | **NOT DONE** (out of scope) |
| Build authorized | **NO** |
| Build implied by this review | **NO** |

**This review does not authorize build or scoreboard edits.**
