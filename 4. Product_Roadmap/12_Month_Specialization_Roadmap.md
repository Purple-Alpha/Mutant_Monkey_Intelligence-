# NorthStar 12-Month Specialization Roadmap
### Fraud Detection + Ransomware Defense — Month-by-Month Build & GTM Plan

## Purpose
This is the **operational unfold** of `Fraud_Ransomware_Specialization_Roadmap.md`. The strategic roadmap answered *which mountain are we climbing*; this doc answers *which step is taken in which month for the next twelve months*. It sequences the four phases (Foundation → Capability Expansion → Market Positioning → Monetization & Scale) onto a realistic timeline that accounts for:

1. **Existing assets.** Parts of Phase 1 already exist in code — the NorthStar Inbox Shield trio (record types, scoring agent, drafting agent), the sandbox loop, the mutation engine, the closed-loop signed-policy pipeline. The plan does not redo those.
2. **Solo-operator + AI-agent pacing.** One substantial build per month, two when the build is mostly content not code, with explicit slack for sales calls and partner work in Months 7+.
3. **Phase overlap.** Phases do not run sequentially in monthly resolution — Phase 2 product surfaces start before Phase 1 finishes, and Phase 3 positioning starts before Phase 2 reporting ships. The plan shows the overlap explicitly.
4. **Horizon 1 of the existing `4. Product_Roadmap/README.md`** — *"First paying client in 90 days"* — runs in parallel with the specialization phases and does not wait for them. The specialization deepens the *product*; client onboarding can land any time after Month 1's digest lockdown.

**Approved by:** Matt
**Approved on:** 2026-05-20
**Start month:** June 2026 (Month 1)
**End month:** May 2027 (Month 12)
**Status:** Active operational direction

---

## At a Glance — Monthly Theme + Gate

| Month | Theme | Gate (the one shippable artifact that marks the month "won") | Phase |
|---|---|---|---|
| 1. June 2026 | Daily Digest lockdown + attachment schema foundations | Digest E2E running unattended on a 5-email synthetic batch with fraud + ransomware framing visible | 1.1 / 1.2 prep |
| 2. July 2026 | Phase 1.1 — Fraud Detection Capabilities | Internal eval shows ≥80% precision on fraud-emails set, ≤10% false-positive rate on legit set | 1.1 |
| 3. August 2026 | Phase 1.2 — Ransomware Precursor Detection (attachments + URLs) | Synthetic ransomware-precursor email scored ≥85 risk_score with all four precursor sub-scores populated | 1.2 |
| 4. September 2026 | Phase 1.3 — Sandbox Training Pit (fraud Red agents) | Red × Blue battery produces weakness report with concrete failure modes per Red profile | 1.3 |
| 5. October 2026 | Phase 1.4 mutation engine specialization + Phase 2.1 product layer start | Mutation engine closes the loop on a vendor-fraud sensitivity boost (sandbox → sign → promote → apply → next-cycle effect) | 1.4 / 2.1 |
| 6. November 2026 | Phase 2.2 Ransomware Defense Product Sheet + Phase 2.3 Evidence & Reporting Layer | End-to-end fraud incident flows to an exportable insurance-ready evidence package with intact audit chain | 2.2 / 2.3 |
| 7. December 2026 | Phase 3.1 messaging + Phase 3.2 MSP bundles | A friendly MSP can explain what NorthStar does to a buyer in 90 seconds, from the bundle spec + pitch + product page | 3.1 / 3.2 |
| 8. January 2027 | Phase 3.3 compliance + insurance positioning | One signed pilot contract on file (Horizon 1 milestone — first paying client, latest acceptable month) | 3.3 |
| 9. February 2027 | Phase 4.1 pricing + Phase 4.2 reseller program v1 | First MSP reseller signed (or LOI on file) | 4.1 / 4.2 |
| 10. March 2027 | Phase 4.3 sales enablement | A second person (contractor, partner, or AI agent) can run a demo end-to-end without Matt in the room | 4.3 |
| 11. April 2027 | Phase 4.4 renewal + expansion motion | One renewal closed + one add-on sold to an existing client | 4.4 |
| 12. May 2027 | Horizon 1 → Horizon 3 bridge — Foundation for the 60-agent platform | Year-2 specialization direction approved; ≥10 active clients on the books; ≥3 MSP resellers active | Horizon 3 prep |

