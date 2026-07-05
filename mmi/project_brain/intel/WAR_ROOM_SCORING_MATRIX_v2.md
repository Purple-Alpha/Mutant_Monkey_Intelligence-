# MMI War Room Scoring Matrix — Operator Tiers (v2)

Date: 2026-06-30
Authority: Matt (Super) — Canadian operator
Status: **ACTIVE** — Matt approved 2026-06-30. Supersedes v1 (`WAR_ROOM_SCORING_MATRIX.md`). Self-assessment worksheet; **not** live CLI scoring.
Lane: Security Intel / War Room V1.1
Jurisdiction: **Canada-first** for all legal/regulatory triggers
Source: v1 (`WAR_ROOM_SCORING_MATRIX.md`) revised against `Research Review — WAR_ROOM_SCORING_MATRIX 2026-06 (ChatGPT)` — sign-off **PASS WITH REVISIONS**. Every Critical/High Crucible Finding from that review is addressed below; see §11 Crucible Findings Resolution Log for the line-by-line map.
Rigor: Built under `lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md` — Canada-first Truth Database. No new statistics introduced in this design pass; legal phrasing below carries the same confidence/jurisdiction labels the ChatGPT review assigned (PIPEDA s.10.1–10.3, OPC guidance, Quebec Law 25, CCCS guidance, CAFC/RCMP, Criminal Code s.342.1 — all 9–10/10 confidence, Canadian primary or statutory).

---

## 1. Purpose & scope

Score **Matt's MMI operator readiness** during:

- A real or simulated incident (purple team Phase 6 — Impact)
- A war room drill (pipe + backup + IR docs + decision log)
- A post-incident review (PIR)

**This is not an enterprise SOC maturity model.** There is no SIEM, EDR auto-block, or SOAR in MMI v1. Scoring measures what Matt **actually has**: local war room CLI, project brain, cold backup, Canadian IR artifacts, and human decision discipline.

**Non-goals (explicit):**

- No SOAR, no automated containment, no endpoint swarm, no live telemetry requirement
- No auto-isolate, no auto-report to CAFC/OPC/CCCS, no auto-score from `war_room.py`
- No comparison against enterprise SIEM/EDR detection speed as a pass/fail bar (see §8)

**Advisory only.** Every containment, reporting, and notification action in this matrix requires a human decision. MMI does not act on Matt's behalf.

---

## 2. Authority & source hierarchy

Canada-first per `lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md` §0:

1. Canadian primary/statutory — CCCS, PIPEDA (Department of Justice), OPC, Quebec Law 25 (Légis Québec), CAFC/RCMP, Criminal Code
2. Canadian government guidance — CCCS Baseline Controls for SMOs, CCCS IR planning (ITSAP.40.003), CCCS Ransomware Playbook, Statistics Canada CSCSC
3. Global frameworks — NIST CSF 2.0, NIST SP 800-61r3, ISO/IEC 27035-1, MITRE ATT&CK/D3FEND, VERIS — vocabulary and structure only, tagged `[Global Data — Requires Localization]`, never presented as Canadian operating truth
4. Vendor survey data (CIRA, etc.) — trend context only, not law or government guidance

Any internal MMI drill threshold (time targets, signal counts) is explicitly **not** ranked against this hierarchy — it is an MMI-only operating target. See §4 for the distinction.

---

## 3. Two scoring axes

| Axis | What it measures |
|------|------------------|
| **A. Technical detection & visibility** | How Matt **knows** something is wrong, using tools he actually owns |
| **B. War room leadership & decisions** | How Matt **organizes**, **documents**, and **acts** without chaos |

Record both axes per incident or drill. **Overall tier = lower of the two (weakest link)** — a strong leadership score never masks missing detection evidence, and vice versa.

```
overall_tier = min(axis_a_detection_tier, axis_b_leadership_tier)
```

No averaging. If Matt wants a separate dashboard-style composite metric later, that is a v3 decision — not this matrix.

A `compensating_strengths` worksheet field (§7.3) records context (e.g. "Axis A was Tier 2 but evidence was preserved cleanly") without changing the gating score.

---

## 4. Two kinds of thresholds — do not confuse them

This is the single biggest correction from the ChatGPT review (Crucible: High). v1 stated exact thresholds (15 min, 60 min, 24h, 72h) without flagging which were internal targets vs. which implied external validation. v2 splits every threshold into one of two buckets:

