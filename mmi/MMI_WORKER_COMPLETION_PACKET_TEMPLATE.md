# MMI Worker Completion Packet Template

**Status:** Tier 1 passive template (F3). **Intake evidence only — not self-approval.**

Submitting this packet does **not** authorize work, sign contracts, flip scoreboard rows, or pass Grok gate. Matt / `MMI-DEC-*` / signed contracts remain authority for acceptance.

**Parent contract:** `mmi/MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_CONTRACT_DRAFT.md` (§11 SIGNED 2026-06-18)

**Rejection rule:** Missing any **required** field below → **auto-reject**; no MMI record advance, no routing state advance.

---

## Required fields

Copy this block into intake or paste in session; fill every required field.

```text
WORKER_COMPLETION_PACKET
task_or_contract_ref:        [e.g. MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_BUILD / INTAKE-2026-06-18-010]
worker_lane:                 [Cursor | Codex | Claude | ChatGPT | Gemini | Grok | Matt]
authorization_ref:           [operator instruction name or MMI-DEC-*]

files_changed:
  - [path]
  - [path]

exact_commit_hash:           [40-char git rev or PENDING if pre-commit]

scope_confirmation:          [one sentence: what was authorized vs what was done]

tests_gates_run:
  - [e.g. python3 scripts/mmi_dispatch.py --verify — PASS]
  - [e.g. pytest path — N passed]
  - [none — docs only]

deviations_from_contract:
  - [list each deviation OR explicit: none]

mmi_verify_output:           [paste full VERDICT line or attach path to saved output]

git_status_short:            [paste `git status --short` output]

no_out_of_scope_confirmations:
  - dispatcher/code/runtime/scoreboard unchanged: [yes/no + note]
  - no registry population: [yes/no]
  - no Architectapp: [yes/no]
  - no #47/#48 changes: [yes/no]
  - no parked draft promotion: [yes/no]
  - no push: [yes/no]

operator_action_required:    [yes/no — for Matt follow-up]
notes:                       [optional]
```

---

## Field definitions

| Field | Requirement |
|---|---|
| `files_changed` | Every path touched; no "etc." |
| `exact_commit_hash` | Final commit for this slice; if multiple commits, list primary closeout hash |
| `scope_confirmation` | Must match authorized scope; if narrower, say so |
| `tests_gates_run` | Every gate invoked; "not run" is a deviation |
| `deviations_from_contract` | Explicit empty list `none` if clean |
| `mmi_verify_output` | Must include `VERDICT: PASS` or `FAIL` from `python3 scripts/mmi_dispatch.py --verify` when routing files changed |
| `git_status_short` | Must be clean at closeout unless documenting intentional untracked items with explanation |
| `no_out_of_scope_confirmations` | All lines required for MMI brain / Tier 1 slices |

---

## Auto-reject conditions

Reject without MMI intake advance if any of:

- missing `exact_commit_hash` (when commit was required)
- missing `mmi_verify_output` (when routing-authority files changed)
- missing `git_status_short`
- missing any `no_out_of_scope_confirmations` line
- `deviations_from_contract` absent or vague
- packet claims ACCEPT without evidence paths or commit hash

---

## Example (empty template — do not treat as completed work)

```text
WORKER_COMPLETION_PACKET
task_or_contract_ref:
worker_lane:
authorization_ref:

files_changed:
  -

exact_commit_hash:

scope_confirmation:

tests_gates_run:
  -

deviations_from_contract:
  - none

mmi_verify_output:

git_status_short:

no_out_of_scope_confirmations:
  - dispatcher/code/runtime/scoreboard unchanged:
  - no registry population:
  - no Architectapp:
  - no #47/#48 changes:
  - no parked draft promotion:
  - no push:

operator_action_required:
notes:
```

---

## Explicit non-authorization

This template is **not** a rubric score, not a gate verdict, and not operator sign-off. Grok `complete_gate.py` and Matt §11 remain separate authorities where applicable.
