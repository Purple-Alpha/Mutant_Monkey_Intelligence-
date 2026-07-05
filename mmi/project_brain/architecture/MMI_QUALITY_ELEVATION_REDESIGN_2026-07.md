# MMI Quality Elevation Redesign — 2026-07

**Task:** `mmi-quality-elevation-redesign`  
**Date:** 2026-07-01  
**Authority:** Matt (Super)  
**Mode:** **Review / planning only** — no implementation in this pass  
**Sign-off:** **PASS WITH REVISIONS**

---

## Executive framing

MMI has earned **controlled operational proof**: detection and recovery discipline work when invoked. That is **real proof**, not fake staging — but it is **not full workflow proof** until checks become **mandatory gates** that block bad evidence before it becomes authority.

**Quality standard:**

```text
Good:        detects known-bad when run
Great:       blocks bad evidence before it becomes authority
Outstanding: explains failure, recovers from evidence, hardens from it
```

**Current maturity:** mostly **Good** (H1–H3, L3-06, L3-04, restore validation on `163709`, B2 through `180124`).  
**Redesign target:** define path to **Great** on closeout, intel, OPSEC, backup, and war room — without pretending habit exists or automating enforcement.

**Revision caveat:** This document proposes slices and contracts; Matt authorization required per implementation slice. No Codex/build until slice auth.

---

## 1. Current good controls

| Control | What it proves | Evidence |
|---------|----------------|----------|
| **H1** closeout `output_files` | Claimed outputs must exist before `complete_task.py` accepts closeout | `scripts/mmi_verify.py closeout`; wired in `complete_task.py` when `--output` used |
| **H2** intel §1 / `smb_relevance` grep | Global/vendor stats cannot launder into headline without quarantine tag | `mmi_verify.py intel-brief[s]`; L3-04 staged PASS |
| **H3** latest-good archive stub | Operator restore pointer under pressure | `backup/MMI_LATEST_GOOD_ARCHIVE.md`; validation on `163709` |
| **Restore validation** | Archive extracts; scratch tree passes `--restore-check` | `MMI_LATEST_GOOD_ARCHIVE_VALIDATION_2026-07.md` |
| **B2 cold mirror** | Off-host copy with manifest + SHA256 | Push log; mirrors through `180124` |
| **L3-06** OPSEC false-DONE | Staged checklist fault detected; live OPSEC-4/5/9 unchanged | `MMI_CHAOS_L3-06_*`, `opsec-checklist` |
| **L3-04** headline laundering | Staged §1 Verizon 88% caught; live briefs clean | `MMI_CHAOS_L3-04_*` |
| **Human-gate worksheet** | Theory and criteria documented; task closed ≠ habit proven | `OPSEC_HUMAN_GATE_DRILL_2026-06-30.md` |
| **War room v1** | Pipe, active task, backup tail, read-only orient | `mmi/war_room.py` |
| **Chaos doctrine** | Levels 1–3 defined; Level 4 prohibited | Tabletop, sandbox, Level 3 plan |

---

## 2. What prevents them from being great

| Gap | Symptom | Risk |
|-----|---------|------|
| **Optional verification** | H1 only runs if `--output` passed; H2 not required before brief filing | False PASS closeout; headline regression |
| **War room incomplete truth** | No latest-good SHA, restore-check status, OPSEC-4/5/9 risk, intel MIXED status, chaos gate | Stale panel → wrong action under pressure |
| **Worksheet vs checklist confusion** | Worksheet complete; checklist still NOT_STARTED | Operator assumes habit proven |
| **Latest-good promotion manual** | Stub updated by hand after push; doc mirror ≠ restore-validated archive | Wrong archive under pressure |
| **Detect-only chaos** | L3 proves detection on staging; workflow does not block | Interpretation layer remains primary snap surface |
| **No closeout evidence contract** | `result_summary` prose-only; no required verification JSON | Pipeline lies with plausible text |
| **Intel claim integrity partial** | §5 quarantine works when disciplined; no gate on amend | Canadian headline laundering on amend |
| **OPSEC evidence-lock absent** | `DONE` editable without verify_method contract enforcement | False maturity (T06 class) |