| Bucket | Meaning | Example |
|--------|---------|---------|
| **MMI drill SLO** | An internal target Matt sets for himself, validated only by his own quarterly drills — not a Canadian legal or industry-validated standard | "Tier 4 target: two independent signals within 15 minutes" |
| **Canadian legal/regulatory trigger** | A real obligation tied to a Canadian statute or government guidance, with no fixed universal clock unless a specific law says so | "PIPEDA notification: as soon as feasible **after determining** real risk of significant harm — not a fixed 72h" |

Every tier table and worksheet field below is labeled with one of these tags. **Never read an MMI drill SLO as a legal deadline, and never assume a fixed Canadian legal clock that isn't in §6.**

---

## 5. Tier definitions (operator)

### Tier 4 — Optimized

**Matt is oriented, backed up, and legally clock-aware within his own drill targets.**

| Axis | Criteria (all true) |
|------|---------------------|
| **A. Technical** *(MMI drill SLO: target <15 min)* | Suspicion or impact confirmed via **two independent, non-derivative signals** from separate evidence families (see §6 for the precise definition — e.g. user report + failed backup verify, MFA push denial + war room BLOCKED, git anomaly + email forwarding-rule change). Pipe status known. Last B2 push <24h (internal backup-recency target) **or** a restore path tested within the last 90 days is documented. |
| **B. Leadership** *(MMI drill SLO: target <15 min)* | `mmi/war_room.py --watch` running on monitor 2. Incident Commander named (Matt or delegate). Decision log opened with first entry timestamped. Evidence ledger opened (§7.2). Canadian legal triage started — PIPEDA RROSH status set to at least `unknown` (not skipped) and Quebec Law 25 applicability checked if Quebec persons/data may be in scope. Comms blackout invoked (§7.5). Stakeholder comms plan selected, not ad-hoc. PIR stub opened same session. |

**MMI commands in play:**
```bash
python mmi/war_room.py --watch --seconds 30
python scripts/mmi_cold_backup.py --backup-and-push   # only if integrity is still good
```

**Canadian legal (advisory, not legal advice):** If Matt has determined a real risk of significant harm to personal information exists, the PIPEDA notification clock is "as soon as feasible after that determination" — flagged in the decision log, not assumed from a fixed-hour deadline. Quebec Law 25 (if Quebec persons/data implicated) requires prompt CAI/affected-person notification when there is a risk of serious injury — also assessed, not assumed.

---

### Tier 3 — Proficient

**Matt is functional but not fully rehearsed.**

| Axis | Criteria |
|------|----------|
| **A. Technical** *(MMI drill SLO: target <60 min)* | At least one high-confidence signal, or two medium-confidence signals, documented in the evidence ledger with source and timestamp. War room pipe **LOADED** or DRY acknowledged. Backup manifest exists and is <72h old (internal backup-recency target, not a legal deadline) **or** a restore-test status is logged from the last quarter. No evidence destruction (reckless `git clean`, mass delete without log). |
| **B. Leadership** | Active task or incident task seeded in `tasks.json`. Roles loosely assigned (Tech vs. Compliance). Decision log started within the drill/incident window. Complexity break used once (assumptions challenged). Restore path identified (not necessarily tested this quarter). |

**Typical gap vs. Tier 4:** Backup stale, legal triage delayed past the first session, monitor 2 not running watch mode, no restore test in 90 days.

---

### Tier 2 — Lagging

**Matt is reactive and under-instrumented.**

| Axis | Criteria |
|------|----------|
| **A. Technical** | Detection missed the 60-minute drill SLO, or detection only happened at visible impact (locked files, account takeover, backup failure discovered late). Pipe **DRY** with no seeded incident task. Backup >72h old or never verified. |
| **B. Leadership** | Tunnel vision on one symptom (e.g. only firewall, only email). No decision log. Canadian reporting obligations not yet assessed. |

**Recovery path:** Open war room, seed incident task, start decision log and evidence ledger, run backup if safe, begin PIPEDA/Law 25 triage even if the answer is currently `unknown`.

---

### Tier 1 — Failed

**Collapse — no orienting surface.**

