# Known-Good Contact Agent Design Contract - Boundary / Unblock Deep Dive

**Status:** DRAFT 2026-06-08. Authored by the LIVE Build Map during CYCLE 21 after BREADTH triage routed #7 Sender Identity to RECLASSIFY and selected swarm #11 Known-Good Contact as the next highest-priority boundary/unblock candidate. This draft authorizes **no code**, **no Vendor Baseline Store change**, **no new contact registry**, **no new signal type**, **no production dispatch**, **no default-registry registration**, **no real-customer-data handling**, **no Evidence Stage 2/3 promotion**, **no payment approval/denial**, and **no autonomous action**. §11 signature is operator-only.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey** only where separately signed buyer-facing specs require it. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Build_Map_Deep_Dive.md` (LIVE build authority; CYCLE 21 TRIAGE -> DRAFT_CONTRACT -> OPERATOR_LOCK)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (governing template; Evidence Stage model)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#11 Known-Good Contact; Layer 3 Verification)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md` (baseline primitive contract; hash-only per-tenant store, closed enum, kill switch, audit write)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/production_state/vendor_baseline/store.py` (`check_signal`, `ingest_signal`, `SignalState`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent`, `AgentContribution`, `DecisionEvidenceRecord`)
- `VISION.md` (Stage A = analyze / recommend / evidence only; seven non-negotiables)

---

## Agent Design Contract block

**Boundary:** This contract governs a future Known-Good Contact **agent wrapper** around the existing signed Vendor Baseline Store read/check primitive. It is additive governance under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend the Vendor Baseline Store primitive, closed enum, tenant isolation, salt/hash derivation, TTL, kill-switch behavior, audit behavior, or any detector that writes into the store.

