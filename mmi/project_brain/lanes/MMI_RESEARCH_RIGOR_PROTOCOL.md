# MMI Research Rigor Protocol

Date: 2026-06-29  
Authority: Matt (Super)  
Status: **LOCKED** — mandatory for all Security Intel research, verification, and audit prompts  
Applies to: Gemini (research), ChatGPT (verification), Gemini Paid API (Evaluator)

---

## Purpose

Stop hallucinated statistics, zombie stats, and vendor-aggregator fiction from entering MMI project brain. Every numeric or external claim must survive **Primary Source Requirement**, **Confidence Scoring**, and **Crucible Protocol** before it appears in operator briefs or architecture docs.

Failures are **Crucible log entries** — document limitations, do not invent middle-ground numbers.

---

## 1. Primary Source Requirement

**Never ask:** "What is the stat for X?"

**Always ask:**

> Access the source PDF for **[Report Name]**, navigate to **[Section/Page]**, and extract the specific claim regarding **[Topic]**. If the exact stat is not explicitly in the text, report **`Insufficient Data`** — do not estimate.

### Accepted primary sources (prefer in order)

1. Named annual reports with downloadable PDF (Verizon DBIR, IBM Cost of a Data Breach, CrowdStrike GTR, Microsoft Digital Defense Report, Veeam, Sophos, CISA, MITRE ATT&CK)
2. Official vendor primary PDFs linked from vendor domain
3. MITRE ATT&CK technique pages for technique IDs only

### Weak sources (flag for manual review — do not treat as primary)

- LinkedIn infographics, blog aggregators, VikingCloud-style stat lists
- "Industry says" without PDF page
- Secondary articles citing another article

### Required output per stat

| Field | Required |
|-------|----------|
| Report name + year | Yes |
| Section or page | Yes — or `Insufficient Data` |
| Exact quoted claim | Yes — or paraphrase marked `INFERRED` |
| SMB-specific vs global | Yes — never convert without source |

---

## 2. Confidence Scoring

For any quick answer or interim research note, force this block on **every claim**:

```markdown
| Claim | Confidence (1-10) | Source link | Page/Section | Manual review? |
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

Topic: [TOPIC]

Primary Source Requirement: For every statistic, access the named report PDF (or official MITRE page for ATT&CK IDs). Extract the exact claim from [Section/Page]. If not explicit, report Insufficient Data — do not estimate.

Confidence Scoring: Include Confidence (1-10), source link, and page/section for every claim. No page = flagged for manual review.

Crucible Protocol: You are forbidden from inventing or aggregating middle-ground numbers. If in doubt, state data limitations.

Output: mmi/project_brain/lanes/RESEARCH_[slug]_[yyyy-mm].md

Hard stops: no endpoint swarm, no live telemetry, no scope expansion.
```

### B. ChatGPT — second opinion / verification

```markdown
PROJECT: MMI Security Intel — VERIFICATION (Second Opinion)

Read: mmi/project_brain/lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md
Read: [RESEARCH_FILE paths]

Independently adjudicate every claim. Challenge first-pass verdicts. Require primary PDF/page for VERIFIED status.

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

Task: PDF/page-check outstanding gaps (IBM $2.66M, Verizon 88% SMB framing, BEC %, MSSP budget %, manufacturing downtime, $53k/hour, SEG 120-180s).

For each gap: VERIFIED (with page) | Insufficient Data | PURGE

Output: lanes/RESEARCH_EVALUATOR_PASS_2026-06.md
Verdict: PASS | FAIL | NEEDS_MATT
Findings: bulleted required_fixes if FAIL

Author cannot grade own work — Evaluator is independent audit lane.
```

### D. PM — quick stat check (non-Crucible)

```markdown
Quick check only — still require Confidence (1-10) + Source Link per claim.
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

---

## Authority

Matt (Super) may relax rigor for exploratory brainstorming only when explicitly labeled `BRAINSTORM — NOT FOR BRIEFS`. Default for all Security Intel pipeline tasks is **Crucible-grade**.
