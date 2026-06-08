# Think Sheet

**Purpose:** A scoring sheet that sits *in front of* the active project plan. When an idea comes up, it gets scored here first to decide whether it's worth pursuing, parking, or dropping. This sheet is not part of the project plan — it's the filter that protects the plan from drift.

**Operating rule:** Ideas are scored here. They do not enter the active project plan (`PROGRESS.md`) without passing the scoring rubric **and** the stress-test gate.

**Last reviewed:** 2026-06-08

---

## Scoring Rubric

Each idea gets scored on five axes, 0–2 per axis, max total of 10. Higher score = stronger candidate for promotion.

| Axis | 0 | 1 | 2 |
|---|---|---|---|
| **Strategic Fit** | Unrelated to the current build arc | Adjacent / mission-aligned but indirect | Directly advances the current build arc |
| **Revenue Path** | No path to money visible | Supports revenue indirectly (better demo, lower churn, stronger proposal, unlocks downstream paid deliverables) | Direct paid deliverable possible within 90 days |
| **Foundation Fit** | Cheap hack — would compromise the architecture, introduce technical debt, or require a workaround later | Acceptable — fits the existing architecture but does not strengthen it | Clean fit — raises the quality floor, strengthens the foundation, removes a future risk |
| **Provability** | Invisible to a non-technical buyer | Produces logs or numbers only an engineer can read | Produces a client-facing artifact (report row, flagged email, dashboard line, signed audit entry) |
| **Anti-Drift (low drift = better)** | New product, new audience, new stack | Feature add that needs research time | Feature in scope, fits the active arc |

### Band thresholds

- **8–10 → `promote`** — candidate to graduate. Requires the stress-test gate before moving out of the sheet.
- **5–7 → `live park`** — keep in the sheet, review monthly. Solid idea, wrong moment.
- **2–4 → `deep park`** — quarterly review only. Don't re-debate every month.
- **0–1 → `retire`** — candidate to remove after one more review cycle.

### Score notation

Scores are written in the table as `F·R·Q·P·D = total` where the five letters map to the axis order: **F**it, **R**evenue, **Q**uality (Foundation Fit), **P**rovability, **D**rift. Example: `2·2·2·2·2 = 10`.

### Rubric history note

The **Foundation Fit** axis replaced an earlier "Build Cost (cheaper = better)" axis on 2026-05-23 after the operator's "I don't build cheap" position. Build-time cost is no longer a scoring axis — speed is captured indirectly via Anti-Drift and via the Stress-Test Gate's hidden-cost question. Rows dated **2026-05-22** and **2026-05-23** below were scored before the rubric change; their third-axis score reflects the prior Build Cost rubric and will be re-scored on the next monthly review unless already shipped.

### Known limitation

A genuinely long-arc / category-defining idea can still score low here because **Revenue Path** penalizes ideas that don't produce a paid deliverable within 90 days. If you suspect an idea is in that category, flag it `moonshot` in the Notes column and review it on a separate quarterly cadence regardless of total.

---

## Stress-Test Gate

Before any idea graduates from this sheet into committed work in `PROGRESS.md`, answer all seven questions below in the **Stress-Test Answers** section. If any answer is "I don't know" or "we'll figure it out later", the idea stays parked with the unanswered question captured in the notes column.

1. **Failure mode** — If this ships and breaks, what does the failure look like to the client?
2. **Hidden cost** — Maintenance, support burden, monthly infrastructure, new external dependency you'll have to update forever.
3. **Specific buyer** — Name a real archetype buyer (e.g., "Kelowna MSP with 5–15 SMB clients") and the dollar number you'd expect from them.
4. **Cost of inaction** — What does NOT having this cost us? Who walks away?
5. **Cheaper proof first** — Can we validate the assumption with zero code (a spreadsheet, a sample email, a customer conversation)?
6. **Existing competitor** — Closest existing competitor. Are we re-inventing something Mimecast / Proofpoint / Avanan / Microsoft Defender already sells?
7. **Pre-mortem** — Write the failure obituary now, in one sentence: "This will have failed because ______."

---

## Idea Table

| Date | Idea | Scope | Score | Band | ST | Notes |
|---|---|---|---|---|---|---|
| 2026-06-08 | **Swarm Oversight Pipeline (Dax-first; officer names deferred)** | governance/process | 2·1·2·1·1 = 7 | live park | n/a | Four-review merge found the destination is right but the timing is early. Do **not** build a five-seat "board" now. Park the control-plane version: Dax-first artifact-cited reports, behavior baselines, drift thresholds, escalation triggers, and an override/decision log that records Matt's prior inclination before reading the report. Names/personas stay thin and last, if used at all. Unblock trigger: real-data intake opens, first agent reaches Evidence Stage 2, or there is enough real override/miss data for the oversight loop to measure whether it changes decisions. Trend Watch / Pointdexter feeds the Build Sequencer as an input, not a board seat. |
| 2026-05-22 | AI market-pusher / project-to-buyer lead miner | adjacent-venture | 1·1·0·0·0 = 2 | deep park | n/a | Agent that finds companies likely to need a finished project and routes outreach. Overlaps with original agentic bidding idea. Parked until revenue path is proven. |
| 2026-05-22 | Iron Grid sponsor-token layer | adjacent-venture | 0·1·0·1·0 = 2 | deep park | n/a | Utility-only fan sponsorship tokens, not betting/payouts. Needs legal/payment review before any launch. |
| 2026-05-22 | Social Architect BC youth-resource ecosystem | adjacent-venture (mission) | 2·0·0·1·0 = 3 | deep park | n/a | Mission project connected to Freedom's Door; long-term priority funded by future revenue. |
| 2026-05-23 | Sender-provenance / geo-velocity detector ("blackbox" for sender origin) — flag when a known vendor's mail suddenly arrives from a new country or ASN | feature-idea | 2·2·1·2·2 = 9 | promote | Y | Matt's own idea. Pure-function deterministic detector, plugs into existing `recommended_risk_floor` overlay. Strongest single defense against Business Email Compromise (BEC). See stress-test answers below. |
| 2026-05-23 | From/Reply-To/Return-Path divergence detector | feature-idea | 2·1·2·2·2 = 9 | ✅ shipped | n/a | Graduated to `PROGRESS.md` Task 15 on 2026-05-23. +24 tests → 534. |
| 2026-05-23 | Ghost-thread validation (`Re:` / `Fwd:` without `In-Reply-To` or `References`) | feature-idea | 2·1·2·2·2 = 9 | ✅ shipped | n/a | Graduated to `PROGRESS.md` Task 16 on 2026-05-23. +21 tests → 555. |
| 2026-05-23 | Adversarial prompt-injection detector (white-on-white text, `[SYSTEM_INSTRUCTION]`, `### Instruction:` delimiters in inbound body) | feature-idea | 2·1·2·2·2 = 9 | promote | Y | Defends downstream LLM scoring layer. See stress-test answers below. |
| 2026-05-23 | Consolidated tampering drill suite (single test file pulling existing tampering coverage into one insurer-presentable surface) | feature-idea | 2·1·2·2·2 = 9 | promote | Y | Mostly existing coverage + consolidation. See stress-test answers below. |
| 2026-05-23 | Schema-fuzzing test on `EmailInboundPayload` (1000 random keys → `ValidationError`) | feature-idea (test infra) | 2·0·2·1·2 = 7 | live park | n/a | No direct revenue surface, strong hardening. Build alongside the divergence detector when convenient. |
| 2026-05-23 | Blackboard hash-chain integrity (`blackboard_integrity_v1`) — Merkle-style hash chain over JSONL events | feature-idea | 2·1·1·1·1 = 6 | live park | n/a | Strong audit story, but needs design work and adds verification cost on every cycle. Review next month. |
| 2026-05-23 | Lift-only invariant property test for `recommended_risk_floor` (prove overlay can never lower an LLM risk score) | feature-idea (test infra) | 2·1·2·1·2 = 8 | ✅ shipped | n/a | Graduated to `PROGRESS.md` Task 14 on 2026-05-23. +11 tests → 510. |
| 2026-05-23 | URL reputation connector (URLhaus, Phishtank) | feature-idea | 2·1·0·2·1 = 6 | live park | n/a | Needs threat-intel connector built first. Pattern is the CISA KEV v0 ingestion. |
| 2026-05-23 | SHA256 malware feed connector (MalwareBazaar / abuse.ch) | feature-idea | 2·1·0·2·1 = 6 | live park | n/a | Same dependency as URL reputation connector. |
| 2026-05-23 | Daily-digest demo packaged as a paid $300 case-study deliverable | process-idea (GTM) | 2·2·2·2·2 = 10 | promote | Y | Demo already exists. Wrap into a one-shot service offering. See stress-test answers below. |
| 2026-05-23 | **Vendor Baseline Store primitive** — per-tenant, hash-only, TTL-bounded historical signal store; foundation for the next five deterministic detectors (Financial State Ledger, Doc Metadata Fingerprinting, Micro-Temporal Mismatches, Sender Provenance/Geo, Historical Relationship Density) | foundational-primitive | 2·1·2·1·2 = 8 | ✅ shipped | n/a | Graduated to `PROGRESS.md` Task 23 on 2026-05-24. §5 API implemented under `core/production_state/vendor_baseline/`; §7 gate covered by 32 new tests (+32 → 587). |
| 2026-05-23 | **Financial State Ledger / Delta Tripwire** — flags any net-new routing number, SWIFT code, IBAN, account number, or payment-portal URL observed from a vendor; mandatory out-of-band human verification on hit | feature-idea (BEC) | 2·2·2·2·2 = 10 | ✅ shipped | n/a | Graduated to `PROGRESS.md` Task 26 on 2026-05-24. Implemented at `core/scoring/financial_state_ledger.py` against the §11-signed spec, with Vendor Baseline Store check-before-ingest, redacted/hash-only findings, risk floor 85 for `new` / `expired`, and mandatory out-of-band verification wording. §7 gate covered by 29 new tests (+29 → 621). Independent Grok audit returned **approve** with no divergence, coverage gaps, or boundary risks. |
| 2026-05-23 | **Document Metadata Fingerprinting** — reads PDF Producer / Creator / Author / CreationDate fields and flags structural anomalies against the vendor's historical invoice-tool baseline (e.g. QuickBooks Commercial → Acrobat Web mismatch) | feature-idea (BEC) | 2·2·2·2·2 = 10 | promote | Y | Scored under new Foundation Fit rubric. Strong client-facing artifact. Gated on Vendor Baseline Store. See stress-test answers below. |
| 2026-05-23 | **Structural Payload Anomalies (OCR / encoding evasion)** — flags image-only invoices when vendor history is text-encoded, invisible white-on-white text overlays, transparent hyperlink overlays routing to attacker domains | feature-idea (evasion) | 2·2·2·2·2 = 10 | promote | Y | Scored under new Foundation Fit rubric. Independent of Vendor Baseline Store — can ship in parallel. See stress-test answers below. |
| 2026-05-23 | **Micro-Temporal Mismatches** — compares PDF document creation timestamp + transmission delta against the vendor's historical send-time-window pattern; flags timezone-mismatch artifacts of attackers in different zones | feature-idea (BEC) | 2·1·2·1·2 = 8 | promote | Y | Scored under new Foundation Fit rubric. Subtle signal — provability is engineer-only without rendering work. Gated on Vendor Baseline Store. See stress-test answers below. |
| 2026-05-23 | **DKIM / SPF / DMARC ingestion** — deterministic overlay reading authentication-result headers; lifts `recommended_risk_floor` on `dkim=fail` / `spf=softfail` / `dmarc=fail` from a domain previously seen passing | feature-idea (email-auth) | 2·1·2·1·2 = 8 | promote | Y | Scored under new Foundation Fit rubric. Table-stakes email-auth coverage; closes the gap identified in the 2026-05-23 system audit. Independent of Vendor Baseline Store. See stress-test answers below. |
| 2026-05-23 | **Callback Phishing / TOAD detection layer** — detects emails that move the fraud off-channel by telling the victim to call a provided number; combines callback-language detection, phone-number baselining, and "do not call the number in this email" audit guidance | feature-idea (BEC / vishing) | 2·2·2·2·2 = 10 | promote — **Part 1 body-language spec DRAFT 2026-05-25** at `4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md` (pre-§11; §10 sub-questions Q1–Q5 require stress test before signature) | Y | Captures Matt's adversarial insight: if the attacker knows email controls exist, they may put a phone number in the email and complete the fraud by voice. Clean fit with Vendor Baseline Store if `phone_number` becomes a future closed enum entry; requires spec revision before implementation. Part 1 (body-language) ships independently of Vendor Baseline Store; Part 2 (phone-number baselining) remains gated on the Vendor Baseline Store enum revision. See stress-test answers below + the spec draft §10 sub-questions. |
| 2026-05-23 | **Two-channel confirmation enforcement** — when a payment-change or high-risk vendor-fraud signal fires, require out-of-band verification against a previously-known vendor channel and record whether the operator confirmed it before money moves | workflow-idea (BEC control) | 2·2·2·2·2 = 10 | promote | Y | Stage A-sized workflow/audit layer. Strengthens the current daily-digest/reporting path without requiring a SaaS portal. Gives NorthStar a clear defense against callback phishing and payment-change fraud: software flags, process verifies, audit trail proves whether the process was followed. See stress-test answers below. |
| 2026-05-23 | **High-trust vendor verification layer** — umbrella strategy for selective financial-change verification using two-channel confirmation now, optional per-vendor challenge/response later, and a NorthStar Portal once Stage A revenue proves demand | strategic-idea (BEC control) | 2·2·2·2·2 = 10 | promote | Y | Captures the "encrypted keys / financial-only high-trust flow" discussion without committing to S/MIME/PGP. Core insight: crypto alone does not solve account-takeover BEC; the durable control is a second channel the attacker does not control. See stress-test answers below. |
| 2026-05-23 | **NorthStar Portal** — Stage B high-trust payment-change surface and brand layer; vendors update sensitive payment/contact data through a controlled NorthStar workflow instead of relying on email alone | product-surface (Stage B / moonshot) | 2·2·2·1·1 = 8 | promote / moonshot | Y | Strong brand + trust layer, but heavier than Stage A: authentication, MFA, vendor onboarding, uptime, tenant isolation, and UX become real product obligations. Keep promoted but gated on Stage A evidence, paid pilots, and a proper portal spec. See stress-test answers below. |
| 2026-05-23 | **Client-facing 5-axis Email Scoring Rubric** — external email-risk score modeled after the think sheet: five 0-2 axes that explain WHY an email was flagged, while the internal 0-100 runtime score remains available for routing | feature-idea (client UX / reporting) | 2·2·2·2·2 = 10 | promote | Y | Captures Matt's idea to make email risk scoring as legible as the rubric. Candidate axes: Sender Identity, Conversation Continuity, Vendor Payment History, Document Integrity, Origin / Timing. Requires a spec so axis definitions do not drift once clients learn them. See stress-test answers below. |
| 2026-05-23 | **NorthStar's 5 W's discovery framework** — informational-interview framework for MSP/customer research: what email security they use, whether vendor fraud is painful, whether they understand the gap, whether they would test a report/pilot, and what pricing feels fair | process-idea (customer development) | 2·2·2·2·2 = 10 | promote | n/a | Monday outreach/research frame, not a build item. Purpose is to learn before selling, collect real pain language, and create a foundation for pricing and product positioning. |
| 2026-05-23 | **Fair-access SMB pricing strategy** — pricing principle that NorthStar should be accessible to working-class small businesses without becoming a cheap or weak product | strategy-idea (pricing) | 2·2·2·1·2 = 9 | promote | n/a | Captures Matt's value position: strong security for businesses too small for enterprise pricing, with sustainable pricing that protects both the client and NorthStar's ability to keep operating. Use discovery calls to learn the real acceptable range before locking pricing. |
| 2026-05-24 | **Visible Multi-Agent Deliberation Layer** — make the swarm show its security reasoning the same way a strong assistant debates, corrects assumptions, and then gives a clean answer: multiple lenses assess an ambiguous email, disagreement is resolved, and the client sees the final plain-English reason | feature-idea (trust / scoring UX) | 2·2·2·2·2 = 10 | promote | Y | Captures Matt's "answer questions the way you reason" insight. Value is not just better detection; it creates a visible audit trail, catches blind spots, and turns each miss into a sharper Red/Blue learning signal. SMB sizing anchor: design for 50-100 employee SMBs, ~10 clients per MSP, ~75 employee average, with ~75-600 ambiguous emails/day/client needing richer deliberation, not enterprise-scale Ledcor-sized volumes. See stress-test answers below. |
| 2026-05-24 | **Tiered Detection Intensity (Low / Medium / High) aligned to sales tiers** — tenant-selectable security intensity that controls routine-mail scrutiny while auto-escalating risky emails; commercial alignment follows Option C: Essentials defaults Low, Plus defaults Medium, Enterprise defaults High, with add-ons separate | feature-idea (tenant policy / GTM alignment) | 2·2·2·2·2 = 10 | promote — **§11 SIGNED + implementation landed + Grok-approved 2026-05-24** (spec at `4. Product_Roadmap/Tiered_Detection_Intensity_Deep_Dive.md`; runtime at `core/operator_state/security_profile.py`; 658 passed, 1 skipped; Grok verdict approve) | Y | Low = LLM single-pass + cheap deterministic overlays + audit/digest; Medium = default SMB posture with full Vendor Baseline reads, Financial State Ledger, PDF metadata, micro-temporal, and callback/TOAD scan; High = full deliberation, judge pass, devil's-advocate on flagged mail, skeptic pass on clean mail, structural payload/OCR checks, and visible reasoning trace. Critical rule: tier is a floor for routine mail, not a ceiling for risky mail; financial deltas, combined BEC signals, prior vendor fraud, high-value invoices, fresh baselines, or manual escalation force High on that email. v1 spec lives at `core/operator_state/security_profile.py`; per-tenant state at `blackboard_root/operator_state/security_profiles/<tenant>.json`. v1 forced-escalation closed enum has four triggers (LLM ≥ 80, header divergence ≥ 80, ghost thread > 0, manual operator escalation); five other triggers (financial_state_delta, high_value_invoice, prior_vendor_fraud_flag, fresh_baseline_vendor, combined_bec_signals) are explicit v2 deferrals. See stress-test answers below. |
| 2026-05-24 | **Independent Grok code-auditor runner** — local xAI/Grok audit script that reads signed spec + implementation + tests + receipt, returns spec divergence / coverage gaps / security risks / verdict, and blocks "done" claims when verdict is not approve or approve-with-notes | process-idea (quality gate) | 2·1·2·2·2 = 9 | promote | N | Prototype landed as `audit_tools/grok_audit_runner.py` during the Vendor Baseline audit cycle and produced real fixes before final `approve with notes`. Needs stress-test before becoming a formal always-on build gate: data-egress boundary, prompt/version locking, report retention, and when to override noisy findings. |
| 2026-05-24 | **Independent decision-auditor lane** — second-model audit for build-order recommendations, spec-lock decisions, and "gold-plating vs necessary quality" calls so the primary assistant's advice can be challenged before it shapes the project path | process-idea (anti-drift governance) | 2·1·2·2·2 = 9 | promote — **§11 SIGNED + implementation landed + first self-audit `proceed` 2026-05-24** (spec at `4. Product_Roadmap/Independent_Decision_Auditor_Deep_Dive.md`; runtime at `audit_tools/decision_audit_runner.py`; 688 passed, 1 skipped) | N | Captures Matt's concern that assistant recommendations can quietly steer choices before drift is visible. Input: one operator-reviewed Markdown packet with decision, recommendation, rationale, alternatives, current state, and constraints. Output: six-section decision-quality report with closed verdict: `proceed`, `proceed_with_notes`, `revise_before_proceeding`, `defer`, or `operator_decision_required`. v1 runner validates packet shape, blocks known secret markers and obvious raw financial strings before network calls, writes reports under `audit_outputs/decision_audits/`, and fail-closes on blocking verdicts unless `--report-only` is explicit. First packet `decision_audit_inputs/20260524_1741_decision_auditor_next.md` returned `proceed`. |
| 2026-05-25 | **NorthStar "Analyst Brain" / AGI-style reasoning layer (research-paste, bundle)** — bundle of (a) higher-level analyst reasoning layer above existing detectors, (b) cross-domain expansion to logs / endpoints / payments, (c) auto-tuning detector ring / self-improving feedback loop, (d) "AGI-style behavior principles" appended to the (deferred) NorthStar Bible | bundle-idea (scope + governance + autonomy) | 1·1·0·1·0 = 3 | drop / reshape — superseded by component decomposition below | Y | Surfaced from operator research material on 2026-05-25. Bundle score reflects the package as written. On operator request 2026-05-25, the bundle was decomposed into six discrete candidate ideas (rows A–F immediately below) and each component was scored + stress-tested independently. The component verdicts replace the bundle verdict for ongoing reference. See stress-test answers and component decomposition section below. |
| 2026-05-25 | **(Component A) NorthStar Analyst Reasoning Layer (cross-detector synthesis, email-only)** — higher-level reasoning module above existing detectors that synthesizes findings into analyst-grade evidence summaries (per-email cross-detector and per-tenant cross-email), producing artifacts richer than the §11-signed 5-axis rubric while staying inside Stage A scope (email-only) | feature-idea (analyst layer / Stage A→B explainability) | 2·2·2·2·1 = 9 | promote | Y | Decomposed component of the 2026-05-25 AGI-Adjacent bundle. Real signal preserved. The §11-signed 5-axis rubric is the per-email instance of this layer; cross-email / cross-detector synthesis remains future work. Build only after the rubric ships and produces evidence about MSP appetite for cross-email synthesis. Needs spec-first deep dive before implementation. See stress-test answers below. |
| 2026-05-25 | **(Component B) Cross-Domain Expansion (logs / endpoints / payments coverage)** — extends NorthStar from email-only to multi-source analysis | scope-expansion-idea (Stage B/C) | 0·1·0·1·0 = 2 | drop | Y | Decomposed component of the 2026-05-25 AGI-Adjacent bundle. Out of Stage A scope per `VISION.md` and 2026-05-25 strategic clarity. Different company shape, different sales motion, different infrastructure surface. Re-evaluate only at a Stage A → Stage B transition decision gated on Stage A revenue + customer trust + proven inbox-layer wedge. See stress-test answers below. |
| 2026-05-25 | **(Component C) Auto-Tuning Detector Ring** — autonomous retraining of detector thresholds / rules / signatures when performance drifts | scope-expansion-idea (Stage C autonomy) | 0·0·0·0·0 = 0 | drop | Y | Decomposed component of the 2026-05-25 AGI-Adjacent bundle. Stage A discipline forbids autonomous tuning per `VISION.md`. Aligns with the existing Stage C "self-evolving defense swarm" milestone, not a near-term lane. See stress-test answers below. |
| 2026-05-25 | **(Component D) Operator-Approved Drift Tuning Surface** — deterministic drift detection that surfaces threshold-update candidates to the operator for explicit human approval (reframe of auto-tuning that preserves determinism + reversibility + auditability) | feature-idea (quality lane) | 1·1·1·1·1 = 5 | revisit | Y | Decomposed component of the 2026-05-25 AGI-Adjacent bundle. Reframes the auto-tuning component into a Stage A-compatible shape: surfacing, not retraining. Borderline; live-park until first paid pilot generates real tenant traffic, then re-score against real evidence about whether detectors drift in production. See stress-test answers below. |
| 2026-05-25 | **(Component E) Threat-Family Hypothesis Engine** — agent that clusters cross-email anomalies and proposes new threat-family hypotheses with evidence chains for human review | feature-idea (Stage B/C threat evolution) | 1·1·1·1·0 = 4 | live park | Y | Decomposed component of the 2026-05-25 AGI-Adjacent bundle. Overlaps with the existing Stage C self-evolving mutation engine. Live-park as a candidate to revisit at the Stage A → Stage B transition once multi-tenant traffic produces real cross-email pattern data. See stress-test answers below. |
| 2026-05-25 | **(Component F) "AGI-Style Behavior Principles" Section in the NorthStar Bible** — adds a new bibles section codifying autonomous-system principles | governance-idea | 0·0·0·0·0 = 0 | drop | Y | Decomposed component of the 2026-05-25 AGI-Adjacent bundle. Walks back the 2026-05-25 bibles deferral and does not fire any of its trigger conditions. "AGI" framing conflicts with the auditability/honesty wedge. See stress-test answers below. |
| 2026-05-25 | **Cyber Insurance Evidence Package** — buyer-ready bundle that packages existing NorthStar artifacts (Inbox Shield monthly report, append-only Blackboard logs, Decision Auditor reviews, signed §11 specs as architecture documentation, deterministic detector evidence chains, lift-only invariant test results, Two-Channel Confirmation enforcement records, cross-tenant isolation test results, kill-switch evidence) into a quarterly or annual deliverable specifically structured to answer 2026 cyber-insurance underwriting questions for the email-security control surface. Carrier-agnostic format; explicit scope = "email-fraud + inbox-layer MDR controls"; does NOT cover MFA / EDR / backups / IR plans / patch management (those are MSP responsibilities). MSP delivers the package to their SMB client; SMB submits with their underwriting application | feature-idea (positioning + packaging surface; Stage A explainability lane) | 2·2·2·2·2 = 10 | **promote with cheaper-proof-first guidance** | Y | Surfaced from the 2026-05-25 Frontier Intake Review #1 as Candidate 3 (cleanest wedge alignment of the five candidates). Selected by operator on 2026-05-25 evening as next gate firing. Score reflects directly-advances-build-arc (packaging surface for the locked auditability + evidence-depth wedge); direct paid deliverable possible within 90 days (bundle into Essentials/Plus/Enterprise tiers OR sell as quarterly add-on); clean Foundation Fit (additive, doesn't compromise determinism, tenant isolation, kill switch, lift-only invariants); client-facing artifact (entire purpose); fits active arc (same audience, same product, same wedge as Stage A). **Cheaper proof BEFORE spec drafting:** run 1-3 local MSP discovery calls (Carpathia IT, NetDNA, EC Managed IT, IT Works MSP BC, SFY IT, Good IT — captured 2026-05-25 in `THREAT_INTEL_LOG.md`) using EXISTING artifacts framed as "cyber-insurance evidence bundle for email-fraud controls" and ask whether their SMB clients would pay for quarterly delivery; binary go/no-go on whether the framing earns a spec-first deep dive. See stress-test answers below. |
| 2026-05-25 | **Trend-Chasing Layer / Frontier Intake (operator-driven, process-only v1)** — structured periodic operator routine that reviews emerging AI / agent / threat patterns from a curated source list (security advisories, AI-research feeds, vendor releases, MSP-channel news) and decides which patterns earn full gate evaluation. Output: a `Frontier_Intake_Log.md` artifact + scored think_sheet rows for any surfaced candidates. No runtime component, no new agent, no new infrastructure — pure operator discipline | process-idea (operator discipline) | 1·1·1·0·2 = 5 | revisit → **cheaper proof complete; monthly cadence committed 2026-05-25** | Y | Surfaced from operator concern on 2026-05-25 about NorthStar falling behind emerging AI / agent / threat patterns. **Cheaper proof complete 2026-05-25:** Review #1 ran the same evening using the locked starter source list; surfaced **5 candidates** (Department-Level Internal Impersonation Detector, OWASP LLM10 Unbounded Consumption Coverage, Cyber Insurance Evidence Package, Auto-Forwarding Inspection, Device-Code / OAuth-Consent Phishing Detector). Per cadence rule (4+ → monthly), recurring discipline committed at monthly cadence with a refinement flag to re-evaluate at the 90-day mark in case the count reflects backlog rather than steady-state pace. Full review record + source citations + sniff-test classifications captured in `Frontier_Intake_Log.md`. **Surfaced candidates are NOT auto-added to this table** — formal gating (5-axis scoring + 7-question stress test) happens only when the operator picks them up one at a time. More ambitious shapings (runtime "frontier intake agent" that watches feeds autonomously; marketable public "frontier watch" transparency surface for MSPs) remain separate ideas that earn their own rows only if v1 evidence warrants them. See stress-test answers below. |