**Core blocker:** tools exist; **workflow does not require them** before authority changes (task completed, brief filed, checklist DONE, archive promoted).

---

## 3. What must be redesigned

| Area | From | To |
|------|------|-----|
| **Closeout** | Optional H1 on `--output` | **Evidence contract**: every completion requires verifiable artifacts + verify pass |
| **Intel filing** | Manual H2 grep | **Brief gate**: §1/smb_relevance scan before index/amend closeout |
| **OPSEC checklist** | Human honesty + dual-read | **Evidence-lock**: `DONE` requires non-empty `last_done` + verify_method class rules |
| **Backup promotion** | Manual H3 stub | **Promotion gate**: SHA + manifest + B2 PASS + restore-check field before stub update |
| **War room** | Pipe + backup tail | **Truth surface**: task, DRY, latest-good, restore status, intel, OPSEC risk, chaos |
| **Chaos program** | Detect in fixtures | **Detect → block → explain** roadmap per scenario class |
| **Operator messaging** | Scattered docs | Single **“task closed ≠ control proven”** visible in war room + closeout |

**Non-goals:** SOAR, EDR, endpoint agents, auto-containment, live malware simulation, NorthStar integration.

---

## 4. Mandatory gates proposal

Gates **block** (exit non-zero / refuse closeout) unless Matt explicitly passes `--force` with logged reason (future slice — default: no force in v1 gates).

| Gate ID | Trigger | Check | Blocks |
|---------|---------|-------|--------|
| **G-CLOSEOUT-1** | `complete_task.py` with any `--output` | H1 `verify_closeout_outputs` | Already partial — extend to **require** `--output` for all PM-tier completions |
| **G-CLOSEOUT-2** | `complete_task.py` Resilience/Verification tier | Run `mmi_verify.py` bundle (H1 + scenario-specific if chaos/intel task) | Missing verification artifact |
| **G-INTEL-1** | New/amend intel brief closeout | H2 `intel-brief` on target path | §1 / smb_relevance violations |
| **G-INTEL-2** | `INTEL_INDEX.md` amend for filed brief | H2 batch must be clean | Index points at dirty brief |
| **G-OPSEC-1** | Checklist row → `DONE` (human edit) | `opsec-checklist` rules: last_done + verify_method class | False DONE (L3-06 rules) |
| **G-BACKUP-1** | Post `--backup-and-push` | local_bytes == remote_bytes; sha in log | False PASS push |
| **G-BACKUP-2** | H3 stub update | Cross-read push log tail + validation doc | Stub/archive mismatch |
| **G-CHAOS-1** | Level 3 execution auth | G0–G6 from Level 3 plan | Batch or live mutation |

**Read-only → mandatory mapping:**

| Current tool | Becomes mandatory at |
|--------------|---------------------|
| `mmi_verify.py closeout` | Every `complete_task.py` with outputs (already); extend to **all** completions with output list |
| `mmi_verify.py intel-brief` | Intel brief task closeout; optional pre-commit hook for `intel/briefs/` |
| `mmi_verify.py opsec-checklist` | Pre-save validation script Matt runs before checklist amend (v1); future: lint on edit |
| Push log byte/sha compare | `mmi_cold_backup.py` post-push self-check (T09 class) |
| `--restore-check` | Latest-good **promotion** after major mirror (see §9) |

---

## 5. War room truth-surface proposal

Extend `mmi/war_room.py` **read-only** panel (implementation slice — spec only here):

```text
┌─ MMI WAR ROOM ─────────────────────────────────────────┐
│ PIPE: LOADED | DRY | HOLD | BLOCKED                    │
│ ACTIVE TASK: id, score, assignee, tier                 │
│ REFRESH: generated_at (warn if > N min stale)          │
├─ TRUTH SURFACE ────────────────────────────────────────┤
│ LATEST-GOOD: name, sha256 (from H3 stub)               │
│ RESTORE-CHECK: PASS|PARTIAL|PENDING (archive id)       │
│ LAST B2: push_file, push_status, byte match            │
│ INTEL: filed briefs count; last H2 batch ok/fail       │
│ OPSEC RISK: OPSEC-4/5/9 → NOT_STARTED (known-risk)     │
│ CHAOS: L3 last scenario + gate (L3-05+ PAUSED)         │
├─ INTERPRETATION WARNINGS ───────────────────────────────┤
│ • Task closed ≠ OPSEC proven                           │
│ • Worksheet ≠ checklist DONE                           │
│ • Push PASS ≠ restore validated (check restore field)  │
│ • Latest B2 mirror ≠ restore-proven archive            │
└────────────────────────────────────────────────────────┘
```

