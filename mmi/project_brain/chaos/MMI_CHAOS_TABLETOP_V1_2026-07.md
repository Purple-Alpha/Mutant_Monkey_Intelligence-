# MMI Chaos Tabletop v1 — Professional Destruction Doctrine & Readiness

**Task:** `mmi-chaos-tabletop-v1`  
**Level:** **1 — Tabletop / readiness only** (no live fault injection run in this session)  
**Authority:** Matt (Super) — Canadian operator  
**Mode:** LOCAL / ADVISORY / NON-DESTRUCTIVE  
**Date:** 2026-07-01  
**North star:**

```text
MMI chaos testing = controlled professional destruction + evidence capture + rebuild.
destroy professionally, rebuild from evidence
```

---

## 0. Definition

For MMI, **chaos testing** means:

```text
We professionally attack what we built, try to break it from every realistic angle,
capture exactly what snaps, and rebuild from evidence until the system becomes stronger.
```

**MMI chaos testing** is controlled adversarial resilience testing of the **project brain** — not random destruction. Every run must be scoped, reversible or sandboxed, and evidence-producing.

### What every chaos run must capture

| Evidence field | Question answered |
|----------------|-------------------|
| What was attacked | Assumption, surface, or file under test |
| What broke | Snap point — truth, evidence, recovery, authority, or integrity lost |
| What held | Control or doc that resisted the break attempt |
| What was detected | Operator or script noticed before harm |
| What was missed | Silent failure — worst case |
| Recovery path | What worked or failed to restore clarity |
| Rebuild action | Patch, checklist item, doc fix, or future task |

**Rules:**

- Chaos testing is **not** random destruction.  
- Every test must have a **rollback or safe sandbox**.  
- Every test must produce **evidence**.  
- Every failure becomes a **patch, checklist item, documentation fix, or future task**.  
- **No pass/fail claims without evidence.**  
- **Level 1 ≠ completed chaos testing** — it defines doctrine and Level 2 readiness only.

---

## 1. Chaos levels

| Level | Name | What happens | MMI status |
|-------|------|--------------|------------|
| **1** | Tabletop / readiness | Doctrine, scenario design, snap-point analysis, Level 2 test specs | **This document** |
| **2** | Non-destructive fixture / sandbox | Isolated copies, `--dry-run`, `--restore-check` on test tar, war_room `--json` drills | **Next authorized step** |
| **3** | Controlled reversible fault injection | Deliberate stale `tasks.json` row in sandbox, manifest gap simulation, index row drift in copy | Requires Matt auth + rollback plan |
| **4** | Destructive / live chaos | Live repo mutation, B2 delete, malware sim | **Prohibited for now** |

### Level 1 hard stops (observed this session)

- No malware or ransomware simulation  
- No destructive changes to live repo  
- No backup overwrite or B2 deletion  
- No endpoint agent / EDR / SOAR  
- No automation expansion  
- No closing OPSEC-4/5/9  
- No claiming Level 1 equals chaos program complete  

---

## 2. MMI chaos attack surfaces

Chaos attacks the **operating system around the project**, not just Python files.

| # | Surface | Attack question |
|---|---------|-----------------|
| 1 | **Current truth** | Can MMI identify active task, latest brief, latest backup, real status? |
| 2 | **Task queue / pipeline** | Stale task, wrong active, duplicate closeout, false DRY? |
| 3 | **War room accuracy** | Does `war_room.py` match `tasks.json` + reload output? |
| 4 | **Intel brief integrity** | Global/vendor stats quarantined from Canadian headlines? |
| 5 | **Canadian localization** | `MIXED` / `[Global Data]` honored under pressure? |
| 6 | **OPSEC honesty** | Worksheet exists but OPSEC-4/5/9 stay `NOT_STARTED` when unproven? |
| 7 | **Backup manifest** | Archive lists required intel/opsec/chaos paths with matching hashes? |
| 8 | **Restore path clarity** | Can Matt name latest good archive under pressure? |
| 9 | **Operator authority** | Work not falsely assigned, approved, or closed without Matt? |
| 10 | **Scope creep resistance** | SOAR, EDR, swarm, NorthStar, non-MMI projects rejected? |