---

## Stress-Test Answers

This section holds completed answers for every idea currently in the `promote` band with `ST = Y`. Promote candidates that still show `ST = N` belong in this section as soon as their answers are filled in.

### Sender-provenance / geo-velocity detector (2026-05-23)

1. **Failure mode** — Two realistic failure modes: (a) **false positives** when a legitimate vendor changes mail-relay infrastructure (e.g., moves from on-prem Exchange to M365), causing the geo baseline to shift abruptly and flag normal mail. Client sees noisy alerts in the daily digest. (b) **false negatives** for any cloud-to-cloud mail (Gmail → M365) because Google normalizes egress IPs to its own ranges and the geo signal is lost. Client gets no extra protection for the most common sender path.
2. **Hidden cost** — Monthly: GeoLite2 database refresh (free but must be scheduled). Per-tenant: a `sender_provenance_baseline.jsonl` file that grows roughly linearly with unique senders (~100 KB per active tenant per month — trivial). One-time: integration test fixtures for the `Received:` header parser, which must handle every real-world relay quirk. Estimated ongoing maintenance: a few hours per quarter as edge cases surface.
3. **Specific buyer** — Kelowna-area MSP with 5–15 SMB clients running mostly on M365 Business Standard. They charge each client ~$15–25/seat/month for managed email. NorthStar adds value as a per-tenant add-on the MSP resells at ~$5–10/seat with a ~70% margin. Geo-detection is the differentiator they cannot get from Microsoft Defender alone.
4. **Cost of inaction** — Without geo detection, BEC compromise of a real vendor account looks identical to legitimate mail through the LLM scoring path (good tone, real history, real account). Skipping this means we cannot honestly claim to defend against the highest-dollar SMB email fraud category, and any insurer review will mark that gap as a coverage exclusion.
5. **Cheaper proof first** — Yes. Before any code, pull two months of `Received:` headers from one volunteer mailbox (Matt's own or a friendly small business), extract sender→ASN/country mappings in a spreadsheet, and visually identify how many vendor accounts have stable origins vs. how many are too noisy to baseline. If <50% of business-critical vendors are stable enough to baseline, the assumption fails and the idea goes back to deep park.
6. **Existing competitor** — Microsoft Defender for Office 365 (P2) has "impossible travel" detection for *user logins* but not for *inbound sender origin*. Proofpoint and Mimecast have sender-reputation lookups but rely on global reputation, not per-tenant baselines. Avanan / Check Point Harmony Email has some inbound geo signals bundled into opaque "AI scoring." None of them expose the per-sender history as a client-readable audit trail — that's the differentiator.
7. **Pre-mortem** — "This will have failed because too many SMB vendors send through cloud-mail providers (Gmail, M365, AWS SES) where the originating user IP is normalized away, leaving the detector with only macro-level Google/Microsoft/AWS ASNs that change too frequently to baseline meaningfully — so the per-tenant baseline becomes either noise or empty for the very vendors clients care about."

**Decision recorded:** Promote candidate **only after** the cheaper-proof step (point 5) returns a positive signal on a real mailbox. Until then, stays in `promote` band but does not enter `PROGRESS.md`.

### Daily-digest demo packaged as a paid $300 case-study deliverable (2026-05-23)

1. **Failure mode** — Client pays $300, runs the demo on their own emails (or sample emails), and concludes "this is just a markdown report — I expected dashboard software." Reputational risk if the deliverable's scope isn't crystal-clear in writing before payment.
2. **Hidden cost** — Per engagement: ~3 hours to ingest the client's sample emails (sanitized), configure the deterministic LLM client to match real risk-band thresholds, run the demo, and write a one-page interpretation. Ongoing: zero infrastructure cost. Maintenance: the demo script must keep passing tests as the runtime evolves (already enforced by the existing test suite).
3. **Specific buyer** — Local Kelowna MSP owner or SMB office manager (~$50–100k revenue tier) who has heard about AI security but isn't ready to commit to a monthly contract. The $300 ask is low enough to be expensable without sign-off. Realistic addressable list: ~20 names within Matt's existing local network.
4. **Cost of inaction** — Without a one-shot paid deliverable, every conversation has to lead to a full retainer pitch, which is a much harder ask for a first-time buyer who has never seen NorthStar work. Skipping this leaves zero stepping stones between "interested" and "first MSP retainer."
5. **Cheaper proof first** — Yes — and it's already done. The runnable demo + generated markdown artifact (`Generated/Inbox_Shield_Daily_Digest_Demo.md`) is the proof. Next cheaper step: show that artifact to three local contacts and ask "would you pay $300 for a version of this run on your own inbox?" Decision gates on at least one "yes."
6. **Existing competitor** — Most cybersecurity vendors won't do a $300 one-shot — they sell annual contracts. The closest competitor is consultants who run security audits (typically $1500–5000 for a small business). NorthStar's offer is differentiated by being concrete, repeatable, AI-readable, and built on a real runtime that the client could later subscribe to.
7. **Pre-mortem** — "This will have failed because the demo artifact, while technically real, doesn't visibly differ from what a generic ChatGPT prompt could produce on the same input — so buyers see no reason to pay $300 for something they think is 'just AI summarizing emails.'"

**Decision recorded:** Promote candidate. Action: prepare a one-page scope document Matt writes himself (AI proofreads only) before any outreach. Then run the cheaper-proof conversation with three local contacts. If ≥1 "yes," move to `PROGRESS.md`.

### Visible Multi-Agent Deliberation Layer (2026-05-24)

1. **Failure mode** — Three realistic failure modes: (a) the reasoning trace becomes too long or too technical, so the client trusts it less, not more; (b) multiple agents repeat the same blind spot because they share the same prompt/model assumptions; (c) API cost/latency grows if deliberation runs on routine mail instead of only ambiguous or escalated mail.
2. **Hidden cost** — More LLM calls per ambiguous email, more prompt/version management, more test fixtures, and a new reporting surface that must stay stable once clients learn it. High tier likely needs 3-5 calls on deliberated emails (two lenses + judge + optional devil's-advocate/skeptic pass). This is acceptable only because NorthStar is sizing for SMBs, not enterprise bulk mail.
3. **Specific buyer** — Kelowna-area MSP with 5-15 SMB clients, especially clients with 50-100 employees and real AP/payroll exposure. Expected packaging: visible deliberation belongs in Plus/Enterprise-style reporting, with High intensity sold to construction firms, accounting firms, payroll-heavy businesses, and other clients moving meaningful ACH/wire volume.
4. **Cost of inaction** — Without visible reasoning, NorthStar risks looking like another opaque "AI risk score." That weakens the anti-commodity story, makes MSPs harder to equip for client conversations, and gives less useful feedback to the Red/Blue learning loop when a miss occurs.
5. **Cheaper proof first** — Yes. Before code, create 3-5 hand-written mock deliberation rows from existing demo emails: one obvious fraud, one benign false-positive candidate, one payment-change case, one ghost-thread case, and one clean email. Show them to an MSP/bookkeeper and ask: "does this make the finding easier to trust, or is it too much?"
6. **Existing competitor** — Defender, Mimecast, Proofpoint, and Avanan all produce alerts, scores, or policy verdicts, but generally do not expose a plain-English multi-agent debate / challenge / judge trail. Security copilots may summarize alerts, but the differentiator is using visible deliberation as part of the detection and audit artifact, not as a chat wrapper after the fact.
7. **Pre-mortem** — "This will have failed because the reasoning trace became expensive, slow, and too verbose for SMB users, causing MSPs to turn it off or ignore it instead of treating it as the trust layer."

**Decision recorded:** Promote candidate, but do not build before the underlying detector set is richer. Best sequence: Vendor Baseline Store -> Financial State Ledger / document signals -> client-facing 5-axis scoring -> visible deliberation. Build only behind Tiered Detection Intensity so Low/Medium tenants do not pay High-tier reasoning cost on routine mail.

### Tiered Detection Intensity (Low / Medium / High) aligned to sales tiers (2026-05-24)

1. **Failure mode** — Two realistic failure modes: (a) clients misunderstand Low as "weak security" instead of "lower routine-mail scrutiny with forced escalation on risky mail"; (b) MSPs misconfigure tenants to Low for cost reasons and then blame NorthStar when a non-escalated edge case is missed. This must be solved with clear defaults, audit visibility, and forced High escalation for hard-risk signals.
2. **Hidden cost** — Requires a new policy surface (`security_intensity_level`), detector minimum-tier metadata, auto-escalation rules, tests for every tier boundary, reporting copy that explains the tiers, and likely product-sheet updates. It also creates support burden because MSPs will ask why one email was escalated beyond the tenant's default tier.
3. **Specific buyer** — Same Kelowna MSP archetype, but this is also the cleanest sales packaging surface. Option C is the recorded commercial alignment: Essentials defaults Low, Plus defaults Medium, Enterprise defaults High, with add-ons separate. Low is for low-exposure SMBs, Medium is the default SMB posture, High is for businesses with payroll/AP/wire-transfer exposure.
4. **Cost of inaction** — Without intensity tiers, NorthStar has one cost/latency posture for every tenant. That makes pricing harder, forces low-risk clients to pay for high scrutiny, and prevents MSPs from matching security depth to client risk and budget. It also weakens the fair-access pricing strategy because the product has no controlled lower-cost posture.
5. **Cheaper proof first** — Yes. Before code, create a one-page tier matrix showing Low/Medium/High capabilities, auto-escalation triggers, and Essentials/Plus/Enterprise alignment. Use Monday discovery calls to ask MSPs whether this maps to how they already sell security tiers.
6. **Existing competitor** — Microsoft Defender has Standard/Strict presets; EDR tools expose prevention/sensitivity levels; MSPs are used to tiered service packages. NorthStar's differentiator is the forced-escalation rule: tier is a floor for routine mail, not a ceiling for risky mail, so an Essentials/Low client still gets High scrutiny on payment deltas or combined BEC signals.
7. **Pre-mortem** — "This will have failed because the tier system became a pricing gimmick instead of a clear security-control model, leading clients to choose Low to save money and misunderstand what protection they actually receive."

**Decision recorded:** Promote candidate. Strong fit because it ties technical cost control, tenant policy, and sales formation together. Requires spec-first treatment before implementation: locked tier definitions, detector minimum-tier contract, forced-escalation closed enum, `tenant_overrides` schema, default = Medium, and gate tests proving risky mail can force High scrutiny regardless of tenant default.

### Financial State Ledger / Delta Tripwire (2026-05-24)

1. **Failure mode** — Two realistic modes: (a) **false positives** when a vendor legitimately changes banks (M&A, branch consolidation, payment-processor switch). Bookkeeper sees an alert on a legitimate update and either learns to ignore alerts or the MSP gets a "why did you bother me" support ticket. (b) **extraction failure** — the detector cannot reliably extract a routing number / IBAN / account number from a poorly-scanned PDF, so the email passes through without a baseline check and the fraud lands.
2. **Hidden cost** — Extraction-regex set for routing numbers / SWIFT / IBAN / account numbers / payment-portal URLs from email body and PDF text (the harder part — PDF text extraction has edge cases). Per-tenant Vendor Baseline Store rows grow linearly with vendor count. Ongoing maintenance: periodic false-positive review when MSPs report "this is a real vendor change."
3. **Specific buyer** — Kelowna MSP with construction-GC, accounting-firm, or property-management clients (~75-employee size, real ACH/wire volume). Sold inside the Plus tier at ~$5–10/seat with ~70% MSP margin. Direct upsell line for the MSP: "we flag every payment-detail change before money moves."
4. **Cost of inaction** — This is THE single highest-dollar BEC pattern in the SMB segment. Skipping it means we cannot honestly claim BEC defense, and any insurer review marks it as the missing control. The product story loses its strongest single proof point.
5. **Cheaper proof first** — Yes. Pull ~30 real invoices from one volunteer mailbox, extract routing numbers / SWIFT / IBAN by hand, and confirm legitimate vendors stay stable quarter-to-quarter at >80%. If stability is below that, baseline matching breaks and the detector needs a different design.
6. **Existing competitor** — Mimecast and Proofpoint extract payment patterns at enterprise pricing tiers. Avanan has fuzzier impersonation detection. No SMB-tier product I'm aware of exposes a per-vendor payment-history baseline as a client-readable audit row.
7. **Pre-mortem** — "This will have failed because too many legitimate vendor payment changes (ESP migrations, M&A, processor switches) produced false positives, MSPs muted the rule, and we lost the protection in the alert-fatigue trap."

**Decision recorded:** Promote candidate. First detector to build after Vendor Baseline Store is implemented. Pair with two-channel confirmation enforcement so MSPs have a clean action attached to every Delta-Tripwire finding.

### Document Metadata Fingerprinting (2026-05-24)

1. **Failure mode** — Vendor upgrades QuickBooks, switches to Xero, has an IT contractor regenerate a PDF, or scans an invoice. False positive on a legitimate tooling change. Bookkeeper sees a flag on a real invoice and trust drops if the explanation is too technical.
2. **Hidden cost** — PDF parsing library dependency (`pypdf`, `pdfplumber`, or similar) — small but adds an external dependency to maintain. Per-tenant `pdf_producer_fingerprint` baseline rows. Edge cases: corrupted PDFs, password-protected PDFs, image-only PDFs (no metadata to read at all — fallback to OCR or skip).
3. **Specific buyer** — Same MSP archetype, particularly clients receiving high-stakes invoices from a stable vendor list (construction GCs receiving subcontractor invoices, accounting firms receiving client documents, real-estate offices receiving title-company invoices).
4. **Cost of inaction** — Attackers commonly re-edit a real PDF in third-party tools (PDF24, Acrobat Web, mobile editors). Skipping this leaves one of the most reliable structural fingerprints of a tampered invoice on the table.
5. **Cheaper proof first** — Yes. Pull 50 real invoices from 5 different vendors across one volunteer mailbox. Confirm that each vendor's PDF Producer field is stable across their last 6 months at >70%. If stability is below that, the signal is too noisy to baseline.
6. **Existing competitor** — Forensic and discovery tools (Magnet AXIOM, FTK) read PDF metadata for legal audits, but no SMB email-security product I'm aware of bakes per-vendor metadata baselining into automated scoring.
7. **Pre-mortem** — "This will have failed because too many legitimate vendors regenerated or re-saved PDFs through web-based viewers or print-to-PDF, the Producer field churned too much to baseline, and the detector produced more noise than signal."

**Decision recorded:** Promote candidate. Second detector to build after Financial State Ledger. The two work as a pair: payment-destination signal + document-integrity signal together are stronger than either alone.

### Micro-Temporal Mismatches (2026-05-24)

1. **Failure mode** — Vendor's bookkeeper is on vacation or sick, so an invoice is actually generated by a different person at an off-pattern time. Or the vendor batches month-end invoices and creates them all at 11pm. Both produce false positives that look like attacker timing.
2. **Hidden cost** — Per-tenant `vendor_send_time_window` baseline rows. Edge cases: vendors with irregular hours, vendors in different time zones than the recipient, daylight savings transitions, holidays, statutory days. Maintenance cost: keeping the timezone-normalisation logic correct as edge cases surface.
3. **Specific buyer** — Same MSP archetype, particularly useful for clients whose vendors have predictable AP patterns — construction, services, recurring SaaS, professional services. Less useful for clients with global vendor sets where time-window stability is naturally low.
4. **Cost of inaction** — Attackers operating from different timezones leave PDF-creation-timestamp signatures that legitimate vendors don't. Skipping this means losing one of the few timezone-anomaly signals available without going to enterprise-tier tooling.
5. **Cheaper proof first** — Yes. Analyse 3 months of timestamps from one volunteer mailbox. Check whether each vendor's send-time-window is consistent enough to baseline (hour-of-day bucket variance < ~3 hours, business-day distribution > ~80%). If not, the signal is too noisy.
6. **Existing competitor** — Some SOC tools flag "off-hours" general patterns at the user level. None I'm aware of baseline send-time at the per-vendor level for SMB inbox.
7. **Pre-mortem** — "This will have failed because vendor send-time patterns turned out too noisy at SMB scale — too many vendors had irregular schedules, batched mail at odd hours, or sent through ESPs that timestamped at server time rather than vendor time."

**Decision recorded:** Promote candidate, but lower priority than Financial State Ledger and Doc Metadata. This is a confirming signal more than a primary one. Build after Doc Metadata, before Structural Payload Anomalies.

### Structural Payload Anomalies (OCR / encoding evasion) (2026-05-24)

1. **Failure mode** — Legitimate vendor scans paper invoices producing image-only PDFs. Some legitimate billing portals use overlaid links for tracking. False positives possible if the detector treats "image-only" or "overlaid link" as inherently suspicious without baseline context.
2. **Hidden cost** — PDF parsing dependency (`pypdf` / `pdfplumber`) plus possible OCR dependency (`tesseract`) — adds significant install complexity, especially on Windows. Maintenance: PDF parsing libraries break on edge cases (encrypted PDFs, corrupted streams, mixed-content PDFs).
3. **Specific buyer** — Same MSP archetype. Particularly valuable for clients in industries where invoice fraud has been observed (construction, AP-heavy businesses). The MSP can use it as upsell ammo: "scanners don't see this — NorthStar does."
4. **Cost of inaction** — Attackers actively use these evasion techniques to bypass automated scanners. Skipping leaves a known evasion path open and weakens the structural-defense story.
5. **Cheaper proof first** — Yes. Pull ~100 real invoices, count how many are image-only PDFs vs text PDFs, count any white-on-white or transparent overlays in legitimate mail. If <5% of legitimate invoices have any of these patterns, the baseline is clean and the detector is high-signal.
6. **Existing competitor** — Some advanced email-security tools do basic content analysis (e.g. Avanan, Abnormal). The differentiator here is the "vendor historically sent text PDFs, this one is image-only" baseline comparison, not the standalone signal.
7. **Pre-mortem** — "This will have failed because the PDF/OCR tooling stack added install friction (especially on Windows) and maintenance burden that wasn't justified by the actual false-positive rate."

**Decision recorded:** Promote candidate, but defer until the PDF dependency decision is made. Independent of Vendor Baseline Store (can ship in parallel) but has its own infrastructure burden. Best ordered after Doc Metadata Fingerprinting (same dependency) and Micro-Temporal (same baseline pattern).

### DKIM / SPF / DMARC ingestion (2026-05-24)

1. **Failure mode** — Legitimate domains have intermittent DKIM/SPF failures due to forwarding rules, mailing-list software, or misconfigured ESPs. False positives on legitimate-but-broken mail are the main risk. Some legitimate small businesses simply do not have DMARC at all — the detector cannot treat "no DMARC" as inherently suspicious.
2. **Hidden cost** — Parsing the `Authentication-Results` header (already well-defined RFC, low maintenance). Per-vendor baseline: track which domains have historically passed so a sudden failure becomes high-signal. Edge cases: domains that always fail one of the three, domains that mix internal/external mail flows.
3. **Specific buyer** — Same MSP archetype. This is the most universal detector — every modern inbound email has these headers, and every MSP already knows what DKIM/SPF/DMARC mean. Easiest detector to explain in a discovery call.
4. **Cost of inaction** — Table-stakes coverage. Any system audit (insurer, MSP technical review, regulatory questionnaire) will flag the absence of DKIM/SPF/DMARC ingestion as a gap. Skipping it materially weakens the audit-trail story.
5. **Cheaper proof first** — Yes. Parse 100 emails from one volunteer mailbox, count pass/fail rates per domain. Confirm legitimate domains have stable pass rates (>95%) and failures cluster on suspicious senders. Should take a few hours of analysis.
6. **Existing competitor** — Defender, Mimecast, Proofpoint all use these signals heavily. The NorthStar differentiator is the **per-vendor baseline** ("this domain has always passed before — this is the first failure") rather than the standalone "this email failed" signal everyone else already produces.
7. **Pre-mortem** — "This will have failed because too many legitimate small businesses don't have proper DMARC, so legitimate inbound mail produced 'failure' signals that were really just bad sender hygiene, not fraud — and the detector got muted."

**Decision recorded:** Promote candidate. Independent of Vendor Baseline Store but materially stronger with it (baseline turns "this domain failed" into "this domain has never failed before"). Can ship in parallel with the BEC detectors. Lowest-risk earliest-shippable detector on the promote list besides the already-shipped header divergence / ghost thread.

### Callback Phishing / TOAD detection layer (2026-05-24)

1. **Failure mode** — Two modes: (a) **false positives** on legitimate vendors that publish phone numbers in invoices (billing department, support line, accounts receivable). The detector must distinguish "call our published billing line" from "URGENT: call this new number to verify." (b) **false negatives** when the attacker uses a VoIP / spoofed number that looks similar to a published vendor line.
2. **Hidden cost** — Body-language regex set (callback phrases). Phone-number extraction + baselining — adds a new closed-enum entry (`phone_number`) to Vendor Baseline Store schema, which requires a Vendor Baseline Store spec revision. VoIP / spoofed-number heuristics (optional v2 — phone-number reputation lookups).
3. **Specific buyer** — Same MSP archetype, but especially important for clients with phone-based finance workflows: payroll bureaus, accounting firms, real-estate offices, anyone whose AP process involves verbal confirmation. The pitch ("attackers are pivoting to phone-based fraud, NorthStar catches the setup email before the call") sells itself.
4. **Cost of inaction** — Attackers are actively pivoting to TOAD precisely because it bypasses email-only controls. Skipping this means we'll miss the next wave of BEC variants that everyone else is also slow to catch.
5. **Cheaper proof first** — Yes. Sample 200 real emails, count how many contain phone numbers in the body. Of those, classify which have callback-language framing. If <10% of legit mail has callback language but suspicious mail clusters >50%, the detector has signal worth building.
6. **Existing competitor** — Some next-gen email security (Abnormal, Avanan) mentions TOAD detection, but rarely with per-vendor phone-number baselining. The baseline-anchored approach ("this vendor has never published this number before") is novel for the SMB tier.
7. **Pre-mortem** — "This will have failed because phone-number baselining proved too noisy at SMB scale (vendors change billing numbers more often than expected) and body-language alone produced too many false positives on legitimate 'please call us to confirm' emails."

**Decision recorded:** Promote candidate. Sequence the build in two parts: (1) body-language detection ships independently as a pure-function detector like header divergence, (2) phone-number baselining waits for a Vendor Baseline Store spec revision to add `phone_number` to the closed enum. Body-language part can ship in parallel with DKIM/SPF/DMARC.

### Two-channel confirmation enforcement (2026-05-24)

1. **Failure mode** — The workflow creates checkbox security: users click "confirmed" without actually verifying through a known channel, or MSPs treat the audit line as proof even when no real call occurred. Another failure mode is friction: bookkeepers find the step annoying and pressure MSPs to disable it.
2. **Hidden cost** — Requires a confirmation state in the report/audit surface, wording for safe verification steps, per-email action status, and possibly a small operator UI or structured digest action. Also creates support questions: "who is allowed to mark confirmed?" and "what evidence is enough?"
3. **Specific buyer** — MSPs serving SMBs with AP/payroll exposure. The buyer value is operational: it gives the MSP a safe process to recommend when NorthStar flags payment-change risk, without requiring the full NorthStar Portal.
4. **Cost of inaction** — Detection without a verification process leaves the human unsure what to do next. If NorthStar says "risky" but does not prescribe and record the out-of-band step, the client can still call the attacker-provided number and lose money.
5. **Cheaper proof first** — Yes. Add the confirmation wording manually to one sample report and ask an MSP/bookkeeper whether it is clear enough to follow: "verify via previously-known phone number, not the number in this email; record who confirmed and when."
6. **Existing competitor** — Big AP/procurement platforms enforce approval workflows, but SMB email-security tools usually stop at alerting. NorthStar's differentiator is connecting email-risk detection to a simple, auditable business process before money moves.
7. **Pre-mortem** — "This will have failed because users treated the confirmation step as paperwork, clicked through it without real verification, and NorthStar's audit trail recorded false confidence instead of real control."

**Decision recorded:** Promote candidate. Build after Financial State Ledger because the workflow is most useful when attached to a concrete payment-delta finding. Stage A version should be report/digest based; no portal required.

### High-trust vendor verification layer (2026-05-24)

1. **Failure mode** — Too broad too early. If we try to solve challenge/response, portal, vendor identity, shared secrets, and two-channel confirmation at once, the feature becomes a second product and slows the core BEC detector path.
2. **Hidden cost** — Vendor onboarding, process documentation, key/token lifecycle if challenge/response is used, support burden when vendors lose tokens or staff change, and legal/contract language around what NorthStar verifies versus what the client remains responsible for.
3. **Specific buyer** — Plus/Enterprise-tier SMBs through MSPs, especially businesses with recurring high-value vendor payments. The MSP sells it as "a safer payment-change process," not as cryptography.
4. **Cost of inaction** — Without a high-trust verification direction, NorthStar may stop at detection and not grow into the workflow layer that actually prevents payment redirection after an alert fires.
5. **Cheaper proof first** — Yes. Validate two-channel confirmation first. If clients follow that process and MSPs can sell it, then consider per-vendor challenge/response or portal-based verification. Do not build cryptographic vendor tokens until process demand is proven.
6. **Existing competitor** — S/MIME/PGP solve message signing poorly at SMB scale; AP portals like Ariba/Coupa solve payment-change workflow at enterprise scale. NorthStar's wedge is the SMB-accessible version focused only on high-risk financial-change flows.
7. **Pre-mortem** — "This will have failed because we mistook a strategic direction for a build ticket, overbuilt a verification system before customers proved demand, and spread the core product thin."

**Decision recorded:** Promote candidate as a strategic umbrella, not a first build. Immediate build is Two-channel confirmation; challenge/response and portal stay downstream until Stage A evidence exists.

### NorthStar Portal (2026-05-24)

1. **Failure mode** — Portal becomes critical-path SaaS before NorthStar has enough customers or operational maturity. Downtime blocks AP workflows, authentication bugs create trust damage, and scope explodes into vendor management / bookkeeping.
2. **Hidden cost** — Hosting, authentication, MFA, account recovery, vendor invitations, tenant isolation, audit UI, uptime expectations, notification workflows, branding/design, security hardening, and support. This is months, not days.
3. **Specific buyer** — Stage B MSP/client accounts with proven need after paid pilots: construction, accounting, property management, real-estate, payroll-heavy businesses. Vendors become secondary users, which creates brand exposure but also support obligations.
4. **Cost of inaction** — Without a portal, NorthStar remains mostly invisible behind reports and digests. That limits brand presence and prevents the strongest payment-change workflow: "vendors update sensitive details through NorthStar, not email."
5. **Cheaper proof first** — Yes. First prove the workflow with report-based two-channel confirmation. Then test a no-code or mock portal flow with 1-2 friendly businesses. Only build real portal after customers demonstrate they will use it.
6. **Existing competitor** — Enterprise AP/procurement portals (Ariba, Coupa) and vendor-management platforms. NorthStar's possible differentiator is narrower: SMB email-fraud and payment-change verification, not full procurement.
7. **Pre-mortem** — "This will have failed because we built a SaaS portal too early, inherited authentication/uptime/support obligations, and diluted the core email-fraud runtime before revenue proved the need."

**Decision recorded:** Promote / moonshot. Stage B only. Requires paid pilots, clear workflow proof, and a dedicated portal deep-dive spec before any implementation.

### Client-facing 5-axis Email Scoring Rubric (2026-05-24)

1. **Failure mode** — The axes are wrong or too abstract, so clients learn a scoring vocabulary that later has to change. Another failure mode: the 5-axis score disagrees with the internal 0-100 score and creates confusion.
2. **Hidden cost** — Requires a stable mapping from internal signals to client-facing axes, documentation, test fixtures for known email patterns, and report rendering. Once published, axis definitions become a brand promise and cannot drift casually.
3. **Specific buyer** — MSPs who need a client-readable monthly report and SMB owners/bookkeepers who need to understand why an email was flagged without reading headers. This directly supports the $300 report and future Plus/Enterprise reporting.
4. **Cost of inaction** — NorthStar risks looking like another opaque risk-score tool. Without a client-facing rubric, the MSP has to translate every technical finding manually, which weakens sales, trust, and monthly-retainer value.
5. **Cheaper proof first** — Yes. Mock 5 scored example emails using existing detectors: header divergence, ghost thread, payment-change, benign vendor mail, and callback phishing. Ask whether the axis score makes the finding easier to understand.
6. **Existing competitor** — Many tools produce severity labels or numeric scores. The differentiator is a stable multi-axis explanation: Sender Identity, Conversation Continuity, Vendor Payment History, Document Integrity, Origin / Timing.
7. **Pre-mortem** — "This will have failed because the score looked simple but hid too much complexity, clients trusted the total without reading the axis detail, and the mapping broke as new detectors were added."

**Decision recorded:** Promote candidate. Build after Financial State Ledger and document-signal detectors exist, so the axes map to real signals. Needs its own spec before implementation.

### Adversarial prompt-injection detector (2026-05-24)

1. **Failure mode** — False positives on legitimate technical mail containing code blocks, Markdown headings, instructions, or pasted AI prompts. False negatives if attackers use subtle natural-language prompt injection instead of obvious `[SYSTEM_INSTRUCTION]` strings.
2. **Hidden cost** — Pure-function body scanner is cheap, but maintaining a useful pattern list requires periodic updates as prompt-injection styles evolve. If expanded to PDF/HTML hidden text, it overlaps with Structural Payload Anomalies and may need PDF parsing.
3. **Specific buyer** — MSPs with clients whose inbound mail is scored by an LLM. Buyer story: "we defend the AI layer itself, not just the mailbox." Stronger for technical clients, but still useful as a trust/audit point.
4. **Cost of inaction** — If an inbound email can instruct or bias the LLM scorer, the scoring layer becomes an attack surface. Skipping this weakens the claim that NorthStar's AI path is hardened against adversarial input.
5. **Cheaper proof first** — Yes. Seed 20 synthetic emails containing obvious prompt-injection strings and 20 legitimate technical emails containing code/Markdown. Confirm the detector catches the former without over-flagging the latter.
6. **Existing competitor** — LLM app-security tools and prompt-injection filters exist, but email-security vendors rarely expose prompt-injection detection for their own AI scoring path. NorthStar differentiator is proving the LLM layer has defensive overlays.
7. **Pre-mortem** — "This will have failed because obvious prompt-injection patterns were easy to catch, but real attacker prompts were subtle, and the detector produced noise on normal technical/business emails."

**Decision recorded:** Promote candidate. Independent and small. Can ship before or alongside DKIM/SPF/DMARC as a pure-function deterministic overlay, but should stay scoped to protecting the scoring path.

### Consolidated tampering drill suite (2026-05-24)

1. **Failure mode** — Becomes presentation polish instead of real coverage. If it only reorganizes existing tests without adding meaningful insurer/MSP-readable scenarios, it may not justify time spent.
2. **Hidden cost** — Low engineering cost, but requires careful curation so the drill suite remains stable, readable, and not a duplicate maintenance burden. Must avoid brittle test ordering or over-coupling unrelated tampering tests.
3. **Specific buyer** — MSPs, insurers, or technical reviewers who want one evidence surface showing that NorthStar tests tampering, injection, cross-tenant boundaries, and lift-only invariants. Indirect buyer value, direct trust artifact.
4. **Cost of inaction** — Existing tampering coverage is scattered. Without consolidation, it is harder to show reviewers a single "this system tests adversarial tampering" proof surface.
5. **Cheaper proof first** — Yes. Create a one-page inventory of current tampering/security tests and show whether they already cover enough to satisfy a reviewer. Only build a consolidated test file if the inventory exposes fragmentation that hurts the evidence story.
6. **Existing competitor** — Mature security products have compliance/security test evidence, but early-stage SMB tools rarely present it cleanly. NorthStar differentiator is auditable proof from the start.
7. **Pre-mortem** — "This will have failed because it became a vanity test suite that duplicated coverage, slowed test maintenance, and did not materially improve buyer trust."

**Decision recorded:** Promote candidate, but low urgency. Best built after the next few detectors land so the suite consolidates real new coverage, not just today's existing tests.

### NorthStar "Analyst Brain" / AGI-style reasoning layer — bundle-level gate (2026-05-25)

Surfaced from operator research material that proposed: (a) a higher-level "analyst-style reasoning layer" above the existing detectors, (b) cross-domain learning across email, logs, payments, and endpoints, (c) an "auto-tuning detector ring" / self-improving feedback loop that retrains rules and thresholds, and (d) an "AGI-style behavior principles" section appended to the NorthStar Bible. The bundle-level 7-question test was run first; on operator request the bundle was then decomposed and each component re-scored individually (see decomposition section below).

1. **Failure mode** — Two distinct failures. First: "AGI" / "AGI-style" framing leaks into product vocabulary, MSP outreach, or `VISION.md`, putting NorthStar's voice into the bloated-vendor language pool the project just decided to differentiate from. Second: cross-domain expansion (logs / endpoints / payments) silently re-widens Stage A from inbox-layer MDR into general-SOC, which is a different company shape, a different sales motion, and a different infrastructure bill.
2. **Hidden cost** — A new "analyst brain" lane requires a new §11 spec, a new runtime module, gate tests, and an audit target. Cross-domain coverage requires log / endpoint / payment connectors and threat models NorthStar does not currently have. An auto-tuning detector ring requires ML training infrastructure, training data, an evaluation harness, rollback safety, and runtime guardrails that do not exist today and would consume months. Re-opening the bibles walks back today's explicit deferral.
3. **Specific buyer** — Buyer is unclear at Stage A. Real local target list (Carpathia IT, NetDNA, EC Managed IT, IT Works MSP BC, SFY IT, Good IT, captured 2026-05-25 in `THREAT_INTEL_LOG.md`) sells fraud detection to 25-200-employee SMBs. "AGI-ready cybersecurity" sells against this audience, not to it. Enterprise SOC buyers exist but are not the Stage A target.
4. **Cost of inaction** — Low. NorthStar already has the analyst-layer kernel: 7 deterministic detectors → scoring agent → Tiered Detection Intensity → Vendor Baseline Store → Financial State Ledger → Two-Channel Confirmation → newly §11-signed Client-Facing 5-Axis Email Scoring Rubric. The 5-axis rubric is the first analyst-style explanation block. We are shipping the analyst-layer direction one piece at a time under existing discipline.
5. **Cheaper proof first** — Yes, and it is already running. The 5-axis rubric is the cheaper proof for the analyst-layer direction. If MSPs in discovery confirm the rubric is valuable, the case for a deeper analyst layer earns evidence. If they do not, no new lane is needed.
6. **Existing competitor** — Microsoft Sentinel, IBM QRadar, Splunk, Palo Alto Cortex XSOAR, and similar enterprise SOC platforms market themselves as "AI / AGI-style" and serve the exact audience NorthStar's wedge does **not** target. Following their language puts NorthStar into a footrace it cannot win and abandons the auditability / explainability / per-tenant tuning / reversibility / evidence-depth differentiation locked on 2026-05-25.
7. **Pre-mortem** — "We added an AGI-style analyst-brain lane in May 2026 because a research paste sounded important. By July scope had crept from email to logs and endpoints. By September the runtime had four new weakly-tested modules. By November the spec → §11 → build discipline had eroded because the new lane did not fit the deep-dive template. MSP discovery calls started using slick AGI language instead of plain English. We failed because we accepted a research paste at face value instead of running the gates."

**Decision recorded:** **Drop / reshape (bundle-level).** The package as written was rejected. On operator request 2026-05-25, the bundle was then decomposed into six discrete components and each was scored + stress-tested individually below. Component verdicts replace the bundle verdict for ongoing reference.

---

### AGI-Adjacent Layer — component decomposition (2026-05-25)

The bundle-level gate above recorded the proposal as `drop / reshape` (score 3/10). On 2026-05-25 Matt asked that the bundle be broken up and run through the gates piece-by-piece so the real signal could be surfaced cleanly.

**Vocabulary boundary:** "AGI" and "AGI-adjacent" are acceptable inside `think_sheet.md` as internal design rationale for an internal stress test. They **do not enter** product surfaces, outreach scripts, deep-dive specs, the NorthStar Bible, or any client-facing artifact. Stage A surfaces use plain English. The wedge is auditability, explainability, per-tenant tuning, reversibility, and evidence depth.

#### Component A — NorthStar Analyst Reasoning Layer (cross-detector synthesis, email-only)

Higher-level reasoning module above the existing detectors that synthesizes findings into analyst-grade evidence summaries: per-email cross-detector and per-tenant cross-email. The §11-signed 5-axis rubric is the per-email instance of this layer; cross-email / cross-detector synthesis is the unbuilt extension.

1. **Failure mode** — Synthesis layer produces output that disagrees with the per-email 5-axis rubric, creating two competing "official" client-facing scores; or duplicates existing scoring-agent / Tiered Detection / Decision Auditor functionality without adding value.
2. **Hidden cost** — New §11 spec, new runtime module, gate tests, audit target. Synthesis logic must define cross-detector aggregation rules (deterministic, LLM-driven, or hybrid), each with its own discipline implications. Probably needs a `synthesis_consistency_override` analogous to the rubric's `rubric_consistency_override`.
3. **Specific buyer** — MSPs running monthly reviews who want a per-tenant synthesis ("here is what happened across this tenant's vendors this month"). SMB owners who want a single coherent narrative rather than 200 per-email findings.
4. **Cost of inaction** — Per-email rubric is the only synthesis surface. MSPs translate per-email findings into monthly narratives manually. Workable in early stage; scaling-limited as tenant count grows.
5. **Cheaper proof first** — Yes. The §11-signed 5-axis rubric is the cheaper proof for the synthesis-layer direction. If MSPs in discovery ask for cross-email synthesis after seeing the rubric, that's the trigger to build it.
6. **Existing competitor** — Most enterprise SOC platforms (Sentinel, QRadar, Cortex XSOAR) bundle a synthesis layer. SMB-channel email tools generally do not. NorthStar's wedge is auditable synthesis specifically for the MSP-channel SMB tier.
7. **Pre-mortem** — "Synthesis layer drifted from the per-email rubric. Clients saw conflicting messages between per-email rubric and per-tenant synthesis. Mitigated by making synthesis a deterministic projection of underlying detector outputs (same discipline as the rubric), with a synthesis-disagreement guard."

**Decision recorded:** **Promote candidate (score 9/10).** Email-only Stage A scope. Build only after the §11-signed 5-axis rubric ships and produces evidence about whether MSPs find cross-email / cross-detector synthesis valuable. Spec-first; needs its own deep dive before implementation. Autonomy-toggle and "callable, not always on" semantics belong inside this spec when it is drafted, not as a separate idea.

#### Component B — Cross-Domain Expansion (logs / endpoints / payments)

1. **Failure mode** — Stage A scope silently expands to general SOC. Existing email-fraud differentiation gets diluted. NorthStar becomes a worse version of Sentinel / QRadar instead of the best version of inbox-layer MDR.
2. **Hidden cost** — Connectors for logs, endpoints, and payments. New threat models. New ingest and scoring pipelines. New compliance surface (SOC2, HIPAA-adjacent in some logs). Different sales motion. Multi-quarter at minimum.
3. **Specific buyer** — Not the Stage A target. Enterprise SOC buyers exist but require a different go-to-market.
4. **Cost of inaction** — Zero in Stage A. NorthStar's Stage A wedge does not require multi-source coverage.
5. **Cheaper proof first** — Yes. Don't build it. Stage B revenue evidence is the gate.
6. **Existing competitor** — Sentinel, QRadar, Splunk, Cortex XSOAR are mature. Entry barrier is high; differentiation is low.
7. **Pre-mortem** — "We tried to be a SOC. We were not a SOC. We lost the fraud-detection wedge that was actually winning."

**Decision recorded:** **Drop for Stage A (score 2/10).** Re-evaluate only at a Stage A → Stage B transition decision, gated on Stage A revenue + customer trust + proven inbox-layer wedge.

#### Component C — Auto-Tuning Detector Ring

1. **Failure mode** — Autonomous tuning changes detector behavior without operator approval, breaking determinism + reversibility + auditability — exactly the wedge.
2. **Hidden cost** — ML training infrastructure, training data, evaluation harness, rollback safety, runtime guardrails. None of these exist; all of them are months of work.
3. **Specific buyer** — Buyers don't ask for self-tuning detectors; they ask for accurate ones. Autonomous tuning is engineering convenience, not buyer demand.
4. **Cost of inaction** — Zero. Stage A discipline forbids autonomous tuning explicitly per `VISION.md`.
5. **Cheaper proof first** — Operator-approved drift tuning (Component D) is the cheaper proof for whether automation is even needed. Most detector tuning works fine with a human-approved surface.
6. **Existing competitor** — Modern ML-driven email security (Abnormal, Defender) uses autonomous models, but they are LLM-class systems with massive training infrastructure. Detector-tuning rings at NorthStar's scale would be ungrounded.
7. **Pre-mortem** — "Autonomous tuning quietly drifted detector thresholds. A regression went undetected for six weeks. Customer fraud was missed. The 'self-improving' label became 'self-degrading' in the post-mortem."

**Decision recorded:** **Drop (score 0/10).** Stage C, possibly never. Aligns with the existing Stage C "self-evolving defense swarm" milestone, not a near-term lane.

#### Component D — Operator-Approved Drift Tuning Surface

Reframe of auto-tuning: deterministic drift detection that surfaces threshold-update *candidates* to the operator for explicit human approval. No autonomy. Preserves determinism, reversibility, auditability.

1. **Failure mode** — Drift surface produces too many false candidates and the operator ignores it; or too few, missing real drift; or fires before NorthStar has enough tenant traffic for "drift" to be a meaningful concept.
2. **Hidden cost** — Drift detection logic, surface UI or report row, approval workflow, rollback path. Modest spec; real engineering.
3. **Specific buyer** — Internal-only initially (Matt and any future operator). Indirectly serves clients via better detector quality over time.
4. **Cost of inaction** — Detectors do not drift cleanly without traffic. Until NorthStar has paid pilots generating real tenant traffic, drift detection is theoretical. Cost of inaction is low until traffic exists.
5. **Cheaper proof first** — Yes. Wait until at least one paid pilot generates real traffic, then evaluate whether detectors are actually drifting. Build on evidence, not on speculation.
6. **Existing competitor** — Generally proprietary in mature security tools; not a public differentiator.
7. **Pre-mortem** — "Built drift surface before having traffic. Surface produced no useful signal. Lane was wasted; should have waited for paid pilots."

**Decision recorded:** **Revisit (score 5/10).** Live-park until first paid pilot generates real tenant traffic. Then re-score with evidence about whether detectors drift in production.

#### Component E — Threat-Family Hypothesis Engine

Cross-email pattern-clustering agent that proposes new threat-family hypotheses with evidence chains for human review.

1. **Failure mode** — Hypothesis engine proposes patterns that look novel but are well-known threat families NorthStar already detects, creating noise; or proposes truly novel patterns operators cannot validate without external threat-intel feeds.
2. **Hidden cost** — Cross-email pattern-clustering logic, hypothesis evidence-chain logging, human-review workflow. Probably uses an LLM with strict evidence boundaries; non-deterministic component class is a discipline shift.
3. **Specific buyer** — Stage B/C trust-layer artifact. Doesn't directly support Stage A revenue.
4. **Cost of inaction** — None in Stage A. Existing detectors handle known families. Adversarial training in `Phase_1_3_Sandbox_Training_Pit_Deep_Dive.md` already creates synthetic novel patterns for Red/Blue learning.
5. **Cheaper proof first** — The `behavioral_deviation_flags` enum in the scoring agent already provides a coarse "this email exhibits unusual patterns" signal. Cluster analysis on that signal once tenant traffic exists is the cheaper proof.
6. **Existing competitor** — Threat-intel feeds (CISA KEV, abuse.ch) and ML-based email security platforms produce threat-family hypotheses. NorthStar's differentiator would be operator-reviewed evidence chains tied to per-tenant data.
7. **Pre-mortem** — "Built hypothesis engine without enough data to learn from. Output was noise. Operators ignored it. Lane was abandoned."

**Decision recorded:** **Live park (score 4/10).** Revisit at Stage A → Stage B transition once multi-tenant traffic produces real cross-email pattern data.

#### Component F — "AGI-Style Behavior Principles" Section in the NorthStar Bible

1. **Failure mode** — Bibles get re-opened; "AGI" vocabulary enters the project voice; today's deferral decision is silently undone.
2. **Hidden cost** — Bibles drafting was explicitly deferred 2026-05-25 with named trigger conditions. Re-opening them requires walking back that decision; this proposal fires zero of the trigger conditions.
3. **Specific buyer** — None. Internal governance only.
4. **Cost of inaction** — Zero. The existing distributed constitution (`VISION.md` non-negotiables, signed §11 specs, Decision Auditor, kill switch, lift-only invariants, append-only Blackboard) already governs autonomous-style behavior.
5. **Cheaper proof first** — The trigger conditions for the bibles deferral *are* the cheaper proof — they say when bible work earns priority. None is fired by this proposal.
6. **Existing competitor** — Companies with AI ethics statements exist; few have constitutional-style governance documents tied to runtime behavior. NorthStar's distributed-constitution approach is already differentiated.
7. **Pre-mortem** — "Re-opened bibles mid-Stage-A. Drafting consumed weeks. Bible language drifted into outreach voice. Wedge eroded."

**Decision recorded:** **Drop (score 0/10).** Walks back today's deferral. Trigger conditions for un-deferring are explicit and not fired by this proposal.

---

### Component decomposition summary (2026-05-25)

| Component | Score | Verdict |
|---|---|---|
| A. NorthStar Analyst Reasoning Layer (cross-detector synthesis, email-only) | **9/10** | **Promote.** Build after rubric ships and MSP feedback supports it. Spec-first. |
| B. Cross-Domain Expansion (logs / endpoints / payments) | 2/10 | Drop for Stage A. Re-evaluate at Stage A → Stage B transition. |
| C. Auto-Tuning Detector Ring | 0/10 | Drop. Stage C, possibly never. |
| D. Operator-Approved Drift Tuning Surface | 5/10 | Revisit. Live-park until paid pilot traffic. |
| E. Threat-Family Hypothesis Engine | 4/10 | Live park. Revisit at Stage A → Stage B transition. |
| F. "AGI-Style Behavior Principles" Bible Section | 0/10 | Drop. Walks back the bibles deferral. |

**One real survivor: Component A.** It is the future Stage A → Stage B bridge for the explainability lane and is the natural successor to the §11-signed 5-axis rubric. The rubric ships first; Component A's spec gets drafted only after MSPs validate the rubric. Until then, no new lane authorized.

The underlying operator concern about staying current with emerging AI / agent / threat patterns is now captured separately as the **Trend-Chasing Layer / Frontier Intake** idea, scored and stress-tested directly below.

---

### Trend-Chasing Layer / Frontier Intake — process-only v1 (2026-05-25)

Surfaced from operator concern raised verbally a week ago and re-raised on 2026-05-25 alongside the AGI-Adjacent decomposition. The concern: the AI / agent / threat landscape moves faster than NorthStar's build cadence, and the project needs a structured way to notice landscape shifts before they erode product-market fit. The v1 scoping here is the cheapest, most defensible shape: **operator-driven, process-only, no runtime, no new agent.** More ambitious shapings (runtime intake agent; public-facing transparency surface) are explicitly out of scope of this row and earn their own rows independently if v1 evidence warrants them.

1. **Failure mode** — Three plausible failure modes. (i) Created once, abandoned: the artifact becomes shelfware and the concern remains unaddressed. (ii) Used too aggressively: every monthly review surfaces 5+ candidates, `think_sheet.md` overflows with research-paper ideas, build queue drifts toward intellectually exciting work and away from customer-driven work. (iii) Vocabulary leak: "AGI" / vendor-marketing language in source feeds bleeds back into NorthStar's voice despite today's vocabulary boundary.
2. **Hidden cost** — Operator time is the real cost. Estimate ~1-2 hours per intake review at monthly cadence, plus ~30 min per surfaced candidate to stress-test. Realistic monthly burn at 4 candidates: ~3-4 hours. Modest but not free. Bigger hidden cost: cognitive load of continuously evaluating new ideas can erode the discipline of "ship the current build queue."
3. **Specific buyer** — None internal. v1 is an operator-only artifact. The marketable transparency-surface variant ("here is what NorthStar is watching") is a separate idea — explicitly out of scope of this row.
4. **Cost of inaction** — Real but bounded. NorthStar's wedge (auditability + deterministic detectors + per-tenant tuning + reversibility + evidence depth) is independent of the AGI-vs-agentic debate; the wedge wins regardless of frontier movement. `THREAT_INTEL_LOG.md` already exists and was refreshed 2026-05-25 with attacker-technique threat-intel; that is the closest existing surface but it does not cover AI / agent landscape shifts. So cost of inaction is moderate (12-month risk of stale architecture or missed MSP-buying-pattern shifts), not catastrophic.
5. **Cheaper proof first** — Yes, and it is a one-shot exercise. Run the intake **once now**, using a starter source list (CISA advisories, abuse.ch, KuppingerCole / Mordor reports, top 3-5 AI-research feeds Matt selects, and the MSP-channel news already cited in `THREAT_INTEL_LOG.md`). Count surfaced candidates that would pass an initial sniff test for full gate evaluation. Decision rule: 0-1 → defer the recurring discipline indefinitely (ad-hoc reviews suffice); 2-3 → commit to a quarterly cadence; 4+ → commit to a monthly cadence.
6. **Existing competitor** — Mandiant, Microsoft Threat Intelligence, Proofpoint, Recorded Future, and similar publish public threat-intelligence reports at scale. NorthStar cannot compete at that scale and should not try; the internal version is what most boutique-scale teams do informally. Formalizing it (tying it to the existing think_sheet gate) is the differentiator from "we read papers sometimes."
7. **Pre-mortem** — Two scenarios. (i) Passive failure: "Created the Frontier Intake artifact in May 2026. Filled it once. Never opened it again. Three months later missed a major shift in MSP buying patterns; spent the next quarter re-orienting." (ii) Active failure (the more dangerous one): "Ran monthly intake religiously. Surfaced 40 candidate ideas. Stress-tested 12. Promoted 1. Built it. The promoted idea was technically interesting but unrelated to what MSPs actually paid for. Three months of build time lost to research-paper-driven roadmap drift instead of customer-driven roadmap." Mitigation for (ii): the existing 5-axis rubric's Strategic Fit and Revenue Path axes already weight customer-relevance heavily, so frontier candidates that fail those axes naturally drop out. The discipline only fails if the rubric is bypassed.

**Decision recorded:** **Revisit / live park (score 5/10).** v1 scoping is process-only with no runtime component. Run the intake once now (cheaper proof, one-shot exercise) and let the result decide the cadence. Cadence rule: 0-1 surfaced candidates → defer recurring discipline; 2-3 → quarterly; 4+ → monthly. More ambitious shapings (runtime intake agent, public transparency surface) are out of scope here and earn their own rows only if v1 evidence warrants them. The vocabulary boundary recorded under the AGI-Adjacent decomposition extends to this idea: "AGI" / "AGI-adjacent" framing from source feeds does not enter NorthStar's product, outreach, spec, or bible voice.

---

### Cyber Insurance Evidence Package (2026-05-25)

Surfaced from the 2026-05-25 Frontier Intake Review #1 as Candidate 3 (cleanest wedge alignment of the five candidates). Selected by operator on 2026-05-25 evening as next gate firing on the basis of highest earnings potential. Buyer-ready bundle that packages existing NorthStar artifacts into a quarterly or annual deliverable specifically structured to answer 2026 cyber-insurance underwriting questions for the email-security control surface. **Carrier-agnostic format; explicit scope boundary as "email-fraud + inbox-layer MDR controls" only**; does NOT cover MFA / EDR / backups / IR plans / patch management (those are MSP responsibilities, not NorthStar's). MSP delivers the package to their SMB client; SMB submits with their underwriting application.

1. **Failure mode** — Four plausible failure modes. (i) **Decoration risk:** package looks comprehensive but underwriters never read it because they only check yes/no boxes (MFA: yes/no, email security: yes/no); the "evidence depth" turns out to be illusory differentiation. (ii) **Email-narrow risk:** underwriting questions cover MFA, EDR, backups, IR plans, etc. — most of which are not NorthStar's surface. The package looks insufficient on its own and the MSP has to assemble the rest from other vendors; NorthStar gets blamed for the gaps. (iii) **Per-carrier fragmentation:** each carrier asks slightly different questions. The package needs per-carrier customization that NorthStar can't scale; by month 6 there are 8 variants always slightly out of date. (iv) **Vocabulary leak:** cyber-insurance language ("attestation," "control efficacy," "regulatory mapping") drifts into NorthStar's voice and contaminates outreach with carrier-jargon that doesn't sound like Matt.
2. **Hidden cost** — Real engineering after the spec is signed: package generation logic that pulls existing artifacts (Inbox Shield monthly report, Blackboard logs, Decision Auditor logs, signed §11 specs index, lift-only invariant test results, Two-Channel Confirmation enforcement records, cross-tenant isolation evidence, kill-switch evidence) and assembles them into a cohesive bundle; per-question mapping table from NorthStar artifacts to common 2026 underwriting questions; underwriter-grade quality bar on existing artifacts (redaction completeness, attestation-style language, signed timestamps); renewal cadence logic (quarterly? annual? on-demand?); MSP delivery mechanism (PDF? branded landing page? evidence vault?). Realistic estimate after spec is signed: 2-3 weeks of engineering. Real research time before the spec: pulling actual underwriter checklists from Nuronus + Data Centre Solutions + GetCybr 2026 sources.
3. **Specific buyer** — Primary: MSPs assembling evidence for their clients' underwriters (local target list captured 2026-05-25 in `THREAT_INTEL_LOG.md`: Carpathia IT, NetDNA, EC Managed IT, IT Works MSP BC, SFY IT, Good IT). Secondary: SMB end-clients with a renewal coming up. Tertiary (audience, not buyer): cyber-insurance underwriters reviewing applications. The framing flip is "we have inbox-layer MDR" (vague) → "we deliver quarterly cyber-insurance evidence bundles for your clients' email-fraud controls" (sharp pitch with explicit value prop).
4. **Cost of inaction** — Continued slow MSP onboarding (REVENUE_MAP Lane 3 currently at 0/7 milestones because nobody's been called yet). Existing pitch is "we detect fraud" — accurate but not differentiated from Microsoft Defender, Abnormal, KnowBe4, or generic email-security gateways. Without the evidence-package framing, NorthStar competes on detector quality, which is technical argument MSPs are not paid to evaluate. With the framing, NorthStar competes on a buyer-readable artifact that maps to a known annual MSP pain point (renewal underwriting). Real revenue cost.
5. **Cheaper proof first** — **Yes, and it is critical.** Existing artifacts are already drafted: `Inbox_Shield_Sample_Monthly_Report.md`, `Acme_Effective_Parameter_Report_Demo.md`, `Inbox_Shield_Daily_Digest_Demo.md`. Cheaper proof = take ONE of these to ONE local MSP discovery call, frame it as "this is what we deliver quarterly to support your clients' cyber-insurance renewals," and ask: "would your clients pay $X/month for this?" Binary go/no-go signal: if 1+ of 3 MSPs in discovery says "yes" or "tell me more," framing earns a spec-first deep dive. If 0/3 say yes, framing doesn't work — reshape or drop. Cost of cheaper proof: ~30 min per discovery call, no engineering. **The cheaper-proof MSP discovery activity is also the existing REVENUE_MAP Lane 3 work** — running this proof advances both the candidate gate AND the bottleneck Lane 3 milestones simultaneously. Two-for-one.
6. **Existing competitor** — General compliance platforms (Vanta, Drata, Tugboat Logic, Apptega, AuditBoard) sell SOC2/HIPAA/PCI evidence automation; some have cyber-insurance modules. KnowBe4 sells security-awareness underwriting-readiness packages. MSPs themselves often hand-assemble evidence packages from multiple vendors (Microsoft Defender, KnowBe4, Veeam, etc.). **No vendor specializes in an EMAIL-FRAUD evidence bundle as a standalone offering.** NorthStar's wedge: deepest evidence specifically for email fraud, deterministic and auditable, packaged for MSP delivery, branded for the underwriter audience. Not competing with general compliance platforms — sliding under them as "the email-fraud module of the broader compliance package the MSP is already assembling."
7. **Pre-mortem** — Two plausible failure scenarios. (i) "Built the package per-carrier. Each carrier asked slightly different questions. By month 6 there were 8 variants and all of them were slightly out of date for the current carrier requirements. Stage A team got pulled into compliance maintenance instead of detector improvement." Mitigation: single carrier-agnostic format with explicit "see your carrier's specific questions for additional details" disclaimer; refuse to maintain per-carrier variants. (ii) "MSPs liked the pitch in discovery calls. Underwriters never read the package because they only checked yes/no boxes. Six months later realized the differentiation was illusory." Mitigation: cheaper-proof discovery calls FIRST. If MSPs don't get traction with the package framing, abandon it before engineering.

**Decision recorded:** **Promote with cheaper-proof-first guidance (score 10/10).** Score reflects directly-advances-build-arc + direct paid deliverable in 90 days + clean Foundation Fit + client-facing artifact + fits active arc. **Spec drafting is gated on cheaper-proof MSP discovery validation.** Run 1-3 local MSP discovery calls using existing artifacts framed as "cyber-insurance evidence bundle for email-fraud controls"; binary go/no-go on whether the framing earns a spec-first deep dive. **The cheaper-proof activity doubles as REVENUE_MAP Lane 3 milestone work** — two-for-one productivity. Vocabulary boundary: "AGI" / "AGI-adjacent" framing does not enter the package; cyber-insurance vocabulary ("attestation," "control efficacy") gets a translation pass to plain English before any client-facing surface ships.

---

## Sub-question stress test — Client-facing 5-axis Email Scoring Rubric §10 (2026-05-25)

The rubric idea passed the idea-level stress test on 2026-05-23. The spec draft `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` then surfaced five sub-questions in §10 that bake into the §11 lockdown if signed. Operating discipline says those sub-questions get stress-tested before signature, the same way ideas do before promotion.

Each sub-question goes through the standard 7-axis test and ends with a recorded verdict. The verdicts then move into §2 of the spec as locked decisions; §10 becomes "resolved."

### Q1. Equal axis weights vs weighted axes for v1

1. **Failure mode** — Equal weights treat a `2` in `origin_timing` (currently the thinnest evidence axis) the same as a `2` in `vendor_payment_history` (strongest financial signal), so total can over- or understate risk relative to where the real evidence sits. Weighted axes pick weights now without per-axis FP/FN data, baking speculation into the contract.
2. **Hidden cost** — Weighted requires documenting and justifying every weight, retesting weights every time a new detector lands, and re-signing the spec on weight changes. Equal is one rule with one number.
3. **Specific buyer** — MSPs reading monthly reports want a quick "where's the risk concentrated" view; both schemes deliver that via per-axis bars. Total reinforces the recommended action either way.
4. **Cost of inaction** — Ship equal wrong → simple v2 weight change once we have real per-axis FP/FN data. Ship weighted wrong → harder to walk back since clients learned the weighted total.
5. **Cheaper proof first** — Yes. We don't have per-axis FP/FN data yet. Equal weights is the conservative default; weighted needs data we won't have until the rubric ships.
6. **Existing competitor** — Microsoft Defender Secure Score uses weighted categories, but Defender has years of per-control telemetry behind those weights. Most BEC tools expose opaque numeric scores with no per-axis weighting at all.
7. **Pre-mortem** — "We picked equal weights because we lacked the per-axis evidence to weight differently. v2 adjusted weights with real data. Equal weights was a defensible starting position."

**Verdict:** Equal weights for v1. Weight revision deferred to v2 and gated on real per-axis FP/FN evidence collected after rubric ships. (D13.)

---

### Q2. Fixed axis order for client reports

1. **Failure mode** — Clients learn an order; reordering later confuses them. Fixed order may also be read as priority ranking, which it is not.
2. **Hidden cost** — Effectively zero. One line in the spec, one renderer constant.
3. **Specific buyer** — MSPs reading monthly reports want a stable layout across clients and across months.
4. **Cost of inaction** — Variable order across reports = visible drift, lost trust. Variable order across emails = harder operator pattern recognition.
5. **Cheaper proof first** — Not needed. Fixed order is the conservative default; the failure modes of *not* fixing order are obvious and asymmetric.
6. **Existing competitor** — Defender, Mimecast, and Proofpoint all use fixed-order tile layouts in client-facing severity panels.
7. **Pre-mortem** — "Fixed order was read as a priority ranking even though we said it wasn't, so an axis at position 1 was assumed most important. Mitigated by adding a one-line disclaimer next to the rubric: 'Order is fixed for stability, not priority.'"

**Verdict:** Fixed axis order for v1, with an explicit "order is fixed for stability, not priority" line in the rendering contract so it isn't misread as a ranking. (D14.)

---

### Q3. `why_this_score` max length: 220 vs 160 chars

1. **Failure mode** — Too short = explanations feel cut off, miss real context. Too long = invites padding, bloats reports, encourages model-style verbosity that clients skim past.
2. **Hidden cost** — 160 forces tighter writing; 220 is more flexible but invites copy-fluff. Either limit must be enforced as a hard validator, not a guideline.
3. **Specific buyer** — SMB owners reading monthly reports want short, scannable sentences. MSPs writing internal notes occasionally want more room.
4. **Cost of inaction** — At rubric scale, 5 axes × ~60 chars difference = ~300 chars per email. Across a 200-email monthly digest, that's ~60KB of difference. Real, but not enormous.
5. **Cheaper proof first** — Yes. Write the same five real explanations under both limits. See whether 160 truncates legitimate content or whether 220 just absorbs slack.
6. **Existing competitor** — Security UI tooltip / short-explanation conventions usually sit at 140–180 chars. Notification-style UX research suggests ~160 is the readability sweet spot.
7. **Pre-mortem** — "We picked 160 and discovered some legitimate explanations needed 200; we widened in v2 and the upgrade path was clean because nothing broke when we relaxed the bound."

**Verdict:** 160 chars for v1. Document the explicit upgrade path: a v2 spec revision may relax to a higher cap (proposed 220) **only** if v1 production data shows ≥ 5% of explanations truncating useful content. (D15.)

---

### Q4. Show `axis_total` to clients, or only per-axis scores + recommended_action

1. **Failure mode** — Showing total = client anchors on "5/10" and skips per-axis context. Hiding total = client mentally aggregates differently from how the system aggregated, drifting from the real evidence.
2. **Hidden cost** — One additional line in the rendered output. Trivial.
3. **Specific buyer** — Both MSP and SMB owner want a headline summary they can scan in two seconds.
4. **Cost of inaction** — If the client computes their own informal total and it disagrees with the system's, trust degrades. Showing the system's total prevents that.
5. **Cheaper proof first** — Yes. Render two mock reports, one with total visible and one without. Show MSPs in discovery calls and observe which is read more clearly.
6. **Existing competitor** — Defender (Secure Score), Mimecast (severity labels), most BEC tools — almost all show a top-line number alongside the breakdown. Hiding the total would be unusual.
7. **Pre-mortem** — "Showing the total caused clients to anchor on it and skip axis detail. Mitigated by giving `recommended_action` (`safe`/`needs_review`/`block`) the most prominent visual position and using axis breakdown — not the total — as the primary reasoning surface. Total exists, action leads."

**Verdict:** Show `axis_total` for v1, but rendering contract pins `recommended_action` as the most prominent element and uses the per-axis breakdown as the primary reasoning surface. The total is a navigation aid, not the headline. (D16.)

---

### Q5. v1 surface: report-only / monthly digest, or also per-email operator view

1. **Failure mode** — Report-only = an operator triaging a single flagged email today has nowhere to see the rubric and falls back to internal evidence. Per-email = two rendering surfaces, twice the places where rubric and internal score must agree, more code-path drift risk.
2. **Hidden cost** — Per-email view requires touching the operator triage UI and the digest. Report-only is one renderer.
3. **Specific buyer** — Report-only directly serves MSP monthly reviews (the named $300 deliverable). Per-email serves operator-side triage, which is current internal usage.
4. **Cost of inaction** — If v1 is report-only and an operator wants to explain a single flagged email, they fall back to internal evidence — which is the current state, so no regression.
5. **Cheaper proof first** — Yes. Ship report-only first. Watch the next 5 MSP discovery calls. If "I want to see the same rubric on one email I'm holding in my hand" comes up, add per-email in v1.1.
6. **Existing competitor** — Mature email-security tools have both a report surface and a per-email surface, but most shipped report surface first.
7. **Pre-mortem** — "Report-only first meant operators occasionally fell back to internal evidence to explain a single email. Per-email view added in v1.1 once one MSP raised it. Shipping order was correct."

**Verdict:** Report-only / monthly digest for v1. Per-email operator surface explicitly deferred to v1.1, gated on MSP discovery feedback. (D17.)

---

### Verdict summary (locks into spec §2 as D13–D17)

| # | Sub-question | Locked v1 verdict |
|---|---|---|
| D13 | Axis weighting | Equal weights for v1; weight revision deferred to v2 and gated on real per-axis FP/FN data. |
| D14 | Axis order | Fixed order for v1; rendering contract includes "order is fixed for stability, not priority" disclaimer. |
| D15 | `why_this_score` max length | 160 chars for v1; documented upgrade path to 220 if production data shows ≥ 5% useful truncation. |
| D16 | `axis_total` visibility | Visible to clients in v1; `recommended_action` is the most prominent element; per-axis breakdown is the primary reasoning surface. |
| D17 | v1 client-facing surface | Report-only / monthly digest in v1; per-email operator view deferred to v1.1, gated on MSP discovery feedback. |

These verdicts move into §2 of `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` as D13–D17 and replace §10's "open questions" status with "resolved 2026-05-25 by stress test."

---

## Sub-question stress test — Callback Phishing / TOAD §10 (2026-05-30)

The Callback Phishing / TOAD body-language detector idea passed the idea-level stress test on 2026-05-24 (row above; `ST = Y`). The spec draft `4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md` then surfaced five sub-questions in §10 that bake into the §11 lockdown if signed. Same discipline as the rubric §10 stress test (above, 2026-05-25): each sub-question goes through the standard 7-axis test, the verdict is recorded here, and the verdict then moves into §2 of the spec as a new D-decision. §10 becomes "resolved." §11 signature still pending after that — these stress-test verdicts do **not** sign the spec.

### Q1. v1 phrase-category list — keep the §3 five, add `mfa_bypass_call`, or remove `support_line_substitution`?

1. **Failure mode** — Adding `mfa_bypass_call` to v1 without real-traffic evidence locks a category whose phrasing overlaps with legitimate IT-helpdesk mail ("call us to reset your MFA"); high false-positive risk on benign helpdesk traffic. Removing `support_line_substitution` loses a documented TOAD play (attacker tells the recipient to "call our updated support line" with an attacker number) that none of the other four categories cleanly cover. Keeping the §3 five preserves the public contract Matt locked in §5 schema (the `category_name` `Literal`) and matches the stress-test answer source on 2026-05-24.
2. **Hidden cost** — Adding a category requires fixture coverage, pattern variants in code, gate-test updates, and a §8 test row per category. Removing a category breaks the §5 schema `Literal` and requires a schema migration. Holding the v1 list and deferring additions to v1.1 is the cheapest move and matches D2's "closed phrase-category vocabulary in v1" rule.
3. **Specific buyer** — Same MSP archetype as the parent idea: payroll bureaus, accounting firms, real-estate offices. The v1 five cover the strongest published TOAD shapes; adding `mfa_bypass_call` mostly helps IT-helpdesk-heavy buyers (different archetype). Removing `support_line_substitution` weakens the pitch for AP buyers receiving fake vendor-support emails.
4. **Cost of inaction** — Not adding `mfa_bypass_call` in v1 means MFA-fatigue callback variants fall back to ransomware-precursor body-language detection + the rubric's `recommended_action`; not silent. Not removing `support_line_substitution` means false-positive risk is bounded by D2's closed-vocabulary discipline + §4.1 banding (single-category fire only lifts to 50 `needs_review`, not `block`).
5. **Cheaper proof first** — Yes. Ship the v1 five, run the detector against the bounded fixture set, watch the next 5 MSP discovery calls. If MFA-fatigue callback shapes show up as a real miss, add `mfa_bypass_call` as a v1.1 spec addendum (one §11 amendment, one schema-`Literal` extension, one fixture row). Cheaper than locking the category now without evidence.
6. **Existing competitor** — Next-gen email security (Abnormal, Avanan, Microsoft Defender) does TOAD-shape detection but rarely publishes its category list. v1's named, closed five is the differentiator; expanding before evidence weakens the auditability story.
7. **Pre-mortem** — "We added `mfa_bypass_call` to v1 without real traffic. The pattern caught a wave of legitimate IT-helpdesk mail at MSPs running mixed-tenant inboxes. Mitigated by holding v1 to the five and gating additions on real-traffic miss reports."

**Verdict:** Keep the §3 five v1 phrase categories (`call_now_pressure`, `do_not_use_known_channel`, `voice_only_finalize`, `support_line_substitution`, `payment_redirect_call`). Do **not** add `mfa_bypass_call` in v1. Do **not** remove `support_line_substitution`. Adding or removing a category is a v1.1 spec addendum gated on real-traffic miss / false-positive evidence after the detector ships. (D11.)

---

### Q2. Numeric `callback_phishing_score` field, or flag + categories + `recommended_risk_floor_lift` only?

1. **Failure mode** — Adding a numeric `callback_phishing_score` creates a second internal score competing with `risk_score` and `recommended_risk_floor_lift`; clients and operators learn another number that has to stay consistent with the §4.1 band table forever. Sibling detectors (FSL, document-metadata) carry their own numeric scores, but those scores feed a richer overlay shape; callback phishing's signal is closer to binary-with-tiers and the §4.1 banding already encodes the tiers via `recommended_risk_floor_lift`.
2. **Hidden cost** — A numeric score requires a published computation rule, a validator, fixture coverage for every band, a rendering contract, and per-axis drift discipline (the same drift-detection burden the rubric carries). Flag + categories + lift is one fewer surface and one fewer source of drift.
3. **Specific buyer** — MSPs reading monthly reports want the `recommended_action` + per-axis `origin_timing` lift; they do not want a fourth detector-specific number on the page. Adding a numeric score would have to be hidden from rendering anyway to avoid clutter (§6 already bounds what surfaces).
4. **Cost of inaction** — Shipping without a numeric score means future analytics ("how many callback-phishing fires hit floor 50 vs 70 vs 85") work from `recommended_risk_floor_lift` + `categories` length, which is already enough signal. v1.1 may add a numeric score if production telemetry needs it; the upgrade path is additive.
5. **Cheaper proof first** — Yes. Ship flag + categories + lift in v1. If MSP discovery or internal analytics show a real gap that a numeric score would close, add it in v1.1 as an additive schema field.
6. **Existing competitor** — Most email-security tools expose opaque numeric severity scores; NorthStar's differentiator is auditable signal-by-signal evidence, not another opaque number. A binary `fired` + structured `categories` matches the rubric's per-axis transparency model.
7. **Pre-mortem** — "We added a numeric `callback_phishing_score` in v1, the §4.1 band table evolved, and the score drifted from the band-implied tier in three releases. Mitigated by not introducing a separate numeric score until production data forces it."

**Verdict:** No numeric `callback_phishing_score` field in v1. Score-emission contract stays: `fired` (bool) + `categories` (tuple) + `recommended_risk_floor_lift` (int, banded per §4.1) + `out_of_band_verification_required` (bool). A numeric score is deferred to v1.1+ and gated on production evidence that the band-implied tier is insufficient signal. (D12.)

---

### Q3. Rubric `origin_timing` mapping — lift to 1 only, or 1/2 with the §4.1 banding?

1. **Failure mode** — A flag-only "lifts to 1" mapping under-weights the strongest callback-phishing hits (multi-category fire + payment overlap, which §4.1 already bands to lift 85) on the client-facing rubric, so the per-axis surface understates risk relative to the internal `recommended_risk_floor`. A 1/2 mapping that uses `risk_score >= 50` as the threshold misses cases where the callback signal itself is the strongest signal on a benign-looking email (the upstream `risk_score` may still be below 50 before the floor lift applies).
2. **Hidden cost** — A 1/2 mapping requires the rubric `origin_timing` mapper to read either `risk_score` or `recommended_risk_floor_lift`, both of which the rubric already consumes; no new dependency. A "lift to 1 only" rule is one branch; a 1/2 rule that also reads `recommended_risk_floor_lift >= 70` is two branches. Negligible code cost either way; the spec cost is the §11.1 amendment to the rubric, which is required regardless because the rubric spec is §11-SIGNED and any addition to its evidence-tag set is a signed amendment.
3. **Specific buyer** — MSPs reading the rubric want axis severity to track real evidence severity. A 1/2 mapping that escalates with the §4.1 band aligns the per-axis surface with what the rest of the system already says about the same email.
4. **Cost of inaction** — A "lift to 1 only" mapping in v1 keeps the rubric understated for high-severity callback hits; clients reading the rubric for the most severe TOAD attacks see `origin_timing = 1` while `recommended_action = block`. Bad alignment between two adjacent surfaces is a trust failure mode the rubric spec is supposed to prevent.
5. **Cheaper proof first** — Not needed. The mapping is deterministic; the §4.1 band table is locked; the rubric spec already supports per-evidence-tag mapping logic. Using both `risk_score >= 50` AND `recommended_risk_floor_lift >= 70` as alternative triggers for the score-2 escalation is the smallest rule that aligns the two surfaces.
6. **Existing competitor** — Defender, Mimecast, and other rubric-style surfaces typically escalate axis severity in lockstep with overall severity; NorthStar's rubric should match that intuition.
7. **Pre-mortem** — "We mapped callback-phishing to `origin_timing = 1` only, missed the multi-category / payment-overlap escalations, and an MSP reading the monthly report saw a misleading `origin_timing` for a `block` action. Mitigated by the 1/2 mapping that uses the callback band as a second trigger."

**Verdict:** Use the 1/2 `origin_timing` rubric mapping:
- `callback_phishing_pattern` present → `origin_timing` lifts to at least 1.
- `callback_phishing_pattern` present **AND** (`risk_score >= 50` **OR** `recommended_risk_floor_lift >= 70`, i.e. the higher callback bands per §4.1) → `origin_timing` maps to 2.

This is a §11.1 amendment to `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` that lands **with** the TOAD detector's §11 signature, not before — the rubric spec stays signed but unamended until the TOAD detector signs. (D13.)

---

### Q4. Read `body_plain` only, or also read `body_html`?

1. **Failure mode** — Reading only `body_plain` misses callback-phishing lures that render styled "Call now!" buttons or hidden phone-number digits inside HTML; the detector under-fires on HTML-only TOAD mail. Reading `body_html` requires a parser, opens a new attack surface (HTML parser CVEs, XSS-shaped patterns inside the parser), and breaks the existing project convention that detectors stay on `body_plain` (header divergence, prompt injection, FSL all read `body_plain` only).
2. **Hidden cost** — `body_html` parsing adds a parser dependency, HTML-sanitization discipline, fixture coverage for parser-edge cases (malformed HTML, encoding quirks, CDATA, comments hiding text), and a new failure mode (`html_parse_error`) the detector has to handle. `body_plain` only is the existing convention and costs nothing new.
3. **Specific buyer** — Same MSP archetype. MSPs whose tenants run modern mail clients almost always have `body_plain` populated alongside `body_html`; v1 sees the same lure text in both for the vast majority of mail. The HTML-only TOAD case is a known edge that v1.1+ can address with evidence.
4. **Cost of inaction** — Not reading `body_html` in v1 misses HTML-only TOAD lures that strip the plain-text alternative. Bounded by the rubric `origin_timing` axis still surfacing other evidence and by the `recommended_action` still being driven by `risk_score` floors from upstream detectors. If real traffic shows HTML-only TOAD lures slipping through, v1.1 adds `body_html` as a spec-first addendum.
5. **Cheaper proof first** — Yes. Ship `body_plain` only in v1, instrument the detector to log when `body_html` is non-empty but the detector did not fire on `body_plain`, and let production data prove (or disprove) the HTML-only miss rate.
6. **Existing competitor** — Mature email-security tools (Defender, Mimecast, Proofpoint) parse HTML routinely. NorthStar's wedge is auditability + deterministic detectors; adding HTML parsing in v1 weakens the "one parser, one input field" simplicity that the existing detectors share.
7. **Pre-mortem** — "We added `body_html` to v1, an HTML-parser bug crashed the detector on malformed mail from a major vendor, and the detector silently went OFF for that tenant. Mitigated by holding v1 to `body_plain` and gating `body_html` on real evidence that HTML-only TOAD lures are a measurable miss."

**Verdict:** v1 reads `body_plain` only. `body_html` is deferred to v1.1+ and gated on real evidence (production telemetry or MSP miss reports) that HTML-only TOAD lures slip through the `body_plain` path. (D14.)

---

### Q5. Reserve `phone_number_assessment` as a typed forward-compat slot, or omit it entirely until Part 2 ships?

1. **Failure mode** — Reserving the slot in v1 locks Part 2's design (the `PhoneNumberAssessment` payload shape, the embedding contract, the `None`-default semantics) before Part 2's spec exists. If Part 2's actual design needs a different shape (e.g. a list of per-number assessments, or an integration with the Vendor Baseline Store enum revision that returns different metadata), v1 has to migrate — defeating the "forward-compat" intent. Omitting the slot in v1 leaves Part 2 free to choose its own schema shape through its own §11-signed spec.
2. **Hidden cost** — Reserving the slot requires a forward-compat validator (v1 must reject any non-`None` value), a §8 gate test (#12 in the current draft), and a documented "this field will be filled by Part 2" comment. All of those have to be revisited when Part 2 actually lands. Omitting the slot is one fewer field, one fewer validator, one fewer gate test, and one less assumption baked into the v1 contract.
3. **Specific buyer** — No buyer cares about the slot in v1 (the field is always `None`). Buyers care about whether the detector fires correctly on the body-language slice. The slot is internal API surface only.
4. **Cost of inaction** — Omitting the slot means Part 2, when it ships, adds a new schema field through its own signed spec (matching the existing additive-only schema discipline used for every detector to date — `EmailAnalysisPayload.callback_phishing_assessment` was itself added this way). No migration pain because the field is brand-new to clients of the schema.
5. **Cheaper proof first** — Yes. The cheaper move is to ship v1 without the slot, let Part 2's spec (gated on the Vendor Baseline Store `vendor_callback_phone_number` enum revision per `4. Product_Roadmap/Vendor_Baseline_Signal_Type_Enum_Revision_Deep_Dive.md`) design the phone-number assessment shape it actually needs, then add it through its own spec-first lane.
6. **Existing competitor** — Not applicable; this is an internal-schema decision.
7. **Pre-mortem** — "We reserved `phone_number_assessment: None` in v1, Part 2 needed a list-shaped payload, and we had to migrate the v1 contract anyway. Mitigated by omitting the slot and letting Part 2's signed spec choose the shape."

**Verdict:** Omit `phone_number_assessment` from the v1 `CallbackPhishingAssessment` schema. Part 2 (if it ships) adds the field through its own §11-signed spec via the Vendor Baseline Store enum revision path (`vendor_callback_phone_number` is already proposed in `4. Product_Roadmap/Vendor_Baseline_Signal_Type_Enum_Revision_Deep_Dive.md`). v1 schema discipline stays additive-only; Part 2 ships as a clean schema extension, not a v1 migration. (D15.)

---

### Verdict summary (locks into spec §2 as D11–D15)

| # | Sub-question | Locked v1 verdict |
|---|---|---|
| D11 | v1 phrase-category list | Keep the §3 five (`call_now_pressure`, `do_not_use_known_channel`, `voice_only_finalize`, `support_line_substitution`, `payment_redirect_call`). Do not add `mfa_bypass_call`; do not remove `support_line_substitution`. Additions/removals are v1.1 spec addenda gated on real-traffic evidence. |
| D12 | Numeric `callback_phishing_score` | Not in v1. Emission contract = `fired` + `categories` + `recommended_risk_floor_lift` + `out_of_band_verification_required`. Numeric score deferred to v1.1+ and gated on production evidence. |
| D13 | Rubric `origin_timing` mapping | 1/2 mapping. Present → `origin_timing >= 1`; present AND (`risk_score >= 50` OR `recommended_risk_floor_lift >= 70`) → `origin_timing == 2`. Lands as a §11.1 amendment to the rubric spec with the TOAD detector's §11 signature. |
| D14 | `body_html` inclusion | v1 reads `body_plain` only. `body_html` deferred to v1.1+ pending real-traffic evidence of HTML-only TOAD lure miss. |
| D15 | `phone_number_assessment` slot | Omit from v1 schema. Part 2 (if it ships) adds the field through its own §11-signed spec via the Vendor Baseline Store `vendor_callback_phone_number` enum revision path. v1 stays additive-only. |

These verdicts move into §2 of `4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md` as D11–D15 and replace §10's "open questions" status with "resolved 2026-05-30 by stress test." §11 signature is **still pending** — these stress-test verdicts do not sign the spec.

---

## Sub-question stress test — Email Security Testing & Evidence Framework §10 (2026-05-31)

The Email Security Testing & Evidence Framework draft `4. Product_Roadmap/Email_Security_Testing_Evidence_Framework_Deep_Dive.md` surfaced nine sub-questions in §10. Q2, Q8, Q9 are already resolved (D23, D21, D22). This pass stress-tests Q1, Q3, Q4 — the three §10 explicitly flagged as needing a stress-test verdict before the v1 implementation pass starts — and records lighter verdicts for Q5, Q6, Q7. Same discipline as the prior two passes (rubric §10 2026-05-25 and TOAD §10 2026-05-30): each sub-question goes through the standard 7-axis test, the verdict is recorded here, then moves into spec §2 as a new D-decision. §10 entries flip to "resolved." §11 signature is still pending after that — these verdicts do not sign the spec.

### Q1. Exact `confidence_bucket` bounds — draft proposal `[0,25] / [26,60] / [61,100]` or recalibrate now?

1. **Failure mode** — Recalibrating the bucket bounds *before* the v1 implementation runs against real fixtures means picking new numbers from intuition rather than evidence; calibration drift is the failure mode the §2 D-decisions are meant to prevent. Keeping the draft proposal preserves a stable target for v1 and forces any future re-calibration to cite empirical fixture distribution as evidence. The competing risk — locking bounds that turn out to be wrong — is bounded because the framework is pre-signature and §11-revision can re-tune the bounds after real data accumulates.
2. **Hidden cost** — A new bound proposal requires re-running every example in §8.2 against the new boundaries, updating the `overconfident` carve-out semantics, and re-justifying the change in §2. Sticking with the draft proposal is zero new work and matches the §8.2 example text already published.
3. **Specific buyer** — Same MSP / cyber-insurance archetype as the parent spec. Buyers care about a single intuitive split: low ≈ "didn't take a strong position," medium ≈ "moderate," high ≈ "confident," overconfident ≈ "confident and wrong." The draft split matches that intuition and is consistent with the existing runtime `risk_score` bands the rubric already publishes (50 / 70 / 85).
4. **Cost of inaction** — Not locking the bounds now leaves Q1 open at §11, which violates the user's "close to §11-signable" goal. Locking the proposal with an explicit recalibration gate is the cheapest closure that does not foreclose evidence-based revision.
5. **Cheaper proof first** — Yes. Ship the draft `[0,25] / [26,60] / [61,100]` split as v1, instrument run output to publish the empirical distribution per bucket in the dashboard `confidence_bucket_distribution` metric (already §8.5), and gate any bound revision on ≥60 real cases distributed across all four buckets + a §11-revision cycle + an operator log entry naming the evidence. The metric already exists; the revision discipline is the cheap addition.
6. **Existing competitor** — Email-security competitors rarely publish calibration bucket boundaries at all (Mimecast, Defender, Abnormal expose opaque severity scores). NorthStar's wedge is auditable signal-by-signal evidence; a published, named four-bucket calibration with explicit revision discipline is a differentiator. Drifting the bounds quietly between runs would erode that differentiator.
7. **Pre-mortem** — "We left Q1 open at §11, the v1 implementation invented its own boundaries, and three different runs reported different `overconfident_rate` numbers depending on which boundary version was in effect. Mitigated by locking D24 with the exact draft bounds and gating revision on real fixture evidence + §11-revision cycle."

**Verdict:** Lock the draft bounds as v1. `confidence_bucket` boundaries are exactly `[0,25] / [26,60] / [61,100]` for `low` / `medium` / `high`; `overconfident` is the subset of `high` whose `verdict_match` is not `exact`. Recalibration requires (a) ≥60 real fixture cases distributed across all four buckets, (b) a §11-revision cycle, and (c) an operator entry in `PROJECT_ACTIVITY_LOG.md` naming the empirical distribution evidence. Pre-§11-signature drift is forbidden. (Locks into spec §2 as D24.)

---

### Q3. Should `adjacent` verdict mismatches count partial credit toward `accuracy_supported_only`, or remain strictly excluded?

1. **Failure mode** — Partial credit creates a fuzzy accuracy denominator: a single number that says "94% accurate" can mean "exactly correct 94% of the time" or "exactly correct 70%, adjacent 24%" depending on the credit weighting. Two runs reporting the same accuracy can have very different real verdict quality. The §3 core philosophy explicitly warns against "clean-looking metrics that hide capability gaps"; partial credit is exactly that pattern at the verdict layer. Strict exclusion keeps the accuracy number honest and surfaces adjacency separately via `verdict_match_distribution` (§8.5) so the operator still sees the adjacency signal — just not averaged into accuracy.
2. **Hidden cost** — Partial credit requires picking a weight (0.5? 0.33? per-axis?), publishing that weight, justifying it, and re-justifying it whenever the rubric ladder changes (the rubric is §11-signed and the ladder shape is fixed, but the underlying severity meaning can shift with new evidence types). Strict exclusion has zero parameter to maintain.
3. **Specific buyer** — MSPs and cyber-insurance underwriters reading buyer-facing accuracy metrics want a number with a clear denominator. "Exact match" is the cleanest denominator. The `verdict_match_distribution` four-value breakdown (exact / adjacent / mismatch / unscored) preserves the adjacency signal in a way buyers can read at a glance ("we were exactly right 80%, one step off 12%, two-plus steps off 8%") — better than a single weighted number that hides the breakdown.
4. **Cost of inaction** — Leaving Q3 open at §11 violates the "close to §11-signable" goal. Locking strict exclusion now keeps accuracy honest and preserves operator-friendly adjacency surfacing. The competing v1.1 path (introducing weighted credit later) is still open via §11-revision if evidence ever supports it; locking strict exclusion now does not foreclose that path.
5. **Cheaper proof first** — Yes. Strict exclusion is the cheaper-to-prove default. If the operator later finds the `verdict_match_distribution` breakdown is genuinely confusing for buyers and a single weighted score would communicate better, the §11-revision path can introduce credit weighting with evidence in hand. The reverse — starting with credit weighting and trying to back out to strict — would require re-justifying every prior accuracy number.
6. **Existing competitor** — Most ML/eval surfaces use strict exact-match accuracy + a confusion matrix breakdown for nuance. Partial credit for "almost right" is rare outside of subjective NLP evaluation; verdict ladders in security tooling are typically strict.
7. **Pre-mortem** — "We weighted adjacent at 0.5 to look smoother in dashboards, an MSP read 92% accuracy as a confidence signal, but the underlying distribution was 70% exact + 44% adjacent, and the buyer was misled. Mitigated by strict exclusion + four-value distribution surfacing the adjacency separately."

**Verdict:** Strict exclusion. `accuracy_supported_only` and the derived precision / recall / FPR / FNR treat any `verdict_match` ≠ `exact` as incorrect. `verdict_match_distribution` (§8.5) preserves the four-value breakdown so operators see adjacent-vs-mismatch separately, without averaging it into accuracy. (Locks into spec §2 as D25. Confirms the §8.1 formula that already excludes adjacent from the numerator.)

---

### Q4. Regression-tolerance default — `0` pp strict, or `2` pp permissive?

1. **Failure mode** — A `2 pp` permissive default means any single regression run can lose up to two percentage points on any per-metric value silently — and two adjacent runs each losing two pp accumulate four pp of silent drift. Across ten runs, twenty pp of silent drift is possible if the tolerance is never tightened. A `0 pp` strict default forces every drop to be acknowledged: the operator either explicitly widens the tolerance with a recorded reason and expiry, or fixes the regression. Strict-default-with-widening-discipline is the structural prevention of the silent-drift failure mode.
2. **Hidden cost** — `0 pp` strict requires per-subcategory widening discipline whenever the operator legitimately needs to accept a small drop (e.g., a new fixture intentionally tightens the bar, or a one-time numeric jitter at a boundary). The widening is one `PROJECT_ACTIVITY_LOG.md` entry per subcategory naming value, rationale, and expiry. That is small, recorded, auditable cost. `2 pp` permissive has no per-event cost but unbounded compounding drift cost over time.
3. **Specific buyer** — MSPs and cyber-insurance underwriters reading the regression report want to see whether NorthStar is getting better, worse, or holding. A `2 pp` default reports "holding" even when underlying performance is sliding; a `0 pp` default reports honestly. The honesty matches the framework's §3 philosophy.
4. **Cost of inaction** — Leaving Q4 open at §11 means v1 ships without a tolerance number, the implementation defaults to whatever the developer picks, and the choice never appears in a §11-signed surface. Locking `0` makes the choice explicit and named.
5. **Cheaper proof first** — Yes. `0 pp` strict is the cheaper-to-revert default. If real operations show the per-subcategory widening discipline is creating excessive friction with low actual value, the §11-revision path can raise the default. The reverse — defaulting to `2 pp`, then trying to tighten after silent drift accumulates — requires reconciling historical regression reports against the new tolerance, which is expensive.
6. **Existing competitor** — CI / regression-testing surfaces in mature engineering shops default to strict (zero-tolerance) regression with explicit, recorded exceptions. Permissive defaults are the documented anti-pattern in the testing literature; they are how legacy test suites slowly become unreliable.
7. **Pre-mortem** — "We defaulted to `2 pp`, the framework reported 'within tolerance' across six runs while per-category recall slid from 88% to 80%, an MSP asked why the dashboard claimed stability and we had to explain accumulated drift. Mitigated by `0 pp` default + explicit named widening per subcategory with hard expiry."

**Verdict:** Default `0` percentage points. §4.2 regression-tier rule fails any per-metric drop on a previously-passing case. Per-subcategory widening above 0 requires an operator entry in `PROJECT_ACTIVITY_LOG.md` naming subcategory, tolerance value (pp), rationale, and hard expiry. Tolerance widening is high-severity drift; the default forces a conscious decision rather than silent erosion. (Locks into spec §2 as D26.)

---

### Lighter verdicts (Q5, Q6, Q7)

These three sub-questions are not flagged by §10 as needing a pre-implementation stress test; verdicts here are lighter and lock straight into spec §2.

- **Q5 verdict — D27.** Defer red-team mission file structure to the first real mission, but lock the eight minimum required fields (`mission_id`, `scope`, `hypothesis`, `threat_model`, `controlled_synthetic_only_acknowledgement`, `success_criteria`, `scheduled_for`, `operator_authorization`). Field names intentionally avoid `attestation` per the spec's D10 forbidden-language inheritance. Rationale: structure-by-mission preserves the §4.4 organic discipline while preventing the first mission from drifting into freeform notes. Eight fields is small enough to remember; large enough to make every mission auditable.
- **Q6 verdict — D28.** No composite quality score in v1. The §8.5 metric list is the dashboard. Rationale: a composite is the exact failure mode §3 warns against — a clean number that hides capability gaps behind averaging. v1.1+ can introduce a composite if buyer feedback genuinely needs it, gated on operator-stated evidence that the §8.5 list is too noisy for monthly reporting.
- **Q7 verdict — D29.** Lock the Decision Auditor trigger condition: failure cards with `failure_type` ∈ {`schema_violation`, `scope_violation`} are Decision Audit candidates and MUST be linked from the audit-trail event via a new optional `decision_audit_candidate_id` field. The packet shape, the runner integration with `audit_tools/decision_audit_runner.py`, and any dashboard surface for outstanding candidates are v1.1 work and require their own §11-signed spec. v1 marks candidates only; v1 does not run the integration. Rationale: marking is cheap and forward-compatible; running the integration without a separate signed spec is scope creep.

---

### Verdict summary (locks into spec §2 as D24–D29)

| # | Sub-question | Locked v1 verdict |
|---|---|---|
| D24 | `confidence_bucket` boundaries | `[0,25] / [26,60] / [61,100]` for `low/medium/high`; `overconfident` carved from `high` by `verdict_match ≠ exact`. Recalibration requires ≥60 real fixture cases, §11-revision, and operator log entry naming evidence. |
| D25 | `adjacent` partial credit | Strictly excluded from accuracy denominators. `verdict_match_distribution` preserves the four-value breakdown so adjacency stays visible without averaging into accuracy. |
| D26 | Regression-tolerance default | `0` percentage points strict. Per-subcategory widening requires operator `PROJECT_ACTIVITY_LOG.md` entry naming subcategory, value, rationale, hard expiry. |
| D27 | Red-team mission file structure | Defer to first mission; lock eight minimum required fields (`mission_id`, `scope`, `hypothesis`, `threat_model`, `controlled_synthetic_only_acknowledgement`, `success_criteria`, `scheduled_for`, `operator_authorization`); field names intentionally avoid `attestation`. |
| D28 | Composite quality score | None in v1. §8.5 metric list is the dashboard. Composite deferred to v1.1+ gated on operator-stated evidence. |
| D29 | Decision Auditor integration | Lock trigger only (failure_type ∈ {`schema_violation`, `scope_violation`}); add `decision_audit_candidate_id` linkage field. Runner integration, packet shape, dashboard surface are v1.1 with own signed spec. |

These verdicts move into §2 of `4. Product_Roadmap/Email_Security_Testing_Evidence_Framework_Deep_Dive.md` as D24–D29 and flip §10 Q1, Q3, Q4, Q5, Q6, Q7 to "resolved 2026-05-31." §11 signature is **still pending** — these stress-test verdicts do not sign the spec.

---

## Sub-question stress test — Score Sheet Candidate Review & Promotion (Wave 3) §10 (2026-06-03)

Draft under review: `4. Product_Roadmap/Score_Sheet_Candidate_Review_Promotion_Deep_Dive.md` (Wave 3 pre-§11). Governing contracts: signed Wave 1 candidate-emission spec, signed Wave 2 implementation spec + §14 helper-module amendment, Wave 0 internal testing-evidence discipline (draft §12 track taxonomy). Manus email-security research zip reviewed as **context only** — not adopted as repo truth. This pass stress-tests the six aligned structural questions (holding area, 8-item checklist, rejection archive, promotion boundary, in-band proof, forbidden automation) plus §10 open questions. These verdicts support operator §11 prep only — they do **not** sign the spec.

### Q1. Holding area — keep `audit_outputs/score_sheet_candidates/` only, or add a second queue surface?

1. **Failure mode** — A second queue (DB, Blackboard, or `tests/3_evolutionary_sandbox/candidate_pool/`) splits operator attention and invites sync drift: promoted rows without archived packets, or packets promoted without ledger rows. Single pool under `audit_outputs/` matches Wave 1 and the gitignored audit_outputs convention.
2. **Hidden cost** — Second surface needs migration rules, duplicate scanners, and new failure modes. Single directory costs zero new infrastructure.
3. **Specific buyer** — Internal discipline only in v1. MSP/buyer surfaces are out of scope per §7. Operator needs one obvious folder to review after `pre_ship_audit` emits.
4. **Cost of inaction** — Without a named holding area, Manus fiction (`candidate_pool/`, production filters) could re-enter as "helpful" layout. Locking Wave 1 path closes that drift door.
5. **Cheaper proof first** — Yes. List `*.candidate.jsonl` in one folder; defer `review_ledger.py` until §11.
6. **Existing competitor** — CI artifact folders + human promotion gates are standard; crypto ledgers are not required for internal evidence.
7. **Pre-mortem** — "We added a second candidate queue, operators promoted from the wrong copy, and audit reconstruction failed. Mitigated by single holding pool + `promoted/` / `rejected/` archives only."

**Verdict:** Active candidates stay in `audit_outputs/score_sheet_candidates/` until operator moves them to `promoted/` or `rejected/`. No second queue in Wave 3 v1.

---

### Q2. Eight-item checklist — hard gate vs advisory reminder?

1. **Failure mode** — Advisory checklist gets skipped under time pressure; `tool_candidate` rows get copy-pasted to canonical ledger without PII re-check or track mapping. Hard gate forces reject/defer instead of sloppy promotion (authority drift).
2. **Hidden cost** — Hard gate adds operator friction per row. Friction is intentional — promotion is the authority act.
3. **Specific buyer** — N/A v1 internal. Underwriter-facing render still forbidden without separate disclosure spec.
4. **Cost of inaction** — Soft checklist repeats the 2026-05-23 audit-packet lesson at the evidence layer: "looked reviewed" without provable checks.
5. **Cheaper proof first** — Yes. Manual promotion with checklist in spec; script may **prompt** later but not auto-promote.
6. **Existing competitor** — Human-in-the-loop promotion with explicit operator confirmation is the conservative pattern for compliance-adjacent evidence.
7. **Pre-mortem** — "We promoted candidates without re-checking PII; a real email slipped into `finding_summary`. Mitigated by eight-item hard gate + §9.1 refusal."

**Verdict:** All eight Wave 1 §12 checklist items are a **hard promotion precondition**. Fail any item → reject or defer, never promote. (Wording avoids forbidden-language term *attestation*; uses explicit operator confirmation instead.)

---

### Q3. Rejected candidates — archive only, or feed mutation / negative training?

1. **Failure mode** — Auto-feeding rejections into a mutation engine creates feedback loops where one operator mistake trains the system away from valid patterns. Archives without automated downstream use preserve auditability.
2. **Hidden cost** — Negative-training plumbing is Phase 1.4 / sandbox scope, not Wave 3. Archive-only is move + rename + reason text.
3. **Specific buyer** — N/A. Internal audit reconstruction only.
4. **Cost of inaction** — Manus `weakness_reports/rejected_mutations.json` fiction could be imported as mandatory. Explicit reject avoids that.
5. **Cheaper proof first** — Yes. `rejected/` + free-text reason; closed enum deferred to §10.
6. **Existing competitor** — Test frameworks keep failed-case artifacts; few auto-train from operator reject without a signed ML pipeline.
7. **Pre-mortem** — "Rejected false positives trained the emitter away from legitimate vendor-payment cases. Mitigated by archive-only v1."

**Verdict:** Rejections go to `rejected/` with operator-authored reason. No mutation-engine or negative-training hook in Wave 3 v1.

---

### Q4. Promotion boundary — manual copy only, or may a script draft the canonical row?

1. **Failure mode** — Script that writes operator-bearing `recorded_by` or assigns `event_id` without an explicit operator click is auto-promotion drift (Wave 0 §8.14). Even "helpful" draft-and-approve UIs blur the line if the default is one-click promote.
2. **Hidden cost** — `review_ledger.py` is valuable but must be spec-gated. v1 manual promotion has no implementation cost.
3. **Specific buyer** — Evidence rows must reconstruct failure → correction → retest from repo paths alone; automation that skips operator edit breaks that chain's credibility.
4. **Cost of inaction** — Deferring boundary language leaves room for Cursor/Manus to "implement promotion" in the emitter helper.
5. **Cheaper proof first** — Yes. Operator authors/edits row, assigns `event_id`, archives packet; script lists packets only after §11 + build auth.
6. **Existing competitor** — Separation of draft vs signed evidence matches audit trails in regulated tooling.
7. **Pre-mortem** — "The review script promoted 12 rows overnight with `operator-Matt` because the operator left a flag on. Mitigated by manual-only v1 + forbidden automation §10."

**Verdict:** v1 promotion is **manual only**. Future `review_ledger.py` may list, validate checklist, and **draft** rows — it must not assign `event_id`, set operator-bearing `recorded_by`, or move packets to `promoted/` without a per-row operator act.

---

### Q5. In-band proof — textual back-pointer vs cryptographic signature?

1. **Failure mode** — Crypto signatures (`operator_cli_key_*`, Blackboard blocks) add key-management failure modes (lost key, wrong key, false sense of legal non-repudiation) without improving v1 reconstructability. Missing `candidate_ref` in the row is the real failure mode.
2. **Hidden cost** — Keys, rotation, verification tooling, and support burden. Textual proof matches Wave 1 §12 item 10.
3. **Specific buyer** — Buyers are not consuming these rows in v1. Internal audit needs packet id + row index + archive path.
4. **Cost of inaction** — Manus crypto promotion language could be mistaken for a D-decision. Explicit textual proof + crypto deferred closes ambiguity.
5. **Cheaper proof first** — Yes. `notes` block with `promoted_from`, `promoted_by`, `promoted_at`; `event_id` at promotion.
6. **Existing competitor** — Git commit identity + structured audit fields are sufficient for internal engineering evidence; HSM-style signing is enterprise GRC overhead.
7. **Pre-mortem** — "We required crypto keys for promotion, ops could not promote during an outage, and candidates piled up unreviewed. Mitigated by in-band textual proof v1."

**Verdict:** In-band proof = `event_id` + operator-bearing `recorded_by` + promotion timestamp + `candidate_packet_id` / `candidate_ref` + archive path in `notes`. Cryptographic signatures **rejected for Wave 3 v1** (§10 Q7 defer).

---

### Q6. Forbidden automation — enumerate tool prohibitions?

1. **Failure mode** — Any tool that auto-promotes, auto-assigns `event_id`, deletes candidates, or writes canonical rows breaks the #1 non-negotiable. LLM summarization that overwrites `finding_summary` without operator edit is authority drift.
2. **Hidden cost** — Explicit prohibition list is documentation cost only; prevents re-litigation each session.
3. **Specific buyer** — N/A.
4. **Cost of inaction** — Without §10 forbidden list, Wave 2 emitter could be extended "just to promote on SHIP."
5. **Cheaper proof first** — Yes. Spec §10 forbidden list; emitter stays emit-only.
6. **Existing competitor** — Human-gated promotion is the conservative default for internal compliance evidence.
7. **Pre-mortem** — "We added auto-promote on green audit to save time; a FIX_FIRST candidate became evidence without human read. Mitigated by forbidden automation table in spec §10."

**Verdict:** Tools must never: auto-promote; assign canonical `event_id`; write operator-bearing `recorded_by`; move to `promoted/`; delete candidates; write canonical ledger; weaken pass/fail; claim compliance/insurance. Emitters remain emit-only.

---

### Lighter verdicts (§10 open questions)

- **Review helper script:** Defer `review_ledger.py` to Wave 3.1 — define in a separate implementation spec after this deep-dive §11; may prompt checklist, must not auto-promote.
- **Canonical write surface:** v1 default = `PROJECT_ACTIVITY_LOG.md` structured promotion entry **or** operator-authorized row block in `Testing_Score_Sheet_Schema.md`; dedicated ledger file still requires Wave 0 Q1 operator authorization.
- **Manus dataset:** Park outside Wave 3; optional future `research_intake` spec only.
- **Stale deferred TTL:** Carry forward Wave 0 Q3 (60-day candidate) — not locked tonight.

### §14 stress-test addendum — staging fatigue vs toxic leakage (2026-06-03)

**Status:** Evaluated as Wave 3 §11-prep input. This is not §11 sign-off, not implementation authorization, and not a mandate to build code tonight.

**Core tension evaluated:** strict Wave 1 / Wave 2 data-sanitization requirements reduce toxic-payload risk, but they increase the manual review burden on the operator. If candidate volume grows, the same human gate that preserves authority can become the bottleneck.

**Primary mitigation lever identified:** future Wave 3.1 `review_ledger.py` interactive triage helper. This helper is no longer merely a convenience idea; it is the leading proposed control for keeping manual-only promotion viable while reducing toxic-payload leakage risk. It still requires a signed implementation spec before build.

| Evaluation axis | Score | Operational impact / strategic assessment |
|---|---:|---|
| Architectural alignment | 9 / 10 | Strong. Preserves Wave 1 manual-only promotion authority while placing automation only at the pre-promotion triage layer. |
| Operational friction | 4 / 10 | Lower is better. A review helper can reduce manual file parsing and format checking without making the promotion decision. |
| Attack surface / data liability | 10 / 10 | Critical defense. Running scanner checks during triage reduces the chance that PII, secrets, raw payloads, or toxic content reach the canonical ledger or archives. |
| Implementation complexity | 6 / 10 | Moderate. Requires JSONL parsing, checklist prompting, scanner reuse, refusal states, and clear no-write boundaries. |
| Dependency ripple | 3 / 10 | Lower is better. Additive if implemented as a review helper; should not alter Wave 0 ledger schema or Wave 1 / Wave 2 candidate schemas. |
| Operator cognitive load | 9 / 10 | High shielding. Converts an 8-item mental checklist into guided, pre-vetted review prompts while preserving human authority. |
| Future scalability | 10 / 10 | Strong. If future sensors, research intake, or Wave 4+ external candidate sources increase volume, the human-in-the-loop lane stays viable only with triage assistance. |

**Gate conclusion:** passes as a **Wave 3 §11-prep recommendation**. `review_ledger.py` should be treated as a critical pipeline security-control candidate for Wave 3.1, not as an optional nicety. It may parse, pre-check, highlight, and draft. It must not auto-promote, assign canonical `event_id`, set operator-bearing `recorded_by`, move packets to `promoted/`, delete candidates, write canonical ledger rows, or weaken the 8-item operator checklist.

**Boundary:** no code, no `review_ledger.py`, no pre-commit hook, no canonical ledger automation, and no §11 signature is authorized by this addendum. Build remains frozen until Wave 3 is signed and the operator separately authorizes Wave 3.1 implementation.

### Verdict summary (feeds Wave 3 §10 / operator §11 prep)

| # | Topic | Wave 3 v1 verdict |
|---|---|---|
| W3-Q1 | Holding area | Single pool `audit_outputs/score_sheet_candidates/` |
| W3-Q2 | Checklist | Hard gate — all 8 items |
| W3-Q3 | Rejection | `rejected/` archive + reason; no mutation feed |
| W3-Q4 | Promotion | Manual only; script assist deferred |
| W3-Q5 | Proof | Textual in-band; no crypto v1 |
| W3-Q6 | Automation | Explicit forbid list; emit-only tools |
| W3-Q7 | Fatigue vs toxic leakage | `review_ledger.py` promoted to critical Wave 3.1 control candidate; still no implementation before signed spec |

These verdicts support operator §11 on `Score_Sheet_Candidate_Review_Promotion_Deep_Dive.md` but do **not** sign it.

---

## Future Concept Research: Project Pneumatic Lung

**Status:** Future design note only (Stage C / Wave 4+). Not scored, not a `think_sheet` idea-table candidate yet, not a spec, not §11, not implementation authorization. Captured verbatim from operator concept on 2026-06-02 for long-term research. Does **not** alter the current strict boundary: no code until Wave 3 specification sign-off. This note authorizes nothing.

**Concept name:** "The Pneumatic Lung" (Crowdsourced Swarm Defense).

### Core metaphor (Inhale / Exhale)

- **INHALE (expansion).** When the threat landscape shifts or experiences a surge, NorthStar opens a secure, external API gateway. This would allow verified independent freelancers and security researchers to temporarily "piggyback" their own custom-built specialized AI security swarms onto our infrastructure, expanding processing and specialized detection power during the surge.
- **EXHALE (contraction).** Once the surge is analyzed, the system contracts. External swarms are disconnected, compressing the collective threat intelligence down into a single, clean candidate packet.

### Strict governance integration (carried as a hard constraint of the concept)

- This is **NOT** a backdoor and grants **no** external code direct access to customer systems.
- External freelance swarms would be strictly restricted: they may **only** emit an unsigned, unverified candidate packet into the isolated `audit_outputs/score_sheet_candidates/` holding area — the same holding pool defined by the Wave 3 draft.
- Any such candidate must still pass the internal 8-item operator review checklist. It can never become active protection without direct, manual human operator promotion (consistent with the Wave 3 manual-only promotion boundary and the #1 non-negotiable: no auto-promotion).

### Why it is parked, not pursued

- Depends on a signed Wave 3 promotion discipline plus a not-yet-existing external-gateway trust / identity / sandboxing spec.
- Introduces a large new attack surface (external code, gateway auth, abuse / poisoning of the candidate pool) that would need its own threat model and signed spec before any prototype.
- Stage C / Wave 4+ horizon; revisit only after Wave 3 is signed and the candidate-review loop is proven in practice.

### Open research questions (for a future dedicated pass, not now)

- How are external swarms verified/identified, and how is candidate-pool poisoning prevented at scale?
- Rate-limiting, isolation, and cost controls for the "inhale" gateway.
- How does "exhale" compression avoid laundering many low-quality candidates into one over-trusted packet?
- Does this belong to NorthStar's product at all, or to a separate research venture?

This entry is research capture only. It creates no D-decision, no gate, no requirement, and does not change any current boundary.

---

## Review Cadence

- **Monthly:** every idea in `live park`, score every unscored idea, fill any `ST = N` answers for `promote` band candidates.
- **Quarterly:** every idea in `deep park` and `moonshot`, revisit the `retire` candidates.
- **On demand:** any time a new idea sparks — score it here first, before it touches `PROGRESS.md`.
