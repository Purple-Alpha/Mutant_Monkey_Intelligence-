# #70 Final Review Agent — Boundary Review (MMI-DEC-240)

**Date:** 2026-06-26  
**Lane:** `DRIFT_CHECK` / `DESIGN`  
**Authority:** Matt depth-queue selection (MMI-DEC-222 step 3) after #66 RECLASSIFY (MMI-DEC-236). **Not** build authorization.

---

## Question

Does scoreboard **#70 Final Review Agent** need a new Agent Design Contract, ES1 wrapper build, merge with `complete_gate.py` / `package_auditor.py`, or **RECLASSIFY**?

---

## Evidence reviewed

| Source | Finding |
|--------|---------|
| Scoreboard #70 | `GOVERNANCE_DOC_ONLY (partial)`; blocker `NEEDS_BUILD_AUTH`; cites `complete_gate.py` + `package_auditor.py` |
| Design tree §1.5 / Level 6 | Confirms verdict+evidence+explanation+action match; releases final decision record — **case-level** audit |
| Reconciliation Q1 (pinned) | #70 → Layer 6 Learning/Governance; restrictive tiebreaker — in Command it could authorize its own outputs |
| `audit_tools/complete_gate.py` | Infrastructure negative-feedback auditor at **readiness boundaries** (done/ship/commit claims). Not an agent. Does not mark work complete. Operator/build-time choke point. |
| `core/evidence_package/package_auditor.py` | Stage 9 **package content** Grok audit (synthetic/test v1). Separate explicit invocation; mirrors gate pattern. Not wired into package generation. |
| `core/orchestrator/agent_contract.py` | `FINAL_REVIEW_AGENT_ID = "final_review_001"` — sole permitted `audit_record_id` writer on DER (builder-auditor separation) |
| `tests/test_agent_contract.py` | Schema rejects `audit_record_id` unless `audit_writer_agent_id == final_review_001` |
| `core/orchestrator/evidence_package_agent.py` | #46 builder explicitly defers audit to Layer 6 / `final_review_001` path |
| Scoreboard #46 | `GOVERNED_AGENT` — assembles packages; does **not** audit |
| Scoreboard #5 | `GOVERNANCE_DOC_ONLY` — Decision Integrity / rubric contradiction guard (distinct slice) |
| Scoreboard #69 | `NOT_STARTED` — Swarm Health (agent consistency/conflict); distinct row |
| Architecture map | #70 = "verdict+evidence+explanation+action match; final decision record" |
| Repo search | No `final_review_agent.py` or governed `FinalReviewAgent` wrapper |

---

## Verdict

**GOVERNANCE_DOC_ONLY (partial — surfaces mapped). Not RECLASSIFY.**

#70 names **two related but distinct functions**. Only the first is satisfied today.

### Slice A — Artifact completion audit (**satisfied**)

| Surface | Role |
|---------|------|
| `audit_tools/complete_gate.py` | Readiness-boundary negative-feedback audit when work is claimed done/ready to ship |
| `core/evidence_package/package_auditor.py` | Evidence-package content audit vs signed contract (Stage 9; synthetic v1) |

Both are **infrastructure / operator tools**, not governed agents. Both are negative-feedback auditors only — they do not approve, score strategy, or self-authorize outputs. This matches the "check over before done" anxiety for **artifacts and build claims**.

**Do not merge these into a single Final Review agent.** They are deliberately outside the swarm dispatch loop.

### Slice B — Case-level DER final review (**not built**)

| Requirement | State |
|-------------|-------|
| Confirm verdict + evidence + explanation + recommendation coherence on a **case** | No runtime module |
| Write `audit_record_id` on assembled DER | Schema reserved for `final_review_001`; **no agent implementation** |
| Layer 6 read-only governed wrapper | Missing — L6 promotion bar requires signed contract + structural read-only constraint |

This slice is **intentionally deferred** in the spine (`agent_contract.py` hook) and is **not** satisfied by `complete_gate` or `package_auditor`.

### Distinct neighbors (do not conflate)

| Row | Relationship |
|-----|----------------|
| #5 Decision Integrity | Rubric / contradiction guard — governance doc, not DER audit writer |
| #46 Evidence Package | Builder; auditor separation requires #70 slice B |
| #69 Swarm Health | Agent consistency/conflict — separate future contract |
| #66 Drift Watch | RECLASSIFY process-only — different problem (#70 has real schema hook) |

---

## Recommendation

1. **Keep** status `GOVERNANCE_DOC_ONLY (partial — surfaces mapped)`.
2. **Change blocker** `NEEDS_BUILD_AUTH` → `NEEDS_SIGNED_CONTRACT` (stale build blocker implied Cursor could build without contract — violates L6 bar and self-approval risk).
3. **Next step (operator choice):** Claude drafts `Final_Review_Agent_Design_Contract_Deep_Dive.md` scoped to **Slice B only**; Codex pre-build gate; Matt §11; then separate explicit build authorization.
4. **Hold** ES1 wrapper until contract pins: no `build_default_registry`, no production dispatch, no self-approval of DER outputs.

---

## Scoreboard action

- Status: `GOVERNANCE_DOC_ONLY (partial — surfaces mapped)` (MMI-DEC-240)
- Blockers: `NEEDS_SIGNED_CONTRACT`
- Re-triage trigger: Matt authorizes contract lane, or amends scope to drop Slice B (would require spine amendment to `audit_record_id` rule)

---

## Depth queue closeout (MMI-DEC-222)

| Step | Agent | Outcome |
|------|-------|---------|
| 1 | #19 Dual-Approval | GATED → GOVERNED_AGENT (MMI-DEC-238) |
| 2 | #66 Drift Watch | RECLASSIFY (MMI-DEC-236) |
| 3 | #70 Final Review | Surfaces mapped (MMI-DEC-240) |
| hold | #43 Geo-Context | Research only |

---

## Boundaries

- No build authorization
- No §11 signing
- No scoreboard promotion to `GOVERNED_AGENT`
- No production dispatch
- No merging Slice A tools into a dispatchable agent without new contract scope
