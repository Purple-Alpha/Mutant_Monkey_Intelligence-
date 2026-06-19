# Case Timeline Agent Design Contract — Boundary / Unblock Deep Dive

**Status:** DRAFT (UNSIGNED) 2026-06-19. Authored after MMI project-direction scoring ranked **Draft #47 Case Timeline Agent Design Contract** highest (16/20) following #48 Verification Outcome Agent promotion to `GOVERNED_AGENT` (`6799978`) and #47 dependency re-triage (`80f128c`, CYCLE 27). Build Map CYCLE 25 found #47 Case Timeline needs a governed verification-outcome input before it can become a clean Evidence-layer timeline agent; #48 now supplies that governed input. This draft defines the Agent Design Contract only. It authorizes **no** code, **no** runtime wrapper, **no** scoreboard promotion, **no** `SIGNED_UNBUILT` flip, **no** `REACTION_TIMING_TEST_LOG.md` mutation, **no** evidence-package / audit-trail behavior change, **no** real-customer-data handling, **no** client-facing timing claim, and **no** build until Matt §11 signs and a separate Build Authorization is issued.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey** only where separately signed buyer-facing specs require it. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Build_Map_Deep_Dive.md` (LIVE build authority; CYCLE 25 TRIAGE annotated #47 `DEPENDS_ON:#48`)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (governing template; Evidence Stage model; Layer 4 promotion bar)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#47 Case Timeline; #48 Verification Outcome `GOVERNED_AGENT`)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `4. Product_Roadmap/Verification_Outcome_Agent_Design_Contract_Deep_Dive.md` (§11-signed #48; governed verification-outcome input; does not build #47)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/verification_outcome_agent.py` (built #48 wrapper; read-only reference for governed input shape)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`DecisionTimestamps`, `DecisionEvidenceRecord`, `AgentContribution`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/evidence_package/package_generator.py` (`audit_trail.json` as package source artifact only; no mutation)
- `REACTION_TIMING_TEST_LOG.md` (operator-maintained reaction-timing ledger; append-only discipline; not written by this agent at Stage 1)
- `AGENTS.md` (reaction-timing test documentation rule; Stage A discipline)
- `VISION.md` (Stage A = analyze / recommend / evidence only; seven non-negotiables)
- `decision_cycles_log.md` (CYCLE 25, CYCLE 27)

