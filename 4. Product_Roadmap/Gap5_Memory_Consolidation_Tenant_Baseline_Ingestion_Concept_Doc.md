# Mutant Monkey Inbox Shield — Memory Consolidation / Tenant Baseline Ingestion
## Gap 5 Concept Document

**Status:** CONCEPT — advisory lane only. No build authorization. Requires design contract and §11 signature before build.
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Source:** Gap List Gap 5 + Organism Design Doctrine v1 + OQ-5 locked decision June 14 2026
**Next step:** Matt reviews, authorizes design contract drafting, then §11.

---

## 1. Executive Summary

Research Gap 5 defines how raw evidence becomes a tenant baseline safely.

The tenant baseline is not a cache. It is not a memory store. It is not an adaptive model that updates in the background. It is a governed, versioned, auditable source-of-truth that downstream detection agents, scoring systems, and reconciliation voters depend on to evaluate whether observed behavior is normal for a given tenant.

Corrupting the tenant baseline corrupts everything downstream. An attacker who can shift the baseline can blind the detection layer without touching a single detector. A careless operator who approves a bad baseline change can create suppression conditions that persist until someone notices the system stopped alerting.

Gap 5 closes this by defining a governed evidence-promotion pipeline. The system may learn from observed tenant behavior. It must not silently normalize suspicious or high-risk behavior. Every baseline change is a state transition with a defined lifecycle, audit trail, and rollback path — not a background update.

---

## 2. Problem Statement

If every repeated observation is allowed to update the tenant baseline, an attacker can slowly train the system to treat malicious behavior as normal. This is not a theoretical risk. It is the natural consequence of any adaptive system without governed ingestion.

Attack and failure patterns this contract must prevent:

**Slow poisoning via repeated attacker-controlled sender behavior.** An attacker who controls a sender address can send enough mail to push that sender into the tenant's known-good baseline before launching a payload. If repetition alone drives promotion, the attacker wins before the attack begins.

**Compromised vendor mailbox normalizing payment-change signals.** A vendor mailbox that has been taken over can generate payment-change patterns at low frequency over weeks. Without lineage-gated promotion rules, those patterns become baseline before any alert fires.

**Multi-agent false agreement on a poisoned telemetry source.** Two detection agents reading the same poisoned log file do not constitute independent cross-source confirmation. If the confidence formula treats agent count as equivalent to source independence, poisoned evidence gets multiplied rather than detected.

**Accidental operator approval of a bad baseline change.** An operator presented with a plausible-looking promotion request under time pressure may approve it. Separation-of-duties rules and risk-tier gates reduce but do not eliminate this risk. Rollback must be bounded and auditable.

**Rollback causing downstream reconciliation chaos.** Rolling back a baseline that was active for weeks can invalidate suppression decisions, closed cases, and downstream baseline candidates. Without a defined blast radius protocol, rollback creates more uncertainty than the original bad change.

---

## 3. Core Design Principle

These four principles govern every decision in this contract:

**Repeated observation is not proof of legitimacy.**
**Multi-agent agreement is not proof of independent confirmation.**
**High confidence is not approval authority.**
**Rollback is not complete until affected downstream decisions are bounded, replayed, and marked.**

And the foundational rule:

**The system does not promote memory. It promotes evidence into baseline only after governance checks pass.**

Confidence scores inform. They do not decide. Operator approval gates decide. Hard lockouts decide. Risk-tier caps decide. The confidence score is an input to the promotion eligibility check, not an override of it.

---

## 4. Evidence-to-Baseline Promotion Model

Baseline promotion is a state transition. It is not a background update, a cron job, or an automatic consequence of high confidence. Each step in the lifecycle must complete before the next begins. A failure at any step halts promotion and produces an audit record.

**Promotion lifecycle:**

1. Raw evidence observed — detection agent produces an observation
2. Evidence normalized — fields validated, entity identified, state extracted
3. Evidence lineage checked — source component, instance, and telemetry chain verified
4. Candidate baseline change proposed — specific baseline key and proposed state identified
5. Confidence score calculated — non-linear formula applied against all inputs
6. Risk tier evaluated — baseline key classified against lockout and tier tables
7. Promotion eligibility checked — all hard gates evaluated; any failure halts here
8. Operator approval applied if required — approval tier determined by risk tier; separation-of-duties enforced
9. Immutable baseline snapshot created — previous baseline version snapshotted before any write
10. Baseline promoted, rejected, or quarantined — state written with audit linkage
11. Audit event recorded — tamper-evident log entry created regardless of outcome

