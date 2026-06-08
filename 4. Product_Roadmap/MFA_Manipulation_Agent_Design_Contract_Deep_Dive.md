# MFA Manipulation Agent Design Contract — Spec-First Deep Dive

**Status:** DRAFT 2026-06-08. Authored as Build Sequencer CYCLE 15 for swarm agent #24. This draft is **not signed** and authorizes **no code**, **no runtime wiring**, **no detector-logic change**, **no default-registry registration**, **no production dispatch**, **no Evidence Stage 2/3 promotion**, and **no autonomous action**. §11 signature is operator-only.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey**. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (governing template; §3 contract block, §6 Evidence Stage / Promotion / Demotion model, §7.0 detector-immutability boundary)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#24 MFA Manipulation; Build Sequencer candidate)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/precursor/body_signal_detector.py` (immutable underlying detector function — `score_mfa_fatigue`)
- `4. Product_Roadmap/Phase_1_2_Ransomware_Precursor_Deep_Dive.md` (governing detector spec for the body-signal detectors)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent` protocol, `AgentContribution`, `DecisionEvidenceRecord`)
- `VISION.md` (Stage A = analyze + recommend only; seven non-negotiables)

---

## Agent Design Contract block

**Boundary:** This contract governs the future MFA Manipulation **agent wrapper** around `score_mfa_fatigue`. It is additive governance under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend the MFA-push phrase lists, verification-code phrase lists, numeric-OTP rule, scoring bands, indicator vocabulary, the sibling `score_credential_harvesting` function (#23's surface), precursor overlay behavior, tenant override behavior, or any existing pipeline wiring. Those remain governed by their prior authorization and are immutable here.

| Field | Value |
|---|---|
| Agent name | MFA Manipulation Agent (`MFAManipulationAgent`) |
| Swarm inventory ID | #24 — MFA Manipulation |
| Canonical layer | 2 — Detection |
| Canonical team / case type | Phishing / credential; MFA-fatigue, authenticator-push, and verification-code lure language in inbound email body text |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed. Validated on synthetic tests only; intentionally NOT registered in `build_default_registry` / production dispatch. Advancement to Stage 2 requires template §6.2 conditions and a Matt-signed promotion record. |
| Role | Produce facts-only MFA-manipulation evidence by running the deterministic body-signal detector over the email's text surfaces and contributing the detected MFA-push / verification-code indicator names to the case Decision Evidence Record. |
| Boundary | The detector is not the decision. The agent must not decide compromise, declare a message malicious, approve/deny mail, block/quarantine, call out to the network, fetch URLs, mutate scores, write to any baseline/memory store, or alter the signed client-facing rubric. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no DNS/network/HTTP fetch; no reputation lookup; no baseline/memory write; no buyer-facing claim; no default-registry registration; no production dispatch at Evidence Stage 1; no emission of the numeric body-signal score as an interpretation field; no use of the sibling `score_credential_harvesting` surface (#23). |
| Inputs | One `EMAIL_INBOUND` Blackboard record located via `MissionContext.source_record_id` on the tenant's own path; reads `body_plain`, `body_html`, and `subject` only, matching the existing detector's multi-text input shape. |
| Outputs | One `AgentContribution` (layer 2): `observed_facts` = detected MFA-manipulation indicator names from the existing closed `PrecursorIndicator` vocabulary. No verification/challenge/evidence/score field is emitted. |
| Evidence emitted | The MFA-manipulation indicator names actually observed: `mfa_push_language` and `verification_code_language`. Raw matched phrases, body snippets, one-time codes, and the numeric `score` do not cross into the contribution. |
| Data minimization | No raw body text, matched-phrase substrings, subject text, one-time codes, URLs, or credentials are emitted in the contribution. `inputs_digest` is a SHA-256 of the email payload, not the payload itself. |
| Tenant isolation | Reads only the tenant's own Blackboard path (`blackboard_path(root, environment, tenant_id)`); tenant A's email body never influences tenant B. Contribution writes are gated by registry `allowed_write_types` (`AGENT_CONTRIBUTION`). The detector is pure (no per-tenant memory), so no cross-tenant state exists. |
| Two-pass role | Pass 1 (detect) only. `challenge()` returns `None` — Pass 2 is a Verification / Challenge-layer concern. |
| Decision Evidence Record contribution | `observed_facts`: detected MFA-manipulation indicator names; `interpretations`: none; `assumptions`: the `EMAIL_INBOUND` record body/subject text is as ingested; `missing_evidence`: the agent does not verify an account-takeover event, confirm an MFA prompt was actually sent, inspect identity-provider logs, or prove the message is phishing; `recommended_verification`: none emitted at this layer; `final_outcome_contribution`: MFA-push / verification-code lure facts only; `retest_or_learning_record`: every real-case miss or demotion trigger becomes a permanent regression test per template §6.5. |
| Human review trigger | None authored by this agent; the Commander and downstream layers own escalation. |
| Verification trigger | None authored by this agent (Layer 2); MFA-manipulation facts can feed future Verification / Challenge agents. |
| Scoring / action posture | Facts-only contribution. The agent performs no scoring lift itself; the underlying detector's existing score and precursor overlay behavior remain unchanged and out of scope. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers and tests until a later signed promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; Stage A router guard rejects autonomy. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires: clean test suite, zero open test failures, Matt review of >= 3 real email samples confirming observed facts, `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. |
| Demotion conditions | Per template §6.3. Automatic: regression failure, Drift Watch anomaly, evidence-chain integrity failure, or out-of-layer field write. Matt-signed: auditor pattern flag, real miss that misled downstream Verification, or signed Challenge contradiction pattern. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent regression test. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires the real-sample review in §6.2; Stage 3 requires Drift Watch active. |
| Failure modes | See §5. |
| Required tests | See §6 — wrapper tests must prove known-bad fire, known-good no-fire, HTML/subject-surface handling, persistence, guardrails, no registry default, and no score/raw-code leakage. |
| Audit requirements | Any contract signature, implementation, or revision remains subject to `complete_gate.py`. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `Phase_1_2_Ransomware_Precursor_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, and canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At §11 signature, this agent is at **Evidence Stage 1** only. No build authorization is granted for Evidence Stage 2/3 registration until §6.2 promotion conditions are satisfied and a separate promotion record is signed. The underlying detector and existing pipeline wiring are unchanged by this contract. |

---

## §0 Purpose

Promote swarm agent #24 MFA Manipulation from an existing deterministic detector surface into a governed-agent path by giving the future wrapper a signed Agent Design Contract. The wrapper will follow the proven `analyze()` -> `AgentContribution` -> Blackboard -> in-memory DER path already used by Header Analysis, Ghost Thread, Email Authentication, Link Inspection, Attachment Risk, and Credential Phishing.

This contract is the governance step. It does not build runtime code until §11 signature / Build Authorization.

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing a future `MFAManipulationAgent` wrapper as a Layer 2 Detection agent.
- Evidence Stage 1 (Synthetic) declaration at signature.
- Facts-only contribution of the existing detector's closed MFA-manipulation indicator names (`mfa_push_language`, `verification_code_language`).
- Explicit preservation of existing `score_mfa_fatigue` behavior and precursor overlay behavior.

### Out of scope
- Any change to `score_mfa_fatigue`, the phrase lists, numeric-OTP rule, scoring bands, indicator vocabulary, or overlay behavior.
- The sibling `score_credential_harvesting` surface (#23 Credential Phishing) — already governed by its own separate contract.
- Emitting the numeric `BodySignalAssessment.score` through the agent contribution.
- Emitting raw body text, matched-phrase substrings, subject text, one-time codes, URLs, or credentials.
- DNS, URL fetch, reputation lookup, sandbox browse, carrier/API enrichment, identity-provider log lookup, or network call.
- Any baseline/memory store read or write (the detector is pure; the wrapper stays pure-read of the email record).
- Registering the agent in `build_default_registry` or production dispatch.
- Changing the Client-Facing 5-Axis Email Scoring Rubric, recommended risk floor behavior, or tenant override behavior.
- Any autonomous action, buyer-facing claim, or Stage B/C autonomy.
- Evidence Stage 2/3 promotion.

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

- **D1 — Identity.** MFA Manipulation is a Layer 2 Detection agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = mfa_manipulation_001`.
- **D2 — Detector immutability.** This contract changes no phrase list, numeric-OTP rule, scoring band, indicator vocabulary, overlay behavior, tenant override, or pipeline wiring. It governs the wrapper only.
- **D3 — Facts-only contribution.** The agent emits only the closed `PrecursorIndicator` MFA-manipulation indicator names as `observed_facts`. It emits no score, no matched phrase, no raw code, no body snippet, no interpretation, no verification field, and no challenge/evidence field.
- **D4 — Input surface.** The agent reads exactly one `EMAIL_INBOUND` record via `MissionContext.source_record_id`, passing `body_plain`, `body_html`, and `subject` to the detector because the existing detector accepts multiple text surfaces.
- **D5 — Persistence + rollout.** Contributions persist via the registry-gated `AGENT_CONTRIBUTION` route. The agent is NOT in `build_default_registry`; it is wired only by explicit callers until a signed promotion.
- **D6 — Stage A / no autonomy.** No block/quarantine/deny/reject; no autonomous action; the agent authors no disposition.
- **D7 — Evidence Stage governance.** Evidence Stage 1 at signing; promotion and demotion follow template §6.2 / §6.3; progressive hardening §6.5 applies.
- **D8 — Data minimization + purity.** No raw body/subject text, matched phrases, or one-time codes in the contribution; the wrapper performs no baseline/memory write and no network call; tenant-scoped reads and registry-gated writes only.
- **D9 — Single-surface scope.** This agent wraps `score_mfa_fatigue` only. The sibling `score_credential_harvesting` (#23) is explicitly out of scope and already has its own governed wrapper, so the two swarm rows stay distinct.
- **D10 — Tests are the Stage 1 evidence.** The wrapper test suite must include known-bad fire, known-good no-fire, documented surface behavior, persistence, registry rejection, and no leakage assertions before the build can close.

---

## §3 Data surface and output schema

- **Reads:** `EmailInboundPayload.body_plain`, `EmailInboundPayload.body_html`, and `EmailInboundPayload.subject`.
- **Underlying detector:** `score_mfa_fatigue(body_plain, body_html, subject)` returns `BodySignalAssessment(score, indicators)`.
- **Emits:** `AgentContribution(agent_id="mfa_manipulation_001", layer=2, observed_facts=<indicators>)`.
- **Does not emit:** `BodySignalAssessment.score`, raw body text, matched phrases, one-time codes, subject text, or URLs.

---

## §4 Evidence Stage declaration

- **Current Evidence Stage at signature: 1 — Synthetic.** Only synthetic-fixture validation will exist at initial build.
- **To reach Stage 2 (Supervised):** all template §6.2 Stage 1->2 conditions, including Matt review of >= 3 real email samples and a signed `PROMOTION` entry.
- **To reach Stage 3 (Production):** template §6.2 Stage 2->3 conditions, including Drift Watch active. Reaching Stage 3 grants no autonomous action.
- **Demotion:** template §6.3 triggers apply.

---

## §5 Failure modes

- **Authority drift** — treating MFA-manipulation language facts as proof of account compromise or final phishing decision. Mitigation: facts-only contribution; Commander/downstream layers own disposition.
- **Score leakage** — emitting `BodySignalAssessment.score` as a DER interpretation or risk field. Mitigation: D3 and layer-field schema boundary.
- **Raw code leakage** — writing a one-time code, matched phrase, body substring, or subject string into the contribution. Mitigation: indicator-only output and no raw evidence fields.
- **Network/reputation creep** — fetching URLs, resolving DNS, querying identity-provider logs, or calling reputation APIs. Mitigation: D2/D8; the detector is string-only.
- **Memory creep** — writing to the Vendor Baseline Store or any memory surface during detection. Mitigation: D8; the body-signal detector is pure and the wrapper performs no baseline write.
- **Surface false negative** — lure language appears only in HTML or subject. Mitigation: wrapper passes `body_plain` + `body_html` + `subject`; every real miss becomes a §6.5 regression.
- **Benign-template false positive** — legitimate MFA notifications, helpdesk messages, or security-awareness templates. Mitigation: this agent emits facts only; downstream review/challenge handles context before action; the detector's conservative phrase lists remain immutable.
- **Cross-tenant read** — reading another tenant's email record. Mitigation: tenant-scoped Blackboard path + `source_record_id` guard.
- **Stage creep** — registering in default dispatch or production while at Evidence Stage 1. Mitigation: explicit default-registry exclusion.

---

## §6 Required tests

The implementation slice must add focused tests proving:

1. `MFAManipulationAgent` satisfies the shared `Agent` protocol.
2. A known-bad email with MFA-push / verification-code language produces expected indicator facts and a `suspicious` DER disposition.
3. A known-good email with routine business language produces empty facts and a `clear` DER disposition.
4. MFA-push language and verification-code language can fire independently.
5. Lure language present only in `body_html` or only in `subject` is included by the wrapper's input surface.
6. A numeric `code: 123456` lure raises the detector's internal score but does not leak the code or score through the contribution.
7. Contribution persistence writes through `submit_agent_contribution` and round-trips through `AgentContributionPayload`.
8. `challenge()` returns `None`.
9. Missing, unknown, and wrong-type `source_record_id` raise `GovernanceError`.
10. Unauthorized registry writes are rejected.
11. `digest_email` is deterministic.
12. `build_default_registry()` does not include `mfa_manipulation_001`.
13. Contributions do not contain the numeric score, a raw matched phrase, a raw one-time code, body text, or subject text.
14. The wrapper performs no baseline/memory write and no network/subprocess call during `analyze()` (purity guard).

---

## §7 Audit requirements

This contract draft and any implementation must be gated through `complete_gate.py`. The implementation manifest must include this contract, the Agent Design Contract Template, the body-signal detector file, the wrapper file, and the focused test file.

---

## §10 Open Questions (operator-only)

No design fork is open in this draft. §11 signature confirms D1-D10 and authorizes the Evidence Stage 1 wrapper build only.

---

## §11 Sign-off

PENDING. Operator-authored signature required before runtime implementation.

> [Matt Nichol — MFA Manipulation Agent Design Contract — date]
