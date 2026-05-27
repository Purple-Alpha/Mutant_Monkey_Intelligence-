# Frontier Intake Log
NorthStar + SwarmCommand Venture

## Purpose
Operator-driven log capturing emerging AI / agent / threat patterns observed during periodic intake reviews. Each review identifies candidates that may warrant full gate evaluation in `think_sheet.md`. Cadence is determined by the cheaper-proof outcome (Review #1) and may be adjusted as evidence accumulates.

## Cadence rule (locked 2026-05-25)
- 0-1 candidates surfaced per review → defer recurring discipline; ad-hoc reviews suffice
- 2-3 → commit to a quarterly cadence
- 4+ → commit to a monthly cadence

## Vocabulary boundary
"AGI" / "AGI-adjacent" framing from source feeds does **not** enter NorthStar's product / outreach / spec / bible voice. Stage A surfaces use plain English. The wedge stays auditability + explainability + per-tenant tuning + reversibility + evidence depth.

## Intake protocol
1. Survey the starter source list across four categories: threat, AI/agent, MSP/buyer, competitor.
2. For each finding, classify as one of:
   - **Confirmation** — reinforces NorthStar's existing direction; record but do not surface as a candidate.
   - **Candidate** — would plausibly survive the 5-axis rubric's Strategic Fit ≥ 1 + Revenue Path ≥ 1 sniff test; surface for formal gating in `think_sheet.md`.
   - **Noise** — irrelevant or already covered; do not record.
3. Record citations for every candidate and every confirmation.
4. Count candidates → apply cadence rule above.
5. Update trackers; **do not** auto-add surfaced candidates to `think_sheet.md` — formal gating happens only when the operator picks them up one at a time. The intake is discovery; gating is a separate step.

---

## Review #1 — 2026-05-25 (cheaper-proof one-shot exercise)

**Operator:** Matt Nichol
**Reviewer agent:** Claude Opus 4.7
**Time-box:** Single session, ~1-2 hours
**Purpose of this review:** Decide cadence per the locked rule above.

### Source list reviewed

Threat side:
- CISA Phishing Guidance + 2026 advisories
- FBI Internet Crime Complaint Center (IC3) Public Service Announcements, May 2026
- Cloud Security Alliance (CSA) AI Safety Initiative research notes, May 2026
- Abnormal Security 2026 Attack Landscape Report (~800,000 email attacks observed H2 2025)
- Proofpoint AI-Driven Attacks 2026 briefing (cited in derived research)
- Cybertechnology Insights 2026 AI-deepfake-BEC research report

AI/agent side:
- OWASP Top 10 for LLM Applications v2025 (current as of April 2026)
- Microsoft Agent Framework FIDES (Flow Integrity Deterministic Enforcement System), May 2026 release
- Open-source agent guardrail projects (Parry, sentinel-inject, PromptGuard-for-Agents)

MSP/buyer side:
- Nuronus 2026 MSP Cyber Insurance Approval Guide
- Data Centre Solutions 2026 MSP cyber insurance notes
- GetCybr NIS2 + NIST CSF 2.0 MSP service-line guides
- Bronston Legal MSP compliance regulations summary

Competitor side:
- Abnormal AI: Inbound Email Security platform, Attune 1.0 behavioral foundation model (March 2026), Detection 360 Insights (GA), Custom AI Models (early access), Auto-Forwarding Mail Protection for Microsoft 365
- Microsoft Defender for Office 365 phishing detection product notes
- IronScales 2026 threat intelligence (triple-brand credential harvest)

Cross-referenced internal sources:
- `THREAT_INTEL_LOG.md` 2026-05-25 entry (Canadian + North American email fraud market intelligence + Okanagan tech sector)
- `PROGRESS.md` task list (verified what NorthStar already covers)

### Findings — confirmations of existing direction (NOT candidates)

These items reinforce NorthStar's locked Stage A wedge or confirm an existing detector / spec is correctly placed. They are recorded as durable signals but **do not** surface as candidates.

1. **AI-deepfake BEC (40% of BEC by Q1 2026; voice clones from 3 sec audio; multi-modal video calls with AI-generated participants).** Defense recommended across all sources is mandatory pre-established out-of-band verification using a stored directory number. NorthStar's Two-Channel Confirmation v1 + Vendor Baseline Store + Financial State Ledger already implement this defense at the email layer. Voice/video deepfake handling is a Stage B/C multi-channel concern and is correctly out of Stage A scope. *Source: Cybertechnology Insights 2026 research report; SecurityElites AI Red Team breakdown.*

2. **Multi-persona BEC campaigns (Proofpoint 2026 AI-Driven Attacks briefing).** AI coordinates fake CFO + legal adviser + supplier across weeks to build social proof before the final payment request. Defense: cross-relationship continuity checking + out-of-band verification. NorthStar's roadmap addresses this through (i) `behavioral_deviation_flags` in the scoring agent for per-email flags and (ii) **Component A (NorthStar Analyst Reasoning Layer / cross-detector synthesis)** from today's AGI-Adjacent decomposition, which is the cross-email synthesis layer that would catch the multi-week pattern. Confirms Component A's promotion is the right next step in the explainability lane. *Source: SecurityElites breakdown of Proofpoint briefing.*

3. **Lateral BEC concentration at enterprise (Abnormal: ~25% of BEC at large orgs vs. 0.24% at small orgs).** Lateral attacks (originating from genuinely compromised internal accounts) require enterprise-scale identity-and-behavior baselines that Abnormal sells at scale. **This finding strengthens NorthStar's SMB wedge** — lateral BEC is nearly nonexistent at the SMB end of the market, so Abnormal's lateral-attack moat does not matter for NorthStar's Stage A target audience. *Source: Abnormal AI 2026 Attack Landscape Report.*

4. **Multi-channel BEC (email + WhatsApp + phone, used in coordination).** Out of Stage A scope; matches today's Component B verdict (cross-domain expansion is Stage B/C only). *Source: PhishSkill GCC 2026 BEC trends.*

5. **Microsoft FIDES (Flow Integrity Deterministic Enforcement System) for prompt injection, May 2026.** Information-flow control with `IntegrityLabel` (trusted/untrusted) × `ConfidentialityLabel` (public/private/user_identity) propagated through tool calls; deterministic policy enforcement before sensitive tool invocation; `approval_on_violation=True` mode with human-in-the-loop. **This is the most sophisticated frontier work converging on what NorthStar already does** — deterministic, label-based, human-approval-on-sensitive-action. Confirms NorthStar's architectural direction is on-trend, not behind. Worth studying as reference architecture if/when NorthStar scales Stage B agent surface. *Source: Microsoft Agent Framework devblog + GitHub PR #5024.*

6. **OWASP LLM Top 10 v2025 (still current April 2026).** Coverage check against NorthStar's runtime:
   - **LLM01 Prompt Injection** — covered (Adversarial Prompt-Injection Detector v1 LANDED)
   - **LLM02 Sensitive Information Disclosure** — covered (hash-only Vendor Baseline Store, no PII in prompts/logs)
   - **LLM06 Excessive Agency** — covered (Tiered Detection Intensity, kill switch, lift-only invariants, human approval)
   - **LLM07 System Prompt Leakage** — covered (system-prompt-extraction guards in Adversarial Prompt-Injection Detector)
   - **LLM10 Unbounded Consumption** — *partial / unclear coverage*; surfaced as Candidate 2 below.
   *Source: OWASP Top 10 for LLM Applications v2025 PDF; Wraith 2026-04-19 annotated edition.*

7. **MSP cyber insurance + NIS2 + NIST CSF 2.0 driving evidence-not-checkboxes shift in 2026.** Underwriters now demand exports/screenshots/reports proving controls. SMB clients hearing about NIST CSF 2.0 from insurers and procurement. NIS2 directly regulates EU MSPs (24/72-hour incident reporting). **This is wedge alignment, not a candidate by itself** — but the *packaging* of NorthStar's existing audit trail into a buyer-ready evidence bundle for cyber-insurance underwriting is a candidate; see Candidate 3 below. *Source: Nuronus 2026 MSP cyber insurance guide; Data Centre Solutions 2026 notes; GetCybr NIS2 + NIST CSF 2.0 guides; Bronston Legal MSP compliance summary.*

8. **Abnormal Detection 360 Insights (GA) — explainability is becoming a competitive axis.** Abnormal is selling visibility into the behavioral reasoning behind every AI determination. Confirms explainability is a frontier-mainstream wedge; NorthStar's *deterministic* explainability (rubric-based) remains a differentiated approach for the auditability market segment. *Source: Abnormal AI Attune 1.0 launch press release (March 2026).*

### Findings — surfaced candidates

The following five patterns each pass the sniff test ("would I plausibly spend 30 min stress-testing this against the 5-axis rubric?"). They are listed here for the operator to pick up one at a time when ready. Each will earn its own scored row + 7-question stress test in `think_sheet.md` when the operator chooses to gate it. **The intake does not pre-score them.**

#### Candidate 1 — Department-Level Internal Impersonation Detector

**Pattern:** Abnormal's 2026 Attack Landscape Report (analysis of ~800,000 email attacks observed H2 2025) shows that at SMB-scale organizations (NorthStar's Stage A target), the dominant BEC pattern is **employee impersonation (45.3%)** + **generic internal department impersonation (36.7%)** — fake IT helpdesk notices, HR benefits updates, payroll system alerts. VIP/executive impersonation is only 8.4%.