---

## 3. Baseline truth (pre-tabletop — evidence at Level 1 start)

Captured **2026-07-01** from local repo; use as reference during scenarios.

| Truth object | Current value | Evidence source |
|--------------|---------------|-----------------|
| Active task | `mmi-chaos-tabletop-v1` (pending) | `tasks.json`, `reload_mmi_pipes.py` |
| Latest B2 archive | `mmi_backup_20260630_154854.tar.gz` | `MMI_BACKUP_PUSH_LOG.json` tail |
| Archive SHA256 | `f1762050bf16d93f1737fbb6b5ae4782c413ec9ef280dc4f1ab42c3d5a8aefd9` | Push log |
| Intel briefs filed | 2 (`MIXED` status) | `INTEL_INDEX.md` v1.3 |
| OPSEC-4/5/9 | `NOT_STARTED` (known operator-risk) | `OPERATOR_OPSEC_CHECKLIST.md` |
| Human-gate task | `mmi-opsec-human-gate-tightening` **completed** (theory ≠ habit) | `tasks.json` |
| Restore proof | File-level PASS + OPSEC-8 drill PASS | `MMI_RESTORE_CHECK_WAR_ROOM_PROOF_2026-06.md` |

---

## 4. Scenario table (Level 1 — professional break design)

For each scenario: **assumption attacked → break attempt → expected snap → detection → recovery → harden → Level 2 test → hard stops.**

### Scenario 1 — War room shows stale active task

| Field | Content |
|-------|---------|
| **Assumption attacked** | `war_room.py --json` always reflects `tasks.json` pending task |
| **Professional break attempt** | Complete task in `tasks.json` manually without re-running war room; operator reads cached terminal |
| **Expected snap point** | Operator acts on wrong task id / score / assignee |
| **Detection evidence** | Diff `tasks.json` active row vs war room `TASK:` line; timestamp of last reload |
| **Recovery evidence** | `python scripts/reload_mmi_pipes.py` or `python mmi/war_room.py --json` |
| **Rebuild / harden** | War room cheatsheet: "always refresh before acting"; optional `--watch` during incidents |
| **Safe Level 2 test** | Sandbox copy of repo; complete dummy task; assert war room before/after mismatch until refresh |
| **Hard stops** | No live task mutation without Matt auth |

### Scenario 2 — Pipeline DRY but operator thinks work is pending

| Field | Content |
|-------|---------|
| **Assumption attacked** | DRY pipe means "nothing to do" |
| **Professional break attempt** | Pipeline tail consumed but Matt believes human-gate still pending; or completed task not removed from mental queue |
| **Expected snap point** | Idle while risk open; or duplicate work |
| **Detection evidence** | `reload_mmi_pipes.py` → `PIPE STATUS: DRY`; cross-check `tasks.json` last completed vs `task_pipeline.json` tail |
| **Recovery evidence** | `MMI_PIPELINE_REFRESH_*.md`; `worksheet_status` vs `status` on closed tasks |
| **Rebuild / harden** | Status doc line: **Task closed ≠ OPSEC proven**; war room shows completed + active separately |
| **Safe Level 2 test** | Tabletop quiz: name active task, last completed, next pipeline id without opening wrong file |
| **Hard stops** | Do not auto-seed without pipeline entry |

### Scenario 3 — Intel brief promotes global/vendor stat into Canadian headline

| Field | Content |
|-------|---------|
| **Assumption attacked** | CA localization pass prevents headline laundering |
| **Professional break attempt** | Editor moves Verizon 88% or Veeam 96% from §5 claims table into §1 threat summary as "Canadian SMB rate" |
| **Expected snap point** | False Canadian fact in operator-facing headline |
| **Detection evidence** | Grep brief §1/ATT&CK `smb_relevance` for `%`; verify `[Global Data]` only in §5+ |
| **Recovery evidence** | `RESEARCH_VERIFICATION_CA_LOCALIZATION_2026-07.md` §3 V1/V5; revert headline |
| **Rebuild / harden** | Brief template hard stop; index `source_status: MIXED` |
| **Safe Level 2 test** | Checklist review of both filed briefs §1 + ATT&CK blocks (pass today — hold regression test) |
| **Hard stops** | No new brief filing without spot-check |

