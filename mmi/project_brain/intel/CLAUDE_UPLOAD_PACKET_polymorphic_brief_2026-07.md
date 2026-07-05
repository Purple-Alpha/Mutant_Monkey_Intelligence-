# Claude Upload Packet — Polymorphic Delivery Intel Brief (Option B)

**Task id:** `mmi-intel-brief-polymorphic-delivery`  
**Matt:** Upload **this entire file** to Claude if folder connect fails.  
**Repo path (for folder connect):** `C:\Architectapp_clean` or WSL `/mnt/c/Architectapp_clean`

---

## Your deliverables

1. `mmi/project_brain/intel/briefs/INTEL_polymorphic-ransomware-delivery_2026-07.md`
2. Update `mmi/project_brain/intel/INTEL_INDEX.md` — add **one row** (full file content returned in chat; Matt/Cursor saves to repo)

**Sign-off line required:** `PASS | PASS WITH REVISIONS | FAIL`

---

## Task rules (hard stops)

- `control_plane_status: ADVISORY_ONLY` — MMI surfaces OPSEC checks for **human review** only
- VERIFIED claims only in headline / ATT&CK `smb_relevance` operator-facing text
- Canadian stats from §CA localization below only — **not** Verizon/Microsoft/CrowdStrike/Veeam/Sophos % as Canadian facts
- MITRE IDs = **Global Framework — technique ID only**
- FORECAST / AI JIT / 6–12mo predictions = **RESEARCH-ONLY** — not headline
- **Purged:** 60% closure, 4× SMB, BEC ~33%, $2.66M IR, 40% MSSP, 72–84h manufacturing, $53k/hr
- No SOAR, EDR, endpoint swarm, auto-containment, live telemetry
- `mitigation_ref`: **OPSEC-4**, **OPSEC-5** (phish discipline) — from checklist below
- Include Crucible **Limitations** block

---

## Brief header (fill in)

```yaml
brief_id: INTEL-polymorphic-ransomware-delivery-2026-07
threat_name: Polymorphic ransomware delivery via adversarial email fraud (SMB-relevant)
date_filed: 2026-07
author: Claude (Design)
source_lanes:
  - lanes/RESEARCH_polymorphic_ransomware_delivery_2026-06.md
jurisdiction_scope: Canada-first
overall_source_status: MIXED   # VERIFIED techniques + RESEARCH-ONLY chain narrative
overall_confidence: 7
control_plane_status: ADVISORY_ONLY
automation_status: NONE
review_mode: HUMAN_REVIEW_ONLY
```

---

## SOURCE: RESEARCH_polymorphic_ransomware_delivery_2026-06.md (full)

Threat: polymorphic ransomware delivery via adversarial email fraud.

**MITRE mapping (verified IDs per RESEARCH_VERIFICATION_2026-06):**

| ID | Name | Stage |
|----|------|-------|
| T1566.002 | Spearphishing Link | delivery |
| T1204.001 | User Execution: Malicious Link | execution |
| T1027 | Obfuscated Files/Information | defense evasion |
| T1027.006 | HTML Smuggling | defense evasion (sub-technique) |
| T1082 | System Information Discovery | discovery |
| T1071.001 | Web Protocols | C2 |
| T1486 | Data Encrypted for Impact | impact |

**Kill chain (RESEARCH-ONLY narrative — document as threat description, not build guide):**  
Spearphish link → client profiling → sandbox benign 404 OR human HTML smuggling → HTTPS C2 → ransomware execution.

**Technical notes (internal):** ephemeral domains, homoglyphs, HTML smuggling via base64 Blob; stage-1 loader sleep/env checks; Kerberoasting T1558.003 = **AD environments only — not solo operator default**.

**NEEDS VERIFY / FORECAST (not headline):**
- SEG sandbox 120–180s — use "within minutes" unless primary source
- AI JIT compilation, C2 via signed enterprise workflows — FORECAST_LOW_CONFIDENCE
- 6–12 month predictions — RESEARCH-ONLY
- Endpoint agent swarm — **not authorized for MMI** — RESEARCH-ONLY

