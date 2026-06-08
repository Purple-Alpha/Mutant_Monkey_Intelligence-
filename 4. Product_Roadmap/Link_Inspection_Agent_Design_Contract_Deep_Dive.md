# Link Inspection Agent Design Contract — Spec-First Deep Dive

**Status:** DRAFT 2026-06-08. Authored as the next Build Sequencer breadth slice for swarm agent #27. This draft is **not signed** and authorizes **no code**, **no runtime wiring**, **no detector-logic change**, **no default-registry registration**, **no production dispatch**, **no Evidence Stage 2/3 promotion**, and **no autonomous action**. §11 signature is operator-only.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey**. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (governing template; §3 contract block, §6 Evidence Stage / Promotion / Demotion model, §7.0 detector-immutability boundary)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#27 Link Inspection; Build Sequencer candidate)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/precursor/url_obfuscation_detector.py` (immutable underlying detector function — `score_url_obfuscation`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent` protocol, `AgentContribution`, `DecisionEvidenceRecord`)
- `VISION.md` (Stage A = analyze + recommend only; seven non-negotiables)

---

## Agent Design Contract block

**Boundary:** This contract governs the future Link Inspection **agent wrapper** around `score_url_obfuscation`. It is additive governance under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend URL extraction, URL scoring, suspicious-TLD sets, shortener lists, login-path tokens, homoglyph rules, precursor overlay behavior, tenant override behavior, or any existing pipeline wiring. Those remain governed by their prior authorization and are immutable here.

| Field | Value |
|---|---|
| Agent name | Link Inspection Agent (`LinkInspectionAgent`) |
| Swarm inventory ID | #27 — Link Inspection |
| Canonical layer | 2 — Detection |
| Canonical team / case type | Phishing / credential; URL-obfuscation and suspicious-link evidence in inbound email body text |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed. Validated on synthetic tests only; intentionally NOT registered in `build_default_registry` / production dispatch. Advancement to Stage 2 requires template §6.2 conditions and a Matt-signed promotion record. |
| Role | Produce facts-only suspicious-link evidence by running the deterministic URL-obfuscation detector and contributing the detected URL indicator names to the case Decision Evidence Record. |
| Boundary | The detector is not the decision. The agent must not decide phishing, declare a URL malicious, approve/deny mail, block/quarantine, call out to the network, fetch URLs, mutate scores, or alter the signed client-facing rubric. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no DNS/network/HTTP fetch; no URL reputation lookup; no buyer-facing claim; no default-registry registration; no production dispatch at Evidence Stage 1; no emission of the numeric URL-obfuscation score as an interpretation field. |
| Inputs | One `EMAIL_INBOUND` Blackboard record located via `MissionContext.source_record_id` on the tenant's own path; reads `body_plain` and `body_html` only, matching the existing detector's multi-text input shape. |
| Outputs | One `AgentContribution` (layer 2): `observed_facts` = detected URL indicator names from the existing closed `PrecursorIndicator` vocabulary. No verification/challenge/evidence/score field is emitted. |
| Evidence emitted | The URL-obfuscation indicator names actually observed, such as `credential_bearing_url`, `url_shortener_present`, `punycode_url_present`, `homoglyph_url_present`, `suspicious_tld_present`, `ip_address_url_present`, and `login_path_url_present`. Raw URLs and the numeric `score` do not cross into the contribution. |
| Data minimization | No raw URL strings, body snippets, query strings, credentials, phone numbers, account numbers, or header values are emitted in the contribution. `inputs_digest` is a SHA-256 of the email payload, not the payload itself. |
| Tenant isolation | Reads only the tenant's own Blackboard path (`blackboard_path(root, environment, tenant_id)`); tenant A's email body never influences tenant B. Contribution writes are gated by registry `allowed_write_types` (`AGENT_CONTRIBUTION`). |
| Two-pass role | Pass 1 (detect) only. `challenge()` returns `None` — Pass 2 is a Verification / Challenge-layer concern. |
| Decision Evidence Record contribution | `observed_facts`: detected URL indicator names; `interpretations`: none; `assumptions`: the `EMAIL_INBOUND` record body text is as ingested; `missing_evidence`: the agent does not fetch or reputation-check URLs and cannot prove destination safety; `recommended_verification`: none emitted at this layer; `final_outcome_contribution`: suspicious-link facts only; `retest_or_learning_record`: every real-case miss or demotion trigger becomes a permanent regression test per template §6.5. |
| Human review trigger | None authored by this agent; the Commander and downstream layers own escalation. |
| Verification trigger | None authored by this agent (Layer 2); suspicious-link facts can feed future Verification / Challenge agents. |
| Scoring / action posture | Facts-only contribution. The agent performs no scoring lift itself; the underlying detector's existing score and precursor overlay behavior remain unchanged and out of scope. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers and tests until a later signed promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; Stage A router guard rejects autonomy. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires: clean test suite, zero open test failures, Matt review of >= 3 real email samples confirming observed facts, `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. |
| Demotion conditions | Per template §6.3. Automatic: regression failure, Drift Watch anomaly, evidence-chain integrity failure, or out-of-layer field write. Matt-signed: auditor pattern flag, real miss that misled downstream Verification, or signed Challenge contradiction pattern. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent regression test. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires the real-sample review in §6.2; Stage 3 requires Drift Watch active. |
| Failure modes | See §5. |
| Required tests | See §6 — wrapper tests must prove known-bad fire, known-good no-fire, HTML-body handling, persistence, guardrails, no registry default, and no score/raw URL leakage. |
| Audit requirements | Any contract signature, implementation, or revision remains subject to `complete_gate.py`. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, and canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At §11 signature, this agent is at **Evidence Stage 1** only. No build authorization is granted for Evidence Stage 2/3 registration until §6.2 promotion conditions are satisfied and a separate promotion record is signed. The underlying detector and existing pipeline wiring are unchanged by this contract. |

