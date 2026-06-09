# Verification Outcome Agent Design Contract — Boundary / Unblock Deep Dive

**Status:** DRAFT — authored by the LIVE Build Map (CYCLE 25, BREADTH) after row-order triage annotated the remaining vendor-payment frontier (#13/#15/#16/#17/#20) as RECLASSIFY / merged and selected swarm #48 Verification Outcome as the first actionable boundary contract. The existing `core/workflows/two_channel_confirmation.py` workflow is useful and already §11-signed by its own implementation spec, but it is a stateful append-only workflow/audit surface (`pending` and `outcome` events), not a pure detector. It therefore requires an explicit Agent Design Contract before becoming a governed Layer 3 Verification agent. **No implementation lands until the §11 Lockdown Signature below is filled in by the operator.** Signing locks D1-D10 and authorizes the Evidence Stage 1 (Synthetic) `VerificationOutcomeAgent` wrapper build + focused tests **only**. It authorizes **no workflow write-path change**, **no new outcome enum**, **no contact execution**, **no payment approval/denial**, **no risk-floor lowering**, **no default-registry registration**, **no production dispatch**, **no real-customer-data handling**, **no Evidence Stage 2/3 promotion**, **no scoring/rubric change**, and **no autonomous action**.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey** only where separately signed buyer-facing specs require it. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Build_Map_Deep_Dive.md` (LIVE build authority; CYCLE 25 TRIAGE -> DRAFT_CONTRACT -> OPERATOR_LOCK)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (governing template; Evidence Stage model)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#48 Verification Outcome; Layer 3 Verification)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `4. Product_Roadmap/Two_Channel_Confirmation_Enforcement_Deep_Dive.md` (§11-signed workflow contract; append-only pending/outcome events; lift-only; no contact execution)
- `4. Product_Roadmap/Vendor_Payment_Verification_Workflow_Ergonomics_Deep_Dive.md` (draft ergonomics/workflow context; not build authority for this wrapper)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/workflows/two_channel_confirmation.py` (`summarize_confirmation_status`, `ConfirmationRecord`, `record_confirmation_request`, `record_confirmation_outcome`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent`, `AgentContribution`, `VerificationOutcome`, `DecisionEvidenceRecord`)
- `VISION.md` (Stage A = analyze / recommend / evidence only; seven non-negotiables)

---

## Agent Design Contract block

**Boundary:** This contract governs a future Verification Outcome **agent wrapper** around the existing signed Two-Channel Confirmation workflow record surface. It is additive governance under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend the §11-signed Two-Channel Confirmation workflow contract, append-only event model, closed outcome/channel enums, kill-switch behavior, tenant isolation, lift-only invariant, or existing workflow write-path behavior.

