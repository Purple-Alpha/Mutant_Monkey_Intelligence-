# Gap 5 — Tenant Baseline Ingestion and Memory Consolidation
## Design Contract

**Document type:** Design Contract
**Status:** SIGNED — §11 authorized for build — Matt Nichol June 15th 2026
**Date:** June 16 2026
**Authority:** Matt Nichol — sole signing authority
**Source:** Gap5_Memory_Consolidation_Tenant_Baseline_Ingestion_Concept_Doc.md + Gap5_Tenant_Baseline_Ingestion_Concept_Doc.md (CONCEPT-COMPLETE June 16 2026) + Research Passes 1–4 + OQ-1 passes A/B/C + adversarial cross-checks 1–3
**Depends on:** Signed blackboard (Component 1, commit ce934f4), Vendor Baseline Store, Privacy Filter (SIGNED), Blast Radius Controller (GATED), ReconciliationAgent (GATED, commit 9cace29)

---

## §11 Signature Block

```
Signed: Matt Nichol
Name:   Matt Nichol
Date:   June 15th 2026
Authority: Sole signing authority — Mutant Monkey Inbox Shield
```

---

## §0 — Hard Boundary

This contract governs the evidence-to-baseline pipeline only. It does not authorize:

- New agents beyond those explicitly named
- Changes to any existing signed or gated contract
- Changes to ReconciliationAgent verdict logic
- Changes to MutationEngine operation
- Changes to Shadow Watcher Swarm behavior
- Any new authority structure, new automation behavior, or new approval power not described in this contract

If any of the above appear in a build, the build has exceeded contract scope.

---

## §1 — Purpose

The tenant baseline is the governed, versioned, auditable source-of-truth that detection agents, scoring systems, and ReconciliationAgent voters depend on to evaluate whether observed behavior is normal for a given tenant.

Corrupting the tenant baseline corrupts every downstream detection. An attacker who can shift the baseline can blind the detection layer without touching a single detector.

This contract defines the governed evidence-to-baseline pipeline: the schemas, confidence models, hard blockers, actor controls, temporal safeguards, and failure modes that determine when and how the system is permitted to update its memory of what is normal.

**The governing principle:** the system earns the right to update memory through evidence — not through volume, not through agent confidence, and not through automation.

---

## §2 — Scope

This contract governs:

- Evidence payload schema and required fields
- Root origin and lineage integrity model
- Ternary signal state model (true | false | unextracted)
- Confidence score formula with hard blockers and soft dampeners
- Six telemetry volatility components and ceiling breach rules
- Cumulative Volatility Index (CVI) model
- Evidence diversity model
- Sensitive key registry and locked classes with payment field fail-secure
- Actor lineage, separation of duties, and delegation rules
- Verification channel integrity
- Normalization versioning and primordial evidence root chain
- Baseline staleness and epoch handling
- Structural drift and cumulative drift with vendor-scoped adaptive lookforward watch
- Operator exception write-lock
- Baseline integrity status and poisoning determination
- Rollback, taint analysis, and downstream re-review
- Audit record schema
- UI flags and operator-facing language
- Carry-forward items CF-1 through CF-4
- Build scope, out-of-scope list, and testable invariants

---

## §3 — Non-Authorizations

Signing this contract authorizes Cursor to build the Gap 5 Tenant Baseline Ingestion pipeline only.

This contract does not:
- Amend any existing signed or gated contract
- Open any new depth gate
- Authorize CIS build
- Authorize Homeostasis Engine build
- Authorize Shadow Watcher Swarm build
- Authorize any new agent type

---

## §4 — Carry-Forward Items (CF-1 through CF-4)

### CF-1 — CVI Review Threshold Floor

```
CVI_block_threshold  = max(sqrt(n × 0.60²), 1.25)
CVI_review_threshold = max(sqrt(n × 0.50²), 1.00)
```

Floor constants `1.25` and `1.00` are calibrated constants. `1.25` represents CVI of two components at ~0.88. `1.00` represents CVI of two components at ~0.71.

### CF-2 — Financial Routing Regex Set Authority

Maintained in same signed registry as sensitive key class registry. Signed by Matt or named MSP authority. Not modifiable by agents, service accounts, or MCP tools. Covers: IBAN format, ACH routing, length-validated account numbers, wire instruction blocks, crypto wallet addresses.

### CF-3 — Canonical Vendor Entity Registry Onboarding Gate