---

## §0 Purpose

Promote swarm agent #27 Link Inspection from an existing deterministic detector surface into a governed-agent path by giving the future wrapper a signed Agent Design Contract. The wrapper will follow the proven `analyze()` -> `AgentContribution` -> Blackboard -> in-memory DER -> Layer 5 challenge-pass path already used by Header Analysis, Ghost Thread, and Email Authentication.

This contract is the governance step. It does not build runtime code until §11 signature / Build Authorization.

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing a future `LinkInspectionAgent` wrapper as a Layer 2 Detection agent.
- Evidence Stage 1 (Synthetic) declaration at signature.
- Facts-only contribution of the existing detector's closed indicator names.
- Explicit preservation of existing `score_url_obfuscation` behavior and precursor overlay behavior.

### Out of scope
- Any change to `score_url_obfuscation`, `URL_PATTERN`, shortener hosts, suspicious TLDs, login-path tokens, homoglyph rules, scoring bands, or overlay behavior.
- Emitting the numeric `UrlRiskAssessment.score` through the agent contribution.
- Emitting raw URLs, query strings, body snippets, credentials, or raw lure text.
- DNS, URL fetch, reputation lookup, sandbox browse, carrier/API enrichment, or network call.
- Registering the agent in `build_default_registry` or production dispatch.
- Changing the Client-Facing 5-Axis Email Scoring Rubric, recommended risk floor behavior, or tenant override behavior.
- Any autonomous action, buyer-facing claim, or Stage B/C autonomy.
- Evidence Stage 2/3 promotion.

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

