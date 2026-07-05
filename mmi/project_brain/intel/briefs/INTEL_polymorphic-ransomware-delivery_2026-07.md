# Intel Brief — Polymorphic Ransomware Delivery via Adversarial Email Fraud

Date filed: 2026-07-01
Authority: Matt (Super) — Canadian operator
Status: **Internal MMI Security Intel note — advisory only.** Not for external publication.
Lane: Security Intel
File: `intel/briefs/INTEL_polymorphic-ransomware-delivery_2026-07.md`

```yaml
brief_id: INTEL-polymorphic-ransomware-delivery-2026-07
threat_name: Polymorphic Ransomware Delivery via Adversarial Email Fraud
date_filed: 2026-07-01
author: Claude (Design)
source_lanes:
  - lanes/RESEARCH_polymorphic_ransomware_delivery_2026-06.md
  - lanes/RESEARCH_VERIFICATION_2026-06.md
  - lanes/RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md
jurisdiction_scope: Canada-first
overall_source_status: MIXED
overall_confidence: 7
control_plane_status: ADVISORY_ONLY
automation_status: NONE
review_mode: HUMAN_REVIEW_ONLY
```

This brief links observed adversarial techniques to OPSEC mitigation references so the operator can **manually review** the relevant hardening checklist during incident review, drill planning, or PIR. MMI can surface linked OPSEC checks for human review. MMI does **not** automatically know which controls to audit or trigger mitigation workflows.

---

## 1. Threat summary

Adversaries are evolving email-borne ransomware delivery to bypass standard secure email gateway (SEG) and EDR controls through dynamic infrastructure rotation, runtime obfuscation, and context-aware delivery — serving a benign page to automated sandboxes and a weaponized payload only to a human click. The chain observed in research: spearphishing link → client/sandbox profiling → HTML smuggling (browser-side payload assembly) → HTTPS command-and-control → ransomware execution.

For a solo Canadian operator running a local-first stack (Mini PC, no SEG/EDR, no SOC), the relevant exposure is not the enterprise lateral-movement tail of this chain — it is the **delivery and execution stages**, where the only real control is human phish discipline, and the **impact stage**, where an isolated, verified backup is the actual recovery path.

---

## 2. Why this matters for local-first MMI

| MMI asset | Risk if delivery succeeds |
|-----------|---------------------------|
| Operator inbox / browser | Entry point — no SEG sandbox, no EDR; human judgment is the only pre-execution control |
| `mmi/project_brain/` | Irreplaceable operator context if local host is encrypted |
| `tasks.json` | Active queue and completion history |
| B2 cold archives | Last off-host recovery path if local tree is encrypted |

MMI v1 has no EDR, no SOAR, and no auto-containment. There is no MMI-level technical control between a clicked link and a running payload — phish discipline (OPSEC-4/5) and verified backup/restore (OPSEC-6/7/8) are the only two control points that actually exist for a solo operator.

---

## 3. MITRE ATT&CK mapping

Technique IDs verified against primary MITRE ATT&CK pages on **2026-06-30** (per `RESEARCH_VERIFICATION_2026-06.md` §4 audit and `RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md` §3 V6 — Global Framework, technique ID only). Technique mapping documents adversary behavior labels — **not** implemented protection. Scope limited to the delivery→impact chain relevant to a solo/SMB operator; AD-specific lateral-movement techniques (e.g. Kerberoasting, T1558.003) from the source research are out of scope for this brief and not included below.

