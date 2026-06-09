# Evidence Package Agent Design Contract — Spec-First Deep Dive

**Status:** DRAFT 2026-06-08. Authored by the LIVE Build Map TRIAGE cycle after #44 Social Engineering merged into #39 Language Pressure and the duplicate/aggregate Layer 2 surfaces (#32 / #37) were rejected as clean wraps. This draft authorizes **no code**, **no package-generation behavior change**, **no buyer-facing package release**, **no real-customer-data handling**, **no Grok submission**, **no done declaration**, **no default-registry registration**, **no production dispatch**, **no Evidence Stage 2/3 promotion**, and **no autonomous action**. §11 signature is operator-only.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing package surfaces use **Mutant Monkey Inbox Shield** exactly where the signed cyber-insurance specs require it. No repo-wide rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Build_Map_Deep_Dive.md` (LIVE build authority; this is the next clean non-Detection breadth candidate after duplicate Layer 2 rows were routed out)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (governing template; Layer 4 Evidence promotion bar, Evidence Stage model, builder-auditor separation)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#46 Evidence Package; Build Sequencer candidate)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` (§13-signed package contract; scope, boundary statement, evidence record schema, done criteria)
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Implementation_Deep_Dive.md` (§11-signed implementation spec; generator boundaries, artifact layout, gates, audit-packet coverage rule)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/evidence_package/package_generator.py` (existing Pass 1 internal Markdown-bundle generator)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/evidence_package/audit_packet.py` (coverage-complete audit-packet assembly used by the generator)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/evidence_package/package_auditor.py` (separate auditor path; explicitly **not** called by this agent at Evidence Stage 1)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent` protocol, `AgentContribution`, `DecisionEvidenceRecord`)
- `VISION.md` (Stage A = analyze / recommend / evidence only; seven non-negotiables)

---

## Agent Design Contract block

**Boundary:** This contract governs the future Evidence Package **agent wrapper** around the existing Pass 1 package-generation path (`generate_package_from_test_plan`). It is additive governance under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend the cyber-insurance deep-dive, implementation spec, evidence schema, gate list, boundary statement, done criteria, redaction rules, audit-packet coverage rule, package-render behavior, package-auditor behavior, or any runtime detection/scoring behavior. Those remain governed by their prior signed specs and are immutable here.

| Field | Value |
|---|---|
| Agent name | Evidence Package Agent (`EvidencePackageAgent`) |
| Swarm inventory ID | #46 — Evidence Package |
| Canonical layer | 4 — Evidence |
| Canonical team / case type | Evidence / audit; internal package assembly over existing evidence artifacts |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed. Validated on synthetic/test-plan fixtures only; intentionally NOT registered in `build_default_registry` / production dispatch. Advancement to Stage 2 requires template §6.2 conditions and a Matt-signed promotion record. |
| Role | Assemble an internal evidence package from already-existing, synthetic/test-plan source artifacts using the signed Pass 1 generator path, then contribute minimal Layer 4 package metadata to the case evidence record. |
| Boundary | The package assembler is not the auditor. The agent must not audit its own output, submit package content to Grok, emit a done declaration, claim underwriting/compliance/security outcomes, publish buyer-facing packages, handle real customer email/package content, alter runtime detectors/scoring, or decide whether a package is complete beyond the existing generator's `is_done=False` Pass 1 result. |
| Explicit non-authorities | No autonomous action; no buyer release; no client-facing claim; no compliance/certification/insurer-approval/premium/coverage claim; no real-customer-data handling; no Grok/xAI/external-model call; no `audit_package()` invocation; no `render_package_pdf()` invocation; no `done_declaration.json` emission; no gate-list change; no boundary-statement edit; no redaction/forbidden-language relaxation; no package-generator behavior change; no runtime detection/scoring/policy write; no default-registry registration; no production dispatch at Evidence Stage 1. |
| Inputs | Stage 1: one governed synthetic/test-plan source directory carrying the five signed package source artifacts (`detection.json`, `verification.json`, `evidence.json`, `audit_trail.json`, `outcome_documentation.md`), plus `tenant_id`, output root, trigger, and timestamp pins supplied by an explicit test/caller. No Blackboard `EMAIL_INBOUND` body and no real tenant data. |
| Outputs | One `AgentContribution` (layer 4): `observed_facts` = safe package assembly facts; `control_mapping` = package/control-surface identifier; `underwriter_note` = bounded safe note that the package is internal Stage 1 synthetic evidence only. The wrapper may also produce the existing internal package directory via `generate_package_from_test_plan` when explicitly called in tests. |
| Evidence emitted | Package metadata only: package id, package version, gates-passed status, audit-packet coverage-complete flag, Markdown-bundle-present flag, `is_done=False`, and record-count facts. No package contents, raw source records, raw email bodies, tenant secrets, vendor names, or package render text enter the contribution. |
| Data minimization | Contribution emits identifiers and boolean/status facts only. It does not emit raw package JSON, Markdown, source artifact content, email body, vendor/customer names, policy secrets, signed-by values, file contents, file hashes except a package-level `sha256:` anchor if needed, or rendered package prose. |
| Tenant isolation | Stage 1 uses synthetic/test tenant identifiers only. Any future real-tenant package generation is outside this contract and requires separate signed promotion/real-data authorization. Output paths are explicit per run; no cross-tenant lookup occurs. |
| Two-pass role | Evidence assembly only. `challenge()` returns `None`; auditing/review is a separate Layer 6 / package-auditor concern. |
| Decision Evidence Record contribution | `observed_facts`: safe package assembly facts; `interpretations`: none; `assumptions`: supplied source artifacts are synthetic/test-plan inputs; `missing_evidence`: no Grok package audit, no PDF render, no done declaration, no buyer release, no real-data proof; `recommended_verification`: package must be reviewed by the separate signed audit path before any done/release claim; `final_outcome_contribution`: internal evidence-package assembly facts only; `retest_or_learning_record`: every package-generation failure/demotion trigger becomes a permanent regression test per template §6.5. |
| Human review trigger | Any move beyond synthetic/internal package assembly, any real-customer package content, any buyer-facing delivery, any Grok submission of package content, any done declaration, or any Evidence Stage promotion requires Matt's separate signed authorization. |
| Verification trigger | The separate package-auditor / Final Review path must review package outputs before any done/release claim. This agent cannot self-verify. |
| Scoring / action posture | Facts-only evidence contribution. No scoring lift, no risk score, no recommended email action, no underwriting decision, no compliance state. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers and tests until a later signed promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; Stage A router guard rejects autonomy. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires: clean test suite, zero open test failures, Matt review of >= 3 real/supervised package-generation samples or equivalent supervised package runs, `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. Any real-data handling also requires the separate real-data/depth authorization gate. |
| Demotion conditions | Per template §6.3. Automatic: regression failure, audit-packet coverage failure, boundary-statement drift, forbidden-language leak, redaction failure, package-auditor contradiction, done-declaration leakage, external-model call at Stage 1, or out-of-layer field write. Matt-signed: auditor pattern flag, buyer-facing overclaim risk, or signed Challenge contradiction pattern. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent regression test. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires supervised package samples and the real-data/depth gate if any real customer artifacts are involved. Stage 3 requires Drift Watch / package freshness controls active. |
| Failure modes | See §5. |
| Required tests | See §6 — wrapper tests must prove package assembly over synthetic fixtures, Layer 4 contribution boundaries, builder/auditor separation, no Grok/PDF/done declaration, persistence/DER path, guardrails, no default registry, no buyer/real-data leakage, and purity/no runtime detection mutation. |
| Audit requirements | Any contract signature, implementation, or revision remains subject to `complete_gate.py`. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `Cyber_Insurance_Evidence_Package_Deep_Dive.md`, `Cyber_Insurance_Evidence_Package_Implementation_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, and canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At §11 signature, this agent is at **Evidence Stage 1** only. No build authorization is granted for Evidence Stage 2/3 registration, real-data package generation, buyer-facing package delivery, Grok package audit, PDF render, done declaration, default registry, or production dispatch until the promotion conditions in §6.2 are satisfied and a separate promotion record / real-data authorization is signed. Existing generator behavior and package specs are unchanged by this contract. |

---

## §0 Purpose

Promote swarm agent #46 Evidence Package from an existing package-assembly implementation into a governed-agent path by giving the future wrapper a signed Agent Design Contract. The wrapper will be the first Layer 4 Evidence agent on the swarm scoreboard: it assembles evidence from already-existing artifacts and contributes bounded metadata to the evidence record.

This contract is the governance step. It does not build runtime code until §11 signature / Build Authorization.

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing a future `EvidencePackageAgent` wrapper as a Layer 4 Evidence agent.
- Evidence Stage 1 (Synthetic) declaration at signature.
- Explicit preservation of existing `generate_package_from_test_plan` behavior.
- Explicit builder/auditor separation: package generation is allowed in Stage 1 synthetic tests; package auditing, Grok submission, PDF rendering, and done declaration remain out of scope.
- Facts-only Layer 4 metadata contribution from generated package results.

### Out of scope
- Any change to `package_generator.py`, `audit_packet.py`, `package_auditor.py`, `pdf_renderer.py`, `done_declaration.py`, package gates, redaction rules, forbidden-language rules, vocabulary translations, artifact layout, package schema, boundary statement, or signed cyber-insurance specs.
- Calling `audit_package()`, `make_xai_client()`, `render_package_pdf()`, or emitting `done_declaration.json`.
- Buyer-facing package release, MSP delivery, underwriter delivery, pricing, claims, or copy.
- Real-customer data / real tenant package generation.
- Runtime detector/scoring/policy changes.
- Registering the agent in `build_default_registry` or production dispatch.
- Any autonomous action, buyer-facing claim, or Stage B/C autonomy.
- Evidence Stage 2/3 promotion.

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

- **D1 — Identity.** Evidence Package is a Layer 4 Evidence agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = evidence_package_001`.
- **D2 — Generator immutability.** This contract changes no package-generation behavior, gate, schema, render, redaction rule, boundary statement, audit-packet coverage rule, done criterion, or runtime detector/scoring behavior. It governs the wrapper only.
- **D3 — Builder/auditor separation.** The agent assembles packages; it never audits its own package, calls `audit_package()`, submits to Grok, or marks the package done. Audit/review remains a separate signed path.
- **D4 — Stage 1 synthetic-only input surface.** The agent may only use synthetic/test-plan package source artifacts at Evidence Stage 1. Real package content requires separate promotion/real-data authorization.
- **D5 — Facts-only Layer 4 contribution.** The agent emits safe package metadata only: package id/version, gate status, coverage status, bundle presence, `is_done=False`, and bounded control mapping / underwriter note. It emits no package contents or buyer claims.
- **D6 — No buyer surface / no claims.** Stage 1 produces internal test evidence only. No buyer package release, compliance/certification/insurer-approval/premium/coverage claim, pricing, or external copy.
- **D7 — Persistence + rollout.** Contributions persist via the registry-gated `AGENT_CONTRIBUTION` route if a wrapper build is signed. The agent is NOT in `build_default_registry`; it is wired only by explicit callers until a signed promotion.
- **D8 — Stage A / no autonomy.** No autonomous action; no final approval; no package done declaration; no external call; the agent authors no disposition.
- **D9 — Evidence Stage governance.** Evidence Stage 1 at signing; promotion and demotion follow template §6.2 / §6.3; progressive hardening §6.5 applies.
- **D10 — Tests are the Stage 1 evidence.** The wrapper test suite must include synthetic package generation, Layer 4 contribution schema, builder/auditor separation, no Grok/PDF/done declaration, no default registry, no buyer/real-data leakage, and purity/no runtime detector mutation before the build can close.

