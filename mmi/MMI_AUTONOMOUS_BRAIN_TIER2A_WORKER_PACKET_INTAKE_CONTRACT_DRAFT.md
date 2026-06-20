# MMI Autonomous Brain — Tier 2A Worker Packet Intake Implementation Contract (Draft)

**Status:** DRAFT — UNSIGNED. **Not in force.** Placement does not authorize implementation, code, or `scripts/mmi_packet_intake.py`.

**Classification:** `CONTRACT_DRAFT` · Tier 2A tooling slice · not implemented

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar` (Mutant Monkey Security)

**Parent doctrine:** `mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md` (review material — not signed)

**Tier 1 prerequisite:** Tier 1 passive foundation complete (`MMI-DEC-021`; F1–F5 including `mmi/MMI_WORKER_COMPLETION_PACKET_TEMPLATE.md` (F3))

**Tier 1 contract:** `mmi/MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_CONTRACT_DRAFT.md` (§11 SIGNED 2026-06-18)

**Date:** 2026-06-18

---

## 1. Executive summary

This contract defines the **first Tier 2 tooling slice** for MMI Autonomous Brain: **Tier 2A Worker Packet Intake** — a fail-closed CLI validator for worker completion packets aligned with Tier 1 F3 and invariant I15.

Future implementation (only after Matt §11 on **this** contract **plus** separate explicit build authorization) may add `scripts/mmi_packet_intake.py` to:

- parse and validate `WORKER_COMPLETION_PACKET` text against F3 required fields
- emit structured stdout results (pass / reject-with-reasons)
- optionally append a narrow intake stub to `mmi/MMI_INTAKE_RECORDS.md` (Mode B only)

Tier 2A is **not** full AUTH-3B. It does **not** authorize dispatcher edits, routing advance, decision-log ACCEPT, scoreboard changes, auto-prompt generation (AUTH-4), contradiction tooling (AUTH-7), dashboards (AUTH-6), or autonomous selection (AUTH-5).

Signing this contract (future §11) approves **contract terms only**. It does **not** authorize implementation.

---

## 2. Scope

### 2.1 In scope (implementation — only after §11 + separate build authorization)

| Item | Description |
|---|---|
| `scripts/mmi_packet_intake.py` | Single CLI script; stdin or file path input; no daemon/hook |
| Packet validation | Closed field set from F3 / I15 |
| Mode A (default) | Stdout-only verdict; **zero file-write authority** |
| Mode B (optional at build) | Stdout + **narrow append** to `mmi/MMI_INTAKE_RECORDS.md` only |
| Synthetic tests | Focused tests for validator only (no routing fixtures) |

### 2.2 Out of scope

| Item | Rule |
|---|---|
| `scripts/mmi_dispatch.py` | No edits (**AUTH-2-EDIT** not authorized) |
| `MMI_CURRENT_STATE.md` routing block | No automated writes |
| `mmi/MMI_DECISION_LOG.md` | No automated ACCEPT / MMI-DEC rows |
| Task registry | No population; no `MMI_TASK_REGISTRY.json` / `.yaml` |
| Scoreboard / runtime / orchestrator | No changes |
| #47 / #48 | Out of scope |
| Parked roadmap drafts | Out of scope |
| Architectapp | Out of scope |
| AUTH-4 / AUTH-5 / AUTH-6 / AUTH-7 | Not authorized by Tier 2A |
| Always-on hooks / daemons / watchers | Prohibited |

---

## 3. Build mode configuration (contract terms — not active until implementation)

**Default recommended build mode:** **Mode A** (stdout-only, zero file-write authority).

| Mode | Stdout | File writes | Notes |
|---|---|---|---|
| **Mode A** | Required — structured pass/reject + missing-field list | **None** | Default for first implementation slice |
| **Mode B** | Same as Mode A | **Append only** to `mmi/MMI_INTAKE_RECORDS.md` | Narrow stub block; no edit/delete of prior intake rows |

Mode selection is **contract configuration** recorded at §11 signature. It does **not** authorize build. Implementation mode must be named again in separate build authorization.

### Mode B append boundary

- Append-only new `INTAKE-*` stub at end of running log
- Stub labels `source: mmi_packet_intake.py` and `classification: WORKER_COMPLETION_PACKET`
- Stub carries validation verdict and packet metadata fields only — **not** routing outcome advance
- No writes to any other path

---

## 4. Locked design decisions

| ID | Decision |
|---|---|
| D1 | Validator only — packet intake does not accept work, sign contracts, or advance routing |
| D2 | F3 field set is authoritative; missing required field → reject (I4 / F3 auto-reject) |
| D3 | Mode A is default build target; Mode B requires explicit naming in build authorization |
| D4 | Fail-closed — ambiguous parse → reject with reason |
| D5 | No network, no subprocess dispatch to workers, no auto `--sync` / `--verify` |
| D6 | Intake append (Mode B) is evidence stub only — not Matt approval |
| D7 | Script reads approved surfaces (F1); does not become dispatcher input |
| D8 | Tier 2A does not close full AUTH-3B gap in F5 — only this narrow intake append in Mode B |

---

## 5. Required packet fields (validator must check)

Aligned with `mmi/MMI_WORKER_COMPLETION_PACKET_TEMPLATE.md`:

- `task_or_contract_ref`
- `worker_lane`
- `authorization_ref`
- `files_changed` (non-empty list)
- `exact_commit_hash` (when commit required for slice)
- `scope_confirmation`
- `tests_gates_run`
- `deviations_from_contract` (explicit `none` allowed)
- `mmi_verify_output` (when routing-authority files changed per F3)
- `git_status_short`
- all `no_out_of_scope_confirmations` lines
- `operator_action_required`

---

## 6. Authority boundaries

| Boundary | Tier 2A posture |
|---|---|
| AUTH-2 | Respect dispatcher — no `mmi_dispatch.py` changes |
| AUTH-2-EDIT | **Not authorized** |
| AUTH-3B (full) | **Not authorized** — Mode B is narrow intake append only |
| AUTH-4 | **Not authorized** |
| AUTH-5 | **Not authorized** |
| AUTH-6 | **Not authorized** |
| AUTH-7 | **Not authorized** |
| Routing advance | **Forbidden** — validator output does not advance MODE or delegation |
| Registry-fed routing | **Forbidden** |

---

## 7. Non-goals / must-not-build

Post-signature implementation must **not**:

- create `scripts/mmi_packet_intake.py` until separate build authorization
- edit dispatcher, scoreboard, gate registry, or runtime code
- write `MMI_CURRENT_STATE.md` except via separate human/MMI workflow
- treat validator PASS as MMI-DEC ACCEPT or intake routing advance
- bundle AUTH-5 or full AUTH-3B in the same build authorization
- push without operator instruction

---

## 8. Verification plan (post-implementation only)

1. `scripts/mmi_packet_intake.py` exists; `scripts/mmi_dispatch.py` untouched
2. Mode A tests: valid packet → stdout PASS; missing field → stdout REJECT
3. Mode B tests (if authorized): append appears only in `mmi/MMI_INTAKE_RECORDS.md`
4. `python3 scripts/mmi_dispatch.py --verify` PASS after any routing-authority record updates
5. `git status --short` clean at closeout
6. Grok gate 0/0 if Matt authorizes gate on implementation slice

---

## 9. Failure modes

| Failure mode | Mitigation |
|---|---|
| Validator PASS treated as acceptance | F3 + contract header: intake evidence only |
| Mode B writes outside intake file | Contract locks append path; tests enforce |
| Tier creep into routing automation | No dispatcher diff in acceptance tests |
| §11 signature confused with build auth | §11 wording below |

---

## 10. Falsifiable acceptance tests (implementation — after §11 + build auth)

| Test ID | Name | Pass condition |
|---|---|---|
| T2A-T1 | Script exists | `scripts/mmi_packet_intake.py` present; dispatcher untouched |
| T2A-T2 | Mode A default | Default CLI path stdout-only; no file writes |
| T2A-T3 | F3 completeness | All F3 required fields enforced |
| T2A-T4 | Reject incomplete | Missing field → REJECT stdout; no routing side effects |
| T2A-T5 | Mode B boundary | If built: append only to `mmi/MMI_INTAKE_RECORDS.md` |
| T2A-T6 | No routing advance | No automated `--sync`, decision log, or CURRENT_STATE routing writes |
| T2A-T7 | verify PASS | `mmi_dispatch.py --verify` after MMI closeout |

---

## 11. Sign-off

**DRAFT — UNSIGNED — NOT IN FORCE.**

**§11 signature language (when signed):** This §11 signature approves the contract only. It does not authorize implementation. Build authorization must be issued separately after signature.

**Contract configuration at signature (not build authorization):**

| Setting | Default |
|---|---|
| Recommended first implementation mode | **Mode A** — stdout-only, zero file-write authority |
| Optional alternate | **Mode B** — stdout + narrow append to `mmi/MMI_INTAKE_RECORDS.md` only |

Matt selects Mode A or Mode B as the **contract default** at §11. Either selection is configuration only until a separate operator instruction names the implementation slice and mode.

> Matt Nichol ____________________  Date __________

---

**End of Tier 2A contract draft. UNSIGNED — placement does not authorize implementation.**