| Axis | Criteria |
|------|----------|
| **A. Technical** | No detection until external disclosure (bank, client, attacker note) or total loss. No backup to restore. Evidence destroyed (wiped disk, overwritten logs, no forensic copy). |
| **B. Leadership** | No Commander. Unauthorized write-actions during the crisis. No chain of command. No decision log. |

**Post-failure minimum:** Preserve disks/images if possible, engage legal counsel, document the timeline retroactively, run `mmi_cold_backup.py` only if it will not overwrite evidence.

---

## 6. Signal independence — precise definition

The ChatGPT review flagged "two independent signals" as undefined in v1 (Crucible: High). v2 fixes this:

> **Two independent signals** means two non-derivative observations from **separate evidence families**. A copied alert, a forwarded email about the same event, or a second look at the same log line does **not** count as a second signal.

**Evidence families recognized by MMI:**

| Family | Examples |
|--------|----------|
| Host/filesystem | Ransom note, mass file-extension change, inaccessible files, unexpected file hash change |
| Backup/recovery | B2/rclone deletion or sync anomaly, failed restore test, `MMI_BACKUP_PUSH_LOG.json` FAIL entry |
| Identity | MFA push fatigue/denial, impossible/unfamiliar sign-in, new admin account or role change |
| Email/cloud identity | New inbox-forwarding rule, suspicious mailbox delegate, provider security alert |
| Local repo | Unauthorized `git` changes, file-hash baseline mismatch, suspicious shell history |
| WSL/host persistence | Suspicious WSL cron/systemd entry, unexpected scheduled task/service, unexpected listening port |
| Network | Unusual outbound connections (Resource Monitor / `netstat` / router log) |
| Legal/criminal | Evidence of unauthorized computer access in the Criminal Code s.342.1 sense (context tag only — not a legal conclusion) |
| External party/fraud | CAFC-style fraud indicator, newly registered phishing domain, vendor/client report |
| Human report | A person says "something looks wrong," with a specific observation attached |

A symptom on its own (CPU spike, fan noise, generic slowness) or an antivirus pop-up with no artifact is **not** strong enough to count as one of the two required signals at Tier 4 — it can support a Tier 3 single-signal case but should be logged as low-confidence.

---

## 7. War Room Worksheet (v2)

Copy this block per incident or drill. This **is** the evidence ledger, decision log, and PIR stub — no separate CLI tool computes this. See §10 for how to externalize sections into standalone template files if Matt wants per-incident folders later.

### 7.1 Incident header

```markdown
incident_id:
opened_at:
opened_by (Commander):
suspected_type:
affected_systems:
business_impact_status:
jurisdiction: Canada [ ]  Quebec — Law 25 in scope [ ]  Other: ___
```

### 7.2 Evidence ledger

```markdown
| timestamp | evidence_family | source | observation | confidence (1-10) | preserved_location | hash/screenshot/log_ref |
|-----------|------------------|--------|--------------|--------------------|---------------------|--------------------------|
|           |                  |        |              |                    |                     |                          |
```

Confidence follows `MMI_RESEARCH_RIGOR_PROTOCOL.md` §2 scale — this is an operator confidence call, not a statistical claim, and does not need a citation, but does need a source and timestamp or it is not admissible as one of the two required signals (§6).

### 7.3 Axis scoring

```markdown
### Axis A — Technical detection & visibility
| # | Check | Y/N | Notes |
|---|-------|-----|-------|
| A1 | Time to suspect/confirm (min): ___ — labeled MMI drill SLO, not external standard | | |
| A2 | war_room.py or command_center consulted | | |
| A3 | Pipe status: LOADED / DRY / BLOCKED | | |
| A4 | Last B2 push age (hours): ___ | | |
| A5 | Two independent signals logged in Evidence Ledger (§7.2), separate families | | |
| A6 | Evidence preservation confirmed (no reckless deletes) | | |
| A7 | Restore path tested within 90 days (Y/N, date if Y) | | |

**Axis A tier (1–4):** ___

### Axis B — War room leadership & decisions
| # | Check | Y/N | Notes |
|---|-------|-----|-------|
| B1 | Commander named | | |
| B2 | Decision log started (first entry timestamp): ___ | | |
| B3 | Roles: Tech / Compliance / Comms assigned | | |
| B4 | Comms blackout invoked (§7.5) | | |
| B5 | Complexity break used (assumptions challenged) | | |
| B6 | PIR stub opened same session (§7.6) | | |

**Axis B tier (1–4):** ___

**Overall tier (min of A, B):** ___
**compensating_strengths (notes only, does not change score):** ___
```

