# MMI Intel Index

Date: 2026-06-30
Authority: Matt (Super) — Canadian operator
Status: **Active — two briefs filed.** Traceability spine; one row per filed brief.
Lane: Security Intel / Design
Task: `mmi-intel-index`
Sources: `architecture/MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md` (Research Index Structure — exact column spec), `intel/templates/INTEL_BRIEF_TEMPLATE.md` (brief fields this index draws from), `lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md` (Canada-first Truth Database)

---

## 0. Purpose

Every operator recommendation in MMI Security Intel must resolve back to a research lane file through exactly one filed brief. This index is that path. A recommendation with no traceable row here is a defect, not a feature, per `MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md`.

Flow (one direction only):

```text
lanes/RESEARCH_*.md  →  intel/briefs/INTEL_<slug>_<yyyy-mm>.md  →  row in this index  →  operator recommendation / opsec item
```

Nothing is recommended to Matt without a traceable source. Nothing is added to this index without a real, filed brief behind it — do not seed rows for briefs that don't exist yet.

---

## 1. How to use this index

1. When a brief is filed at `intel/briefs/INTEL_<slug>_<yyyy-mm>.md`, add exactly one row to §3 below.
2. Pull `attack_ids` and `source_status` straight from the brief's §1 header and §2 ATT&CK block — don't re-derive or summarize them differently here.
3. `recommendations` lists linked `OPSEC-<n>` item IDs from `opsec/OPERATOR_OPSEC_CHECKLIST.md` and/or opsec artifact IDs (e.g. `OPSEC-BACKUP-PATHS` → `opsec/BACKUP_PROTECTED_PATHS.md`). MMI surfaces these for **human review** — no automatic checklist dispatch.
4. `source_status` here is the brief's `overall_source_status` (`VERIFIED` / `NEEDS VERIFY` / `RESEARCH-ONLY` / `MIXED`) — not a separate judgment call.
5. Update `updated` on every edit to that row, including status changes (e.g. a `NEEDS VERIFY` claim later gets sourced and the brief is amended).
6. Never add a row for a planned or in-progress brief. A row implies a filed, readable brief exists at the linked path.

---

## 2. Column spec

Per `MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md` Research Index Structure:

| Field | Purpose |
|---|---|
| `brief_id` | Stable brief identifier, matches the brief's own `brief_id` header field |
| `threat` | Threat name, matches the brief's `threat_name` |
| `source_lanes` | Research lane files the brief drew from |
| `attack_ids` | ATT&CK technique IDs referenced in the brief's ATT&CK block(s) |
| `recommendations` | Linked operator recommendations (opsec item ID once that checklist exists, otherwise plain text) |
| `source_status` | The brief's `overall_source_status` |
| `updated` | Last update date for this row |

---

## 3. Index

| `brief_id` | `threat` | `source_lanes` | `attack_ids` | `recommendations` | `source_status` | `updated` |
|---|---|---|---|---|---|---|
| `INTEL-ransomware-backup-targeting-2026-06` | Ransomware with backup-repository targeting (SMB-relevant pattern) | `lanes/RESEARCH_smb_threat_landscape_2026-06.md`, `lanes/RESEARCH_polymorphic_ransomware_delivery_2026-06.md`, `lanes/RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md` | T1486, T1490 | `OPSEC-3`, `OPSEC-6`, `OPSEC-7`, `OPSEC-8`, `OPSEC-BACKUP-PATHS` | MIXED | 2026-07-01 |
| `INTEL-polymorphic-ransomware-delivery-2026-07` | Polymorphic Ransomware Delivery via Adversarial Email Fraud | `lanes/RESEARCH_polymorphic_ransomware_delivery_2026-06.md`, `lanes/RESEARCH_VERIFICATION_2026-06.md`, `lanes/RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md` | T1566.002, T1204.001, T1027, T1027.006, T1082, T1071.001, T1486 | `OPSEC-4`, `OPSEC-5`, `OPSEC-6`, `OPSEC-7`, `OPSEC-8`, `OPSEC-9`, `OPSEC-BACKUP-PATHS` | MIXED | 2026-07-01 |

Brief files:
- `intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md`
- `intel/briefs/INTEL_polymorphic-ransomware-delivery_2026-07.md`

---

## 4. Hard stops (reaffirmed)

- No row without a filed brief behind it — this index never leads a reader to a brief that doesn't exist.
- No row presents a `NEEDS VERIFY` or `RESEARCH-ONLY` brief's content as settled fact — `source_status` is carried through unchanged from the brief, never upgraded here.
- This index is a local markdown file under `mmi/project_brain/intel/`. No hosted DB, no live query layer, no NorthStar bridge (`MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md` Local-First Constraints).
- This index does not itself make recommendations — it links to recommendations a filed brief already made. Don't add new operator guidance here that isn't already in a brief.
- `recommendations` must use real `OPSEC-<n>` IDs from `opsec/OPERATOR_OPSEC_CHECKLIST.md` and/or artifact IDs defined in opsec files — surfaced for human review only; no automatic enforcement.

---

## 5. Acceptance checklist (run before treating a row as valid)

- [ ] The brief at the linked path actually exists and is readable
- [ ] `attack_ids` match what's in the brief's ATT&CK block(s), not a paraphrase
- [ ] `source_status` matches the brief's `overall_source_status` exactly
- [ ] `recommendations` doesn't introduce guidance beyond what the brief itself states
- [ ] `updated` reflects the most recent edit to this row, not the brief's original filing date if they differ

---

## 6. Version history

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-30 | Initial seed — empty index, column spec and rules only. No briefs filed yet. |
| 1.1 | 2026-06-30 | First row — `INTEL-ransomware-backup-targeting-2026-06`; OPSEC + `OPSEC-BACKUP-PATHS` wiring (`mmi-wire-mitigation-refs`). |
| 1.2 | 2026-07-01 | Second row — `INTEL-polymorphic-ransomware-delivery-2026-07`; MIXED status (VERIFIED MITRE/CA-primary headline, NEEDS VERIFY + FORECAST_LOW_CONFIDENCE quarantined internal) (`mmi-intel-brief-polymorphic-delivery`). |
| 1.3 | 2026-07-01 | First row amended � `INTEL-ransomware-backup-targeting-2026-06` normalized against CA localization pass; `source_status` VERIFIED ? MIXED; localization lane added (`mmi-intel-brief-ca-normalize-backup-targeting`). |
