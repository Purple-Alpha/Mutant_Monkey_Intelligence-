# Dual-Approval Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_19_DUAL_APPROVAL_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** DRAFT (pre-§11). Advisory placement only — **not** §11 signed, **not** build authorized, **not** scoreboard lifecycle mutation, **not** production dispatch. Routed by MMI-DEC-222 (Matt selected #19 contract lane).

**Owner:** Matt Nichol

**Candidate:** #19 — Dual-Approval

**Track:** BREADTH / Vendor-payment verification (Layer 3 Verification scoreboard row)

**Lane:** Agent Design Contract (project-brain active task · score 8/10)

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** Not built. Scoreboard `SPEC_ONLY` · blocker `NEEDS_SIGNED_CONTRACT`.

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `4. Product_Roadmap/Vendor_Payment_Verification_Workflow_Ergonomics_Deep_Dive.md` (upstream workflow ergonomics — DRAFT pre-§11; trigger feedstock)
- `4. Product_Roadmap/Two_Channel_Confirmation_Enforcement_Deep_Dive.md` (§11 signed workflow — read-only boundary)
- `4. Product_Roadmap/Callback_Verification_Agent_Design_Contract_Deep_Dive.md` (#18 sibling — callback OOB projector)
- `4. Product_Roadmap/Verification_Outcome_Agent_Design_Contract_Deep_Dive.md` (#48 sibling — generic two-channel projector)
- `4. Product_Roadmap/Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` (payment-destination delta findings)
- `4. Product_Roadmap/Research_Inputs/Vendor_Payment_Change_Verification_Research_Report.md` (advisory thresholds — not locked)
- `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` (forbidden-language + advise boundary)
- `4. Product_Roadmap/Gap5_Memory_Consolidation_Tenant_Baseline_Ingestion_Design_Contract.md` (SoD pattern: `approver_1 ≠ approver_2`, requester cannot approve)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#19 row)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (missing-evidence: "No second-person approval recorded yet")
- `VISION.md` (Stage A — analyze / recommend / evidence only)

**Proposed future build path (not authorized here):** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/dual_approval_agent.py`

---

## Agent Design Contract block

**Boundary:** This contract governs the Dual-Approval **agent wrapper** (`DualApprovalAgent`). It is additive governance under template §7.0. It does **not** edit, reinterpret, relax, or extend any §11-signed detector contract, Two-Channel Confirmation workflow write semantics, or Vendor Payment Verification workflow disposition rules. Those remain immutable.

| Field | Value |
|---|---|
| Agent name | Dual-Approval Agent (`DualApprovalAgent`) |
| Swarm inventory ID | #19 — Dual-Approval |
| Canonical layer | 3 — Verification |
| Canonical team / case type | Vendor-payment / BEC — separation-of-duties on payment or banking-detail release |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (see template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic.** Validated on synthetic / replayed payment scenarios only; intentionally NOT registered in `build_default_registry` / production dispatch. |
| Role | Consume upstream Vendor Payment Verification evidence and, when risk criteria are met, **raise a dual-approval requirement** with a bounded evidence packet — and, when integrated, **surface** customer-recorded approval state. Never approve, hold, release, or move money. |
| Boundary | Workflow signal only. Enforcement is the customer's control plane. MMI is **not** one of the two approvers. |
| Explicit non-authorities | No payment execution, hold, release, block, or reversal; no auto-approval; no approver impersonation; no claim that a payment is safe or fraudulent; no autonomous action; no buyer-facing compliance guarantee; no default-registry registration at ES1; no AUTH-5. |
| Inputs | One explicit verification request per call: `tenant_id`, `finding_id`, closed `verification_class=vendor_payment_dual_approval` (or successor enum), optional `case_id` / `source_record_id`, Blackboard root/environment. Upstream evidence references only — agent does not re-run detectors or derive payment risk from raw email/financial strings. |
| Outputs | One `AgentContribution` (layer 3): closed dual-approval facts + `verification_source` + `verification_outcome`. No challenge/evidence/control fields at Stage 1 beyond the closed fact set. |
| Evidence emitted | Closed facts only, e.g. `dual_approval_required`, `dual_approval_pending`, `dual_approval_satisfied`, `dual_approval_missing`, `dual_approval_not_applicable` (single-owner fallback path when policy marks no second approver). No approver identities, payment amounts, routing/account strings, or raw finding payloads in the contribution. |
| Data minimization | No mailbox body, no raw financial identifiers, no approver PII, no payment destination strings, and no operator free-text in the contribution — only closed-set indicator names and bounded linkage refs (`finding_id`, `case_id`). |
| Tenant isolation | Reads only tenant-scoped upstream evidence for the supplied `tenant_id`; tenant A requirements never surface for tenant B. |
| Two-pass role | Pass 1 Verification only. `challenge()` returns `None`. |
| Decision Evidence Record contribution | `observed_facts`: closed dual-approval requirement/state facts; `interpretations`: none; `assumptions`: upstream Vendor Payment Verification / payment-change pipeline produced the cited finding; customer-side approval records (if any) are authoritative for satisfaction; `missing_evidence`: e.g. no second-person approval recorded yet (design-tree pattern); `recommended_verification`: none emitted at Layer 3 (Commander / customer workflow owns next step); `final_outcome_contribution`: dual-approval requirement/state facts only; `retest_or_learning_record`: per template §6.5. |
| Human review trigger | None authored by this agent; dual-approval satisfaction is always customer-human action outside MMI. |
| Verification trigger | This agent is a verification contributor; it does not initiate OOB contact, record disposition, or write Two-Channel pending/outcome events. |
| Scoring / action posture | Facts-only + Layer 3 verification outcome. No risk-floor lift/lower, no rubric mutation, no payment-authorization language. |
| Default rollout | Evidence Stage 1 — not in `build_default_registry`; explicit callers/tests only until signed promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`. |
| Promotion conditions | Per template §6.2 Stage 1→2 bar: clean tests, supervised vendor-payment samples, signed promotion record. |
| Demotion conditions | Per template §6.3. False-negative on real fraud (failed to raise dual-approval when required) is the highest-severity demotion trigger. |
| Retest evidence | Per template §6.5 progressive hardening — every false-negative → permanent regression test. |
| Calibration requirement | ES1 synthetic fixtures only; Stage 2 requires supervised vendor-payment samples and separate real-data authorization if applicable. |
| Failure modes | See §5. |
| Required tests | `tests/test_dual_approval_agent.py` — wrapper protocol, trigger/skip paths, read-only upstream consumption, no workflow writes, no payment path, tenant isolation, no registry default. |
| Audit requirements | Step 00 `scripts/validate_agent_contract_block.py` PASS; pre-build gate via `audit_tools/complete_gate.py`; completion gate on implementation slice. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `Vendor_Payment_Verification_Workflow_Ergonomics_Deep_Dive.md`, `Two_Channel_Confirmation_Enforcement_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`. |
| Build Authorization dependency | Contract placement only. No build until §11 + operator build authorization. Upstream workflow/detector behavior remains immutable. Distinct from #18 callback OOB and #48 generic two-channel projectors — #19 owns the dual-approval governed slot only. |

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-26 (draft placement · MMI-DEC-222 lane):

| GAP (advisory draft) | Resolved value | Repo evidence |
|---|---|---|
| **#19 repo home** | `4. Product_Roadmap/Dual_Approval_Agent_Design_Contract_Deep_Dive.md` | All Agent Design Contracts live in `4. Product_Roadmap/` per template §1; runtime wrapper under `core/orchestrator/`, not `core/scoring/` |
| **Vendor Payment Verification feedstock** | `Vendor_Payment_Verification_Workflow_Ergonomics_Deep_Dive.md` — operator disposition workflow after Delta Tripwire flags a vendor-payment change; **not** a separate swarm agent ID | Scoreboard code-evidence label; FSL deferral §1; workflow §0–§5 |
| **§3 trigger set (authoritative)** | Raise `dual_approval_required` when **all** hold: (a) upstream payment-change finding is open/`awaiting_disposition` or has active two-channel `pending` without terminal outcome; **and** (b) at least one risk signal from the closed set in §3.1 is present in upstream evidence. Agent does **not** invent triggers from raw mail. | Workflow §0–§4; Two-Channel §0–§3; design-tree missing-evidence example |
| **Evidence schema (upstream)** | Disposition record §5.1 (`finding_id`, `disposition`, `verification_channel`, `what_was_confirmed`, `recorded_by`, `recorded_at_utc`, linkage refs) + `TwoChannelConfirmationPayload` (`event_type`, `finding_id`, `detector`, `outcome_status`, `channel_kind`) — read-only consumption | Workflow ergonomics §5; Two-Channel §3 |
| **Template section numbering** | This file follows template §0–§11 + Agent Design Contract block per #18/#21 pattern | `Agent_Design_Contract_Template_Deep_Dive.md` |
| **Evidence Stage 2/3 naming** | Stage 2 = Supervised; Stage 3 = Production per template §6.1 (not "Historical-real" / "Production-adjacent" informal labels) | Template §6.0–§6.1 |
| **Legal advise framing** | Inherited from `Compliance_and_Trend_Watch_Process.md` + workflow D5/D8 + `VISION.md` — MMI advises; customer decides and carries liability | See §8 |

**Remaining open (Matt / upstream §11):**

| Open item | Blocker |
|---|---|
| Workflow ergonomics §10 Q1–Q6 | Follow-up SLA, relation to two-channel enum, on-disk surface, false-positive auto-link, who may record, idempotency — workflow spec pre-§11 |
| Workflow ergonomics §11 | Upstream feedstock UNSIGNED |
| Locked payment-amount / tier thresholds for #19 | Research report advisory only; design tree says "larger payment changes" without numeric lock |
| Single-owner business fallback policy | Research notes substitute controls; product policy choice for `dual_approval_not_applicable` |
| Contract §11 signature | Scoreboard `NEEDS_SIGNED_CONTRACT` |
| Explicit build authorization | Separate from §11 per established MMI pattern |

---

## §0 Purpose — the one invariant

**MMI raises a dual-approval requirement and supplies the evidence. It never moves, holds, releases, or approves a payment, and it is never one of the two approvers.** Both approvals are humans on the customer side. The moment this component touches the money flow, it is enacting — and detect-not-enact is broken. Every clause below exists to keep it on the detect/advise side of that line.

Complete the contract lane for swarm #19: place a full Agent Design Contract governing the future `DualApprovalAgent` wrapper over upstream Vendor Payment Verification evidence without changing signed detector or workflow semantics. Closes governance parity gap (#19 at `SPEC_ONLY` with workflow draft reference only).

---

## §1 Scope

### In scope

- Agent Design Contract block governing `DualApprovalAgent`.
- Evidence Stage 1 (Synthetic) declaration.
- Read-only consumption of upstream Vendor Payment Verification / payment-change evidence.
- Closed-set dual-approval requirement and state facts (§3–§4).
- Focused test plan proving Agent contract → AgentContribution → Blackboard → DER path.

### Out of scope

- Any change to Delta Tripwire / FSL detector logic, Two-Channel Confirmation workflow writes, or Vendor Payment Verification disposition write semantics.
- Autonomous payment action (approve, block, hold, release, reverse).
- Acting as or impersonating either approver.
- Default registry / production dispatch at ES1.
- Buyer-facing compliance or insurance claims.
- Replacing #18 callback OOB projection or #48 generic two-channel projection.

---

## §2 Locked Design Decisions

- **D1 — Identity.** Dual-Approval is Layer 3 Verification, Authority Level 3, VISION Stage A, Evidence Stage 1 at signing. `agent_id = dual_approval_001`.
- **D2 — Upstream immutability.** Wrapper-only; signed detector and workflow contracts immutable (template §7.0).
- **D3 — Facts-only contribution.** Emits only closed dual-approval facts; no payment authorization language, amounts, or approver identities.
- **D4 — Input surface.** Caller-supplied `tenant_id` + `finding_id` + verification class; reads upstream evidence by reference — no raw email/financial re-parse.
- **D5 — Separation of duties.** When dual approval applies: `approver_1 ≠ approver_2` and requester cannot be either approver (Gap5 TBI pattern — customer-side enforcement; MMI surfaces requirement only).
- **D6 — Not an approver.** MMI never counts toward the two approvals; satisfaction facts are read-only projections of customer-recorded state when integrated.
- **D7 — Stage A / no autonomy.** No block/quarantine/deny; no autonomous action.
- **D8 — Evidence Stage governance.** Template §6.2 / §6.3 / §6.5 apply; false-negatives weighted heaviest in Health Score.
- **D9 — Data minimization + tenant isolation.** Per-tenant evidence reads; no cross-tenant approval state.
- **D10 — Tests are promotion-bar evidence.** `tests/test_dual_approval_agent.py` is the ES1 runtime proof baseline once wrapper is built.

---

## §3 Trigger logic and upstream evidence

### §3.1 Closed trigger signal set

Raised when upstream Vendor Payment Verification evidence shows risk on a payment or banking-detail change. Typical upstream signals (house-pattern intent reconciled to repo — agent consumes evidence refs, does not re-derive):

| Signal class | Upstream source |
|---|---|
| New or changed payee banking details | Delta Tripwire / #14 payment-change facts (`Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md`) |
| Open payment-change finding awaiting disposition | Workflow ergonomics §4 step 1 (`awaiting_disposition`) |
| Active two-channel `pending` without terminal `outcome` | `Two_Channel_Confirmation_Enforcement_Deep_Dive.md` §3 |
| New/unrecognized vendor (when surfaced in upstream evidence) | Vendor-payment pipeline / baseline mismatch facts |
| Look-alike or mismatched sender domain (when cited in upstream packet) | Layer 2 facts from #10 / related detection — by reference only |
| Reply-chain / thread-forgery indicators (when cited) | Upstream BEC evidence packet — by reference only |
| Executive / urgency pressure markers (when cited) | Layer 2 facts from #21 / pressure vocabulary — by reference only |

**Research advisory (not locked D-decisions):** second-person approval when a second approver exists; bank-detail changes treated as high risk regardless of amount; stronger controls at higher payment tiers (`Vendor_Payment_Change_Verification_Research_Report.md`).

### §3.2 Upstream evidence schema (read-only)

**Disposition-side (workflow ergonomics §5.1):** `disposition_id`, `tenant_id`, `finding_id`, `disposition` (`verified` \| `unresolved` \| `false_positive` \| `follow_up_needed`), `verification_channel`, `what_was_confirmed`, `recorded_by`, `recorded_at_utc`, linkage refs.

**Two-channel-side (§3 schema):** `TwoChannelConfirmationPayload` with `event_type` (`pending` \| `outcome`), `finding_id`, `detector`, `outcome_status` (`confirmed` \| `rejected` \| `unable_to_verify` \| `expired`), `channel_kind` (closed enum).

### §3.3 Skip / not-applicable

Emit `dual_approval_not_applicable` only when a signed customer policy marks single-owner fallback (§9 OQ-1). Default when uncertain: raise requirement or `dual_approval_missing` — never silently skip on ambiguous upstream evidence.

---

## §4 What MMI does — and explicitly does not

| Does | Does NOT |
|---|---|
| Raise `dual_approval_required` + attach bounded evidence refs | Execute, block, hold, release, or reverse a payment |
| Surface approval state when customer records exist (read-only) | Approve, or act as either approver |
| Supply reasoning a human approver needs (via upstream packet refs) | Impersonate a person or auto-clear |
| Log the requirement for audit via standard contribution path | Guarantee a payment is safe or fraudulent |
| Emit `dual_approval_missing` when policy requires two approvals and none recorded | Lower trigger sensitivity below agreed floor to reduce friction |

---

## §5 Failure modes

- **False-negative (dangerous):** failed to raise dual-approval on a real fraud where policy required it → permanent regression + demotion review (template §6.5).
- **False-positive:** raised requirement on a legit payment → friction cost; tune only with signed policy change, never by silent threshold relaxation.
- **Enactment creep:** any code path that holds/releases/approves payment → hard fail / demotion.
- **Approver impersonation:** MMI recorded as an approver → hard fail.
- **Upstream conflation:** re-running detectors or writing disposition/two-channel events from this wrapper → hard fail (same class as #18/#48 boundary violations).
- **Raw financial leakage:** routing/account/body/approver identity in contribution → hard fail.
- **Tenant contamination:** cross-tenant approval state → hard fail.

---

## §6 Evidence Stage, promotion, and demotion

Per `Agent_Design_Contract_Template_Deep_Dive.md` §6:

| Stage | Data | May do | May NOT do |
|---|---|---|---|
| **1 — Synthetic** *(current)* | Synthetic / replayed vendor-payment scenarios | Raise + surface requirements in sandbox | Real tenant data; touch live payments |
| **2 — Supervised** *(proposed)* | Privacy-filtered real past vendor-fraud cases (`#93` linkage when authorized) | Validate triggers vs actual incidents | Live payment systems |
| **3 — Production** *(proposed)* | Live verification signal | Raise requirements on real flow | **Move/approve money — never, any stage** |

Promotion/demotion: template §6.2–§6.3. Progressive hardening §6.5: every miss → permanent regression test.

---

## §7 Hard limits

- **No money-movement path** — by construction.
- **No auto-approval, no approver impersonation.**
- **Human decision is final and carries the liability** — MMI advises; customer decides.
- **AUTH-5 blocked.** Safe-Stop (Matt-only) halts the agent.
- Scoreboard row + Health Score; dispatcher-routed when build-authorized.

---

## §8 Legal / non-guarantee

This component sits on a money-loss surface. Binding posture:

- MMI **advises**; does not guarantee a transaction's legitimacy.
- Customer retains the decision and the liability.
- Forbidden-language scope: `Compliance_and_Trend_Watch_Process.md` (inherited verbatim).
- Workflow ergonomics D5/D8: disposition / verification outcome **does not** authorize payment.
- Contractual liability framework remains open (`VISION.md` BL1 milestone) — **legal scoping is a prerequisite before §11**, not a parallel task.

---

## §9 Open questions (operator-only)

- **OQ-1 — Single-owner fallback:** When no second approver exists, what substitute controls are required before emitting `dual_approval_not_applicable` vs `dual_approval_required` with owner-only delay? (Research suggests callback + delay + micro-deposit — product policy choice.)
- **OQ-2 — Amount / tier thresholds:** Lock numeric tiers for dual-approval trigger, or treat all bank-detail changes as triggering regardless of amount? (ICAEW / research favor all bank-detail changes; design tree mentions "larger payment changes" only.)
- **OQ-3 — Workflow ergonomics §10:** Resolve Q1–Q6 on upstream workflow spec before treating disposition records as authoritative feedstock for Stage 2.
- **OQ-4 — Customer approval record surface:** Where customer-side dual-approval satisfaction is recorded for read-only projection (external to MMI vs future tenant workflow module).

---

## §10 Audit requirements

- Step 00: `python3 scripts/validate_agent_contract_block.py` on this file — expect PASS before pre-build gate.
- Pre-build gate: `audit_tools/complete_gate.py` with manifest listing all `files_read` source contracts.
- Adversarial cross-check focus before §11: **can an attacker suppress the dual-approval trigger** (false-negative path)?
- Completion gate on implementation slice after build authorization.

---

## §11 Sign-off

```
§11 — Dual-Approval Agent (#19) Design Contract (Deep Dive)
Authority: Matt Nichol (sole signer)
Signature: __________________________   Date: __________
[UNSIGNED — advisory lane; pre-build gate not run; not build authorization]
```

**Signing locks D1–D10 and authorizes Evidence Stage 1 wrapper build + focused tests only.** It authorizes **no** upstream workflow/detector change, **no** default-registry registration, **no** production dispatch, **no** autonomous action, and **no** AUTH-5.

---

## Execution checklist (post-§11 — not authorized in this slice)

1. Resolve OQ-1–OQ-4 and upstream workflow §10 + §11.
2. Pre-build gate (Codex) on this contract — manifest with `files_read`.
3. Matt §11 signature.
4. Operator build authorization → wrapper at proposed build path.
5. Completion gate 0/0 + tests.
6. Closeout: `lane_board_sync` → `dispatch --sync` → `dispatch --verify` → `pmv`.
