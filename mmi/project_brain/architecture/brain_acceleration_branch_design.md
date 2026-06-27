# Brain Acceleration Branch — Design + Sponge-Input Triage

> **Source:** research-AI sponge input ("speed up the swarm"). **Triaged against governance — not adopted wholesale.**
> **Lane:** Advisory (Claude) draft → Cursor writes. **Authority:** Matt §11. **Status:** advisory only — not §11, not build, not promotion.
> **Branch intent:** a governed performance layer for the brain that buys speed **without** spending the autonomy guardrails.

---

## 0. The one invariant

**Speed never comes from removing the human gate.** Every acceleration in this branch is either (a) inside the detection/triage path where it can't enact, or (b) a faster *path to a §11-signed rule* — never an autonomous substitute for one. Fast and governed are separate axes; this branch moves only the first.

---

## 1. Sponge-input triage (summary)

| Idea from doc | Verdict | Reason |
|---|---|---|
| Dynamic context pruning | **ACCEPT** | Least-privilege |
| Edge pre-filter | **REFRAME** | Triage/prioritize yes; drop/block = governed control |
| Parallelize non-dependent tasks | **ACCEPT (caveat)** | Separate audit trails; blast radius bounded |
| Thinking budgets | **REFRAME** | OK off verdict path; **never** on detection-verdict path |
| Few-shot output templating | **ACCEPT** | Formatting only |
| Gold-standard template from chains | **REFRAME** | Reference library; verified via #65 not agent say-so |
| Cached reasoning → auto production rule | **REJECT** | Use #67 → #65 → #70 → §11 path |
| Remove LLM forever static rules | **REJECT** | Same |
| MCP stable inter-agent contracts | **ACCEPT** | Compatible |
| Hardware mapping Commander/workers | **ACCEPT** | X8/A8 plan |

**Do not adopt sponge doc names** "DriftWatcher / Reality Controller" — use canonical roster below.

---

## 2. Canonical agent roster (replaces sponge placeholders)

### Naming collisions — read first

| Sponge / informal name | **Use in code/docs** | Scoreboard | Notes |
|---|---|---|---|
| "DriftWatcher" (operator) | **DriftWatcher operator role** | **Not** a scoreboard row | Cold worktree research only (`driftwatcher.md`) |
| "DriftWatcher" (runtime) | **`DriftWatcher` class, W2** | **#86** | `core/watchers/drift_watcher.py` — confidence-distribution observer |
| "Drift Watch" | **Compliance process** | **#66 RECLASSIFY** | Operator process, not runtime agent |
| "Reality Controller" | **`reality_controller/` research stack** | **None** | Lane 4 PARK — not production |
| "Commander" | **`SwarmCommanderAgent`** | **#1** | `agent_id`: `swarm_commander_001` |
| "Mode Controller" | **`ModeController`** | **#92** | `core/mode_controller/` |
| "Reconciliation" | **`ReconciliationAgent`** | **#84** | `agent_id`: `reconciliation_agent` |

### Brain Acceleration §2 layer → canonical mapping

| Acceleration layer | Canonical component | Scoreboard | Runtime path / class |
|---|---|---|---|
| **Scoped context** | `MissionContext` + per-agent contract slice | **#2** Mission Context Agent | `core/command/mission_context_agent.py`; DER type `MissionContext` in `agent_contract.py` |
| **Scoped context** (gateway) | Tenant segmentation + ring assignment | **#89** Blast Radius Controller | `GatewayController` → `TenantSegmentationController`, `RingController` |
| **Triage pre-filter** (flag/route) | Risk telemetry — score only | **#3** Risk Triage Agent | `core/command/risk_triage_agent.py` — **no** route-by-score keys |
| **Triage pre-filter** (edge heuristic) | Detection agents (pre-LLM facts) | **#78–#83** Phase 3 | e.g. `GeoVelocityAgent` (#79), detectors in `core/detectors/` |
| **Parallel mesh** (case loop) | Stage A orchestrator | **#1** | `SwarmCommander.run_case()` — **sequential today** |
| **Parallel mesh** (control plane) | Gateway per-tool gate | **#89** | `GatewayController.handle()` — one request at a time; audit per dispatch |
| **Parallel mesh** (fission) | Watcher-triggered copies | **#90**, **#91** | `LoadFissionController`, `SpecialisationFissionController` |
| **Parallel mesh** (verdict) | Ensemble voters R1/R2/R3 | **#84** | `ReconciliationAgent` — separate voter sub-budgets |
| **Tiered reasoning / budgets** | Session token budgets | **#89** (BRC Gate 1) | `SessionBudgetStore` / `TIER_BUDGETS` — **not** LLM thinking tiers yet |
| **Tiered reasoning** (verdict exempt) | Reconciliation ensemble | **#84** | Per-voter 50K sub-budget; exhaustion = `incomplete_budget_exhausted` |
| **Templated output** | `AgentContribution` + DER schema | All layers | `core/orchestrator/agent_contract.py` |
| **Stable tool contracts** | Gateway tool dispatch | **#89** | `GatewayRequest.tool` + `ModeCheck` seam |
| **Hardware pinning** | Operator infra | — | Outside repo; Commander = best HW per ops plan |
| **Swarm health observers** | Watcher trio | **#85**, **#86**, **#87** | `TimingWatcher`, `DriftWatcher`, `IntegrityWatcher` |
| **Threat escalation** | `ThreatLevelClassifier` | **#85–87** | ≥2 watchers to escalate above ROUTINE |
| **Rule promotion path** | Sandbox → evidence → review | **#67**, **#65**, **#70** | Never direct cache-to-production |
| **Safe halt** | Safe-Stop State Machine | **#94** | Matt-only recovery; halts branch |

