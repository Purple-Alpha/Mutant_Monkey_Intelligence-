# MMI Operator OpSec Checklist

Date: 2026-06-30
Authority: Matt (Super) — Canadian operator
Status: **Seeded — first fill pending.** All items below default to `NOT_STARTED` until Matt sets a real `last_done` date.
Lane: Security Intel / Design
Task: `mmi-operator-opsec-checklist`
Sources: `architecture/MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md` (Operator OpSec Checklist Structure — exact column spec, seed categories), `intel/WAR_ROOM_SCORING_MATRIX_v2.md` (backup-recency and restore-test criteria this checklist feeds), `lanes/RESEARCH_VERIFICATION_2026-06.md` (VERIFIED claims used in `why` framing — no `NEEDS VERIFY` stat used as justification)

---

## 0. Purpose

A local, state-tracked checklist for Matt's Mini PC and accounts. This is a human-run control list, not automation — nothing here executes, scans, or remediates on its own. Per `MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md`, this is MVP Deliverable #4: MFA, phish discipline, backup cadence, restore drill — actionable, state-tracked, local.

**Hard rule:** a control marked `DONE` with no real `last_done` date and no real `verify_method` evidence is an assumption, not a control. The restore drill (§4) exists specifically because an unverified backup is the most common false sense of security in a solo-operator setup.

---

## 1. Column spec

Per `MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md` Operator OpSec Checklist Structure:

| Field | Content |
|---|---|
| `item_id` | `OPSEC-<n>` |
| `control` | Plain description of the control |
| `category` | `MFA`, `PHISH`, `BACKUP`, `RESTORE`, `DISCIPLINE` |
| `why` | Which ATT&CK techniques this blunts, or which war room criterion it feeds |
| `cadence` | `one-time`, `daily`, `weekly`, `monthly`, `quarterly` |
| `state` | `NOT_STARTED`, `IN_PROGRESS`, `DONE`, `OVERDUE` |
| `last_done` | Date — leave blank, never guessed, until actually done |
| `verify_method` | How Matt confirms it's real, not assumed |

`why` claims are framed using only `VERIFIED` material from `lanes/RESEARCH_VERIFICATION_2026-06.md` §7, or direct references to ATT&CK technique IDs / `WAR_ROOM_SCORING_MATRIX_v2.md` criteria — no `NEEDS VERIFY` percentage is used to justify an item.

---

## 2. Category: MFA

MFA materially reduces account-compromise risk (`RESEARCH_VERIFICATION_2026-06.md` §7 — Microsoft-backed research, >99% reduction in large commercial datasets; phishing-resistant MFA preferred where available). Targets accounts that gate everything else.

| `item_id` | `control` | `category` | `why` | `cadence` | `state` | `last_done` | `verify_method` |
|---|---|---|---|---|---|---|---|
| OPSEC-1 | MFA enabled on primary email account(s) | MFA | Email is the root recovery path for most other accounts; blunts T1566.002 / T1204.001 follow-on account takeover | one-time (re-check quarterly) | NOT_STARTED | | Log into account security settings, screenshot or note MFA method shown as active |
| OPSEC-2 | MFA enabled on admin accounts (hosting, domain registrar, Supabase/cloud admin) | MFA | Admin account compromise is the highest-impact single point of failure for MMI infrastructure | one-time (re-check quarterly) | NOT_STARTED | | Same as OPSEC-1, per account |
| OPSEC-3 | MFA enabled on backup/recovery accounts (B2, any cold-backup provider login) | MFA | A compromised backup account lets an attacker delete the recovery path itself — directly feeds `WAR_ROOM_SCORING_MATRIX_v2.md` backup-recency criteria | one-time (re-check quarterly) | DONE | 2026-06-30 | Operator confirmed 2FA enabled on Backblaze/B2 account (2026-06-30); MFA method not stored in repo per hygiene |

---

## 3. Category: PHISH

**Human gate authority:** `intel/drills/OPSEC_HUMAN_GATE_DRILL_2026-06-30.md` — documents vendor/email-platform defense baseline (Microsoft Defender, Google Workspace, optional SEG) vs what those controls **cannot** prove (business truth, vendor intent, compromised mailbox). Matt's gate covers the gap for **action-bearing vendor email**; platform hygiene ≠ authorization to act.

