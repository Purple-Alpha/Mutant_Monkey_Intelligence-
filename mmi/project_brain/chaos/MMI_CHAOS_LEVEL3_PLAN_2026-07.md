# MMI Chaos Level 3 Plan — Reversible Fault Injection (Planning Only)

**Task:** `mmi-chaos-level3-planning`  
**Date:** 2026-07-01  
**Authority:** Matt (Super) — planning authorization only  
**Mode:** PLANNING ONLY — **Level 3 execution is NOT authorized**  
**Doctrine:** `MMI_CHAOS_TABLETOP_V1_2026-07.md`  
**Prior levels:** Level 1 COMPLETE · Level 2 COMPLETE · H1–H3 COMPLETE · Restore validation PASS on `163709`  
**Level 4:** **PROHIBITED** — no planning beyond this prohibition statement  

**North star:**

```text
destroy professionally, rebuild from evidence
```

---

## Executive summary

Level 2 proved **detection in isolated fixtures**. Level 3 asks whether MMI can survive **controlled, reversible faults closer to operator workflow** without losing truth — one fault at a time, with explicit rollback and evidence.

This document defines **what may be broken, where rollback lives, what is prohibited, and how execution will be gated**. It does **not** authorize any Level 3 test run.

**Planning sign-off: PASS WITH REVISIONS**

| Criterion | Result |
|-----------|--------|
| Level 3 execution authorized | **NO** — explicitly blocked |
| Candidate faults defined with rollback | **YES** — 6 scenarios |
| Lowest-risk ordering | **YES** — staged copies first |
| Fresh B2 / latest-good gate before execution | **YES** |
| OPSEC-4/5/9 preserved NOT_STARTED on live checklist | **YES** |
| Level 4 beyond “prohibited” | **NO** |

**Revision caveat:** Detection for several scenarios still relies on existing read-only tools (`mmi_verify.py`, manual war-room refresh) — not a dedicated Level 3 runner integrated into live workflow. First execution pass should remain **staged-copy only** until Matt approves any live-ish step.

---

## Prerequisites (must pass before ANY Level 3 execution)

| Gate | Requirement | Evidence source |
|------|-------------|-----------------|
| G0 | Level 3 **execution** Matt authorization per scenario | Separate auth string per test |
| G1 | H1–H3 hardening complete | `MMI_CHAOS_HARDENING_H1-H3_2026-07.md` |
| G2 | Restore-validated archive confirmed | `163709` — tar + `--restore-check` PASS (`MMI_LATEST_GOOD_ARCHIVE_VALIDATION_2026-07.md`) |
| G3 | Fresh latest-good / B2 confirmation immediately before each test | Read `MMI_LATEST_GOOD_ARCHIVE.md` + push log tail; SHA256 match |
| G4 | Staging root clean or versioned | `mmi/project_brain/chaos/fixtures/v3/` (create on first execution auth) |
| G5 | Live OPSEC-4/5/9 remain `NOT_STARTED` | `opsec/OPERATOR_OPSEC_CHECKLIST.md` pre-check grep |
| G6 | One fault · one rollback · one evidence packet | No batch runs |

**Restore reference distinction (do not conflate):**

| Role | Archive |
|------|---------|
| Restore-validated content snapshot | `mmi_backup_20260630_163709.tar.gz` |
| Latest documentation mirror | `mmi_backup_20260630_164111.tar.gz` |

---

## Execution model — flight test, not batch chaos

```text
For each authorized Level 3 test:
  1. Matt authorization (single scenario ID)
  2. Pre-check gates G0–G6
  3. Inject ONE reversible fault (staging or approved live-ish target)
  4. Run detection (read-only where possible)
  5. Capture evidence packet (before/after JSON or diff)
  6. Rollback to known-good state
  7. Post-check: live authority unchanged unless scenario explicitly scoped
  8. Close evidence note — PASS | PASS WITH REVISIONS | FAIL
  9. B2 mirror evidence (Matt-authorized) before next test
```

**Staging root (execution, not created in this planning pass):**

```text
mmi/project_brain/chaos/fixtures/v3/<scenario_id>/
  BEFORE/          # known-good copy
  FAULT/           # fault-injected copy
  EVIDENCE/        # detection output, diffs, timestamps
  ROLLBACK.md      # exact revert steps for this run
```

---

## Hard stops (all levels — non-negotiable)

| Stop | Rule |
|------|------|
| HS1 | No destructive live repo changes without Matt per-scenario auth + documented rollback |
| HS2 | No B2 deletion, overwrite, or remote mutation |
| HS3 | No malware / ransomware simulation |
| HS4 | No endpoint agent, EDR, SOAR, auto-containment |
| HS5 | Do not change live OPSEC-4/5/9 to DONE or fabricate `last_done` |
| HS6 | No Level 3 batch runs |
| HS7 | No Level 4 planning or execution |
| HS8 | Do not integrate chaos fixture runner into live workflow except read-only verification |

---

