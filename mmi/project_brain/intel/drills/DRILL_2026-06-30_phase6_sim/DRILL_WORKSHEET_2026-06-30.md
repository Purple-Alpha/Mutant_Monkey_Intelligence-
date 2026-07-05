# MMI War Room Score — 2026-06-30 PHASE6 SIMULATION

**Drill type:** Purple Team Phase 6 (MITRE T1486 simulated)  
**Authority:** `intel/WAR_ROOM_SCORING_MATRIX_v2.md` §12  
**Elapsed (setup + worksheet):** ~8 min (local drill metric — not external standard)  
**Result:** **TIER 4 DRILL PASS** (worksheet criteria met)

---

## 7.1 Incident header

```markdown
incident_id: DRILL-2026-06-30-PHASE6
opened_at: 2026-06-30T (operator local)
opened_by (Commander): Matt
suspected_type: Simulated ransomware precursor + identity + backup anomaly (drill)
affected_systems: mmi/project_brain/intel/drills/DRILL_2026-06-30_phase6_sim/ (isolated sim folder only)
business_impact_status: none — exercise only
jurisdiction: Canada [x]  Quebec — Law 25 in scope [ ] assessment pending  Other: ___
```

**Simulation artifacts path:** `mmi/project_brain/intel/drills/DRILL_2026-06-30_phase6_sim/`

---

## 7.2 Evidence ledger

| timestamp | evidence_family | source | observation | confidence | preserved_location | hash/screenshot/log_ref |
|-----------|-----------------|--------|-------------|------------|------------------|-------------------------|
| T+0 | host/filesystem | drill folder | Two files renamed `.locked-simulated` + `README_RECOVER_SIMULATION.txt` | 10 | `drills/DRILL_2026-06-30_phase6_sim/` | file listing |
| T+1 | identity | SIMULATED_IDENTITY_ALERT.txt | MFA push denied 02:14 unknown device (drill inject) | 8 | same drill folder | inject file |
| T+2 | backup/recovery | SIMULATED_BACKUP_ANOMALY.txt + push log | Simulated rclone delete candidate; live last B2 push PASS 2026-06-30T02:02:27Z | 9 | `MMI_BACKUP_PUSH_LOG.json` tail | push log ref |
| T+3 | local repo | war_room.py --json | Pipe LOADED; backup status PASS; brain links include scoring v2 | 9 | terminal capture | PM drill run |

**Two independent signals (§6):** host/filesystem (T+0) + identity (T+1) — separate families, non-derivative. Backup signal (T+2) is third family corroboration.

---

## 7.3 Axis scoring

### Axis A — Technical detection & visibility

| # | Check | Y/N | Notes |
|---|-------|-----|-------|
| A1 | Time to suspect/confirm (min): **<5** — MMI drill SLO | Y | Sim inject discovered immediately on folder create |
| A2 | war_room.py consulted | Y | `--json` captured pipe + backup |
| A3 | Pipe status: **LOADED** | Y | `mmi-intel-brief-template` pending |
| A4 | Last B2 push age: **<24h** | Y | 2026-06-30T02:02:27Z PASS |
| A5 | Two independent signals in ledger | Y | host + identity |
| A6 | Evidence preservation | Y | No destructive commands; sim isolated in drills/ |
| A7 | Restore path tested within 90 days | **N** | B2 path **identified** from push log; full restore drill not run this quarter |

**Axis A tier (1–4):** **4** (drill SLO; A7 gap noted for next quarter)

### Axis B — War room leadership & decisions

| # | Check | Y/N | Notes |
|---|-------|-----|-------|
| B1 | Commander named | Y | Matt |
| B2 | Decision log started | Y | this worksheet |
| B3 | Roles assigned | Y | Commander=Matt; Tech=PM drill runner; Compliance=Matt |
| B4 | Comms blackout invoked | Y | §7.5 below |
| B5 | Complexity break used | Y | Confirmed SIMULATION labels before any backup push |
| B6 | PIR stub opened | Y | §7.7 below |

**Axis B tier (1–4):** **4**

**Overall tier (min of A, B):** **4**  
**compensating_strengths:** A7 restore test overdue — schedule quarterly restore drill next.

---

## 7.4 Regulatory/legal triage

```markdown
personal_info_involved: unknown (drill — no real PII in sim folder)
pipeda_rrosh_status: unknown
breach_record_required: unknown
qc_law25_in_scope: assessment pending
cccs_report_considered: no (drill only)
criminal_fraud_branch: not applicable
legal_context_tag: unknown
```

All fields **touched** — valid drill outcome per §12 step 13.

---

## 7.5 Comms blackout checklist

- [x] No contact with attacker (sim note explicitly says do not pay)
- [x] No public posting
- [x] No vendor/client notification
- [x] Out-of-band: Matt + PM drill documentation only

---

## 7.6 Recovery

```markdown
last_known_good_backup: matt:mmi-cold-storage/archives/mmi_backup_20260629_190227.tar.gz (73193 bytes, PASS)
restore_test_status: not tested — date: n/a
b2_rclone_evidence_ref: mmi/project_brain/status/MMI_BACKUP_PUSH_LOG.json (last entry)
credential_reset_required: no (drill)
mfa_review_required: no (drill)
```

---

## 7.7 PIR stub (day 0)

```markdown
root_cause_hypothesis: N/A — scheduled purple Phase 6 exercise
what_worked: Two-signal rule; isolated sim folder; war room JSON + backup log cross-check
what_failed: n/a (drill)
control_gaps: No quarterly restore test on calendar yet; RESEARCH_EVALUATOR_PASS file still missing for intel brief task
evidence_gaps: Simulated identity/backup injects are not live provider logs
v2/v3_backlog_items: Seed restore-drill task; file evaluator pass or unblock intel brief template
pir_full_review_scheduled_for: 2026-07-07 (7 days — drill debrief)
```

---

## 7.8 Actions before close

- [x] No backup push during drill (environment trusted; no real incident)
- [ ] Complete task: n/a — drill only
- [x] Full PIR debrief scheduled
- [x] ATT&CK: **T1486** (simulated)
- [x] Purple phase: **6**

---

## §12 pass condition checklist

| Criterion | Met |
|-----------|-----|
| Two independent signals documented | Yes |
| Owner named | Yes — Matt |
| Regulatory triage touched (unknown OK) | Yes |
| Restore path identified | Yes — B2 archive |
| Comms blackout invoked | Yes |
| PIR stub created | Yes |

**Drill verdict: PASS — Tier 4 operator drill**

---

## Cleanup

Simulation folder is **safe to keep** as drill record or delete after review. Files are plaintext labels only — not malware.

```bash
# Optional remove after Matt review:
# rm -rf mmi/project_brain/intel/drills/DRILL_2026-06-30_phase6_sim
```

---

## War room snapshot (drill time)

- **Pipe:** LOADED — `mmi-intel-brief-template` (Claude)
- **Backup:** PASS — 2026-06-30T02:02:27Z
- **Panel:** `python mmi/war_room.py --json` — brain links include scoring matrix v2
