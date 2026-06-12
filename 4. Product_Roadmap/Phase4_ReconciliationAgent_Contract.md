# Phase 4 — ReconciliationAgent Agent Design Contract
## Layer 4: The Verdict Agent (three-voter ensemble)

**Document type:** Agent Design Contract
**Status:** §11 SIGNED — Matt Nichol June 11th 2026. Build authorization granted per §11 scope.
**Date drafted:** June 11 2026
**Drafted by:** Cursor (execution lane), transcribing the operator-settled June 11 2026 session design per the agreed model (operator/advisory designs → execution lane writes to disk; signature reserved for the operator).
**Authority:** Matt Nichol — sole signing authority
**Depends on:** Phase 1 (`fe355da`) + Phase 2 (`43b5511`) + Phase 3 (`6deffd9`, phase-closed `ce386f7`). Concept basis: `ReconciliationAgent_Concept_Doc.md` (`4944b34`).

---

## §0 — Purpose

The ReconciliationAgent is the **only** agent in the swarm that produces a verdict. Every Layer 1 detection agent (#78-83) produces a structured evidence contribution and no verdict; the ReconciliationAgent consumes those contributions for a single `email_id` and issues exactly one verdict. It does so through a **three-voter ensemble** — R1, R2, R3 — voting independently, best 2-out-of-3. One signature covers the agent and its three internal voters. ELITE health score 85+ is the target.

---

## §1 — Scope

### In scope
1. ReconciliationAgent — consumes all Layer 1 contributions for one `email_id`, runs the three-voter ensemble, issues one verdict, emits a plain-English evidence chain.
2. R1 Signal Weight Voter, R2 Pattern Match Voter, R3 Conflict Resolution Voter — internal voters of the ReconciliationAgent.

### Explicitly out of scope
- Re-detection — the ReconciliationAgent does not re-inspect the raw email. It reasons only over Layer 1 contributions + Layer 0 knowledge.
- The Lung — separate contract. The Lung dial is an input here (see §10), not built here.
- Mutation Engine — separate contract. Zero-day candidates are referred to it (§8), not processed here.
- Collective Immune System — DEPTH GATE CLOSED.
- Any change to Phase 1/2/3 signed surfaces.

---

## §2 — Locked Design Decisions

| # | Decision | Locked value |
|---|---|---|
| P4-D1 | Three-tier data model, single aggregated UI | Evidence is surfaced in three tiers — raw Layer 1 contributions, per-voter reasoning, final verdict — through a **single aggregated UI view** for the operator. One screen, three depths. |
| P4-D2 | Named CIRT individual per tenant | The CIRT role is a **named individual per tenant**, not a generic/rotating role. The named person (e.g. Todd's client's tech person) is written into the contract at onboarding and holds **dial authority and freeze authority** for that tenant. Their name is on every decision they make in the audit trail. |
| P4-D3 | Deterministic lockdown | `MEDIUM_RISK` + Lung `Deep breath` state = **automatic `HIGH_RISK`**. Deterministic, not discretionary. |
| P4-D4 | R1 isolated from human input | R1 (Signal Weight Voter) is isolated from human input. The attacker-sophistication rubric feeds the **Lung only** — it does **not** feed R1 weighting. R1 is numbers from Layer 1 contributions only. |
| P4-D5 | Verdict is the only verdict surface | No Layer 1 agent issues a verdict; the ReconciliationAgent is the sole verdict producer. Closed verdict enum (§5). |
| P4-D6 | Independent voting | The three voters cast independently and cannot see one another's votes before casting. |
| P4-D7 | Health score target | ELITE — 85+ on the signed Agent Health Score Rubric. Gate does not close below 85. |
| P4-D8 | Tenant isolation | Reads filtered by `tenant_id`; verdict write carries `tenant_id`. No cross-tenant access (inherits P1/P3 discipline). |

---

## §3 — The three-voter ensemble

All three voters run **independently**. No voter sees another's vote before casting (P4-D6). Each returns a vote (verdict enum value) and a confidence score in `0.0-1.0`.

### §3.1 — R1 Signal Weight Voter
Quantitative confidence scoring across all Layer 1 agent contributions. **Numbers only.** Aggregates the `confidence` values and signal strengths from every detection contribution into a weighted quantitative score. No pattern reasoning, no narrative. **Isolated from human input** (P4-D4): the attacker-sophistication rubric does not reach R1.

### §3.2 — R2 Pattern Match Voter
Compares the assembled evidence chain against Layer 0 knowledge patterns. The question: **does this combination of signals match a known threat profile?** Reasons over the shape of the combined evidence against the threat-intel briefings (phish, BEC, ransomware, trojan-delivery, geo, AI-gen content), not the raw numbers.

### §3.3 — R3 Conflict Resolution Voter
Specifically targets where Layer 1 agents **disagreed** and weighs the conflict as information — disagreement is signal, not noise. The Ukraine-IP-vs-40-prior-emails scenario lives here: a high-risk geo origin that contradicts a long established sender history is exactly the conflict R3 adjudicates.

---

## §4 — Vote outcomes & resolution

| Outcome | Result |
|---|---|
| All three agree | Unanimous — verdict issued at highest confidence |
| 2-out-of-3 agree | Verdict issued; **minority opinion always logged** |
| All three disagree | `ESCALATE` — no verdict; routed to the tenant's named CIRT individual (P4-D2) for operator review |

- **Minority always logged.** On any 2-of-3 split, the dissenting voter's vote and confidence are persisted with the verdict — never discarded.
- **Escalation path.** `ESCALATE` routes to the named CIRT individual for that tenant (P4-D2), who holds freeze authority. No automated verdict is issued in the all-disagree case.

---

## §5 — Verdict enum (closed)

- `HIGH_RISK`
- `MEDIUM_RISK`
- `LOW_RISK`
- `DELIVERY_PROBLEM`
- `ESCALATE`

No verdict value exists outside this set. Schema validation rejects any other value.

---

## §6 — Voter confidence & weighting

- Each voter returns a confidence in `0.0-1.0`.
- **Equal weights at launch** — R1, R2, R3 weighted equally.
- **Calibration path:** weights are tuned only via a signed amendment **after real tenant data** exists. No autonomous re-weighting.

---

## §7 — Evidence chain output (required fields)

The verdict output must include the fields below. The evidence chain must be **plain English readable by a non-technical MSP operator** — not a raw signal dump.

```
email_id:              str    — the email this verdict is for
tenant_id:             str    — owning tenant
verdict:               enum    — one of §5
ensemble_outcome:      enum    — unanimous | majority | escalate
overall_confidence:    float  — 0.0-1.0
r1_vote:               enum   ; r1_confidence: float
r2_vote:               enum   ; r2_confidence: float
r3_vote:               enum   ; r3_confidence: float
minority_opinion:      str    — logged dissent on a 2-of-3 split; empty if unanimous
contributing_evidence: list   — references to the Layer 1 contributions consumed
plain_english_chain:   str    — operator-readable narrative of why this verdict
cirt_individual:       str    — named CIRT person for this tenant (P4-D2)
lockdown_applied:      bool   — true if P4-D3 deterministic lockdown fired
delivery_problem_path: bool   — true if routed via spam_signal_only (§8)
zero_day_referred:     bool   — true if a zero-day candidate was referred to mutation engine (§8); does NOT affect verdict
timestamp:             str    — ISO 8601
```

*(Field list drafted from the June 11 2026 session design; confirm/adjust at signing.)*

---

## §8 — Special paths

- **`spam_signal_only` (ImageClassifier #83)** routes to `DELIVERY_PROBLEM`, not `HIGH_RISK`. A delivery/spam surface signal with no fraud indicators is a delivery problem, not a fraud verdict.
- **`zero_day_candidate` (AttachmentSandbox #82)** is referred to the mutation engine **separately** and **does not change the verdict**. It is recorded (`zero_day_referred`) but is not a verdict input.

---

## §9 — Open questions from concept doc — resolved

| Concept-doc open question | Resolution in this contract |
|---|---|
| Does each voter get its own scoreboard row? | No — one row (#84) for the ReconciliationAgent ensemble; R1/R2/R3 are internal voters (§1, §8 scoreboard). |
| Escalation path when all three disagree? | `ESCALATE` → tenant's named CIRT individual with freeze authority (§4, P4-D2). |
| Does the Lung dial affect verdict thresholds under Deep breath? | Yes — `MEDIUM_RISK` + `Deep breath` = automatic `HIGH_RISK` (P4-D3). |
| Does the attacker sophistication rubric feed R1 weighting? | No — R1 is isolated from human input; the rubric feeds the Lung only (P4-D4). |

---

## §10 — Lung dependency

The Lung dial state is an **input** to the ReconciliationAgent (P4-D3), not built here. Under `Deep breath`, the deterministic lockdown in P4-D3 applies. The attacker-sophistication rubric feeds the Lung (P4-D4); the Lung's resulting state is what reaches this agent. The Lung itself is a separate contract.

---

## §11 — Test requirements

**Class 1 — Expected pass**
- Three voters each cast a vote + confidence in `0.0-1.0`; verdict resolved by 2-of-3.
- Unanimous, majority, and all-disagree outcomes each produce the correct result (§4).
- Minority opinion logged on a 2-of-3 split.
- Verdict written tenant-isolated; plain-English evidence chain present and populated.
- `spam_signal_only` → `DELIVERY_PROBLEM`; `zero_day_candidate` referred without changing verdict.
- P4-D3 deterministic lockdown: `MEDIUM_RISK` + `Deep breath` → `HIGH_RISK`.

**Class 2 — Adversarial (ELITE standard)**
- A voter cannot see another voter's vote before casting (independence enforced, P4-D6).
- Verdict outside the closed enum (§5) fails schema validation.
- All-three-disagree cannot silently emit a verdict — must `ESCALATE`.
- Cross-tenant read/write blocked (P4-D8).
- Attacker-sophistication rubric cannot reach R1 (P4-D4).
- Malformed / partial contribution set returns a safe error, not a crash.
- `spam_signal_only` must not route to `HIGH_RISK`; zero-day must not alter verdict.

**Class 3 — Known-gap xfail**
- Real-tenant verdict calibration — deferred. Reason: equal weights at launch; weight tuning needs real data + signed amendment (§6). Completion path: post-onboarding amendment.
- Lung live integration — deferred. Reason: Lung is a separate unbuilt contract. Completion path: after Lung contract.
- CIRT freeze-authority live wiring — deferred. Reason: operator-state/onboarding surface. Completion path: onboarding integration.

---

## §12 — Failure modes

| Failure mode | Detection | Response |
|---|---|---|
| Verdict outside closed enum | Schema validation + Class 2 | Immediate fail — cannot ship |
| Voter sees another's vote before casting | Class 2 independence test | Immediate fail — ensemble integrity |
| All-disagree emits a verdict | Class 2 | Immediate fail — must ESCALATE |
| Tenant isolation breach | Class 2 | Immediate fail — ledger integrity |
| Rubric feeds R1 | Class 2 | Immediate fail — P4-D4 violation |
| `spam_signal_only` → HIGH_RISK | Class 2 | Immediate fail — false-positive protection |
| Zero-day alters verdict | Class 2 | Immediate fail — P4-D... special path |
| Health score below 85 | Agent Health Score Rubric | Phase does not close — reworked until ELITE |

---

## §13 — Dependencies, scoreboard, relationship to signed specs

- **Dependency:** Phase 3 must be **fully GATED** before this contract is drafted into build. (Phase 3 closed `ce386f7`.)
- **Scoreboard:** add row **84 — ReconciliationAgent ensemble, `SIGNED_UNBUILT`, Layer 4 Evidence, DEPTH priority** (added on signing).
- **Relationship:**
  - Phase 1 — verdict written to `core/blackboard/` per Phase 1 schema (new verdict surface to be defined in build).
  - Phase 2 — R2 consumes Layer 0 briefings.
  - Phase 3 — consumes all six Layer 1 evidence types; uses `sender_domain` (Amendment 1 §B) as the correlation join key.
  - Agent Health Score Rubric — ELITE 85+ required.

---

## §14 — Operator Sign-Off

**Status:** §11 SIGNED — build authorization granted per §11 scope.

**Signed:** Matt Nichol
**Date:** June 11th 2026
