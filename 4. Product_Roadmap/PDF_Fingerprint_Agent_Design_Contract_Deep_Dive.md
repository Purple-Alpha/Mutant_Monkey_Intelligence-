# PDF Fingerprint Agent Design Contract — Boundary / Unblock Deep Dive

**Status:** §11 SIGNED 2026-06-08 by Matt Nichol. Authored by the LIVE Build Map after the clean pure-wrap BREADTH runway was exhausted; this is the named UNBLOCK action for swarm #31 PDF Fingerprint. The existing `assess_document_metadata_fingerprint` detector is useful and already signed, but it mutates the per-tenant Vendor Baseline Store (`check_signal` -> `ingest_signal`) and therefore required an explicit boundary contract before becoming a governed swarm agent. Signing locks D1-D10 and authorizes the Evidence Stage 1 (Synthetic) `PDFFingerprintAgent` wrapper build + focused tests **only**. It authorizes **no detector-logic change**, **no Vendor Baseline Store change**, **no new signal type**, **no production dispatch**, **no default-registry registration**, **no real-customer-data handling**, **no Evidence Stage 2/3 promotion**, **no scoring/rubric change**, **no PDF byte parsing**, and **no autonomous action**.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey** only where separately signed buyer-facing specs require it. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Build_Map_Deep_Dive.md` (LIVE build authority; pure-wrap runway exhausted -> UNBLOCK highest-priority blocked Detection candidate)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (governing template; Evidence Stage model)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#31 PDF Fingerprint; `NEEDS_SIGNED_CONTRACT`)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `4. Product_Roadmap/Document_Metadata_Fingerprinting_Deep_Dive.md` (§11-signed detector contract; v1 metadata-only, check-before-ingest, floor 75, no PDF byte parsing)
- `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md` (baseline primitive contract; hash-only per-tenant store, closed enum, kill switch, audit write)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/document_metadata_detector.py` (`assess_document_metadata_fingerprint`, `vendor_domain_from_sender`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/production_state/vendor_baseline/store.py` (`check_signal`, `ingest_signal`, `SignalState`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent`, `AgentContribution`, `DecisionEvidenceRecord`)
- `VISION.md` (Stage A = analyze / recommend / evidence only; seven non-negotiables)

---

## Agent Design Contract block

**Boundary:** This contract governs the future PDF Fingerprint **agent wrapper** around the existing signed `assess_document_metadata_fingerprint` detector. It is additive governance under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend the §11-signed Document Metadata Fingerprinting detector contract, the Vendor Baseline Store primitive, the `pdf_producer_fingerprint` closed enum, check-before-ingest ordering, risk floor, profile gating, kill-switch behavior, tenant isolation, or existing scoring overlay behavior.

| Field | Value |
|---|---|
| Agent name | PDF Fingerprint Agent (`PDFFingerprintAgent`) |
| Swarm inventory ID | #31 — PDF Fingerprint |
| Canonical layer | 2 — Detection |
| Canonical team / case type | Attachment / document-integrity / BEC precursor; PDF Producer/Creator metadata drift against per-tenant vendor memory |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed. Validation is synthetic-only and uses isolated tenant baseline state. Intentionally NOT registered in `build_default_registry` / production dispatch. Advancement requires template §6.2 and Matt-signed promotion. |
| Role | Produce facts-only document-tooling fingerprint evidence by running the existing metadata-only detector against one inbound email's attachment metadata and comparing each unique Producer/Creator fingerprint against that tenant/vendor's Vendor Baseline Store. |
| Boundary | This is a stateful Detection agent, not a pure detector wrap. The only authorized mutation is the existing signed detector's `pdf_producer_fingerprint` baseline ingest for the same tenant/vendor/fingerprint being assessed, in the existing check-before-ingest order. The agent must not create new signal types, write raw metadata, bypass the kill switch, change TTL/salt/hash behavior, parse PDF bytes, OCR files, fetch attachments, call the network, or treat a new/stale fingerprint as fraud proof. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no declaration that a PDF is forged; no payment approval/denial; no PDF byte parsing; no OCR; no attachment fetch; no sandbox detonation; no network/HTTP/DNS/WHOIS/reputation lookup; no Vendor Baseline Store schema/enum/TTL/salt/hash change; no cross-tenant baseline; no raw Producer/Creator persistence outside the existing hash-only store; no buyer-facing claim; no default-registry registration; no production dispatch at Evidence Stage 1; no Evidence Stage 2/3 promotion. |
| Inputs | One `EMAIL_INBOUND` Blackboard record located via `MissionContext.source_record_id`, plus caller-supplied `tenant_id`, `vendor_domain` (or strictly normalized sender-derived vendor domain), and aware `now`. Reads `EmailInboundPayload.attachments[*].pdf_metadata.producer/creator` only. No raw PDF bytes. |
| Outputs | One `AgentContribution` (layer 2): `observed_facts` = closed document-metadata indicator names (`new_pdf_producer_fingerprint`, `expired_pdf_producer_fingerprint`) and minimal attachment-field facts when needed (`pdf_metadata_field:producer`, `pdf_metadata_field:creator`). No verification/challenge/evidence/score field is emitted. |
| Evidence emitted | Closed indicator names from `DocumentMetadataAssessment.indicators`, plus optional non-sensitive counts such as `document_metadata_finding_count:<n>` if the wrapper needs a stable DER fact. Raw Producer/Creator values, redacted displays, filenames, attachment indexes, signal hashes, risk floor, explanation text, and recommended verification wording do not cross into the contribution at Stage 1. |
| Data minimization | The contribution emits no raw Producer/Creator string, no redacted display, no filename, no attachment index, no PDF metadata object, no signal hash, no vendor-domain prose, no raw email body, no PDF bytes, and no file path. The Vendor Baseline Store remains hash-only per its signed primitive; `inputs_digest` is a SHA-256 of the email/boundary input, not the input itself. |
| Tenant isolation | Reads and writes only through the tenant-scoped Vendor Baseline Store path for the `tenant_id` supplied by the case context. Stage 1 tests must use isolated synthetic tenant IDs and reset/contain baseline state. Tenant A's fingerprints never affect tenant B. |
| Two-pass role | Pass 1 Detection only. `challenge()` returns `None`; Verification / Challenge layers decide whether document-integrity evidence changes the case posture. |
| Decision Evidence Record contribution | `observed_facts`: closed document-metadata indicator names/counts only; `interpretations`: none; `assumptions`: attachment metadata was extracted upstream and vendor identity was supplied/normalized by caller; `missing_evidence`: the agent does not parse PDF bytes, inspect visual content, verify invoice legitimacy, or prove forgery; `recommended_verification`: none emitted at Layer 2; `final_outcome_contribution`: document-tooling fingerprint drift facts only; `retest_or_learning_record`: every real-case miss or demotion trigger becomes a permanent regression test per template §6.5. |
| Human review trigger | None authored by this agent. Downstream Command / Verification layers own review routing. |
| Verification trigger | None authored by this agent at Layer 2. A new/expired fingerprint can feed future Verification/Challenge layers and may pair with payment-change evidence, but this agent does not itself initiate verification. |
| Scoring / action posture | Facts-only contribution. The wrapper does not emit `recommended_risk_floor`, `recommended_action`, explanation, or verification wording. Existing scoring overlay behavior from the signed detector spec remains unchanged and out of scope. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers/tests until a later signed promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; Stage A router guard rejects autonomy. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires clean suite, zero open test failures, Matt review of >= 3 supervised PDF/invoice samples with known tenant/vendor boundaries, a `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. Any real-customer sample use requires the separate real-data/depth authorization gate. |
| Demotion conditions | Per template §6.3. Automatic: regression failure, cross-tenant baseline contamination, raw metadata leakage, kill-switch bypass, baseline write outside `pdf_producer_fingerprint`, out-of-layer contribution field write, unexpected network/subprocess/PDF-byte read, or scoring/rubric mutation. Matt-signed: auditor pattern flag, real miss that misled downstream Verification, or signed Challenge contradiction pattern. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent regression test. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires supervised PDF/invoice samples with operator-reviewed expected outcomes. Stage 3 requires Drift Watch active and real-data controls signed/open. |
| Failure modes | See §5. |
| Required tests | See §6 — wrapper tests must prove known-new and known-expired fire, known fingerprint no-fire, check-before-ingest preservation, synthetic baseline isolation, kill-switch inheritance, persistence, guardrails, no default registry, no PDF-byte/network/subprocess behavior, and no score/raw metadata/hash/filename leakage. |
| Audit requirements | Any contract signature, implementation, or revision remains subject to `complete_gate.py`. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `Document_Metadata_Fingerprinting_Deep_Dive.md`, `Vendor_Baseline_Store_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, and canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At §11 signature, this agent is at **Evidence Stage 1** only. No build authorization is granted for Evidence Stage 2/3 registration, default registry, production dispatch, real-customer-data handling, new baseline signal types, scoring/rubric changes, or detector/store behavior changes until promotion conditions in §6.2 are satisfied and a separate promotion/authorization record is signed. |

---

## §0 Purpose

Unblock swarm #31 PDF Fingerprint by defining the state boundary that kept it from being a clean pure-detector wrap. Unlike the recent body/URL/attachment wrappers, #31's detector legitimately uses per-tenant memory: it compares PDF Producer/Creator fingerprints against the Vendor Baseline Store and then ingests the observed fingerprint so future observations become known.

The purpose of this contract is not to make that statefulness disappear. The purpose is to govern it: exactly one signed baseline signal type, exactly one tenant/vendor scope, existing check-before-ingest ordering, hash-only storage, no raw metadata leakage, no PDF byte parsing, and no autonomous action.

This contract is the governance step. It does not build runtime code until §11 signature / Build Authorization.

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing a future `PDFFingerprintAgent` wrapper as a Layer 2 Detection agent.
- Evidence Stage 1 (Synthetic) declaration at signature.
- Explicit state boundary for the existing signed detector's Vendor Baseline Store read/write behavior.
- Facts-only contribution of closed document-metadata indicator names/counts.
- Preservation of existing `assess_document_metadata_fingerprint` behavior and the §11-signed Document Metadata Fingerprinting contract.

### Out of scope
- Any change to `assess_document_metadata_fingerprint`, check-before-ingest ordering, `DocumentMetadataAssessment`, risk floor 75, profile gating, overlay behavior, Vendor Baseline Store schema, signal enum, TTL, salt/hash derivation, kill-switch behavior, or audit behavior.
- Adding new baseline signal types or implementing the unsigned Vendor Baseline Signal Type Enum Revision draft.
- Emitting `recommended_risk_floor`, `recommended_action`, explanation text, verification wording, raw Producer/Creator values, redacted display strings, filenames, attachment indexes, signal hashes, raw email body, PDF metadata objects, PDF bytes, or file paths through the agent contribution.
- PDF byte parsing, OCR, password-protected PDF handling, visual invoice analysis, attachment fetching, detonation, sandbox browse, AV/reputation lookup, DNS/network/HTTP calls.
- Registering the agent in `build_default_registry` or production dispatch.
- Real-customer-data handling or Evidence Stage 2/3 promotion.
- Any autonomous action, buyer-facing claim, or Stage B/C autonomy.

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

- **D1 — Identity.** PDF Fingerprint is a Layer 2 Detection agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = pdf_fingerprint_001`.
- **D2 — Stateful boundary.** This is not a pure-detector wrapper. The only authorized state mutation is the existing signed detector's `vendor_baseline.ingest_signal(... signal_type="pdf_producer_fingerprint" ...)` call for the same tenant/vendor/fingerprint being assessed, after `check_signal` runs first.
- **D3 — Detector/store immutability.** This contract changes no document-metadata detector logic, Vendor Baseline Store behavior, enum, schema, normalization, TTL, salt/hash derivation, kill switch, audit behavior, scoring/rubric behavior, or pipeline wiring. It governs the wrapper only.
- **D4 — Facts-only contribution.** The agent emits only closed document-metadata indicator names and bounded non-sensitive counts. It emits no score, action, explanation, verification wording, raw metadata, redacted display, filename, signal hash, interpretation, verification field, challenge field, or evidence field.
- **D5 — Input surface.** The agent reads exactly one `EMAIL_INBOUND` record via `MissionContext.source_record_id`, uses `EmailInboundPayload.attachments[*].pdf_metadata` only, and takes a caller-owned `vendor_domain`/aware `now`. No raw PDF bytes are read.
- **D6 — Persistence + rollout.** Contributions persist via the registry-gated `AGENT_CONTRIBUTION` route. The agent is NOT in `build_default_registry`; it is wired only by explicit callers until signed promotion.
- **D7 — Stage A / no autonomy.** No block/quarantine/deny/reject; no payment decision; no forgery declaration; no autonomous action; the agent authors no disposition.
- **D8 — Evidence Stage governance.** Evidence Stage 1 at signing; promotion and demotion follow template §6.2 / §6.3; progressive hardening §6.5 applies.
- **D9 — Metadata-only inspection.** The wrapper never parses PDF bytes, fetches files, OCRs, detonates, uses reputation, or performs network/subprocess calls. It relies only on upstream bounded `pdf_metadata`.
- **D10 — Tests are the Stage 1 evidence.** The wrapper test suite must include new/known/expired states, check-before-ingest preservation, tenant isolation, kill-switch inheritance, persistence, default-registry exclusion, no network/subprocess/PDF-byte behavior, and no score/raw metadata/hash/filename leakage before the build can close.

---

## §3 Data surface and output schema

- **Reads:** one `EmailInboundPayload` from the tenant's Blackboard path; `attachments[*].pdf_metadata.producer/creator`; caller-owned `vendor_domain`; aware `now`.
- **Underlying detector:** `assess_document_metadata_fingerprint(tenant_id, vendor_domain, email, now)` returns `DocumentMetadataAssessment`.
- **Emits:** `AgentContribution(agent_id="pdf_fingerprint_001", layer=2, observed_facts=<closed indicator/count facts>)`.
- **Allowed fact vocabulary:** `new_pdf_producer_fingerprint`, `expired_pdf_producer_fingerprint`, `document_metadata_finding_count:<n>`, `document_metadata_extracted_count:<n>`.
- **Does not emit:** `recommended_risk_floor`, `recommended_action`, `DocumentMetadataFinding.explanation`, `recommended_verification`, `redacted_display`, `signal_hash`, `attachment_filename`, `attachment_index`, `vendor_domain`, raw metadata, PDF bytes, file path, or email body.

---

## §4 Evidence Stage declaration

- **Current Evidence Stage at signature: 1 — Synthetic.** Only synthetic-fixture validation will exist at initial build. Synthetic tests may exercise isolated Vendor Baseline Store state, but no real tenant data.
- **To reach Stage 2 (Supervised):** all template §6.2 Stage 1->2 conditions, including Matt review of >= 3 supervised PDF/invoice samples with expected outcomes and a signed `PROMOTION` entry. Real-customer samples require separate real-data/depth authorization.
- **To reach Stage 3 (Production):** template §6.2 Stage 2->3 conditions, including Drift Watch active. Reaching Stage 3 grants no autonomous action.
- **Demotion:** template §6.3 triggers apply.

---

## §5 Failure modes

- **Silent state mutation creep** — wrapper writes baseline state outside the signed detector path or outside `pdf_producer_fingerprint`. Mitigation: D2/D3 and tests spying `check_signal`/`ingest_signal`.
- **Check/ingest inversion** — first observation is swallowed as known because ingest happens before check. Mitigation: D2 and explicit ordering test.
- **Raw metadata leakage** — Producer/Creator strings, redacted displays, filenames, attachment indexes, or hashes enter the contribution. Mitigation: D4 / §3 allowed vocabulary.
- **Forgery overclaim** — new PDF tooling is treated as proof of fraud or forged invoice. Mitigation: Layer 2 facts-only boundary and no interpretation/action fields.
- **Tenant contamination** — one tenant/vendor baseline affects another. Mitigation: tenant-scoped baseline state and synthetic isolation tests.
- **PDF-byte scope creep** — wrapper reads/parses/fetches attachments, OCRs, or introduces PDF parser dependencies. Mitigation: metadata-only D9 and no file/network/subprocess tests.
- **Kill-switch bypass** — baseline APIs are bypassed or mocked around in production path. Mitigation: inherited Vendor Baseline Store entry points and kill-switch test.
- **Score/rubric mutation** — wrapper changes risk floors, scoring overlays, or client-facing rubric behavior. Mitigation: D3/D4; wrapper emits facts only.
- **Stage creep** — default registry or production dispatch while at Evidence Stage 1. Mitigation: D6 test.

---

## §6 Required tests

The implementation slice must add focused tests proving:

1. `PDFFingerprintAgent` satisfies the shared `Agent` protocol.
2. First-seen PDF Producer/Creator metadata emits `new_pdf_producer_fingerprint` fact and persists via `AgentContribution`.
3. Known fingerprint emits no suspicious indicator on a second run for the same tenant/vendor/fingerprint.
4. Expired fingerprint emits `expired_pdf_producer_fingerprint`.
5. `check_signal` is called before `ingest_signal` for each unique fingerprint.
6. Duplicate fingerprints in one email are deduped for baseline calls.
7. Creator-only path works.
8. Non-PDF / non-invoice attachments are ignored.
9. Missing `source_record_id`, unknown record, wrong record type, invalid `vendor_domain`, or naive `now` fail closed.
10. Tenant isolation: same fingerprint under two tenant IDs does not share baseline state.
11. Kill-switch inheritance is preserved through Vendor Baseline Store entry points.
12. Contribution persistence writes through `submit_agent_contribution` and round-trips through `AgentContributionPayload`.
13. `challenge()` returns `None`.
14. Unauthorized registry writes are rejected.
15. `digest_email` / equivalent input digest is deterministic.
16. Agent is not in `build_default_registry()`.
17. Contribution emits no `recommended_risk_floor`, `recommended_action`, explanation, verification wording, raw Producer/Creator value, redacted display, filename, attachment index, signal hash, vendor domain, PDF bytes, or file path.
18. Wrapper performs no network/subprocess/PDF-byte read and imports no PDF parser dependency.
19. Wrapper does not change scoring overlay, client-facing rubric, Vendor Baseline Store enum/schema/TTL/salt/hash behavior, or detector logic.

---

## §7 Audit requirements

This contract draft and any implementation must be gated through `complete_gate.py`. The implementation manifest must include this contract, the Agent Design Contract Template, the signed Document Metadata Fingerprinting spec, the Vendor Baseline Store spec, the detector file, the Vendor Baseline Store file, the wrapper file, and the focused test file.

---

## §10 Open Questions (operator-only)

No design fork is open in this draft. §11 signature confirms D1-D10 and authorizes the Evidence Stage 1 synthetic `PDFFingerprintAgent` wrapper build + focused tests only.

---

## §11 Sign-off

SIGNED. This signature locks D1-D10 and authorizes the Evidence Stage 1 (Synthetic) `PDFFingerprintAgent` wrapper build + focused tests only; no detector-logic change, no Vendor Baseline Store change, no new signal type, no default-registry registration, no production dispatch, no real-customer-data handling, no Evidence Stage 2/3 promotion, no scoring/rubric change, no PDF byte parsing, no autonomous action.

> Matt Nichol June 8th 2026
