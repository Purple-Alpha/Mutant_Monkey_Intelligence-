# MMI_DISPATCHER_ROUTING_OPERATOR_DECISIONS.md

> **OPERATOR DECISION LOG — REVIEW FOLLOW-ON.**
> Records Matt's decisions on the six findings from
> `mmi/reviews/MMI_DISPATCHER_ROUTING_ALIGNMENT_REVIEW.md`.
> **Does not authorize implementation.** Each decision becomes spec input for a
> future authorized dispatcher/routing patch lane.

**Authority:** Matt Nichol  
**Started:** 2026-06-16  
**Implementation status:** NOT AUTHORIZED

---

## Decision 1 — ALL_CLEAR candidate enumeration

**Status:** DECIDED (Matt, 2026-06-16)

**Question:** When `MODE: ALL_CLEAR`, should MMI emit concrete next-direction candidates
instead of only broad phase categories?

**Answer:** **YES — Option A** with off-scoreboard guardrail.

### Approved doctrine

When `MODE: ALL_CLEAR`, MMI emits concrete next-direction **candidates** (routing compass,
not authorization). Matt still **names the target**; MMI **surfaces valid choices**.

### Candidate sources (allowed)

1. Scoreboard `SIGNED_UNBUILT` rows
2. Signed §11 contracts on disk missing scoreboard rows (drift candidates only)
3. Existing design/research discovery functions (`get_next_concept_without_contract`,
   `get_next_research_task`, etc.)
4. Parked untracked concept drafts — **filename only**, `PARKED_DRAFT`

### Required labels (every candidate)

| Label | Meaning |
|---|---|
| `SCOREBOARD_READY` | On scoreboard with correct lifecycle row; normal sequencer input |
| `NEEDS_SCOREBOARD_ROW` | Signed contract or handoff reference exists; scoreboard row missing/wrong |
| `NEEDS_MMI_REVIEW` | Surfaced for visibility; classification or authority unclear |
| `PARKED_DRAFT` | Untracked concept; not authorized |
| `NOT_AUTHORIZED` | Candidate is not build/research/design authorization |

### Hard rules

- A candidate surfaced by ALL_CLEAR is **not authorization**.
- Off-scoreboard signed contracts **must not** appear as normal build-ready items.
- They must be labeled `NEEDS_SCOREBOARD_ROW` / `NEEDS_MMI_REVIEW` until Matt resolves drift.

### Example (off-scoreboard — required format)

```text
BUILD CANDIDATE:
Threat Intelligence Daemon
Source: signed contract on disk / handoff
Scoreboard status: MISSING SIGNED_UNBUILT ROW
Classification: NEEDS_SCOREBOARD_ROW
Authorization required: YES
Build implied: NO
```

### Implementation

`DO_NOT_PATCH_WITHOUT_AUTHORIZATION` — spec input for future dispatcher patch.

---

## Decision 2 — Matt target vs MMI lane doctrine

**Status:** DECIDED (Matt, 2026-06-16)

**Question:** Should the Matt-target / MMI-lane split be promoted into MMI governance docs
and dispatcher output labels?

**Answer:** **YES — Option A.**

### Approved doctrine

```text
Matt names the authorized target.
MMI assigns the lane by task shape.
Matt only picks the worker when routing affects authority, scope, live data, or material risk.
```

### Files for future patch (not authorized now)

- `mmi/MMI_PROTOCOL.md`
- `mmi/MMI_ROUTING_RULES.md`
- `scripts/mmi_dispatch.py` output labels

### Required dispatcher output labels (future implementation)

| Label | Value |
|---|---|
| `OPERATOR_NAMES_TARGET` | `Matt` |
| `MMI_ASSIGNS_LANE` | `YES` |
| `LANE_ESCALATION_TO_MATT` | `only on authority/scope/live-data/material-risk fork` |
| `BUILD_AUTHORIZATION_IMPLIED` | `NO unless Matt explicitly authorizes build` |

### Codex

Codex **must** be included in the MMI lane model (routing rules + authority matrix when patched).

### Guardrails

- `AGENTS.md` §2.2 remains the higher-level orientation source if wording conflicts.
- MMI docs must **mirror** `AGENTS.md`, not create a new authority model.
- Promoting doctrine to `mmi/` is **not** dispatcher implementation.

