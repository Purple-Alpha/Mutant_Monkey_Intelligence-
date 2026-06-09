# Language Pressure Agent Design Contract — Spec-First Deep Dive

**Status:** §11 SIGNED 2026-06-08 by Matt Nichol ("Matt Nichol June 8th 2026", placed verbatim in §11). Authored by the first live Build Map TRIAGE cycle for swarm agent #39. The signature authorizes the **Evidence Stage 1 (Synthetic) `LanguagePressureAgent` wrapper build + focused tests only**. It authorizes **no detector-logic change**, **no default-registry registration**, **no production dispatch**, **no Evidence Stage 2/3 promotion**, **no callback-verification workflow**, **no phone-number handling**, and **no autonomous action**. D1-D10 are locked.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey**. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Build_Map_Deep_Dive.md` (LIVE build authority; first live TRIAGE cycle selected #39 after #25 RECLASSIFY)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (governing template; §3 contract block, §6 Evidence Stage / Promotion / Demotion model, §7.0 detector-immutability boundary)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#39 Language Pressure; Build Sequencer candidate)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md` (§11-signed detector spec for the pure body-language detector; Part 1 only)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/callback_phishing_detector.py` (immutable underlying detector function — `detect_callback_phishing`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent` protocol, `AgentContribution`, `DecisionEvidenceRecord`)
- `VISION.md` (Stage A = analyze / recommend / evidence only; seven non-negotiables)

---

## Agent Design Contract block

**Boundary:** This contract governs the future Language Pressure **agent wrapper** around `detect_callback_phishing`. It is additive governance under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend the callback-phishing phrase categories, regex patterns, risk-floor bands, rendering wording, feature-flag behavior, client-facing rubric projection, or any existing pipeline wiring. Those remain governed by the §11-signed `Callback_Phishing_TOAD_Detector_Deep_Dive.md` and are immutable here.