```
tenant_onboarding_complete = false
  if canonical_vendor_entity_registry.vendor_count == 0
```

No baseline evaluation may proceed for a vendor until that vendor has a canonical entity record. Agents cannot populate the canonical registry.

### CF-4 — Soft Dampener Score Floor Directionality

The `0.85` floor is a maximum dampener value — not a minimum confidence score. Implementation must include:

```python
# soft_dampener_floor = 0.85 means confidence_score is multiplied by AT MOST 0.85
# This REDUCES confidence — it does not floor it
if any(component > 0.70 for component in active_volatility_components):
    effective_dampener = min(calculated_dampener, 0.85)
```

---

## §5 — Evidence Payload Schema

```python
class EvidencePayloadSchema(StrictModel):
    schema_version: str
    evidence_id: str
    tenant_id: str
    observed_at: datetime
    received_at: datetime
    source_component: str
    source_instance_id: str
    evidence_type: EvidenceType
    entity_type: EntityType
    entity_id: str
    candidate_baseline_key: str
    sensitive_key_class: str            # registry lookup only — not agent-assigned
    observed_state: str
    normalized_state: str
    normalization_engine_id: str
    normalization_engine_version: str
    normalization_ruleset_hash: str
    pre_normalization_hash: str
    post_normalization_hash: str
    normalization_generation: int       # > 1 requires review; > 2 blocks
    root_origin_entropy_hash: str | None
    origin_confidence: OriginConfidence
    independent_lineage_eligible: bool
    ancestral_raw_evidence_id: str | None
    is_primordial_root: bool
    confidence_inputs: dict
    confidence_score: float
    risk_tier: RiskTier
    telemetry_signature: str
    lineage_group_id: str
    lineage_independence: bool
    telemetry_lineage: list[LineageEntry]
    signal_states: dict[str, SignalState]  # true | false | unextracted
    retention_policy: str
```

### Ternary signal state

```python
class SignalState(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNEXTRACTED = "unextracted"
```

Null or unparseable signals must never default to `false`. Unextracted penalty scores:

```
payment_metadata_volatility      → 0.75
user_verification_volatility     → 0.75
sender_identity_volatility       → 0.50
infrastructure_volatility        → 0.50
artifact_structure_volatility    → 0.50
communication_pattern_volatility → 0.25
```

---

## §6 — Root Origin and Lineage Model

`root_origin_entropy_hash`: SHA-256 of stable JSON canonical input (sorted keys, UTF-8, UTC timestamps, no insignificant whitespace).

Two items sharing the same hash count as one root origin. Multi-agent processing is not multi-source evidence.

If null: `independent_lineage_eligible: false`. If unknown-origin ratio > 40%: hard blocker.

Primordial root: `is_primordial_root: true` on raw capture. All re-normalized records carry `ancestral_raw_evidence_id` to primordial root directly.

```
normalization_generation > 1 → review_required
normalization_generation > 2 → hard blocker
resolution_pending → hold, 4-hour default timeout, escalate on expiry
```

---

## §7 — Sensitive Key Registry and Locked Classes

Static, code-controlled, signed, versioned. Registry lookup is deterministic. Agents cannot assign `sensitive_key_class`.

Registry signature block must validate atomically (version + hash + signature). Any mismatch: hard blocker.

| sensitive_key_class | Auto-Promotion | Human Review |
|---|---|---|
| `money_movement` | Never | Always |
| `payment_approval_channel` | Never | Always |
| `iam` | Never | Always |
| `alert_suppression` | Never | Always |
| `security_control` | Never | Always |
| `legal_identity` | Never | Always |
| `vendor_identity` | Never | Always |
| `invoice_structure` | No | Usually |
| `communication_pattern` | Conditional | Required above threshold |
| `infrastructure_metadata` | Conditional | Required above threshold |
| `benign_metadata` | Conditional | Sometimes |
| `unregistered` | Never | Always |

### Payment field fail-secure

Unknown fields matching operator-signed financial routing regex set → `unknown_payment_destination_field_detected: true` → hard blocker. Fires regardless of document layout classification.

### Operator exception write-lock

`operator_exception_with_logged_risk` → `baseline_key_write_lock_status: locked`. Lock scope uses canonical vendor identity (not raw string). Visible on every transaction UI touchpoint. Releases only on Matt or MSP authority key-unlock record.

---

