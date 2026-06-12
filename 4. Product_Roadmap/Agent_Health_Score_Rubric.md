# Agent Health Score — Scoring Rubric
**Status:** §11 SIGNED — Matt Nichol June 10th 2026. Active scoring authority.
**Date:** June 10, 2026
**Authority:** Matt Nichol — sole signing authority

---

## The Formula (already signed)

| Component | Weight |
|---|---|
| Evidence Stage maturity | 30% |
| Proof depth | 20% |
| Governance completeness | 20% |
| Boundary safety | 15% |
| Integration health | 15% |

---

## HOW TO SCORE — 0 to 100 per agent

### Component 1 — Evidence Stage Maturity (30 points max)

| Score | What it means |
|---|---|
| 25-30 | ES3 — agent has passed adversarial tests with real-data signals |
| 15-24 | ES2 — agent has passed adversarial tests with synthetic data |
| 5-14 | ES1 — agent has expected-pass tests only |
| 0-4 | No tests or tests failing |

**BENEFIT:** Score 25+ unlocks promotion eligibility
**HARM:** Score below 5 triggers demotion review

---

### Component 2 — Proof Depth (20 points max)

| Score | What it means |
|---|---|
| 17-20 | Evidence chain includes 3+ independent signal types reconciled |
| 11-16 | Evidence chain includes 2 signal types |
| 5-10 | Single signal only — no reconciliation |
| 0-4 | No evidence chain — verdict only |

**BENEFIT:** Score 17+ qualifies agent for ReconciliationAgent input
**HARM:** Score below 5 means agent cannot contribute to a verdict — advisory only

---

### Component 3 — Governance Completeness (20 points max)

| Score | What it means |
|---|---|
| 17-20 | §11 signed contract + scoreboard row + all 3 test classes + gate clean |
| 11-16 | §11 signed + scoreboard row + tests passing but missing one test class |
| 5-10 | Scoreboard row exists but contract unsigned or tests incomplete |
| 0-4 | No scoreboard row, no contract, no gate |

**BENEFIT:** Score 17+ agent is GOVERNED — can be cited in MSP audit trail
**HARM:** Score below 10 agent cannot be in production registry

---

### Component 4 — Boundary Safety (15 points max)

| Score | What it means |
|---|---|
| 13-15 | Agent has never fired outside its defined evidence type. Zero boundary violations in test history. |
| 8-12 | One boundary warning in test history — resolved and documented |
| 3-7 | Multiple boundary warnings — pattern of drift detected |
| 0-2 | Active boundary violation — agent producing output outside its contract |

**BENEFIT:** Score 13+ agent qualifies for Phase 2+ deployment
**HARM:** Score below 3 triggers immediate demotion — agent pulled from registry pending contract review

---

### Component 5 — Integration Health (15 points max)

| Score | What it means |
|---|---|
| 13-15 | Agent writes cleanly to core/blackboard/ on every run. Schema validation 100% pass rate. Tenant isolation confirmed. |
| 8-12 | Occasional schema warning — non-blocking, documented |
| 3-7 | Schema failures occurring — intermittent broken writes |
| 0-2 | Agent cannot write to ledger reliably |

**BENEFIT:** Score 13+ agent is production-ready
**HARM:** Score below 3 agent is blocked from production — ledger integrity at risk

---

## COMPOSITE SCORE BANDS

| Band | Score | What happens |
|---|---|---|
| ELITE | 85-100 | Agent is fully governed, battle-tested, production-ready. Eligible for ReconciliationAgent input. |
| HEALTHY | 70-84 | Agent is production-ready. Minor gaps documented. Improvement path clear. |
| MARGINAL | 50-69 | Agent needs work before next phase. Cannot be cited in audit trail until gaps closed. |
| AT RISK | 25-49 | Agent is in demotion review. Cannot contribute to verdicts. Operator notified. |
| DEMOTED | 0-24 | Agent pulled from registry. Contract review required before reinstatement. Matt signs reinstatement. |

---

## CURRENT SCORES — GOVERNED AGENTS