---

## Quarterly Checkpoints

- **End of Q1 (end of Month 3):** Phase 1.1 + 1.2 capabilities live in the runtime; fraud + ransomware precursor scoring producing structured output for real emails.
- **End of Q2 (end of Month 6):** Phase 1 complete; Phase 2 product layer + reporting shipped; the product is *demoable*.
- **End of Q3 (end of Month 9):** Phase 3 positioning + Phase 4.1–4.2 pricing/reseller live; first paying client + first MSP reseller closed.
- **End of Q4 (end of Month 12):** Full sales motion repeatable without Matt in every call; renewal + expansion mechanics proven; ≥10 active clients; Year-2 direction approved.

---

# Month-by-Month Detail

## Month 1 — June 2026
**Theme:** Daily Digest lockdown + attachment schema foundations.

**Why this month:** The Daily Digest system prompt has been the longest-standing open Inbox Shield item. Locking it through the specialization's messaging pillars makes the existing runtime tell the right story. In parallel, the attachment schema needs deepening *now* so Month 3's ransomware precursor work doesn't stall on input-shape blockers.

**Deliverables:**
- Daily Digest system prompt locked, anchored to the three messaging pillars in `Fraud_Ransomware_Specialization_Roadmap.md` §3.1 ("Fraud starts in the inbox." / "Ransomware starts with a click." / "We stop the attack before it becomes an incident.").
- Daily Digest agent wired into `ProductionLoopConfig.run_daily_digest_at_end_of_cycle` (default OFF, kill-switch-safe — the operator kill switch makes this safe to wire on).
- `EmailAttachmentMeta` extended with `content_type`, `size_bytes`, `sha256`, `extracted_text` (when safely extractable), and `attachment_class` (Literal: `invoice` / `payment_request` / `credential_lure` / `payload_carrier` / `executable_doc` / `unknown`).
- Phase 1.1 deep dive document drafted at `4. Product_Roadmap/Phase_1_1_Fraud_Prevention_Deep_Dive.md`.
- ≥5 new unit tests covering attachment schema validation and digest prompt anchoring.

**Gate:** Daily Digest E2E running unattended on a 5-email synthetic batch with fraud + ransomware framing visible in the digest output.

**Risk / dependency:** Matt needs to provide or approve the final digest prompt text. The placeholder has been blocking for weeks; if it slips again, Month 2 should still proceed.

**Parallel work:** Multi-tenant isolation Phase 2 (currently in flight) lands during this month and closes the cross-tenant governance gap before any second-tenant onboarding.

---

## Month 2 — July 2026
**Theme:** Phase 1.1 — Fraud Detection Capabilities.

**Why this month:** Half of §1.1 is already in the schema (`impersonation_analysis` block, `financial_risk` enum). The agent does not yet *score* fraud explicitly — it produces fields adjacent to fraud but doesn't anchor them in fraud-specialist language. Month 2 closes that gap and gets the first real eval numbers on the table.

**Deliverables:**
- Extend `EmailAnalysisRiskAnalysis` payload with: `vendor_fraud_score` (0–100), `wire_transfer_anomaly_score` (0–100), `invoice_authenticity_score` (0–100), `behavioral_deviation_flags` (list of strings from a controlled enum).
- Rewrite `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT` to instruct the LLM to score these dimensions explicitly, with worked examples for each. Lock the new prompt.
- Build a small internal eval harness: 20 real (or realistic) fraud emails from public datasets + 20 legit emails; baseline precision / recall on the new fraud scores.
- Activity log entry with the eval numbers (precision, recall, F1, false-positive rate per category).
- ≥8 new scoring tests covering the new dimensions on deterministic LLM fakes.

**Gate:** Eval shows **≥80% precision on the fraud-emails set with ≤10% false-positive rate** on the legit set. Document where it underperforms; capture as Q2 backlog.

