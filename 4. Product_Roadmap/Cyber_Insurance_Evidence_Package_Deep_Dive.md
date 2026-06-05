# Cyber Insurance Evidence Package — Deep Dive

**Status:** §13 SIGNED 2026-06-03 by Matt Nichol (operating entity name TBD pending project rename; the "zebra-comit" handle is retracted). This signature is recorded in the working tree and is uncommitted; committing it fires the pre-ship / completion gate per `AGENTS.md` §5, which must pass or be explicitly operator-overridden with a recorded reason before commit. Prior state was DRAFT (pre-§11). §12 Q1-Q11 resolved by operator on 2026-05-26 through 2026-05-30 (pending §13 lock as D1-D2e, D3-D3a, D4, D5, D6, D7, D8, D9, D10, D11). §13 sign-off state at this revision: precondition 1 (all §12 questions resolved) satisfied; precondition 2 (v1 test plan defined and runnable from the spec alone) satisfied by §14 added 2026-05-30; precondition 3 (operator-set Q10 count threshold — 2 of 3 relevant MSP conversations meeting the D10 per-MSP definition — met in actual cheaper-proof MSP discovery OR explicitly overridden by Matt with recorded reason) satisfied by Matt's signed operator override in `PROJECT_ACTIVITY_LOG.md` on 2026-06-03. D10 is **overridden, not met**; do not describe the override as D10 completion, cheaper-proof validation, or market proof. §11 criterion 15 (v1 test plan **executed** end to end) remains open until the §14 plan has been run and the run-level pass / fail recorded in the project's normal test-evidence surfaces.

**Authority model:** Matt's vision is the product authority. This document is a Technical Verification Layer artifact. It defines technical risks, failure modes, evidence schemas, audit requirements, and machine-readable "done" criteria. It does not score, approve, or judge the product direction.

**Scope reminder:** This package is an *organizational and presentation* layer over evidence NorthStar Inbox Shield already produces. It does not introduce new detection capability, new external claims, or new scope. It assembles existing audit artifacts into a buyer-readable bundle for the email-fraud / inbox-layer MDR control surface only.

**Direction lock:** This package sits inside NorthStar's Evidence and Outcome Reporting lane: Detection → Verification → Evidence → Audit Trail → Outcome Documentation. The v1 evidence-record set in §6 / §12.Q7 maps one record to each stage. Any spec change that breaks this five-stage mapping requires a new operator decision.

**Protected sentence (Cyber Insurance lane invariant):** *"NorthStar helps identify, review, verify, and document high-risk financial exposure before action is taken."* This sentence is the operator-authored summary line for this package's value proposition. The exact wording is preserved; paraphrases, expansions, or softer marketing-style rewrites are drift incidents at sign-off time.

**Selected by:** Operator selection 2026-05-25 evening. Matt's selection is the authority. Cross-reference: `think_sheet.md` row "Cyber Insurance Evidence Package" (2026-05-25); any score recorded there is historical metadata only, not decision authority. The active guidance is "promote with cheaper-proof-first guidance."

**Spec drafting is operator-authorized and originally gated on cheaper-proof MSP discovery validation** per the think_sheet stress test verdict. On 2026-06-03, Matt signed an operator override removing the D10 cheaper-proof gate as the active blocker on the §13 readiness path. This override does not claim cheaper-proof validation and does not unblock implementation by itself; it only allows §13 sign-off review to proceed on an explicitly recorded operator decision supported by direction-confirming signal.

---

## §1 Purpose

NorthStar Inbox Shield produces a substantial body of audit evidence as a natural byproduct of normal Stage A operation — append-only Blackboard records, signed policy state, tenant override audit events, scoring explanations, daily digest artifacts, sample monthly reports, lift-only invariant test results, kill-switch wiring evidence, and signed §11 specifications as architecture documentation. Today this evidence exists but is scattered across the repo in shapes calibrated for engineering and operator use, not for the SMB cyber-insurance buyer chain.

The Cyber Insurance Evidence Package assembles a defined subset of this existing material into a buyer-readable bundle the MSP can present to support an SMB client's cyber-insurance underwriting conversation for the email-fraud / inbox-layer MDR surface.

The purpose is **packaging and presentation**, not new claims. Every evidence item in the package traces to an artifact NorthStar already produces under the existing signed architecture. The package does not invent new control claims, does not assert capabilities outside the email-fraud / inbox-layer MDR boundary, and does not promise underwriting approval or premium reduction.

---

## §2 Scope / Non-Scope

### In scope

- Email fraud evidence (vendor invoice fraud, executive impersonation, payment redirect, urgent-payment social engineering, callback / TOAD body-language patterns when that detector ships)
- Inbox-layer MDR evidence (deterministic detector overlays, lift-only invariant evidence, scoring explanations, daily digest action queues)
- Audit logs from the append-only Blackboard
- Scoring explanations (internal 0–100 score and client-facing 5-axis rubric where applicable)
- Signed §11 specifications as architecture-documentation references
- Tenant override audit events with provenance (`requested_by` / `approved_by` separation)
- Tenant isolation test results
- Cross-tenant rejection evidence
- Kill-switch wiring evidence
- Lift-only invariant test results
- Decision Auditor outputs and independent audit summaries
- Effective parameter reports per tenant
- Sample monthly report artifacts
- Source artifact mapping (every claim in the package links to a source file)
- Redaction requirements
- Machine-readable evidence record format ("the package is a directory of structured records, not a stack of PDFs")
- Scope boundary statement (printed in the package itself, not just in this spec)

### Non-scope

The package explicitly does **not** cover:

- Multi-Factor Authentication (MFA) — MSP / identity vendor responsibility
- Endpoint Detection and Response (EDR) — MSP / EDR vendor responsibility
- Backups and disaster recovery — MSP / backup vendor responsibility
- Incident Response (IR) plans — MSP / SMB responsibility
- Patch management — MSP / RMM vendor responsibility
- SOC 2 attestation — out of scope; NorthStar is not SOC 2 certified
- ISO 27001 certification — out of scope; NorthStar is not ISO 27001 certified
- Full cyber-insurance compliance for any carrier — out of scope
- Any guarantee of underwriting approval
- Any guarantee or implication of premium reduction
- Any claim of "compliance," "fully secure," "bulletproof," "guaranteed," or equivalent absolute language

### Required boundary statement (printed in the generated package)

> *"This package covers Mutant Monkey Inbox Shield's email-fraud and inbox-layer MDR control surface only. Other controls in your security stack — including MFA, EDR, backups, incident response plans, and patch management — are not in this package's scope and must be evidenced by your MSP or other vendors. This package does not guarantee underwriting approval or premium reduction; it provides auditable evidence of one control surface for your underwriter's review."*

This statement is part of the contract. Removing it, softening it, or replacing it with marketing copy is a drift incident.

**Buyer-facing brand note (§13 revision 2026-06-05):** the product is named **Mutant Monkey Inbox Shield** on all buyer-facing surfaces (the rebrand Option B external/commercial brand; see `_Rebrand_to_Mutant_Monkey_Security_Consequence_Matrix.md`). "NorthStar Inbox Shield" remains the **internal codename** used throughout the runtime code and the engineering-facing prose in this and other specs; the deep rename of internal code/specs stays deferred per Option B. Only buyer-facing strings (this boundary statement, the rendered package, the MSP retainer summary) carry the external brand in v1.

---

## §3 Buyer Chain: MSP → SMB → Underwriter

The package flows through three parties with distinct roles and distinct constraints. Confusing them is one of the failure modes in §5.

### MSP (primary buyer, package consumer)

- Pays NorthStar. Owns the customer relationship.
- Assembles evidence for the SMB client's underwriting application — typically pairing NorthStar's email-fraud / inbox-layer MDR package with their own MFA, EDR, backup, and IR evidence from other vendors.
- Reads the package to understand what they are presenting and what they are *not* presenting.
- Needs the scope boundary printed clearly so they can position the package honestly to the SMB and to the underwriter.

### SMB (end client, package submitter)

- The party with the active cyber-insurance application or renewal.
- Receives the package from the MSP, typically as part of a larger evidence bundle.
- Submits the bundle with the underwriting application.
- Generally does not read the package in technical detail; relies on the MSP to vouch.

### Underwriter (audience, not buyer)

- Reviews the package as part of the SMB's application.
- Real underwriters in 2026 may either (a) read the package in depth as differentiated evidence, or (b) check it as a yes/no-box for "email security control evidence present." The package format must survive both reads.
- Vocabulary boundary: the package speaks in plain English. Cyber-insurance jargon ("attestation," "control efficacy," "regulatory mapping," "compensating control") gets a translation pass before any client-facing surface ships. See §5 failure mode iv.

### Boundary implications

- The package is structured for the underwriter's worst-case read (yes/no-box) while preserving depth for the best-case read (deep technical review). Both reads must reach the same correct conclusion about what the package covers and does not cover.
- The MSP is the contractual relationship; the underwriter is the audience. The package cannot pretend to be a direct underwriter deliverable from NorthStar.

---

## §4 Evidence Sources

Every evidence record in the package traces to an existing NorthStar artifact. The package generates no new evidence; it organizes what already exists.