**Proposed future build path (not authorized here):** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/case_timeline_agent.py` (`CaseTimelineAgent` wrapper + focused tests). No file is authorized until §11 signature.

---

## Agent Design Contract block

**Boundary:** This contract governs a future Case Timeline **agent wrapper** that projects caller-supplied case timing anchors and governed verification-phase context into a bounded Layer 4 `AgentContribution`. It is additive governance under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend `DecisionTimestamps`, `DecisionEvidenceRecord`, the §11-signed Verification Outcome contract/build, the evidence-package generator, cyber-insurance package specs, `REACTION_TIMING_TEST_LOG.md`, or any workflow write path.

| Field | Value |
|---|---|
| Agent name | Case Timeline Agent (`CaseTimelineAgent`) |
| Swarm inventory ID | #47 — Case Timeline |
| Canonical layer | 4 — Evidence |
| Canonical team / case type | Evidence / audit; reaction-timing timeline projection for one in-memory case decision |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed. Validation is synthetic-only over caller-supplied `DecisionTimestamps` and optional governed verification-phase fact names. Intentionally NOT registered in `build_default_registry` / production dispatch. Advancement requires template §6.2 and Matt-signed promotion. |
| Role | Produce bounded case-timeline evidence by projecting which reaction-timing anchors are present, whether the anchor sequence is internally consistent, and whether a governed verification-outcome phase is represented for the case — without computing client-facing SLA claims or mutating timing ledgers. |
| Boundary | Read-only Evidence agent over caller-supplied timing anchors and caller-attested governed verification context. The wrapper must not append to `REACTION_TIMING_TEST_LOG.md`, mutate package `audit_trail.json`, write Blackboard workflow events, invoke `#48 VerificationOutcomeAgent`, call `summarize_confirmation_status`, lower risk, approve/deny payment, or emit performance guarantees. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no payment approval/denial; no client-facing timing/SLA claim; no "detected in X seconds" outreach copy; no `REACTION_TIMING_TEST_LOG.md` append; no package-generator / audit-trail / PDF / done-declaration mutation; no Grok/xAI call; no network/subprocess lookup; no workflow enum/schema change; no default-registry registration; no production dispatch at Evidence Stage 1; no real-customer-data handling; no Evidence Stage 2/3 promotion; no builder self-audit (`audit_record_id` remains Final Review only). |
| Inputs | One explicit case-timeline request supplied by a trusted caller: `tenant_id`, `case_id`, caller-owned `DecisionTimestamps`, optional `inputs_digest`, and optional caller-attested governed verification-phase fact names already present in the case DER (for example closed facts emitted by `#48 VerificationOutcomeAgent`). The wrapper does not read raw email bodies, attachments, payment details, operator labels, channel descriptions, or external systems. |
| Outputs | One `AgentContribution` (layer 4): `observed_facts` = closed case-timeline phase facts; optional bounded `control_mapping` (for example `case_timeline:stage_a_synthetic`); optional bounded Stage 1 `underwriter_note` stating internal synthetic timeline evidence only. No verification/challenge fields are emitted. |
| Evidence emitted | Closed fact names only: `case_timeline_detected_at_present`, `case_timeline_verification_requested_at_present`, `case_timeline_verification_outcome_at_present`, `case_timeline_closed_at_present`, `case_timeline_sequence_monotonic`, `case_timeline_sequence_invalid`, `case_timeline_verification_phase_missing`, `case_timeline_verification_phase_present`, `case_timeline_closure_missing`, optional bounded `case_timeline_verification_fact:<closed_fact_name>` when caller attests a governed #48 fact is in scope. Raw timestamps, millisecond durations, record IDs, operator names, email content, and client-facing narrative do not cross into the contribution at Stage 1. |
| Data minimization | The contribution emits presence/sequence/phase facts only. It does not emit ISO timestamps, elapsed milliseconds, human-segment durations, Blackboard record IDs, package JSON, audit-trail content, vendor/customer names, or reaction-timing test verdicts. |
| Tenant isolation | Stage 1 uses isolated synthetic tenant IDs supplied by the caller. The wrapper does not read another tenant's Blackboard path or mix tenant context across cases. |
| Relation to #48 Verification Outcome | `#48` is the governed Layer 3 verification-outcome projector over two-channel confirmation workflow state. `#47` does **not** re-run #48. At Stage 1 the caller attests which closed verification-outcome facts (if any) are already in the case DER; `#47` may emit `case_timeline_verification_phase_present` only when both (a) `verification_outcome_at` is present in caller-supplied `DecisionTimestamps` and (b) the caller attests at least one governed #48 closed fact name is in scope. |
| Two-pass role | Evidence assembly only. `challenge()` returns `None`; Challenge / Final Review layers decide sufficiency. |
| Decision Evidence Record contribution | `observed_facts`: closed timeline phase facts only; `interpretations`: none; `assumptions`: caller-supplied timestamps and attested verification facts reflect the same synthetic case; `missing_evidence`: wrapper does not prove operational production timing or real-mailbox latency; `recommended_verification`: none emitted directly; `final_outcome_contribution`: timeline phase projection only; `retest_or_learning_record`: every real-case miss / demotion trigger becomes a permanent regression test per template §6.5. |
| Human review trigger | Any move beyond synthetic in-memory timeline projection, any append to `REACTION_TIMING_TEST_LOG.md`, any package/audit-trail mutation, or any client-facing timing claim requires separate Matt-signed authorization. |
| Verification trigger | The agent does not initiate verification. It may reflect that a verification-outcome anchor exists only when caller inputs say so. |
| Scoring / action posture | Facts-only Layer 4 evidence. No scoring lift, no risk floor, no recommended action, no compliance/insurance claim, no performance guarantee. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers/tests until a later signed promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; Stage A router guard rejects autonomy. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires clean suite, zero open test failures, Matt review of >= 3 supervised timeline samples with expected phase facts, a `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. Any real-mailbox or production timing evidence requires separate real-data/depth authorization. |
| Demotion conditions | Per template §6.3. Automatic: regression failure, cross-tenant contamination, timestamp/duration/record-id leakage, sequence logic inversion, unauthorized workflow or ledger write, package/audit-trail mutation, invocation of #48 or two-channel workflow writes, client-facing timing claim, out-of-layer field write, or external call. Matt-signed: auditor pattern flag or signed Challenge contradiction pattern. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent regression test. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires supervised timeline samples with operator-reviewed expected phase facts. Stage 3 requires Drift Watch active and real-data controls signed/open. |
| Failure modes | See §5. |
| Required tests | See §6 — wrapper tests must prove anchor presence/sequence behavior, governed #48 phase gating, read-only purity, tenant isolation, persistence, no ledger/package/workflow writes, no default registry, no network/subprocess behavior, and no timestamp/duration/record leakage. |
| Audit requirements | This contract draft and any future implementation remain subject to `complete_gate.py`. Draft gate required before §11 signature; implementation gate required before build close. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `Verification_Outcome_Agent_Design_Contract_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, `REACTION_TIMING_TEST_LOG.md` (read-only discipline reference), and canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At §11 signature, this agent is at **Evidence Stage 1** only. No build authorization is granted for Evidence Stage 2/3 registration, default registry, production dispatch, real-customer-data handling, reaction-timing ledger writes, package/audit-trail mutation, client-facing timing claims, or autonomous action until promotion conditions in §6.2 are satisfied and a separate promotion record is signed. |