```yaml
mitre_techniques:
  - id: T1566.002
    name: Spearphishing Link
    source: MITRE ATT&CK
    url: https://attack.mitre.org/techniques/T1566/002/
  - id: T1204.001
    name: User Execution: Malicious Link
    source: MITRE ATT&CK
    url: https://attack.mitre.org/techniques/T1204/001/
  - id: T1027
    name: Obfuscated Files or Information
    source: MITRE ATT&CK
    url: https://attack.mitre.org/techniques/T1027/
  - id: T1027.006
    name: HTML Smuggling
    source: MITRE ATT&CK
    url: https://attack.mitre.org/techniques/T1027/006/
  - id: T1082
    name: System Information Discovery
    source: MITRE ATT&CK
    url: https://attack.mitre.org/techniques/T1082/
  - id: T1071.001
    name: Web Protocols
    source: MITRE ATT&CK
    url: https://attack.mitre.org/techniques/T1071/001/
  - id: T1486
    name: Data Encrypted for Impact
    source: MITRE ATT&CK
    url: https://attack.mitre.org/techniques/T1486/
```

### ATT&CK block — T1566.002

| Field | Value |
|-------|--------|
| `technique_id` | T1566.002 |
| `technique_name` | Spearphishing Link |
| `chain_stage` | delivery |
| `smb_relevance` | Personalized, redirect-laden links are the entry point for a solo operator with no SEG; this is the single highest-leverage point to stop the chain before it starts |
| `operator_signal` | Unexpected link in an email claiming urgency, an invoice, or a credential/account-change prompt; mismatched sender domain or display-name spoofing |
| `mitigation_ref` | `OPSEC-4` |
| `source_status` | VERIFIED |

### ATT&CK block — T1204.001

| Field | Value |
|-------|--------|
| `technique_id` | T1204.001 |
| `technique_name` | User Execution: Malicious Link |
| `chain_stage` | execution |
| `smb_relevance` | Without EDR or browser isolation, the click itself is the execution gate; if the link also carries a payment/credential-change ask, this is also a social-engineering/BEC-style risk |
| `operator_signal` | Browser download prompt or redirect immediately after clicking; any follow-up request to change payment details or credentials received the same channel |
| `mitigation_ref` | `OPSEC-4`, `OPSEC-5` |
| `source_status` | VERIFIED |

### ATT&CK block — T1027 / T1027.006

| Field | Value |
|-------|--------|
| `technique_id` | T1027 (parent), T1027.006 (sub-technique) |
| `technique_name` | Obfuscated Files or Information / HTML Smuggling |
| `chain_stage` | defense evasion |
| `smb_relevance` | HTML smuggling assembles the payload client-side in the browser cache, which defeats proxy/attachment-style file inspection on first click — MMI has no mail-filter or proxy telemetry to detect this technically; the link-hover/sender check (OPSEC-4) is the only control that exists before this stage triggers |
| `operator_signal` | A "benign-looking" landing page that triggers an unexpected file download; no MMI-visible signal exists once this stage executes |
| `mitigation_ref` | `OPSEC-4` — no technical detection control exists at this stage (Insufficient Data; out of scope per hard stops, no EDR/mail-filter telemetry) |
| `source_status` | VERIFIED (T1027.006 confirmed sub-technique per `RESEARCH_VERIFICATION_2026-06.md` §4) |

### ATT&CK block — T1082

| Field | Value |
|-------|--------|
| `technique_id` | T1082 |
| `technique_name` | System Information Discovery |
| `chain_stage` | discovery |
| `smb_relevance` | Client fingerprinting (registry, processes, language packs) ahead of stage-2 lets the payload distinguish a sandbox from a real operator host; this happens after execution and is not human-visible |
| `operator_signal` | None reliably observable by a human operator at this stage |
| `mitigation_ref` | Insufficient Data — no MMI checklist item covers endpoint telemetry or fingerprinting detection; out of scope per hard stops (no EDR/live telemetry) |
| `source_status` | VERIFIED |

### ATT&CK block — T1071.001

| Field | Value |
|-------|--------|
| `technique_id` | T1071.001 |
| `technique_name` | Web Protocols |
| `chain_stage` | command and control |
| `smb_relevance` | C2 over HTTPS, domain fronting, or ephemeral tunnels blends with normal browser traffic; a solo operator has no network telemetry layer to distinguish this from legitimate HTTPS traffic |
| `operator_signal` | None reliably observable by a human operator at this stage |
| `mitigation_ref` | Insufficient Data — no MMI checklist item covers network C2 detection; out of scope per hard stops (no SOAR/live telemetry) |
| `source_status` | VERIFIED |

