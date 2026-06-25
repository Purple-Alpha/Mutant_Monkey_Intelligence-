# Token Usage Tracker — Per-Component Agent Design Contract (Deep Dive)

**Draft ID:** `MMI_71_TOKEN_USAGE_TRACKER_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** DRAFT UNSIGNED — pre-§11. Repo evidence: implementation built under Phase 1 (`fe355da`); 12 focused tests + 1 documented xfail (`tests/test_token_usage_tracker.py`). Signing locks D1–D10 and authorizes **GOVERNED_AGENT promotion review only** — **not** a wrapper re-build, **not** `SIGNED_UNBUILT` reconcile, **not** default-registry wiring, **not** production dispatch, **not** AUTH-5.

**Candidate:** #71 — Token Usage Tracker

**Owner:** Matt Nichol

**Track:** BREADTH / Governance (Layer 6 Learning / Governance — infrastructure component)

**Lane:** Agent Design Contract (BOR feedstock rank 1 · MMI-DEC-183)

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** **INFRASTRUCTURE_BUILT** — Phase 1 Component 3 already on disk; this contract closes the per-component promotion bar only.

**Source-of-truth links:**
- `4. Product_Roadmap/Phase1_Infrastructure_Agent_Design_Contract.md` (§11 SIGNED 2026-06-09 · P1-D5, P1-D6, P1-D8 · parent build authority)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (per-component promotion bar; Evidence Stage model)
- `4. Product_Roadmap/Swarm_Build_Map_Master.md` (Layer 6 — TokenUsageTracker #71)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#71 row — `NEEDS_SIGNED_CONTRACT`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/token_usage_tracker.py`
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_token_usage_tracker.py`
- `mmi/concepts/MMI_OPERATOR_LUNG_DIAL_SPEC.md` (Playhouse CostAttributionDashboard downstream — not built here)

**On-disk implementation path (already built — do not relocate):**
`3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/token_usage_tracker.py`

---

## Agent Design Contract block

Infrastructure ledger — not a detection/verification agent. Records per-tenant token consumption for Playhouse cost attribution only (P1-D6 reporting-only; P1-D8 no `AgentContribution`).

## Agent Design Contract

Agent name: Token Usage Tracker (`TokenUsageTracker`)
Swarm inventory ID: #71 — Token Usage Tracker
Canonical layer: 6 — Learning / Governance (infrastructure)
Canonical team / case type: N/A — infrastructure ledger (Playhouse cost attribution; not a case-type agent)
Authority level: Infrastructure component — observe/record only
Stage posture: VISION Stage A — analyze / recommend / evidence only
Evidence Stage (current): Stage 1 — Synthetic (at §11 signature, if signed)

Role: Append-only, tenant-isolated token-usage ledger + read-only per-tenant aggregates for Playhouse
Boundary: Ledger-in, reporting-out. No decision surface. No cross-tenant reads
Explicit non-authorities: No gate/block/throttle; no AgentContribution; no blackboard evidence writes; no scoring; no production dispatch; no default registry; no Playhouse UI build; no real-billing integration at ES1; no AUTH-5

Inputs: Validated `TokenUsageRecord` writes (caller-supplied closed schema)
Outputs: Append-only JSONL ledger rows; tenant-scoped reads; `TenantTokenUsageSummary` aggregates
Evidence emitted: none — infrastructure ledger; not a DER participant (P1-D8)
Data minimization: No raw prompt/content storage; closed enum fields only; caller-supplied metadata tokens
Tenant isolation: `read_for_tenant` and `aggregate_for_tenant` scoped to single `tenant_id`; no cross-tenant API

Two-pass role: N/A — not a two-pass detection/verification agent
Decision Evidence Record contribution: none (P1-D8)
Human review trigger: N/A at ES1 — operator GOVERNED_AGENT promotion review after §11 + clean gate
Verification trigger: Existing pytest suite (`test_token_usage_tracker.py`) + pre-build gate 0 blocking on contract

Scoring / action posture: No scoring; no action surface; observe/record only
Default rollout: Infrastructure built at `fe355da`; promotion gated on this contract + §11 + operator review
Autonomous action: none

Promotion conditions: §11 signed; Step 00 validator PASS; pre-build gate 0 blocking; tests green; operator promotion MMI-DEC
Demotion conditions: Cross-tenant leak; silent drop of rejected writes; ledger mutation; throttle/gate side effect introduced
Retest evidence: Permanent regression for any demotion trigger per template §6.5
Calibration requirement: N/A at ES1 — synthetic fixtures only until Stage 2 promotion authorization

Failure modes: Cross-tenant read; mutable ledger; throttle side effect; DER pollution; schema bypass
Required tests: `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_token_usage_tracker.py` (12 pass + 1 documented xfail)
Audit requirements: Step 00 `scripts/validate_agent_contract_block.py` PASS; pre-build gate via `audit_tools/complete_gate.py`; completion gate if code touched
Signed-spec dependencies: `4. Product_Roadmap/Phase1_Infrastructure_Agent_Design_Contract.md` (§11 signed 2026-06-09 · P1-D5, P1-D6, P1-D8)
Build Authorization dependency: Build complete at `fe355da` — §11 authorizes GOVERNED_AGENT promotion review only (not SIGNED_UNBUILT re-build). At signing, Evidence Stage 1 — Synthetic.

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-25 (draft placement · MMI-DEC-184):

| Placeholder | Resolved value | Repo evidence |
|---|---|---|
| Parent build authority | Phase 1 §3 Component 3 authorized build at `fe355da` | `Phase1_Infrastructure_Agent_Design_Contract.md` §11 |
| Per-component promotion bar | Separate contract required before `GOVERNED_AGENT` (Phase 1 §9 Q1 pattern) | Scoreboard `#71` `NEEDS_SIGNED_CONTRACT` |
| Record schema | `tenant_id`, `agent_id`, `model_id`, `token_count`, `action_type`, `timestamp`, `session_id` + immutable `record_id` | `TokenUsageRecord` in `token_usage_tracker.py` |
| Action-type closed enum | `detection`, `verification`, `reconciliation`, `mutation`, `audit` | `TokenActionType` enum |
| Tenant isolation | Reads and aggregates scoped to single `tenant_id`; no cross-tenant path | `test_tenant_isolation_on_read_and_aggregate` |
| Rejected-write audit | Malformed writes logged append-only to governance reject trail | `_log_rejected_write` |
| Test posture | 3 classes per Phase 1 §5 / AGENTS §5 | `test_token_usage_tracker.py` (12 passed + 1 xfail) |
| Playhouse consumer | CostAttributionDashboard reads aggregates only — separate contract | Swarm Build Map Playhouse table |