---

## §3 Data surface and output schema

- **Reads:** synthetic/test-plan package source files only: `detection.json`, `verification.json`, `evidence.json`, `audit_trail.json`, and `outcome_documentation.md`.
- **Underlying generator:** `generate_package_from_test_plan(source_dir, output_root, tenant_id, trigger, now, ...)` returns `EvidencePackageResult`.
- **Emits:** `AgentContribution(agent_id="evidence_package_001", layer=4, observed_facts=<safe package facts>, control_mapping=<package/control identifier>, underwriter_note=<bounded Stage 1 note>)`.
- **Does not emit:** raw source artifact content, package JSON/Markdown, tenant secrets, real customer data, vendor/customer names, package prose, package gate findings with raw values, Grok output, PDF bytes, done declaration, pricing, compliance/insurance claims, or any email decision.

---

## §4 Evidence Stage declaration

- **Current Evidence Stage at signature: 1 — Synthetic.** Only synthetic/test-plan package validation will exist at initial build.
- **To reach Stage 2 (Supervised):** all template §6.2 Stage 1->2 conditions, including Matt review of >= 3 supervised package samples or equivalent supervised package-generation runs, a signed `PROMOTION` entry, and real-data/depth authorization if real customer artifacts are involved.
- **To reach Stage 3 (Production):** template §6.2 Stage 2->3 conditions, including Drift Watch / package freshness controls active. Reaching Stage 3 grants no autonomous action.
- **Demotion:** template §6.3 triggers apply.

