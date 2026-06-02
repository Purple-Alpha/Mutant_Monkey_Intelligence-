# Cyber-Insurance Evidence Pain Points — Research Map

**Status:** Research input only. Pre-spec. Unsigned. Not §11. Not client-facing copy. Not implementation authorization.

**Captured:** 2026-06-01 by Cursor (Claude Opus 4.7) at operator request while Matt gathers external evidence / pain-point inputs around cyber-insurance underwriting and evidence readiness.

**Purpose of this artifact:** Give Matt and future sessions a single lightweight capture surface for *what we are investigating* — not what NorthStar claims, ships, or has proven in MSP discovery.

**Related artifacts (read for context; this file does not amend them):**
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` (§13-signed spec — do not edit from this research pass)
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Cheaper_Proof_Runbook.md` (D10 MSP discovery gate — unchanged by this file)
- `4. Product_Roadmap/_NorthStar_Cyber_Insurance_Vendor_Payment_Integrity_SPARK.md` (direction SPARK — vocabulary boundary)
- `4. Product_Roadmap/Research_Inputs/Vendor_Payment_Change_Verification_Research_Report.md` (adjacent vendor-payment workflow research)

---

## 1. Purpose

Matt is collecting external signals (MSP conversations, broker / underwriting anecdotes, industry write-ups, operator observations) about how SMBs and their service providers struggle to produce **underwriting-ready evidence** for cyber-insurance conversations — especially where email-fraud controls, vendor-payment integrity, and security operations overlap.

This map:
- Lists pain points worth probing in discovery and desk research.
- Defines what evidence to log when a source mentions a pain (without turning the log into a product claim).
- States how each theme might relate to NorthStar's existing Stage A evidence surfaces — **as hypotheses only**.
- Draws hard boundaries so this file cannot be mistaken for D10 progress, §13 advancement, or buyer-facing copy.

This map is **not** a spec, scoring rubric, or gate artifact. Findings here do not change build queue order unless Matt explicitly promotes them.

---

## 2. Pain points to investigate

Each row is an investigation theme. Severity, prevalence, and NorthStar fit remain **open** until captured in §4 evidence fields from real sources.

| ID | Pain point | What we are trying to learn |
|---|---|---|
| P01 | **Scattered evidence** | Where do MSPs / SMBs store control evidence today (tickets, spreadsheets, portals, M365 exports, screenshots)? What breaks at renewal time? |
| P02 | **Proving controls operate, not just exist** | What do underwriters ask beyond "we have MFA / EDR / backups"? What operational proof (logs, tests, outcomes) do reviewers accept or reject? |
| P03 | **Partial implementations and awkward exceptions** | How do teams document "we have the control except for these users / sites / legacy apps"? Is the exception narrative trusted or penalized? |
| P04 | **Sharper underwriting questions** | Which questions got harder in 2025–2026 (AI use, BEC, vendor fraud, incident history, third-party risk)? Who is unprepared? |
| P05 | **Technical teams oversharing** | When IT / MSPs submit evidence, what do they include that confuses underwriters (raw configs, jargon, irrelevant scan output)? What gets sent back? |
| P06 | **Cost-to-fix vs cost-to-risk decisions** | How do SMBs / MSPs decide what to remediate before renewal vs accept as residual risk? Who owns that tradeoff? |
| P07 | **Vendor-payment fraud evidence gaps** | What evidence do brokers / insurers want after a payment-detail change, attempted BEC, or loss? What do finance and IT actually have? |
| P08 | **Unclear ownership (MSP / SMB / broker / finance / IT)** | Who is expected to gather, attest, and present each control family? Where do handoffs fail? |
| P09 | **Legacy systems and exception handling** | How are unsupported apps, flat file shares, shared mailboxes, or non-SSO users described without sinking the application? |
| P10 | **Reviewer-ready wording** | What tone, structure, and vocabulary make evidence easy for a non-technical reviewer vs trigger follow-up loops? |
| P11 | **Evidence freshness** | How stale can logs / policies / test results be? What triggers a "please refresh" request mid-renewal? |
| P12 | **Broker / insurer / MSP expectation mismatch** | Where do three parties disagree on what "good enough" looks like for the same control? |
| P13 | **Raw technical evidence confusion** | How are vulnerability scans, pen-test PDFs, screenshots, and SIEM exports interpreted (or misinterpreted) in underwriting packets? |
| P14 | **Incident or claim documentation stress** | After an event, what timeline / decision / communication records do insurers request? What is painful to reconstruct? |
| P15 | **Repeatable MSP evidence packaging** | Do MSPs want a per-client template, a quarterly bundle, or ad-hoc fire drills? What would they pay operational time to standardize? |

