# Phase 1 Infrastructure — Agent Design Contract
## Swarm Foundation Layer: Evidence Ledger, Role Separation, Token Tracking

**Document type:** Agent Design Contract
**Status:** §11 SIGNED — Matt Nichol June 9th 2026. Build authorization granted per §11 scope.
**Date drafted:** June 9, 2026
**Drafted by:** Claude (advisory lane) — design/governance lane per AGENTS.md §2.1
**Authority:** Matt Nichol — sole signing authority
**Repo path:** `4. Product_Roadmap/Phase1_Infrastructure_Agent_Design_Contract.md`

---

## §0 — Purpose

This contract governs the four foundational infrastructure components required before any new swarm agent can be built. It formalises existing surfaces, extends existing patterns, and introduces one genuinely new component. It does not authorize any new detection, verification, or autonomy capability.

Everything in this contract is a prerequisite. Nothing above Phase 1 in the Swarm Build Map (`4. Product_Roadmap/Swarm_Build_Map_Master.md`) is buildable until this contract is signed and Phase 1 clears `complete_gate.py` at 0/0.

---

## §1 — Scope

### In scope
1. **Canonical Evidence Ledger** — formalising `core/blackboard/` as the single append-only evidence store all agents write to
2. **Role Separation Controller** — formalising builder-auditor separation as a named, enforced infrastructure component extending the pattern already established in #46 Evidence Package
3. **Token Usage Tracker** — net-new component tracking per-tenant, per-agent, per-model token consumption
4. **Layer Model Reconciliation Table** — explicit mapping of the new product architecture concept (Layer 0-6) to the signed 6-layer Design Tree

### Explicitly out of scope
- Any detection agent (Layer 0 knowledge agents, Layer 1 detection agents)
- ReconciliationAgent — requires its own separate contract
- The Lung / elastic scaling — extends Tiered Detection Intensity spec; requires its own separate contract
- Collective Immune System — DEPTH GATE is CLOSED; not buildable until gate opens
- Mutation Engine extension — `core/mutation/engine.py` exists sandbox-only; extension requires its own separate contract
- Any Stage B autonomy capability — STAGE_B GATE is CLOSED
- Any change to `core/evidence_package/` path or its governed surfaces
- Any change to any §11-signed spec

---

## §2 — Locked Design Decisions

| # | Decision | Locked value |
|---|---|---|
| P1-D1 | Canonical evidence ledger path | `core/blackboard/` — this is the SharedEvidenceLedger. No parallel namespace (e.g. `core/evidence_ledger/`, `core/shared_state/`) may be created for this surface. |
| P1-D2 | Ledger write contract | Every agent contribution is append-only. No agent may modify or delete a prior entry. The ledger is a fact accumulator, not a mutable state store. |
| P1-D3 | Ledger read access | All agents may read the full ledger for their tenant. No agent may read another tenant's ledger entries. Tenant isolation is enforced at the ledger level, not assumed. |
| P1-D4 | Builder-auditor separation | The agent that assembles an evidence package cannot audit it. This constraint is structural — enforced at the credential/role level, not by convention. RoleSeparationController enforces this at runtime. |
| P1-D5 | Token tracker scope | TokenUsageTracker records: tenant_id, agent_id, model_id, token_count, timestamp, action_type. Read-only reporting surface only. No agent may read another tenant's token data. |
| P1-D6 | Token tracker authority | TokenUsageTracker is a ledger, not a decision surface. It informs the Playhouse cost attribution dashboard. It does not gate, block, or modify any agent's operation. |
| P1-D7 | Layer model mapping | The new product concept Layer 0-6 maps to the signed 6-layer Design Tree per §4 of this contract. The Design Tree is the governance authority. The product concept is a communication layer only. |
| P1-D8 | No new detection surface | Phase 1 infrastructure components observe and record. They do not detect, score, flag, or produce AgentContributions of their own. |
| P1-D9 | Linux-primary path | All new files land at `/home/socialarchitect/northstar/` in the Linux working copy. No Windows paths. Per CURRENT_STATE_MAP development surface doctrine. |

---

## §3 — Component Definitions

