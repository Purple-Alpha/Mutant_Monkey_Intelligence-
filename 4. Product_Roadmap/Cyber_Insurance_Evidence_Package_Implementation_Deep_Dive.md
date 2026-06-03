# Cyber Insurance Evidence Package — Implementation Deep Dive

**Status:** DRAFT pre-§11. Not signed. Not implementation authorization. Not runtime code yet. Not client-facing copy. This document defines *how* the Cyber Insurance Evidence Package would be built; it does not authorize building it. Code begins only after this spec is §11-signed AND Matt issues a separate explicit start-build instruction.

**Date drafted:** 2026-06-03

**Project name note:** The project rename away from "NorthStar" is in progress and unresolved as of this draft (see `PROJECT_ACTIVITY_LOG.md` 2026-06-03). This spec uses "NorthStar" as a placeholder. A controlled rename pass will sweep this file with the rest of the repo once the operator selects a name; no name is locked here.

**Authority model:** Matt's vision is the product authority. This is a Technical Verification Layer artifact. It defines build mechanics, module boundaries, file layouts, gate logic, render toolchain pins, and test mechanics. It does not score, approve, or judge product direction, and it cannot relax any decision locked by the signed deep-dive.

---

## §0 Purpose

Define exactly how the Cyber Insurance Evidence Package would be implemented under the §13-signed contract `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md`.

The signed deep-dive answers **what** the package is, **what** it claims and refuses to claim, **what** records it contains, and **what** "done" means. This implementation spec answers **how**: the generation pipeline, the module boundaries, the on-disk artifact layout, the concrete gate checks, the redaction mechanics, the two render surfaces, the Grok audit wiring, and the determinism pins that the deep-dive (HC7) deliberately parked at the implementation layer so prompt-tuning does not force a §13 re-sign.

This spec adds **no new product claim, no new evidence capability, and no new scope.** Every behavior it describes is a mechanical realization of a decision already locked in the signed deep-dive (D1–D11, HC6–HC13, §6/§7/§8/§9/§10/§11/§14).

---

## §1 Scope

### In scope

- The package-generation pipeline: stages, ordering, and control flow from tenant selection to `done_declaration.json`.
- Module / component boundaries and where code lives (isolation from runtime detection code).
- On-disk artifact layout: the package directory, the structured evidence-record files, the Markdown bundle archive layout, the manifest, and `done_declaration.json`.
- Evidence collection mechanics for the §12.Q7 / D7 five-record set (Detection, Verification, Evidence, Audit Trail, Outcome Documentation).
- Verification-command execution, `content_hash` computation, and the §6.1 freshness policy enforcement.
- Concrete implementation of each §7 gate, and the gate ordering.
- Redaction sweep, forbidden-language gate, vocabulary-translation gate, and the D11 vendor-name silent-redaction implementation.
- Render surfaces: PDF artifact and Markdown bundle, including HC6 toolchain pinning, HC7 bundle format, HC8 branding rules.
- Determinism pins (HC7): model identity, temperature, toolchain version, eval-harness contrast-pair source identifier.
- Grok audit-packet assembly and the §10 audit-packet coverage rule.
- Drift Incident Report emission (§8 of the deep-dive) at the implementation layer.
- The §14 test-plan **runner** mechanics — how the inherited §14 plan is executed (the plan itself is inherited verbatim, not re-authored here).
- HC10 free-work boundary text, HC11 anniversary cost monitoring, HC12 schema forward-compatibility, HC13 MSP retainer one-liner — as build commitments.

### Out of scope

- Writing the generation code. This is a spec; code is gated on §11 sign-off + a separate operator start-build instruction.
- Modifying any runtime detection module, scoring module, or the signed-promotion pipeline. The package **reads** runtime evidence; it never changes how runtime evidence is produced.
- Re-opening or re-deciding any D1–D11 decision. Those are locked by the signed deep-dive; this spec implements them.
- D10 completion. D10 is **overridden, not met** (2026-06-03 operator override). This spec does not represent the override as cheaper-proof validation or market proof.
- Any new external claim, any compliance / certification / insurer-approval / coverage / premium / fraud-prevention claim.
- The v1.1 deferred surfaces (branded landing page, evidence vault, top-level JSON render, pricing field). Those remain gated on cheaper-proof MSP demand evidence per the signed deep-dive.
- Per-carrier variants (D4 forbids them in v1 and later).

---

## §2 Governing Contract

This spec inherits and must not contradict the §13-signed deep-dive. The binding invariants it implements:

