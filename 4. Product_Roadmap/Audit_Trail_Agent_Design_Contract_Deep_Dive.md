# Audit Trail Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_49_AUDIT_TRAIL_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** §11 SIGNED 2026-06-25 by Matt Nichol (Gemini pre-build gate clean `audit_outputs/mmi_49_contract_gate_20260625T191119Z.md` 0 blocking / 0 warnings; MMI-DEC-199). Red Team tighten complete; Step 00 PASS 31/31. **SIGNED CONTRACT — BUILD NOT AUTHORIZED** until separate operator build-lane authorization (MMI-DEC). Signing locks D1–D10 for `AuditTrailAgent` (Layer 4 Evidence, ES1 Synthetic). Pre-build gate review authorized. Wrapper build + focused tests authorized **only after** clean pre-build gate and separate MMI-DEC build lane. BOR feedstock rank-1 (Estimator **27.00** · MMI-DEC-197). Authorizes **no** Canonical Evidence Ledger schema change, **no** evidence/workflow ledger append/update/delete (except registry-gated `AGENT_CONTRIBUTION`), **no** Blackboard reads at ES1, **no** audit-packet import/assembly, **no** mutation-engine `audit_trail.py` import, **no** default-registry registration, **no** production dispatch, **no** autonomous action, and **no** AUTH-5.

**Candidate:** #49 — Audit Trail

**Owner:** Matt Nichol

**Track:** BREADTH / Evidence-and-Outcome-Reporting stage 4 (Layer 4 Evidence scoreboard row)

