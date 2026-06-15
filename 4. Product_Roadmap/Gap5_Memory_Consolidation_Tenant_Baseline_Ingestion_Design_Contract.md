# Mutant Monkey Inbox Shield — Memory Consolidation / Tenant Baseline Ingestion Design Contract

**Status:** SIGNED — §11 authorized for build
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Source:** Gap5_Memory_Consolidation_Tenant_Baseline_Ingestion_Concept_Doc.md + Organism Design Doctrine v1 + OQ-5 locked June 14 2026
**Depends on:** Mode Controller (SIGNED), Privacy Filter (SIGNED), ReconciliationAgent (GATED), Safe-Stop State Machine (GATED + Amendment 01 SIGNED), Cortex/Immune Interface (SIGNED), Collective Immune System (SIGNED)

---

## §11 Signature Block

```
Signed: Matt Nichol
Name:   Matt Nichol
Date:   June 14th 2026
Authority: Sole signing authority — Mutant Monkey Inbox Shield
```

---

## Purpose

This contract governs the Memory Consolidation / Tenant Baseline Ingestion system. It defines how raw evidence becomes a tenant baseline safely. It does not define detection agents, reconciliation logic, or any immune component. It governs the promotion pipeline only.

The tenant baseline is a governed, versioned, auditable source-of-truth. It is not a cache, a memory store, or an adaptive model. Every change to the tenant baseline is a state transition with a defined lifecycle, audit trail, and rollback path.

---

## Governing Principle

The system does not promote memory. It promotes evidence into baseline only after governance checks pass.

- Repeated observation is not proof of legitimacy.
- Multi-agent agreement is not proof of independent confirmation.
- High confidence is not approval authority.
- Rollback is not complete until affected downstream decisions are bounded, replayed, and marked.

---

## Section 1 — Evidence-to-Baseline Promotion Lifecycle

Promotion is a state transition. Steps execute in order. Failure at any step halts promotion and produces an audit record with the failure reason code.

| Step | Action | Failure halts at |
|---|---|---|
| 1 | Raw evidence observed | — |
| 2 | Evidence normalized — fields validated, entity identified, state extracted | Step 2 |
| 3 | Evidence lineage checked — source, instance, telemetry chain verified | Step 3 |
| 4 | Candidate baseline change proposed — key and proposed state identified | Step 4 |
| 5 | Confidence score calculated | Step 5 |
| 6 | Risk tier evaluated — key classified against lockout and tier tables | Step 6 |
| 7 | Promotion eligibility checked — all hard gates evaluated | Step 7 |
| 8 | Operator approval applied if required | Step 8 |
| 9 | Immutable baseline snapshot created — atomic with step 10 | Step 9 |
| 10 | Baseline promoted, rejected, or quarantined | Step 10 |
| 11 | Audit event recorded — regardless of outcome | Step 11 |

Steps 9 and 10 are atomic. If the snapshot cannot be created, the promotion does not proceed and an audit record is written.

---

## Section 2 — Evidence Payload Requirements

All fields are required. A missing or invalid field causes the record to fail at Step 2 with reason code `incomplete_evidence_payload`.

| Field | Requirement |
|---|---|
| `schema_version` | Contract version the record was produced against |
| `evidence_id` | Globally unique — UUID or equivalent |
| `tenant_id` | Tenant scope — no cross-tenant reads permitted downstream |
| `observed_at` | ISO 8601 timestamp of the original observation |
| `received_at` | ISO 8601 timestamp when the ingestion pipeline received the record |
| `source_component` | Agent or component that produced the evidence |
| `source_instance_id` | Specific instance — distinguishes two agents of the same type |
| `evidence_type` | Classification of what was observed |
| `entity_type` | Type of entity described (vendor, sender, employee, executive, etc.) |
| `entity_id` | Specific entity identifier within tenant scope |
| `candidate_baseline_key` | The exact baseline key this evidence proposes to affect |
| `observed_state` | Raw observed state before normalization |
| `normalized_state` | Normalized state proposed for baseline |
| `confidence_inputs` | All inputs used to calculate confidence score — serialized, auditable |
| `confidence_score` | Calculated score — must be reproducible from `confidence_inputs` |
| `risk_tier` | Risk classification of the candidate baseline key |
| `telemetry_signature` | Hash of the telemetry payload |
| `retention_policy` | Retention duration for this evidence record |
| `telemetry_lineage` | Chain of custody — sources, components, instances that contributed |
| `lineage_independence` | Boolean plus supporting detail — are contributing sources independent? |

### Telemetry Lineage Rule

Two agents reading the same upstream source do not constitute independent confirmation. The `telemetry_lineage` field must trace to the original data source for each contributing observation. If two contributing observations share any upstream source, `lineage_independence` must be set to false.

- Multi-agent agreement: does not establish independence
- Multi-source agreement: does not establish independence if sources share upstream
- Independent-lineage agreement: no shared upstream telemetry path — the only form that strongly supports promotion

If `lineage_independence = false`, `independent_lineage_factor` is set to its minimum value in the confidence formula.

---

## Section 3 — Confidence Score Formula

