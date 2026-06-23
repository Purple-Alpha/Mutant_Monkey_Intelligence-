# Swarm Commander Agent Design Contract — Contract Review Draft

**Draft ID:** `MMI_01_SWARM_COMMANDER_AGENT_DESIGN_CONTRACT_REVIEW_DRAFT`

**Status:** §11 SIGNED 2026-06-21 by Matt Nichol. Pre-build gate clean 0/0 (`audit_outputs/mmi_01_contract_gate_20260622T032315Z.md`; packet SHA256 `82806c4c32ca6920d426b9f26e190df52feefb4a3fea775c0ebdbaccc99e1035`; MMI-DEC-101). Locks D1–D10, RC-AUTH route-commander spine, and DER assembly boundary. Authorizes **contract text only** — **no** build, **no** `SIGNED_UNBUILT`, **no** scoreboard lifecycle promotion, **no** AUTH-5.

**Candidate:** #1 — Swarm Commander

**Owner:** Matt Nichol

**Track:** Command-layer route commander (Layer 1 Command — route-only boundary)

**Lane:** Agent Design Contract (frozen design-draft storage; not Build Authorization)

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** **BLOCKED** until separate operator Build Authorization. §11 signature does not authorize wrapper promotion, registry default dispatch, or `SIGNED_UNBUILT` reconcile.

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (template shape only — this draft is not §11-signed)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#1 Swarm Commander — inventory row; scoreboard prose may drift; this contract locks the spine boundary)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (Layer 1 Command — §1.1 Swarm Commander)
- `docs/mmi/contracts/003_risk_triage_contract.md` (#3 sibling — §11 SIGNED; score-only telemetry spine)
- `4. Product_Roadmap/Layer_5_Aggregate_Challenge_Pass_Deep_Dive.md` (Pass-2 challenge orchestration; Commander owns disposition)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/swarm_commander.py` (legacy Stage A case loop — **partial** spine; not formally promoted governed agent)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/routes.py` (`validate_agent_dispatch` guard)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (DER + `Agent` interface)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/registry.py` (dispatch metadata)
- `VISION.md` (Stage A analyze/evidence posture)
- `AGENTS.md` (authority / gate discipline)

**#105 Governance Invariants (compatibility only):** This draft is **designed to align** with `#105` posture (no autonomous action, human-in-the-loop downstream, authority probes). It **must not depend** on unsigned or ungated #105 authority beyond Lane 1 probe compatibility. #105 alignment is informative, not a prerequisite for this draft to exist or be reviewed.

**MMI brain AUTH namespace note:** Swarm-spine authority labels declared in `docs/mmi/contracts/` are **contract-local** for governed agent wrappers. They are **not** MMI brain `AUTH-*` gates (`mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md`). No collision between spine labels and MMI Tier gates is implied.

---

## Spine boundary (core invariant)

```text
#1 routes; it never scores.
#3 scores; it never routes, dispatches, recommends, alerts, blocks, quarantines, or triggers mitigation.
```

**Interpretation:** Swarm Commander (#1) owns routing, dispatch, registry-validated invocation order, conservative disposition assembly, and human-review path selection. Risk Triage (#3) owns numeric risk telemetry only. No agent may hold both authorities in one envelope. #1 may **read** #3 telemetry as optional evidence input to a **separate signed routing-policy annex**; #1 must **never** compute rubric-axis values, `aggregate_risk_score`, or scoring reason codes.

---

## Agent Design Contract block

| Field | Value |
|---|---|
| Agent name | Swarm Commander Agent (`SwarmCommander` — proposed governed wrapper name TBD at Build Authorization) |
| Swarm inventory ID | #1 — Swarm Commander |
| Canonical layer | 1 — Command (route commander slot; **not** telemetry scorer) |
| Canonical team / case type | Cross-cutting Stage A case orchestration; registry-gated agent dispatch |
| Authority level | **Route Commander (RC-AUTH)** — see narrowed declaration below |
| Stage posture | VISION Stage A — route and assemble evidence; no tenant action |
| Evidence Stage (current) | **Not promoted** — draft/review only |
| Role | Accept `MissionContext` + explicit agent lists; validate registry metadata; dispatch Pass-1 `analyze()` and optional Pass-2 `challenge()` per signed Layer 5 rules; assemble in-memory `DecisionEvidenceRecord`; emit conservative disposition — **no risk scoring** |
| Boundary | Route-in-DER-out. Registry dispatch + contribution aggregation only. No scoring, no mitigation, no narrative artifacts |
| Explicit non-authorities | See RC-AUTH and prohibited behaviors below |
| Inputs | `MissionContext`, declared `agents[]`, optional `challenge_agents[]`, registry entries, optional read-only #3 score telemetry envelope |
| Outputs | `DecisionEvidenceRecord` assembly (Section 6 allowlist semantics) |
| Evidence emitted | One DER per case with contributions + challenge_pass + disposition + timestamps; **no** score telemetry authored by #1 |

---

## RC-AUTH — Route Commander (narrowed)

**RC-AUTH grants only:**

- Validate each candidate agent against its signed registry entry (`layer`, `authority_level`, `stage_allowed`, `autonomous_action_allowed`) before invocation.
- Invoke `validate_agent_dispatch` (or successor guard) before any `analyze()` or `challenge()` call.
- Dispatch Pass-1 agents in the **caller-declared order** (no autonomous agent discovery or promotion).
- Dispatch Pass-2 Layer 5 challenge agents **once per case** over the full contribution set per `Layer_5_Aggregate_Challenge_Pass_Deep_Dive.md`.
- Assemble `DecisionEvidenceRecord` from agent-returned contributions and challenge results.
- Compute **conservative disposition** from contribution facts + challenge outcomes using a **declared, versioned disposition rule set** — **no risk arithmetic**, no rubric-axis math, no hidden weights.
- Set `human_state` from disposition mapping (`human_required` → `requested`; otherwise `not_required`).
- Optionally attach `evidence_anchor` only via explicit `anchor_provider` injection (Evidence Package Agent seam — #1 does not seal packages).

**RC-AUTH explicitly does not grant:**

| Forbidden authority | Rule |
|---|---|
| Scoring / telemetry authority | No `aggregate_risk_score`, `axis_scores`, rubric-axis computation, or scoring reason codes — **#3 only** |
| Mitigation authority | No block, quarantine, contain, alert, notify, or trigger-mitigation semantics |
| Autonomous tenant action | `autonomous_action_allowed` must remain false on governed #1 wrapper; Stage A only |
| Agent discovery / promotion | No registry mutation, no default-on wiring, no unprompted agent registration |
| Narrative / client copy | No plain-English explanations, verification instructions, or buyer-facing artifacts |
| Package sealing | No evidence package generation or sealing inside #1 |
| Audit authority | No `audit_record_id` writes (Final Review Agent only per `agent_contract.py`) |
| Scoreboard authority | No updates to `Blue_Team_Swarm_70_Agent_Scoreboard.md` or inventory lifecycle state |
| Operator-delegated approval authority | Disposition informs review posture; it does **not** authorize Matt or tenant action by itself |

**Relation to #3:** #3 holds telemetry-scorer authority. #1 must never substitute for #3. If both appear in a pipeline, #1 consumes #3 telemetry optionally; #3 never consumes #1 routing decisions as binding input.

---

## §0 Purpose

Swarm Commander (#1) is the command-layer **route commander**: it turns a declared case context and registry-known agents into a governed dispatch sequence and one in-memory `DecisionEvidenceRecord`. It does **not** score risk, does **not** compute rubric telemetry, and does **not** produce client-facing explanations or recommended tenant actions.

This draft exists to unblock contract review, Estimator visibility, and Grok pre-build gate after BOR unpark (MMI-DEC-099) — without Build Authorization, §11 signature, or `SIGNED_UNBUILT` promotion.

---

## §1 Scope

### In scope

- Contract-review definition of #1 role, RC-AUTH boundary, registry-first dispatch, disposition assembly rules, DER allowlist, and spine split with #3.
- Alignment with signed Layer 5 aggregate challenge pass (orchestration only).
- Explicit rejection of risk scoring, rubric math, and plain-English artifact generation by #1.
- Legacy `swarm_commander.py` posture note: partial spine implementation; governed wrapper must reconcile drift (Section 7).

### Out of scope

- Build Authorization, implementation promotion, default-on activation, or production dispatch.
- §11 signature or `SIGNED_UNBUILT` scoreboard reconcile.
- Risk Triage (#3) scoring policy, retrofit, or build (governed by `003_risk_triage_contract.md`).
- Mission Context (#2), Severity Commander (#1.3 design-tree label), or other Command sub-agents — separate contracts.
- Client-facing copy, verification instructions, or buyer claims.
- Blackboard persistence of DER, package sealing, or Final Review audit writes.
- MMI dispatcher routing, PM Voice authority, or AUTH-5 autonomous selection.

---

## §2 Locked design decisions (draft — unsigned)

| # | Decision | Locked value (pending operator review) |
|---|---|---|
| D1 | Spine split | #1 routes never scores; #3 scores never routes or mitigates |
| D2 | RC-AUTH scope | Route commander only; table in RC-AUTH section is exhaustive for this draft |
| D3 | Registry-first dispatch | No invocation without registry entry + metadata match + `validate_agent_dispatch` |
| D4 | No risk arithmetic | Disposition from contribution facts + challenge outcomes only — **not** from rubric scores computed inside #1 |
| D5 | #3 consumption | Optional read-only #3 telemetry input only; #1 never recomputes scores |
| D6 | Caller-declared agents | No autonomous agent discovery; explicit `agents` / `challenge_agents` iterables only |
| D7 | DER seam | In-memory DER assembly only; sealing and `audit_record_id` belong to downstream agents |
| D8 | Layer 5 fit | Challenge pass follows signed Layer 5 spec; Commander owns disposition, not challenge verdict weight |
| D9 | Stage A only | No autonomous action path; router guard rejects autonomy claims before invocation |
| D10 | Lifecycle | Draft/review storage only until separate operator §11 + Build Authorization path |

---

## §3 Inputs

### Required envelope fields (inbound)

| Field | Requirement |
|---|---|
| `MissionContext` | Case identity + inputs digest per `agent_contract.py` |
| `agents` | Explicit iterable of Pass-1 agents to dispatch (caller-supplied order) |
| `stage` | Stage gate string (default `stage_a` in legacy slice) |
| Registry map | `dict[str, AgentRegistryEntry]` keyed by `agent_id` |

### Optional inbound fields

| Field | Requirement |
|---|---|
| `challenge_agents` | Explicit Layer 5 agents; empty by default; no auto-discovery |
| `anchor_provider` | Callable seam for future Evidence Package Agent; absent → `evidence_anchor = None` |
| `risk_triage_telemetry` | Optional read-only #3 score envelope per `003_risk_triage_contract.md` Section 6 — **never** required for dispatch to succeed |

### Input validation rules

1. **Registry presence:** Unknown `agent_id` → `GovernanceError` before invocation.
2. **Metadata match:** Runtime agent metadata must match registry entry fields (`layer`, `authority_level`, `stage_allowed`, `autonomous_action_allowed`) or dispatch fails closed.
3. **Stage + autonomy guard:** `validate_agent_dispatch` runs before every invocation.
4. **Contribution integrity:** Returned `AgentContribution.agent_id` and `layer` must match dispatched agent or dispatch fails closed.
5. **No scoring keys as routing instructions:** Inbound payloads (including optional #3 telemetry) must not be treated as authorization to skip registry guards. Forbidden routing-by-score pattern: using `aggregate_risk_score` alone to auto-select agents, auto-skip human review, or auto-escalate without a **separate signed routing-policy annex** and operator process.

---

## §4 Routing behavior (never scores)

### Permitted orchestration

- Registry-validated sequential dispatch of caller-declared Pass-1 agents.
- Optional Pass-2 Layer 5 challenge dispatch (aggregate input per signed Layer 5 spec).
- Contribution collection and DER assembly.
- Conservative disposition mapping per Section 5.
- `human_state` derivation from disposition.

### Prohibited orchestration / computation

- Rubric-axis numeric computation, `aggregate_risk_score`, or scoring reason code generation (**#3 domain**).
- Risk-band thresholds computed inside #1 without a signed routing-policy annex.
- Client-facing explanations, advice, or `recommended_action` fields.
- Autonomous block/quarantine/alert/notify to tenant systems.
- Agent registry mutation, scoreboard updates, or lifecycle promotion.
- Blackboard writes of DER (unless a **separate signed spec** authorizes a future persistence seam — not in this draft).

---

## §5 Disposition assembly (conservative rules only)

### v1 disposition precedence (aligned with legacy `swarm_commander._determine_disposition`)

Precedence (most cautious first):

1. No contributions → `human_required`
2. Any contradicted challenge → `human_required`
3. Any inconclusive challenge → `hold`
4. Any contribution `verification_outcome == contradicted` → `hold`
5. All contribution `observed_facts` empty → `clear`
6. Otherwise → `suspicious`

### Disposition rules (draft locks)

| Rule | Requirement |
|---|---|
| No risk arithmetic | Disposition logic must not compute rubric scores or weighted risk totals |
| No score thresholds in Commander | Numeric score thresholds live in signed routing-policy annex or downstream review — **not** silently embedded in Commander v1 |
| Challenge verdict weighting | Challenge agents author verdicts only; Commander maps outcomes to disposition — no authority-level weighting (Layer 5 D5) |
| Determinism | Same contributions + challenge_pass → same disposition (no hidden randomness) |
| Human gate | `human_required` disposition must map to `human_state = requested` |

**Drift trap (scoreboard watch):** If Commander starts absorbing #3 scoring or severity scoring (#1.3 design-tree label), a Command agent is making scorer-level decisions — `AUTHORITY_INVARIANT_BREACH`.

---

## §6 Outbound schema — DER assembly allowlist

#1 output is a `DecisionEvidenceRecord` per `agent_contract.py`. #1 **assembles**; it does not invent scorer telemetry.

### Allowed DER fields (assembled by #1)

| Field | Notes |
|---|---|
| `case_id` | From `MissionContext` |
| `inputs_digest` | From `MissionContext` |
| `contributions` | Tuple of agent-returned `AgentContribution` records (unchanged) |
| `challenge_pass` | Tuple of `ChallengeResult` records (unchanged) |
| `disposition` | Closed vocabulary: `clear`, `suspicious`, `hold`, `escalate`, `human_required` |
| `human_state` | `requested` or `not_required` derived from disposition |
| `timestamps` | `DecisionTimestamps` (e.g. `detected_at`) |
| `evidence_anchor` | Only when `anchor_provider` supplied; otherwise `None` |

### Prohibited fields / behaviors on #1 output path

- #1-authored `aggregate_risk_score`, `axis_scores`, `scoring_reason_codes`, or rubric telemetry blobs
- `audit_record_id` (Final Review Agent only)
- `recommended_action`, `next_action`, `dispatch_hint`, mitigation commands
- `plain_english_summary`, `client_message`, `verification_instructions`, narrative advice
- Reasoning traces / chain-of-thought storage in DER
- Any field reasonably read as autonomous tenant action or authorization

**Violation posture:** Authority probes must treat prohibited scorer or command fields emitted by the governed #1 wrapper as `AUTHORITY_INVARIANT_BREACH`.

---

## §7 Relationship to sibling agents and legacy surfaces

| Agent / surface | Relationship |
|---|---|
| #3 Risk Triage | Downstream telemetry producer; optional read-only input; never routes. Governed by signed `003_risk_triage_contract.md`. |
| #2 Mission Context | Upstream case classifier (governed by signed `002_mission_context_contract.md`); not owned by this draft. |
| Detectors (#10, #21, …) | Pass-1 contributors via `analyze()`; untrusted until their own contracts validate outputs. |
| Layer 5 Challenge agents | Pass-2 contributors via `challenge()`; verdict-only; Commander owns disposition. |
| #52 Plain-English Explanation | Downstream narrative consumer; #1 must not emit plain-English artifacts. |
| #46 Evidence Package | Downstream sealing; `anchor_provider` seam only. |
| Final Review Agent | Sole `audit_record_id` writer; #1 cannot audit DER. |
| Legacy `swarm_commander.py` | Partial spine: registry dispatch + DER assembly + v1 disposition without formal Agent Design Contract metadata. `_determine_disposition` is **routing posture assembly**, not risk scoring — but promotion requires governed wrapper + authority probe alignment with this contract. |
| Legacy `email_risk_scoring_agent.py` | Pre-contract scorer surface; **not** #1; must not be conflated with Commander routing. |

---

## §8 Failure modes

| Failure mode | Detection | Response (commander-local only) |
|---|---|---|
| Unknown agent in registry | `_entry_for` / registry lookup | `GovernanceError`; no invocation |
| Metadata divergence | `_assert_metadata_match` | `GovernanceError`; no invocation |
| Stage/autonomy guard fail | `validate_agent_dispatch` | `GovernanceError`; no invocation |
| Contribution agent_id/layer mismatch | Post-analyze check | `GovernanceError`; fail closed |
| Challenge agent not Layer 5 | Layer check | `GovernanceError`; fail closed |
| Scoring inside Commander | Authority probe / static scan | `AUTHORITY_INVARIANT_BREACH` |
| #3 boundary bleed | Authority probe | Commander attempted scorer semantics |
| Routing-by-score only | Policy audit | Block promotion until routing-policy annex signed |
| Plain-English leakage | Outbound schema scan | Contract violation |
| Autonomous action attempt | Router guard | Reject before invocation |

---

## §9 Build path (not authorized)

**Proposed future path (frozen for review only):**

Governed wrapper promotion reconciles existing `core/orchestrator/swarm_commander.py` to carry Agent Design Contract metadata and authority-probe compliance. Exact file path and registry wiring are **TBD at Build Authorization** — no default-on registry dispatch authorized by this draft.

No scoreboard `SIGNED_UNBUILT` reconcile, registry default wiring, or production dispatch is authorized by this draft.

---

## §10 Open questions (draft)

1. Signed **routing-policy annex** — when may #1 read #3 `aggregate_risk_score` vs contribution facts only for disposition hints?
2. Mission Context (#2) contract ordering — sequential gate after #1 vs parallel advisory review.
3. Whether `escalate` disposition requires a separate signed escalation spec before use in production paths.
4. Blackboard persistence seam — remain in-memory only vs future signed persistence contract.
5. Registry default wiring — which agents are eligible for caller-supplied lists vs manifest-enumerated Stage A sets at Build Authorization.
6. Reconcile scope for legacy `swarm_commander.py` — metadata-only retrofit vs replacement wrapper.

---

## §11 Sign-off — SIGNED 2026-06-21

Signed by Matt Nichol on 2026-06-21 after pre-build gate clean 0/0 (`audit_outputs/mmi_01_contract_gate_20260622T032315Z.md`; MMI-DEC-101). Locks D1–D10, RC-AUTH, registry-first dispatch, disposition rules, and DER assembly allowlist. Authorizes contract text only. Does **not** authorize build, `SIGNED_UNBUILT`, scoreboard reconcile, or AUTH-5.

### Sign-off line

> matt Nichol June 21st 2026

Per Authorship Rule: operator-authored signature, placed verbatim.

---

**End of contract. §11 in force as of 2026-06-21 (MMI-DEC-102).**