**Risk / dependency:** Eval dataset must be assembled or sourced. If sourcing real fraud samples is slow, synthetic Red-agent generation can be brought forward from Month 4 to seed the eval set.

---

## Month 3 — August 2026
**Theme:** Phase 1.2 — Ransomware Precursor Detection (attachments + URLs).

**Why this month:** Largest single-month build in Q1. The current scoring agent reads `subject` and `body_text` only; ransomware precursor work requires attachment inspection + URL analysis as first-class inputs. This is where the specialization gains its sharpest technical edge over generic phishing tools.

**Deliverables:**
- New module `core/precursor/attachment_classifier.py` — sandbox-safe inspector producing `attachment_class`, `risk_indicators` (list), and `extracted_text` (when safe).
- New module `core/precursor/url_obfuscation_detector.py` — URL parser detecting homoglyphs, IDN tricks, URL shorteners, credential-bearing URLs, suspicious TLDs, and known phishing-kit patterns.
- Extend `EmailAnalysisPayload` with a new `ransomware_precursor_analysis` block: `attachment_risk_score` (0–100), `url_obfuscation_score` (0–100), `credential_harvesting_score` (0–100), `mfa_fatigue_score` (0–100), `precursor_indicators` (list of strings from a controlled enum).
- Update the scoring agent to consume the two new modules and emit the new block in `EmailAnalysisPayload`.
- Phase 1.2 deep dive document drafted at `4. Product_Roadmap/Phase_1_2_Ransomware_Precursor_Deep_Dive.md`.
- ≥15 new tests: attachment classifier (5+), URL obfuscation detector (5+), agent integration (5+).
- Q1 checkpoint document at `4. Product_Roadmap/Q1_Checkpoint_2026.md`.

**Gate:** A synthetic ransomware-precursor email (malicious attachment + obfuscated URL + credential lure) scored **≥85 risk_score** with all four precursor sub-scores populated, on a deterministic LLM client run reproducing across CI.

**Risk / dependency:** Attachment inspection has to stay sandbox-safe — under no circumstances does the inspector execute attachment content. Static analysis only. Document this explicitly in the deep-dive doc.

---

## Month 4 — September 2026
**Theme:** Phase 1.3 — Sandbox Training Pit (fraud-specialized Red agents).

**Why this month:** Phase 1.1 and 1.2 produced a scoring surface; Month 4 stress-tests it. The sandbox loop and the Red-vs-Blue evaluation framework already exist as infrastructure. What's new is *fraud-specialized adversarial generation*.

**Deliverables:**
- Four new Red agent profiles registered in the agent registry:
  - `fake_invoice_red_001`
  - `vendor_update_red_001`
  - `malicious_attachment_red_001`
  - `obfuscated_url_red_001`
- Synthetic-generation module emitting ≥100 unique adversarial cases per Red profile per run.
- Blue evaluation: the scoring agent (Phase 1.1) + precursor modules (Phase 1.2) run against every Red case; pass / fail / edge captured per case.
- Aggregate weakness reports per Red profile, written to the Blackboard as `WeaknessReport` records.
- ≥10 new tests covering Red agent registration, generation determinism, and weakness-report shape.

**Gate:** Red × Blue battery runs end-to-end producing a weakness report with **concrete, documented failure modes per Red profile** (not a flat aggregate — categorized).

**Risk / dependency:** Synthetic generation must avoid leaking into real customer data paths. Sandbox tenant isolation (already enforced by Multi-tenant isolation Phase 2) is the safety net here.

---

## Month 5 — October 2026
**Theme:** Phase 1.4 mutation engine specialization + Phase 2.1 product layer start.

**Why this month:** The mutation engine infrastructure exists. Month 5 specializes it with three fraud-specific mutation kinds and closes the loop on a real sensitivity adjustment. In parallel, Phase 2.1's first customer-facing artifact ships.

**Deliverables:**
- Three new mutation kinds in `core/mutation/engine.py`:
  - `fraud_pattern_threshold` (adjusts vendor / wire / invoice score thresholds)
  - `attachment_classifier_boost` (adjusts ransomware attachment sensitivity)
  - `url_obfuscation_sensitivity` (adjusts URL obfuscation threshold)