Steps 9 and 10 are atomic. If the snapshot cannot be created, the promotion does not proceed.

---

## 5. Evidence Payload Requirements

Every evidence record submitted for baseline promotion must contain the following fields. A missing required field causes the record to fail normalization and halts promotion with reason code `incomplete_evidence_payload`.

| Field | Purpose |
|---|---|
| `schema_version` | Contract version the record was produced against |
| `evidence_id` | Globally unique identifier for this evidence record |
| `tenant_id` | Tenant scope — no cross-tenant reads permitted downstream |
| `observed_at` | Timestamp of the original observation |
| `received_at` | Timestamp when the ingestion pipeline received the record |
| `source_component` | Agent or component that produced the evidence |
| `source_instance_id` | Specific instance identifier — distinguishes two agents of the same type |
| `evidence_type` | Classification of what was observed |
| `entity_type` | Type of entity the evidence describes (vendor, sender, employee, etc.) |
| `entity_id` | Specific entity identifier within the tenant scope |
| `candidate_baseline_key` | The exact baseline key this evidence proposes to affect |
| `observed_state` | The raw observed state before normalization |
| `normalized_state` | The normalized state proposed for baseline |
| `confidence_inputs` | All inputs used to calculate the confidence score — serialized for audit |
| `confidence_score` | Calculated score — must be reproducible from `confidence_inputs` |
| `risk_tier` | Risk classification of the candidate baseline key |
| `telemetry_signature` | Hash of the telemetry payload for tamper detection |
| `retention_policy` | How long this evidence record must be retained |
| `telemetry_lineage` | Chain of custody — which sources, components, and instances contributed |
| `lineage_independence` | Boolean and supporting detail — are contributing sources independent? |

### Why Telemetry Lineage Is Required

Two agents reading the same poisoned log file must not count as independent cross-source confirmation. Without `telemetry_lineage`, the confidence formula cannot distinguish:

- **Multi-agent agreement:** Two agents produced the same observation. Does not establish source independence if they read the same input.
- **Multi-source agreement:** Observations came from different data sources. Stronger, but sources may still share a common upstream.
- **Independent-lineage agreement:** Observations came from sources with no shared upstream telemetry path. This is the only form of agreement that strongly supports baseline promotion.

The `telemetry_lineage` field must trace the chain of custody to the original data source. The `lineage_independence` field must assert whether that chain is independent of all other contributing sources in the same promotion candidate. If `lineage_independence` is false or cannot be determined, the `independent_lineage_factor` in the confidence formula is set to its minimum value.

---

## 6. Confidence Score Formula

The confidence score uses a non-linear model. A purely linear weighted sum allows high sample size or high recency to compensate for poisoned sources. The non-linear gate multiplier prevents this.

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

Why this formula behaves correctly:

- `source_reliability^2` — weak source reliability does not reduce the score linearly; it collapses it. A source at 0.70 reliability contributes 0.49 to the gate multiplier, not 0.70.
- `lineage_adjusted_agreement^2` — weak independent lineage similarly collapses the gate multiplier regardless of how many agents agreed.
- Large sample size increases `sample_size_weight` inside `base_quality` but cannot rescue a low gate multiplier. A poisoned source with 10,000 observations still produces a near-zero confidence score if `source_reliability` is low.
- `operator_policy_factor` is set to 0.0 for permanently locked baseline keys, forcing `confidence_score` to zero regardless of all other inputs.
- `(1 - anomaly_penalty)` applies a direct reduction for anomalous observations. An anomalous source does not get to contribute normally to the score.

### Hard Minimum Gates

All five gates must pass before promotion eligibility is evaluated. Any single failure sets `promotion_eligible = false`.

```
source_reliability >= 0.70
lineage_adjusted_agreement >= 0.70
evidence_completeness >= 0.90
normalization_quality >= 0.90
anomaly_penalty <= 0.20
```

If any gate fails:
```
promotion_eligible = false
promotion_reason_code = hard_gate_failed:[gate_name]
```

---

## 7. Risk-Tier Caps

High confidence scores on high-risk baseline keys are intentionally capped. Confidence does not equal authority to promote. A confidence score of 0.95 on a vendor payment key does not mean the payment key should update. It means the evidence is of high quality — which is still not sufficient authority for auto-promotion.

```
low risk:      risk_tier_cap = 1.00
medium risk:   risk_tier_cap = 0.90
high risk:     risk_tier_cap = 0.75
critical risk: risk_tier_cap = 0.60
```

A critical-risk baseline key can never produce a confidence score above 0.60 regardless of evidence quality. This prevents a high-quality evidence package from being used to argue that a critical-risk change is safe to auto-promote.