### Component 1 — Canonical Evidence Ledger
**Existing surface:** `core/blackboard/` (#49 Audit Trail, `DETECTOR_FUNCTION`)
**Action:** Formalise — add governing contract metadata, define write schema, enforce tenant isolation, document append-only invariant

**Write schema (per entry):**
```
agent_id:        str   — canonical agent name from scoreboard
tenant_id:       str   — MSP tenant identifier
email_id:        str   — unique email case identifier
evidence_type:   str   — closed enum (see below)
details:         dict  — agent-specific facts, closed vocabulary per agent contract
confidence:      float — 0.0 to 1.0
timestamp:       str   — ISO 8601
stage:           str   — Evidence Stage (ES1 / ES2 / ES3)
```

**Evidence type closed enum (initial):**
`header_signal | authentication_signal | thread_signal | geo_signal | content_signal | url_signal | attachment_signal | image_signal | sender_signal | knowledge_signal`

New evidence types require a signed amendment to this contract before use.

**Invariants:**
- Entries are immutable after write
- No delete operation exists
- Tenant isolation: `tenant_id` is mandatory on every write; reads are filtered by tenant_id at query time
- Schema validation fires before every write; malformed entries are rejected and logged to the governance audit trail

---

### Component 2 — Role Separation Controller
**Existing pattern:** Builder-auditor separation in #46 Evidence Package (`GOVERNED_AGENT`), `core/operator_state/` kill-switch (#4)
**Action:** Formalise as a named infrastructure component — extend existing structural pattern to cover all future agents

**Roles (closed enum):**
- `BUILDER` — may write agent code, write to blackboard, run detectors
- `AUDITOR` — may read blackboard, run `complete_gate.py`, approve evidence packages, approve mutations
- `OPERATOR` — Matt Nichol only. May sign §11, commit, push, open/close gates, approve mutations

**Separation rules:**
- A `BUILDER` credential cannot hold `AUDITOR` on the same surface it built
- `complete_gate.py` runs under `AUDITOR` credentials only
- Evidence package assembly is `BUILDER`; evidence package audit is `AUDITOR`; these cannot be the same process in the same run
- Mutation validation is `AUDITOR`; mutation deployment requires `OPERATOR` sign-off

**This component does not introduce new authentication infrastructure.** It formalises the separation discipline already encoded in `AGENTS.md` §2 and the #46 contract into a named, documented, testable constraint.

---

### Component 3 — Token Usage Tracker
**Existing surface:** None. Genuinely net-new. Requires new scoreboard row.
**Proposed scoreboard placement:** Team 7 Evidence/Audit — row #71 (or next available)
**Action:** Build new — lightweight append-only usage ledger

**Record schema:**
```
tenant_id:    str   — MSP tenant identifier
agent_id:     str   — canonical agent name
model_id:     str   — model identifier (e.g. claude-sonnet-4, gpt-4o)
token_count:  int   — tokens consumed in this operation
action_type:  str   — closed enum: detection | verification | reconciliation | mutation | audit
timestamp:    str   — ISO 8601
session_id:   str   — links related operations in one case
```

**Invariants:**
- Append-only. No modification after write.
- Tenant isolation identical to Evidence Ledger.
- No agent gates or blocks on token count — reporting only.
- Aggregate queries available to Playhouse CostAttributionDashboard per tenant.

**Scoreboard row to be added:**
`#71 | Token Usage Tracker | GOVERNANCE_DOC_ONLY (pre-build) | none | 6 Learning/Governance | A | NEEDS_SIGNED_CONTRACT | BREADTH`

---

### Component 4 — Layer Model Reconciliation Table
**Purpose:** Prevent future sessions from treating the product concept architecture (Layer 0-6) as a replacement for the signed 6-layer Design Tree. This table is the permanent mapping. The Design Tree governs. The product concept communicates.

| Product concept layer | Description | Maps to Design Tree layer | Notes |
|---|---|---|---|
| Layer 0 — Threat Intelligence Foundation | Knowledge agents — brief, don't detect | 6 Learning/Governance | Knowledge agents are Learning/Governance — they inform, they don't detect or act |
| Layer 1 — Detection Swarm | Active detection, evidence contributions | 2 Detection | Direct map — all existing governed agents are here |
| Layer 2 — Reconciliation | Evidence chain synthesis, verdict | 4 Evidence + 1 Command | ReconciliationAgent spans Evidence assembly (#46 pattern) and Command routing (#1 pattern). Needs its own contract to resolve the split. |
| Layer 3 — The Lung | Elastic scaling, protection depth dial | 1 Command + 6 Governance | Scaling is Command orchestration. Depth dial extends Tiered Detection Intensity (signed). Requires its own contract. |
| Layer 4 — Collective Immune System | Cross-tenant pattern sharing | 6 Learning/Governance | DEPTH GATE CLOSED. Not buildable until gate opens. |
| Layer 5 — Mutation and Evolution | Swarm learning, 3-shot confirmation | 6 Learning/Governance | `core/mutation/engine.py` exists sandbox-only (#67). Extension requires its own contract. |
| Layer 6 — Governance and Audit | Logging, override, drift detection | 6 Learning/Governance | Maps to existing governance spine: `core/blackboard/`, `complete_gate.py`, `core/operator_state/` |
| The Playhouse | Operator control surface | 1 Command (operator interface) | Extends existing operator surface. Requires its own contract. |

---

## §4 — What This Contract Does NOT Authorize

Explicitly stating what cannot be inferred as authorized from this contract:

- No new detection agent may be built citing this contract as authorization
- No change to `core/evidence_package/` path or any surface governed by the Evidence Package spec
- No extension to `core/mutation/engine.py` beyond its current sandbox boundary
- No Collective Immune System component — DEPTH GATE is CLOSED
- No Stage B autonomy capability — STAGE_B GATE is CLOSED
- No production dispatch of any agent — all Phase 1 components are infrastructure only, not in `build_default_registry`
- No push to remote without Matt's explicit go-ahead

---

## §5 — Test Requirements

Three test classes required for every Phase 1 component per AGENTS.md §5:

**Class 1 — Expected pass**
- Ledger: valid entry writes successfully, tenant isolation confirmed, schema validation passes
- Role Separation: BUILDER cannot invoke AUDITOR function, AUDITOR cannot write to blackboard
- Token Tracker: record writes, tenant query returns only own tenant's data

**Class 2 — Adversarial / break-it**
- Ledger: attempt to modify existing entry — must fail and log
- Ledger: attempt to write entry without tenant_id — must reject
- Ledger: attempt to read another tenant's entries — must return empty, not error
- Role Separation: attempt to run `complete_gate.py` under BUILDER credentials — must fail
- Token Tracker: attempt cross-tenant query — must return empty, not error

**Class 3 — Known-gap xfail**
- Ledger: distributed consistency under concurrent writes — ES1 synthetic only, not tested until real-data gate opens. Reason: requires production infrastructure. Completion path: Stage 2 infrastructure contract.
- Token Tracker: real-time streaming aggregation — deferred. Reason: batch reporting sufficient for Phase 1. Completion path: Playhouse dashboard contract.

---

## §6 — Failure Modes

| Failure mode | Detection | Response |
|---|---|---|
| Namespace drift | New `core/` directory created without this contract's authorization | Gate rejects; execution lane halts |
| Tenant isolation breach | Cross-tenant read returns data | Test Class 2 catches at build time |
| Builder-auditor collapse | Same process assembles and audits evidence | Role Separation Controller rejects |
| Token tracker used as gate | Any agent branches on token count | Code review + gate catches |
| Layer model confusion | Product concept layer used to authorize a build | This contract is the mapping authority — refer to §4 |

---

## §7 — Relationship To Existing Signed Specs

| Existing signed spec | Relationship |
|---|---|
| Header Analysis Agent Design Contract | Writes to `core/blackboard/` — this contract governs that write surface |
| Email Authentication Agent Design Contract | Same |
| Ghost Thread Agent Design Contract | Same |
| All 13 currently governed agents | Same — all write to `core/blackboard/` |
| Evidence Package Agent Design Contract (#46) | Builder-auditor separation pattern extended by RoleSeparationController |
| Tiered Detection Intensity Deep Dive | Lung/depth dial concept extends this spec — not replaced by this contract |
| Financial State Ledger Delta Tripwire | Not touched by this contract |
| Cyber Insurance Evidence Package | Not touched by this contract |

---

## §8 — Scoreboard Updates Required On Signing

1. Row #49 Audit Trail — update status from `DETECTOR_FUNCTION` to `GOVERNED_AGENT` once contract signed and gate clears
2. Add row #71 Token Usage Tracker — `GOVERNANCE_DOC_ONLY` until built
3. Update `CURRENT_STATE_MAP.md` — add Phase 1 infrastructure as a settled doctrine entry
4. Log to `decision_cycles_log.md` — type: `INFRASTRUCTURE_CONTRACT`

---

## §9 — Open Questions (pre-signature)

1. Does #49 Audit Trail promote to `GOVERNED_AGENT` in this contract or does it need a separate per-agent contract per the promotion bar in Q4 of the scoreboard reconciliation?
2. Token Usage Tracker — row #71 or does Matt want a different numbering approach for infrastructure components vs detection agents?
3. The ReconciliationAgent spans Layer 4 Evidence and Layer 1 Command per the reconciliation table. Does Matt want to resolve this split in a separate contract before Phase 1 is closed, or after?

---

## §10 — Open Questions For Next Session

- Phase 2 contract (Layer 0 knowledge agents) — can all six be specced in one contract or does each need its own?
- ReconciliationAgent contract — is this Phase 2 or Phase 3?
- Lung contract — does this extend the signed Tiered Detection Intensity spec via amendment, or as a new companion spec?

---

## §11 — Operator Sign-Off

This contract is DRAFT. No build authorization is granted until signed.

By signing below, Matt Nichol authorizes:
- Formalisation of `core/blackboard/` as the Canonical Evidence Ledger per §3 Component 1
- Formalisation of Role Separation Controller per §3 Component 2
- Build of Token Usage Tracker per §3 Component 3
- Layer Model Reconciliation Table as the permanent mapping authority per §3 Component 4
- Addition of scoreboard row #71 Token Usage Tracker
- Phase 1 build to begin, gated by `complete_gate.py` 0/0 before phase closure

**Signed:** Matt Nichol
**Date:** June 9th 2026
