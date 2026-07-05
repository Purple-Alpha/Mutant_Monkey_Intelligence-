# MMI Intel Brief Template

Date: 2026-06-29
Authority: Matt (Super) — Canadian operator
Status: **Template — fillable.** Copy this file per brief; do not edit this master.
Lane: Security Intel / Design
Task: `mmi-intel-brief-template`
Sources: `architecture/MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md` (deliverable spec), `lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md` (Canada-first Truth Database, Confidence Scoring, Crucible Protocol), `lanes/RESEARCH_VERIFICATION_2026-06.md` (accepted research baseline — PASS WITH REVISIONS)

---

## 0. How to use this template

1. Copy this file to `mmi/project_brain/intel/briefs/INTEL_<slug>_<yyyy-mm>.md`. Do not build briefs in this template file.
2. Fill every field. If a field is unknown, write `Insufficient Data` — never invent a value (Crucible Protocol, `MMI_RESEARCH_RIGOR_PROTOCOL.md` §3).
3. Every claim needs a `source_status`. Only `VERIFIED` claims may leave this project as external or operator-facing fact. `NEEDS VERIFY` and `RESEARCH-ONLY` stay internal.
4. Every claim sourced from a non-Canadian report (Verizon, IBM, CrowdStrike, Microsoft, Veeam, Sophos, etc.) carries `[Global Data — Requires Localization]` and a Canadian cross-reference field — even if that field currently reads `Insufficient Data`. Do not present global stats as Canadian fact.
5. This brief informs the operator. It never blocks, contains, quarantines, or touches a host. If a recommendation implies automated action, it is out of scope — flag it and stop (see §7 Hard stops).
6. The worked example in §6 uses **VERIFIED claims only**. Do not copy a `NEEDS VERIFY` or `RESEARCH-ONLY` claim into a brief's headline findings — those statuses exist for internal prioritization, not for the example pattern.
7. Every filed brief must wire `mitigation_ref` to real `OPSEC-<n>` items in `opsec/OPERATOR_OPSEC_CHECKLIST.md` and/or opsec artifacts (e.g. `opsec/BACKUP_PROTECTED_PATHS.md`) where applicable. MMI surfaces these links for **human review** — it does not dispatch or enforce controls automatically.

---

## 1. Brief header

```markdown
brief_id: INTEL-<slug>-<yyyy-mm>
threat_name:
date_filed:
author:
source_lanes:            # research lane files this brief draws from, e.g. lanes/RESEARCH_smb_threat_landscape_2026-06.md
jurisdiction_scope: Canada-first   # per MMI_RESEARCH_RIGOR_PROTOCOL.md §0 — global sources must be localized or marked Insufficient Data
overall_source_status:   # VERIFIED | NEEDS VERIFY | RESEARCH-ONLY | MIXED (see §4 rules)
overall_confidence:      # 1-10, see §3 Confidence Scoring
control_plane_status: ADVISORY_ONLY
automation_status: NONE
review_mode: HUMAN_REVIEW_ONLY
```

`overall_source_status` is `MIXED` whenever a brief carries both `VERIFIED` and `NEEDS VERIFY` claims — which is normal. `MIXED` briefs may circulate internally; only the `VERIFIED` claims within them may be quoted externally.

### 1.1 MITRE and mitigation wiring (required where applicable)

Use primary MITRE ATT&CK pages only for technique IDs. Technique mapping documents adversary behavior — **not** implemented protection.

```yaml
mitre_techniques:
  - id: T1486
    name: Data Encrypted for Impact
    source: MITRE ATT&CK
    url: https://attack.mitre.org/techniques/T1486/

mitigation_refs:
  - id: OPSEC-6
    title: <from OPERATOR_OPSEC_CHECKLIST.md>
    file: opsec/OPERATOR_OPSEC_CHECKLIST.md
    status: NEEDS_REVIEW | ACTIVE
    review_mode: HUMAN_REVIEW_ONLY
  - id: OPSEC-BACKUP-PATHS
    title: Backup Protected Paths (if backup/recovery scoped)
    file: opsec/BACKUP_PROTECTED_PATHS.md
    status: DRAFT | ACTIVE
    review_mode: HUMAN_REVIEW_ONLY
```

