# NorthStar Cyber Insurance / Vendor Payment Integrity — Direction SPARK

**Status:** SPARK only. Pre-spec. Unsigned. Not §11. Not client-facing copy. Not pricing approval. Not a broker / insurer claim. Not implementation authorization.

**Captured:** 2026-05-31 by Cursor (Claude Opus 4.7) at operator request, after commit `7faa86b` (`seed current state map with alert fatigue doctrine`).

**Architect:** Matt. The strategic direction of NorthStar's positioning, the wedge framing, and any future commercial / pricing / channel decisions are Matt's to make.

**Purpose:** Preserve the operator's strategic-direction conclusion that the cyber-insurance discovery lane is a **buyer-pressure / evidence-readiness wedge** for a Vendor Payment Integrity business spine — *while* translating risky `compliance` / `certification` / `premium reduction` / `approved by` language into NorthStar-safe wording before any of it reaches a buyer surface. Held, not buried.

**Authority gate:** Nothing in this SPARK authorizes runtime code, edits to signed specs, additions to the build queue, pricing decisions, broker outreach, carrier outreach, client-facing copy, or any change to the `Cyber_Insurance_Evidence_Package_Deep_Dive.md` (§13-signed). The active operational queue remains MSP discovery against the §11-signed `Compliance_and_Trend_Watch_Process.md` discipline and the existing `Cyber_Insurance_Evidence_Package_Cheaper_Proof_Runbook.md` D10 gate.

---

## §1 Core thesis

NorthStar should move toward **Vendor Payment Integrity Evidence** as the business spine: identify, review, and document risky vendor-payment changes *before* money-movement decisions are made.

The cyber-insurance lane is the **wedge** that gives this spine commercial pull. MSPs and their SMB clients face concrete underwriting-conversation pressure during policy renewal and post-incident review. NorthStar's already-existing Financial State Ledger / Vendor Baseline Store / Two-Channel Confirmation surfaces produce exactly the structured evidence that supports those conversations — *as evidence*, never as a claim of underwriting approval, certification, or premium effect.

The wedge is a discovery vehicle, not a product line. NorthStar does not become a cyber-insurance product. NorthStar becomes a Vendor Payment Integrity Evidence engine that *happens to be useful* during cyber-insurance underwriting, renewal, and post-incident conversations.

---

## §2 Keep / rewrite table

| Discipline | Item |
|---|---|
| **Keep** | Insurance readiness as a discovery wedge (not a product positioning) |
| **Keep** | Vendor Payment Integrity as the strongest control story NorthStar already has evidence for |
| **Keep** | Evidence trail as the product asset (the audit-grade record, not the verdict) |
| **Keep** | Carrier-agnostic reports (single format per `Cyber_Insurance_Evidence_Package_Deep_Dive.md` D4 — no per-carrier variants) |
| **Keep** | MSP + broker discovery as a *future* channel test, gated on the existing D10 cheaper-proof bar |
| **Keep** | No warranty / no guarantee posture; the existing `Compliance_and_Trend_Watch_Process.md` §5.1 / §5.2 boundary holds |

| Rewrite (from `→` to) | Use instead |
|---|---|
| `Compliance Engine` | **Evidence Readiness Engine** *or* **Cyber Insurance Evidence Support** |
| `Integrity Certificate` | **Monthly Evidence Summary** |
| `Premium Reducer` | **Insurance Conversation Support** |
| `NorthStar Verified` | **Verified Review Recorded** *or* **NorthStar Evidence Available** |
| `required by carriers` | **structured around common underwriting evidence requests** |
| `approve coverage` | **support underwriting conversations** |

The rewrite column is the only authorized vocabulary NorthStar may use on any surface that touches buyers, MSPs, brokers, carriers, or underwriters. The left-column phrases appear in this SPARK only as the explicit list of phrases to avoid.

---

## §3 NorthStar-safe positioning sentence

This is the one positioning sentence the operator authorized for use on internal positioning surfaces (deck draft, MSP discovery script, broker discovery script). It is **not** approved for client-facing copy yet — that promotion requires a separate operator decision after MSP / broker discovery evidence.

> *"NorthStar helps MSPs produce structured evidence that vendor-payment changes were identified, reviewed, and documented, so SMBs can better support cyber-insurance underwriting, renewal, and post-incident conversations."*

Authorship rule applies: this sentence is operator-authored. AI-generated rewrites of it are forbidden as buyer-facing copy without a fresh operator pass on the rewritten text.

---

## §4 Explicit boundary

NorthStar **does not** claim, imply, or position around:

- `compliance` with any framework (absolute or partial) — see `Compliance_and_Trend_Watch_Process.md` §5.1.
- `certification` of any kind, by any body, against any standard.
- `insurer approval`, `carrier approval`, `underwriter approval`, `approved by carriers`, or any equivalent third-party endorsement language.
- `premium reduction`, `premium effect`, `cheaper coverage`, or any pricing-outcome promise tied to using NorthStar.
- `policy eligibility`, `coverage qualification`, or any underwriting-decision substitute.
- `fraud prevention` as an absolute (NorthStar surfaces evidence for human review — see Financial State Ledger / Vendor Baseline Store deep-dives; the recommendation is `needs_review`, not `block`).
- `coverage approval` of any kind.

This SPARK:

- Does not add runtime code.
- Does not edit signed specs.
- Does not alter the current `Cyber_Insurance_Evidence_Package_Deep_Dive.md` spec.
- Does not promote anything to `PROJECT_BUILD_AND_AUDIT_QUEUE.md`.

The active queue remains: **MSP discovery — 3 relevant MSP conversations, looking for 2 strong yeses with a named SMB anchor and a named upcoming insurance / underwriting conversation**, per `Cyber_Insurance_Evidence_Package_Cheaper_Proof_Runbook.md` D10 and the `Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv` worksheet.

