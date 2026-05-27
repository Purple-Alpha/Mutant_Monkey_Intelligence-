# Cyber Insurance Evidence Package — Deep Dive

**Status:** DRAFT (pre-§11). §12 Q1/Q2/Q3 resolved by operator on 2026-05-26 (pending §13 lock as D1-D2e and D3-D3a); remaining §12 open questions still require operator resolution before §13 sign-off.

**Authority model:** Matt's vision is the product authority. This document is a Technical Verification Layer artifact. It defines technical risks, failure modes, evidence schemas, audit requirements, and machine-readable "done" criteria. It does not score, approve, or judge the product direction.

**Scope reminder:** This package is an *organizational and presentation* layer over evidence NorthStar Inbox Shield already produces. It does not introduce new detection capability, new external claims, or new scope. It assembles existing audit artifacts into a buyer-readable bundle for the email-fraud / inbox-layer MDR control surface only.

**Selected by:** Operator selection 2026-05-25 evening. Matt's selection is the authority. Cross-reference: `think_sheet.md` row "Cyber Insurance Evidence Package" (2026-05-25); any score recorded there is historical metadata only, not decision authority. The active guidance is "promote with cheaper-proof-first guidance."

**Spec drafting is operator-authorized and gated on cheaper-proof MSP discovery validation** per the think_sheet stress test verdict. This draft does not unblock implementation; it produces the contract that cheaper-proof discovery conversations can frame against.

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

> *"This package covers NorthStar Inbox Shield's email-fraud and inbox-layer MDR control surface only. Other controls in your security stack — including MFA, EDR, backups, incident response plans, and patch management — are not in this package's scope and must be evidenced by your MSP or other vendors. This package does not guarantee underwriting approval or premium reduction; it provides auditable evidence of one control surface for your underwriter's review."*

This statement is part of the contract. Removing it, softening it, or replacing it with marketing copy is a drift incident.

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
- **HC7 — Bundle format.** The implementation spec must specify the Markdown bundle archive format (deterministic zipped package), the file layout (rendered Markdown, structured records directory, README, manifest, content hashes), and the integrity model (per-file content hash plus a top-level package hash). Loose-directory delivery is not v1 acceptable.
- **HC8 — Minimal branding rules.** The implementation spec must define minimal branding rules so the PDF reads as credible without overclaim or scope drift. Branding must not introduce forbidden-language phrases (§9), must not surface repo-internal identifiers (§9 redaction), and must not expand or soften the §2 boundary statement into marketing copy.

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
- Raw vendor names if customer-confidential (vendor-name handling is per-tenant policy; see §12 open question)
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

### Vocabulary translation list (v1, enforced by `vocabulary_translation` gate)

Plain-English replacements for carrier jargon are applied at render time. The translation rule list is itself an evidence record and is itself versioned.

| Carrier jargon | Plain English replacement (proposed) |
|---|---|
| Control efficacy | How well this control works in practice |
| Regulatory mapping | Cross-reference to specific underwriting questions |
| Compensating control | A different control that addresses the same risk |
| Control attestation framework | The way we record what each control does |
| Material weakness | A meaningful gap |

The exact translation list is open for operator review at §12.

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

### Machine-readable done declaration

When all 14 criteria are met, the package emits a `done_declaration.json`:

```json
{
  "package_id": "cybins-evd-acme-2026-q2",
  "package_version": "v1",
  "tenant_id": "acme-industries-demo",
  "generated_at": "2026-05-26T20:43:12Z",
  "done_at": "2026-05-26T20:55:03Z",
  "criteria_met": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
  "grok_audit_output": "audit_outputs/cyber_insurance_evidence_package_2026-05-26T204502Z.md",
  "drift_incidents_resolved": ["drift-..."],
  "operator_signature_evidence_id": "evd-..."
}
```

A missing or partial `done_declaration.json` means the package is not done, regardless of what the rendered surface looks like.

---

## §12 Open Questions for Matt

These resolve into locked decisions (D1–Dn) at §11 sign-off. Until then they are open and the spec is pre-§11.

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

The think_sheet stress test verdict was single carrier-agnostic with a "see your carrier's specific questions" disclaimer. This question is open here only to lock that verdict explicitly at §11.

### Q5. Pricing model

Per-package? Bundled in MSP retainer? Per-tenant-per-month surcharge? Out of NorthStar product scope strictly — but the answer shapes how the package's `package_id` and `package_version` are issued and tracked.

### Q6. Translation list scope

The §9 vocabulary translation list is open. Carrier jargon to translate, plain-English replacements, edge cases (terms that are sometimes jargon and sometimes legitimate). Matt's call on each entry.

### Q7. Which existing artifacts go in v1 vs v1.1

v1 candidate set is large (everything in §4). Going wide on v1 increases surface area and engineering cost. Going narrow risks omissions underwriters expect. Trade-off is Matt's to make; the spec doesn't prejudge it.

### Q8. Forbidden-language list — additions

§9 lists v1 forbidden phrases. Carrier-specific jargon, regulator-specific phrases, or competitor-specific language (e.g. "we replace Defender") may need to join the list.

### Q9. Render surfaces — Markdown vs JSON vs both

Engineering question. The structured evidence records are JSON / YAML by spec. The buyer-readable surface is open: Markdown for engineering visibility, PDF for delivery, JSON for machine consumption (e.g. an MSP's evidence-management platform). Likely the answer is "all of the above," but Matt confirms.

### Q10. Cheaper-proof gating — what counts as go?

The think_sheet verdict gates spec implementation on cheaper-proof MSP discovery. What signal counts as "go" — 1 of 3 MSPs saying yes? 2 of 3? A different bar? Matt sets the threshold.

---

## §13 §11 Sign-Off Placeholder

This section is empty until Matt signs.

### Locked decisions (D1–Dn) — populated on sign-off

| # | Decision | Note |
|---|---|---|
| (pending) | (pending) | Decisions enter this table only after Matt's signed acceptance of the corresponding §12 open question. |

### Sign-off line

> *(To be authored by Matt in his own words at §11 sign-off.)*

Per the Authorship Rule (2026-05-25/26 discussion, cross-reference to the deleted `Human_Written_Communication_Policy.md` failure mode): the sign-off text is operator-authored. AI may help structure, may proofread, may flag inconsistencies — AI does not draft the operator's signature wording or attribute decisions to the operator without explicit operator authorship.

### What sign-off does

Signing this spec:

1. Locks D1–Dn from §12 question resolution.
2. Authorizes the next stage — cheaper-proof MSP discovery framing if not yet done, or implementation spec authoring if cheaper-proof has already validated the framing.
3. Anchors the spec for Pass 1 / Pass 2 implementation work when authorized.

Signing does **not**:

- Authorize implementation by itself (Matt's separate authorization required).
- Reduce or remove any of the §11 Done Criteria.
- Permit any AI-side scoping of the audit packet.
- Override any of the seven non-negotiables in `VISION.md`.

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