---

## §0 Purpose

Unblock swarm #47 Case Timeline by defining the Evidence-layer boundary that kept it from being a clean governed agent after CYCLE 25 triage. The scoreboard row cites partial infrastructure (`REACTION_TIMING_TEST_LOG.md`, `DecisionTimestamps`, package `audit_trail.json` references) but no per-agent contract or wrapper.

The safe Stage 1 agent is narrower than a reaction-timing test runner or evidence-package assembler. It does not append timing-test records, assemble cyber-insurance packages, or contact anyone. It projects caller-supplied case timing anchors — now composable with governed verification-outcome context from `#48` — into closed Layer 4 timeline facts for the DER.

This contract is the governance step only. It does not build runtime code until §11 signature / Build Authorization.

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing a future `CaseTimelineAgent` wrapper as a Layer 4 Evidence agent.
- Evidence Stage 1 (Synthetic) declaration at signature.
- Read-only use of caller-supplied `DecisionTimestamps` and caller-attested governed verification fact names.
- Facts-only Layer 4 contribution through the existing `AgentContribution` schema.
- Explicit non-goals: no workflow writes, no ledger append, no package mutation, no client-facing timing claims.
- Preservation of existing `DecisionTimestamps`, `#48 VerificationOutcomeAgent`, evidence-package, and reaction-timing ledger boundaries.

### Out of scope
- Any change to `DecisionTimestamps`, `DecisionEvidenceRecord`, `AgentContribution` layer rules, `REACTION_TIMING_TEST_LOG.md` schema, package generator gates, `audit_trail.json` schema, or `#48` runtime behavior.
- Appending reaction-timing test records or substituting for `REACTION_TIMING_TEST_LOG.md`.
- Calling `VerificationOutcomeAgent`, `summarize_confirmation_status`, `record_confirmation_request`, or `record_confirmation_outcome`.
- Emitting raw timestamps, elapsed milliseconds, record IDs, package contents, audit-trail JSON, or client-facing performance language.
- Registering the agent in `build_default_registry` or production dispatch.
- Real-customer-data handling or Evidence Stage 2/3 promotion.
- Any autonomous action, buyer-facing claim, payment decision, or Stage B/C autonomy.

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

- **D1 — Identity.** Case Timeline is a Layer 4 Evidence agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = case_timeline_001`.
- **D2 — Read-only timeline boundary.** The wrapper reads only caller-supplied `DecisionTimestamps` and caller-attested verification fact names. It must not read Blackboard workflow state directly, append timing-test records, or mutate package artifacts at Stage 1.
- **D3 — Source restriction.** All timing anchors and verification-phase context are caller-supplied for the explicit case request. The agent does not discover cases, infer timestamps from raw email, or re-run `#48`.
- **D4 — Immutability of sibling surfaces.** This contract changes no `DecisionTimestamps` schema, `#48` behavior, evidence-package behavior, cyber-insurance specs, or reaction-timing ledger append model. It governs the wrapper only.
- **D5 — Facts-only Layer 4 contribution.** The agent emits closed observed facts plus optional bounded `control_mapping` / Stage 1 `underwriter_note`. It emits no verification/challenge fields, no durations, no timestamps, and no narrative explanation.
- **D6 — #48 composition rule.** `case_timeline_verification_phase_present` requires both `verification_outcome_at` in caller timestamps and caller attestation of at least one governed #48 closed fact name. Missing either emits `case_timeline_verification_phase_missing` or absent verification anchor facts as defined in §3.
- **D7 — Sequence rule.** When all supplied anchors are non-null, they must be monotonic: `detected_at <= verification_requested_at <= verification_outcome_at <= closed_at`. Violations emit `case_timeline_sequence_invalid`; valid monotonic sequences emit `case_timeline_sequence_monotonic`.
- **D8 — Builder/auditor separation.** The timeline projector is not the package assembler and not the Final Review auditor. It must not set `audit_record_id` or call `audit_package()`.
- **D9 — No client-facing timing claims.** Stage 1 produces internal synthetic timeline evidence only. No SLA, performance guarantee, or "we respond in X" language.
- **D10 — Tests are the Stage 1 evidence.** The wrapper test suite must prove anchor presence, monotonic sequence handling, #48 phase gating, read-only purity, tenant isolation, persistence, default-registry exclusion, no network/subprocess behavior, and no timestamp/duration/record leakage before the build can close.

