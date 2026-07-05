# Research Verification — Canadian Localization Pass 2026-07

**Task:** `mmi-research-ca-localization-pass`  
**Lane:** ChatGPT — Deep / secondary research  
**Authority:** `MMI_RESEARCH_RIGOR_PROTOCOL.md` §0 (Canada-first Truth Database)  
**Inputs:** `RESEARCH_VERIFICATION_2026-06.md` §7–§8  
**Sign-off:** **PASS WITH REVISIONS**

---

## 1. Executive summary

Canadian primary sources **support the ransomware and cyber-incident risk theme** for operator-facing material, but they **do not** support converting most global/vendor percentages (Verizon SMB 88%, Veeam 96%, Sophos 94%, CrowdStrike breakout minutes, Microsoft >99% MFA) into **Canadian facts**.

Use StatCan and CCCS for Canadian prevalence and threat framing; label CIRA as **survey result** (not national rate); keep Verizon/IBM/CrowdStrike/Veeam/Sophos/Microsoft claims as `[Global Data — Requires Localization]` with `CA cross-reference: Confirms theme | Insufficient Data for exact %`.

---

## 2. Methodology

1. Search Canadian primary sources first: StatCan, CCCS, OPC, CIRA, ISED/Get Cyber Safe  
2. For each claim in `RESEARCH_VERIFICATION_2026-06.md` §7, record: Canadian source (if any), CA cross-ref (`Confirms` | `Diverges` | `Insufficient Data`)  
3. §8 purged stats: do not resurrect; CA cross-ref only if Canadian primary exists  
4. Confidence scoring per rigor protocol §2; no page = manual review flag  

---

## 3. Localization table — §7 claims

| ID | Original claim | Original jurisdiction | Canadian source | CA cross-ref | Confidence (1-10) | Page/Section | Manual review? |
|----|----------------|----------------------|-----------------|--------------|-------------------|--------------|----------------|
| V1 | Ransomware in 88% of SMB breach cases (Verizon 2025 DBIR SMB dataset) | Global Data — Requires Localization | StatCan 2023: 13% of **impacted** businesses reported ransomware as attack method; 16% of businesses impacted by cyber incidents | **Confirms theme, Diverges on magnitude** — Canadian rate is not 88% | 8 | StatCan Daily 2024-10-21; table 22-10-0078-01 | Yes — Verizon SMB ≠ StatCan denominator |
| V2 | Third-party involvement ~30% globally (Verizon 2025 DBIR) | Global Data — Requires Localization | No Canadian primary equivalent found | **Insufficient Data** | 5 | Verizon global; no StatCan/CCCS match | Yes |
| V3 | MFA reduces account-compromise risk >99% (Microsoft) | Global Data — Requires Localization | No Canadian primary percentage found; ISED/Get Cyber Safe recommends MFA qualitatively | **Confirms theme (MFA recommended), Insufficient Data for >99% in Canada** | 7 | Microsoft blog 2019; no CA % | Yes |
| V4 | Rapid eCrime breakout (48 min avg 2025; 29 min 2026 CrowdStrike framing) | Global Data — Requires Localization | CCCS NCTA 2025–2026: evolving cybercrime/AI capability; no Canadian timing metric | **Confirms evolving threat, Insufficient Data for minutes** | 6 | CrowdStrike GTR; CCCS NCTA PDF | Yes |
| V5 | Backup repositories targeted (Veeam 96% / Sophos 94%) | Global Data — Requires Localization | CCCS ransomware guidance; MITRE T1490 — no Canadian % for backup targeting | **Confirms theme (recovery inhibition), Insufficient Data for exact %** | 7 | Veeam/Sophos global; CCCS + MITRE T1490 | Yes |
| V6 | MITRE ATT&CK technique IDs (T1486, T1490, T1566, T1078, etc.) | Global Framework — technique ID only | MITRE ATT&CK live matrix | **N/A — technique IDs not jurisdiction-specific** | 9 | attack.mitre.org | No |

---

## 4. §8 items — CA cross-reference only

| Claim | CA cross-ref | Action |
|-------|--------------|--------|
| 4× SMB targeting | Insufficient Data | PURGE exact number |
| BEC ~33% | Insufficient Data | NEEDS VERIFY / internal only |
| $2.66M IR savings | Insufficient Data | NEEDS VERIFY exact $ |
| 40% MSSP budget | Insufficient Data | PURGE / internal only |
| 60% SMB closure (6 mo) | N/A — zombie (NCSA disavowed) | **PURGE** |
| Manufacturing 72–84h downtime | Insufficient Data | NEEDS VERIFY |
| $53k/hour SMB downtime | Insufficient Data | **PURGE** |

