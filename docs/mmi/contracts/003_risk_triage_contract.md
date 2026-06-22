# Risk Triage Agent Design Contract — Contract Review Draft

**Draft ID:** `MMI_03_RISK_TRIAGE_AGENT_DESIGN_CONTRACT_REVIEW_DRAFT`

**Status:** §11 SIGNED 2026-06-21 by Matt Nichol. Pre-build gate clean 0/0 (`audit_outputs/mmi_03_contract_gate_20260622T015428Z.md`; packet SHA256 `1555e24e65cef67ecc238ae8afc3a374f8c60f4de9a92c5959d8dfef9dc6e37e`). Locks D1–D9 spine boundary and AUTH-4 telemetry-scorer scope. Authorizes **contract text only** — **no** build, **no** `SIGNED_UNBUILT`, **no** scoreboard lifecycle promotion, **no** AUTH-5.

**Candidate:** #3 — Risk Triage

**Owner:** Matt Nichol

**Track:** Command-layer telemetry scorer (Layer 1 Command — score-only boundary)

**Lane:** Agent Design Contract (frozen design-draft storage; not Build Authorization)

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** **BLOCKED** until separate operator Build Authorization. §11 signature does not authorize wrapper build, registry dispatch, or `SIGNED_UNBUILT` reconcile.

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (template shape only — this draft is not §11-signed)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#3 Risk Triage — inventory row; scoreboard prose may drift; this contract locks the spine boundary)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (Layer 1 Command placement)
- `4. Product_Roadmap/Plain_English_Explanation_Agent_Design_Contract_Deep_Dive.md` (#52 downstream explanation surface — not owned by #3)
- `docs/mmi/contracts/` (companion contract-review storage; #1 Swarm Commander contract pending sibling draft)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/email_risk_scoring_agent.py` (legacy Stage A scorer — **not** governed wrapper authority; retrofit must reconcile outbound schema drift)
- `VISION.md` (Stage A analyze/evidence posture)
- `AGENTS.md` (authority / gate discipline)

**#105 Governance Invariants (compatibility only):** This draft is **designed to align** with `#105 Governance Invariants` posture (score-only telemetry, no autonomous action, human-in-the-loop downstream). It **must not depend** on unsigned or ungated #105 authority. #105 compatibility is informative, not a prerequisite for this draft to exist or be reviewed.

---

## Spine boundary (core invariant)

```text
#1 routes; it never scores.
#3 scores; it never routes, dispatches, recommends, alerts, blocks, quarantines, or triggers mitigation.
```

**Interpretation:** Swarm Commander (#1) owns routing, dispatch, and command-lane selection. Risk Triage (#3) owns numeric risk telemetry only. No agent may hold both authorities in one envelope. Downstream consumers (operator review, PM Voice relay, explanation agents such as #52, verification lane) may **read** scores; they must not treat #3 output as authorization to act.

---

## Agent Design Contract block

| Field | Value |
|---|---|
| Agent name | Risk Triage Agent (`RiskTriageAgent` — proposed build name TBD at separate Build Authorization) |
| Swarm inventory ID | #3 — Risk Triage |
| Canonical layer | 1 — Command (telemetry scorer slot; **not** routing commander) |
| Canonical team / case type | Cross-cutting command telemetry; consumes detector evidence bundles |
| Authority level | **AUTH-4 — Telemetry Scorer** (see narrowed declaration below) |
| Stage posture | VISION Stage A — structured score telemetry only; no tenant action |
| Evidence Stage (current) | **Not promoted** — draft/review only |
| Role | Accept validated, provenance-tagged detector evidence; compute declared rubric-axis numeric values and aggregate risk telemetry; emit strict allowlist score envelope |
| Boundary | Score-in-evidence-out. Structured numerics + reason codes + provenance only. No routing, no mitigation, no narrative artifacts |
| Explicit non-authorities | See AUTH-4 and prohibited outbound fields below |
| Inputs | `message_id`, `tenant_id`, validated `detector_outputs[]`, scoring policy version reference |
| Outputs | Strict allowlist score telemetry envelope (Section 6) |
| Evidence emitted | Score record with full provenance chain to detector inputs + policy version |

---

## AUTH-4 — Telemetry Scorer (narrowed)

**AUTH-4 grants only:**

- Compute structured score telemetry from validated detector evidence.
- Emit numeric rubric-axis values, aggregate risk telemetry, scoring reason codes, policy version, and source provenance / evidence references per declared scoring policy.

**AUTH-4 explicitly does not grant:**

| Forbidden authority | Rule |
|---|---|
| Routing authority | No target agent, lane, queue, or dispatch hint in input handling or output |
| Mitigation authority | No block, quarantine, contain, alert, or trigger-mitigation semantics |
| Tenant policy mutation | No change to tenant rules, thresholds exposed as tenant config, or policy store writes |
| Lifecycle promotion | No scoreboard/registry promotion, demotion, or Evidence Stage writes |
| Scoreboard authority | No updates to `Blue_Team_Swarm_70_Agent_Scoreboard.md` or inventory lifecycle state |
| Operator-delegated approval authority | No approval, authorization, or "operator may proceed" language in output |

**Relation to #1:** #1 holds routing/dispatch authority. #3 must never substitute for #1. If both appear in a pipeline, #1 consumes #3 telemetry; #3 never consumes #1 routing decisions as binding input.

---

## §0 Purpose

Risk Triage (#3) is the command-layer **telemetry scorer**: it turns validated detector evidence into numeric risk telemetry under a declared, versioned scoring policy. It does **not** decide what happens next, does **not** route work, and does **not** produce client-facing explanations or recommended actions.

This draft exists to unblock contract review and Estimator visibility without Build Authorization, §11 signature, or `SIGNED_UNBUILT` promotion.

---

## §1 Scope

### In scope

- Contract-review definition of #3 role, boundary, AUTH-4, inbound validation, outbound allowlist, and score provenance.
- Alignment note with #105 governance posture (compatibility only).
- Explicit rejection of plain-English / narrative artifact generation by #3.
- Explicit treatment of `detector_outputs` as untrusted structured input until validated.

### Out of scope

- Build Authorization, implementation, default-on activation, or production dispatch.
- §11 signature or `SIGNED_UNBUILT` scoreboard reconcile.
- Retrofit authorization for `email_risk_scoring_agent.py` (legacy surface emits `recommended_action` — **out of contract** until separate governed retrofit).
- Swarm Commander (#1) contract (sibling draft pending).
- Client-facing copy, verification instructions, or buyer claims.
- Live learning, self-adjusting thresholds, or hidden weight mutation.

---

## §2 Locked design decisions (draft — unsigned)

| # | Decision | Locked value (pending operator review) |
|---|---|---|
| D1 | Spine split | #1 routes never scores; #3 scores never routes or mitigates |
| D2 | AUTH-4 scope | Telemetry scorer only; table in AUTH-4 section is exhaustive for this draft |
| D3 | Detector trust | Inbound `detector_outputs` are untrusted until provenance + schema validation pass |
| D4 | Outbound shape | Strict allowlist only; any command-like field is a contract violation |
| D5 | Aggregate score semantics | `aggregate_risk_score` is telemetry for downstream review, not decision authority |
| D6 | Score provenance | Every output score traceable to detector inputs + declared policy version; no hidden weights |
| D7 | Explanation surface | Plain-English narrative belongs to downstream explanation consumer (#52-style), not #3 |
| D8 | #105 coupling | Compatibility alignment only; no dependency on unsigned #105 authority |
| D9 | Lifecycle | Draft/review storage only until separate operator §11 + Build Authorization path |

---

## §3 Inputs — untrusted `detector_outputs`

### Required envelope fields (inbound)

| Field | Requirement |
|---|---|
| `message_id` | Correlation id; opaque to routing decisions inside #3 |
| `tenant_id` | Tenant scope for telemetry tagging only; **no** tenant policy mutation |
| `detector_outputs` | Array of structured detector evidence records |
| `scoring_policy_version` | Declared policy id + version string #3 must echo on output |

### `detector_outputs` validation rules

Each detector record is **untrusted structured input** until validated:

1. **Source provenance required:** `detector_id`, `detector_contract_version` (or equivalent signed spec reference), `evidence_ref`, and `emitted_at` (or record id) must be present. Records missing provenance are dropped and logged as `INPUT_PROVENANCE_MISSING` (telemetry reason code — not a routing signal).

2. **Schema validation required:** Payload must match the allowlisted detector evidence schema for that `detector_id`. Unknown fields are stripped or cause record rejection per build-time parser rules. **No pass-through of undeclared keys.**

3. **No routing keys from detectors:** Inbound payloads must not contain, and #3 must not act on: `target_agent`, `route_to`, `lane`, `next_action`, `escalate_to`, `mitigation`, `quarantine`, `block`, `alert`, `dispatch`, `recommended_action`, `NEXT_DECIDED`, or semantically equivalent hints even if nested. If present, the record is rejected as `INPUT_ROUTING_KEY_FORBIDDEN` — #3 does not sanitize-and-forward routing hints.

4. **Score-only consumption:** #3 may read detector factual claims and detector-local numeric hints **only** as evidence inputs to declared scoring axes. It may not treat detector-supplied routing, escalation, or mitigation hints as instructions.

---

## §4 Scoring behavior

### Permitted computation

- Rubric-axis numeric values (e.g., vendor fraud axis, wire anomaly axis — exact axis set fixed at Build Authorization from signed rubric/policy annex).
- `aggregate_risk_score` — **telemetry aggregate** computed by declared formula in `scoring_policy_version`; informs downstream human or governed review surfaces only.
- Scoring reason codes — machine-readable enums tied to evidence refs (not prose).
- Policy version echo and evidence reference list.

### Prohibited computation / artifacts

- Client-facing explanations, advice, recommendations, judgments, or verification instructions.
- Plain-English risk rubric artifacts or narrative "because" paragraphs.
- `recommended_action`, approval language, or action bands that imply authorization.
- Any field that could be read as "do X next" without a separate routing agent (#1) and operator/human gate.

### `aggregate_risk_score` — telemetry, not authority

The aggregate score:

- **May** inform downstream review, ranking, or explanation inputs.
- **Must not** by itself decide, authorize, or trigger a tenant action.
- **Must not** auto-escalate, auto-block, or auto-notify.
- Carries no implicit threshold authority unless a **separate signed downstream spec** and operator process say so — that authority does not live in #3.

---

## §5 Score provenance (mandatory)

Every emitted score must satisfy:

| Rule | Requirement |
|---|---|
| Traceability | Each numeric output maps to: (a) one or more accepted `detector_outputs` evidence refs, and (b) `scoring_policy_version` |
| Declared weights | All axis weights and aggregation formula live in the signed policy annex for that version — **no hidden weights** in runtime |
| Stable thresholds | Band boundaries are policy-version constants — **no self-adjusting thresholds** inside #3 |
| No live learning | **No live learning loop** that mutates scoring policy from production traffic |
| No silent optimization | **No probabilistic optimization** that changes effective policy without Matt-signed policy update and version bump |
| Audit replay | Given the same validated inputs + policy version, output numerics must be reproducible (deterministic scorer path) or record explicit non-determinism source in provenance (e.g., external model id) — never silent drift |

---

## §6 Outbound schema — strict allowlist

### Allowed fields

| Field | Type / notes |
|---|---|
| `message_id` | string |
| `tenant_id` | string |
| `aggregate_risk_score` | number — telemetry only (Section 4) |
| `axis_scores` | object of numeric rubric-axis values only |
| `scoring_reason_codes` | array of machine enums |
| `scoring_policy_version` | string — must match declared inbound policy version used |
| `source_provenance` | array of `{ detector_id, detector_contract_version, evidence_ref }` |
| `score_record_id` | uuid — optional correlation |
| `emitted_at` | timestamp — optional |

### Prohibited fields (non-exhaustive — any command-like field forbidden)

- `target_agent`, `target_agents`, `route_to`, `routing_lane`, `lane`
- `next_action`, `next_actions`, `dispatch`, `handoff_to`
- `contain`, `block`, `quarantine`, `isolate`, `alert`, `notify`
- `recommended_action`, `recommendation`, `approval`, `authorized`, `NEXT_DECIDED`
- `verification_instructions`, `client_message`, `plain_english_summary`, `narrative`, `advice`
- `tenant_policy_patch`, `threshold_override`, `promotion`, `demotion`
- Any field name or value reasonably read as a command, authorization, or routing instruction

**Violation posture:** Build-time validators and authority probes must treat prohibited fields as `AUTHORITY_INVARIANT_BREACH` if emitted by the governed #3 wrapper.

---

## §7 Relationship to sibling agents

| Agent | Relationship |
|---|---|
| #1 Swarm Commander | Upstream router; never scores. Consumes #3 telemetry optionally; #3 never routes. |
| Detectors (#10, #21, …) | Upstream evidence producers; untrusted until Section 3 validation. |
| #52 Plain-English Explanation | Downstream consumer; owns narrative artifacts #3 must not emit. |
| #105 Governance Invariants | Compatibility alignment only; not a dependency for this draft. |
| Legacy `email_risk_scoring_agent.py` | Pre-contract scorer; emits `recommended_action` — **non-compliant** with this contract until governed retrofit authorized separately. |

---

## §8 Failure modes

| Failure mode | Detection | Response (scorer-local only) |
|---|---|---|
| Routing key in detector input | Inbound validator | Reject record; reason code `INPUT_ROUTING_KEY_FORBIDDEN`; no partial route |
| Missing provenance | Inbound validator | Drop record; reason code `INPUT_PROVENANCE_MISSING` |
| Schema drift | Inbound validator | Reject record; reason code `INPUT_SCHEMA_INVALID` |
| Prohibited outbound field | Outbound validator / authority probe | Fail closed; do not emit envelope |
| Hidden weight / undeclared axis | Policy audit / replay test | Block promotion until policy annex updated |
| Plain-English leakage | Outbound schema scan | Treat as contract violation |
| #1 boundary bleed | Authority probe | `AUTHORITY_INVARIANT_BREACH` — scorer attempted routing semantics |

---

## §9 Build path (not authorized)

**Proposed future path (frozen for review only):**

`3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/command/risk_triage_agent.py`

No file creation, registry entry, or scoreboard `SIGNED_UNBUILT` reconcile is authorized by this draft.

---

## §10 Open questions (draft)

1. Exact rubric axis set and aggregation formula annex — which signed rubric spec is canonical for email command telemetry at Build Authorization?
2. Governed retrofit vs replacement for `email_risk_scoring_agent.py` — separate operator decision.
3. Whether `axis_scores` uses fixed key names from Client-Facing 5-Axis rubric or internal axis ids only at telemetry layer.
4. Maximum `detector_outputs` array size and rejection policy when all records invalid (empty score vs error envelope).
5. Companion #1 Swarm Commander contract draft ordering — parallel review vs sequential gate.

---

## §11 Sign-off — SIGNED 2026-06-21

Signed by Matt Nichol on 2026-06-21 after pre-build gate clean 0/0 (`audit_outputs/mmi_03_contract_gate_20260622T015428Z.md`; MMI-DEC-097). Locks D1–D9, AUTH-4, inbound/outbound schema, and score provenance rules. Authorizes contract text only. Does **not** authorize build, `SIGNED_UNBUILT`, scoreboard reconcile, or AUTH-5.

### Sign-off line

> matt Nichol June 21st 2026

Per Authorship Rule: operator-authored signature, placed verbatim.

---

**End of contract. §11 in force as of 2026-06-21 (MMI-DEC-098).**
