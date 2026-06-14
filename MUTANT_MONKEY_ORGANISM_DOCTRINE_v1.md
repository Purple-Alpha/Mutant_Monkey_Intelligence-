# Mutant Monkey Inbox Shield — Organism Design Doctrine v1
**Status:** DOCTRINE — advisory lane only. No build authorization. Contracts required before build.
**Date:** June 13 2026
**Authority:** Matt Nichol — sole signing authority
**Source:** Architecture critique session June 13 2026. Pressure-tested against all signed/gated contracts.

---

## Governing Thesis

Mutant Monkey Inbox Shield is a bounded defensive organism whose cortex interprets evidence and whose immune system stabilizes the organism under stress, but neither organ may overrule signed safety contracts, cross tenant boundaries, mutate itself at runtime, or act outside reversible, logged, operator-governed limits. The organism is alive only while it preserves compartmentalization, privacy, mode authority, evidence discipline, and fail-closed recovery. Resilience is not permission to self-expand, self-authorize, or improvise beyond contract.

---

## Non-Negotiable Invariants

All 21 invariants are falsifiable. Each names the enforcing component or contract.

| # | Invariant | Enforced by | Falsifiable test |
|---|---|---|---|
| 1 | Mode Controller is sole global epoch and mode authority for NORMAL / DEGRADED / ISOLATED / RECOVERING. No other component may increment epoch or declare global mode transition. | Mode Controller MC-D2 | Attempt epoch increment from any component other than Mode Controller — verify rejected |
| 2 | Heartbeat timeout triggers local ISOLATED WITHOUT epoch increment. Only Mode Controller increments epoch on recovery broadcast. Local epoch is never incremented during local fallback. | Mode Controller MC-D6 | Simulate heartbeat loss — verify epoch unchanged on tenant side |
| 3 | No raw tenant identifier, mailbox content, vendor identifier, user identifier, or tenant-specific evidence may cross a tenant boundary. The Privacy Filter is the fail-closed boundary. | Privacy Filter PF-D5 | Inject raw tenant_id into broadcast candidate — verify pipeline blocks it |
| 4 | If the Privacy Filter pipeline or independent breaker cannot validate a cross-tenant broadcast, the broadcast is denied. Logging the violation is not sufficient — the broadcast must not occur. | Privacy Filter PF-D2/PF-D3 | Open Privacy Filter breaker — verify zero broadcast events emitted |
| 5 | Every control-plane action must pass identity → ring → budget → breaker → mode → dispatch → telemetry in order. A skipped lifecycle step invalidates the action. | Blast Radius Controller BRC-D1 | Attempt direct agent tool call bypassing gateway — verify rejection |
| 6 | Rings 0-3 are hard containment boundaries. No agent, child, dispatch, or telemetry path may exceed its assigned ring without a new signed authorization path. | Blast Radius Controller | Attempt cross-ring action without authorization — verify blocked and logged |
| 7 | Watcher Agents are neutral observers. They append to ObservationLog and classify threat level. They do not produce final verdicts or enforcement decisions. | Watcher Agents WA-D1 | Verify watcher output contains no verdict fields |
| 8 | Load Fission and Specialisation Fission may only originate from legitimate Watcher escalation. No detection agent, cortex process, or optimization loop may self-trigger fission. | Load/Specialisation Fission v2 LF-D1 | Inject fission instruction into email payload — verify no fission fires |
| 9 | Children may not spawn grandchildren. Any attempt at deeper fission than one generation is invalid and must fail closed. | Fission v2 LF-D2/SF-D2 | Attempt child-initiated fission — verify blocked and logged |
| 10 | Load Fission may create exact-copy children only. Net-new agent types require Specialisation Fission and operator sign-off gate. | Specialisation Fission v2 SF-D6 | Attempt net-new type activation without sign-off — verify blocked |
| 11 | Every child agent receives a fresh identity. Permissions are the intersection of parent authority, tenant context, ring boundary, and signed contract. No inherited credentials. | Fission v2 LF-D3 | Verify child token does not contain parent credentials |
| 12 | Layer 0 Knowledge agents and Layer 1 Detection swarm generate evidence, observations, and signals only. They do not produce verdicts. | Layer 0/1 GATED | Scan all detection agent outputs for verdict fields — verify absence |
| 13 | Verdict authority belongs only to the gated ReconciliationAgent ensemble. No single detector, watcher, cortex process, or immune subsystem may bypass it. | ReconciliationAgent GATED | Verify no component other than ReconciliationAgent writes to verdict ledger |
| 14 | If two detection agents produce conflicting evidence, the conflict must be surfaced as a named conflict in the evidence chain and resolved by R3 Conflict Resolution Voter. Conflicts are not hidden. | ReconciliationAgent R3 voter | Inject conflicting evidence — verify named conflict record created |
| 15 | ReconciliationAgent ensemble must use at minimum two voters with different input weighting schemes. Voter configuration is version-controlled and immutable at runtime. | ReconciliationAgent contract | Verify voter configuration cannot be changed at runtime |
| 16 | Mutation Engine may operate only in sandbox conditions, requires 3-shot confirmation, requires operator sign-off, and must preserve rollback capability. | Mutation Engine GATED | Attempt mutation deployment without 3-shot confirmation — verify blocked |
| 17 | Agent confidence baselines may only change after sufficient tenant data exists and by signed amendment to the relevant agent contract. Runtime self-reweighting is forbidden. | Agent contract amendment policy | Verify no runtime confidence baseline changes without signed amendment |
| 18 | After a threat event is closed by the ReconciliationAgent, confirmed evidence may be promoted to the tenant baseline only through a governed ingestion step that validates schema, provenance, and reversibility. | Memory consolidation contract — NEEDED | Verify no automatic baseline update without governed ingestion |
| 19 | Collective Immune System may not be built or activated merely because Mode Controller and Privacy Filter are signed. Their signing satisfies the DEPTH GATE prerequisite only. A new signed CIS contract is still required before build. | DEPTH GATE policy | Verify no CIS code exists without signed CIS contract |
| 20 | The organism enters controlled safe-stop when: Mode Controller quorum is lost beyond defined timeout, Privacy Filter breaker cannot recover, or any two simultaneous CRITICAL watcher events cannot be resolved within defined window. Safe-stop is logged and requires operator action to exit. | Safe-stop contract — NEEDED | Simulate each condition — verify safe-stop fires and operator action required |
| 21 | Biological language is allowed only as framing. Any principle that cannot be translated into a falsifiable constraint is not doctrine. | This document | Review every principle — verify each has a corresponding testable rule |

