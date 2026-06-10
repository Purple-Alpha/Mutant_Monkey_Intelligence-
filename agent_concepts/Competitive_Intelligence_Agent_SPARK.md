# Competitive Intelligence Agent — SPARK Concept Capture
**Status:** CONCEPT ONLY — NOT §11 signed. Advisory lane. No build authorization. No scoreboard row yet.
**Last updated:** June 9, 2026
**Source:** Matt Nichol verbal direction

---

## What Matt Asked For

> "I need an agent to study everything about these companies and find where they all excel and where they drop the ball. I want an agent that will study all this and become that brain to feedback all this info to us."

---

## What This Agent Is

A **Competitive Intelligence Agent** — a dedicated Layer 6 Learning/Governance agent that continuously ingests, structures, and surfaces knowledge about competing email security vendors.

This is NOT a detection agent. It does not analyze emails.
It analyzes **the market** — specifically what competitors do well, what they miss, and where the gaps are that we fill.

It becomes the swarm's standing memory on the competitive landscape.

---

## Why Layer 6 (Learning/Governance)

This agent does not detect fraud. It does not verify senders. It does not produce evidence chains.

It **learns** — ingests external information and distills it into structured knowledge that feeds:
- Product positioning decisions
- Build prioritization (what gaps are worth filling)
- MSP sales conversations
- Product Bible updates

Layer 6 is the right home. It is the swarm's brain for "what do we know about the world outside" rather than "what do we know about this email."

---

## Competitors to Study (initial list)

| Vendor | Known strength | Known gap (hypothesis) |
|---|---|---|
| Barracuda | Price, brand recognition, SMB penetration | Siloed detection, black box verdicts, no evidence chain |
| Microsoft Defender | Ubiquity, M365 integration | No explainability, no override path, single-model verdict |
| Proofpoint | Enterprise scale, threat intel feeds | Expensive, complex, overkill for SMB/MSP |
| Mimecast | Archiving + security bundle | Legacy architecture, UI complexity |
| Abnormal Security | AI-native BEC detection | Price point, enterprise-only |
| Avanan (Check Point) | Cloud-native, API-based | Less known in Canadian MSP market |

This list grows as the agent learns. It is not locked at build time.

---

## What the Agent Studies Per Vendor

For each competitor, the agent builds and maintains a structured profile:

1. **What they detect well** — known strengths, published detection rates, case studies
2. **What they miss** — documented false positives, known failure modes, gap analysis
3. **How they explain decisions** — do they surface evidence or just return a verdict?
4. **Pricing model** — per seat, per tenant, volume tiers
5. **MSP channel approach** — how they sell to MSPs, what margin looks like
6. **Customer complaints** — G2, Reddit, MSP forums, public incident reports
7. **Architecture model** — single model, ensemble, rule-based, AI-native
8. **Token/cost transparency** — do they expose per-tenant AI cost attribution?
9. **False positive recovery** — what happens when they're wrong? Is there an appeal path?
10. **Canada-specific posture** — insurance requirements, geo assumptions, data residency

---

## What It Feeds Back to Us

The agent does not just store information. It produces **structured gap reports**:

- **Gap report:** here is what Barracuda does not do that we do
- **Wedge report:** here are the three scenarios where every competitor fails that we can demo
- **Objection brief:** here is how to answer "why not just buy Barracuda"
- **Build signal:** here are gaps in the market that no competitor fills yet — candidate for a new agent

---

## The Token Tracking Angle (unique to us)

No competitor currently exposes:
- Which AI model ran for which detection
- How many tokens were consumed per tenant per time window
- Per-client cost attribution for MSP billing

This agent should track whether any competitor begins offering this. If none do, it confirms our differentiation. If one does, it flags it immediately.

---

## How It Operates (Phase 1 — manual)

Phase 1 is a **manual knowledge base** — not autonomous web scraping. Matt or the advisory lane feeds it structured inputs:
- Todd Chapman debrief notes
- G2/Capterra review exports
- Vendor documentation and pricing pages
- MSP forum threads
- Incident reports (e.g. the Defender outage story)

The agent structures, stores, and surfaces this in a readable format for product and sales decisions.

Phase 2 (future, separate authorization) could involve automated ingestion — RSS feeds, vendor changelog monitoring, forum monitoring. That requires its own signed spec and is explicitly out of scope here.

---

## Governance Notes

- **Layer:** 6 Learning/Governance
- **Authority level:** read-only knowledge synthesis. No detection. No scoring. No verdict.
- **Autonomy:** none. Phase 1 is human-fed, human-queried.
- **Evidence emitted:** structured competitive profiles + gap reports. Not an `AgentContribution` in the fraud-detection chain.
- **Scoreboard:** needs a new row (71?) or a separate competitive intelligence register. Matt decides.
- **Build gate:** needs its own Agent Design Contract before any runtime work. This is concept capture only.

---

## Proposed Name

**Competitive Intelligence Agent** (`CompetitiveIntelligenceAgent`)
Internal codename: **Market Brain**

---

## Next Actions (requires Matt direction)

1. Does this get a scoreboard row? If yes, what number — 71, or a separate register?
2. Does Phase 1 start as a flat markdown knowledge base (no code) or does it get a lightweight runtime store?
3. Who feeds it — Matt only, or does Todd Chapman's feedback flow directly in?
4. Should gap reports feed the Product Bible update cycle on a schedule?
