# Swarm Commander Routing-Policy Annex — Contract Review Draft

**Draft ID:** `MMI_01_SWARM_COMMANDER_ROUTING_POLICY_ANNEX_REVIEW_DRAFT`

**Status:** DRAFT UNSIGNED — contract review storage only. Pre-build gate clean **0 blocking / 0 warnings** at `audit_outputs/routing_policy_annex_pre_build_gate_20260624T015713Z.md` (Gemini `gemini-2.5-pro`; packet SHA256 `474d2756fea42431ead9a9d957284c81ae21469a5a89512c84eb2533fc5ecac2`; MMI-DEC-120). Prior run **0 blocking / 1 warning** at `audit_outputs/routing_policy_annex_pre_build_gate_20260624T015436Z.md` (MMI-DEC-119; spine-boundary repair applied). **Optional Matt §11** when ready; no runtime wiring without separate Build Authorization.

**Parent contract:** `docs/mmi/contracts/001_swarm_commander_contract.md` (§11 SIGNED MMI-DEC-102; `SwarmCommanderAgent` GATED MMI-DEC-112)

**Resolves:** Parent contract §10 open question 1 — when may #1 read #3 telemetry vs contribution facts only?

**Candidate:** #1 — Swarm Commander (routing-policy consumption only)

**Owner:** Matt Nichol

**Track:** Command spine wiring annex (Layer 1 — RC-AUTH adjunct; **not** scorer authority)

**Lane:** Contract Review Draft (frozen design storage; not Build Authorization)

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** **BLOCKED** until separate operator §11 signature **and** Build Authorization to wire `SwarmCommanderAgent.run_case(risk_triage_telemetry=...)`. Stage 1 wrapper currently rejects routing-by-score keys and **does not** apply score-derived disposition hints (MMI-DEC-111).