- Each mutation kind emits a signed `policy_update` carrying its parameter, applied through the Guardrail 11 gate (the cross-tenant binding from the multi-tenant Phase 2 work is already in force at this point).
- **Fraud Detection Product Sheet** drafted at `4. Product_Roadmap/Product_Sheets/Fraud_Detection_Product_Sheet.md` — one-page customer-facing artifact built from the Month 2 eval numbers.
- ≥8 new tests covering mutation kind validation, parameter signing, and closed-loop application.
- Optional: design spec for the Evidence & Reporting Layer (Phase 2.3); no code yet.

**Gate:** Mutation engine successfully boosts `vendor_fraud_score` sensitivity through the full closed loop — sandbox identifies a Red weakness, signs a mutation, promotion pipeline approves it, gate applies it, next production cycle uses the boosted threshold. Verified with a single deterministic test.

**Risk / dependency:** None unique to this month; the closed-loop pattern is already proven for generic policies, this just specializes the parameter dictionary.

---

## Month 6 — November 2026
**Theme:** Phase 2.2 Ransomware Defense Product Sheet + Phase 2.3 Evidence & Reporting Layer.

**Why this month:** Phase 2 customer surfaces complete; reporting starts. Phase 1 essentially done; Phase 2 dominates. The evidence chain that the SwarmCommand runtime maintains by construction (Blackboard records signed and chained) becomes a *commercial asset* this month.

**Deliverables:**
- **Ransomware Defense Product Sheet** drafted at `4. Product_Roadmap/Product_Sheets/Ransomware_Defense_Product_Sheet.md`.
- Evidence & Reporting Layer v1:
  - `core/reporting/incident_timeline.py` — builds an incident timeline from Blackboard records (EMAIL_INBOUND → EMAIL_ANALYSIS → DAILY_DIGEST chain → optional incident escalation).
  - `core/reporting/evidence_package.py` — exports a signed evidence package (JSON + accompanying PDF when a renderer is available) with the full audit chain.
  - `core/reporting/compliance_map.py` — maps agent outputs to SOC 2 CC7 controls and ISO 27001 A.13.2 controls; static mapping for now.
- Compliance mapping document drafted at `4. Product_Roadmap/Compliance_Mapping.md`.
- ≥10 new tests covering incident timeline construction, evidence package export, and compliance mapping completeness.
- Q2 checkpoint document at `4. Product_Roadmap/Q2_Checkpoint_2026.md`.

**Gate:** An end-to-end fraud incident (synthetic) flows from email ingest → analysis → digest → incident timeline → exportable evidence package with the **full audit chain intact and re-verifiable from the export alone**.

**Risk / dependency:** PDF rendering is optional this month — if it adds complexity, ship JSON only and queue PDF for Month 7. The audit-chain integrity is non-negotiable.

---

## Month 7 — December 2026
**Theme:** Phase 3.1 messaging + Phase 3.2 MSP bundles.

**Why this month:** Stop building, start positioning. The product is shippable; now make the story crisp. December's lower business-day count is good for writing work, less good for closing — so this month is content-heavy.

**Deliverables:**
- Positioning document at `6. Internal_Strategy/Positioning_Fraud_Ransomware.md` — formalizes the three messaging pillars into buyer-language with proof points pulled from the Month 2 + Month 6 eval and demo artifacts.
- Three MSP-Ready Bundle SKU specs:
  - `Bundles/Fraud_Defense_Add_On.md`
  - `Bundles/Ransomware_Prevention_Add_On.md`
  - `Bundles/Human_Layer_Security_Suite.md`
- One-page pitch deck per SKU (three decks total) under `1. Business_Operations/Sales_Materials/Pitch_Decks/`.
- **MSP Sales Pitch for Fraud + Ransomware** drafted at `1. Business_Operations/Sales_Materials/MSP_Sales_Pitch.md`.
- One product-page draft for the NorthStar website at `1. Business_Operations/Website_Copy/Product_Page_Inbox_Shield.md`.