### Implementation

`DO_NOT_PATCH_WITHOUT_AUTHORIZATION` — spec input for future dispatcher/routing patch.

---

## Decision 3 — BUILD routing: Cursor → Codex pre-build → Cursor

**Status:** DECIDED (Matt, 2026-06-16)

**Question:** Should BUILD mode model the full pre-build loop?

**Answer:** **YES — Option A.** Full three-step lane.

### Approved doctrine

```text
BUILD = Cursor plan → Codex pre-build review → Cursor build
```

### Required future dispatcher behavior

1. Cursor drafts the implementation plan from the signed contract.
2. Codex reviews the plan before build begins.
3. Cursor builds only after Codex clears the plan.
4. Post-build Codex/Grok review remains separate and still applies where already required
   (`AWAITING_AUDIT` / Grok gate path unchanged).

### Required output fields (future implementation)

| Field | Value |
|---|---|
| `MODE` | `BUILD` |
| `ASSIGNED_TO` | `Cursor → Codex → Cursor` |
| `PRE_BUILD_REVIEW` | `Codex` |
| `BLOCKED_UNTIL` | `Codex clears build plan` |
| `OPERATOR_ACTION_REQUIRED` | `NO`, unless Codex finds authority/scope/material-risk fork |
| `BUILD_AUTHORIZATION_IMPLIED` | `NO`, unless Matt explicitly authorized the build target |

### Authority resolution

- `AGENTS.md` §2.1.2 controls.
- `MMI_THREAD_HANDOFF.md` is incomplete (post-build Codex only).
- Future implementation patch **must reconcile** `MMI_THREAD_HANDOFF.md` to include pre-build Codex step.

### Implementation

`DO_NOT_PATCH_WITHOUT_AUTHORIZATION` — spec input for future dispatcher/routing patch.

---

## Decision 4 — Independent review → Codex, OPERATOR_ACTION_REQUIRED: NO

**Status:** DECIDED (Matt, 2026-06-16)

**Question:** Should independent review route to Codex with `OPERATOR_ACTION_REQUIRED: NO`?

**Answer:** **YES — Option B.** Codex by default; explicit Matt escalation on fork.

### Approved doctrine

```text
Independent review lane = Codex.
MMI assigns Codex automatically when a gated adversarial suite has "Independent review pending."
Matt does not manually pick the reviewer during normal review routing.
```

### Required future dispatcher behavior

| Field | Value |
|---|---|
| `MODE` | `REVIEW` |
| `ASSIGNED_TO` | `Codex` |
| `NEXT_PROMPT_GOES_TO` | `Codex` |
| `OPERATOR_ACTION_REQUIRED` | `NO` |
| `LANE_ESCALATION_TO_MATT` | `only if Codex flags authority, scope, live-data, material-risk, or hardening-claim decision` |
| `BLOCKED_UNTIL` | `Codex review returns findings or clearance` |

### Hardening authority (separate from review routing)

- Codex may review evidence.
- Codex may recommend clearance or return.
- Codex **may not** grant `ADVERSARIALLY HARDENED` status.
- Matt remains the only hardening-claim authority per `MMI_AUTHORITY_MATRIX.md`.

### Guardrail

Review routing and hardening approval are **separate acts**. Routing to Codex is not
granting hardened status.

### Implementation

`DO_NOT_PATCH_WITHOUT_AUTHORIZATION` — spec input for future dispatcher/routing patch.

---

## Decision 5 — --verify doctrine checks

**Status:** DECIDED (Matt, 2026-06-16)

**Question:** Should `--verify` check routing-doctrine compliance?

**Answer:** **YES — Option B.** Add doctrine checks **after** implementation patch lands.

### Approved doctrine

`--verify` should eventually prove both:

1. Current-state consistency (existing checks).
2. Routing-doctrine compliance (new checks post-implementation).

`--verify` remains **consistency-only** until the authorized dispatcher patch.

Do **not** add doctrine checks before implementation — would create expected FAIL noise
and confuse the meaning of current PASS.

### Future required doctrine checks (post-implementation)