| `item_id` | `control` | `category` | `why` | `cadence` | `state` | `last_done` | `verify_method` |
|---|---|---|---|---|---|---|---|
| OPSEC-4 | Link-hover, sender, Reply-To, and domain check before clicking any link in unexpected email — pause on new/unusual/urgent/payment/login/admin/link-heavy mail per human-gate drill §4.1 | PHISH | Blunts T1566.002 and pre-T1204.001; platform Safe Links/Sandbox do not prove link safety at click (`OPSEC_HUMAN_GATE_DRILL_2026-06-30.md` §3) | daily (habit) | NOT_STARTED | | Worksheet §5: self-attestation date + one weekly spot-check note (no PII). Habit defined in drill §4.2–§4.4 |
| OPSEC-5 | Known-good out-of-band confirmation before any payment, banking, wire, or credential-change action prompted by email — never use contact details from the suspicious message | PHISH | Business-truth layer; SPF/DMARC/BEC filters cannot prove vendor intent or uncompromised mailbox (`OPSEC_HUMAN_GATE_DRILL_2026-06-30.md` §3) | one-time (habit, re-affirm quarterly) | NOT_STARTED | | Worksheet §5: rule acknowledged + decision-log entry when invoked (real preferred; drill dry-run in §6 is worksheet evidence only, insufficient alone for DONE) |

---

## 4. Category: BACKUP

Backup repositories are routinely targeted in ransomware incidents (`RESEARCH_VERIFICATION_2026-06.md` §7 — Veeam 96% / Sophos 94%, both `[Global Data — Requires Localization]`, Canadian cross-reference `Insufficient Data` per `MMI_RESEARCH_RIGOR_PROTOCOL.md` §7). Cadence and recency feed directly into `WAR_ROOM_SCORING_MATRIX_v2.md` Tier criteria.

