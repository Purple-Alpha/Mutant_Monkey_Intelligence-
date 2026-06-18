# Mutant Monkey Brain / Immune / Lung Zero-Trust Control Loop Concept

> **NON-AUTHORITATIVE CONCEPT — NOT AUTHORITY.**
> This document records research input and design material for future MMI review. It does **not**
> authorize implementation, automation, runtime wiring, dispatcher changes, scoreboard changes,
> or transfer of project authority. Matt Nichol remains final authority.

**Classification:** `CONCEPT_IDEA` · `RESEARCH_INPUT` · `NEEDS_MMI_REVIEW` · `PARKED_DRAFT`
**Authority Status:** Non-authoritative concept material
**Build Status:** Not build-authorized
**Runtime Status:** Not runtime-authorized
**Source Material:** Manus AI zero-trust swarm homeostasis output and follow-up adversarial review
**Date:** 2026-06-18

---

## 1. Concept Thesis

The Mutant Monkey Brain / Immune / Lung control loop is a proposed zero-trust architecture for safely scaling, observing, reconciling, and containing multi-agent defensive work.

The core idea is:

```text
Lung = scaling and fission control
Brain = reconciliation and reasoning control
Immune System = safety, containment, teardown, privacy, and safe-stop enforcement
MMI = project intelligence and routing authority surface
```

This concept is intended to support the future evolution of Mutant Monkey Intelligence and its agentic control-plane architecture. It is not a signed contract and does not authorize implementation.

---

## 2. Purpose

The purpose of this concept is to explore how Mutant Monkey can safely operate a multi-agent defensive system without allowing:

* uncontrolled fission
* AI token/resource exhaustion
* child-agent self-scoring
* state drift
* stale baseline poisoning
* parser failure laundering
* cascading runtime exploitation
* cross-tenant data leakage
* unauthorized mode changes
* silent reconciliation denominator collapse

This concept attempts to preserve one central doctrine:

```text
Child agents observe.
Reconciliation decides.
Mode Controller governs.
Matt remains final authority.
```

---

## 3. Core Components

### 3.1 Lung Controller

The Lung Controller manages agent scaling.

Its responsibilities include:

* deciding when to Inhale/spawn child agents
* deciding when to Exhale/scale down child agents
* applying pre-fission budget checks
* preventing adversarial fission floods
* tracking active child agents
* enforcing cooldown and teardown rules
* preserving system visibility during cooldown

The Lung Controller must not become an uncontrolled scaling engine. It must treat attacker-controlled volume as a cost attack unless proven otherwise.

---

### 3.2 Brain / Reconciliation Gate

The Brain is the reconciliation layer.

Its responsibilities include:

* verifying child output tokens
* enforcing the Facts-Only Detector Contract
* rejecting child outputs that contain scores, verdicts, or recommendations
* calculating CVI or other risk metrics only outside child runtime
* tracking quorum
* preserving expected denominator counts
* handling UNEXTRACTED / CORRUPT / TIMEOUT states
* deciding whether evidence is complete enough to proceed
* routing unresolved uncertainty to fail-closed outcomes

The Brain must never trust a child agent's interpretation. It may only consume verified facts.

---

### 3.3 Immune System

The Immune System protects the swarm.

Its responsibilities include:

* Drop-and-Purge child teardown
* runtime vaporization
* memory zeroization
* child key revocation
* parser-failure containment
* privacy filter enforcement
* baseline mutation gating
* safe-stop escalation
* mode transition audit
* cross-tenant leakage prevention

The Immune System exists to prevent the swarm from becoming its own attack surface.

---

## 4. Facts-Only Detector Contract

Child agents are stateless, expendable observer cells.

They may observe and report facts only.

### 4.1 Child Agents May Return

* `observed_value`
* `extraction_state`
* `parser_status`
* `raw_metadata`
* `evidence_pointer`
* `input_context_hash`
* `output_hash`
* `child_agent_id`
* `parent_agent_id`
* `event_id`
* `parser_error_code`
* `timestamp`
* `signature`

### 4.2 Child Agents Must Not Return

* `risk_score`
* `confidence_score`
* `trust_score`
* `severity`
* `priority`
* `recommendation`
* `verdict`
* `classification`
* `anomaly_score`
* `weighted_signal`
* `normalized_score`
* `likelihood`
* `probability`
* `decision`
* `allow`
* `block`
* `approve`
* `reject`

