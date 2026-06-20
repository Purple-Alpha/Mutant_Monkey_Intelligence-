# MMI Task Registry — Manual Update Rules (Mode A)

**Status:** Tier 2B Mode A procedural guide. **Human-maintained only.** Not automation authority.

**Registry instance:** `mmi/MMI_TASK_REGISTRY.yaml`

**Signed contract:** `mmi/MMI_AUTONOMOUS_BRAIN_TIER2B_PASSIVE_TASK_REGISTRY_CONTRACT_DRAFT.md` (§11 SIGNED 2026-06-19; Mode A selected; Mode B parked)

---

## Authority boundary

This registry is **passive instance data only**:

- not AUTH-3B automation
- not dispatcher input (`dispatcher_reads` must remain `false`)
- not autonomous task selection (`autonomous_selection` must remain `false`)
- not build authorization, worker assignment authority, or routing advance
- does not replace signed contracts, git commits, `python3 scripts/mmi_dispatch.py --verify`, `mmi/MMI_DECISION_LOG.md`, or `mmi/MMI_INTAKE_RECORDS.md`

---

## Who may edit

Humans only (Matt / MMI workflow). No machine writer. No background sync from scoreboard, git, or dispatcher.

---

## Envelope updates (required on every human edit)

Update on each manual registry change:

- `last_human_update_at` — ISO-8601 UTC
- `last_human_update_ref` — `MMI-DEC-*`, operator instruction name, or session note

Do **not** change:

- `dispatcher_reads` (must stay `false`)
- `autonomous_selection` (must stay `false`)
- `maintained_by` (must stay `human`)

Bump `registry_version` only when Matt authorizes a schema/envelope revision.

---

## Adding or updating task rows

1. Assign stable `task_id` (`TASK-YYYY-MM-DD-NNN`); never reuse for different scope.
2. Set `status` from the closed enum in contract §9 only.
3. Provide non-empty `source_evidence` and `status_evidence` for the **current** status.
4. Apply only allowed transitions from contract §10.1; never skip evidence steps.
5. Append `transition_log` entries when recording status changes (recommended).
6. Never delete rows with status `PARKED`, `REJECTED`, `SUPERSEDED`, `CONTRADICTION`, or `DO_NOT_USE` unless Matt explicitly authorizes hard deletion (corrupt write only).

---

## Status semantics (do not launder)

| Status | Remember |
|---|---|
| `CANDIDATE` | Not selected or next task |
| `SIGNED_CONTRACT` | Not build authorized |
| `BUILD_AUTHORIZED` | Requires `MMI-DEC-*` or operator instruction with explicit build authorization |
| `ACCEPTED_FOR_REVIEW` | Review workflow only — not approved or complete |
| `COMPLETE` | Lifecycle record with closeout evidence — not verify PASS or routing completion |

Full rules: contract §9.1, §10, §11, §12.

---

## After routing-authority MMI closeout

When registry edits accompany `MMI_CURRENT_STATE.md`, decision log, or intake updates: human runs `python3 scripts/mmi_dispatch.py --verify` after commit. Registry tooling does not run verify.

---

**End of manual update rules. Mode B structural validator not implemented.**
