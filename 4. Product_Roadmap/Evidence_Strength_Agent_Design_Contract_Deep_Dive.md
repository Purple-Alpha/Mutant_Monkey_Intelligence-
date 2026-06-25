# Evidence Strength Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_50_EVIDENCE_STRENGTH_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** §11 SIGNED 2026-06-25 by Matt Nichol (Gemini pre-build gate clean `audit_outputs/mmi_50_contract_gate_20260625T210447Z.md` 0 blocking / 0 warnings; MMI-DEC-205). Step 00 PASS 31/31. **SIGNED CONTRACT — BUILD NOT AUTHORIZED** until separate operator build-lane authorization (MMI-DEC). Signing locks D1–D11 for `EvidenceStrengthAgent` (Layer 4 Evidence, ES1 Synthetic). Pre-build gate review complete. Wrapper build + focused tests authorized **only** after separate MMI-DEC build lane. BOR feedstock rank-1 (Estimator **17.00** · MMI-DEC-203). Authorizes **no** eval-harness execution, **no** metric computation from fixtures, **no** `pre_ship_audit.py` invocation, **no** Blackboard reads at ES1, **no** evidence/workflow ledger append/update/delete (except registry-gated `AGENT_CONTRIBUTION`), **no** capability-registry mutation, **no** accuracy/compliance/certification claim, **no** default-registry registration, **no** production dispatch, **no** autonomous action, and **no** AUTH-5.

**Candidate:** #50 — Evidence Strength

**Owner:** Matt Nichol

**Track:** BREADTH / Evidence-and-Outcome-Reporting stage 4 (Layer 4 Evidence scoreboard row)

