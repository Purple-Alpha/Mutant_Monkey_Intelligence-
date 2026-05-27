# Compliance and Trend Watch Process — Deep Dive

**Status:** §11 SIGNED 2026-05-26 by Matt Nichol. Sharp Grok audit clean: `audit_outputs/compliance_trend_watch_signoff_sharp_20260527T004134Z.md` returned 0 Blocking / 0 Warning. Non-blocking §10 questions remain open for v1.x / retrospective handling.

**Authority model:** Matt's vision is the product authority. This document is a Technical Verification Layer artifact. It defines a process — watched sources, cadence, signal criteria, compliance-claim boundaries, trigger categories, audit requirements, and machine-checkable done criteria. It does not score, approve, or judge any specific trend, framework, or candidate. Promoting any item surfaced by this process remains Matt's call, on the same terms as any other think_sheet candidate.

**Scope reminder:** This is a *process* spec, not a runtime feature. It introduces no new agent, no new infrastructure, no new runtime code path. The artifact is `Frontier_Intake_Log.md` plus zero-or-more `think_sheet.md` candidate rows per review cycle. The discipline lives in the operator-driven review, not in automation.

**Selected by:** Operator authorization 2026-05-26 to codify the trend-watch and compliance-claim discipline that has been running ad-hoc since the 2026-05-25 Frontier Intake Review #1 + Cyber Insurance Evidence Package draft. This spec captures decisions already implicit in those artifacts and adds the missing pieces (spec-update vs product-pivot trigger taxonomy, broader compliance-claim boundary that extends beyond the Cyber Insurance Evidence Package's email-fraud surface, Grok audit posture for the review output itself).

---

## §1 Purpose

NorthStar + SwarmCommand is a long-arc product (per `VISION.md`: Stage A now → Stage B 12–24 months → Stage C 3–5 years). The threat landscape, AI agent patterns, compliance frameworks, MSP buying behavior, and competitive incumbents all evolve faster than NorthStar ships. Without a deliberate process to watch, decide, and act on those changes, two specific failure modes show up:

1. **Drift toward obsolescence.** A detector or spec ships that's already behind the threat pattern it claims to address. Underwriters or MSPs read NorthStar's evidence and recognise stale assumptions.
2. **Trend-chasing bloat.** Every new framework or AI-agent-paper becomes a new spec proposal. The think_sheet inflates, decision fatigue compounds, and the active build queue gets crowded out by speculative work that hasn't earned a slot.

This process exists to do neither — to watch deliberately, decide binarily, and act only on signals that meet stated criteria. The artifact is the `Frontier_Intake_Log.md`. The discipline is operator-driven, not AI-autonomous.

This spec also formalises the *compliance-claim boundary* that NorthStar maintains across every surface (not just the Cyber Insurance Evidence Package) — what NorthStar never claims about any compliance framework, regulator, or carrier, and what NorthStar may safely claim with evidence to back it.

### §1.1 Supersession of prior rubric-sniff language

`Frontier_Intake_Log.md` (2026-05-25 intake protocol) contains language that says candidates are surfaced if they "would plausibly survive the 5-axis rubric's Strategic Fit ≥ 1 + Revenue Path ≥ 1 sniff test." That language predates the 2026-05-26 workflow shift recorded in the cyber-insurance deep-dive and confirmed in the NorthStar Operating Constitution discussion: **rubrics are visibility only, not decision authority.**

This spec supersedes the rubric-sniff wording in `Frontier_Intake_Log.md`. The §4 trend-signal criteria below are the binding filter for what counts as a candidate. Rubric scoring may still be applied later as a *visibility* tool inside `think_sheet.md` once a candidate is being gated; it is not a precondition for surfacing a candidate from a Frontier Intake Review.

The `Frontier_Intake_Log.md` intake-protocol step that names the rubric sniff test is targeted for revision at the next Log entry, or earlier if the operator chooses. Until that edit lands, this §1.1 is the controlling statement.

---

## §2 Watched Sources

Five categories. Sources are concrete and named — "we watch threat intel" is not a source; specific feeds are. Adding a source follows §2.7 source-addition governance.

### §2.0 Source authority classification

Every source carries a class. Classes drive what the source can be cited for:

- **Primary authority (P)** — first-hand reporter for the fact it states. Examples: a CISA advisory is primary authority for what CISA recommends; a Microsoft Defender release note is primary authority for what Microsoft is shipping; a direct MSP conversation is primary authority for what that MSP said. Primary sources may stand alone as evidence for what they directly report.
- **Vendor trend signal (V)** — vendor-published research, vendor industry reports, vendor marketing-adjacent commentary. May corroborate candidates, inform competitive-landscape understanding, and contribute to trend-shape claims. **May not be the sole evidence for any compliance, regulatory, or underwriting conclusion** (§2.6 expands this).

A single source may operate in both classes depending on what it is cited for. Microsoft Defender product notes are P for "what Microsoft ships" and V for "what the industry believes about phishing trends." When a source is cited, the class for that citation must be named.

### Sentinel set per category

Each category names a sentinel source set. A sentinel review covers only the sentinel sources rather than the full source list. Sentinel reviews are permitted under the §9 done criteria; the full sweep is required at least once per quarter (see §9.1).

### §2.1 Threat intelligence

