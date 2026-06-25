# Callback Verification Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_18_CALLBACK_VERIFICATION_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** §11 SIGNED 2026-06-25 by Matt Nichol (Gemini pre-build gate clean `mmi_18_contract_gate_20260625T175158Z.md` 0 blocking / 1 warning; MMI-DEC-192). Evidence Stage 1 (Synthetic) agent wrapper authorized by signature. Signing locks D1–D10 and authorizes the `CallbackVerificationAgent` wrapper build + focused tests **only**. It authorizes **no** TOAD detector change, **no** Two-Channel Confirmation workflow write-path change, **no** default-registry registration, **no** production dispatch, **no** autonomous action, and **no** AUTH-5. Scoreboard `SIGNED_UNBUILT` reconciled in this signing action (MMI-DEC-193).

**Candidate:** #18 — Callback Verification

**Owner:** Matt Nichol

**Track:** BREADTH / Vendor-payment verification (Layer 3 Verification scoreboard row)

**Lane:** Agent Design Contract (BOR feedstock rank 1 · MMI-DEC-190)

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** Built — `CallbackVerificationAgent` at `core/orchestrator/callback_verification_agent.py` (MMI-DEC-194); scoreboard `AWAITING_AUDIT`; completion gate pending

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md` (§11 signed Layer 2 detector — immutable; **not** invoked by #18)
- `4. Product_Roadmap/Two_Channel_Confirmation_Enforcement_Deep_Dive.md` (§11 signed workflow — read-only boundary for #18)
- `4. Product_Roadmap/Verification_Outcome_Agent_Design_Contract_Deep_Dive.md` (#48 sibling — generic two-channel projector; #18 is callback-scoped)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#18 row — detector/workflow split)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/callback_phishing_detector.py` (Layer 2 — out of scope for wrapper calls)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/workflows/two_channel_confirmation.py` (`summarize_confirmation_status` read surface only)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py`
- `VISION.md` (Stage A — analyze / recommend / evidence only)