---

## §5 Failure modes

- **Builder/auditor collapse** — the package assembler audits or approves its own output. Mitigation: D3; `audit_package()` and Grok submission are explicitly out of scope.
- **Done-state leakage** — Stage 1 emits `done_declaration.json` or claims package completion. Mitigation: D8/D10; Pass 1 `is_done=False` is expected at Stage 1.
- **Buyer-facing overclaim** — generated evidence is described as compliance, certification, insurer approval, premium reduction, coverage support guarantee, or release-ready. Mitigation: D6 and signed cyber-insurance boundary statement.
- **Real-data creep** — Stage 1 processes real customer package content or real tenant evidence. Mitigation: D4 synthetic-only input surface; real-data gate required.
- **Audit-packet coverage gap** — generated package touches files that are not represented in the audit packet. Mitigation: signed implementation spec coverage rule; tests assert coverage-complete.
- **Package-content leakage into DER** — raw package JSON/Markdown, source artifacts, vendor names, or tenant secrets enter the `AgentContribution`. Mitigation: D5 metadata-only contribution.
- **Runtime mutation** — package assembly changes detectors, scoring, policy, or signed specs. Mitigation: D2; wrapper imports generator read-only and does not touch runtime detector modules.
- **External-model call at Stage 1** — wrapper submits package content to Grok/xAI or another external model. Mitigation: D3/D8; package audit remains separately invoked and synthetic/test-only even when authorized.
- **PDF/render expansion** — wrapper calls PDF render or broadens package surfaces. Mitigation: Stage 1 wrapper stays Pass 1 Markdown-bundle/internal metadata only.
- **Cross-tenant leak** — output path or source artifacts mix tenant/package data. Mitigation: explicit source/output paths and synthetic tenant fixtures in Stage 1; future real tenant runs require separate authorization.
- **Stage creep** — default registry or production dispatch while at Evidence Stage 1. Mitigation: explicit default-registry exclusion.

