# Intel Brief — Ransomware Backup Targeting

Date filed: 2026-06-30  
Authority: Matt (Super) — Canadian operator  
Status: **Internal MMI Security Intel note — advisory only.** Not for external publication.  
Lane: Security Intel  
File: `intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md`

```yaml
brief_id: INTEL-ransomware-backup-targeting-2026-06
threat_name: Ransomware with backup-repository targeting (SMB-relevant pattern)
date_filed: 2026-06-30
author: Cursor PM (wire-mitigation-refs)
source_lanes:
  - lanes/RESEARCH_smb_threat_landscape_2026-06.md
  - lanes/RESEARCH_polymorphic_ransomware_delivery_2026-06.md
  - lanes/RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md
jurisdiction_scope: Canada-first
overall_source_status: MIXED
overall_confidence: 8
control_plane_status: ADVISORY_ONLY
automation_status: NONE
review_mode: HUMAN_REVIEW_ONLY
```

This brief links observed adversarial techniques to OPSEC mitigation references so the operator can **manually review** the relevant hardening checklist during incident review, drill planning, or PIR. MMI can surface linked OPSEC checks for human review. MMI does **not** automatically know which controls to audit or trigger mitigation workflows.

---

## 1. Threat summary

Ransomware operators frequently target backup repositories and recovery paths so encryption of live data becomes irreversible for the victim. For a solo Canadian operator running a local-first stack (`tasks.json` + `mmi/project_brain/` + B2 cold mirror), the failure mode is not only host encryption — it is **loss of the last known-good offline copy** or an **unverified restore path**.

Verizon reports 88% of Canadian SMB breaches involve ransomware. This brief is scoped to backup-targeting and recovery-inhibition patterns relevant to Matt's MMI workstation model. It does not establish Canadian national prevalence rates.

---

## 2. Why this matters for local-first MMI

| MMI asset | Risk if backup/recovery fails |
|-----------|-------------------------------|
| `mmi/project_brain/` | Intel, opsec, drills, architecture — irreplaceable operator context |
| `tasks.json` | Active queue and completion history |
| B2 cold archives | Last off-host recovery if local tree is encrypted or corrupted |
| Restore drill evidence | Without `OPSEC-8`, backup cadence (`OPSEC-6`) is assumption |

MMI v1 has no EDR, no SOAR, and no auto-containment. Recovery depends on **human-run** backup discipline and documented restore proof (`status/MMI_RESTORE_DRILL_2026-06.md`, future drill worksheets).

---

## 3. MITRE ATT&CK mapping

Technique IDs verified against primary MITRE ATT&CK pages on **2026-06-30** (per `RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md` §3 V6 — Global Framework, technique ID only). Technique mapping documents adversary behavior labels — **not** implemented protection.

```yaml
mitre_techniques:
  - id: T1486
    name: Data Encrypted for Impact
    source: MITRE ATT&CK
    url: https://attack.mitre.org/techniques/T1486/
  - id: T1490
    name: Inhibit System Recovery
    source: MITRE ATT&CK
    url: https://attack.mitre.org/techniques/T1490/
```

### ATT&CK block — T1486

| Field | Value |
|-------|--------|
| `technique_id` | T1486 |
| `technique_name` | Data Encrypted for Impact |
| `chain_stage` | impact |
| `smb_relevance` | Encrypting local project files and backups on the same host defeats recovery unless an isolated copy exists |
| `operator_signal` | Ransom note, mass extension change, inaccessible `mmi/` or repo files; see `intel/WAR_ROOM_SCORING_MATRIX_v2.md` §8 P1 host/filesystem |
| `mitigation_ref` | `OPSEC-6`, `OPSEC-7`, `OPSEC-8`, `OPSEC-BACKUP-PATHS` |
| `source_status` | VERIFIED |

### ATT&CK block — T1490

| Field | Value |
|-------|--------|
| `technique_id` | T1490 |
| `technique_name` | Inhibit System Recovery |
| `chain_stage` | impact |
| `smb_relevance` | Adversaries delete or disable backups and recovery tools so T1486 impact is permanent; B2 account compromise is in scope for a solo operator |
| `operator_signal` | Missing backup archives, failed restore, shadow-copy/backup-service tampering (if observed), unauthorized B2/rclone activity |
| `mitigation_ref` | `OPSEC-3`, `OPSEC-6`, `OPSEC-7`, `OPSEC-8`, `OPSEC-BACKUP-PATHS` |
| `source_status` | VERIFIED |

---

## 4. Mitigation references (human review only)

