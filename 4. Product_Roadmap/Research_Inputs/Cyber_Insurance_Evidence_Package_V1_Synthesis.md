# Cyber Insurance Evidence Package — V1 Synthesis

**Status:** Pre-spec synthesis. Research / shaping input only. Not §11. Not §13. Not implementation authorization. Not client-facing copy. Not pricing approval.

**Captured:** 2026-06-01 by Cursor (Claude Opus 4.7) at operator request, after Matt collected enough directional evidence to shape v1 without pretending the MSP discovery gate has passed.

**Authority:** Matt decides. This file proposes a v1 *shape* against existing signed and pre-spec artifacts; it does not change any signed contract, does not advance D10, and does not authorize implementation.

**Companion artifacts (read for context; this file does not amend them):**
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` (DRAFT pre-§11; §12 Q1–Q11 resolved pending §13 lock; §14 v1 test plan defined; D10 cheaper-proof still open)
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Cheaper_Proof_Runbook.md` (D10 go bar)
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv`
- `4. Product_Roadmap/_NorthStar_Cyber_Insurance_Vendor_Payment_Integrity_SPARK.md`
- `4. Product_Roadmap/Research_Inputs/Cyber_Insurance_Evidence_Pain_Points_Research_Map.md`
- `4. Product_Roadmap/Research_Inputs/Vendor_Payment_Change_Verification_Research_Report.md`
- `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` §5 (forbidden-language + vocabulary-translation canonical list)
- `CURRENT_STATE_MAP.md` Alert-fatigue doctrine + False-positive / false-negative correction evidence loop (2026-06-01)
- `Frontier_Intake_Log.md` 2026-06-01 Reddit confirmation entry

---

## §1 Current evidence summary

Where the inputs actually sit as of 2026-06-01:

| Input | Shape | What it tells us | What it does NOT do |
|---|---|---|---|
| `Cyber_Insurance_Evidence_Package_Deep_Dive.md` | DRAFT (pre-§11) with §12 Q1–Q11 resolved, §14 v1 test plan defined | Buyer-readable bundle scope is locked at the design layer: email-fraud / inbox-layer MDR only; carrier-agnostic; structured records; scope-boundary statement printed in the package; full failure-mode list with mitigations | Does not authorize implementation; §13 sign-off blocked on D10 cheaper-proof + §14 executed run |
| `Cyber_Insurance_Evidence_Package_Cheaper_Proof_Runbook.md` + worksheet | Operator runbook + 3-row CSV | 2-of-3 relevant MSP conversations needed; each "yes" requires a **named SMB anchor** AND a **named upcoming insurance / underwriting conversation** | Does not lower the bar to "sounds interesting"; informal signal is `partial` at best |
| `_NorthStar_Cyber_Insurance_Vendor_Payment_Integrity_SPARK.md` | SPARK direction | Cyber-insurance is the **wedge**; Vendor Payment Integrity Evidence is the **spine**; keep / rewrite vocabulary table | Does not authorize buyer-facing copy or pricing |
| `Cyber_Insurance_Evidence_Pain_Points_Research_Map.md` (P01–P15) | Pre-spec research input (2026-06-01) | 15 investigation themes already framed; §4 evidence-capture schema is ready for live captures | Does not advance D10; hypotheses only in §5 |
| `Vendor_Payment_Change_Verification_Research_Report.md` | Archived research synthesis | The defensible **workflow shape** is: request logged → known-good callback → second approval where possible → delayed first payment to changed account → evidence preserved | Not D10 evidence; not customer discovery |
| Reddit confirmation (`Frontier_Intake_Log.md` 2026-06-01) | Three replies, peer signal | Underwriter questions have sharpened since ~2023; reviewers ask for **proof a control is operating**; one respondent asked whether `nmap`-style raw evidence is enough — confusion about what evidence is credible is real | Not D10; not validated market proof |
| `CURRENT_STATE_MAP.md` false-positive / false-negative correction evidence loop (2026-06-01) | Operator-captured doctrine | NorthStar moves forward by preserving misses and over-flags, recording the why, applying scoped corrections, and proving the correction now holds — internal credibility record, not necessarily public | Does not weaken any test; does not authorize tuning around failures |
| Todd Chapman / CMIT Solutions reply (operator-reported, not yet logged in `Frontier_Intake_Log.md` / worksheet) | MSP-owner reply: skeptical of the outreach wording but offered coffee and wants to understand mutual value | A real door has opened with a real MSP owner; framing pushback is signal, not failure | Not a D10 yes (see §7); not implementation green-light |
| Existing runtime evidence | `core/scoring/financial_state_ledger.py`, Vendor Baseline Store, Two-Channel Confirmation pin, ghost-thread + header-divergence detectors, signed policy state, append-only Blackboard, kill switch, signed §11 specs as architecture documentation, 1055-test baseline with intentional FAIL → patch → recovery records preserved in `eval_report_2026_05_22_phase_1_5_*` | Stage A already produces the artifacts the §14 fictional case maps onto; the FP/FN correction loop has real anchors in repo | Not buyer validation; not packaging itself |

**Bottom line:** The shape of the package is well-defined. The remaining open gates are operator-side (D10 cheaper-proof + §14 executed run), not design-side.

---

## §2 What pain is now validated enough to move forward

"Validated enough to **shape** v1" is a lower bar than "validated enough to **ship**." Shaping is the work that lets the v1 package answer real pains the moment D10 closes; it does not bypass D10.

The pains where the inputs converge across **at least two independent sources** (per `Compliance_and_Trend_Watch_Process.md` §2.6 confirmation discipline):

| Pain (from research map IDs) | Sources that converge | Why this is enough for shaping |
|---|---|---|
| **P02 — Proving controls operate, not just exist** | Reddit reply ("underwriters ask better questions, harder to answer yes on partial implementations"); Pain Map P02; vendor-payment research workflow expectation; existing FSL / Vendor Baseline Store / Two-Channel Confirmation runtime evidence | Two independent confirmations + a runtime surface that already produces "control-operating" evidence → safe to shape against |
| **P07 — Vendor-payment fraud evidence gaps** | Vendor-payment research report; SPARK §1 thesis; Pain Map P07; Reddit signal that evidence-collection is bottlenecked by legacy design and individual company shortcomings | Documented review workflow is a known artifact category; gaps are widely reported |
| **P10 — Reviewer-ready wording** | Reddit reply about oversharing risk in underwriter kickoffs; Pain Map P10; SPARK §2 rewrite list; `Compliance_and_Trend_Watch_Process.md` §5.5 vocabulary translation | Two independent confirmations + an existing vocabulary-translation list → safe to shape against |
| **P13 — Raw technical evidence confusion** | Reddit `nmap` question; Pain Map P13; cyber-insurance deep-dive §5 failure mode iv (vocabulary leak) | Confusion about "what is enough" is real; shaping a structured-record format is the answer |
| **P15 — Repeatable MSP evidence packaging** | Pain Map P15; SPARK §1 wedge framing; existing `MSP_Discovery_Evidence_Package.md` pattern; deep-dive §6 record schema | The "directory of structured records, not a stack of PDFs" choice already addresses this |

Pains that are **signal-present but not yet two-source-confirmed** (continue to investigate via §4 of the research map; do not let them drive v1 shape yet):

- P01 (scattered evidence), P03 (partial implementations / exceptions), P04 (sharper underwriting questions broadly), P05 (oversharing), P06 (cost-to-fix vs cost-to-risk), P08 (ownership), P09 (legacy exceptions), P11 (freshness), P12 (broker / insurer / MSP mismatch), P14 (incident / claim documentation stress).

**What this does not validate:** that MSPs will buy; that brokers will adopt; that underwriters will accept the artifact format; that any specific pricing works. Those questions still belong to D10 discovery and post-D10 work.

---

## §3 Why Vendor Payment Change Review is the safest v1 wedge

Within the email-fraud / inbox-layer MDR scope already locked in the deep-dive §2, **Vendor Payment Change Review** is the narrowest, evidence-richest, lowest-claim slice. The reasons line up across multiple signed and pre-spec artifacts:

1. **Existing runtime evidence is densest here.** Financial State Ledger / Delta Tripwire, Vendor Baseline Store (per-tenant SQLite + HKDF salt + Guardrail 11 + 12 wiring), Two-Channel Confirmation enforcement, ghost-thread and header-divergence detectors, kill-switch wiring, append-only Blackboard, signed policy state, and tenant override audit events all converge on this surface. The §14 fictional Stage A case is itself a payment-redirect scenario.
2. **The control reality is one sentence.** "Was a vendor payment change identified, reviewed, and documented before action?" That is a single-question control-operation check — exactly what the Reddit signal and Pain Map P02 say underwriters want.
3. **Workflow shape is independently documented.** The vendor-payment research report records the defensible review pattern (request logged → known-good callback → second approval where possible → delayed first payment → evidence preserved). NorthStar's runtime already produces machine-readable records of the email-side half of that workflow.
4. **It maps cleanly to the five-stage Evidence and Outcome Reporting lane** the deep-dive locks: Detection → Verification → Evidence → Audit Trail → Outcome Documentation. The §6 / §12.Q7 schema already names one record per stage.
5. **It does not require scope expansion.** Nothing here pushes past the deep-dive §2 in-scope list. MFA / EDR / backups / IR / patching remain MSP responsibility, with the boundary statement in §2 unchanged.
6. **It is the wedge the SPARK already names.** Per `_NorthStar_Cyber_Insurance_Vendor_Payment_Integrity_SPARK.md` §1, Vendor Payment Integrity Evidence is the spine; the cyber-insurance package is the discovery surface. v1 should not re-litigate that direction.
7. **It has the strongest false-positive / false-negative narrative.** The 2026-05-22 eval report preserves a gate FAIL on `vendor_invoice_fraud` recall and the subsequent no-spend prompt patch + 5/5 diagnostic recovery — exactly the evidence shape the new correction-evidence-loop doctrine names. The internal credibility record is already on disk.

**Important non-claim:** "Safest v1 wedge" means the easiest evidence surface to shape without overclaiming. It does not mean "validated to sell." That validation still belongs to D10.

---

## §4 What the v1 package should include

Each row is shaped against existing signed and pre-spec artifacts. v1 = single-tenant, single-vendor, single-invoice (per deep-dive §14.2). Multi-tenant / multi-vendor / multi-invoice cases are out of scope until §14 has cleared at least one end-to-end pass.

### §4.1 Five-stage record set (Detection → Verification → Evidence → Audit Trail → Outcome Documentation)

| Stage | Record content (v1) | Source anchor | Notes |
|---|---|---|---|
| **Detection** | Lift-only invariant test outputs for the detectors that fired on the case: FSL / Delta Tripwire, Vendor Baseline Store new-or-changed signal, header divergence (From / Reply-To / Return-Path / Sender), ghost-thread continuity, Callback Phishing / TOAD body-language hits where applicable | Deep-dive §14.3.1; `tests/test_recommended_risk_floor_lift_only_invariant.py`; relevant detector files | Direction-of-effect is mathematically locked (lift-only); no detector lowers risk |
| **Verification** | Client-facing 5-axis rubric scoring explanation (`sender_identity`, `conversation_context`, `content`, `intent`, `origin_timing`), `recommended_action` most prominent, `why_this_score` per axis | Deep-dive §14.3.2; signed `Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` §11 + §11.1 + §11.2 | Includes the §11.2 `callback_phishing_pattern → origin_timing` mapping where TOAD fired |
| **Evidence** | Effective parameter report for the affected tenant, with per-key provenance (`default` / `signed_policy` / `tenant_override`) and reverse-chronological override audit tail | Deep-dive §14.3.3; `core/production_state/effective_parameters_report.py`; `Generated/Acme_Effective_Parameter_Report_Demo.md` | Per-tenant only; cross-tenant aggregation is non-scope for v1 |
| **Audit Trail** | Signed policy state hash + tenant override audit events with `requested_by` / `approved_by` separation; reference into append-only Blackboard for the relevant `EMAIL_INBOUND`, `EMAIL_ANALYSIS`, `EFFECTIVE_PARAMETERS_REPORT` records | Deep-dive §14.3.4; `core/production_state/`; `core/blackboard/` runtime | Hash references, not raw email bodies |
| **Outcome Documentation** | Single review-recorded outcome line — e.g. `payment_change_reviewed_before_action` — with timestamp, operator role, scope of review, and the source artifact path of the record(s) that drove the outcome | Deep-dive §14.3.5; SPARK §3 protected sentence shape | Phrased as `review recorded`, not "approved" / "blocked" |

### §4.2 Cross-cutting elements

- **Scope-boundary statement** printed in the package (deep-dive §2 required boundary statement, verbatim).
- **Carrier-agnostic format**, single rendering, no per-carrier variants (deep-dive §5 failure mode x; D4).
- **Plain-English language pass** against `Compliance_and_Trend_Watch_Process.md` §5.5 vocabulary translation list.
- **Source-artifact map** showing every claim's `source_artifact_path` (deep-dive §4 / §6).
- **Freshness fields** per §6.1 (30-day for mutable operational evidence, 90-day for reproducible / slower-decay, freshness-exempt for structurally signed immutable evidence with valid `signed_by.signature_value`).
- **False-positive / false-negative correction evidence section** (see §6 of this synthesis).
- **Single-tenant filter** end-to-end; cross-tenant aggregates allowed only when explicitly marked and provably non-identifying (deep-dive §5 failure mode v).
- **Operator-authored summary** of the case — including the protected sentence from the deep-dive (cyber-insurance lane invariant) verbatim, not paraphrased.

### §4.3 Shape, not implementation

v1 shape work is a markdown / structured-record sketch against `tests/fixtures/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001.json`. It is **not** code that generates packages. Implementation is the spec-after-§13 step; the §14 plan governs the runnable test once signed.

---

## §5 What the v1 package must NOT include

Hard non-scope. Every item in this list maps to either a signed contract, a failure-mode mitigation, or the project's compliance-claim boundary.

- **Cross-tenant data.** Per-tenant filter applies end-to-end. (Deep-dive §5.v, Guardrail 11.)
- **Anything outside email-fraud / inbox-layer MDR.** No MFA, EDR, backups, IR plans, patch management, vulnerability scans, SOC reports, ISO certificates. (Deep-dive §2 non-scope.)
- **Per-carrier variants** or carrier-specific question mappings. (Deep-dive §5.x; D4.)
- **Raw email bodies, full headers, account numbers, routing numbers, IBANs, SWIFT codes, payment portal URLs with tokens, or attachment payloads.** Hash references and structured records only. (Vendor Baseline Store §D2 hash-only + per-tenant HKDF salt; FSL D13 data minimization.)
- **Real client production data without explicit operator consent.** v1 demos run against the fictional `bluefin-marine-supplies-demo` fixture or equivalent synthetic case (deep-dive §14.2).
- **Per-event alert stream rendering.** Stage A is batched / daily-digest / decision-support; per-email alert pretence violates the Alert-fatigue doctrine.
- **Forbidden-claim language.** `compliant`, `certified`, `insurer-approved`, `premium reducer`, `coverage approved`, `guarantee`, `bulletproof`, `fully secure`, `complete`, attestation, SOC 2 / ISO 27001 attestation language, and the rest of `Compliance_and_Trend_Watch_Process.md` §5.1 outside the §5.3 allowed-context carve-outs.
- **Buyer-facing rewrites of the protected sentence.** The cyber-insurance lane invariant — *"NorthStar helps identify, review, verify, and document high-risk financial exposure before action is taken."* — is operator-authored; AI-paraphrased versions are forbidden (Authorship Rule).
- **Cyber-insurance jargon** (`attestation`, `control efficacy`, `regulatory mapping`, `compensating control`, `material weakness`) outside the vocabulary-translation list contexts.
- **Pricing copy, bundle copy, or commercial framing.** The SPARK §3 internal positioning sentence may appear in internal docs; buyer-facing copy is a separate operator pass.
- **Any claim that the package makes anyone compliant, approved, insured, eligible, or premium-reduced.** The package supports underwriting conversations with dated, scoped evidence; it does not produce outcomes.
- **Detector behavior changes.** v1 is a packaging surface over evidence the runtime already produces. New detection capability is out of scope.

---

## §6 How false positives / false negatives / corrective actions appear in the internal evidence record

This section operationalizes the 2026-06-01 `CURRENT_STATE_MAP.md` correction-evidence-loop doctrine for the v1 package. The record is **internal credibility evidence**; it can be referenced from the package's audit-trail surface but does not have to be rendered to the buyer in full unless the operator decides otherwise on a later pass.

### §6.1 Record shape (one entry per preserved miss or over-flag)

| Field | Description |
|---|---|
| `correction_id` | Short unique id (e.g. `fpfn-2026-06-01-001`) |
| `surface` | Detector / scoring / digest / workflow / prompt / fixture / expectation-contract / other |
| `failure_type` | `false_negative` / `false_positive` / `expectation_contract` / `fixture` / `prompt` / `detector` / `workflow` |
| `case_ref` | Eval case id, fixture path, or sanitized scenario description (no raw client data) |
| `observed_behavior` | What fired or did not fire, summarized |
| `why_corrective_action_warranted` | Risk, buyer-trust impact, alert-fatigue risk, evidence gap, or signed-spec mismatch — the **why** the doctrine requires |
| `correction_applied` | Scoped change: prompt floor, fixture fix, contract revision, detector pattern, workflow step |
| `retest_evidence` | Test name(s), eval rerun reference, or regression-coverage line that now pins the correction |
| `proportionality_note` | Why the correction is scoped and proportionate, not a blanket loosening |
| `recorded_at` | ISO timestamp |
| `recorded_by` | Operator-authored (Matt) or AI-drafted under operator review |
| `linked_artifacts` | Failure card path, eval report path, activity-log entry, audit packet path |

### §6.2 Anchor examples already in the repo (used as template, not as v1 content)

- `eval_report_2026_05_22_phase_1_5_rerun.md` — preserved 36/40 gate FAIL with clean precision / FPR but weak `vendor_invoice_fraud` recall (40% vs 60% floor required). Failure preserved; not hidden.
- `eval_report_2026_05_22_phase_1_5_vf-00{1..5}_diagnostic.md` — per-case `grok-4` diagnostics after the no-spend prompt patch added the Phase 1.5 vendor-invoice recall floor to `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT`; 5/5 PASS recorded with raw LLM JSON.
- `tests/test_email_risk_scoring_agent.py` — prompt-lock regression coverage that pins the patched prompt and prevents silent drift.
- `tests/test_vendor_payment_integrity_break_it.py` — six break-it tests pinning Alert-fatigue doctrine, hash-only storage, per-tenant HKDF salt, lift-only max-merge floor, recommended-action `needs_review` invariant.

### §6.3 Inclusion rule in the v1 package

For each detector or workflow surface that contributes evidence to a v1 record, the package must be able to **reference** the most recent correction record(s) for that surface — even if the buyer-facing render shows only a count, a date range, and the proportionality note. The full why-rationale lives in the internal credibility record; the package surface respects the operator's redaction call per deep-dive §9.

### §6.4 Non-authorization

Nothing in §6 authorizes weakening tests, dropping cases, retroactively relabeling fixtures to make failures disappear, or tuning around an inconvenient eval result. The doctrine's boundary text applies verbatim: *"The correction must be scoped, proportionate, and retestable."*

---

## §7 How Todd's response should be classified

**Verdict:** **Credible door opening. Not a D10 yes (yet).**

Reasoning, against the locked `Cyber_Insurance_Evidence_Package_Cheaper_Proof_Runbook.md` D10 go bar:

- A D10 per-MSP "yes" requires both:
  1. A **named SMB anchor** voluntarily provided by the MSP.
  2. A **named upcoming insurance / underwriting / renewal / claim-documentation conversation** for that SMB.
- Todd's reply (as reported by the operator) is an **MSP-owner reply** with skepticism on the outreach wording and an invitation to coffee to understand whether there is mutual value.
- That is exactly what the runbook calls `partial` at best: framing interest from a relevant MSP, without either named anchor present yet.
- The runbook explicitly warns: *"Do not lower the bar to 'sounds interesting.' Interest without both named anchors is a useful signal, but it is not a D10 yes."*

**What Todd's reply IS:**
- A real MSP-owner conversation in motion. The first one. That alone is more than the worksheet has logged so far.
- Useful signal that the outreach **framing** triggered a skeptical-but-engaged response — better diagnostic than a polite decline. Skepticism on wording is buyer language about what reads as overclaim or unclear value, not buyer rejection of the underlying idea.
- A natural setting (coffee) for asking the three runbook questions and the pricing-signal question without sales pressure.

**What Todd's reply IS NOT:**
- A D10 yes row in `Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv`.
- Authorization to mark the cheaper-proof gate cleared.
- Authorization to draft an implementation spec or to claim §13 sign-off readiness.
- Validated market proof of MSP demand by itself.

**Recommended worksheet handling (operator decides):**

- Log Todd's reply as a `partial` row when he is met, *only* if the conversation establishes him as a **relevant MSP** (per the runbook definition: an MSP that can plausibly answer the framing for SMB cyber-insurance evidence packaging). Until then, it is pre-D10 conversation in motion.
- If the coffee conversation produces both named anchors, log a `yes` row and use Todd's verbal confirmation as the gate evidence (verbal counts per D10).
- If the conversation produces only one anchor (e.g. named SMB but no named upcoming underwriting conversation), it is `partial` — useful, not a gate pass.
- Record the wording skepticism as Discovery signal in the worksheet's notes / `Frontier_Intake_Log.md` so the framing learning is durable.

---

## §8 Remaining decision — keep D10, revise D10, or treat D10 as discovery quality bar while shaping v1 in parallel

Three options. The operator decides. This synthesis describes shape, not choice.

### Option A — Keep D10 as-is

- **What it means:** 3 relevant MSP conversations; 2 of 3 must produce both named anchors; verbal confirmation counts; the §13 sign-off precondition stays exactly as locked in the deep-dive.
- **Pros:** Preserves spec integrity. No risk of moving the bar to fit Todd. The §13 precondition is one operator decision — keep it stable.
- **Cons:** Slows v1 shape work while the gate stays open. May feel artificial if 1-of-3 produces an unambiguous deeply-engaged MSP yes and the other two cannot be reached.
- **Compatible with this synthesis?** Yes. Shaping work (§4 / §6) is allowed in parallel because it is pre-spec research, not implementation.

### Option B — Revise D10

- **What it means:** Edit the per-MSP "yes" definition or the count threshold in the runbook + worksheet + deep-dive §12.Q10 + D10. Requires operator decision plus the normal revision path (operator instruction → spec edit → fresh `complete_gate.py` → §13 readiness re-eval). Cursor / Claude cannot draft signature wording.
- **Pros:** May be appropriate if discovery is harder than the original gate assumed (e.g. local MSP density is lower than anticipated; broker / bookkeeper conversations are richer than MSP conversations).
- **Cons:** Highest risk of authority drift if revised under one specific MSP's pressure (Todd-shape revision). The §13 precondition exists exactly to prevent post-hoc loosening. Any revision should be operator-justified by **general** discovery evidence, not by accommodation of a single contact.
- **Compatible with this synthesis?** Yes, but only if the revision is operator-driven and recorded with a written reason.

### Option C — Treat D10 as discovery quality bar while continuing v1 package shaping

- **What it means:** D10 stays the locked §13 gate (no revision). Pre-spec v1 shape work continues against the §14 fictional case (e.g. mock record-set drafts, internal credibility-record templates, plain-English language passes). Implementation spec drafting, signature work, and runtime code remain blocked behind D10.
- **Pros:** Keeps build momentum on the safest evidence surface (vendor payment change review) without pretending the gate is met. Shaping work is exactly the kind of pre-spec preparation `AGENTS.md` §6 allows ("Pre-§11 drafts iterate freely"). Lets the §14 test plan be exercised against a synthetic case so an executed v1 test plan run is closer to ready when D10 clears.
- **Cons:** Requires discipline to not let shaping work bleed into implementation. Requires every shaping artifact to carry the same boundary header this file uses.
- **Compatible with this synthesis?** This is the option this synthesis is implicitly written for, but it remains the operator's call.

**This file does not pick.** Matt decides which option holds, and the choice gets recorded in `PROJECT_ACTIVITY_LOG.md` / `PROJECT_HANDSHAKE.md` per existing discipline.

---

## §9 Next concrete work items

In suggested execution order; each is gated only where noted. Operator selects which to run.

1. **Log Todd's reply into `Frontier_Intake_Log.md`** as a 2026-06-01 entry under the existing 2026-06-01 section pattern, marked `partial` discovery signal, with explicit D10 status (`Does NOT advance D10`) and the named-anchors-still-missing reason. (Operator-authored or AI-drafted under operator review.)
2. **Run the Todd coffee conversation** using the existing `Cyber_Insurance_Vendor_Payment_Integrity_MSP_Call_Pack.md` 10-minute call flow + three runbook questions + pricing-signal question. Log the outcome in `Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv` against the D10 per-MSP definition (yes / partial / no, with anchors recorded only when voluntarily provided).
3. **Continue reaching 2 more relevant MSP conversations** per the runbook's starter target list (Carpathia IT / NetDNA / EC Managed IT / IT Works MSP BC / SFY IT / Good IT — or any relevant MSP that meets the framing). 2-of-3 D10 yes remains the gate; nothing in this synthesis changes that.
4. **Capture each new pain-point input** using the §4 evidence-fields schema in `Cyber_Insurance_Evidence_Pain_Points_Research_Map.md`. Tag with `confidence` and `source_type`; separate observed pain from inferred NorthStar relevance.
5. **Draft a v1 record-set sketch** against the §14 fictional Stage A case (`tests/fixtures/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001.json`) — five-stage records in the §4 shape, with the boundary statement printed and the vocabulary-translation pass applied. This is shaping work, not generation code. Save under `4. Product_Roadmap/Research_Inputs/` or as a separate pre-spec artifact named so it cannot be mistaken for implementation.
6. **Begin an internal correction-evidence-record log** for the email-fraud detector set, using the §6.1 record shape in this synthesis. Seed with the existing 2026-05-22 vendor-invoice recall preservation + patch + diagnostic recovery as the first entry. Internal credibility record; not yet a buyer-facing surface.
7. **Once D10 clears** (operator decision), the next gated step is the §13 sign-off readiness review and `complete_gate.py` packet — *not* implementation. Implementation requires §13 signed plus an explicit start-build instruction per the deep-dive footer.
8. **Defer pricing, packaging, broker outreach, and any client-facing copy** until D10 closes and an operator-authored pass clears the §3 SPARK positioning sentence for buyer-facing use.

---

## §10 Boundaries / non-authorizations

This synthesis does **not**:

- Edit or reinterpret `Cyber_Insurance_Evidence_Package_Deep_Dive.md`, `Cyber_Insurance_Evidence_Package_Cheaper_Proof_Runbook.md`, or any §11- / §13-signed spec.
- Change D10 criteria, the per-MSP "yes" definition, the count threshold, the privacy boundary, or the worksheet schema.
- Claim that D10 is complete, partially complete, met, cleared, or satisfied.
- Claim MSP discovery progress beyond what is recorded in `Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv`.
- Authorize implementation, runtime code, package generation, redaction logic, buyer-facing rendering, pricing, broker outreach, carrier outreach, or client-facing copy.
- Use forbidden claim language (`compliant`, `certified`, `insurer-approved`, `premium reducer`, `guarantee`, etc.) outside `Compliance_and_Trend_Watch_Process.md` §5.3 allowed contexts.
- Treat any internal score, matrix, or rubric as a decision.
- Substitute for the operator's authorship on the SPARK §3 protected sentence or the deep-dive protected sentence.

If any phrase in this synthesis conflicts with a §11- or §13-signed spec, the signed spec wins.

---

**End of v1 synthesis. Operator decides next action; this file logs what we know and what we do not know.**
