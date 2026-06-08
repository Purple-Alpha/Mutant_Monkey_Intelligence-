# Email Authentication Agent Design Contract - Spec-First Deep Dive

**Status:** §11 SIGNED 2026-06-07 by Matt Nichol ("Matt Nichol June 7th 2026", placed verbatim at §11). Authored 2026-06-07 by Cursor on Matt Nichol's instruction, written against the actual runtime code (`score_email_authentication` + `EmailAuthenticationAgent`) before signature. Signing promotes the implemented Email Authentication wrapper from `DETECTOR_FUNCTION` to `GOVERNED_AGENT` at **Evidence Stage 1 (Synthetic)** and locks D1-D9 + the §4 Evidence Stage declaration. Signing authorizes **no** detector-logic change, **no** default-registry registration, **no** production dispatch, **no** scoring/rubric change, **no** buyer-facing claim, and **no** autonomous action. Evidence Stage 2/3 promotion is a separate, later, Matt-signed event per template §6.2. §11 signature is operator-only. **§10 Q1 resolved at signing:** Email Authentication earns its own scoreboard row (separate detector file, attack surface, and `agent_id` - the Ghost Thread precedent); its prior placement under #6 was a pre-wrapper classification artifact, corrected in the post-signature scoreboard/tracker commit.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey**. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (the governing template; §3 contract block, §6 Evidence Stage / Promotion / Demotion model, §7.0 detector-immutability boundary)
- `4. Product_Roadmap/Header_Analysis_Agent_Design_Contract_Deep_Dive.md` (closest signed peer; #6 owns From / Reply-To / Return-Path / Sender domain divergence)
- `4. Product_Roadmap/Ghost_Thread_Agent_Design_Contract_Deep_Dive.md` (most recent signed peer; identical wrapper structure)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (this detector file is currently listed under #6 Header Analysis code evidence; SPARK-slot resolution is §10 Q1)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/email_authentication_detector.py` (the immutable underlying detector function - `score_email_authentication`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/email_authentication_agent.py` (the governed-agent wrapper - `EmailAuthenticationAgent`, committed `8e3df20`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_email_authentication_agent.py` (the known-input tests that satisfy the L2 runtime proof bar)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent` protocol, `AgentContribution`, `DecisionEvidenceRecord`)
- `VISION.md` (Stage A = analyze + recommend only; the seven non-negotiables)

---

## Agent Design Contract block

**Boundary:** This contract governs the Email Authentication **agent wrapper** (`EmailAuthenticationAgent`). It is additive governance, applied under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend the underlying detector logic (`score_email_authentication`, including the `Authentication-Results` parsing, the per-mechanism score constants, the combination bump, and the `_MAX_SCORE` cap), any existing scoring overlay, or any pipeline wiring. Those remain governed by their prior authorization and are immutable here.

| Field | Value |
|---|---|
| Agent name | Email Authentication Agent (`EmailAuthenticationAgent`) |
| Swarm inventory ID | TBD - the detector file is listed under #6 Header Analysis code evidence today; whether SPF/DKIM/DMARC is a sub-signal of #6 or earns its own SPARK slot is unresolved (see §10 Q1) |
| Canonical layer | 2 - Detection |
| Canonical team / case type | Email identity / sender analysis; gateway-authentication posture where upstream SPF / DKIM / DMARC results indicate failure or unknown posture |
| Authority level | Level 3 - Specialist Agent (matches #6 / #8 / #10 / #21) |
| Stage posture | VISION Stage A - analyze / recommend / evidence only. Distinct from Evidence Stage (see §6.0 of the template). |
| Evidence Stage (current) | **Stage 1 - Synthetic.** Validated on synthetic test data only; intentionally NOT registered in `build_default_registry` / production dispatch. Advancement to Stage 2 requires the template §6.2 conditions and a Matt-signed promotion record. |
| Role | Produce facts-only gateway-authentication evidence by running the deterministic email-authentication detector and contributing the detected SPF/DKIM/DMARC failure indicators to the case Decision Evidence Record. |
| Boundary | The detector is not the decision. The agent must not decide fraud, approve/deny mail, block/quarantine, change payment behavior, mutate `EmailAnalysisRiskAnalysis`, or alter the signed Client-Facing 5-Axis Email Scoring Rubric. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no network/DNS/crypto/LLM call; no buyer-facing claim; no default-registry registration; no production dispatch at Evidence Stage 1; no emission of the numeric authentication score as an interpretation field (facts-only at Layer 2). |
| Inputs | One `EMAIL_INBOUND` Blackboard record located via `MissionContext.source_record_id` (per-tenant path); the wrapper passes `sender` and `headers` into the detector. The detector reads the `Authentication-Results` header for SPF/DKIM/DMARC results, and uses `sender` only to derive `from_domain` (which is NOT emitted). No body content is read into the contribution. |
| Outputs | One `AgentContribution` (layer 2): `observed_facts` = the detector's failure indicators (a subset of a closed set) when any mechanism fails or shows unknown posture, otherwise empty. No verification/challenge/evidence/score field is emitted (layer-restricted by the schema validator). |
| Evidence emitted | Closed-set indicator names only: `spf_fail`, `spf_softfail`, `spf_permerror`, `spf_temperror`, `dkim_fail`, `dkim_none`, `dkim_permerror`, `dmarc_fail`, `dmarc_none`, `dmarc_permerror`, `dmarc_temperror`. The numeric `score`, `from_domain`, and per-mechanism `*_result` values from the underlying assessment are intentionally NOT carried into the contribution. |
| Data minimization | No mailbox body content, no raw `Authentication-Results` header value, no sender address, and no secret/value leakage in the contribution - only closed-set indicator names. `inputs_digest` is a SHA-256 of the email payload, not the payload itself. |
| Tenant isolation | Reads only the tenant's own Blackboard path (`blackboard_path(root, environment, tenant_id)`); tenant A's records never influence tenant B. Contribution writes are gated by the registry's `allowed_write_types` (`AGENT_CONTRIBUTION`). |
| Two-pass role | Pass 1 (detect) only. `challenge()` returns `None` - Pass 2 is a Verification / Challenge-layer concern. The contribution provides facts a future Layer 5 challenge agent can inspect alongside other agents' contributions. |
| Decision Evidence Record contribution | `observed_facts`: the SPF/DKIM/DMARC failure indicators when present; `interpretations`: none (Layer 2 emits no interpretation); `assumptions`: the upstream mail gateway already performed the SPF/DKIM/DMARC protocol checks and stamped `Authentication-Results` honestly; the `EMAIL_INBOUND` record headers are as received; `missing_evidence`: a missing or absent `Authentication-Results` header is unknown posture, not a pass - the agent does not perform its own DNS/crypto verification; `recommended_verification`: none emitted at this layer; `final_outcome_contribution`: authentication-failure fact only - no disposition authored by this agent; `retest_or_learning_record`: every real-case miss or demotion trigger becomes a new permanent regression test per template §6.5. |
| Human review trigger | None authored by this agent; the Commander's conservative disposition rules and downstream layers own escalation. |
| Verification trigger | None authored by this agent (Layer 2); authentication facts feed future Layer 3 Verification / Layer 5 Challenge agents. |
| Scoring / action posture | Facts-only contribution. The detector is lift-only (it can only raise risk on failure / unknown posture and never lowers risk on pass), but the wrapper performs no scoring lift itself and the underlying numeric score is not emitted; it remains out of scope for this contract. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers (and the swarm spine tests) until a signed Stage 2 promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; rejected outright in Stage A by the router guard. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires: clean test suite (known-bad fires, known-good does not, edge case as documented), zero open test failures, Matt review of >= 3 real email samples confirming the `observed_facts` match a trained analyst, a `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. |
| Demotion conditions | Per template §6.3. Automatic: a previously-passing regression test fails, Drift Watch anomaly, evidence-chain integrity failure, or an out-of-layer field write. Matt-signed: auditor pattern flag, a real miss that would have misled a downstream Verification agent, or a signed Challenge agent contradicting this agent on >= 2 cases in any 30-day window. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent (append-only) regression test the agent must pass before (re-)promotion. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires the real-sample review in §6.2; Stage 3 requires Drift Watch active. |
| Failure modes | See §5. |
| Required tests | See §6 - `tests/test_email_authentication_agent.py` (the L2 known-input runtime proof bar) plus the underlying detector's existing tests (`tests/test_email_authentication_detector.py`). |
| Audit requirements | Any implementation/revision remains subject to `complete_gate.py`; this contract draft must be gated as a spec artifact before signature or commit. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, and the canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At signing, this agent is at **Evidence Stage 1**. No build authorization is granted for Evidence Stage 2 or Stage 3 registration until the §6.2 promotion conditions are satisfied and a separate promotion record is signed. The underlying detector and its existing pipeline wiring are unchanged by this contract. |

---

## §0 Purpose

Promote the already-built, already-tested Email Authentication agent wrapper from a runtime *proof* (`DETECTOR_FUNCTION` on the scoreboard) to a *governed agent* (`GOVERNED_AGENT`) by giving it a signed Agent Design Contract - the L2 promotion bar from the 70-agent scoreboard (signed contract + known-input tests + declared DER contribution). It is the third real detector wrapper to prove the `analyze()` -> `AgentContribution` -> Blackboard -> in-memory DER -> Layer 5 challenge-pass path, following Header Analysis (#6) and Ghost Thread (#8).

This contract does not build anything new. The detector and its wrapper already exist and are tested (wrapper committed `8e3df20`); this records the governance that converts "proven" into "governed," at the honest evidence level (Stage 1 Synthetic, since only synthetic tests exist today).

This contract also names a scope boundary: the Email Authentication detector reads upstream gateway `Authentication-Results` (SPF/DKIM/DMARC). That is a **distinct** Layer 2 signal from #6 Header Analysis's From / Reply-To / Return-Path / Sender **domain divergence**. The two are independent attack surfaces. The detector file is presently listed under #6 on the scoreboard; whether SPF/DKIM/DMARC earns its own SPARK inventory slot or remains a sub-signal of #6 is the §10 Q1 operator decision.

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing the `EmailAuthenticationAgent` wrapper as a Layer 2 Detection agent.
- The Evidence Stage 1 (Synthetic) declaration and the promotion/demotion path inherited from template §6.
- Recording that the existing known-input tests (`tests/test_email_authentication_agent.py`) satisfy the current L2 runtime proof bar.
- Naming the scope boundary between this agent (gateway-authentication posture) and #6 Header Analysis (domain divergence).

### Out of scope
- Any change to `score_email_authentication` logic, score constants, the combination bump, the `_MAX_SCORE` cap, or its existing consumption by any scoring pipeline (immutable per template §7.0).
- Any claim that this agent performs its own DNS resolution, DKIM crypto verification, or SPF evaluation; it ingests the upstream gateway's stamped result only.
- Registering the agent in `build_default_registry` or any production dispatch (Evidence Stage 1 forbids it).
- Any change to the Client-Facing 5-Axis Email Scoring Rubric or `recommended_risk_floor` behavior.
- Any autonomous action, buyer-facing claim, or Stage B/C autonomy.
- Promotion to Evidence Stage 2/3 (a later, separately-signed event).

---

## §2 Locked Design Decisions (confirmed and locked at §11, 2026-06-07)

- **D1 - Identity.** Email Authentication is a Layer 2 Detection agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = email_authentication_001`.
- **D2 - Detector immutability.** This contract changes no detector logic, score constant, threshold, or pipeline wiring (template §7.0). It governs the wrapper only. Any change to `email_authentication_detector.py` requires a separate operator-authorized spec/revision path before Cursor may touch it.
- **D3 - Facts-only contribution.** The agent emits only closed-set SPF/DKIM/DMARC failure indicators as `observed_facts`. It emits no numeric score, no `from_domain`, no per-mechanism `*_result` string, no interpretation, no confidence value, and no verification/challenge/evidence field (schema-enforced by the `AgentContribution` layer validator).
- **D4 - Input surface.** The agent reads exactly one `EMAIL_INBOUND` record via `MissionContext.source_record_id` on the tenant's own Blackboard path. The wrapper loads the `EmailInboundPayload` and passes only `email.sender` and `email.headers` into `score_email_authentication`. Within `headers`, the detector reads only the `Authentication-Results` header (case-insensitive) for `spf` / `dkim` / `dmarc` results; `sender` is used only to derive `from_domain`, which is computed by the detector but NOT carried into the contribution. It does **not** read email body content, read attachments, perform DNS / crypto / network calls, or read any record outside the tenant's scoped Blackboard path.
- **D5 - Persistence + rollout.** Contributions persist via the registry-gated `AGENT_CONTRIBUTION` route. The agent is NOT in `build_default_registry`; it is wired only by explicit callers until a signed Stage 2 promotion.
- **D6 - Stage A / lift-only / no autonomy.** No block/quarantine/deny/reject; no autonomous action; the agent authors no disposition and no recommended action. The detector is lift-only (never lowers risk on a pass). Stage A discipline holds.
- **D7 - Evidence Stage governance.** Evidence Stage 1 at signing; promotion and demotion follow template §6.2 / §6.3; progressive hardening §6.5 applies (every miss becomes a permanent regression test).
- **D8 - Data minimization + tenant isolation.** No body content, raw header values, sender address, or per-mechanism result strings are emitted in the contribution; tenant-scoped reads and registry-gated writes only.
- **D9 - Tests are the promotion-bar evidence.** `tests/test_email_authentication_agent.py` provides the current known-bad-fires / known-good-does-not / persistence / guardrail coverage required for this Stage 1 runtime proof; it is the regression baseline for §6.5. Edge-case coverage beyond the all-fail / all-pass / missing-header cases - for example softfail-only, single-mechanism failure, the multi-failure combination bump, malformed or partial `Authentication-Results` strings, and the `bestguesspass` normalization path - is required before Stage 2 promotion is authorized. This gap is known and accepted at Stage 1.

---

## §3 Data surface and output schema

- **Reads:** `EmailInboundPayload.sender` and `EmailInboundPayload.headers`. The underlying detector performs a case-insensitive lookup of the `Authentication-Results` header and parses `spf` / `dkim` / `dmarc` results from it; `sender` is parsed only to derive `from_domain`.
- **Underlying detector:** `score_email_authentication(sender=..., headers=...)` returns `EmailAuthenticationAssessment(score, from_domain, spf_result, dkim_result, dmarc_result, indicators)`. Only `indicators` cross into the agent contribution; `score`, `from_domain`, and the `*_result` fields do not.
- **Firing condition (lift-only):** an indicator is emitted for each mechanism showing failure or unknown posture - SPF `fail` / `softfail` / `permerror` / `temperror`; DKIM `fail` / `none` / `permerror`; DMARC `fail` / `none` / `permerror` / `temperror`. A `pass` result, a missing `Authentication-Results` header, or an unparseable result emits nothing for that mechanism. An all-pass or header-absent email produces empty `observed_facts`.
- **Emits:** `AgentContribution(agent_id="email_authentication_001", layer=2, observed_facts=<indicators>)`. No authentication failure -> empty `observed_facts` -> Commander disposition `clear` when all contributions are empty.

---

## §4 Evidence Stage declaration

- **Current Evidence Stage: 1 - Synthetic.** Only synthetic-fixture validation exists (`tests/test_email_authentication_agent.py` and `tests/test_email_authentication_detector.py`). The agent is not in production dispatch.
- **To reach Stage 2 (Supervised):** all template §6.2 Stage 1->2 conditions, including Matt's review of >= 3 real email samples and a signed `PROMOTION` entry. Stage 2 also requires resolving or explicitly deferring §10 Q1 (the SPARK slot) and adding or identifying the edge-case tests named in D9.
- **To reach Stage 3 (Production):** template §6.2 Stage 2->3 conditions, including Drift Watch active. Reaching Stage 3 grants no autonomous action (template §6.0).
- **Demotion:** template §6.3 triggers apply.

---

## §5 Failure modes

- **Authority drift** - the agent (or a caller) treating an authentication-failure fact as a decision. Mitigation: facts-only contribution; Commander owns disposition; no score emitted.
- **Score leakage** - emitting `EmailAuthenticationAssessment.score` (or `from_domain` / `*_result`) as an interpretation or risk field. Mitigation: D3 + the layer-restricted `AgentContribution` validator.
- **"Pass means safe" fallacy** - treating an SPF/DKIM/DMARC pass as evidence the email is benign. The detector docstring is explicit: a phisher can pass authentication from a lookalike domain they control. Mitigation: the agent is lift-only and emits nothing on pass; it never authors a "clear / safe" assertion. Domain trust is #6 Header Analysis and #10 Lookalike Domain's concern, not this agent's.
- **Header-divergence conflation** - describing this agent as a From / Reply-To / Return-Path / Sender divergence detector. Mitigation: D4 + §3 code-accurate firing condition; Header Analysis (#6) owns domain divergence. This agent reads only `Authentication-Results`.
- **Gateway-trust assumption gap** - the detector trusts the upstream gateway's stamped `Authentication-Results` and performs no independent verification; a forged or spoofed `Authentication-Results` header from an untrusted relay would be ingested as-is. Mitigation: record as an assumption (DER `assumptions`); upstream-relay trust / received-chain integrity is a separate agent's concern (see #6 received-chain parsing and future provenance work).
- **Missing-header ambiguity** - an absent `Authentication-Results` header is unknown posture, not a pass; the detector emits nothing in that case (score 0), so absence is currently silent at this layer. Mitigation: documented here as known behavior; whether absent-posture should itself raise a low-confidence indicator is deferred (see §10 Q2).
- **Cross-tenant read** - reading another tenant's record. Mitigation: tenant-scoped Blackboard path + `source_record_id` type guard.
- **Stage creep** - registering in the default registry or dispatching in production while at Evidence Stage 1. Mitigation: D5 + the Evidence Stage 1 "not in production dispatch" rule.

---

## §6 Required tests

The current L2 runtime proof is satisfied by `tests/test_email_authentication_agent.py`, which proves: the agent satisfies the `Agent` protocol; a known-bad email (`Authentication-Results` with `spf=fail; dkim=fail; dmarc=fail`) produces the `("spf_fail", "dkim_fail", "dmarc_fail")` facts and a `suspicious` disposition; an all-pass email and a missing-header email each produce empty facts and a `clear` disposition (lift-only); the contribution persists to the Blackboard and round-trips; the Layer 5 challenge pass can review the real contribution; `challenge()` returns `None`; missing / unknown / wrong-type `source_record_id` is rejected; an unauthorized agent cannot write the contribution; `digest_email` is deterministic; and the persisted payload model round-trips.

`tests/test_email_authentication_detector.py` remains the underlying detector's pure-function baseline for the SPF/DKIM/DMARC parsing, per-mechanism scoring, combination bump, and `_MAX_SCORE` cap.

These tests are the append-only regression baseline for template §6.5. Before any Stage 2 promotion, the promotion packet must also add the edge-case coverage named in D9 (softfail-only, single-mechanism, combination bump as a contribution fact set, malformed/partial header, `bestguesspass` normalization) and show each behaves exactly as documented.

---

## §7 Audit requirements

This contract must be gated through `complete_gate.py` as a spec artifact before signature or commit. No runtime registration, default-on, or production dispatch is authorized by signing - only the governance promotion to Evidence Stage 1.

Any audit packet must include the scope-boundary statement: this agent reads only `Authentication-Results` (SPF/DKIM/DMARC gateway posture); From / Reply-To / Return-Path / Sender domain divergence is owned by Header Analysis (#6), and the agent never asserts an email is safe on a pass.

---

## §10 Open Questions (operator-only)

- **Q1 - SPARK inventory slot. RESOLVED at signing (2026-06-07).** Email Authentication earns its **own scoreboard row** - a separate detector file, a separate attack surface, and a separate `agent_id` (`email_authentication_001`), exactly the Ghost Thread precedent. Its prior placement under #6 Header Analysis code evidence was a pre-wrapper classification artifact, not a design decision, and is corrected in the post-signature scoreboard/tracker commit. SPF/DKIM/DMARC gateway posture is a distinct signal from #6's domain divergence.
- **Q2 - Absent-posture indicator.** A missing `Authentication-Results` header is unknown posture, not a pass, but currently emits nothing (score 0). Should a future detector version emit a low-confidence "authentication posture unknown" indicator? This is a detector-logic change (out of scope here, immutable per D2); deferred to a separate detector spec if real-case evidence justifies it.
- **Q3 - Score as a future Verification input.** Should the numeric authentication score ever surface (as an interpretation) through a Layer 3 Verification agent rather than this Layer 2 agent? Boundary: Layer 2 never emits the numeric score under any condition; any future use of the score as a Verification-layer input is authored in the Verification-layer spec only and requires no amendment to this contract. (Mirrors Ghost Thread §10.A Q3.)
- **Q4 - Indicator granularity.** The agent emits one indicator per failing mechanism (up to 11 closed-set names). Should any be merged or split before Stage 2? **Recommendation:** keep the current per-mechanism granularity - it matches the detector exactly and gives a Layer 5 challenge agent the most precise fact set; revisit only with real-case evidence.

---

## §11 Sign-off

SIGNED. This promotes the implemented Email Authentication wrapper to `GOVERNED_AGENT` at **Evidence Stage 1 (Synthetic)** and locks D1-D9 + the §4 Evidence Stage declaration as the Email Authentication Agent Design Contract. Signing authorizes **no** detector-logic change, **no** default-registry registration, **no** production dispatch, **no** scoring/rubric change, and **no** autonomous action. Promotion to Evidence Stage 2/3 is a separate, later, Matt-signed event per template §6.2. §10 Q1 is resolved at signing (Email Authentication earns its own scoreboard row); the scoreboard promotion and tracker updates follow in the post-signature commit.

> §11 SIGNATURE - Matt Nichol June 7th 2026