```
base_quality =
  0.20 * evidence_completeness +
  0.20 * observation_stability +
  0.15 * historical_consistency +
  0.15 * sample_size_weight +
  0.10 * recency_weight +
  0.20 * normalization_quality

lineage_adjusted_agreement =
  cross_source_agreement * independent_lineage_factor

gate_multiplier =
  source_reliability^2
  * lineage_adjusted_agreement^2
  * operator_policy_factor
  * (1 - anomaly_penalty)

raw_confidence_score =
  base_quality * gate_multiplier

confidence_score =
  clamp(raw_confidence_score, 0, risk_tier_cap)
```

### Hard Minimum Gates

All five must pass. Any single failure sets `promotion_eligible = false` with reason code `hard_gate_failed:[gate_name]`.

```
source_reliability >= 0.70
lineage_adjusted_agreement >= 0.70
evidence_completeness >= 0.90
normalization_quality >= 0.90
anomaly_penalty <= 0.20
```

### Risk-Tier Caps

```
low risk:      risk_tier_cap = 1.00
medium risk:   risk_tier_cap = 0.90
high risk:     risk_tier_cap = 0.75
critical risk: risk_tier_cap = 0.60
```

Confidence scores are capped by risk tier. Confidence does not equal authority to promote.

---

## Section 4 — Promotion Rules

All seven conditions must be true simultaneously. Failure at any condition halts promotion.

1. All required evidence fields present and valid
2. Confidence score meets threshold for the risk tier
3. All five hard minimum gates pass
4. `lineage_independence = true` or manually reviewed and approved by operator
5. Rollback snapshot of current baseline exists before promotion write
6. Separation-of-duties rule satisfied
7. Baseline key not in permanent auto-promotion lockout class

### Auto-Promotion Requirements

```
risk_tier = low
confidence_score >= 0.95
source_reliability >= 0.85
lineage_adjusted_agreement >= 0.85
independent_lineage_factor >= 0.85
evidence_completeness >= 0.95
normalization_quality >= 0.95
anomaly_penalty <= 0.05
rollback_snapshot_exists = true
baseline_key not in permanent lockout class
```

If any single condition fails, auto-promotion is blocked. Candidate enters operator review queue.

---

## Section 5 — Permanent Auto-Promotion Lockouts

The following key classes can never auto-promote. Permanent. No exceptions.

- Money movement keys
- IAM keys
- Alert suppression keys
- Security policy keys
- Executive authority keys
- Vendor payment identity keys
- Privileged access keys
- Detector threshold keys
- Allowlist keys that reduce detection coverage

Example locked keys:

```
vendor.payment_accounts.*
vendor.routing_number_hash
vendor.bank_account_hash
vendor.payment_instruction_change_pattern
vendor.known_good_callback_number
vendor.approved_payment_channel
employee.privileged_access_pattern
employee.admin_role_assignment
executive.payment_authority_pattern
identity_provider.privileged_group_membership
identity_provider.mfa_exception
identity_provider.conditional_access_exception
detector.alert_suppression_rule
detector.allowlist_entry
detector.threshold_reduction
security_policy.exfiltration_baseline
security_policy.login_geo_baseline_for_privileged_user
```

For any key in the lockout class:
```
operator_policy_factor = 0.0
promotion_eligible = false
auto_promotion = false
```

Manual promotion of locked keys requires dual-operator approval with full audit trail.

---

## Section 6 — Operator Approval and Separation of Duties

### Approval Tiers

| Risk tier | Approval required |
|---|---|
| Low | Auto-promotion if all strict gates pass; otherwise single-operator |
| Medium | Single-operator approval required |
| High | Dual-operator approval required |
| Critical | Dual-operator or admin/tenant-owner approval required |

### Separation-of-Duties Rules

```
The actor_id that generated the evidence cannot approve the baseline promotion.
The actor_id that requested the promotion cannot approve the baseline promotion.
The actor_id that implemented the change cannot be the sole approver.
```

For dual approval:
```
approver_1.actor_id != approver_2.actor_id
approver_1.actor_id != requester.actor_id
approver_2.actor_id != requester.actor_id
```

If separation-of-duties fails:
```
operator_policy_factor = 0.0
promotion_eligible = false
promotion_reason_code = separation_of_duties_failed
```

---

## Section 7 — Rollback and Reversibility

Every baseline promotion creates an immutable versioned snapshot before the promotion write. If the snapshot cannot be created, promotion does not proceed.

Rollback must answer:
- What changed in the baseline?
- Why was it promoted?
- Who or what approved it?
- When was it active?
- What detections were affected?
- Which events need re-evaluation?
- What changed after replay?
- Was the original promotion a false positive, false negative, operator error, or process defect?

---

## Section 8 — Rollback Blast Radius Protocol

### Step 1 — Freeze
```
baseline_status = frozen_pending_reconciliation
```
No new promotions. New evidence collected but not applied. Operator review permitted.

### Step 2 — Build impact graph
Nodes: baseline versions, evidence records, alerts, cases, recommendations, suppression decisions, downstream baseline candidates, reports.
Edges: `used_baseline_version`, `generated_from_evidence`, `suppressed_by_baseline`, `promoted_from_decision`, `included_in_report`, `operator_acted_on`.

