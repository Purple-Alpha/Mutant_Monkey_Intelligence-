# MMI Autonomous Brain — Tier 2C Contradiction / Stale-State Report-Only Detection Contract

**Status:** §11 SIGNED 2026-06-19 by Matt Nichol. Signing approves **contract terms only** with **Mode A** selected (stdout-only, read-only, zero file-write report CLI only). Signing does **not** authorize implementation, `scripts/mmi_contradiction_report.py`, tests, fixtures, or `mmi/reports/`. **Mode B remains parked** (not selected at signature). Separate explicit build authorization is required before any Tier 2C implementation; first authorized build slice must be **Mode A only**.

**Classification:** `SIGNED_CONTRACT` · Tier 2C tooling slice · not implemented

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar` (Mutant Monkey Security)

**Parent doctrine:** `mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md` (review material — not signed)

**Tier 1 prerequisite:** Tier 1 passive foundation complete (`MMI-DEC-021`; F1–F5)

**Tier 1 contract:** `mmi/MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_CONTRACT_DRAFT.md` (§11 SIGNED 2026-06-18)

**Tier 2A prerequisite:** Tier 2A Mode A packet intake complete (`MMI-DEC-025`; `10fd8d6`; hygiene `a66b088`)

**Tier 2A contract:** `mmi/MMI_AUTONOMOUS_BRAIN_TIER2A_WORKER_PACKET_INTAKE_CONTRACT_DRAFT.md` (§11 SIGNED 2026-06-19)

**Tier 2B prerequisite:** Tier 2B Mode A passive registry complete (`MMI-DEC-028`; `e374a40`); initial completed rows seeded and hygiene-closed (`MMI-DEC-029`; `bcfc4e8`; hygiene `9d1f54f`)

**Tier 2B contract:** `mmi/MMI_AUTONOMOUS_BRAIN_TIER2B_PASSIVE_TASK_REGISTRY_CONTRACT_DRAFT.md` (§11 SIGNED 2026-06-19)

**Date:** 2026-06-19

**Draft authorization:** `MMI_AUTONOMOUS_BRAIN_TIER2C_CONTRADICTION_STALE_STATE_CONTRACT_DRAFT` only

**Wording patch:** 2026-06-19 — Tier 2C contract review PASS WITH CHANGES (dispatcher/verify citation boundary, forbidden-vocabulary scope, E-01 advisory wording, no-renaming authority). Contract wording only; not implementation.

**§11 signature:** 2026-06-19 — Mode A selected (stdout-only, read-only, zero file-write); Mode B not selected (parked). Signing is not build authorization.

---

## 1. Executive summary

This contract defines **Tier 2C Contradiction / Stale-State Report-Only Detection** — a **read-only** tooling slice that helps MMI and Matt **identify possible** contradictions, stale state, naming drift, and evidence mismatches across MMI governance surfaces.

Tier 2C answers **observability questions** such as:

- Does `MMI_CURRENT_STATE.md` prose disagree with a registry row?
- Does a registry row claim `COMPLETE` without sufficient closeout evidence?
- Does a signed contract exist but the registry still says `DRAFT_CONTRACT`?
- Does a build commit exist but the registry still says `SIGNED_CONTRACT`?
- Does a row claim `BUILD_AUTHORIZED` without explicit Matt authorization evidence?
- Are legacy names (Swarm Command Center, NorthStar, etc.) used in **active** MMI governance where current wording should apply?
- Are parked, rejected, superseded, `CONTRADICTION`, or `DO_NOT_USE` items cited as live authority without evidence?
- Are stale commit hashes, old statuses, or obsolete authority paths still cited as current?

Tier 2C **does not** answer:

- What should be built next?
- Which task should be selected?
- Which worker should be assigned?
- Whether a task is authorized to build.
- Whether a task is complete.
- Whether the dispatcher should change routing.

Tier 2C creates **report-only mechanics only**. It is a **narrow AUTH-7 tooling slice** (report-only default per review material). It does **not** create AUTH-5, does **not** feed `scripts/mmi_dispatch.py`, does **not** replace `python3 scripts/mmi_dispatch.py --verify`, does **not** replace `scripts/detect_drift.py` or `scripts/verify_build_truth.py`, and does **not** auto-block, auto-halt, or auto-repair anything.

Future implementation (only after Matt §11 on **this** contract **plus** separate explicit build authorization) may add:

- **Mode A (default):** stdout-only report CLI (e.g. `scripts/mmi_contradiction_report.py`) — **zero file-write authority**
- **Mode B (parked):** optional report file under `mmi/reports/` — **only if Matt explicitly authorizes later**; still no registry/current-state/decision-log/intake writes

Signing this contract (future §11) approves **contract terms only**. It does **not** authorize implementation, code, tests, or report fixtures.

---

## 2. Signed authority base

| Layer | Artifact | Status | Relevance to Tier 2C |
|---|---|---|---|
| Vision / floor | `VISION.md`, `AGENTS.md` | Active | No proxy decisions; no autonomy laundering; no forbidden-language slips |
| Tier 1 F1 | `mmi/MMI_REPO_SURFACE_REGISTRY.md` | Passive | Closed read surfaces; forbidden inference rules; conflict handling doctrine |
| Tier 1 F2 | `mmi/MMI_TASK_REGISTRY_SCHEMA.md` | Passive schema | Field vocabulary baseline for registry cross-checks |
| Tier 1 F3 | `mmi/MMI_WORKER_COMPLETION_PACKET_TEMPLATE.md` | Passive template | Closeout evidence shape for `COMPLETE` mismatch checks |
| Tier 1 F4 | `mmi/MMI_DECISION_AUDIT_APPENDIX_SCHEMA.md` | Passive schema | Selection history separate; Tier 2C does not populate appendix |
| Tier 1 F5 | `mmi/MMI_AUTONOMOUS_BRAIN_STAGE1_GAPS.md` | Gap callout | Contradiction tooling gap; Tier 2C closes **report-only** slice only |
| Review material | `mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md` | Review only | AUTH-7 report-only default; Tier 1 manual flag vs AUTH-7 automation boundary |
| Tier 2A | `mmi/MMI_AUTONOMOUS_BRAIN_TIER2A_WORKER_PACKET_INTAKE_CONTRACT_DRAFT.md` | §11 SIGNED | Packet admissibility separate; Tier 2C does not run packet intake |
| Tier 2A impl | `scripts/mmi_packet_intake.py` | Mode A built | Structural packet check only; Tier 2C does not call or wrap it |
| Tier 2B | `mmi/MMI_AUTONOMOUS_BRAIN_TIER2B_PASSIVE_TASK_REGISTRY_CONTRACT_DRAFT.md` | §11 SIGNED | Registry lifecycle vocabulary; Tier 2C reads registry; never writes |
| Tier 2B impl | `mmi/MMI_TASK_REGISTRY.yaml` | Mode A built | Passive human-maintained rows; `dispatcher_reads: false` |
| Tier 2B rules | `mmi/MMI_TASK_REGISTRY_UPDATE_RULES.md` | Procedural | Human edit rules; Tier 2C cites for mismatch context |
| Routing | `scripts/mmi_dispatch.py` | Untouched by Tier 2C | Operational routing truth; Tier 2C does **not** execute, import, or call dispatcher; human-supplied `--verify` text may be cited in evidence only |
| Drift tools | `scripts/detect_drift.py`, `scripts/verify_build_truth.py` | Existing | Independent truth tools; Tier 2C does not replace or invoke for routing |
| MMI records | `mmi/MMI_DECISION_LOG.md`, `mmi/MMI_INTAKE_RECORDS.md` | Human-maintained | Evidence cross-check surfaces; not replaced or appended by Tier 2C |
| Current state | `MMI_CURRENT_STATE.md` | Routing-authority prose | Tier 2C reads; never writes routing block or prose |

**AUTH-5 autonomous task selection remains blocked** before, during, and after Tier 2C unless a **standalone** future gate explicitly authorizes AUTH-5. Tier 2C cannot be bundled with AUTH-5 authorization.

**Registry-fed routing remains forbidden.** Tier 2C must not create registry-fed routing or cause the dispatcher to read the registry.

---

## 3. Problem statement

After Tier 1–2B, MMI has:

- passive evidence surfaces (F1)
- structural packet intake (Tier 2A)
- a human-maintained task registry with completed historical rows (Tier 2B)

But **no read-only cross-surface scanner** that systematically compares registry rows, current state prose, decision log entries, intake records, signed contracts, and git evidence for **possible** contradictions or stale references.

Today, mismatches are caught by:

- human session review
- `python3 scripts/mmi_dispatch.py --verify` (routing/build-truth/doctrine)
- `scripts/detect_drift.py` (cross-artifact dispatcher-input integrity)
- `scripts/verify_build_truth.py` (docs vs code/git)

Those tools do **not** specialize in registry-vs-MMI-record lifecycle alignment, legacy naming drift in active governance, or `DO_NOT_USE` / superseded revival patterns across the task registry.

Without Tier 2C, contradiction and stale-state detection remains manual — increasing session rediscovery risk and making "registry says X but decision log says Y" harder to audit before closeout.

Tier 2C closes the **report-only contradiction/stale-state detection** slice in F5. It does **not** close AUTH-5, registry-fed routing, full AUTH-7 automated halt, AUTH-3B write automation, AUTH-4 prompts, or AUTH-6 dashboards.

---

## 4. Exact Tier 2C scope

### 4.1 In scope (implementation — only after §11 + separate build authorization)

| Item | Description |
|---|---|
| Report CLI (Mode A default) | Read-only CLI (e.g. `scripts/mmi_contradiction_report.py`); stdout-only findings report |
| Read-only inputs | Named MMI governance files listed in §7 only; optional read of `git log` / `git show` for commit existence checks — **read only** |
| Finding emission | Structured report-only findings with category, severity, evidence cites, and human-readable explanation |
| Cross-surface rules | Registry vs current state, decision log, intake, contracts, commit references, naming drift |
| Synthetic tests | Focused tests with fixture files only; no production MMI file mutation in tests |
| Mode A (default) | Stdout-only; **zero file-write authority** |
| Mode B (parked) | Optional report file under `mmi/reports/` — only if Matt names Mode B in separate build authorization |

**First implementation slice:** **Mode A only** — stdout-only report CLI — unless Matt explicitly names Mode B in separate build authorization.

### 4.2 Out of scope (hard limits)

| Item | Rule |
|---|---|
| `scripts/mmi_dispatch.py` | No edits, wraps, imports, execution, subprocess calls, or feeding dispatcher input (**AUTH-2-EDIT** not authorized). Tier 2C tooling must **not** execute `mmi_dispatch.py`, must **not** import `mmi_dispatch.py`, and must **not** call `python3 scripts/mmi_dispatch.py --verify`. Human-supplied pasted verify output, human-provided captured text, or a human-provided read-only file path may be cited as evidence only — citation does not make Tier 2C a verifier |
| Registry-fed routing | Tier 2C must not cause dispatcher to read registry or change routing |
| AUTH-5 | Autonomous task selection **not** created or enabled |
| AUTH-4 | Auto-prompt generation **not** authorized |
| AUTH-6 | Dashboard / UI **not** authorized |
| Full AUTH-7 automated halt | Tier 2C is **report-only**; no automated BLOCK/halt/repair |
| AUTH-3B | No automated MMI record writes |
| `MMI_CURRENT_STATE.md` | Tier 2C tooling **never writes** routing block or prose |
| `mmi/MMI_DECISION_LOG.md` | No automated decision-log rows |
| `mmi/MMI_INTAKE_RECORDS.md` | No automated intake append |
| `mmi/MMI_TASK_REGISTRY.yaml` | No registry mutation; no status transitions; no envelope literal changes |
| Scoreboard / runtime / orchestrator | No changes |
| #47 / #48 | Out of scope |
| Parked roadmap drafts | Out of scope; may report if cited as authority elsewhere |
| Architectapp | Out of scope |
| Always-on hooks / daemons / watchers | Prohibited |
| Auto-sync / auto-verify / auto-commit | Prohibited |
| Replacement of `--verify` | Tier 2C does not replace or supersede dispatcher verify |

---

## 5. Explicit non-goals

Tier 2C must **never**:

1. Select the next task, rank candidates, or emit delegation scores.
2. Assign workers or lanes.
3. Authorize builds, sign contracts, or mark work complete.
4. Change routing MODE, scoreboard rows, or gate registry.
5. Write, append, or delete any routing-authority or MMI record file.
6. Modify the task registry (rows, status, evidence, envelope literals).
7. Emit authority verdict vocabulary on stdout (§8).
8. Auto-block, auto-halt, or auto-repair contradictions.
9. Run in background, on hooks, or on file-watch triggers.
10. Become AUTH-5 or a path to AUTH-5 bundling.
11. Feed `scripts/mmi_dispatch.py` or become dispatcher input.
12. Execute, import, or call `scripts/mmi_dispatch.py` or `python3 scripts/mmi_dispatch.py --verify`.
13. Replace `python3 scripts/mmi_dispatch.py --verify`, `scripts/detect_drift.py`, or `scripts/verify_build_truth.py`.
14. Authorize renaming, bulk find-replace, automated text correction, or historical evidence rewrites (report-only detection only).

---

## 6. Proposed implementation artifact(s)

Future build authorization may create **only** the artifacts named in that authorization. Default Mode A proposal:

| Artifact | Mode | Purpose |
|---|---|---|
| `scripts/mmi_contradiction_report.py` | A (default) | Read-only report CLI; stdout-only |
| `tests/test_mmi_contradiction_report.py` | A | Contract tests T2C-T1–T16 |
| `tests/fixtures/mmi_contradiction/*` | A | Synthetic fixture governance snippets only |

Mode B (parked — separate authorization required):

| Artifact | Mode | Purpose |
|---|---|---|
| `mmi/reports/.gitkeep` or similar | B | Directory convention only if Matt authorizes |
| `mmi/reports/<timestamp>_contradiction_report.txt` | B | Optional human-requested report file output; not auto-written |

**Not authorized by this contract:** registry validator (`mmi_task_registry_validate.py` remains Tier 2B Mode B parked slice), packet intake changes, dispatcher edits, dashboard, hooks.

---

## 7. Read-only source surfaces

Tier 2C tooling may **read only** these surfaces unless a future contract revision expands the list with operator gate:

| Surface | Read purpose | Write |
|---|---|---|
| `MMI_CURRENT_STATE.md` | Routing block + `LAST_COMPLETED` prose cross-check | **Never** |
| `mmi/MMI_TASK_REGISTRY.yaml` | Registry rows, status, evidence, envelope literals | **Never** |
| `mmi/MMI_TASK_REGISTRY_UPDATE_RULES.md` | Human update rules context | **Never** |
| `mmi/MMI_DECISION_LOG.md` | `MMI-DEC-*` authorization and closeout cites | **Never** |
| `mmi/MMI_INTAKE_RECORDS.md` | Intake classification and artifact cites | **Never** |
| `mmi/MMI_REPO_SURFACE_REGISTRY.md` | In-scope surface list; naming and authority boundaries | **Never** |
| `mmi/MMI_AUTONOMOUS_BRAIN_STAGE1_GAPS.md` | Gap context; do not over-claim closure | **Never** |
| `mmi/MMI_TASK_REGISTRY_SCHEMA.md` | Field vocabulary for structural mismatch context | **Never** |
| `mmi/MMI_WORKER_COMPLETION_PACKET_TEMPLATE.md` | Closeout evidence field expectations | **Never** |
| `mmi/*CONTRACT*.md` (§11-signed only) | Signed contract existence and status cross-check | **Never** |
| Human-supplied dispatcher verify evidence | **Citation/reference only** — pasted text, human-provided captured output, or human-provided read-only file path supplied as input; Tier 2C does **not** execute, import, or call `mmi_dispatch.py` or `--verify` | **Never** (tool does not run or modify verify) |
| `git log`, `git show`, `git cat-file` | Commit existence/hash validation for cited evidence | **Never** (read-only git queries only) |

**Explicitly out of read scope for Tier 2C v1 (unless future revision):**

- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (scoreboard lifecycle is `detect_drift.py` / dispatcher domain)
- `core/`, runtime, orchestrator source (not MMI governance cross-check v1)
- Chat transcripts, session memory
- Architectapp paths

Tier 2C may note `DISPATCHER_REGISTRY_BOUNDARY_RISK` if registry content **appears** to claim routing authority. Tier 2C does not read or execute dispatcher source; it may compare registry/registry-evidence text against human-supplied verify citations only.

---

## 8. Report-only output vocabulary

### 8.1 Locked stdout envelope (Mode A)

The report CLI stdout surface uses **only** these top-level tokens:

| Token | Meaning |
|---|---|
| `REPORT_ONLY_FINDINGS` | One or more findings follow; report is advisory only |
| `NO_REPORTABLE_FINDINGS` | No findings matched configured rules in this run |
| `REVIEW_REQUIRED` | Summary flag: at least one finding has severity `REVIEW`, `HIGH_REVIEW`, or `CRITICAL_REVIEW` — **human review suggested**; not authorization |

**Forbidden authority verdicts (never emitted by Tier 2C tooling as its own conclusion):**

`PASS`, `FAIL`, `BLOCK`, `APPROVED`, `VERIFIED`, `COMPLETE`, `BUILD_AUTHORIZED`, `SIGNED`, `PROMOTED`, `SELECTED`, `DELEGATED`, `GATED`, `ACCEPT`, `REJECT`, `NEXT_TASK`, `RECOMMENDED`, `AUTHORIZED`.

**Scope rule:** Forbidden tokens apply to Tier 2C tool-emitted **envelope**, **summary**, **result**, and **finding-verdict** lines only. They must not appear as Tier 2C's own verdict or conclusion.

**Evidence citation exception:** `evidence` / `note` bodies inside finding records may quote external output verbatim — including strings such as `VERDICT: PASS` from human-supplied dispatcher verify captures — without constituting a Tier 2C tool verdict. Quoted text is cited evidence only; Tier 2C still must not emit authority verdicts as its own top-level output.

### 8.2 Finding record shape (stdout / optional Mode B file)

Each finding under `REPORT_ONLY_FINDINGS`:

```yaml
finding_id: T2C-F-<sequential>
category: <closed enum from §9>
severity: INFO | REVIEW | HIGH_REVIEW | CRITICAL_REVIEW
summary: <one-line human-readable observation>
evidence:
  - path: <file path>
    ref: <line/field/commit/MMI-DEC-id>
note: <optional; not authority>
```

Findings are **observations**, not decisions. Matt or explicit `MMI-DEC-*` resolves contradictions.

---

## 9. Finding categories

Closed enum for v1:

| Category | Detects (report-only) |
|---|---|
| `REGISTRY_CURRENT_STATE_MISMATCH` | Registry row vs `MMI_CURRENT_STATE.md` prose claims disagree |
| `REGISTRY_DECISION_LOG_MISMATCH` | Registry `status_evidence` vs `MMI-DEC-*` claims disagree |
| `REGISTRY_INTAKE_RECORD_MISMATCH` | Registry cites vs `INTAKE-*` record disagree |
| `SIGNED_CONTRACT_WITHOUT_REGISTRY_ROW` | §11-signed MMI brain-slice contract exists; no matching registry row — **INFO advisory** unless a signed MMI rule explicitly requires a registry row for that slice |
| `BUILD_COMMIT_WITHOUT_REGISTRY_UPDATE` | Cited build commit exists; registry status not advanced per Tier 2B transition rules |
| `COMPLETE_WITHOUT_CLOSEOUT_EVIDENCE` | Registry `COMPLETE` without required `status_evidence` types |
| `BUILD_AUTHORIZED_WITHOUT_MATT_AUTH` | `BUILD_AUTHORIZED` without `mmi_decision` or `operator_instruction` evidence |
| `LEGACY_NAMING_DRIFT` | Legacy project-brain naming in **active** MMI governance context |
| `SUPERSEDED_ITEM_REINTRODUCED` | `SUPERSEDED` / `DO_NOT_USE` scope cited as live authority |
| `PARKED_ITEM_PROMOTED_WITHOUT_AUTH` | Parked/rejected item appears build-authorized without decision evidence |
| `DO_NOT_USE_REFERENCED_AS_AUTHORITY` | `DO_NOT_USE` row or identifier used as authority cite |
| `STALE_COMMIT_REFERENCE` | Cited commit not in ancestry or does not exist |
| `MISSING_EVIDENCE_LINK` | Required evidence type absent for claimed status |
| `DISPATCHER_REGISTRY_BOUNDARY_RISK` | Registry text/envelope implies dispatcher read, selection, or routing feed |

New categories require contract revision + operator authorization.

---

## 10. Severity labels

Report-only severities — **never auto-block**:

| Severity | Meaning | Auto-block? |
|---|---|---|
| `INFO` | Informational observation; may be expected in historical context | **No** |
| `REVIEW` | Worth human review in active session | **No** |
| `HIGH_REVIEW` | Stronger mismatch; prioritize human review | **No** |
| `CRITICAL_REVIEW` | Severe possible authority confusion; urgent human review | **No** |

**Rule:** Severity influences sort order and `REVIEW_REQUIRED` summary only. No severity may change exit code to gate routing, block commits, or halt dispatcher.

**Suggested default exit codes (Mode A):**

| Code | Meaning |
|---|---|
| `0` | Report completed (`REPORT_ONLY_FINDINGS` or `NO_REPORTABLE_FINDINGS`) |
| `2` | Tool error (parse failure, missing required input file, internal error) |

Exit code `0` **even when** findings include `CRITICAL_REVIEW`. Findings are not failures of the repo — they are observations.

---

## 11. Contradiction detection rules

Rules produce **findings only**. They do not resolve contradictions.

| Rule ID | Condition | Category | Default severity |
|---|---|---|---|
| C-01 | Registry row `status: COMPLETE` but `status_evidence` lacks `commit` + (`mmi_decision` or `worker_packet`) | `COMPLETE_WITHOUT_CLOSEOUT_EVIDENCE` | `HIGH_REVIEW` |
| C-02 | Registry row `status: BUILD_AUTHORIZED` but no `mmi_decision` / `operator_instruction` evidence with explicit build authorization language | `BUILD_AUTHORIZED_WITHOUT_MATT_AUTH` | `CRITICAL_REVIEW` |
| C-03 | Registry `status: SIGNED_CONTRACT` but cited contract file header is DRAFT/UNSIGNED at read time | `REGISTRY_DECISION_LOG_MISMATCH` | `HIGH_REVIEW` |
| C-04 | `MMI-DEC-*` ACCEPT references build artifacts but registry row for same scope remains `SIGNED_CONTRACT` or lower | `BUILD_COMMIT_WITHOUT_REGISTRY_UPDATE` | `REVIEW` |
| C-05 | Registry row `status: DO_NOT_USE` or `SUPERSEDED` cited in another row's `source_evidence` or `status_evidence` as live authority | `DO_NOT_USE_REFERENCED_AS_AUTHORITY` | `HIGH_REVIEW` |
| C-06 | Registry row `status: PARKED` or `REJECTED` but `MMI_CURRENT_STATE.md` prose implies active build authorization for same scope | `PARKED_ITEM_PROMOTED_WITHOUT_AUTH` | `HIGH_REVIEW` |
| C-07 | `MMI_CURRENT_STATE.md` `LAST_COMPLETED` names slice X; registry has no row or row status contradicts closeout | `REGISTRY_CURRENT_STATE_MISMATCH` | `REVIEW` |
| C-08 | Registry `transition_log` shows forbidden jump (per Tier 2B §10.2) without retrospective closeout note | `MISSING_EVIDENCE_LINK` | `REVIEW` |
| C-09 | Registry envelope `dispatcher_reads` or `autonomous_selection` not `false` | `DISPATCHER_REGISTRY_BOUNDARY_RISK` | `CRITICAL_REVIEW` |
| C-10 | Registry envelope `maintained_by` not `human` | `DISPATCHER_REGISTRY_BOUNDARY_RISK` | `CRITICAL_REVIEW` |

**Retrospective historical rows:** Rules C-01 and C-08 must honor Tier 2B retrospective `COMPLETE` notes (e.g. explicit "no ACCEPTED_FOR_REVIEW recorded; historical row only") — do not false-positive when closeout evidence and note satisfy Tier 2B hygiene pattern.

---

## 12. Stale-state detection rules

Stale means **possibly out of date** — Tier 2C reports mismatch; it does not decide correct state.

| Rule ID | Condition | Category | Default severity |
|---|---|---|---|
| S-01 | `status_evidence` or `source_evidence` cites commit hash that does not resolve in `git cat-file -t` | `STALE_COMMIT_REFERENCE` | `HIGH_REVIEW` |
| S-02 | Registry `updated_at` older than cited `MMI-DEC-*` / `INTAKE-*` dates by > policy threshold (default: any inversion) | `REGISTRY_DECISION_LOG_MISMATCH` | `REVIEW` |
| S-03 | `MMI_CURRENT_STATE.md` references LAST_COMPLETED commit/hash superseded by later MMI-DEC closeout not reflected in prose | `REGISTRY_CURRENT_STATE_MISMATCH` | `INFO` |
| S-04 | Registry row references pre-Tier-2B artifact path that no longer exists at cited path | `MISSING_EVIDENCE_LINK` | `REVIEW` |
| S-05 | `last_human_update_ref` in registry does not match any known `MMI-DEC-*` or named operator instruction pattern | `MISSING_EVIDENCE_LINK` | `INFO` |
| S-06 | Intake record cites artifact path; file missing or status changed since intake | `REGISTRY_INTAKE_RECORD_MISMATCH` | `REVIEW` |

---

## 13. Naming-drift detection rules

**Principle:** Flag legacy naming in **active MMI governance** only. Preserve legacy wording in historical evidence, old commits, superseded sections, and quoted citations.

**No-renaming authority:** Tier 2C does **not** authorize renaming, bulk find-replace, automated text correction, or historical evidence rewrites. It reports possible drift only; Matt or explicit `MMI-DEC-*` resolves wording.

### 13.1 Legacy terms (default list)

| Term / pattern | Example contexts |
|---|---|
| `Swarm Command Center` | Active doctrine, routing prose, registry notes |
| `SwarmCommand` (as project brain label) | Active MMI authority claims |
| `NorthStar` (as project identity) | Active governance where `Mutant Monkey Security` / `MMI` is current |
| `old project-brain naming` | Any explicit retired brain label in active authority sections |

### 13.2 Rules

| Rule ID | Condition | Category | Default severity |
|---|---|---|---|
| N-01 | Legacy term in `MMI_CURRENT_STATE.md` routing block or `LAST_COMPLETED` active prose | `LEGACY_NAMING_DRIFT` | `REVIEW` |
| N-02 | Legacy term in `mmi/MMI_TASK_REGISTRY.yaml` `notes` or `status_evidence.note` for non-historical row | `LEGACY_NAMING_DRIFT` | `REVIEW` |
| N-03 | Legacy term in `mmi/MMI_DECISION_LOG.md` entry dated after project identity guard (2026-06-16+) | `LEGACY_NAMING_DRIFT` | `REVIEW` |
| N-04 | Legacy term inside quoted historical evidence, old commit message cite, or `SUPERSEDED` context | — | **No finding** or `INFO` only |
| N-05 | Legacy term in file path string cite (path history) | — | **No finding** |

---

## 14. Evidence mismatch rules

| Rule ID | Condition | Category | Default severity |
|---|---|---|---|
| E-01 | §11-signed MMI brain-slice contract on disk; no matching registry row — emit `INFO` advisory only; not a defect unless a signed MMI rule (e.g. Tier 2B contract/registry update rules) explicitly requires a row for that slice | `SIGNED_CONTRACT_WITHOUT_REGISTRY_ROW` | `INFO` |
| E-02 | `INTAKE-*` references `MMI-DEC-*` not present in decision log | `REGISTRY_INTAKE_RECORD_MISMATCH` | `HIGH_REVIEW` |
| E-03 | Registry `status_evidence.ref` names `MMI-DEC-*` not found in decision log | `REGISTRY_DECISION_LOG_MISMATCH` | `HIGH_REVIEW` |
| E-04 | Registry `status_evidence.ref` names `INTAKE-*` not found in intake records | `REGISTRY_INTAKE_RECORD_MISMATCH` | `HIGH_REVIEW` |
| E-05 | `verify_output` evidence cite lacks `VERDICT:` line and contract E4 expected verify cite | `MISSING_EVIDENCE_LINK` | `INFO` |
| E-06 | Registry cites `mmi/MMI_TASK_REGISTRY.yaml` as completion authority without built-artifact-only note (Tier 2B self-cite pattern) | `DISPATCHER_REGISTRY_BOUNDARY_RISK` | `REVIEW` |

---

## 15. Relationship to other surfaces

| Surface | Relationship |
|---|---|
| **Task registry** | Tier 2C **reads** `mmi/MMI_TASK_REGISTRY.yaml`; compares rows/evidence; **never writes** |
| **Packet intake validator** | Independent tool; Tier 2C does not call `scripts/mmi_packet_intake.py`; packet admissibility ≠ contradiction report |
| **MMI decision log** | Read-only cross-check for `MMI-DEC-*`; does not append decisions |
| **MMI intake records** | Read-only cross-check for `INTAKE-*`; does not append intake |
| **MMI current state** | Read-only; compares prose to registry; does not run `--sync` or edit routing block |
| **Dispatcher verify** | Independent authority check run by humans; Tier 2C does not execute/import/call dispatcher verify; may read human-supplied pasted or file-cited verify text as evidence reference only; does not replace verify |
| **Repo surface registry (F1)** | Defines allowed read surfaces and forbidden inference; Tier 2C must stay within F1 boundaries |
| **Stage 1 gaps (F5)** | Tier 2C closes **report-only** contradiction slice; does not claim full AUTH-7 halt or BLOCK enforcement |
| **detect_drift.py** | Complementary; drift detector governs dispatcher-input integrity; Tier 2C governs registry/MMI-record alignment |
| **verify_build_truth.py** | Complementary; build truth vs docs/code; Tier 2C does not duplicate |

**Authority precedence (unchanged):** Signed contracts + git + operator decisions > registry observations > Tier 2C report findings. Findings never override routing.

---

## 16. Security and authority risks

| Risk | Mitigation in contract |
|---|---|
| **Report-as-verdict** | Forbidden stdout vocabulary (§8); findings labeled report-only |
| **Report-as-routing** | No dispatcher calls; no registry-fed routing; envelope boundary checks |
| **Report-as-selection** | No next-task output; AUTH-5 blocked |
| **Silent repair** | Zero file-write in Mode A; Mode B report file only with separate auth |
| **Authority laundering** | `REVIEW_REQUIRED` is not authorization; severity does not block |
| **False BLOCK** | Tier 2C must not emit `BLOCK`; review material BLOCK contradiction remains manual operator halt |
| **Registry mutation drift** | Digest/immutability tests on routing-authority files |
| **Bundled AUTH-5** | Reject authorizations naming Tier 2C + AUTH-5 together |
| **Over-read exfiltration** | Closed read surface list (§7); no runtime source scraping in v1 |
| **Historical false positives** | Retrospective COMPLETE notes; naming-drift historical carve-out (§13) |

---

## 17. Failure modes

| Failure mode | Detection | Mitigation |
|---|---|---|
| **Report-as-verify** | Operators skip `--verify` because report ran | Contract + closeout discipline: human verify remains required |
| **Report-as-complete** | `NO_REPORTABLE_FINDINGS` treated as closeout PASS | Forbidden vocabulary tests; training: only `--verify` PASS gates routing |
| **Auto-halt creep** | Tool exits non-zero on `CRITICAL_REVIEW` | Exit code policy §10; tests lock `0` on findings |
| **Registry writer creep** | Tool opens registry for write | Mode A digest tests; demotion §18 |
| **Dispatcher coupling** | Tool imports, executes, or calls `mmi_dispatch.py` or `--verify` | T2C-T12; demotion §18 |
| **Finding inflation** | Every naming mention flagged | Historical carve-out tests N-04/N-05 |
| **Stale rule brittleness** | False positives on intentional retrospective rows | Fixture tests with hygiene-closed rows |
| **Mode B scope creep** | Report files become input to routing | Mode B parked; report dir not dispatcher input |
| **AUTH-7 over-claim** | Tier 2C described as full contradiction automation | F5 gap wording; §5 non-goals |

---

## 18. Rollback / demotion plan

### Rollback

- Revert or disable `scripts/mmi_contradiction_report.py` if contract violated
- **Tier 1, Tier 2A, Tier 2B remain untouched** — rollback does not demote prior tiers
- Optional Mode B report files may remain as historical artifacts; delete only by operator choice

### Demotion triggers (immediate)

Disable Tier 2C tooling if:

- tool writes any file outside explicitly authorized Mode B report path
- tool writes registry, `MMI_CURRENT_STATE.md`, decision log, or intake records
- tool imports, executes, calls, or modifies `scripts/mmi_dispatch.py` (including `--verify`)
- tool emits forbidden authority vocabulary (§8)
- tool emits next-task, worker assignment, or selection labels
- tool runs on hooks, daemons, or file watchers
- tool exit code gates routing or replaces `--verify` PASS requirement
- registry envelope literals change due to tooling

Demotion affects **Tier 2C only**.

---

## 19. Falsifiable acceptance tests

Locked vocabulary per §8. Tests use synthetic fixtures under `tests/fixtures/mmi_contradiction/` only.

| Test ID | Name | Pass condition |
|---|---|---|
| T2C-T1 | CLI exists read-only | `scripts/mmi_contradiction_report.py` runs without writing files (Mode A) |
| T2C-T2 | Complete without evidence | Fixture registry `COMPLETE` missing closeout evidence → `REPORT_ONLY_FINDINGS` + `COMPLETE_WITHOUT_CLOSEOUT_EVIDENCE` |
| T2C-T3 | Signed contract no row | Fixture signed contract present; empty registry → finding `SIGNED_CONTRACT_WITHOUT_REGISTRY_ROW` (severity `INFO` per E-01) |
| T2C-T4 | Build commit stale status | Fixture build commit + registry `SIGNED_CONTRACT` → `BUILD_COMMIT_WITHOUT_REGISTRY_UPDATE` |
| T2C-T5 | DO_NOT_USE as authority | Fixture cites `DO_NOT_USE` row as authority → `DO_NOT_USE_REFERENCED_AS_AUTHORITY` |
| T2C-T6 | Legacy naming active | Fixture active MMI section contains `NorthStar` as project identity → `LEGACY_NAMING_DRIFT` |
| T2C-T7 | Legacy naming historical | Fixture historical evidence section with `NorthStar` → **no finding** or `INFO` only |
| T2C-T8 | No file writes Mode A | Run report on fixtures; digest/routing files unchanged |
| T2C-T9 | No registry edit | `mmi/MMI_TASK_REGISTRY.yaml` digest unchanged after run |
| T2C-T10 | No MMI record edit | Decision log and intake digests unchanged |
| T2C-T11 | No current state edit | `MMI_CURRENT_STATE.md` digest unchanged |
| T2C-T12 | No dispatcher execution | Tool does not import, execute, subprocess-call, or invoke `mmi_dispatch.py` or `--verify`; dispatcher file digest unchanged; human-supplied verify text may be read as input evidence only |
| T2C-T13 | Forbidden vocabulary scope | Tool-emitted envelope/summary/result/finding-verdict lines never contain `PASS`, `FAIL`, `BLOCK`, `APPROVED`, `COMPLETE`, `SELECTED`, etc. as Tier 2C conclusions; evidence `note`/`evidence` bodies may quote `VERDICT: PASS` verbatim without being a tool verdict |
| T2C-T14 | Exit code policy | Findings present including `CRITICAL_REVIEW` → exit `0`; parse error → exit `2` |
| T2C-T15 | Retrospective row tolerance | Hygiene-closed Tier 1/2A/2B historical `COMPLETE` fixtures → no false `COMPLETE_WITHOUT_CLOSEOUT_EVIDENCE` |
| T2C-T16 | Human verify after closeout | Human `mmi_dispatch.py --verify` PASS after Tier 2C routing-authority closeout (not report CLI) |

---

## 20. What must not be built in Tier 2C

| Forbidden build | Reason |
|---|---|
| Dispatcher edits or registry-fed routing | AUTH-2-EDIT / routing boundary |
| AUTH-5 autonomous selection paths | Terminal standalone gate |
| Registry machine writer / auto-sync | AUTH-3B not authorized |
| Auto-prompt generation | AUTH-4 not authorized |
| Dashboard / UI | AUTH-6 not authorized |
| Full AUTH-7 automated halt / BLOCK enforcement | Tier 2C is report-only slice only |
| Tier 2B Mode B registry validator | Separate parked slice |
| Hooks, daemons, watchers, background runs | Always-on prohibition |
| Scoreboard / runtime / orchestrator changes | Out of MMI governance slice |
| #47 / #48 implementation | Out of scope |
| Parked draft promotion | Out of scope |
| Architectapp work | Out of scope |
| Replacement of `--verify` / `detect_drift.py` / `verify_build_truth.py` | Independent truth tools |

---

## 21. Sign-off

**§11 SIGNED — Matt Nichol 2026-06-19.**

This §11 signature approves the contract only. It does **not** authorize implementation, `scripts/mmi_contradiction_report.py`, tests, fixtures, `mmi/reports/`, registry mutation, dispatcher edits, or routing changes.

Separate explicit build authorization is still required before creating:

- `scripts/mmi_contradiction_report.py`
- `tests/test_mmi_contradiction_report.py`
- `tests/fixtures/mmi_contradiction/*`
- `mmi/reports/` or any Mode B report file output path

**AUTH-5 autonomous task selection remains blocked.** Registry-fed routing remains forbidden.

**Contract configuration recorded at signature (not build authorization):**

| Setting | Recorded at §11 |
|---|---|
| Selected implementation mode | **Mode A** — stdout-only, read-only, zero file-write report CLI |
| Mode B optional report files | **Not selected — remains parked** |
| Dispatcher execution | **Forbidden** — Tier 2C tooling must not execute, import, or call `mmi_dispatch.py` or `--verify` |
| Registry / MMI record writes by tooling | **Forbidden** |

**Mode B** (optional report file under `mmi/reports/`) remains parked unless Matt separately signs or authorizes Mode B in a future contract revision **and** names Mode B in separate build authorization. **First build authorization, if issued, must name Mode A only.**

> Matt Nichol June 19th 2026

---

## Appendix A — Recommended first build slice

**Mode A only** (stdout-only report CLI):

1. Create `scripts/mmi_contradiction_report.py` — read-only; rules §11–§14; stdout vocabulary §8
2. Create `tests/test_mmi_contradiction_report.py` — T2C-T1–T16
3. Create `tests/fixtures/mmi_contradiction/*` — synthetic snippets only
4. Closeout: `MMI-DEC-*`, `INTAKE-*`, `MMI_CURRENT_STATE.md` `LAST_COMPLETED` update, `MASTER_INDEX.md` entry
5. Human runs `python3 scripts/mmi_dispatch.py --sync` + `--verify` after commit

**Mode B** remains **parked** unless Matt explicitly names it in separate build authorization.

---

## Appendix B — Exact files that would change in future implementation

| File | Mode A | Mode B |
|---|---|---|
| `scripts/mmi_contradiction_report.py` | Create | Same |
| `tests/test_mmi_contradiction_report.py` | Create | Same |
| `tests/fixtures/mmi_contradiction/*` | Create | Same |
| `mmi/MMI_DECISION_LOG.md` | Closeout append | Closeout append |
| `mmi/MMI_INTAKE_RECORDS.md` | Closeout append | Closeout append |
| `MMI_CURRENT_STATE.md` | `LAST_COMPLETED` update | Same |
| `MASTER_INDEX.md` | Index entry | Index entry |
| `mmi/reports/` | — | Optional dir + report output |

**Must not change in Tier 2C build:** `scripts/mmi_dispatch.py`, `mmi/MMI_TASK_REGISTRY.yaml` (except human edits separate from tooling), scoreboard, runtime, orchestrator, #47/#48, Architectapp.

---

## Appendix C — Tests that must pass before Tier 2C closeout

- All T2C-T1–T16 (§19)
- `python3 -m unittest tests.test_mmi_packet_intake -v` — still OK (no Tier 2A regression)
- `python3 scripts/mmi_dispatch.py --verify` — PASS (human-run after closeout; not report CLI)

---

**Implementation remains blocked** until separate explicit operator build authorization for a Tier 2C Mode A slice.

**End of Tier 2C contract. §11 signed; Tier 2C implementation requires separate build authorization (Mode A only). AUTH-5 remains blocked. Registry-fed routing remains forbidden.**
