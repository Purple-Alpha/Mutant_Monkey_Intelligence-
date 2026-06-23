# Mission Context Agent Design Contract — Contract Review Draft

**Draft ID:** `MMI_02_MISSION_CONTEXT_AGENT_DESIGN_CONTRACT_REVIEW_DRAFT`

**Status:** §11 SIGNED 2026-06-21 by Matt Nichol. Pre-build gate manifest repaired 2026-06-22 (re-run `mmi_02_contract_gate` for 0/0 receipt; gate receipt SHA to be pinned on next clean run). Locks D1–D10, MC-AUTH case-classifier spine, and closed classification vocabularies. Authorizes **contract text only** — **no** build, **no** `SIGNED_UNBUILT`, **no** scoreboard lifecycle promotion, **no** AUTH-5.

**Candidate:** #2 — Mission Context

**Owner:** Matt Nichol

**Track:** Command-layer case classifier (Layer 1 Command — classify-only boundary)

**Lane:** Agent Design Contract (frozen design-draft storage; not Build Authorization)

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** **BLOCKED** until separate operator Build Authorization. §11 signature (when granted) does not authorize wrapper build, registry dispatch, `MissionContext` schema mutation on disk, or `SIGNED_UNBUILT` reconcile.

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (template shape only — this draft is not §11-signed)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#2 Mission Context — inventory row; scoreboard prose may drift; this contract locks the spine boundary)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (Layer 1 Command — §1.2 Mission Context Agent)
- `docs/mmi/contracts/001_swarm_commander_contract.md` (#1 sibling — §11 SIGNED; route commander)
- `docs/mmi/contracts/003_risk_triage_contract.md` (#3 sibling — §11 SIGNED; telemetry scorer)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`MissionContext` type — **partial** spine seam; no governed classifier agent yet)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/swarm_commander.py` (legacy Commander consumes caller-supplied `MissionContext` + agent lists — **no** #2 classifier wired)
- `VISION.md` (Stage A analyze/evidence posture)
- `AGENTS.md` (authority / gate discipline)

**#105 Governance Invariants (compatibility only):** This draft is **designed to align** with `#105` posture (classify-only telemetry, no autonomous action, human-in-the-loop downstream). It **must not depend** on unsigned or ungated #105 authority beyond Lane 1 probe compatibility. #105 alignment is informative, not a prerequisite for this draft to exist or be reviewed.

**MMI brain AUTH namespace note:** Command-spine authority labels declared in `docs/mmi/contracts/` are **contract-local** for governed agent wrappers. They are **not** MMI brain `AUTH-*` gates (`mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md`). No collision between spine labels and MMI Tier gates is implied.

---

## Spine boundary (core invariant)

```text
#2 classifies; it never routes, dispatches, scores, mitigates, or assembles disposition.
#1 routes; it never scores.
#3 scores; it never routes, dispatches, recommends, alerts, blocks, quarantines, or triggers mitigation.
```

**Interpretation:** Mission Context (#2) owns **case-type classification**, **required review depth**, and **required evidence manifest** under a declared taxonomy. Swarm Commander (#1) owns registry-validated dispatch and DER assembly. Risk Triage (#3) owns numeric risk telemetry only. No agent may hold two of these authorities in one envelope.

**Downstream consumption rule:** #1 (or the operator) may **read** #2 classification output when selecting Pass-1 / Pass-2 agent lists — but #2 output is **advisory structure only** until a **separate signed routing-policy annex** binds classification → agent manifests. #2 must never emit registry dispatch commands, `agents[]` ordering, or disposition.

---

## Agent Design Contract block

| Field | Value |
|---|---|
| Agent name | Mission Context Agent (`MissionContextAgent` — proposed governed wrapper name TBD at Build Authorization) |
| Swarm inventory ID | #2 — Mission Context |
| Canonical layer | 1 — Command (case classifier slot; **not** route commander, **not** telemetry scorer) |
| Canonical team / case type | Cross-cutting Stage A case framing; consumes blackboard / analysis record pointers |
| Authority level | **MC-AUTH — Case Classifier** (see narrowed declaration below) |
| Stage posture | VISION Stage A — structured classification only; no tenant action |
| Evidence Stage (current) | **Not promoted** — draft/review only |
| Role | Accept validated case inputs; classify case type; declare required review depth; emit required-evidence manifest — **no routing, no scoring, no narrative** |
| Boundary | Classify-in-structure-out. Closed vocabulary case types + evidence requirements only. No dispatch, no mitigation, no score telemetry |
| Explicit non-authorities | See MC-AUTH and prohibited behaviors below |
| Inputs | `tenant_id`, `inputs_digest`, `source_record_id` (or successor blackboard pointer), optional detector summary refs — per Section 3 |
| Outputs | Strict allowlist classification envelope (Section 6) |
| Evidence emitted | One classification record per case with taxonomy version + input provenance |

---

## MC-AUTH — Case Classifier (narrowed)

**MC-AUTH grants only:**

- Classify the case into one **closed vocabulary** `case_type` (Section 6).
- Declare `review_depth` (closed vocabulary depth tier for downstream review posture — **not** disposition).
- Emit `required_evidence` manifest: ordered or unordered list of **evidence capability tags** or **registry agent capability ids** that the case class requires — **manifest only**, not invocation.
- Echo `classification_policy_version` and input provenance (`inputs_digest`, `source_record_id`, accepted detector refs).
- Optionally emit `case_type_confidence` as a **numeric telemetry field** describing classifier certainty — **not** risk score, **not** rubric-axis math (**#3 domain**).

**MC-AUTH explicitly does not grant:**

| Forbidden authority | Rule |
|---|---|
| Routing / dispatch authority | No `agents[]`, `challenge_agents[]`, `target_agent`, `dispatch`, `lane`, or invocation order — **#1 only** |
| Scoring / telemetry authority | No `aggregate_risk_score`, `axis_scores`, rubric-axis computation, or scoring reason codes — **#3 only** |
| Disposition authority | No `disposition`, `human_state`, `escalate`, mitigation, or review **decision** — **#1 assembly only** |
| Mitigation authority | No block, quarantine, contain, alert, notify, or trigger-mitigation semantics |
| Autonomous tenant action | `autonomous_action_allowed` must remain false on governed #2 wrapper; Stage A only |
| Narrative / client copy | No plain-English explanations, verification instructions, or buyer-facing artifacts (**#52 domain**) |
| Registry / scoreboard mutation | No agent discovery, promotion, demotion, or lifecycle writes |
| Operator-delegated approval authority | Classification informs review scope; it does **not** authorize Matt or tenant action by itself |

**Relation to #1 and #3:** #1 routes; #3 scores; #2 classifies. #2 must never substitute for #1 or #3. If all three appear in a pipeline, ordering is: **#2 classification → (optional) Pass-1 detectors → (optional) #3 telemetry → #1 dispatch/assembly** — exact orchestration binding requires a signed routing-policy annex; this draft does not authorize production wiring.

---

## §0 Purpose

Mission Context (#2) is the command-layer **case classifier**: it turns validated case inputs into a structured classification envelope (case type, review depth, required evidence manifest). It does **not** dispatch agents, does **not** compute risk telemetry, does **not** assemble disposition, and does **not** produce client-facing explanations.

This draft exists to complete the Command spine contract trio (#1 routes / #2 classifies / #3 scores) at the review layer — without Build Authorization, §11 signature, or `SIGNED_UNBUILT` promotion.

---

## §1 Scope

### In scope

- Contract-review definition of #2 role, MC-AUTH boundary, inbound validation, outbound allowlist, and spine split with #1 and #3.
- Closed vocabulary for `case_type` and `review_depth` (Section 6).
- Required-evidence manifest semantics (capability tags — not dispatch).
- Alignment with `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` §1.2 responsibilities.
- Explicit rejection of routing, scoring, disposition, and plain-English artifact generation by #2.

### Out of scope

- Build Authorization, implementation promotion, `MissionContext` pydantic field additions on disk, or production dispatch.
- §11 signature or `SIGNED_UNBUILT` scoreboard reconcile.
- Swarm Commander (#1) routing-policy annex (separate signed artifact).
- Risk Triage (#3) scoring policy or build (governed by `003_risk_triage_contract.md`).
- Human-in-the-Loop (#4), Decision Integrity (#5), Severity Commander (design-tree §1.3 label) — separate contracts.
- Client-facing copy, verification instructions, or buyer claims.
- Blackboard writes beyond a **separate signed persistence seam** (not authorized here).
- MMI dispatcher routing, PM Voice authority, or AUTH-5 autonomous selection.

---

## §2 Locked design decisions (draft — unsigned)

| # | Decision | Locked value (pending operator review) |
|---|---|---|
| D1 | Spine split | #2 classifies never routes/scores; #1 routes never scores; #3 scores never routes |
| D2 | MC-AUTH scope | Case classifier only; table in MC-AUTH section is exhaustive for this draft |
| D3 | Closed taxonomy | `case_type` and `review_depth` use closed vocabularies only — no free-text case labels in v1 |
| D4 | Evidence manifest | `required_evidence` lists capability requirements — not agent dispatch instructions |
| D5 | No routing keys | Outbound envelope must not contain dispatch, disposition, or score telemetry fields |
| D6 | Policy versioning | `classification_policy_version` required on every output; no silent taxonomy drift |
| D7 | Input trust | Blackboard/detector inputs are untrusted until provenance + schema validation pass |
| D8 | #1 consumption | #1 may read #2 output only as advisory input until routing-policy annex signed |
| D9 | Stage A only | No autonomous action path; classifier emits structure only |
| D10 | Lifecycle | Draft/review storage only until separate operator §11 + Build Authorization path |

---

## §3 Inputs — untrusted case material

### Required envelope fields (inbound)

| Field | Requirement |
|---|---|
| `tenant_id` | Tenant scope for classification tagging only; **no** tenant policy mutation |
| `inputs_digest` | SHA-256 digest of material under review per `agent_contract.py` / Commander seam |
| `source_record_id` | Blackboard or analysis record pointer (UUID) — primary case material locator |
| `classification_policy_version` | Declared taxonomy id + version string #2 must echo on output |

### Optional inbound fields

| Field | Requirement |
|---|---|
| `detector_summary_refs` | Opaque refs to already-emitted detector contributions — **read-only**; not re-scored by #2 |
| `message_id` | Correlation id for telemetry tagging only |

### Input validation rules

1. **Provenance required:** Missing `inputs_digest` or `source_record_id` → fail closed (`INPUT_PROVENANCE_MISSING`).
2. **No routing keys inbound:** Payloads must not contain `agents`, `dispatch`, `disposition`, `aggregate_risk_score`, or semantically equivalent hints. If present → reject (`INPUT_ROUTING_KEY_FORBIDDEN`).
3. **No scorer authority inbound:** #2 must not treat inbound numeric scores as binding classification shortcuts without declared policy rules in a **separate signed classification-policy annex** — v1 default: detector numerics are **not** classification inputs.
4. **Schema validation:** Unknown top-level keys stripped or rejected per build-time parser rules.

---

## §4 Classification behavior (never routes or scores)

### Permitted computation

- Map validated inputs to one `case_type` from Section 6 closed vocabulary.
- Map to one `review_depth` tier from Section 6 closed vocabulary.
- Build `required_evidence` manifest from taxonomy rules (capability tags / registry capability ids).
- Emit `classification_reason_codes` — machine enums tied to input refs (not prose).
- Echo `classification_policy_version` and provenance chain.

### Prohibited computation / artifacts

- Agent dispatch lists, invocation order, or registry lookups that **execute** routing.
- Rubric-axis values, `aggregate_risk_score`, or scoring reason codes (**#3 domain**).
- `disposition`, `human_state`, `escalate`, mitigation commands (**#1 domain**).
- Client-facing explanations, advice, `recommended_action`, or verification instructions.
- Plain-English case narratives or buyer-facing copy (**#52 domain**).
- Scoreboard/registry/lifecycle mutation.

### `case_type_confidence` — classifier telemetry, not risk authority

If emitted:

- **May** inform downstream review or explanation inputs.
- **Must not** auto-route, auto-escalate, auto-block, or substitute for #3 risk telemetry.
- **Must not** by itself authorize tenant action.

---

## §5 Classification provenance (mandatory)

| Rule | Requirement |
|---|---|
| Traceability | Each `case_type` / `review_depth` maps to: (a) accepted input refs, and (b) `classification_policy_version` |
| Declared taxonomy | All case-type → evidence-manifest rules live in signed classification-policy annex for that version |
| Stable mapping | Taxonomy changes require version bump + operator-signed policy update — **no silent relabeling** |
| No live learning | **No live learning loop** that mutates taxonomy from production traffic inside #2 |
| Audit replay | Same validated inputs + policy version → same classification output (deterministic path) or explicit non-determinism recorded |

---

## §6 Outbound schema — strict allowlist

### Closed vocabulary — `case_type` (v1 draft)

| Code | Meaning (internal) |
|---|---|
| `phishing` | Credential / link / impersonation phishing pattern |
| `vendor_payment_fraud` | Payment redirect / banking detail change fraud |
| `business_email_compromise` | BEC-style trusted-thread abuse |
| `executive_impersonation` | CEO/CFO-style impersonation |
| `invoice_fraud` | Invoice manipulation / fake invoice |
| `payroll_diversion` | Payroll / HR payment redirect |
| `ransomware_precursor` | Precursor signals — not full incident classification |
| `cyber_insurance_evidence` | Evidence-package / audit-request framing |
| `unknown` | Insufficient signal — explicit unknown; not a silent default |

**v1 rule:** Exactly one `case_type` per envelope. `unknown` is allowed; silent omission is not.

### Closed vocabulary — `review_depth` (v1 draft)

| Code | Meaning |
|---|---|
| `standard` | Default Stage A detector + verification path |
| `enhanced` | Additional verification / challenge agents per manifest |
| `human_required` | Classification declares human review scope — **not** the same field as Commander `human_state`; downstream #1 / HITL agents reconcile |

### Allowed fields

| Field | Type / notes |
|---|---|
| `tenant_id` | string |
| `inputs_digest` | string — echo inbound |
| `source_record_id` | uuid string — echo inbound |
| `case_type` | enum — Section 6 vocabulary |
| `review_depth` | enum — Section 6 vocabulary |
| `required_evidence` | array of capability tag strings (e.g. `header_analysis`, `payment_change_detection`, `verification_outcome`) — **manifest only** |
| `classification_reason_codes` | array of machine enums |
| `classification_policy_version` | string |
| `case_type_confidence` | number 0–1 optional — classifier certainty only |
| `classification_record_id` | uuid optional |
| `emitted_at` | timestamp optional |

### Prohibited fields (non-exhaustive — any command-like field forbidden)

- `agents`, `challenge_agents`, `target_agent`, `route_to`, `dispatch`, `lane`, `handoff_to`
- `disposition`, `human_state`, `escalate`, `next_action`, `NEXT_DECIDED`
- `aggregate_risk_score`, `axis_scores`, `scoring_reason_codes`
- `contain`, `block`, `quarantine`, `alert`, `notify`, `recommended_action`, `authorized`
- `plain_english_summary`, `client_message`, `verification_instructions`, `narrative`, `advice`
- `tenant_policy_patch`, `promotion`, `demotion`, registry mutation keys

**Violation posture:** Authority probes must treat prohibited routing, scoring, or command fields emitted by the governed #2 wrapper as `AUTHORITY_INVARIANT_BREACH`.

---

## §7 Relationship to sibling agents and legacy surfaces

| Agent / surface | Relationship |
|---|---|
| #1 Swarm Commander | Downstream route commander; may consume #2 classification as **advisory** input per future routing-policy annex; never classifies. Governed by signed `001_swarm_commander_contract.md`. |
| #3 Risk Triage | Sibling scorer; parallel telemetry path; #2 never consumes #3 scores as binding classification input in v1. Governed by signed `003_risk_triage_contract.md`. |
| `MissionContext` (`agent_contract.py`) | Legacy/minimal case framing type (`case_id`, `tenant_id`, `inputs_digest`, `source_record_id`). **Does not yet carry** `case_type` / `required_evidence`. Governed wrapper + schema extension are **Build Authorization** — not this draft. |
| Detectors (#6, #10, …) | Upstream evidence producers; may inform classification via `detector_summary_refs` only — untrusted until validated. |
| #52 Plain-English Explanation | Downstream narrative consumer; #2 must not emit plain-English artifacts. |
| #4 Human-in-the-Loop | Downstream reviewer gate; may consume `review_depth` — separate contract TBD. |
| Legacy `swarm_commander.py` | Caller supplies `agents[]` today; no #2 classifier wired. Promotion requires routing-policy annex + #2 wrapper. |

---

## §8 Failure modes

| Failure mode | Detection | Response (classifier-local only) |
|---|---|---|
| Routing key in input | Inbound validator | Reject; `INPUT_ROUTING_KEY_FORBIDDEN` |
| Missing provenance | Inbound validator | Fail closed; `INPUT_PROVENANCE_MISSING` |
| Unknown `case_type` emitted | Outbound validator | Contract violation — closed vocabulary only |
| Score telemetry on #2 path | Outbound validator / authority probe | `AUTHORITY_INVARIANT_BREACH` |
| Dispatch list on #2 path | Outbound validator / authority probe | `AUTHORITY_INVARIANT_BREACH` |
| Disposition on #2 path | Outbound validator | `AUTHORITY_INVARIANT_BREACH` |
| Plain-English leakage | Outbound schema scan | Contract violation |
| Taxonomy drift | Policy version audit | Block promotion until classification-policy annex updated |
| #1 / #3 boundary bleed | Authority probe | Classifier attempted routing or scoring semantics |

---

## §9 Build path (not authorized)

**Proposed future path (frozen for review only):**

`3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/command/mission_context_agent.py`

Build Authorization must also specify:

- Whether `MissionContext` gains optional classification fields vs separate `MissionClassification` envelope.
- Signed **classification-policy annex** (taxonomy rules → `required_evidence` manifests).
- Signed **routing-policy annex** (#2 output → Commander `agents[]` hints) — if any automation is desired.

No file creation, registry entry, schema mutation, or scoreboard `SIGNED_UNBUILT` reconcile is authorized by this draft.

---

## §10 Open questions (draft)

1. **Classification-policy annex** — which artifact owns taxonomy → `required_evidence` rules at Build Authorization?
2. **Routing-policy annex** — may #1 auto-expand `agents[]` from #2 manifest, or operator/caller declaration only in v1?
3. **`review_depth` vs Commander `human_state`** — explicit handoff rules to #4 Human-in-the-Loop (contract TBD).
4. **`unknown` case_type** — fail-open manifest (minimal detectors) vs fail-closed (human_required depth only)?
5. **Cyber-insurance evidence case type** — carve-out scope vs overlap with #46 Evidence Package agent.
6. **Whether `required_evidence` entries** are registry `agent_id` strings vs capability tags (recommendation: capability tags in v1 to avoid dispatch laundering).

---

## §11 Sign-off — SIGNED 2026-06-21

Signed by Matt Nichol on 2026-06-21 after manifest repair for Grok pre-build gate `mmi_02_contract_gate` (re-run for 0/0 receipt). Locks D1–D10, MC-AUTH, inbound/outbound schema, and closed vocabularies in Section 6. Authorizes contract text only. Does **not** authorize build, `SIGNED_UNBUILT`, scoreboard reconcile, or AUTH-5.

### Sign-off line

> Matt Nichol June 21st 2026

Per Authorship Rule: operator-authored signature, placed verbatim.

---

**End of contract. §11 in force as of 2026-06-21 (MMI-DEC-105).**