### Scenario 4 — B2 archive manifest misses required files

| Field | Content |
|-------|---------|
| **Assumption attacked** | `BACKUP_ALLOWLIST` + push log manifest = complete recovery set |
| **Professional break attempt** | New file under `intel/chaos/` or amended brief not pushed before incident |
| **Expected snap point** | Restore from "latest" archive missing chaos doctrine or human-gate worksheet |
| **Detection evidence** | Compare `MMI_BACKUP_PUSH_LOG.json` file list vs required paths; `tar -tzf` spot-check |
| **Recovery evidence** | Matt-authorized `--backup-and-push`; prior archive still on B2 |
| **Rebuild / harden** | Post-amend push SOP; OPSEC-6 cadence; manifest includes `intel/drills/`, `opsec/`, `intel/briefs/` |
| **Safe Level 2 test** | `--dry-run` manifest after chaos doc lands; verify path listed before closeout push |
| **Hard stops** | No B2 delete; no overwrite without new archive name |

### Scenario 5 — Restore path unclear under pressure

| Field | Content |
|-------|---------|
| **Assumption attacked** | Operator knows which archive is "latest good" |
| **Professional break attempt** | Multiple `mmi_backup_*.tar.gz` names; push log JSON too large to skim; panic picks wrong date |
| **Expected snap point** | Restore from stale archive; lose human-gate or intel amendments |
| **Detection evidence** | Push log **tail entry** `push_file` + `archive_sha256`; worksheet names expected SHA |
| **Recovery evidence** | `MMI_RESTORE_CHECK_WAR_ROOM_PROOF_2026-06.md` procedure; isolated `--restore-check` |
| **Rebuild / harden** | One-line "latest good" in war room or status stub; OPSEC-7 weekly tar spot-check |
| **Safe Level 2 test** | Timed drill: name latest archive + SHA from push log in <2 min |
| **Hard stops** | No live restore over production tree without isolated dir |

### Scenario 6 — OPSEC-4/5/9 falsely assumed DONE

| Field | Content |
|-------|---------|
| **Assumption attacked** | Worksheet completion = operator controls proven |
| **Professional break attempt** | Reader sees `OPSEC_HUMAN_GATE_DRILL` sign-off and marks checklist DONE without habit evidence |
| **Expected snap point** | False maturity; chaos/tabletop passes while human gate open |
| **Detection evidence** | Checklist rows `NOT_STARTED`; worksheet §5 unchecked boxes; `Task closed ≠ OPSEC proven` |
| **Recovery evidence** | Revert checklist state; version history v1.8 |
| **Rebuild / harden** | Mandatory dual read: worksheet + checklist `state` column |
| **Safe Level 2 test** | Audit: any OPSEC-4/5/9 `DONE` without `last_done` + verify_method → FAIL |
| **Hard stops** | **Do not close OPSEC-4/5/9 in chaos tasks** |

### Scenario 7 — Suspicious vendor email, no decision log

| Field | Content |
|-------|---------|
| **Assumption attacked** | OPSEC-9 habit exists because template exists |
| **Professional break attempt** | Urgent vendor wire request; operator investigates without timestamped log |
| **Expected snap point** | No Axis B evidence; tunnel vision; wrong payment action |
| **Detection evidence** | Missing `decision_log_id` + `opened_at` before investigation (war room §7) |
| **Recovery evidence** | `OPSEC_HUMAN_GATE_DRILL_2026-06-30.md` §6 template; pause + known-good channel |
| **Rebuild / harden** | OPSEC-9 real entry when evidence ready; polymorphic brief T1566.002 → OPSEC-4 first |
| **Safe Level 2 test** | Tabletop walkthrough scenario 7 with timed first log entry (paper only) |
| **Hard stops** | No real payment actions in drill |