**Gate:** A friendly MSP partner reads the pitch + bundle spec + product-page draft and can explain what NorthStar does to a buyer **in 90 seconds**, in their own words.

**Risk / dependency:** The 90-second test requires an actual friendly MSP partner. Identify one in Month 6 so the asset is ready to be tested when it ships.

---

## Month 8 — January 2027
**Theme:** Phase 3.3 compliance + insurance positioning. **First paying client (latest acceptable month).**

**Why this month:** Insurance-flavored credibility is the procurement lever for the SMB and MSP buyer. Tying the technical evidence chain (Phase 2.3) to procurement-ready compliance positioning is what turns a demo into a signed contract. Month 8 is the *latest acceptable month* for the first paying client — Horizon 1 of the existing `4. Product_Roadmap/README.md` targets 90 days, which puts the early-paying-client target in Q1. Most ventures slip; Month 8 is the explicit floor.

**Deliverables:**
- Compliance positioning document at `4. Product_Roadmap/Compliance_Positioning.md` — explicit mapping of the audit chain to:
  - Cyber insurance application questions (top 20 questions from major insurers)
  - SOC 2 CC7 human-layer controls
  - ISO 27001 A.13.2 controls
- Insurance-ready evidence package template (PDF + signed JSON), reviewed by an actual insurance broker contact if reachable.
- Two letters of validation (LoV) requested from insurance broker / CISO contacts — optional but high-leverage.
- **First paying client onboarded** — even at a discounted pilot rate. The signed contract is the unlock.

**Gate:** **One signed pilot contract on file.**

**Risk / dependency:** This is the hardest gate of the year. If Matt is not running active outreach in Months 5–7, the Month 8 client-signing target is unreachable. Build outreach motion in parallel from Month 5 onward, regardless of which phase deliverables dominate the build calendar.

---

## Month 9 — February 2027
**Theme:** Phase 4.1 pricing + Phase 4.2 reseller program v1.

**Why this month:** Make the business model real. Pricing tiers locked; reseller program structure published. With one paying client signed (Month 8), the pricing is now empirically grounded, not theoretical.

**Deliverables:**
- **NorthStar Pricing Sheet** drafted at `1. Business_Operations/Sales_Materials/NorthStar_Pricing_Sheet.md` — three tiers from the strategic roadmap ($3–5 / $3–5 / $7–10 per user / month) with explicit volume discounts and annual-vs-monthly pricing.
- Wholesale pricing structure for MSPs (margins documented; suggested 30–40% standard, 40–50% with volume commitment).
- White-label options spec at `NorthStar Certification + Licensing + Partner Ecosystem/White_Label_Options.md` — what's customizable (logo, color, report header), what isn't (the engine, the audit chain, the messaging pillars).
- Co-branded report templates (2–3 variants) under `NorthStar Certification + Licensing + Partner Ecosystem/Report_Templates/`.
- Partner portal v1 specification at `NorthStar Certification + Licensing + Partner Ecosystem/Partner_Portal_Spec.md` — Notion page or real portal, decided based on confirmed partner count.
- Q3 checkpoint document at `4. Product_Roadmap/Q3_Checkpoint_2027.md`.

**Gate:** **First MSP reseller signed** (or LOI on file with mutual commitment to a paper signature in Month 10).

**Risk / dependency:** Reseller acquisition is a separate motion from end-buyer acquisition. The 90-second-pitch test from Month 7 should already have produced 1–2 warm MSP relationships; Month 9 converts the warmest one.

---

## Month 10 — March 2027
**Theme:** Phase 4.3 sales enablement.

**Why this month:** Make the sales motion repeatable so it doesn't depend on Matt being in every call. With one paying client and one reseller, the question stops being *can we sell?* and becomes *can we sell at scale?*

**Deliverables:**
- **NorthStar MSP Sales Deck** drafted at `1. Business_Operations/Sales_Materials/NorthStar_MSP_Sales_Deck.md` — the full deck, not the one-pagers.
- Demo scripts (three scenarios) under `1. Business_Operations/Sales_Materials/Demo_Scripts/`:
  - Vendor fraud demo
  - Wire transfer fraud demo
  - Ransomware precursor demo