## §8 — Confidence Model

### Hard blockers (any fires → immediately blocked)

```
sensitive_key_class in locked registry
unknown_origin_ratio > 40%
evidence_diversity_class == low
actor_lineage_violation
sensitive_key_registry_signature_mismatch
telemetry_volatility_ceiling_breach == true
CVI >= cvi_block_threshold
systemic_visibility_loss == true
unknown_payment_destination_field_detected == true
verification_channel_not_historical_baseline
closed_loop_verification_channel
structural_drift_hard_trigger fired
normalization_engine == under_review or blocked
unresolvable_primordial_evidence_root
normalization_generation > 2
cumulative_structural_drift_score >= 1.00
poisoning_determination_actor_conflict
delegation_root_actor_type != human
baseline_staleness_status != active used to reduce risk
operator_exception_write_lock active
temporal_risk_decay_state == capped
source_reliability < 0.70
lineage_adjusted_agreement < 0.70
evidence_completeness < 0.90
normalization_quality < 0.90
anomaly_penalty > 0.20
```

### Confidence formula

```
base_quality =
  0.20 * evidence_completeness + 0.20 * observation_stability +
  0.15 * historical_consistency + 0.15 * sample_size_weight +
  0.10 * recency_weight + 0.20 * normalization_quality

lineage_adjusted_agreement = cross_source_agreement * independent_lineage_factor

gate_multiplier =
  source_reliability² * lineage_adjusted_agreement²
  * operator_policy_factor * (1 - anomaly_penalty)

confidence_score = clamp(base_quality * gate_multiplier, 0, risk_tier_cap)
```

`operator_policy_factor = 0.0` for locked key classes.

Risk-tier caps: low 1.00, medium 0.90, high 0.75, critical 0.60.

### Soft dampeners

```
Baseline_Confidence_Score =
  Base_Evidence_Quality
  × Source_Reliability_Gate (floor 0.10)
  × Independent_Lineage_Gate
  × Evidence_Diversity_Coefficient
  × Freshness_Gate
  × Normalization_Stability_Gate
  × Structural_Drift_Penalty
  × Conflict_Dampener (floor 0.15)
  × Sensitive_Key_Dampener
  × Telemetry_Volatility_Dampener
```

CF-4 rule: if any volatility component > 0.70, effective_dampener = min(calculated_dampener, 0.85). This reduces confidence — it does not floor it.

---

## §9 — Telemetry Volatility Model

### sender_identity_volatility

Signals: `display_name_changed`, `from_domain_changed`, `reply_to_domain_mismatch`, `reply_to_domain_new`, `spf_status_degraded`, `dkim_status_degraded`, `dmarc_status_degraded`, `lookalike_domain_detected`, `executive_impersonation_signal`, `new_sending_identity_not_in_baseline`

```
0.00  all false
0.25  1 low-weight signal
0.50  reply_to_mismatch OR lookalike OR 2+ auth degradations
0.75  from_domain_changed OR executive_impersonation OR new_identity_not_in_baseline
1.00  from_domain_changed AND payment/approval action present
      OR executive_impersonation AND payment action present
      OR lookalike AND from_domain_changed
```

### infrastructure_volatility

Signals: `sending_ip_range_changed`, `mail_provider_changed`, `mta_path_changed`, `asn_changed`, `geo_anomaly_detected`, `dns_mx_changed`, `new_infrastructure_not_in_baseline`

```
0.00  all false
0.25  geo_anomaly alone OR asn_changed alone
0.50  mail_provider_changed OR mta_path_changed OR 2+ signals
0.75  sending_ip_range_changed AND mail_provider_changed OR new_infrastructure_not_in_baseline
1.00  sending_ip_range_changed AND sender_identity >= 0.75
      OR new_infrastructure_not_in_baseline AND payment action present
```

### payment_metadata_volatility

Signals: `bank_account_changed`, `routing_number_changed`, `wire_instructions_changed`, `ach_destination_changed`, `payment_rail_changed`, `remittance_address_changed`, `crypto_wallet_changed`, `unknown_payment_destination_field_detected`, `callback_number_changed`, `approval_contact_changed`

```
0.75  payment_rail_changed alone OR remittance_address_changed alone
      OR callback_number_changed alone OR approval_contact_changed alone
      OR unknown_payment_destination_field_detected
1.00  bank_account_changed OR routing_number_changed OR wire_instructions_changed
      OR ach_destination_changed OR crypto_wallet_changed
      OR any 0.75 signal AND coincides_with_action_request == true
```