| Source | Class | Why it's watched |
|---|---|---|
| CISA Phishing Guidance + current-year advisories | P | Authoritative US-government view on phishing / BEC patterns SMBs face |
| FBI IC3 Public Service Announcements | P | Incident-level evidence of what's actually losing money this year |
| Cloud Security Alliance (CSA) AI Safety Initiative research notes | V | Industry consensus on AI-driven attacks against AI-driven defenses |
| Abnormal Security annual Attack Landscape Report | V | Largest public dataset of observed email attacks; useful for sizing/share trend lines |
| Proofpoint / Cybertechnology Insights AI-deepfake-BEC research | V | Multi-modal BEC research that informs Stage B/C scope decisions |
| IronScales threat intelligence (triple-brand credential harvest, etc.) | V | Pattern-level write-ups MSPs reference |

**Sentinel set:** CISA advisories (P) + FBI IC3 PSAs (P).

### §2.2 AI / agent patterns

| Source | Class | Why it's watched |
|---|---|---|
| OWASP Top 10 for LLM Applications (current version) | P | Coverage check against NorthStar's runtime detector set |
| Microsoft Agent Framework (FIDES, etc.) — release notes / repo | P (for "what Microsoft is shipping") / V (for trend commentary) | Frontier reference architecture for deterministic agent guardrails |
| Open-source agent guardrail projects (e.g. PromptGuard-for-Agents, sentinel-inject) | P (per project) | Implementation patterns NorthStar may adopt or pointedly avoid |

**Sentinel set:** OWASP LLM Top 10 (P).

### §2.3 Compliance / underwriting

| Source | Class | Why it's watched |
|---|---|---|
| Nuronus MSP Cyber Insurance Approval Guide (current year) | V (vendor-derived) / P (for what the document itself recommends to MSPs) | Practical underwriter checklists MSPs actually use |
| Data Centre Solutions MSP cyber-insurance notes | V | Cross-check on underwriting trends |
| GetCybr NIS2 + NIST CSF 2.0 MSP service-line guides | V | Carrier-aligned framework crosswalks |
| Bronston Legal MSP compliance regulations summaries | P (for legal commentary) | Regulatory environment for MSP-delivered controls |
| Direct carrier / broker conversations (when available) | P | Carrier-side signal about what underwriters actually read |

**Sentinel set:** Nuronus current guide (V) + at least one direct MSP-or-carrier conversation in the last 30 days when available (P).

Per §2.6, vendor (V) sources here may inform candidates but cannot stand alone as the sole evidence for a compliance, regulatory, or underwriting conclusion.

### §2.4 Competitive landscape

| Source | Class | Why it's watched |
|---|---|---|
| Abnormal Security product releases (Attune model, Detection 360, Custom AI Models, Auto-Forwarding Mail Protection) | P (for what Abnormal ships) | Largest incumbent in the wedge — track whether they move down-market |
| Microsoft Defender for Office 365 phishing-detection product notes | P (for what Microsoft ships) | Default-bundled competitor for SMBs already on Microsoft 365 |
| KnowBe4, Mimecast, Vade, Avanan release notes | P (for what each ships) | Adjacent competitors whose roadmaps inform positioning |

**Sentinel set:** Abnormal Security release notes (P).

### §2.5 Operator personal network