- Objection handling document at `1. Business_Operations/Sales_Materials/Objection_Handling.md` — top 15 objections with crisp answers.
- Final-version one-page product sheets (sales-team-ready, polished pass) replacing the Month 5 + Month 6 drafts.
- Sales CRM workflow + lead-to-close playbook at `1. Business_Operations/Sales_Materials/Sales_Playbook.md`.

**Gate:** A second person (contractor, partner MSP, or AI agent) can **run a full demo end-to-end without Matt in the room**, from cold open to ask-for-the-pilot.

**Risk / dependency:** Identify the "second person" candidate in Month 9 so Month 10's gate has a real human to test against.

---

## Month 11 — April 2027
**Theme:** Phase 4.4 renewal + expansion motion.

**Why this month:** Make existing clients more valuable. Renewal mechanics + expansion upsells. With Month 8's first pilot now ~120 days into the relationship and the pricing surface from Month 9 in place, Month 11 is the natural moment to formalize the recurring + expansion motion.

**Deliverables:**
- Quarterly Fraud Risk Review (QFRR) template + delivery workflow at `2. Delivery_Engine/Quarterly_Fraud_Risk_Review_Template.md`.
- Annual Ransomware Readiness Assessment template at `2. Delivery_Engine/Annual_Ransomware_Readiness_Assessment_Template.md`.
- Add-on upsell catalog at `1. Business_Operations/Sales_Materials/Add_On_Catalog.md`:
  - Tabletop Exercise (existing offering)
  - Threat Briefing (existing offering)
  - AI Policy Drafting (existing offering)
  - Quarterly Fraud Risk Review (new)
  - Annual Ransomware Readiness Assessment (new)
- **First renewal closed** (Horizon 2 milestone from existing README — Month 4–12, on target).
- **First add-on sold to an existing client** (Horizon 2 milestone — Tabletop, Threat Briefing, AI Policy, or one of the new SKUs).

**Gate:** **One renewal closed + one add-on sold.**

**Risk / dependency:** Renewal probability is highly dependent on Month 8's client experience. Active QFRR delivery in Months 9, 10, 11 to the original pilot client is the leading indicator that the renewal will close.

---

## Month 12 — May 2027
**Theme:** Horizon 1 → Horizon 3 bridge — Foundation for the 60-Agent Platform.

**Why this month:** Close the 12-month sprint with the foundation for the next horizon. The specialization is alive in market; now plant the seeds for productizing the engine. This month's deliverables map directly to the three Horizon-3 TODOs in `4. Product_Roadmap/README.md`.

