# MMI War Room Scoring Matrix — Operator Tiers

> **SUPERSEDED** — use **`WAR_ROOM_SCORING_MATRIX_v2.md`** (Matt approved 2026-06-30). Kept for history only.

Date: 2026-06-30  
Authority: Matt (Super) — Canadian operator  
Status: **Superseded by v2** — do not use for scoring  
Lane: Security Intel / War Room V1.1  
Jurisdiction: **Canada-first** for legal/regulatory triggers  
Source: Adapted from `lanes/RESEARCH_purple_team_war_room_matrix_2026-06.md` (enterprise matrix localized for MMI)

---

## Purpose

Score **Matt's MMI operator readiness** during:

- A real or simulated incident (purple team Phase 6 — Impact)
- A war room drill (pipe + backup + IR docs + decision log)
- A post-incident review (PIR)

This is **not** an enterprise SOC maturity model. There is no SIEM, EDR auto-block, or SOAR in MMI v1. Scoring measures what you **actually have**: local war room CLI, project brain, cold backup, Canadian IR artifacts, and human decision discipline.

**Advisory only.** MMI does not auto-isolate, auto-report to CAFC/OPC, or auto-score from `war_room.py`.

---

## Two scoring axes

| Axis | What it measures |
|------|------------------|
| **A. Technical detection & visibility** | How fast you **know** something is wrong using tools you own |
| **B. War room leadership & decisions** | How fast you **organize**, **document**, and **act** without chaos |

Record both axes. **Overall tier = lower of the two** (weakest link).

---

## Tier definitions (operator)

### Tier 4 — Optimized

**You are oriented, backed up, and legally clock-aware within minutes.**

| Axis | Criteria (all true) |
|------|---------------------|
| **A. Technical** | Suspicion or impact confirmed **<15 min** via at least two signals (e.g. user report + failed backup verify, phish click + anomalous process, war room BLOCKED + git anomaly). Pipe status known. Last B2 push **<24h** or verified restore path documented. |
| **B. Leadership** | `mmi/war_room.py --watch` running on monitor 2. Incident Commander role assigned (**Matt** or named delegate). Decision log started **<15 min**. Canadian legal triggers assessed (PIPEDA / Law 25 if applicable). Stakeholder comms plan selected — not ad-hoc panic. |

**MMI commands in play:**
```bash
python mmi/war_room.py --watch --seconds 30
python scripts/mmi_cold_backup.py --backup-and-push   # if integrity still good
```

**Canadian legal (advisory):** If real risk of significant harm to personal information is **confirmed**, PIPEDA notification clock and Quebec Law 25 obligations (if QC data/subjects) are **flagged in decision log** — not guessed from US playbooks.

---

### Tier 3 — Proficient

**You are functional but not fully rehearsed.**

| Axis | Criteria |
|------|----------|
| **A. Technical** | Issue known **<60 min**. War room pipe **LOADED** or DRY acknowledged. Backup within **72h** or manifest exists. No evidence destruction (reckless `git clean`, mass delete without log). |
| **B. Leadership** | Active task or incident task seeded in `tasks.json`. Roles loosely assigned (Tech vs Compliance). Decision log started **<30 min**. Complexity break used once (assumptions challenged). |

**Typical gap vs Tier 4:** Backup stale, legal assessment delayed, monitor 2 not running watch mode.

---

### Tier 2 — Lagging

**You are reactive and under-instrumented.**

| Axis | Criteria |
|------|----------|
| **A. Technical** | Detection **>1 hour** or only at impact (locked files, account takeover, backup failure discovered late). Pipe **DRY** with no seeded incident task. Backup **>72h** or never verified. |
| **B. Leadership** | Tunnel vision on one symptom (e.g. only firewall, only email). No decision log. Executive/comms updates interrupt technical work. Canadian reporting obligations not yet assessed. |

**Recovery path:** Open war room, seed incident task, start decision log, run backup if safe.

---

### Tier 1 — Failed

**Collapse — no orienting surface.**

| Axis | Criteria |
|------|----------|
| **A. Technical** | No detection until external disclosure (bank, client, attacker note) or total loss. No backup to restore. Evidence destroyed (wiped disk, overwritten logs without forensic copy). |
| **B. Leadership** | No Commander. Unauthorized write-actions during crisis. No chain of command. No decision log. |

**Post-failure minimum:** Preserve disks/images if possible, engage legal counsel, document timeline retroactively, run `mmi_cold_backup.py` only if it does not overwrite evidence.

---

## Scoring worksheet

Copy per incident or drill.

