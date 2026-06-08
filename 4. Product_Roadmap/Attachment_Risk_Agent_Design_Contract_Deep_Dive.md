# Attachment Risk Agent Design Contract — Spec-First Deep Dive

**Status:** DRAFT 2026-06-08. Authored as Build Sequencer CYCLE 13 for swarm agent #30. This draft is **not signed** and authorizes **no code**, **no runtime wiring**, **no detector-logic change**, **no default-registry registration**, **no production dispatch**, **no Evidence Stage 2/3 promotion**, and **no autonomous action**. §11 signature is operator-only.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey**. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (governing template; §3 contract block, §6 Evidence Stage / Promotion / Demotion model, §7.0 detector-immutability boundary)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#30 Attachment Risk; Build Sequencer candidate)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/precursor/attachment_classifier.py` (immutable underlying detector function — `score_attachment_risk`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent` protocol, `AgentContribution`, `DecisionEvidenceRecord`)
- `VISION.md` (Stage A = analyze + recommend only; seven non-negotiables)

---

## Agent Design Contract block

**Boundary:** This contract governs the future Attachment Risk **agent wrapper** around `score_attachment_risk`. It is additive governance under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend attachment classification, extension sets, scoring bands, encrypted-archive patterns, double-extension rules, precursor overlay behavior, ingest-hook behavior, tenant override behavior, or any existing pipeline wiring. Those remain governed by their prior authorization and are immutable here.

| Field | Value |
|---|---|
| Agent name | Attachment Risk Agent (`AttachmentRiskAgent`) |
| Swarm inventory ID | #30 — Attachment Risk |
| Canonical layer | 2 — Detection |
| Canonical team / case type | Attachment / ransomware precursor; static attachment-metadata evidence in inbound email |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed. Validated on synthetic tests only; intentionally NOT registered in `build_default_registry` / production dispatch. Advancement to Stage 2 requires template §6.2 conditions and a Matt-signed promotion record. |
| Role | Produce facts-only attachment-risk evidence by running the deterministic static attachment classifier over the email's attachment metadata and contributing detected attachment indicator names to the case Decision Evidence Record. |
| Boundary | The detector is not the decision. The agent must not decide ransomware, declare an attachment malicious, approve/deny mail, block/quarantine, execute or detonate attachment content, call out to sandbox/network services, mutate scores, or alter the signed client-facing rubric. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no attachment execution; no macro execution; no archive extraction; no file fetch; no sandbox detonation; no AV/reputation lookup; no buyer-facing claim; no default-registry registration; no production dispatch at Evidence Stage 1; no emission of the numeric `AttachmentRiskAssessment.risk_score` as an interpretation field. |
| Inputs | One `EMAIL_INBOUND` Blackboard record located via `MissionContext.source_record_id` on the tenant's own path; reads `attachments` metadata only (`EmailAttachmentMeta` values already on the Blackboard). No raw attachment bytes are read by the wrapper. |
| Outputs | One `AgentContribution` (layer 2): `observed_facts` = detected attachment-risk indicator names from the existing closed `PrecursorIndicator` vocabulary. No verification/challenge/evidence/score field is emitted. |
| Evidence emitted | The attachment-risk indicator names actually observed, such as `double_extension_attachment`, `executable_attachment`, `iso_or_disk_image_attachment`, `macro_enabled_office_document`, `html_smuggling_attachment`, and `encrypted_archive_attachment`. Raw filenames, hashes, content references, extracted text, MIME values, and numeric scores do not cross into the contribution. |
| Data minimization | No raw filename, path, hash, content reference, extracted text, PDF metadata, MIME type, attachment bytes, or attachment body snippet is emitted in the contribution. `inputs_digest` is a SHA-256 of the email payload, not the payload itself. |
| Tenant isolation | Reads only the tenant's own Blackboard path (`blackboard_path(root, environment, tenant_id)`); tenant A's email attachments never influence tenant B. Contribution writes are gated by registry `allowed_write_types` (`AGENT_CONTRIBUTION`). |
| Two-pass role | Pass 1 (detect) only. `challenge()` returns `None` — Pass 2 is a Verification / Challenge-layer concern. |
| Decision Evidence Record contribution | `observed_facts`: detected attachment-risk indicator names; `interpretations`: none; `assumptions`: the `EMAIL_INBOUND` record attachment metadata is as ingested; `missing_evidence`: the agent does not execute, detonate, parse, fetch, or reputation-check attachment content and cannot prove payload safety; `recommended_verification`: none emitted at this layer; `final_outcome_contribution`: suspicious-attachment facts only; `retest_or_learning_record`: every real-case miss or demotion trigger becomes a permanent regression test per template §6.5. |
| Human review trigger | None authored by this agent; the Commander and downstream layers own escalation. |
| Verification trigger | None authored by this agent (Layer 2); suspicious-attachment facts can feed future Verification / Challenge agents. |
| Scoring / action posture | Facts-only contribution. The agent performs no scoring lift itself; the underlying detector's existing score and precursor overlay behavior remain unchanged and out of scope. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers and tests until a later signed promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; Stage A router guard rejects autonomy. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires: clean test suite, zero open test failures, Matt review of >= 3 real email samples confirming observed facts, `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. |
| Demotion conditions | Per template §6.3. Automatic: regression failure, Drift Watch anomaly, evidence-chain integrity failure, or out-of-layer field write. Matt-signed: auditor pattern flag, real miss that misled downstream Verification, or signed Challenge contradiction pattern. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent regression test. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires the real-sample review in §6.2; Stage 3 requires Drift Watch active. |
| Failure modes | See §5. |
| Required tests | See §6 — wrapper tests must prove known-bad fire, known-good no-fire, multi-attachment handling, persistence, guardrails, no registry default, no execution/network behavior, and no score/raw attachment metadata leakage. |
| Audit requirements | Any contract signature, implementation, or revision remains subject to `complete_gate.py`. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, and canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At §11 signature, this agent is at **Evidence Stage 1** only. No build authorization is granted for Evidence Stage 2/3 registration until §6.2 promotion conditions are satisfied and a separate promotion record is signed. The underlying detector and existing pipeline wiring are unchanged by this contract. |