---

## Organ Boundary Doctrine

### Cortex — Interpretation Organ

The cortex interprets tenant-scoped evidence, proposes hypotheses, compares signals, and contributes evidence into the governed chain. It may reason about inbox events, vendor drift, sender history, geo anomalies, timing, and behavioral patterns.

**The cortex may ask:** "What does this evidence appear to mean?"

**The cortex may not:**
- Authorize enforcement actions
- Trigger fission
- Trigger mutation
- Declare global mode transitions
- Perform cross-tenant data access
- Produce final verdicts

### Immune System — Stabilization Organ

The immune system preserves safety, containment, and recoverability. It includes Mode Controller, Privacy Filter, Blast Radius Controller, Watcher Agents, Fission mechanisms, Mutation Engine, and ReconciliationAgent.

**The immune system may decide:** "What state is safe for the organism?"

**The immune system may not:**
- Silently rewrite cortex reasoning
- Mutate detector logic without operator sign-off
- Promote memory without governed ingestion
- Produce enforcement actions that bypass ReconciliationAgent

### Control Plane — Enforcement Organ

The control plane enforces gateway lifecycle, mode state, privacy filtering, and blast radius containment.

**The control plane may not:**
- Read email content
- Produce evidence or verdicts
- Be influenced by agent-reported state

### Watcher Agents — Observation Organ

Watcher Agents are neutral observers. They classify threat level and are the only legitimate fission trigger source.

**Watcher Agents may not:**
- Write to core/blackboard/
- Influence verdicts
- Act unilaterally on threat level — requires at least two independent watchers
- Communicate directly with detection agents or ReconciliationAgent

### Memory — Evidence and Audit Organ

Memory includes the evidence ledger, mutation audit trail, and governance decision log.

**Memory may not:**
- Allow cross-tenant reads of raw evidence
- Allow modification of committed records
- Be updated by any agent without governed ingestion

---

