# Audit Trail Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_49_AUDIT_TRAIL_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** DRAFT UNSIGNED — pre-§11. BOR feedstock rank-1 (Estimator **27.00** · MMI-DEC-197). Signing locks D1–D10 and authorizes the `AuditTrailAgent` Stage 1 wrapper build + focused tests **only**. It authorizes **no** Canonical Evidence Ledger schema change, **no** blackboard write/delete, **no** `assemble_audit_packet` / package-generator mutation, **no** mutation-engine `audit_trail.py` change, **no** default-registry registration, **no** production dispatch, **no** autonomous action, and **no** AUTH-5.

**Candidate:** #49 — Audit Trail

**Owner:** Matt Nichol

**Track:** BREADTH / Evidence-and-Outcome-Reporting stage 4 (Layer 4 Evidence scoreboard row)

**Lane:** Agent Design Contract (BOR feedstock rank 1 · MMI-DEC-197)

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** BLOCKED until §11 signature + separate build authorization

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `4. Product_Roadmap/Phase1_Infrastructure_Agent_Design_Contract.md` (Component 1 Canonical Evidence Ledger — append-only; **not** rewritten by #49)
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` (§14.3.4 Audit Trail stage — policy hash + tenant override separation)
- `4. Product_Roadmap/Evidence_Package_Agent_Design_Contract_Deep_Dive.md` (#46 sibling — package/audit-packet builder; #49 does not assemble packets)
- `4. Product_Roadmap/Case_Timeline_Agent_Design_Contract_Deep_Dive.md` (#47 sibling — timing anchors; distinct from audit-trail posture)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#49 row — ledger/packet split locked in contract)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/` (append-only ledger — read-only summary surface for wrapper; no writes)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/evidence_package/audit_packet.py` (§10 coverage assembly — **not** invoked by #49 wrapper)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py`
- `VISION.md` (Stage A — analyze / recommend / evidence only)

**Proposed future build path (not authorized here):** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/audit_trail_agent.py`

---

## Agent Design Contract block

**Boundary split (Open-Q1 / scoreboard reconciliation):** Phase 1 Component 1 (`core/blackboard/` append-only Canonical Evidence Ledger) and cyber-insurance `assemble_audit_packet` (#46 builder path) are **outside** this agent as mutable or assembly surfaces. #49 is a read-only Layer 4 Evidence wrapper that projects case audit-trail posture from caller-attested anchors and optional tenant-scoped read-only record summaries — it never writes ledger entries, never deletes records, never assembles audit packets, and never touches mutation-engine `core/mutation/audit_trail.py`.

## Agent Design Contract

Agent name: Audit Trail Agent (`AuditTrailAgent`)
Swarm inventory ID: #49 — Audit Trail
Canonical layer: 4 — Evidence
Canonical team / case type: Evidence / audit — stage-4 audit-trail posture for one governed case (policy hash + override separation + append-only chain)
Authority level: Level 3 — Specialist Agent
Stage posture: VISION Stage A — analyze / recommend / evidence only
Evidence Stage (current): Stage 1 — Synthetic (at §11 signature, if signed)

Role: For one caller-supplied audit-trail request, project whether governed append-only evidence-chain anchors and policy/override audit posture are present for the case and emit bounded Layer 4 audit-trail facts
Boundary: Caller-attested anchors-in, audit-trail contribution-out. No blackboard writes/deletes, no package/audit-packet assembly, no policy mutation, no Grok submission, no done declaration
Explicit non-authorities: No `assemble_audit_packet`, `generate_package_from_test_plan`, or `audit_package()`; no blackboard append/update/delete; no mutation-engine audit trail APIs; no policy/override authoring; no tenant override creation; no compliance/certification/insurer-approval claim; no buyer-facing audit release; no scoreboard/registry/governance writes; no AUTH-5; no autonomous operation

Inputs: One explicit request: `tenant_id`, `case_id`, optional `policy_hash_present` (bool), optional `tenant_override_separation_valid` (bool — caller attests requested_by ≠ approved_by without emitting operator labels), optional `append_only_records_present` (bool), optional bounded `attested_record_types` (closed enum names from Phase 1 evidence types or `RecordType` names — caller attested only), optional Blackboard root/environment. Caller supplies case identity — agent does not discover from raw email or external systems
Outputs: One `AgentContribution` (layer 4): closed audit-trail facts + optional bounded `control_mapping` + optional bounded Stage 1 `underwriter_note`. No verification/challenge fields at Stage 1
Evidence emitted: Closed facts only, e.g. `audit_trail_missing`, `audit_trail_policy_hash_present`, `audit_trail_policy_hash_missing`, `audit_trail_override_separation_present`, `audit_trail_override_separation_missing`, `audit_trail_append_only_chain_present`, `audit_trail_append_only_chain_missing`, optional bounded `audit_trail_record_type:<type>`. No policy hash values, operator names, override text, record payloads, package paths, or audit-packet file lists
Data minimization: No raw blackboard payloads, policy file contents, override requested_by/approved_by strings, signed_by paths, email bodies, tenant secrets, or audit-packet chunk bodies in the contribution
Tenant isolation: Reads only caller-supplied tenant scope; tenant A attestation never verifies tenant B; optional read-only summaries use tenant-scoped Blackboard paths only

Two-pass role: Pass 1 Evidence only. `challenge()` returns `None`
Decision Evidence Record contribution: `observed_facts`: closed audit-trail posture facts; `interpretations`: none; `assumptions`: caller attestation reflects the same synthetic case; upstream agents wrote append-only records per signed contracts; `missing_evidence`: wrapper does not prove on-disk signed-policy artifact resolution or live override registry state; `recommended_verification`: none emitted; `final_outcome_contribution`: audit-trail stage posture projection only
Human review trigger: Any move beyond synthetic attestation, any real policy/override registry read, any package/audit-packet assembly, or any buyer-facing audit release requires separate Matt-signed authorization
Verification trigger: This agent does not initiate policy review or override approval; it reflects caller-attested posture only

Scoring / action posture: Facts-only Layer 4 evidence. No scoring lift, no risk floor, no recommended action, no compliance/insurance claim
Default rollout: Evidence Stage 1 — not in `build_default_registry`; explicit callers/tests only until signed promotion
Autonomous action: none

Promotion conditions: Per template §6.2 — §11 signed; wrapper tests green; pre-build + completion gates 0 blocking; >= 3 supervised audit-trail samples with expected posture facts; operator promotion MMI-DEC
Demotion conditions: Blackboard write/delete, audit-packet assembly, policy/override authoring, cross-tenant leak, hash/operator/override-text leakage, or package-generator mutation — per template §6.3
Retest evidence: Permanent regression for every demotion trigger per template §6.5
Calibration requirement: ES1 synthetic fixtures only; Stage 2 requires supervised audit-trail samples and separate real-data authorization if applicable

Failure modes: Ledger-write creep; audit-packet conflation with #46; timeline conflation with #47; mutation audit_trail conflation with #88; policy-hash/override raw leakage; cross-tenant attestation mix — see §5
Required tests: Wrapper protocol, missing/present policy/override/chain mapping, read-only purity, no blackboard writes, no `assemble_audit_packet`, tenant isolation, no registry default, no network/subprocess, no raw leakage — see §6
Audit requirements: Step 00 `scripts/validate_agent_contract_block.py` PASS; pre-build gate via `audit_tools/complete_gate.py`; completion gate on implementation slice
Signed-spec dependencies: `Agent_Design_Contract_Template_Deep_Dive.md`, `Phase1_Infrastructure_Agent_Design_Contract.md`, `Cyber_Insurance_Evidence_Package_Deep_Dive.md`, `Evidence_Package_Agent_Design_Contract_Deep_Dive.md`, `VISION.md`, `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`
Build Authorization dependency: At §11 signature, Evidence Stage 1 only. No build until §11 + operator build authorization. Canonical Evidence Ledger and audit-packet assembly behavior remain immutable. Distinct from #46 `EvidencePackageAgent` and #47 `CaseTimelineAgent` — #49 owns the stage-4 audit-trail governed slot only

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-25 (draft placement · MMI-DEC-198):

| Placeholder | Resolved value | Repo evidence |
|---|---|---|
| Ledger surface | `core/blackboard/` append-only — Phase 1 §3 Component 1 | Phase 1 contract §11 signed; scoreboard #49 row |
| Packet surface | `core/evidence_package/audit_packet.py` — #46 builder only | Evidence Package contract D3 builder/auditor split |
| Mutation trail | `core/mutation/audit_trail.py` — #88 ensemble component | Not #49; scoreboard row #88 |
| Stage-4 test-plan anchor | Cyber Insurance §14.3.4 policy hash + override separation | Five-stage chain stage 4 |
| #47 relationship | `CaseTimelineAgent` GOVERNED_AGENT — timing anchors | MMI-DEC-168; does not retire #49 slot |
| #46 relationship | `EvidencePackageAgent` GOVERNED_AGENT — package assembly | Distinct builder path |

Repo-reconciliation placeholders: **resolved for draft review.** §11 unsigned; pre-build gate not run.

---

## §0 Purpose

Unblock swarm #49 Audit Trail by signing the **ledger/packet split** that blocked Phase 1 Open-Q1. The scoreboard row names both `core/blackboard/` and `evidence_package/audit_packet.py`; a governed wrapper must not conflate Canonical Evidence Ledger infrastructure with cyber-insurance audit-packet assembly.

#49 is the read-only Evidence agent for stage-4 audit-trail posture: it tells the swarm whether governed append-only chain anchors and policy/override audit separation are attested for a case — not whether a package is complete, not whether timing SLAs hold, and not whether policy files on disk resolve.

This contract is governance + draft placement only. It does not build runtime code, sign §11, reconcile scoreboard lifecycle, or unlock AUTH-5.

---

## §1 Scope

### In scope
- Agent Design Contract block governing a future `AuditTrailAgent` wrapper (Layer 4 Evidence).
- Evidence Stage 1 (Synthetic) at signature.
- Caller-attested policy-hash presence, tenant-override separation validity, and append-only chain presence for one case.
- Optional bounded attested record-type facts using closed vocabulary.
- Explicit prohibition on blackboard writes, audit-packet assembly, and package-generator calls.

### Out of scope
- Any change to Canonical Evidence Ledger schema, write routes, or Phase 1 Component 1 text.
- Any change to `assemble_audit_packet`, package generator stages, or #46 wrapper behavior.
- Calling `generate_package_from_test_plan`, `audit_package()`, or mutation-engine audit trail APIs from the wrapper.
- Replacing or merging #46 Evidence Package or #47 Case Timeline — parallel governed slots.
- Registering in `build_default_registry` or production dispatch at ES1.
- Real-customer-data handling, Evidence Stage 2/3 promotion, or autonomous action.

---

## §2 Locked Design Decisions

| ID | Decision |
|---|---|
| D1 | **Identity.** Audit Trail is Layer 4 Evidence, Authority Level 3 Specialist, VISION Stage A, ES1 Synthetic at signing. `agent_id = audit_trail_001`. |
| D2 | **Ledger immutability.** Wrapper must not append, update, or delete blackboard records. Phase 1 append-only invariant stays infrastructure-only. |
| D3 | **Packet read-only.** Wrapper must not import or call `assemble_audit_packet` or any package-generator write path. #46 owns assembly. |
| D4 | **Caller-attested anchors.** Policy hash presence, override separation validity, and chain presence come from explicit governed caller context — no external discovery. |
| D5 | **Posture semantics.** All three anchors present → `audit_trail_posture_complete`; any missing → specific missing facts; none authorize compliance, insurer approval, or buyer release. |
| D6 | **Audit-scoped facts.** Fact prefix `audit_trail_*` distinguishes #49 contributions from #47 timeline facts and #46 package metadata. |
| D7 | **Persistence + rollout.** Contributions via registry-gated `AGENT_CONTRIBUTION`; not in `build_default_registry` at ES1. |
| D8 | **Stage A / no autonomy.** No block/quarantine/policy mutation; no autonomous action. |
| D9 | **No external side effects.** No outbound network, subprocess, Grok, PDF render, or done declaration. |
| D10 | **Tests are Stage 1 evidence.** Suite must prove D2–D9 before build close. |

---

## §5 Failure modes

| Failure | Expected behavior |
|---|---|
| Ledger-write creep | Any blackboard write/delete is forbidden |
| #46 conflation | Audit-packet assembly remains #46; #49 adds posture slot only |
| #47 conflation | Timeline projection remains #47 |
| #88 conflation | Mutation audit trail remains #88 ensemble |
| Policy overclaim | Present facts are not compliance/certification approval |
| Raw leakage | Policy hashes, operator labels, override text never in contribution |
| Cross-tenant attestation | Tenant-scoped inputs only |

---

## §6 Required tests (implementation slice — not run at draft)

1. `AuditTrailAgent` satisfies `Agent` protocol.
2. All anchors missing → `audit_trail_missing` + missing-component facts.
3. Policy hash attested present → `audit_trail_policy_hash_present`.
4. Override separation attested valid → `audit_trail_override_separation_present`.
5. Append-only chain attested present → `audit_trail_append_only_chain_present`.
6. Complete posture → `audit_trail_posture_complete` when all three anchors present.
7. Partial posture → specific missing facts without overclaiming complete.
8. Never calls blackboard write helpers, `assemble_audit_packet`, or package generator.
9. Tenant isolation on shared `case_id` across tenants.
10. Not in `build_default_registry()`; no network/subprocess; no raw leakage.

---

## §8 Pre-Build Gate Plan

1. Step 00: `python3 scripts/validate_agent_contract_block.py` on this contract (exit 0 required).
2. Pre-build gate via `audit_tools/complete_gate.py` (0 blocking target).
3. Adversarial focus: can wrapper write to blackboard or invoke audit-packet assembly via import side effect?
4. Manifest must list contract + template + Phase 1 + Cyber Insurance §14 excerpt — not implementation files.

Gate glob: `mmi_49_contract_gate_*.md`

---

## §11 Signature Block

**§11 — Audit Trail Agent Design Contract (Deep Dive)**

- [ ] I approve this contract as written.
- [ ] I authorize pre-build gate review when ready.
- [ ] On clean gate, I §11-sign and authorize Stage 1 wrapper build + focused tests only.

Confirmed: #49 projects stage-4 audit-trail posture only; it never writes ledger entries and never assembles audit packets.

> _(unsigned — Matt Nichol §11 pending)_

---

## BUILD CONDITIONS (post-§11)

At signing, Evidence Stage 1 — Synthetic only. §11 authorizes wrapper build path only when operator separately authorizes build lane (MMI-DEC pattern). No change to Canonical Evidence Ledger or audit-packet modules implied.

---

*End of contract.*
