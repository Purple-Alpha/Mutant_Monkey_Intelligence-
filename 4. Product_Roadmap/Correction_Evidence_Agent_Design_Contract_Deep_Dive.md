# Correction Evidence Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_65_CORRECTION_EVIDENCE_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** §11 SIGNED 2026-06-24 by Matt Nichol (pre-build gate clean `mmi_65_contract_gate_20260624T221330Z` 0 blocking / 1 warning · MMI-DEC-161). Evidence Stage 1 (Synthetic) agent wrapper authorized by signature. Signing locks D1–D9 and authorizes the `CorrectionEvidenceAgent` wrapper build + focused tests **only**. It authorizes **no** Blueprint-of-Record population beyond feedstock completion, **no** default-registry registration, **no** production dispatch, **no** rule promotion/apply, and **no** AUTH-5. Scoreboard `SIGNED_UNBUILT` reconciled in same signing action per MMI-DEC-162.

**Candidate:** #65 — Correction Evidence

**Owner:** Matt Nichol

**Track:** BREADTH / Governance (Layer 6 Learning / Governance scoreboard row)

**Lane:** Agent Design Contract (BOR feedstock rank 1 · MMI-DEC-159)

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** AWAITING_AUDIT — Stage 1 wrapper built (MMI-DEC-163); completion gate pending; separate operator build authorization satisfied for implementation slice only

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (Evidence Stage §6 canonical)
- `4. Product_Roadmap/Failure_Classification_Agent_Design_Contract_Deep_Dive.md` (#64 upstream — §11 signed)
- `4. Product_Roadmap/Rule_Improvement_Agent_Design_Contract_Deep_Dive.md` (#67 upstream — §11 signed)
- `4. Product_Roadmap/Regression_Test_Agent_Design_Contract_Deep_Dive.md` (#62 corpus generator — §11 signed; generate-only)
- `4. Product_Roadmap/Phase5_MutationEngine_Contract.md` (HumanSignOffGate — promotion outside #65)
- `4. Product_Roadmap/Research_Inputs/Cyber_Insurance_Internal_Correction_Evidence_Record_Set.md` (research seed — not runtime authority)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#65 Correction Evidence)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/sandbox/loop.py` (`run_sandbox_cycle` — sandbox eval surface)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/sandbox/regression_test_agent.py` (regression-case shape — generate-only consumer)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/sandbox/rule_improvement_agent.py` (`RULE_IMPROVEMENT_PROPOSAL` + `correction_evidence_slot`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/sandbox/failure_classification_agent.py` (`FAILURE_CLASSIFICATION` envelope)
- `VISION.md` (Stage A — analyze / recommend / evidence only)

**Proposed future build path (not authorized here):** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/sandbox/correction_evidence_agent.py` (name TBD at build). No file is authorized until §11 signature.

**Lineage:** Team 9 governance chain — `#64` labels the failure · `#67` proposes the sandbox correction · `#65` validates evidence for §11 promotion review · `#62` supplies permanent regression cases when validation fails (§6.5).

---

## Agent Design Contract block

**Boundary:** #65 reads one **scoped correction validation request** (upstream `#64` classification + `#67` proposal + target failure ref) and **assembles/validates** a Correction Evidence Packet. It **never** promotes, applies, signs, or deploys a rule change. A `SUFFICIENT` verdict is **not** authorization — Matt §11 + Phase 5 HumanSignOffGate remain mandatory.

| Field | Value |
|---|---|
| Agent name | Correction Evidence Agent (`CorrectionEvidenceAgent`) |
| Swarm inventory ID | #65 — Correction Evidence |
| Canonical layer | 6 — Learning / Governance |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed |
| Role | Validate that a `#67` candidate fixes the `#64`-classified target failure without new blind spots; emit Correction Evidence Packet or `INSUFFICIENT` |
| Boundary | Evidence-in, evidence-verdict-out. Sandbox evaluation only. No promote / apply / sign |
| Inputs | One correction validation request envelope per Section 5 |
| Outputs | Section 6 `CORRECTION_EVIDENCE_PACKET` (`SUFFICIENT` / `INSUFFICIENT`), or `INPUT_INSUFFICIENT_CANNOT_VALIDATE` |
| Explicit non-authorities | No rule promotion; no `DEPLOY_MUTATION`; no production policy write; no §11 substitute; no auto-advance on `SUFFICIENT`; no scoreboard/registry/governance mutation; no AUTH-5; no autonomous/background operation |

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-24 (draft placement · MMI-DEC-160):

| Placeholder | Resolved value | Repo evidence |
|---|---|---|
| Upstream #64 handoff | `FAILURE_CLASSIFICATION` envelope: `id`, `failure_ref`, `category`, `severity`, `evidence_ref`, `rationale` — `#65` requires `failure_ref` match to validation request | `failure_classification_agent.py` `format_classification` / §4 schema |
| Upstream #67 handoff | `RULE_IMPROVEMENT_PROPOSAL` envelope: `proposal_id`, `request_ref`, `mutation_kind`, confidence deltas, `sandbox_evidence_ids`, `blast_radius_note`, `correction_evidence_slot` (was `reserved` — populated by #65 packet id when SUFFICIENT) | `rule_improvement_agent.py` `format_proposal` / §6.1 |
| Sandbox eval surface (ES1) | `run_sandbox_cycle(context, config=SandboxLoopConfig(...))` on caller-supplied `RouteContext` — replay positive (fix) + negative (corpus) checks inside sandbox tenant only | `core/sandbox/loop.py`; patterns in `tests/test_rule_improvement_agent.py`, `tests/test_mutation_engine.py` |
| Regression corpus shape (ES1) | `#62` `REGRESSION_CASE` envelopes + recorded baseline refs — **#65 consumes** case definitions; **does not** call `#62` generator inline at runtime unless caller supplies cases | `regression_test_agent.py` generate-only boundary (D3) |
| No-regression proof (ES1) | Synthetic corpus fixture set (bundled in tests at build) — zero new misses vs baseline detection expectations encoded in cases; not whole-repo pytest in agent core | `#62` contract FLOW CONTRACT downstream = pytest consumer |
| Promotion path (explicitly outside #65) | Phase 5 `HumanSignOffGate` + operator `DEPLOY_MUTATION` — `#65` output queues for §11 review only | `Phase5_MutationEngine_Contract.md`; `#67` §6.3 |
| Research input (non-authority) | `Cyber_Insurance_Internal_Correction_Evidence_Record_Set.md` — credibility-trail seed; optional field naming for packet sections only | Research input header — not D10 |
| False-clear guard (§6.5) | Failed `SUFFICIENT` that later regresses → permanent `#62` regression case + demotion review input (Health Score) | Template §6.5; `#67` §6.5 cross-ref |

**Open before build (PARK build if unresolved):**
1. ES1 synthetic corpus fixture manifest path (build defines `tests/fixtures/correction_evidence/` or equivalent).
2. Pre-build gate on this contract after §11 sign (Gemini/Grok via `complete_gate.py`).

Repo-reconciliation placeholders: **resolved for draft review.** §11 signed; separate operator build authorization still required.

---

## §0 Purpose — Executive Summary

When `#67` proposes a sandbox correction, operators need **proof** before §11 promotion: the fix resolves the classified miss, introduces no new blind spots, blast radius is bounded, and the verdict is reproducible.

The Correction Evidence agent assembles and **validates** that proof inside the sandbox harness. It emits a Correction Evidence Packet with verdict `SUFFICIENT` or `INSUFFICIENT`. It does **not** promote, apply, or sign anything.

**The one invariant:** this agent produces and validates evidence. **Evidence ≠ authorization.** A `SUFFICIENT` packet is an *input* to Matt's §11 decision — never a substitute for it.

Fits Team 9 alongside `#64` (classifies), `#67` (proposes), `#62` (permanent regression hardening on false-clears).

This contract is governance + draft placement only. It does not build runtime code, sign §11, reconcile scoreboard lifecycle, or unlock AUTH-5.

---

## §1 Scope

### In scope
- Reading one correction validation request envelope (Section 5).
- Consuming `#64` classification + `#67` proposal references (structured envelopes — not chat memory).
- Running sandbox-only evaluation via `run_sandbox_cycle` (and injectable test runner at build for focused ES1 proofs).
- Validating four proof bars (Section 3): fix proof, no-regression proof, blast-radius estimate, reproducibility.
- Emitting `CORRECTION_EVIDENCE_PACKET` or explicit insufficient-input / insufficient-evidence outcomes.
- Populating `#67` `correction_evidence_slot` with packet id when verdict is `SUFFICIENT` (attachment reference only — no promotion).

### Out of scope
- Rule promotion, apply, deploy, or §11 signature.
- Calling `DEPLOY_MUTATION`, HumanSignOffGate sign-off, or production policy writes.
- Replacing `#62` generator or executing whole-repo pytest as autonomous background work.
- Inventing evidence, corpus entries, or pass results without sandbox replay.
- Real tenant mail at Evidence Stage 1.
- Scoreboard, registry, governance file, or AUTH-5 mutation.
- Default registry, production Commander dispatch.

---

## §2 Locked Design Decisions

| ID | Decision |
|---|---|
| D1 | Request-in, evidence-packet-out; one validation request per invocation |
| D2 | Sandbox-only evaluation via `RouteContext` + `Environment.SANDBOX`; no production write path |
| D3 | Detect-not-enact: surfaces verdict; never promotes or applies corrections |
| D4 | Four proof bars mandatory — missing any bar → `INSUFFICIENT`, not partial pass |
| D5 | `#64` / `#67` inputs are advisory structured envelopes — no auto-routing on upstream labels |
| D6 | Insufficient request → `INPUT_INSUFFICIENT_CANNOT_VALIDATE` with named gaps |
| D7 | `#67` `correction_evidence_slot` populated only on `SUFFICIENT`; remains empty on `INSUFFICIENT` |
| D8 | Zero writes to production policy, scoreboard, registry, governance files, or AUTH-5 |
| D9 | False-clear (certified `SUFFICIENT` later fails) → mandatory `#62` permanent regression case + demotion review feed (§6.5) |

---

## §3 Wrap Points — Sandbox + Regression Harness (reconciled)

The agent **extends** existing sandbox/regression surfaces; it does **not** rebuild the mutation engine or `#62` generator.

| Step | Surface | #65 use |
|---|---|---|
| 1 — Context | `RouteContext(blackboard_root=...)` sandbox tenant | Caller-supplied sandbox context only at ES1 |
| 2 — Positive (fix proof) | `run_sandbox_cycle` with target failure fixture replay | Confirm `#67` candidate addresses `#64.failure_ref` classified miss |
| 3 — Negative (no-regression) | Same sandbox cycle against bundled synthetic corpus fixtures (`#62`-shaped cases) | Zero new misses vs baseline expectations |
| 4 — Blast radius | Reuse `#67` `estimated_detection_impact` + `blast_radius_note` + bounded parameter-key summary | Must appear in packet; agent may downgrade to `INSUFFICIENT` if unbounded |
| 5 — Reproducibility | Record `corpus_hash`, `harness_version`, `inputs_digest`, sandbox evidence ids | Independent re-run must be possible from packet fields |
| 6 — Optional inject | `evaluation_runner: Callable[..., EvaluationResult]` at build | ES1 tests use injectable runner — no network/subprocess in core path unless test harness |

**Hard rule:** #65 must not import production deploy helpers, write production policy, or treat `SUFFICIENT` as promotion. Arch review at build must confirm no promote/apply/sign path exists in the wrapper module.

---

## §4 Evidence Stage (canonical — `Agent_Design_Contract_Template` §6)

Evidence Stage is **validation maturity**, orthogonal to VISION Stage A/B/C autonomy.

| Stage | Name | #65 meaning |
|---|---|---|
| **1** | **Synthetic** *(default at §11)* | Synthetic / replayed sandbox corpus only; bundled fixtures; no real tenant data |
| **2** | **Supervised** *(future promotion)* | Real past misses, privacy-filtered (`#93`), sandbox-evaluated; Matt confirms ≥3 samples per template §6.2 |
| **3** | **Production-adjacent** *(future promotion)* | Live signal may inform request selection; evaluation remains sandbox-only; **never promote/apply** |

**Signing locks Evidence Stage 1 only.** Stage 2/3 require separate signed promotion records per template §6.2.

---

## §5 Inputs — Correction Validation Request Envelope

Exactly one input per invocation:

```
CORRECTION_VALIDATION_REQUEST
request_id:           <uuid>
failure_ref:          <must match #64.failure_ref when classification supplied>
classification_ref:   <optional #64 FAILURE_CLASSIFICATION.id>
proposal_ref:         <#67 RULE_IMPROVEMENT_PROPOSAL.proposal_id — required>
target_category:      <optional — must match #64.category when both present>
corpus_refs:          [<#62 REGRESSION_CASE ids or fixture manifest keys>]
tenant_scope:         sandbox_only | <tenant_id ES2+ only — blocked at ES1>
evidence_refs:        [<traceable ids>]
notes:                <optional operator context — not authority>
```

**ES1 build:** `tenant_scope` must be `sandbox_only`. Missing `proposal_ref` or `failure_ref` → `INPUT_INSUFFICIENT_CANNOT_VALIDATE`.

When `classification_ref` is supplied, `#64` category must be in `{REGRESSION, FUNCTIONAL, UNCLASSIFIED}` with severity ≥ `MEDIUM` for §11 promotion path — otherwise packet may still be assembled but verdict defaults to `INSUFFICIENT` with named gap (wrapper does not guess).

---

## §6 Outputs — Correction Evidence Packet

### §6.1 Primary success envelope (`SUFFICIENT` only when all four proof bars satisfied)

```
CORRECTION_EVIDENCE_PACKET
packet_id:              <uuid>
request_ref:            <CORRECTION_VALIDATION_REQUEST.request_id>
proposal_ref:           <#67 proposal_id>
classification_ref:     <optional #64 id>
verdict:                SUFFICIENT | INSUFFICIENT
fix_proof:              <evidence-traced — target failure replay pass>
no_regression_proof:    <corpus run — zero new misses; case ids listed>
blast_radius_estimate:  <bounded — from #67 + quantified note>
reproducibility:        corpus_hash=<sha256> harness_version=<semver/id> inputs_digest=<sha256>
sandbox_evidence_ids:   [<UUID>]
gaps:                   [] when SUFFICIENT; named list when INSUFFICIENT
rationale:              plain text — no promote/apply/sign language
```

### §6.2 Explicit non-success outcomes

- `INPUT_INSUFFICIENT_CANNOT_VALIDATE` — missing required envelope fields.
- `CORRECTION_EVIDENCE_PACKET` with `verdict: INSUFFICIENT` — partial proof; `gaps` lists missing bars (fix / no-regression / blast-radius / reproducibility).

### §6.3 §11 promotion (explicitly NOT this agent)

`SUFFICIENT` → queued for Matt §11 promotion review + Phase 5 HumanSignOffGate. #65 never auto-advances lifecycle, scoreboard, or registry.

### §6.4 `#67` slot wiring

On `SUFFICIENT` only: set `#67` proposal's `correction_evidence_slot` to `packet_id` (reference attachment — not inline promotion).

---

## §6.5 Progressive Hardening (false-clear guard)

The dangerous failure is a **false-clear** — certifying a bad correction as `SUFFICIENT`.

- Any `#65` `SUFFICIENT` packet whose proposal **later fails** validation or production-adjacent replay → mandatory **permanent `#62` regression case** + **demotion review** of `#65`.
- False-clear rate is a tracked Health Score input; repeated false-clears force demotion per template §6.3.
- Adversarial requirement: a crafted `#67` proposal must not be able to manufacture `SUFFICIENT` without satisfying all four proof bars (build must include adversarial pytest).

Cross-refs: `#64` classifies false-clear failures · `#62` consumes new permanent cases · `#67` §6.5 failed proposals feed regression downstream.

---

## §7 Hard Limits

| Limit | Rule |
|---|---|
| AUTH-5 | Blocked — no autonomous task selection or routing |
| Promote / apply / sign | No path by construction — verdict is evidence only |
| §11 | Human review mandatory regardless of verdict |
| Production rule store | No write path in this component |
| Safe-Stop | Matt-only halt — honor `#94` when wired |
| Guardrail 11 | No cross-tenant content in packets — sandbox evidence ids + hashes only |
| Blast radius | Bounded + quantified in every packet; unbounded → `INSUFFICIENT` |
| Health Score | ELITE 85+ target at GATED; false-clear rate weighted |
| Dispatcher | Scoreboard row #65; lifecycle tracked; not default registry at ES1 |

---

## §8 Relationship to Signed Surfaces

- **#64 Failure Classification** — upstream failure label; no auto-response.
- **#67 Rule Improvement** — upstream proposal; `correction_evidence_slot` reserved until #65 packet attaches.
- **#62 Regression Test** — generate-only; #65 consumes case shapes; false-clears append permanent cases.
- **Phase 5 Mutation Engine** — promotion/deploy outside #65.
- **Governed Swarm Charter** — charter ≠ agent authorization.

---

## §9 Pre-Build Gate Plan

When Matt chooses §11 path:
1. Pre-build gate via `audit_tools/complete_gate.py` on this contract (0 blocking target).
2. Adversarial focus: can a crafted `#67` proposal force `SUFFICIENT` without fix + no-regression proof?
3. Worker manifest must prove no promote/apply/sign path and no production write in wrapper module.

---

## §10 Open Questions (operator / gate)

| # | Question | Default |
|---|---|---|
| Q1 | ES1 bundled corpus manifest location | `tests/fixtures/correction_evidence/` at build |
| Q2 | Minimum `#62` case count for no-regression bar at ES1 | ≥1 positive target case + ≥3 corpus negatives (synthetic) |
| Q3 | Stage 2 real-miss privacy filter | `#93` contract — separate promotion record |

---

## §11 Signature Block

**§11 — Correction Evidence Agent Design Contract (Deep Dive)**

SIGNED. This signature locks D1–D9 and authorizes the Evidence Stage 1 (Synthetic) `CorrectionEvidenceAgent` wrapper build + focused tests only; no Blueprint-of-Record population beyond feedstock completion, no default-registry registration, no production dispatch, no rule promotion/apply, no AUTH-5. Matt also authorized `MMI_65_SCOREBOARD_SIGNED_UNBUILT_RECONCILE_ONLY` in this signing action.

- [x] I approve this contract as written.
- [x] I authorize pre-build gate review when ready — completed clean 0 blocking (`mmi_65_contract_gate_20260624T221330Z`).
- [x] On clean gate, I §11-sign and authorize reconcile to SIGNED_UNBUILT.

Confirmed: #65 **validates** correction evidence for §11 review; it **never** promotes, applies, or signs rule changes. A `SUFFICIENT` verdict is **not** authorization.

> Matt Nichol June 24th 2026

---

## BUILD CONDITIONS (post-§11)

§11 SIGNED. Authorizes Stage 1 `CorrectionEvidenceAgent` wrapper build + focused tests only when operator separately names build.

At signing, this agent is at **Evidence Stage 1 — Synthetic**. No build authorization for Evidence Stage 2 or 3 until promotion conditions in `Agent_Design_Contract_Template_Deep_Dive.md` §6.2 are satisfied and a separate promotion record is signed.

Matt Nichol — Correction Evidence Agent Design Contract §11 signed (MMI-DEC-162).

---

*End of contract.*