| Field | Value |
|---|---|
| Agent name | Verification Outcome Agent (`VerificationOutcomeAgent`) |
| Swarm inventory ID | #48 — Verification Outcome |
| Canonical layer | 3 — Verification |
| Canonical team / case type | Evidence / audit and vendor-payment verification; projects an existing two-channel-confirmation workflow state into a bounded `AgentContribution` |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed. Validation is synthetic-only and uses isolated Blackboard tenant state. Intentionally NOT registered in `build_default_registry` / production dispatch. Advancement requires template §6.2 and Matt-signed promotion. |
| Role | Produce bounded verification-outcome evidence by reading the current `ConfirmationRecord` for one caller-supplied `finding_id` and translating the workflow state into closed facts plus Layer 3 `verification_source` / `verification_outcome`. |
| Boundary | This is a read-only Verification agent over an existing workflow/audit trail. The wrapper may call `summarize_confirmation_status(...)` only for the case finding it was asked to project. It must not call `record_confirmation_request`, `record_confirmation_outcome`, `submit_two_channel_confirmation`, contact anyone, mutate workflow state, lower risk, approve/deny payment, or treat a `confirmed` outcome as authorization to pay. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no payment approval/denial/release/hold; no out-of-band contact execution; no email/SMS/phone/chat workflow; no network/HTTP/DNS/WHOIS/reputation lookup; no workflow enum/schema change; no event mutation or deletion; no second outcome write; no risk-floor lowering; no buyer-facing claim; no default-registry registration; no production dispatch at Evidence Stage 1; no Evidence Stage 2/3 promotion. |
| Inputs | One explicit verification-outcome request supplied by a trusted caller: `tenant_id`, `finding_id`, optional `case_id` / `source_record_id` context, and a Blackboard root/environment. The wrapper does not read raw email bodies, attachments, vendor contact details, payment details, or external systems. |
| Outputs | One `AgentContribution` (layer 3): `observed_facts` = closed two-channel workflow facts; `verification_source = "two_channel_confirmation:<finding_id>"` or a bounded equivalent; `verification_outcome` maps workflow status to the existing Layer 3 enum (`confirmed`, `contradicted`, `unable_to_verify`). No challenge/evidence/control fields are emitted. |
| Evidence emitted | Closed fact names only: `two_channel_confirmation_missing`, `two_channel_confirmation_pending`, `two_channel_confirmation_confirmed`, `two_channel_confirmation_rejected`, `two_channel_confirmation_unable_to_verify`, `two_channel_confirmation_expired`, optional bounded `two_channel_detector:<detector>`, and optional bounded `two_channel_channel_kind:<channel_kind>`. Operator labels, channel descriptions, reasons, timestamps, raw finding values, risk floors, vendor contact details, and payment details do not cross into the contribution at Stage 1. |
| Outcome semantics | `outcome_status="confirmed"` maps to `verification_outcome="confirmed"`. `outcome_status="rejected"` maps to `verification_outcome="contradicted"`. Missing record, pending record, `unable_to_verify`, and `expired` map to `verification_outcome="unable_to_verify"`. A `confirmed` outcome is evidence that a human recorded a verification result; it is **not** a payment authorization and does not lower risk. |
| Data minimization | The contribution emits no raw email body, attachment data, vendor-domain prose, payment destination, account/routing/IBAN/SWIFT/portal value, phone number, email address, operator label, channel description, reason text, timestamps, risk floor, recommended action, or file path. |
| Tenant isolation | Reads only the tenant-scoped Blackboard path for the supplied `tenant_id`. Stage 1 tests must use isolated synthetic tenant IDs and reset/contain Blackboard state. Tenant A's confirmation state never verifies tenant B. |
| Two-pass role | Pass 1 Verification only. `challenge()` returns `None`; Challenge / Final Review layers decide whether verification evidence is sufficient, contradictory, stale, or missing. |
| Decision Evidence Record contribution | `observed_facts`: closed two-channel workflow facts only; `interpretations`: none; `assumptions`: a trusted upstream detector/workflow created the `finding_id` and any pending/outcome event; `missing_evidence`: the agent does not perform the verification call or inspect external channels; `recommended_verification`: none emitted directly; `final_outcome_contribution`: current workflow-state projection only; `retest_or_learning_record`: every real-case miss or demotion trigger becomes a permanent regression test per template §6.5. |
| Human review trigger | None authored by this agent. The underlying Two-Channel Confirmation workflow may represent a human-review task, but this wrapper only projects current state. |
| Verification trigger | The agent is itself a verification contributor. It does not initiate verification, create a pending request, or record an outcome. |
| Scoring / action posture | Facts-only + Layer 3 verification outcome. The wrapper does not emit risk floors, recommended actions, payment decisions, explanation text, or client-facing rubric language. It never lowers an existing risk floor. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers/tests until a later signed promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; Stage A router guard rejects autonomy. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires clean suite, zero open test failures, Matt review of >= 3 supervised two-channel confirmation samples with expected outcomes, a `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. Any real-customer sample use requires the separate real-data/depth authorization gate. |
| Demotion conditions | Per template §6.3. Automatic: regression failure, cross-tenant Blackboard contamination, operator/channel/reason/raw-value leakage, workflow write from this wrapper, risk-floor lowering, out-of-layer contribution field write, unexpected network/subprocess call, enum/schema mutation, or scoring/rubric mutation. Matt-signed: auditor pattern flag, real miss that misled downstream Verification/Command, or signed Challenge contradiction pattern. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent regression test. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires supervised verification-outcome records with operator-reviewed expected outcomes. Stage 3 requires Drift Watch active and real-data controls signed/open. |
| Failure modes | See §5. |
| Required tests | See §6 — wrapper tests must prove missing/pending/confirmed/rejected/unable/expired behavior, read-only summary usage, no workflow writes, tenant isolation, persistence, guardrails, no default registry, no network/subprocess behavior, and no raw/operator/channel/reason/risk leakage. |
| Audit requirements | Any contract signature, implementation, or revision remains subject to `complete_gate.py`. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `Two_Channel_Confirmation_Enforcement_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, and canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At §11 signature, this agent is at **Evidence Stage 1** only. No build authorization is granted for Evidence Stage 2/3 registration, default registry, production dispatch, real-customer-data handling, workflow write-path changes, new outcome/channel enums, risk-floor lowering, payment decisions, contact execution, scoring/rubric changes, or autonomous action until promotion conditions in §6.2 are satisfied and a separate promotion/authorization record is signed. |

