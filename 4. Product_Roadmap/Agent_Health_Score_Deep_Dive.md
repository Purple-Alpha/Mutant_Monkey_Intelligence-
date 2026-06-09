# Agent Health Score — §11 Spec (Phase 1: Manual)

**Status:** DRAFT — UNSIGNED. Awaiting Matt §11 signature. Nothing is written to the scoreboard until this is signed.
**Authored:** 2026-06-08 (Mutant Monkey). Origin: operator request for a visible, permanent per-agent confidence score on top of the Evidence Stage ladder.
**Scope of this signature:** Phase 1 only — add a manual `SCORE` column to the Build Sequencer scoreboard, update it by hand at Build Loop Step 6.5, and log every change in `decision_cycles_log.md`. **No automation, no gate condition, no promotion/demotion authority** in this phase.

---

## 1. Why this exists

The **Evidence Stage** (1 Synthetic → 2 Supervised → 3 Production) tells you *what level* an agent has reached. It does not tell you, at a glance, *how trustworthy an agent is right now* — whether it has drifted, gone stale, or been demoted and only partially recovered.

The **Agent Health Score** is a single `0–100` number per governed agent, shown on the scoreboard, that moves as agents perform, drift, or age. Stage is the label; Score is the live pulse. Think credit score per agent: it rises when an agent earns it and falls when it fails, and the fall is on the permanent record.

This is a **governance instrument, not a build instrument.** Per scoreboard Rule 4 it is authority-free: a score never means "approved," never authorizes a build, and never by itself promotes or demotes an agent.

---

## 2. The formula (7-component blend — LOCKED for Phase 1)

A weighted sum of seven `0–100` sub-scores. Weights total 100.

| # | Component | Weight | What it measures |
|---|-----------|--------|------------------|
| 1 | Evidence Stage maturity | 20 | ladder position: ES1 = 33, ES2 = 66, ES3 = 100 |
| 2 | Governance completeness | 20 | §11-signed, gate-clean, full per-agent contract with D1–D10 locked |
| 3 | Test pass rate | 15 | passing tests / total tests for this agent |
| 4 | Scope discipline | 15 | zero boundary violations = 100; **permanent record** |
| 5 | Demotion history | 15 | starts 100; drops per demotion; partial recovery on re-promotion; **permanent record** |
| 6 | Integration health | 10 | full chain wired (Agent → Contribution → blackboard → DER → L5), no blocked deps |
| 7 | Validation age | 5 | how recently the last clean gate ran |

`SCORE = 0.20·Stage + 0.20·Gov + 0.15·TestPass + 0.15·Scope + 0.15·Demotion + 0.10·Integration + 0.05·Age`

**Weight rationale (operator-confirmed):** governance and stage are weighted heaviest because a well-built agent that drifts is more dangerous than a mediocre one that stays in scope. Scope discipline and demotion history are permanent — no agent can fully erase a failure by adding tests. Validation age is intentionally light (5%) in Phase 1; staleness weight is a Phase 2 dial-in question, not a Phase 1 guess.

### 2.1 Sub-score scales (Phase 1 manual rules)

- **Evidence Stage:** ES1 = 33, ES2 = 66, ES3 = 100.
- **Governance completeness:** full per-agent §11 contract (D1–D10) + gate-clean = 100; metadata-only retrofit (signed wrapper, no dedicated per-agent contract) = 70; ungoverned = 0.
- **Test pass rate:** (passing / total) × 100 for the agent's focused suite. All-green = 100.
- **Scope discipline:** 100 with zero recorded boundary violations; −20 per recorded violation (floor 0). Permanent — violations are never removed.
- **Demotion history:** start 100; −25 per demotion event; +10 on a clean re-promotion (net −15 retained per demotion cycle, floor 0). Permanent record.
- **Integration health:** full chain to DER (and L5 aggregate challenge for Detection-layer agents), no blocked deps = 100; shallower-but-wired or first-of-layer = 90–95; blocked dependency = ≤50.
- **Validation age:** last clean gate within 7 days = 100; −10 per additional 7-day bucket (floor 40).

---

## 3. Seed scores — the 13 current governed agents (Phase 1, 2026-06-08)

Computed from current repo state. ES1 caps everyone below ~87 by design — you cannot reach 100 until production (ES3). Sub-scores shown for transparency.