**Lane:** Agent Design Contract (BOR feedstock rank 1 · MMI-DEC-197)

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** Built — `AuditTrailAgent` at `core/orchestrator/audit_trail_agent.py` (MMI-DEC-200); scoreboard `AWAITING_AUDIT`; completion gate pending

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `4. Product_Roadmap/Phase1_Infrastructure_Agent_Design_Contract.md` (Component 1 Canonical Evidence Ledger — append-only; **not** rewritten by #49)
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` (§14.3.4 Audit Trail stage — policy hash + tenant override separation)
- `4. Product_Roadmap/Evidence_Package_Agent_Design_Contract_Deep_Dive.md` (#46 sibling — package/audit-packet builder; #49 does not assemble packets)
- `4. Product_Roadmap/Case_Timeline_Agent_Design_Contract_Deep_Dive.md` (#47 sibling — timing anchors; distinct from audit-trail posture)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#49 row — ledger/packet split locked in contract)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/` (append-only Canonical Evidence Ledger — not read or written by #49 wrapper at ES1)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/evidence_package/audit_packet.py` (§10 coverage assembly — **not** invoked by #49 wrapper)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py`
- `VISION.md` (Stage A — analyze / recommend / evidence only)

**Build path:** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/audit_trail_agent.py` — **built MMI-DEC-200**

---

## Agent Design Contract block

**Boundary split (Open-Q1 / scoreboard reconciliation):** Phase 1 Component 1 (`core/blackboard/` append-only Canonical Evidence Ledger) and cyber-insurance `assemble_audit_packet` (#46 builder path) are **outside** this agent as mutable, read, or assembly surfaces at ES1. #49 is a caller-attestation-only Layer 4 Evidence wrapper that projects stage-4 audit-trail posture from explicit governed caller booleans — it never reads the ledger, never writes evidence/workflow ledger entries, never deletes records, never reads `audit_trail.json` or package directories, never assembles audit packets, and never imports or calls mutation-engine `core/mutation/audit_trail.py`.

## Agent Design Contract

Agent name: Audit Trail Agent (`AuditTrailAgent`)
Swarm inventory ID: #49 — Audit Trail
Canonical layer: 4 — Evidence
Canonical team / case type: Evidence / audit — stage-4 audit-trail posture for one governed case (policy hash + override separation + append-only chain)
Authority level: Level 3 — Specialist Agent
Stage posture: VISION Stage A — analyze / recommend / evidence only
Evidence Stage (current): Stage 1 — Synthetic (§11 signed 2026-06-25)

Role: For one caller-supplied audit-trail request, project which governed append-only evidence-chain anchors and policy/override audit posture the caller attests for the case and emit bounded Layer 4 audit-trail attestation facts
Boundary: Caller-attested anchors-in, audit-trail contribution-out. No Blackboard reads at ES1; no evidence/workflow ledger append/update/delete except registry-gated `AGENT_CONTRIBUTION` via `submit_agent_contribution`; no package/audit-packet assembly or import; no policy mutation; no Grok submission; no done declaration
Explicit non-authorities: No `assemble_audit_packet`, `write_audit_packet`, `generate_package_from_test_plan`, `audit_package()`, or any `core/evidence_package/` import; no `read_records`, `append_record`, or direct Blackboard workflow reads at ES1; no mutation-engine `core/mutation/audit_trail.py` import or API call; no evidence/workflow ledger append/update/delete except `submit_agent_contribution`; no policy/override authoring; no tenant override creation; no §14.3.4 pass/compliance/certification/insurer-approval claim; no buyer-facing audit release; no scoreboard/registry/governance writes; no AUTH-5; no autonomous operation

Inputs: One explicit request: `tenant_id`, `case_id`, optional explicit anchor booleans (`policy_hash_attested_present`, `override_separation_attested_valid`, `append_only_chain_attested_present` — omitted means unknown/not attested, `false` means caller attests absent/invalid), optional bounded `attested_record_types` (max 8 names from `RecordType` in `core/blackboard/models.py` — caller attested only; unknown names rejected). No Blackboard root/environment at ES1. Caller supplies case identity — agent does not discover from raw email, ledger paths, package artifacts, or external systems
Outputs: One `AgentContribution` (layer 4): closed audit-trail attestation facts + bounded `control_mapping` (`audit_trail:stage_a_synthetic` at ES1) + optional bounded Stage 1 `underwriter_note`. No verification/challenge fields at Stage 1
Evidence emitted: Closed facts only: `audit_trail_synthetic_attestation_only` (always at ES1), `audit_trail_missing`, `audit_trail_policy_hash_attested_present`, `audit_trail_policy_hash_attested_missing`, `audit_trail_override_separation_attested_present`, `audit_trail_override_separation_attested_missing`, `audit_trail_append_only_chain_attested_present`, `audit_trail_append_only_chain_attested_missing`, `audit_trail_attestation_all_anchors_present` (only when all three anchors explicitly attested present — not a §14.3.4 stage pass), optional bounded `audit_trail_record_type:<type>` (max 8, `RecordType` enum names from `core/blackboard/models.py` only). Never emit `audit_trail_posture_complete`, `audit_trail_policy_hash_present`, or other facts that imply on-disk hash match, `signed_by` resolution, or Cyber §14.3.4 pass. No policy hash values, operator names, override text, record payloads, package paths, or audit-packet file lists
Data minimization: No raw blackboard payloads, policy file contents, override requested_by/approved_by strings, signed_by paths, email bodies, tenant secrets, or audit-packet chunk bodies in the contribution. Optional `underwriter_note` is max 160 chars (shared `AgentContribution` cap), facts-only posture summary — no operator names, hash fragments, override text, or §14.3.4 pass language
Tenant isolation: Uses only caller-supplied `tenant_id` and `case_id`; tenant A attestation never verifies tenant B; no cross-tenant anchor reuse

Two-pass role: Pass 1 Evidence only. `challenge()` returns `None`
Decision Evidence Record contribution: `observed_facts`: closed audit-trail attestation facts only; `interpretations`: none; `assumptions`: caller attestation reflects the same synthetic case; `missing_evidence`: wrapper does not verify on-disk policy hash match, `signed_by` resolution, override registry state, append-only ledger contents, or Cyber §14.3.4 stage pass; `recommended_verification`: none emitted; `final_outcome_contribution`: synthetic attestation projection only — not evidence-package stage validation
Human review trigger: Any move beyond synthetic attestation, any real policy/override registry read, any package/audit-packet assembly, or any buyer-facing audit release requires separate Matt-signed authorization
Verification trigger: This agent does not initiate policy review or override approval; it reflects caller-attested posture only

Scoring / action posture: Facts-only Layer 4 evidence. No scoring lift, no risk floor, no recommended action, no compliance/insurance claim
Default rollout: Evidence Stage 1 — not in `build_default_registry`; explicit callers/tests only until signed promotion
Autonomous action: none

Promotion conditions: Per template §6.2 — §11 signed; wrapper tests green; pre-build + completion gates 0 blocking; >= 3 supervised audit-trail samples with expected attestation facts at ES1; **ES2 promotion additionally requires >= 1 supervised sample with ledger-derived (non-attested-only) verification** under separate real-data/ledger-read authorization; operator promotion MMI-DEC
Demotion conditions: Evidence/workflow ledger write/delete outside `submit_agent_contribution`, Blackboard read at ES1, `audit_trail.json`/package read, audit-packet assembly/import, mutation `audit_trail.py` import/call, §14.3.4 pass overclaim facts, policy/override authoring, cross-tenant leak, hash/operator/override-text leakage, or package-generator mutation — per template §6.3
Retest evidence: Permanent regression for every demotion trigger per template §6.5
Calibration requirement: ES1 synthetic fixtures only; Stage 2 requires supervised audit-trail samples and separate real-data authorization if applicable

Failure modes: Ledger-write creep; audit-packet conflation with #46; timeline conflation with #47; mutation audit_trail conflation with #88; policy-hash/override raw leakage; cross-tenant attestation mix — see §5
Required tests: Wrapper protocol, tri-state anchor mapping, attestation fact vocabulary, persistence via `submit_agent_contribution` only, no ledger/workflow writes, no Blackboard or package reads, no `assemble_audit_packet` or `evidence_package` import, tenant isolation, no registry default, no network/subprocess, no raw leakage, no §14.3.4 pass overclaim — see §6
Audit requirements: Step 00 `scripts/validate_agent_contract_block.py` PASS; pre-build gate via `audit_tools/complete_gate.py`; completion gate on implementation slice
Signed-spec dependencies: `Agent_Design_Contract_Template_Deep_Dive.md`, `Phase1_Infrastructure_Agent_Design_Contract.md`, `Cyber_Insurance_Evidence_Package_Deep_Dive.md`, `Evidence_Package_Agent_Design_Contract_Deep_Dive.md`, `VISION.md`, `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`
Build Authorization dependency: At §11 signature, Evidence Stage 1 only. No build until §11 + operator build authorization. Canonical Evidence Ledger and audit-packet assembly behavior remain immutable. Distinct from #46 `EvidencePackageAgent` and #47 `CaseTimelineAgent` — #49 owns the stage-4 audit-trail governed slot only

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-25 (draft placement · MMI-DEC-198):

| Placeholder | Resolved value | Repo evidence |
|---|---|---|
| Ledger surface | `core/blackboard/` append-only — Phase 1 §3 Component 1 | Phase 1 contract §11 signed; scoreboard #49 row |
| Packet surface | `core/evidence_package/audit_packet.py` — #46 builder/export only (`assemble_audit_packet`, `write_audit_packet`); #49 must not import | Evidence Package contract D3 builder/auditor split |
| ES2 ledger read | `core/production_state/` + Blackboard read paths — not authorized at ES1 | Deferred to ES2+ MMI-DEC; Red Team R15 |
| Mutation trail | `core/mutation/audit_trail.py` — #88 ensemble component | Not #49; scoreboard row #88 |
| Stage-4 test-plan anchor | Cyber Insurance §14.3.4 policy hash + override separation | Five-stage chain stage 4 |
| #47 relationship | `CaseTimelineAgent` GOVERNED_AGENT — timing anchors | MMI-DEC-168; does not retire #49 slot |
| #46 relationship | `EvidencePackageAgent` GOVERNED_AGENT — package assembly | Distinct builder path |

Repo-reconciliation placeholders: **resolved.** §11 signed MMI-DEC-199 2026-06-25; pre-build gate clean `mmi_49_contract_gate_20260625T191119Z.md` 0 blocking / 0 warnings.

---

## §0 Purpose

Unblock swarm #49 Audit Trail by signing the **ledger/packet split** that blocked Phase 1 Open-Q1. The scoreboard row names both `core/blackboard/` and `evidence_package/audit_packet.py`; a governed wrapper must not conflate Canonical Evidence Ledger infrastructure with cyber-insurance audit-packet assembly.

#49 is the caller-attestation-only Evidence agent for stage-4 audit-trail posture: it tells the swarm which governed anchors the caller attests for a case — not whether a package is complete, not whether timing SLAs hold, and not whether policy files on disk resolve.

This contract is governance + signed spec placement. §11 signed 2026-06-25 (MMI-DEC-199). It does not build runtime code or unlock AUTH-5 without separate build-lane authorization. **Scoreboard posture:** row #49 §11 signed; `DETECTOR_FUNCTION` retained for Estimator compatibility until wrapper build + `GOVERNED_AGENT` promotion (same pattern as #46/#47 pre-build).

---

## §1 Scope

### In scope
- Agent Design Contract block governing a future `AuditTrailAgent` wrapper (Layer 4 Evidence).
- Evidence Stage 1 (Synthetic) at signature.
- Caller-attested policy-hash presence, tenant-override separation validity, and append-only chain presence for one case.
- Optional bounded attested record-type facts using `RecordType` from `core/blackboard/models.py` (max 8).
- Explicit prohibition on Blackboard reads, evidence/workflow ledger writes (except `submit_agent_contribution`), audit-packet assembly/import, and package-generator calls.

### Out of scope
- Any change to Canonical Evidence Ledger schema, write routes, or Phase 1 Component 1 text.
- Any change to `assemble_audit_packet`, package generator stages, or #46 wrapper behavior.
- Reading Blackboard state, `audit_trail.json`, or package directories at ES1.
- Importing or calling `core/evidence_package/`, `generate_package_from_test_plan`, `audit_package()`, or mutation-engine `audit_trail.py` from the wrapper.
- Replacing or merging #46 Evidence Package or #47 Case Timeline — parallel governed slots.
- Registering in `build_default_registry` or production dispatch at ES1.
- Real-customer-data handling, Evidence Stage 2/3 promotion, or autonomous action.

---

## §2 Locked Design Decisions

| ID | Decision |
|---|---|
| D1 | **Identity.** Audit Trail is Layer 4 Evidence, Authority Level 3 Specialist, VISION Stage A, ES1 Synthetic at signing. `agent_id = audit_trail_001`. |
| D2 | **Ledger immutability (ES1).** Wrapper must not read Blackboard state, call `read_records`/`append_record`, or append/update/delete evidence/workflow ledger entries. Type-only imports from `core.blackboard` (`AgentContributionPayload`, `Environment`, `GovernanceError`) are allowed; no ledger I/O. Registry-gated `AGENT_CONTRIBUTION` persistence via `submit_agent_contribution` only (same carve-out as #47). Phase 1 append-only invariant stays infrastructure-only. |
| D3 | **Packet read-only.** Wrapper must not import `core/evidence_package/` (including `audit_packet.py`, `package_generator.py`), read `audit_trail.json` or package directories, or call `assemble_audit_packet`, `write_audit_packet`, `generate_package_from_test_plan`, or `audit_package()`. #46 owns assembly, disk export, and §14.3.4 artifact validation. |
| D4 | **Caller-attested anchors (tri-state).** Policy hash presence, override separation validity, and chain presence come only from explicit governed caller booleans supplied by a **trusted test harness or explicitly wired orchestrator caller** (same ES1 pattern as #47/#48). Omitted = unknown/not attested; `false` = caller attests absent/invalid; `true` = caller attests present/valid. No Blackboard, package, `core/production_state/`, or filesystem discovery at ES1. Ledger-derived verification deferred to ES2+ with separate Matt-signed MMI-DEC. |
| D5 | **Attestation semantics (not §14.3.4 pass).** Every ES1 contribution emits `audit_trail_synthetic_attestation_only`. All three anchors explicitly attested present → `audit_trail_attestation_all_anchors_present` plus component attested-present facts; any omitted or false → specific attested-missing facts and never `audit_trail_attestation_all_anchors_present`. Forbidden at ES1: `audit_trail_posture_complete` and any fact name implying hash match, `signed_by` resolution, or Cyber §14.3.4 stage pass. None authorize compliance, insurer approval, or buyer release. |
| D6 | **Audit-scoped facts + cross-slot rule.** Fact prefix `audit_trail_*` distinguishes #49 from #47 `case_timeline_*` and #46 package metadata. Coexistence on one DER is allowed; **no consumer may infer** Cyber §14.3.4 stage pass, package completeness, or timing SLA satisfaction from `#49` facts alone or from `#49` + `#47` facts combined without separate #46 package validation. |
| D7 | **Persistence + rollout.** Contributions persist only via registry-gated `submit_agent_contribution` → `AGENT_CONTRIBUTION`; not in `build_default_registry` at ES1. Direct `append_record` / workflow writes forbidden. |
| D8 | **Stage A / no autonomy.** No block/quarantine/policy mutation; no autonomous action. |
| D9 | **No external side effects.** No outbound network, subprocess, Grok, PDF render, or done declaration. |
| D10 | **Tests are Stage 1 evidence.** Suite must prove D2–D9 before build close, including persistence round-trip, import guards, tri-state anchors, and no §14.3.4 pass overclaim. |

---



## §3 Data surface (ES1)

- **Reads:** caller-supplied `tenant_id`, `case_id`, explicit tri-state anchor booleans, optional bounded `attested_record_types` (max 8, `RecordType` names from `core/blackboard/models.py`).
- **Does not read:** Blackboard JSONL, `read_records`, package directories, `audit_trail.json`, policy files on disk, override registry, `core/evidence_package/`, `core/mutation/audit_trail.py`, raw email, or external systems.
- **Persists:** `AgentContribution` only through `submit_agent_contribution` → `AGENT_CONTRIBUTION` (D2/D7 carve-out).
- **Emits:** `AgentContribution(agent_id="audit_trail_001", layer=4, observed_facts=<closed attestation facts>, control_mapping="audit_trail:stage_a_synthetic", underwriter_note=<optional bounded Stage 1 note>)`.
- **Does not emit:** facts implying §14.3.4 pass, hash match, `signed_by` resolution, or insurer/buyer approval.

## §5 Failure modes

| Failure | Expected behavior |
|---|---|
| Ledger-write creep | No direct evidence/workflow ledger write/delete; only registry-gated `submit_agent_contribution` allowed |
| #46 conflation | Audit-packet assembly remains #46; #49 adds posture slot only |
| #47 conflation | Timeline projection remains #47 |
| #88 conflation | Mutation audit trail remains #88 ensemble |
| Policy overclaim | Present facts are not compliance/certification approval |
| Raw leakage | Policy hashes, operator labels, override text never in contribution |
| Cross-tenant attestation | Tenant-scoped inputs only |
| ES1 overclaim | `audit_trail_synthetic_attestation_only` required; no §14.3.4 pass facts |
| Blackboard read creep | No `read_records` or ledger verification at ES1 |
| D2/D7 collapse | Only `submit_agent_contribution` may append; no direct ledger writes |
| Package disk write | `write_audit_packet` and package export remain #46; #49 never touches disk |
| Untrusted caller | ES1 callers must be test harness or explicitly wired orchestrator only |

---

## §6 Required tests (implementation slice — not run at draft)

1. `AuditTrailAgent` satisfies `Agent` protocol.
2. No anchor booleans supplied → `audit_trail_missing`, `audit_trail_synthetic_attestation_only`, and no `audit_trail_attestation_all_anchors_present`.
3. Explicit `false` on one anchor → corresponding `*_attested_missing` fact; never `audit_trail_attestation_all_anchors_present`.
4. All three anchors explicitly attested present → `audit_trail_attestation_all_anchors_present` + component `*_attested_present` facts + `audit_trail_synthetic_attestation_only`; never `audit_trail_posture_complete` or §14.3.4 pass-implying facts.
5. Partial attestation → specific missing facts without `audit_trail_attestation_all_anchors_present`.
6. `attested_record_types` capped at 8; only `RecordType` names from `core/blackboard/models.py` accepted; unknown names rejected or omitted without emitting `audit_trail_record_type:<name>`.
7. Never calls `read_records`, `append_record`, or reads Blackboard/package paths at ES1.
8. Never imports `core/evidence_package/` or `core/mutation/audit_trail.py`; never calls `assemble_audit_packet` or package generator.
9. Contribution persistence writes through `submit_agent_contribution` and round-trips through `AgentContributionPayload`.
10. Tenant isolation on shared `case_id` across tenants.
11. Not in `build_default_registry()`; no network/subprocess; no raw leakage.
12. Every contribution includes `audit_trail_synthetic_attestation_only`.
13. Never calls `write_audit_packet` or any `core.evidence_package.audit_packet` export helper.
14. Never calls `CanonicalEvidenceLedger.append`, `storage.append_record`, or `verdict_ledger.append` (mock/spy all three write paths).
15. Import guard: importing `audit_trail_agent` does not import `core.evidence_package` or `core.mutation.audit_trail` at module load.
16. `underwriter_note` when present respects 160-char cap and contains no forbidden substrings (hash hex, operator labels, §14.3.4 pass phrasing).

---

## §8 Pre-Build Gate Plan

1. Step 00: `python3 scripts/validate_agent_contract_block.py` on this contract (exit 0 required). **PASS 31/31**
2. Pre-build gate via `audit_tools/complete_gate.py` (0 blocking target). **CLEAN 2026-06-25** — `audit_outputs/mmi_49_contract_gate_20260625T191119Z.md` (Gemini, 0 blocking / 0 warnings; packet 94,781 bytes)
3. Adversarial focus: can wrapper read Blackboard/package paths at ES1; call `write_audit_packet` or `assemble_audit_packet`; import `core/evidence_package` or `core/mutation/audit_trail` at load time; or bypass `submit_agent_contribution` via `canonical_ledger.append` / `storage.append_record` / `verdict_ledger.append`?
4. Manifest: `audit_outputs/pending/mmi_49_contract_gate.manifest.json` — contract + Phase 1 + Cyber §14.3.4 excerpts only (lean slice; scoreboard/MMI log in separate commit)

Gate glob: `mmi_49_contract_gate_*.md`

---

## §11 Sign-off

**§11 SIGN-OFF — APPROVED BY MATT**

**Date:** 2026-06-25

**Authority:** Matt operator approval (MMI-DEC-199)

**Status after signature:** SIGNED CONTRACT — BUILD NOT AUTHORIZED

This signature locks D1–D10 for swarm #49 Audit Trail (`AuditTrailAgent`) as a Layer 4 Evidence Stage 1 (Synthetic) governed design contract.

**Explicitly not authorized by this signature:**

- Pre-build gate clean 2026-06-25 (`mmi_49_contract_gate_20260625T191119Z.md`, 0 blocking / 0 warnings). Implementation remains blocked until separate operator build-lane authorization.
- Lifecycle reconcile to build feedstock remains blocked until separate authorization.
- No runtime wrapper is built by this signature alone.
- No production dispatch, default-registry registration, or AUTH-5 unlock.

Signing authorizes **no** Blackboard read at ES1, **no** evidence/workflow ledger write/delete (except registry-gated `AGENT_CONTRIBUTION`), **no** `assemble_audit_packet` / `write_audit_packet` / package-generator import, **no** mutation-engine `audit_trail.py` import, **no** §14.3.4 pass claim, and **no** autonomous action.

> Matt Nichol — June 25th 2026

---

## BUILD CONDITIONS (post-§11)

At signing, Evidence Stage 1 — Synthetic only. §11 authorizes wrapper build path only when operator separately authorizes build lane (MMI-DEC pattern). No change to Canonical Evidence Ledger or audit-packet modules implied.

---

*End of contract.*
