# Header Analysis Agent Design Contract — Spec-First Deep Dive

**Status:** §11 SIGNED 2026-06-07 by Matt Nichol ("Matt Nichol June 7th 2026", placed verbatim at §11). Authored 2026-06-07 by Cursor on Matt Nichol's instruction ("lets go" — formalize the Header Analysis wrapper). This is the first per-agent Agent Design Contract under the §11-signed `Agent_Design_Contract_Template_Deep_Dive.md` (including its 2026-06-07 §11.A Evidence Stage revision) and the first application of the Evidence Stage model. Signing promotes swarm agent #6 **Header Analysis** from `DETECTOR_FUNCTION` to `GOVERNED_AGENT` at **Evidence Stage 1 (Synthetic)** and locks D1-D9 + the §4 Evidence Stage declaration. Signing authorizes **no** detector-logic change, **no** default-registry registration, **no** production dispatch, **no** scoring/rubric change, and **no** autonomous action. Evidence Stage 2/3 promotion is a separate, later, Matt-signed event per template §6.2. §11 signature is operator-only.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey**. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (the governing template; §3 contract block, §6 Evidence Stage / Promotion / Demotion model, §7.0 detector-immutability boundary)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (this is agent #6 Header Analysis; L2 promotion bar in Q4)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/header_divergence_detector.py` (the immutable underlying detector function — `score_header_divergence`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/header_divergence_agent.py` (the governed-agent wrapper — `HeaderDivergenceAgent`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_header_divergence_agent.py` (the known-input tests that satisfy the L2 promotion bar)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent` protocol, `AgentContribution`, `DecisionEvidenceRecord`)
- `VISION.md` (Stage A = analyze + recommend only; the seven non-negotiables)

---

## Agent Design Contract block

**Boundary:** This contract governs the Header Analysis **agent wrapper** (`HeaderDivergenceAgent`). It is additive governance, applied under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend the underlying detector logic (`score_header_divergence`, including its score bands `_SCORE_REPLY_TO_DIVERGENCE`/`_SCORE_RETURN_PATH_DIVERGENCE`/`_SCORE_SENDER_HEADER_DIVERGENCE`/`_COMBINATION_BUMP`/`_MAX_SCORE`), its existing consumption by `core/scoring/email_risk_scoring_agent.py`, or any pipeline wiring. Those remain governed by their prior authorization and are immutable here.