| # | Agent | Layer | Stage(20) | Gov(20) | Test(15) | Scope(15) | Demo(15) | Integ(10) | Age(5) | **SCORE** |
|---|-------|-------|-----------|---------|----------|-----------|----------|-----------|--------|-----------|
| 6 | Header Analysis | 2 | 33 | 100 | 100 | 100 | 100 | 100 | 100 | **87** |
| 6A | Email Authentication | 2 | 33 | 100 | 100 | 100 | 100 | 100 | 100 | **87** |
| 8 | Ghost Thread | 2 | 33 | 100 | 100 | 100 | 100 | 100 | 100 | **87** |
| 10 | Lookalike Domain | 2 | 33 | 70 | 100 | 100 | 100 | 90 | 100 | **80** |
| 11 | Known-Good Contact | 3 | 33 | 100 | 100 | 100 | 100 | 100 | 100 | **87** |
| 14 | Payment Change Detection | 2 | 33 | 100 | 100 | 100 | 100 | 100 | 100 | **87** |
| 23 | Credential Phishing | 2 | 33 | 100 | 100 | 100 | 100 | 100 | 100 | **87** |
| 24 | MFA Manipulation | 2 | 33 | 100 | 100 | 100 | 100 | 100 | 100 | **87** |
| 27 | Link Inspection | 2 | 33 | 100 | 100 | 100 | 100 | 100 | 100 | **87** |
| 30 | Attachment Risk | 2 | 33 | 100 | 100 | 100 | 100 | 100 | 100 | **87** |
| 31 | PDF Fingerprint | 2 | 33 | 100 | 100 | 100 | 100 | 100 | 100 | **87** |
| 39 | Language Pressure | 2 | 33 | 100 | 100 | 100 | 100 | 100 | 100 | **87** |
| 46 | Evidence Package | 4 | 33 | 100 | 100 | 100 | 100 | 95 | 100 | **86** |

**What the seed pass already tells you:**
- The cohort is uniform (11 of 13 at 87) — exactly what you'd expect from a freshly-built, uniformly-governed ES1 batch. The score earns its keep as agents *diverge* over time, not on day one.
- **#10 Lookalike Domain = 80** is the standout. It is a metadata-only retrofit (signed wrapper, no dedicated per-agent D1–D10 contract). The score is correctly flagging it as the weakest-governed agent — a real, actionable item: give it a full per-agent contract to bring it to parity.
- **#46 Evidence Package = 86** sits one point low because it is the first Layer-4 agent, tested to the blackboard rather than the full DER/L5 challenge chain. Expected for first-of-layer; revisit as the Evidence path matures.

---

## 4. Where the score lives + how it's updated (Phase 1)

- **Scoreboard column:** add `SCORE` to each agent row in `Blue_Team_Swarm_70_Agent_Scoreboard.md`, alongside `LAST_RUBRIC_SCORE` (different thing — rubric score is a per-cycle selection input; Health Score is a standing per-agent grade).
- **Update cadence:** the execution lane recomputes the affected agent's SCORE by hand as part of **Build Loop Step 6.5** (AGENTS.md §3.2), the same step that already updates row status after a gated change.
- **Permanent record:** every SCORE change gets a timestamped line in `decision_cycles_log.md` — the same ledger that already records promotions and demotions — stating the old value, new value, and which component moved and why. Nothing is overwritten silently.

---

## 5. Boundaries (what this is NOT, Phase 1)

- **Not automated.** No script computes this in Phase 1. Manual only, so the formula can be stress-tested against reality before it is frozen.
- **Not a gate condition.** A low or dropping score does not block a commit in Phase 1. (That is a Phase 3 decision.)
- **Not build permission.** Rule 4 applies fully — a SCORE is status, never authorization.
- **Not promotion/demotion authority.** The score reflects promotions/demotions; it does not cause them. Stage changes still go through the signed promotion bar / demotion triggers.
- **Not a real-data claim.** Scores are computed from build/governance state only; they assert nothing about real-world detection performance until Stage 2 data exists.

---

## 6. Phase roadmap

- **Phase 1 — Manual (this spec).** SCORE column + manual Step 6.5 updates + permanent log. Watch it across ~10 cycles; tweak weights/scales when something doesn't reflect reality.
- **Phase 2 — Dial in (after ~10 cycles).** Review scores against what actually happened: did high scores predict good behavior, did low scores predict problems? Adjust weights (esp. validation-age weight) on real evidence. Re-sign the formula.
- **Phase 3 — Automate (when proven).** Write the scoring script once the formula is locked; add it to `complete_gate.py` as an automated check; a dropping score can then trigger a review. Requires its own §11 signature.

---

## 7. Scoreboard amendment (applied on signature)

On signature, add to the Build Sequencer locked-decisions table:

> **BS-D7 — Agent Health Score (Phase 1 manual).** A `0–100` `SCORE` column is added to every governed-agent row, computed from the 7-component blend in `Agent_Health_Score_Deep_Dive.md` §2. Updated by the execution lane at Build Loop Step 6.5; every change logged in `decision_cycles_log.md`. Authority-free (Rule 4) — never build permission, never promotion/demotion authority. Automation deferred to Phase 3 under separate signature.

---

## §11 — Lockdown signature

UNSIGNED — awaiting operator. Signing authorizes Phase 1 only: the `SCORE` column, the manual Step 6.5 update procedure, the permanent-log rule, BS-D7, and seeding the 13 scores in §3 above. No automation, no gate condition, no promotion/demotion authority. Weights and scales are frozen for Phase 1 and revisited at Phase 2.

> _Operator signature pending: _____________________________
