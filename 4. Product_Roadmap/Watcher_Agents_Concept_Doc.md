# Watcher Agents — Concept Doc

## Three neutral observer agents (W1 / W2 / W3)

**Document type:** Concept Doc (CONCEPT — advisory lane only)
**Status:** CONCEPT — **no build authorization. No contract yet. Contract required before any build.**
**Date:** June 11 2026
**Drafted by:** Cursor (execution lane), transcribing the operator-settled session design. Signature reserved for the operator.
**Authority:** Matt Nichol — sole signing authority
**Scoreboard:** rows **#85, #86, #87 reserved** (W1 / W2 / W3) — reserved labels only, not governed, not built.
**Relationship:** observes the existing swarm (Phase 1-4 GATED). Adds **no** verdict surface and changes **no** signed Phase 1/2/3/4 surface.

---

## §0 — Purpose

The Watcher Agents are **neutral observers**. They do not detect threats, do not vote, and do not produce a verdict — that line is owned by the ReconciliationAgent (#84, P4-D5). Watchers sit beside the swarm and report on the **health of the swarm's own behaviour**: timing, drift, and integrity. Their output is **advisory** — signal for the operator and the governance layer, never an automated action.

This is a concept doc only. It records the design so a future §11 contract session has a settled starting point. Nothing here authorizes code.

---

## §1 — The three watchers

### W1 — TimingWatcher (#85, reserved)
Observes **how long things take**. Per-agent and per-case latency: detection-swarm fan-out time, ReconciliationAgent ensemble resolution time, end-to-end case time. Flags timing anomalies — an agent that suddenly runs 10× slower, a case that stalls, a voter that hangs. Timing is a leading indicator of both attack (resource exhaustion) and decay (a degrading dependency). **Observes only — never throttles or kills.**

### W2 — DriftWatcher (#86, reserved)
Observes **how behaviour changes over time**. Verdict-mix drift (sudden swing in HIGH_RISK vs LOW_RISK rates), confidence drift (voters trending toward the extremes), evidence-type drift (one detector going quiet or loud). Drift is how you catch a model or knowledge base going stale, or an attacker successfully shifting the baseline. **Observes only — never re-weights or re-tunes** (re-weighting is a signed amendment per P4-D6 / §6).

### W3 — IntegrityWatcher (#87, reserved)
Observes **whether the rules still hold**. Append-only ledger integrity (no rewrites/deletes on the evidence or verdict ledgers), tenant-isolation integrity (no cross-tenant leakage), role-separation integrity (no builder-auditor collapse, no CIRT cross-tenant action), schema integrity (no out-of-enum verdict, no smuggled field). Integrity is the structural promise of the whole system; W3 watches the promise. **Observes and reports — enforcement stays where it already lives** (the ledgers, the controller, the schema).

---

## §2 — Shared design stance (concept)

- **Neutral.** Watchers have no stake in any verdict. They never see an email's content as a detector would; they observe the swarm's own telemetry and the ledgers' shape.
- **Read-only.** Watchers write only their own observation records; they never mutate detection contributions, verdicts, role state, or production surfaces.
- **Advisory output.** A watcher finding is a flag for the operator / governance layer — never an automated freeze, throttle, re-weight, or kill. (Freeze authority is the CIRT individual's, per P4-D2 / the CIRT amendment.)
- **Tenant-aware.** Observations are tenant-scoped where they touch tenant data, inheriting P1-D3 / P4-D8 isolation discipline.
- **Layer placement (proposed):** Layer 6 Learning/Governance — they audit the swarm's behaviour, so by the restrictive-tiebreaker rule they cannot sit inside the loop they observe.

---

## §3 — Explicitly out of scope (concept boundary)

- **No verdict.** Watchers never issue or alter a verdict (P4-D5 stays sole-source).
- **No enforcement.** No throttle, freeze, kill, re-weight, or auto-tune. Those are either CIRT authority or signed-amendment paths.
- **No new detection.** Watchers are not detectors; they do not inspect email content for threats.
- **No change to signed surfaces.** Phase 1/2/3/4 contracts are untouched.

---

## §4 — Open questions for the contract session

1. **Telemetry source.** Do watchers read a dedicated telemetry/observation surface, or derive from the existing ledgers + token tracker? (Affects whether a new append-only surface is needed.)
2. **Baseline & thresholds.** Drift/timing baselines need data — equal to the Phase 4 "calibration needs real tenant data" problem. Launch with conservative static thresholds, tune by signed amendment?
3. **Scoreboard rows.** One row per watcher (#85/#86/#87) confirmed here, or a single "Watcher ensemble" row like the ReconciliationAgent's #84? (Reserved as three for now.)
4. **Health-score track.** Watchers are observers, not detectors or verdict producers — likely need their own Agent Health Score Rubric track (as Layer 4 got one), scored on observation coverage / false-flag rate / boundary safety.
5. **Escalation path.** When a watcher flags an integrity breach, where does it route — operator, governance layer, or the tenant's CIRT individual?
6. **Dependency ordering.** Do watchers depend on Phase 5+ surfaces (e.g. Mutation Engine, The Lung) before they are worth building, or can they observe the Phase 1-4 swarm as-is?

---

## §5 — Status line

**CONCEPT — advisory lane only. No build authorization. Contract required before build.** Scoreboard rows #85-87 are reserved labels; they are not governed agents and carry no health score. Phase 5 (Mutation Engine) remains the next signed-contract gate; this concept does not change that ordering.