### ATT&CK block — T1486

| Field | Value |
|-------|--------|
| `technique_id` | T1486 |
| `technique_name` | Data Encrypted for Impact |
| `chain_stage` | impact |
| `smb_relevance` | Once the chain reaches this stage, prevention has already failed; the operator's recovery path (isolated backup, tested restore) is the only remaining control |
| `operator_signal` | Ransom note, mass file-extension change, inaccessible `mmi/` or repo files; see `intel/WAR_ROOM_SCORING_MATRIX_v2.md` §8 P1 host/filesystem |
| `mitigation_ref` | `OPSEC-6`, `OPSEC-7`, `OPSEC-8`, `OPSEC-BACKUP-PATHS`, `OPSEC-9` (decision log at first suspicion) |
| `source_status` | VERIFIED |

---

## 4. Mitigation references (human review only)

```yaml
mitigation_refs:
  - id: OPSEC-4
    title: Link-hover and sender-domain check before clicking any link in an unexpected email
    file: opsec/OPERATOR_OPSEC_CHECKLIST.md
    status: NEEDS_REVIEW
    review_mode: HUMAN_REVIEW_ONLY
  - id: OPSEC-5
    title: Out-of-band confirmation before acting on a payment or credential-change request received by email
    file: opsec/OPERATOR_OPSEC_CHECKLIST.md
    status: NEEDS_REVIEW
    review_mode: HUMAN_REVIEW_ONLY
  - id: OPSEC-6
    title: Cold backup pushed to B2 on schedule
    file: opsec/OPERATOR_OPSEC_CHECKLIST.md
    status: NEEDS_REVIEW
    review_mode: HUMAN_REVIEW_ONLY
  - id: OPSEC-7
    title: Backup integrity check
    file: opsec/OPERATOR_OPSEC_CHECKLIST.md
    status: NEEDS_REVIEW
    review_mode: HUMAN_REVIEW_ONLY
  - id: OPSEC-8
    title: Full restore drill (quarterly)
    file: opsec/OPERATOR_OPSEC_CHECKLIST.md
    status: NEEDS_REVIEW
    review_mode: HUMAN_REVIEW_ONLY
  - id: OPSEC-9
    title: Decision log opened at first moment of suspicion
    file: opsec/OPERATOR_OPSEC_CHECKLIST.md
    status: NEEDS_REVIEW
    review_mode: HUMAN_REVIEW_ONLY
  - id: OPSEC-BACKUP-PATHS
    title: Backup Protected Paths / scope for human review
    file: opsec/BACKUP_PROTECTED_PATHS.md
    status: DRAFT
    review_mode: HUMAN_REVIEW_ONLY
```

**Traceability chain:**

```text
T1566.002 / T1204.001 / T1027.006 → this brief → OPSEC-4 / OPSEC-5 (pre-execution, human only)
T1486 → this brief → OPSEC-6 / OPSEC-7 / OPSEC-8 / OPSEC-BACKUP-PATHS / OPSEC-9 (post-impact recovery)
T1082 / T1071.001 → this brief → Insufficient Data (no MMI technical control exists; out of scope by design)
```

---

## 5. Claims table