| Field | Value |
|---|---|
| Agent name | Known-Good Contact Agent (`KnownGoodContactAgent`) |
| Swarm inventory ID | #11 - Known-Good Contact |
| Canonical layer | 3 - Verification |
| Canonical team / case type | Email identity / sender and vendor-payment verification; confirms whether a caller-supplied vendor signal is already known for the tenant/vendor boundary |
| Authority level | Level 3 - Specialist Agent |
| Stage posture | VISION Stage A - analyze / recommend / evidence only. Distinct from Evidence Stage (template §6.0). |
| Evidence Stage (current) | **Stage 1 - Synthetic** at §11 signature, if signed. Validation is synthetic-only and uses isolated tenant baseline state. Intentionally NOT registered in `build_default_registry` / production dispatch. Advancement requires template §6.2 and Matt-signed promotion. |
| Role | Produce bounded verification evidence by checking whether a caller-supplied vendor signal is already known in the tenant-scoped Vendor Baseline Store. |
| Boundary | This is a read-only Verification agent, not a detector and not a learning path. The wrapper may call `vendor_baseline.check_signal(...)` only. It must not call `ingest_signal`, create a contact registry, add a signal type, write raw contact data, bypass the kill switch, change TTL/salt/hash behavior, or treat a known baseline hit as proof that a payment/contact request is legitimate. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no payment approval/denial; no declaration that a sender/contact is legitimate; no out-of-band contacting; no email sending; no phone/SMS/chat workflow; no network/HTTP/DNS/WHOIS/reputation lookup; no Vendor Baseline Store schema/enum/TTL/salt/hash change; no baseline ingest from the suspicious event; no cross-tenant baseline; no raw signal/contact persistence; no buyer-facing claim; no default-registry registration; no production dispatch at Evidence Stage 1; no Evidence Stage 2/3 promotion. |
| Inputs | One explicit verification request supplied by a trusted caller: `tenant_id`, `vendor_domain`, one closed-enum Vendor Baseline Store `signal_type`, one candidate `raw_value`, aware `now`, and optional `case_id` / `source_record_id` context. The wrapper does not read raw email bodies or attachments directly. |
| Outputs | One `AgentContribution` (layer 3): `observed_facts` = closed known-good verification facts; `verification_source` = bounded `vendor_baseline:<signal_type>` label; `verification_outcome` = `confirmed` when state is `known`, `unable_to_verify` when state is `new` or `expired`. No challenge/evidence/control fields are emitted. |
| Evidence emitted | Closed fact names only: `known_good_contact_signal_known`, `known_good_contact_signal_new`, `known_good_contact_signal_expired`, and optional bounded `known_good_contact_signal_type:<signal_type>`. Raw values, signal hashes, vendor-domain prose, contact names, email addresses, phone numbers, bank details, URLs, and store record timestamps do not cross into the contribution at Stage 1. |
| Data minimization | The contribution emits no raw signal value, no signal hash, no vendor-domain prose, no contact name, no email address, no phone number, no account/routing/IBAN/SWIFT/URL/PDF metadata value, no raw email body, no attachment metadata, and no file path. The Vendor Baseline Store remains hash-only per its signed primitive. |
| Tenant isolation | Reads only through the tenant-scoped Vendor Baseline Store path for the `tenant_id` supplied by the case context. Stage 1 tests must use isolated synthetic tenant IDs and reset/contain baseline state. Tenant A's known signal never verifies tenant B. |
| Two-pass role | Pass 1 Verification only. `challenge()` returns `None`; Challenge / Final Review layers decide whether the verification evidence is sufficient or contradicted. |
| Decision Evidence Record contribution | `observed_facts`: closed known-good verification facts only; `interpretations`: none; `assumptions`: the caller supplied the correct tenant/vendor boundary and a candidate signal extracted by a governed upstream detector/workflow; `missing_evidence`: the agent does not perform out-of-band contact, inspect inbox history, verify invoice legitimacy, or prove identity; `recommended_verification`: none emitted directly; `final_outcome_contribution`: baseline-known / not-known verification evidence only; `retest_or_learning_record`: every real-case miss or demotion trigger becomes a permanent regression test per template §6.5. |
| Human review trigger | None authored by this agent. Downstream Command / Verification workflows own review routing. |
| Verification trigger | The agent is itself a verification contributor. It does not initiate a second verification workflow. |
| Scoring / action posture | Facts-only + layer-3 verification outcome. The wrapper does not emit risk floors, recommended actions, payment decisions, explanation text, or client-facing rubric language. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers/tests until a later signed promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; Stage A router guard rejects autonomy. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires clean suite, zero open test failures, Matt review of >= 3 supervised verification samples with known tenant/vendor/source boundaries, a `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. Any real-customer sample use requires the separate real-data/depth authorization gate. |
| Demotion conditions | Per template §6.3. Automatic: regression failure, cross-tenant baseline contamination, raw signal/contact leakage, kill-switch bypass, baseline write from this wrapper, unsupported signal type, out-of-layer contribution field write, unexpected network/subprocess call, or scoring/rubric mutation. Matt-signed: auditor pattern flag, real miss that misled downstream Verification/Command, or signed Challenge contradiction pattern. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent regression test. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires supervised verification samples with operator-reviewed expected outcomes. Stage 3 requires Drift Watch active and real-data controls signed/open. |
| Failure modes | See §5. |
| Required tests | See §6 - wrapper tests must prove known/new/expired behavior, read-only `check_signal` usage, no `ingest_signal`, synthetic baseline isolation, kill-switch inheritance, persistence, guardrails, no default registry, no network/subprocess behavior, and no raw value/hash/contact leakage. |
| Audit requirements | Any contract signature, implementation, or revision remains subject to `complete_gate.py`. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `Vendor_Baseline_Store_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, and canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At §11 signature, this agent is at **Evidence Stage 1** only. No build authorization is granted for Evidence Stage 2/3 registration, default registry, production dispatch, real-customer-data handling, new baseline signal types, contact-registry creation, Vendor Baseline Store behavior changes, scoring/rubric changes, or autonomous action until promotion conditions in §6.2 are satisfied and a separate promotion/authorization record is signed. |

---

## §0 Purpose

Unblock swarm #11 Known-Good Contact by defining the source boundary that kept it from being a clean detector wrap. The scoreboard row points at the Vendor Baseline Store, but that store is stateful production memory, not a contact-verification agent and not a source of payment approval.

The purpose of this contract is to govern the narrow Stage 1 wrapper that can exist safely: a Layer 3 Verification agent that checks whether one caller-supplied, closed-enum vendor signal is already known for the tenant/vendor. It does not learn from the suspicious event, contact anyone, approve anything, or create a new contact database.

This contract is the governance step. It does not build runtime code until §11 signature / Build Authorization.

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing a future `KnownGoodContactAgent` wrapper as a Layer 3 Verification agent.
- Evidence Stage 1 (Synthetic) declaration at signature.
- Read-only use of `vendor_baseline.check_signal(...)` for existing closed-enum signal types.
- Facts-only + verification-outcome contribution through the existing `AgentContribution` schema.
- Explicit prohibition on learning/ingest from suspicious-event data.
- Preservation of existing Vendor Baseline Store behavior and signed primitive boundaries.