### 4.3 Hard Rule

```text
If a child agent produces a score, verdict, recommendation, or decision, its output must be rejected.
```

---

## 5. Proposed Workflow

```text
Raw Event Ingestion
→ Fact-Sniffer Gateway
→ Pre-Fission Budget Check
→ Inhale Decision
→ Immutable Context Snapshot
→ Fragmented Child Deployment
→ Facts-Only Child Observation
→ Child Output Token
→ Drop-and-Purge Teardown
→ Reconciliation Gate
→ Baseline Mutation Gate
→ Mode Controller / Safe-Stop Decision
```

---

## 6. Key Design Ideas Worth Preserving

### 6.1 Fact-Sniffer Gateway

Before expensive AI fission, a cheap script-level gateway should inspect the raw event.

It should evaluate:

* malformed payload ratio
* repeated-source pressure
* near-duplicate burst fingerprints
* source reputation
* invalid transaction ratio
* queue depth
* tenant token budget
* fission budget breaker state

Purpose:

```text
Attacker-controlled event volume must not linearly increase LLM spend.
```

---

### 6.2 Systemic Visibility Loss Circuit Breaker

Parser failure must not reduce risk.

The system should distinguish:

```text
OBSERVED    = expected component was parsed
ABSENT      = component was not present and absence is meaningful
UNEXTRACTED = component was expected but could not be parsed
CORRUPT     = component appears corrupted or malformed
TIMEOUT     = parser failed to complete
```

Hard rule:

```text
UNEXTRACTED is not ABSENT.
UNEXTRACTED must never become 0.00 risk.
```

Repeated UNEXTRACTED / CORRUPT / TIMEOUT states should increase visibility pressure and may trigger write-lock, isolation, or safe-stop depending on severity.

---

### 6.3 Drop-and-Purge Child Lifecycle

The design must prohibit partial runtime handoff.

Forbidden:

* child-to-child handoff
* child-to-parent partial memory handoff
* suspended runtime resumption
* serialized partial context recovery
* retry from child memory
* peer continuation from child runtime state

Allowed recovery:

```text
Parent re-ingests the original immutable raw event from the evidence ledger and spawns a fresh child with a fresh immutable context snapshot.
```

---

### 6.4 Reconciliation Denominator Protection

If 5 child agents are expected and only 3 return, the system must not silently calculate based only on 3.

Required fields:

* `expected_child_count`
* `returned_child_count`
* `missing_child_count`
* `quorum_required`
* `quorum_met`
* `failed_child_policy`
* `denominator_policy`
* `timeout_policy`

Hard rule:

```text
Missing child outputs must not silently disappear from the denominator.
```

---

### 6.5 Adaptive Vendor-Scoped Sliding Lookforward Watch

The system should protect against temporal arbitrage.

Example attack:

```text
Day 1: attacker stages malicious baseline change
Day 31: attacker executes against staged baseline after fixed window expires
```

Required concept:

```text
No fixed clean cutoff may allow Day+1 evasion.
```

The watch should include:

* `watched_baseline_key`
* `vendor_scope_id`
* `baseline_epoch_timestamp`
* `lookforward_window_start`
* `lookforward_window_expiry`
* `renewal_reason`
* `direct_dependency_keys`
* `staged_change_hash`
* `execution_event_hash`
* `taint_analysis_window`
* `maximum_renewal_count`
* `fallback_cap_timestamp`
* `permanent_promotion_lockout`

Renewal must be constrained. The watch should not renew forever due to attacker-generated noise.

---

### 6.6 Parent-Only Baseline Mutation

No child output may directly alter:

* tenant baseline
* vendor baseline
* sender baseline
* payment baseline
* model weights
* tenant profile
* memory state

All mutation must pass through a parent-controlled Baseline Mutation Gate.

Required fields:

* `baseline_key`
* `previous_baseline_hash`
* `new_candidate_baseline_hash`
* `source_evidence_hash`
* `actor_lineage_chain`
* `taint_marker_propagation_status`
* `ratification_status`
* `rollback_hash`
* `permanent_lockout_conditions_met`

---

### 6.7 Mode Controller / Safe-Stop Interlock

