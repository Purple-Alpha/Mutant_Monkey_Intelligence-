# Mutant Monkey Inbox Shield — Organism Architecture Gap List
**Status:** ADVISORY — gap list only. No build authorization. Each gap requires a signed contract before build.
**Date:** June 13 2026
**Source:** Organism Design Doctrine critique session June 13 2026.
**Dependency order:** gaps listed in the order they must be closed.

---

## Gap 1 — Collective Immune System Contract
**Priority:** IMMEDIATE — DEPTH GATE is now open
**Blocks:** all Phase 6 build work
**What it must define:** scope, organs, authority, escalation paths, containment, recovery, relationship to Mode Controller and Privacy Filter
**What it must NOT include:** Homeostasis Engine internal logic, memory consolidation rules, cognitive diversity seeding, specific consensus technology

---

## Gap 2 — Safe-Stop State Machine Contract
**Priority:** HIGH — referenced in doctrine but not governed
**Blocks:** organism resilience guarantees
**What it must define:** five named entry conditions, logging requirements, operator exit requirements, recovery proof requirements, relationship to ISOLATED / DEGRADED / RECOVERING modes
**What it must NOT include:** automatic recovery without operator sign-off

---

## Gap 3 — Cortex / Immune Interface Contract
**Priority:** HIGH — boundary rules exist implicitly, not formally
**Blocks:** cross-organ communication governance
**What it must define:** legal signals between organs, forbidden channels, evidence handoff, reconciliation feedback, baseline update boundaries, no-hidden-channel invariant
**What it must NOT include:** implementation of any organ — interface only

---

## Gap 4 — Homeostasis Engine Policy Contract
**Priority:** MEDIUM — Global Homeostasis Index named in Mode Controller but engine not specified
**Blocks:** actions beyond Mode Controller health computation
**What it must define:** thresholds, actions, non-authority boundaries, relationship to Mode Controller, eight health layer inputs
**What it must NOT include:** authority to override Mode Controller, Privacy Filter, or ReconciliationAgent

---

## Gap 5 — Memory Consolidation / Tenant Baseline Ingestion Contract
**Priority:** MEDIUM — no governed process for evidence-to-baseline promotion
**Blocks:** learning loop closing correctly
**What it must define:** governed ingestion step, schema validation, provenance validation, tenant scope validation, reversibility, operator approval thresholds
**What it must NOT include:** automatic baseline updates without governed ingestion

---

## Gap 6 — Agent Confidence Baseline Amendment Policy
**Priority:** MEDIUM — runtime self-reweighting is forbidden but no amendment process defined
**Blocks:** legitimate calibration after real tenant data
**What it must define:** what constitutes sufficient tenant data, amendment process, operator sign-off requirement, which agent contracts must be amended
**What it must NOT include:** runtime reweighting without signed amendment

---

## Gap 7 — Reconciliation Voter Configuration Contract
**Priority:** LOW — ReconciliationAgent is gated but voter weighting immutability not fully specified
**Blocks:** full Invariant 15 coverage
**What it must define:** minimum voter count, different weighting schemes requirement, immutable runtime configuration, versioning, R3 Conflict Resolution Voter behavior
**Note:** R3 is already defined in the ReconciliationAgent GATED contract — review whether this gap is already partially closed before drafting

---

## Gap 8 — Behavioral Loop Detection Detail
**Priority:** LOW — BRC mentions loop detection but thresholds not fully specified
**Blocks:** complete safe-stop interaction definition
**What it must define:** detection window, threshold values, escalation path, safe-stop interaction
**What it must NOT include:** semantic content analysis — loop detection must remain behavioral only

---

## Gap 9 — Cross-Organ Telemetry and Audit Standard
**Priority:** LOW — individual contracts have audit requirements, no unified standard
**Blocks:** complete audit credibility across all organs
**What it must define:** mandatory log fields across cortex, immune, reconciliation, fission, mutation, privacy, mode, and safe-stop events; retention requirements; export format; cross-component correlation
**What it must NOT include:** new authority structures — telemetry only

---

## Gap 10 — Operator Authority Policy
**Priority:** LOW — operator sign-off required in many contracts but no unified policy
**Blocks:** clear emergency override boundaries
**What it must define:** who can sign, when sign-off is required, what emergency override means, how reversibility is proven, whether any invariants may be suspended under operator authority
**What it must NOT include:** automatic override capability — operator action must be explicit and logged

---

## Open Questions For Matt Before Next Contract Session

1. Should CIS move from depth-gated concept into a signed design contract now?
2. What is the exact safe-stop timeout for Mode Controller quorum loss?
3. What is the exact recovery window for unresolved simultaneous CRITICAL watcher events?
4. Who has authority to exit safe-stop — Matt only or rotating CIRT role?
5. Does Homeostasis remain inside Mode Controller authority only or become a separate contract?
6. Should baseline ingestion after a closed threat event require operator approval every time or only above defined risk threshold?
7. What evidence fields are mandatory before confirmed evidence may update a tenant baseline?
8. What telemetry must be mandatory across all organs for audit credibility?
9. Are any emergency overrides allowed or are the 21 invariants absolute?