**Data sources (read-only files only):**

| Field | Source |
|-------|--------|
| Active task / DRY | `command_center.build_state()` |
| Latest-good | `backup/MMI_LATEST_GOOD_ARCHIVE.md` parse |
| Restore-check | `status/MMI_LATEST_GOOD_ARCHIVE_VALIDATION_2026-07.md` + stub |
| B2 tail | `MMI_BACKUP_PUSH_LOG.json` |
| Intel H2 status | Last run artifact or lightweight cache file (future) |
| OPSEC-4/5/9 | Parse `OPERATOR_OPSEC_CHECKLIST.md` rows |
| Chaos | Last completed L3 report + `MMI_CHAOS_LEVEL3_PLAN_2026-07.md` gate line |

**Cheatsheet addition:** “Refresh before act” (R4) — re-run war room before closeout/restore/intel amend.

---

## 6. Closeout evidence contract

Every task completion should carry **machine-checkable** evidence, not prose alone.

**Required fields (future `tasks.json` / closeout protocol):**

| Field | Requirement |
|-------|-------------|
| `output_files` | Non-empty for artifact tasks; H1 verified |
| `verification_commands` | Optional JSON list of commands run + exit codes |
| `verification_artifact` | Path to JSON under `status/verify/` or task evidence dir |
| `result_summary` | Human prose **plus** sign-off enum: PASS \| PASS WITH REVISIONS \| FAIL |
| `sign_off_tier` | Who accepted revision caveats |

**Tier rules:**

| Tier | Minimum verification |
|------|---------------------|
| Resilience / Verification | H1 + task-specific `mmi_verify` subcommand |
| Security Intel | H2 if brief touched |
| Architecture | H1 on spec path |
| PM bootstrap | H1 on status doc |

**Block closeout if:** H1 missing paths; H2 fail on intel task; no `output_files` when instruction lists Required output.

---

## 7. OPSEC evidence-lock rules

Preserve **honesty** for OPSEC-4/5/9 while making false DONE **structurally obvious**.

| Rule | Enforcement |
|------|-------------|
| **E1** | `DONE` requires non-empty `last_done` (ISO date) |
| **E2** | `verify_method` for OPSEC-4/5/9 cannot contain only “worksheet”, “dry-run”, “template” without real habit evidence class |
| **E3** | Worksheet completion **never** auto-flips checklist row — separate Matt action with real verify_method |
| **E4** | War room shows OPSEC-4/5/9 as **KNOWN OPERATOR-RISK** while NOT_STARTED |
| **E5** | Task closed (human-gate) displays banner: **does not change checklist state** |
| **E6** | L3-06 class violations = block if gate G-OPSEC-1 implemented |

**Visible until real evidence:**

```text
OPSEC-4/5/9: NOT_STARTED — known operator-risk (human-gate theory complete; habit not proven)
```

No fabricated `last_done`. Checklist remains source of truth for habit; worksheet remains research/training input only.

---

## 8. Intel claim-level integrity model

**Layers:**

| Layer | Content | Gate |
|-------|---------|------|
| **L0 Headline** | §1 Threat summary; ATT&CK `smb_relevance` | H2 mandatory — zero vendor % / unquarantined vendor names |
| **L1 Canadian primary** | StatCan, CCCS, CIRA (labeled survey) | Allowed in §1 with source framing |
| **L2 Quarantined global** | §5 claims table with `[Global Data — Requires Localization]` | Allowed **only** in §5+ |
| **L3 Purged** | Zombie stats per localization pass | Must not appear anywhere |

**Amend workflow (future):**

