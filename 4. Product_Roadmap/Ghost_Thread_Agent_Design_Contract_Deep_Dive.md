# Ghost Thread Agent Design Contract - Spec-First Deep Dive

**Status:** §11 SIGNED 2026-06-07 by Matt Nichol ("Matt Nichol June 7th 2026", placed verbatim at §11). Authored 2026-06-07 by Cursor on Matt Nichol's instruction, correcting the supplied #8 Ghost Thread / Reply-To Mismatch draft against the actual runtime code before signature. Signing promotes the implemented Ghost Thread wrapper from `DETECTOR_FUNCTION` to `GOVERNED_AGENT` at **Evidence Stage 1 (Synthetic)** and locks D1-D9 + the §4 Evidence Stage declaration. Signing authorizes **no** detector-logic change, **no** default-registry registration, **no** production dispatch, **no** scoring/rubric change, **no** buyer-facing claim, and **no** autonomous action. Evidence Stage 2/3 promotion is a separate, later, Matt-signed event per template §6.2. §11 signature is operator-only.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey**. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (the governing template; §3 contract block, §6 Evidence Stage / Promotion / Demotion model, §7.0 detector-immutability boundary)
- `4. Product_Roadmap/Header_Analysis_Agent_Design_Contract_Deep_Dive.md` (closest signed peer; #6 owns From / Reply-To / Return-Path / Sender divergence)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (this runtime proof is recorded on #8 Reply-To Mismatch / Ghost Thread; see §10 Q1 for the naming overlap)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/ghost_thread_detector.py` (the immutable underlying detector function - `score_ghost_thread`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/ghost_thread_agent.py` (the governed-agent wrapper - `GhostThreadAgent`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_ghost_thread_agent.py` (the known-input tests that satisfy the L2 runtime proof bar)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent` protocol, `AgentContribution`, `DecisionEvidenceRecord`)
- `VISION.md` (Stage A = analyze + recommend only; the seven non-negotiables)

---

## Agent Design Contract block

**Boundary:** This contract governs the Ghost Thread **agent wrapper** (`GhostThreadAgent`). It is additive governance, applied under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend the underlying detector logic (`score_ghost_thread`, including `_SCORE_GHOST_THREAD`, the threading-prefix rule, and the `In-Reply-To` / `References` absence rule), any existing scoring overlay, or any pipeline wiring. Those remain governed by their prior authorization and are immutable here.

| Field | Value |
|---|---|
| Agent name | Ghost Thread Agent (`GhostThreadAgent`) |
| Swarm inventory ID | #8 — Reply-To Mismatch / Ghost Thread (v1 map inventory/backlog reference only; naming overlap unresolved, see §10 Q1) |
| Canonical layer | 2 — Detection |
| Canonical team / case type | Email identity / sender analysis; fake conversation-continuity signal where a subject claims reply/forward context without real RFC 5322 threading headers |
| Authority level | Level 3 — Specialist Agent (matches #6 / #10 / #21) |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (see §6.0 of the template). |
| Evidence Stage (current) | **Stage 1 — Synthetic.** Validated on synthetic test data only; intentionally NOT registered in `build_default_registry` / production dispatch. Advancement to Stage 2 requires the template §6.2 conditions and a Matt-signed promotion record. |
| Role | Produce facts-only fake-thread-continuity evidence by running the deterministic ghost-thread detector and contributing the detected `ghost_thread_subject` indicator to the case Decision Evidence Record. |
| Boundary | The detector is not the decision. The agent must not decide fraud, approve/deny mail, block/quarantine, change payment behavior, mutate `EmailAnalysisRiskAnalysis`, or alter the signed Client-Facing 5-Axis Email Scoring Rubric. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no network/DNS/LLM call; no buyer-facing claim; no default-registry registration; no production dispatch at Evidence Stage 1; no emission of the numeric ghost-thread score as an interpretation field (facts-only at Layer 2). |
| Inputs | One `EMAIL_INBOUND` Blackboard record located via `MissionContext.source_record_id` (per-tenant path); reads `subject` and `headers` only, specifically whether the subject has a reply/forward prefix and whether `In-Reply-To` or `References` has a non-empty value. No body content is read into the contribution. |
| Outputs | One `AgentContribution` (layer 2): `observed_facts` = `("ghost_thread_subject",)` when the detector fires, otherwise empty. No verification/challenge/evidence/score field is emitted (layer-restricted by the schema validator). |
| Evidence emitted | The closed-set indicator name `ghost_thread_subject` when a subject claims threaded context (`Re:` / `Fw:` / `Fwd:` with supported variants) and no non-empty `In-Reply-To` / `References` header exists; nothing else. The numeric `score` from the underlying detector is intentionally NOT carried into the contribution. |
| Data minimization | No mailbox body content, no raw subject text, no raw header values, and no secret/value leakage in the contribution — only the closed-set indicator name. `inputs_digest` is a SHA-256 of the email payload, not the payload itself. |
| Tenant isolation | Reads only the tenant's own Blackboard path (`blackboard_path(root, environment, tenant_id)`); tenant A's records never influence tenant B. Contribution writes are gated by the registry's `allowed_write_types` (`AGENT_CONTRIBUTION`). |
| Two-pass role | Pass 1 (detect) only. `challenge()` returns `None` — Pass 2 is a Verification / Challenge-layer concern. The contribution provides facts a future Layer 5 challenge agent can inspect. |
| Decision Evidence Record contribution | `observed_facts`: `ghost_thread_subject` when present; `interpretations`: none (Layer 2 emits no interpretation); `assumptions`: the `EMAIL_INBOUND` record subject and RFC 5322 threading headers are as received; `missing_evidence`: absent/empty threading headers are the condition being detected, but the agent does not verify mailbox history; `recommended_verification`: none emitted at this layer; `final_outcome_contribution`: fake-thread-continuity fact only — no disposition authored by this agent; `retest_or_learning_record`: every real-case miss or demotion trigger becomes a new permanent regression test per template §6.5. |
| Human review trigger | None authored by this agent; the Commander's conservative disposition rules and downstream layers own escalation. |
| Verification trigger | None authored by this agent (Layer 2); ghost-thread facts feed future Layer 3 Verification / Layer 5 Challenge agents. |
| Scoring / action posture | Facts-only contribution. The agent performs no scoring lift itself; the underlying detector's numeric score is not emitted by this wrapper and remains out of scope for this contract. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers (and the swarm spine tests) until a signed Stage 2 promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; rejected outright in Stage A by the router guard. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires: clean test suite (known-bad fires, known-good does not, edge case as documented), zero open test failures, Matt review of >= 3 real email samples confirming the `observed_facts` match a trained analyst, a `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. |
| Demotion conditions | Per template §6.3. Automatic: a previously-passing regression test fails, Drift Watch anomaly, evidence-chain integrity failure, or an out-of-layer field write. Matt-signed: auditor pattern flag, a real miss that would have misled a downstream Verification agent, or a signed Challenge agent contradicting this agent on >= 2 cases in any 30-day window. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent (append-only) regression test the agent must pass before (re-)promotion. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires the real-sample review in §6.2; Stage 3 requires Drift Watch active. |
| Failure modes | See §5. |
| Required tests | See §6 — `tests/test_ghost_thread_agent.py` (the L2 known-input runtime proof bar) plus the underlying detector's existing tests. |
| Audit requirements | Any implementation/revision remains subject to `complete_gate.py`; this contract draft must be gated as a spec artifact before signature or commit. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, and the canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At signing, this agent is at **Evidence Stage 1**. No build authorization is granted for Evidence Stage 2 or Stage 3 registration until the §6.2 promotion conditions are satisfied and a separate promotion record is signed. The underlying detector and its existing pipeline wiring are unchanged by this contract. |

---

## §0 Purpose

Promote the already-built, already-tested Ghost Thread agent wrapper from a runtime *proof* (`DETECTOR_FUNCTION` on the scoreboard) to a *governed agent* (`GOVERNED_AGENT`) by giving it a signed Agent Design Contract — the L2 promotion bar from the 70-agent scoreboard (signed contract + known-input tests + declared DER contribution). It is the second real detector wrapper to prove the `analyze()` -> `AgentContribution` -> Blackboard -> in-memory DER -> Layer 5 challenge-pass path, following Header Analysis.

This contract does not build anything new. The detector and its wrapper already exist and are tested; this records the governance that converts "proven" into "governed," at the honest evidence level (Stage 1 Synthetic, since only synthetic tests exist today).

This draft also corrects a naming hazard: the implemented Ghost Thread detector does **not** inspect Reply-To domain mismatch. It detects fake thread continuity: a reply/forward-looking subject without real `In-Reply-To` / `References` threading headers. From / Reply-To divergence is already governed by #6 Header Analysis.

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing the `GhostThreadAgent` wrapper as a Layer 2 Detection agent.
- The Evidence Stage 1 (Synthetic) declaration and the promotion/demotion path inherited from template §6.
- Recording that the existing known-input tests (`tests/test_ghost_thread_agent.py`) satisfy the current L2 runtime proof bar.
- Correcting the prior draft's detector description so the contract matches the actual code: subject threading prefix + missing `In-Reply-To` / `References`.

### Out of scope
- Any change to `score_ghost_thread` logic, score band, or its existing consumption by any scoring pipeline (immutable per template §7.0).
- Any claim that Ghost Thread detects From / Reply-To domain mismatch; that belongs to Header Analysis (#6).
- Registering the agent in `build_default_registry` or any production dispatch (Evidence Stage 1 forbids it).
- Any change to the Client-Facing 5-Axis Email Scoring Rubric or `recommended_risk_floor` behavior.
- Any autonomous action, buyer-facing claim, or Stage B/C autonomy.
- Promotion to Evidence Stage 2/3 (a later, separately-signed event).

---

## §2 Locked Design Decisions (confirmed and locked at §11, 2026-06-07)

- **D1 — Identity.** Ghost Thread is a Layer 2 Detection agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = ghost_thread_001`.
- **D2 — Detector immutability.** This contract changes no detector logic, score band, threshold, or pipeline wiring (template §7.0). It governs the wrapper only. Any change to `ghost_thread_detector.py` requires a separate operator-authorized spec/revision path before Cursor may touch it.
- **D3 — Facts-only contribution.** The agent emits only the closed-set fake-thread-continuity indicator `ghost_thread_subject` as an `observed_fact`. It emits no numeric score, no interpretation, no confidence value, and no verification/challenge/evidence field (schema-enforced by the `AgentContribution` layer validator).
- **D4 — Input surface.** The agent reads exactly one `EMAIL_INBOUND` record via `MissionContext.source_record_id` on the tenant's own Blackboard path. The wrapper loads the `EmailInboundPayload` and passes only `email.subject` and `email.headers` into `score_ghost_thread`. Within `headers`, the detector checks only whether `In-Reply-To` or `References` carries a non-empty value. It does **not** inspect `Reply-To`, compare From/Reply-To domains, read email body content, read attachments, call external resources, or read any record outside the tenant's scoped Blackboard path.
- **D5 — Persistence + rollout.** Contributions persist via the registry-gated `AGENT_CONTRIBUTION` route. The agent is NOT in `build_default_registry`; it is wired only by explicit callers until a signed Stage 2 promotion.
- **D6 — Stage A / lift-only / no autonomy.** No block/quarantine/deny/reject; no autonomous action; the agent authors no disposition and no recommended action. Stage A discipline holds.
- **D7 — Evidence Stage governance.** Evidence Stage 1 at signing; promotion and demotion follow template §6.2 / §6.3; progressive hardening §6.5 applies (every miss becomes a permanent regression test).
- **D8 — Data minimization + tenant isolation.** No body content, raw subject text, raw header values, or thread metadata are emitted in the contribution; tenant-scoped reads and registry-gated writes only.
- **D9 — Tests are the promotion-bar evidence.** `tests/test_ghost_thread_agent.py` provides the current known-bad-fires / known-good-does-not / persistence / guardrail coverage required for this Stage 1 runtime proof; it is the regression baseline for §6.5. Edge-case coverage for legitimate reply/forward-like chains with modified subjects, whitespace-only threading headers, or equivalent documented ghost-thread edge cases is required before Stage 2 promotion is authorized. This gap is known and accepted at Stage 1.

---

## §3 Data surface and output schema

- **Reads:** `EmailInboundPayload.subject` and `EmailInboundPayload.headers`. The underlying detector performs a case-insensitive lookup of `In-Reply-To` and `References` only. It does not inspect `Reply-To` or sender domains.
- **Underlying detector:** `score_ghost_thread(subject=..., headers=...)` returns `GhostThreadAssessment(score, indicators)`. Only `indicators` cross into the agent contribution; `score` does not.
- **Firing condition:** subject begins with a supported threading prefix (`Re:`, `Fw:`, `Fwd:`, with the detector's supported whitespace / bracketed-counter variants) and neither `In-Reply-To` nor `References` carries a non-empty value.
- **Emits:** `AgentContribution(agent_id="ghost_thread_001", layer=2, observed_facts=<indicators>)`. Indicators are currently either `("ghost_thread_subject",)` or empty. No ghost-thread fact -> empty `observed_facts` -> Commander disposition `clear` when all contributions are empty.

---

## §4 Evidence Stage declaration

- **Current Evidence Stage: 1 — Synthetic.** Only synthetic-fixture validation exists (`tests/test_ghost_thread_agent.py` and `tests/test_ghost_thread_detector.py`). The agent is not in production dispatch.
- **To reach Stage 2 (Supervised):** all template §6.2 Stage 1->2 conditions, including Matt's review of >= 3 real email samples and a signed `PROMOTION` entry. Stage 2 also requires resolving or explicitly deferring §10 Q1 and adding or identifying the edge-case test required by D9 / template §6.2.
- **To reach Stage 3 (Production):** template §6.2 Stage 2->3 conditions, including Drift Watch active. Reaching Stage 3 grants no autonomous action (template §6.0).
- **Demotion:** template §6.3 triggers apply.

---

## §5 Failure modes

- **Authority drift** — the agent (or a caller) treating the `ghost_thread_subject` fact as a decision. Mitigation: facts-only contribution; Commander owns disposition; no score emitted.
- **Score leakage** — emitting `_SCORE_GHOST_THREAD` / `GhostThreadAssessment.score` as an interpretation or risk field. Mitigation: D3 + the layer-restricted `AgentContribution` validator.
- **Reply-To conflation** — describing Ghost Thread as a From / Reply-To divergence detector. Mitigation: D4 + §3 code-accurate firing condition; Header Analysis (#6) owns Reply-To divergence.
- **Legitimate broken threading false positive** — a legitimate reply/forward-like subject arrives without `In-Reply-To` / `References` because of client/forwarding behavior. Mitigation: any real-case false positive becomes a §6.5 regression test; Layer 5 challenge / Layer 3 verification should inspect context before escalation.
- **Subject-prefix false negative** — attacker implies prior conversation without a supported `Re:` / `Fw:` / `Fwd:` prefix. Mitigation: body-language or conversation-continuity variants are separate future agents/contracts; do not expand this detector by implication.
- **Mailbox-history assumption gap** — the detector does not validate referenced `Message-ID`s against the recipient mailbox; it only sees the inbound record's subject and headers. Mitigation: record as missing evidence; future per-tenant mailbox-state validation requires its own spec.
- **Cross-tenant read** — reading another tenant's record. Mitigation: tenant-scoped Blackboard path + `source_record_id` type guard.
- **Stage creep** — registering in the default registry or dispatching in production while at Evidence Stage 1. Mitigation: D5 + the Evidence Stage 1 "not in production dispatch" rule.

---

## §6 Required tests

The current L2 runtime proof is satisfied by `tests/test_ghost_thread_agent.py`, which proves: the agent satisfies the `Agent` protocol; a known-bad email (`Re:` subject with no threading headers) produces the `ghost_thread_subject` fact and a `suspicious` disposition; a known-good threaded reply (`Re:` subject with `In-Reply-To`) produces empty facts and a `clear` disposition; the contribution persists to the Blackboard and round-trips; the Layer 5 challenge pass can review the real contribution; `challenge()` returns `None`; missing / unknown / wrong-type `source_record_id` is rejected; an unauthorized agent cannot write the contribution; `digest_email` is deterministic; and the persisted payload model round-trips.

`tests/test_ghost_thread_detector.py` remains the underlying detector's pure-function baseline for subject-prefix and threading-header behavior.

These tests are the append-only regression baseline for template §6.5. Before any Stage 2 promotion, the promotion packet must also identify the template-required edge case for this detector (for example, a supported subject-prefix variant, whitespace-only threading header, or legitimate forwarding edge case) and show it behaves exactly as documented.

---

## §7 Audit requirements

This contract must be gated through `complete_gate.py` as a spec artifact before signature or commit. No runtime registration, default-on, or production dispatch is authorized by signing — only the governance promotion to Evidence Stage 1.

Any audit packet must include the code-accuracy correction that Ghost Thread does **not** inspect Reply-To domain mismatch and that Reply-To divergence is already owned by Header Analysis (#6).

---

## §10 Open Questions (operator-only)

- **Q1 — Scoreboard naming overlap.** #8 is named "Reply-To Mismatch" in the SPARK inventory / scoreboard, but the implemented and tested wrapper is Ghost Thread only. The actual firing condition is subject threading prefix plus missing non-empty `In-Reply-To` / `References`; it does **not** require or inspect Reply-To mismatch. From / Reply-To divergence belongs to Header Analysis (#6). Before Stage 2, should #8 be renamed/split in the scoreboard, or should the Reply-To-mismatch half be retired as already covered by #6?
- **Q2 — Stage 2 registry posture.** When Ghost Thread is promoted to Evidence Stage 2, should it register in `build_default_registry` for supervised dispatch, or remain explicitly-wired until Stage 3? (Deferred to the Stage 2 promotion event.)
- **Q3 — Score as a future Verification input.** Should the numeric ghost-thread score ever surface (as an interpretation) through a Layer 3 Verification agent rather than this Layer 2 agent? (Deferred to the Verification-layer spec; not authored here.)
- **Q4 — Future indicator split.** Should `ghost_thread_subject` remain one composite fact, or should a future version split subject-prefix evidence from missing-threading-header evidence? Since the current detector fires only on their conjunction, one fact is acceptable for Stage 1; revisit only with real-case evidence or Stage 2 review.

---

## §11 Sign-off

SIGNED. This promotes swarm agent #8 Ghost Thread to `GOVERNED_AGENT` at **Evidence Stage 1 (Synthetic)** and locks D1-D9 + the §4 Evidence Stage declaration as the Ghost Thread Agent Design Contract. Signing authorizes **no** detector-logic change, **no** default-registry registration, **no** production dispatch, **no** scoring/rubric change, and **no** autonomous action. Promotion to Evidence Stage 2/3 is a separate, later, Matt-signed event per template §6.2.

> §11 SIGNATURE — Matt Nichol June 7th 2026