### Scenario 8 — Non-MMI project enters MMI scope

| Field | Content |
|-------|---------|
| **Assumption attacked** | `MMI_ACTIVE_SCOPE.md` blocks drift |
| **Professional break attempt** | Seed Social Architect / DAX task; reference NorthStar bridge in intel brief |
| **Expected snap point** | Queue pollution; wrong agent work |
| **Detection evidence** | `reload_mmi_pipes.py` → `Non-MMI active task`; task id lacks `mmi-` prefix |
| **Recovery evidence** | Pause non-MMI tasks; `is_mmi_task()` guard in reload |
| **Rebuild / harden** | Hard stops in chaos + intel docs; pipeline description reaffirms |
| **Safe Level 2 test** | Attempt seed fake task in sandbox `tasks.json`; assert reload BLOCKED |
| **Hard stops** | No NorthStar, web/, npm without Matt auth |

### Scenario 9 — Backup hash mismatch

| Field | Content |
|-------|---------|
| **Assumption attacked** | Local archive bytes = remote bytes = push log SHA |
| **Professional break attempt** | Partial rclone upload; local tar edited after push; log append without verify |
| **Expected snap point** | False PASS; restore corrupt |
| **Detection evidence** | `local_sha256` vs `remote_bytes` vs on-disk `sha256sum`; rclone `--checksum` exit 0 |
| **Recovery evidence** | Re-push from known-good local tar; OPSEC-7 `tar -tzf` |
| **Rebuild / harden** | Never skip checksum on push; OPSEC-7 weekly |
| **Safe Level 2 test** | Level 2: corrupt sandbox tar one byte; assert push or verify fails |
| **Hard stops** | No delete remote archive to "fix" |

### Scenario 10 — Duplicate task closeout / false PASS

| Field | Content |
|-------|---------|
| **Assumption attacked** | `complete_task.py` once = honest closeout |
| **Professional break attempt** | Close task with PASS while deliverable missing; or close twice with conflicting summaries |
| **Expected snap point** | Pipeline thinks work done; artifact absent or wrong |
| **Detection evidence** | `output_files` exist on disk; sign-off in artifact matches `result_summary` |
| **Recovery evidence** | Reopen task or new amend task; fix artifact |
| **Rebuild / harden** | Closeout requires output path + spot-check block in summary |
| **Safe Level 2 test** | Sandbox: complete task with fake output path; assert file-exists check in review |
| **Hard stops** | No amend `completed_at` without Matt |

---

## 5. Level 1 findings table (tabletop — no live injection)

| ID | Scenario | What would snap (today) | What held (today) | Detected? | Missed if careless? | Priority |
|----|----------|-------------------------|-------------------|-----------|---------------------|----------|
| F1 | Stale war room | Operator trust stale terminal | `war_room.py --json` works when run | Yes, if refreshed | **Yes** | High |
| F2 | DRY vs mental pending | Confusion after honest close | `Task closed ≠ OPSEC proven` in worksheet | Partial | **Yes** | Medium |
| F3 | Global stat in headline | Brief integrity | Both briefs quarantined vendor % | Yes (current files) | Regression risk | Medium |
| F4 | Manifest gap | Restore missing new files | Allowlist covers `mmi/project_brain` tree | After push | **Yes** if no post-edit push | High |
| F5 | Restore path pressure | Wrong archive picked | Push log tail + restore proof doc | If trained | **Yes** under stress | High |
| F6 | OPSEC false DONE | Maturity lie | Checklist still NOT_STARTED | Yes (today) | **Yes** if reader lazy | **Critical** |
| F7 | No decision log | Payment mistake | Template exists; habit not proven | N/A — habit open | **Yes** | **Critical** |
| F8 | Non-MMI scope | Wrong work | `is_mmi_task()` + scope doc | Yes | Low if guards used | Medium |
| F9 | Hash mismatch | Corrupt cold mirror | Checksum on push PASS history | On push | Silent if verify skipped | High |
| F10 | False PASS closeout | Pipeline lie | Output files + sign-off pattern | On review | **Yes** if rushed | High |