`payment_rail_changed` and `remittance_address_changed` elevate to 1.00 when coincides_with_action_request. Neither ever auto-promotes.

### communication_pattern_volatility

Signals: `send_time_anomaly`, `urgency_language_detected`, `secrecy_language_detected`, `thread_initiation_pattern_changed`, `writing_style_drift_detected`, `cadence_anomaly`, `authority_language_detected`

```
0.00  all false
0.25  send_time_anomaly OR cadence_anomaly alone
0.50  urgency_language OR writing_style_drift OR 2+ signals
0.75  urgency AND secrecy OR authority AND thread_initiation_changed
1.00  any 0.75 combination AND payment action within lookforward window
```

Communication pattern change accepted → 30-day structural_drift_penalty on payment/approval keys for that vendor.

### artifact_structure_volatility

Signals: `pdf_producer_changed`, `invoice_template_changed`, `invoice_numbering_pattern_changed`, `attachment_type_changed`, `attachment_hash_not_in_baseline`, `document_metadata_anomaly`, `remittance_block_format_changed`

```
0.00  all false
0.25  invoice_numbering_pattern_changed alone OR document_metadata_anomaly alone
0.50  pdf_producer_changed OR invoice_template_changed OR attachment_type_changed
0.75  remittance_block_format_changed OR attachment_hash_not_in_baseline AND template_changed
1.00  any 0.75 AND payment action present OR unknown_payment_field in document
```

### user_verification_volatility

Signals: `verification_channel_matches_historical_baseline`, `verification_channel_source` (enum), `verification_performed`, `verification_outcome` (enum), `multi_party_verification_performed`, `cryptographic_challenge_response_used`

```
0.00  channel matches baseline AND outcome confirmed AND (multi_party OR other components < 0.50)
0.50  performed, channel == operator_entered or external_directory
0.75  not performed OR outcome == unconfirmed
1.00  channel_source == newly_supplied_payload OR outcome failed/bypassed
      OR channel_matches_historical_baseline == false
```

Any other component >= 0.75 → `multi_party_verification_required: true`.

### Weighted mean

Default weights (operator-configurable in signed config — agents cannot modify):
```
payment_metadata: 0.30, user_verification: 0.20, sender_identity: 0.20
infrastructure: 0.15, artifact_structure: 0.10, communication_pattern: 0.05
```

Thresholds: >= 0.60 unstable/review_required; >= 0.80 blocked.

### Ceiling breach (independent of weighted mean)

Hard blocker if any:
```
any single component == 1.00
any two components >= 0.75
payment_metadata >= 0.75 AND any other >= 0.50
sender_identity >= 0.75 AND infrastructure >= 0.75
user_verification >= 0.75 AND financial/action request present
```

### CVI (CF-1)

```
CVI = sqrt(sum of active component scores squared)
CVI_block_threshold  = max(sqrt(n × 0.60²), 1.25)
CVI_review_threshold = max(sqrt(n × 0.50²), 1.00)
```

CVI >= review_threshold → unextracted signals escalate to high-risk.
CVI >= block_threshold → hard blocker.

### Unextracted signal classification

Always high-risk: payment_metadata, user_verification, sender_identity signals.
Conditional (when financial action present): infrastructure, artifact_structure signals.
Not counted: communication_pattern signals (unless financial action present).

`unextracted_high_risk_signal_count > 2` → `systemic_visibility_loss: true` → hard blocker.

---

## §10 — Evidence Diversity Model

```
Evidence_Diversity_Coefficient =
  min(1.0, (unique_root_origin_count + unique_source_system_count
    + unique_collector_family_count + unique_evidence_type_count) / denominator)
```

Denominator from signed `active_source_family_config` (Matt only, carries expiry + revocation). Default ceiling 8.

```
0.00–0.39 = low → blocked
0.40–0.69 = medium
0.70–1.00 = high
```

Only `independent_lineage_eligible: true` evidence increases diversity.

---

## §11 — Actor Lineage, Separation of Duties, and Delegation

Permitted for all actor types: observe, collect, normalize, score, request, recommend.
Human actors only: reviewed, approved, rejected (final), rolled_back (final), clear_poisoning.
clear_poisoning additionally requires: `authority_scope: approve_high_risk`.