### Governed rule path (replaces "cache to production")

```
#67 RuleImprovementAgent (sandbox proposal)
  → #65 CorrectionEvidenceAgent (proof bars)
  → #70 FinalReviewAgent (READY-FOR-§11, not authorized)
  → Matt §11
  → THEN fast deterministic rule / reduced LLM on that threat class
```

---

## 3. Interface specs — two dispatchers (do not conflate)

### A. Operator dispatcher (`scripts/mmi_dispatch.py`) — **not** the parallel mesh

**Role:** Governance queue truth for Matt/Cursor — derives `MODE`, ranked lanes, `--verify`.

**Not wired to:** runtime agent invocation, scoped context injection, or parallel case execution.

**Key surfaces:**

```python
# scripts/mmi_dispatch.py
PROJECT_IDENTITY = "Mutant Monkey Security"
REPO = "/home/socialarchitect/northstar"  # legacy path string in script

# CLI: python3 scripts/mmi_dispatch.py [--sync] [--verify]
# --sync: updates MMI_CURRENT_STATE.md routing block + MMI_RANKED_NEXT_ACTIONS.md
# --verify: routing-authority committed, build truth, drift, doctrine checks
```

Use this for **operator closeout**, not brain acceleration runtime.

### B. Runtime orchestrator — `SwarmCommander` / `SwarmCommanderAgent` (#1)

**Files:**

- Legacy spine: `core/orchestrator/swarm_commander.py` — class `SwarmCommander`
- Governed wrapper: `core/command/swarm_commander_agent.py` — class `SwarmCommanderAgent`

**Case loop entry (scoped context injection point today):**

```python
def run_case(
    self,
    context: MissionContext,
    agents: Iterable[Agent],
    *,
    stage: str = "stage_a",
    challenge_agents: Iterable[Agent] = (),
    anchor_provider: Callable[[], str | None] | None = None,
) -> DecisionEvidenceRecord:
```

**`MissionContext` (per-agent analyze input — intentionally minimal):**

```python
class MissionContext(StrictModel):
    case_id: UUID
    tenant_id: str
    inputs_digest: str          # SHA-256 of material under review
    source_record_id: UUID | None = None
    created_at: datetime
```

Agents read case material from Blackboard — raw body not duplicated in context. **Scoped context pruning** = pass only `MissionContext` + agent's contract slice, not full corpus.

**Pre-dispatch guard (every agent):**

```python
def validate_agent_dispatch(
    agent: AgentRegistryEntry,
    *,
    stage: str,
    requests_autonomous_action: bool = False,
) -> None:  # raises GovernanceError
```

**Parallel mesh status:** `run_case` iterates `agents` **sequentially** (`for agent in agents: agent.analyze(context)`). **No `asyncio.gather` / thread pool in spine today.** Parallel acceleration must either:

