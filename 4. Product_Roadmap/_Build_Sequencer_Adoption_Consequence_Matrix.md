# Build Sequencer Adoption Consequence Matrix

**Status:** Operator-triggered Consequence Matrix under Butterfly Hard-Stop (AGENTS.md §7.1). Pre-spec, non-binding until operator records outcome.  
**Date:** 2026-06-08  
**Owner:** Matt Nichol  
**Decision layer:** Path-setting — canonical next-action authority chain + signed rubric substance (D13).

---

## Decision

**Decision:** How should the project resolve the "what's next" trap — keep `PROJECT_BUILD_AND_AUDIT_QUEUE.md` as the canonical ordering authority (Option A) or retire queue ordering authority and move candidate generation to the 70-agent scoreboard with a signed rubric D13 revision (Option B)?

**Why this matters:** The operator repeatedly had to ask "what's on the milestone list today?" because no single file owned actionable-now state and enforced freshness. The queue is stale (cyber-insurance only, no #1-target swarm). The signed Next-Action Decision Rubric (D13) currently preserves the queue's canonical-ordering claim. Option B changes signed-spec substance and the authority chain future sessions inherit. Scoring is a core backbone of the build — without a persistent, dependency-aware candidate source feeding the rubric, the project goes blind.

**Hard current boundaries:**
- The rubric ranks; Matt selects (D2). Neither option gives the map or score a decision authority.
- Option B requires a fresh §11 re-sign on the rubric spec-revision (D13 change).
- Gate automation for scoreboard freshness is NOT claimed in v1 — doctrine-enforced Steps 0.5 / 6.5 only until a separate gate-code slice exists.

---

## Options

- **Option A — Reconcile but keep queue authority.** Refresh queue content; scoreboard remains status-only; D13 hybrid stays (queue default, conversational when stale). Hand-sync queue and scoreboard ongoing.
- **Option B — Retire queue ordering + revise rubric D13.** Queue becomes read-only historical record with RETIRED header. Scoreboard becomes canonical candidate generator (Build Sequencer). Rubric D13 revised: scoreboard generates, rubric ranks, Matt selects. Handshake remains one-screen daily view derived from scoreboard + rubric output.
- **Option C — New fifth artifact.** Create a standalone Build Sequencer file separate from scoreboard and queue. Highest fragmentation risk; rejected in design review unless A and B both fail.

---

## Short-Term Consequences (0-30 days)

| Option | Opens | Closes | Build Surface Added | Reduces Risk | Creates Risk | Pipeline Signal |
|---|---|---|---|---|---|---|
| A | Fastest doc-only reconcile; no rubric re-sign. | Leaves two ordering surfaces alive; hand-sync burden persists. | Queue refresh edits only. | Low immediate change risk. | "What's next" trap likely recurs; FC debt on every session. | Shows discipline without fixing authority chain. |
| B | Single source of truth for actionable-now; scoring backbone wired to live swarm state. | Queue ordering authority; D13 hybrid-with-queue. | Scoreboard columns + header; generator contract; AGENTS Steps 0.5/6.5; rubric D13 revision; queue RETIRED header. | Eliminates fragmentation seam; makes breadth/depth gates visible. | Rubric re-sign + multi-file governance slice; adoption backfill work. | Proves the project can READ next instead of ASK next. |
| C | Cleanest standalone spec possible. | Nothing — adds a fifth surface. | New artifact + cross-links to scoreboard/queue/handshake. | None vs B. | Highest fragmentation and drift risk (FM vi queue/rubric collision). | Negative signal — more files, same problem. |

---

## Long-Term Consequences (3-12 months)

| Option | Architecture Lock-In | Trust / Credibility Impact | Legal / Insurance Exposure | Maintenance Burden | Evidence / Data Value | Doctrine Drift Risk | Claim / Forbidden-Language Risk | Operator-Time Burden | Long-Term Reversibility |
|---|---|---|---|---|---|---|---|---|---|
| A | Locks dual-authority hand-sync pattern. | Operator loses trust in trackers; "what's next" keeps returning. | None direct. | High — two surfaces to keep true. | Low — stale maps produce false confidence. | High — fragmentation is the drift vector. | None. | High — re-derivation every session. | Reversible but problem persists. |
| B | Locks scoreboard-as-generator + rubric-as-ranker + Matt-as-selector. | Strong — operator opens one file, reads ranked candidates with gate context. | None direct. | Medium upfront (backfill + loop discipline); lower recurring. | High — every cycle logs scored candidates against live swarm state. | Medium — Step 0.5/6.5 skipped = stale map; mitigated by doctrine. | None. | Low after adoption — read, don't ask. | Reversible via spec revision; sunk cost in scoreboard schema. |
| C | Locks toward artifact sprawl. | Confusing — which file is canonical? | None. | Highest — three+ surfaces. | Medium but duplicated. | Highest. | None. | High. | Reversible by consolidation later. |

---

## Decision Notes

- **Biggest upside:** Option B ends the structural cause of the "what's next" trap and wires scoring to the #1 target (70-agent swarm) instead of a stale cyber-insurance queue.
- **Biggest downside:** Requires rubric re-sign and a multi-file governance adoption slice before mechanical backfill.
- **Hidden dependency:** Signed rubric D13 explicitly forbids overriding queue authority today — Option B is not a scoreboard-only edit.
- **Assumption that must be true:** Execution lane will run Steps 0.5 and 6.5 on every swarm-map slice without waiting for gate automation.
- **Optionality killed:** Option A keeps the dual-surface seam. Option C kills anti-fragmentation.
- **What this implicitly authorizes:** Adoption of the Build Sequencer generator contract and queue retirement as ordering authority — NOT individual agent builds (Rule 4 stands).
- **Reverse trigger:** Scoreboard goes stale again (no Step 6.5 updates); queue un-retired without spec revision; rubric score treated as build permission.
- **Evidence needed before committing:** clean gate on governance slice; operator §11 re-sign on rubric D13 revision; decision_cycles_log entry.

---

## Ranked Decision Aid (Next-Action Rubric — advisory only)

Pre-scored on the unmodified rubric axes (Leverage / Risk / Evidence / FutureCost / Reversibility):

| Option | L | R | E | FC | Rv | TOTAL |
|---|---|---|---|---|---|---|
| B — Retire queue authority + revise D13 | 2 | 2 | 2 | 2 | 1 | **9** |
| A — Reconcile, keep queue authority | 1 | 1 | 2 | 0 | 2 | **6** |
| C — New fifth artifact | 1 | 0 | 1 | 0 | 1 | **3** |

Matt selected **Option B** (2026-06-08): scoring is a core backbone; going blind without a proper map is unacceptable.

---

## Outcome

**Operator decision:** Option B — retire queue ordering authority; revise rubric D13; extend scoreboard as Build Sequencer; amend AGENTS.md Build Loop with Steps 0.5 and 6.5.  
**Reason:** Single source of truth for actionable-now candidates feeding the signed rubric; eliminates the fragmentation seam that caused the "what's next" trap. Best-in-class fit toward the #1 target (full 70-agent governed swarm).  
**Review trigger or date:** First build cycle after adoption — verify Step 0.5/6.5 ran and handshake list was derived from scoreboard, not re-asked.
