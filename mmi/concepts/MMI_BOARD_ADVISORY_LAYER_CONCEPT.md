# MMI Board Advisory Layer — Concept Lock

> **NON-AUTHORITATIVE CONCEPT — NOT AUTHORITY.**
> This document records a concept doctrine for future requirements research. It does **not**
> authorize implementation, automation, runtime wiring, dispatcher changes, scoreboard changes,
> or transfer of project authority. Matt Nichol remains final authority.

**Classification:** `CONCEPT_IDEA` · `NEEDS_MMI_REVIEW` · `PARKED_DRAFT`  
**Lock date:** 2026-06-16  
**Authorized scope:** `MMI_BOARD_ADVISORY_LAYER_CONCEPT_LOCK` — documentation / concept lock only  
**Status:** Parked until Matt authorizes requirements research

---

## 1. Concept thesis

Mutant Monkey Intelligence (MMI) should evolve an **autonomous board advisory layer** —
a project-management and decision-support surface that helps Matt choose what to build,
what to park, what to reject, and what to route — without becoming a yes-agent, a
gatekeeper, or a replacement for operator authority.

The board layer evaluates what is best for **Mutant Monkey Security** as a product and
business, ranks opportunities by value and cost, detects and explains drift, proposes
safer alternatives, keeps parked ideas clean, and routes **approved** work to the correct
lane — while protecting Matt's time, money, credits, and focus.

This is **advisory doctrine only**. Stage 1 MMI today remains file-based governance plus
`scripts/mmi_dispatch.py` scoreboard-derived routing. This concept describes a **future**
layer above that foundation.

---

## 2. What MMI Board is

MMI Board is an **autonomous advisory and project-management layer** that:

| Capability | Description |
|---|---|
| Opportunity evaluation | Surfaces what is best for the product and company given current repo state |
| Ranked next directions | Orders candidates by product value, revenue value, risk, timing, and build cost |
| Drift detection | Flags when work, docs, or claims diverge from signed authority |
| Drift education | Explains *why* something is drift — not just that it is drift |
| Safer alternatives | Proposes lower-risk or higher-leverage paths when drift or overload is detected |
| Parked-idea hygiene | Keeps parked concepts labeled, deduplicated, and out of authority surfaces |
| Approved-work routing | Routes work Matt has authorized to the correct model/tool lane |
| Operator protection | Reduces wasted time, spend, credits, and focus fragmentation |

MMI Board **improves** Matt's decisions. It does not **make** them.

---

## 3. What MMI Board is not

| MMI Board is NOT | Why |
|---|---|
| A yes-agent | Must challenge weak ideas, drift, and overclaim — not rubber-stamp |
| A gatekeeper that blocks without explanation | Must educate and propose alternatives, not opaque STOP |
| A replacement for Matt | Signatures, phase authorization, and hardening claims remain Matt-only |
| An autonomous builder | Does not modify code, scoreboard, or signed specs by itself |
| Runtime authority (today) | No always-on process, hooks, or silent state changes in this concept lock |
| A revenue promise | Revenue lanes are hypotheses for research — not booked revenue |

**Core lines to preserve:**

```text
MMI is not a yes-agent.
MMI is not a gatekeeper.
MMI is not a replacement for Matt.
```

---

## 4. Board seats

Nine advisory seats — each evaluates proposals and candidates from its domain. Seats
**recommend and score**; they do not authorize.

| # | Seat | Primary question |
|---|---|---|
| 1 | **Product Board Seat** | Does this strengthen the wedge, roadmap coherence, and buyer value? |
| 2 | **Revenue Board Seat** | Which revenue lane does this open or protect? What is the path to paid proof? |
| 3 | **Technical Board Seat** | Is this buildable with current architecture? What is the real build cost? |
| 4 | **Security Board Seat** | Does this improve defensive posture without unsafe scope expansion? |
| 5 | **Operations Board Seat** | Can MSPs/operators run this without heroic manual effort? |
| 6 | **Finance / Cost Board Seat** | What does this cost in credits, infra, and Matt's time? |
| 7 | **Legal / Trust Board Seat** | What consent, liability, or trust boundaries apply? |
| 8 | **Strategy / Moat Seat** | Does this widen defensible differentiation vs commodity MDR? |
| 9 | **Drift Educator Seat** | What drift exists, why does it matter, and what is the safer alternative? |

Seats may disagree. The board layer's job is to **surface disagreement with evidence**,
not to collapse it into a single confident answer.

---

## 5. Future revenue lanes

Hypothesized revenue lanes to preserve for requirements research. **Not authorized products.**