- ALL_CLEAR output includes concrete `CANDIDATES` with required labels (Decision 1).
- Off-scoreboard signed contracts labeled `NEEDS_SCOREBOARD_ROW` / `NEEDS_MMI_REVIEW`, not build-ready.
- Dispatcher output includes Matt-target / MMI-lane fields where applicable (Decision 2).
- BUILD mode includes Cursor → Codex pre-build review → Cursor build (Decision 3).
- REVIEW mode assigns Codex with `OPERATOR_ACTION_REQUIRED: NO` (Decision 4).
- `LANE_ESCALATION_TO_MATT` appears for authority/scope/live-data/material-risk forks.
- Codex exists in `mmi/MMI_ROUTING_RULES.md` and `mmi/MMI_AUTHORITY_MATRIX.md`.
- MMI docs do not contradict `AGENTS.md` §2.2.
- `--verify` catches regression if committed dispatcher behavior drops these fields later.

### Optional later

Separate `--verify-doctrine` command may be considered only if `--verify` becomes too broad.
**Do not add it now.**

### Implementation

`DO_NOT_PATCH_WITHOUT_AUTHORIZATION` — doctrine checks ship in same commit as dispatcher patch.

---

## Decision 6 — PROJECT_HANDSHAKE stale-line reconciliation

**Status:** DECIDED (Matt, 2026-06-16)

**Question:** How and when should `PROJECT_HANDSHAKE.md` be reconciled?

**Answer:** **YES — Option A.** Separate doc-only pass; MMI subsection only.

### Approved doctrine

`PROJECT_HANDSHAKE.md` must distinguish:

| Layer | Status |
|---|---|
| **Stage 1 dispatcher** | **ACTIVE** — file-based, manual-run, scoreboard-derived (`scripts/mmi_dispatch.py`) |
| **Runtime MMI integration** | **NOT active** — no live wiring, no autonomous execution, no always-on MMI process |
| **Automation** | **NOT active** — no watcher/hook auto-runs dispatcher or changes state |

### Future MMI governance-center wording (handshake patch)

```text
MMI GOVERNANCE CENTER:
- Dispatcher Stage 1: ACTIVE — file-based, scoreboard-derived (`scripts/mmi_dispatch.py`)
- Runtime MMI integration: NOT active
- Automation: NOT active
```

### Scope guard — do NOT refresh in this pass

- HEAD / commit snapshot
- Full STATE block
- NEXT ACTION block
- #99–#102 accepted / parent hardened summary
- Full ALL_CLEAR snapshot

Those require a later broader handshake refresh.

### Future authorized lane (not authorized now)

`PROJECT_HANDSHAKE_MMI_SUBSECTION_RECONCILIATION` — doc-only.

**Scope:** Update MMI governance-center subsection only. Do not modify dispatcher code,
routing rules, authority matrix, scoreboards, or full handshake state snapshot.

### Implementation

`DO_NOT_PATCH_WITHOUT_AUTHORIZATION` — input for later doc-only authorization.

---

## Operator decision pass — COMPLETE

All six decisions recorded. **Implementation status: NOT AUTHORIZED.**

| # | Decision | Answer |
|---|---|---|
| 1 | ALL_CLEAR candidate enumeration | A — with off-scoreboard guardrail |
| 2 | Matt target vs MMI lane | A — promote to `mmi/` + dispatcher labels |
| 3 | BUILD routing | A — Cursor → Codex pre-build → Cursor |
| 4 | Independent review | B — Codex default; Matt escalation on fork |
| 5 | `--verify` doctrine checks | B — add after implementation patch |
| 6 | Handshake reconciliation | A — MMI subsection only (separate doc lane) |

**Next lanes (each requires separate Matt authorization):**

1. `MMI_DISPATCHER_ROUTING_IMPLEMENTATION` — dispatcher + `mmi/` docs + doctrine verify checks + `MMI_THREAD_HANDOFF.md` reconciliation
2. `PROJECT_HANDSHAKE_MMI_SUBSECTION_RECONCILIATION` — handshake MMI block only

---

## Final rule

Decisions recorded here do not authorize dispatcher implementation, routing patches,
handshake edits, or next-phase build/research/design work until Matt opens a separate
implementation authorization lane.
