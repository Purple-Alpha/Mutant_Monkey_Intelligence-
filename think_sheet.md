# Think Sheet

**Purpose:** A scoring sheet that sits *in front of* the active project plan. When an idea comes up, it gets scored here first to decide whether it's worth pursuing, parking, or dropping. This sheet is not part of the project plan — it's the filter that protects the plan from drift.

**Operating rule:** Ideas are scored here. They do not enter the active project plan (`PROGRESS.md`) without passing the scoring rubric **and** the stress-test gate.

**Last reviewed:** 2026-05-24

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
| 2026-05-23 | **Callback Phishing / TOAD detection layer** — detects emails that move the fraud off-channel by telling the victim to call a provided number; combines callback-language detection, phone-number baselining, and "do not call the number in this email" audit guidance | feature-idea (BEC / vishing) | 2·2·2·2·2 = 10 | promote | Y | Captures Matt's adversarial insight: if the attacker knows email controls exist, they may put a phone number in the email and complete the fraud by voice. Clean fit with Vendor Baseline Store if `phone_number` becomes a future closed enum entry; requires spec revision before implementation. See stress-test answers below. |
| 2026-05-23 | **Two-channel confirmation enforcement** — when a payment-change or high-risk vendor-fraud signal fires, require out-of-band verification against a previously-known vendor channel and record whether the operator confirmed it before money moves | workflow-idea (BEC control) | 2·2·2·2·2 = 10 | promote | Y | Stage A-sized workflow/audit layer. Strengthens the current daily-digest/reporting path without requiring a SaaS portal. Gives NorthStar a clear defense against callback phishing and payment-change fraud: software flags, process verifies, audit trail proves whether the process was followed. See stress-test answers below. |
| 2026-05-23 | **High-trust vendor verification layer** — umbrella strategy for selective financial-change verification using two-channel confirmation now, optional per-vendor challenge/response later, and a NorthStar Portal once Stage A revenue proves demand | strategic-idea (BEC control) | 2·2·2·2·2 = 10 | promote | Y | Captures the "encrypted keys / financial-only high-trust flow" discussion without committing to S/MIME/PGP. Core insight: crypto alone does not solve account-takeover BEC; the durable control is a second channel the attacker does not control. See stress-test answers below. |
| 2026-05-23 | **NorthStar Portal** — Stage B high-trust payment-change surface and brand layer; vendors update sensitive payment/contact data through a controlled NorthStar workflow instead of relying on email alone | product-surface (Stage B / moonshot) | 2·2·2·1·1 = 8 | promote / moonshot | Y | Strong brand + trust layer, but heavier than Stage A: authentication, MFA, vendor onboarding, uptime, tenant isolation, and UX become real product obligations. Keep promoted but gated on Stage A evidence, paid pilots, and a proper portal spec. See stress-test answers below. |
| 2026-05-23 | **Client-facing 5-axis Email Scoring Rubric** — external email-risk score modeled after the think sheet: five 0-2 axes that explain WHY an email was flagged, while the internal 0-100 runtime score remains available for routing | feature-idea (client UX / reporting) | 2·2·2·2·2 = 10 | promote | Y | Captures Matt's idea to make email risk scoring as legible as the rubric. Candidate axes: Sender Identity, Conversation Continuity, Vendor Payment History, Document Integrity, Origin / Timing. Requires a spec so axis definitions do not drift once clients learn them. See stress-test answers below. |
| 2026-05-23 | **NorthStar's 5 W's discovery framework** — informational-interview framework for MSP/customer research: what email security they use, whether vendor fraud is painful, whether they understand the gap, whether they would test a report/pilot, and what pricing feels fair | process-idea (customer development) | 2·2·2·2·2 = 10 | promote | n/a | Monday outreach/research frame, not a build item. Purpose is to learn before selling, collect real pain language, and create a foundation for pricing and product positioning. Fits the Human-Written / AI-Proofread policy: Matt asks in his own words; AI only helps proofread. |
| 2026-05-23 | **Fair-access SMB pricing strategy** — pricing principle that NorthStar should be accessible to working-class small businesses without becoming a cheap or weak product | strategy-idea (pricing) | 2·2·2·1·2 = 9 | promote | n/a | Captures Matt's value position: strong security for businesses too small for enterprise pricing, with sustainable pricing that protects both the client and NorthStar's ability to keep operating. Use discovery calls to learn the real acceptable range before locking pricing. |
| 2026-05-24 | **Visible Multi-Agent Deliberation Layer** — make the swarm show its security reasoning the same way a strong assistant debates, corrects assumptions, and then gives a clean answer: multiple lenses assess an ambiguous email, disagreement is resolved, and the client sees the final plain-English reason | feature-idea (trust / scoring UX) | 2·2·2·2·2 = 10 | promote | Y | Captures Matt's "answer questions the way you reason" insight. Value is not just better detection; it creates a visible audit trail, catches blind spots, and turns each miss into a sharper Red/Blue learning signal. SMB sizing anchor: design for 50-100 employee SMBs, ~10 clients per MSP, ~75 employee average, with ~75-600 ambiguous emails/day/client needing richer deliberation, not enterprise-scale Ledcor-sized volumes. See stress-test answers below. |
| 2026-05-24 | **Tiered Detection Intensity (Low / Medium / High) aligned to sales tiers** — tenant-selectable security intensity that controls routine-mail scrutiny while auto-escalating risky emails; commercial alignment follows Option C: Essentials defaults Low, Plus defaults Medium, Enterprise defaults High, with add-ons separate | feature-idea (tenant policy / GTM alignment) | 2·2·2·2·2 = 10 | promote — **§11 SIGNED + implementation landed + Grok-approved 2026-05-24** (spec at `4. Product_Roadmap/Tiered_Detection_Intensity_Deep_Dive.md`; runtime at `core/operator_state/security_profile.py`; 658 passed, 1 skipped; Grok verdict approve) | Y | Low = LLM single-pass + cheap deterministic overlays + audit/digest; Medium = default SMB posture with full Vendor Baseline reads, Financial State Ledger, PDF metadata, micro-temporal, and callback/TOAD scan; High = full deliberation, judge pass, devil's-advocate on flagged mail, skeptic pass on clean mail, structural payload/OCR checks, and visible reasoning trace. Critical rule: tier is a floor for routine mail, not a ceiling for risky mail; financial deltas, combined BEC signals, prior vendor fraud, high-value invoices, fresh baselines, or manual escalation force High on that email. v1 spec lives at `core/operator_state/security_profile.py`; per-tenant state at `blackboard_root/operator_state/security_profiles/<tenant>.json`. v1 forced-escalation closed enum has four triggers (LLM ≥ 80, header divergence ≥ 80, ghost thread > 0, manual operator escalation); five other triggers (financial_state_delta, high_value_invoice, prior_vendor_fraud_flag, fresh_baseline_vendor, combined_bec_signals) are explicit v2 deferrals. See stress-test answers below. |
| 2026-05-24 | **Independent Grok code-auditor runner** — local xAI/Grok audit script that reads signed spec + implementation + tests + receipt, returns spec divergence / coverage gaps / security risks / verdict, and blocks "done" claims when verdict is not approve or approve-with-notes | process-idea (quality gate) | 2·1·2·2·2 = 9 | promote | N | Prototype landed as `audit_tools/grok_audit_runner.py` during the Vendor Baseline audit cycle and produced real fixes before final `approve with notes`. Needs stress-test before becoming a formal always-on build gate: data-egress boundary, prompt/version locking, report retention, and when to override noisy findings. |
| 2026-05-24 | **Independent decision-auditor lane** — second-model audit for build-order recommendations, spec-lock decisions, and "gold-plating vs necessary quality" calls so the primary assistant's advice can be challenged before it shapes the project path | process-idea (anti-drift governance) | 2·1·2·2·2 = 9 | promote — **§11 SIGNED + implementation landed + first self-audit `proceed` 2026-05-24** (spec at `4. Product_Roadmap/Independent_Decision_Auditor_Deep_Dive.md`; runtime at `audit_tools/decision_audit_runner.py`; 688 passed, 1 skipped) | N | Captures Matt's concern that assistant recommendations can quietly steer choices before drift is visible. Input: one operator-reviewed Markdown packet with decision, recommendation, rationale, alternatives, current state, and constraints. Output: six-section decision-quality report with closed verdict: `proceed`, `proceed_with_notes`, `revise_before_proceeding`, `defer`, or `operator_decision_required`. v1 runner validates packet shape, blocks known secret markers and obvious raw financial strings before network calls, writes reports under `audit_outputs/decision_audits/`, and fail-closes on blocking verdicts unless `--report-only` is explicit. First packet `decision_audit_inputs/20260524_1741_decision_auditor_next.md` returned `proceed`. |

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

---

## Review Cadence

- **Monthly:** every idea in `live park`, score every unscored idea, fill any `ST = N` answers for `promote` band candidates.
- **Quarterly:** every idea in `deep park` and `moonshot`, revisit the `retire` candidates.
- **On demand:** any time a new idea sparks — score it here first, before it touches `PROGRESS.md`.