| Claim | Jurisdiction | Confidence (1-10) | Source + date | Page/Section | CA cross-reference | Manual review? |
|-------|--------------|--------------------|-----------------|---------------|----------------------|------------------|
| T1566.002, T1204.001, T1027, T1027.006, T1082, T1071.001, and T1486 are current MITRE ATT&CK technique IDs | Global Framework — technique ID only | 9 | MITRE ATT&CK (attack.mitre.org), checked 2026-06-30 | N/A — live matrix lookup | Not applicable to technique-ID claims | No |
| Ransomware ranks among the most disruptive cybercrime threats and is described as the top cybercrime threat facing Canada's critical infrastructure | Canada (primary) | 7 | CCCS National Cyber Threat Assessment 2025–2026 (PDF) | Insufficient Data — exact page/section not extracted | N/A — Canadian primary source | Yes (no page/section) |
| 16% of Canadian businesses were impacted by a cybersecurity incident in 2023; 13% of impacted businesses reported ransomware as the attack method; recovery spending reached CAD $1.2B | Canada (primary) | 8 | Statistics Canada Daily, 2024-10-21, table 22-10-0078-01 | Daily release; granular table page not pulled | N/A — Canadian primary source | Yes (granular table page not pulled) |
| 24% of surveyed Canadian organizations reported a ransomware attack in the last 12 months | Canada (survey) | 6 | 2025 CIRA Cybersecurity Survey | Page not extracted | N/A — label as CIRA survey result, not a national incident rate | Yes |
| Ransomware was present in 88% of SMB breach cases in Verizon's 2025 DBIR SMB Snapshot dataset | Global Data — Requires Localization | 8 | Verizon 2025 DBIR SMB Snapshot | Infographic — no page numbers | Confirms theme, Diverges on magnitude — StatCan 2023 shows 13% of impacted Canadian businesses cite ransomware, a different denominator and methodology; not usable as a Canadian rate | Yes (no page number; internal context only, excluded from headline) |
| SEG sandbox detonation windows of approximately 120–180 seconds | Unsourced (research pack secondary claim) | 3 | Research pack, no primary citation found | None | Insufficient Data | Yes — NEEDS VERIFY, excluded from headline; safe language "within minutes" used instead |
| AI-assisted JIT compilation in delivery scripts (6–12 month outlook) | Forecast | 2 | Research pack forecast section, no primary source | None | Insufficient Data | Yes — `FORECAST_LOW_CONFIDENCE`, RESEARCH-ONLY |
| C2 via signed enterprise workflows (Apps Script, Power Automate, Cloudflare Workers) (6–12 month outlook) | Forecast | 2 | Research pack forecast section, no primary source | None | Insufficient Data | Yes — `FORECAST_LOW_CONFIDENCE`, RESEARCH-ONLY |

---

## 6. Forecast items (RESEARCH-ONLY — `FORECAST_LOW_CONFIDENCE`, not headline)

The following are theoretical 6–12 month projections from the source research pack. They are **not** verified, **not** Canadian-localized, and must never be presented as current fact or operator-facing finding:

- AI-assisted just-in-time (JIT) compilation in delivery scripts.
- Command-and-control routed through signed enterprise workflow platforms (Apps Script, Power Automate, Cloudflare Workers).

Neither item has a primary source. Both stay internal, labeled `FORECAST_LOW_CONFIDENCE` wherever referenced.

A theoretical agentic "endpoint swarm" (ingress evaluator + automated containment) appears in the source research as a defensive concept. It is **explicitly research-only and not authorized for MMI implementation** — MMI v1 has no EDR, no SOAR, and no auto-containment, and this brief makes no recommendation toward building one.

---

## 7. War-room relevance

| Scoring matrix touchpoint | How this brief supports review |
|---------------------------|-------------------------------|
| `WAR_ROOM_SCORING_MATRIX_v2.md` Axis B (decision log) | `OPSEC-9` at first suspicion of a phishing click or unexpected download |
| §8 P1 backup/recovery signals | Operator compares post-impact signals to this brief's T1486 block |
| Tier 3/4 restore path tested | `OPSEC-8` — this brief's impact-stage findings feed the next quarterly drill scenario |

War room panels remain read-only. This brief does not change tier scores automatically.

---

## 8. Limitations (Crucible)

