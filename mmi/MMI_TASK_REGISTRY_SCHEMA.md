# MMI Task Registry Schema — Schema Only (Not a Live Registry)

**Status:** Tier 1 passive schema (F2). **Human-maintained documentation only.**

**This is NOT:**

- a live task registry
- a dispatcher input surface
- signed contract authority
- component build authority
- git truth
- scoreboard authority
- gate-registry authority

**No machine writer.** No dispatcher reader. No auto-sync from scoreboard or git.

**Parent contract:** `mmi/MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_CONTRACT_DRAFT.md` (§11 SIGNED 2026-06-18)

**Future instance path (not created at Tier 1):** `mmi/MMI_TASK_REGISTRY.json` or `.yaml` — requires separate AUTH-3A approval and explicit authorization before any file exists.

---

## Purpose

Define the **shape** of a future human-maintained task lifecycle record. Today `scripts/mmi_dispatch.py` `collect_delegation_tasks()` **derives** candidates from repo evidence; it does **not** read this schema or any registry file.

**Registry existence must not change routing behavior.** Wiring the registry into the dispatcher requires separate authorization naming registry-fed routing.

---

## Required fields (candidate)

| Field | Type | Required | Notes |
|---|---|---|---|
| `task_id` | string | yes | Stable identifier; never reused for a different scope |
| `classification` | closed enum | yes | Aligned with delegation scoring (see below) |
| `status` | closed enum | yes | Lifecycle state only |
| `source_evidence` | string[] | yes | File paths and/or commit hashes |
| `assigned_worker` | closed enum | no | Cursor, Codex, Claude, ChatGPT, Gemini, Grok, Matt |
| `operator_action_required` | yes \| no | yes | |
| `matt_approval_required` | yes \| no | yes | |
| `blockers` | closed vocabulary[] | no | Empty when actionable-now |
| `task_or_contract_ref` | string | no | Human-readable reference to contract or intake |
| `created_at` | ISO-8601 | yes | Record creation (human or future AUTH-3B) |
| `updated_at` | ISO-8601 | yes | Last status transition |

---

## `classification` (closed enum — candidate)

Align with `scripts/mmi_dispatch.py` delegation scoring where applicable:

- `SCOREBOARD_READY`
- `NEEDS_SCOREBOARD_ROW`
- `INTAKE_CLASSIFY_BATCH`
- `EXTERNAL_LANE`
- `NEEDS_MMI_REVIEW`
- `RESEARCH`
- `PARKED_DRAFT`
- `CONTRACT_DRAFT`
- `TIER1_FOUNDATION` (example — human-maintained only)

New values require schema revision + operator authorization.

---

## `status` (closed enum)

| Status | Meaning |
|---|---|
| `open` | Identified; not yet delegated |
| `delegated` | Lane assigned; work in progress |
| `completed` | Worker completion packet accepted |
| `blocked` | Cannot advance; blocker documented |
| `parked` | Intentionally deferred |
| `rejected` | Operator or intake rejected; **never deleted** |
| `superseded` | Replaced by newer task_id; **never deleted** |

---

## Non-deletion rule

Entries with status `rejected`, `parked`, or `superseded` are **never deleted** from a future live registry. They remain visible in history. Corrections are append-only status transitions or new records with cross-reference.

---

## Negative authority (repeat)

| This schema is NOT | Authority lives elsewhere |
|---|---|
| Signed contract authority | `4. Product_Roadmap/*` §11-signed files |
| Build authorization | Operator explicit instruction + `MMI-DEC-*` |
| Scoreboard truth | `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` |
| Git truth | `git log`, `git status`, commits |
| Dispatcher routing | `scripts/mmi_dispatch.py` until separately authorized |

---

## Tier 1 posture

At Tier 1 build close: **this file only**. No `MMI_TASK_REGISTRY.json` / `.yaml`. No task rows. No dispatcher integration.
