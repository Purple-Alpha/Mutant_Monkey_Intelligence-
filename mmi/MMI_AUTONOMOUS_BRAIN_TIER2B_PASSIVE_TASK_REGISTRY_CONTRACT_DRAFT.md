# MMI Autonomous Brain — Tier 2B Passive Task Registry Implementation Contract

**Status:** DRAFT UNSIGNED — contract terms only. **Does not authorize implementation.** No registry instance file, no validator code, no dispatcher changes.

**Classification:** `DRAFT_CONTRACT` · Tier 2B tooling slice · not implemented

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar` (Mutant Monkey Security)

**Parent doctrine:** `mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md` (review material — not signed)

**Tier 1 prerequisite:** Tier 1 passive foundation complete (`MMI-DEC-021`; F1–F5)

**Tier 1 contract:** `mmi/MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_CONTRACT_DRAFT.md` (§11 SIGNED 2026-06-18)

**Tier 2A prerequisite:** Tier 2A worker packet intake contract signed (`MMI-DEC-024`; `e08792a`); Mode A validator built (`MMI-DEC-025`, `10fd8d6`; hygiene `a66b088`)

**Tier 2A contract:** `mmi/MMI_AUTONOMOUS_BRAIN_TIER2A_WORKER_PACKET_INTAKE_CONTRACT_DRAFT.md` (§11 SIGNED 2026-06-19)

**Date:** 2026-06-19

**Draft authorization:** `MMI_AUTONOMOUS_BRAIN_TIER2B_PASSIVE_TASK_REGISTRY_CONTRACT_DRAFT` only

**Wording patch:** 2026-06-19 — Tier 2B contract review PASS WITH CHANGES (DO_NOT_USE non-deletion, §9.1 guards, F2 enum relationship, AUTH-3B boundary, §13 F4/F5, test wording).

---

## 1. Executive summary

This contract defines **Tier 2B Passive Task Registry Mechanics** — a **human-maintained**, **passive** task lifecycle registry so MMI can answer, in structured form:

- What tasks exist?
- What is each task's current lifecycle state?
- What contract, decision, intake, commit, or evidence supports that state?
- What is blocked, parked, rejected, superseded, or complete?
- What requires Matt decision?
- What is eligible for review but **not automatically selected**?

Tier 2B creates **registry mechanics only**. It does **not** create AUTH-5. It does **not** let MMI select the next task. It does **not** feed `scripts/mmi_dispatch.py` routing. It does **not** authorize builds, replace signed contracts, replace git truth, or replace `python3 scripts/mmi_dispatch.py --verify`.

Future implementation (only after Matt §11 on **this** contract **plus** separate explicit build authorization) may add:

- **Mode A (default):** a human-maintained registry instance file (`mmi/MMI_TASK_REGISTRY.yaml`) and manual update rules — **no machine writer**
- **Mode B (parked):** a read-only structural registry validator CLI — stdout-only structural checks; **no file writes**

Signing this contract (future §11) approves **contract terms only**. It does **not** authorize implementation, registry population, or validator code.

---

## 2. Signed authority base

| Layer | Artifact | Status | Relevance to Tier 2B |
|---|---|---|---|
| Vision / floor | `VISION.md`, `AGENTS.md` | Active | No proxy decisions; no autonomy laundering |
| Tier 1 F2 | `mmi/MMI_TASK_REGISTRY_SCHEMA.md` | Passive schema | Field vocabulary baseline; Tier 2B extends lifecycle states |
| Tier 1 F3 | `mmi/MMI_WORKER_COMPLETION_PACKET_TEMPLATE.md` | Passive template | Closeout evidence shape for `BUILT_NEEDS_REVIEW` → `COMPLETE` |
| Tier 1 F4 | `mmi/MMI_DECISION_AUDIT_APPENDIX_SCHEMA.md` | Passive schema | Selection history separate; registry is lifecycle not selection audit |
| Tier 1 F5 | `mmi/MMI_AUTONOMOUS_BRAIN_STAGE1_GAPS.md` | Gap callout | `MMI_TASK_REGISTRY` mechanics gap targeted by Tier 2B |
| Review material | `mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md` | Review only | AUTH-3A format vs AUTH-3B writes; registry not dispatcher input |
| Tier 2A | `mmi/MMI_AUTONOMOUS_BRAIN_TIER2A_WORKER_PACKET_INTAKE_CONTRACT_DRAFT.md` | §11 SIGNED | Packet admissibility separate from registry lifecycle |
| Tier 2A impl | `scripts/mmi_packet_intake.py` | Mode A built | Structural packet check; does not read or write registry |
| Routing | `scripts/mmi_dispatch.py` | Untouched by Tier 2B | `collect_delegation_tasks()` remains evidence-derived |
| MMI records | `mmi/MMI_DECISION_LOG.md`, `mmi/MMI_INTAKE_RECORDS.md` | Human-maintained | Evidence cites for registry rows; not replaced by registry |
| Current state | `MMI_CURRENT_STATE.md` | Routing-authority prose | Registry does not replace routing block |

**AUTH-5 autonomous task selection remains blocked** before, during, and after Tier 2B unless a **standalone** future gate explicitly authorizes AUTH-5. Tier 2B cannot be bundled with AUTH-5 authorization.

---

## 3. Problem statement

Today MMI can derive delegation candidates from repo evidence via `scripts/mmi_dispatch.py`, and Tier 1 F2 defines a **schema-only** task shape. There is **no populated, human-maintained registry** that:

- tracks known work items across sessions with stable `task_id`s
- records lifecycle state with evidence links per transition
- preserves blocked, parked, rejected, superseded, and contradictory items without deletion
- separates **eligible for review** from **selected**, **signed** from **build-authorized**, and **built** from **complete**

Without Tier 2B mechanics, task state scatters across scoreboard rows, decision log prose, intake records, and session memory — increasing drift risk and making "what exists but is not next" hard to audit.

Tier 2B closes the **passive registry mechanics** gap in F5. It does **not** close AUTH-5, registry-fed routing, or full AUTH-3B write automation.

---

## 4. Exact Tier 2B scope

### 4.1 In scope (implementation — only after §11 + separate build authorization)

| Item | Description |
|---|---|
| Registry instance file | Human-maintained `mmi/MMI_TASK_REGISTRY.yaml` (preferred) or `.json` if Matt names JSON at build authorization |
| Manual update rules | Documented transition and evidence rules in contract + optional `mmi/MMI_TASK_REGISTRY_UPDATE_RULES.md` if named in build authorization |
| Task rows | Stable `task_id`, lifecycle `status`, evidence cites, blockers, operator flags |
| Schema alignment | Extends F2 field vocabulary; may require F2 cross-reference note (not F2 rewrite without gate) |
| Mode A (default) | Registry file + rules only; **human editor only**; no machine writer |
| Mode B (parked) | Read-only structural validator CLI (e.g. `scripts/mmi_task_registry_validate.py`); stdout-only; **no file writes** |
| Synthetic tests | Focused tests for Mode B validator only; registry fixture files for structural cases |

**First implementation slice:** **Mode A only** — human-maintained registry file and update rules — unless Matt explicitly names Mode B in separate build authorization.

**Populated Mode A registry boundary:** A populated Mode A registry is **human-maintained instance data only**. It is **not** MMI write automation, **not** dispatcher input, **not** registry-fed routing, and **not** AUTH-3B automation.

### 4.2 Out of scope (hard limits)

| Item | Rule |
|---|---|
| `scripts/mmi_dispatch.py` | No edits, wraps, or reads from dispatcher (**AUTH-2-EDIT** not authorized; **registry-fed routing** not authorized) |
| Registry-fed routing | Registry is **not** dispatcher input unless future separate authorization names registry-fed routing |
| AUTH-5 | Autonomous task selection **not** created or enabled |
| AUTH-4 | Auto-prompt generation **not** authorized |
| AUTH-7 | Contradiction tooling automation **not** authorized (manual `CONTRADICTION` status only) |
| AUTH-6 | Dashboard / UI **not** authorized |
| Full AUTH-3B | Registry human maintenance only; no automated MMI record writes from registry tooling |
| `MMI_CURRENT_STATE.md` | Tier 2B tooling **never writes** routing block |
| `mmi/MMI_DECISION_LOG.md` | No automated decision-log rows from registry tooling |
| `mmi/MMI_INTAKE_RECORDS.md` | No automated intake append from registry tooling (Tier 2A Mode B remains separate parked slice) |
| Scoreboard / runtime / orchestrator | No changes |
| #47 / #48 | Out of scope |
| Parked roadmap drafts | No promotion via registry |
| Architectapp | Out of scope |
| Hooks / daemons / watchers | Prohibited |
| Auto-sync / auto-verify / auto-commit | Prohibited |
| Push | Operator instruction only |

---

## 5. Explicit non-goals

Tier 2B must **not**:

- answer "what should MMI do next autonomously?"
- assign workers automatically
- promote tasks automatically
- authorize builds from registry state alone
- mark tasks `COMPLETE` without human/MMI closeout evidence
- emit `NEXT_DELEGATED_TASK`, `RECOMMENDED_DIRECTION`, or routing verdicts
- replace §11-signed contracts as authority
- replace git commits as truth
- replace `python3 scripts/mmi_dispatch.py --verify`
- delete `REJECTED`, `PARKED`, `SUPERSEDED`, `CONTRADICTION`, or `DO_NOT_USE` rows
- collapse registry status into scoreboard lifecycle rows without separate authorization

---

## 6. Proposed implementation artifact(s)

| Artifact | Mode | When | Machine writer |
|---|---|---|---|
| `mmi/MMI_TASK_REGISTRY.yaml` | A | First authorized build | **No** — human only |
| `mmi/MMI_TASK_REGISTRY_UPDATE_RULES.md` | A | Optional if named in build auth | Human only |
| `scripts/mmi_task_registry_validate.py` | B | Only if Mode B separately authorized | Read-only; stdout only |
| `tests/test_mmi_task_registry_validate.py` | B | Mode B only | Test code |
| `tests/fixtures/mmi_task_registry/*.yaml` | B | Mode B only | Fixtures |

**Not created at Tier 2B contract draft:** any of the above files. **Not created without §11 + build authorization.**

**MASTER_INDEX.md** entry update allowed at implementation closeout only.

---

## 7. Registry file shape

Preferred instance path: **`mmi/MMI_TASK_REGISTRY.yaml`**

Human-maintained YAML with a top-level envelope and a `tasks` array. JSON acceptable only if Matt names JSON at build authorization.

### 7.1 Top-level envelope (required)

| Field | Required | Notes |
|---|---|---|
| `registry_version` | yes | Integer; start at `1` for first instance |
| `maintained_by` | yes | `human` only at Tier 2B — no `mmi_automation` value |
| `last_human_update_at` | yes | ISO-8601 UTC |
| `last_human_update_ref` | yes | `MMI-DEC-*`, session note, or operator instruction name |
| `dispatcher_reads` | yes | Must be `false` — literal false |
| `autonomous_selection` | yes | Must be `false` — literal false |
| `tasks` | yes | Array of task records; may be empty at first creation |

### 7.2 Illustrative shape (not live data)

```yaml
registry_version: 1
maintained_by: human
last_human_update_at: 2026-06-19T12:00:00Z
last_human_update_ref: MMI-DEC-EXAMPLE
dispatcher_reads: false
autonomous_selection: false
tasks:
  - task_id: TASK-2026-06-19-001
    title: Tier 2B passive task registry mechanics
    status: DRAFT_CONTRACT
    classification: TIER2B_REGISTRY
    task_or_contract_ref: mmi/MMI_AUTONOMOUS_BRAIN_TIER2B_PASSIVE_TASK_REGISTRY_CONTRACT_DRAFT.md
    source_evidence:
      - mmi/MMI_AUTONOMOUS_BRAIN_TIER2B_PASSIVE_TASK_REGISTRY_CONTRACT_DRAFT.md
    status_evidence:
      - type: contract_draft
        ref: mmi/MMI_AUTONOMOUS_BRAIN_TIER2B_PASSIVE_TASK_REGISTRY_CONTRACT_DRAFT.md
        recorded_at: 2026-06-19T12:00:00Z
    assigned_worker: null
    operator_action_required: yes
    matt_approval_required: yes
    blockers: []
    superseded_by: null
    supersedes: null
    notes: Example only — not live registry data
    created_at: 2026-06-19T12:00:00Z
    updated_at: 2026-06-19T12:00:00Z
```

---

## 8. Required fields per task

Aligned with F2; Tier 2B extensions marked.

| Field | Required | Notes |
|---|---|---|
| `task_id` | yes | Stable string; never reused for different scope; format `TASK-YYYY-MM-DD-NNN` recommended |
| `title` | yes | Short human-readable label |
| `status` | yes | Closed enum (§9) |
| `classification` | yes | Closed enum from F2 or Tier 2B extension with schema note |
| `source_evidence` | yes | Non-empty list of repo paths and/or 40-char commit hashes |
| `status_evidence` | yes | Non-empty list of evidence objects for **current** status (§11) |
| `task_or_contract_ref` | yes when contract-scoped | Path or `MMI-DEC-*` / `INTAKE-*` |
| `assigned_worker` | no | Cursor, Codex, Claude, ChatGPT, Gemini, Grok, Matt — **assignment is informational only** |
| `operator_action_required` | yes | `yes` \| `no` |
| `matt_approval_required` | yes | `yes` \| `no` |
| `blockers` | yes | Array; empty when none; closed vocabulary where possible |
| `superseded_by` | yes when `status: SUPERSEDED` | `task_id` of replacement |
| `supersedes` | no | Prior `task_id` when this row replaces another |
| `created_at` | yes | ISO-8601 UTC |
| `updated_at` | yes | ISO-8601 UTC of last status transition |
| `notes` | no | Human context; not authority |

### 8.1 `status_evidence` object (required per current status)

| Subfield | Required | Notes |
|---|---|---|
| `type` | yes | Closed enum: `contract_draft`, `contract_signed`, `mmi_decision`, `intake_record`, `commit`, `worker_packet`, `operator_instruction`, `scoreboard_row`, `verify_output`, `other` |
| `ref` | yes | Path, `MMI-DEC-*`, `INTAKE-*`, commit hash, or `WORKER_COMPLETION_PACKET` session id |
| `recorded_at` | yes | ISO-8601 UTC when human recorded this evidence link |
| `note` | no | Optional human clarification |

**Rule:** Every task row must have at least one `status_evidence` entry that supports the **current** `status`. Missing or empty `status_evidence` → structurally inadmissible (Mode B validator rejects).

---

## 9. Allowed lifecycle states

Closed enum. **Status labels are lifecycle facts, not authority verdicts.**

| Status | Meaning | Not equivalent to |
|---|---|---|
| `CANDIDATE` | Identified work item; not selected | selected, delegated, or authorized |
| `DRAFT_CONTRACT` | Contract draft exists or in progress | signed or build-authorized |
| `SIGNED_CONTRACT` | §11 contract signed | build authorization |
| `BUILD_AUTHORIZED` | Matt issued explicit build authorization | work complete or verified |
| `BUILT_NEEDS_REVIEW` | Implementation exists; awaits MMI/human review | complete |
| `ACCEPTED_FOR_REVIEW` | Structurally admissible for review (e.g. packet intake accept) | work approved or complete |
| `COMPLETE` | Human/MMI closeout with evidence | autonomous closure |
| `BLOCKED` | Cannot advance; blocker documented | deleted or rejected |
| `PARKED` | Intentionally deferred | rejected or superseded |
| `REJECTED` | Operator or intake rejected scope | deleted |
| `SUPERSEDED` | Replaced by another `task_id` | deleted |
| `CONTRADICTION` | Conflicting evidence; needs human resolution | auto-resolved |
| `NEEDS_MATT_DECISION` | Fork requires Matt | Matt already decided |
| `DO_NOT_USE` | Deprecated identifier or scope; retained for history | deleted, authoritative, or safe to remove from history |

### 9.1 Status semantics guards (locked)

| Status | Guard |
|---|---|
| `CANDIDATE` | **Must not** mean selected, ranked first, or next task |
| `SIGNED_CONTRACT` | **Must not** imply `BUILD_AUTHORIZED` without separate build-auth evidence |
| `BUILD_AUTHORIZED` | **Must** cite `mmi_decision` or `operator_instruction` evidence with explicit build authorization language |
| `BUILT_NEEDS_REVIEW` | **Must not** mean `COMPLETE` |
| `ACCEPTED_FOR_REVIEW` | Accepted into review workflow only — **must not** mean approved, verified, complete, signed, promoted, or build-authorized |
| `COMPLETE` | Lifecycle record backed by closeout evidence (commit + `MMI-DEC-*` and/or admissible worker packet + verify PASS reference as cite only) — **not** verify PASS, routing completion, build authorization, or autonomous promotion |
| `CONTRADICTION` | **Never deleted** by default; remains until human resolution, supersession, or correction evidence is recorded |
| `REJECTED` / `PARKED` / `SUPERSEDED` / `DO_NOT_USE` | **Never deleted** from registry history |

---

## 10. State transition rules

Humans apply transitions manually. No automated transition engine in Tier 2B.

### 10.1 Allowed transitions (positive list)

| From | To | Required evidence |
|---|---|---|
| `CANDIDATE` | `DRAFT_CONTRACT` | `contract_draft` ref |
| `CANDIDATE` | `PARKED`, `REJECTED`, `NEEDS_MATT_DECISION`, `DO_NOT_USE` | matching `type` + ref |
| `DRAFT_CONTRACT` | `SIGNED_CONTRACT` | `contract_signed` ref (§11 signature recorded) |
| `DRAFT_CONTRACT` | `PARKED`, `REJECTED`, `NEEDS_MATT_DECISION`, `BLOCKED` | matching evidence |
| `SIGNED_CONTRACT` | `BUILD_AUTHORIZED` | `mmi_decision` or `operator_instruction` with **explicit build authorization** — not §11 alone |
| `SIGNED_CONTRACT` | `PARKED`, `BLOCKED`, `NEEDS_MATT_DECISION`, `REJECTED` | matching evidence |
| `BUILD_AUTHORIZED` | `BUILT_NEEDS_REVIEW` | `commit` hash for implementation slice |
| `BUILD_AUTHORIZED` | `BLOCKED` | blocker evidence |
| `BUILT_NEEDS_REVIEW` | `ACCEPTED_FOR_REVIEW` | `worker_packet` with Tier 2A `ACCEPT_FOR_MMI_REVIEW` outcome recorded by human |
| `BUILT_NEEDS_REVIEW` | `BLOCKED`, `NEEDS_MATT_DECISION` | matching evidence |
| `ACCEPTED_FOR_REVIEW` | `COMPLETE` | `commit` + `mmi_decision` and/or closeout intake + `verify_output` cite |
| Any non-terminal | `SUPERSEDED` | `superseded_by` + replacement `task_id` |
| Any | `CONTRADICTION` | human flags conflicting cites |
| Any | `NEEDS_MATT_DECISION` | human flags fork |

### 10.2 Forbidden transitions (fail-closed)

| Forbidden transition | Reason |
|---|---|
| `CANDIDATE` → `COMPLETE` | Skips contract, build auth, build, review, closeout |
| `CANDIDATE` → `BUILD_AUTHORIZED` | No signed contract path |
| `SIGNED_CONTRACT` → `COMPLETE` | Skips build and review |
| `SIGNED_CONTRACT` → `BUILT_NEEDS_REVIEW` | Skips explicit build authorization |
| `BUILT_NEEDS_REVIEW` → `COMPLETE` | Skips review admissibility and closeout evidence |
| `BUILD_AUTHORIZED` → `COMPLETE` | Skips built artifact and closeout |
| Any → delete row | Non-deletion rule (§12) |
| Any status change without new `status_evidence` | Evidence required per transition |

Mode B validator (if built) checks structural transition admissibility against §10 when `transition_log` entries are present; it does **not** apply transitions.

### 10.3 Optional `transition_log` (recommended for Mode A)

Per-task append-only list:

```yaml
transition_log:
  - from: SIGNED_CONTRACT
    to: BUILD_AUTHORIZED
    at: 2026-06-19T12:00:00Z
    evidence_ref: MMI-DEC-026
    human_editor: Matt Nichol
```

If present, each entry must match an allowed transition in §10.1.

---

## 11. Evidence-linking rules

| Rule | Requirement |
|---|---|
| E1 | Every task row has non-empty `source_evidence` |
| E2 | Every task row has non-empty `status_evidence` supporting **current** `status` |
| E3 | `BUILD_AUTHORIZED` requires evidence type `mmi_decision` or `operator_instruction` — not `contract_signed` alone |
| E4 | `COMPLETE` requires at least one `commit` evidence and one `mmi_decision` or `worker_packet` + `verify_output` cite |
| E5 | `SIGNED_CONTRACT` requires `contract_signed` evidence pointing to §11-signed contract path |
| E6 | Pasted `VERDICT: PASS` in evidence notes is **citation only** — registry tooling does not emit `PASS`/`FAIL` on stdout |
| E7 | Registry evidence cites do not override signed contracts, git, or dispatcher verify |

---

## 12. Non-deletion and supersession rules

| Rule | Requirement |
|---|---|
| ND1 | Rows with status `REJECTED`, `PARKED`, `SUPERSEDED`, `CONTRADICTION`, or `DO_NOT_USE` are **never deleted** |
| ND2 | Corrections use new `status_evidence` entries and/or `transition_log` append — not silent edits without audit |
| ND3 | `SUPERSEDED` rows must set `superseded_by` to the replacement `task_id` |
| ND4 | Replacement row should set `supersedes` when applicable |
| ND5 | Hard deletion of any row requires **explicit Matt authorization** (corrupt or out-of-scope registry write only) |
| ND6 | `CONTRADICTION` rows remain until human resolves to another status with new evidence |

---

## 13. Relationship to other surfaces

| Surface | Tier 2B relationship |
|---|---|
| **F2 `MMI_TASK_REGISTRY_SCHEMA.md`** | Tier 2B registry instance uses the **Tier 2B lifecycle enum** (§9). If F2 schema wording differs, Tier 2B does **not** silently rewrite F2; F2 may be cross-referenced or revised only under separate authorization |
| **F4 `MMI_DECISION_AUDIT_APPENDIX_SCHEMA.md`** | Registry does not replace decision audit appendix or selection audit history |
| **F5 `MMI_AUTONOMOUS_BRAIN_STAGE1_GAPS.md`** | Tier 2B closes only the passive registry mechanics gap; it does **not** close AUTH-5, registry-fed routing, contradiction tooling, auto-prompting, or dashboard gaps |
| **`mmi/MMI_INTAKE_RECORDS.md`** | Intake rows may be cited in `status_evidence`; registry does not auto-append intake |
| **`mmi/MMI_DECISION_LOG.md`** | `MMI-DEC-*` rows are primary evidence for `BUILD_AUTHORIZED` and `COMPLETE`; registry does not replace decision log |
| **`scripts/mmi_packet_intake.py`** | Tier 2A admissibility is separate; human may cite `ACCEPT_FOR_MMI_REVIEW` in `status_evidence`; validator does not read registry |
| **`MMI_CURRENT_STATE.md`** | Routing block remains dispatcher-derived; registry does not write or replace routing block |
| **`scripts/mmi_dispatch.py --verify`** | Human runs after routing-authority updates; registry tooling does not run verify; `COMPLETE` may cite verify output as evidence only |
| **Scoreboard** | Scoreboard rows may be cited; registry does not flip scoreboard status |
| **Git** | Commit hashes are evidence cites; registry does not substitute for `git log` |

**Registry-fed routing:** **Forbidden** in Tier 2B. `collect_delegation_tasks()` must remain unchanged unless a **future separate authorization** names registry-fed routing.

---

## 14. Security and authority risks

| Risk | Mitigation |
|---|---|
| Registry mistaken as build authority | Status guards (§9.1); `BUILD_AUTHORIZED` evidence rule (E3) |
| Registry mistaken as next-task selector | `autonomous_selection: false`; no selection stdout; AUTH-5 blocked |
| Dispatcher drift if registry wired silently | No dispatcher reads; demotion if dispatcher imports registry |
| Authority vocabulary on validator stdout | Mode B locked vocabulary (§16) — no `PASS`/`FAIL`/`APPROVED` |
| Deletion of rejected history | Non-deletion rule (§12) |
| `COMPLETE` without closeout | Forbidden transition + evidence rule E4 |
| Contradiction laundering | `CONTRADICTION` status preserved until resolved |
| Tier creep to AUTH-3B automation | Mode A human-only; no machine writer |

---

## 15. Failure modes

| Failure mode | Detection | Mitigation |
|---|---|---|
| **Registry-as-routing** | Dispatcher diff reads registry | Demotion §17; revert dispatcher change |
| **Registry-as-selector** | Tool emits next task | Demotion; remove tool |
| **Status laundering** | `CANDIDATE` → `COMPLETE` jump | Mode B validator; human audit |
| **Build auth laundering** | `SIGNED_CONTRACT` → `BUILD_AUTHORIZED` without `MMI-DEC` | Evidence rule E3; validator |
| **Silent deletion** | Missing historical `REJECTED` rows | Non-deletion tests; git history |
| **Evidence-free status** | Empty `status_evidence` | Structural reject |
| **Forbidden stdout vocabulary** | Mode B emits `PASS`/`APPROVED` | Demotion §17 |
| **§11 confused with build auth** | Build starts at signature only | Contract + decision log discipline |
| **AUTH-5 bundling** | Single authorization names Tier 2B + AUTH-5 | Reject authorization; split gates |

---

## 16. Mode B validator vocabulary (parked — if separately authorized)

Mode B stdout uses **only**:

| Verdict | Meaning |
|---|---|
| `REGISTRY_STRUCTURALLY_ADMISSIBLE` | Registry file parses; required fields present; transitions/evidence rules satisfied structurally |
| `REGISTRY_STRUCTURALLY_INADMISSIBLE` | Registry fails structural rules; reason codes follow |

**Forbidden stdout:** `PASS`, `FAIL`, `APPROVED`, `VERIFIED`, `COMPLETE`, `BUILD_AUTHORIZED`, `SIGNED`, `PROMOTED`, standalone `REJECT`, `NEXT_TASK`, `SELECTED`, `DELEGATED`.

Mode B is **read-only** — no file writes, no transitions applied, no dispatcher calls.

---

## 17. Rollback / demotion plan

### Rollback

- Revert or disable Tier 2B registry file and/or Mode B validator if contract violated
- **Tier 1 F1–F5 and Tier 2A remain untouched** — rollback does not demote Tier 1 or Tier 2A
- Registry file may remain as historical evidence unless corrupt — prefer `DO_NOT_USE` status over deletion

### Demotion triggers (immediate)

Disable Tier 2B tooling if:

- dispatcher reads registry or routing output changes because of registry
- tooling emits next-task selection or worker assignment
- tooling writes routing-authority files (`MMI_CURRENT_STATE.md`, decision log, intake) without separate authorization
- Mode B emits forbidden vocabulary (§16)
- automated status transitions run without human action
- `REJECTED`/`SUPERSEDED` rows deleted by tooling

Demotion affects **Tier 2B only** — not Tier 1 foundation or Tier 2A packet intake.

---

## 18. Falsifiable acceptance tests (implementation — after §11 + build auth)

Locked vocabulary per §16 for Mode B. Tests use synthetic fixture registries only.

| Test ID | Name | Pass condition |
|---|---|---|
| T2B-T1 | Registry file exists | `mmi/MMI_TASK_REGISTRY.yaml` present; dispatcher untouched |
| T2B-T2 | Mode A human-only | No machine writer in Tier 2B code; `maintained_by: human` |
| T2B-T3 | Envelope guards | `dispatcher_reads: false` and `autonomous_selection: false` |
| T2B-T4 | Missing evidence rejects | Row with empty `status_evidence` → Mode B `REGISTRY_STRUCTURALLY_INADMISSIBLE` + reason code |
| T2B-T5 | Signed not build auth | `SIGNED_CONTRACT` without build-auth evidence cannot structurally justify `BUILD_AUTHORIZED` |
| T2B-T6 | No candidate to complete | `CANDIDATE` → `COMPLETE` forbidden transition flagged |
| T2B-T7 | Built not complete | `BUILT_NEEDS_REVIEW` → `COMPLETE` without closeout evidence flagged |
| T2B-T8 | No dispatcher feed | `mmi_dispatch.py` unchanged; no import of registry module |
| T2B-T9 | No selection stdout | No tooling stdout contains next-task or selection labels |
| T2B-T10 | Historical rows persist | Fixture rows with status `PARKED`, `REJECTED`, `SUPERSEDED`, `CONTRADICTION`, or `DO_NOT_USE` remain present after validator run |
| T2B-T11 | Mode B read-only | Mode B makes zero file writes; digest tests on routing surfaces |
| T2B-T12 | AUTH-5 still blocked | No AUTH-5 flag, config, or autonomous selection path introduced |
| T2B-T13 | Non-deletion | Tooling does not delete rows; `PARKED`, `REJECTED`, `SUPERSEDED`, `CONTRADICTION`, and `DO_NOT_USE` rows retained |
| T2B-T14 | Human verify after closeout | Human `mmi_dispatch.py --verify` PASS after routing-authority closeout (not registry tooling) |

---

## 19. What must not be built in Tier 2B

Post-signature implementation must **not**:

- edit `scripts/mmi_dispatch.py` or wire `collect_delegation_tasks()` to registry
- enable AUTH-5 or autonomous task ranking/selection
- auto-assign `assigned_worker` from registry state
- auto-promote scoreboard rows from registry status
- run background sync from git/scoreboard into registry
- replace `mmi/MMI_DECISION_LOG.md` or `mmi/MMI_INTAKE_RECORDS.md` with registry-only workflow
- write `MMI_CURRENT_STATE.md` from registry tooling
- bundle Mode B intake append (Tier 2A parked slice) into Tier 2B build
- create dashboard, UI, or always-on watcher
- push without operator instruction

---

## 20. Locked design decisions

| ID | Decision |
|---|---|
| D1 | Tier 2B is passive lifecycle tracking only — not selection, routing, or build authority |
| D2 | Registry instance is human-maintained at Mode A; no machine writer |
| D3 | `dispatcher_reads: false` and `autonomous_selection: false` are required envelope literals |
| D4 | Every status requires `status_evidence` — fail-closed |
| D5 | `SIGNED_CONTRACT` ≠ `BUILD_AUTHORIZED` — separate evidence required |
| D6 | `COMPLETE` requires closeout evidence — not validator admissibility alone |
| D7 | Non-deletion for `REJECTED`, `PARKED`, `SUPERSEDED`, `CONTRADICTION`, `DO_NOT_USE` |
| D8 | Registry is not dispatcher input in Tier 2B |
| D9 | AUTH-5 cannot be authorized in same build slice as Tier 2B |
| D10 | Mode A default first; Mode B validator parked until separately authorized |

---

## 21. Verification plan (post-implementation only)

1. `mmi/MMI_TASK_REGISTRY.yaml` exists with valid envelope; `scripts/mmi_dispatch.py` untouched
2. Mode A: human update rules documented; no machine writer code
3. Mode B (if authorized): structural validator stdout-only; reason codes on inadmissible fixtures
4. Human runs `python3 scripts/mmi_dispatch.py --verify` after routing-authority closeout records
5. `git status --short` clean at closeout
6. Grok gate 0/0 if Matt authorizes gate on implementation slice

---

## 22. Sign-off

**§11 UNSIGNED — awaiting Matt Nichol signature.**

This §11 signature would approve the contract only. It would **not** authorize implementation, registry population, or validator code.

**Contract configuration to record at signature (not build authorization):**

| Setting | Options |
|---|---|
| Selected first build mode | **Mode A** (recommended) — human-maintained registry file + rules |
| Mode B structural validator | **Parked** unless explicitly selected at §11 |
| Registry format | **YAML** (`mmi/MMI_TASK_REGISTRY.yaml`) recommended; JSON only if named at §11 |

**Mode B** (read-only structural validator CLI) remains parked unless Matt separately selects it at §11 **and** names Mode B in separate build authorization. **First build authorization, if issued, should name Mode A only.**

> [Blank — Matt Nichol signature line]

---

**End of Tier 2B contract draft. DRAFT UNSIGNED. Implementation blocked until Matt §11 signature and separate build authorization.**
