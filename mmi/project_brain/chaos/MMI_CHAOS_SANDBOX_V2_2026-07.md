# MMI Chaos Sandbox v2 — Level 2 Non-Destructive Fixture Results

**Task:** `mmi-chaos-sandbox-v2`  
**Level:** **2 — Sandbox / fixture only** (no live authority mutation)  
**Doctrine:** `mmi/project_brain/chaos/MMI_CHAOS_TABLETOP_V1_2026-07.md`  
**Fixture root:** `mmi/project_brain/chaos/fixtures/v2/`  
**Fixture manifest:** `mmi/project_brain/chaos/fixtures/v2/FIXTURE_MANIFEST.json`  
**Detection runner:** `mmi/project_brain/chaos/fixtures/v2/_run_detections.py` (sandbox-only; not live pipeline)  
**Authority:** Matt (Super)  
**Date:** 2026-07-01  
**Mode:** LOCAL / ADVISORY / NON-DESTRUCTIVE  

**North star:**

```text
destroy professionally, rebuild from evidence
```

---

## Executive verdict

Level 2 injected **10 controlled faults** into **isolated fixture copies**. All **10 faults were detected** by the sandbox detection runner or equivalent manual checks documented per test.

**Sign-off: PASS WITH REVISIONS**

**Why not plain PASS:** Detection methods are **not yet integrated** into `war_room.py`, `reload_mmi_pipes.py`, or closeout automation — they require a **chaos runner or disciplined human grep**. Recovery paths are **documented but interpretation-dependent** (stale war room, push-log tail under pressure, dual-read OPSEC worksheet vs checklist). Level 2 proves **breaks are detectable in principle**, not that production operator workflow detects them automatically.

**Level 2 ≠ production chaos-proof.** Live repo authority was not fault-injected.

---

## Hard-stop spot-check (post-run)

| Hard stop | Result |
|-----------|--------|
| Live `tasks.json` / checklist / briefs mutated for faults | **NO** — fixtures only |
| Live OPSEC-4/5/9 state changed | **NO** — all `NOT_STARTED` on live checklist |
| B2 backup mutated/deleted | **NO** |
| Destructive repo changes | **NO** |
| Malware/ransomware simulation | **NO** |
| SOAR/EDR/endpoint agent/automation expansion | **NO** |
| Level 2 claimed as full chaos program | **NO** |

Live checklist verified unchanged after run.

---

## Per-test findings table

| ID | Scenario | Fixture path | Injected fault | Expected detection | Actual detection | Result | Recovery path |
|----|----------|--------------|----------------|-------------------|------------------|--------|---------------|
| T01 | Stale active task | `fixtures/v2/test01_stale_war_room/` | War room `TASK: mmi-chaos-tabletop-v1` vs truth `mmi-chaos-sandbox-v2` | TASK id mismatch | `mismatch=True` | **PASS** | Re-run `war_room.py --json` / `reload_mmi_pipes.py` |
| T02 | DRY confusion | `fixtures/v2/test02_dry_confusion/` | Operator assumes human-gate pending; truth completed | Cross-read contradiction | `confusion_risk=True` | **PASS** | Read `tasks.json` + worksheet sign-off |
| T03 | Headline launder | `fixtures/v2/test03_headline_launder/` | Verizon 88% in §1 without tag | §1 grep violation | `fixture_violation=True`, live clean | **PASS** | Revert §1; stats in §5 only |
| T04 | Manifest gap | `fixtures/v2/test04_manifest_gap/` | Chaos doctrine path removed from manifest copy | Required path missing | `required_missing=True` | **PASS** | Post-amend push SOP |
| T05 | Restore ambiguity | `fixtures/v2/test05_restore_ambiguity/` | Two archives, no `latest_good_pointer` | Ambiguity flag | `ambiguous=True` | **PASS** | Push log tail; add latest-good stub (R3) |
| T06 | OPSEC false DONE | `fixtures/v2/test06_opsec_false_done/` | OPSEC-4/5 DONE without evidence | Audit violations | 2 violations; live all NOT_STARTED | **PASS** | Dual-read worksheet + checklist |
| T07 | No decision log | `fixtures/v2/test07_no_decision_log/` | Urgent wire, no `decision_log_id` | Missing log | `decision_log_present=False` | **PASS** | Human-gate drill §6 template |
| T08 | Non-MMI scope | `fixtures/v2/test08_non_mmi_scope/` | `phase1-stability-audit` only active | `is_mmi_task` False | `should_block=True` | **PASS** | Scope doc + reload guard |
| T09 | Hash mismatch | `fixtures/v2/test09_hash_mismatch/` | PASS label, bytes differ | Integrity fail | `bytes_mismatch=True` | **PASS** | sha256 + byte verify; OPSEC-7 |
| T10 | False PASS | `fixtures/v2/test10_false_pass_closeout/` | Completed PASS, missing output | File-exists fail | `false_pass=True` | **PASS** | Closeout output spot-check |

