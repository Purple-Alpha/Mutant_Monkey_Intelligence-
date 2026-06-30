# Research Verification — MMI Security Intel 2026-06 (ChatGPT Second Opinion)

**Status: DRAFT pending Evaluator / Matt**  
**Sign-off: PASS WITH REVISIONS**  
**Lanes:** Gemini (first pass) → ChatGPT (second opinion) → Evaluator / Matt (final)

## 1. Executive Summary

The research pack is usable as an **internal threat-intel baseline only after revisions**. Several claims are well-supported by primary or near-primary sources, especially ransomware prevalence in SMB breaches, backup targeting, MFA effectiveness, third-party breach involvement, and rapid adversary breakout time. Several other statistics are weak, over-specific, or appear to be "zombie stats," especially the "60% of SMBs close within six months" claim. Gemini's first pass was directionally responsible but incomplete: it missed or under-treated claims #8 and #10, softened some claims correctly, but also marked at least one statistic as "verified" without preserving the exact source limitation. The pack should not use unsupported exact numbers in operator-facing or external material. For MMI Security Intel, the safe path is to preserve the verified evidence, tag weak claims as `NEEDS_VERIFY`, and quarantine marketing-style statistics until primary PDFs are reviewed.

## 2. Methodology Note

Claims were evaluated against primary or near-primary sources first: Verizon DBIR, IBM Cost of a Data Breach, Microsoft security research, CrowdStrike Global Threat Report, MITRE ATT&CK, CISA/Canadian Centre for Cyber Security, Sophos, and Veeam. Vendor survey data was accepted only where the claim was clearly framed as "reported by surveyed organizations," not as universal ground truth. Blog posts, aggregator statistics, LinkedIn posts, and uncited industry claims were treated as weak unless they pointed back to a primary report. This review distinguishes **SMB-specific** statistics from **global enterprise** statistics and avoids converting enterprise-wide data into SMB claims. Desk research cannot prove live prevalence inside Matt's environment or the `Architectapp_clean` project; it can only establish whether the research pack's cited claims are defensible enough for internal briefs.

## 3. Claim-by-Claim Adjudication Table

| Claim ID | Original claim | Gemini verdict | ChatGPT verdict | Confidence | Primary source(s) | Replacement / safe wording | Action |
| -------- | ---------------- | -------------- | --------------- | ---------- | ------------------- | -------------------------- | ------ |
| A1 | SMBs targeted ~4× more frequently than large enterprises | NEEDS VERIFY | Not verified as written | Low | Verizon 2025 DBIR SMB Snapshot | "SMBs remain a high-volume and high-impact target, especially where security maturity, backup resilience, and incident-response capacity are limited." | REMOVE exact number / SOFTEN |
| A2 | Initial access to AD compromise + exfil in <25 minutes | NEEDS VERIFY | Too specific | Medium | CrowdStrike 2025/2026 Global Threat Report | "Advanced eCrime actors can move from initial access to lateral movement in under an hour, with fastest observed cases measured in seconds." | SOFTEN |
| A3 | Ransomware = 88% of successful SMB data breaches | REPLACE / WEAK | Verified with precise wording (SMB dataset framing) | High | Verizon 2025 DBIR SMB Snapshot | "In Verizon's 2025 DBIR SMB analysis, ransomware was present in 88% of SMB breach cases in that dataset." | KEEP with exact source framing |
| A4 | BEC = ~33% of initial breaches | NEEDS VERIFY | Not verified as written | Low | Verizon DBIR / FBI IC3 (BEC material) | "BEC remains a major social-engineering and financial-fraud threat; do not claim one-third initial-breach share without primary source." | NEEDS VERIFY / SOFTEN |
| A5 | Supply chain = 30% of SMB breaches | NEEDS VERIFY | Partially verified globally, not SMB-specific | Medium | Verizon 2025 DBIR (~30% third-party involvement globally) | "Third-party involvement reached roughly 30% of breaches in Verizon's 2025 DBIR dataset; SMB-specific rates require separate verification." | SOFTEN |
| A6 | Hardware-enforced MFA blocks ~90% of credential stuffing/spray | VERIFIED | MFA strongly supported; hardware-specific wording needs care | High | Microsoft Digital Defense / MFA research | "MFA materially reduces account-compromise risk; use phishing-resistant MFA where possible." | KEEP with corrected wording |
| A7 | Tested IR plans save ~$2.66M vs ad-hoc response | VERIFIED | Correct source family; exact number needs PDF/page check | Medium | IBM Cost of a Data Breach 2025 | "Preparation and tested IR reduce breach impact; verify exact dollar deltas against IBM PDF." | NEEDS VERIFY for exact number |
| A8 | MDR/vCISO: detection/containment weeks → hours | Gemini skipped | Plausible, remain qualitative | Medium-Low | IBM 2025 breach lifecycle; vendor MDR claims | "MDR can reduce detection/response latency where telemetry and escalation are well configured." | SOFTEN |
| A9 | 96% of ransomware attempts target backup destruction first | VERIFIED | Mostly verified; prefer "backup repositories targeted" | High | Veeam 2024; Sophos 2024 | "Veeam reported 96% backup-repository targeting; Sophos reported 94% attempted backup compromise." | KEEP with corrected wording |
| A10 | ~40% of SMB security budget to outsourced SOC/MSSP | Gemini skipped | Not verified | Low | MSSP Alert / ESET 2022 (outsourcing adoption, not budget %) | "Many SMBs rely on MSPs/MSSPs; do not claim 40% budget allocation without primary benchmark." | REMOVE / NEEDS VERIFY |
| A11 | 60% of SMBs out of business within 6 months | REPLACE / WEAK | Remove — zombie statistic | High | NCSA correction (Stay Safe Online) | "Avoid unsupported closure-rate claims." | REMOVE |
| A12 | Manufacturing: 72–84h recovery downtime | NEEDS VERIFY | Not verified as general stat | Low | Sophos manufacturing reporting | "Manufacturing incidents can create multi-day operational disruption." | NEEDS VERIFY / SOFTEN |
| A13 | $53,000/hour average SMB downtime cost | NEEDS VERIFY | Not primary-source verified | Low | Aggregator sources only | "Use scenario-based exposure ranges, not a universal hourly cost." | REMOVE / NEEDS VERIFY |

