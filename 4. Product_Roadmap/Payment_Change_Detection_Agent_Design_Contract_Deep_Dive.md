# Payment Change Detection Agent Design Contract — Boundary / Unblock Deep Dive

**Status:** §11 SIGNED 2026-06-08 by Matt Nichol (CYCLE 23 draft `edd44a6`; signature CYCLE 24). Authored by the LIVE Build Map (CYCLE 23, BREADTH) after triage found no remaining clean pure-detector wrap in row order. This is the named UNBLOCK action for swarm #14 Payment Change Detection. The existing `assess_financial_state_delta` detector (Financial State Ledger / Delta Tripwire) is useful and already §11-signed (2026-05-24 by Matt), but it mutates the per-tenant Vendor Baseline Store (`check_signal` -> `ingest_signal`) for payment-destination signal types and therefore required an explicit boundary contract before becoming a governed swarm agent. Signing locks D1-D10 and authorizes the Evidence Stage 1 (Synthetic) `PaymentChangeDetectionAgent` wrapper build + focused tests **only**. It authorizes **no detector-logic change**, **no Vendor Baseline Store change**, **no new signal type**, **no production dispatch**, **no default-registry registration**, **no real-customer-data handling**, **no Evidence Stage 2/3 promotion**, **no scoring/rubric change**, **no payment decision**, and **no autonomous action**.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey** only where separately signed buyer-facing specs require it. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Build_Map_Deep_Dive.md` (LIVE build authority; pure-wrap runway exhausted -> UNBLOCK highest-priority blocked Detection candidate backed by a §11-signed single detector)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (governing template; Evidence Stage model)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#14 Payment Change Detection; `NEEDS_SIGNED_CONTRACT`)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `4. Product_Roadmap/Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` (§11-signed detector contract; closed financial signal enum, check-before-ingest, risk floor 85, hash-only baseline, no raw financial-string persistence)
- `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md` (baseline primitive contract; hash-only per-tenant store, closed enum, kill switch, audit write)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/financial_state_ledger.py` (`assess_financial_state_delta`, `FinancialStateLedgerAssessment`, `DeltaTripwireFinding`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/production_state/vendor_baseline/store.py` (`check_signal`, `ingest_signal`, `SignalState`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent`, `AgentContribution`, `DecisionEvidenceRecord`)
- Precedent stateful boundary: `4. Product_Roadmap/PDF_Fingerprint_Agent_Design_Contract_Deep_Dive.md` (#31; §11 SIGNED 2026-06-08; same check-before-ingest Vendor Baseline Store mutation pattern)
- `VISION.md` (Stage A = analyze / recommend / evidence only; seven non-negotiables)

---

## Agent Design Contract block

**Boundary:** This contract governs the future Payment Change Detection **agent wrapper** around the existing signed `assess_financial_state_delta` detector. It is additive governance under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend the §11-signed Financial State Ledger / Delta Tripwire detector contract, the Vendor Baseline Store primitive, the closed financial-signal enum, check-before-ingest ordering, risk floor 85, kill-switch behavior, tenant isolation, data-minimization rules, or existing scoring overlay behavior.

| Field | Value |
|---|---|
| Agent name | Payment Change Detection Agent (`PaymentChangeDetectionAgent`) |
| Swarm inventory ID | #14 — Payment Change Detection |
| Canonical layer | 2 — Detection |
| Canonical team / case type | Vendor-payment / BEC; new or stale payment-destination signal (routing number, SWIFT/BIC, IBAN, account number, payment-portal URL) introduced by a known vendor email vs per-tenant vendor memory |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed. Validation is synthetic-only and uses isolated tenant baseline state. Intentionally NOT registered in `build_default_registry` / production dispatch. Advancement requires template §6.2 and Matt-signed promotion. |
| Role | Produce facts-only payment-destination delta evidence by running the existing Financial State Ledger detector against one inbound email's text/attachment-extracted text and comparing each unique payment-destination signal against that tenant/vendor's Vendor Baseline Store. |
| Boundary | This is a stateful Detection agent, not a pure detector wrap. The only authorized mutation is the existing signed detector's payment-signal baseline ingest for the same tenant/vendor/signal being assessed, in the existing check-before-ingest order. The agent must not create new signal types, write raw financial strings, bypass the kill switch, change TTL/salt/hash behavior, change risk floor 85, approve/deny payment, or treat a new/stale signal as fraud proof. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no declaration that a payment is fraudulent; no payment approval/denial/hold; no out-of-band verification execution; no network/HTTP/DNS/WHOIS/reputation lookup; no Vendor Baseline Store schema/enum/TTL/salt/hash change; no cross-tenant baseline; no raw financial-string persistence outside the existing hash-only store; no buyer-facing claim; no default-registry registration; no production dispatch at Evidence Stage 1; no Evidence Stage 2/3 promotion. |
| Inputs | One `EMAIL_INBOUND` Blackboard record located via `MissionContext.source_record_id`, plus caller-supplied `tenant_id`, `vendor_domain` (or strictly normalized sender-derived vendor domain), and aware `now`. Reads `EmailInboundPayload.body_plain` and `attachments[*].extracted_text` only, as the signed detector already does. No payment execution data, no raw attachment bytes. |
| Outputs | One `AgentContribution` (layer 2): `observed_facts` = closed payment-destination indicator names (`new_payment_destination_signal`, `expired_payment_destination_signal`) plus closed signal-type facts (`payment_signal_type:routing_number`, `:swift_bic_code`, `:iban`, `:account_number`, `:payment_portal_url`). No verification/challenge/evidence/score field is emitted. |
| Evidence emitted | Closed indicator names derived from `FinancialStateLedgerAssessment.findings[*].baseline_state`, plus optional non-sensitive bounded counts such as `payment_delta_finding_count:<n>` / `payment_signal_extracted_count:<n>` if the wrapper needs a stable DER fact. Raw financial strings, normalized values, redacted displays, signal hashes, source surface details, attachment filenames/indexes, risk floor 85, recommended action, explanation text, and recommended verification wording do not cross into the contribution at Stage 1. |
| Data minimization | The contribution emits no raw financial string, no normalized value, no redacted display, no signal hash, no attachment filename/index, no risk floor, no recommended action/verification wording, no vendor-domain prose, no raw email body, and no file path. The Vendor Baseline Store remains hash-only per its signed primitive; `inputs_digest` is a SHA-256 of the email/boundary input, not the input itself. |
| Tenant isolation | Reads and writes only through the tenant-scoped Vendor Baseline Store path for the `tenant_id` supplied by the case context. Stage 1 tests must use isolated synthetic tenant IDs and reset/contain baseline state. Tenant A's payment signals never affect tenant B. |
| Two-pass role | Pass 1 Detection only. `challenge()` returns `None`; Verification / Challenge layers decide whether payment-delta evidence changes the case posture. |
| Decision Evidence Record contribution | `observed_facts`: closed payment-destination indicator names/signal-type facts/counts only; `interpretations`: none; `assumptions`: financial signals were extracted by the signed detector and vendor identity was supplied/normalized by caller; `missing_evidence`: the agent does not verify the change out of band, prove fraud, confirm the legitimate account, or contact the vendor; `recommended_verification`: none emitted at Layer 2; `final_outcome_contribution`: payment-destination delta facts only; `retest_or_learning_record`: every real-case miss or demotion trigger becomes a permanent regression test per template §6.5. |
| Human review trigger | None authored by this agent. Downstream Command / Verification layers own review routing. |
| Verification trigger | None authored by this agent at Layer 2. A new/expired payment signal can feed future Verification/Challenge layers (and may pair with #11 Known-Good Contact or document-fingerprint evidence), but this agent does not itself initiate verification. |
| Scoring / action posture | Facts-only contribution. The wrapper does not emit `recommended_risk_floor` (85), `recommended_action` (`needs_review`), `requires_out_of_band_verification`, explanation, or verification wording. Existing scoring overlay behavior from the signed detector spec remains unchanged and out of scope. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers/tests until a later signed promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; Stage A router guard rejects autonomy. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires clean suite, zero open test failures, Matt review of >= 3 supervised payment-change samples with known tenant/vendor boundaries, a `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. Any real-customer sample use requires the separate real-data/depth authorization gate. |
| Demotion conditions | Per template §6.3. Automatic: regression failure, cross-tenant baseline contamination, raw financial-string leakage, kill-switch bypass, baseline write outside the signed financial signal enum, out-of-layer contribution field write, unexpected network/subprocess behavior, risk-floor mutation, or scoring/rubric mutation. Matt-signed: auditor pattern flag, real miss that misled downstream Verification, or signed Challenge contradiction pattern. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent regression test. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires supervised payment-change samples with operator-reviewed expected outcomes. Stage 3 requires Drift Watch active and real-data controls signed/open. |
| Failure modes | See §5. |
| Required tests | See §6 — wrapper tests must prove new and expired payment-destination signals fire, a known signal does not fire, check-before-ingest preservation, synthetic baseline isolation, kill-switch inheritance, persistence, guardrails, no default registry, no network/subprocess behavior, and no risk-floor/raw-financial-string/hash/redacted-display leakage. |
| Audit requirements | Any contract signature, implementation, or revision remains subject to `complete_gate.py`. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md`, `Vendor_Baseline_Store_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, and canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At §11 signature, this agent is at **Evidence Stage 1** only. No build authorization is granted for Evidence Stage 2/3 registration, default registry, production dispatch, real-customer-data handling, new baseline signal types, scoring/rubric changes, payment decisions, or detector/store behavior changes until promotion conditions in §6.2 are satisfied and a separate promotion/authorization record is signed. |

---

## §0 Purpose

Unblock swarm #14 Payment Change Detection by defining the state boundary that kept it from being a clean pure-detector wrap. Like #31 PDF Fingerprint, #14's detector (`assess_financial_state_delta`) legitimately uses per-tenant memory: it compares payment-destination signals against the Vendor Baseline Store and then ingests the observed signal so future observations become known. This is the exact check-before-ingest pattern already governed for #31.

The purpose of this contract is not to make that statefulness disappear. The purpose is to govern it: only the existing signed financial signal types, exactly one tenant/vendor scope, existing check-before-ingest ordering, hash-only storage, no raw financial-string leakage, no risk-floor emission, no payment decision, and no autonomous action.

This contract is the governance step. It does not build runtime code until §11 signature / Build Authorization.

This contract governs the **#14 agent only**. The shared Financial State Ledger surface also underlies #16 Bank Detail Drift and #20 Financial Exposure; those remain separate scoreboard rows and require their own boundary contracts (or an explicit merge decision) — they are out of scope here.

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing a future `PaymentChangeDetectionAgent` wrapper as a Layer 2 Detection agent.
- Evidence Stage 1 (Synthetic) declaration at signature.
- Explicit state boundary for the existing signed detector's Vendor Baseline Store read/write behavior over the closed financial signal enum.
- Facts-only contribution of closed payment-destination indicator names / signal-type facts / counts.
- Preservation of existing `assess_financial_state_delta` behavior and the §11-signed Financial State Ledger / Delta Tripwire contract.

### Out of scope
- Any change to `assess_financial_state_delta`, check-before-ingest ordering, `FinancialStateLedgerAssessment`, risk floor 85, action `needs_review`, signal extraction regexes, Vendor Baseline Store schema, signal enum, TTL, salt/hash derivation, kill-switch behavior, or audit behavior.
- Adding new baseline signal types.
- Emitting `recommended_risk_floor`, `recommended_action`, `requires_out_of_band_verification`, explanation text, verification wording, raw financial strings, normalized values, redacted display strings, signal hashes, attachment filenames/indexes, raw email body, or file paths through the agent contribution.
- Any payment approval, denial, hold, or out-of-band verification execution; any fraud declaration.
- Network/HTTP/DNS/WHOIS/reputation lookup; subprocess; attachment byte parsing.
- Registering the agent in `build_default_registry` or production dispatch.
- Real-customer-data handling or Evidence Stage 2/3 promotion.
- Any autonomous action, buyer-facing claim, or Stage B/C autonomy.
- #16 Bank Detail Drift and #20 Financial Exposure governance.

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

- **D1 — Identity.** Payment Change Detection is a Layer 2 Detection agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = payment_change_detection_001`.
- **D2 — Stateful boundary.** This is not a pure-detector wrapper. The only authorized state mutation is the existing signed detector's `vendor_baseline.ingest_signal(...)` call for the same tenant/vendor/signal being assessed, after `check_signal` runs first, restricted to the existing signed financial signal enum (`routing_number`, `swift_bic_code`, `iban`, `account_number`, `payment_portal_url`).
- **D3 — Detector/store immutability.** This contract changes no Financial State Ledger detector logic, Vendor Baseline Store behavior, enum, schema, normalization, TTL, salt/hash derivation, kill switch, audit behavior, risk floor 85, scoring/rubric behavior, or pipeline wiring. It governs the wrapper only.
- **D4 — Facts-only contribution.** The agent emits only closed payment-destination indicator names, closed signal-type facts, and bounded non-sensitive counts. It emits no score, risk floor, action, explanation, verification wording, raw financial string, normalized value, redacted display, signal hash, interpretation, verification field, challenge field, or evidence field.
- **D5 — Input surface.** The agent reads exactly one `EMAIL_INBOUND` record via `MissionContext.source_record_id`, uses `EmailInboundPayload.body_plain` and `attachments[*].extracted_text` (as the signed detector already does), and takes a caller-owned `vendor_domain`/aware `now`. No payment-execution data and no raw attachment bytes are read.
- **D6 — Persistence + rollout.** Contributions persist via the registry-gated `AGENT_CONTRIBUTION` route. The agent is NOT in `build_default_registry`; it is wired only by explicit callers until signed promotion.
- **D7 — Stage A / no autonomy.** No block/quarantine/deny/reject; no payment decision; no out-of-band verification execution; no fraud declaration; no autonomous action; the agent authors no disposition.
- **D8 — Evidence Stage governance.** Evidence Stage 1 at signing; promotion and demotion follow template §6.2 / §6.3; progressive hardening §6.5 applies.
- **D9 — No risk-floor / no action emission.** The wrapper never emits the detector's risk floor 85, `recommended_action`, or `requires_out_of_band_verification`. Those remain the signed detector's scoring-overlay concern, consumed by Command/Verification layers, not republished as agent facts.
- **D10 — Tests are the Stage 1 evidence.** The wrapper test suite must include new/known/expired states, check-before-ingest preservation, tenant isolation, kill-switch inheritance, persistence, default-registry exclusion, no network/subprocess behavior, and no risk-floor/raw-financial-string/hash/redacted-display leakage before the build can close.

---

## §3 Data surface and output schema

- **Reads:** one `EmailInboundPayload` from the tenant's Blackboard path; `body_plain` and `attachments[*].extracted_text`; caller-owned `vendor_domain`; aware `now`.
- **Underlying detector:** `assess_financial_state_delta(tenant_id, vendor_domain, email, now)` returns `FinancialStateLedgerAssessment`.
- **Emits:** `AgentContribution(agent_id="payment_change_detection_001", layer=2, observed_facts=<closed indicator/type/count facts>)`.
- **Allowed fact vocabulary:** `new_payment_destination_signal`, `expired_payment_destination_signal`, `payment_signal_type:routing_number`, `payment_signal_type:swift_bic_code`, `payment_signal_type:iban`, `payment_signal_type:account_number`, `payment_signal_type:payment_portal_url`, `payment_delta_finding_count:<n>`, `payment_signal_extracted_count:<n>`.
- **Does not emit:** `recommended_risk_floor`, `recommended_action`, `requires_out_of_band_verification`, `DeltaTripwireFinding.explanation`, `recommended_verification`, `redacted_display`, `signal_hash`, `attachment_filename`, `attachment_index`, `vendor_domain`, raw financial string, normalized value, file path, or email body.

---

## §4 Evidence Stage declaration

- **Current Evidence Stage at signature: 1 — Synthetic.** Only synthetic-fixture validation will exist at initial build. Synthetic tests may exercise isolated Vendor Baseline Store state, but no real tenant data.
- **To reach Stage 2 (Supervised):** all template §6.2 Stage 1->2 conditions, including Matt review of >= 3 supervised payment-change samples with expected outcomes and a signed `PROMOTION` entry. Real-customer samples require separate real-data/depth authorization.
- **To reach Stage 3 (Production):** template §6.2 Stage 2->3 conditions, including Drift Watch active. Reaching Stage 3 grants no autonomous action and no payment decision authority.
- **Demotion:** template §6.3 triggers apply.

---

## §5 Failure modes

- **Silent state mutation creep** — wrapper writes baseline state outside the signed detector path or outside the signed financial signal enum. Mitigation: D2/D3 and tests spying `check_signal`/`ingest_signal`.
- **Check/ingest inversion** — first observation is swallowed as known because ingest happens before check. Mitigation: D2 and explicit ordering test.
- **Raw financial leakage** — raw account/routing/IBAN strings, normalized values, redacted displays, or hashes enter the contribution. Mitigation: D4 / §3 allowed vocabulary.
- **Risk-floor / action republication** — wrapper emits risk floor 85, `needs_review`, or verification wording as agent facts. Mitigation: D4/D9; facts-only.
- **Fraud overclaim** — a new/stale payment signal is treated as proof of fraud or a confirmed redirect. Mitigation: Layer 2 facts-only boundary and no interpretation/action fields.
- **Payment-decision creep** — wrapper approves, denies, holds, or routes a payment. Mitigation: D7 explicit non-authority and no disposition field.
- **Tenant contamination** — one tenant/vendor baseline affects another. Mitigation: tenant-scoped baseline state and synthetic isolation tests.
- **Kill-switch bypass** — baseline APIs are bypassed or mocked around in production path. Mitigation: inherited Vendor Baseline Store entry points and kill-switch test.
- **Scope creep** — wrapper parses attachment bytes, calls network/subprocess, or fetches data. Mitigation: detector-only input surface D5 and no file/network/subprocess tests.
- **Stage creep** — default registry or production dispatch while at Evidence Stage 1. Mitigation: D6 test.

---

## §6 Required tests

The implementation slice must add focused tests proving:

1. `PaymentChangeDetectionAgent` satisfies the shared `Agent` protocol.
2. First-seen payment-destination signal (e.g. labelled routing number in `body_plain`) emits `new_payment_destination_signal` + the matching `payment_signal_type:*` fact and persists via `AgentContribution`.
3. Known signal emits no suspicious indicator on a second run for the same tenant/vendor/signal.
4. Expired signal emits `expired_payment_destination_signal`.
5. `check_signal` is called before `ingest_signal` for each unique signal.
6. Duplicate signals in one email are deduped for baseline calls.
7. Attachment-extracted-text path works (signal in `attachments[*].extracted_text`).
8. Email with no financial signal emits no payment-destination indicator and writes no baseline rows.
9. Missing `source_record_id`, unknown record, wrong record type, invalid `vendor_domain`, or naive `now` fail closed.
10. Tenant isolation: same signal under two tenant IDs does not share baseline state.
11. Kill-switch inheritance is preserved through Vendor Baseline Store entry points.
12. Contribution persistence writes through `submit_agent_contribution` and round-trips through `AgentContributionPayload`.
13. `challenge()` returns `None`.
14. Unauthorized registry writes are rejected.
15. `digest_email` / equivalent input digest is deterministic.
16. Agent is not in `build_default_registry()`.
17. Contribution emits no `recommended_risk_floor` (85), `recommended_action`, `requires_out_of_band_verification`, explanation, verification wording, raw financial string, normalized value, redacted display, signal hash, attachment filename/index, vendor domain, or file path.
18. Wrapper performs no network/subprocess call and parses no attachment bytes.
19. Wrapper does not change scoring overlay, risk floor, Vendor Baseline Store enum/schema/TTL/salt/hash behavior, or detector logic.

---

## §7 Audit requirements

This contract draft and any implementation must be gated through `complete_gate.py`. The implementation manifest must include this contract, the Agent Design Contract Template, the signed Financial State Ledger / Delta Tripwire spec, the Vendor Baseline Store spec, the detector file, the Vendor Baseline Store file, the wrapper file, and the focused test file.

---

## §10 Open Questions (operator-only)

No design fork is open in this draft. §11 signature confirms D1-D10 and authorizes the Evidence Stage 1 synthetic `PaymentChangeDetectionAgent` wrapper build + focused tests only.

---

## §11 Lockdown Signature

SIGNED. This signature locks D1-D10 and authorizes the Evidence Stage 1 (Synthetic) `PaymentChangeDetectionAgent` wrapper build + focused tests only; no detector-logic change, no Vendor Baseline Store change, no new signal type, no default-registry registration, no production dispatch, no real-customer-data handling, no Evidence Stage 2/3 promotion, no scoring/rubric change, no payment decision, no autonomous action.

> Matt Nichol June 8th 2026