**Acceptable framing:** *This brief links observed techniques to OPSEC references so the operator can manually review relevant checklist items during incident review, drill planning, or PIR.*

**Forbidden framing:** *This automatically triggers the correct mitigation workflow* or *MMI automatically knows which controls to audit.*

Use existing `OPSEC-<n>` IDs from `OPERATOR_OPSEC_CHECKLIST.md` only — do not invent conflicting IDs. Opsec artifacts use stable `artifact_id` values (e.g. `OPSEC-BACKUP-PATHS`) defined in their own files.

---

## 2. ATT&CK block (repeat per technique)

SMB-scoped only — use techniques relevant to a solo/SMB operator, not the full enterprise matrix, per `MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md`.

```markdown
| Field | Value |
|---|---|
| `technique_id` | e.g. T1566.002 |
| `technique_name` | e.g. Spearphishing Link |
| `chain_stage` | delivery / execution / defense evasion / discovery / command and control / impact |
| `smb_relevance` | 1-2 lines: why a solo/SMB operator should care |
| `operator_signal` | What the operator might actually observe (tie to evidence families in `intel/WAR_ROOM_SCORING_MATRIX_v2.md` §6 where relevant) |
| `mitigation_ref` | `OPSEC-<n>` and/or artifact ID (e.g. `OPSEC-BACKUP-PATHS`) — must resolve to `opsec/OPERATOR_OPSEC_CHECKLIST.md` or a named opsec artifact file |
| `source_status` | VERIFIED / NEEDS VERIFY / RESEARCH-ONLY |
```

Technique IDs and names are checked against the live MITRE ATT&CK matrix at brief-filing time — note the check date. ATT&CK technique IDs themselves are treated as `Global Framework — technique ID only`; they don't need a Canadian cross-reference, but any claim about *how often* a technique appears in a Canadian context does.

---

## 3. Claims table (Confidence Scoring)

Every numeric or external claim in the brief — not just headline stats — gets a row. Format locked by `MMI_RESEARCH_RIGOR_PROTOCOL.md` §2.

```markdown
| Claim | Jurisdiction | Confidence (1-10) | Source + date | Page/Section | CA cross-reference | Manual review? |
|-------|--------------|--------------------|-----------------|---------------|----------------------|------------------|
|       |              |                    |                 |               |                      |                  |
```

Rules (do not relax these in a filled brief):

- No page/section → automatic `Manual review: Yes`.
- Confidence ≤4 → `NEEDS VERIFY`; may not appear in this brief's headline findings or be published.
- Confidence 5–7 → internal use only, with source framing intact.
- Confidence ≥8 → eligible for operator-facing material once jurisdiction/CA cross-reference is resolved.
- Global source with no Canadian cross-reference yet → `CA cross-reference: Insufficient Data` is correct and honest; do not leave the cell blank, and do not guess a Canadian number to fill it.

---

## 4. Source-status rules

| `source_status` | Meaning | May appear in... |
|------------------|---------|---------------------|
| `VERIFIED` | Named source + date, confidence ≥8, jurisdiction labeled, CA cross-reference resolved or explicitly `Insufficient Data` | Operator-facing briefs and external material |
| `NEEDS VERIFY` | Retained for internal prioritization; not yet sourced to the §3 bar | Internal use only — **forbidden in this brief's headline findings, forbidden in template worked examples** |
| `RESEARCH-ONLY` | Theoretical, forecast, or internal narrative (e.g. a documented attack-chain description) never presented as fact | Internal use only, always labeled `RESEARCH-ONLY` inline wherever it's referenced |

A brief is `MIXED` (§1) when it carries more than one of the above. That's expected — most real briefs will. What's not allowed is presenting a `NEEDS VERIFY` claim as if it were `VERIFIED` anywhere a reader (including future-Matt) might mistake it for settled fact.

---

## 5. Crucible limitations block (required, every brief)

Per `MMI_RESEARCH_RIGOR_PROTOCOL.md` §3 — Security Intel pipeline tasks default to Crucible-grade. Do not skip this section even on a short brief.