- **What this brief does NOT establish:** Canadian-specific frequency or prevalence rates for polymorphic email delivery techniques specifically; it does not validate the SEG sandbox dwell-time window; it does not establish that any forecast item (AI JIT, signed-workflow C2) is occurring now, only that the source research flagged them as plausible 6–12 month trends.
- **Claims downgraded from the source research and why:** the SEG sandbox "120–180 seconds" window is downgraded to internal-only / NEEDS VERIFY — no primary source was found, per `RESEARCH_VERIFICATION_2026-06.md` §5; the Verizon 88% SMB ransomware-in-dataset figure is kept as a properly labeled global claim only — `RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md` §3 (V1) found it "Confirms theme, Diverges on magnitude" against StatCan's 13%, so it is excluded from this brief's headline and from any Canadian-fact framing.
- **Claims purged outright (zombie stats, unsupported conversions) and why:** per `RESEARCH_VERIFICATION_2026-06.md` §8 and `RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md` §4/§7 — the 4× SMB targeting ratio, the <25-minute AD-compromise claim, BEC ~33% of initial breaches, supply chain 30% presented as SMB-specific, the exact $2.66M IR-savings figure, the 40% MSSP budget share, "60% of SMBs close within six months" (confirmed zombie statistic, NCSA disavowed), manufacturing 72–84h downtime, and $53,000/hour SMB downtime. None of these appear anywhere in this brief.
- **What would resolve each remaining `Insufficient Data` / `NEEDS VERIFY` item:** an exact page/section citation from the CCCS NCTA 2025–2026 PDF for the critical-infrastructure ransomware ranking; the specific cell reference in StatCan table 22-10-0078-01; a primary vendor or CCCS technical source for SEG sandbox dwell-time; a primary source for either forecast item if one emerges before the next research cycle.
- **Canadian-localization status (per global-sourced claim in §5):** CCCS NCTA and StatCan claims are Canadian primary sources — Confirms, no further localization needed. CIRA 24% is a Canadian survey result, correctly labeled as such, not a national incident rate. Verizon 88% SMB ransomware-in-dataset — Confirms theme, Diverges on magnitude (StatCan denominator and methodology differ); excluded from headline. SEG sandbox timing and both forecast items — Insufficient Data, excluded from headline.

---

## 9. Canadian SMB context

- Operator jurisdiction: Canada (British Columbia). Regulatory triage for real incidents stays in `WAR_ROOM_SCORING_MATRIX_v2.md` §7.4/§9 — not in this brief.
- CCCS National Cyber Threat Assessment 2025–2026 frames ransomware as the top cybercrime threat to Canada's critical infrastructure — used here as Canadian primary context for why delivery-chain discipline matters, not as a delivery-technique-specific statistic.
- StatCan 2023 (table 22-10-0078-01) is the only Canadian primary source with a quantified ransomware-prevalence figure (13% of impacted businesses); it does not speak to delivery mechanism specifically and should not be read as validating the 88% SMB figure or any vendor delivery-bypass statistic.
- CIRA 2025 survey (24%) is a self-selected survey sample, not a national incident rate — labeled accordingly throughout this brief.

---

## 10. Hard stops

- Advisory-only; no auto-containment, endpoint swarm, EDR requirement, live telemetry, or SOAR — this brief makes no recommendation toward building any of these, including the theoretical agentic swarm described in §6.
- No external publication language; internal operator note only.
- Surface OPSEC links for **human review** — never imply automatic mitigation dispatch.
- No `NEEDS VERIFY`, `RESEARCH-ONLY`, or `FORECAST_LOW_CONFIDENCE` claim appears in this brief's headline findings or ATT&CK `smb_relevance` text as if settled.

---

## Sign-off

**PASS WITH REVISIONS** — Headline ATT&CK mapping and Canadian primary-source context (CCCS, StatCan, CIRA) are filing-ready. Internal gaps remain open pending: CCCS/StatCan page-level citations, a primary source for SEG sandbox timing, and ongoing monitoring of the two `FORECAST_LOW_CONFIDENCE` forecast items. None of these gaps affect the headline VERIFIED claims used above.