```yaml
mitigation_refs:
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
  - id: OPSEC-3
    title: MFA on backup/recovery accounts (B2)
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
T1486 / T1490 → this brief → OPSEC-6/7/8 + OPSEC-BACKUP-PATHS → war-room evidence (push log, restore drill worksheet)
```

---

## 5. Claims table

| Claim | Jurisdiction | Confidence (1-10) | Source + date | Page/Section | CA cross-reference | Manual review? |
|-------|--------------|-------------------|---------------|--------------|---------------------|----------------|
| T1486 and T1490 are current MITRE ATT&CK technique IDs | Global Framework — technique ID only | 9 | MITRE ATT&CK (attack.mitre.org), checked 2026-06-30 | N/A — live matrix lookup | Not applicable to technique-ID claims | No |
| Ransomware ranks among the most disruptive cybercrime threats and is described as the top cybercrime threat facing Canada's critical infrastructure | Canada (primary) | 7 | CCCS National Cyber Threat Assessment 2025–2026 (PDF) | Insufficient Data — exact page/section not extracted | N/A — Canadian primary source | Yes (no page/section) |
| 16% of Canadian businesses were impacted by a cybersecurity incident in 2023; 13% of impacted businesses reported ransomware as the attack method; recovery spending reached CAD $1.2B | Canada (primary) | 8 | Statistics Canada Daily, 2024-10-21, table 22-10-0078-01 | Daily release; granular table page not pulled | N/A — Canadian primary source | Yes (granular table page not pulled) |
| 24% of surveyed Canadian organizations reported a ransomware attack in the last 12 months | Canada (survey) | 6 | 2025 CIRA Cybersecurity Survey | Page not extracted | N/A — label as CIRA survey result, not a national incident rate | Yes |
| Backup repositories are routinely targeted in ransomware incidents (Veeam 96% targeting framing) | Global Data — Requires Localization | 8 | Veeam 2024 Ransomware Trends Report | Exact page not extracted | Confirms theme (recovery inhibition), Insufficient Data for exact % — per `RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md` §3 (V5); CCCS ransomware guidance and MITRE T1490 support theme, not Canadian % | Yes (internal context only, excluded from headline) |
| Backup compromise attempted in 94% of reported ransomware incidents (Sophos framing) | Global Data — Requires Localization | 7 | Sophos 2024 ransomware reporting | Exact page not extracted | Confirms theme (recovery inhibition), Insufficient Data for exact % — per localization §3 (V5) | Yes (internal context only, excluded from headline) |
| Ransomware present in 88% of SMB breach cases in Verizon 2025 DBIR SMB Snapshot dataset | Global Data — Requires Localization | 8 | Verizon 2025 DBIR SMB Snapshot | Infographic — no page numbers | Confirms theme, Diverges on magnitude — StatCan 2023 shows 13% of impacted Canadian businesses cite ransomware, a different denominator and methodology; not usable as a Canadian rate — per localization §3 (V1) | Yes (internal context only, excluded from headline) |

---

## 6. War-room relevance

| Scoring matrix touchpoint | How this brief supports review |
|---------------------------|-------------------------------|
| `WAR_ROOM_SCORING_MATRIX_v2.md` Axis A (technical evidence) | Backup recency, restore-test SLO |
| §8 P1 backup/recovery signals | Operator compares live signals to this brief's technique labels |
| Tier 3/4 restore path tested | `OPSEC-8` — use this brief when planning next quarterly drill |
| Decision log (Axis B) | `OPSEC-9` at first suspicion of backup tampering |

War room panels remain read-only. This brief does not change tier scores automatically.

---

## 7. Purple-team / restore-drill relevance

- **Phase 6 drill** (`intel/drills/DRILL_2026-06-30_phase6_sim/`) identified A7 restore-path gap — closed once in `status/MMI_RESTORE_DRILL_2026-06.md`; `OPSEC-8` remains `NOT_STARTED` on checklist until Matt records `last_done`.
- **Recommended drill use:** use this brief as the intel input when running the **next** restore drill — scenario: "B2 archive exists but local `mmi/project_brain/` is unavailable; prove recovery from cold mirror."
- **Do not conflate:** one successful restore drill ≠ all `OPSEC-6/7/8` items `DONE`.

---

## 8. Limitations (Crucible)