- **Five-stage direction lock.** Detection → Verification → Evidence → Audit Trail → Outcome Documentation, one record per stage (D7 / Shape α). Breaking this mapping is a new operator decision, not an implementation detail.
- **Packaging, not new claims.** Every evidence record traces to an artifact the runtime already produces (§4 of the deep-dive). The generator organizes; it never invents.
- **Boundary statement is mandatory and unedited** (§2 of the deep-dive), printed prominently in the rendered package.
- **Protected sentence** (Cyber Insurance lane invariant) and **operator-authored outcome wording** ("Vendor invoice review — payment change reviewed before action") are verbatim contracts; paraphrase is drift.
- **Forbidden-language authority** is `Compliance_and_Trend_Watch_Process.md` §5.1 (D8); the deep-dive §9 twelve-term avoid-list is review guidance only and does not expand the enforced gate.
- **Vocabulary-translation list is locked at five rows for v1** (D6).
- **Two delivery surfaces only for v1**: PDF + Markdown bundle (D3 / D9). No landing page, no vault, no top-level JSON render in v1.
- **Not priced by NorthStar in v1** (D5); no pricing field in schema or `done_declaration.json`; schema stays forward-compatible (HC12).
- **Vendor names silently redacted by default** when tenant policy marks them customer-confidential (D11); no buyer-facing redaction annotation in v1.
- **15 Done Criteria** (§11 of the deep-dive) are the acceptance contract; this spec may not reduce or remove any.
- **Audit-packet coverage rule** (§10): every file touched during generation — read or written — is in the Grok audit packet. No AI-side scoping.
- **§14 test plan** is inherited verbatim; this spec defines only the runner that executes it.

If any instruction in this spec appears to conflict with the signed deep-dive, the signed deep-dive wins and the conflict is a drift incident to be raised to the operator, not silently resolved here.

---

## §3 Generation Pipeline

The generator is a deterministic, staged pipeline. Each stage has a defined input, output, and failure behavior. The pipeline halts on any blocking failure and emits a Drift Incident Report (§8 of the deep-dive); it does not produce a partial package that looks done.

**Pipeline stages, in order:**

1. **Tenant + trigger resolution.** Resolve the target `tenant_id` and the generation trigger (quarterly snapshot, on-demand, or annual full review per D1 / §6.1). On-demand requests for the same tenant queue behind any active job for that tenant — no parallel generation against the same tenant evidence set.
2. **Review-mode resolution.** Quarterly and on-demand runs reuse prior category / structural-exemption assignments. Annual full review re-evaluates category assignment, structural-exemption eligibility, evidence lineage, and superseded-spec references before any record is accepted.
3. **Evidence collection.** Gather the five D7 stage records (§6 of this spec). Each record is built from an existing runtime artifact; no record is synthesized.
4. **Verification + freshness.** Run each record's `verification_command`, compute `content_hash`, stamp `last_verified_at`, and apply the §6.1 freshness policy (with structural-exemption override for valid `signed_by` records). Stale non-exempt records fail the `stale_evidence` gate.
5. **Gate sweep.** Run all nine §7 gates (§7 of this spec) in the defined order. Any gate fail emits a Drift Incident Report; blocking severities halt the pipeline.
6. **Redaction sweep.** Apply the redaction gate, forbidden-language gate, vocabulary-translation gate, and D11 vendor-name redaction against every record and every rendered surface (§8 of this spec).
7. **Render.** Produce the PDF artifact and the Markdown bundle (§9 of this spec), with toolchain identity folded into the manifest (HC6).
8. **Audit-packet assembly.** Collect every file touched (read or written) during stages 1–7 into the Grok audit packet (§10 of this spec).
9. **Grok audit.** Submit the packet + the contract documents to Grok as a negative-feedback auditor (§10 of the deep-dive). Save output to `audit_outputs/`. Every deviation becomes a Drift Incident Report.
10. **Done declaration.** Only when all 15 Done Criteria hold, emit `done_declaration.json` (§11 of this spec). A package with any unresolved blocking drift incident, or a missing Grok audit dated after generation, is **not done** regardless of how the rendered surface looks.

**Determinism requirement.** Two runs against the same tenant evidence set, the same pins (§13 of this spec), and the same source artifacts must produce comparable structured records and comparable rendered Markdown. Non-determinism in the rendered explanation is constrained by the §13 pins.

**Fail-closed requirement.** Every stage fails closed. A stage that cannot complete its check treats the result as fail, not pass. This mirrors §11 criterion 15's fail-closed posture.

---

## §4 Module / Component Boundaries