**Lane:** Agent Design Contract (BOR feedstock rank 1 · MMI-DEC-203)

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** Built — `EvidenceStrengthAgent` at `core/orchestrator/evidence_strength_agent.py` (`fddccbd`, MMI-DEC-207); completion gate 0/0 — `audit_outputs/evidence_strength_20260625T213536Z.md` (MMI-DEC-208); scoreboard `GATED`

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `4. Product_Roadmap/Email_Security_Testing_Evidence_Framework_Deep_Dive.md` (parent testing/evidence framework — **not** rewritten by #50)
- `4. Product_Roadmap/Audit_Trail_Agent_Design_Contract_Deep_Dive.md` (#49 sibling — audit-trail attestation; distinct slot)
- `4. Product_Roadmap/Evidence_Package_Agent_Design_Contract_Deep_Dive.md` (#46 sibling — package assembly; distinct slot)
- `4. Product_Roadmap/Regression_Test_Agent_Design_Contract_Deep_Dive.md` (#62 sibling — Layer 5 regression-case generator; distinct slot)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#50 row — framework/harness split locked in contract)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/eval/` (fraud eval harness — **not** invoked by #50 wrapper at ES1)
- `audit_tools/pre_ship_audit.py` (commit-completeness gate consumer — **not** invoked by #50 wrapper at ES1)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py`
- `VISION.md` (Stage A — analyze / recommend / evidence only)

**Build path:** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/evidence_strength_agent.py` — **built MMI-DEC-207**

---

## Agent Design Contract block

**Boundary split (Open-Q1 / scoreboard reconciliation):** The Email Security Testing & Evidence Framework (`Email_Security_Testing_Evidence_Framework_Deep_Dive.md`) and the existing eval harness (`core/scoring/eval/`, including `fraud_eval_harness.py` and `fraud_eval_dataset.jsonl`) are **outside** this agent as execution, metric-computation, or gate-invocation surfaces at ES1. #50 is a caller-attestation-only Layer 4 Evidence wrapper that projects testing-framework evidence-strength posture from explicit governed caller booleans — it never runs eval cases, never computes accuracy/precision/recall, never reads fixture payloads, never mutates the capability registry, and never claims framework compliance or test-run pass.

## Agent Design Contract

Agent name: Evidence Strength Agent (`EvidenceStrengthAgent`)
Swarm inventory ID: #50 — Evidence Strength
Canonical layer: 4 — Evidence
Canonical team / case type: Evidence / testing discipline — stage-4 evidence-strength posture for one governed eval/test run (capability honesty, denominator discipline, evidence-required rule)
Authority level: Level 3 — Specialist Agent
Stage posture: VISION Stage A — analyze / recommend / evidence only
Evidence Stage (current): Stage 1 — Synthetic (§11 signed 2026-06-25)

Role: For one caller-supplied evidence-strength request, project which governed testing-framework discipline anchors the caller attests for the eval run and emit bounded Layer 4 evidence-strength attestation facts
Boundary: Caller-attested anchors-in, evidence-strength contribution-out. No Blackboard reads at ES1; no eval-harness or pre-ship audit invocation; no metric computation; no evidence/workflow ledger append/update/delete except registry-gated `AGENT_CONTRIBUTION` via `submit_agent_contribution`; no capability-registry write; no done declaration
Explicit non-authorities: No `fraud_eval_harness`, `runner.py`, or eval-dataset reads for scoring; no `pre_ship_audit.py` or commit-completeness gate execution; no `assemble_audit_packet` or `core/evidence_package/` import; no accuracy/precision/recall/FPR/FNR computation; no capability-registry append/promote/demote; no failure-card or retest-loop execution; no red-team/smoke/regression tier execution; no compliance/certification/insurer-approval/bulletproof claim; no buyer-facing test verdict; no scoreboard/registry/governance writes; no AUTH-5; no autonomous operation

Inputs: One explicit request: `tenant_id`, `case_id`, optional `eval_run_id`, optional explicit anchor booleans (`capability_registry_discipline_attested_present`, `supported_only_denominator_attested_present`, `evidence_required_per_score_attested_present`, `no_chain_of_thought_attested_present`, `synthetic_fixtures_only_attested_present` — omitted means unknown/not attested, `false` means caller attests absent/invalid), optional bounded `attested_category_statuses` (max 8 names from closed enum `supported`, `not_supported_yet`, `not_present_in_sample`, `evidence_missing` — caller attested only). No Blackboard root/environment at ES1. Caller supplies run identity — agent does not discover from fixture paths, JSONL rows, harness stdout, or external systems
Outputs: One `AgentContribution` (layer 4): closed evidence-strength attestation facts + bounded `control_mapping` (`evidence_strength:stage_a_synthetic` at ES1) + optional bounded Stage 1 `underwriter_note`. No challenge/evidence/control fields beyond contribution schema at Stage 1
Evidence emitted: Closed facts only: `evidence_strength_synthetic_attestation_only` (always at ES1), `evidence_strength_missing`, `evidence_strength_capability_registry_attested_present`, `evidence_strength_capability_registry_attested_missing`, `evidence_strength_supported_denominator_attested_present`, `evidence_strength_supported_denominator_attested_missing`, `evidence_strength_evidence_bundle_attested_present`, `evidence_strength_evidence_bundle_attested_missing`, `evidence_strength_no_cot_attested_present`, `evidence_strength_no_cot_attested_missing`, `evidence_strength_synthetic_fixtures_attested_present`, `evidence_strength_synthetic_fixtures_attested_missing`, `evidence_strength_attestation_all_anchors_present` (only when all five anchors explicitly attested present — not a framework pass or accuracy certification), optional bounded `evidence_strength_category_status:<status>` (max 8, closed enum only). Never emit `evidence_strength_posture_complete`, `evidence_strength_framework_compliant`, `evidence_strength_accuracy_certified`, or facts that imply a test run passed, metrics were computed, or the Email Security Testing framework §11 is satisfied
Data minimization: No raw fixture content, eval JSONL rows, confusion-matrix values, accuracy percentages, capability-registry file bodies, failure-card text, chain-of-thought strings, tenant secrets, or reviewer-note prose in the contribution. Optional `underwriter_note` is max 160 chars (shared `AgentContribution` cap), facts-only posture summary — no metric values, forbidden-language claims, or §11 framework pass language
Tenant isolation: Uses only caller-supplied `tenant_id` and `case_id`; tenant A attestation never verifies tenant B; no cross-tenant category-status reuse

Two-pass role: Pass 1 Evidence only. `challenge()` returns `None`
Decision Evidence Record contribution: `observed_facts`: closed evidence-strength attestation facts only; `interpretations`: none; `assumptions`: caller attestation reflects the same synthetic eval run; `missing_evidence`: wrapper does not verify on-disk capability registry, harness execution, metric denominators, evidence-bundle contents, or Email Security Testing framework §11 signature state; `recommended_verification`: none emitted; `final_outcome_contribution`: synthetic attestation projection only — not eval-harness pass/fail or buyer-facing test verdict
Human review trigger: Any move beyond synthetic attestation, any real eval-harness execution, any metric computation, any pre-ship audit invocation, or any buyer-facing test verdict requires separate Matt-signed authorization
Verification trigger: This agent does not initiate test execution or framework audits; it reflects caller-attested discipline posture only

Scoring / action posture: Facts-only Layer 4 evidence. No scoring lift, no risk floor, no recommended action, no accuracy/precision/recall emission, no compliance/insurance claim
Default rollout: Evidence Stage 1 — not in `build_default_registry`; explicit callers/tests only until signed promotion
Autonomous action: none

Promotion conditions: Per template §6.2 — §11 signed; wrapper tests green; pre-build + completion gates 0 blocking; >= 3 supervised evidence-strength samples with expected attestation facts at ES1; **ES2 promotion additionally requires >= 1 supervised sample with harness-derived (non-attested-only) verification** under separate real-data/eval-execution authorization; operator promotion MMI-DEC
Demotion conditions: Eval-harness invocation, metric computation, pre-ship audit invocation, capability-registry write, Blackboard read at ES1, not_supported-scored-as-zero overclaim, accuracy/compliance overclaim facts, chain-of-thought leakage, cross-tenant leak, fixture/raw-value leakage, or package-generator mutation — per template §6.3
Retest evidence: Permanent regression for every demotion trigger per template §6.5
Calibration requirement: ES1 synthetic fixtures only; Stage 2 requires supervised eval-discipline samples and separate real-data/eval-execution authorization if applicable

Failure modes: Harness-execution creep; metric-computation creep; framework-compliance overclaim; #62 regression-generator conflation; #46 package conflation; #49 audit-trail conflation; capability-registry mutation; not_supported-as-zero denominator lie; chain-of-thought leakage — see §5
Required tests: Wrapper protocol, tri-state anchor mapping, attestation fact vocabulary, persistence via `submit_agent_contribution` only, no ledger/workflow writes, no Blackboard or eval-harness reads, no `pre_ship_audit` import/call, tenant isolation, no registry default, no network/subprocess, no raw leakage, no framework-pass overclaim — see §6
Audit requirements: Step 00 `scripts/validate_agent_contract_block.py` PASS; pre-build gate via `audit_tools/complete_gate.py`; completion gate on implementation slice
Signed-spec dependencies: `Agent_Design_Contract_Template_Deep_Dive.md`, `Email_Security_Testing_Evidence_Framework_Deep_Dive.md`, `Compliance_and_Trend_Watch_Process.md`, `VISION.md`, `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`
Build Authorization dependency: At §11 signature, Evidence Stage 1 only. No build until §11 + operator build authorization. Existing eval harness and Email Security Testing framework behavior remain immutable. Distinct from #49 `AuditTrailAgent`, #46 `EvidencePackageAgent`, and #62 `RegressionTestAgent` — #50 owns the stage-4 evidence-strength governed slot only

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-25 (draft placement · MMI-DEC-204):

| Placeholder | Resolved value | Repo evidence |
|---|---|---|
| Parent framework | `Email_Security_Testing_Evidence_Framework_Deep_Dive.md` — DRAFT pre-§11; four-value category status + evidence-required discipline; D27 `attestation` ban is red-team mission field names only (not Layer 4 ES1 caller-asserted facts) | Scoreboard #50 row; MMI-DEC-203 unpark source |
| Eval harness surface | `core/scoring/eval/fraud_eval_harness.py`, `runner.py`, `fraud_eval_dataset.jsonl` — execution outside #50 at ES1 | Framework §1 in-scope wrap of existing harness |
| Pre-ship gate | `audit_tools/pre_ship_audit.py` — commit-completeness consumer; not invoked by #50 | Framework §4.5.9 D22 |
| Category status enum | `supported`, `not_supported_yet`, `not_present_in_sample`, `evidence_missing` | Framework D1 |
| #49 relationship | `AuditTrailAgent` GOVERNED_AGENT — audit-trail posture | MMI-DEC-201; distinct Layer 4 slot |
| #46 relationship | `EvidencePackageAgent` GOVERNED_AGENT — package assembly | Distinct builder path |
| #62 relationship | `RegressionTestAgent` — Layer 5 regression-case generator | Generate-only; distinct slot |

Repo-reconciliation placeholders: **resolved.** §11 signed MMI-DEC-206 2026-06-25; pre-build gate clean `audit_outputs/mmi_50_contract_gate_20260625T210447Z.md` 0 blocking / 0 warnings.

---

## §0 Purpose

Unblock swarm #50 Evidence Strength by placing the Agent Design Contract that separates **testing-framework discipline** from **eval-harness execution**. The scoreboard row names the Email Security Testing framework (draft); a governed wrapper must not conflate framework attestation with running `fraud_eval_harness`, computing accuracy, or invoking pre-ship audit gates.

#50 is the caller-attestation-only Evidence agent for stage-4 evidence-strength posture: it tells the swarm which governed testing-discipline anchors the caller attests for an eval run — not whether tests passed, not whether accuracy improved, and not whether the framework is §11 signed.

This contract is governance + signed spec placement. §11 signed 2026-06-25 (MMI-DEC-206). It does not build runtime code or unlock AUTH-5 without separate build-lane authorization. **Scoreboard posture:** row #50 §11 signed; `SPEC_ONLY` -> `SIGNED_UNBUILT` (MMI-DEC-206); wrapper build next.

---

## §1 Scope

### In scope
- Agent Design Contract block governing a future `EvidenceStrengthAgent` wrapper (Layer 4 Evidence).
- Evidence Stage 1 (Synthetic) at signature.
- Caller-attested capability-registry discipline, supported-only denominator discipline, evidence-required-per-score discipline, no-chain-of-thought discipline, and synthetic-fixtures-only discipline for one eval run.
- Optional bounded attested category-status facts using the framework four-value enum (max 8).
- Explicit prohibition on eval-harness execution, metric computation, pre-ship audit invocation, Blackboard reads, and capability-registry writes.

### Out of scope
- Any change to `Email_Security_Testing_Evidence_Framework_Deep_Dive.md`, eval harness modules, dataset files, or `pre_ship_audit.py` behavior.
- Running smoke/regression/adversarial/red-team tiers or emitting pass/fail verdicts.
- Computing accuracy, precision, recall, FPR, FNR, UDR, or capability-coverage metrics.
- Mutating capability registry status or promoting/demoting categories.
- Replacing or merging #62 Regression Test, #46 Evidence Package, or #49 Audit Trail — parallel governed slots.
- Registering in `build_default_registry` or production dispatch at ES1.
- Real-customer-data handling, Evidence Stage 2/3 promotion, or autonomous action.

---

## §2 Locked Design Decisions

| ID | Decision |
|---|---|
| D1 | **Identity.** Evidence Strength is Layer 4 Evidence, Authority Level 3 Specialist, VISION Stage A, ES1 Synthetic at signing. `agent_id = evidence_strength_001`. |
| D2 | **Harness immutability.** Wrapper must not import or call `fraud_eval_harness`, `runner.py`, or read eval dataset rows for scoring. Harness execution remains governed separately. |
| D3 | **Attestation-only at ES1.** Only authorized persistence: `submit_agent_contribution` → `AGENT_CONTRIBUTION`. No Blackboard reads; no direct ledger writes. |
| D4 | **Caller-supplied run context.** `tenant_id`, `case_id`, and anchor booleans come from explicit governed caller context — no discovery from fixtures or harness output. |
| D5 | **Discipline semantics.** Attested anchors map to closed `evidence_strength_*` facts; none imply test pass, metric values, or framework §11 satisfaction. |
| D6 | **Category-status facts.** Optional `attested_category_statuses` use framework D1 enum only; unknown values rejected; max 8. |
| D7 | **Persistence + rollout.** Contributions via registry-gated `AGENT_CONTRIBUTION`; not in `build_default_registry` at ES1. |
| D8 | **Stage A / no autonomy.** No block/quarantine/test execution; no autonomous action. |
| D9 | **No gate side effects.** No `pre_ship_audit.py`, subprocess test runners, or network calls. |
| D10 | **Tests are Stage 1 evidence.** Suite must prove D2–D9 before build close. |
| D11 | **Attestation vocabulary carve-out (D27 scope).** Internal Layer 4 fact prefixes `evidence_strength_*_attested_*` and `evidence_strength_synthetic_attestation_only` denote caller-supplied boolean discipline anchors only — the same ES1 pattern as #49 `audit_trail_*_attested_*` (MMI-DEC-199). This is **not** carrier-jargon "control attestation," **not** Email Security Testing framework D27 red-team mission **field naming**, and **not** a buyer-facing compliance/warranty claim per `Compliance_and_Trend_Watch_Process.md`. |

---

## §5 Failure modes

| Failure | Expected behavior |
|---|---|
| Harness re-run | Wrapper must never invoke eval harness; fail closed in tests |
| Metric creep | Any accuracy/precision/recall computation forbidden |
| Framework overclaim | `evidence_strength_framework_compliant` / posture-complete facts forbidden |
| Registry mutation | Capability-registry writes forbidden |
| #62 conflation | Regression-case generation remains #62; #50 adds evidence-strength slot only |
| Raw leakage | Fixture rows, metric values, chain-of-thought never in contribution |
| Cross-tenant attestation | Tenant-scoped caller context only |

---

## §6 Required tests (implementation slice — not run at draft)

1. `EvidenceStrengthAgent` satisfies `Agent` protocol.
2. Missing anchors → `evidence_strength_missing` + synthetic attestation fact.
3. Tri-state mapping for all five anchor booleans.
4. All five present → `evidence_strength_attestation_all_anchors_present` without framework-pass language.
5. Optional category-status facts capped at 8 with enum validation.
6. Persistence only via `submit_agent_contribution`.
7. Never calls eval harness, pre-ship audit, or Blackboard read paths.
8. Tenant isolation on shared `case_id` across tenants.
9. Not in `build_default_registry()`; no network/subprocess; no raw leakage.
10. Forbidden overclaim facts never emitted.

---

## §8 Pre-Build Gate Plan

1. Step 00: `python3 scripts/validate_agent_contract_block.py` on this contract (exit 0 required).
2. Pre-build gate via `audit_tools/complete_gate.py` (0 blocking target).
3. Adversarial focus: can wrapper invoke eval harness or compute metrics via import side effect?
4. Manifest must list contract + template + Email Security Testing framework — not implementation files.

Gate glob: `mmi_50_contract_gate_*.md`

---

## §11 Signature Block

**§11 — Evidence Strength Agent Design Contract (Deep Dive)**

- [x] I approve this contract as written.
- [x] I authorize pre-build gate review when ready.
- [x] On clean gate, I §11-sign and authorize Stage 1 wrapper build + focused tests only.

Confirmed: #50 projects testing-framework evidence-strength attestation only; it never runs the eval harness, never computes metrics, and never claims framework compliance.

> Matt Nichol June 25th 2026

---

## BUILD CONDITIONS (post-§11)

At signing, Evidence Stage 1 — Synthetic only. §11 authorizes wrapper build path only when operator separately authorizes build lane (MMI-DEC pattern). No change to eval harness or Email Security Testing framework modules implied.

---

*End of contract.*