**Open before §11 (PARK sign if unresolved):**
1. Step 00 PASS — `python3 scripts/validate_agent_contract_block.py` on this contract (required before gate).
2. Pre-build gate on this contract via `audit_tools/complete_gate.py` (0 blocking target).
3. Confirm ES1 caps Agent Health Score at ~87 until Stage 2 promotion (template §6).

Repo-reconciliation placeholders: **resolved for draft review.** §11 unsigned; promotion review only after clean gate + signature.

---

## §0 Purpose

Phase 1 built the Token Usage Tracker as Component 3 under the infrastructure contract. The scoreboard correctly keeps #71 at `INFRASTRUCTURE_BUILT` with `NEEDS_SIGNED_CONTRACT` until this **per-component** Agent Design Contract satisfies the promotion bar (same pattern as #49 Audit Trail per Phase 1 §9).

This contract governs the **already-built** ledger surface. §11 signature authorizes **GOVERNED_AGENT promotion review** when repo evidence supports it — not a second build slice.

---

## §1 Scope

### In scope
- Governing metadata and invariants for the existing `TokenUsageTracker` implementation.
- Evidence Stage 1 (Synthetic) declaration at signature.
- Locked alignment with P1-D5, P1-D6, P1-D8 from the parent Phase 1 contract.
- Promotion path: `INFRASTRUCTURE_BUILT` → `GOVERNED_AGENT` after §11 + clean gate + operator promotion review.
- Regression test ownership for the existing 12 + 1 xfail suite.

### Out of scope
- Re-build, relocation, or behavior expansion of `TokenUsageTracker`.
- Playhouse CostAttributionDashboard UI implementation.
- Real MSP billing, invoice generation, or external cost APIs.
- Token throttling, budget enforcement, or agent operation gating.
- `AgentContribution` / blackboard evidence-chain participation.
- Default registry registration or production Commander dispatch.
- Evidence Stage 2/3 promotion or real-tenant billing data.
- Any change to Phase 1 parent contract text.

---

## §2 Locked Design Decisions

| ID | Decision |
|---|---|
| D1 | **Identity.** Token Usage Tracker is Layer 6 infrastructure, not a Layer 1–5 swarm agent. `agent_id` token for records uses canonical scoreboard agent names supplied by callers. |
| D2 | **Parent immutability.** P1-D5 record fields, P1-D6 reporting-only posture, and P1-D8 no-AgentContribution rule are inherited unchanged. This contract does not relax them. |
| D3 | **Append-only ledger.** `record()` appends; no update/delete API exists on `TokenUsageTracker`. |
| D4 | **Tenant isolation.** `read_for_tenant` and `aggregate_for_tenant` are scoped to one tenant; empty ledger returns empty list/summary, not error. |
| D5 | **Closed action enum.** Only `TokenActionType` values may be written; schema validation rejects extras via `StrictModel`. |
| D6 | **Rejected-write logging.** Invalid writes fail closed and append to governance reject JSONL — never silently dropped without audit. |
| D7 | **Aggregate reporting surface.** `TenantTokenUsageSummary` breaks out totals by agent, model, and action type for Playhouse — read-only batch summary. |
| D8 | **No wrapper indirection at ES1.** Governance attaches to the existing infrastructure module; no separate orchestrator wrapper required for promotion. |
| D9 | **Build already complete.** §11 does **not** authorize `SIGNED_UNBUILT` reconcile or a second implementation pass. |
| D10 | **Promotion bar.** `GOVERNED_AGENT` requires: this §11-signed contract, Grok/Codex pre-build gate 0 blocking on contract text, existing test suite green, separate operator promotion review record (MMI-DEC pattern). |

