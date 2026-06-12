# ReconciliationAgent — Concept Doc

**Status:** CONCEPT — advisory lane only. No build authorization. Contract required before build.
**Date:** June 11 2026
**Document type:** Concept doc (advisory lane output, pre-contract, pre-§11)
**Authority:** Matt Nichol — sole signing authority. This doc grants nothing; it records a design decision for a future contract session.

---

## Purpose

The ReconciliationAgent is the only agent in the swarm that produces a verdict. Every Layer 1 detection agent (#78-83) deliberately produces structured evidence contributions and **no** verdict; the ReconciliationAgent consumes those contributions and issues the single verdict per email. This doc captures Matt's design decision from the June 11 2026 session: a **three-agent ensemble verdict model** — three independent voters, best 2-out-of-3.

---

## The three-voter ensemble

Three voters cast independently. Best 2-out-of-3 carries the verdict.

### R1 — Signal Weight Voter
Quantitative confidence scoring across all Layer 1 agent contributions. Numbers only. Aggregates the `confidence` values and signal strengths from every detection contribution into a weighted quantitative score. No pattern reasoning, no narrative — pure numerical weighting.

### R2 — Pattern Match Voter
Compares the evidence chain against Layer 0 knowledge patterns. The question it answers: **does this combination of signals match a known threat profile?** Reasons over the *shape* of the combined evidence against the threat-intel briefings (phishing, BEC, ransomware, trojan-delivery, geo, AI-gen content), not the raw numbers.

### R3 — Conflict Resolution Voter
Specifically targets where Layer 1 agents disagreed and weighs the conflict **as information**. Disagreement between detectors is itself a signal, not noise to be averaged away. The Ukraine IP vs. 40 prior emails scenario lives here: a foreign/high-risk geo origin that contradicts a long, established sender history is exactly the kind of conflict R3 exists to adjudicate.

---

## Vote outcomes

| Outcome | Result |
|---|---|
| All three agree | Unanimous — highest confidence verdict |
| 2-out-of-3 agree | Verdict issued; minority opinion logged |
| All three disagree | ESCALATE — no verdict; operator review required |

---

## Verdict enum (closed)

- `HIGH_RISK`
- `MEDIUM_RISK`
- `LOW_RISK`
- `DELIVERY_PROBLEM`
- `ESCALATE`

---

## Key rules

- **Independent voting.** Voters run independently and cannot see each other's votes before casting. No voter is influenced by another's output.
- **Minority always logged.** Whenever a verdict is issued on a 2-out-of-3 split, the minority opinion is always logged — never discarded.
- **Plain-English evidence chain.** The evidence chain output must be readable by a non-technical MSP operator. Plain English, not raw signal dumps.

---

## Special paths

- **`spam_signal_only` (from ImageClassifier #83)** routes to `DELIVERY_PROBLEM`, **not** `HIGH_RISK`. A delivery/spam surface signal with no fraud indicators is a delivery problem, not a fraud verdict.
- **`zero_day_candidate` (from AttachmentSandbox #82)** passes to the mutation engine separately and **does not change the verdict**. It feeds the mutation pipeline only; it is not a verdict input.

---

## Open questions for the contract session

1. Does each voter (R1, R2, R3) get its own scoreboard row?
2. What is the escalation path when all three disagree?
3. Does the Lung dial affect verdict thresholds under Deep breath?
4. Does the attacker sophistication rubric score feed into R1 weighting?

---

## Dependencies

- Phase 3 must be **fully GATED** before the Phase 4 contract is drafted.

---

## Status

**CONCEPT — advisory lane only. No build authorization. Contract required before build.**
**Date:** June 11 2026