**Cross-cutting probes (use on any row):**
- Who felt the pain (MSP tech, MSP owner, SMB owner, finance, broker, underwriter)?
- When did it surface (new business, renewal, claim, audit, board question)?
- What artifact did they wish they had had ready?
- What did they submit instead, and what happened?

---

## 3. Source types to collect

Prioritize sources that can be cited in §4 without client-identifying data unless Matt explicitly authorizes named references.

| Source type | Examples | Strength | Weakness |
|---|---|---|---|
| **Operator MSP discovery** | Conversations logged per `Cyber_Insurance_Evidence_Package_Cheaper_Proof_Runbook.md` + worksheet CSV | Highest for buyer language and workflow truth | Not generalizable until pattern count grows; D10 bar is separate |
| **Broker / underwriting anecdotes** | Matt's network, conference conversations, LinkedIn threads (sanitized) | Surfaces reviewer-ready wording and question shifts | Often second-hand; confirm with primary where possible |
| **SMB / finance operator stories** | Reddit / forums / case studies (sanitized), Matt observations | Grounds cost-to-fix vs cost-to-risk | Selection bias; verify claims |
| **Industry / government guidance** | CISA, FBI IC3, insurer application checklists (public), trade press | Good for "what reviewers ask" framing | Rarely MSP-operational detail |
| **Competitive / adjacent product marketing** | Email-security vendors' "insurance" pages | Shows market vocabulary to **avoid** copying | Heavy decoration risk; not evidence of NorthStar fit |
| **Internal NorthStar artifacts (read-only)** | Signed specs, sample reports, MSP discovery package, FSL / Vendor Baseline docs | Shows what we *could* illustrate — not what buyers validated | Must not be cited as market proof |

**Collection hygiene:**
- Tag each capture with `source_type`, `date_observed`, and `confidence` (`anecdote` / `single-primary` / `multi-source`).
- Separate **observed pain** from **inferred NorthStar relevance** (§5 is only for hypotheses).
- Do not paste raw client emails, tenant IDs, or production paths into this file.

---

## 4. Evidence fields to capture

When Matt (or a future session) logs an external input, use a consistent mini-record — in this file's appendix, a worksheet, or `Frontier_Intake_Log.md` as appropriate.

| Field | Description |
|---|---|
| `capture_id` | Short unique id (e.g. `cybins-pain-20260601-001`) |
| `date_observed` | ISO date |
| `pain_ids` | One or more P01–P15 |
| `source_type` | From §3 table |
| `speaker_role` | MSP tech / MSP owner / SMB owner / finance / broker / underwriter / other |
| `trigger_event` | renewal / new policy / claim / incident / sales cycle / other |
| `verbatim_quote` | Optional; sanitize; no client names unless authorized |
| `paraphrase` | Neutral summary of the pain |
| `artifacts_mentioned` | What they had, wished they had, or were asked for |
| `failure_mode` | What went wrong (delay, declination, rework, confusion, cost) |
| `ownership_gap` | Who they expected to own vs who actually did |
| `vocabulary_risk` | Any forbidden or risky phrases heard (`compliant`, `certified`, `premium`, etc.) |
| `northstar_hypothesis` | Optional link to §5 — **hypothesis only** |
| `follow_up` | Next question to ask |

---

## 5. NorthStar relevance (hypotheses only)