| Field | Value |
|---|---|
| Agent name | Language Pressure Agent (`LanguagePressureAgent`) |
| Swarm inventory ID | #39 — Language Pressure |
| Canonical layer | 2 — Detection |
| Canonical team / case type | Language / behavior / deception; callback-pressure and TOAD-style off-channel coercion language in inbound email body text |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed. Validated on synthetic tests only; intentionally NOT registered in `build_default_registry` / production dispatch. Advancement to Stage 2 requires template §6.2 conditions and a Matt-signed promotion record. |
| Role | Produce facts-only language-pressure evidence by running the deterministic callback-phishing body-language detector over the email body and contributing the detected closed category names to the case Decision Evidence Record. |
| Boundary | The detector is not the decision. The agent must not verify callback legitimacy, inspect or store phone numbers, decide fraud, declare TOAD, approve/deny mail, block/quarantine, call out to the network, fetch URLs, mutate scores, write to any baseline/memory store, alter the client-facing rubric, or operate the #18 Callback Verification workflow. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no phone-number extraction, normalization, hashing, baselining, reputation lookup, or storage; no DNS/network/HTTP fetch; no carrier/API enrichment; no baseline/memory write; no buyer-facing claim; no default-registry registration; no production dispatch at Evidence Stage 1; no emission of `recommended_risk_floor_lift` as an interpretation or score field; no operation of the Layer 3 callback-verification workflow. |
| Inputs | One `EMAIL_INBOUND` Blackboard record located via `MissionContext.source_record_id` on the tenant's own path; reads `body_plain` only, matching the signed TOAD v1 detector input surface (D14). |
| Outputs | One `AgentContribution` (layer 2): `observed_facts` = detected callback/body-language category names from the signed v1 closed vocabulary. No verification/challenge/evidence/score field is emitted. |
| Evidence emitted | The category names actually observed: `call_now_pressure`, `do_not_use_known_channel`, `voice_only_finalize`, `support_line_substitution`, and/or `payment_redirect_call`. Raw matched phrases, body snippets, phone-number-shaped strings, and the numeric `recommended_risk_floor_lift` do not cross into the contribution. |
| Data minimization | No raw body text, matched-phrase substrings, phone numbers/digits, URLs, account/routing identifiers, category explanations, or rendered verification wording are emitted in the contribution. `inputs_digest` is a SHA-256 of the email payload, not the payload itself. |
| Tenant isolation | Reads only the tenant's own Blackboard path (`blackboard_path(root, environment, tenant_id)`); tenant A's email body never influences tenant B. Contribution writes are gated by registry `allowed_write_types` (`AGENT_CONTRIBUTION`). The detector is pure (no per-tenant memory), so no cross-tenant state exists. |
| Two-pass role | Pass 1 (detect) only. `challenge()` returns `None` — Pass 2 is a Verification / Challenge-layer concern. |
| Decision Evidence Record contribution | `observed_facts`: detected language-pressure category names; `interpretations`: none; `assumptions`: the `EMAIL_INBOUND` record body text is as ingested; `missing_evidence`: the agent does not inspect/verify phone numbers, confirm a callback destination, prove fraud, or establish account/vendor identity; `recommended_verification`: none emitted at this layer; `final_outcome_contribution`: language-pressure facts only; `retest_or_learning_record`: every real-case miss or demotion trigger becomes a permanent regression test per template §6.5. |
| Human review trigger | None authored by this agent; the Commander and downstream layers own escalation. |
| Verification trigger | None authored by this agent (Layer 2); language-pressure facts can feed future Verification / Challenge agents, including a separately authorized #18 Callback Verification path. |
| Scoring / action posture | Facts-only contribution. The agent performs no scoring lift itself; the underlying detector's existing risk-floor lift behavior and any scoring-agent integration remain unchanged and out of scope. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers and tests until a later signed promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; Stage A router guard rejects autonomy. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires: clean test suite, zero open test failures, Matt review of >= 3 real email samples confirming observed facts, `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. |
| Demotion conditions | Per template §6.3. Automatic: regression failure, Drift Watch anomaly, evidence-chain integrity failure, or out-of-layer field write. Matt-signed: auditor pattern flag, real miss that misled downstream Verification, or signed Challenge contradiction pattern. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent regression test. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires the real-sample review in §6.2; Stage 3 requires Drift Watch active. |
| Failure modes | See §5. |
| Required tests | See §6 — wrapper tests must prove known-bad fire, known-good no-fire, category handling, body-only input boundary, persistence, guardrails, no registry default, no phone-number/phrase/score leakage, and purity. |
| Audit requirements | Any contract signature, implementation, or revision remains subject to `complete_gate.py`. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `Callback_Phishing_TOAD_Detector_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, and canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At §11 signature, this agent is at **Evidence Stage 1** only. No build authorization is granted for Evidence Stage 2/3 registration until §6.2 promotion conditions are satisfied and a separate promotion record is signed. The underlying detector and existing pipeline wiring are unchanged by this contract. |

---

## §0 Purpose

Promote swarm agent #39 Language Pressure from an existing deterministic detector surface into a governed-agent path by giving the future wrapper a signed Agent Design Contract. The wrapper will follow the proven `analyze()` -> `AgentContribution` -> Blackboard -> in-memory DER path already used by Header Analysis, Ghost Thread, Email Authentication, Link Inspection, Attachment Risk, Credential Phishing, and MFA Manipulation.

This contract is the governance step. It does not build runtime code until §11 signature / Build Authorization.

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing a future `LanguagePressureAgent` wrapper as a Layer 2 Detection agent.
- Evidence Stage 1 (Synthetic) declaration at signature.
- Facts-only contribution of the existing detector's closed callback/body-language category names.
- Explicit preservation of existing `detect_callback_phishing` behavior and the signed TOAD v1 body-only input boundary.

### Out of scope
- Any change to `detect_callback_phishing`, phrase categories, regex patterns, risk-floor bands, validator schema, rendering wording, feature flag, client-facing rubric projection, or scoring-agent integration.
- The #18 Callback Verification workflow, phone-number baselining, or any Part 2 TOAD surface.
- Emitting `CallbackPhishingAssessment.recommended_risk_floor_lift` or any numeric score/tier through the agent contribution.
- Emitting raw body text, matched-phrase substrings, phone-number-shaped strings, URLs, account/routing identifiers, or category explanations.
- DNS, URL fetch, reputation lookup, carrier/API enrichment, sandbox browse, or network call.
- Any baseline/memory store read or write.
- Registering the agent in `build_default_registry` or production dispatch.
- Changing the Client-Facing 5-Axis Email Scoring Rubric, recommended risk floor behavior, tenant override behavior, or buyer-facing rendering.
- Any autonomous action, buyer-facing claim, or Stage B/C autonomy.
- Evidence Stage 2/3 promotion.

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

- **D1 — Identity.** Language Pressure is a Layer 2 Detection agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = language_pressure_001`.
- **D2 — Detector immutability.** This contract changes no phrase category, regex pattern, risk-floor band, schema field, feature flag, client-facing projection, overlay behavior, tenant override, or pipeline wiring. It governs the wrapper only.
- **D3 — Facts-only contribution.** The agent emits only closed TOAD v1 category names as `observed_facts`. It emits no risk-floor lift, no score, no matched phrase, no body snippet, no phone number/digit, no interpretation, no verification field, and no challenge/evidence field.
- **D4 — Input surface.** The agent reads exactly one `EMAIL_INBOUND` record via `MissionContext.source_record_id`, passing `body_plain` only to the detector because the signed TOAD v1 detector is body-plain-only.
- **D5 — Persistence + rollout.** Contributions persist via the registry-gated `AGENT_CONTRIBUTION` route. The agent is NOT in `build_default_registry`; it is wired only by explicit callers until a signed promotion.
- **D6 — Stage A / no autonomy.** No block/quarantine/deny/reject; no autonomous action; the agent authors no disposition.
- **D7 — Evidence Stage governance.** Evidence Stage 1 at signing; promotion and demotion follow template §6.2 / §6.3; progressive hardening §6.5 applies.
- **D8 — Data minimization + purity.** No raw body text, matched phrases, phone-number-shaped strings, category explanations, or risk-floor lift values in the contribution; the wrapper performs no baseline/memory write and no network call; tenant-scoped reads and registry-gated writes only.
- **D9 — Boundary split from #18.** This agent wraps the pure Layer 2 language detector only. It does not operate #18 Callback Verification, perform independent callback verification, inspect phone numbers, or touch the future Part 2 phone-baseline path.
- **D10 — Tests are the Stage 1 evidence.** The wrapper test suite must include known-bad fire, known-good no-fire, category-specific behavior, persistence, registry rejection, body-only boundary, no leakage assertions, and purity guards before the build can close.