Only the Mode Controller may change global mode.

Modes:

* `NORMAL`
* `DEGRADED`
* `ISOLATED`
* `RECOVERING`
* `SAFE_STOP`

Possible triggers:

* quorum loss timeout
* dual-critical watcher condition
* privacy breaker escalation
* fission budget breaker escalation
* systemic visibility loss
* baseline mutation violation
* child-output schema violation
* repeated fission-wave abuse

Hard rule:

```text
No child agent, spawned fission wave, or runtime worker may change global mode.
```

---

## 7. Manus AI Output Assessment

The Manus AI output produced a strong architecture skeleton and correctly included major elements such as:

* workflow matrix
* cryptographic ledger schemas
* child validation packet
* Drop-and-Purge teardown
* Reconciliation Gate
* Baseline Mutation Gate
* Mode Controller
* CVI integration
* red-team tests

However, it should not be treated as authoritative.

### 7.1 Useful Material

The following should be preserved as useful design input:

* Fact-Sniffer Gateway
* Pre-Fission Budget Check
* Lung Controller State Record
* Visibility Loss Record
* Sliding Lookforward Watch Record
* Stateless Child Validation Packet
* Destroyed Child Audit Record
* Reconciliation Quorum Record
* Baseline Mutation Request Record
* Mode Transition Record
* Red-team test cases

### 7.2 Identified Weaknesses

The Manus output had several weaknesses that require MMI review:

1. Cross-tenant privacy was marked as PASS while still underdefined.
2. Score-like fields appeared in control-plane schemas without enough boundary clarity.
3. Retry / respawn policy was not bounded tightly enough.
4. CVI constants and thresholds were too vague for build use.
5. Sliding lookforward renewal criteria were not exact enough.
6. Some medium risks were treated too gently in the self-audit table.

---

## 8. Required Hardening Before This Can Become a Signed Contract

Before this concept can become a signed design contract, it needs:

1. Explicit cross-tenant privacy schema.
2. Allowed aggregate fields list.
3. Forbidden raw tenant fields list.
4. Minimum cohort / k-anonymity rule.
5. Per-tenant key separation rule.
6. Strict retry cap for failed child agents.
7. Same-failure-family breaker.
8. No retry after suspected memory corruption.
9. Exact CVI constants.
10. Exact visibility-loss threshold.
11. Exact non-linear floor rule.
12. Exact write-lock trigger rule.
13. Exact lookforward renewal criteria.
14. Exact non-renewal criteria.
15. Safe-stop trigger mapping.
16. Red-team test acceptance criteria.

---

## 9. Classification

This document should be classified as:

```text
CONCEPT_IDEA
RESEARCH_INPUT
NEEDS_MMI_REVIEW
PARKED_DRAFT
```

It should not be classified as:

```text
AUTHORITATIVE_CURRENT
SIGNED_BUT_UNBUILT
SUPPORTED_BY_REPO
BUILT_NEEDS_VERIFICATION
```

unless and until MMI explicitly reviews, reconciles, and promotes it through the proper authority process.

---

## 10. Non-Authorization Statement

This concept does not authorize:

* implementation
* runtime wiring
* automation
* dispatcher changes
* scoreboard changes
* build work
* product feature work
* baseline mutation
* cross-tenant signal sharing
* child-agent deployment
* fission runtime expansion
* safe-stop behavior changes

This concept preserves design material only.

Matt remains final authority.

---

## 11. Suggested File Path

Recommended save path:

```text
mmi/concepts/MMI_BRAIN_IMMUNE_LUNG_ZERO_TRUST_CONTROL_LOOP_CONCEPT.md
```

Alternative if this should live closer to product architecture:

```text
4. Product_Roadmap/MMI_Brain_Immune_Lung_Zero_Trust_Control_Loop_Concept.md
```

Preferred path:

```text
mmi/concepts/MMI_BRAIN_IMMUNE_LUNG_ZERO_TRUST_CONTROL_LOOP_CONCEPT.md
```

because this is MMI control-plane concept material, not customer-facing product work.

---

## 12. Next Review Question

The next MMI review should answer:

```text
Should this concept remain parked, be split into separate Brain / Immune / Lung concept docs, or be converted into a formal requirements research lane?
```

No build should be inferred from this concept.