1. Add explicit dependency graph + concurrent invoke inside `SwarmCommander` (signed amendment), or
2. Use watcher-triggered fission (#90/#91) for isolated parallel copies with separate namespaces.

**Race-condition guard for future parallel:** each parallel branch needs separate `session_id` in `GatewayController`; shared `MissionContext.case_id` OK; contributions merged only after all branches complete — engines stay separate in DER (`contributions` tuple order = audit trail).

### C. Control-plane gateway — `GatewayController` (#89)

**File:** `core/control_plane/gateway.py`

**Every tool/agent action passes:**

```python
@dataclass(frozen=True)
class GatewayRequest:
    token: str
    claimed_agent_id: str
    tenant_id: str
    tool: str
    session_id: str
    args: Any = None
    candidate_id: str | None = None
    credential: str | None = None

def handle(self, request: GatewayRequest) -> GatewayDecision:
    # identity → ring → budget → breaker → mode → dispatch → telemetry
    # Any failure → GatewayRejected (no partial dispatch)
```

**Scoped context at gateway:** `args` may include `estimated_max_tokens` for pre-dispatch budget lock. Payloads claiming control-plane authority keys are **rejected** before dispatch.

**Mode seam (BRC-D10):**

```python
class ModeCheck(Protocol):
    def is_dispatch_allowed(self, tenant_id: str) -> bool: ...
```

Implemented by **#92 `ModeController`** — gateway reads only; agents cannot flip mode.

### D. Verdict path (verdict-budget exempt zone)

**#84 `ReconciliationAgent.analyze()`** — sole verdict producer; consumes `CanonicalEvidenceLedger`, not Commander loop.

Budget: `RoleTier.RECONCILIATION` — 150K tokens, per-voter sub-budgets R1/R2/R3 at 50K each (`budget.py`).

**Brain Acceleration rule:** no tiered "routine" budget reduction on this path.

---

## 4. Location map

### Design artifact (this branch)

| Path | Purpose |
|---|---|
| **`mmi/project_brain/architecture/brain_acceleration_branch_design.md`** | **This file** — advisory design + triage + roster + interfaces |
| `mmi/project_brain/architecture/geo_context_43_research_lanes.md` | Separate #43 research (not this branch) |
| `mmi/project_brain/architecture/reality_controller/` | Lane 4 PARK deception research — **exclude** from acceleration build |

### Reasoning / session budget config — **what exists today**

| Question | Answer |
|---|---|
| **`reasoning_budget_config` file?** | **Does not exist.** Sponge "thinking budgets" are not implemented as a separate config. |
| **Token/session budgets** | `core/control_plane/budget.py` — `TIER_BUDGETS`, `RECONCILIATION_VOTER_TOKEN_SUBBUDGET` |
| **Proposed future config** | `core/control_plane/reasoning_budget.py` or amendment block in `budget.py` — **requires signed contract** before implementation |
| **Verdict-path exemption** | Document in contract: `RoleTier.RECONCILIATION` + `#84` path immutable to "routine" tier |

**Current `TIER_BUDGETS` (BRC-D14 defaults):**

```python
TIER_BUDGETS = {
    RoleTier.DETECTION: Budget(50_000, 30, 15 * 60),
    RoleTier.RECONCILIATION: Budget(150_000, 90, 20 * 60),
    RoleTier.CONTROL_PLANE: Budget(25_000, 20, 10 * 60),
}
```

### Runtime wire points (Cursor execution targets)

| Concern | Path |
|---|---|
| Case orchestration | `core/orchestrator/swarm_commander.py` |
| Commander wrapper (#1) | `core/command/swarm_commander_agent.py` |
| Agent interface + `MissionContext` | `core/orchestrator/agent_contract.py` |
| Dispatch guard | `core/orchestrator/routes.py` → `validate_agent_dispatch` |
| Gateway spine | `core/control_plane/gateway.py` |
| Session budgets | `core/control_plane/budget.py` |
| Mode read seam | `core/mode_controller/controller.py` |
| Verdict ensemble | `core/reconciliation/reconciliation_agent.py` |
| Watchers | `core/watchers/` |
| Rule sandbox chain | `core/sandbox/rule_improvement_agent.py`, `correction_evidence_agent.py` |
| Final review | `core/orchestrator/final_review_agent.py` |
| Operator queue (not runtime) | `scripts/mmi_dispatch.py` |

---

## 5. Execution checklist (Cursor — after Matt ACCEPT)

1. Map §2 layers using **canonical names in §2 roster** — never sponge placeholders.
2. Confirm triage pre-filter is **flag/route only** — #3 rejects routing-by-score keys already.
3. Confirm tiered budgets **exempt #84** — grep any new budget config for `RECONCILIATION` / `reconciliation_agent`.
4. Route "turn into rule" through **#67 → #65 → #70 → §11** only.
5. Adversarial cross-check: can "routine" classification or pre-filter **suppress** detection?
6. Record ACCEPT/REJECT in **MMI_DECISION_LOG** on hot merge (Superintendent — not cold feedstock).
7. `mmi_dispatch.py --sync` + `--verify` + `pmv` on hot after merge.

---

## 6. Superintendent action — routing (Matt)

**Question:** ACCEPT this branch as a **governed performance layer** (REJECT rows stay out of build)?

| Response | Next step |
|---|---|
| **ACCEPT** | Signed design amendment or contract slice; then scoped implementation PRs per layer |
| **VERIFY** | Confirm pre-filter flag-not-drop + verdict-path budget exemption in first PR |
| **HOLD** | Park until #43 / breadth queue clears |

---

## Boundaries

- Advisory only — no §11, no build authorization, no scoreboard change from this file alone
- Lane 4 Reality Controller stays PARK
- Operator DriftWatcher role ≠ #86 W2 DriftWatcher ≠ #66 process