### 7.4 Regulatory/legal triage

Advisory only — not legal advice. Confirm with counsel before any external filing.

```markdown
personal_info_involved: yes / no / unknown
pipeda_rrosh_status: unknown / unlikely / likely / determined
  (PIPEDA notification to OPC + affected individuals is "as soon as feasible after
   determination" of real risk of significant harm — not a fixed 72h clock)
breach_record_required: yes / no / unknown   (default: unknown until assessed —
  PIPEDA requires a record of every breach of safeguards, RROSH or not)
qc_law25_in_scope: not applicable / assessment pending / risk of serious injury — notify CAI+individuals
cccs_report_considered: yes / no
criminal_fraud_branch: local police / CAFC-RCMP / not applicable
legal_context_tag: Criminal Code s.342.1 (unauthorized computer use) possible — yes / no / unknown
  (context flag only, not a legal conclusion)
```

### 7.5 Comms blackout checklist

```markdown
- [ ] No contact with attacker (no ransom negotiation, no reply to extortion message)
- [ ] No public posting (social media, status page) before Commander decision
- [ ] No vendor/client notification before Commander + Compliance lead sign-off
- [ ] Out-of-band contact method confirmed for internal team
```

### 7.6 Recovery

```markdown
last_known_good_backup:
restore_test_status: not tested / tested — date: ___ / failed — notes: ___
b2_rclone_evidence_ref:
credential_reset_required: yes / no
mfa_review_required: yes / no
```

### 7.7 PIR stub (opened day 0, not after memory fades)

```markdown
root_cause_hypothesis:
what_worked:
what_failed:
control_gaps:
evidence_gaps:
v2/v3_backlog_items:
pir_full_review_scheduled_for:
```

### 7.8 Actions before close

```markdown
- [ ] Backup push if safe: `python scripts/mmi_cold_backup.py --backup-and-push`
- [ ] Complete task: `python scripts/complete_task.py ...`
- [ ] Full PIR review scheduled (separate from the day-0 stub above)
- [ ] ATT&CK technique(s) noted, if known: ___
- [ ] Purple phase reached (1–6): ___
```

---

## 8. Signal catalog — Matt's actual stack

MMI does not have a SIEM. The catalog below assumes **Windows + WSL + local project brain + B2 cold backup + cloud identity/email** — not enterprise tooling. Priority reflects how strong the signal is on its own, not how common it is.

| Priority | Signal | Detection method | Evidence family |
|----------|--------|-------------------|------------------|
| P1 | Ransom note, mass file-extension changes, inaccessible files | Manual observation; recent-modified-files check | Host/filesystem |
| P1 | Backup deletion, failed restore, abnormal B2/rclone sync/delete volume | B2 console; rclone logs; `MMI_BACKUP_PUSH_LOG.json` | Backup/recovery |
| P1 | New inbox-forwarding rule or suspicious mailbox delegate | Email admin UI; mailbox rules export if available | Email/cloud identity |
| P1 | MFA push fatigue, repeated denied pushes, impossible/unfamiliar sign-in | Identity provider sign-in log; account security email | Identity |
| P1 | Unexpected admin login, new admin account, or role change | Cloud admin portal; Windows local users; GitHub org audit if used | Identity/admin |
| P1 | Unauthorized repo changes or suspicious scripts in MMI repo | `git status`, `git log`, file-hash baseline, shell history | Local repo |
| P1 | Suspicious scheduled task, startup item, or service | Windows Task Scheduler, Services | Host persistence |
| P1 | Evidence of unauthorized computer access | Event logs, account history | Legal/criminal (context tag only) |
| P2 | Windows Event ID clusters (failed logons, admin logons, service installs, scheduled-task creation) | Event Viewer / PowerShell queries — only if logging retained | Host logs |
| P2 | PowerShell script-block or suspicious command history | PowerShell history, event logs if enabled | Host execution |
| P2 | WSL suspicious cron/systemd entry, bash history, unexpected listening port | WSL shell history, `/etc/cron*`, process list, listening ports | WSL/Linux |
| P2 | Browser session/token anomalies | Account security page, password-manager alerts, new-device email | Identity/session |
| P2 | Newly registered domain in a phishing email | Email headers, registrar lookup | External/email |
| P2 | Unusual outbound network connections | Resource Monitor, `netstat`, router log if available | Network |
| P3 | Antivirus alert without an artifact | Windows Security history | Endpoint alert |
| P3 | User "something looks weird" report | Worksheet note | Human report |
| P3 | Generic CPU spike, fan noise, slowness | Task Manager | Host symptom — too weak alone, never counts as one of the two required Tier 4 signals |