The generator is **isolated from runtime detection code.** It imports runtime modules read-only to collect evidence; it never modifies detection, scoring, policy, or promotion behavior. This mirrors the Wave 2 isolated-emitter discipline (`Score_Sheet_Candidate_Emit_Implementation_Deep_Dive.md` §3/§9) and the Frontier pipeline guardrails.

Proposed component decomposition (names are implementation-spec proposals, not locked identities):

- **`collector`** — gathers the five D7 stage records from existing runtime artifacts. Read-only against runtime. One sub-collector per stage.
- **`verifier`** — runs `verification_command` per record, computes `content_hash`, applies §6.1 freshness, resolves structural exemptions.
- **`gates`** — the nine §7 gates as independent, individually runnable checks. Each emits a gate-log entry (§7 schema of the deep-dive).
- **`redactor`** — redaction sweep, forbidden-language scan, vocabulary translation, and D11 vendor-name redaction. Reuses the project's existing scanner discipline where possible (see §8 of this spec).
- **`renderer`** — produces the PDF and the Markdown bundle. Owns the pinned toolchain (HC6).
- **`auditpacket`** — assembles the touched-files set and submits to Grok; saves output.
- **`declaration`** — evaluates the 15 Done Criteria and emits `done_declaration.json`.
- **`drift`** — emits Drift Incident Reports (§8 of the deep-dive) on any gate/scan/coverage failure.

**Authority boundaries in code (non-negotiable):**

- The generator never writes to the canonical ledger, never assigns canonical `event_id`s, and never alters signed policy state.
- The generator never edits a signed §11 spec.
- The generator never marks its own output "done" outside the `declaration` component's 15-criteria evaluation.
- The generator never widens scope beyond the email-fraud / inbox-layer MDR surface.
- A shared helper module (JSONL/record construction, hashing, atomic writes, scanning) is permitted only as part of the generator path, mirroring the §14 helper-boundary amendment of the sibling implementation spec; it does not become a standalone tool.

**Atomic writes.** All record and artifact writes are atomic (write to a temp file in the same directory, then rename) so an interrupted run never leaves a half-written package, record, or `done_declaration.json`.

---

## §5 On-Disk Artifact Layout

A generated package is a directory of structured records plus the two render surfaces. The structured records are the source of truth; the renders are derived. Proposed layout (paths relative to a generation output root, e.g. `audit_outputs/cyber_insurance_packages/`):

```
<package_id>/
  manifest.json                         # package manifest: package_id, package_version, tenant_id,
                                         #   generation trigger, toolchain identity+version (HC6),
                                         #   per-file content hashes, top-level package hash (HC7)
  records/                              # stable internal path (D9 / HC7 v1.1-forward-compat)
    detection.json                      # §14.3.1 shape; claim_category detection_evidence
    verification.json                   # §14.3.2 shape; claim_category scoring_explanation
    evidence.json                       # §14.3.3 shape; effective parameter report record
    audit_trail.json                    # §14.3.4 shape; signed policy state + override audit
    outcome_documentation.json          # §14.3.5 record metadata (renders to the .md below)
  rendered/
    package.pdf                         # buyer-facing PDF (D3) — boundary statement, claims, manifest summary
    package.md                          # rendered Markdown explanation (audit/engineering companion)
    README.md                           # who-reads-what; HC13 MSP retainer one-liner; HC10 free-work boundary text
  gates/
    gate_<gate_id>.json                 # one §7 gate-log entry per gate run
  drift/
    drift_<incident_id>.json            # one §8 Drift Incident Report per incident (if any)
  done_declaration.json                 # emitted only when all 15 Done Criteria hold (§11)
```

**Markdown bundle (HC7 / D9).** The deliverable Markdown bundle is a deterministic zipped archive of the package directory (excluding the PDF, which ships alongside). It contains: the rendered Markdown (`rendered/package.md`), the structured records directory (`records/` at the stable internal path), the `README.md`, the `manifest.json`, and per-file content hashes plus a top-level package hash. Loose-directory delivery is **not** v1-acceptable. The structured-records path is stable so a future v1.1 top-level JSON render can reuse the same records without bundle-format churn.

**Package identifier (D5).** `package_id` is constructed from `tenant_id + generation_timestamp` and is opaque to clients. `package_version` carries the spec version (`v1`). No pricing field exists anywhere in the layout (HC12 keeps the schema open to a future v1.1 pricing field without breaking v1 packages).

---

## §6 Evidence Collection & Verification