- **What this brief does NOT establish:** Canadian-specific frequency or prevalence rates for backup-repository targeting specifically; no Canadian primary source provides a quantified backup-targeting rate — vendor percentages (Veeam 96%, Sophos 94%) remain global-only and excluded from headline findings.
- **Claims downgraded from the source research and why:** Veeam 96% and Sophos 94% backup-targeting figures are kept as properly labeled global claims only — `RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md` §3 (V5) found "Confirms theme (recovery inhibition), Insufficient Data for exact %" against CCCS ransomware guidance and MITRE T1490; the Verizon 88% SMB ransomware-in-dataset figure is kept as a properly labeled global claim only — localization §3 (V1) found "Confirms theme, Diverges on magnitude" against StatCan's 13%, so it is excluded from headline and from any Canadian-fact framing.
- **Claims purged outright (zombie stats, unsupported conversions) and why:** per `lanes/RESEARCH_VERIFICATION_2026-06.md` §8 and `RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md` §4/§7 — the 4× SMB targeting ratio, BEC ~33% of initial breaches, the exact $2.66M IR-savings figure, the 40% MSSP budget share, "60% of SMBs close within six months" (confirmed zombie statistic, NCSA disavowed), manufacturing 72–84h downtime, and $53,000/hour SMB downtime. None of these appear anywhere in this brief.
- **What would resolve each remaining `Insufficient Data` item:** an exact page/section citation from the CCCS NCTA 2025–2026 PDF for the critical-infrastructure ransomware ranking; the specific cell reference in StatCan table 22-10-0078-01; a Canadian primary source with a quantified backup-targeting rate (none found in localization pass).
- **Canadian-localization status (per claim in §5):** CCCS NCTA and StatCan claims are Canadian primary sources — Confirms, no further localization needed. CIRA 24% is a Canadian survey result, correctly labeled as such, not a national incident rate. Veeam 96% / Sophos 94% backup-targeting — Confirms theme (recovery inhibition), Insufficient Data for exact %; excluded from headline. Verizon 88% SMB ransomware-in-dataset — Confirms theme, Diverges on magnitude (StatCan denominator and methodology differ); excluded from headline.
- MITRE mapping describes adversary techniques — **not** proof that OPSEC items are implemented or effective.
- `OPSEC-BACKUP-PATHS` is DRAFT documentation; it does not enforce path protection.
- `mmi/war_room.py` patched into cold-backup allowlist (`mmi-war-room-backup-allowlist-patch`). B2 cold mirror pushed (`mmi_backup_20260629_203555.tar.gz`, PASS 2026-06-30) and isolated `--restore-check` validated file recovery (7,889 bytes). **File-level recoverability proven** — quarterly `OPSEC-8` operator drill evidence (`last_done`) remains a separate task.
- Optional techniques (T1027, T1059, T1070, T1485) are **not** included — this brief does not discuss those chains; adding them would require separate justification.

---

## 9. Canadian SMB context

- Operator jurisdiction: Canada (British Columbia). Regulatory triage for real incidents stays in `WAR_ROOM_SCORING_MATRIX_v2.md` §7.4/§9 — not in this brief.
- CCCS National Cyber Threat Assessment 2025–2026 frames ransomware as the top cybercrime threat to Canada's critical infrastructure — used here as Canadian primary context for why backup/recovery discipline matters, not as a backup-targeting-specific statistic.
- StatCan 2023 (table 22-10-0078-01) is the only Canadian primary source with a quantified ransomware-prevalence figure (13% of impacted businesses); it does not speak to backup-repository targeting specifically and should not be read as validating the Veeam/Sophos backup-targeting percentages or the Verizon 88% SMB figure.
- CIRA 2025 survey (24%) is a self-selected survey sample, not a national incident rate — labeled accordingly throughout this brief.
- CCCS guidance on testing recovery in isolated environments is reflected in project practice (`MMI_RESTORE_DRILL_2026-06.md`) but is procedural evidence, not a prevalence claim.

---

## 10. Hard stops

- Advisory-only; no auto-containment, endpoint swarm, EDR requirement, live telemetry, or SOAR.
- No external publication language; internal operator note only.
- Surface OPSEC links for **human review** — never imply automatic mitigation dispatch.
- No global vendor percentage appears in this brief's headline findings or ATT&CK `smb_relevance` text as if it were a Canadian fact.

---

## Sign-off

**PASS WITH REVISIONS** — Headline ATT&CK mapping and Canadian primary-source context (CCCS, StatCan, CIRA) are filing-ready after CA localization normalize (`mmi-intel-brief-ca-normalize-backup-targeting`). Internal gaps remain open pending: CCCS/StatCan page-level citations and a Canadian primary source for backup-targeting prevalence (none found). Global vendor percentages (Veeam, Sophos, Verizon) remain claims-table-only with proper localization tags. None of these gaps affect the headline VERIFIED MITRE claims or Canadian-primary context used above.