---

## §0 Purpose

Promote swarm agent #30 Attachment Risk from an existing deterministic detector surface into a governed-agent path by giving the future wrapper a signed Agent Design Contract. The wrapper will follow the proven `analyze()` -> `AgentContribution` -> Blackboard -> in-memory DER path already used by Header Analysis, Ghost Thread, Email Authentication, and Link Inspection.

This contract is the governance step. It does not build runtime code until §11 signature / Build Authorization.

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing a future `AttachmentRiskAgent` wrapper as a Layer 2 Detection agent.
- Evidence Stage 1 (Synthetic) declaration at signature.
- Facts-only contribution of the existing detector's closed indicator names.
- Explicit preservation of existing `score_attachment_risk` behavior and precursor overlay behavior.

### Out of scope
- Any change to `score_attachment_risk`, `attachment_inspector`, extension sets, scoring bands, encrypted-archive patterns, double-extension detection, class refinement, or overlay behavior.
- Emitting the numeric `AttachmentRiskAssessment.risk_score` through the agent contribution.
- Emitting raw filenames, content references, hashes, MIME values, extracted text, PDF metadata, raw attachment bytes, or body snippets.
- Executing attachments, running macros/scripts, extracting archives, detonation, sandbox browse, AV/reputation lookup, DNS/network/HTTP calls, or file fetch.
- Registering the agent in `build_default_registry` or production dispatch.
- Changing the Client-Facing 5-Axis Email Scoring Rubric, recommended risk floor behavior, or tenant override behavior.
- Any autonomous action, buyer-facing claim, or Stage B/C autonomy.
- Evidence Stage 2/3 promotion.

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