**MMI relevance:** phish/link discipline (Mini PC), cold backup recovery layer — not SEG/EDR/swarm build.

---

## SOURCE: RESEARCH_VERIFICATION_2026-06.md (relevant excerpts)

**Verified MITRE IDs:** T1566.002, T1204.001, T1027, T1027.006, T1082, T1071.001, T1486, T1558.003 (AD context only).

**File B verdicts:**
- HTML smuggling T1027.006 — Verified as technique label
- SEG 120–180s — NEEDS VERIFY
- AI JIT / polymorphic phishing — FORECAST / LOW CONFIDENCE
- C2 via signed enterprise workflows — FORECAST / LOW CONFIDENCE

**Purged — never use:** 60% closure, 4× targeting, BEC ~33%, $2.66M, 40% MSSP, 72–84h, $53k/hr.

---

## SOURCE: RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md (safe for Canadian context)

**Safe in briefs (Canadian):**
- StatCan 2023: **16%** of Canadian businesses impacted by cyber incidents; **13%** of impacted businesses reported **ransomware** as attack method; recovery spend **CAD $1.2B**
- CCCS NCTA 2025–2026: ransomware among most disruptive cybercrime threats; **top threat to Canada's critical infrastructure**
- CIRA 2025 survey: **24% of surveyed Canadian organizations** reported ransomware in last 12 months — label **CIRA survey**, not national rate

**Global only (if mentioned):** Verizon 88%, MFA >99%, CrowdStrike minutes, Veeam/Sophos backup % — `[Global Data — Requires Localization]`, CA cross-ref Insufficient Data for exact %

---

## OPSEC checklist rows (mitigation_ref)

| ID | Control | Category |
|----|---------|----------|
| OPSEC-4 | Link-hover and sender-domain check before clicking unexpected email links | PHISH |
| OPSEC-5 | Out-of-band confirmation before acting on payment/credential-change email requests | PHISH |

Use `mitigation_ref: OPSEC-4` for T1566.002 / T1204.001 blocks. Use `OPSEC-5` where BEC-style fraud framing applies (qualitative only — no BEC ~33% stat).

---

## INTEL_INDEX row to add (§3 table)

| brief_id | threat | source_lanes | attack_ids | recommendations | source_status | updated |
|----------|--------|--------------|------------|-----------------|---------------|---------|
| INTEL-polymorphic-ransomware-delivery-2026-07 | Polymorphic ransomware delivery via adversarial email fraud | lanes/RESEARCH_polymorphic_ransomware_delivery_2026-06.md | T1566.002, T1204.001, T1027.006, T1486 | OPSEC-4, OPSEC-5 | MIXED | 2026-07 |

Brief file: `intel/briefs/INTEL_polymorphic-ransomware-delivery_2026-07.md`

---

## Brief structure (match first brief pattern)

1. Threat summary (delivery/phish chain — solo operator / Mini PC)
2. Why this matters for local-first MMI (no mail-filter telemetry; human phish discipline is the control)
3. MITRE ATT&CK blocks (at minimum T1566.002, T1204.001, T1027.006, T1486 — add T1082/T1071.001 if discussed in smb_relevance)
4. Mitigation refs (OPSEC-4, OPSEC-5) — human review only
5. Claims table with jurisdiction + CA cross-ref
6. War-room relevance (mail/phish signals in scoring matrix §8 if applicable)
7. Limitations (Crucible) — exclude FORECAST items from headline; endpoint swarm not build
8. Canadian SMB context (StatCan/CCCS/CIRA from localization)
9. Hard stops
10. Sign-off: PASS | PASS WITH REVISIONS | FAIL

---

## Pattern reference

First brief: `INTEL-ransomware-backup-targeting-2026-06.md` — same yaml header style, ADVISORY_ONLY framing, limitations block, no auto-enforcement language.

---

## Return format for Matt

Paste back:
1. Full markdown for `INTEL_polymorphic-ransomware-delivery_2026-07.md`
2. Full updated `INTEL_INDEX.md` (or just §3 table + version history line)
3. Sign-off line

Matt will save to repo via Cursor.