---

## §3 Data surface and output schema

- **Reads:** `EmailInboundPayload.body_plain`.
- **Underlying detector:** `detect_callback_phishing(body_plain=<body_plain>)` returns `CallbackPhishingAssessment(fired, categories, recommended_risk_floor_lift, out_of_band_verification_required)`.
- **Emits:** `AgentContribution(agent_id="language_pressure_001", layer=2, observed_facts=<category_names>)`.
- **Does not emit:** `recommended_risk_floor_lift`, `out_of_band_verification_required`, `why_this_category`, raw body text, matched phrases, phone numbers/digits, URLs, account/routing identifiers, or rendered verification wording.

---

## §4 Evidence Stage declaration

- **Current Evidence Stage at signature: 1 — Synthetic.** Only synthetic-fixture validation will exist at initial build.
- **To reach Stage 2 (Supervised):** all template §6.2 Stage 1->2 conditions, including Matt review of >= 3 real email samples and a signed `PROMOTION` entry.
- **To reach Stage 3 (Production):** template §6.2 Stage 2->3 conditions, including Drift Watch active. Reaching Stage 3 grants no autonomous action.
- **Demotion:** template §6.3 triggers apply.

---

## §5 Failure modes

- **Authority drift** — treating language-pressure category facts as proof of fraud, TOAD, or callback destination compromise. Mitigation: facts-only contribution; Commander/downstream layers own disposition.
- **Layer drift into #18** — using this agent to verify phone numbers or run callback workflow logic. Mitigation: D9 boundary split; #18 remains separate and blocked until its own signed boundary contract.
- **Risk-floor leakage** — emitting `recommended_risk_floor_lift` as a DER interpretation or score field. Mitigation: D3 and layer-field schema boundary.
- **Raw phrase / phone-number leakage** — writing matched lure phrases, raw body text, or phone-number-shaped strings into the contribution. Mitigation: category-name-only output and no raw evidence fields.
- **Network/reputation creep** — resolving URLs, querying phone-number reputation, carrier APIs, DNS, or any enrichment service. Mitigation: D2/D8; the detector is a pure body-language scanner.
- **Memory creep** — writing to the Vendor Baseline Store or any memory surface during detection. Mitigation: D8; the detector is pure and the wrapper performs no baseline write.
- **Body-only false negative** — TOAD lure appears only in HTML or attachment text. Mitigation: v1 preserves the signed TOAD D14 body_plain-only boundary; HTML/attachment expansion requires a later signed evidence-driven addendum.
- **Benign callback false positive** — legitimate billing/support emails that mention a phone call. Mitigation: this agent emits facts only; detector categories are conservative and require misdirection, urgency, or off-channel coercion patterns.
- **Cross-tenant read** — reading another tenant's email record. Mitigation: tenant-scoped Blackboard path + `source_record_id` guard.
- **Stage creep** — registering in default dispatch or production while at Evidence Stage 1. Mitigation: explicit default-registry exclusion.

