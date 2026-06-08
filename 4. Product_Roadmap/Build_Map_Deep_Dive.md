# Build Map — Spec-First Deep Dive

**Status:** DRAFT 2026-06-08. Authored from the Claude design-lane proposal (Build Map state machine) with six operator-approved fixes folded in (2026-06-08). This draft is **not signed** and authorizes **no code**, **no `complete_gate.py` amendment**, **no new write path**, and **no runtime change**. §11 signature is operator-only. Adopting this Map is itself a path-setting (butterfly) decision per §4 and requires Matt's §11 signature to become live authority.

**Date:** 2026-06-08

**Owner:** Matt Nichol

**Source-of-truth links:**
- `AGENTS.md` §3.2 (the Build Loop this Map formalizes into a deterministic state machine; the Map does not replace the loop, it makes its branches deterministic)
- `4. Product_Roadmap/Next_Action_Decision_Rubric_Deep_Dive.md` (§11-SIGNED tactical scorer; the Map generates the post-triage candidate set, the rubric ranks it — D2 preserved: rubric ranks, human selects the genuine locks)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (Build Sequencer; canonical candidate generator the Map reads and annotates)
- `think_sheet.md` (idea filter; the Map's IDEA_INTERRUPT route writes here, and `promote`-band ideas must pass its 7-question stress-test gate before reaching the scoreboard)
- `PROJECT_HANDSHAKE.md` (home of the one-screen CURRENT NEXT ACTION header, §9)
- `decision_cycles_log.md` (rubric-cycle log; see §10 Q2 for the triage-logging dependency)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (§11 signature convention; Evidence Stage model the Map respects)

This document is the spec-first contract for a deterministic build-decision state machine that answers "what is the single next action" without presenting the operator a menu for routine work.

---

## §0 Purpose

The project has a candidate generator (the Build Sequencer scoreboard) and a candidate scorer (the Next-Action Decision Rubric). It does **not** have a deterministic controller that, from any state, yields **exactly one next action** and stops for the operator **only** on a defined, minimal set of genuine locks.

Without that controller, every time reality leaves the happy path — a mislabeled candidate, a blocked candidate, a breadth-vs-depth choice, a mid-build idea — the assistant falls back to presenting "N honest paths, your call." That is the exact "what's next?" failure the operator has outlawed: the operator should not be the router for routine work.

This Map exists to solve one problem:

> From any state, deterministically produce THE single next action. Resolve all routine decisions automatically and proceed. Stop and wait for the operator only on §11 signatures, butterfly/path-setting decisions, and money/legal.

---

## §1 Scope

### In scope (v1)
- An eight-state deterministic build-decision state machine (§3) with one async route (IDEA_INTERRUPT).
- A testable AUTO-DECIDE vs OPERATOR-LOCK taxonomy with worked precedents (§4).
- A per-layer pre-flight triage (§5) that validates a candidate before it can become "next."
- Deterministic handling for the five friction cases that have actually occurred (§6).
- A breadth-vs-depth track-selection rule and an exhaustion rule that always names a specific unblock action (§7).
- A definition of how the Map consumes and annotates existing artifacts without duplicating them (§8).
- The one-screen CURRENT NEXT ACTION header and its (doctrine-level) maintenance rule (§9).

### Out of scope (v1)
- No change to the rubric's authority model (rubric ranks; the Map never converts a score into an executed decision for an OPERATOR-LOCK item).
- No autonomous action beyond analyze / flag / route / rank / draft. The Map never commits, signs, deploys, or promotes Evidence Stages.
- **No `complete_gate.py` amendment.** Gate enforcement of header freshness is a named, unauthorized dependency (§10 Q1).
- **No new write path to `decision_cycles_log.md` for triage decisions.** That is a named, unauthorized dependency (§10 Q2).
- No replacement of the Build Loop (`AGENTS.md` §3.2); the Map formalizes it.
- No new persistence surface beyond the existing scoreboard / handshake / log writes already authorized.

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

| # | Decision | Locked value |
|---|---|---|
| D1 | Core invariant | From any state, exactly one next action. No forks for routine work. The operator touches exactly three things: §11 signatures, butterfly/path-setting decisions, money/legal. |
| D2 | Authority preserved | The Map generates candidates and enforces triage; the rubric scores; the human decides genuine locks. The Map never overrides the rubric's D2 (rubric ranks, human selects) and never self-authorizes a lock item. |
| D3 | State set | Eight states: IDLE, TRIAGE, RECLASSIFY, UNBLOCK, DRAFT_CONTRACT, OPERATOR_LOCK, BUILD_ACTIVE, COMMIT_UPDATE. Plus one async route: IDEA_INTERRUPT (not a state). |
| D4 | Drafting is auto, signing is the lock (FIX 1) | Producing an Agent Design Contract is AUTO-DECIDE work performed in DRAFT_CONTRACT. Only the §11 signature is an OPERATOR_LOCK. The Map never stops for a missing contract; it drafts, then stops only for the signature. |
| D5 | Per-layer triage (FIX 2) | Triage checks are layer-aware. The "one pure detector" check applies only to Detection-layer breadth candidates. Synthesizing agents (Verification / Evidence / Challenge / Learning, including aggregates) are validated against their declared input artifacts, not a single detector. |
| D6 | Re-entry path (FIX 3) | RECLASSIFY and UNBLOCK rows carry a named re-triage trigger. When that trigger is satisfied (detector built, boundary contract signed, dependency/depth gate opened), the row automatically re-enters TRIAGE. Nothing is benched permanently by silent omission. |
| D7 | Idea route through the stress-test gate (FIX 5) | IDEA_INTERRUPT routes a new idea to `think_sheet` and scores it. A `promote`-band result routes to the think_sheet 7-question stress-test gate; only a passed stress test promotes the idea to the scoreboard. Non-promote bands park in think_sheet. The build never pauses for this. |
| D8 | Track selection + exhaustion (§7) | Breadth-vs-depth is selected by a deterministic rule keyed off the scoreboard DEPTH GATE field. The exhaustion path always names a specific unblock action; the Map never outputs "I don't know what to do next." |
| D9 | Tie-break | Equal rubric scores break by layer order (Detection → Verification → Evidence → Challenge → Learning), then by scoreboard row order (lower wins). The operator is never the tie-breaker for routine work. |
| D10 | Preserved invariants | No autonomous action; §11 signatures stay human; the audit gate stays load-bearing and has no override path; best-in-class selection (cost/cheapness is never a scoring axis or a point in favor). |

---

## §3 State machine

Eight states. Every transition is deterministic.

```
IDLE
  │  pull top candidate from scoreboard (post track-selection, §7)
  ▼
TRIAGE  (§5 per-layer checks, in order; first failure routes out)
  │
  ├─ FAIL (label error: no/!matching detector, wrong layer-as-label) ─► RECLASSIFY
  │                                                                        │ mark row, note expected-vs-actual, set re-triage trigger (D6)
  │                                                                        └─► IDLE (pull next)
  │
  ├─ BLOCKED (real boundary/stateful/undeclared dependency) ─► UNBLOCK
  │                                                              │ mark row BLOCKED:NEEDS_BOUNDARY_CONTRACT; add boundary-contract row above it
  │                                                              │ (TRACK=BREADTH, BLOCKERS=NONE); set re-triage trigger (D6)
  │                                                              └─► IDLE (the boundary contract is itself the next candidate)
  │
  ├─ PASS, no signed contract ─► DRAFT_CONTRACT  (AUTO; FIX 1 / D4)
  │                                  │ draft the Agent Design Contract (authorizes no code)
  │                                  └─► OPERATOR_LOCK (§11 needed)
  │                                          │ signed ──► BUILD_ACTIVE
  │                                          └─ not yet ─► stays in OPERATOR_LOCK (no alternative offered)
  │
  └─ PASS, contract already signed ─► BUILD_ACTIVE
                                         │ build slice; run gate (§5 of loop)
                                         ├─ slice complete, gate clean ─► COMMIT_UPDATE
                                         │                                    │ update scoreboard + log + handshake header (§9)
                                         │                                    └─► IDLE (pull next)
                                         └─ §11 placeholder hit mid-slice ─► OPERATOR_LOCK ─ signed ─► BUILD_ACTIVE
```

**IDEA_INTERRUPT (async route, not a state):** any new idea routes directly to `think_sheet` (D7) and the current state continues unchanged. The Map never pauses a build for an idea.

---

## §4 AUTO-DECIDE vs OPERATOR-LOCK taxonomy

**OPERATOR-LOCK — stop and wait.** True if ANY of:

| Criterion | Test |
|---|---|
| §11 signature required | Does an Agent Design Contract (or this Map, or a spec revision) have an unsigned §11 placeholder that must be live before work proceeds? |
| Butterfly / path-setting | Does this change product identity, the revenue model, an architecture/layer boundary, or an agent's authority ceiling? |
| Money or legal | Does this touch pricing, contracts, compliance claims, or real-customer data handling? |
| Evidence Stage promotion | Does this advance an agent past its current Evidence Stage? |

If none are true → **AUTO-DECIDE**: the Map resolves and proceeds without asking.

**Worked precedents (FIX 4) — keeps the butterfly test mechanical, not a disguised fork:**

| Decision | Verdict | Why |
|---|---|---|
| Retire the build/audit queue as ordering authority | OPERATOR-LOCK | Changed an architecture/authority boundary (done via §12 revision + consequence matrix). |
| Adopt this Build Map | OPERATOR-LOCK | Path-setting: changes how the whole build is governed. |
| Open the real-data intake / depth gate | OPERATOR-LOCK | Path-setting + touches real-customer data handling. |
| Change an agent's layer or authority ceiling | OPERATOR-LOCK | Authority-boundary change. |
| Pricing / client-facing claim change | OPERATOR-LOCK | Money/legal. |
| Pick the next clean breadth wrap | AUTO-DECIDE | Routine candidate selection (scoreboard rank + triage). |
| Mark a mislabeled row RECLASSIFY | AUTO-DECIDE | Triage correctness, not a path change. |
| Add a boundary-contract row above a blocked candidate | AUTO-DECIDE | Queues the unblock action; the contract's §11 is the only lock. |
| Route a new idea to think_sheet | AUTO-DECIDE | Filtering, not adoption. |
| Choose slice order within a candidate | AUTO-DECIDE | Mechanical (spec section order). |
| Break a rubric tie | AUTO-DECIDE | Deterministic rule (D9). |

---

## §5 Pre-flight triage (per-layer; FIX 2)

Triage runs before any candidate becomes "next." Checks run in order; the first failure routes the candidate out and no further checks run. The candidate's declared layer selects the check variant.

**Detection-layer breadth candidates:**
1. **Detector exists and is clean** — the candidate's detector function exists, is a pure function (no side effects, no per-tenant state mutation), and `agent_id` maps unambiguously to one detector. Failure → RECLASSIFY.
2. **Layer is correct** — declared layer matches behavior. A detector that reads/writes a per-tenant store is not Layer 2; a detector that synthesizes across contributions is not Layer 2. Failure → RECLASSIFY (label error) or UNBLOCK (real boundary problem).
3. **No hidden state / undeclared dependency** — no dependency on infrastructure not yet built (Drift Watch, Production Evidence Store, real-data intake). Failure → UNBLOCK with the named missing dependency.
4. **Contract status** — a signed Agent Design Contract exists, or none exists. If none exists → DRAFT_CONTRACT (auto), then OPERATOR_LOCK for the signature (D4). A drafted-but-unsigned contract → OPERATOR_LOCK.

**Non-Detection candidates (Verification / Evidence / Challenge / Learning, incl. aggregates):**
1. **Declared inputs exist and are governed** — the contributions / records / artifacts the agent synthesizes are produced by agents already at `GOVERNED_AGENT`. (Replaces the single-detector check; a synthesizing agent legitimately has no one detector.) Failure → UNBLOCK (named missing upstream agent) or RECLASSIFY (label error).
2. **Layer is correct** — declared layer matches behavior. Failure → RECLASSIFY or UNBLOCK.
3. **No hidden state / undeclared dependency** — as above. Failure → UNBLOCK.
4. **Contract status** — as above (D4).

All checks pass → BUILD_ACTIVE (if contract signed) or DRAFT_CONTRACT → OPERATOR_LOCK (if not).

---

## §6 Friction case handling (deterministic, no forks)

**Case 1 — Mislabeled candidate** (Check 1 or 2 fires): mark row RECLASSIFY; note expected-vs-actual; set re-triage trigger (D6); pull next candidate. Output: *NEXT ACTION — build [next clean candidate].* Operator not asked.

**Case 2 — Blocked candidate** (Check 2 or 3 fires): mark row BLOCKED:NEEDS_BOUNDARY_CONTRACT; add a boundary-contract row above it (TRACK=BREADTH, BLOCKERS=NONE) — it is itself the unblock action; set re-triage trigger; the boundary contract becomes the next candidate (→ DRAFT_CONTRACT → OPERATOR_LOCK for its §11). Output: *NEXT ACTION — draft boundary contract for [blocked candidate]; its §11 signature unblocks it.*

**Case 3 — Breadth vs depth** (§7): while DEPTH GATE = CLOSED, always TRACK=BREADTH. Output: *NEXT ACTION — wrap next BREADTH candidate.* No fork.

**Case 4 — Idea interrupt** (async; D7): route to think_sheet, score it. `promote` → 7-question stress-test gate → if passed, add to scoreboard; else park. Non-promote → park. Output: *CURRENT BUILD CONTINUES.* Operator not interrupted.

**Case 5 — Genuine operator lock** (Check 4, or a §11 placeholder hit mid-slice): state = OPERATOR_LOCK. Output exactly: *BLOCKED ON §11 SIGNATURE — [spec name].* No alternative candidates offered; the lock is the output.

---

## §7 Track selection + exhaustion

Deterministic, no operator input:

```
IF depth_gate == OPEN AND an agent is at Evidence Stage 1 with >= 3 real samples available:
    TRACK = DEPTH (promote that agent — note: the promotion itself is an OPERATOR-LOCK, §4)
ELSE IF any BREADTH candidate passes triage:
    TRACK = BREADTH (wrap next clean detector)
ELSE IF all BREADTH candidates are BLOCKED or RECLASSIFY:
    NEXT ACTION = "unblock [highest-priority blocked candidate]: [specific named action]"
ELSE IF no candidates remain of any kind:
    NEXT ACTION = "open the real-data intake / depth gate" (named butterfly decision — OPERATOR-LOCK)
```

The Map never outputs "I don't know what to do next." The only legitimate dead-end is the real-data intake / depth gate, which is correctly an operator lock. `depth_gate` is a scoreboard header field (OPEN/CLOSED); flipping it OPEN is an OPERATOR-LOCK (§4).

---

## §8 How the Map consumes existing artifacts

| Artifact | Map's relationship |
|---|---|
| Scoreboard (Build Sequencer) | Reads for candidates; writes BLOCKERS, TRACK, RECLASSIFY/BLOCKED status, LAST_UPDATED after every slice (existing write path, Build Loop Step 6.5). |
| Next-Action Decision Rubric | The Map generates the 3–7 post-triage clean candidate set and feeds it to the rubric; rubric ranks; D2 preserved. The Map does not score. |
| think_sheet | Receives all new ideas via IDEA_INTERRUPT; promotion gated by the 7-question stress test (D7). |
| decision_cycles_log | Updated at COMMIT_UPDATE by Build Loop Step 7 (existing write path). Triage-decision logging is a **separate, unauthorized** write path — see §10 Q2. |
| Audit gate (`complete_gate.py`) | Unchanged and load-bearing; the gate must pass before any transition to COMMIT_UPDATE. Header-freshness enforcement is a **separate, unauthorized** amendment — see §10 Q1. |
| Agent Design Contracts | Read by triage Check 4; §11 status drives DRAFT_CONTRACT / OPERATOR_LOCK. |
| Handshake | The CURRENT NEXT ACTION header (§9) is written here at every COMMIT_UPDATE (existing write path). |

Separation of duties: the Map generates candidates and enforces triage; the rubric scores. These are different jobs and stay separate.

---

## §9 Artifact form + one-screen header

Home: top of `PROJECT_HANDSHAKE.md`, replaced every session at Build Loop Step 6.5.

```
═══════════════════════════════════════════════
CURRENT NEXT ACTION (as of [commit hash])
═══════════════════════════════════════════════
STATE: [IDLE / TRIAGE / DRAFT_CONTRACT / BUILD_ACTIVE / OPERATOR_LOCK / UNBLOCK / RECLASSIFY / COMMIT_UPDATE]
TRACK: [BREADTH / DEPTH / UNBLOCK]
DEPTH GATE: [OPEN / CLOSED]

NEXT ACTION:
  [One sentence. Specific. Actionable. No forks.]

IF BLOCKED:
  [Named §11 spec or named gate. Nothing else proceeds.]

CANDIDATE QUEUE (post-triage, ranked):
  1. [agent_id] — [layer] — [BREADTH/DEPTH] — rubric [n/10]
  2. ...
  3. ...

LAST UPDATED: [commit hash] [timestamp]
═══════════════════════════════════════════════
```

**Maintenance rule (v1, doctrine-level):** Build Loop Step 6.5 writes this header; a swarm/agent slice that does not update it is incomplete. This is enforced by doctrine in v1, identical to the current treatment of Steps 0.5/6.5. **Gate-level enforcement of header freshness is NOT part of v1** — it is the unauthorized dependency in §10 Q1.

A cold future session opens `PROJECT_HANDSHAKE.md`, reads ~10 lines, and knows the single next action without re-derivation.

---

## §10 Open Questions (operator-only)

- **Q1 — Gate enforcement of header freshness (UNAUTHORIZED DEPENDENCY).** Enforcing "a commit that touches any agent file or spec fails the gate unless the CURRENT NEXT ACTION header was updated" requires a `complete_gate.py` amendment. That amendment is a **code change that needs its own Build Authorization (signed scope) before implementation.** The Map does **not** assume this enforcement exists. Until separately authorized and built, header freshness is doctrine-enforced only (like Build Loop Steps 0.5/6.5 today). Resolution at §11 does not authorize the gate change.
- **Q2 — Triage-decision logging to `decision_cycles_log.md` (UNAUTHORIZED DEPENDENCY).** Writing triage outcomes (RECLASSIFY/BLOCKED with rationale) into `decision_cycles_log.md` is a **new write path that must be explicitly authorized** before implementation. The Map does **not** assume it. Until authorized, triage decisions are recorded only on the scoreboard row + its note (existing write path). This is the audit trail for triage in v1.
- **Q3 — State location.** v1 holds live state in the `PROJECT_HANDSHAKE.md` header (§9). Whether a dedicated machine-readable state file is warranted is deferred until the header proves insufficient.
- **Q4 — Non-Detection triage refinement.** The per-layer triage checks for Verification / Evidence / Challenge / Learning (§5) are specified from first principles; they will be refined the first time a non-Detection candidate is actually triaged, captured as a spec revision if needed.

§11 signature confirms D1–D10 and adopts the Map as live build authority, **excluding** the §10 Q1/Q2 dependencies, which remain unauthorized until their own signed scope.

---

## §11 Sign-off

PENDING. Operator-authored signature required before the Map becomes live build authority. Signing adopts D1–D10 and §3–§9; it does **not** authorize the §10 Q1 gate amendment or the §10 Q2 triage-logging write path.

> [Matt Nichol — Build Map — date]
