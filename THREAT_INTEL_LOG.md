# NorthStar + SwarmCommand — Threat Intel Log

**Purpose:** The swarm's evolution is recorded here. Every time a new threat pattern is ingested — from a feed, from a customer report, or from a Red battery synthesis — log it. Every time that intake produces a policy update, link it.

This file is what proves NorthStar is *actually getting smarter over time* rather than just claiming to.

**See also:** `VISION.md` (why this file exists), `MILESTONE_ARC.md` C1 (threat-intel ingestion agent).

**Last reviewed:** 2026-05-25

---

## Intake Sources (Planned)

The threat-intel ingestion agent (Stage C milestone C1) will pull from these sources on a regular cadence. Until that agent exists, intake is manual.

| Source | URL | Cadence | Cost | Status |
|---|---|---|---|---|
| CISA KEV (Known Exploited Vulnerabilities) | `https://www.cisa.gov/known-exploited-vulnerabilities-catalog` | Daily | Free | Planned |
| MITRE ATT&CK | `https://attack.mitre.org/` | Quarterly | Free | Planned |
| abuse.ch URLhaus | `https://urlhaus.abuse.ch/` | Daily | Free | Planned |
| abuse.ch MalwareBazaar | `https://bazaar.abuse.ch/` | Daily | Free | Planned |
| abuse.ch ThreatFox | `https://threatfox.abuse.ch/` | Daily | Free | Planned |
| Phishtank | `https://www.phishtank.com/` | Daily | Free | Planned |
| US-CERT / CISA alerts | `https://www.cisa.gov/news-events/cybersecurity-advisories` | As published | Free | Planned |
| AlienVault OTX | `https://otx.alienvault.com/` | Configurable | Free tier | Planned |

**Operating rule:** Always start from free, high-signal sources. Paid feeds (Recorded Future, Mandiant, etc.) are deferred until ARR justifies them.

---

## Entry Format

```markdown
## YYYY-MM-DD — Short title

**Source:** Where the intel came from (feed name, MSP report, Red battery synthesis, customer escalation).
**Pattern class:** Vendor invoice fraud / executive impersonation / ransomware precursor / etc.
**Pattern shape:** Plain-English description of what the new attack looks like.
**Evidence:** Sample IDs, links, or raw indicators (never store customer data here).
**Action taken:** None / sandbox test added / mutation proposed / policy updated / promoted.
**Policy update link:** Path to the signed policy update, if any.
**Verification:** Test name and result that proves the new pattern is now defended against.
```

---

## Entries

### 2026-05-22 — Vendor-invoice fraud recall floor (5 weak shapes)