---

## §0 Purpose

Unblock swarm #48 Verification Outcome by defining the state boundary that kept it from being a clean wrap. The scoreboard row points at `two_channel_confirmation.py`, but that module is a workflow/audit primitive: it writes append-only `pending` and `outcome` events and summarizes the current state of a `finding_id`.

The safe Stage 1 agent is narrower than the workflow. It does not create requests, record outcomes, or contact vendors. It reads one existing workflow state and contributes a bounded verification outcome to the swarm evidence chain.

This contract is the governance step. It does not build runtime code until §11 signature / Build Authorization.

This contract also unblocks #47 Case Timeline conceptually, because a governed verification-outcome projection gives later Evidence-layer timeline work a stable verification-state input. It does not build #47.

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing a future `VerificationOutcomeAgent` wrapper as a Layer 3 Verification agent.
- Evidence Stage 1 (Synthetic) declaration at signature.
- Read-only use of `summarize_confirmation_status(...)` for one caller-supplied `finding_id`.
- Facts-only + verification-outcome contribution through the existing `AgentContribution` schema.
- Explicit prohibition on workflow writes, contact execution, payment decisions, and risk lowering.
- Preservation of existing Two-Channel Confirmation behavior and signed workflow boundaries.

### Out of scope
- Any change to `record_confirmation_request`, `record_confirmation_outcome`, `list_pending_confirmations`, `summarize_confirmation_status`, `ConfirmationRecord`, `TwoChannelConfirmationPayload`, closed enums, append-only behavior, kill-switch behavior, tenant isolation, or lift-only invariant.
- Calling `record_confirmation_request`, `record_confirmation_outcome`, `submit_two_channel_confirmation`, or any private workflow write helper from the wrapper.
- Executing out-of-band contact by email, phone, SMS, chat, portal, network lookup, or CRM lookup.
- Emitting operator labels, channel descriptions, reason text, timestamps, risk floors, recommended actions, raw payment details, raw finding values, vendor-domain prose, raw email body, attachment metadata, or file paths through the agent contribution.
- Registering the agent in `build_default_registry` or production dispatch.
- Real-customer-data handling or Evidence Stage 2/3 promotion.
- Any autonomous action, buyer-facing claim, payment approval/denial, or Stage B/C autonomy.

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