**Not valid as a sole signal at any tier:** gut feeling with no artifact, unverified vendor stat, single antivirus pop-up without triage.

---

## 9. Canadian regulatory triggers — decision tree

Advisory only — not legal advice. Confirm with counsel. Branches are kept **separate** because the ChatGPT review flagged PIPEDA/OPC, CAFC/RCMP, and CCCS as commonly conflated (Crucible: High).

| Branch | Trigger | What starts the clock | Action |
|--------|---------|------------------------|--------|
| **Privacy — PIPEDA (federal)** | Breach of security safeguards involving personal information | Reasonable belief of real risk of significant harm (RROSH) | Report to OPC + notify individuals **as soon as feasible after determination** — not a fixed 72h. Record **every** breach of safeguards regardless of RROSH outcome. |
| **Privacy — Quebec Law 25** | Confidentiality incident involving personal information, Quebec persons/business context in scope | Risk of serious injury (sensitivity, consequences, likelihood of injurious use) | Prompt notification to CAI and affected persons. Only applies if Quebec data/subjects/business context is implicated — do not apply as a default federal rule. |
| **Cyber incident support — CCCS** | Unauthorized attempt to access/change/delete/block/shut down a system, network, or account, successful or not | Operator discretion — voluntary support channel, not a legal deadline | Consider reporting via CCCS incident-reporting channel. Emergency = local police, not CCCS. |
| **Ransomware-specific — CCCS Ransomware Playbook** | Ransomware discovered | Operator discretion | Report to local police, CAFC, and the Cyber Centre — not just CCCS alone. |
| **Criminal/fraud — CAFC/RCMP** | Experienced or witnessed cybercrime or fraud | Operator discretion; local police investigate if Matt is a victim | Report via CAFC/RCMP national reporting channel and/or local police. This is **not** a substitute for the PIPEDA privacy-regulator branch — file both if both apply. |
| **Legal context only — Criminal Code s.342.1** | Facts suggest unauthorized computer use/access/interception | N/A — context tag, not a self-determined legal conclusion | Flag `legal_context_tag` in the worksheet (§7.4). Legal interpretation requires counsel. |

---

## 10. Implementation notes for Matt (new artifacts, if any)

**Bottom line: v2 requires no new files and no Codex work.** The expanded worksheet (evidence ledger, decision log, regulatory triage, PIR stub) is embedded as one markdown block in §7 — consistent with the "advisory-only, local-first, human worksheet, no live CLI auto-score" rule. Copy §7 per incident; that's the whole workflow.

**Optional, only if Matt wants per-incident folders later (not required for v2 sign-off):**