| Source artifact | Path / surface | Claim category supported |
|---|---|---|
| Inbox Shield sample monthly report | `1. Business_Operations/Client_Documents/Inbox_Shield_Sample_Monthly_Report.md` | Operational evidence: detection volume, top findings, recommended actions, MSP-grade reporting cadence |
| Effective parameter report (per-tenant) | `tenant_override_operator report --format markdown` output, e.g. `Generated/Acme_Effective_Parameter_Report_Demo.md` | Tenant-specific policy tuning with signed provenance; demonstrates per-client calibration |
| Daily digest demo | `Generated/Inbox_Shield_Daily_Digest_Demo.md` (from `scripts/inbox_shield_daily_digest_demo.py`) | Daily operational artifact; action queue rendering; advisory-boundary clarity (Stage A: `block` is advisory, not mailbox-level quarantine) |
| MSP discovery evidence package | `Client_Documents/MSP_Discovery_Evidence_Package.md` | Architecture overview, eval evidence, safe-claim boundary, non-negotiables, free pilot terms |
| Blackboard append-only records | `core/blackboard/` (runtime) | Audit trail: every email inbound, every analysis, every audit verdict, every override event, every report — timestamped and immutable |
| Signed policy state | `core/production_state/` (runtime) | Cryptographic attribution of policy versions and tenant override events; `requested_by` / `approved_by` separation |
| Signed §11 specifications | `4. Product_Roadmap/*.md` (§11-locked specs) | Architecture documentation under signed change control; demonstrates that detector behavior matches a signed contract |
| Lift-only invariant test results | `tests/` (e.g. ransomware precursor, FSL, callback phishing) | Detectors cannot lower risk; mathematically locked direction-of-effect |
| Tenant isolation tests | `tests/` (cross-tenant rejection, per-tenant override scoping) | Customer data never crosses tenants; signed policy updates can cross, customer data cannot (Guardrail 11) |
| Kill switch wiring evidence | `tests/` + Guardrail 12 documentation | Operator kill switch overrides the swarm at all 9 loop entry points |
| Decision Auditor outputs | `audit_tools/decision_audit_runner.py` artifacts | Independent governance review surface |
| Grok audit outputs | `audit_outputs/*.md` | External-model negative-feedback audit output (see §10) |
| Eval reports (when present) | `eval_reports/` | Per-case scoring evidence on labeled fraud cases |

### Coverage rule

If the package references an artifact, that artifact must exist at the cited path at package-generation time. A missing source artifact is a hard fail. This is enforced by §11 Done Criteria, not by hope.

---

## §5 Failure Modes

Enumerated honestly. These define what the gate tests and audit requirements protect against.

### i. Overclaiming

The package implies controls or coverage NorthStar does not provide. Examples: "fully compliant," "guaranteed protection," "covers all email threats," "SOC 2 ready." Underwriter or MSP reads the claim, audits later finds the gap, NorthStar trust erodes.

**Mitigation:** §6 evidence record schema requires every claim to have a `claim_category` and a `source_artifact_path`. Claims without a source are blocked. The boundary statement (§2) is mandatory and unedited. A forbidden-language list is enforced at package generation (see §9 redaction / §11 done criteria).

### ii. Stale evidence

The package references artifacts that no longer exist, were renamed, or describe a system state that has since changed. Examples: a sample monthly report quoting a test count from three months ago when the suite is now 50 tests larger; a signed-spec reference to a spec that was superseded.

**Mitigation:** §6 evidence records include `last_verified_at`, `content_hash`, and signed provenance where applicable. Package generation applies the freshness policy in §6.1: mutable operational authority and tenant-scoped enforcement evidence has a 30-day threshold; reproducible / slower-decay evidence has a 90-day threshold; structurally signed immutable evidence is freshness-exempt only when its `signed_by.signature_value` resolves to a valid signed artifact. A stale record makes the `stale_evidence` gate fail for package completion. A broken `source_artifact_path` is always a hard fail.

### iii. Missing provenance

Evidence is shown without traceable origin. Examples: a per-tenant override is described in the package but the underlying audit event isn't linked; a policy version is named but the signature provenance isn't shown.

**Mitigation:** Every evidence record requires `source_artifact_path` and, where applicable, `signed_by`. Records without provenance fail validation.

### iv. Vocabulary leak

Cyber-insurance jargon — "attestation," "control efficacy," "regulatory mapping," "compensating control," "control attestation framework" — drifts into NorthStar's voice and into outreach materials. The result reads as carrier-bureaucracy, not as NorthStar. (Cross-reference: think_sheet 2026-05-25 entry, failure mode iv, and the deleted `Human_Written_Communication_Policy.md` vocabulary-leak guardrail.)

**Mitigation:** A vocabulary-translation rule list is part of the package contract. Cyber-insurance terms get translated to plain English before any client-facing surface ships. The translation rule list is itself an evidence record under change control. Vocabulary boundary is scoped strictly to this one buyer-facing surface — it does not leak into `REVENUE_MAP.md`, MSP discovery scripts, `PROGRESS.md`, or other internal docs.

### v. Tenant-data leakage

The package, generated for one MSP / SMB, contains data belonging to another tenant. Catastrophic — violates Guardrail 11.

**Mitigation:** Every evidence record carries `tenant_id` (or `null` for cross-tenant evidence like aggregate test counts). Generation logic filters strictly by tenant; cross-tenant aggregate evidence is allowed only when explicitly marked and provably non-identifying. A redaction sweep runs before any client-bound artifact (§9). Tenant isolation tests in the existing test suite are themselves part of the evidence the package references.

### vi. Unsigned policy artifacts

The package references a policy state, tenant override, or detector configuration that was not signed under the existing signed-promotion pipeline. Looks like evidence, isn't.

**Mitigation:** Every policy / override evidence record requires a signature reference. Unsigned policy state is excluded by the generator and flagged as a drift incident if encountered (§8).

### vii. Audit gap (coverage gap)

