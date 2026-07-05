# MMI OPSEC-8 Quarterly Operator Drill — 2026-06-30

**Task:** `mmi-opsec-8-quarterly-operator-drill`  
**Mode:** LOCAL / NON-DESTRUCTIVE / HUMAN-ONLY  
**Timebox:** 15–30 minutes  
**Elapsed (setup + worksheet):** ~22 min (operator local metric)  
**Authority:** `intel/WAR_ROOM_SCORING_MATRIX_v2.md` §12; `opsec/OPERATOR_OPSEC_CHECKLIST.md` OPSEC-8  
**Intel brief:** `intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md`  
**Recovery proof referenced (not re-run):** `status/MMI_RESTORE_CHECK_WAR_ROOM_PROOF_2026-06.md` — COMPLETE — PASS  
**Result:** **COMPLETE — PASS** (Matt accepted 2026-06-30). Operator readiness proof layer closed. Did not rerun backup push; referenced `MMI_RESTORE_CHECK_WAR_ROOM_PROOF_2026-06.md` only.

---

## 7.1 Incident header

```markdown
incident_id: DRILL-2026-06-30-OPSEC8
opened_at: 2026-06-30T20:40:00-07:00 (operator local)
opened_by (Commander): Matt
suspected_type: Simulated ransomware backup-targeting (operator readiness drill)
affected_systems: mmi/project_brain/intel/drills/DRILL_2026-06-30_opsec8_quarterly/ (isolated sim folder only)
business_impact_status: none — exercise only
jurisdiction: Canada [x]  Quebec — Law 25 in scope [ ] assessment pending  Other: ___
```

**Simulation path:** `mmi/project_brain/intel/drills/DRILL_2026-06-30_opsec8_quarterly/`

---

## 7.2 Evidence ledger

| timestamp | evidence_family | source | observation | confidence | preserved_location | hash/screenshot/log_ref |
|-----------|-----------------|--------|-------------|------------|------------------|-------------------------|
| T+0 | host/filesystem | drill folder | `.locked-simulated` file + `SIMULATED_HOST_RANSOMWARE.txt` | 10 | `drills/DRILL_2026-06-30_opsec8_quarterly/` | file listing |
| T+2 | backup/recovery | `SIMULATED_BACKUP_RESTORE_ALERT.txt` + restore proof | Simulated B2 delete alert; operator referenced `MMI_RESTORE_CHECK_WAR_ROOM_PROOF_2026-06.md` (restore-check PASS, war_room.py 7889 bytes) — **no new push** | 9 | restore proof doc + sim inject | proof doc ref |
| T+4 | local repo | `war_room.py --json` | Pipe LOADED (`mmi-opsec-8-quarterly-operator-drill`); read-only panel | 9 | terminal capture | drill run |

**Two independent signals (§6):** host/filesystem (T+0) + backup/recovery (T+2) — separate families, non-derivative.

---

## 7.3 Axis scoring

### Axis A — Technical detection & visibility

| # | Check | Y/N | Notes |
|---|-------|-----|-------|
| A1 | Time to suspect/confirm (min): **<15** — MMI drill SLO | Y | Sim injects reviewed within drill window |
| A2 | war_room.py consulted | Y | `--json` captured pipe LOADED |
| A3 | Pipe status: **LOADED** | Y | `mmi-opsec-8-quarterly-operator-drill` active |
| A4 | Last B2 push age: **<24h** | Y | `mmi_backup_20260629_203555.tar.gz` PASS 2026-06-30T03:35:56Z |
| A5 | Two independent signals in ledger | Y | host + backup/recovery |
| A6 | Evidence preservation | Y | Sim isolated; no destructive commands |
| A7 | Restore path tested within 90 days | **Y** | **Referenced** `MMI_RESTORE_CHECK_WAR_ROOM_PROOF_2026-06.md` — isolated restore-check PASS 2026-06-30; not re-run this drill |

**Axis A tier (1–4):** **4**

### Axis B — War room leadership & decisions

| # | Check | Y/N | Notes |
|---|-------|-----|-------|
| B1 | Commander named | Y | Matt |
| B2 | Decision log started | Y | this worksheet (T+0) |
| B3 | Roles assigned | Y | Commander=Matt; Operator=Matt |
| B4 | Comms blackout invoked | Y | §7.5 below |
| B5 | Complexity break used | Y | SIMULATION labels confirmed before any action |
| B6 | PIR stub opened | Y | `PIR_STUB_2026-06-30.md` |

**Axis B tier (1–4):** **4**

**Overall tier (min of A, B):** **4**  
**compensating_strengths:** Operator drill proves readiness to reference locked restore-check proof without rerunning backup mechanics.

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

All fields **touched** — valid drill outcome.

---

## 7.5 Comms blackout checklist

- [x] No contact with attacker
- [x] No public posting
- [x] No vendor/client notification
- [x] Out-of-band: Matt drill documentation only

---

## 7.6 Recovery (reference only — not re-executed)

```markdown
last_known_good_backup: matt:mmi-cold-storage/archives/mmi_backup_20260629_203555.tar.gz (128494 bytes, PASS)
restore_test_status: PASS — referenced from MMI_RESTORE_CHECK_WAR_ROOM_PROOF_2026-06.md (2026-06-30 isolated restore-check; war_room.py verified)
b2_rclone_evidence_ref: mmi/project_brain/status/MMI_BACKUP_PUSH_LOG.json (2026-06-30T03:35:56Z entry)
credential_reset_required: no (drill)
mfa_review_required: no (drill)
new_backup_push_this_drill: no — Matt did not authorize; proof referenced only
```

---

## 7.7 PIR stub

See: `PIR_STUB_2026-06-30.md` in this drill folder.

---

## 7.8 Actions before close

- [x] No backup push during drill
- [x] Restore-check proof referenced (not re-run)
- [x] OPSEC-8 `last_done` updated only (see checklist)
- [x] OPSEC-3/6/7 and other items **not** marked DONE
- [x] ATT&CK: **T1486**, **T1490** (simulated / intel brief framing)
- [x] Boundaries preserved

---

## §12 pass condition checklist

| Criterion | Met |
|-----------|-----|
| Two independent signals documented | Yes |
| Owner named | Yes — Matt |
| Regulatory triage touched (unknown OK) | Yes |
| Restore path identified / proof referenced | Yes — MMI_RESTORE_CHECK_WAR_ROOM_PROOF |
| Comms blackout invoked | Yes |
| PIR stub created | Yes |

**Drill verdict: PASS — Tier 4 operator drill**

Proves Matt can detect, classify, document, reference recovery proof, and open a PIR stub within the local drill window. Does **not** prove OPSEC hardening implementation.

---

## War room snapshot (drill time)

- **Pipe:** LOADED — `mmi-opsec-8-quarterly-operator-drill` (Matt)
- **Backup:** PASS — 2026-06-30T03:35:56Z (`mmi_backup_20260629_203555.tar.gz`)
- **Panel:** `python mmi/war_room.py --json`