1. Create `intel/templates/WAR_ROOM_WORKSHEET_TEMPLATE.md` — copy §7 in full as a blank starting template.
2. If incidents start running multi-day and the single-block worksheet gets unwieldy, split out:
   - `intel/templates/DECISION_LOG_TEMPLATE.md` (from §7.3's decision-log fields)
   - `intel/templates/EVIDENCE_LEDGER_TEMPLATE.md` (from §7.2)
   - `intel/templates/PIR_STUB_TEMPLATE.md` (from §7.7)
   This is a pure copy/paste/save operation — no scripting, no Codex task needed.
3. **Restore drill cadence** — this is a calendar/task action, not a doc. Add a recurring entry (personal calendar or a seeded `tasks.json` task) for a quarterly B2 restore-test, so Axis A's "restore path tested within 90 days" criterion (§5, §7.3 A7) has something to point to. If Matt wants this seeded as an MMI task, that's a candidate for `status/MMI_NEXT_SAFE_TASK.md` — flag to PM, not built here.
4. **Future, not in v2 scope:** when Matt authorizes the V1.1 Codex CLI update already planned in `architecture/MMI_WAR_ROOM_SPEC.md` (§"V1.1 Codex scope"), `war_room.py` could gain an `intel_status()` row showing last restore-drill date and last verification-lane sign-off. That is explicitly deferred — this matrix does not direct Codex to build it now.

---

## 11. Crucible Findings Resolution Log

Every Critical/High finding from the ChatGPT review is fixed below. Medium findings are also addressed for completeness.

| # | Crucible finding | Severity | Resolved in |
|---|-------------------|----------|--------------|
| 1 | Exact thresholds (15/60/72h/24h) stated without primary validation | High | §4 splits every threshold into "MMI drill SLO" vs. "Canadian legal trigger"; all tier tables (§5) re-labeled |
| 2 | PIPEDA "72-hour" language is wrong for general PIPEDA | **Critical** | §5 Tier 4, §7.4, §9 — replaced with "as soon as feasible after determination of RROSH" everywhere; no fixed-hour PIPEDA clock anywhere in this doc |
| 3 | CAFC/CCCS/OPC may be conflated | High | §9 splits into five separate branches (PIPEDA, Law 25, CCCS general, CCCS ransomware, CAFC/RCMP) with explicit "not a substitute for" language |
| 4 | Enterprise SOC comparison creates false inferiority | Medium | §8 reframed around Matt's actual stack only; §1 non-goals explicitly excludes SIEM/EDR speed as a pass/fail bar; old "Relationship to enterprise matrix" table from v1 removed |
| 5 | "Two independent signals" undefined | High | §6 defines evidence families and the non-derivative rule precisely |
| 6 | Criteria may reward security theater (opening a "war room" without evidence preservation) | High | §7.2 evidence ledger requires timestamp + source + confidence + preserved_location for every entry; §7.3 A5/A6 gate on it |
| 7 | Missing WSL/local-repo signals | High | §8 adds WSL cron/systemd/listening-port row, local-repo git/hash/shell-history row |
| 8 | Missing cloud identity/email signals | High | §8 adds MFA push-fatigue, forwarding-rule, admin-role-change rows (P1 priority) |
| 9 | Possible US-centric legal framing (CFAA-style) | High | §7.4, §9 use Criminal Code s.342.1 as a context tag only; no CFAA reference anywhere in v2 |
| 10 | Possible conflict with advisory-only doctrine | **Critical** | §1 non-goals + every regulatory action in §9/§7.4 marked "advisory only," human decision required |
| 11 | Possible conflict with local-first doctrine | **Critical** | §1 non-goals explicitly excludes live telemetry requirement; §5 criteria reference only tools Matt owns |
| 12 | Missing restore-drill criterion | High | §5 Tier 3/4 add restore-path/restore-test criteria; §7.3 A7; §7.6; §10 step 3 (quarterly drill cadence) |
| 13 | Missing comms-blackout criterion | Medium | §7.5 dedicated comms blackout checklist; §5 Tier 4 leadership requires it |
| 14 | Missing PIR linkage (opened after memory fades) | Medium | §7.7 PIR stub opened same session, day 0 — separate from the full PIR review in §7.8 |

---

## 12. Purple Team Phase 6 drill (quarterly, 15–30 min)

Local-only, harmless artifacts. Tests **detect → decide → document → restore** — never auto-contain, matching the advisory-only doctrine (§1, §10 finding #10/#11).

**Scenario:** simulated ransomware precursor on local workstation + backup anomaly (maps to MITRE T1486, simulated only).

1. Start timer.
2. Create a harmless test folder; rename a few files to `.locked-simulated`.
3. Drop a fake ransom note: `README_RECOVER_SIMULATION.txt`.
4. Add one fake identity-alert note: "MFA push denied at 02:14 from unknown device."
5. Add one fake backup-anomaly note: "rclone dry-run shows unexpected delete candidate."
6. Open the §7 worksheet; log the first signal in the evidence ledger (§7.2).
7. Capture the second independent signal from a different evidence family (§6) — e.g. host/filesystem + identity, or host/filesystem + backup.
8. Score Axis A (§7.3).
9. Name the Commander; start the decision log.
10. Invoke the comms blackout checklist (§7.5) — no attacker contact, no ransom discussion, no public posting.
11. Check the last-known-good backup manifest (§7.6).
12. Run no destructive commands.
13. Complete regulatory triage fields (§7.4) as `unknown` / `not determined` — that's a valid drill outcome, not a failure, as long as the fields are touched.
14. Open the PIR stub (§7.7) with three gaps noted.
15. Stop timer; record elapsed time as a **local drill metric**, not external truth (§4).

**Pass condition for a Tier 4 drill:** two independent signals documented, owner named, regulatory triage fields touched (even if `unknown`), restore path identified, comms blackout invoked, and PIR stub created — all inside the drill window.

| Step | Tier target | MMI command |
|------|-------------|--------------|
| 1 | B ≥3 | Start `war_room.py --watch` |
| 2 | A ≥3 | Confirm backup age; run push if environment trusted |
| 3 | B ≥4 | Decision log + regulatory triage block touched |
| 4 | A ≥4 | Second independent signal documented |
| 5 | B ≥4 | PIR stub opened |

---

## 13. Tier improvement targets (MMI-only)

| From → To | Highest-leverage moves |
|-----------|------------------------|
| 1 → 2 | Run war room watch; start decision log; stop destructive writes |
| 2 → 3 | Seed incident task; backup push; assign Compliance lead; touch regulatory triage fields even if `unknown` |
| 3 → 4 | Daily backup habit; rehearse worksheet quarterly; verify B2 restore within 90 days; monitor 2 always on during incidents |
| Any → maintain 4 | Purple drill Phase 6 quarterly (§12); verify B2 restore at least quarterly; re-run regulatory triage on any new fact |

---

## 14. Comparison frame — what this matrix is and isn't

> MMI War Room is not an enterprise SOC. It is a local-first operator decision worksheet that helps a Canadian solo-operator preserve evidence, classify severity, open the right reporting branches, and avoid panic decisions during ransomware, account compromise, fraud, or data-exposure events.

| Comparison frame | Usefulness |
|--------------------|------------|
| Solo-operator / micro-business readiness | Best fit — measures whether Matt can detect, decide, document, and recover without enterprise tooling |
| CCCS SMB baseline (80/20 practicality model) | Best Canadian anchor for what "good enough" looks like at this scale |
| Canadian incident-reporting readiness | Strong fit — measures whether legal/reporting branches get opened, not skipped |
| Enterprise SOC maturity (SIEM/EDR/SOAR speed) | Explicitly out of scope for v1/v2 — not a scoring axis here |

---

## 15. Hard stops (unchanged from v1, reaffirmed)

- MMI war room CLI does **not** compute or display a live tier — this remains a **human worksheet**
- No automated CAFC/OPC/CCCS filing from MMI
- No hack-back (Canada Criminal Code s.342.1)
- No unverified stats in PIR or this matrix — `MMI_RESEARCH_RIGOR_PROTOCOL.md` applies
- Tier 4 does not require enterprise EDR/SIEM
- Every regulatory/legal action is advisory only and requires Matt's (or counsel's) decision — MMI does not file, notify, or contain on Matt's behalf

---

## 16. References

- `mmi/war_room.py` — read-only orient panel
- `mmi/project_brain/architecture/MMI_WAR_ROOM_SPEC.md` — V1.1-PROTOTYPE
- `mmi/project_brain/lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md` — Canada-first Truth Database
- `mmi/project_brain/lanes/RESEARCH_purple_team_war_room_matrix_2026-06.md` — source research (pre-Canada-first; localization applied here)
- `mmi/project_brain/status/MMI_CANADIAN_IR_FIT.md` — IR artifact map
- `Research Review — WAR_ROOM_SCORING_MATRIX 2026-06 (ChatGPT)` — Crucible review driving this v2 pass; PASS WITH REVISIONS — filed at `lanes/RESEARCH_SCORING_MATRIX_REVIEW_2026-06.md`

---

## 17. Version history

| Version | Date | Change | Driven by |
|---------|------|--------|-----------|
| 1.0 | 2026-06-30 | Initial operator tier matrix shipped alongside `war_room.py` v1 | v1 design |
| **2.0** | 2026-06-30 | Full v2 crucible revisions — see §11 | ChatGPT + Claude |
| **2.0 drill** | 2026-06-30 | First Phase 6 quarterly drill **PASS Tier 4** — `intel/drills/DRILL_2026-06-30_phase6_sim/DRILL_WORKSHEET_2026-06-30.md` | Matt — run drill |

**Next review:** After first purple Phase 6 drill run against this v2 worksheet, or after Matt's sign-off — whichever comes first. **Pending Matt review** — v2 sits alongside v1 until Matt approves replacement.