Each of the five D7 stage records is collected from an existing runtime artifact per the §4 evidence-source map of the deep-dive. The record schema is the §6 deep-dive schema verbatim; this spec defines how each field is populated mechanically.

**Per-stage source binding (v1, D7):**

| Stage | Record | Source artifact | `claim_category` |
|---|---|---|---|
| Detection | `detection.json` | Lift-only invariant test results | `detection_evidence` |
| Verification | `verification.json` | Scoring explanations (internal 0–100 + client-facing 5-axis rubric) | `scoring_explanation` |
| Evidence | `evidence.json` | Per-tenant effective parameter report | `operational_artifact` |
| Audit Trail | `audit_trail.json` | Signed policy state + tenant override audit | `policy_change_control` |
| Outcome Documentation | `outcome_documentation.json` → `package.md` | Inbox Shield sample monthly report | `operational_artifact` |

**Field population mechanics:**

- `evidence_id` — generated, unique within the package.
- `source_artifact_path` — the resolved path to the existing artifact. Must exist at generation time (`broken_link` gate). A missing source is a hard fail.
- `verification_command` — recorded and **executed**; the run result populates `result` (`pass` | `fail` | `stale`).
- `last_verified_at` — UTC timestamp of verification-command execution.
- `content_hash` — `sha256` of `source_artifact_path` content at `last_verified_at`.
- `tenant_id` — the target tenant, or `null` for cross-tenant aggregate evidence explicitly marked in `scope_limitations`.
- `signed_by` — populated for policy/override records; must resolve to an existing signed artifact (`signed_provenance` gate).
- `scope_limitations` — carries the email-fraud / inbox-layer MDR limitation text.

**Freshness enforcement (§6.1 / D2):**

- 30-day categories: `policy_change_control`, `tenant_isolation`, `kill_switch`.
- 90-day categories: `detection_evidence`, `scoring_explanation`, `test_evidence`, `independent_audit`, `operational_artifact`.
- Structural exemption: any record with non-null `signed_by` resolving to a valid signed artifact is freshness-exempt regardless of category.
- Superseded signed artifacts remain exempt as historical evidence but the render must annotate `superseded by <new spec>`, and the annual full review must confirm the package does not rely on the superseded artifact as current architecture.
- **Pre-warning behavior (operational commitment).** The generator surfaces stale-approaching 30-day-category records as a `warning` Drift Incident *before* a threshold breach, so staleness never first appears only at final generation. The exact pre-warning offset is an implementation detail; the invariant is "no surprise staleness at done time."
- **Monthly internal verification path.** A scheduled internal verification re-stamps 30-day-category records so on-demand generation does not fail unexpectedly on stale operational state.

---

## §7 Gate Implementation

The nine §7 gates of the deep-dive are implemented as independent, individually runnable checks. Each emits a gate-log entry (§7 schema). Proposed run order (renderer ordering between gates is an implementation detail per D4, but the order below is the v1 proposal):

| Order | Gate | Concrete check |
|---|---|---|
| 1 | `broken_link` | Every `source_artifact_path` resolves on disk. Hard fail if any missing. |
| 2 | `signed_provenance` | Every policy/override record's `signed_by` resolves to an existing signed artifact. |
| 3 | `stale_evidence` | No non-exempt `last_verified_at` exceeds its §6.1 threshold; exemptions resolve; superseded artifacts annotated. |
| 4 | `claim_validation` | Every claim in the render maps to ≥1 structured record with a non-null `source_artifact_path`. |
| 5 | `redaction` | No secrets, raw bodies, raw credentials, or cross-tenant identifiers in any record or render. |
| 6 | `forbidden_language` | No §9 forbidden phrase used as a NorthStar claim (authority: `Compliance_and_Trend_Watch_Process.md` §5.1; allowed contexts per §9 of the deep-dive). |
| 7 | `vocabulary_translation` | The five-row carrier-jargon translation (D6) is applied at render time. |
| 8 | `scope_boundary` | The §2 boundary statement is present, unedited, prominent. |
| 9 | `audit_packet_coverage` | Every file touched during generation is in the Grok audit packet. Mismatch is a hard fail. |

Each gate is binary pass/fail. A fail emits a Drift Incident Report (§8 of the deep-dive). All gates must pass for the package to reach done state (Done Criteria 3–10). Gates are individually runnable so the §14 runner and operators can invoke a single gate against a package directory for debugging.

---

## §8 Redaction & Language Implementation

The redactor enforces four protections, reusing the project's existing scanner discipline where practical (the Wave 2 `pre_ship_audit.py` scanner minimums in `Score_Sheet_Candidate_Emit_Implementation_Deep_Dive.md` §13.1 are a reference baseline for secret / PII / raw-payload detection).