---

## §5 Future trigger conditions

This SPARK may be promoted out of SPARK status only when **at least one** of the following holds, *and* Matt explicitly authorizes the promotion. Cursor / Codex / Claude may flag a candidate trigger; promotion is not automatic.

1. **MSP discovery evidence (primary trigger).** MSP discovery (per the D10 cheaper-proof bar) produces evidence that buyers ask their MSP for vendor-payment evidence in insurance / underwriting / renewal conversations. "Asks for it" must be a named MSP, a named SMB-side context, and a concrete request shape — not generalized interest.
2. **Broker discovery evidence (parallel trigger, gated on operator authorization to do broker discovery at all).** A broker / underwriter / carrier-side conversation surfaces vendor-payment-change evidence as a structured underwriting-question category for the email-fraud / inbox-layer surface — primary source (`P`) per `Compliance_and_Trend_Watch_Process.md` §2.6, not vendor (`V`).
3. **Post-incident evidence demand (reactive trigger).** A real SMB-side post-incident review (NorthStar tenant or not) surfaces a documented request for vendor-payment-change evidence as part of the incident-response or carrier-side conversation. Captured through the existing `THREAT_INTEL_LOG.md` pattern.

Triggers that **do not** justify promotion:

- Internal enthusiasm. A clean spec or a satisfying matrix score is not buyer-pressure evidence.
- Single-source vendor research (`V`). Carrier-aligned vendor reports may inform; they cannot trigger.
- AI / agent-side argument that "this would obviously sell." The Authorship Rule applies: a buyer-pressure conclusion requires an operator-recorded source, not a model assertion.
- A signed spec elsewhere that mentions vendor-payment integrity. Signature on the existing package does not promote this SPARK; this SPARK is positioning, not implementation.

When a trigger fires, the operator's promotion path is: capture the trigger evidence into `THREAT_INTEL_LOG.md` and `think_sheet.md`, then decide whether to spec a follow-on Vendor Payment Integrity Positioning deep-dive (which would be its own §11 candidate, separate from the existing Cyber Insurance Evidence Package).

---

## §6 Boundaries (anti-drift footer)

- This SPARK does not decide.
- This SPARK does not authorize buyer-facing copy. The §3 positioning sentence is internal-only until a separate operator pass clears it for buyer-facing surfaces.
- This SPARK does not authorize broker or carrier outreach. Broker / carrier conversations remain operator-gated and require Matt's explicit decision before any contact is initiated.
- This SPARK does not authorize pricing, packaging, or product-sheet changes. Any future commercial framing for Vendor Payment Integrity Evidence is a separate operator pass against `Product_Sheets/` discipline.
- This SPARK does not authorize edits to the §13-signed `Cyber_Insurance_Evidence_Package_Deep_Dive.md`. That spec governs the *package implementation* and remains authoritative on package shape, redaction rules, vocabulary translation list, and boundary statement.
- This SPARK does not authorize a new §5.1 forbidden-language addition. Project-wide forbidden-language additions remain a `Compliance_and_Trend_Watch_Process.md` §5.1 revision path with §11 re-signature.
- If any phrase or claim in this SPARK conflicts with a §11-signed spec, the signed spec wins.
- If this SPARK creates discovery friction (e.g. the rewrite table makes operator MSP-conversation language unnatural), the operator may rewrite the rewrite table — not the buyer-facing surfaces — in a follow-up SPARK pass.

---

## §7 Named failure modes to recognize by name

- **Wedge-as-product drift.** Treating the cyber-insurance lane as a product line rather than a discovery wedge. The spine is Vendor Payment Integrity Evidence; the wedge is the discovery surface.
- **Forbidden-language slip via wedge framing.** "Of course it's fine to say `compliance` once because we're talking about insurance" — no. The §5.1 boundary holds across every surface. The rewrite column is the only authorized vocabulary on buyer-facing surfaces.
- **Decision laundering through the matrix.** Treating any internal scoring (Strategic Relevance Score, Pain Matrix, Revenue Matrix per `_NorthStar_Strategy_Matrix_Discipline_SPARK.md`) as authorization to promote this SPARK. Matrices rank; the operator decides; the trigger conditions in §5 above are the gating bar.
- **Pre-discovery promotion.** Promoting this SPARK before §5's trigger evidence exists. Internal enthusiasm is not buyer pressure.
- **Free-work perception.** Offering vendor-payment-integrity evidence work as a free add-on to MSP discovery conversations. Discovery is discovery; *implementation work* requires a pricing pass that does not exist yet.
- **Authority drift via positioning sentence.** Treating the §3 positioning sentence as a sales-page line, a product tagline, or a pricing statement. It is none of those.
- **Authorship Rule violation.** Generating buyer-facing rewrites of the §3 positioning sentence and presenting them as operator-approved without a fresh operator pass.
- **Sycophancy / praise-stacking.** Returning to this SPARK to retroactively reinforce its conclusions because they sound smart. Re-reading is fine; re-scoring is decision laundering.

---

## §8 Index entry intent (for `MASTER_INDEX.md`)

When indexed, this SPARK should read as: pre-spec direction capture of the Vendor Payment Integrity / Cyber Insurance wedge framing; preserves the keep-list, the rewrite list, the §3 internal-only positioning sentence, the §4 "what NorthStar does not claim" boundary, and the §5 trigger conditions for promotion; introduces no new D-decisions, no new gates, no new requirements; does not alter the existing §13-signed `Cyber_Insurance_Evidence_Package_Deep_Dive.md`; held, not buried — promotion requires both an operator-recorded §5 trigger and Matt's explicit decision.

---

**End of SPARK. Direction only. No decision implied.**