**Deliverables:**
- Agent inventory drafted at `4. Product_Roadmap/60_Agent_Platform_Vision.md` — ≤60 agents grouped by function, using the fraud + ransomware specialization as the seed grouping.
- Platform Architecture v1 diagram at `4. Product_Roadmap/Architecture_Diagrams/Platform_Architecture_v1.md` — finally closing one of the original Horizon-3 TODOs from the folder's README.
- Promotion path documented: `SwarmCommand_Engine/Experiments` → `Future_Platform_Agents` → platform — under `4. Product_Roadmap/Agent_Promotion_Path.md`.
- Multi-tenant data model sketched (the cross-tenant work from this conversation's earlier Phase 2 mission generalizes naturally here) at `4. Product_Roadmap/Multi_Tenant_Data_Model.md`.
- Year-1 retrospective at `4. Product_Roadmap/Year_1_Retrospective_2026_2027.md` — what shipped, what missed, what was learned.
- Year-2 specialization roadmap drafted at `4. Product_Roadmap/Year_2_Specialization_Roadmap_2027_2028.md` — next-12-month direction approved.

**Gate:** **Year-2 specialization direction approved by Matt; ≥10 active clients on the books; ≥3 MSP resellers active; ≥1 renewal closed; ≥1 add-on sold.**

**Risk / dependency:** The active-client and reseller counts depend on Months 8–11 execution. If those months slip, the Year-1 retrospective should be honest about it and Year-2 should adjust accordingly rather than papering over the gap.

---

## Assumptions and Risks

### Hard assumptions
- **Solo operator + AI agents** (Matt + Cursor + Codex). No additional engineering headcount in Year 1. Plan rebalances if a contractor or co-founder joins.
- **Single canonical LLM provider** for the scoring + drafting agents. Switching providers in-year is possible but assumed to be Year 2 work, not Year 1.
- **Canadian hosting for production data.** No US data-residency exception in Year 1.
- **No regulated-industry rollout in Year 1.** SMBs and MSPs only; no public-sector, no healthcare, no banking-prime. Those tiers come in Year 2+.

### Highest-impact risks
1. **First paying client slips past Month 8.** If Months 5–7 do not run a parallel outreach motion, Month 8's gate is unreachable. Mitigation: schedule outreach work explicitly from Month 5 onward, treat the build calendar and the sales calendar as independent threads.
2. **LLM eval performance falls short of the Month 2 gate.** If precision is <80% or false-positive rate is >10%, the specialization story weakens. Mitigation: budget a Month 2.5 / Month 3 prompt-engineering loop; if needed, push Phase 1.2 (Month 3) by two weeks.
3. **Insurance broker validation does not materialize by Month 8.** Mitigation: insurance positioning can ship without external LoVs; the audit-chain story is strong enough on its own to anchor procurement conversations.
4. **MSP partner relationships do not convert by Month 9.** Mitigation: direct-to-SMB sales remains a viable second channel; reseller program can slip to Q3 Year 2 without breaking the rest of the plan.

### Soft assumptions worth surfacing
- The strategic specialization (fraud + ransomware) holds for the full 12 months. If a major market signal emerges that the wedge should be narrower (e.g., "wire transfer fraud only" or "MSP-only") or broader (e.g., "AI-era social engineering"), the Year-1 retrospective in Month 12 should re-test the wedge before committing Year 2.
- The existing handshake + activity log + guardrails workflow scales to a 12-month build cadence without restructuring. If those tracking surfaces become noisy at high write volume, that's a Year-2 problem.

---

## How This Document Stays Current

- **Monthly bump:** at the end of each month, update the row in the "At a Glance" table with the gate outcome (`HIT` / `MISS` / `PARTIAL`) and link the gate's deliverable.
- **Quarterly checkpoint files:** four explicit checkpoint files (`Q1_Checkpoint_2026.md`, `Q2_Checkpoint_2026.md`, `Q3_Checkpoint_2027.md`, `Q4` rolls into the Year-1 retrospective in Month 12).
- **Drift control:** if the actual calendar slips a month behind the plan by the end of Q1, **adjust the plan in writing** rather than pretending the slip didn't happen. The plan exists to be useful, not to be right.
- **Cross-reference with the handshake:** `PROJECT_HANDSHAKE.md` remains the always-on "where are we right now" surface; this document is the always-on "where are we going next" surface. They reference each other; neither replaces the other.

---

## Cross-references

- `4. Product_Roadmap/Fraud_Ransomware_Specialization_Roadmap.md` — strategic specialization this roadmap operationalizes.
- `4. Product_Roadmap/12_Week_Timeline.md` — tactical week-by-week build sequence (Months 1–3 of this plan unfold further into weeks there).
- `4. Product_Roadmap/README.md` — three-horizon framing this roadmap rides on top of (Horizon 1: paying clients; Horizon 2: scale + product loops; Horizon 3: 60-agent platform).
- `PROJECT_HANDSHAKE.md` — the always-current build state.
- `PROJECT_ACTIVITY_LOG.md` — the always-current change log; each month's gate should produce one entry here.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/` — the runtime that hosts the Phase 1 capability builds.
- `1. Business_Operations/` — where Months 7–11 sales artifacts live.
- `2. Delivery_Engine/` — where Months 11–12 delivery templates live.
- `6. Internal_Strategy/` — where positioning + competitive context live.
- `NorthStar Certification + Licensing + Partner Ecosystem/` — where Month 9's reseller assets live.

---

## Last Updated
2026-05-20
