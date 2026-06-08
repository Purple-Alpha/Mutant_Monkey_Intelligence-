# Aggregate Corroboration Agent Design Contract — Spec-First Deep Dive

**Status:** §11 SIGNED 2026-06-08 by Matt Nichol ("Matt Nichol June 8th", placed
verbatim at §11). §10 questions resolved in §10.A below. Authored 2026-06-08 by
Claude advisory lane on Matt Nichol's instruction (Section 5, spec-first);
reconciled and gated clean (Grok 0 blocking / 0 warnings) by Cursor execution
lane. This is the first Agent Design Contract for a Layer 5 Challenge agent under
the signed Layer 5 Aggregate Challenge Pass spec (§11 SIGNED 2026-06-07) and the
signed Agent Design Contract Template (§11 SIGNED 2026-06-06, §11.A 2026-06-07).
This signature promotes this agent to Evidence Stage 1 (Synthetic) and is the
Build Authorization for the Section 5 code implementation at Evidence Stage 1. No
code exists yet; the Section 5 build is now authorized at Evidence Stage 1 and is
the next concrete step.

**Owner:** Matt Nichol

**Brand:** internal codename NorthStar Inbox Shield in code/spec prose per rebrand
Option B; buyer-facing surfaces use Mutant Monkey. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Layer_5_Aggregate_Challenge_Pass_Deep_Dive.md`
  (§11 SIGNED 2026-06-07 — D1-D9 govern this agent's entire behavioral contract)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
  (§11 SIGNED 2026-06-06, §11.A 2026-06-07 — §3 contract block, §4 authority
  levels, §6 Evidence Stage / Promotion / Demotion model, §7.0 immutability
  boundary)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py`
  (`Agent` protocol, `AgentContribution`, `ChallengeResult`, `MissionContext`,
  `DecisionEvidenceRecord`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/swarm_commander.py`
  (the challenge-pass loop this agent is invoked by; `_validate_agent_for_dispatch`
  metadata-match guard)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/models.py`
  (`AgentRegistryEntry`, `AgentRole`, `GovernanceError`)
- `audit_outputs/failure_register/layer5_section6_failure_register.json`
  (ADV-005/D4 vote-counting gap → closed by D4 enforcement clause;
  KG-002/§10 Q1 arbitration gap → closed by §10.A Q1 Option B)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`
  (canonical 6-layer design source)
- `VISION.md` (Stage A = analyze + recommend only; seven non-negotiables)

---

## Agent Design Contract block

**Wiring note — authority_level and registry role:** The Commander's
`_assert_metadata_match` guard compares the runtime agent's `authority_level`
against its `AgentRegistryEntry`. This agent's registry entry must declare
`authority_level=5` and `role=AgentRole.BLUE` with `allowed_write_types=set()`
(matching the pattern of existing challenge entries). Any divergence — including
using the `_challenge_entry` test double's default of `authority_level=3` — raises
`GovernanceError: metadata diverges` before invocation. The Section 5 test suite
must construct registry entries with `authority_level=5`.

| Field | Value |
|---|---|
| Agent name | Aggregate Corroboration Agent (`AggregateCorroborationAgent`) |
| Swarm inventory ID | Layer 5 — first Challenge/Red-Team agent (no v1 map number; Challenge layer was not populated in the v1 inventory) |
| Canonical layer | 5 — Challenge / Red-Team |
| Canonical team / case type | Email fraud — BEC / vendor-impersonation / executive-impersonation. Reviews aggregate per-case Detection evidence from Layers 2-4. |
| Authority level | **Level 5 — Challenge Agent.** Template §10.A Q3 sets the Stage A default at Level 3 Specialist; "any higher level requires its own signed authority decision." This §11 signature is that authority decision for Level 5. Level 5 is correct for a Challenge agent: it may challenge weak decisions, flag assumptions and missing evidence, and force review; it must not approve risky actions without required evidence and must not author a disposition. |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic** at signing. Validated on synthetic test data only; not registered in `build_default_registry` / production dispatch. Advancement to Stage 2 requires template §6.2 conditions and a Matt-signed promotion record. |
| Role | Review the full per-case `tuple[AgentContribution, ...]` from all dispatched Detection agents and return one case-level `ChallengeResult` — `confirmed`, `contradicted`, or `inconclusive` — based on whether the independent signals genuinely corroborate, contradict, or provide insufficient evidence to reach a verdict. |
| Boundary | The agent authors a verdict only. The Commander owns disposition. The agent must not author a disposition, recommend a business action, block/quarantine/deny/reject mail, change payment behavior, or claim fraud. |
| Explicit non-authorities | No autonomous action; no disposition authoring; no block/quarantine/deny/reject verb; no buyer-facing claim; no default-registry registration at Evidence Stage 1; no production dispatch at Evidence Stage 1; no access to detector internals, scoring logic, or reasoning traces (facts and outcomes only, per Layer 5 spec D3). |
| Inputs | `tuple[AgentContribution, ...]` — the full per-case contribution set as assembled by the Commander (Layer 5 spec D1). Plus `MissionContext` digest for case identity. No raw email payload, no detector internals, no reasoning trace, no chain-of-thought. |
| Outputs | One `ChallengeResult \| None`. `ChallengeResult` carries `agent_id`, `challenge_outcome` (`confirmed` / `contradicted` / `inconclusive`), and `challenge_basis` (one client-safe sentence, max 160 chars). `None` when the agent has no verdict. |
| Evidence emitted | The `ChallengeResult` itself — a single case-level verdict with a one-sentence corroboration or contradiction basis. No new `AgentContribution` is written; the challenge result flows into `DecisionEvidenceRecord.challenge_pass` via the Commander. |
| Data minimization | Reads only `AgentContribution.observed_facts` and `AgentContribution.layer` — no raw header values, no email body, no scoring internals. `challenge_basis` must not echo raw fact strings verbatim or expose internal indicator names beyond what is client-safe. |
| Tenant isolation | The Commander passes this agent only the contributions for the current case. The agent never reads the Blackboard directly; cross-tenant leakage is structurally impossible given the input surface. |
| Two-pass role | Pass 2 (challenge) only. `analyze()` is not invoked by the Commander for Challenge agents; it raises `AssertionError` as a guard (matching the existing test-double pattern). |
| Decision Evidence Record contribution | See §5 for the conceptual seven-field interface. Note: these seven fields are the conceptual evidence shape from template §5 — they are NOT new fields to add to the `DecisionEvidenceRecord` Pydantic class in `agent_contract.py`. The code DER stores `contributions`, `challenge_pass`, and `disposition`; the seven fields describe what this agent contributes conceptually, not a schema change. |
| Human review trigger | `challenge_outcome = contradicted` → Commander routes to `human_required` (existing `_determine_disposition` rule, unchanged). |
| Verification trigger | None authored at this layer. |
| Scoring / action posture | Verdict-only. No score, no lift, no floor change. The agent does not touch `EmailAnalysisRiskAnalysis` or the Client-Facing 5-Axis Rubric. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers and the swarm spine tests until a signed Stage 2 promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; rejected by the router guard before invocation. |
| Registry entry | `AgentRegistryEntry(agent_id="aggregate_corroboration_001", display_name="Aggregate Corroboration Agent", role=AgentRole.BLUE, allowed_environments={Environment.PRODUCTION, Environment.SANDBOX}, allowed_write_types=set(), layer=5, authority_level=5, stage_allowed="stage_a")` |
| Promotion conditions | Per template §6.2. Stage 1 → Stage 2 requires: clean test suite (known-bad corroboration fires correctly, known-good does not over-fire, adversarial vote-counting probe does not mislead), zero open test failures, Matt review of >= 3 real email contribution sets confirming the verdict matches what a trained analyst would conclude, a `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. |
| Demotion conditions | Per template §6.3. Automatic: a previously-passing regression test fails, Drift Watch anomaly, evidence-chain integrity failure, or an out-of-layer field write. Matt-signed: auditor flags a pattern of verdicts inconsistent with the declared corroborate-not-vote-count rule (D4), a real miss that would have escalated a benign case or suppressed a real one, or a signed second Challenge agent contradicting this agent on >= 2 cases in any 30-day window. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent (append-only) regression test before (re-)promotion. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires real-contribution review per §6.2; Stage 3 requires Drift Watch active. |
| Failure modes | See §6. |
| Required tests | See §7. |
| Audit requirements | Any implementation/revision is subject to `complete_gate.py`. This contract is gated as a spec artifact before §11 signature. |
| Signed-spec dependencies | `Layer_5_Aggregate_Challenge_Pass_Deep_Dive.md` (§11 SIGNED 2026-06-07), `Agent_Design_Contract_Template_Deep_Dive.md` (§11 SIGNED + §11.A), `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At signing, this agent is at **Evidence Stage 1**. Signing this contract is the Build Authorization for the Section 5 code implementation at Evidence Stage 1. No build authorization is granted for Evidence Stage 2 or Stage 3 registration until the §6.2 promotion conditions are satisfied and a separate promotion record is signed. |

---

## §0 Purpose

The Layer 5 Aggregate Challenge Pass spec (§11 SIGNED 2026-06-07) built the spine.
Section 6 proved the mechanism is trustworthy and documented its gaps. This contract
is the first Challenge agent that actually uses that spine.

The agent's job is narrow: look at what the governed Detection agents observed
independently across different email surfaces, and answer one question — do these
signals genuinely corroborate each other, or does the aggregate picture not hold up?
It is a false-positive reducer and an independent second pass, not a vote counter and
not a decision maker.

Nothing here changes any detector. Nothing changes the Commander's disposition rules.
The only new thing is a governed Layer 5 agent that can say "these independent signals
point at the same attack pattern" or "this single weak signal does not warrant
escalation."

---

## §1 Scope

### In scope
- The Agent Design Contract block above.
- The corroborate-not-vote-count behavioral rule (D4) as an enforceable contract
  clause, not just a stated principle.
- The Evidence Stage 1 (Synthetic) declaration and the promotion/demotion path.
- The §10.A operator decisions: Q1 cross-arbitration Option B, Q2 `challenge_basis`
  enforcement Option A, Q3 `agent_id` confirmed.

### Out of scope
- Any change to detector logic, scoring, or `analyze()` behavior (immutable, D6).
- Any change to `_determine_disposition` precedence rules (D2; unchanged).
- Any second Challenge agent (cross-arbitration logic is deferred per §10.A Q1).
- Any change to `DecisionEvidenceRecord` fields in `agent_contract.py`.
- `build_default_registry` registration (Evidence Stage 1 forbids it).
- Any autonomous action, buyer-facing claim, or Stage B/C autonomy.

---

## §2 Locked Design Decisions (confirmed at §11)

- **D1 — Identity.** `AggregateCorroborationAgent`, Layer 5 Challenge/Red-Team,
  Authority Level 5 (this signature is the authority decision per template §10.A Q3),
  VISION Stage A, Evidence Stage 1 (Synthetic) at signing.
  `agent_id = "aggregate_corroboration_001"`.
- **D2 — Verdict only.** Returns one `ChallengeResult | None` per case. No
  `AgentContribution` written; no disposition authored; Commander owns routing.
- **D3 — Facts-only input surface.** Reads `AgentContribution.observed_facts` and
  `AgentContribution.layer` only. No detector internals, no reasoning trace, no raw
  email payload (Layer 5 spec D3). `AgentContribution` has no `reasoning_trace`
  field — confirmed clean by Section 6 ADV-004.
- **D4 — Corroborate, do not vote-count (enforceable contract clause).** A verdict
  of `confirmed` requires `challenge_basis` to name the corroborating surfaces and
  the attack-pattern connection. A basis of "N signals fired" or equivalent is a
  contract violation. The Section 5 test suite enforces this via an adversarial
  probe that asserts `challenge_basis` does not contain count-only language and does
  name independent surfaces. This closes failure register ADV-005.
- **D5 — `challenge_basis` constraint.** One client-safe sentence, max 160 chars.
  Must name the corroborating surfaces or the contradiction basis. Must not echo raw
  header values. Must not be count-only language. Must not be empty on a non-`None`
  return.
- **D6 — No detector logic change.** No change to any Detection agent, its scoring,
  or its `analyze()` behavior (Layer 5 spec D6).
- **D7 — Evidence Stage governance.** Evidence Stage 1 at signing; template §6.2/
  §6.3/§6.5 apply in full.
- **D8 — Stage A / no autonomy.** `autonomous_action_allowed = False`. Router guard
  enforces before invocation.
- **D9 — Cross-arbitration posture.** v1 keeps the Commander's existing precedence
  rules (any `contradicted` → `human_required`, any `inconclusive` → `hold`). No
  cross-arbitration logic is built in this contract. The second Challenge agent's
  contract must resolve it. (§10.A Q1 Option B; closes failure register KG-002 as
  a named deferred decision.)

---

## §3 Corroboration rule — behavioral specification (D4 expanded)

The naive implementation votes: if N signals fired, return `confirmed`. This is the
failure mode the Layer 5 spec §4 and failure register ADV-005 name explicitly. This
agent must not vote.

The correct implementation corroborates: for each `AgentContribution` in the set,
determine whether its `observed_facts` are consistent with a coherent attack pattern,
whether they contradict it, or whether the evidence is insufficient. The verdict
earns its strength from the attack-pattern connection, not the count.

**Compliance test (D4 enforcement):**
- Given three contributions with weak, benign-explained, non-overlapping facts → must
  return `inconclusive` or `contradicted`, not `confirmed`.
- Given two contributions whose facts independently point at the same spoofed sending
  domain (e.g. `from_reply_to_divergence` from Header Analysis + `dmarc_fail` from
  Email Authentication) → `confirmed` is appropriate; `challenge_basis` must name
  the surfaces (e.g. "Reply-To divergence and DMARC failure independently indicate
  spoofed sending domain.").

Both cases are required Class 1 expected-pass tests. The adversarial count-language
probe is a required Class 2 break-it test.

---

## §4 Evidence Stage declaration

- **Current Evidence Stage: 1 — Synthetic.** Synthetic test data only; not in
  production dispatch.
- **To reach Stage 2 (Supervised):** template §6.2 Stage 1→2 conditions, including
  Matt's review of >= 3 real email contribution sets and a signed `PROMOTION` entry.
- **To reach Stage 3 (Production):** template §6.2 Stage 2→3 conditions, including
  Drift Watch active. Stage 3 grants no autonomous action (template §6.0).
- **Demotion:** template §6.3 triggers apply.

---

## §5 Conceptual evidence contribution (template §5 interface)

These seven fields describe what this agent contributes conceptually. They are NOT
new fields on the `DecisionEvidenceRecord` Pydantic class — that class stores
`contributions`, `challenge_pass`, and `disposition` and is not modified by this
contract. The seven fields are the template §5 evidence shape, expressed for this
agent.

- **observed_facts:** none — Challenge layer does not emit detection facts.
- **interpretations:** the corroboration or contradiction basis in `challenge_basis`.
- **assumptions:** each `AgentContribution` in the tuple was emitted by a governed
  Detection agent running on the same email case.
- **missing_evidence:** expressed as `challenge_outcome = inconclusive` when
  contributions are empty, contradictory without a corroborating surface, or
  insufficient to reach a verdict.
- **recommended_verification:** none authored at this layer — `contradicted` signals
  the Commander to route to `human_required`, which is the verification escalation.
- **final_outcome_contribution:** one `ChallengeResult` per case, one verdict per
  agent.
- **retest_or_learning_record:** every real-case miss or demotion trigger becomes a
  permanent regression test per template §6.5.

---

## §6 Failure modes

- **Vote-counting** — `confirmed` based on `len(contributions)` alone. Mitigation:
  D4 as an enforceable contract clause + adversarial probe in Section 5 suite.
- **Authority drift** — verdict treated as disposition by the agent or caller.
  Mitigation: D2; Commander owns disposition; no autonomous action.
- **Reasoning-trace access** — reading detector internals. Mitigation: D3; input
  surface is contribution tuple + `MissionContext` digest; no internals exist on
  `AgentContribution`.
- **Empty-basis confirmation** — `confirmed` with no surface-naming basis. Mitigation:
  D5 + test that validates basis content on every non-`None` return.
- **Over-contradiction** — `contradicted` on a single weak signal, forcing unnecessary
  `human_required`. Mitigation: `inconclusive` is the correct output for a single
  weak signal; test must cover this path.
- **Stage creep** — registering in `build_default_registry` at Evidence Stage 1.
  Mitigation: D7 + Evidence Stage 1 "not in production dispatch" rule.
- **Authority-level wiring mismatch** — registry entry declares `authority_level=3`
  (the test-double default) instead of `authority_level=5` → `GovernanceError:
  metadata diverges`. Mitigation: D1 + wiring note in contract block + Section 5
  test suite must construct registry entries with `authority_level=5`.

---

## §7 Required tests (plan — execution lane implements after §11 signature)

**Class 1 — Expected pass:**
- Two contributions from independent surfaces pointing at the same attack pattern
  → `confirmed`; `challenge_basis` names the surfaces.
- Single weak contribution with benign explanation → `inconclusive`.
- Empty contributions tuple → `None`.
- Facts internally inconsistent across contributions → `contradicted`.
- `agent_id` on returned `ChallengeResult` == `"aggregate_corroboration_001"`.
- `challenge_basis` <= 160 chars on all non-`None` paths.
- `analyze()` raises `AssertionError`.
- `autonomous_action_allowed` is `False`.
- Registry entry with `authority_level=5` passes the Commander's metadata-match guard.

**Class 2 — Adversarial / break-it:**
- Vote-counting probe: N contributions with weak, benign-explained, non-overlapping
  facts → must NOT return `confirmed`. (Closes ADV-005.)
- Count-language basis probe: any `confirmed` result must not contain count-only
  language ("N signals", "3 detectors", "majority"); must name surfaces.
- Empty-basis probe: agent must never return a `ChallengeResult` with an empty
  `challenge_basis`.
- Over-contradiction probe: single weak signal must not return `contradicted`.
- Authority-level mismatch probe: registry entry with `authority_level=3` → confirms
  `GovernanceError: metadata diverges` is raised.

**Class 3 — Known-gap xfail:**
- Real-email verdict quality: blocked until Stage 2 real contribution sets.
- Cross-arbitration: second Challenge agent conflict deferred per §10.A Q1 / D9.

---

## §10 Open Questions

All three questions are resolved in §10.A below.

### §10.A Operator-Confirmed Decisions (2026-06-08)

**Q1 — Multi-Challenge-agent cross-arbitration (closes failure register KG-002).**
**Option B — Explicit deferral.** v1 keeps the Commander's existing most-cautious-wins
precedence (any `contradicted` → `human_required`, any `inconclusive` → `hold`). No
cross-arbitration logic is built in this contract. The gap is named here; the second
Challenge agent's contract must resolve it. The KG-002 xfail in the Section 5 suite
keeps the gap visible. Locked as D9.

**Q2 — `challenge_basis` enforcement.**
**Option A — Contract + test, no runtime self-validation.** D4/D5 state the rule; the
Class 2 adversarial probe in the Section 5 test suite enforces it. Runtime
self-validation is a weaker guarantee than an independent test. The count-language
probe is a string heuristic — correct to use as a probe; not oversold as airtight
enforcement.

**Q3 — `agent_id` string.**
**Confirmed:** `"aggregate_corroboration_001"`. Consistent with the existing
`_challenge_entry` convention and the codebase `_001` suffix pattern.

---

## §11 Sign-off

§11 SIGNED. §10 is resolved in §10.A. This signature locks D1-D9 + §10.A as the
Aggregate Corroboration Agent Design Contract and authorizes the Section 5 code
implementation at Evidence Stage 1 (Synthetic).

This signature authorizes NO detector-logic change, NO `_determine_disposition`
change, NO `DecisionEvidenceRecord` schema change, NO `build_default_registry`
registration, NO production dispatch, and NO autonomous action. Evidence Stage 2/3
promotion is a separate, later, Matt-signed event per template §6.2.

> §11 SIGNATURE — Matt Nichol June 8th