---

## §3 Invariants (must hold in production code)

1. **P1-D6 — Not a decision surface.** No method named or behaving as allow/block/gate/throttle on token counts.
2. **Append-only.** No in-place ledger mutation or delete path.
3. **Tenant boundary.** No API returns another tenant's rows from a single-tenant query.
4. **Schema fail-closed.** Malformed records raise `TokenUsageSchemaError` and log rejection — never land on ledger.
5. **No evidence-chain write.** Token ledger is separate from Canonical Evidence Ledger writes.
6. **Contract metadata pin.** `TOKEN_USAGE_TRACKER_CONTRACT` dict on module documents parent authority — update only via signed amendment.

---

## §4 Evidence Stage Declaration

At §11 signature (if signed): **Evidence Stage 1 — Synthetic** only.

- Validated on synthetic tenant/agent/model fixtures in tests.
- Not registered in `build_default_registry`.
- Not production-dispatched.
- Stage 2+ requires template §6.2 promotion conditions and separate operator authorization.

---

## §5 Failure Modes

| Failure | Expected behavior |
|---|---|
| Missing/empty `tenant_id` on read | `TokenUsageError` — fail closed |
| Invalid `token_count` (negative) | Schema rejection + governance reject log |
| Unknown `action_type` | Schema rejection |
| Cross-tenant read attempt via wrong tenant_id arg | Returns only matching rows — never leaks other tenant totals |
| Caller attempts to use ledger as throttle | Out of scope — no API exists; document as invariant violation if added |

---

## §6 Required Tests (existing — must remain green)

Path: `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_token_usage_tracker.py`

| Class | Purpose |
|---|---|
| Class 1 | Expected pass — record/read/aggregate happy paths |
| Class 2 | Adversarial — tenant isolation, schema rejection, reject logging |
| Class 3 | Known-gap xfail — documented completion path only |

No new tests required for contract draft placement. Gate may require manifest proof that Class 2 covers cross-tenant leakage.

---

## §7 Relationship to Signed Surfaces

- **Phase 1 Infrastructure Contract** — parent build authority; Component 3 definition.
- **Canonical Evidence Ledger (#49 pattern)** — sibling infrastructure; separate per-component contract path.
- **All governed agents** — may call `record()` as callers; ledger never calls back into agents.
- **Playhouse CostAttributionDashboard** — downstream read consumer; not authorized here.

---

## §8 Pre-Build Gate Plan

When Matt chooses §11 path:
1. Step 00: `python3 scripts/validate_agent_contract_block.py` on this contract (exit 0 required).
2. Pre-build gate via `audit_tools/complete_gate.py` on this contract (0 blocking target).
3. Adversarial focus: can a crafted record bypass tenant isolation or append without schema validation?
4. Worker manifest must prove no gate/throttle API and no AgentContribution path in module.

Gate glob: `mmi_71_contract_gate_*.md`

---

## §9 Open Questions (operator / gate)

| # | Question | Default |
|---|---|---|
| Q1 | ES1 health score cap | ~87 per template until Stage 2 |
| Q2 | Promotion without wrapper | Allowed — infrastructure module is the governed surface (D8) |
| Q3 | Stage 2 real billing data | Separate real-data / depth authorization |

---

## §11 Signature Block

**§11 — Token Usage Tracker Agent Design Contract (Deep Dive)**

- [ ] I approve this contract as written.
- [ ] I authorize pre-build gate review when ready.
- [ ] On clean gate, I §11-sign and authorize **GOVERNED_AGENT promotion review** (not SIGNED_UNBUILT, not re-build).

Confirmed: #71 **records** token usage for cost attribution; it **never** gates, blocks, or modifies agent operations.

> _(unsigned — Matt Nichol §11 pending)_

---

## BUILD CONDITIONS (post-§11)

**Not applicable for re-build.** Implementation exists at `fe355da`. §11 signature authorizes promotion review path only when operator separately records GOVERNED_AGENT promotion (MMI-DEC entry).

At signing, this component remains at **Evidence Stage 1 — Synthetic**. No Playhouse UI, real billing, or production dispatch implied.

---

*End of contract.*