```markdown
## Limitations

- What this brief does NOT establish:
- Claims downgraded from the source research and why:
- Claims purged outright (zombie stats, unsupported conversions) and why:
- What primary source or page citation would resolve each remaining `Insufficient Data` / `NEEDS VERIFY` item:
- Canadian-localization status: confirms / diverges / Insufficient Data — for every global-sourced claim in §3
```

---

## 6. Worked example (VERIFIED claims only)

This example exists to show the pattern. It deliberately uses only claims carrying `VERIFIED` status in `lanes/RESEARCH_VERIFICATION_2026-06.md` §7 — no `NEEDS VERIFY` claim from that file appears below, by design.

```markdown
brief_id: INTEL-ransomware-backup-targeting-2026-06
threat_name: Ransomware with backup-repository targeting (SMB-relevant pattern)
date_filed: 2026-06-29
author: Claude (Design)
source_lanes: lanes/RESEARCH_smb_threat_landscape_2026-06.md, lanes/RESEARCH_polymorphic_ransomware_delivery_2026-06.md
jurisdiction_scope: Canada-first
overall_source_status: VERIFIED
overall_confidence: 8
```

**ATT&CK block:**

| Field | Value |
|---|---|
| `technique_id` | T1486 |
| `technique_name` | Data Encrypted for Impact |
| `chain_stage` | impact |
| `smb_relevance` | Ransomware was the dominant pattern in the Verizon 2025 DBIR SMB breach dataset; backup destruction is a routine precursor, so a solo operator's recovery path is the actual point of failure, not just the initial infection |
| `operator_signal` | Ransom note, mass file-extension change, inaccessible files; cross-check against `intel/WAR_ROOM_SCORING_MATRIX_v2.md` §8 P1 host/filesystem and backup/recovery signals |
| `mitigation_ref` | `OPSEC-6`, `OPSEC-7`, `OPSEC-8`, `OPSEC-BACKUP-PATHS` |
| `source_status` | VERIFIED |

| Field | Value |
|---|---|
| `technique_id` | T1490 |
| `technique_name` | Inhibit System Recovery |
| `chain_stage` | impact |
| `smb_relevance` | Backup deletion and recovery inhibition make T1486 permanent; B2 account and local archive paths are in scope for a solo operator |
| `operator_signal` | Missing or tampered backup archives, failed restore, suspicious B2/rclone activity; cross-check `intel/WAR_ROOM_SCORING_MATRIX_v2.md` §8 P1 backup/recovery |
| `mitigation_ref` | `OPSEC-3`, `OPSEC-6`, `OPSEC-7`, `OPSEC-8`, `OPSEC-BACKUP-PATHS` |
| `source_status` | VERIFIED |

| Field | Value |
|---|---|
| `technique_id` | T1027.006 |
| `technique_name` | HTML Smuggling |
| `chain_stage` | defense evasion |
| `smb_relevance` | Confirmed sub-technique used to deliver payloads past mail filtering; relevant to phishing-discipline opsec, not to endpoint defense MMI does not build | 
| `operator_signal` | Unusual attachment/link behavior reported by a human; MMI has no mail-filter telemetry to detect this automatically |
| `mitigation_ref` | `OPSEC-4` |
| `source_status` | VERIFIED |

**Claims table:**

| Claim | Jurisdiction | Confidence (1-10) | Source + date | Page/Section | CA cross-reference | Manual review? |
|-------|--------------|--------------------|-----------------|---------------|----------------------|------------------|
| Ransomware was present in 88% of SMB breach cases in Verizon's 2025 DBIR SMB Snapshot dataset | Global Data — Requires Localization | 8 | Verizon 2025 DBIR SMB Snapshot (2025) | Single-page infographic — no internal page numbers | Insufficient Data — Canadian localization pass not yet run per `MMI_RESEARCH_RIGOR_PROTOCOL.md` §7 | Yes (no page number) |
| Backup repositories were targeted in 96% of reported ransomware incidents | Global Data — Requires Localization | 8 | Veeam 2024 Ransomware Trends Report | Insufficient Data — exact page not extracted | Insufficient Data — Canadian localization pass not yet run | Yes (no page number) |
| Backup compromise was attempted in 94% of reported ransomware incidents | Global Data — Requires Localization | 7 | Sophos 2024 (ransomware reporting) | Insufficient Data — exact page not extracted | Insufficient Data — Canadian localization pass not yet run | Yes (no page number) |
| T1486, T1490, and T1027.006 are confirmed current MITRE ATT&CK technique IDs | Global Framework — technique ID only | 9 | MITRE ATT&CK (attack.mitre.org), checked 2026-06-30 | N/A — live matrix lookup | Not applicable to technique-ID claims | No |