```markdown
## MMI War Room Score — [DATE] [EXERCISE/REAL]

**Incident ID:**  
**Commander:**  
**Tech lead:**  
**Compliance lead:**  
**Jurisdiction:** Canada [ ]  Quebec (Law 25) [ ]  Other: ___

### Axis A — Technical detection & visibility
| # | Check | Y/N | Notes |
|---|-------|-----|-------|
| A1 | Time to suspect/confirm (min): ___ | | |
| A2 | war_room.py or command_center consulted | | |
| A3 | Pipe status: LOADED / DRY / BLOCKED | | |
| A4 | Last B2 push age (hours): ___ | | |
| A5 | Second independent signal (not single alert) | | |
| A6 | Evidence preservation (no reckless deletes) | | |

**Axis A tier (1–4):** ___

### Axis B — War room leadership & decisions
| # | Check | Y/N | Notes |
|---|-------|-----|-------|
| B1 | Commander named <15 min | | |
| B2 | Decision log started (path): ___ | | |
| B3 | Roles: Tech / Compliance / Comms assigned | | |
| B4 | Canadian legal triggers assessed (PIPEDA/Law 25) | | |
| B5 | Complexity break used | | |
| B6 | Stakeholder comms plan (not ad-hoc) | | |

**Axis B tier (1–4):** ___

### Overall
**Overall tier (min of A, B):** ___

### ATT&CK (if known)
Primary technique(s): ___  
Purple phase reached: 1–6 ___

### Actions before close
- [ ] Backup push (if safe): `python scripts/mmi_cold_backup.py --backup-and-push`
- [ ] Complete task: `python scripts/complete_task.py ...`
- [ ] PIR scheduled within 72h
```

---

## Signal catalog — what counts as "detection" on MMI stack

MMI does not have SIEM. Valid **operator signals**:

| Signal | Source |
|--------|--------|
| Pipe BLOCKED / non-MMI task | `mmi/war_room.py` |
| Backup push FAIL | `MMI_BACKUP_PUSH_LOG.json` |
| Phish / credential concern | Human report |
| Ransomware / encryption | User-visible impact |
| Git corruption / missing objects | `git status` / fsck |
| Unauthorized cloud/API use | Provider alerts (B2, email MFA) |
| Purple team inject | Exercise brief (documented) |

**Not valid as sole signal:** gut feeling without artifact; unverified vendor stat; single antivirus pop-up without triage.

---

## Purple team Phase 6 mapping

When exercise reaches **T1486 Data Encrypted for Impact** (simulated):

| Step | Tier target | Action |
|------|-------------|--------|
| 1 | B ≥3 | Start `war_room.py --watch` |
| 2 | B ≥3 | Open IR template + commander checklist (when filed) |
| 3 | A ≥3 | Confirm backup age; run push if environment trusted |
| 4 | B ≥4 | Decision log + PIPEDA/Law 25 assessment block |
| 5 | A ≥4 | Second signal documented (e.g. test dir lock + war room BLOCKED) |

Enterprise phases 1–5 (EDR, SIEM, AD) score separately under `[Enterprise Reference]` if Matt runs them in a lab — **not** required for MMI operator tier.

---

## Canadian regulatory triggers (advisory checklist)

Use with Compliance lead role. **Not legal advice** — confirm with counsel.

| Trigger | Action flag in decision log |
|---------|----------------------------|
| Real risk of significant harm (PIPEDA) | `[REQ: PIPEDA assessment]` → OPC breach record if required |
| Quebec residents / QC org (Law 25) | `[REQ: Law 25 notification timeline]` |
| Criminal conduct (extortion, unauthorized access) | `[REQ: CAFC / local police consideration]` |
| CCCS significant incident (federal context) | `[REQ: CCCS reporting assessment]` |

Link future: `intel/LOCAL_INCIDENT_PLAYBOOK.md`, `intel/INCIDENT_DECISION_GATE.md`.

---

## Tier improvement targets (MMI-only)

| From → To | Highest-leverage moves |
|-----------|------------------------|
| 1 → 2 | Run war room watch; start decision log; stop destructive writes |
| 2 → 3 | Seed incident task; backup push; assign Compliance lead |
| 3 → 4 | Daily backup habit; rehearse IR template quarterly; monitor 2 always on during incidents |
| Any → maintain 4 | Purple drill Phase 6 quarterly; verify B2 restore annually |

---

## Relationship to enterprise matrix

| Enterprise (research) | MMI operator (this doc) |
|----------------------|-------------------------|
| SIEM <5 min | Multi-signal confirm <15 min |
| EDR auto-block | Human containment + backup |
| SOAR isolation | Document only — out of MMI scope |
| Executive dashboard auto-update | `war_room.py --watch` |
| AD / LSASS / ADCS | `[Enterprise Reference]` — lab only |

---

## Hard stops

- MMI war room CLI does **not** compute or display live tier — this is a **human worksheet**
- No automated CAFC/OPC filing from MMI
- No hack-back (Canada Criminal Code s.342.1)
- No unverified stats in PIR — use `MMI_RESEARCH_RIGOR_PROTOCOL.md`
- Tier 4 does not require enterprise EDR/SIEM

---

## References

- `mmi/war_room.py` — read-only orient panel
- `architecture/MMI_WAR_ROOM_SPEC.md` — V1.1-PROTOTYPE
- `lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md` — Canada-first Truth Database
- `lanes/RESEARCH_purple_team_war_room_matrix_2026-06.md` — source research
- `status/MMI_CANADIAN_IR_FIT.md` — IR artifact map

---

## Version

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Next review | After first purple Phase 6 drill or real incident PIR |