## 4. MITRE ATT&CK Audit

| ATT&CK ID | Name | Audit verdict | Notes |
| --------- | ---- | ------------- | ----- |
| T1566.002 | Spearphishing Link | Verified | Correct for malicious email links |
| T1204.001 | User Execution: Malicious Link | Verified | Correct follow-on user action |
| T1027 | Obfuscated Files or Information | Verified | Correct for encoded/obfuscated payloads |
| T1027.006 | HTML Smuggling | Verified | Confirmed sub-technique |
| T1082 | System Information Discovery | Verified | Correct post-execution discovery |
| T1071.001 | Web Protocols | Verified | Correct for HTTPS/web C2 |
| T1486 | Data Encrypted for Impact | Verified | Correct for ransomware impact |
| T1558.003 | Kerberoasting | Verified, context-limited | AD/Kerberos environments only — not solo operators |

## 5. Technical Claims Review — File B

| Claim | Verdict |
| ----- | ------- |
| HTML smuggling (T1027.006) | Verified — safe as technique label |
| Ephemeral domains | Plausible — no quantitative claim without source |
| SEG sandbox 120–180 seconds | NEEDS VERIFY — use "within minutes" unless primary source found |
| AI JIT / polymorphic phishing | FORECAST / LOW CONFIDENCE |
| C2 via signed enterprise workflows | FORECAST / LOW CONFIDENCE |
| 6–12 month predictions | Opinion only — exclude from factual operator briefs |

## 6. Gemini Critique

Gemini was right to reject or soften most weak stats and the 60% zombie claim. Gemini was **too conservative** on the 88% ransomware figure — supported by Verizon 2025 DBIR SMB material with exact dataset framing. Gemini's MFA "99.9%" upgrade is directionally right for MFA broadly but should not be attributed to hardware-enforced MFA without source precision. Gemini **missed claims A8 and A10**. Kerberoasting needs SMB/AD context warning.

## 7. Verified Claims — Final

- Verizon 2025 DBIR SMB material: ransomware present in 88% of SMB breach cases **in that dataset**
- Verizon 2025 DBIR: third-party involvement ~30% globally (not SMB-specific without further source)
- Microsoft-backed research: MFA reduces account-compromise risk above 99% in large commercial datasets
- CrowdStrike: rapid eCrime breakout (48 min avg 2025; 29 min avg 2026 reporting)
- Veeam/Sophos: backup repositories routinely targeted in ransomware incidents
- MITRE: all listed ATT&CK IDs confirmed, including T1027.006

## 8. Do Not Use Externally

- 4× SMB targeting ratio
- <25 min AD compromise + exfil as general claim
- BEC ~33% initial breaches
- Supply chain 30% as SMB-specific without source
- Exact $2.66M IR savings until IBM PDF page-check
- 40% SMB budget to MSSP
- 60% close within six months (zombie — NCSA disavowed)
- Manufacturing 72–84h without primary source
- $53,000/hour SMB downtime

## 9. Suggested Safe Language Pack