## Candidate scenarios — ordered lowest risk first

**Order rationale:** Staged-file-only faults first (no live path touch). Copied-tree faults second. Live-ish war-room compare last (read-only detection against live `tasks.json`, fault only in staging artifact).

| Order | ID | Scenario | Target type |
|-------|-----|----------|-------------|
| 1 | L3-06 | OPSEC false-DONE | Staged checklist copy only |
| 2 | L3-04 | Intel headline laundering | Staged brief copy only |
| 3 | L3-05 | Manifest / hash mismatch | Staged manifest JSON only |
| 4 | L3-03 | Latest-good pointer inconsistency | Staged stub copy only |
| 5 | L3-02 | Task closeout output mismatch | Staged `tasks.json` slice / temp closeout dry-run |
| 6 | L3-01 | Stale war-room pointer | Staged war-room output vs live truth |

---

## Scenario specifications

### L3-06 — OPSEC false-DONE (staged checklist only)

| Field | Value |
|-------|--------|
| **Live or copy** | **Copied target only** — do not edit live checklist |
| **Path** | `fixtures/v3/L3-06_opsec_false_done/FAULT/opsec/OPERATOR_OPSEC_CHECKLIST.md` (copy from live BEFORE/) |
| **Fault** | Set OPSEC-4 and/or OPSEC-5 to `DONE` with empty or worksheet-only `last_done` |
| **Pre-check** | Live checklist: OPSEC-4/5/9 all `NOT_STARTED`; copy BEFORE/ from live |
| **Detection expected** | Manual dual-read vs `intel/drills/OPSEC_HUMAN_GATE_DRILL_2026-06-30.md`; Level 2 T06 logic — violations flagged |
| **Rollback** | Delete `FAULT/` tree; confirm live checklist unchanged (sha256 or diff live file) |
| **Recovery evidence** | `EVIDENCE/violations.json` + live file hash unchanged |
| **Abort if** | Any write touches live `opsec/OPERATOR_OPSEC_CHECKLIST.md` |
| **Operator approval** | Matt — per test auth |

---

### L3-04 — Intel headline laundering (staged brief copy only)

| Field | Value |
|-------|--------|
| **Live or copy** | **Copied target only** |
| **Path** | `fixtures/v3/L3-04_headline_launder/FAULT/intel/briefs/INTEL_ransomware-backup-targeting_2026-06.md` |
| **Fault** | Inject Verizon 88% (or equivalent) into `## 1. Threat summary` without `[Global Data` tag (mirror Level 2 T03) |
| **Pre-check** | `python scripts/mmi_verify.py intel-briefs` → live `ok: true` |
| **Detection expected** | `python scripts/mmi_verify.py intel-brief <FAULT path>` → `ok: false`, `section_1_threat_summary` violation |
| **Rollback** | Remove FAULT brief; re-run live `intel-briefs` → still `ok: true` |
| **Recovery evidence** | Detection JSON before/after; live brief paths unchanged |
| **Abort if** | Live `intel/briefs/*.md` modified |
| **Operator approval** | Matt |

---

### L3-05 — Manifest / hash mismatch (staged manifest only)

| Field | Value |
|-------|--------|
| **Live or copy** | **Copied target only** |
| **Path** | `fixtures/v3/L3-05_hash_mismatch/FAULT/push_log_snippet.json` (synthetic slice, not live push log) |
| **Fault** | Record `push_status: PASS` with `local_bytes` ≠ `remote_bytes` or wrong `archive_sha256` (mirror T09) |
| **Pre-check** | Live `MMI_BACKUP_PUSH_LOG.json` tail unchanged |
| **Detection expected** | Byte + SHA256 compare script/logic → integrity fail despite PASS label |
| **Rollback** | Delete staged manifest; confirm live push log unmodified |
| **Recovery evidence** | `EVIDENCE/integrity_check.json` |
| **Abort if** | Live `status/MMI_BACKUP_PUSH_LOG.json` edited |
| **Operator approval** | Matt |

---

### L3-03 — Latest-good archive pointer inconsistency (staged stub only)

| Field | Value |
|-------|--------|
| **Live or copy** | **Copied target only** |
| **Path** | `fixtures/v3/L3-03_latest_good_inconsistent/FAULT/backup/MMI_LATEST_GOOD_ARCHIVE.md` |
| **Fault** | Point archive name to `163709` but SHA256 to a different archive, or name `164111` with `163709` hash |
| **Pre-check** | Live stub consistent with validation doc; `163709` restore-check PASS on record |
| **Detection expected** | Cross-read stub vs `MMI_LATEST_GOOD_ARCHIVE_VALIDATION_2026-07.md` + push log tail → inconsistency flagged |
| **Rollback** | Delete staged stub; live `backup/MMI_LATEST_GOOD_ARCHIVE.md` unchanged |
| **Recovery evidence** | Diff + live stub SHA256 unchanged |
| **Abort if** | Live H3 stub modified without Matt auth |
| **Operator approval** | Matt |