| # | Lane | Notes |
|---|---|---|
| 1 | MSP pilot revenue | Wedge entry; operator-validated pilots |
| 2 | Vendor payment fraud review | Core authenticated-deception detection path |
| 3 | Evidence package / audit trail | Cyber-insurance and buyer-proof track |
| 4 | False-positive recovery | Operator-trust and cost-of-friction reduction |
| 5 | Tenant baseline intelligence | Gap 5 / memory consolidation commercial angle |
| 6 | Underwriter / cyber-insurance evidence support | Evidence-as-product, not claims automation |
| 7 | MSP dashboard / reporting | Operator-facing visibility and reporting |
| 8 | Premium adversarial hardening | Adversarial suite depth as differentiated offering |
| 9 | Local/private inference cost advantage | Cost moat via governed inference architecture |

Ranking across lanes is a **future board function** — not active in Stage 1 dispatcher.

---

## 6. Drift education behavior

When drift is detected, MMI Board must not only flag it. It must **educate**:

1. **What drifted** — file, claim, scoreboard row, handshake block, or intake item
2. **Against what authority** — signed spec, gate registry, `AGENTS.md`, scoreboard, git evidence
3. **Why it matters** — authority bleed, false build-ready signal, stale operator picture
4. **Safer alternative** — reconcile scoreboard, park the idea, run verify, or name explicit Matt decision
5. **Classification** — `CONTRADICTION`, `NEEDS_SCOREBOARD_ROW`, `PARKED_DRAFT`, etc.

The Drift Educator Seat owns this voice. It complements `scripts/detect_drift.py` and
`scripts/mmi_dispatch.py --verify` — it does not replace them.

---

## 7. Decision rubric

Future board ranking should score candidates (not authorize them) across dimensions Matt
already uses elsewhere in the project:

| Dimension | Question |
|---|---|
| Product value | Does this advance the governed swarm / inbox-shield wedge? |
| Revenue value | Which revenue lane(s) does it strengthen? |
| Risk | Authority, security, legal, reputational, or scope risk? |
| Timing | Is this the right phase given current ALL_CLEAR / queue state? |
| Build cost | Engineering depth, adversarial obligation, operator burden? |

Output format (future): ranked candidate list with **scores and tradeoffs in prose** —
never bare multiple-choice. Matt names the target; MMI assigns the lane (per operator
decisions 2026-06-16).

Candidates surfaced by any board function must carry labels such as:
`SCOREBOARD_READY`, `NEEDS_SCOREBOARD_ROW`, `NEEDS_MMI_REVIEW`, `PARKED_DRAFT`,
`NOT_AUTHORIZED`.

---

## 8. Authority limits

| Action | MMI Board may | Matt must |
|---|---|---|
| Rank opportunities | Recommend with evidence | Authorize phase / target |
| Detect / explain drift | Flag and educate | Decide reconcile or override |
| Route approved work | Assign lane by task shape | Name authorized target |
| Park ideas | Label and quarantine | Promote or delete |
| Sign specs / contracts | Never | Always |
| Grant hardened claims | Never | Always |
| Change scoreboard | Never | Always |
| Commit / push code | Never | Always |
| Authorize build/research/design | Never | Always |

**Routing is not authority.** Board recommendations are evidence for Matt — not permission.

Current authority surfaces remain: `mmi/MMI_GATE_REGISTRY.md`, `mmi/MMI_DECISION_LOG.md`,
`scripts/mmi_dispatch.py --verify`, and Matt's explicit phase authorization.

---

## 9. Future requirements questions

Parked for a future **requirements research** authorization — not answered by this lock:

1. What inputs does the board read (scoreboard only, intake folder, revenue models, git)?
2. How are seat scores combined into a single ranked list without hiding disagreement?
3. What is the minimum viable board (which seats first)?
4. How does board output relate to ALL_CLEAR `CANDIDATES` without duplicating authority?
5. How are revenue lanes validated (pilot data vs hypothesis)?
6. What credit/cost model governs autonomous board runs?
7. How does drift education avoid contradicting `AGENTS.md` and signed specs?
8. What human-readable artifact does the board produce per cycle?
9. What automation boundaries stay forbidden even if board logic exists?
10. When does board output escalate to Matt vs stay informational?

---

## 10. Non-authorization statement

This concept lock **does not authorize**:

- Implementation of board logic, seats, or scoring engines
- Runtime wiring, hooks, watchers, or always-on MMI processes
- Automation that changes `MMI_CURRENT_STATE.md`, scoreboard, or dispatcher without explicit command
- Dispatcher, routing rules, or authority matrix changes
- Build, research, or design of any revenue lane or board seat
- Promotion out of `PARKED_DRAFT` or `NEEDS_MMI_REVIEW`
- Transfer of signature, hardening, or phase authority from Matt

**Matt Nichol remains final authority.**

Next step when ready: Matt authorizes **requirements research** on this concept — not
implementation — and records that authorization separately in `mmi/MMI_INTAKE_RECORDS.md`.

---

## Authority footer

This file is a **concept lock** only. It preserves doctrine for future MMI evolution.
It is not a signed spec, not §11, and not routing authority.