1. Edit brief draft (live or branch copy).
2. Run `mmi_verify.py intel-brief PATH` → must pass before filing.
3. Update §5 claims table for any new stat — never promote §5 row to §1 without rewrite + re-verify.
4. `INTEL_INDEX.md` amend only after H2 batch clean.

**Canadian headline rule (canonical):**

```text
Global/vendor evidence must never become Canadian headline truth.
```

Detection (H2) → gate (G-INTEL-1) → explain (violations JSON with context line).

---

## 9. Latest-good archive promotion rules

Distinguish **restore-validated archive** vs **latest documentation mirror** (lesson from `163709` vs `164111` vs `180124`).

**Promotion checklist (all required for H3 stub “safe to use”):**

| Step | Check |
|------|-------|
| P1 | `mmi_cold_backup.py --backup-and-push` → `push_status: PASS` |
| P2 | `local_bytes == remote_bytes` |
| P3 | `archive_sha256` recorded in push log |
| P4 | `tar -tzf` spot-check OR prior `--restore-check` on **this** archive |
| P5 | Manifest includes required high-signal paths (chaos, intel, opsec, scripts, tasks) |
| P6 | Matt-authorized promotion note in validation doc or stub version history |

**Stub fields (required):**

- Archive name, SHA256, UTC time, remote path  
- **Restore-check status** (PASS on this archive \| PARTIAL \| PENDING)  
- **Supersedes** pointer  
- **Safe for restore reference?** YES only if P4 PASS on this tarball  

**Rule:** Documentation-only delta (validation note added) does not require re-restoring entire tree if manifest delta is non-material — but stub must **honestly** say restore-check applies to which archive ID.

---

## 10. Chaos detect-to-block roadmap

**Current:** Level 1 doctrine → Level 2 fixtures → H1–H3 → L3 staged flight tests (L3-06, L3-04 complete + mirrored).

**Paused:** L3-05+ until gate redesign slices land.

| Phase | Focus | Detect → Block |
|-------|-------|----------------|
| **Now** | Quality redesign (this doc) | Plan only |
| **Slice A** | Closeout + H1 mandatory | Block false missing output (T10) |
| **Slice B** | Intel H2 mandatory on brief tasks | Block §1 laundering (T03, L3-04) |
| **Slice C** | War room truth surface | Explain stale/wrong archive (T01, T05) — block is operator discipline + visible warnings |
| **Slice D** | OPSEC evidence-lock lint | Block false DONE (T06, L3-06) |
| **Slice E** | Push integrity self-check | Block hash/byte mismatch PASS (T09) |
| **Slice F** | Resume L3-05, L3-03, L3-02, L3-01 one-at-a-time | Each must map to a gate slice |
| **Never** | Level 4 | **PROHIBITED** |

**Level 3 after redesign:**

- Continue **one scenario · one rollback · one evidence packet**  
- Require **gate slice** linked to scenario before execution  
- B2 mirror after each flight test  
- No batch; no live OPSEC/intel mutation without per-scenario auth  

**Controlled operational proof** remains valid; **full workflow proof** requires corresponding gate implemented.

---

## 11. Priority rebuild list

Ordered by **risk reduction / effort** (Matt auth per slice):

| Priority | Slice | Delivers | Depends on |
|----------|-------|----------|------------|
| **P0** | Document-only (this task) | Redesign spec | — |
| **P1** | G-CLOSEOUT-1/2 — require outputs + verify JSON on Verification tier | Blocks T10 class | H1 exists |
| **P2** | G-INTEL-1 — intel task closeout runs H2 | Blocks T03 / L3-04 class | H2 exists |
| **P3** | War room truth surface v1.2 | Explains T01/T05/DRY confusion | Read-only parse |
| **P4** | G-BACKUP-1 push byte/sha self-check | Blocks T09 class | `mmi_cold_backup.py` |
| **P5** | H3 promotion helper script (read-only validate, human stub update) | Reduces restore ambiguity | Validation doc |
| **P6** | G-OPSEC-1 opsec-checklist on amend helper | Blocks T06 / L3-06 class | L3-06 rules |
| **P7** | Resume L3-05 (staged manifest) | Flight test for P4 | P4 optional |
| **P8** | Closeout evidence contract fields in tasks | Outstanding explain/recover | P1 |
| **P9** | L3-03, L3-02, L3-01 | Remaining flight tests | P3, P5, P1 |