**Aggregate:** 10/10 faults detected in sandbox. **0/10** silent misses in fixture layer.

---

## Detailed test records

### T01 — Stale active-task mismatch

- **Evidence:** `war_room_stale.txt` vs `tasks_truth.json`  
- **Hardening:** War room cheatsheet — refresh before act (R4)  
- **Interpretation risk:** Operator trusts stale terminal without re-run  

### T02 — DRY pipeline confusion

- **Evidence:** `operator_assumption.md` vs `tasks_truth.json`  
- **Hardening:** Prominent **Task closed ≠ OPSEC proven** in status docs  
- **Interpretation risk:** Closed task mentally still "pending"  

### T03 — Global/vendor stat in Canadian headline

- **Evidence:** `INTEL_brief_INJECTED.md` line 34 — Verizon 88% in §1; live brief §1 clean  
- **Hardening:** Brief closeout §1 grep (R5); initial detection script used wrong `---` split — fixed to `## 1.` boundary  
- **Interpretation risk:** Automated grep not in standard closeout yet  

### T04 — Archive manifest missing required file

- **Evidence:** `manifest_gap.json` lacks `MMI_CHAOS_TABLETOP_V1_2026-07.md`  
- **Hardening:** Required-path checklist on push manifest review  

### T05 — Restore-path ambiguity

- **Evidence:** `restore_ambiguity.json`; live tail `mmi_backup_20260630_162035.tar.gz`  
- **Hardening:** `MMI_LATEST_GOOD_ARCHIVE.md` stub (R3)  

### T06 — OPSEC falsely marked DONE

- **Evidence:** Fixture violations OPSEC-4 empty `last_done`, OPSEC-5 dry-run-only; **live checklist all NOT_STARTED**  
- **Hardening:** Worksheet + checklist dual-read — **what held on live repo**  

### T07 — Missing decision log

- **Evidence:** `vendor_email_scenario.txt` — no `decision_log_id`  
- **Hardening:** OPSEC-9 real habit (Matt-owned); template exists  

### T08 — Non-MMI scope contamination

- **Evidence:** `is_mmi_task(phase1-stability-audit)` → False  
- **Hardening:** Keep non-MMI tasks paused  

### T09 — Backup hash mismatch

- **Evidence:** `local_bytes=200` vs `remote_bytes=100` with `push_status: PASS`  
- **Hardening:** Never trust PASS label alone  

### T10 — False PASS closeout

- **Evidence:** `MISSING_OUTPUT.md` absent while task `completed` + `PASS`  
- **Hardening:** `output_files` existence check before accepting closeout  

---

## What snapped (in fixtures)