### Out of scope
- Any change to `check_signal`, `ingest_signal`, `expire_stale_signals`, baseline normalization, closed enum, schema, TTL, salt/hash derivation, tenant isolation, kill switch, or audit behavior.
- Adding a contact registry, phone/email directory, CRM integration, mailbox history, or out-of-band communication workflow.
- Adding new baseline signal types or implementing the unsigned Vendor Baseline Signal Type Enum Revision draft.
- Calling `ingest_signal` from the wrapper or updating baseline state based on the suspicious event being verified.
- Emitting raw values, signal hashes, contact names, email addresses, phone numbers, bank details, URLs, PDF metadata, vendor-domain prose, raw email body, attachment metadata, or file paths through the agent contribution.
- Registering the agent in `build_default_registry` or production dispatch.
- Real-customer-data handling or Evidence Stage 2/3 promotion.
- Any autonomous action, buyer-facing claim, payment approval/denial, or Stage B/C autonomy.

---

## §2 Locked Design Decisions (candidate - confirmed at §11)

- **D1 - Identity.** Known-Good Contact is a Layer 3 Verification agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = known_good_contact_001`.
- **D2 - Read-only verification boundary.** The only authorized Vendor Baseline Store call from the wrapper is `check_signal`. The wrapper must not call `ingest_signal`, `expire_stale_signals`, private store helpers, or any write path.
- **D3 - Source restriction.** The candidate signal must be supplied by an explicit governed caller/workflow. The agent does not extract from raw email and does not treat suspicious-event data as a new source of truth.
- **D4 - Store immutability.** This contract changes no Vendor Baseline Store behavior, enum, schema, normalization, TTL, salt/hash derivation, kill switch, audit behavior, scoring/rubric behavior, or pipeline wiring. It governs the wrapper only.
- **D5 - Facts-only verification contribution.** The agent emits closed observed facts plus `verification_source` and `verification_outcome` allowed for Layer 3. It emits no score, action, explanation, client-facing wording, raw signal, signal hash, contact detail, challenge field, or evidence field.
- **D6 - Outcome semantics.** `known` maps to `verification_outcome="confirmed"`. `new` and `expired` map to `verification_outcome="unable_to_verify"`; they are not proof of fraud and not a contradicted verification by themselves.
- **D7 - Persistence + rollout.** Contributions persist via the registry-gated `AGENT_CONTRIBUTION` route. The agent is NOT in `build_default_registry`; it is wired only by explicit callers until signed promotion.
- **D8 - Stage A / no autonomy.** No block/quarantine/deny/reject; no payment decision; no legitimacy declaration; no autonomous action; the agent authors no disposition.
- **D9 - No contact/channel side effects.** The wrapper never sends email, calls phones, opens chat/SMS, queries DNS/WHOIS/reputation, fetches CRM data, or performs network/subprocess calls.
- **D10 - Tests are the Stage 1 evidence.** The wrapper test suite must include known/new/expired state handling, read-only check behavior, no ingest, tenant isolation, kill-switch inheritance, persistence, default-registry exclusion, no network/subprocess behavior, and no raw value/hash/contact leakage before the build can close.

---

## §3 Data surface and output schema

- **Reads:** caller-supplied `tenant_id`, `vendor_domain`, `signal_type`, `raw_value`, aware `now`; optional `MissionContext.case_id` / `source_record_id` for persistence context.
- **Underlying primitive:** `vendor_baseline.check_signal(tenant_id, vendor_domain, signal_type, raw_value, now)` returns `SignalLookupResult`.
- **Emits:** `AgentContribution(agent_id="known_good_contact_001", layer=3, observed_facts=<closed known-good facts>, verification_source="vendor_baseline:<signal_type>", verification_outcome=<confirmed|unable_to_verify>)`.
- **Allowed fact vocabulary:** `known_good_contact_signal_known`, `known_good_contact_signal_new`, `known_good_contact_signal_expired`, `known_good_contact_signal_type:<signal_type>`.
- **Does not emit:** raw value, normalized value, signal hash, vendor-domain prose, first/last/expires timestamps, contact name, email address, phone number, account/routing/IBAN/SWIFT/URL/PDF metadata value, recommended action, risk floor, explanation text, client-facing rubric wording, file path, or email body.

---

## §4 Evidence Stage declaration

- **Current Evidence Stage at signature: 1 - Synthetic.** Only synthetic-fixture validation will exist at initial build. Synthetic tests may exercise isolated Vendor Baseline Store state, but no real tenant data.
- **To reach Stage 2 (Supervised):** all template §6.2 Stage 1->2 conditions, including Matt review of >= 3 supervised known-good verification samples with expected outcomes and a signed `PROMOTION` entry. Real-customer samples require separate real-data/depth authorization.
- **To reach Stage 3 (Production):** template §6.2 Stage 2->3 conditions, including Drift Watch active. Reaching Stage 3 grants no autonomous action.
- **Demotion:** template §6.3 triggers apply.

---

## §5 Failure modes

- **Suspicious-event learning loop** - wrapper writes a candidate signal into the baseline and then verifies it as known. Mitigation: D2/D3 and tests proving no `ingest_signal` call.
- **Known means trusted overclaim** - a known baseline hit is treated as payment approval or sender legitimacy proof. Mitigation: D6/D8 facts-only verification semantics.
- **Raw value leakage** - account/routing/IBAN/SWIFT/URL/PDF/contact data enters the contribution. Mitigation: D5 / §3 allowed vocabulary.
- **Contact-registry creep** - wrapper grows a new phone/email/CRM directory. Mitigation: §1 out-of-scope and no network/subprocess tests.
- **Tenant contamination** - one tenant/vendor baseline verifies another tenant's candidate. Mitigation: tenant-scoped baseline state and synthetic isolation tests.
- **Kill-switch bypass** - baseline APIs are bypassed or mocked around in production path. Mitigation: inherited Vendor Baseline Store entry points and kill-switch test.
- **Store/enum mutation** - wrapper changes the closed enum or store behavior to fit the agent label. Mitigation: D4 and store immutability tests.
- **Stage creep** - default registry or production dispatch while at Evidence Stage 1. Mitigation: D7 test.

---

## §6 Required tests

The implementation slice must add focused tests proving:

1. `KnownGoodContactAgent` satisfies the shared `Agent` protocol.
2. A known tenant/vendor/signal emits `known_good_contact_signal_known`, `verification_source="vendor_baseline:<signal_type>"`, and `verification_outcome="confirmed"`.
3. A new signal emits `known_good_contact_signal_new` and `verification_outcome="unable_to_verify"`.
4. An expired signal emits `known_good_contact_signal_expired` and `verification_outcome="unable_to_verify"`.
5. The wrapper calls `check_signal` exactly once per explicit verification request.
6. The wrapper never calls `ingest_signal`, `expire_stale_signals`, or private Vendor Baseline Store helpers.
7. Invalid signal type, invalid vendor domain, missing raw value, or naive `now` fail closed.
8. Tenant isolation: the same signal under two tenant IDs does not share verification state.
9. Kill-switch inheritance is preserved through the Vendor Baseline Store entry point.
10. Contribution persistence writes through `submit_agent_contribution` and round-trips through `AgentContributionPayload`.
11. `challenge()` returns `None`.
12. Unauthorized registry writes are rejected.
13. `digest_request` / equivalent input digest is deterministic.
14. Agent is not in `build_default_registry()`.
15. Contribution emits no raw value, normalized value, signal hash, vendor-domain prose, contact name, email address, phone number, payment detail, URL, PDF metadata, timestamp, file path, risk floor, recommended action, or explanation text.
16. Wrapper performs no network/subprocess call and imports no phone/email/CRM/reputation client dependency.
17. Wrapper does not change Vendor Baseline Store enum/schema/TTL/salt/hash behavior, detector logic, scoring overlay, or client-facing rubric.

---

## §7 Audit requirements

This contract draft and any implementation must be gated through `complete_gate.py`. The implementation manifest must include this contract, the Agent Design Contract Template, the Vendor Baseline Store spec, the Vendor Baseline Store file, the wrapper file, and the focused test file.

---

## §10 Open Questions (operator-only)

No design fork is open in this draft. §11 signature confirms D1-D10 and authorizes the Evidence Stage 1 synthetic `KnownGoodContactAgent` wrapper build + focused tests only.

---

## §11 Sign-off

PENDING. Operator-authored signature required before any runtime build. Signing will lock D1-D10 and authorize the Evidence Stage 1 (Synthetic) `KnownGoodContactAgent` wrapper build + focused tests only; no Vendor Baseline Store change, no new signal type, no contact registry, no baseline ingest from the suspicious event, no default-registry registration, no production dispatch, no real-customer-data handling, no Evidence Stage 2/3 promotion, no scoring/rubric change, no network/contact workflow, no autonomous action.

> [Matt Nichol - Known-Good Contact Agent - date]