| `item_id` | `control` | `category` | `why` | `cadence` | `state` | `last_done` | `verify_method` |
|---|---|---|---|---|---|---|---|
| OPSEC-6 | Cold backup pushed to B2 (or equivalent offline/immutable copy) on a defined schedule | BACKUP | Blunts T1486 (Data Encrypted for Impact) by ensuring an isolated copy exists outside the attack surface; feeds `WAR_ROOM_SCORING_MATRIX_v2.md` "B2 push <24h" Tier 4 criterion | daily (or per Matt's defined schedule) | DONE | 2026-06-30 | `MMI_BACKUP_PUSH_LOG.json` — `mmi_backup_20260629_205505.tar.gz` PASS end-of-night close (135444 bytes) |
| OPSEC-7 | Backup integrity check — confirm the pushed backup is readable, not just present | BACKUP | A backup that exists but won't open is not a control; this is the check between "pushed" and "usable" | weekly | DONE | 2026-06-30 | `tar -tzf` spot-check on `mmi_backup_20260629_204836.tar.gz` — `tasks.json` + `mmi/war_room.py` listed; sha256 matches push log (`b5524ee9...`) |

---

## 5. Category: RESTORE

The highest-value item in this checklist. A backup nobody has restored is an assumption (`MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md` — "the restore drill is the highest-value item"). This is the same drill referenced as already executed once in `mmi-restore-drill-quarterly` and logged against `WAR_ROOM_SCORING_MATRIX_v2.md` Axis A.

| `item_id` | `control` | `category` | `why` | `cadence` | `state` | `last_done` | `verify_method` |
|---|---|---|---|---|---|---|---|
| OPSEC-8 | Full restore drill — actually restore a backup set and confirm the restored files open and are intact | RESTORE | Directly satisfies `WAR_ROOM_SCORING_MATRIX_v2.md` Tier 3/4 "restore path tested within the last 90 days" criterion; without this, backup cadence (OPSEC-6) is unverified | quarterly | DONE | 2026-06-30 | Operator drill `intel/drills/DRILL_2026-06-30_opsec8_quarterly/DRILL_WORKSHEET_2026-06-30.md` — referenced `MMI_RESTORE_CHECK_WAR_ROOM_PROOF_2026-06.md` (restore-check PASS); no new push this drill |

---

## 6. Category: DISCIPLINE

Ties to the war room leadership axis (`WAR_ROOM_SCORING_MATRIX_v2.md` §3 Axis B) rather than a single ATT&CK technique — these are the human habits that make the rest of this checklist trustworthy instead of assumed.

| `item_id` | `control` | `category` | `why` | `cadence` | `state` | `last_done` | `verify_method` |
|---|---|---|---|---|---|---|---|
| OPSEC-9 | Open a decision log entry at the first moment of suspicion, before investigating further — record platform banner if seen, but do not treat banner as business authorization | DISCIPLINE | Feeds `WAR_ROOM_SCORING_MATRIX_v2.md` Axis B Tier 4; separates platform hygiene from business truth (`OPSEC_HUMAN_GATE_DRILL_2026-06-30.md` §6 template) | one-time (habit, re-affirm quarterly) | NOT_STARTED | | Worksheet §5–§6: template + dry-run completed for worksheet phase; DONE requires real incident or quarterly drill entry with timestamp before further investigation |
| OPSEC-10 | Quarterly review of this entire checklist — confirm no item's `state` is stale or assumed | DISCIPLINE | Prevents this checklist itself from becoming a zombie artifact; matches the quarterly cadence of the Phase 6 purple team drill in `WAR_ROOM_SCORING_MATRIX_v2.md` §12 | quarterly | NOT_STARTED | | Walk every row, update `last_done`/`state` honestly, log the review date here in §8 version history notes if anything changed |

---

## 7. Hard stops (reaffirmed)

- This checklist is human-run. No item here triggers automated remediation, blocking, or containment (`MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md` Out of Scope V1).
- `state: DONE` requires a real `last_done` date and a real `verify_method` result — never set `DONE` to make the list look complete.
- Local-first: this file lives in `mmi/project_brain/opsec/`. No hosted DB, no live dashboard, no NorthStar bridge.
- `why` framing never upgrades a `NEEDS VERIFY` stat to justify a control — see OPSEC-5's BEC note as the pattern to follow for any future item.
- This checklist informs Matt. It does not file a report, notify a regulator, or contact a third party — those decisions stay in `WAR_ROOM_SCORING_MATRIX_v2.md` §7.4/§9 regulatory triage, not here.

---

## 8. Acceptance checklist (run before treating an item as real)

- [ ] Every item has `item_id`, `category` from the five seed categories, and a `cadence` from the enum
- [ ] `why` cites either a specific ATT&CK ID, a `WAR_ROOM_SCORING_MATRIX_v2.md` criterion, or a `VERIFIED` claim — never an unsourced number
- [ ] `verify_method` describes a concrete check, not "trust it's done"
- [ ] Restore drill (OPSEC-8) is present and distinct from backup cadence (OPSEC-6/7) — these are never merged into one item
- [ ] No automated action implied by any `control` description

---

## 9. Version history

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-30 | Initial seed — 10 items across MFA, PHISH, BACKUP, RESTORE, DISCIPLINE. All `NOT_STARTED`. No real `last_done` dates set yet — pending Matt's first fill pass. |
| 1.4 | 2026-06-30 | OPSEC-7 DONE — archive integrity spot-check (`mmi-opsec-7-backup-integrity-check`); end-of-night close |
| 1.5 | 2026-06-30 | Human-gate worksheet filed (`mmi-opsec-human-gate-tightening` worksheet phase) — vendor/email defense baseline vs business-truth gap; OPSEC-4/5/9 completion criteria updated; items remain NOT_STARTED pending Matt habit evidence (`intel/drills/OPSEC_HUMAN_GATE_DRILL_2026-06-30.md`) |
| 1.6 | 2026-06-30 | Task closed PASS WITH REVISIONS — worksheet + criteria complete; OPSEC-4/5/9 **known operator-risk** (NOT_STARTED, no fabricated evidence). Habit proof deferred to Matt when ready; update checklist rows only when real evidence exists |
| 1.7 | 2026-06-30 | Worksheet §8 addendum — unsourced Canadian SMB email summary quarantined (RESEARCH INPUT ONLY); CASL/PIPEDA narrow wording; checklist states unchanged |
| 1.8 | 2026-06-30 | Task closed PASS WITH REVISIONS (`mmi-opsec-human-gate-tightening`) — task closed ≠ OPSEC proven; OPSEC-4/5/9 remain NOT_STARTED known operator-risk |