---

## §6 Required tests

The implementation slice must add focused tests proving:

1. `EvidencePackageAgent` satisfies the shared `Agent` protocol if implemented as a wrapper agent.
2. A synthetic five-record source directory generates an internal package through the existing `generate_package_from_test_plan` path.
3. Generated package facts produce a Layer 4 `AgentContribution` with expected safe `observed_facts`, `control_mapping`, and bounded `underwriter_note`.
4. Contribution persistence writes through `submit_agent_contribution` and round-trips through `AgentContributionPayload`.
5. `challenge()` returns `None`.
6. Missing or invalid package source artifacts fail closed and do not produce a misleading contribution.
7. The wrapper does not call `audit_package()`, `make_xai_client()`, `render_package_pdf()`, or emit `done_declaration.json`.
8. The generated package result remains `is_done=False` at Stage 1 and `done_declaration_path is None`.
9. The wrapper does not register in `build_default_registry()`.
10. Unauthorized registry writes are rejected.
11. `digest_package_request` / equivalent input digest is deterministic.
12. Contributions do not contain raw package JSON, rendered Markdown, raw source artifact content, vendor/customer names, tenant secrets, signed-by values, forbidden package claims, or file contents.
13. The wrapper performs no network/subprocess/external-model call during package assembly.
14. The wrapper does not import or mutate runtime detector/scoring modules.
15. Audit-packet coverage-complete status from the generator is surfaced as metadata only, not treated as a done declaration.
16. Builder/auditor separation is enforced by a test that monkeypatches the package-auditor path to fail if invoked.

---

## §7 Audit requirements

This contract draft and any implementation must be gated through `complete_gate.py`. The implementation manifest must include this contract, the Agent Design Contract Template, the cyber-insurance deep-dive, the cyber-insurance implementation spec, the package generator, the package auditor boundary file, the wrapper file, and the focused test file.

---

## §10 Open Questions (operator-only)

No design fork is open in this draft. §11 signature confirms D1-D10 and authorizes the Evidence Stage 1 synthetic wrapper build only.

---

## §11 Sign-off

PENDING. Operator-authored signature required before any runtime build. Signing will lock D1-D10 and authorize the Evidence Stage 1 (Synthetic) `EvidencePackageAgent` wrapper build + focused tests only; no package-generation behavior change, no buyer-facing package release, no real-customer-data handling, no Grok submission, no PDF render, no done declaration, no default-registry registration, no production dispatch, no Evidence Stage 2/3 promotion, no runtime detector/scoring change, no self-audit, no autonomy.

> [Matt Nichol — Evidence Package Agent — date]