* Replace **"SMBs targeted ~4× more frequently than large enterprises"** with: "SMBs remain a high-volume target because they often combine valuable payment, identity, and customer data with constrained security capacity."
* Replace **"Initial access to AD compromise + exfil in <25 minutes"** with: "Modern eCrime actors can move from initial access to lateral movement in under an hour in observed cases."
* Replace **"Ransomware = 88% of successful SMB data breaches"** with: "In Verizon's 2025 DBIR SMB dataset, ransomware was present in 88% of SMB breach cases."
* Replace **"BEC = ~33% of initial breaches"** with: "BEC remains a major financial-fraud and social-engineering risk, but this pack does not currently verify a one-third initial-breach share."
* Replace **"Supply chain = 30% of SMB breaches"** with: "Verizon's 2025 DBIR reported third-party involvement in roughly 30% of breaches globally; SMB-specific exposure requires separate validation."
* Replace **"Hardware-enforced MFA blocks ~90%"** with: "MFA materially reduces account-compromise risk; phishing-resistant MFA should be preferred for high-risk roles."
* Replace **"Tested IR plans save $2.66M"** with: "Tested incident-response capability is associated with lower breach impact and faster recovery; exact dollar deltas require IBM PDF confirmation."
* Replace **"MDR/vCISO: weeks → hours"** with: "Managed detection and response can reduce detection and response latency where telemetry, escalation, and response authority are well configured."
* Replace **"96% target backup destruction first"** with: "Backup repositories are frequently targeted during ransomware incidents; Veeam reported 96% targeting and Sophos reported 94% attempted compromise."
* Replace **"40% SMB security budget to outsourced SOC/MSSP"** with: "Many SMBs rely on MSP/MSSP support because they lack in-house security skills and 24/7 response capacity."
* Replace **"60% close within six months"** with: "Cyber incidents can create severe continuity pressure for SMBs; avoid unsupported closure-rate claims."
* Replace **"Manufacturing 72–84h downtime"** with: "Manufacturing incidents can create multi-day operational disruption due to coupled IT, OT, scheduling, identity, and supplier dependencies."
* Replace **"$53,000/hour SMB downtime"** with: "Downtime cost should be estimated per business using revenue dependency, payroll exposure, production halt, customer impact, and recovery labor."

## 10. Product Impact for MMI

**Keep:** ransomware-dominant SMB pattern (with DBIR framing), backup targeting, MFA reduction, third-party risk trend, rapid breakout, MITRE mapping.

**Tag NEEDS_VERIFY:** BEC %, exact IR $, MDR timing, MSSP budget %, manufacturing hours, hourly downtime.

**Purge:** 60% closure stat, 4× targeting, global→SMB stat conversions without source.

## 11. Hard Boundaries Reaffirmation

No endpoint swarm, live telemetry, automated containment, cloud runtime, or external publication of unverified stats. Local-first; cold B2 backup only.

## 12. Outstanding Gaps

- Evaluator/Matt: IBM 2025 PDF page-check for $2.66M
- Evaluator: Verizon 2025 SMB Snapshot PDF page numbers for 88%
- Primary source for BEC 33% if it exists
- Primary source for 40% MSSP budget share if it exists
- Sophos manufacturing PDF for 72–84h claim
- Purge or source $53k/hour
- SEG primary source for 120–180s window
- Matt: keep File B forecasts as `FORECAST_LOW_CONFIDENCE` or remove

## Sign-off

**PASS WITH REVISIONS.** Usable for internal MMI Security Intel briefs after unsupported exact statistics are softened, quarantined, or removed. Not safe for external publication until PDF/page citations added and zombie stats purged.

## Source links

- [Verizon 2025 DBIR SMB Snapshot](https://www.verizon.com/business/resources/infographics/2025-dbir-smb-snapshot.pdf)
- [CrowdStrike 2025 Global Threat Report](https://www.crowdstrike.com/en-us/press-releases/crowdstrike-releases-2025-global-threat-report/)
- [Microsoft MFA 99.9% blog](https://www.microsoft.com/en-us/security/blog/2019/08/20/one-simple-action-you-can-take-to-prevent-99-9-percent-of-account-attacks/)
- [IBM Cost of a Data Breach 2025](https://www.ibm.com/reports/data-breach)
- [Veeam 2024 Ransomware Trends Report](https://www.primesys.co.uk/wp-content/uploads/2024/10/Veeam-2024-ransomware-trends-report.pdf)
- [NCSA zombie stat correction](https://www.staysafeonline.org/press/national-cyber-security-alliance-statement-regarding-incorrect-small-business-statistic)
- [MITRE ATT&CK](https://attack.mitre.org/)
