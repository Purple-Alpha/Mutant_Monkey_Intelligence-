# MMI Research Rigor Protocol

Date: 2026-06-30  
Authority: Matt (Super) — Canadian operator; Truth Database is Canada-first  
Status: **LOCKED** — mandatory for all Security Intel research, verification, and audit prompts  
Applies to: Gemini (research), ChatGPT (verification), Gemini Paid API (Evaluator)

---

## Purpose

Stop hallucinated statistics, zombie stats, and vendor-aggregator fiction from entering MMI project brain. Every numeric or external claim must survive **Primary Source Requirement**, **Confidence Scoring**, and **Crucible Protocol** before it appears in operator briefs or architecture docs.

Failures are **Crucible log entries** — document limitations, do not invent middle-ground numbers.

Matt is **Canadian**. The Truth Database is **Canada-first**. US/global vendor stats are secondary and must be labeled.

---

## 0. Canadian-First Truth Database (mandatory)

Whenever a statistic or framework is needed, search **Canadian primary sources first**. Only use global/US data when Canadian data is insufficient — and never present global data as if it applies to Matt's context without localization.

### Canadian primary sources (search first)

| Source | Use for |
|--------|---------|
| **Statistics Canada** — Survey of Cyber Security and Cybercrime (e.g. 2023 table 22-10-0078-01) | Canadian business cyber incident rates, reporting, impacts |
| **CCCS** — Canadian Centre for Cyber Security (ITSM, National Cyber Threat Assessment, alerts) | Frameworks, national threat trends, guidance |
| **OPC** — Office of the Privacy Commissioner Annual Report | Breach reporting, privacy enforcement context |
| **CIRA** — Canadian Internet Registration Authority reports | Canadian org cyber posture, DNS/phishing context |
| **Cybersecurity Canada Report** (when published) | Canadian sector landscape |
| **ISED / Get Cyber Safe** | SMB-oriented Canadian guidance |

### Contextualizing global data

If a global report is used (Verizon DBIR, IBM, CrowdStrike, Microsoft, etc.), **every such claim** must carry:

```markdown
[Jurisdiction: Global Data — Requires Localization]
```

Then:

1. Search for a **Canadian primary source** on the same topic  
2. State whether Canadian data **confirms**, **diverges from**, or **Insufficient Data** vs the global claim  
3. Do not use global SMB stats as Canadian SMB facts without a Canadian source

### Source citation rule

Prioritize links to the **specific Canadian document** (PDF, table ID, report year) so Matt reviews the same evidence. Example formats:

- `Statistics Canada, Table 22-10-0078-01, 2023`
- `CCCS National Cyber Threat Assessment 2025-2026, p. XX`
- `OPC Annual Report 2024-25, Section X`

---

## 1. Primary Source Requirement

**Never ask:** "What is the stat for X?"

**Always ask:**

> Access the source PDF for **[Report Name]**, navigate to **[Section/Page]**, and extract the specific claim regarding **[Topic]**. If the exact stat is not explicitly in the text, report **`Insufficient Data`** — do not estimate.

### Accepted primary sources (prefer in order)

1. **Canadian primary** — StatCan, CCCS, OPC, CIRA, ISED (see §0)
2. Named annual reports with downloadable PDF (Verizon DBIR, IBM Cost of a Data Breach, CrowdStrike GTR, Microsoft Digital Defense Report, Veeam, Sophos) — **label Global Data — Requires Localization**
3. MITRE ATT&CK technique pages for technique IDs only (global framework; note Canadian sector context separately)
4. CISA / US-only sources — last resort; always label jurisdiction and seek Canadian cross-reference

### Weak sources (flag for manual review — do not treat as primary)

- LinkedIn infographics, blog aggregators, VikingCloud-style stat lists
- "Industry says" without PDF page
- Secondary articles citing another article

### Required output per stat

| Field | Required |
|-------|----------|
| Jurisdiction | `Canadian` \| `Global Data — Requires Localization` \| `Insufficient Data` |
| Report name + year | Yes |
| Section or page | Yes — or `Insufficient Data` |
| Exact quoted claim | Yes — or paraphrase marked `INFERRED` |
| Canadian cross-reference | Required when jurisdiction is Global |
| SMB-specific vs global | Yes — never convert without source |

---

## 2. Confidence Scoring

For any quick answer or interim research note, force this block on **every claim**:

```markdown
| Claim | Jurisdiction | Confidence (1-10) | Source link | Page/Section | CA cross-ref | Manual review? |
```

**Rules:**

- **No page/section link → automatic manual review flag**
- Confidence **≤ 4** → `NEEDS VERIFY` — may not appear in briefs
- Confidence **5-7** → internal use only with source framing
- Confidence **≥ 8** → eligible for intel briefs after Evaluator PASS
- Confidence **10** → only with primary PDF quote + page number

---

## 3. Crucible Protocol

When Matt or PM marks a task **Crucible-grade**, the researcher/auditor is **strictly forbidden** from:

- Inventing a number because "it sounds right"
- Averaging conflicting sources into a middle-ground stat
- Converting global enterprise data into SMB-specific claims
- Converting US/global data into Canadian operator context without localization
- Using zombie stats (e.g. "60% of SMBs close within six months" — NCSA disavowed)