1. **Redaction sweep (`redaction` gate).** Block raw email bodies, raw credentials/tokens/keys, raw recipient identities beyond what the MSP/SMB chose to include, LLM responses verbatim, internal developer identifiers, and any tenant identifier inside a different tenant's record (Guardrail 11 — sacred). Binary pass/fail; manual operator review only on warnings.
2. **Forbidden-language gate.** Enforce the canonical §5.1 list (D8). Allowed contexts are exactly the deep-dive §9 allowed contexts (boundary statement, non-scope sections, the list itself, bad-claim examples, drift reports). The same phrase is blocking when used as a NorthStar capability/certification/compliance/security/detection/underwriting/outcome claim. The twelve-term operator avoid-list is a **review flag only**, not an enforced gate expansion.
3. **Vocabulary-translation gate.** Apply the five locked rows (D6) at render time: control efficacy → "how well this control works in practice"; regulatory mapping → "cross-reference to specific underwriting questions"; compensating control → "a different control that addresses the same risk"; control attestation framework → "the way we record what each control does"; material weakness → "a meaningful gap." No per-carrier or runtime expansion in v1; additions arrive only via the Frontier Intake → `think_sheet.md` → §11 revision channel.
4. **D11 vendor-name redaction.** When a tenant policy marks vendor names customer-confidential, the renderer silently redacts them in the buyer-facing surfaces. v1 adds **no** buyer-facing redaction annotation; explicit annotation is deferred to v1.1 pending cheaper-proof feedback.

The redactor runs against every structured record AND every rendered surface before the package is considered complete. Any forbidden-language hit, any cross-tenant identifier, or any unsafe payload is a **blocking** Drift Incident.

---

## §9 Render Surfaces

Two surfaces ship in v1 (D3 / D9): a buyer-facing PDF and an audit/engineering Markdown bundle.

**HC6 — Toolchain pinning.** The PDF render toolchain is pinned: render engine identity, engine version, fonts, and template assets. The toolchain identity and version are folded into `manifest.json`. Silent toolchain mutation across versions is a determinism failure and is prevented by the manifest carrying the pinned identity. A render whose toolchain identity does not match the pinned manifest value fails closed.

**HC7 — Bundle format & structured-records path.** The Markdown bundle is a deterministic zipped archive (stable file ordering, stable internal paths). It contains the rendered Markdown, the `records/` directory at its stable internal path, the README, the manifest, per-file content hashes, and a top-level package hash. The structured-records path is stable to keep a future v1.1 top-level JSON render reusable without bundle churn.

**HC7 — Rendered-explanation prompting pattern.** The per-record rendered-Markdown explanation is generated with **two-shot evidence-explanation prompting**: one fraud-row and one legit-row contrast pair sourced from the existing eval harness. Only the positive pattern is named ("two-shot evidence-explanation format"); rejected prompting modes are not enumerated in this spec or in any buyer-facing copy.

**HC8 — Minimal branding rules.** Branding must keep the PDF credible without overclaim or scope drift. Branding must not introduce forbidden-language phrases (§8 of this spec), must not surface repo-internal identifiers (redaction), and must not expand or soften the §2 boundary statement into marketing copy. The boundary statement and protected sentence render verbatim.

**Worst-case-read survivability (§3 of the deep-dive).** The PDF is structured so the underwriter's yes/no-box read and the deep technical read reach the same correct conclusion about what the package covers and does not cover. The boundary statement is prominent; claims trace to records.

---

## §10 Grok Audit Integration

Per §10 of the deep-dive, Grok is a **negative-feedback auditor**, not an approval authority.

**Audit-packet assembly.** The `auditpacket` component collects **every file touched during generation — read or written — into the packet.** This deliberately includes read inputs, not only modified outputs, because the 2026-05-23 weekend Pass-1 wiring bug was a read-from-but-silently-mishandled miss. AI-side scoping of the packet is forbidden. Touched-files vs. packet-contents mismatch is itself a `missing_file_in_audit_packet` drift incident.

**Packet-size reality.** Package generation may read many source artifacts, so the packet can be large. The deep-dive accepts that cost; the 200 KB `complete_gate.py` packet cap (`AGENTS.md` §5) is a *separate* gate for commit-time audits, not the Grok package-generation audit. If a package-generation audit packet must be trimmed for transport, trimming reads is forbidden — the coverage rule is non-negotiable; instead the packet is chunked while preserving full coverage.

