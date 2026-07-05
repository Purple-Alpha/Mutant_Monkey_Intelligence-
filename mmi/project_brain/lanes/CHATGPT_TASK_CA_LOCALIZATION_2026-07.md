# ChatGPT Task Brief — Canadian Localization Pass (Option A)

**Matt authorized:** 2026-07 (session start)  
**Task id:** `mmi-research-ca-localization-pass`  
**Output file:** `mmi/project_brain/lanes/RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md`  
**Lane:** ChatGPT — Deep / secondary research (verification)

---

## Mission

For each claim in **RESEARCH_VERIFICATION_2026-06.md §7** (and related §8 items), search **Canadian primary sources first** (StatCan, CCCS, OPC, CIRA, ISED). Produce CA cross-reference: **Confirms | Diverges | Insufficient Data**. Do not present global stats as Canadian facts.

---

## Claims to localize (from §7)

| ID | Global / verified claim | Prior source |
|----|-------------------------|--------------|
| V1 | Ransomware in 88% of SMB breach cases (Verizon 2025 DBIR SMB dataset) | Verizon SMB Snapshot |
| V2 | Third-party involvement ~30% globally | Verizon 2025 DBIR |
| V3 | MFA reduces account-compromise risk >99% (large commercial datasets) | Microsoft |
| V4 | Rapid eCrime breakout (48 min avg 2025; 29 min 2026) | CrowdStrike |
| V5 | Backup repositories routinely targeted (Veeam 96% / Sophos 94% framing) | Veeam/Sophos |
| V6 | MITRE ATT&CK IDs listed (technique IDs only) | MITRE |

## §8 items — CA cross-ref only if Canadian analogue exists (do not re-verify global purge list)

A1 4× SMB targeting · A4 BEC ~33% · A7 $2.66M IR · A10 40% MSSP budget · A11 60% closure (PURGE) · A12 manufacturing 72–84h · A13 $53k/hour

For §8: state **Insufficient Data** unless Canadian primary source found; never resurrect purged stats.

---

## Required output sections

1. Executive summary  
2. Methodology (Canada-first search order)  
3. Claim table with columns: Claim | Original jurisdiction | Canadian source | CA cross-ref (Confirms/Diverges/Insufficient Data) | Confidence 1–10 | Page/Section | Manual review?  
4. Safe for intel briefs (Canadian or global with localization tag)  
5. Internal only (NEEDS VERIFY)  
6. Purged / unchanged  
7. Sign-off: PASS | PASS WITH REVISIONS | FAIL  

---

## Hard stops

No endpoint swarm, SOAR, auto-containment, live telemetry. No invented stats. No Canadian prevalence claims from US vendor data alone.