Service accounts, MCP tools, external systems, agents: no approval authority.

Separation of duties:
```
requested_by_actor_id != approver_actor_id
approver not in actor_lineage_chain as: observed | collected | normalized | scored | requested
```

Delegation: valid only when `delegation_root_actor_type == human`. Agent-to-agent delegation: hard blocker.

**OQ-2 locked:** Poisoning clearance requires `actor_type: human` AND `authority_scope: approve_high_risk`. No exceptions. Original approver cannot clear their own candidate.

---

## §12 — Verification Channel Integrity

Channel must be trusted before the request arrived. Hard blockers:
```
verification_channel_matches_historical_baseline == false
  → [verification_channel_not_historical_baseline], user_verification_volatility: 1.00

verification_channel_source == newly_supplied_payload
  → [closed_loop_verification_channel], integrity_status: attacker_supplied
```

Any component >= 0.75 → `multi_party_verification_required: true`.

---

## §13 — Normalization Versioning and Primordial Root

Every evidence item bound to pinned engine + version + ruleset hash. Re-normalization produces new immutable record — originals never overwritten. Ancestral_raw_evidence_id must point to primordial root directly.

```
normalization_generation > 1 → review_required
normalization_generation > 2 → hard blocker
```

Unresolvable (permanent) → block. Resolution_pending (temporary) → hold, 4-hour default, escalate on timeout.

---

## §14 — Baseline Staleness

| Class | Threshold | Behavior |
|---|---|---|
| money_movement, payment_approval_channel, iam, security_control | 0 | Never trust by inactivity |
| vendor_identity, invoice_structure | 7,776,000s | Stale after 90 days |
| infrastructure_metadata, communication_pattern | 2,592,000s | Stale after 30 days |
| benign_metadata | 15,552,000s | Stale after 180 days |

Stale baselines may increase suspicion. May not reduce risk without fresh evidence.

---

## §15 — Structural Drift and Cumulative Drift

Compares against `last_locked_baseline_configuration`. Fluid candidates cannot be comparison anchors.

Cumulative drift window defaults:
```
locked classes                         → no window; any drift = immediate review
vendor_identity, invoice_structure     → 7,776,000s (90 days)
communication_pattern, infrastructure  → 2,592,000s (30 days)
benign_metadata                        → 15,552,000s (180 days)
```

```
>= 0.70 → review_required
>= 1.00 → hard blocker
```

Hard triggers (always block):
```
new payment instruction block
new remittance address
new callback number
new approval contact
new vendor domain + payment request
reply-to mismatch + financial action
```

Severity: single | compound | critical.

---

## §16 — Vendor-Scoped Adaptive Lookforward Watch

`coincides_with_action_request`: true if financial/security action occurs in same session OR within 30-day vendor-scoped lookforward window for that specific baseline key. General communication does not trigger.

Watch: 30-day initial window. Renewal trigger: events touching modified baseline key OR dependent key classes. General vendor communication does not renew. Maximum: 7,776,000s (90 days).

Capped state: watch hits maximum without operator sign-off → `temporal_risk_decay_state: capped` (not expired). While capped: mandatory human review on all transactions involving key. `expired` only with operator sign-off.

---

## §17 — Baseline Integrity Status and Poisoning

```
trusted | under_review | suspected_poisoned | confirmed_poisoned | rolled_back
```

Automated systems may set `suspected_poisoned`. `confirmed_poisoned` requires human with `approve_high_risk` not in original candidate lifecycle. See §11 OQ-2.

---

## §18 — Rollback, Taint Analysis, Downstream Re-Review

Lookback minimums: locked classes 30 days, review-required 7 days, low-risk 24 hours.
Dynamic lookforward: `max(minimum_lookforward_seconds, max_downstream_execution_delay_seconds)`. Minimum 1 hour.

Pending states requiring inclusion: pending | scheduled | queued | awaiting_approval | awaiting_payment | awaiting_export | awaiting_sync | unexecuted.

Tainted detections: `{baseline_taint_status: tainted, re_review_required: true}`. UI must show active warning until explicitly cleared.

Blast radius protocol:
```
1. Freeze affected baseline key
2. Build impact graph
3. Define reconciliation window
4. Replay without recursive promotion (no baseline writes during replay)
5. Assign reconciliation outcomes
6. Limit cascade depth to 1 (deeper requires dual-operator approval)
7. Quarantine downstream candidates from bad baseline window
```