---

## 8. Promotion Rules

Baseline promotion requires all seven conditions to be true simultaneously. Failure at any condition halts promotion.

1. All required evidence fields are present and valid
2. Confidence score meets the threshold for the risk tier
3. All five hard minimum gates pass
4. Telemetry lineage is acceptable — `lineage_independence` is true or has been manually reviewed and approved
5. A rollback snapshot of the current baseline exists before the promotion write
6. Separation-of-duties rule is satisfied
7. Baseline key is not in the permanent auto-promotion lockout class

### Auto-Promotion Requirements

Auto-promotion may only apply to low-risk, non-suppressive baseline facts. All of the following must be true simultaneously:

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

If any single condition fails, auto-promotion is blocked and the candidate enters the operator review queue.

---

## 9. Permanent Auto-Promotion Lockouts

The following baseline key classes can never auto-promote. This restriction is permanent. It cannot be overridden by confidence score, sample size, stability, source agreement, operator convenience, or time pressure.

- Money movement keys
- IAM keys
- Alert suppression keys
- Security policy keys
- Executive authority keys
- Vendor payment identity keys
- Privileged access keys
- Detector threshold keys
- Allowlist keys that reduce detection coverage

Example keys in the permanent lockout class:

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

For any key in this class:
```
operator_policy_factor = 0.0
promotion_eligible = false
auto_promotion = false
```

Operator approval is still required for manual promotion. The lockout applies to auto-promotion only. Manual promotion of these keys requires dual-operator approval with full audit trail.

---

## 10. Operator Approval and Separation of Duties

### Approval Tiers

| Risk tier | Approval required |
|---|---|
| Low | Auto-promotion if all strict gates pass; otherwise single-operator |
| Medium | Single-operator approval required |
| High | Dual-operator approval required |
| Critical | Dual-operator or admin/tenant-owner approval required |

### Separation-of-Duties Rule

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

This failure is logged as an audit event regardless of whether promotion was requested in good faith.

---

## 11. Rollback and Reversibility

Every baseline promotion creates an immutable versioned snapshot of the previous baseline state before the promotion write. If the snapshot cannot be created, the promotion does not proceed.

Rollback must be able to answer all of the following:

- What changed in the baseline?
- Why was it promoted — what evidence and confidence score supported it?
- Who or what approved it — actor IDs, approval tier, timestamps?
- When was it active — activation time and rollback time?
- What detections were affected while it was active?
- Which events need re-evaluation against the restored baseline?
- What changed after replay — did risk scores increase, decrease, or stay the same?
- Was the original promotion a false positive, false negative, operator error, or schema/process defect?

Rollback that cannot answer these questions is incomplete.

---

## 12. Rollback Blast Radius Protocol

When a bad baseline is identified and rolled back, the following protocol applies in order.

### Step 1 — Freeze the affected baseline key

```
baseline_status = frozen_pending_reconciliation
```

During this state:
- No new promotions are allowed for that key
- New evidence may be collected
- New evidence cannot mutate the baseline
- Operator review may still occur

### Step 2 — Build an impact graph

The impact graph must identify every downstream artifact that depended on the rolled-back baseline version.

Nodes:
- Baseline versions
- Evidence records
- Alerts
- Cases
- Recommendations
- Suppression decisions
- Downstream baseline candidates
- Reports

Edges:
- `used_baseline_version`
- `generated_from_evidence`
- `suppressed_by_baseline`
- `promoted_from_decision`
- `included_in_report`
- `operator_acted_on`

### Step 3 — Define the reconciliation window

```
window_start = bad_baseline_activated_at
window_end = rollback_applied_at + ingestion_delay_buffer
```

All artifacts created within this window that depended on the rolled-back baseline are in scope for reconciliation.

### Step 4 — Replay without recursive promotion

During replay:
```
baseline promotion is disabled
new baseline candidates may be flagged
new baseline candidates cannot be applied
operator approval cannot be auto-triggered from replay alone
```

Replay may update:
- Case status
- Risk score
- Alert severity
- Evidence package annotations
- Suppression correction records
- Operator review queue

Replay may not update:
- Active baseline
- Global baseline
- Tenant allowlist
- Suppression rules
- IAM assumptions
- Payment identity assumptions

### Step 5 — Assign reconciliation outcomes

Each affected artifact receives one outcome:

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

A deeper replay — replaying the consequences of replay — requires explicit dual-operator approval. Unlimited cascade depth creates reconciliation loops.

### Step 7 — Quarantine downstream baseline candidates