**Audit prompt.** Grok receives the package contents, the signed deep-dive, the seven `VISION.md` non-negotiables, the boundary statement, the forbidden-language list, the vocabulary-translation list, and the touched-files packet, and is asked only to identify deviations — not to score, approve, or assess product-market fit.

**Output handling.** Grok output is saved to `audit_outputs/cyber_insurance_evidence_package_<timestamp>.md`. Zero deviations on a complete packet is the compliant state. Every deviation becomes a Drift Incident Report that must be resolved or operator-accepted with an `operator_resolution_note` before done. "Grok said nothing" on a partial packet is **not** compliance.

**Cadence.** Every generation event — quarterly, on-demand, annual — gets its own fresh Grok audit dated after generation finished. Cached audits satisfy a new event only if packet hash, evidence set, and rendered package are byte-identical.

---

## §11 Done Declaration

The `declaration` component evaluates the 15 Done Criteria (§11 of the deep-dive) and emits `done_declaration.json` only when all 15 hold. The declaration is the machine-readable acceptance record; a missing or partial declaration means not-done regardless of the rendered surface.

`done_declaration.json` carries: `package_id`, `package_version`, `tenant_id`, `generated_at`, `done_at`, `criteria_met` (must list all of 1–15), `grok_audit_output` path, `drift_incidents_resolved`, and `operator_signature_evidence_id`. No pricing field (HC12).

**Criterion 14 (operator signature).** The package-level operator sign-off is a `signed_by_operator` evidence record with Matt's own wording. AI-authored sign-off text is forbidden (Authorship Rule). This is the *package* sign-off, distinct from this implementation spec's own §11 sign-off below.

**Criterion 15 (test plan executed).** A package cannot be done unless the §14 test plan has been run end to end at least once and logged through the project's normal test-evidence surfaces. Fails closed.

---

## §12 Drift Incident Handling

The `drift` component emits Drift Incident Reports per the §8 deep-dive schema on: any §7 gate failure (`blocking`), any forbidden-language hit in the render (`blocking`), any cross-tenant identifier in a tenant-scoped record (`blocking`), any vocabulary-leak phrase outside scope (`warning`), any `last_verified_at` approaching threshold under the pre-warning rule (`warning`), and any operator-invoked Hard Stop (`blocking`).

`blocking` incidents prevent done state until resolved or operator-accepted with an `operator_resolution_note`. `warning` incidents allow done state but are recorded in the package's own evidence trail (the package contains the audit of its own generation).

If a `done_declaration.json` omits criterion 15 from `criteria_met`, that is treated as not-done; whether it fires a new `finding_type` enum value or fits an existing one (e.g. `overclaiming` if done state is also asserted) is resolved at build time and may require a §8 enum revision then.

---

## §13 Determinism Pins (parked here by HC7)

The deep-dive (HC7, §13 "Signing does not… lock prompting determinism pins") deliberately keeps these values at the implementation layer so prompt-tuning refinements do not force a §13 re-sign. The v1 pin values below are **operator-accepted 2026-06-03** (advisory scoring by the Technical Verification Layer, operator-selected; see §16). They are refinable without a deep-dive re-sign:

- **Model identity — Grok-4 (xAI).** Matches the provider already used by `audit_tools/` (Grok audit/decision-audit) and the eval harness, so no new provider surface is introduced. The exact pinned identity string is recorded in the package manifest at generation time.
- **Temperature — 0 (lowest deterministic value supported).** Fixed near-zero so two runs against the same inputs produce comparable rendered Markdown (HC7 determinism). Recorded in the manifest.
- **Render-toolchain version — a dedicated pinned PDF toolchain (IQ2).** The operator selected a dedicated PDF dependency over reusing an existing toolchain. The exact engine + version + fonts + template assets are frozen at build-start and folded into the manifest (HC6). Watch-item: the engine must be cross-platform (Linux-primary surface) and is new supply-chain surface to pin, test, and audit.
- **Eval-harness contrast-pair source identifier — fraud row `vf-001` (vendor-invoice fraud, validated risk 88) + a clean legit vendor-email row, both from `core/scoring/eval/fraud_eval_dataset.jsonl`.** On-domain to the vendor-payment-fraud use case and already validated; gives the two-shot prompt a sharp, stable contrast. The exact legit-row identifier is confirmed at build-start and recorded in the manifest.

Two runs against the same inputs and the same pins must produce comparable structured records and comparable rendered Markdown. Pin values are recorded in the package manifest so a given package is reproducible against its own recorded pins.

---

## §14 Test-Plan Runner (executes the inherited §14)