---

## §19 — Audit Record Schema

Append-only, tamper-evident, hash-chained. Broken chain = contract violation.

Required fields: `audit_event_id`, `tenant_id`, `event_time`, `event_type`, `actor_type`, `actor_id`, `baseline_key`, `old_baseline_version`, `new_baseline_version`, `evidence_ids`, `decision`, `promotion_reason_codes`, `hard_blockers`, `risk_tier`, `approval_policy`, `request_context`, `separation_of_duties`, `rollback_status`, `rollback_blast_radius`, `normalization_engine_id`, `normalization_engine_version`, `normalization_ruleset_hash`, `sensitive_key_registry_signature_block` (snapshot), `cvi_block_threshold` (at evaluation time), `actor_lineage_chain` (snapshot), `audit_signature` (hash chained to previous).

No chain-of-thought in audit records. All references must be to committed, resolvable artifacts. Legacy validation code preserved when normalization engine changes.

---

## §20 — UI Flags

| Flag | Condition |
|---|---|
| `LOW_EVIDENCE_DIVERSITY` | diversity_coefficient < 0.40 |
| `DO_NOT_TREAT_AS_INDEPENDENT_CONFIRMATION` | diversity_coefficient < 0.40 |
| `SINGLE_ROOT_ORIGIN` | unique_root_origin_count < 2 |
| `MULTI_AGENT_REVIEW_DOES_NOT_EQUAL_MULTI_SOURCE_EVIDENCE` | unique_root_origin_count < 2 |
| `HIGH_UNKNOWN_ORIGIN_RATIO` | unknown_origin_ratio > 40% |
| `SYSTEMIC_VISIBILITY_LOSS` | unextracted_high_risk_signal_count > 2 |
| `UNLISTED_TELEMETRY_SOURCE` | source not in signed config |
| `SOURCE_FAMILY_NOT_DENOMINATOR_ELIGIBLE` | source not in signed config |
| `BASELINE_TAINTED` | baseline_taint_status == tainted |
| `RE_REVIEW_REQUIRED` | re_review_required == true |
| `CUMULATIVE_DRIFT_WARNING` | cumulative_structural_drift_score >= 0.70 |
| `STRUCTURAL_DRIFT_CRITICAL` | structural_drift_severity_class == critical |
| `VERIFICATION_CHANNEL_ATTACKER_SUPPLIED` | channel_source == newly_supplied_payload |
| `MULTI_PARTY_VERIFICATION_REQUIRED` | any volatility component >= 0.75 |
| `STALE_BASELINE_CANNOT_REDUCE_RISK` | stale baseline used to reduce risk |
| `POISONING_DETERMINATION_CONFLICT` | actor_lineage_conflict == true |
| `BASELINE_KEY_WRITE_LOCKED` | write_lock_status == locked |
| `TEMPORAL_WATCH_CAPPED` | temporal_risk_decay_state == capped |
| `UNKNOWN_PAYMENT_DESTINATION_DETECTED` | unknown_payment_destination_field_detected == true |

All UI language plain English. No schema field names in operator-facing surfaces.

---

## §21 — Testable Invariants