Any candidate created during the bad baseline window that depended on the rolled-back baseline:

```
candidate_status = quarantined_due_to_parent_rollback
```

Quarantined candidates cannot be promoted until an operator explicitly reviews and clears them, after the reconciliation window is closed.

---

## 13. Audit Schema Requirements

All audit events are append-only and tamper-evident. Audit logs must be hash-chained or use an equivalent tamper-detection mechanism. A broken chain is a contract violation.

Minimum required fields for every audit event:

| Field | Purpose |
|---|---|
| `audit_event_id` | Unique identifier for this audit record |
| `tenant_id` | Tenant scope |
| `event_time` | Timestamp of the event |
| `event_type` | Promotion, rejection, quarantine, rollback, replay, approval, separation-of-duties-failure |
| `actor_type` | Agent, operator, system |
| `actor_id` | Specific actor identifier |
| `baseline_key` | The key affected |
| `old_baseline_version` | Version before the event |
| `new_baseline_version` | Version after the event (null for rejection) |
| `evidence_ids` | All evidence records that contributed to this decision |
| `decision` | promoted, rejected, quarantined, rolled_back |
| `promotion_reason_codes` | All reason codes that contributed to or blocked promotion |
| `risk_tier` | Risk tier of the baseline key |
| `approval_policy` | Which approval tier applied |
| `request_context` | Full context of the promotion request |
| `separation_of_duties` | Whether separation-of-duties was satisfied; actor IDs evaluated |
| `rollback_status` | Whether this event is part of a rollback and which rollback ID |
| `rollback_blast_radius` | Summary of impacted artifacts if this is a rollback event |
| `audit_signature` | Hash of this record chained to the previous record |

---

## 14. Required Failure Mode Tests

The following test cases must exist and pass before implementation is considered complete. These are not unit tests for individual functions. They are system-level behavioral assertions.

1. Repeated attacker-controlled observations cannot promote a baseline — high repetition alone does not increase promotion eligibility if source reliability or lineage independence is low.
2. Two agents reading the same poisoned source do not create independent agreement — `lineage_independence = false` when both agents share an upstream telemetry source.
3. Money-movement keys cannot auto-promote — `promotion_eligible = false` for all keys in `vendor.payment_accounts.*` regardless of confidence score.
4. IAM keys cannot auto-promote — `promotion_eligible = false` for all identity provider keys in the lockout class.
5. Alert-suppression keys cannot auto-promote — `promotion_eligible = false` for `detector.alert_suppression_rule` and `detector.allowlist_entry`.
6. Requester cannot approve own baseline change — `separation_of_duties_failed` when `approver.actor_id == requester.actor_id`.
7. Same actor cannot satisfy dual approval — `separation_of_duties_failed` when `approver_1.actor_id == approver_2.actor_id`.
8. Rollback freezes the affected baseline key — `baseline_status = frozen_pending_reconciliation` immediately on rollback.
9. Replay cannot recursively promote new baseline changes — no promotion writes occur during replay.
10. Downstream baseline candidates from the bad window are quarantined — `candidate_status = quarantined_due_to_parent_rollback` for all in-window candidates.
11. Audit record includes old and new baseline versions — `old_baseline_version` and `new_baseline_version` present in every promotion and rollback audit event.
12. Audit record includes evidence IDs and approval identities — `evidence_ids`, `actor_id`, and `approval_policy` present in every audit event.
13. Rollback produces reconciliation outcomes — every artifact in the reconciliation window receives one of the defined outcome codes.

---

## Definition of Done

Research Gap 5 is concept-complete when the following are documented and ready to be turned into schemas, tests, and build tasks:

- Evidence-to-baseline promotion lifecycle — 11 ordered steps, each a defined state transition
- Evidence payload requirements — all required fields with purpose and validation rules
- Confidence score formula — non-linear model with gate multiplier and risk-tier cap
- Hard minimum gates — five gates, any failure blocks promotion
- Risk-tier caps — four tiers with defined maximum confidence values
- Promotion rules — seven conditions, all required simultaneously
- Auto-promotion requirements — strict gate set for low-risk keys only
- Permanent auto-promotion lockouts — named classes and example keys, no exceptions
- Operator approval tiers — four tiers with separation-of-duties enforcement
- Rollback and reversibility — immutable snapshot requirement and eight required answers
- Rollback blast radius protocol — seven-step protocol with cascade depth limit
- Audit schema — minimum required fields, tamper-evident requirement
- Failure mode tests — 13 system-level behavioral assertions

This concept document is complete. It does not authorize build. A design contract and §11 signature are required before Cursor may implement any part of this system.