---

## §6 Required tests

The implementation slice must add focused tests proving:

1. `LanguagePressureAgent` satisfies the shared `Agent` protocol.
2. A known-bad email with callback pressure / known-channel misdirection produces expected category facts and a `suspicious` DER disposition.
3. A known-good routine business email produces empty facts and a `clear` DER disposition.
4. Each closed category can appear as an observed fact when the detector fires on that category.
5. Multiple categories aggregate in deterministic detector order with dedupe.
6. The wrapper passes `body_plain` only; `body_html` and subject-only lure text do not affect Stage 1 output.
7. Contribution persistence writes through `submit_agent_contribution` and round-trips through `AgentContributionPayload`.
8. `challenge()` returns `None`.
9. Missing, unknown, and wrong-type `source_record_id` raise `GovernanceError`.
10. Unauthorized registry writes are rejected.
11. `digest_email` is deterministic.
12. `build_default_registry()` does not include `language_pressure_001`.
13. Contributions do not contain risk-floor lift values, category explanations, raw matched phrases, raw body text, phone-number-shaped strings, URLs, account/routing identifiers, or rendered verification wording.
14. The wrapper performs no baseline/memory write and no network/subprocess call during `analyze()` (purity guard).

---

## §7 Audit requirements

This contract draft and any implementation must be gated through `complete_gate.py`. The implementation manifest must include this contract, the Agent Design Contract Template, the signed TOAD detector spec, the callback detector file, the wrapper file, and the focused test file.

---

## §10 Open Questions (operator-only)

No design fork is open in this draft. §11 signature confirms D1-D10 and authorizes the Evidence Stage 1 wrapper build only.

---

## §11 Sign-off

SIGNED. D1-D10 locked. Authorizes the Evidence Stage 1 (Synthetic) `LanguagePressureAgent` wrapper build + focused tests only; no detector-logic change, no default-registry registration, no production dispatch, no Evidence Stage 2/3 promotion, no callback-verification workflow, no phone-number handling, no autonomy.

> Matt Nichol June 8th 2026