## Cortex-Immune Interface Rules

1. Cortex-to-immune communication must be evidence-bearing, logged, and tenant-scoped.
2. Immune-to-cortex communication must occur through mode state, reconciliation output, safe-stop state, or governed baseline updates.
3. Watcher observations may trigger escalation paths, but raw watcher output may not directly alter cortex logic.
4. Reconciliation verdicts may close events, surface named conflicts, and authorize governed ingestion. They do not create new build authority.
5. Baseline updates require schema validation, provenance validation, tenant scope validation, and reversibility.
6. No hidden channel may exist between cortex and immune organs.
7. No organ may bypass Mode Controller, Privacy Filter, Blast Radius Controller, or ReconciliationAgent.

---

## Existing Coverage Map

| Principle | Coverage status |
|---|---|
| Mode authority is singular | Fully covered — Mode Controller SIGNED |
| Heartbeat timeout without epoch increment | Fully covered — Mode Controller SIGNED MC-D6 |
| Tenant data never crosses raw | Fully covered — Privacy Filter SIGNED |
| Privacy failure blocks communication | Fully covered — Privacy Filter SIGNED |
| Ring containment and lifecycle gateway | Fully covered — BRC GATED |
| Watcher-driven escalation | Fully covered — Watcher Agents GATED |
| Fission watcher-triggered only | Fully covered — Fission v2 SIGNED |
| Fission max depth 1 | Fully covered — Fission v2 SIGNED |
| Fresh identity and permission intersection | Fully covered — Fission v2 SIGNED |
| Evidence-only detection | Fully covered — Layer 0/1 GATED |
| Sole verdict producer | Fully covered — ReconciliationAgent GATED |
| Named conflict handling | Covered — R3 Conflict Resolution Voter in ReconciliationAgent contract |
| Minimum two voters different weighting | Partially covered — ReconciliationAgent ensemble exists, weighting immutability not fully specified |
| Mutation sandbox reversible 3-shot | Fully covered — Mutation Engine GATED |
| Runtime self-reweighting forbidden | Not covered — agent confidence baseline amendment policy needed |
| Governed memory ingestion | Not covered — memory consolidation contract needed |
| DEPTH GATE | Fully covered — policy enforced |
| Safe-stop state | Not covered — safe-stop contract needed |
| Cortex-immune boundary | Partially covered — implicit across contracts, no single interface contract |
| Global Homeostasis Index | Partially covered — named in Mode Controller, no Homeostasis Engine contract |
| Cross-organ telemetry standard | Partially covered — individual contracts have audit requirements, no unified standard |

---

## Failure and Safe-Stop Model

The organism does not fail catastrophically. It enters controlled safe-stop when core safety guarantees can no longer be trusted.

**Safe-stop conditions — any one triggers:**
1. Mode Controller quorum loss exceeds defined timeout
2. Privacy Filter breaker cannot recover
3. Two simultaneous CRITICAL watcher events remain unresolved within defined window
4. A fission, mutation, or dispatch path violates its signed boundary and containment cannot be proven
5. Named evidence conflicts cannot be resolved by ReconciliationAgent

**Safe-stop properties:**
- Named controlled state — not an error condition
- Logged immediately on entry with full context
- Requires operator action to exit
- No automatic recovery without operator sign-off
- Proof of state safety required before exit

Safe-stop is not a failure of discipline. It is the proof that the organism prefers bounded shutdown over silent corruption.

---

## Overengineering Conversions

These biological metaphors have been converted into enforceable engineering constraints:

| Metaphor | Enforceable constraint |
|---|---|
| Lateral inhibition between cortical columns | Conflicting evidence from two detection agents must be surfaced as a named conflict and resolved by R3 Conflict Resolution Voter |
| Hippocampal memory consolidation | After a threat event is closed, confirmed evidence is promoted to tenant baseline only through governed ingestion that validates schema, provenance, tenant scope, and reversibility |
| Hebbian plasticity strengthens pathways | Agent confidence baseline updates require signed amendment after sufficient tenant data — no runtime reweighting |
| Organism mortality | Controlled safe-stop with five named entry conditions, logged state, operator exit required |
| Cognitive diversity seeding | ReconciliationAgent ensemble must use at minimum two voters with different input weighting schemes — immutable at runtime |