| ID | Invariant | Test |
|---|---|---|
| TBI-INV-01 | Evidence theater blocked | 50 email_header items → diversity blocks |
| TBI-INV-02 | Lineage collusion collapses | 3 collectors, same root hash → counted as one |
| TBI-INV-03 | Agents cannot self-assign class | Agent declares money_movement → registry overrides |
| TBI-INV-04 | Agent-to-agent delegation blocked | Agent_A → Agent_B approval → hard blocker |
| TBI-INV-05 | Rollback marks all influenced detections | Poisoned baseline rolled back → all marked tainted |
| TBI-INV-06 | Re-normalization does not overwrite | Engine updated → original immutable, new record created |
| TBI-INV-07 | Stale baseline cannot reduce risk | Old retired hash → staleness fires |
| TBI-INV-08 | Communication drift triggers structural penalty | Pattern drift accepted → payment change hits penalty |
| TBI-INV-09 | Closed-loop verification blocked | New callback in payload used → attacker_supplied fires |
| TBI-INV-10 | Score zero-flattening triggers volatility alert | Conflicting low-reliability evidence → volatility elevated |
| TBI-INV-11 | Primordial root laundering blocked | Re-normalized twice submitted as root → generation > 2 fires |
| TBI-INV-12 | Original approver cannot clear poisoning | Original approver attempts → actor_lineage_conflict fires |
| TBI-INV-13 | Pending artifacts in rollback | Scheduled invoice in taint window → included |
| TBI-INV-14 | Unlisted source cannot alter denominator | Unlisted source → denominator unchanged, flag shown |
| TBI-INV-15 | Registry mismatch blocks atomically | Old registry evaluated → signature block mismatch fires |
| TBI-INV-16 | Null signals take penalty | Signal null → unextracted with penalty, not false |
| TBI-INV-17 | Temporal arbitrage blocked | Day 0 change, day 31 execution → capped state blocks |
| TBI-INV-18 | Sub-threshold squatting triggers CVI | All six at 0.74 → CVI threshold fires |
| TBI-INV-19 | Unknown payment field triggers fail-secure | IBAN in non-payment region → regex override fires |
| TBI-INV-20 | Write-lock string variation blocked | Vendor name permutation → canonical resolver catches |
| TBI-INV-21 | Component collapse triggers visibility loss | Full artifact block unextracted → systemic_visibility_loss fires |
| TBI-INV-22 | Watch cap requires sign-off | 90-day watch expires without sign-off → capped, not expired |
| TBI-INV-23 | Requester cannot approve own change | approver == requester → separation_of_duties_failed |
| TBI-INV-24 | Rollback snapshot exists before write | Snapshot fails → promotion does not proceed |
| TBI-INV-25 | CVI_review_threshold floor (CF-1) | n=2 → CVI_review_threshold >= 1.00 |
| TBI-INV-26 | Dampener floor reduces not floors (CF-4) | Component > 0.70 → dampener caps at 0.85, reduces score |
| TBI-INV-27 | Canonical registry gates onboarding (CF-3) | Zero vendor records → baseline evaluation blocked |
| TBI-INV-28 | Financial regex set operator-signed (CF-2) | Agent modifies regex → blocked, only signed registry accepted |

---

## §22 — Out of Scope

Homeostasis Engine logic, CIS escalation logic, Cortex/Immune Interface, new agent types, new authority structures, automatic Safe-Stop recovery, verdict production, cross-tenant evidence aggregation outside ReconciliationAgent, runtime self-modification of thresholds or weights, auto-clearing of write-locks, promotion of locked key classes without dual-operator approval.

---

## §23 — Non-Negotiable Rules

1. Agents may observe, collect, normalize, score, request, or recommend. Agents may not approve, reject as final authority, clear poisoning, or finalize rollback.
2. Service accounts and MCP tools may not approve baseline changes.
3. Matt or named MSP authority must sign all sensitive authority-changing configuration.
4. No sensitive key may be auto-promoted.
5. Unknown-origin evidence may not create independent confirmation.
6. Multi-agent review is not multi-source evidence.
7. Verification must use historically trusted channels.
8. Structural drift compares against the last locked baseline.
9. Rollback is incomplete until downstream detections and pending artifacts are marked.
10. No audit record may depend on private chain-of-thought.
11. Weighted volatility cannot launder component-level ceiling breaches.
12. Registry version, hash, and signature must validate atomically.
13. Re-normalized evidence must resolve to a primordial raw evidence root.
14. Poisoning clearance requires `actor_type: human` AND `authority_scope: approve_high_risk`. No exceptions.
15. Stale baselines may increase suspicion. They may not reduce risk without fresh evidence.
16. Unextracted signals take class-specific penalty scores — never default to false.
17. Watch at maximum without operator sign-off is `capped`, not `expired`.
18. Write-locked keys are visible on every transaction touchpoint.
19. Write-lock scope uses canonical normalized vendor identity, not raw strings.
20. Single-factor verification insufficient when any volatility component >= 0.75.
21. Payment rail and remittance address changes that coincide with action requests elevate to hard-block.
22. Canonical vendor entity registry must be seeded at tenant onboarding. Agents cannot populate it.

---

## §24 — Definition of Done

1. All 28 testable invariants pass
2. `complete_gate.py` reports 0/0 blocking
3. Agent Health Score >= 85
4. CF-1 through CF-4 documented in code with required comment blocks
5. All six volatility components implemented with ternary state handling
6. Audit record hash chain verified by separate audit verification test
7. Rollback blast radius protocol completes without recursive promotion in integration test
8. Matt reviews output and signs closure
