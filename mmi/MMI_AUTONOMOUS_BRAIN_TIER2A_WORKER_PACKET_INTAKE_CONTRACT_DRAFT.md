# MMI Autonomous Brain — Tier 2A Worker Packet Intake Implementation Contract

**Status:** §11 SIGNED 2026-06-19 by Matt Nichol. Signing approves **contract terms only** with **Mode A** selected (stdout-only, zero file-write authority). Signing does **not** authorize implementation, code, or `scripts/mmi_packet_intake.py`. **Mode B remains parked** (not selected at signature). Separate explicit build authorization is required before any Tier 2A implementation; first authorized build slice must be **Mode A only**.

**Classification:** `SIGNED_CONTRACT` · Tier 2A tooling slice · not implemented

**Wording patch:** 2026-06-18 — Tier 2A contract review PASS WITH CHANGES (vocabulary, structural-only, exit codes, rollback/demotion, tests).

**§11 signature:** 2026-06-19 — Mode A selected; Mode B not selected (parked).

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar` (Mutant Monkey Security)

**Parent doctrine:** `mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md` (review material — not signed)

**Tier 1 prerequisite:** Tier 1 passive foundation complete (`MMI-DEC-021`; F1–F5 including `mmi/MMI_WORKER_COMPLETION_PACKET_TEMPLATE.md` (F3))

**Tier 1 contract:** `mmi/MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_CONTRACT_DRAFT.md` (§11 SIGNED 2026-06-18)

**Date:** 2026-06-18

---

## 1. Executive summary

This contract defines the **first Tier 2 tooling slice** for MMI Autonomous Brain: **Tier 2A Worker Packet Intake** — a fail-closed CLI validator that checks whether a worker completion packet is **structurally admissible for human/MMI review**, aligned with Tier 1 F3 and invariant I15.

Future implementation (only after Matt §11 on **this** contract **plus** separate explicit build authorization) may add `scripts/mmi_packet_intake.py` to:

- parse `WORKER_COMPLETION_PACKET` text against F3 required fields (structural checks only)
- emit structured stdout verdict `ACCEPT_FOR_MMI_REVIEW` or `REJECT_INCOMPLETE_PACKET` plus rejection reason codes
- optionally append a narrow intake stub to `mmi/MMI_INTAKE_RECORDS.md` (**Mode B only** — parked unless separately authorized)

Tier 2A is **not** full AUTH-3B. It does **not** authorize dispatcher edits, routing advance, decision-log rows, scoreboard changes, auto-prompt generation (AUTH-4), contradiction tooling (AUTH-7), dashboards (AUTH-6), or autonomous selection (AUTH-5).

Signing this contract (future §11) approves **contract terms only**. It does **not** authorize implementation.

---

## 2. Scope

### 2.1 In scope (implementation — only after §11 + separate build authorization)

| Item | Description |
|---|---|
| `scripts/mmi_packet_intake.py` | Single CLI script; file-path input only (Mode A); no stdin; no daemon/hook |
| Packet validation | Closed field set from F3 / I15; structural-only (§4) |
| Mode A (default) | Stdout-only `ACCEPT_FOR_MMI_REVIEW` or `REJECT_INCOMPLETE_PACKET`; **zero file-write authority** |
| Mode B (parked) | Stdout + **narrow append** to `mmi/MMI_INTAKE_RECORDS.md` only — not first-build default |
| Synthetic tests | Focused tests for validator only (no routing fixtures) |

**First implementation slice:** **Mode A only** unless Matt explicitly names Mode B in separate build authorization.

### 2.2 Out of scope

| Item | Rule |
|---|---|
| `scripts/mmi_dispatch.py` | No edits, wraps, or calls (**AUTH-2-EDIT** not authorized) |
| `MMI_CURRENT_STATE.md` | **Tier 2A script never writes this file** (§4, §7) |
| `mmi/MMI_DECISION_LOG.md` | No automated decision-log rows |
| Task registry | No population; no `MMI_TASK_REGISTRY.json` / `.yaml` |
| Scoreboard / runtime / orchestrator | No changes |
| #47 / #48 | Out of scope |
| Parked roadmap drafts | Out of scope |
| Architectapp | Out of scope |
| AUTH-4 / AUTH-5 / AUTH-6 / AUTH-7 | Not authorized by Tier 2A |
| Always-on hooks / daemons / watchers | Prohibited |
| Auto-sync / auto-verify / auto-commit | Prohibited (§7, §12) |

---

## 3. Output vocabulary (locked)

The validator stdout surface uses **only** these verdict tokens:

| Verdict | Meaning |
|---|---|
| `ACCEPT_FOR_MMI_REVIEW` | Packet is structurally admissible for human/MMI review |
| `REJECT_INCOMPLETE_PACKET` | Packet is inadmissible; one or more rejection reason codes follow |

**Forbidden stdout verdicts and standalone authority words** — the validator must **never** emit:

`PASS`, `FAIL`, `APPROVED`, `VERIFIED`, `COMPLETE`, `BUILD_AUTHORIZED`, `SIGNED`, `PROMOTED`, or `REJECT` as a standalone verdict.

**`ACCEPT_FOR_MMI_REVIEW` is not:**

- work approval
- verify PASS
- build authorization
- lifecycle completion
- operator sign-off
- acceptance for routing advance

It means only: **structurally admissible for human/MMI review**.

**Packet field content vs validator verdict:** A worker may paste dispatcher text such as `VERDICT: PASS` inside the `mmi_verify_output` field. That pasted line is **packet content only**. The validator checks presence/format per F3; it does **not** treat pasted verify text as its own verdict and does **not** emit `PASS` or `FAIL` on stdout.

---

## 4. Structural-only validation

| Rule | Requirement |
|---|---|
| Scope | Structural field-presence and format checks only |
| No quality judgment | Validator does not judge work quality, scope correctness, or gate outcomes |
| No verify execution | Validator does **not** run `python3 scripts/mmi_dispatch.py --verify` |
| Verify field | Checks that `mmi_verify_output` is present/referenced when F3 requires it — not whether verify outcome is correct |
| Git/commit fields | Treats pasted git status, commit hashes, and verify output as packet fields — does not interpret them as proof of correctness |
| No build truth | Validator does not validate build truth or compare commits to live repo state |
| No authority actions | Validator never approves, verifies, signs, completes, or authorizes work |

---

## 5. Exit-code semantics

| Condition | Meaning |
|---|---|
| Exit 0 with `ACCEPT_FOR_MMI_REVIEW` | Packet structurally admissible for review |
| Non-zero with `REJECT_INCOMPLETE_PACKET` | **Packet inadmissibility only** |

Non-zero exit does **not** mean:

- build failure
- worker failure
- verify failure
- underlying work is wrong

The worker may correct the packet and resubmit. Rejection reason codes identify missing or malformed fields only.

---

## 6. Build mode configuration (contract terms — not active until implementation)

**Default recommended build mode:** **Mode A** (stdout-only, zero file-write authority).

**Mode B remains parked** unless Matt explicitly selects it at §11 **and** separately names Mode B in build authorization. **First implementation should be Mode A only** unless Matt says otherwise.

| Mode | Stdout | File writes | Notes |
|---|---|---|---|
| **Mode A** | `ACCEPT_FOR_MMI_REVIEW` or `REJECT_INCOMPLETE_PACKET` + reason codes | **None** | Default first implementation slice |
| **Mode B** (parked) | Same as Mode A | **Append only** to `mmi/MMI_INTAKE_RECORDS.md` | Requires explicit §11 choice + separate build authorization naming Mode B |

Mode selection is **contract configuration** recorded at §11 signature. It does **not** authorize build. Implementation mode must be named again in separate build authorization.

### Mode B append boundary (if ever authorized)

- Append-only new `INTAKE-*` stub at end of running log
- Stub labels `source: mmi_packet_intake.py` and `classification: WORKER_COMPLETION_PACKET`
- Stub carries admissibility verdict and packet metadata only — **not** routing outcome advance
- No writes to any other path

---

## 7. Locked design decisions

| ID | Decision |
|---|---|
| D1 | Validator only — does not approve work, sign contracts, verify work, or advance routing/lifecycle |
| D2 | F3 field set is authoritative; missing required field → `REJECT_INCOMPLETE_PACKET` (I4 / F3 auto-reject) |
| D3 | Mode A is default first build; Mode B parked until explicit §11 + build authorization |
| D4 | Fail-closed — ambiguous parse → `REJECT_INCOMPLETE_PACKET` with reason codes |
| D5 | No network, no subprocess worker dispatch, no auto `--sync` / `--verify` / auto-commit |
| D6 | Mode B intake append is evidence stub only — not Matt approval or routing advance |
| D7 | Script reads approved surfaces (F1); does not become dispatcher input |
| D8 | Tier 2A does not close full AUTH-3B gap in F5 — only narrow intake append in Mode B |
| D9 | Locked stdout vocabulary only (§3) |
| D10 | Tier 2A script never writes `MMI_CURRENT_STATE.md` |

---

## 8. Required packet fields and validation rules

Aligned with `mmi/MMI_WORKER_COMPLETION_PACKET_TEMPLATE.md`:

- `task_or_contract_ref`
- `worker_lane`
- `authorization_ref`
- `files_changed` (non-empty list)
- `exact_commit_hash` — required when the closing contract requires a commit hash for the slice; otherwise packet must explicitly state why commit hash is not applicable (e.g. pre-commit `PENDING`)
- `scope_confirmation`
- `tests_gates_run`
- `deviations_from_contract` — see deviations rule below
- `mmi_verify_output` — when routing-authority files changed per F3; presence/reference only
- `git_status_short`
- all `no_out_of_scope_confirmations` lines
- `operator_action_required`

### Deviations rule

| Condition | Result |
|---|---|
| Missing `deviations_from_contract` heading | `REJECT_INCOMPLETE_PACKET` |
| Blank deviations value | `REJECT_INCOMPLETE_PACKET` |
| `deviations_from_contract: none` or explicit list | admissible if other fields OK |
| Vague values (`N/A`, `etc.`, empty list without `none`) | `REJECT_INCOMPLETE_PACKET` unless F3 explicitly allows |

### Packet field content (not validator verdict)

Pasted `VERDICT: PASS` or `VERDICT: FAIL` inside `mmi_verify_output` is **worker-supplied packet content**. The validator checks field presence per F3; it does not re-emit gate vocabulary on stdout.

---

## 9. Authority boundaries

| Boundary | Tier 2A posture |
|---|---|
| AUTH-2 | Respect dispatcher — no `mmi_dispatch.py` changes or invocations |
| AUTH-2-EDIT | **Not authorized** |
| AUTH-3B (full) | **Not authorized** — Mode B is narrow intake append only |
| AUTH-4 | **Not authorized** |
| AUTH-5 | **Not authorized** |
| AUTH-6 | **Not authorized** |
| AUTH-7 | **Not authorized** |
| Routing / lifecycle advance | **Forbidden** |
| Registry-fed routing | **Forbidden** |
| `MMI_CURRENT_STATE.md` | **Tier 2A script never writes** — humans/Cursor update only outside validator per existing MMI workflow |

---

## 10. Non-goals / must-not-build

Post-signature implementation must **not**:

- create `scripts/mmi_packet_intake.py` until separate build authorization
- edit dispatcher, scoreboard, gate registry, or runtime code
- write `MMI_CURRENT_STATE.md` from the validator (human/MMI workflow only)
- treat `ACCEPT_FOR_MMI_REVIEW` as decision-log acceptance, routing advance, or build authorization
- run auto-sync, auto-verify, or auto-commit
- bundle AUTH-5 or full AUTH-3B in the same build authorization
- push without operator instruction

---

## 11. Verification plan (post-implementation only)

1. `scripts/mmi_packet_intake.py` exists; `scripts/mmi_dispatch.py` untouched
2. Mode A: complete packet → stdout `ACCEPT_FOR_MMI_REVIEW`; missing field → stdout `REJECT_INCOMPLETE_PACKET` + reason codes
3. Mode B (if separately authorized): append only in `mmi/MMI_INTAKE_RECORDS.md`
4. Human runs `python3 scripts/mmi_dispatch.py --verify` after any routing-authority record updates (not the validator)
5. `git status --short` clean at closeout
6. Grok gate 0/0 if Matt authorizes gate on implementation slice

---

## 12. Failure modes

| Failure mode | Mitigation |
|---|---|
| `ACCEPT_FOR_MMI_REVIEW` treated as work approval | §3 vocabulary; §4 structural-only |
| Forbidden stdout vocabulary | T2A-T8; demotion §13 |
| Mode B writes outside intake file | Contract path lock; T2A-T11 |
| Tier creep into routing automation | T2A-T6, T2A-T10; no dispatcher diff |
| §11 signature confused with build auth | §14 wording |
| Pasted verify text confused with validator verdict | §3, §8 packet-content note |

---

## 13. Rollback / demotion

### Rollback

- Revert or disable Tier 2A validator implementation if it violates this contract
- **Tier 1 F1–F5 remain untouched** — rollback does not demote Tier 1 artifacts
- Validator removal does not delete Tier 1 templates or schemas

### Intake history (Mode B, if ever authorized)

- Intake append history is **not deleted by default**
- Corrections use superseding/correction intake records — not silent deletion
- Hard deletion or revert of intake records requires **explicit Matt authorization** (corrupt or out-of-scope writes only)

### Demotion triggers

Immediate demotion (disable script / revert slice) if implementation:

- emits forbidden stdout vocabulary (§3)
- writes outside authorized target
- writes `MMI_CURRENT_STATE.md`
- writes scoreboard, task registry, or `mmi/MMI_DECISION_LOG.md`
- calls, wraps, or modifies `scripts/mmi_dispatch.py`
- runs auto-sync, auto-verify, or auto-commit
- installs background hook, daemon, or watcher behavior

Demotion affects **Tier 2A only** — not Tier 1 foundation artifacts.

---

## 14. Falsifiable acceptance tests (implementation — after §11 + build auth)

All tests use locked vocabulary: `ACCEPT_FOR_MMI_REVIEW`, `REJECT_INCOMPLETE_PACKET` — never `PASS`, `FAIL`, or standalone `REJECT` on stdout.

| Test ID | Name | Pass condition |
|---|---|---|
| T2A-T1 | Script exists | `scripts/mmi_packet_intake.py` present; dispatcher untouched |
| T2A-T2 | Mode A default | Default CLI stdout-only; **no file writes** |
| T2A-T3 | F3 completeness | All F3 required fields enforced structurally |
| T2A-T4 | Reject incomplete | Missing field → `REJECT_INCOMPLETE_PACKET` + reason codes; no routing side effects |
| T2A-T5 | Mode B boundary | **If Mode B authorized:** append only to `mmi/MMI_INTAKE_RECORDS.md` |
| T2A-T6 | No routing advance | No automated `--sync`, decision log, or `MMI_CURRENT_STATE.md` writes from validator |
| T2A-T7 | Human verify after closeout | Human-run `mmi_dispatch.py --verify` after MMI closeout (not validator) |
| T2A-T8 | Forbidden vocabulary | Stdout never contains banned words from §3 |
| T2A-T9 | Multi-field rejection | Multiple missing fields → single `REJECT_INCOMPLETE_PACKET` with **all** applicable reason codes |
| T2A-T10 | Accept-side immutability | After `ACCEPT_FOR_MMI_REVIEW`: no change to `MMI_CURRENT_STATE.md`, scoreboard, dispatcher output, task registry, `mmi/MMI_DECISION_LOG.md`, or build/component status |
| T2A-T11 | Write containment | Mode A: zero file writes; Mode B (if built): only `mmi/MMI_INTAKE_RECORDS.md` |
| T2A-T12 | Auto-commit ban | Validator does not stage, commit, or push |

---

## 15. Sign-off

**§11 SIGNED — Matt Nichol 2026-06-19.**

This §11 signature approves the contract only. It does **not** authorize implementation. Build authorization must be issued separately after signature before creating `scripts/mmi_packet_intake.py` or any Tier 2A code.

**Contract configuration recorded at signature (not build authorization):**

| Setting | Recorded at §11 |
|---|---|
| Selected implementation mode | **Mode A** — stdout-only, zero file-write authority |
| Mode B | **Not selected — remains parked** |

**Mode B** (stdout + narrow append to `mmi/MMI_INTAKE_RECORDS.md`) remains parked unless Matt separately signs or authorizes Mode B in a future contract revision **and** names Mode B in a separate build authorization. **First build authorization, if issued, must name Mode A only.**

> Matt Nichol June 19th 2026

---

**End of Tier 2A contract. §11 signed; Tier 2A implementation requires separate build authorization (Mode A only).**