---

## §3 Data surface and output schema

- **Reads:** caller-supplied `tenant_id`, `case_id`, `DecisionTimestamps`, optional `inputs_digest`, optional tuple of attested governed verification fact names (closed vocabulary from `#48` only).
- **Does not read:** raw email, Blackboard bodies, package directories, `audit_trail.json` contents, external clocks beyond supplied datetimes, or workflow APIs.
- **Emits:** `AgentContribution(agent_id="case_timeline_001", layer=4, observed_facts=<closed timeline facts>, control_mapping="case_timeline:stage_a_synthetic", underwriter_note=<bounded Stage 1 note>)`.
- **Allowed fact vocabulary:** see Agent Design Contract block `Evidence emitted`.
- **Does not emit:** ISO-8601 strings, integer milliseconds, `time_to_*` metric names as contribution facts, Blackboard record IDs, package hashes except via separate Evidence Package agent, operator labels, email content, or forbidden client-facing timing claims.

---

## §4 Evidence Stage declaration

- **Current Evidence Stage at signature: 1 — Synthetic.** Only synthetic in-memory timeline validation will exist at initial build.
- **To reach Stage 2 (Supervised):** all template §6.2 Stage 1->2 conditions, including Matt review of >= 3 supervised timeline samples with expected phase facts and a signed `PROMOTION` entry. Real-mailbox timing requires separate real-data/depth authorization.
- **To reach Stage 3 (Production):** template §6.2 Stage 2->3 conditions, including Drift Watch active. Reaching Stage 3 grants no autonomous action and no client-facing timing claim authority.
- **Demotion:** template §6.3 triggers apply.

---

## §5 Failure modes

- **Ledger-write creep** — wrapper appends to `REACTION_TIMING_TEST_LOG.md` or treats itself as the reaction-timing test runner. Mitigation: D2 and explicit out-of-scope tests.
- **Package/audit-trail mutation** — wrapper edits `audit_trail.json` or package generator outputs. Mitigation: D2/D8 and purity tests.
- **#48 re-run creep** — wrapper invokes `VerificationOutcomeAgent` or `summarize_confirmation_status`. Mitigation: D3/D6 and import/call guards.
- **Timing overclaim** — wrapper emits milliseconds, SLA language, or client-facing performance claims. Mitigation: D5/D9 and leakage tests.
- **Sequence laundering** — invalid anchor order is silently accepted. Mitigation: D7 sequence tests.
- **Verification phase false positive** — `verification_outcome_at` present without attested governed #48 facts still marks verification phase present. Mitigation: D6 gating tests.
- **Tenant contamination** — one tenant's timeline request uses another tenant's attested facts. Mitigation: tenant-scoped caller inputs and isolation tests.
- **Builder/auditor collapse** — timeline agent sets `audit_record_id` or audits packages. Mitigation: D8 and DER validator inheritance.
- **Stage creep** — default registry or production dispatch while at Evidence Stage 1. Mitigation: D7 rollout tests.

---

## §6 Required tests

The implementation slice must add focused tests proving:

1. `CaseTimelineAgent` satisfies the shared `Agent` protocol.
2. Missing `detected_at` fails closed.
3. Only `detected_at` present emits `case_timeline_detected_at_present` and missing-anchor facts for later phases as applicable.
4. Full anchor set with monotonic ordering emits `case_timeline_sequence_monotonic` and the corresponding `*_present` facts.
5. Non-monotonic anchor ordering emits `case_timeline_sequence_invalid` and does not emit `case_timeline_sequence_monotonic`.
6. `verification_outcome_at` present without attested governed #48 fact names emits `case_timeline_verification_phase_missing` (or fails closed per implementation choice locked at build — default: emit missing-phase fact).
7. `verification_outcome_at` present with attested governed #48 closed fact emits `case_timeline_verification_phase_present` and optional bounded `case_timeline_verification_fact:<name>`.
8. Missing `closed_at` when other anchors exist emits `case_timeline_closure_missing` when closure is expected by caller scenario; otherwise remains absent without overclaim.
9. The wrapper never appends to `REACTION_TIMING_TEST_LOG.md` and never mutates package or audit-trail files.
10. The wrapper never calls `VerificationOutcomeAgent`, `summarize_confirmation_status`, or workflow write helpers.
11. Invalid `case_id` / missing tenant context fails closed.
12. Tenant isolation: the same anchor set under two tenant IDs does not cross-contaminate attested verification facts.
13. Contribution persistence writes through `submit_agent_contribution` and round-trips through `AgentContributionPayload`.
14. `challenge()` returns `None`.
15. Unauthorized registry writes are rejected.
16. `digest_request` / equivalent input digest is deterministic.
17. Agent is not in `build_default_registry()`.
18. Contribution emits no ISO timestamp strings, millisecond counts, record IDs, raw email content, payment data, client-facing timing claim, or forbidden-language package/insurance wording.
19. Wrapper performs no network/subprocess call and imports no external timing/CRM/reputation client dependency.
20. Wrapper does not set `audit_record_id`, call `audit_package()`, or mutate runtime detector/scoring modules.

---

## §7 Audit requirements

This contract draft must pass `complete_gate.py` before §11 signature. Any implementation must pass a fresh gate before build close. The manifest must include this contract, the Agent Design Contract Template, the §11-signed Verification Outcome contract, `agent_contract.py`, the proposed wrapper file, focused tests, and scoreboard `#47/#48` rows.

---

## §8 Explicit non-goals and remaining blockers

### Non-goals (Stage 1)
- Not a replacement for `REACTION_TIMING_TEST_LOG.md`.
- Not a cyber-insurance evidence-package generator or auditor.
- Not a workflow engine for two-channel confirmation.
- Not a client-facing performance dashboard.
- Not authorized to use real-mailbox or production tenant timing data.

### Remaining blockers after this draft (expected)
- **Matt §11 signature** on this contract (required before `SIGNED_UNBUILT` reconcile or build).
- **Grok draft gate clean 0/0** on this contract slice.
- **Separate Build Authorization** after §11 signature (this draft does not authorize implementation).
- **Scoreboard reconcile** from `NEEDS_SIGNED_CONTRACT` to `SIGNED_UNBUILT` only after §11 signature — not at draft time.

---

## §10 Open Questions (operator-only)

1. **Stage 1 closure semantics:** when `closed_at` is absent but other anchors exist, should the wrapper emit `case_timeline_closure_missing` always, or only when the caller sets an explicit `expect_closure=true` flag? Default draft posture: caller-owned expectation flag at Stage 1 build time.
2. **Attested #48 fact transport:** should caller pass fact names only, or fact names plus a digest of the `#48` contribution? Default draft posture: closed fact names only at Stage 1.
3. **Duration buckets:** should Stage 2 introduce bounded duration-bucket facts (for example `case_timeline_detection_to_verification_bucket:short`), or remain presence/sequence-only forever? Default draft posture: presence/sequence-only at Stage 1; duration buckets deferred to Stage 2+ with separate authorization.

No design fork is resolved until Matt selects in §11 signature or a recorded operator decision.

---

## §11 Sign-off

**UNSIGNED — OPERATOR_LOCK pending Matt Nichol §11 signature.**

Signing would lock D1-D10 and authorize only the Evidence Stage 1 (Synthetic) `CaseTimelineAgent` wrapper build + focused tests. Signing would authorize **no** reaction-timing ledger append, **no** package/audit-trail mutation, **no** default-registry registration, **no** production dispatch, **no** real-customer-data handling, **no** client-facing timing claim, **no** `#48` behavior change, and **no** autonomous action.

> Matt Nichol ____________________  Date __________