**NorthStar gap:** The current detector set covers vendor-side (Vendor Baseline Store, Financial State Ledger, Document Metadata Fingerprinting) and external-impersonation header divergence (From / Reply-To / Return-Path / Sender). It does **not** explicitly cover internal-department lure patterns where the From: looks like a legitimate internal sender and the body matches a known fake-IT / fake-HR / fake-payroll template.

**Why this is a Stage A fit:** SMB-target audience is exactly where this pattern dominates; vendor-impersonation alone leaves the 36.7% generic-internal-impersonation slice uncovered.

**Source:** Abnormal AI 2026 Attack Landscape Report — `https://abnormal.ai/blog/2026-attack-landscape-report-bec`.

#### Candidate 2 — OWASP LLM10 (Unbounded Consumption) Coverage

**Pattern:** OWASP LLM Top 10 v2025 LLM10 covers recursive output forcing, context-window exhaustion, and tool-call bombs (model calls tool, tool response triggers another tool call, chain doesn't terminate). Defense: per-request input/output token caps, max tool-call depth per conversation, per-user rate limit at the inference layer, circuit breaker on cost-per-request anomalies.

**NorthStar gap:** Tiered Detection Intensity, kill switch, and lift-only invariants address LLM06 Excessive Agency. LLM10 Unbounded Consumption (depth caps + token caps + cost-per-request circuit breaker) is **not explicitly verified** in the current runtime. May already exist implicitly via timeouts but is not documented as a guardrail surface.

**Why this is a Stage A fit:** Operational hardening, low-cost, internal-only. Likely scores in revisit band (Provability is low because it's invisible to buyers) but matters for NorthStar's reliability story when scaling to multi-tenant traffic.

**Source:** OWASP Top 10 for LLM Applications v2025 PDF — `https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf`; Wraith annotated 2026 edition — `https://wraith.sh/learn/owasp-top-10-llm-annotated`.

#### Candidate 3 — Cyber Insurance Evidence Package (positioning + packaging)

**Pattern:** 2026 MSP cyber-insurance underwriting has decisively shifted from checkboxes to evidence packages — exports, screenshots, reports proving controls. NIS2 (EU) and NIST CSF 2.0 (North America) reinforce this shift. SMB clients now ask their MSPs for help assembling the evidence package because they cannot answer the 2026 underwriting questions on their own.

**NorthStar gap:** Not a detector gap — a **positioning/packaging** opportunity. NorthStar already has the building blocks (`Inbox_Shield_Sample_Monthly_Report.md`, `Acme_Effective_Parameter_Report_Demo.md`, append-only Blackboard, Decision Auditor logs, signed §11 specs, deterministic detector evidence chains). What does not yet exist is a **buyer-ready bundle** that packages these artifacts specifically for the cyber-insurance underwriting question set.

**Why this is a Stage A fit:** This is the cleanest wedge alignment from the entire intake — NorthStar's auditability + evidence depth + per-tenant logs are exactly what 2026 MSPs need. Could become a sales tool that closes deals faster than a per-feature pitch.

**Source:** Nuronus 2026 MSP cyber insurance guide — `https://nuronus.com/blog/cyber-insurance-checklist-msp-2026`; Data Centre Solutions 2026 MSP cyber insurance notes — `https://datacentre.solutions/blogs/58789/what-msps-need-to-know-about-cyber-insurance-in-2026`; GetCybr NIST CSF 2.0 service-line guide — `https://getcybr.com/insights/msp-nist-csf-2-compliance-service-line/`.

#### Candidate 4 — Auto-Forwarding Inspection (outbound rule monitoring + downstream-mail inspection)

**Pattern:** Microsoft 365 auto-forwarding rules are a documented exfiltration and persistence mechanism in compromised accounts. Abnormal launched Auto-Forwarding Mail Protection in 2026 to inspect mail before it reaches downstream tools (Salesforce, Zendesk, ServiceNow) — pre-delivery rather than post-delivery. The attack surface is: an attacker compromises an MSP-managed M365 account, sets up a forwarding rule, and exfiltrates inbound mail without ever interacting with the inbox UI again.

**NorthStar gap:** Current detector set inspects inbound mail per-email. It does **not** monitor outbound auto-forwarding rule changes or inspect mail being forwarded to external destinations. Stage A scope is "inbox-layer MDR" so this does fit the wedge.

**Why this is a Stage A fit:** SMB MSPs manage Microsoft 365 tenants. Auto-forwarding-rule abuse is a real, post-account-compromise pattern. Caveat: SMB auto-forwarding is less complex than enterprise, so Strategic Fit may score 1 (adjacent) rather than 2 (directly advances). Worth stress-testing.

**Source:** Abnormal AI Auto-Forwarding Mail Protection blog — `https://abnormal.ai/blog/auto-forwarding-mail-protection-microsoft-365`.

#### Candidate 5 — Device-Code / OAuth-Consent Phishing Detector

**Pattern:** FBI IC3 Public Service Announcement, 21 May 2026 (PSA260521): a new Phishing-as-a-Service kit called **Kali365**, first observed April 2026, distributed via Telegram, captures Microsoft 365 OAuth access/refresh tokens and bypasses MFA via OAuth device-code flow. The phishing email impersonates trusted cloud productivity / document-sharing services and contains a "device code" with instructions to visit a legitimate Microsoft verification page. CSA's EvilTokens research note (May 2026) documents the same pattern expanding via AI-driven automation. CISA + FBI mitigation: disable / restrict OAuth device-code flow in Microsoft Entra Conditional Access; audit OAuth grants.

**NorthStar gap:** This attack pattern is a **specific email body + URL combination** that current NorthStar detectors do not explicitly look for. The Adversarial Prompt-Injection Detector covers some adjacent patterns (instruction-override, system-prompt-extraction) but device-code phishing is a distinct lure shape: legitimate Microsoft URL + body content directing user to enter a code + OAuth-token capture as the goal (not credential capture).

**Why this is a Stage A fit:** SMB Microsoft 365 tenants are exactly the target audience. The attack bypasses MFA (which most MSPs already deployed). It is current (FBI PSA dated less than 5 days before this intake). It is specific enough to detect with a deterministic body-content + URL pattern detector.

**Source:** FBI IC3 PSA 2026-05-21 — `https://www.ic3.gov/PSA/2026/PSA260521`; CSA AI Safety Initiative research note (May 2026) on OAuth Consent Phishing / EvilTokens — `https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/05/CSA_research_note_oauth_consent_phishing_ai_identity_20260521-csa-styled.pdf`.

### Cadence verdict

**Total candidates surfaced: 5.**

Per the locked cadence rule: **4+ candidates → monthly cadence.** Recurring discipline is committed.

**Refinement flag (revisit at 90-day mark):** This is the first intake ever, so the count may reflect an accumulated backlog of trends that have built up over the months since these patterns emerged, rather than steady-state pace. Plausible that subsequent intakes will surface 2-3 candidates per month rather than 5. Recommend re-evaluating cadence at the third intake (approximately 2026-08): if the steady-state count is 2-3, drop to quarterly; if it remains 4+, stay at monthly.

### Notes / observations

- **Vocabulary boundary held without being tested.** None of the source feeds in this review used "AGI" or "AGI-adjacent" framing in the email-security space. The boundary remains in force.
- **Strong wedge alignment confirmation.** The 2026 frontier (Microsoft FIDES; Abnormal Detection 360 Insights; cyber-insurance evidence-not-checkboxes shift) is converging on auditability, deterministic explainability, evidence depth, and human-approval-on-sensitive-action — exactly NorthStar's locked differentiation standards. This intake's primary signal is: NorthStar is on-trend, not behind.
- **One unexpected market intelligence finding.** Lateral BEC concentration at enterprise (~25%) vs. SMB (0.24%) means Abnormal's strongest moat (identity-and-behavior baselines for lateral attacks) is irrelevant at the SMB end. NorthStar's SMB-via-MSP wedge is structurally insulated from Abnormal's enterprise advantage. Worth recording in `THREAT_INTEL_LOG.md` at the next refresh.
- **No noise-only findings discarded silently.** Triple-brand credential harvest (IronScales) was considered but classified as already-covered-indirectly by the existing Adversarial Prompt-Injection Detector + header-divergence detector. Mentioned here for completeness.

### Next step

Operator chooses the next move. Three honest options:
1. **Pick one candidate** and run the full 5-axis + 7-question gate against it in `think_sheet.md`.
2. **Defer all five** and let them sit in this log until the next monthly intake or until external pressure (e.g., a real fraud incident matching one of the patterns) elevates one above the others.
3. **Mark a subset for prioritized gating** and pick them up across the next few sessions.

The intake itself is complete. No detector, spec, or runtime change is authorized by this intake.

---