**Limitations:**

- This brief does NOT establish Canadian-specific ransomware prevalence rates for SMBs — every percentage above is global/US vendor data, not Canadian primary data.
- `MMI_RESEARCH_RIGOR_PROTOCOL.md` §7 explicitly says existing research files predate the Canada-first protocol and must be treated as US/global-biased until a localization pass runs. That pass has not run as of this brief's filing date — hence every `CA cross-reference` cell above reads `Insufficient Data`, not a guess.
- Claims downgraded from the source research: the 4× SMB targeting ratio, the <25-minute AD-compromise claim, BEC ~33%, the $2.66M IR-savings figure, the 40% MSSP budget share, manufacturing 72–84h downtime, and $53,000/hour downtime are all `NEEDS VERIFY` or purged per `lanes/RESEARCH_VERIFICATION_2026-06.md` §8 and are deliberately **not** used as headline findings in this worked example.
- Purged outright: "60% of SMBs close within six months" — confirmed zombie statistic per NCSA's own correction; do not resurrect this number in any future brief.
- What would resolve the remaining gaps: a Canadian primary source on ransomware/backup-targeting prevalence (StatCan Survey of Cyber Security and Cybercrime, or a CCCS incident-trend publication) and exact page/section citations from the Verizon SMB Snapshot, Veeam 2024, and Sophos 2024 reports.
- Canadian-localization status: Insufficient Data for all three percentage claims above; Confirms/Diverges cannot be assessed until the StatCan/CCCS cross-reference is run.
```

---

## 7. Hard stops (reaffirmed for every brief built from this template)

- No endpoint swarm, no live telemetry, no Sysmon/EDR requirement, no automated containment — a brief informs the operator; it never acts on a host (`MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md` Out of Scope).
- Local-first: briefs live in `mmi/project_brain/intel/briefs/`; no hosted DB, no live cloud queue, no NorthStar bridge.
- No `NEEDS VERIFY` or `RESEARCH-ONLY` claim is ever published externally or presented as settled fact internally.
- No global vendor stat is presented as a Canadian fact without the `[Global Data — Requires Localization]` tag and an honest CA cross-reference (even when that reference is `Insufficient Data`).
- `mitigation_ref` values must resolve to real `OPSEC-<n>` items in `opsec/OPERATOR_OPSEC_CHECKLIST.md` or named opsec artifacts (e.g. `opsec/BACKUP_PROTECTED_PATHS.md`). MMI surfaces these for human review only — no automatic dispatch.
- `INTEL_INDEX.md` traceability: every filed brief gets one index row in `intel/INTEL_INDEX.md` §3.

---

## 8. Acceptance checklist (run before filing a real brief)

- [ ] Every claim in the claims table has a `source_status` and, if global, a `[Global Data — Requires Localization]` tag
- [ ] No `NEEDS VERIFY` or `RESEARCH-ONLY` claim appears in the brief's headline findings or ATT&CK `smb_relevance` text as if settled
- [ ] Every claim with no page/section citation is flagged `Manual review: Yes`
- [ ] Limitations block is filled, not skipped
- [ ] ATT&CK technique IDs/names checked against the live matrix on the filing date
- [ ] `mitigation_ref` values resolve to real `OPSEC-<n>` or artifact IDs — not placeholders
- [ ] `control_plane_status: ADVISORY_ONLY` and `review_mode: HUMAN_REVIEW_ONLY` set in header wiring
- [ ] No recommendation implies automated blocking, containment, or endpoint action

---

## 9. Version

| Field | Value |
|-------|-------|
| Version | 1.1 |
| Status | Template — `mitigation_ref` wired to real OPSEC IDs per `mmi-wire-mitigation-refs` |
| Next review | When new opsec artifacts land or first brief pattern changes |