- **D1 — Identity.** Link Inspection is a Layer 2 Detection agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = link_inspection_001`.
- **D2 — Detector immutability.** This contract changes no URL extraction, scoring, indicator vocabulary, overlay behavior, tenant override, or pipeline wiring. It governs the wrapper only.
- **D3 — Facts-only contribution.** The agent emits only closed `PrecursorIndicator` URL-obfuscation indicator names as `observed_facts`. It emits no score, no URL, no interpretation, no verification field, and no challenge/evidence field.
- **D4 — Input surface.** The agent reads exactly one `EMAIL_INBOUND` record via `MissionContext.source_record_id`, using `body_plain` and `body_html` only because the existing detector accepts multiple text surfaces.
- **D5 — Persistence + rollout.** Contributions persist via the registry-gated `AGENT_CONTRIBUTION` route. The agent is NOT in `build_default_registry`; it is wired only by explicit callers until a signed promotion.
- **D6 — Stage A / no autonomy.** No block/quarantine/deny/reject; no autonomous action; the agent authors no disposition.
- **D7 — Evidence Stage governance.** Evidence Stage 1 at signing; promotion and demotion follow template §6.2 / §6.3; progressive hardening §6.5 applies.
- **D8 — Data minimization + tenant isolation.** No raw URLs or raw body text in the contribution; tenant-scoped reads and registry-gated writes only.
- **D9 — Tests are the Stage 1 evidence.** The wrapper test suite must include known-bad fire, known-good no-fire, documented edge behavior, persistence, registry rejection, and no leakage assertions before the build can close.

---

## §3 Data surface and output schema

- **Reads:** `EmailInboundPayload.body_plain` and `EmailInboundPayload.body_html`.
- **Underlying detector:** `score_url_obfuscation(email.body_plain, email.body_html)` returns `UrlRiskAssessment(score, indicators)`.
- **Emits:** `AgentContribution(agent_id="link_inspection_001", layer=2, observed_facts=<indicators>)`.
- **Does not emit:** `UrlRiskAssessment.score`, raw URLs, raw body text, URL host/path/query, or URL credential substrings.

---

## §4 Evidence Stage declaration

- **Current Evidence Stage at signature: 1 — Synthetic.** Only synthetic-fixture validation will exist at initial build.
- **To reach Stage 2 (Supervised):** all template §6.2 Stage 1->2 conditions, including Matt review of >= 3 real email samples and a signed `PROMOTION` entry.
- **To reach Stage 3 (Production):** template §6.2 Stage 2->3 conditions, including Drift Watch active. Reaching Stage 3 grants no autonomous action.
- **Demotion:** template §6.3 triggers apply.

---

## §5 Failure modes

- **Authority drift** — treating suspicious-link facts as a final phishing decision. Mitigation: facts-only contribution; Commander/downstream layers own disposition.
- **Score leakage** — emitting `UrlRiskAssessment.score` as a DER interpretation or risk field. Mitigation: D3 and layer-field schema boundary.
- **Raw URL leakage** — writing a URL, query string, credential-bearing URL, or body substring into the contribution. Mitigation: indicator-only output and no raw evidence fields.
- **Network/reputation creep** — fetching URLs, resolving DNS, or calling reputation APIs. Mitigation: D2/D4; existing detector is string-only.
- **HTML/body mismatch false negative** — link appears only in HTML or only in plain text. Mitigation: wrapper passes both existing surfaces to the detector; every real miss becomes a §6.5 regression.
- **Benign-shortener false positive** — legitimate use of a URL shortener. Mitigation: this agent emits facts only; downstream review/challenge handles context before action.
- **Cross-tenant read** — reading another tenant's email record. Mitigation: tenant-scoped Blackboard path + `source_record_id` guard.
- **Stage creep** — registering in default dispatch or production while at Evidence Stage 1. Mitigation: explicit default-registry exclusion.

---

## §6 Required tests

The implementation slice must add focused tests proving:

1. `LinkInspectionAgent` satisfies the shared `Agent` protocol.
2. A known-bad email with a suspicious URL produces expected URL indicator facts and a `suspicious` DER disposition.
3. A known-good email with no URLs produces empty facts and a `clear` DER disposition.
4. A `body_html`-only suspicious URL is included by the wrapper's input surface.
5. Contribution persistence writes through `submit_agent_contribution` and round-trips through `AgentContributionPayload`.
6. `challenge()` returns `None`.
7. Missing, unknown, and wrong-type `source_record_id` raise `GovernanceError`.
8. Unauthorized registry writes are rejected.
9. `digest_email` is deterministic.
10. `build_default_registry()` does not include `link_inspection_001`.
11. Contributions do not contain numeric score, raw URL, query string, or body snippet.

---

## §7 Audit requirements

This contract draft and any implementation must be gated through `complete_gate.py`. The implementation manifest must include this contract, the Agent Design Contract Template, the URL detector file, the wrapper file, and the focused test file.

---

## §10 Open Questions (operator-only)

No design fork is open in this draft. §11 signature confirms D1-D9 and authorizes the Evidence Stage 1 wrapper build only.

---

## §11 Sign-off

PENDING. Operator-authored signature required before runtime implementation.

> [Matt Nichol — Link Inspection Agent Design Contract — date]