### Step 3 — Reconciliation window
```
window_start = bad_baseline_activated_at
window_end = rollback_applied_at + ingestion_delay_buffer
```

### Step 4 — Replay without recursive promotion
Replay may update: case status, risk score, alert severity, evidence package annotations, suppression correction records, operator review queue.
Replay may not update: active baseline, global baseline, tenant allowlist, suppression rules, IAM assumptions, payment identity assumptions.

### Step 5 — Assign reconciliation outcomes
```
unchanged_after_replay
risk_increased_after_replay
risk_decreased_after_replay
alert_should_have_fired
alert_was_correctly_suppressed
alert_was_incorrectly_suppressed
case_requires_operator_review
report_requires_amendment
downstream_baseline_candidate_invalidated
```

### Step 6 — Limit cascade depth
```
max_reconciliation_depth = 1
```
Deeper replay requires explicit dual-operator approval.

### Step 7 — Quarantine downstream candidates
```
candidate_status = quarantined_due_to_parent_rollback
```
Cannot be promoted until operator explicitly clears after reconciliation window closes.

---

## Section 9 — Audit Schema

All audit events append-only and hash-chained. Broken chain is a contract violation.

| Field | Purpose |
|---|---|
| `audit_event_id` | Unique identifier |
| `tenant_id` | Tenant scope |
| `event_time` | ISO 8601 timestamp |
| `event_type` | promotion, rejection, quarantine, rollback, replay, approval, separation_of_duties_failure |
| `actor_type` | agent, operator, system |
| `actor_id` | Specific actor identifier |
| `baseline_key` | Key affected |
| `old_baseline_version` | Version before event |
| `new_baseline_version` | Version after event — null for rejection |
| `evidence_ids` | All contributing evidence records |
| `decision` | promoted, rejected, quarantined, rolled_back |
| `promotion_reason_codes` | All codes that contributed to or blocked promotion |
| `risk_tier` | Risk tier of the baseline key |
| `approval_policy` | Approval tier applied |
| `request_context` | Full promotion request context |
| `separation_of_duties` | Whether SoD satisfied; actor IDs evaluated |
| `rollback_status` | Whether part of a rollback and which rollback ID |
| `rollback_blast_radius` | Summary of impacted artifacts on rollback |
| `audit_signature` | Hash chained to previous record |

---

## Section 10 — Testable Invariants

| # | Invariant | Falsifiable test |
|---|---|---|
| TBI-INV-1 | High-repetition low-reliability observations cannot promote. | 10,000 observations from low-reliability source — verify hard gate blocks promotion |
| TBI-INV-2 | Two agents sharing upstream source do not create independent agreement. | Shared-source submission — verify `lineage_independence = false` |
| TBI-INV-3 | Money-movement keys cannot auto-promote. | Perfect-score evidence for `vendor.payment_accounts.*` — verify blocked |
| TBI-INV-4 | IAM keys cannot auto-promote. | Perfect-score evidence for `identity_provider.privileged_group_membership` — verify blocked |
| TBI-INV-5 | Alert-suppression keys cannot auto-promote. | Perfect-score evidence for `detector.alert_suppression_rule` — verify blocked |
| TBI-INV-6 | Requester cannot approve own change. | `approver.actor_id == requester.actor_id` — verify `separation_of_duties_failed` |
| TBI-INV-7 | Same actor cannot satisfy dual approval. | Both approvers share `actor_id` — verify `separation_of_duties_failed` |
| TBI-INV-8 | Rollback freezes key immediately. | Trigger rollback — verify `frozen_pending_reconciliation` before any other action |
| TBI-INV-9 | Replay cannot recursively promote. | Run replay — verify no promotion writes occur |
| TBI-INV-10 | In-window candidates are quarantined. | Trigger rollback — verify all in-window candidates quarantined |
| TBI-INV-11 | Audit record includes both baseline versions. | Any promotion or rollback — verify `old_baseline_version` and `new_baseline_version` present |
| TBI-INV-12 | Audit record includes evidence IDs and approval identities. | Any promotion — verify `evidence_ids` and `actor_id` present |
| TBI-INV-13 | Rollback produces reconciliation outcomes for all in-window artifacts. | Trigger rollback — verify every artifact receives one outcome code |
| TBI-INV-14 | Snapshot failure blocks promotion. | Simulate snapshot write failure — verify promotion blocked and audit record written |
| TBI-INV-15 | Broken audit chain is detectable. | Modify a committed audit record — verify chain validation fails |

---

## Out of Scope

- Detection agent logic
- Reconciliation verdict logic
- Immune component implementation
- New authority structures
- Auto-promotion of any locked key class
- Cascade replay beyond depth 1 without dual-operator approval
- Baseline updates bypassing the 11-step lifecycle

---

## Non-Authorizations

- Signing this contract authorizes Cursor to build the evidence-to-baseline promotion pipeline only, within the scope defined above.
- This contract does not amend any existing signed or gated contract.
- This contract does not define detection agents, reconciliation logic, or immune components.