The signed deep-dive §14 defines the v1 test plan verbatim and is **runnable from that section alone**. This spec does not re-author the plan; it defines the **runner** that executes it and the build mechanics around it.

**Inherited contract (do not restate as new decisions):** fictional case `cybins-v1-testplan-vendor-payment-redirect-001`; tenant `bluefin-marine-supplies-demo`; sender `accounts@billing.harborline-marine-services.example`; auth SPF/DKIM/DMARC pass; payment-change + urgency body; one `record_confirmation_request`; one `record_confirmation_outcome` = `payment_change_reviewed_before_action`; five stage records; the verbatim outcome heading "Vendor invoice review — payment change reviewed before action"; the seven §14.4 pass conditions; the §14.5 fixture path, runtime invocation sequence, and output-artifact paths.

**Runner mechanics (this spec's contribution):**

- The runner is an **inline runner created outside the repo at run time** (mirroring rxt-2026-05-30-001), so durable repository evidence stays the fixture, the records, and the activity-log entry — not a runner script committed to the tree. No runtime code is modified by the run.
- The runner imports runtime modules and calls, in order: `ingest_email` → `run_email_risk_scoring_cycle` → `record_confirmation_request` → `record_confirmation_outcome` (outcome `payment_change_reviewed_before_action`) → `run_daily_digest_cycle`, against the §14.5 fixture.
- The five stage outputs are written to the §14.5 output-artifact paths under `audit_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/`. These paths become the `source_artifact_path` values §6 requires.
- The run applies the nine §7 gates against the rendered Outcome Documentation section and evaluates the seven §14.4 conditions as a single boolean (no partial pass).
- **Pass/fail logging.** The run produces one `PROJECT_ACTIVITY_LOG.md` entry (run description, pass/fail, timestamp, the seven conditions evaluated) and, if timing was measured, one `rxt-` record in `REACTION_TIMING_TEST_LOG.md` mirroring rxt-2026-05-30-001. Per `AGENTS.md` §5, any reaction-timing measurement must carry `test_id`, `run_started_at`, `run_finished_at`, scenario, expected, actual, verdict, timing fields, evidence paths, and notes.

This runner satisfies §11 criterion 15 once it has executed end to end at least once with a recorded verdict. It does **not** authorize implementation work beyond the test-plan run.

---

## §15 Commercial-Boundary & Operational Commitments

Mechanical realization of D5 / HC10–HC13:

- **HC10 — Free-work boundary text.** The bundle README carries plain-English text distinguishing what NorthStar provides (the package-generation surface, as a feature of the Inbox Shield runtime) from what the MSP separately charges their SMB clients for (if anything). This protects MSPs from positioning the package as a NorthStar-priced deliverable and protects NorthStar from the free-work perception.
- **HC11 — Anniversary cost monitoring.** The generator tracks Grok API spend for annual full reviews, which cluster on insurance-renewal anniversaries, so concentrated cost spikes are visible rather than absorbed silently.
- **HC12 — Schema forward-compatibility.** The package schema, `done_declaration.json`, and structured records stay open to a v1.1 pricing-field addition without breaking already-generated v1 packages. No pricing field in v1.
- **HC13 — MSP retainer one-liner.** NorthStar provides a single one-line plain-English package summary MSPs can paste into their own retainers, staying inside the §2 boundary statement and the §9 forbidden-language list. It ships as a render-time artifact in the Markdown bundle README, not as a separate marketing document.

---

## §16 Resolved Implementation Decisions (IQ1–IQ7)

**Status:** All seven resolved 2026-06-03 — operator-selected after advisory best/worst scoring by the Technical Verification Layer. These are build-layer decisions; none re-opens a signed deep-dive decision. They are **pending §11 lock** (the spec is still pre-§11) and refinable without a deep-dive re-sign.

- **IQ1. Generation entrypoint — RESOLVED: both.** A callable runtime function plus a thin CLI wrapper (e.g. `evidence_package_generate --tenant <id> --trigger <quarterly|on_demand|annual>`). Rationale: best for tests and operator runs; modest extra surface accepted.
- **IQ2. PDF render engine — RESOLVED: dedicated pinned PDF dependency.** Operator chose a dedicated PDF toolchain over reusing an existing one, for cleaner buyer-facing output. Watch-item (TVL flag): new cross-platform supply-chain surface to pin, test, and audit; exact engine/version frozen in the manifest at build-start (HC6, §13).
- **IQ3. Model + temperature pins — RESOLVED: Grok-4 at temperature 0 (lowest deterministic).** Best-scored: honors HC7's two-shot prompting requirement, reuses the existing xAI provider, keeps runs reproducible. Worst-scored and rejected: "no LLM / templates only" — would contradict the §13-signed HC7 render-pattern commitment. See §13.
- **IQ4. Eval contrast-pair source — RESOLVED: `vf-001` vendor-invoice fraud row + a clean legit vendor-email row from `core/scoring/eval/fraud_eval_dataset.jsonl`.** Best-scored: on-domain, already validated, sharp contrast. Worst-scored and rejected: an ambiguous `needs_review` case or a cross-category pair (muddy wording, weak determinism). See §13.
- **IQ5. Stale pre-warning offset — RESOLVED: 7 days.** Best-scored: enough lead to re-verify 30-day operational evidence before an on-demand package fails; pairs with the monthly re-stamp path. Worst-scored and rejected: 1-day / none (surprise staleness) and overly long offsets (warning noise vs. the Alert-fatigue doctrine). See §6.
- **IQ6. Output root path — RESOLVED: `audit_outputs/cyber_insurance_packages/`.** Best-scored: gitignored, consistent with other generated artifacts, separate from the §14 test-plan output path, audit-discoverable. Worst-scored and rejected: any tracked/committed location (especially under `Client_Documents/`) — tenant-data-leak and audit-cleanliness hazard.
- **IQ7. Build sequencing — RESOLVED: test-plan runner first.** Best-scored: smallest end-to-end slice, directly discharges Done Criterion 15, de-risks before the general generator, keeps audit packets small. Worst-scored and rejected: build the whole generator at once (bigger blast radius, oversized audit packet, more rework).

---

## §17 §11 Sign-Off Placeholder

**Status:** UNSIGNED. This is a placeholder. The sign-off line is operator-authored per the Authorship Rule (`AGENTS.md` §4 / §12, deleted `Human_Written_Communication_Policy.md` failure mode). The assistant does not draft Matt's signature wording or attribute the decision to him.

### What signing this spec would do

1. Lock the build-layer decisions in §3–§15 and the §16 IQ1–IQ7 resolutions (operator-selected 2026-06-03, pending this §11 lock).
2. Confirm the §13 determinism pins (Grok-4 / temp 0 / dedicated PDF toolchain / `vf-001`+legit contrast pair) as the v1 baseline (refinable later without a deep-dive re-sign).
3. Authorize Pass-1 implementation work **only** after a separate explicit operator start-build instruction, and only within the scope above.

### What signing this spec would NOT do

- Authorize code by itself (a separate operator start-build instruction is still required).
- Re-open or relax any signed deep-dive decision (D1–D11, HC6–HC13, the 15 Done Criteria, the audit-packet coverage rule).
- Represent the D10 override as cheaper-proof validation or market proof.
- Permit any AI-side scoping of the Grok audit packet.
- Override any of the seven `VISION.md` non-negotiables.
- Authorize any new external, compliance, certification, insurer-approval, coverage, premium, or fraud-prevention claim.

### Audit precondition (queue Audit List item 3)

Before this implementation spec can be called ready/signed, the audit must verify: the cheaper-proof gate was satisfied or explicitly overridden by Matt with a recorded reason (overridden 2026-06-03); the deep-dive is §13-signed (it is); implementation scope matches the signed spec with no scope creep; and no claim falls outside the email-fraud / inbox-layer MDR boundary. That audit runs at the readiness/commit boundary, not at draft time.

### Sign-off line (operator-authored — placeholder, do not fill in for Matt)

> _Pending. Matt authors this line when he chooses to sign. Operating entity name to be set once the project rename is decided._

---

## Cross-references

- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` — §13-SIGNED governing contract. This spec implements it and may not contradict it.
- `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` — §11 SIGNED 2026-05-26; canonical forbidden-language authority (§5.1) and compliance-claim boundary (§5).
- `4. Product_Roadmap/Score_Sheet_Candidate_Emit_Implementation_Deep_Dive.md` — sibling implementation-spec template + isolated-emitter / scanner discipline reference.
- `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` — rubric whose outputs feed the Verification-stage scoring-explanation record.
- `VISION.md` — seven non-negotiables that govern this spec.
- `PROJECT_ACTIVITY_LOG.md` — 2026-06-03 D10 override + §13 sign-off entries; project-rename status.
- `PROJECT_BUILD_AND_AUDIT_QUEUE.md` — Build List item 3 (this spec); Audit List item 3 (the gate before it ships).

---

**End of draft. Pre-§11. No implementation work, code, or commit is authorized by this document.**