NorthStar's Stage A posture is **decision-support + audit-grade evidence for email-fraud / inbox-layer controls**, not full-stack cyber-insurance attestation. The table below maps pain themes to **existing or contemplated surfaces** — for research prioritization, not product promises.

| Pain IDs | Hypothesis — why this might matter to NorthStar | Existing anchor (if any) |
|---|---|---|
| P01, P15 | MSPs may value a repeatable **evidence bundle** per client rather than one-off exports | `Cyber_Insurance_Evidence_Package_Deep_Dive.md` §4 source map; MSP discovery evidence package |
| P02, P11 | Underwriters may care about **operational traces** (review outcomes, timestamps) not checkbox policies | Blackboard audit trail; reaction-timing log discipline |
| P07, P03 | Vendor-payment change stories align with **documented review workflow** evidence | FSL / Vendor Baseline Store specs; vendor-payment verification research input |
| P05, P13, P10 | NorthStar's explainability / rubric direction may reduce oversharing **if** MSPs adopt structured summaries | Client-Facing 5-Axis Rubric (signed); daily digest / monthly report samples |
| P08 | Role confusion may mean MSP-facing packaging must state **scope boundaries** loudly | `Compliance_and_Trend_Watch_Process.md`; cyber-insurance spec scope table |
| P04, P12 | Sharper questions may favor **carrier-agnostic** evidence sections with plain-English glossaries | Cyber-insurance spec D4 (carrier-agnostic) — do not expand scope here |
| P06, P09, P14 | May be **mostly out of scope** for Stage A email wedge — log for wedge discipline, not immediate build | `VISION.md` Stage A boundary; spec out-of-scope list |

**Explicit non-claims:** Nothing in §5 asserts MSP demand, underwriting acceptance, revenue, or that NorthStar closes any pain without future operator decisions and spec gates.

---

## 6. Boundaries / non-authorizations

This research map does **not**:

- Edit or reinterpret `Cyber_Insurance_Evidence_Package_Deep_Dive.md` or any other §11- / §13-signed spec.
- Change D10 criteria, worksheet definitions, or cheaper-proof runbook thresholds.
- Count as MSP discovery progress, a D10 "yes," or §13 sign-off readiness.
- Authorize runtime code, report generation, pricing, or client-facing copy.
- Use forbidden claim language: `compliant`, `certified`, `insurer-approved`, `premium reducer`, `guarantee`, or equivalents (see `Compliance_and_Trend_Watch_Process.md` §5).

Matt decides promotion paths. Typical promotion chain (for reference only): research captures → operator synthesis → `think_sheet.md` / Frontier Intake if warranted → spec amendment or new deep-dive → explicit build authorization.

---

## 7. Open questions for deeper research

1. **Underwriter persona:** Which roles actually read MSP-submitted packets (underwriter, broker technician, third-party auditor)? What format do they prefer?
2. **Minimum viable bundle:** For email-fraud / BEC / vendor-payment controls only, what is the smallest artifact set that stops a follow-up loop — per region / carrier tier?
3. **Freshness windows:** Median acceptable age for training records, phishing simulations, MFA reports, and payment-change logs at renewal.
4. **Exception narrative:** Do underwriters want a separate "known exceptions" appendix or inline flags per control?
5. **Finance vs IT evidence:** For vendor-payment integrity, whose signature / approval trail counts as control evidence?
6. **Post-incident packet:** What is the 72-hour / 30-day evidence ask after a BEC attempt vs a paid fraud loss?
7. **MSP packaging economics:** Would MSPs standardize quarterly evidence packaging per seat, per client, or only for insurance-heavy verticals?
8. **Oversharing catalog:** Top ten artifacts MSPs submit that underwriters ignore or penalize — build a "do not lead with" list.
9. **Broker translation layer:** Do brokers rewrite MSP technical evidence, and what gets lost in translation?
10. **NorthStar wedge test:** Among P01–P15, which pains are **email / inbox-layer addressable** vs require partners (EDR, backup, IR) — to protect Stage A scope?

---

**End of research map. Append captures below or link from `Frontier_Intake_Log.md` / operator worksheets; do not treat empty appendices as negative evidence.**