| Field | Value |
|---|---|
| Agent name | Header Analysis Agent (`HeaderDivergenceAgent`) |
| Swarm inventory ID | #6 — Header Analysis (v1 map inventory/backlog reference only) |
| Canonical layer | 2 — Detection |
| Canonical team / case type | Email identity / sender analysis; From / Reply-To / Return-Path / Sender header divergence (BEC vendor-impersonation routing signal) |
| Authority level | Level 3 — Specialist Agent (matches #10 / #21) |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (see §6.0 of the template). |
| Evidence Stage (current) | **Stage 1 — Synthetic.** Validated on synthetic test data only; intentionally NOT registered in `build_default_registry` / production dispatch. Advancement to Stage 2 requires the template §6.2 conditions and a Matt-signed promotion record. |
| Role | Produce facts-only sender-identity-divergence evidence by running the deterministic header-divergence detector and contributing the detected divergence indicators to the case Decision Evidence Record. |
| Boundary | The detector is not the decision. The agent must not decide fraud, approve/deny mail, block/quarantine, change payment behavior, mutate `EmailAnalysisRiskAnalysis`, or alter the signed Client-Facing 5-Axis Email Scoring Rubric. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no network/DNS/LLM call; no buyer-facing claim; no default-registry registration; no production dispatch at Evidence Stage 1; no emission of the numeric divergence score as an interpretation field (facts-only at Layer 2). |
| Inputs | One `EMAIL_INBOUND` Blackboard record located via `MissionContext.source_record_id` (per-tenant path); reads `sender` (From) and `headers` (Reply-To / Return-Path / Sender) only. No body content is read into the contribution. |
| Outputs | One `AgentContribution` (layer 2): `observed_facts` = the detected divergence indicators from the closed set `{from_reply_to_divergence, from_return_path_divergence, from_sender_header_divergence}`. No verification/challenge/evidence/score field is emitted (layer-restricted by the schema validator). |
| Evidence emitted | The closed-set divergence indicator names actually observed for the email; nothing else. The numeric `score` from the underlying detector is intentionally NOT carried into the contribution (Layer 2 facts-only discipline; the score remains consumed only by the existing scoring overlay, unchanged). |
| Data minimization | No mailbox body content, no raw header values, and no secret/value leakage in the contribution — only the closed-set indicator names. `inputs_digest` is a SHA-256 of the email payload, not the payload itself. |
| Tenant isolation | Reads only the tenant's own Blackboard path (`blackboard_path(root, environment, tenant_id)`); tenant A's records never influence tenant B. Contribution writes are gated by the registry's `allowed_write_types` (`AGENT_CONTRIBUTION`). |
| Two-pass role | Pass 1 (detect) only. `challenge()` returns `None` — Pass 2 is a Verification / Challenge-layer concern. The contribution provides facts a future Layer 5 challenge agent can inspect. |
| Decision Evidence Record contribution | `observed_facts`: detected divergence indicators (closed set); `interpretations`: none (Layer 2 emits no interpretation); `assumptions`: the `EMAIL_INBOUND` record headers are as received; `missing_evidence`: absent/garbled headers disable the signal (score 0, empty indicators); `recommended_verification`: none emitted at this layer (downstream verification is a Layer 3 concern); `final_outcome_contribution`: divergence facts only — no disposition authored by this agent; `retest_or_learning_record`: every real-case miss or demotion trigger becomes a new permanent regression test per template §6.5. |
| Human review trigger | None authored by this agent; the Commander's conservative disposition rules and downstream layers own escalation. |
| Verification trigger | None authored by this agent (Layer 2); divergence facts feed a future Layer 3 Verification agent's out-of-band confirmation decision. |
| Scoring / action posture | Facts-only contribution. The agent performs no scoring lift itself; the underlying detector's existing lift-only overlay in the scoring pipeline is unchanged and out of scope for this contract. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers (and the swarm spine tests) until a signed Stage 2 promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; rejected outright in Stage A by the router guard. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires: clean test suite (known-bad fires, known-good does not, edge case as documented), zero open test failures, Matt review of >= 3 real email samples confirming the `observed_facts` match a trained analyst, a `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. |
| Demotion conditions | Per template §6.3. Automatic: a previously-passing regression test fails, Drift Watch anomaly, evidence-chain integrity failure, or an out-of-layer field write. Matt-signed: auditor pattern flag, a real miss that would have misled a downstream Verification agent, or a signed Challenge agent contradicting this agent on >= 2 cases in any 30-day window. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent (append-only) regression test the agent must pass before (re-)promotion. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires the real-sample review in §6.2; Stage 3 requires Drift Watch active. |
| Failure modes | See §5. |
| Required tests | See §6 — `tests/test_header_divergence_agent.py` (the L2 known-input bar) plus the underlying detector's existing tests. |
| Audit requirements | Any implementation/revision remains subject to `complete_gate.py`; this contract draft is gated as a spec artifact. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, and the canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At signing, this agent is at **Evidence Stage 1**. No build authorization is granted for Evidence Stage 2 or Stage 3 registration until the §6.2 promotion conditions are satisfied and a separate promotion record is signed. The underlying detector and its existing pipeline wiring are already authorized and are unchanged by this contract. |

---

## §0 Purpose

Promote the already-built, already-tested Header Analysis agent wrapper from a runtime *proof* (`DETECTOR_FUNCTION` on the scoreboard) to a *governed agent* (`GOVERNED_AGENT`) by giving it a signed Agent Design Contract — the L2 promotion bar from the 70-agent scoreboard Q4 (signed contract + known-input tests + declared DER contribution). It is the first per-agent contract drafted under the signed template and the first application of the Evidence Stage model, and it sets the repeatable pattern every subsequent detector wrap will follow.

This contract does not build anything new. The detector and its wrapper already exist and are tested; this records the governance that converts "proven" into "governed," at the honest evidence level (Stage 1 Synthetic, since only synthetic tests exist today).

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing the `HeaderDivergenceAgent` wrapper as a Layer 2 Detection agent.
- The Evidence Stage 1 (Synthetic) declaration and the promotion/demotion path inherited from template §6.
- Recording that the existing known-input tests (`tests/test_header_divergence_agent.py`) satisfy the L2 promotion bar.

### Out of scope
- Any change to `score_header_divergence` logic, score bands, or its existing consumption by the scoring pipeline (immutable per template §7.0).
- Registering the agent in `build_default_registry` or any production dispatch (Evidence Stage 1 forbids it).
- Any change to the Client-Facing 5-Axis Email Scoring Rubric or `recommended_risk_floor` behavior.
- Any autonomous action, buyer-facing claim, or Stage B/C autonomy.
- Promotion to Evidence Stage 2/3 (a later, separately-signed event).

---

## §2 Locked Design Decisions (confirmed and locked at §11, 2026-06-07)

- **D1 — Identity.** Header Analysis is a Layer 2 Detection agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = header_divergence_001`.
- **D2 — Detector immutability.** This contract changes no detector logic, score band, or pipeline wiring (template §7.0). It governs the wrapper only.
- **D3 — Facts-only contribution.** The agent emits only the closed-set divergence indicators as `observed_facts`. It emits no numeric score, no interpretation, and no verification/challenge/evidence field (schema-enforced by the `AgentContribution` layer validator).
- **D4 — Input surface.** The agent reads exactly one `EMAIL_INBOUND` record via `MissionContext.source_record_id` on the tenant's own Blackboard path, using `sender` + `headers` only.
- **D5 — Persistence + rollout.** Contributions persist via the registry-gated `AGENT_CONTRIBUTION` route. The agent is NOT in `build_default_registry`; it is wired only by explicit callers until a signed Stage 2 promotion.
- **D6 — Stage A / lift-only / no autonomy.** No block/quarantine/deny/reject; no autonomous action; the agent authors no disposition. Stage A discipline holds.
- **D7 — Evidence Stage governance.** Evidence Stage 1 at signing; promotion and demotion follow template §6.2 / §6.3; progressive hardening §6.5 applies (every miss becomes a permanent regression test).
- **D8 — Data minimization + tenant isolation.** No body content or raw header values in the contribution; tenant-scoped reads and registry-gated writes only.
- **D9 — Tests are the promotion-bar evidence.** `tests/test_header_divergence_agent.py` provides the known-bad-fires / known-good-does-not / edge-case coverage required by the L2 bar; it is the regression baseline for §6.5.

---

## §3 Data surface and output schema

- **Reads:** `EmailInboundPayload.sender` (From) and `EmailInboundPayload.headers` (case-insensitive lookup of `Reply-To`, `Return-Path`, `Sender`).
- **Underlying detector:** `score_header_divergence(sender=..., headers=...)` returns `HeaderDivergenceAssessment(score, indicators)`. Only `indicators` cross into the agent contribution; `score` does not.
- **Emits:** `AgentContribution(agent_id="header_divergence_001", layer=2, observed_facts=<indicators>)`. Indicators are a deduplicated, source-order-stable subset of `{from_reply_to_divergence, from_return_path_divergence, from_sender_header_divergence}`. No divergence -> empty `observed_facts` -> Commander disposition `clear` (when all contributions are empty).

---

## §4 Evidence Stage declaration

- **Current Evidence Stage: 1 — Synthetic.** Only synthetic-fixture validation exists (`tests/test_header_divergence_agent.py`). The agent is not in production dispatch.
- **To reach Stage 2 (Supervised):** all template §6.2 Stage 1->2 conditions, including Matt's review of >= 3 real email samples and a signed `PROMOTION` entry.
- **To reach Stage 3 (Production):** template §6.2 Stage 2->3 conditions, including Drift Watch active. Reaching Stage 3 grants no autonomous action (template §6.0).
- **Demotion:** template §6.3 triggers apply.

---

## §5 Failure modes

- **Authority drift** — the agent (or a caller) treating the divergence facts as a decision. Mitigation: facts-only contribution; Commander owns disposition; no score emitted.
- **Score leakage** — emitting the numeric divergence score as an interpretation field. Mitigation: D3 + the layer-restricted `AgentContribution` validator.
- **Root-domain heuristic false divergence** — the eTLD+1 heuristic mis-handles `.co.uk`-style domains (documented limitation in the detector). Mitigation: inherited from the underlying detector; any real miss becomes a §6.5 regression test.
- **Cross-tenant read** — reading another tenant's record. Mitigation: tenant-scoped Blackboard path + `source_record_id` type guard.
- **Stage creep** — registering in the default registry or dispatching in production while at Evidence Stage 1. Mitigation: D5 + the Evidence Stage 1 "not in production dispatch" rule.

---

## §6 Required tests

The L2 promotion bar is satisfied by `tests/test_header_divergence_agent.py`, which proves: the agent satisfies the `Agent` protocol; a known-bad email (Reply-To divergence) produces the `from_reply_to_divergence` fact and a `suspicious` disposition; a known-good email (subdomain, not divergence) produces empty facts and a `clear` disposition; the contribution persists to the Blackboard and round-trips; `challenge()` returns `None`; missing/wrong `source_record_id` is rejected; an unauthorized agent cannot write the contribution; and `digest_email` is deterministic. These tests are the append-only regression baseline for template §6.5.

---

## §7 Audit requirements

This contract is gated through `complete_gate.py` as a spec artifact (clean audit at draft on 2026-06-07; re-gated clean at signing). No runtime registration, default-on, or production dispatch is authorized by signing — only the governance promotion to Evidence Stage 1.

---

## §10 Open Questions (operator-only)

- **Q1 — Stage 2 registry posture.** When Header Analysis is promoted to Evidence Stage 2, should it register in `build_default_registry` for supervised dispatch, or remain explicitly-wired until Stage 3? (Deferred to the Stage 2 promotion event.)
- **Q2 — Score as a future Verification input.** Should the numeric divergence score ever surface (as an interpretation) through a Layer 3 Verification agent rather than this Layer 2 agent? (Deferred to the Verification-layer spec; not authored here.)

---

## §11 Sign-off

SIGNED. This promotes swarm agent #6 Header Analysis to `GOVERNED_AGENT` at **Evidence Stage 1 (Synthetic)** and locks D1-D9 + the §4 Evidence Stage declaration as the Header Analysis Agent Design Contract. Signing authorizes **no** detector-logic change, **no** default-registry registration, **no** production dispatch, **no** scoring/rubric change, and **no** autonomous action. Promotion to Evidence Stage 2/3 is a separate, later, Matt-signed event per template §6.2.

> §11 SIGNATURE — Matt Nichol June 7th 2026