**Proposed future build path (not authorized here):** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/callback_verification_agent.py` — **built MMI-DEC-194**

---

## Agent Design Contract block

**Boundary split (CYCLE 12):** Layer 2 TOAD detection (`callback_phishing_detector.py`) and Layer 3 Two-Channel Confirmation workflow writes are **outside** this agent. #18 is a read-only Layer 3 Verification wrapper that projects callback-phishing out-of-band verification posture from an existing two-channel workflow record — it never re-scans email bodies and never records pending/outcome events.

## Agent Design Contract

Agent name: Callback Verification Agent (`CallbackVerificationAgent`)
Swarm inventory ID: #18 — Callback Verification
Canonical layer: 3 — Verification
Canonical team / case type: Vendor-payment fraud — callback-phishing / TOAD out-of-band verification (known-good channel; never trust in-email numbers)
Authority level: Level 3 — Specialist Agent
Stage posture: VISION Stage A — analyze / recommend / evidence only
Evidence Stage (current): Stage 1 — Synthetic (at §11 signature, if signed)

Role: For one caller-supplied callback-verification request, read the current Two-Channel Confirmation state for `finding_id` and emit a bounded Layer 3 verification contribution scoped to callback-phishing OOB verification posture
Boundary: Read-only workflow summary-in, verification contribution-out. No TOAD detector calls, no email-body reads, no workflow writes, no contact execution, no payment decisions
Explicit non-authorities: No `detect_callback_phishing` or TOAD scoring; no `record_confirmation_request` / `record_confirmation_outcome`; no block/quarantine/approve payment; no in-email number validation; no phone/SMS/email outbound; no network/reputation lookup; no scoreboard/registry/governance writes; no AUTH-5; no autonomous operation

Inputs: One explicit request: `tenant_id`, `finding_id`, closed `verification_class=callback_phishing_oob` (or successor enum), optional `case_id` / `source_record_id`, Blackboard root/environment. Caller supplies finding identity — agent does not derive from raw email
Outputs: One `AgentContribution` (layer 3): closed callback-OOB verification facts + `verification_source` + `verification_outcome`. No challenge/evidence/control fields at Stage 1
Evidence emitted: Closed facts only, e.g. `callback_oob_verification_missing`, `callback_oob_verification_pending`, `callback_oob_verification_confirmed`, `callback_oob_verification_rejected`, `callback_oob_verification_unable_to_verify`, `callback_oob_verification_expired`, optional bounded `callback_verification_detector:<detector>`. No raw lure text, phone digits, or body snippets
Data minimization: No raw email body, attachment data, phone numbers, payment destinations, operator labels, channel descriptions, reason text, timestamps, risk floors, or recommended actions in the contribution
Tenant isolation: Reads only the tenant-scoped Blackboard path for the supplied `tenant_id`; tenant A state never verifies tenant B

Two-pass role: Pass 1 Verification only. `challenge()` returns `None`
Decision Evidence Record contribution: `observed_facts`: closed callback-OOB workflow facts; `interpretations`: none; `assumptions`: upstream Layer 2/scoring created the finding and any pending/outcome events per signed workflow; `missing_evidence`: agent does not perform the verification call; `recommended_verification`: none emitted; `final_outcome_contribution`: current OOB verification state projection only
Human review trigger: None authored by this agent (underlying workflow may surface human tasks)
Verification trigger: This agent is a verification contributor; it does not initiate OOB contact or create pending requests

Scoring / action posture: Facts-only + Layer 3 verification outcome. No risk-floor lift/lower, no rubric mutation, no `OUT_OF_BAND_VERIFICATION_WORDING` emission (rendering stays in signed TOAD pass-2 / digest surfaces)
Default rollout: Evidence Stage 1 — not in `build_default_registry`; explicit callers/tests only until signed promotion
Autonomous action: none

Promotion conditions: Per template §6.2 — §11 signed; wrapper tests green; pre-build + completion gates 0 blocking; >= 3 supervised callback-OOB samples with expected outcomes; operator promotion MMI-DEC
Demotion conditions: TOAD detector invocation, workflow write, cross-tenant leak, payment-approval overclaim, phone/body/raw-value leakage, or scoring/rubric mutation — per template §6.3
Retest evidence: Permanent regression for every demotion trigger per template §6.5
Calibration requirement: ES1 synthetic fixtures only; Stage 2 requires supervised callback-OOB samples and separate real-data authorization if applicable

Failure modes: Detector/workflow conflation; workflow-write creep; treating `confirmed` as payment authorization; TOAD re-scan; raw phone/body leakage; tenant contamination — see §5
Required tests: Wrapper protocol, missing/pending/confirmed/rejected/unable/expired mapping, read-only `summarize_confirmation_status`, no TOAD import/call, no workflow writes, tenant isolation, no registry default, no network/subprocess, no raw leakage — see §6
Audit requirements: Step 00 `scripts/validate_agent_contract_block.py` PASS; pre-build gate via `audit_tools/complete_gate.py`; completion gate on implementation slice
Signed-spec dependencies: `Agent_Design_Contract_Template_Deep_Dive.md`, `Callback_Phishing_TOAD_Detector_Deep_Dive.md`, `Two_Channel_Confirmation_Enforcement_Deep_Dive.md`, `VISION.md`, `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`
Build Authorization dependency: At §11 signature, Evidence Stage 1 only. No build until §11 + operator build authorization. Underlying TOAD detector and Two-Channel workflow behavior remain immutable. Distinct from #48 `VerificationOutcomeAgent` — #18 owns the callback-phishing OOB verification governed slot only

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-25 (draft placement · MMI-DEC-191):

| Placeholder | Resolved value | Repo evidence |
|---|---|---|
| Layer 2 detector surface | `core/scoring/callback_phishing_detector.py` — §11 TOAD spec; pass-2 scoring wiring not #18 | Scoreboard + CYCLE 12 pre-build review |
| Layer 3 workflow surface | `core/workflows/two_channel_confirmation.py` — append-only pending/outcome; read via `summarize_confirmation_status` | §11 Two-Channel spec; #48 read pattern |
| #48 relationship | `VerificationOutcomeAgent` GOVERNED_AGENT — generic two-channel projector | MMI-DEC-012; does not retire #18 SPARK slot |
| Sibling pattern | `Verification_Outcome_Agent_Design_Contract_Deep_Dive.md` read-only boundary | Proven Layer 3 wrap |
| Finding identity | Caller-supplied `finding_id`; wrapper never derives from email body | Same as #48 D3 |
| OOB wording constant | `OUT_OF_BAND_VERIFICATION_WORDING` in TOAD module — rendering only, not emitted by #18 contribution | TOAD spec D8 |

Repo-reconciliation placeholders: **resolved for draft review.** §11 unsigned; pre-build gate not run.

---

## §0 Purpose

Unblock swarm #18 Callback Verification by signing the **detector/workflow split** that blocked CYCLE 12. The scoreboard row names both `callback_phishing_detector.py` and `two_channel_confirmation.py`; a governed wrapper must not conflate Layer 2 TOAD detection with Layer 3 workflow audit writes.

#18 is the read-only Verification agent for callback-phishing out-of-band verification posture: it tells the swarm whether a known-good channel verification was recorded for a finding — not whether the email is malicious, and not whether payment may proceed.

This contract is governance + draft placement only. It does not build runtime code, sign §11, reconcile scoreboard lifecycle, or unlock AUTH-5.

---

## §1 Scope

### In scope
- Agent Design Contract block governing a future `CallbackVerificationAgent` wrapper (Layer 3 Verification).
- Evidence Stage 1 (Synthetic) at signature.
- Read-only use of `summarize_confirmation_status(...)` for one caller-supplied `finding_id` with `verification_class=callback_phishing_oob`.
- Callback-scoped closed fact vocabulary and Layer 3 `verification_outcome` mapping.
- Explicit prohibition on TOAD detector calls, email-body reads, workflow writes, and payment decisions.

### Out of scope
- Any change to `detect_callback_phishing`, TOAD categories, risk-floor lifts, or pass-2 scoring wiring.
- Any change to Two-Channel Confirmation workflow writes, enums, append-only model, or kill-switch behavior.
- Calling `record_confirmation_request`, `record_confirmation_outcome`, or `submit_two_channel_confirmation` from the wrapper.
- Replacing or merging #48 Verification Outcome — parallel governed slots.
- Registering in `build_default_registry` or production dispatch at ES1.
- Real-customer-data handling, Evidence Stage 2/3 promotion, or autonomous action.

---

## §2 Locked Design Decisions

| ID | Decision |
|---|---|
| D1 | **Identity.** Callback Verification is Layer 3 Verification, Authority Level 3 Specialist, VISION Stage A, ES1 Synthetic at signing. `agent_id = callback_verification_001`. |
| D2 | **TOAD immutability.** Wrapper must not import or call `detect_callback_phishing` or read inbound email bodies for detection. Layer 2 remains governed separately. |
| D3 | **Workflow read-only.** Only authorized workflow call: `summarize_confirmation_status(...)`. No write paths. |
| D4 | **Caller-supplied finding.** `finding_id` and `verification_class` come from explicit governed caller context — no discovery from raw email. |
| D5 | **Outcome semantics.** `confirmed` → `verification_outcome="confirmed"`; `rejected` → `contradicted`; missing/pending/unable/expired → `unable_to_verify`. None authorize payment or lower risk. |
| D6 | **Callback-scoped facts.** Fact prefix `callback_oob_verification_*` distinguishes #18 contributions from generic #48 facts while using the same underlying workflow record. |
| D7 | **Persistence + rollout.** Contributions via registry-gated `AGENT_CONTRIBUTION`; not in `build_default_registry` at ES1. |
| D8 | **Stage A / no autonomy.** No block/quarantine/payment decision; no autonomous action. |
| D9 | **No contact side effects.** No outbound email/SMS/phone, DNS, reputation, or CRM lookup. |
| D10 | **Tests are Stage 1 evidence.** Suite must prove D2–D9 before build close. |

---

## §5 Failure modes

| Failure | Expected behavior |
|---|---|
| TOAD re-scan | Wrapper must never call detector; fail closed in tests |
| Workflow-write creep | Any write to two_channel events is forbidden |
| Payment overclaim | `confirmed` is not payment approval |
| #48 conflation | Generic two-channel projection remains #48; #18 adds callback-scoped slot only |
| Raw leakage | Phone digits, body text, operator labels never in contribution |
| Cross-tenant read | Tenant-scoped Blackboard only |

---

## §6 Required tests (implementation slice — not run at draft)

1. `CallbackVerificationAgent` satisfies `Agent` protocol.
2. Missing record → `callback_oob_verification_missing` + `unable_to_verify`.
3. Pending → `callback_oob_verification_pending` + `unable_to_verify`.
4. Confirmed → `callback_oob_verification_confirmed` + `confirmed`.
5. Rejected → `callback_oob_verification_rejected` + `contradicted`.
6. Unable/expired → mapped closed facts + `unable_to_verify`.
7. Exactly one `summarize_confirmation_status` call per request.
8. Never calls workflow write helpers or TOAD detector.
9. Tenant isolation on shared `finding_id` across tenants.
10. Not in `build_default_registry()`; no network/subprocess; no raw leakage.

---

## §8 Pre-Build Gate Plan

1. Step 00: `python3 scripts/validate_agent_contract_block.py` on this contract (exit 0 required).
2. Pre-build gate via `audit_tools/complete_gate.py` (0 blocking target).
3. Adversarial focus: can wrapper invoke TOAD detector or workflow writes via import side effect?
4. Manifest must list contract + template + TOAD spec + Two-Channel spec — not implementation files.

Gate glob: `mmi_18_contract_gate_*.md`

---

## §11 Signature Block

**§11 — Callback Verification Agent Design Contract (Deep Dive)**

- [x] I approve this contract as written.
- [x] I authorize pre-build gate review when ready.
- [x] On clean gate, I §11-sign and authorize Stage 1 wrapper build + focused tests only.

Confirmed: #18 projects callback-phishing OOB verification state only; it never detects TOAD patterns and never records workflow outcomes.

> Matt Nichol June 25th 2026

---

## BUILD CONDITIONS (post-§11)

At signing, Evidence Stage 1 — Synthetic only. §11 authorizes wrapper build path only when operator separately authorizes build lane (MMI-DEC pattern). No change to TOAD detector or Two-Channel workflow modules implied.

---

*End of contract.*