- **D1 — Identity.** Verification Outcome is a Layer 3 Verification agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = verification_outcome_001`.
- **D2 — Read-only workflow boundary.** The only authorized Two-Channel Confirmation workflow call from the wrapper is `summarize_confirmation_status(...)`. The wrapper must not call `record_confirmation_request`, `record_confirmation_outcome`, `submit_two_channel_confirmation`, or any write path.
- **D3 — Source restriction.** The `finding_id` must be supplied by an explicit governed caller/workflow. The agent does not discover findings, create pending tasks, or infer outcomes from raw email.
- **D4 — Workflow immutability.** This contract changes no Two-Channel Confirmation workflow behavior, payload schema, enum, append-only model, kill-switch behavior, tenant isolation, risk-floor lift-only invariant, scoring/rubric behavior, or pipeline wiring. It governs the wrapper only.
- **D5 — Facts-only verification contribution.** The agent emits closed observed facts plus `verification_source` and `verification_outcome` allowed for Layer 3. It emits no score, action, explanation, client-facing wording, operator label, channel description, reason, timestamp, risk floor, payment data, challenge field, or evidence field.
- **D6 — Outcome semantics.** `confirmed` maps to `verification_outcome="confirmed"`. `rejected` maps to `verification_outcome="contradicted"`. Missing, pending, `unable_to_verify`, and `expired` map to `verification_outcome="unable_to_verify"`. None of these outcomes authorizes payment or changes risk.
- **D7 — Persistence + rollout.** Contributions persist via the registry-gated `AGENT_CONTRIBUTION` route. The agent is NOT in `build_default_registry`; it is wired only by explicit callers until signed promotion.
- **D8 — Stage A / no autonomy.** No block/quarantine/deny/reject; no payment decision; no legitimacy declaration; no autonomous action; the agent authors no disposition.
- **D9 — No contact/channel side effects.** The wrapper never sends email, calls phones, opens chat/SMS, queries DNS/WHOIS/reputation, fetches CRM data, or performs network/subprocess calls.
- **D10 — Tests are the Stage 1 evidence.** The wrapper test suite must include missing/pending/confirmed/rejected/unable/expired state handling, read-only summary behavior, no workflow writes, tenant isolation, persistence, default-registry exclusion, no network/subprocess behavior, and no raw/operator/channel/reason/risk leakage before the build can close.

---

## §3 Data surface and output schema

- **Reads:** caller-supplied `tenant_id`, `finding_id`, optional `MissionContext.case_id` / `source_record_id` for persistence context, Blackboard root/environment.
- **Underlying primitive:** `summarize_confirmation_status(tenant_id, finding_id, blackboard_root)` returns `ConfirmationRecord | None`.
- **Emits:** `AgentContribution(agent_id="verification_outcome_001", layer=3, observed_facts=<closed two-channel facts>, verification_source="two_channel_confirmation:<finding_id>", verification_outcome=<confirmed|contradicted|unable_to_verify>)`.
- **Allowed fact vocabulary:** `two_channel_confirmation_missing`, `two_channel_confirmation_pending`, `two_channel_confirmation_confirmed`, `two_channel_confirmation_rejected`, `two_channel_confirmation_unable_to_verify`, `two_channel_confirmation_expired`, `two_channel_detector:<detector>`, `two_channel_channel_kind:<channel_kind>`.
- **Does not emit:** requested/outcome timestamps, requested_by/outcome_by, channel_description, reason, risk_floor, recommended_action, raw email body, attachment data, payment destination, account/routing/IBAN/SWIFT/portal value, phone number, email address, vendor-domain prose, file path, or client-facing explanation.

---

## §4 Evidence Stage declaration

- **Current Evidence Stage at signature: 1 — Synthetic.** Only synthetic-fixture validation will exist at initial build. Synthetic tests may exercise isolated Blackboard state, but no real tenant data.
- **To reach Stage 2 (Supervised):** all template §6.2 Stage 1->2 conditions, including Matt review of >= 3 supervised two-channel confirmation samples with expected outcomes and a signed `PROMOTION` entry. Real-customer samples require separate real-data/depth authorization.
- **To reach Stage 3 (Production):** template §6.2 Stage 2->3 conditions, including Drift Watch active. Reaching Stage 3 grants no autonomous action and no payment decision authority.
- **Demotion:** template §6.3 triggers apply.

---

## §5 Failure modes

- **Workflow-write creep** — wrapper records pending/outcome events or calls private write helpers. Mitigation: D2 and tests spying write paths.
- **Outcome overclaim** — `confirmed` is treated as payment approval or lowers risk. Mitigation: D6/D8 and facts-only Layer 3 contribution.
- **Contradiction loss** — `rejected` is flattened into `unable_to_verify` instead of `contradicted`. Mitigation: D6 mapping tests.
- **Raw/operator leakage** — operator labels, channel descriptions, reason text, timestamps, payment values, or raw finding values enter the contribution. Mitigation: D5 / §3 allowed vocabulary.
- **Contact execution creep** — wrapper sends email, calls phones, opens chat/SMS, or queries external services. Mitigation: D9 and no network/subprocess tests.
- **Tenant contamination** — one tenant's confirmation state verifies another tenant's finding. Mitigation: tenant-scoped Blackboard reads and synthetic isolation tests.
- **Kill-switch misunderstanding** — wrapper blocks read-only summaries during a production kill switch or mutates during a halt. Mitigation: signed workflow D12: read-only summaries remain available; wrapper has no write path.
- **Stage creep** — default registry or production dispatch while at Evidence Stage 1. Mitigation: D7 test.

---

## §6 Required tests

The implementation slice must add focused tests proving:

1. `VerificationOutcomeAgent` satisfies the shared `Agent` protocol.
2. Missing `finding_id` / no workflow record emits `two_channel_confirmation_missing` and `verification_outcome="unable_to_verify"`.
3. Pending confirmation emits `two_channel_confirmation_pending` and `verification_outcome="unable_to_verify"`.
4. Confirmed outcome emits `two_channel_confirmation_confirmed` and `verification_outcome="confirmed"`.
5. Rejected outcome emits `two_channel_confirmation_rejected` and `verification_outcome="contradicted"`.
6. Unable-to-verify outcome emits `two_channel_confirmation_unable_to_verify` and `verification_outcome="unable_to_verify"`.
7. Expired outcome emits `two_channel_confirmation_expired` and `verification_outcome="unable_to_verify"`.
8. The wrapper calls `summarize_confirmation_status` exactly once per explicit verification-outcome request.
9. The wrapper never calls `record_confirmation_request`, `record_confirmation_outcome`, `submit_two_channel_confirmation`, or private workflow write helpers.
10. Invalid `finding_id` or missing caller context fails closed.
11. Tenant isolation: the same `finding_id` under two tenant IDs does not share state.
12. Read-only summary remains available under production kill switch, and no wrapper write path exists.
13. Contribution persistence writes through `submit_agent_contribution` and round-trips through `AgentContributionPayload`.
14. `challenge()` returns `None`.
15. Unauthorized registry writes are rejected.
16. `digest_request` / equivalent input digest is deterministic.
17. Agent is not in `build_default_registry()`.
18. Contribution emits no requested_by/outcome_by, channel_description, reason, timestamp, risk_floor, recommended_action, raw payment value, raw finding value, vendor-domain prose, phone number, email address, file path, or client-facing explanation.
19. Wrapper performs no network/subprocess call and imports no phone/email/CRM/reputation client dependency.
20. Wrapper does not change Two-Channel Confirmation enum/schema/append-only/lift-only behavior, scoring overlay, or client-facing rubric.

---

## §7 Audit requirements

This contract draft and any implementation must be gated through `complete_gate.py`. The implementation manifest must include this contract, the Agent Design Contract Template, the signed Two-Channel Confirmation Enforcement spec, the workflow file, the wrapper file, and the focused test file.

---

## §10 Open Questions (operator-only)

No design fork is open in this draft. §11 signature confirms D1-D10 and authorizes the Evidence Stage 1 synthetic `VerificationOutcomeAgent` wrapper build + focused tests only.

---

## §11 Lockdown Signature

UNSIGNED — awaiting operator. Signing locks D1-D10 and authorizes the Evidence Stage 1 (Synthetic) `VerificationOutcomeAgent` wrapper build + focused tests only; no workflow write-path change, no new outcome enum, no default-registry registration, no production dispatch, no real-customer-data handling, no Evidence Stage 2/3 promotion, no scoring/rubric change, no contact execution, no payment decision, no risk-floor lowering, no autonomous action.

> _Operator signature pending: _____________________________
