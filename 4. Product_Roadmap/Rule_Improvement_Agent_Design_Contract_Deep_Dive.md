# Rule Improvement Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_67_RULE_IMPROVEMENT_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** §11 SIGNED 2026-06-24 by Matt Nichol (pre-build gate clean `mmi_67_contract_gate_20260624T185114Z` 0/0 · MMI-DEC-153). Evidence Stage 1 (Synthetic) agent wrapper authorized by signature. Signing locks D1–D9 and authorizes the `RuleImprovementAgent` wrapper build + focused tests **only**. It authorizes **no** Blueprint-of-Record population beyond feedstock completion, **no** default-registry registration, **no** production dispatch, **no** production mutation deploy, and **no** AUTH-5. Scoreboard `SIGNED_UNBUILT` reconciled in same signing action per MMI-DEC-154.

**Candidate:** #67 — Rule Improvement

**Owner:** Matt Nichol

**Track:** BREADTH / Governance (Layer 6 Learning / Governance scoreboard row)

**Lane:** Agent Design Contract (BOR feedstock rank 1 · MMI-DEC-151 unpark)

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** BLOCKED until separate operator build authorization (§11 signed; scoreboard `SIGNED_UNBUILT` per MMI-DEC-154)

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (Evidence Stage §6 canonical)
- `4. Product_Roadmap/Phase5_MutationEngine_Contract.md` (§11 SIGNED — sandbox + 3-shot + HumanSignOffGate; #67 extends orchestration, does not replace)
- `4. Product_Roadmap/Phase_1_4_Mutation_Engine_Specialization_Deep_Dive.md`
- `4. Product_Roadmap/Failure_Classification_Agent_Design_Contract_Deep_Dive.md` (#64 upstream classifier — §11 signed)
- `4. Product_Roadmap/Load_Fission_Contract.md` (LF-D1–D12 — anti-self-fission; #67 is rule tuning, not agent fission)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#67 Rule Improvement)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/mutation/engine.py` (wrap target — sandbox-only)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/mutation/sign_off_gate.py` (`MutationProposal` — operator sign-off surface)
- `VISION.md` (Stage A — analyze / recommend / evidence only)

**Proposed future build path (not authorized here):** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/sandbox/rule_improvement_agent.py` (name TBD at build). No file is authorized until §11 signature.

**Lineage:** Downstream consumers: `#64` Failure Classification (upstream miss/failure signal) · `#65` Correction Evidence (future §11 — correction packet for promotion review) · `#62` Regression Test (permanent hardening suite per §6.5).

---

## Agent Design Contract block

**Boundary:** #67 reads one **scoped improvement request** (failure classification and/or sandbox weakness signal) and **proposes** a sandbox-evaluated rule mutation candidate by calling the existing mutation engine. It **never** deploys to production, **never** invokes `DEPLOY_MUTATION`, **never** writes production policy/registry, and **never** auto-applies a candidate rule.

| Field | Value |
|---|---|
| Agent name | Rule Improvement Agent (`RuleImprovementAgent`) |
| Swarm inventory ID | #67 — Rule Improvement |
| Canonical layer | 6 — Learning / Governance |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed |
| Role | Translate a scoped detection miss/failure signal into a sandbox mutation cycle; emit a held **proposal packet** with candidate + evidence — never enact |
| Boundary | Signal-in, proposal-out. Sandbox engine calls only. No production deploy, no autonomous rule store write, no governance mutation |
| Inputs | One improvement request envelope per Section 5 |
| Outputs | Section 6 `RULE_IMPROVEMENT_PROPOSAL` envelope, `INPUT_INSUFFICIENT_CANNOT_PROPOSE`, or `NO_CANDIDATE_SANDBOX_RETIRED` |
| Explicit non-authorities | No production rule deploy; no `DEPLOY_MUTATION`; no default registry; no production dispatch; no cross-tenant pattern broadcast; no agent fission; no Safe-Stop override; no AUTH-5; no autonomous/background operation; no weakening a rule without explicit adversarial review of the proposal packet |

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-24 (draft placement · MMI-DEC-151 unpark):

| Placeholder | Resolved value | Repo evidence |
|---|---|---|
| Mutation engine path | `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/mutation/engine.py` (scoreboard shorthand: `core/mutation/engine.py` relative to Runtime_Implementation root) | Phase 5 §3.1; scoreboard #67 code evidence |
| Primary wrap entrypoint | `run_mutation_cycle(context: RouteContext, *, config: MutationEngineConfig \| None = None) -> MutationEngineResult` | `engine.py` module docstring: sandbox-only; never writes production |
| Optional Phase 5 orchestration read | `run_mutation_cycle_with_pipeline(...)` → per-candidate `MutationProposal \| None` routed to HumanSignOffGate surface — **read/propose only**; #67 must not perform sign-off | Phase 5 P5-D4; `propose_mutation_to_pipeline` docstring |
| Kind selection (advisory) | `select_mutation_kind(...)` pure function — wrapper may **log** suggested kind; engine remains authoritative inside `run_mutation_cycle` | Phase 1.4 §2.2 |
| Sandbox write boundary | Engine promoted items call `submit_policy_update(...)` → **sandbox blackboard only** (`Environment.SANDBOX`, `sandbox_tenant_id`). Production promotion requires Phase 5 HumanSignOffGate + operator `DEPLOY_MUTATION` — **outside #67** | `engine.py` `_load_sandbox_records`; `role_separation.py` OPERATOR gate |
| Upstream #64 handoff | `#64` `FAILURE_CLASSIFICATION` envelope (`failure_ref`, `category`, `severity`, `evidence_ref`, `rationale`) when `category` ∈ `{REGRESSION, FUNCTIONAL, UNCLASSIFIED}` and severity ≥ `MEDIUM` — maps to improvement-request `failure_signal_kind=recorded_failure` | `#64` §4 output schema |
| Alternate upstream (sandbox) | `WEAKNESS_REPORT` / `MUTANT_EVALUATION` blackboard records already consumed by engine — wrapper may pass `RouteContext` + preloaded sandbox tenant only | Phase 1.4 grouping in `run_mutation_cycle` |
| Downstream #65 (future) | `#65` Correction Evidence — **no §11 contract on disk**; scoreboard `GOVERNANCE_DOC_ONLY`. Promotion review packet schema **TBD at #65 contract** — #67 proposal must include `correction_evidence_slot` reserved empty until #65 signs | Scoreboard row #65; `4. Product_Roadmap/Research_Inputs/Cyber_Insurance_Internal_Correction_Evidence_Record_Set.md` (research input only) |
| Downstream regression | `#62` Regression Test Agent — failed proposals become permanent regression cases per §6.5 | `#62` §11 signed |
| Blast radius estimate | Reuse engine `MutationCandidate` confidence delta + `MutationKind` + `per_cycle_promotion_cap` — packet includes `estimated_detection_impact` enum `{bounded_low, bounded_medium, bounded_high, unknown}` derived from promotion cap + kind, not LLM guess | `MutationEngineConfig.per_cycle_promotion_cap`; BRC adjacency (#89) read-only at build |

**Open before build (PARK build if unresolved):**
1. `#65` Correction Evidence wire format — placeholder field only until #65 §11.
2. Pre-build gate on this contract after §11 sign (Grok/Gemini via `complete_gate.py`).

Repo-reconciliation placeholders: **resolved for draft review** except #65 slot. §11 signature still required before build authorization.

---

## §0 Purpose — Executive Summary

The Rule Improvement agent closes the loop between **"we missed something"** and **"here is a sandbox-proven candidate fix"** — without ever putting an unsigned change into production.

It observes a scoped failure or weakness signal, runs (or triggers) the existing sandbox mutation engine, and emits a **proposal packet**: candidate mutation + evidence chain + blast-radius estimate. Matt (or a separate §11-signed promotion act) decides whether a candidate graduates toward production via the Phase 5 HumanSignOffGate pipeline.

**The one invariant:** this agent **proposes** rule changes; it **never enacts** them in production. If any draft of this contract reads otherwise, that draft is wrong.

Fits the governance track alongside `#64` (labels failures), `#62` (regression hardening), and the Phase 5 Mutation Engine ensemble (3-shot → validate → sign-off → deploy).

This contract is governance + draft placement only. It does not build runtime code, sign §11, reconcile scoreboard lifecycle, or unlock AUTH-5.

---

## §1 Scope

### In scope
- Reading one improvement request envelope (Section 5).
- Invoking `run_mutation_cycle` (and optionally reading `run_mutation_cycle_with_pipeline` outcomes) inside **sandbox** `RouteContext` only.
- Emitting a `RULE_IMPROVEMENT_PROPOSAL` packet (Section 6) for each promoted sandbox candidate, or explicit no-candidate / insufficient-input outcomes.
- Tracing every proposal field to sandbox evidence ids (engine `MutationEngineResult.item_results` / `PolicyUpdatePayload.sandbox_evidence_ids`).
- Reserving `correction_evidence_slot` for future `#65` attachment.

### Out of scope
- Production detection rule deploy or registry mutation.
- Calling `DEPLOY_MUTATION` or bypassing HumanSignOffGate.
- Autonomous mutation kind invention outside closed `MutationKind` enum (Phase 5 P5-D7).
- Cross-tenant rule broadcast (Collective Immune System / federation mesh — separate contracts).
- Agent fission / Load Multiplier copy inflation (LF-D2).
- Replacing or rewriting `core/mutation/engine.py` core logic — **extend via wrapper only**.
- Live tenant mail processing at Evidence Stage 1.
- AUTH-5, default registry, production Commander dispatch.

---

## §2 Locked Design Decisions

| ID | Decision |
|---|---|
| D1 | Signal-in, proposal-out; one improvement request per invocation |
| D2 | Sandbox-only engine calls via `RouteContext` + `Environment.SANDBOX` tenant |
| D3 | Production deploy is **always** a separate operator act — never an agent output side effect |
| D4 | Every proposal carries typed evidence refs from engine results — no orphan claims |
| D5 | `#64` classifications are advisory input only — wrapper does not auto-route on classification |
| D6 | Insufficient signal → `INPUT_INSUFFICIENT_CANNOT_PROPOSE` with named gap |
| D7 | Engine retires all candidates → `NO_CANDIDATE_SANDBOX_RETIRED` with engine `retired_reason` preserved |
| D8 | Zero writes to production policy store, scoreboard, registry, governance files, or AUTH-5 surfaces |
| D9 | Failed/degraded proposals feed §6.5 permanent regression cases via `#62` consumer — not inline mutation |

---

## §3 Wrap Points — `core/mutation/engine.py` (reconciled)

The agent **calls** the existing engine; it does **not** replace it.

| Step | Engine surface | #67 use |
|---|---|---|
| 1 — Context | `RouteContext` with `blackboard_root` + sandbox tenant | Wrapper supplies caller-declared sandbox context only |
| 2 — Config | `MutationEngineConfig` (optional) | Wrapper may tighten `per_cycle_promotion_cap` default; must not disable sandbox guards |
| 3 — Cycle | `run_mutation_cycle(context, config=...)` → `MutationEngineResult` | Primary orchestration call |
| 4 — Items | `MutationEngineResult.item_results[]` → `MutationCandidate` + optional sandbox `policy_update` | Map promoted rows to proposal packet |
| 5 — Pipeline (optional read) | `run_mutation_cycle_with_pipeline(...)` → `MutationProposal \| None` | Attach pipeline stamp to packet when Phase 5 ensemble configured — **no sign-off** |
| 6 — Kind hint (optional) | `select_mutation_kind(...)` | Log-only advisory; engine selection wins |

**Hard rule:** #67 must not import or call production deploy helpers, `DEPLOY_MUTATION` role checks as executor, or mutate engine source. Grep/arch review at build time must confirm no production write path is introduced in the wrapper module.

---

## §4 Evidence Stage (canonical — `Agent_Design_Contract_Template` §6)

Evidence Stage is **validation maturity**, orthogonal to VISION Stage A/B/C autonomy.

| Stage | Name | #67 meaning |
|---|---|---|
| **1** | **Synthetic** *(default at §11)* | Synthetic / replayed sandbox corpus only; `RouteContext` sandbox tenant; no real tenant mail |
| **2** | **Supervised** *(future promotion)* | Real past failures, privacy-filtered (`#93`), sandbox-evaluated; Matt confirms ≥3 samples per template §6.2 |
| **3** | **Production** *(future promotion)* | Live failure **signal** may inform requests; evaluation remains sandbox-only; **never auto-apply** |

**Signing locks Evidence Stage 1 only.** Stage 2/3 require separate signed promotion records in `decision_cycles_log.md` per template §6.2.

---

## §5 Inputs — Improvement Request Envelope

Exactly one input per invocation:

```
RULE_IMPROVEMENT_REQUEST
request_id:           <uuid>
failure_signal_kind:  recorded_failure | sandbox_weakness | operator_manual
failure_ref:          <id/path — e.g. #64 failure_ref or weakness_report id>
classification_ref:   <optional #64 FAILURE_CLASSIFICATION id>
scope:                <closed enum: detection_rule | threshold | signal_heuristic>
tenant_scope:         sandbox_only | <tenant_id for ES2+ only — blocked at ES1>
evidence_refs:        [<traceable ids>]
notes:                <optional operator context — not authority>
```

**ES1 build:** `tenant_scope` must be `sandbox_only`. Real tenant ids are rejected at wrapper boundary.

If required fields missing → `INPUT_INSUFFICIENT_CANNOT_PROPOSE`.

---

## §6 Outputs — Proposal Packet

### §6.1 Primary success envelope

```
RULE_IMPROVEMENT_PROPOSAL
proposal_id:              <uuid>
request_ref:              <RULE_IMPROVEMENT_REQUEST.request_id>
mutation_kind:            <MutationKind from engine candidate>
baseline_agent_id:        <from MutationCandidate>
candidate_agent_id:       <from MutationCandidate>
baseline_confidence:      <float>
candidate_confidence:     <float>
sandbox_evidence_ids:     [<UUID> — from PolicyUpdatePayload when promoted>]
engine_retired_reason:    null | <string when not promoted>
estimated_detection_impact: bounded_low | bounded_medium | bounded_high | unknown
pipeline_result:          optional — Phase 5 PipelineResult summary when ensemble run
correction_evidence_slot: reserved — populate when #65 contract exists
blast_radius_note:        plain text — parameter keys only, no raw tenant content
rationale:                evidence-traced; no deploy recommendation language
```

### §6.2 Explicit non-success outcomes

- `INPUT_INSUFFICIENT_CANNOT_PROPOSE` — named missing fields.
- `NO_CANDIDATE_SANDBOX_RETIRED` — engine processed but no promoted candidate; includes dominant `retired_reason`.

### §6.3 Production promotion (explicitly NOT this agent)

Candidate → production requires **Phase 5** HumanSignOffGate + Matt operator `DEPLOY_MUTATION` + separate §11 promotion record. #67 output stops at proposal packet.

---

## §6.5 Progressive Hardening

Every proposal that **degrades** detection on the synthetic corpus, fails `#62` regression, or is shown adversarially manipulable becomes a **permanent regression case** in the rule-improvement suite (append-only).

- `#64` Failure Classification: when a proposal fails validation, classify *why* → feeds hardening taxonomy.
- `#62` Regression Test: consumes new baseline cases — generator never executes tests.
- `#65` Correction Evidence (**future**): any candidate forwarded for §11 promotion review must attach correction evidence proving target miss fixed without new blind spots — slot reserved in §6.1.

---

## §7 Hard Limits

| Limit | Rule |
|---|---|
| AUTH-5 | Blocked — no autonomous task selection or routing |
| Production rule store | No write path in this component |
| Safe-Stop | Matt-only halt — agent must honor external safe-stop signal (#94) when wired |
| Mode Controller | Consent / mesh paths do not apply — sandbox tenant only at ES1 |
| Guardrail 11 | No cross-tenant content in proposal packets — sandbox evidence ids only |
| Health Score | ELITE 85+ target at GATED (align with Phase 5 P5-D9 pattern) |
| Dispatcher | Scoreboard row #67; lifecycle tracked; not default registry at ES1 |

---

## §8 Relationship to Signed Surfaces

- **Phase 5 Mutation Engine** — #67 orchestrates sandbox cycle; Phase 5 owns 3-shot, ValidationGate, HumanSignOffGate, deploy.
- **#64 Failure Classification** — upstream failure labels; no auto-response.
- **#61–#63 test-support** — adversarial/regression consumers of proposals.
- **Governed Swarm Charter** — charter ≠ agent authorization; #67 build requires this §11 + separate build auth.
- **MMI-DEC-150** — depth-first execution may proceed in parallel; #67 does not unblock Lung/Mesh.

---

## §9 Pre-Build Gate Plan

When Matt chooses §11 path:
1. Grok/Gemini pre-build gate via `audit_tools/complete_gate.py` on this contract (0 blocking target).
2. Adversarial focus: can hostile `RULE_IMPROVEMENT_REQUEST` steer the wrapper to weaken a rule or skip sandbox?
3. Worker manifest must list governance boundary tests proving no `DEPLOY_MUTATION` path.

---

## §10 Open Questions (operator / gate)

| # | Question | Default |
|---|---|---|
| Q1 | `#65` wire format | PARK build until #65 §11 or explicit Matt waiver |
| Q2 | ES1 default tenant id | `sandbox_default` per `MutationEngineConfig` |
| Q3 | Pipeline integration in v1 wrapper | Optional read of `run_mutation_cycle_with_pipeline`; not required for ES1 GATED |

---

## §11 Signature Block

**§11 — Rule Improvement Agent Design Contract (Deep Dive)**

SIGNED. This signature locks D1–D9 and authorizes the Evidence Stage 1 (Synthetic) `RuleImprovementAgent` wrapper build + focused tests only; no Blueprint-of-Record population beyond feedstock completion, no default-registry registration, no production dispatch, no production mutation deploy, no AUTH-5. Matt also authorized `MMI_67_SCOREBOARD_SIGNED_UNBUILT_RECONCILE_ONLY` in this signing action.

- [x] I approve this contract as written.
- [x] I authorize pre-build gate review — completed clean 0/0 (MMI-DEC-153).
- [x] On clean gate, I §11-sign and authorize reconcile to SIGNED_UNBUILT.

Confirmed: #67 **proposes** sandbox rule mutations from scoped failure signals; it **never** deploys to production, **never** invokes `DEPLOY_MUTATION`, and **never** auto-applies candidates.

> Matt Nichol June 24th 2026

---

## BUILD CONDITIONS (post-§11)

§11 SIGNED. Authorizes Stage 1 `RuleImprovementAgent` wrapper build + focused tests only when operator separately names build.

At signing, this agent is at **Evidence Stage 1 — Synthetic**. No build authorization for Evidence Stage 2 or 3 until promotion conditions in `Agent_Design_Contract_Template_Deep_Dive.md` §6.2 are satisfied and a separate promotion record is signed.

---

Matt Nichol — Rule Improvement Agent Design Contract §11 signed (MMI-DEC-154).