---

## 5. Safe for intel briefs (Canadian or properly labeled)

**Canadian-supported (use with citation):**

- StatCan 2023: **16%** of Canadian businesses impacted by cybersecurity incidents; **13%** of impacted businesses reported **ransomware** as the attack method; recovery spending **CAD $1.2B** (doubled vs prior cycle).  
  Source: [Statistics Canada — Impact of cybercrime on Canadian businesses, 2023](https://www150.statcan.gc.ca/n1/daily-quotidien/241021/dq241021a-eng.htm)

- CCCS: ransomware among most disruptive cybercrime threats; **top cybercrime threat facing Canada's critical infrastructure**.  
  Source: [CCCS National Cyber Threat Assessment 2025–2026 (PDF)](https://www.cyber.gc.ca/sites/default/files/ncta-2025-2026-e.pdf)

- CIRA 2025 Cybersecurity Survey: **24% of surveyed Canadian organizations** reported a ransomware attack in the last 12 months — label as **CIRA survey result**, not national incident rate.  
  Source: [2025 CIRA Cybersecurity Survey](https://www.cira.ca/en/resources/documents/cybersecurity/2025-cybersecurity-survey/)

- MITRE ATT&CK technique IDs (e.g. T1486, T1490, T1566, T1078): **Global Framework — technique ID only**.  
  Source: [MITRE ATT&CK](https://attack.mitre.org/)

**Global — briefs OK only with localization tag:**

- Verizon 88% SMB ransomware-in-dataset framing — `[Global Data — Requires Localization]` + StatCan cross-ref above  
- Backup targeting theme — `[Global Data — Requires Localization]` + T1490 + CCCS ransomware guidance  

---

## 6. Internal only / NEEDS VERIFY

- Verizon **88%** SMB dataset statistic as Canadian prevalence  
- Verizon **30%** third-party involvement as SMB-specific Canadian rate  
- Microsoft **>99%** MFA as Canadian primary statistic  
- CrowdStrike **48/29 minute** breakout as Canadian operator timing  
- Veeam **96%** / Sophos **94%** backup-targeting as Canadian rates  

---

## 7. Purged (unchanged — do not resurrect)

60% SMB closure · 4× SMB targeting · BEC ~33% · $2.66M IR savings · 40% MSSP budget · manufacturing 72–84h · $53k/hour downtime

---

## 8. Product impact for MMI

- **INTEL briefs:** Prefer StatCan + CCCS + CIRA (labeled) for Canadian ransomware/incident framing  
- **Existing brief** `INTEL_ransomware-backup-targeting_2026-06.md`: global percentages remain valid only with `[Global Data — Requires Localization]`; add StatCan/CCCS citations where headline Canadian context is needed  
- **OPSEC checklist:** qualitative MFA/backup framing unchanged; no new unsourced %  

---

## 9. Open gaps

- OPC breach-reporting stats for ransomware-specific Canadian rates (if needed for PIPEDA context)  
- Primary PDF page numbers for StatCan table 22-10-0078-01 granular cells  
- IBM $2.66M — still NEEDS VERIFY if ever cited  
- SEG 120–180s — still NEEDS VERIFY (File B)  

---

## 10. Source links

- [Statistics Canada — Impact of cybercrime on Canadian businesses, 2023](https://www150.statcan.gc.ca/n1/daily-quotidien/241021/dq241021a-eng.htm)
- [CCCS National Cyber Threat Assessment 2025–2026 (PDF)](https://www.cyber.gc.ca/sites/default/files/ncta-2025-2026-e.pdf)
- [CIRA 2025 Cybersecurity Survey](https://www.cira.ca/en/resources/documents/cybersecurity/2025-cybersecurity-survey/)
- [MITRE ATT&CK — T1490 Inhibit System Recovery](https://attack.mitre.org/techniques/T1490/)
- [Microsoft MFA 99.9% blog (global)](https://www.microsoft.com/en-us/security/blog/2019/08/20/one-simple-action-you-can-take-to-prevent-99-9-percent-of-account-attacks/)
- [CrowdStrike Global Threat Report (global)](https://www.crowdstrike.com/en-us/global-threat-report/)
- Prior verification: `lanes/RESEARCH_VERIFICATION_2026-06.md`

---

## Sign-off

**PASS WITH REVISIONS** — Canadian localization pass complete. Intel briefs may use Canadian primary sources listed in §5; global vendor percentages remain internal or must carry localization tags. Not safe to present Verizon/Veeam/Sophos/CrowdStrike/Microsoft percentages as Canadian national rates.