A file actually touched during package generation is not present in the audit packet that Grok reviews. The audit silently approves package generation without seeing the parts that changed. (This is the exact failure mode caught by the 2026-05-23/24 weekend Pass-1 wiring bug; cross-reference last weekend's drift discussion.)

**Mitigation:** §10 Grok audit requirements mandate that the audit packet includes every file touched during package generation, with no AI-side scoping. Mismatch between touched-files and audit-packet contents is a hard fail.

### viii. Decoration risk

The package looks comprehensive but underwriters never read it because they only check yes/no boxes. Evidence depth turns out to be illusory differentiation. (think_sheet failure mode i.)

**Mitigation:** This is a *go-to-market* failure mode, not a generation-layer one. Mitigation lives in the cheaper-proof discovery process gating spec implementation: MSP discovery calls must produce go/no-go signal before engineering proceeds. The spec itself cannot mitigate; it can only flag the dependency.

### ix. Email-narrow risk

Underwriting questions cover MFA, EDR, backups, IR plans, etc. Most are not NorthStar's surface. Package looks insufficient on its own and MSP has to assemble the rest from other vendors. NorthStar gets blamed for the gaps. (think_sheet failure mode ii.)

**Mitigation:** The boundary statement (§2) is mandatory and printed prominently in the package itself. The package positions as "the email-fraud module of a broader compliance package the MSP is assembling" — not as a standalone compliance solution. MSPs are responsible for assembling the rest. The package's structure makes this explicit.

### x. Per-carrier fragmentation

Each carrier asks slightly different questions. The package needs per-carrier customization that NorthStar cannot scale. (think_sheet failure mode iii.)

**Mitigation:** Single carrier-agnostic format with an explicit "see your carrier's specific questions for additional details" disclaimer. NorthStar refuses to maintain per-carrier variants. Cross-reference §12 Q4 on per-carrier variants vs. single carrier-agnostic format.

---

## §6 Evidence Record Schema

The package is a directory of structured evidence records plus a generated human-readable surface. The structured records are the source of truth; the human-readable surface is a render. Delivery surfaces for v1 are defined in §6.2.

```yaml
evidence_id: "evd-2026-05-26-001"             # stable identifier; opaque to clients
claim: "Tenant policy changes are signed and auditable with separated requester / approver."
claim_category: "policy_change_control"        # closed enum, see below
source_artifact_path: "1. Business_Operations/Client_Documents/Generated/Acme_Effective_Parameter_Report_Demo.md"
source_artifact_type: "tenant_effective_parameter_report"  # closed enum
verification_command: "python -m scripts.acme_effective_parameter_report_demo --verify"
last_verified_at: "2026-05-26T20:43:11Z"
result: "pass"                                 # pass | fail | stale
scope_limitations: "Email-fraud and inbox-layer MDR controls only. Does not cover MFA, EDR, backups, IR, patch management."
content_hash: "sha256:..."                     # of source_artifact_path at last_verified_at
generated_at: "2026-05-26T20:43:12Z"
tenant_id: "acme-industries-demo"              # or null for cross-tenant evidence
signed_by:                                     # null if not applicable
  signature_type: "policy_version"
  signature_value: "acme-demo-policy-v1"
  signed_at: "2026-05-23T14:02:08Z"
```

### `claim_category` closed enum (proposed v1)

| Value | Meaning |
|---|---|
| `detection_evidence` | Detector output and lift-only invariant evidence |
| `scoring_explanation` | Internal score and client-facing rubric outputs |
| `policy_change_control` | Signed policy state, tenant override audit, requester/approver separation |
| `tenant_isolation` | Cross-tenant rejection, per-tenant override scoping |
| `kill_switch` | Operator authority evidence |
| `architecture_documentation` | Signed §11 specs |
| `test_evidence` | Lift-only invariant tests, gate tests, regression coverage |
| `independent_audit` | Grok output, Decision Auditor output |
| `operational_artifact` | Sample monthly report, daily digest, evidence-package precedents |

Adding categories is a v1.1 spec change.

### §6.1 Freshness policy (operator-resolved Q1/Q2)

The package cadence is hybrid:

- **Quarterly snapshot.** Each tenant gets a scheduled quarterly evidence-package snapshot so the MSP has a current baseline package available without waiting for a renewal event.
- **On-demand regeneration.** A package may be regenerated at any time for insurance renewal, MSP sales support, underwriter follow-up, incident response, or operator-directed need. Concurrent on-demand requests for the same tenant are queued behind the active generation job; they do not run in parallel against the same tenant evidence set.
- **Annual full review.** Each tenant receives one comprehensive review per insurance-renewal anniversary. This review re-evaluates claim-category assignment, structural exemption eligibility, evidence lineage, and references to superseded specifications. Quarterly and on-demand regenerations use the prior category / exemption assignments unless the operator explicitly triggers a full review early.

Freshness requirements correspond to the expected rate of materially relevant state change associated with the evidence class:

| Evidence class | Default threshold | Rule |
|---|---:|---|
| `policy_change_control` | 30 days | Mutable operational authority; stale records can misrepresent who approved or changed tenant policy. |
| `tenant_isolation` | 30 days | Tenant-scoped enforcement state; stale records can misrepresent isolation guarantees. |
| `kill_switch` | 30 days | Operator-authority evidence; stale records can misrepresent current emergency-control posture. |
| `detection_evidence` | 90 days | Reproducible detector evidence; refreshes on package generation or scheduled verification. |
| `scoring_explanation` | 90 days | Reproducible scoring / explanation evidence; slower-decay than mutable tenant state. |
| `test_evidence` | 90 days | Regression and lift-only invariant evidence; refreshed on test/gate runs. |
| `independent_audit` | 90 days | Grok / Decision Auditor evidence tied to a packet and timestamp. |
| `operational_artifact` | 90 days | Daily digest / monthly report artifacts and evidence-package precedents. |
| `architecture_documentation` | Exempt when structurally signed | Signed §11 specs are durable records when the `signed_by` reference resolves. |

Structural exemption overrides category default: any evidence record with non-null `signed_by` whose `signature_value` resolves to a valid signed artifact is freshness-exempt regardless of `claim_category`. If the signed artifact is later superseded, the record remains freshness-exempt as a historical signed artifact, but the rendered package must annotate it as `superseded by <new spec>` and the annual full review must verify that the package is not relying on the superseded artifact as current architecture.

Operational commitments introduced by this policy:

- The implementation spec must include a monthly internal verification path for 30-day categories so on-demand package generation does not fail unexpectedly on stale operational-state records.
- The implementation spec must include stale-evidence pre-warning behavior before a threshold breach. The alert channel and exact offset are implementation details; the v1 invariant is that stale evidence should not first become visible only at final package generation.
- The implementation spec must track Grok API availability / cost as an operational dependency for quarterly, on-demand, and annual package-generation audits.

### §6.2 Delivery surfaces (operator-resolved Q3)

The package ships in **two delivery surfaces** for v1:

- **PDF artifact (buyer-facing).** The PDF is the surface the MSP hands to the SMB and the SMB attaches to the underwriting application. It survives the worst-case yes/no-box underwriter read while preserving readability for the deep technical read. It carries the §2 boundary statement, the rendered evidence claims, and the package manifest summary.
- **Markdown bundle (audit / engineering companion).** The Markdown bundle ships alongside the PDF and contains the rendered Markdown explanation, the structured evidence records (the source of truth per §6), a README explaining who reads what, the package manifest, and the traceability material that lets a deep-reading underwriter or LLM-assisted reviewer follow each claim back to a `source_artifact_path`.

Deferred to v1.1+ pending cheaper-proof MSP demand evidence (Q10):

- **Branded landing page** — adds a hosted runtime surface that must enforce Guardrail 11 tenant isolation at the web layer; not bought against unproven demand.
- **Evidence vault with signed URL and audit log** — adds vault infrastructure, underwriter authentication, and an additional audit log surface; not bought against unproven demand.

A v1.1 reopening of either deferred surface requires concrete MSP-or-underwriter demand evidence captured during cheaper-proof discovery, plus a follow-up spec entry that re-evaluates the Guardrail 11 surface area cost.

Operational commitments introduced by this policy:

- **HC6 — Toolchain pinning.** The implementation spec must pin the PDF render toolchain (engine, version, fonts, template assets) and fold the toolchain identity and version into the package manifest. Silent toolchain mutation across versions is a determinism failure mode and must be prevented by the manifest.
- **HC7 — Bundle format, structured-records path, prompting pattern, and determinism pins.** The implementation spec must specify:
  - the Markdown bundle archive format (deterministic zipped package), the file layout (rendered Markdown, structured records directory at a stable internal path, README, manifest, content hashes), and the integrity model (per-file content hash plus a top-level package hash); loose-directory delivery is not v1 acceptable;
  - that the structured records directory uses a stable internal folder/path so a future v1.1 top-level JSON render can reuse the same records without bundle-format churn (Q9 D);
  - the prompting pattern used to generate the rendered-Markdown explanation section for each evidence record: **two-shot evidence-explanation prompting** with one fraud-row and one legit-row contrast pair sourced from the existing eval harness (Q7 / Q8 doctrine consumers); only the positive pattern is named ("two-shot evidence-explanation format"), and rejected prompting modes are not enumerated in the spec or in any buyer-facing copy;
  - the determinism pins (model identity, temperature, toolchain version, eval-harness contrast-pair source identifier) so two runs against the same inputs produce comparable rendered Markdown; pin values live in the implementation spec, not in §13, so prompt-tuning refinements do not force a spec re-sign.
- **HC8 — Minimal branding rules.** The implementation spec must define minimal branding rules so the PDF reads as credible without overclaim or scope drift. Branding must not introduce forbidden-language phrases (§9), must not surface repo-internal identifiers (§9 redaction), and must not expand or soften the §2 boundary statement into marketing copy.

### §6.3 Pricing scope (operator-resolved Q5)

The Cyber Insurance Evidence Package is **not priced by NorthStar in v1**. Package generation is treated as a feature of the underlying Inbox Shield runtime, not as a metered commercial line item. The MSP — as the contractual relationship per §3 — decides independently whether to bundle the package into their own client retainers, surcharge for it, absorb it, or omit it from their offering.

Package identifier issuance is technical, not commercial:

- `package_id` is constructed from `tenant_id + generation_timestamp` and is opaque to clients.
- `package_version` carries the spec version (`v1`) and any future spec revisions; it does not encode commercial state.
- No pricing field is added to the package schema, the `done_declaration.json`, or any structured evidence record in v1.

The package schema is forward-compatible to a future pricing field (HC12) without breaking v1 packages or their `done_declaration.json` files. Reopening pricing remains an explicit v1.1 spec decision, gated on cheaper-proof discovery evidence (Q10).

Operational commitments introduced by this scope:

- **HC10 — Free-work-perception risk.** The implementation spec must include plain-English boundary text distinguishing what NorthStar provides (the package generation surface) from what the MSP separately charges their SMB clients for (if anything). The boundary text protects MSPs from positioning the package as a NorthStar-priced deliverable they did not actually pay for, and protects NorthStar from MSP perception that valuable work is being given away for free.
- **HC11 — Anniversary cost monitoring.** The implementation spec must include a cost-monitoring path for Grok API spend during annual full reviews (§6.1), since insurance-renewal anniversaries cluster annual reviews into specific calendar windows. Without this monitoring, NorthStar absorbs concentrated cost spikes silently.
- **HC12 — Schema forward-compatibility.** The implementation spec must keep the package schema, `done_declaration.json`, and structured evidence records open to a v1.1 pricing field addition without breaking v1 packages already generated. No pricing field exists in v1.
- **HC13 — MSP retainer wording.** NorthStar must provide a single one-line plain-English package summary that MSPs can paste into their own client retainers or contracts. The summary stays inside the §2 boundary statement and the §9 forbidden-language list. It is provided as a render-time artifact in the Markdown bundle (per §6.2), not as a separate marketing document.

Q10 dependency (locked here): when Q10 (cheaper-proof go bar) is resolved, the discovery-call script must include a pricing-signal sub-question — e.g. *"If this package were a separate line item, what would you pay for it?"* — so any v1.1 pricing reopen rests on real MSP data rather than guess.

### Cross-record invariants

- Every `evidence_id` is unique within a package.
- Every `source_artifact_path` resolves to an existing file at package-generation time.
- Every `result: pass` has a fresh `last_verified_at` under the §6.1 freshness policy, unless it is structurally exempt through a valid `signed_by` reference.
- Every `signed_by` value, when present, traces to an existing signed artifact.
- Every rendered package annotates structurally signed records that reference superseded artifacts as `superseded by <new spec>`.
- Every record either has a `tenant_id` or is explicitly marked cross-tenant in `scope_limitations`.

---

## §7 Gate Log Schema

The package generation is itself audited. Every gate that runs against the package emits a gate log entry.

```yaml
gate_id: "gate-2026-05-26-001"
gate_name: "evidence_redaction_sweep"
gate_type: "redaction" | "claim_validation" | "scope_boundary" | "vocabulary_translation" | "audit_packet_coverage" | "broken_link" | "stale_evidence" | "forbidden_language" | "signed_provenance"
gate_command: "python -m scripts.evidence_package_verify --package <path> --gate redaction"
run_at: "2026-05-26T20:43:14Z"
result: "pass" | "fail"
findings: []                                   # populated on fail
relevant_evidence_ids: ["evd-2026-05-26-001", ...]
output_path: "audit_outputs/evidence_gate_<gate_id>.json"
```

### Required gates (v1)

| Gate | Pass condition |
|---|---|
| `claim_validation` | Every claim has at least one supporting evidence record |
| `broken_link` | Every `source_artifact_path` exists on disk |
| `stale_evidence` | No non-exempt `last_verified_at` exceeds the §6.1 threshold for its `claim_category`; structurally signed exemptions must resolve and superseded signed artifacts must be annotated |
| `forbidden_language` | No `guaranteed`, `bulletproof`, `fully secure`, `compliant` (absolute use), `SOC 2`, `ISO 27001` as a NorthStar claim — see §9 forbidden-language list |
| `scope_boundary` | Boundary statement present, unedited, prominent |
| `redaction` | No secrets, no raw credentials, no raw email bodies, no cross-tenant identifiers |
| `vocabulary_translation` | Carrier-jargon translation pass applied |
| `audit_packet_coverage` | Every file touched during generation is in the audit packet |
| `signed_provenance` | Every policy / override evidence record has a valid signature reference |

All gates must pass for the package to reach §11 done state. Gate failures emit a Drift Incident Report (§8).

---

## §8 Drift Incident Report Schema

A drift incident is any condition that would have shipped a deficient package if unblocked. Reports are auto-generated; they are not optional.

```yaml
incident_id: "drift-2026-05-26-001"
detected_at: "2026-05-26T20:43:15Z"
detector: "audit_packet_coverage_gate"
finding_type: "missing_file_in_audit_packet" | "broken_source_link" | "stale_evidence" | "unsigned_policy_artifact" | "forbidden_language" | "scope_boundary_missing" | "cross_tenant_identifier_leak" | "vocabulary_leak" | "overclaiming"
severity: "blocking" | "warning"
affected_evidence_ids: ["evd-..."]
affected_files: ["<path>", ...]
description: "Concise description of what was found and why it matters."
remediation_suggestion: "Plain-text guidance for how to resolve."
operator_acknowledged_at: null                 # filled when Matt accepts / resolves
operator_resolution_note: null                 # filled by Matt on acknowledge
resolution_path: null                          # link to fix commit / spec change / re-run if applicable
```

### Severity rules

- `blocking`: package cannot reach done state until resolved or explicitly accepted by Matt with `operator_resolution_note`.
- `warning`: package can reach done state but the warning is recorded in the package's own evidence trail (yes — the package contains the audit of its own generation).

### Auto-trigger conditions

A Drift Incident Report auto-generates on:

- Any §7 gate failure (`blocking`)
- Detection of forbidden language anywhere in the rendered package (`blocking`)
- Detection of cross-tenant identifier in a tenant-scoped record (`blocking`)
- Detection of a vocabulary-leak phrase outside the package's own scope (`warning` — see §5 iv)
- A `last_verified_at` approaching the §6.1 threshold under the implementation-defined pre-warning rule (`warning`)
- Any operator-invoked Hard Stop during generation (`blocking`)

---

## §9 Redaction / Secret Handling

The package never contains:

- Raw email bodies
- Raw vendor names if customer-confidential (vendor-name handling is per-tenant policy; see §12.Q11)
- Raw recipient identities (employee names, emails) beyond what the MSP / SMB chooses to include
- API keys, tokens, credentials, signing keys, or any other secret material
- Any tenant identifier inside a different tenant's record (Guardrail 11 — sacred)
- LLM client API responses verbatim (only validated structured outputs are referenced)
- Internal NorthStar developer identifiers, GitHub usernames, or repo-internal references that have no buyer relevance

### Forbidden-language list (v1, enforced by `forbidden_language` gate)

- `guaranteed`, `guarantee` (when applied to detection / outcome)
- `bulletproof`
- `fully secure`, `100% secure`, `complete security`
- `compliant`, `compliance` (as absolute claim about NorthStar)
- `SOC 2`, `SOC2`, `ISO 27001`, `HIPAA`, `PCI` (as NorthStar attestation — they are out of scope)
- `attestation` (when used to claim NorthStar attests to a control surface it doesn't own)
- `prevents all`, `stops all`, `eliminates all`
- `replaces your` (e.g. "replaces your email gateway" — NorthStar augments, does not replace)

Detection of any forbidden phrase outside an allowed context is a blocking drift incident.

### Allowed contexts for forbidden phrases

Forbidden phrases may appear only when the rendered package is explicitly limiting or rejecting a claim. Allowed contexts are:

- The required §2 scope boundary statement.
- Non-scope / "what NorthStar does NOT do" sections.
- The forbidden-language list itself.
- Bad-claim examples used to explain what must not ship.
- Drift Incident Reports that quote or identify the forbidden phrase being blocked.

The same phrase is blocking when used as a NorthStar capability, certification, compliance, security, detection, underwriting, or outcome claim.

### Operator avoid-list for this package (non-canonical, review guidance only) — Q8 D

The following twelve phrases are operator-flagged for this package's drafting and review. This list is **non-canonical**. The canonical forbidden-language authority for the project is `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` §5.1 (§11-signed 2026-05-26). Nothing on this list overrides or expands §5.1; promotion of any term into enforced project-wide forbidden-language status requires a signed §5.1 revision, not an edit here.

- `saved money`
- `prevented fraud`
- `blocked the loss`
- `stopped fraud`
- `chain of thought`
- `self-improving AI`
- `autonomous evolution`
- `compliant`
- `certified`
- `approved by insurer`
- `carrier-approved`
- `underwriter-approved`

Use of any phrase on this avoid-list inside Cyber Insurance Evidence Package drafting, generated artifacts, or buyer-facing copy is treated as a review-time flag for operator attention. Operator decides whether to rewrite, accept (with documented context), or, if the case is strong enough, request the §5.1 canonical revision separately.

`compliant` is intentionally retained on this avoid-list even though it already appears in the §7 `forbidden_language` gate above; redundancy here is allowed because the operator avoid-list is a human-readability review aid, not a second source of truth for the gate.

### Vocabulary translation list (v1, enforced by `vocabulary_translation` gate) — Q6 A

Plain-English replacements for carrier jargon are applied at render time. The translation rule list is itself an evidence record and is itself versioned.

| Carrier jargon | Plain English replacement (proposed) |
|---|---|
| Control efficacy | How well this control works in practice |
| Regulatory mapping | Cross-reference to specific underwriting questions |
| Compensating control | A different control that addresses the same risk |
| Control attestation framework | The way we record what each control does |
| Material weakness | A meaningful gap |

**v1 lock.** The five rows above are the v1 translation list. Additions, removals, or rewrites in v1.1+ arrive through the cheaper-proof MSP discovery feedback channel: surface as Frontier Intake entry → `think_sheet.md` row → spec-first promotion through §11 revision (Q7 feedback channel pattern, applied here). No per-carrier or runtime expansion in v1.

### Redaction sweep workflow

The redaction sweep is a §7 gate (`redaction`). It runs against every evidence record and every rendered surface before the package is considered complete. It is a binary pass/fail. Manual operator review is required only on warnings, not on passes.

---

## §10 Grok Audit Requirements

Grok is a **negative-feedback auditor**, not an approval authority. Per the 2026-05-26 workflow change, Grok's role is to identify deviations, not to score or judge.

### Audit prompt contract

Grok receives:

- The current package contents (all evidence records + all rendered surfaces).
- This deep-dive spec (the contract Grok audits against).
- The seven non-negotiables from `VISION.md`.
- The scope boundary statement.
- The forbidden-language list.
- The vocabulary-translation list.
- The list of files actually touched during package generation (the audit packet).

Grok is asked exactly:

> *"Identify any deviations from the spec, the seven non-negotiables, the scope boundary, the forbidden-language list, the vocabulary-translation list, or the audit-packet coverage rule. Do not score. Do not approve. Do not assess product-market fit or strategic alignment. Report only deviations and gaps."*

### Audit packet coverage rule

The audit packet given to Grok **must** include every file that was touched during package generation. AI-side scoping of the audit packet is forbidden. If a file was read, written, or modified by the generation process, it goes in the packet. Mismatch between touched-files and audit-packet contents is itself a `missing_file_in_audit_packet` drift incident.

This deliberately includes read inputs, not only modified outputs. The 2026-05-23 weekend bug was a read-from-but-silently-mishandled failure mode; a modified-outputs-only packet would not have caught the same class of miss. The tradeoff is packet inflation: package generation may read dozens of source artifacts, so Grok's packet can be large. That cost is accepted because large text audit packets are cheaper than another silent evidence miss.

This rule is non-negotiable. It is the specific lesson from the 2026-05-23 weekend Pass-1 wiring bug — the wiring file was not in the original audit packet, so the audit missed the silent flag-drop. Same shape of failure cannot recur here.

### Output handling

- Grok output is saved to `audit_outputs/cyber_insurance_evidence_package_<timestamp>.md`.
- If Grok identifies zero deviations, that is the compliant state.
- Every deviation Grok identifies generates a Drift Incident Report (§8).
- Drift incidents must be resolved or explicitly accepted by Matt with an `operator_resolution_note` before the package reaches done state.
- "Grok said nothing" is a compliant outcome **only** if the audit packet covered every touched file. Silence on a partial packet is not compliance.

### Audit cadence

- Every package generation triggers a Grok audit before completion.
- A package is not "done" without a fresh Grok audit output dated after generation finished.
- This is a hard rule. The §11 done criteria enforce it.
- Under the hybrid cadence in §6.1, this means every quarterly snapshot, every on-demand regeneration, and every annual full review gets its own fresh Grok audit. Cached or prior audits do not satisfy a new package-generation event unless the packet hash, generated evidence set, and rendered package are identical.
- Annual full reviews are anchored to the tenant's insurance-renewal anniversary. They re-evaluate category assignment, structural exemption eligibility, lineage, and superseded-spec references before the package can reach done state.

---

## §11 Done Criteria

A package reaches "done" if and only if **all** of the following are true:

1. **Boundary statement present.** The §2 scope boundary statement appears in the rendered package, unedited.
2. **Every claim has evidence.** Every claim in the rendered package corresponds to at least one structured evidence record with a non-null `source_artifact_path`.
3. **Every source path resolves.** Every `source_artifact_path` exists on disk at package-generation time.
4. **No stale evidence.** No non-exempt `last_verified_at` exceeds the §6.1 threshold for its `claim_category`; every structural exemption resolves to a valid signed artifact; every superseded signed artifact is annotated in the rendered package.
5. **No forbidden language.** The `forbidden_language` gate (§7) passes.
6. **Redaction sweep passes.** The `redaction` gate (§7) passes — no secrets, no raw bodies, no cross-tenant identifiers.
7. **Vocabulary translation applied.** The `vocabulary_translation` gate (§7) passes.
8. **Signed provenance complete.** The `signed_provenance` gate (§7) passes — every policy / override record traces to a signed artifact.
9. **Tenant isolation invariants hold.** No tenant-scoped record contains a different tenant's identifier.
10. **Audit packet covers touched files.** The `audit_packet_coverage` gate (§7) passes — every file touched during generation is in the packet.
11. **Grok audit run.** A Grok audit output file exists in `audit_outputs/` dated after package-generation completion, and that audit was performed on the complete audit packet (rule 10).
12. **Grok findings resolved.** Every Grok-identified deviation is either resolved or explicitly accepted by Matt with `operator_resolution_note` in the corresponding Drift Incident Report.
13. **No blocking drift incidents open.** All `blocking` Drift Incident Reports are resolved or accepted.
14. **Operator signature.** Matt has reviewed the rendered package and signed off in his own words. The signature is part of the package — a `signed_by_operator` evidence record with timestamp, scope acknowledgment, and Matt's own wording. AI-authored sign-off text is forbidden (cross-reference: deleted `Human_Written_Communication_Policy.md`, Authorship Rule discussion 2026-05-25/26).
15. **v1 test plan executed.** The v1 test plan defined in §14 (and inherited verbatim by the future implementation spec) has rendered at least one fictional Stage A evidence case end to end across all five Evidence-and-Outcome-Reporting stages — Detection → Verification → Evidence → Audit Trail → Outcome Documentation — against the five-record set from §12.Q7. The test-plan run produces the captured artifact set §14.5 names and is logged through the project's normal test-evidence surfaces (e.g. `REACTION_TIMING_TEST_LOG.md` when timing is in scope; activity-log entry plus tracked test-input artifact otherwise). This criterion fails closed: a package cannot be done if the §14 test plan has never been run end to end.

### Machine-readable done declaration

When all 15 criteria are met, the package emits a `done_declaration.json`:

```json
{
  "package_id": "cybins-evd-acme-2026-q2",
  "package_version": "v1",
  "tenant_id": "acme-industries-demo",
  "generated_at": "2026-05-26T20:43:12Z",
  "done_at": "2026-05-26T20:55:03Z",
  "criteria_met": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
  "grok_audit_output": "audit_outputs/cyber_insurance_evidence_package_2026-05-26T204502Z.md",
  "drift_incidents_resolved": ["drift-..."],
  "operator_signature_evidence_id": "evd-..."
}
```

A missing or partial `done_declaration.json` means the package is not done, regardless of what the rendered surface looks like. A `done_declaration.json` that omits `15` from `criteria_met` is treated as the package not being done; whether that fires a blocking Drift Incident under a new `finding_type` enum value or fits under an existing one (e.g. `overclaiming` if the package is also asserting done state) is an implementation-spec detail and may require a §8 enum revision at that time.

---

## §12 Open Questions for Matt

These resolve into locked decisions D1–D11 at §11 sign-off (D1–D2e from Q1/Q2, D3–D3a from Q3, D4 from Q4, D5 from Q5, D6–D11 from Q6–Q11). All eleven questions are operator-resolved as of 2026-05-30 (each marked "Resolved YYYY-MM-DD by operator (pending §13 lock as DN)" inline), but the spec remains pre-§11 until §13 sign-off lands; the §13 preconditions in that section define what still has to be true before sign-off can begin.

### Q1. Cadence

**Resolved 2026-05-26 by operator (pending §13 lock as D1).** Cadence is hybrid: quarterly snapshot, on-demand regeneration, and annual full review anchored to the tenant's insurance-renewal anniversary. Quarterly and on-demand regenerations use prior category / exemption assignments; annual full review re-evaluates category assignment, structural exemption eligibility, evidence lineage, and superseded-spec references.

### Q2. Stale-evidence threshold

**Resolved 2026-05-26 by operator (pending §13 lock as D2-D2e).** Threshold model is per-category default with structural exemption override:

- 30-day default: `policy_change_control`, `tenant_isolation`, `kill_switch`.
- 90-day default: `detection_evidence`, `scoring_explanation`, `test_evidence`, `independent_audit`, `operational_artifact`.
- Structural exemption: any record with non-null `signed_by` whose `signature_value` resolves to a valid signed artifact is freshness-exempt regardless of category.
- Supersession handling: a superseded signed artifact remains freshness-exempt as historical signed evidence, but the rendered package must annotate it as `superseded by <new spec>` and cannot rely on it as current architecture after the annual full review.
- Operational commitments acknowledged by operator: monthly internal verification path for 30-day categories, annual full review as a new spec requirement, stale-evidence pre-warning behavior, queued on-demand concurrency for the same tenant, and Grok API availability/cost as an operational dependency.

### Q3. Delivery mechanism

**Resolved 2026-05-26 by operator (pending §13 lock as D3-D3a).** v1 ships two delivery surfaces only: PDF artifact (buyer-facing) and Markdown bundle (audit / engineering companion). Branded landing page and evidence vault with signed URL are deferred to v1.1+ pending cheaper-proof MSP demand evidence (Q10). Operational commitments acknowledged by operator: HC6 toolchain pinning, HC7 bundle format specification, HC8 minimal branding rules — all to be encoded in the implementation spec. Full surface and commitment definitions are in §6.2.

### Q4. Per-carrier variants vs single carrier-agnostic format

**Resolved 2026-05-26 by operator (pending §13 lock as D4).** D4: single carrier-agnostic format only — no per-carrier variants in v1, v1.1, or any later scope. This is product policy, not a deferred backlog item; reopening it requires a new signed spec, not a one-off exception. D4 is locked as a structural constraint only. Q6 (vocabulary-translation list) and Q8 (forbidden-language list) remain independent filters under §9; they are not bundled with D4 under a unified governance frame. Renderer ordering between §7 gates is an implementation-spec detail, not §6 / §9 doctrine.

### Q5. Pricing model

**Resolved 2026-05-27 by operator (pending §13 lock as D5).** D5: not priced by NorthStar in v1. Package generation is a feature of the underlying Inbox Shield runtime; the MSP independently decides whether to bundle, surcharge, absorb, or omit the package in their own client offerings. `package_id` and `package_version` are tied to `tenant_id + generation_timestamp` only; no pricing field exists in the package schema, `done_declaration.json`, or any structured evidence record in v1. Schema is forward-compatible to a v1.1 pricing field. Operational commitments acknowledged by operator: HC10 free-work-perception risk, HC11 anniversary cost monitoring, HC12 schema forward-compatibility, HC13 MSP retainer wording. Q10 dependency locked: cheaper-proof discovery must include a pricing-signal sub-question. Full scope and commitment definitions are in §6.3.

### Q6. Translation list scope

**Resolved 2026-05-30 by operator (pending §13 lock as D6).** D6: lock the §9 vocabulary translation list at its current five rows as the v1 canonical set. Additions, removals, or rewrites in v1.1+ arrive through the cheaper-proof MSP discovery feedback channel — surface as a Frontier Intake entry, promote to `think_sheet.md`, then spec-first promotion through §11 revision. No per-carrier or runtime expansion in v1. See §9 vocabulary translation list for the v1 lock and feedback-channel rule.

### Q7. Which existing artifacts go in v1 vs v1.1

**Resolved 2026-05-30 by operator (pending §13 lock as D7).** D7: Shape α — one record per Evidence-and-Outcome-Reporting stage in v1, with v1.1 expansion allowed only on cheaper-proof feedback. The v1 record set:

| Stage | v1 evidence record |
|---|---|
| Detection | Lift-only invariant test results |
| Verification | Scoring explanations: internal 0–100 + client-facing 5-axis rubric |
| Evidence | Effective parameter report, per-tenant |
| Audit Trail | Signed policy state + tenant override audit |
| Outcome Documentation | Inbox Shield sample monthly report |

Feedback channel for v1.1 additions: surface cheaper-proof MSP discovery requests as a Frontier Intake entry → promote to `think_sheet.md` → spec-first promotion through §11 revision if the change is structural. Light record-swap tuning between v1 and v1.1 follows the same path; the feedback channel is not a runtime expansion lane.

Cross-reference: the Direction lock (top of spec) requires the five-stage mapping to remain intact; any v1.1 change that breaks the one-record-per-stage shape is a new operator decision, not a tuning detail.

### Q8. Forbidden-language list — additions

**Resolved 2026-05-30 by operator (pending §13 lock as D8).** D8: this package inherits the canonical forbidden-language list from `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` §5.1 (§11-signed 2026-05-26). For drafting and review of this package only, a twelve-term **non-canonical operator avoid-list** lives in §9 as review guidance. The avoid-list does not create a second source of truth: it does not override §5.1, does not expand the §7 `forbidden_language` gate, and does not authorize new enforcement. Any term whose canonical enforcement is needed project-wide must be added through a signed §5.1 revision, not through this package. See §9 "Operator avoid-list" for the twelve terms.

### Q9. Render surfaces — Markdown vs JSON vs both

**Resolved 2026-05-30 by operator (pending §13 lock as D9).** D9: v1 ships **PDF + Markdown bundle** (per Q3 / §6.2). The Markdown bundle must preserve the machine-readable structured records at a stable internal folder/path inside the bundle so they remain discoverable for downstream tooling without a v1 top-level JSON render surface. **Top-level JSON render is deferred to v1.1**, gated on cheaper-proof MSP demand evidence. HC7 already requires the structured-records directory; D9 sharpens that requirement by locking the path stability as a v1.1-forward-compat constraint. See HC7 in §6.2 for the bundle-format and structured-records-path requirement.

### Q10. Cheaper-proof gating — what counts as go?

**Resolved 2026-05-30 by operator (pending §13 lock as D10).** D10 resolves both sub-questions of Q10 — the per-MSP definition of "yes" and the count threshold required to consider cheaper-proof validated.

**Per-MSP "yes" definition.**

- A single MSP's "yes" requires two named anchors: a **named SMB** plus a **named upcoming insurance / underwriting conversation** for that SMB.
- Verbal confirmation is acceptable for discovery logging; written follow-up strengthens the signal but is not required to satisfy the per-MSP definition.
- Discovery scripts must capture the two named anchors verbatim and log them through the existing project surfaces (cheaper-proof runbook + worksheet).

**Count threshold (operator-set 2026-05-30).**

- **2 of 3 relevant MSP conversations** must meet the per-MSP "yes" definition above to consider cheaper-proof validated for the purpose of unlocking implementation-spec authoring.
- "Relevant" means the MSP could plausibly answer the cheaper-proof framing for an SMB cyber-insurance evidence package — not any three conversations.
- Verbal confirmation counts for cheaper-proof logging.
- Written follow-up strengthens the evidence but is **not** required as a gate. Adding a written-follow-up requirement before the framing is known to land would raise friction prematurely; written follow-up stays "evidence strength," not "evidence gate."
- Operator rationale recorded in-line: 1-of-3 overfits to one friendly signal; 3-of-3 risks stalling the lane; 2-of-3 is the clean middle showing the framing is not a one-off while staying fast enough for Stage A.

Reopening the threshold (to 1-of-3, 3-of-3, written-follow-up required, or any other revision) is a v1.1 question pending live discovery feedback; it follows the Frontier Intake → `think_sheet.md` → spec-first §11 revision pattern.

Implementation-spec authoring is not authorized by D10 threshold-set alone. The original §13 sign-off precondition required the 2-of-3 threshold to be **met** in actual cheaper-proof discovery work, not merely asserted. On 2026-06-03, Matt signed an operator override removing that cheaper-proof gate as the active blocker. The override is preserved as "D10 overridden, not met" and must not be represented as cheaper-proof validation or market proof.

### Q11. Vendor-name redaction policy

**Resolved 2026-05-30 by operator (pending §13 lock as D11).** D11: in v1, vendor names are **silently redacted by default** in the rendered package whenever a tenant policy marks them as customer-confidential. The package does not annotate redaction events to buyer-facing readers in v1. v1.1 may add explicit redaction annotations to the rendered package if cheaper-proof MSP feedback (per Q10) shows that underwriters or MSPs care about redaction visibility as part of the evidence chain. Reopening this for v1.1 requires the same feedback-channel pattern as Q7 / D7 — Frontier Intake → `think_sheet.md` → §11 revision. The default-silent / future-visible split keeps v1 surface lean while preserving the operator's option to upgrade redaction visibility if downstream demand justifies it.

---

## §13 §11 Sign-Off

**Status:** SIGNED 2026-06-03 by Matt Nichol. Operating entity name is TBD pending the in-progress project rename (the "zebra-comit" handle is retracted). Operator authorized this sign-off in-session on 2026-06-03 by selecting "Lock Cyber Insurance §13 now under Matt Nichol (entity name TBD after rename)." The sign-off is recorded in the working tree and is uncommitted; committing it fires the pre-ship / completion gate per `AGENTS.md` §5.

### Preconditions for §13 sign-off

§13 cannot be signed until all three of the following hold. These are gating preconditions, not done criteria — they govern whether the sign-off step can begin, not whether a generated package is done.

1. **All §12 questions resolved.** Q1 through Q11 are each marked "Resolved YYYY-MM-DD by operator (pending §13 lock as DN)" in §12 with the operator-authored resolution text intact. At sign-off, every Q maps to a DN in the locked-decisions table below.
2. **v1 test plan defined and runnable from the spec alone.** Satisfied 2026-05-30 by §14 of this deep dive. §14 names the fictional Stage A case, the fixture path, the per-stage expected outputs, the end-to-end pass / fail criteria, and the runtime invocation sequence — all of which the implementation spec inherits verbatim when it gets written. A signed-but-test-plan-less package is the failure mode this precondition exists to prevent; §14's presence in the spec closes that failure mode at the *defined* layer. The *executed* layer is covered separately by §11 criterion 15.
3. **Q10 count threshold met or explicitly overridden.** The operator-set Q10 count threshold — **2 of 3 relevant MSP conversations** meeting the D10 per-MSP definition — is the default cheaper-proof gate. On 2026-06-03, Matt signed an operator override in `PROJECT_ACTIVITY_LOG.md` removing that cheaper-proof gate as the active blocker on the §13 readiness path. The override is supported by direction-confirming signal already logged in `Frontier_Intake_Log.md` and explicitly characterized as **not D10 evidence** and **not validated market proof**. Therefore, for this §13 review, precondition 3 is satisfied by explicit operator override, not by D10 completion.

The §11 Done Criteria criterion 15 enforces the same five-stage end-to-end rendering at package-done time. The §13 precondition 2 above enforces it earlier — at sign-off — so the spec cannot lock without the test plan that criterion 15 later checks against.

### Locked decisions (D1–D11) — locked at sign-off 2026-06-03

| # | Decision | Note |
|---|---|---|
| D1 | Cadence: hybrid — quarterly snapshot, on-demand regeneration, annual full review at the tenant's insurance-renewal anniversary. | From Q1. |
| D2–D2e | Stale-evidence thresholds: 30-day vs 90-day per-category defaults, structural signed-artifact freshness exemption, superseded-artifact annotation. | From Q2. |
| D3–D3a | v1 delivery surfaces: PDF (buyer-facing) + Markdown bundle (audit/engineering companion); landing page and evidence vault deferred to v1.1+. | From Q3. |
| D4 | Single carrier-agnostic format; no per-carrier variants in v1 or later (product policy, not backlog). | From Q4. |
| D5 | Not priced by NorthStar in v1; MSP decides bundling; no pricing field in package schema or `done_declaration.json`. | From Q5. |
| D6 | Lock the §9 vocabulary-translation list at its current five rows for v1; additions via the cheaper-proof feedback channel + §11 revision. | From Q6. |
| D7 | Shape α: exactly one evidence record per Evidence-and-Outcome-Reporting stage (Detection → Verification → Evidence → Audit Trail → Outcome Documentation). | From Q7. |
| D8 | Inherit the canonical forbidden-language list from `Compliance_and_Trend_Watch_Process.md` §5.1; the §9 twelve-term avoid-list is review guidance only. | From Q8. |
| D9 | v1 ships PDF + Markdown bundle with structured records at a stable internal path; top-level JSON render deferred to v1.1. | From Q9. |
| D10 | Cheaper-proof go bar definition retained (per-MSP "yes" = named SMB + named upcoming underwriting conversation; 2-of-3 relevant MSPs). **For this sign-off, D10 is OVERRIDDEN, not met**, per Matt's signed 2026-06-03 operator override in `PROJECT_ACTIVITY_LOG.md`. The override is operator decision + direction-confirming signal, not validated market proof. | From Q10 + 2026-06-03 override. |
| D11 | Vendor names silently redacted by default in the rendered package when tenant policy marks them customer-confidential in v1; explicit redaction annotations deferred to v1.1. | From Q11. |

### Sign-off line

> §13 SIGNED 2026-06-03 — Matt Nichol (operating entity name TBD pending project rename). Authorized in-session; accepts the 2026-06-03 D10 operator override (D10 overridden, not met) as the basis for precondition 3.

**REVISION RE-SIGNED 2026-06-05.** The §2 boundary statement was revised this date — the buyer-facing product name changed from "NorthStar Inbox Shield" to "Mutant Monkey Inbox Shield" (rebrand Option B external brand; internal codename unchanged; see the §2 buyer-facing brand note and `_Rebrand_to_Mutant_Monkey_Security_Consequence_Matrix.md`). Per `AGENTS.md` §6 this revision required a fresh gate and a new operator re-signature. Matt authored the re-signature wording below in-session; the assistant only placed it.

> §13 RE-SIGNED 2026-06-05 — Approved by Matt Nichol, Sovereign Operator

*Authorship note: the line above records Matt's explicit in-session authorization to lock §13 (he selected the "lock §13 now under Matt Nichol, entity TBD" option). The assistant did not compose sign-off rationale in the operator's voice; Matt may replace this line with his own personal wording at any time, and must set the operating entity name once the project rename is decided.*

*Commit discipline: this sign-off is recorded in the working tree and is uncommitted. Per `AGENTS.md` §5, committing it fires the pre-ship / completion gate, which must pass or be explicitly operator-overridden with a recorded reason before commit.*

Per the Authorship Rule (2026-05-25/26 discussion, cross-reference to the deleted `Human_Written_Communication_Policy.md` failure mode): the sign-off text is operator-authored. AI may help structure, may proofread, may flag inconsistencies — AI does not draft the operator's signature wording or attribute decisions to the operator without explicit operator authorship.

### What sign-off does

Signing this spec:

1. Locks D1–D11 from §12 question resolution (D1–D2e from Q1/Q2, D3–D3a from Q3, D4 from Q4, D5 from Q5, D6–D11 from Q6–Q11).
2. Authorizes the next stage — implementation spec authoring only if Matt either (a) treats cheaper-proof as validated through future discovery, or (b) continues under the 2026-06-03 signed operator override that removes D10 as the active blocker while preserving the "overridden, not met" boundary.
3. Anchors the spec for Pass 1 / Pass 2 implementation work when authorized.

Signing does **not**:

- Authorize implementation by itself (Matt's separate authorization required).
- Reduce or remove any of the §11 Done Criteria.
- Permit any AI-side scoping of the audit packet.
- Override any of the seven non-negotiables in `VISION.md`.
- Lock prompting determinism pins, contrast-pair sources, or render-toolchain versions — those live at HC7 / implementation spec so prompt-tuning refinements do not force a §11 re-sign.

---

## §14 v1 Test Plan — Fictional Stage A End-to-End Case

§14 defines the v1 test plan §11 criterion 15 requires and §13 precondition 2 makes a sign-off gate. The test plan is **runnable from this section alone** — no operator memory required. The implementation spec inherits §14 verbatim when it gets written.

§14 is the contract for the test plan, not the test results. Running the plan and recording pass / fail is the next build step, performed against this section and logged through the project's normal test-evidence surfaces.

### §14.1 Purpose and scope

The test plan exercises one fictional Stage A evidence case end to end across all five Evidence-and-Outcome-Reporting stages (Detection → Verification → Evidence → Audit Trail → Outcome Documentation) against the §12.Q7 v1 record set:

1. Detection — Lift-only invariant test results.
2. Verification — Scoring explanations (internal 0–100 + client-facing 5-axis rubric).
3. Evidence — Effective parameter report, per-tenant.
4. Audit Trail — Signed policy state + tenant override audit.
5. Outcome Documentation — Inbox Shield sample monthly report.

What the test plan covers:

- The full case path from email ingest to rendered monthly-report section.
- One confirmation request and one confirmation outcome.
- Production of all five records with a `source_artifact_path` per §6.
- All §7 gates applied against the rendered Outcome Documentation section.

What the test plan does **not** cover:

- Real attack content (the fixture is synthetic).
- Real customer data (the tenant is fictional).
- Cross-tenant interaction (the case is single-tenant).
- Latency / timing claims (timing is captured if measured but is not part of v1 pass / fail criteria).
- Real underwriter feedback (the rendered section is reviewed against §7 gates, not against a live underwriter).

### §14.2 Fictional case

**Case ID.** `cybins-v1-testplan-vendor-payment-redirect-001`.

**Tenant.** `bluefin-marine-supplies-demo` — a fictional SMB in the marine equipment supply line. The tenant is fictional and not tied to any real customer; the tenant ID is fresh to v1 and does not reuse the `acme-industries-demo` example tenant from §11's done-declaration block, so the example tenant is not implied to be canonical.

**Sender.** `accounts@billing.harborline-marine-services.example` — a fictional vendor name on the IANA-reserved `.example` TLD. The vendor is plausible-sounding for a marine supply SMB but is fictional and not tied to any real business.

**Recipient.** `ap@bluefin-marine-supplies-demo.example` — fictional accounts-payable mailbox on the same reserved TLD.

**Auth posture.** SPF pass, DKIM pass, DMARC pass — the email passes authentication. This is the deliberate "auth pass does not mean safe" pattern the rxt-2026-05-30-001 lab test established and that this package is designed to demonstrate at the buyer-facing surface.

**Content shape.** A fictional vendor invoice asking the recipient to update the vendor's bank account on file and to wire payment to the new account against an attached invoice. The body carries:

- Payment-change request language ("we have updated our banking details").
- Urgency markers ("please update before the end of the week").
- A new fictional account number (synthetic, not a real bank account).

The body text is synthetic and is not lifted from any real attack. The full body lives in the fixture (§14.5), not in this section.

**Confirmation lifecycle.** The runtime records:

- One `record_confirmation_request` — a confirmation request raised against the new banking detail change.
- One `record_confirmation_outcome` — outcome `payment_change_reviewed_before_action`, mirroring the operator-authored outcome heading §14.3.5 renders.

The case is intentionally single-tenant, single-vendor, single-invoice. Multi-tenant, multi-vendor, and multi-invoice cases are out of scope for v1; v1.1 may add them after the §14 plan has cleared §11 criterion 15 at least once.

### §14.3 Per-stage records and expected outputs

Each of the five records below must exist with a non-null `source_artifact_path` (§6 / §11 criterion 2) and must satisfy the stage-specific shape requirements. Exact numerical values are deterministic at run time and captured into the output artifacts; §14 locks the *shape* of each record so that pass / fail can be evaluated against the section without pre-locked numbers that would force a §14 re-sign on every rubric refinement.

#### §14.3.1 Detection — Lift-only invariant test results

**Record content.**

- Named lift-only invariant: `payment_change_body_pattern_v1`.
- `result`: `pass` — the invariant performed correctly, meaning the runtime produced *additive* risk above baseline (which is what the invariant tests). This is **not** a claim that the runtime caught the attack.
- A deterministic pattern ID identifying the body-content pattern that triggered the invariant.
- `claim_category`: `detection_evidence` per §6.1.

**Pass condition for the stage.**

- The record exists.
- The lift-only invariant reports `pass`.
- The record traces to a `source_artifact_path` that exists on disk.
- No raw email body appears in the record (§9 redaction).

#### §14.3.2 Verification — Scoring explanations

**Record content.**

- One scoring explanation block for this case.
- Internal 0–100 score, deterministic at run time, captured as an integer.
- Client-facing 5-axis rubric values per `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`: Sender, Content, Intent, Context, Urgency. Each axis is a deterministic integer at run time.
- Plain-English reasoning text that names the auth-pass-vs-content-risk pattern without using any forbidden phrase from §9 or any term from the §9 operator avoid-list.

**Pass condition for the stage.**

- The record exists.
- Both the internal score and all five axis values are present.
- The reasoning text passes the `forbidden_language` and `vocabulary_translation` gates (§7).
- Content axis and Intent axis values both reflect high content risk (each ≥ 70 / 100); the Sender axis value reflects the auth-pass posture (lower than Content / Intent but non-zero); the Urgency axis value reflects the urgent-payment markers (≥ 50 / 100). Exact values are captured at run time, not pre-locked in §14.

#### §14.3.3 Evidence — Effective parameter report, per-tenant

**Record content.**

- Per-tenant effective parameter report for `bluefin-marine-supplies-demo` at run time.
- For each detector that fired during the case, the report lists:
  - Detector name.
  - Effective parameter values used during this case.
  - Whether each value is the runtime default or a tenant override.
- A `policy_hash` reference identifying the signed policy state under which the report was produced.

**Pass condition for the stage.**

- The record exists.
- Every detector that fired in §14.3.1 has at least one entry in the report.
- Every entry names its source as either `default` or `tenant_override`.
- The `policy_hash` resolves to an existing signed-policy artifact on disk.

#### §14.3.4 Audit Trail — Signed policy state + tenant override audit

**Record content.**

- The signed policy state hash referenced by §14.3.3.
- A tenant override audit entry for `bluefin-marine-supplies-demo` capturing one fictional override the case exercises: a tenant-specific content-risk threshold tighter than the runtime default, used to demonstrate the override path.
- The override entry includes `requested_by` and `approved_by` fields with a fictional separation (different fictional identifiers); the case is single-tenant, but the audit-trail surface requires the separation to be visible.

**Pass condition for the stage.**

- The record exists.
- The `policy_hash` matches the value referenced by §14.3.3.
- The override entry has both `requested_by` and `approved_by`, with the two fields holding different values.
- The override traces to a `signed_by` reference resolvable on disk.

#### §14.3.5 Outcome Documentation — Inbox Shield sample monthly report

**Record content.**

- A rendered Markdown section for `bluefin-marine-supplies-demo`'s monthly report covering the run period.
- The section lists exactly one case for the period — case ID `cybins-v1-testplan-vendor-payment-redirect-001` — under the operator-authored outcome heading:

  > *"Vendor invoice review — payment change reviewed before action."*

- The section includes the §2 boundary statement, unedited.
- The section references each of §14.3.1 – §14.3.4 by `source_artifact_path` so a reader can trace every claim in the rendered section back to a structured record.

**Pass condition for the stage.**

- The record exists.
- The outcome heading is rendered with the exact operator-authored wording above. Paraphrases such as "redirect prevented," "fraud blocked," "loss avoided," "saved money," "stopped fraud," and similar outcome-claim rewrites are drift incidents and fail this stage.
- The §2 boundary statement appears unedited.
- Every `source_artifact_path` reference in the section resolves on disk (`broken_link` gate, §7).
- No forbidden-language phrase or §9 operator avoid-list term appears in the rendered section as a NorthStar claim.

### §14.4 End-to-end pass / fail criteria

A v1 test-plan run **passes** when **all** of the following hold:

1. All five records (§14.3.1 – §14.3.5) exist with non-null `source_artifact_path` values that resolve on disk.
2. Every stage-specific pass condition in §14.3.1 – §14.3.5 holds.
3. The §7 gates `claim_validation`, `broken_link`, `stale_evidence`, `forbidden_language`, `scope_boundary`, `redaction`, `vocabulary_translation`, `audit_packet_coverage`, and `signed_provenance` all pass against the rendered §14.3.5 section.
4. The §2 boundary statement appears in the rendered section, unedited.
5. No forbidden-language phrase and no §9 operator avoid-list term appears as a NorthStar claim anywhere across the five records or the rendered section.
6. No raw email body, no secret material, no cross-tenant identifier, and no tenant-private identifier other than the fictional `bluefin-marine-supplies-demo` appears in any record (§9 redaction).
7. The outcome heading in §14.3.5 is rendered verbatim: *"Vendor invoice review — payment change reviewed before action."*

A run **fails** if any of the seven conditions does not hold. Each failure produces a Drift Incident Report per §8 with the affected `evidence_id`(s) and `affected_files` populated; the run-level outcome is recorded as a fail in the test-evidence log §14.5 names.

The run-level pass / fail is a single boolean; partial passes are not recognized. A run that produces four good records and one missing record is a **fail**, not a four-of-five pass.

### §14.5 Run surface

The test plan is runnable from §14 alone. The following names are stable contracts; substitute paths are not §14-conformant.

**Fixture path.**

```
3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/fixtures/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001.json
```

The fixture contains the synthetic email payload, the fictional `Authentication-Results` headers (SPF / DKIM / DMARC pass), the fictional sender / recipient / tenant identifiers from §14.2, and the synthetic body content. The fixture is created when the test plan is first run (the next build step); §14 names the path so the fixture has a stable, spec-named home.

**Tenant config.** `bluefin-marine-supplies-demo` is registered with one fictional tenant override (the tighter content-risk threshold §14.3.4 names). Tenant registration happens in the test-plan run, not in §14.

**Runtime invocation sequence.** From `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation` as the working directory, an inline runner imports the runtime modules and calls, in order:

1. `ingest_email` against the fixture payload → produces the `EmailInboundPayload`.
2. `run_email_risk_scoring_cycle` against the inbound payload → produces the `EmailAnalysisPayload` and the scoring explanation.
3. `record_confirmation_request` → produces the confirmation request record for the new banking detail change.
4. `record_confirmation_outcome` with outcome `payment_change_reviewed_before_action` → produces the confirmation outcome record.
5. `run_daily_digest_cycle` → produces the digest output that feeds the monthly-report section §14.3.5 renders.

No runtime code is modified by the test-plan run. The inline runner is created outside the repo at run time (mirroring rxt-2026-05-30-001) so the durable repository evidence stays the fixture, the records, and the activity-log entry.

**Output artifacts.**

| Stage | Output artifact (relative to repo root) |
|---|---|
| §14.3.1 | `audit_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/detection.json` |
| §14.3.2 | `audit_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/verification.json` |
| §14.3.3 | `audit_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/evidence.json` |
| §14.3.4 | `audit_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/audit_trail.json` |
| §14.3.5 | `audit_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/outcome_documentation.md` |

The five output paths form the `source_artifact_path` values §6 requires.

**Pass / fail logging.** The run produces:

- One entry in `PROJECT_ACTIVITY_LOG.md` describing the run, the pass / fail outcome, the run timestamp, and the seven §14.4 conditions evaluated.
- If timing was measured, one `rxt-` record in `REACTION_TIMING_TEST_LOG.md` mirroring the rxt-2026-05-30-001 shape.

Both surfaces are part of the project's existing test-evidence surfaces; §14 does not introduce a new test-evidence surface.

### §14.6 What §14 does not authorize

- Implementation work outside the test-plan run. §14 satisfies §13 precondition 2 ("v1 test plan defined and runnable from the spec alone"); it does **not** satisfy §13 precondition 3 (operator-set Q10 count threshold met in actual cheaper-proof MSP discovery) and does **not** satisfy §11 sign-off. Implementation-spec authoring still requires §13 sign-off, which itself still requires precondition 3.
- Real-customer data substitution. The tenant `bluefin-marine-supplies-demo`, the vendor `harborline-marine-services.example`, the recipient mailbox, and the body content are all fictional; substituting real customer data for any of these voids the test plan and is a §9 redaction failure.
- Drift in the outcome wording. The outcome heading "Vendor invoice review — payment change reviewed before action" is operator-authored. Paraphrases, expansions, or any phrasing that asserts NorthStar prevented, blocked, or stopped the attack are drift incidents at run time.
- A §11 re-sign without operator authorization. §14 may be tightened in future revisions; any tightening that would force §13 to re-sign requires explicit operator authorization, not an implicit edit.

---

## Cross-references

- `VISION.md` — seven non-negotiables that govern this spec
- `think_sheet.md` — 2026-05-25 Cyber Insurance Evidence Package row + stress-test answers (score 10/10, "promote with cheaper-proof-first guidance")
- `MILESTONE_ARC.md` — Stage A → B → C arc; this package is a Stage A explainability-lane artifact
- `REVENUE_MAP.md` — Lane 3 MSP discovery; cheaper-proof activity for this spec doubles as Lane 3 milestone work (two-for-one)
- `1. Business_Operations/Client_Documents/Inbox_Shield_Sample_Monthly_Report.md` — primary existing artifact this package organizes around
- `1. Business_Operations/Client_Documents/MSP_Discovery_Evidence_Package.md` — architectural precursor; demonstrates the safe-claim discipline this package inherits
- `4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md` — sibling deep-dive style reference
- `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` — rubric whose outputs feed scoring-explanation evidence records

---

**End of draft. Pre-§11. No implementation work is authorized by this document.**