| Snap | Meaning |
|------|---------|
| Stale vs truth task id | Operator could act on wrong task |
| Mental pending vs completed | Idle/confusion; duplicate work risk |
| §1 vendor % | Canadian fact laundering |
| Missing manifest path | Restore without chaos doctrine |
| No latest-good pointer | Wrong archive under pressure |
| OPSEC DONE without evidence | False maturity |
| No decision log | Payment action without timestamp |
| Non-MMI active task | Scope escape if guard ignored |
| Byte/sha mismatch labeled PASS | False recovery confidence |
| Missing closeout output | Pipeline lie |

---

## What held (live repo + guards)

| Held | Evidence |
|------|----------|
| Live OPSEC-4/5/9 honesty | All `NOT_STARTED` after sandbox run |
| Live brief headlines | No vendor % in §1 on disk |
| `is_mmi_task()` guard | Blocks non-MMI active task |
| Push log tail integrity | Latest archive named with sha |
| Human-gate worksheet | Task closed ≠ habit proven documented |
| Level 1 doctrine | Attack surfaces mapped before sandbox |
| Fixture isolation | `live_authority_mutated: false` in manifest |

---

## Interpretation-layer risks (primary)

Level 2 confirms the Level 1 finding: **the repo can tell the truth when asked**, but **nothing forces the ask** at operator decision time.

| Risk | Why it persists after Level 2 |
|------|-------------------------------|
| Stale war room | No auto-refresh on task transition |
| Worksheet vs habit | Worksheet complete; checklist not DONE |
| Headline regression | Detection is grep discipline, not CI |
| Restore under pressure | Push log tail requires training |
| False PASS closeout | `complete_task.py` does not verify output paths exist |
| Decision log | Template exists; habit not proven |

**Chaos value:** These are the breaks that matter — not missing files on disk.

---

## Required hardening / remediation

| ID | Action | Owner | Priority |
|----|--------|-------|----------|
| H1 | Add closeout check: `output_files` must exist on disk | Cursor PM | High |
| H2 | Add brief amend grep: no `%` / vendor names in §1 + ATT&CK `smb_relevance` | Cursor PM | High |
| H3 | Create `status/MMI_LATEST_GOOD_ARCHIVE.md` one-liner from push log tail | Cursor PM | High |
| H4 | War room cheatsheet bullet: refresh before act | Cursor PM | Medium |
| H5 | Optional: integrate T01/T10 checks into `reload_mmi_pipes` / `complete_task` (Matt auth) | Codex | Medium |
| H6 | Matt OPSEC-4/5/9 habit evidence when ready | Matt | Critical (operator) |
| H7 | Level 3 sandbox copy fault injection — **CONDITIONAL** on H1–H3 | Matt | Next chaos gate |

---

## Readiness for Level 3

**CONDITIONAL — YES after H1–H3**

Level 2 shows faults are **detectable in fixture copies** with explicit checks. Level 3 (controlled reversible fault injection on **sandbox repo copy**, not live) is justified **after** closeout path verification and latest-good archive stub land — not before.

Level 4 remains **PROHIBITED**.

---

## Chaos lane status (updated)

```text
Chaos lane:
- Level 1 tabletop doctrine: COMPLETE — PASS WITH REVISIONS
- Level 2 sandbox testing: COMPLETE — PASS WITH REVISIONS (this document)
- Level 3 reversible fault injection: NOT STARTED — CONDITIONAL on H1–H3
- Level 4 destructive/live chaos: PROHIBITED
```

---

## Sign-off

**PASS WITH REVISIONS**

All 10 injected fixture faults detected. Live authority unchanged. OPSEC-4/5/9 unchanged. Recovery paths documented but not automated — interpretation layer remains the primary snap surface. Level 2 does not equal production chaos-proof.

**Evidence artifacts:**

- `mmi/project_brain/chaos/MMI_CHAOS_SANDBOX_V2_2026-07.md` (this file)  
- `mmi/project_brain/chaos/fixtures/v2/FIXTURE_MANIFEST.json`  
- `mmi/project_brain/chaos/fixtures/v2/test01–test10/` fixture directories  