**Required when in doubt:**

> State the limitations of the data. Report `Insufficient Data`. List what PDF or primary source would resolve the gap.

Crucible-grade tasks output to `lanes/` or `status/` with explicit **limitations section**.

---

## 4. Prompt templates (copy-paste)

### A. Gemini — primary research (Crucible-grade)

```markdown
PROJECT: MMI Security Intel — CRUCIBLE-GRADE RESEARCH

Read: mmi/project_brain/lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md

Operator context: Matt is Canadian. Truth Database is CANADA-FIRST.

Topic: [TOPIC]

Canadian-First Hierarchy:
1. Search Canadian primary sources FIRST (StatCan Cyber Security survey, CCCS ITSM/NCTA, OPC Annual Report, CIRA, Cybersecurity Canada Report, ISED).
2. If using global data (DBIR, IBM, CrowdStrike, etc.), label every claim: [Global Data — Requires Localization].
3. Cross-reference global claims against Canadian sources — state Confirms | Diverges | Insufficient Data.
4. Link to the specific Canadian document/table/page so Matt sees the same evidence.

Primary Source Requirement: For every statistic, access the named report PDF (or official MITRE page for ATT&CK IDs). Extract the exact claim from [Section/Page]. If not explicit, report Insufficient Data — do not estimate.

Confidence Scoring: Include Jurisdiction, Confidence (1-10), source link, page/section, and Canadian cross-ref for every claim. No page = flagged for manual review.

Crucible Protocol: Forbidden from inventing or aggregating middle-ground numbers. Forbidden from presenting US/global stats as Canadian facts.

Output: mmi/project_brain/lanes/RESEARCH_[slug]_[yyyy-mm].md

Hard stops: no endpoint swarm, no live telemetry, no scope expansion.
```

### B. ChatGPT — second opinion / verification

```markdown
PROJECT: MMI Security Intel — VERIFICATION (Second Opinion)

Read: mmi/project_brain/lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md
Read: [RESEARCH_FILE paths]

Operator context: Matt is Canadian. Re-verify with CANADA-FIRST lens.

Independently adjudicate every claim. Challenge first-pass verdicts. Require primary PDF/page for VERIFIED status.

For every global/US stat: require [Global Data — Requires Localization] label and Canadian cross-reference (Confirms | Diverges | Insufficient Data).

Reject any claim presented as Canadian fact that relies only on US vendor data without Canadian primary source.

Output: mmi/project_brain/lanes/RESEARCH_VERIFICATION_[yyyy-mm].md
Sign-off: PASS | PASS WITH REVISIONS | FAIL

Crucible-grade: no invented stats; purge zombie stats explicitly.
```

### C. Gemini Paid API — Evaluator pass

```markdown
PROJECT: MMI Security Intel — EVALUATOR PASS (Crucible-grade)

Read: mmi/project_brain/lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md
Read: lanes/RESEARCH_VERIFICATION_2026-06.md
Read: lanes/RESEARCH_*.md

Operator context: Matt is Canadian. Audit for Canada-first compliance.

Task: PDF/page-check outstanding gaps. For each global stat, verify Canadian cross-reference exists or mark Insufficient Data.

For each gap: VERIFIED (with page) | Insufficient Data | PURGE | [Global Data — Requires Localization]

Output: lanes/RESEARCH_EVALUATOR_PASS_2026-06.md
Verdict: PASS | FAIL | NEEDS_MATT
Findings: bulleted required_fixes if FAIL

Author cannot grade own work — Evaluator is independent audit lane.
```

### D. PM — quick stat check (non-Crucible)

```markdown
Quick check only — Canada-first: prefer StatCan/CCCS/OPC/CIRA before global vendors.
Still require Jurisdiction, Confidence (1-10) + Source Link per claim.
Global data must be labeled [Global Data — Requires Localization].
If no link to specific report page, flag for manual review. Do not use in external briefs.
```

---

## 5. Integration with MMI lanes

| Lane | Rigor applies |
|------|----------------|
| Gemini research | Templates A, D |
| ChatGPT verify | Template B |
| Gemini Paid API Evaluator | Template C |
| Claude design | Must reference verification status; no new unverified stats |
| Codex build | No stats in code/docs without VERIFIED or NEEDS VERIFY stamp |

---

## 6. Product impact

- **INTEL_BRIEF_TEMPLATE** may only embed claims with Evaluator PASS or Confidence ≥ 8 + page citation
- **OPERATOR_OPSEC_CHECKLIST** uses verified claims + safe language pack from verification doc
- Zombie stats and unverified percentages are **forbidden** in operator-facing material
- **Global vendor stats** without `[Global Data — Requires Localization]` and Canadian cross-reference are **forbidden** in Canadian operator briefs

---

## 7. Re-verification note (2026-06-30)

Existing `RESEARCH_*.md` and `RESEARCH_VERIFICATION_2026-06.md` were produced before Canada-first protocol. Treat their statistics as **US/global-biased** until a Canadian localization pass is run under this protocol.

---

## Authority

Matt (Super) may relax rigor for exploratory brainstorming only when explicitly labeled `BRAINSTORM — NOT FOR BRIEFS`. Default for all Security Intel pipeline tasks is **Crucible-grade**.