**Level 1 summary:** Architecture and docs **hold** under analysis. Highest snap risk is **human/interpretation layer** (F6, F7, F2, F5) — consistent with known operator-risk, not a hidden pipeline bug.

---

## 6. Pass / fail criteria

### Level 1 tabletop (this document)

| Criterion | Pass | Fail |
|-----------|------|------|
| Doctrine defined | Professional destruction + evidence + rebuild stated | Missing or vague |
| Levels 1–4 defined | Yes, L4 prohibited | Missing levels |
| 10 scenarios documented | Full table §4 | <10 or missing columns |
| Attack surfaces mapped | §2 complete | Code-only focus |
| Live fault injection | **Not run** | Destructive test run without auth |
| OPSEC-4/5/9 state | Unchanged NOT_STARTED | Marked DONE in chaos task |
| Evidence for PASS claim | This doc + baseline §3 | "Chaos done" without evidence |

**Level 1 result:** **PASS WITH REVISIONS** — doctrine and Level 2 readiness defined; live injection not run; OPSEC honesty preserved.

### Level 2 readiness gate (future)

Pass when at least **3** sandbox scenarios executed with captured before/after evidence (F4 manifest dry-run, F1 war room stale, F5 restore-path timed drill recommended first).

---

## 7. Remediation list (rebuild from evidence)

| ID | Finding | Rebuild action | Owner | When |
|----|---------|----------------|-------|------|
| R1 | F6/F7 human gate open | Matt supplies OPSEC-4/5/9 evidence → checklist only | Matt | When ready |
| R2 | F4 post-edit manifest | B2 push after chaos doc + task closeout | Matt/Cursor | After this task close |
| R3 | F5 restore clarity | Add `MMI_LATEST_GOOD_ARCHIVE.md` one-liner stub in status/ | Cursor PM | Level 2 prep |
| R4 | F1 stale war room | War room cheatsheet bullet: refresh before act | Cursor PM | Level 2 prep |
| R5 | F3 headline regression | Brief amend spot-check grep in closeout template | Cursor PM | Next brief |
| R6 | Level 2 program | Seed `mmi-chaos-sandbox-v2` after v1 close | Matt | Next auth |

**Not remediation:** pretending worksheet = habit; closing OPSEC-4/5/9 without evidence.

---

## 8. Scope creep resistance (chaos program)

Chaos testing **must not** become:

- SOAR / EDR / endpoint agent build  
- Live malware or ransomware simulation  
- Automated enforcement of OPSEC  
- NorthStar or non-MMI project work  
- Proof that operator habits exist when checklist says NOT_STARTED  

---

## 9. Relationship to human-gate closeout

```text
Human-gate task:     CLOSED (theory + criteria + §8 addendum)
OPSEC-4/5/9:         NOT_STARTED (known operator-risk)
Chaos Level 1:       Documents that honesty — Scenario 6 & 7 test it
```

Chaos does **not** replace human-gate evidence. It verifies the **repo tells the truth** about that gap.

---

## Sign-off

**PASS WITH REVISIONS**

- Professional destruction doctrine and chaos levels defined.  
- Ten scenarios with full break/design columns.  
- Level 1 findings table and remediation list filed.  
- **No live fault injection performed.**  
- OPSEC-4/5/9 states not modified.  
- Level 2 sandbox execution remains future authorized work.

**North star retained:**

```text
destroy professionally, rebuild from evidence
```

---

## 10. Chaos lane status (recorded 2026-07-01)

```text
Chaos lane:
- Level 1 tabletop doctrine: COMPLETE — PASS WITH REVISIONS
- Level 2 sandbox testing: NOT STARTED (seed after Level 1 B2 mirror)
- Level 3 reversible fault injection: NOT STARTED
- Level 4 destructive/live chaos: PROHIBITED
```

**Level 1 is complete, but not chaos-proven yet.** Doctrine and target list exist; sandbox copy has not been broken.

**Focus:** interpretation layer — misreading evidence as completion, stale state as current, worksheet as habit, brief as more verified than it is, restore path as obvious under pressure.