- **D1 — Identity.** Attachment Risk is a Layer 2 Detection agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = attachment_risk_001`.
- **D2 — Detector immutability.** This contract changes no attachment classification, extension vocabulary, scoring band, indicator vocabulary, overlay behavior, tenant override, ingest hook, or pipeline wiring. It governs the wrapper only.
- **D3 — Facts-only contribution.** The agent emits only closed `PrecursorIndicator` attachment-risk indicator names as `observed_facts`. It emits no score, no filename/hash/content reference, no interpretation, no verification field, and no challenge/evidence field.
- **D4 — Input surface.** The agent reads exactly one `EMAIL_INBOUND` record via `MissionContext.source_record_id`, using the existing `EmailInboundPayload.attachments` metadata list only.
- **D5 — Persistence + rollout.** Contributions persist via the registry-gated `AGENT_CONTRIBUTION` route. The agent is NOT in `build_default_registry`; it is wired only by explicit callers until a signed promotion.
- **D6 — Stage A / no autonomy.** No block/quarantine/deny/reject; no autonomous action; the agent authors no disposition.
- **D7 — Evidence Stage governance.** Evidence Stage 1 at signing; promotion and demotion follow template §6.2 / §6.3; progressive hardening §6.5 applies.
- **D8 — Static-only inspection.** The wrapper never executes, detonates, extracts, fetches, or interprets raw attachment bytes. It calls the existing static metadata detector only.
- **D9 — Tests are the Stage 1 evidence.** The wrapper test suite must include known-bad fire, known-good no-fire, documented edge behavior, persistence, registry rejection, no default registration, no execution/network behavior, and no leakage assertions before the build can close.

---

## §3 Data surface and output schema

- **Reads:** `EmailInboundPayload.attachments` (`EmailAttachmentMeta` values already stored on the Blackboard).
- **Underlying detector:** `score_attachment_risk(meta)` returns `AttachmentRiskAssessment(classification, risk_score, indicators)` for each attachment.
- **Emits:** `AgentContribution(agent_id="attachment_risk_001", layer=2, observed_facts=<deduped indicators in attachment/source order>)`.
- **Does not emit:** `AttachmentRiskAssessment.risk_score`, `classification`, raw filename, content reference, SHA-256, MIME type, size, extracted text, PDF metadata, raw attachment bytes, or body snippets.

---

## §4 Evidence Stage declaration

- **Current Evidence Stage at signature: 1 — Synthetic.** Only synthetic-fixture validation will exist at initial build.
- **To reach Stage 2 (Supervised):** all template §6.2 Stage 1->2 conditions, including Matt review of >= 3 real email samples and a signed `PROMOTION` entry.
- **To reach Stage 3 (Production):** template §6.2 Stage 2->3 conditions, including Drift Watch active. Reaching Stage 3 grants no autonomous action.
- **Demotion:** template §6.3 triggers apply.

---

## §5 Failure modes

- **Authority drift** — treating attachment-risk facts as a final malware/ransomware decision. Mitigation: facts-only contribution; Commander/downstream layers own disposition.
- **Score leakage** — emitting `AttachmentRiskAssessment.risk_score` as a DER interpretation or risk field. Mitigation: D3 and layer-field schema boundary.
- **Raw attachment metadata leakage** — writing filename, hash, content reference, MIME value, extracted text, or PDF metadata into the contribution. Mitigation: indicator-only output and no raw evidence fields.
- **Execution creep** — executing, detonating, extracting, or opening attachment content. Mitigation: D8; existing detector is static metadata only.
- **Over-certainty on benign business attachments** — routine invoices/payment requests may carry low detector scores without malicious indicators. Mitigation: this agent emits facts only; no-empty-indicator score becomes no contribution fact.
- **Multi-attachment confusion** — one dangerous attachment among benign attachments is lost or duplicated. Mitigation: source-order aggregation with dedupe and synthetic multi-attachment tests.
- **Cross-tenant read** — reading another tenant's email record. Mitigation: tenant-scoped Blackboard path + `source_record_id` guard.
- **Stage creep** — registering in default dispatch or production while at Evidence Stage 1. Mitigation: explicit default-registry exclusion.

---

## §6 Required tests

The implementation slice must add focused tests proving:

1. `AttachmentRiskAgent` satisfies the shared `Agent` protocol.
2. A known-bad email with an executable / double-extension attachment produces expected attachment indicator facts and a `suspicious` DER disposition.
3. A known-good email with no attachments or routine attachment metadata produces empty facts and a `clear` DER disposition.
4. Multiple attachments aggregate indicator facts in deterministic source order with dedupe.
5. Contribution persistence writes through `submit_agent_contribution` and round-trips through `AgentContributionPayload`.
6. `challenge()` returns `None`.
7. Missing, unknown, and wrong-type `source_record_id` raise `GovernanceError`.
8. Unauthorized registry writes are rejected.
9. `digest_email` is deterministic.
10. `build_default_registry()` does not include `attachment_risk_001`.
11. Contributions do not contain numeric score, classification, raw filename, hash, MIME value, content reference, extracted text, or body snippet.
12. Tests monkeypatch / guard against any wrapper network, subprocess, exec/eval, archive extraction, or file-open behavior; the wrapper must only call the static detector over stored metadata.

---

## §7 Audit requirements

This contract draft and any implementation must be gated through `complete_gate.py`. The implementation manifest must include this contract, the Agent Design Contract Template, the attachment detector file, the wrapper file, and the focused test file.

---

## §10 Open Questions (operator-only)

No design fork is open in this draft. §11 signature confirms D1-D9 and authorizes the Evidence Stage 1 wrapper build only.

---

## §11 Sign-off

PENDING. Operator-authored signature required before runtime implementation.

> [Matt Nichol — Attachment Risk Agent Design Contract — date]