---

## 12. What must remain prohibited

| Prohibition | Reason |
|-------------|--------|
| **Level 4** destructive/live chaos | Irreversible risk; no rollback contract |
| Live malware / ransomware simulation | Out of scope; not local-first MMI |
| SOAR, EDR, endpoint agents, auto-containment | Product scope escape |
| Fabricating OPSEC-4/5/9 DONE or `last_done` | Integrity violation |
| Worksheet → checklist auto-promotion | Human-gate honesty |
| B2 delete/overwrite | Recovery path destruction |
| Batch Level 3 | Flight-test discipline |
| NorthStar / non-MMI scope in active queue | Scope lock |
| Claiming chaos-proof without gate implementation | Interpretation honesty |
| Automation that enforces payment/wire/action | Advisory-only MMI |

**Level 4 discussion threshold (default: do not discuss):**

Would require: multi-operator runbook, isolated environment, legal/insurance review, explicit rollback SLA, and Matt written authorization — **none requested**. **Level 4 remains PROHIBITED.**

---

## 13. Recommended next implementation slices (risk reduction order)

### Slice 1 — Closeout gate hardening (P1)

- **Scope:** `complete_task.py` — require `--output` for defined task tiers; optional `--verify-json` path; fail if H1 fails.  
- **Risk:** Low — extends existing H1.  
- **Proves:** T10 blocked at workflow.  
- **Not in slice:** Auto-seed changes, pipeline rewrites.

### Slice 2 — Intel brief closeout gate (P2)

- **Scope:** Wrapper or `complete_task.py` hook for intel task IDs → run H2 before save.  
- **Risk:** Low — read-only scan.  
- **Proves:** L3-04 class blocked on filing path.

### Slice 3 — War room truth surface (P3)

- **Scope:** Read-only parsers for H3 stub, validation doc, OPSEC-4/5/9, chaos status, intel last-scan.  
- **Risk:** Low — display only.  
- **Proves:** T01/T02/T05 visibility; “refresh before act”.

### Slice 4 — Push integrity check (P4)

- **Scope:** Post-push assert in `mmi_cold_backup.py` local/remote bytes + sha.  
- **Risk:** Low — fails push record, not live tree.  
- **Proves:** T09 class.

### Slice 5 — OPSEC amend helper (P6)

- **Scope:** `mmi_verify.py opsec-checklist` before Matt manual checklist edit (documented SOP).  
- **Risk:** Medium — human process, not file watcher.  
- **Proves:** L3-06 class on amend path.

### After slices 1–3 minimum — Matt review + B2 mirror

Then consider **L3-05** (staged manifest mismatch) as next flight test — **not before** slice 4 recommended.

---

## Design question answers (summary)

| Question | Answer |
|----------|--------|
| Which checks become mandatory? | H1 all artifact closeouts; H2 intel tasks; opsec-checklist on DONE edits; push integrity on backup |
| Where H1/H2/H3 run? | `complete_task.py`; intel filing wrapper; post-push + stub promotion helper |
| OPSEC-4/5/9 visibility? | War room KNOWN OPERATOR-RISK; never fabricated DONE |
| War room display? | §5 truth surface proposal |
| Prevent global → Canadian headline? | G-INTEL-1 + claim-level model L0–L3 |
| Prevent worksheet = habit? | E3/E5 evidence-lock; war room banner |
| Latest-good promotion? | §9 P1–P6 checklist |
| Level 3 after redesign? | Paused until P1–P3; then L3-05 one-at-a-time with gate link |
| Level 4? | **PROHIBITED** — no further planning |

---

## Hard stops honored (this task)

- No implementation or code changes  
- No Level 3 execution or L3-05  
- No OPSEC/intel/B2 mutation  
- No automation expansion  
- Level 4 beyond PROHIBITED statement  

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | Initial quality elevation redesign — PASS WITH REVISIONS |