---

### L3-02 — Task closeout output mismatch (staged / dry-run)

| Field | Value |
|-------|--------|
| **Live or copy** | **Copied target + dry-run closeout** — do not complete a live task with fake outputs |
| **Path** | `fixtures/v3/L3-02_closeout_mismatch/FAULT/tasks_snippet.json` + dry-run: `complete_task.py` with `--output fake/missing.md` against **non-persisted** or **fixture task id** only |
| **Fault** | Attempt closeout claiming `output_files` path that does not exist (mirror T10 / H1) |
| **Pre-check** | H1 gate active in `complete_task.py`; no pending task mutated |
| **Detection expected** | `complete_task.py` exit 1; H1 JSON shows `missing` list; **no** `tasks.json` write on failure |
| **Rollback** | N/A if pre-check holds — verify `tasks.json` hash unchanged |
| **Recovery evidence** | CLI stdout + `tasks.json` before/after hash |
| **Abort if** | Real task id in `tasks.json` gets `completed` with missing outputs |
| **Operator approval** | Matt |

---

### L3-01 — Stale war-room pointer (live-ish, lowest live touch)

| Field | Value |
|-------|--------|
| **Live or copy** | **Live-ish** — fault in **staged war-room capture only**; live `tasks.json` is truth |
| **Path** | `fixtures/v3/L3-01_stale_war_room/FAULT/war_room_capture.txt` (stale TASK id) vs live `tasks.json` |
| **Fault** | Staged capture shows `TASK: <old-id>` while live active/completed task differs (mirror T01) |
| **Pre-check** | Run `python mmi/war_room.py --json` → save to `BEFORE/war_room_live.json` |
| **Detection expected** | Compare staged stale capture to live JSON → `mismatch=True`; operator procedure: re-run war room before act |
| **Rollback** | Delete FAULT capture; re-run live war room → matches `tasks.json` |
| **Recovery evidence** | Before/after war room JSON; live `tasks.json` unchanged |
| **Abort if** | `tasks.json` edited to match stale capture; war room script modified |
| **Operator approval** | Matt — **last in sequence** (most live-ish) |

---

## Detection tooling map (read-only)

| Scenario | Tool / procedure |
|----------|------------------|
| L3-06 | Checklist dual-read + T06 fixture logic pattern |
| L3-04 | `scripts/mmi_verify.py intel-brief` |
| L3-05 | SHA256 + byte compare (manual or small read-only script) |
| L3-03 | Cross-read stub / validation doc / push log tail |
| L3-02 | `complete_task.py` H1 gate (must not persist on fail) |
| L3-01 | `war_room.py --json` vs staged capture diff |

**Not authorized:** wiring these into `reload_mmi_pipes.py` or auto-enforcement without separate Matt auth.

---

## Evidence packet template (per execution)

Each authorized run produces:

```text
mmi/project_brain/chaos/fixtures/v3/<scenario_id>/EVIDENCE/
  pre_check.json
  fault_description.md
  detection_output.json
  rollback_confirmation.json
  post_check_live_unchanged.json
  signoff.txt          # PASS | PASS WITH REVISIONS | FAIL
```

Optional rollup after all six (future): `MMI_CHAOS_LEVEL3_RESULTS_2026-07.md` — **not part of this planning pass**.

---

## OPSEC and human-gate preservation

| Control | Planning commitment |
|---------|---------------------|
| OPSEC-4 | Live checklist stays `NOT_STARTED` until Matt habit evidence |
| OPSEC-5 | Live checklist stays `NOT_STARTED` |
| OPSEC-9 | Live checklist stays `NOT_STARTED` |
| Human-gate worksheet | Reference only — not proof of habit |
| Task closed ≠ OPSEC proven | Preserved in all scenario abort rules |

Level 3 tests **verify the repo and procedures under fault** — they do **not** close OPSEC gaps.

---

## Level 4 — prohibited

Level 4 (destructive / live chaos, backup deletion, live malware simulation, production fault injection without guaranteed rollback) remains **PROHIBITED**. No Level 4 scenario table, seed tasks, or execution planning beyond this sentence.

---

## Recommended sequence after plan approval

```text
1. Matt reviews this plan → approve / revise
2. B2 mirror plan artifact (Matt-authorized push)
3. Authorize L3-06 only → execute → evidence → rollback → B2
4. Repeat one scenario at a time in order (L3-06 → … → L3-01)
5. After all staged scenarios PASS, decide whether L3-01 live-ish needs repeat
6. Only then consider Level 3 program closeout doc — not Level 4
```

---

## Changed / new artifacts (this task)

| Path | Status |
|------|--------|
| `mmi/project_brain/chaos/MMI_CHAOS_LEVEL3_PLAN_2026-07.md` | **NEW** — this file |
| `mmi/project_brain/chaos/fixtures/v3/` | **Not created** — execution only |

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | Level 3 planning only — 6 scenarios, execution NOT authorized |