| Source | Class | Why it's watched |
|---|---|---|
| Local MSP discovery conversations (`THREAT_INTEL_LOG.md` Canadian/Okanagan target list — Carpathia IT, NetDNA, EC Managed IT, IT Works MSP BC, SFY IT, Good IT) | P | First-hand buyer-side signal; out-ranks any secondary source for the SMB wedge |
| Reddit / industry communities where Matt actively engages | P (operator's first-hand observation) | Unfiltered SMB owner pain; raw qualitative data |
| Direct vendor / supplier conversations (e.g. existing carrier or broker relationships, if any) | P | Carrier-side signal about what they actually read in submitted evidence |

**Sentinel set:** Any direct MSP conversation in the last 30 days (P). If none has occurred in the last 30 days, the category cannot be "sentinel-reviewed" and must either run a full sweep or be logged as a skipped category.

### §2.6 Source-list governance

- **Replacement.** Sources that go quiet for more than two consecutive review cycles are flagged for replacement in §10.
- **Quality bar.** Sources must publish concrete claims or evidence. Marketing pages and conference keynote summaries are not sources.
- **Bias hygiene.** Vendor (V) sources are included but explicitly tagged. Specifically:
  - Vendor (V) sources may corroborate a candidate; they may not be the *sole* evidence for any candidate.
  - Vendor (V) sources may *not* be the sole authority for any compliance, regulatory, underwriting, or framework-alignment conclusion. Such conclusions require at least one Primary (P) source — a regulator, carrier, MSP-side direct conversation, or equivalent first-hand reporter.
  - Vendor (V) sources may stand alone only for **confirmations** that do not create a new candidate, do not alter source-list governance, and do not support a compliance / regulatory / underwriting / framework-alignment conclusion. Example: "Abnormal reports increased QR-code phishing" may confirm existing QR/phishing watch direction; it cannot by itself create a NorthStar roadmap candidate or buyer-facing claim.
  - Primary (P) sources may stand alone as evidence for what they directly report (e.g. CISA's recommendation, an MSP's stated preference, Microsoft's release note).
- **Citation discipline.** Every citation in a review entry names the source AND its class for that citation (e.g. "Abnormal 2026 Attack Landscape Report (V)" or "Direct conversation with Carpathia IT 2026-06-04 (P)"). Class-less citations are a §9 done-criteria failure.

### §2.7 Source-addition governance

**Resolved 2026-05-26 by operator direction, pending §11 lock as Dn.**

New watched sources are added by one of three paths:

1. **Operator-add.** Matt may add a source directly during a review or between reviews. The next `Frontier_Intake_Log.md` entry records: source name, class (P/V), category, reason added, and whether it joins the sentinel set. Operator-adds do not require a `think_sheet.md` row.
2. **Evidence-backed proposal.** Cursor / assistant may propose a source only when it names the category, source class, concrete value, and what existing source it complements or replaces. The proposal is logged as a review note; Matt decides whether to add it. No auto-add.
3. **Spec-amendment path.** If a source addition changes a category boundary, changes sentinel coverage, creates a new watched category, or changes the §5 compliance-claim boundary, it requires a spec amendment and §11 re-signature.

Routine additions to the existing five categories do **not** require a full spec amendment when they do not alter category boundaries or sentinel rules. The source registry is the latest signed spec plus logged source-addition records in `Frontier_Intake_Log.md`.

Deletion follows the same authority pattern: Matt may remove a stale or low-quality source directly, but the next review entry records the removal reason. Cursor may propose removals; it does not remove sources autonomously.

---

## §3 Review Cadence

Defers to the cadence rule locked in `Frontier_Intake_Log.md` (2026-05-25):

- 0–1 candidates per review → defer recurring discipline; ad-hoc reviews suffice.
- 2–3 candidates → quarterly cadence committed.
- 4+ candidates → monthly cadence committed.

Per the log, Review #1 surfaced 5 candidates → monthly cadence is the current commitment.

### Review types

| Type | When | Output |
|---|---|---|
| **Monthly Frontier Intake Review** | First Monday of each calendar month, with the §3 Calendar rhythm holiday/deferral rules | New entry in `Frontier_Intake_Log.md`; zero-or-more new `think_sheet.md` candidate rows |
| **Quarterly deep review** | Every third monthly review, combined with a parked-candidate re-scan whose exact scope remains the non-blocking Q2 follow-up | Same artifacts plus an explicit re-evaluation note on any parked candidate the quarter's trends affect |
| **On-demand review** | Operator surfaces a question that touches a watched area outside the regular cycle | A dated mini-entry in `Frontier_Intake_Log.md` with the triggering question and the answer |

### Cadence drift handling

- **Skipped month.** Recorded in the log as `Skipped — <reason>`. Two consecutive skips trigger an open-question entry in §10.
- **Low-signal month.** Logged with explicit "0 candidates" finding; not skipped. Confirms the discipline is running even when output is small.

### Calendar rhythm

**Resolved 2026-05-26 by operator direction, pending §11 lock as Dn.**

- **Monthly trigger.** The monthly Frontier Intake Review is triggered on the **first Monday** of each calendar month. If that Monday is a statutory holiday in British Columbia, the trigger shifts to the next non-holiday weekday.
- **Operator deferral window.** Matt may defer the review up to **7 calendar days** without recording a reason. A deferral beyond 7 calendar days is recorded in the next review entry's preamble with the reason and the new target date.
- **No-signal cycle.** If the 30 days before the trigger produce zero §4 candidates and zero confirmations, the review may record a compact `no-signal cycle` entry instead of a full narrative review. The no-signal entry must still name sources sampled, source classes (P/V), sentinel-vs-full review mode per §9.1, and reason `no §4 signal`.
- **No-signal cap.** No more than **two consecutive** no-signal cycles are allowed. The third cycle must be a full review with §4 evaluation and source citations regardless of perceived signal density.
- **Quarterly deep review.** The third monthly review in each rolling quarter is a quarterly deep review unless Matt explicitly defers it under the same 7-day rule. The quarterly review cannot be replaced by a no-signal cycle.

---

## §4 Trend-Signal Criteria

A surfaced item passes the trend-signal filter only if **all** of the following hold. Items that pass at least one filter but not all are recorded as confirmations or noise, not as candidates.

1. **Surface alignment.** The item materially affects NorthStar's current or near-term control surface (email-fraud, inbox-layer MDR, the seven non-negotiables, or the wedge identified in `VISION.md`). Items that affect adjacent surfaces (endpoint, identity, network) are recorded as confirmations or future-stage notes, not candidates.
2. **Concrete evidence.** A named source, dated within the last 12 months, with a specific claim. "AI is changing security" is not a signal; "Proofpoint 2026 briefing reports 40% of BEC now uses voice-clone components" is.
3. **Named threat or named buyer.** Either a specific attack pattern with named victims/sources, or a specific buyer-side requirement (a carrier asked for X; an MSP raised Y in discovery).
4. **Implication-stateable.** The reviewer can state, in one sentence, what NorthStar would plausibly do differently if this signal were true. If "I don't know what we'd do with this" is the honest answer, the item is logged as a confirmation or noise, not a candidate.
5. **Not redundant.** The signal does not duplicate an existing detector, spec, or `think_sheet.md` row that already covers it. Confirmations of existing direction are logged but not surfaced as candidates.

### Confirmation vs candidate vs noise

The classification matches the existing intake protocol in `Frontier_Intake_Log.md`:

- **Confirmation** — reinforces existing direction. Logged; no candidate row.
- **Candidate** — passes all five filters above. Surfaced for `think_sheet.md` gating in a separate operator-led step (the intake itself is discovery; gating is the next step and remains Matt's call).
- **Noise** — fails one or more filters and is also not a confirmation. Not recorded.

---

## §5 Compliance-Claim Boundaries

This section is the canonical boundary for *every* NorthStar surface that touches compliance language — outreach, marketing, spec, demo, evidence package, support ticket. The Cyber Insurance Evidence Package deep-dive §9 forbidden-language list is the specific application of these boundaries to that one buyer-facing artifact; this section is the broader rule.

### §5.1 What NorthStar never claims

- Not SOC 2 attested.
- Not ISO 27001 certified.
- Not HIPAA-covered.
- Not PCI-DSS scoped.
- Not GDPR-compliant in itself.
- Not NIS2-compliant in itself.
- Not a substitute for any MFA / EDR / backup / IR / patch-management product.
- Not a guarantee of any underwriting outcome or premium effect.
- Not "compliant" with any framework as an absolute statement.
- Not "fully secure," "bulletproof," "guaranteed," "complete," or any absolute-coverage language.
- Not an attestation, certification, or warranty of any kind.

### §5.2 What NorthStar may claim, with evidence

- "Provides auditable evidence for [a specific named control on the email-fraud / inbox-layer MDR surface]."
- "Documents [a specific detection capability] with [a specific test/audit artifact backing it]."
- "Aligns with [a specific framework function or control reference] for [the specific scope NorthStar covers]" — only when the alignment is documented in a signed spec and the scope is named in the same sentence.
- "Produces [a specific machine-readable artifact] that an MSP may include in [a specific buyer process]."

Every "may-claim" sentence must name the specific scope (`email-fraud and inbox-layer MDR control surface only`) in the same sentence or in an immediately adjacent boundary statement.

### §5.3 Allowed-context carve-outs

The §5.1 phrases may appear in a NorthStar surface only inside one of these contexts:

- An explicit non-scope statement (e.g. the boundary statement in the Cyber Insurance Evidence Package).
- A forbidden-language list (such as this section, or §9 of the cyber-insurance package).
- A spec's bad-example or anti-pattern section.
- A historical record of a past claim that was retracted.

Outside these contexts, the §5.1 phrases are drift incidents.

### §5.4 Framework crosswalks

When a watched source (NIST CSF, NIS2, OWASP LLM Top 10, etc.) maps to NorthStar capability, crosswalks are permissible *if and only if* each line of the crosswalk:

1. Names the framework's specific function/control identifier.
2. Names the specific NorthStar artifact that backs the claim.
3. Names the explicit scope limit ("email-fraud surface only", "inbox-layer detection only").
4. Does not claim certification or attestation against the framework.

A crosswalk that fails any one of these is a §5.1 drift incident.

### §5.5 Vocabulary translation

Carrier-jargon ("attestation," "control efficacy," "regulatory mapping," "compensating control," "material weakness") gets translated to plain English in any client-facing surface.

**Canonical inheritance order (resolved by operator 2026-05-26, pending §11 lock as Dn):**

1. **This document §5 is canonical** for the project-wide compliance-claim boundary, forbidden-language list, and vocabulary-translation list.
2. **The Cyber Insurance Evidence Package deep-dive §9 is the buyer-surface application** — it renders this list (with any presentation differences the buyer-facing context warrants) for the cyber-insurance evidence-bundle audience.
3. **If the two diverge in the future**, this document is canonical. The buyer-surface artifact gets updated to match, not the other way around.
4. **Downstream code** (currently `audit_tools/complete_gate.py`'s `FORBIDDEN_LANGUAGE_LIST` and `VOCABULARY_TRANSLATION_LIST` constants) inherits from this spec. Comments in that code may currently cite the cyber-insurance package §9 as the source of truth; the comments will be updated to cite this spec when §11 is signed. The constant values themselves are unchanged by this lockdown — only the cited-as-canonical authority is.

#### Vocabulary-translation list (v1, canonical)

| Carrier jargon | Plain English replacement |
|---|---|
| Control efficacy | How well this control works in practice |
| Regulatory mapping | Cross-reference to specific underwriting questions |
| Compensating control | A different control that addresses the same risk |
| Control attestation framework | The way we record what each control does |
| Material weakness | A meaningful gap |

Additions to this list flow through this spec first; they may then be propagated to the Cyber Insurance Evidence Package §9 rendering and to `audit_tools/complete_gate.py`'s constant. Removals follow the same path.

The full v1 list lives here. Any future divergence between this list and the cyber-insurance package §9 is itself a §6 spec-update trigger against that package.

---

## §6 Spec-Update Triggers

A trend signal warrants an *amendment* to an existing signed §11 spec when **at least one** of the following holds. Spec amendments require a re-signature; they are not silent edits.

| Trigger | Example |
|---|---|
| **T1 — Detector coverage gap** | A trend describes an attack pattern that an existing detector should cover but doesn't, within the existing scope of that detector. *Example:* Callback Phishing TOAD detector's phrase-category list does not cover a newly-observed lure family. |
| **T2 — Scoring axis drift** | A trend reveals a failure mode in an existing scoring axis or rubric category — e.g. axis weights perform poorly against the new pattern, or the rubric explanation is no longer accurate. |
| **T3 — Buyer-language change** | A trend changes the buyer-readable language (carrier vocabulary shift, MSP terminology evolution). Affects the vocabulary-translation list (§5.5) and any client-facing rendering surface. |
| **T4 — Redaction / privacy contract drift** | A regulation, framework, or industry practice shifts the bar for what may appear in a buyer-facing artifact (e.g. raw vendor names, hashed-vs-plain identifiers). The redaction rules in the affected spec require updating. |
| **T5 — Forbidden-language list addition** | A carrier-specific or regulator-specific phrase joins the §5.1 list. Specs that print the list inline (e.g. cyber-insurance package §9) get amended. |
| **T6 — Failure mode discovery** | A trend or post-mortem reveals a failure mode the original spec didn't anticipate (e.g. a new pre-mortem scenario that the spec's §10 sub-questions never asked). |

### Spec-update workflow

1. Trend-signal item surfaces in a Frontier Intake Review and is classified as a Candidate.
2. Reviewer (or operator on follow-up) checks the candidate against §6 triggers.
3. If a trigger fires, the affected spec is named in the log entry, and a `spec-amendment candidate` row is added to `think_sheet.md`.
4. Operator decides whether to schedule the amendment.
5. Amendment goes through normal spec-first discipline: draft, §10 stress-test, §11 re-signature.
6. Spec version increments; the amendment record cites the trend signal that triggered it.

Spec-update triggers do not auto-amend. They surface candidates for amendment. The amendment itself remains a spec-first operator-authorized action.

---

## §7 Product-Pivot Triggers

A trend signal warrants a *roadmap pivot* — a bigger change than spec amendment — when **at least one** of the following holds. Pivots stop work; they are not absorbed quietly into the build queue.

| Trigger | Example |
|---|---|
| **P1 — Wedge moves** (resolved 2026-05-26 by operator; pending §11 lock as Dn) | **≥5 relevant MSP conversations across at least two distinct MSP profiles**, **OR** **≥3 conversations sharing the same concrete negative reason**, returning signal that the current wedge framing (e.g. "email-fraud evidence bundle for cyber-insurance underwriting") is not landing. "MSP profile" = the combination of size band (boutique / mid-size / enterprise), geography (regional / national), and vertical specialization (healthcare / legal / general / etc.). Two profiles means meaningfully different on at least one of these dimensions. "Concrete negative reason" = a named, specific objection (e.g. "underwriters in our region don't ask about email controls separately"), not a polite-no or non-response. The wedge — not just the language — needs reconsideration when this trigger fires. |
| **P2 — Stage-arc obsolescence** | The threat landscape moves beyond the current stage's control surface in a way no near-term detector can address (e.g. SMB attacks shift entirely off email to a surface NorthStar does not cover and cannot reach in Stage A). |
| **P3 — Regulatory non-shippability** | A regulator or framework action makes a current capability non-shippable (e.g. a privacy regulation makes a current data path illegal in a target jurisdiction). |
| **P4 — Category-defining incumbent ships the wedge** | An incumbent (Abnormal, Microsoft, KnowBe4, etc.) ships the exact wedge NorthStar is building toward, at SMB price points, with comparable auditability. The differentiated position is gone; a new wedge must be identified. |
| **P5 — Non-negotiable contradiction** | A trend forces a real choice between honoring a `VISION.md` non-negotiable and continuing the current direction. Per `VISION.md`, the non-negotiable wins; the direction pivots. |
| **P6 — Buyer chain breaks** | A structural change in the MSP-to-SMB market (e.g. MSPs consolidating into vertically-integrated insurance companies; SMBs bypassing MSPs for direct SaaS security) invalidates the current buyer chain. |

### Pivot workflow

1. Trend-signal item surfaces and the reviewer flags a §7 trigger as plausibly firing.
2. The review immediately surfaces the pivot signal to the operator. Pivots are not deferred to the next review cycle.
3. Operator reviews the signal. The signal is *not* an authorization; it is an alert.
4. If the operator confirms the pivot, the existing roadmap is paused, the affected stage-arc element is opened for revision, and `MILESTONE_ARC.md` / `VISION.md` are reviewed for changes.
5. Pivot decisions are recorded in `PROJECT_ACTIVITY_LOG.md` with full provenance (trigger that fired, sources, operator reasoning).
6. AI does not auto-classify ambiguous signals as pivots. Ambiguity defaults to "log, surface, wait for operator review" — never "act."

Product-pivot triggers do not auto-pivot. They surface a serious enough signal that the operator must look at it.

---

## §8 Grok Audit Requirements

Per the project workflow established 2026-05-26, Grok is a negative-feedback auditor, not an approval authority. The completion gate (`audit_tools/complete_gate.py`) is the enforcement layer; this section defines the audit contract for *this* process's output specifically.

### §8.1 What Grok audits in a Frontier Intake Review

When a monthly / quarterly / on-demand review is claimed as ready, the Grok audit reviews:

- Every cited source against §2 watched-sources list. A citation not in §2 (or in §2's documented expansion record) is a deviation.
- Every claim about NorthStar capability against §5 compliance-claim boundaries. Any §5.1 phrase outside an allowed-context carve-out (§5.3) is a `blocking` deviation.
- Every candidate against §4 trend-signal criteria. A candidate that fails one or more filters but is still surfaced as a candidate is a deviation.
- Every spec-update trigger and product-pivot trigger flagged in the review against §6 / §7 criteria — including the inverse: an item that *should* have fired §6 or §7 but didn't.
- Vocabulary-translation discipline (§5.5) across the entire review.
- That the review's classifications (Confirmation / Candidate / Noise) match the criteria in §4 and don't conflate them.

### §8.2 What Grok does NOT audit

- Whether the candidates are "good ideas." That is operator judgment, gated by `think_sheet.md`.
- Whether the project should pivot. That is an operator decision following a §7 alert; Grok flags missed triggers, it does not opine on the pivot itself.
- The strategic merit of any specific source on the watched list. Source-list governance is operator-only.

### §8.3 Audit contract — the prompt context Grok receives

The audit packet (assembled by `complete_gate.py`) must include:

- This document, in full (§1–§11).
- The Frontier Intake Log entry being audited.
- The `VISION.md` non-negotiables section.
- The Cyber Insurance Evidence Package §9 forbidden-language and vocabulary-translation lists (for §5.1 / §5.5 cross-check).
- Any signed §11 spec the review's spec-update triggers cite.
- The negative-feedback prompt (from `complete_gate.py`).

### §8.4 Output handling

- Grok output saved to `audit_outputs/compliance_and_trend_watch_<timestamp>.md` (or per §8.5 when split).
- Blocking deviations must be resolved (or accepted by Matt with `operator_resolution_note`) before the review entry is considered complete.
- Warning-level deviations are recorded in the review entry itself for the next cycle to consider.
- "Grok said nothing" is compliant *only* if the audit packet covered the entire review and the full watched-sources list (or the sentinel subset declared for that cycle per §9.1). Partial packets that are not declared as such are not compliant — same rule as Cyber Insurance Evidence Package §10.

### §8.5 Packet-size handling and splitting

A single combined audit packet for a busy review cycle may approach or exceed the 200 KB total cap enforced by `audit_tools/complete_gate.py`. When that happens, the audit is split into multiple precise packets rather than truncated or sent partial. The split rule is deterministic:

1. **One Grok audit per spec-update trigger fired (§6).** Each packet contains: the relevant signed §11 spec, the trigger description, the candidate that fired the trigger, the relevant excerpt from the review entry. Filename: `audit_outputs/compliance_and_trend_watch_<timestamp>_spec-<spec-slug>.md`.
2. **One Grok audit per product-pivot trigger fired (§7).** Each packet contains: the trigger description, the supporting evidence chain (sources and counts that met the threshold), the operator-alert section of the review entry. Filename: `audit_outputs/compliance_and_trend_watch_<timestamp>_pivot-<trigger-id>.md`.
3. **One Grok audit for the "no-trigger" body.** Contains the rest of the review entry: confirmations, candidates that did not fire any trigger, classification sweep, vocabulary-translation sweep, and source-citation discipline. Filename: `audit_outputs/compliance_and_trend_watch_<timestamp>_body.md`.

When split:

- The done-declaration JSON (§9 machine-checkable section) lists every split audit output file under `grok_audit_outputs` as an array, not a single string.
- The review is "done" only when every split audit's blocking deviations are resolved or operator-accepted. No silent partial sign-off.
- A split is allowed even when the combined packet would fit under cap — the operator may elect a precise split for clarity even on smaller cycles. Combined packets are also allowed for small cycles that fit under cap.

---

## §9 Done Criteria

A Frontier Intake Review (monthly / quarterly / on-demand) reaches "done" when **all** of the following are true:

1. **Source coverage.** Every category in §2 has been reviewed in this cycle by **either**:
   - a **full sweep** (all sources in that category named in §2.1–§2.5 are reviewed), or
   - a **sentinel review** (only the sentinel set named in that category is reviewed; the entry records this explicitly as `sentinel`).

   Sentinel-only reviewing must be expanded to a full sweep at least once per quarter for every category (see §9.1). Categories with no source covered (neither full nor sentinel) are recorded as skipped with reason.
2. **Findings classified.** Every surfaced finding is classified as Confirmation, Candidate, or Noise (or Noise-implicit by not being recorded), with the §4 filter result recorded for any item the reviewer hesitated to drop as Noise.
3. **Trigger sweep.** Every Candidate has been checked against §6 spec-update triggers and §7 product-pivot triggers. Triggers that fired are recorded in the entry.
4. **Compliance-claim sweep.** The review entry contains no §5.1 phrase outside an allowed-context carve-out.
5. **Vocabulary translation applied.** Carrier-jargon in the entry is translated per §5.5.
6. **Citations resolve.** Every cited source has a working reference (URL, document title, dated publication) and is included in §2 or its documented expansion record.
7. **Candidate gating handoff documented.** Surfaced candidates each have a corresponding row in `think_sheet.md` (or an explicit "deferred to next review" note). No silent surfacing.
8. **Pivot alert sent.** If any §7 trigger fired, the operator is alerted in the review entry itself (not buried in a footnote).
9. **Audit packet covers entry.** Every file touched while preparing the entry is in the audit packet for §8 Grok review.
10. **Grok audit run.** A Grok audit output for this review exists in `audit_outputs/`, dated after the review entry was finalized.
11. **Blocking deviations resolved or accepted.** Every Grok-identified blocking deviation is either resolved in the entry or explicitly accepted by Matt with a written rationale.
12. **No blocking drift incidents open.** All open `blocking`-severity drift incidents (`audit_outputs/drift_incidents/`) for this task ID are resolved or operator-accepted.
13. **Operator signature on the review entry.** The review entry is signed off by Matt in his own words. AI-authored sign-off text is forbidden (Authorship Rule, 2026-05-25/26).

A review is not "done" until all 13 criteria hold. The cadence rule in §3 governs when the next review starts; the done criteria govern when the current one stops.

### §9.1 Sentinel-vs-full-sweep schedule

To keep monthly reviews bounded while preventing the sentinel set from quietly becoming the *only* set ever consulted:

- Within any rolling quarter, every category must have at least **one full sweep**. The other reviews in that quarter may be sentinel.
- A sentinel-reviewed category records the sentinel sources actually consulted in the entry. Sources declared in the sentinel set but not actually reviewed are a `criterion 1` failure.
- A category that has gone two consecutive months on sentinel-only review without a full sweep triggers an entry-level note ("`<category>` overdue for full sweep") and the next review must full-sweep that category.
- Discovery / opportunistic findings outside a sentinel review (e.g. an MSP conversation that surfaces a new threat pattern) count as full-sweep evidence for the operator-network category in that cycle.

### Machine-checkable done declaration

A done review emits a small JSON sidecar.

**Resolved 2026-05-26 by operator direction, pending §11 lock as Dn.**

- **Storage path:** `audit_outputs/frontier_intake_reviews/<review_id>.done.json`
- **Shape stability:** `schema_version` starts at `1`. Additive fields are allowed in v1.x; renamed or removed fields require a schema-version bump.
- **Required fields:** every field in the example below is required unless explicitly nullable.
- **Sentinel ledger:** the sidecar records both the current cycle's review mode and the rolling-quarter full-sweep status. This avoids needing a second ledger file in v1.

```json
{
  "schema_version": 1,
  "review_id": "frontier-intake-2026-06",
  "cadence": "monthly",
  "started_at": "...",
  "done_at": "...",
  "criteria_met": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
  "category_review_mode": {
    "threat_intelligence": "sentinel",
    "ai_agent_patterns": "full",
    "compliance_underwriting": "sentinel",
    "competitive_landscape": "sentinel",
    "operator_personal_network": "full"
  },
  "rolling_quarter_full_sweep": {
    "quarter_id": "2026-Q2",
    "threat_intelligence": true,
    "ai_agent_patterns": true,
    "compliance_underwriting": false,
    "competitive_landscape": true,
    "operator_personal_network": true
  },
  "candidates_surfaced": ["..."],
  "spec_update_triggers_fired": [],
  "product_pivot_triggers_fired": [],
  "grok_audit_outputs": [
    "audit_outputs/compliance_and_trend_watch_2026-06-...md"
  ],
  "operator_signature_evidence_id": "evd-..."
}
```

`grok_audit_outputs` is an array because §8.5 allows splitting; even a single combined audit is represented as a one-element array for shape stability. `category_review_mode` records sentinel vs full for §9.1 enforcement. `rolling_quarter_full_sweep` records the full-sweep requirement from §9.1 without creating a separate ledger.

The JSON sidecar is an audit artifact, not a progress tracker. It is generated or assembled only when a review is being claimed ready / done / signed, and it is covered by the §8 Grok audit packet.

---

## §10 Open Questions for Matt

These resolve into locked decisions at §11 sign-off. Until then, the spec is pre-§11.

### Resolved 2026-05-26 by operator (pending §11 lock as D-n)

Seven §10 questions were resolved in the 2026-05-26 revision passes. They remain in this section as numbered placeholders for traceability; the resolutions are reflected in the spec body above and become D-numbered locked decisions when Matt signs §11.

- **Q1 — Calendar-rhythm specifics (§3).** Resolved: first-Monday monthly trigger; BC-holiday shift to next non-holiday weekday; 7-day operator deferral window; compact no-signal cycle allowed with source/mode record; no more than two consecutive no-signal cycles; quarterly deep review cannot be replaced by a no-signal cycle. Full statement inline in §3 Calendar rhythm. (Becomes Dn at §11.)
- **Q3 — Source-list additions (§2.7).** Resolved: Matt may operator-add or remove sources with logged reason; Cursor/assistant may only propose evidence-backed source changes; category-boundary, sentinel-rule, or compliance-boundary changes require spec amendment and §11 re-signature. Full statement inline in §2.7. (Becomes Dn at §11.)
- **Q4 — Pivot-trigger threshold (§7 P1).** Resolved: "≥5 relevant MSP conversations across at least two distinct MSP profiles, OR ≥3 conversations sharing the same concrete negative reason." Definitions for "MSP profile" and "concrete negative reason" are inline in §7 P1. (Becomes Dn at §11.)
- **Q7 — Done-declaration JSON shape (§9).** Resolved: sidecar path `audit_outputs/frontier_intake_reviews/<review_id>.done.json`; `schema_version: 1`; required shape defined inline; sentinel/full-cycle status tracked inside `rolling_quarter_full_sweep`, not a separate v1 ledger. Full statement inline in §9 Machine-checkable done declaration. (Becomes Dn at §11.)
- **Q8 — Vendor-source weighting (§2.6).** Resolved: vendor sources cannot be sole evidence for candidates or for compliance / regulatory / underwriting / framework-alignment conclusions. Vendor sources may stand alone only for confirmations that do not create a candidate, change governance, or support a buyer/compliance claim. Full statement inline in §2.6. (Becomes Dn at §11.)
- **Q10 — Compliance-claim boundary inheritance order.** Resolved: this document §5 is canonical for the project; the Cyber Insurance Evidence Package §9 is the buyer-surface application; on divergence, this document wins and the buyer-facing artifact is updated to match. Full statement inline in §5.5. (Becomes Dn at §11.)
- **Q11 — Downstream constant sync (§5.5 / Build Queue item 2).** Resolved: after §11 signature, updating `audit_tools/complete_gate.py` comments/source-of-truth references to cite this spec is routine enforcement-reference maintenance, not a cyber-insurance spec amendment. Because `audit_tools/` is now in scope, the change itself must run through `complete_gate.py`. Constant values remain unchanged unless the §5.1 or §5.5 lists change. Full statement inline in §5.5 and queued as Build List item 2 in `PROJECT_BUILD_AND_AUDIT_QUEUE.md`. (Becomes Dn at §11.)

### Still open, non-blocking for v1 sign-off

### Q2. Quarterly deep-review composition

The deep review re-evaluates parked candidates. Which parked candidates — all `live park`, or also `deep park`? Re-evaluation criteria: same as initial gating, or a different bar?

### Q5. Allowed-context carve-out enumeration

§5.3 names allowed contexts (non-scope statement, forbidden-language list, anti-pattern section, retraction record). Are there others worth naming explicitly? Comparison tables vs. competitors? Training material? Internal-only documents?

### Q6. Framework-crosswalk standard

§5.4 defines the conditions for permissible framework crosswalks. Should this spec include a worked example of a compliant crosswalk vs. a non-compliant one, or is enumeration of the four conditions sufficient?

### Q9. Pivot-trigger surfacing protocol

§7 says pivot triggers are surfaced "immediately to the operator." What does "immediately" mean operationally — interrupt current work, log only in the review entry, or both? Should there be a separate `pivot_alert.json` artifact?

---

## §11 Sign-Off

This section records Matt's §11 signature and the decisions locked by that signature.

### Locked decisions (D1–Dn) — populated on sign-off

| # | Decision | Note |
|---|---|---|
| D1 | Q1 — Calendar-rhythm specifics | First-Monday monthly trigger; BC-holiday shift to next non-holiday weekday; 7-day operator deferral window; compact no-signal cycle allowed with source/mode record; no more than two consecutive no-signal cycles; quarterly deep review cannot be replaced by a no-signal cycle. |
| D2 | Q3 — Source-list additions | Matt may operator-add or remove sources with logged reason; Cursor/assistant may only propose evidence-backed source changes; category-boundary, sentinel-rule, or compliance-boundary changes require spec amendment and §11 re-signature. |
| D3 | Q4 — Pivot-trigger threshold (§7 P1) | P1 fires at ≥5 relevant MSP conversations across at least two distinct MSP profiles, OR ≥3 conversations sharing the same concrete negative reason. |
| D4 | Q7 — Done-declaration JSON shape | Sidecar path is `audit_outputs/frontier_intake_reviews/<review_id>.done.json`; `schema_version: 1`; required shape defined inline; sentinel/full-cycle status tracked inside `rolling_quarter_full_sweep`, not a separate v1 ledger. |
| D5 | Q8 — Vendor-source weighting | Vendor sources cannot be sole evidence for candidates or for compliance / regulatory / underwriting / framework-alignment conclusions. Vendor sources may stand alone only for confirmations that do not create a candidate, change governance, or support a buyer/compliance claim. |
| D6 | Q10 — Compliance-claim boundary inheritance order | This document §5 is canonical for the project; the Cyber Insurance Evidence Package §9 is the buyer-surface application; on divergence, this document wins and the buyer-facing artifact updates to match. |
| D7 | Q11 — Downstream constant sync | After §11 signature, updating `audit_tools/complete_gate.py` comments/source-of-truth references to cite this spec is routine enforcement-reference maintenance, not a cyber-insurance spec amendment. Because `audit_tools/` is in scope, the change itself must run through `complete_gate.py`. Constant values remain unchanged unless §5.1 or §5.5 changes. |

### Sign-off line

> *Matt Nichol May 26th. 2026*

Per the Authorship Rule (2026-05-25/26): the sign-off text is operator-authored. AI may help structure, may proofread, may flag inconsistencies — AI does not draft the operator's signature wording or attribute decisions to the operator without explicit operator authorship.

### What sign-off does

Signing this spec:

1. Locks D1–Dn from §10 question resolution.
2. Authorizes the monthly-cadence Frontier Intake Review process to continue under this contract.
3. Establishes §5 as the canonical compliance-claim boundary for the project; downstream artifacts (Cyber Insurance Evidence Package §9, future client documents) inherit and apply it.
4. Activates the §8 Grok-audit posture for every future review entry, with the §9 done-criteria checklist as the readiness contract.

Signing does **not**:

- Promote any specific candidate currently in `Frontier_Intake_Log.md` or `think_sheet.md`. Promotion remains the operator's per-candidate call.
- Authorize any spec amendment automatically. Amendments still go through spec-first discipline.
- Trigger any product pivot automatically. Pivots remain operator decisions.
- Override any of the seven non-negotiables in `VISION.md`.

---

## Cross-references

- `VISION.md` — seven non-negotiables that govern this spec and provide the non-negotiable-contradiction trigger (§7 P5)
- `Frontier_Intake_Log.md` — the running output artifact of this process; cadence rule locked there
- `THREAT_INTEL_LOG.md` — operator-network sourced intelligence; threat-side evidence
- `think_sheet.md` — gating ground for any candidate this process surfaces; this process is discovery, gating is separate
- `MILESTONE_ARC.md` — stage-arc reference for §7 P2 (stage-arc obsolescence)
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` — buyer-surface application of §5 boundaries to the cyber-insurance buyer surface. Per the §5.5 lock (Q10 resolved 2026-05-26), this document is canonical and the cyber-insurance package §9 is the application; on divergence, this document wins and the buyer-facing artifact updates to match
- `audit_tools/complete_gate.py` — the enforcement layer for §8 Grok audit requirements (v1.1 onward; signed-spec scope means this spec triggers the gate only after §11 sign-off)
- `PROJECT_ACTIVITY_LOG.md` — where §7 pivot decisions are recorded with full provenance

---

**End of draft. Pre-§11. No runtime code, automation, or progress-tracker changes are authorized by this document.**