**Source:** Phase 1.5 full 40-case `grok-4` rerun diagnostic
**Pattern class:** Vendor invoice fraud
**Pattern shape:** Five weak shapes the locked prompt under-scored:
1. First invoice after onboarding with remittance instructions only inside the attached PDF.
2. Updated remit-to address with old instructions declared invalid.
3. Fake thread continuity (`Re:`, "following up as discussed below", "as discussed" with no quoted history).
4. High-value emergency invoice approval before EOD tied to shipment / operations pressure.
5. Explicit new ACH / banking details with urgency.
**Evidence:** `eval_report_2026_05_22_phase_1_5_rerun.md` (FAIL), `eval_report_2026_05_22_phase_1_5_vf-00{1..5}_diagnostic.md` (5/5 PASS post-patch)
**Action taken:** No-spend prompt remediation. Added "Phase 1.5 vendor-invoice recall floor" section to `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT`.
**Policy update link:** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/email_risk_scoring_agent.py`
**Verification:** `tests/test_email_risk_scoring_agent.py::test_phase_1_5_vendor_invoice_recall_floor_is_pinned` (28 passed, full suite 472 passed)

---

### 2026-05-25 — Canadian + North American email fraud market intelligence (multi-source data mine)

**Source:** Canadian Anti-Fraud Centre 2024/2025 Annual Statistical Reports; Canadian Centre for Cyber Security National Cyber Threat Assessment 2025-2026; Payments Canada 2024 business payment fraud study; KuppingerCole Email Security Leadership Compass 2025; Mordor Intelligence cloud email security market report 2025; Accelerate Okanagan / KPMG 2024 economic impact study; Central Okanagan Economic Development Commission (`investkelowna.com`); Vendr Abnormal Security pricing data; CostBench email security pricing benchmarks; Cybersecurity Canada BEC analysis; multiple Castanet / OK-Go / Penticton Now reports on the Okanagan tech sector.

**Intel class:** Market intelligence / competitive landscape / threat scale (multi-domain data mine, not a single attack pattern).

**Findings — Canada fraud landscape:**

- 2025 total Canadian fraud losses (CAFC reported): **$704M** (record high). 2024: $647M.
- 2025 spear phishing / BEC reported: **$67.9M**. 2024: $67.5M.
- CAFC explicitly estimates only **5-10% of victims report**, so true Canadian BEC loss is plausibly **$679M-$1.36B annually**.
- **1 in 5 Canadian businesses (20%)** experienced payment fraud in past 6 months (Payments Canada 2024).
- Top business fraud type: **impersonator fraud at 25%** — phone or email appearing to come from a trusted business source. Direct overlap with NorthStar's BEC / vendor-impersonation detector surface.
- Local example: Vancouver-area law firm hit by BEC for **$2.3M CAD** wire to Hong Kong (CAFC press release, July 2025). Recovered through international cooperation. Lower Mainland BC, 2025.
- Strategic threat assessment (CCCS NCTA 2025-2026): cybercrime is "persistent, widespread, disruptive" against Canadian organizations. Ransomware up 26% year-over-year. SMBs increasingly targeted via Cybercrime-as-a-Service.

**Findings — competitive market shape:**

- Cloud-based email security market: **$5.55B in 2025**, projected **$11.22B by 2031** (12.45% CAGR).
- Large enterprises = 69.35% of 2025 revenue. SMBs = ~30%, but growing faster at **13.98% CAGR**.
- Pricing benchmarks: SMB direct $3-8/user/month, mid-market $20-40/user/year, enterprise $30-80+/user/year. MSP-channel typically $1-5/user/month with volume discounts.
- Enterprise-focused players: Proofpoint, Mimecast, Cisco Secure Email, Abnormal Security, Darktrace.
- Mixed (SMB + enterprise): Barracuda, Trend Micro, Sophos, Fortinet, OpenText, IRONSCALES, Check Point Harmony Email (Avanan).
- **MSP-channel-focused (NorthStar's actual competitive set):** Vade / Hornetsecurity (12,000+ partners, 125,000 customers), Datto SaaS Defense, Coro, N-able Mail Assure, plus smaller European players (Mailinblack FR, xorlab CH).
- **Major market shift — December 2025:** Proofpoint acquired Hornetsecurity for $1B and launched "Proofpoint 365 Total Protection" in North America via Pax8 marketplace. The largest enterprise email security vendor is now actively consolidating the MSP channel for SMBs. Every Pax8 MSP in North America is being pitched this product in 2026.
- **Differentiation gap identified:** competitors' marketing leads with detection accuracy, AI sophistication, or scale. None lead with auditability + explainability + per-tenant tuning + reversibility + evidence depth. That's NorthStar's wedge.

**Findings — Okanagan tech sector and local MSP landscape:**

- Okanagan tech sector: **$4.98B annual economic impact** (Accelerate Okanagan + KPMG, 2024 report on 2023 data). Up nearly $3B from the 2017 study.
- 787 tech companies, 32,645 jobs supported, $3.16B paid in salaries.
- **14% average YoY growth over the past 10 years.**
- Central Okanagan (Kelowna / West Kelowna / Lake Country) specifically: $3.01B impact, 19,747 jobs, 467 businesses. Per BC government, "fastest-growing technology hub in BC."
- Subsector mix: SaaS 16%, Life sciences 11%, **AI 9%** (~$448M), advanced manufacturing 8%, cleantech 5%, gaming/animation 4%, aerospace 3%, agritech 3%.
- **65% of Okanagan tech companies planning to hire** in next year.
- Stated headwinds (per Accelerate Okanagan CEO): access to capital, markets, and talent.
- **Local MSP discovery target list (real names, all reachable):**
  - Carpathia IT (Kelowna / Penticton / Vernon)
  - NetDNA MSP (Penticton, 15+ years, IT + AI + marketing)
  - EC Managed IT (Vernon / North Okanagan)
  - IT Works MSP BC (Kelowna, mid-sized regional, 25-200 employee target)
  - SFY IT (Kelowna, 20+ years)
  - Good IT (Kelowna, sells MDR locally — direct competitor signal)
- **Useful positioning quote** (from IT Works MSP BC's own public marketing copy): *"Most Kelowna MSPs are Vancouver or Calgary firms treating the Okanagan as a secondary market."* That's the wedge.
- Cybersecurity demand signals: KF Aerospace (1,100 employees, Kelowna-based) actively hiring Cyber Security Analyst (real local enterprise security buyer); Good IT runs a local MDR practice; cybersecurity analyst roles listed as consistent demand in Kelowna.

**Strategic implications recorded:**

- Stage A scope confirmed and narrowed: **email fraud detection for SMBs via MSPs**. Not "cybersecurity in general." Sector is bloated; depth beats breadth.
- Differentiation standards locked: **auditability, explainability, per-tenant tuning, reversibility, evidence depth.** No competitor leads with this combination.
- Build queue re-ordering decided in this session:
  - **A — Deepen (top priority):** make existing 7 detectors excellent; improve client-facing explanation language; strengthen evidence package; better operator triage UX.
  - **B — Deepen BEC coverage (second priority):** Callback Phishing / TOAD body-language detector; Micro-Temporal Mismatches; Client-facing 5-axis Email Scoring Rubric.
  - **C — Defer (widening scope):** Sender-provenance / geo-velocity (also held by today's `needs_more_samples` proof verdict); Structural Payload Anomalies / OCR; TOAD Part 2 phone baselining.
  - **D — Stage B/C only:** auto-quarantine connectors, cross-tenant signature sharing, threat-intel autonomy, production-side self-evolving mutation. Important, not discarded; gated on Stage A revenue + customer trust + risk infrastructure.
- MSP discovery target list now contains real, locally reachable names rather than abstract categories.
- Pitch wedge sharpened to a one-line positioning: *"NorthStar is MDR for the inbox layer, focused on email fraud, with auditable AI as the standard."*

**Action taken:** No runtime changes. Strategy / positioning / build-prioritization record only. Trackers (`PROJECT_HANDSHAKE.md`, `PROGRESS.md`, `PROJECT_ACTIVITY_LOG.md`) updated separately per their own conventions.

**Policy update link:** N/A (no signed policy change resulted from this entry).

**Verification:** Sources cited above; multi-source convergence (Canadian government, Canadian industry survey, US government competitive analyses, local Accelerate Okanagan / KPMG study, Central Okanagan EDC, vendor pricing benchmarks) used to triangulate findings rather than relying on any single source. Quoted figures are attributable to a named report and traceable.

---

## Empty Intake Queue

Future entries land below this line as new threat patterns are ingested.

(none yet)