**Source-of-truth links:**
- `docs/mmi/contracts/001_swarm_commander_contract.md` (RC-AUTH parent; DER allowlist; disposition precedence `mmi_sc_v1`)
- `docs/mmi/contracts/003_risk_triage_contract.md` (#3 RiskScoreTelemetry allowlist; AUTH-4; GATED MMI-DEC-116)
- `docs/mmi/contracts/002_mission_context_contract.md` (#2 classification envelope; MC-AUTH; GATED MMI-DEC-109 — manifest binding deferred to future annex revision)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/command/swarm_commander_agent.py` (v1 read-only ingest + reject routing keys)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/command/risk_triage_agent.py` (`RiskScoreTelemetry` shape; `SCORING_POLICY_VERSION=mmi_rt_v1`)
- `AGENTS.md` (authority / gate discipline)

**#105 Governance Invariants (compatibility only):** This annex preserves human-in-the-loop posture. Score telemetry may **inform** conservative disposition hints only; it must not authorize autonomous tenant action or bypass operator gates.

---

## Spine boundary (parent invariant — verbatim)

Parent `001_swarm_commander_contract.md` core invariant block — **unchanged**:

```text
#1 routes; it never scores.
#3 scores; it never routes, dispatches, recommends, alerts, blocks, quarantines, or triggers mitigation.
```

**Interpretation (parent):** Swarm Commander (#1) owns routing, dispatch, registry-validated invocation order, conservative disposition assembly, and human-review path selection. Risk Triage (#3) owns numeric risk telemetry only. No agent may hold both authorities in one envelope. #1 may **read** #3 telemetry as optional evidence input to this **separate signed routing-policy annex**; #1 must **never** compute rubric-axis values, `aggregate_risk_score`, or scoring reason codes.

### Command spine context (#2 sibling note — not parent invariant text)

Mission Context (#2) is a **sibling** GATED wrapper (`002_mission_context_contract.md`; MMI-DEC-109). For orientation only:

```text
#2 classifies; it never routes, dispatches, scores, mitigates, or assembles disposition.
```

This annex does **not** modify the parent #1/#3 invariant block and does **not** bind `#2` classification to agent manifests in v1 (see §5).

**Annex scope:** Defines **read-only consumption rules** for optional `#3 RiskScoreTelemetry` by `#1 Swarm Commander` when assembling disposition. This annex does **not** grant #1 scoring authority, registry mutation, or autonomous routing.

---

## §0 Purpose

Command spine wrappers #1–#3 are GATED at Stage 1 (MMI-DEC-112/109/116). The parent Commander contract permits optional read-only `#3` telemetry but forbids score-only auto-routing until a **separate signed routing-policy annex** exists (parent §3 rule 5, §4, §5, §10 Q1).

This draft annex locks:

1. Which `#3` fields `#1` may read.
2. How those fields may **conservatively influence** disposition assembly **without** bypassing contribution-first precedence.
3. Forbidden routing-by-score patterns (explicit deny list aligned with runtime probes).

It does **not** authorize production dispatch, default registry wiring, GOVERNED_AGENT promotion, or AUTH-5.

---

## §1 Scope

### In scope

- Read-only `#3 RiskScoreTelemetry` field allowlist for `#1` consumption.
- Versioned routing-policy id `mmi_rp_v1` disposition-hint rules (conservative only).
- Explicit prohibition of agent-list mutation, registry bypass, and human-review suppression from score alone.
- Alignment with `RiskScoreTelemetry` emitted under `scoring_policy_version=mmi_rt_v1`.
- Authority probe expectations for governed `#1` wrapper when annex is wired.

### Out of scope

- §11 signature, pre-build gate record, or Build Authorization for runtime wiring.
- `#2 MissionContext` classification → `agents[]` manifest binding (reserved §10 Q2 — future annex revision or sibling annex).
- `#3` scoring policy changes (governed by `003_risk_triage_contract.md` and `mmi_rt_v1`).
- Client-facing copy, mitigation commands, tenant notifications.
- MMI dispatcher / PM Voice authority.
- Blackboard persistence of DER or score records.

---

## §2 Locked design decisions (draft — unsigned)

| # | Decision | Locked value (pending operator review) |
|---|---|---|
| R1 | Parent dependency | Annex inactive until §11 signed; parent RC-AUTH remains authoritative |
| R2 | Read-only ingest | `#1` may read allowlisted `#3` fields; must not copy scorer fields into DER |
| R3 | No score-only routing | `aggregate_risk_score` alone must never select agents, skip registry guards, or suppress human review |
| R4 | Contribution-first | Disposition precedence in parent §5 runs first; hints may only **raise** caution, never lower it |
| R5 | Policy version echo | `#1` must record `routing_policy_version=mmi_rp_v1` in route audit metadata when hints applied (implementation detail at Build Authorization — not DER field) |
| R6 | Scoring policy coupling | Accept `#3` telemetry only when `scoring_policy_version=mmi_rt_v1` matches declared scorer output |
| R7 | Refusal handling | If `#3` telemetry missing, malformed, or policy mismatch → hints skipped; case proceeds on contributions only |
| R8 | Stage A only | No autonomous action path enabled by this annex |

---

## §3 Permitted `#3` telemetry consumption (read-only)

### Inbound envelope

`SwarmCommanderAgent.run_case(..., risk_triage_telemetry=...)` accepts a mapping shaped like `#3` `RiskScoreTelemetry` (see `risk_triage_agent.py`).

### Allowlisted fields `#1` may read

| Field | Use permitted |
|---|---|
| `message_id` | Correlation only; must match `MissionContext` case identity when both present |
| `tenant_id` | Correlation only |
| `aggregate_risk_score` | Disposition hint input only (§4); **not** routing |
| `axis_scores` | Disposition hint input only (§4); numeric values only |
| `scoring_reason_codes` | Audit metadata for hint application; **not** routing instructions |
| `scoring_policy_version` | Must equal `mmi_rt_v1` or hints are skipped |
| `source_provenance` | Audit metadata only |
| `score_record_id` | Audit metadata only |
| `emitted_at` | Audit metadata only |

### Fields `#1` must ignore for routing purposes

All allowlisted fields are **telemetry for disposition hints only**. None may select Pass-1 / Pass-2 agent lists, reorder caller-declared `agents[]`, or bypass `validate_agent_dispatch`.

### Inbound validation (fail closed on forbidden keys)

Reject case before dispatch if `risk_triage_telemetry` contains any key in the **forbidden routing-by-score set** (aligned with `swarm_commander_agent._ROUTING_BY_SCORE_KEYS` plus parent §3):

- `auto_select_agents`, `auto_route`, `route_by_score`, `skip_human_review`, `select_agents`, `dispatch_hint`, `target_agent`
- Any `#3`-forbidden command field from `003_risk_triage_contract.md` §6 prohibited list if erroneously present on the telemetry blob

Validation failure → `GovernanceError`; no partial hint application.

---

## §4 Disposition hint rules (`routing_policy_version=mmi_rp_v1`)

Hints apply **after** Pass-1 / Pass-2 dispatch completes and **after** base disposition is computed per parent §5 (`mmi_sc_v1` precedence). Hints may **only escalate** human-review posture; they must **never** reduce caution below the base disposition.

### Base disposition source (unchanged)

Parent §5 precedence on contributions + challenge_pass remains the sole base disposition computer. This annex does **not** replace or short-circuit that precedence.

### Hint table (conservative escalation only)

| Condition (all must hold) | Hint effect |
|---|---|
| Base disposition ∈ `{clear, suspicious}` **and** `aggregate_risk_score >= 85` | Elevate final disposition to `hold` |
| Base disposition ∈ `{clear, suspicious, hold}` **and** `aggregate_risk_score >= 95` | Elevate final disposition to `human_required` |
| Any base disposition **and** any single `axis_scores` value `>= 90` | Elevate final disposition by one caution step: `clear→suspicious`, `suspicious→hold`, `hold→human_required`; `human_required` unchanged |
| `scoring_policy_version != mmi_rt_v1` | Skip all hints |
| Telemetry absent or empty | Skip all hints |

**Caution step ceiling:** Final disposition after hints must not exceed `human_required`. Hints must not produce `escalate` unless a separate signed escalation spec authorizes that vocabulary in production (parent §10 Q3).

### Explicit prohibitions

| Forbidden pattern | Rule |
|---|---|
| Score-only agent selection | No mapping from score → `agents[]` or `challenge_agents[]` |
| Score-only registry bypass | Hints must not skip `validate_agent_dispatch` or metadata match |
| Score-only human suppression | High scores must not downgrade `human_required` or clear human review |
| DER scorer leakage | Hints must not add `aggregate_risk_score`, `axis_scores`, or `scoring_reason_codes` to DER |
| Mitigation semantics | No block / quarantine / alert / notify derived from score in `#1` |

---

## §5 Relationship to `#2` Mission Context

`002_mission_context_contract.md` states classification → agent manifest binding requires a **separate signed routing-policy annex**. **This draft (v1) does not bind `#2` outputs to agent lists.** Classification may be consumed by the operator or a future `mmi_rp_v2` revision. `#1` continues to accept caller-declared `agents[]` only.

---

## §6 Runtime wiring expectations (post-Build Authorization)

When Matt authorizes wiring (separate from this §11 review):

1. `SwarmCommanderAgent.run_case` applies §3 validation then §4 hints after legacy `_determine_disposition`.
2. Authority probes (`assert_der_rc_auth_compliant`) remain unchanged — DER must stay scorer-free.
3. Route audit metadata (logs/tests only at Build Authorization) records `{routing_policy_version, hints_applied, base_disposition, final_disposition}`.
4. Default registry / production dispatch remain blocked until separate authorization.

**Not authorized by this draft:** changing `DISPOSITION_POLICY_VERSION` from `mmi_sc_v1` without signed amendment.

---

## §7 Failure modes

| Failure mode | Detection | Response |
|---|---|---|
| Routing key on telemetry | `_reject_routing_by_score` / probe | `GovernanceError`; fail closed |
| Scorer fields on DER | `assert_der_rc_auth_compliant` | `AUTHORITY_INVARIANT_BREACH` |
| Hint lowers caution | Policy audit test | Contract violation; block promotion |
| Policy version mismatch | `scoring_policy_version != mmi_rt_v1` | Skip hints; base disposition only |
| Score-only agent pick | Static scan / probe | `AUTHORITY_INVARIANT_BREACH` |

---

## §8 Build path — NOT AUTHORIZED

This draft placement resolves PMV chain fork (MMI-DEC-116/117). **No runtime wiring** until:

1. Grok pre-build gate clean 0/0 on this annex draft.
2. Matt §11 signature on this annex.
3. Separate Matt Build Authorization to implement §6 in `swarm_commander_agent.py` (+ focused tests).

Parent `#1` wrapper remains GATED without annex wiring. **Not GOVERNED_AGENT**; not default registry.

---

## §9 Open questions (draft)

1. Should axis-specific hint thresholds mirror Client-Facing 5-Axis rubric band names in audit metadata?
2. Whether `#2` manifest binding belongs in `mmi_rp_v2` or a sibling `#2` routing annex.
3. Whether hint application requires explicit operator feature flag per tenant at Stage A.
4. Replay fixture pack for hint boundary tests (85/95 thresholds, axis 90 escalation chain).

---

## §10 Sign-off — UNSIGNED

Matt §11 signature required after pre-build gate review. Signature authorizes **annex text only** — not Build Authorization, not GOVERNED_AGENT, not production dispatch, not AUTH-5.

### Sign-off line

> _(pending Matt Nichol §11 signature)_

---

**End of routing-policy annex draft. Inactive until §11 signed.**