| Agent | E.Stage | Proof | Governance | Boundary | Integration | TOTAL | Band |
|---|---|---|---|---|---|---|---|
| HeaderDivergenceAgent | 27 | 18 | 19 | 14 | 14 | 92 | ELITE |
| EmailAuthenticationAgent | 27 | 18 | 19 | 14 | 14 | 92 | ELITE |
| GhostThreadAgent | 27 | 18 | 19 | 14 | 14 | 92 | ELITE |
| Verification Outcome Agent | 25 | 17 | 18 | 13 | 13 | 86 | ELITE |
| PhishIntelAgent (#72) | 14 | 12 | 19 | 14 | 13 | 72 | HEALTHY |
| RansomwareIntelAgent (#73) | 14 | 12 | 19 | 14 | 13 | 72 | HEALTHY |
| BECIntelAgent (#74) | 14 | 12 | 19 | 14 | 13 | 72 | HEALTHY |
| TrojanDeliveryIntelAgent (#75) | 14 | 12 | 19 | 14 | 13 | 72 | HEALTHY |
| GeoIntelAgent (#76) | 14 | 12 | 19 | 14 | 13 | 72 | HEALTHY |
| AIGenContentIntelAgent (#77) | 14 | 12 | 19 | 14 | 13 | 72 | HEALTHY |
| SenderHistoryAgent (#78) | 22 | 14 | 20 | 15 | 15 | 86 | ELITE |
| GeoVelocityAgent (#79) | 22 | 14 | 20 | 15 | 15 | 86 | ELITE |
| ContentAnalyzer (#80) | 22 | 14 | 20 | 15 | 15 | 86 | ELITE |
| URLReceptor (#81) | 22 | 14 | 20 | 15 | 15 | 86 | ELITE |
| AttachmentSandbox (#82) | 22 | 14 | 20 | 15 | 15 | 86 | ELITE |
| ImageClassifier (#83) | 22 | 14 | 20 | 15 | 15 | 86 | ELITE |

*The first four (detection/verification) rows remain estimates pending exact recompute. The six Layer 0 knowledge agents (#72-77) are **computed Phase 2 scores** (2026-06-10; build gate-clean, full suite 1497 passing, 3 test classes each). They are structurally identical, so they score identically. All six clear the 70+ phase-closure gate (contract §10). The six Layer 1 detection agents (#78-83) are **computed Phase 3 scores** (2026-06-11; build gate-clean, full suite 1553 passing, 3 test classes each + Amendment 1 assertions). Structurally identical; all six score 86 ELITE (clears the 85+ phase-closure gate per contract §10).*

**Layer 0 scoring interpretation (flagged for operator — possible rubric amendment):** this rubric is written for detection agents; two components needed interpretation for *brief-only* Layer 0 knowledge agents:
1. **Evidence Stage (14):** capped at ES1 per the signed Phase 2 contract P2-D3 ("all six start at ES1"), even though they pass adversarial synthetic tests — which this rubric's Component 1 would otherwise read as ES2 (15-24). The signed contract wins.
2. **Integration Health (13):** Component 5's top band rewards writing to `core/blackboard/`, which Layer 0 agents are contractually forbidden to do (P2-D7). Scored instead on 100% schema-validation integrity + honored read-only boundary — not penalized for a write they must never perform.
3. **Proof Depth (12):** each briefs 4 independent intel signal types but performs no reconciliation (that is Phase 4), so scored mid-band rather than the reconciliation-gated top band.

A future signature could add an explicit Layer 0 scoring track so these don't require interpretation.

**Layer 1 scoring interpretation (Phase 3 detection agents #78-83):**
1. **Evidence Stage (22):** ES2 — adversarial synthetic tests pass including Amendment 1 assertions (sender_domain normalization, token attribution, tenant isolation).
2. **Proof Depth (14):** each agent consumes a mandatory Layer 0 briefing (knowledge input) and writes one detection signal — a 2-type evidence chain per P3-D3, scored mid-band (11-16) rather than the reconciliation-gated top band (17-20, Phase 4).
3. **Integration Health (15):** 100% schema-validation pass on `CanonicalEvidenceLedger` writes; tenant isolation confirmed on every write (P3-D5); Amendment §C token attribution verified for ContentAnalyzer and AttachmentSandbox.

---

## WHAT THIS DOES TO THE BUILD MAP

- Any agent scoring below 50 cannot advance to the next phase
- Any agent scoring below 25 blocks the phase it belongs to from closing
- Phase closure requires every agent in the phase scoring 70+
- Matt sees the scoreboard before signing any phase closure

---

## §11 — Operator Sign-Off

**Signed:** Matt Nichol
**Date:** June 10th 2026
