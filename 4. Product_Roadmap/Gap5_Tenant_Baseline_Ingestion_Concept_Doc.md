# Tenant Baseline Ingestion and Memory Consolidation — Concept Document

## Mutant Monkey Inbox Shield

**Document type:** Concept Document
**Status:** CONCEPT-COMPLETE — OQ-1 RESOLVED — OQ-2 LOCKED — contract session authorized
**Date:** June 16 2026
**Revised:** June 16 2026 (OQ-1 and OQ-2 resolved, research passes 1–4 and OQ-1A/B/C integrated)
**Authority:** Matt Nichol — sole signing authority
**Source:** Research Passes 1–4, adversarial cross-checks 1–3, OQ-1 passes A/B/C
**Depends on:** Signed blackboard (Component 1), Vendor Baseline Store, Privacy Filter, Blast Radius Controller, ReconciliationAgent

---

## Document Status Key

```
CONCEPT-READY         = described, architecturally sound, no open blockers
CONCEPT-COMPLETE      = all open questions resolved, ready for contract session
SCHEMA OPEN           = schema defined but one or more constraints need resolution
BUILD-BLOCKING        = cannot be built until named question is resolved
OPERATOR APPROVAL     = Matt must sign before implementation begins
```

---

## §1 — Purpose

Mutant Monkey Inbox Shield builds detection on what is normal. Normal is not static. Vendors change banks. Invoices evolve. Communication patterns shift. The system must learn — but learning is the highest-risk operation in the pipeline.

A poisoned memory update is worse than a missed detection. A missed detection fails once. A poisoned baseline corrupts every future detection against that vendor until the baseline is corrected.

This concept document defines the governed evidence-to-baseline pipeline — the set of rules, schemas, confidence models, actor controls, and failure modes that determine when and how the system is permitted to update its memory of what is normal.

The governing principle is: **the system earns the right to update memory through evidence, not through volume, not through agent confidence, and not through automation.**

---

## §2 — Scope

This document covers:

- Candidate baseline change lifecycle from evidence collection to promotion or rejection
- Evidence quality, lineage, diversity, and origin integrity
- Confidence scoring model including hard blockers and soft dampeners
- Telemetry volatility model including all six component definitions
- Sensitive key classification and locked registry
- Actor lineage, separation of duties, and delegation rules
- Verification channel integrity
- Normalization versioning and primordial evidence root chain
- Baseline staleness and epoch handling
- Structural drift detection including cumulative drift
- Temporal arbitrage prevention via vendor-scoped adaptive lookforward watch
- Baseline integrity status and poisoning determination
- Rollback, taint analysis, and downstream re-review
- Audit record requirements
- UI flags and operator-facing language
- Build readiness gate

---

## §3 — Non-Goals

This document does not cover:

- Real-time email detection logic (governed by existing signed agent contracts)
- ReconciliationAgent verdict logic
- MutationEngine operation
- Shadow Watcher Swarm attacker cost doctrine
- Honeypot or deception layer
- Builder Radar market intelligence system
- Any new agent type, new authority structure, or new automation behavior not described in this document

---

## §4 — Threat Model

### Assets

```
Raw vendor payment instructions
Tenant baseline memory store
Candidate baseline change records
Evidence items and audit records
Actor lineage records
Normalization engine versions
Primordial evidence root store
Operator approval authority
Canonical vendor entity registry
```

### Trust Boundaries

```
Email ingress boundary          Raw email enters; stops at Q-class
Evidence collection boundary    Agents collect; cannot approve
Baseline update boundary        No update without evidence threshold + human sign-off on locked keys
Tenant boundary                 Cross-tenant evidence access is forbidden
Operator boundary               Matt or named MSP authority controls locked configuration
Audit boundary                  Audit records are immutable after creation
Registry boundary               Sensitive key registry signed by Matt only; agents cannot modify
```

### Attacker Goals Against the Baseline System

```
Poison vendor payment instructions to redirect funds
Suppress anomaly detection by pre-normalizing attacker behavior
Launder fake cross-source agreement to fake independent confirmation
Replay old trusted baseline states to redirect funds to retired accounts
Gradually drift communication patterns to desensitize detection before payment attack
Compromise verification channel to close the loop on fake out-of-band verification
Inject high-volume single-type evidence to create review theater
Use agent delegation chains to self-approve baseline changes
Freeze legitimate baseline updates by sustaining low-level noise
Erase audit trail by exploiting non-deterministic normalization hashes
Stage baseline changes in one session, execute payment fraud in a later session
Manipulate write-lock scope via vendor identity string permutations
Inject unregistered payment fields disguised as metadata
Exhaust operator capacity to force exception clearance of blocked candidates
Collapse component visibility via coordinated unextracted signal injection
```

### Failure Modes

```
False promotion           Attacker-controlled baseline accepted as trusted memory
Denial of update          Legitimate vendor change permanently blocked by noise injection
Audit failure             Normalization version drift makes historical hashes unverifiable
Rollback gap              Detections made during poisoned window remain marked safe
Verification theater      Attacker-supplied channel accepted as out-of-band verification
Evidence theater          High-volume single-type evidence accepted as diverse confirmation
Actor laundering          Agent delegation chain bypasses separation of duties
Replay attack             Retired trusted baseline state re-activated by attacker
Cumulative drift          Gradual structural change escapes single-delta detection
Temporal arbitrage        Baseline change and payment execution split across session boundary
Sub-threshold squatting   Coordinated multi-vector attack stays below all individual thresholds
Operator fatigue bypass   Exception clearance used to pass a blocked high-risk candidate
Visibility collapse       Coordinated unextracted signals prevent meaningful scoring
Write-lock circumvention  Vendor identity string variation bypasses lock scope lookup
```

---

## §5 — Evidence-to-Baseline Lifecycle

```
Evidence Collection
     │
     ▼
Root Origin Assignment
(root_origin_entropy_hash per evidence item)
     │
     ▼
Normalization
(versioned, pinned, immutable primordial root preserved)
     │
     ▼
Candidate Assembly
(affected_baseline_key, sensitive_key_class from registry only)
     │
     ▼
Ternary Signal State Evaluation
(true | false | unextracted — unextracted takes class-specific penalty score)
     │
     ▼
Hard Blocker Evaluation
(any blocker fires → blocked, no further scoring)
     │
     ▼
Cumulative Volatility Index Evaluation
(CVI = Euclidean norm of all components; threshold = max(sqrt(n×0.60²), 1.25))
     │
     ▼
Soft Dampener Scoring
(baseline_confidence_score calculated with non-linear floor)
     │
     ▼
Telemetry Volatility Evaluation
(six-component model; ceiling breach check independent of weighted mean)
     │
     ▼
Evidence Diversity Evaluation
(diversity coefficient from signed source family config; UI flags if low)
     │
     ▼
Structural Drift Evaluation
(cumulative drift against last locked baseline; vendor-scoped adaptive lookforward)
     │
     ▼
Actor Lineage Validation
(separation of duties; delegation root must be human)
     │
     ▼
Promotion Eligibility Decision
(auto_ineligible | review_required | eligible_after_review)
     │
     ▼
Human Review (always required for locked key classes)
     │
     ▼
Approval or Rejection
(Matt or named MSP authority for locked classes)
     │
     ▼
Baseline Update + Taint Window Registration
+ Vendor-Scoped Lookforward Watch Initiated
     │
     ▼
Downstream Detection Tagging
(affected_downstream_detection_ids populated)
```

---

## §6 — Candidate Baseline Change Schema

**Status: CONCEPT-COMPLETE**

Key fields by category. Full consolidated schema in Research Pass 2 and Pass 4.

### Identity fields
```
tenant_id
candidate_baseline_change_id
created_at
affected_baseline_key
affected_entity_type
sensitive_key_class               (registry lookup only — agents cannot self-assign)
```

### Baseline state fields
```
current_baseline_value_hash
candidate_value_hash
baseline_epoch_timestamp
last_confirmed_observed_timestamp
inactivity_threshold_seconds
baseline_staleness_status         (active | stale | expired | dormant)
last_locked_baseline_id
last_locked_baseline_hash
last_locked_baseline_signed_by_actor_id
last_locked_baseline_timestamp
```

### Normalization fields
```
normalization_engine_id
normalization_engine_version      (semver — pinned at evaluation time)
normalization_ruleset_hash
normalization_time
```

### Telemetry volatility fields
```
sender_identity_volatility
infrastructure_volatility
payment_metadata_volatility
communication_pattern_volatility
artifact_structure_volatility
user_verification_volatility
telemetry_volatility_score        (weighted mean of six components)
telemetry_volatility_ceiling_breach
telemetry_volatility_ceiling_reasons
cumulative_volatility_index       (Euclidean norm)
cvi_block_threshold               (max(sqrt(n×0.60²), 1.25))
cvi_review_threshold              (max(sqrt(n×0.50²), 1.00))
unextracted_high_risk_signal_count
systemic_visibility_loss          (bool — fires hard blocker if count > 2)
```

### Scoring output fields
```
baseline_confidence_score
soft_dampener_score
soft_dampener_floor_applied       (bool — true if any component > 0.70 triggered floor)
evidence_diversity_coefficient
evidence_diversity_class
structural_drift_penalty
cumulative_structural_drift_score
cumulative_structural_drift_window_seconds
structural_drift_severity_class   (single | compound | critical)
hard_blockers                     (array — any entry blocks promotion)
promotion_confidence_class        (blocked | unstable | review_required | eligible_after_review)
promotion_eligibility             (auto_ineligible | review_required | eligible_after_review)
auto_promotion_allowed
review_required
approval_status
```

### Temporal arbitrage watch fields
```
vendor_scoped_lookforward_watch
  watch_id
  vendor_canonical_id
  affected_baseline_key
  watch_start
  watch_current_end
  watch_renewal_count
  maximum_total_watch_seconds     (default 7,776,000 = 90 days)
  temporal_risk_decay_state       (active | renewed | capped | cleared | expired_with_operator_signoff)
  watch_renewal_trigger_scope     (events_touching_modified_baseline_key | events_touching_dependent_key_classes)
  last_renewal_event_id
  last_renewal_time
  operator_signoff_required_at_cap
```

### Write-lock fields
```
baseline_key_write_lock_status    (unlocked | locked | locked_pending_release)
baseline_key_write_lock_scope
  tenant_id
  vendor_canonical_id             (normalized — not raw string)
  affected_baseline_key
baseline_key_write_lock_triggered_by    (operator_exception_with_logged_risk | confirmed_poisoned)
baseline_key_write_lock_release_authority  (matt_nichol | designated_msp_authority)
baseline_key_write_lock_ui_visible  (bool — must be true; visible on all transaction touchpoints)
```

### Registry signature block
```
sensitive_key_registry_signature_block
  registry_id
  registry_version
  registry_hash
  registry_signature
  registry_effective_timestamp
  registry_expiry_timestamp
  registry_revocation_status
  validated_at
  validated_by_actor_id
```

### Actor fields
```
actor_lineage_chain               (array — full chain from observe to approve)
requested_by_actor_id
approver_actor_id
```

### Taint and rollback fields
```
taint_analysis_window
  window_start
  window_end
  lookback_seconds
  dynamic_lookforward_seconds
  max_downstream_execution_delay_seconds
  reason
affected_downstream_detection_ids
pending_downstream_artifact_ids
rollback_pointer
baseline_integrity_status         (trusted | under_review | suspected_poisoned | confirmed_poisoned | rolled_back)
poisoning_determination_record
  determined_by_actor_id
  determination_time
  evidence_reference
  determination_method            (automated | operator | external_report)
  independent_reviewer_actor_type (must be human)
  independent_reviewer_authority_scope (must be approve_high_risk)
poisoning_determination_independent_reviewer_required  (always true for confirmed_poisoned)
poisoning_determination_actor_lineage_conflict
```

### Verification channel fields
```
verification_channel_matches_historical_baseline
verification_channel_source       (historical_baseline | newly_supplied_payload | operator_entered | external_directory | unknown)
verification_channel_id_used
verification_channel_integrity_status  (trusted | changed | unknown | attacker_supplied)
historical_trusted_verification_channel_ids
verification_credential_class     (standard | multi_party | cryptographic_challenge_response)
multi_party_verification_required (true when any component >= 0.75)
```

### Audit fields
```
audit_record_id
ui_flags
```

---

## §7 — Root Origin and Telemetry Lineage Model

**Status: CONCEPT-COMPLETE**

Every evidence item must carry a `root_origin_entropy_hash` representing the earliest recoverable origin before any agent processing.

### Hashing spec

Canonical input object serialized as stable JSON (sorted keys, UTF-8, no insignificant whitespace, timestamps normalized to UTC), SHA-256, lowercase hex.

### Rules

Two evidence items sharing the same `root_origin_entropy_hash` count as one root origin regardless of how many agents processed them. Multi-agent processing is not multi-source evidence.

If root origin cannot be recovered: `independent_lineage_eligible: false`. Unknown-origin evidence may appear in the UI as context but must not increase independent lineage count or diversity score.

If more than 40% of evidence items have `independent_lineage_eligible: false`: `promotion_confidence_class: blocked`, UI flag `HIGH_UNKNOWN_ORIGIN_RATIO`.

---

## §8 — Sensitive Key Registry and Locked Classes

**Status: CONCEPT-COMPLETE**

The sensitive key registry is static, code-controlled, signed, and versioned. Agents cannot assign `sensitive_key_class`. The engine performs registry lookup deterministically.

### Registry by class

| sensitive_key_class | Examples | Auto-Promotion | Human Review |
|---|---|---|---|
| `money_movement` | bank account, routing number, wire instructions, ACH/EFT, crypto wallet, payment rail | Never | Always |
| `payment_approval_channel` | callback number, approval email, finance approver identity | Never | Always |
| `iam` | user identity, role, privilege, MFA state, SSO mapping | Never | Always |
| `alert_suppression` | allowlist, spam bypass, fraud bypass, domain trust override | Never | Always |
| `security_control` | MFA enforcement, DMARC enforcement, SPF/DKIM override | Never | Always |
| `legal_identity` | vendor legal name, tax ID, business registration | Never | Always |
| `vendor_identity` | primary vendor domain, sender identity, executive identity | Never | Always |
| `invoice_structure` | invoice template, PDF producer, invoice numbering | No | Usually |
| `communication_pattern` | writing style, cadence, send time, thread behavior | Conditional | Required above threshold |
| `infrastructure_metadata` | sending IP range, mail provider, MTA path | Conditional | Required above threshold |
| `benign_metadata` | formatting preference, newsletter cadence, non-financial alias | Conditional | Sometimes |
| `unregistered` | any key not in registry | Never | Always |

### Payment field fail-secure rule

Unknown fields are not evaluated as metadata by default. If any unknown or unregistered field matches the financial routing regex set (IBAN format, ACH routing structures, length-validated account number patterns), `unknown_payment_destination_field_detected: true` fires regardless of document layout classification. The regex set is operator-signed and maintained in the same signed registry as the sensitive key class registry. Agents cannot modify the regex set.

### Registry versioning and signing

Registry stored as atomic signed object. Version, hash, and signature must validate atomically. Registry must carry `registry_expiry_timestamp` and `registry_revocation_status`. Expired or revoked registry triggers `review_required`. Only Matt or named MSP authority may sign.

---

## §9 — Confidence Model: Hard Blockers and Soft Dampeners

**Status: CONCEPT-COMPLETE**

### Hard blockers (any fires → immediately blocked)

```
sensitive_key_class in locked registry
unknown_origin_ratio > 40%
evidence_diversity_class == low
actor_lineage_violation
sensitive_key_registry_signature_mismatch
telemetry_volatility_ceiling_breach == true
cumulative_volatility_index >= cvi_block_threshold
systemic_visibility_loss == true (unextracted_high_risk_signal_count > 2)
unknown_payment_destination_field_detected == true
verification_channel_not_historical_baseline
closed_loop_verification_channel
structural_drift_hard_trigger fired
normalization_engine under_review or blocked
unresolvable_primordial_evidence_root
normalization_generation > 2
cumulative_structural_drift_score >= 1.00
poisoning_determination_actor_conflict
delegation_root_actor_type != human
baseline_staleness_status != active used to reduce risk
operator_exception_write_lock active on affected_baseline_key
temporal_risk_decay_state == capped (requires operator sign-off before any transaction)
```

### Soft dampeners with non-linear floor

Applied multiplicatively after all hard blockers pass. Each dampener has a defined minimum floor. A single dampener cannot zero out the score alone.

```
Baseline_Confidence_Score =
  Base_Evidence_Quality
  × Source_Reliability_Gate (floored at 0.10)
  × Independent_Lineage_Gate
  × Evidence_Diversity_Coefficient
  × Freshness_Gate
  × Normalization_Stability_Gate
  × Structural_Drift_Penalty
  × Conflict_Dampener (floored at 0.15)
  × Sensitive_Key_Dampener
  × Telemetry_Volatility_Dampener
```

Non-linear floor rule: if any individual volatility component exceeds `0.70`, `Soft_Dampener_Score` pins to a minimum value of `0.85`. This prevents a single clean signal from diluting severe risk across other vectors. The `0.85` value is a minimum dampener floor — it means the confidence score is multiplied by at most `0.85`, not that the score itself is `0.85`.

---

## §10 — Telemetry Volatility Model

**Status: CONCEPT-COMPLETE — OQ-1 RESOLVED**

The telemetry volatility model measures whether the observed evidence environment is too unstable to safely update memory.

### Ternary signal state model

All input signals use a strict ternary state: `true | false | unextracted`. A null or unparseable signal must never default to `false`. If a signal is unextracted, it takes a class-specific penalty score:

```
payment_metadata_volatility signals      → unextracted penalty: 0.75
user_verification_volatility signals     → unextracted penalty: 0.75
sender_identity_volatility signals       → unextracted penalty: 0.50
infrastructure_volatility signals        → unextracted penalty: 0.50
artifact_structure_volatility signals    → unextracted penalty: 0.50
communication_pattern_volatility signals → unextracted penalty: 0.25
```

If `CVI >= CVI_review_threshold`, all unextracted signals across all active components automatically escalate to high-risk classification regardless of their individual component category.

### High-risk unextracted signal count

`unextracted_high_risk_signal_count` tracks signals classified as high-risk from:
- Any signal from `payment_metadata_volatility`, `user_verification_volatility`, `sender_identity_volatility` — always high-risk
- Signals from `infrastructure_volatility` and `artifact_structure_volatility` — high-risk when financial action request is present
- Signals from `communication_pattern_volatility` — not counted as high-risk unless financial action request is present

If `unextracted_high_risk_signal_count > 2`: `systemic_visibility_loss: true`, immediate hard block.

---

### Component 1 — sender_identity_volatility

**Purpose:** Detect changes to who the sender appears to be — display identity, domain, authentication posture.

**Input signals:**

| Signal | Type | Description |
|---|---|---|
| `display_name_changed` | bool | Sender display name differs from baseline |
| `from_domain_changed` | bool | From domain differs from baseline |
| `reply_to_domain_mismatch` | bool | Reply-To domain differs from From domain |
| `reply_to_domain_new` | bool | Reply-To domain not in historical baseline |
| `spf_status_degraded` | bool | SPF result worsened vs baseline (pass → fail/softfail) |
| `dkim_status_degraded` | bool | DKIM result worsened vs baseline |
| `dmarc_status_degraded` | bool | DMARC result worsened vs baseline |
| `lookalike_domain_detected` | bool | From or Reply-To domain matches lookalike registry |
| `executive_impersonation_signal` | bool | Display name matches known executive, domain does not |
| `new_sending_identity_not_in_baseline` | bool | Sender combination never seen for this vendor |

**Scoring boundaries:**

```
0.00  All signals false, matches baseline exactly
0.25  1 low-weight signal (display_name_changed alone, or spf_degraded alone)
0.50  Any combination: reply_to_mismatch OR lookalike_domain OR 2+ auth degradations
0.75  from_domain_changed OR executive_impersonation OR new_sending_identity_not_in_baseline
1.00  from_domain_changed AND payment/approval action present
      OR executive_impersonation AND payment/approval action present
      OR lookalike_domain AND from_domain_changed
```

**Hard blocker trigger:** score == 1.00 or combined with ceiling breach rule.

**Coincides-with rule:** `change_coincides_with_action_request` is true if a financial or security action request occurs within the same session OR within the vendor-scoped 30-day adaptive lookforward window of any baseline state modification for that vendor.

---

### Component 2 — infrastructure_volatility

**Purpose:** Detect changes to the sending infrastructure — mail path, IP ranges, hosting, DNS.

**Input signals:**

| Signal | Type | Description |
|---|---|---|
| `sending_ip_range_changed` | bool | Sending IP outside known baseline range |
| `mail_provider_changed` | bool | MTA or ESP changed vs baseline |
| `mta_path_changed` | bool | Received chain hop pattern changed |
| `asn_changed` | bool | Autonomous system number differs from baseline |
| `geo_anomaly_detected` | bool | Origin geo outside baseline pattern |
| `dns_mx_changed` | bool | MX records differ from baseline |
| `new_infrastructure_not_in_baseline` | bool | Infrastructure combination never seen for vendor |

**Scoring boundaries:**

```
0.00  All signals false
0.25  1 low-weight signal (geo_anomaly alone or asn_changed alone)
0.50  mail_provider_changed OR mta_path_changed OR 2+ signals active
0.75  sending_ip_range_changed AND mail_provider_changed
      OR new_infrastructure_not_in_baseline
1.00  sending_ip_range_changed AND sender_identity_volatility >= 0.75
      OR new_infrastructure_not_in_baseline AND payment action present
```

**Hard blocker trigger:** score == 1.00 or ceiling breach with sender_identity_volatility >= 0.75.

---

### Component 3 — payment_metadata_volatility

**Purpose:** Detect any change to payment routing, destination, or approval channel — the highest-risk surface.

**Input signals:**

| Signal | Type | Description |
|---|---|---|
| `bank_account_changed` | bool | Bank account number changed vs baseline |
| `routing_number_changed` | bool | Routing number changed vs baseline |
| `wire_instructions_changed` | bool | Wire instruction block changed |
| `ach_destination_changed` | bool | ACH destination changed |
| `payment_rail_changed` | bool | Payment mechanism changed (ACH → wire, etc.) |
| `remittance_address_changed` | bool | Remittance address block changed |
| `crypto_wallet_changed` | bool | Crypto wallet address changed |
| `unknown_payment_destination_field_detected` | bool | Unregistered field matches financial routing regex |
| `callback_number_changed` | bool | Callback verification number changed |
| `approval_contact_changed` | bool | Named approval contact changed |

**Scoring boundaries:**

```
0.00  All signals false
0.75  payment_rail_changed alone
      OR remittance_address_changed alone
      OR callback_number_changed alone
      OR approval_contact_changed alone
      OR unknown_payment_destination_field_detected
1.00  bank_account_changed
      OR routing_number_changed
      OR wire_instructions_changed
      OR ach_destination_changed
      OR crypto_wallet_changed
      OR any 0.75 signal coincides_with_action_request
```

Note: `payment_rail_changed` and `remittance_address_changed` are elevated to `1.00` when coincides_with_action_request is true. They are never auto-promoted at any score.

**Hard blocker trigger:** score >= 0.75 always requires human review. Score == 1.00 always blocks.

---

### Component 4 — communication_pattern_volatility

**Purpose:** Detect changes to how the vendor communicates — timing, tone, thread behavior, urgency. Low-risk in isolation; elevated in combination with financial signals.

**Input signals:**

| Signal | Type | Description |
|---|---|---|
| `send_time_anomaly` | bool | Send time outside historical pattern |
| `urgency_language_detected` | bool | Urgency or pressure language present |
| `secrecy_language_detected` | bool | Secrecy, confidentiality, or bypass language present |
| `thread_initiation_pattern_changed` | bool | Thread initiation style differs from baseline |
| `writing_style_drift_detected` | bool | Linguistic fingerprint diverges from baseline |
| `cadence_anomaly` | bool | Email frequency outside baseline pattern |
| `authority_language_detected` | bool | Executive authority or escalation language present |

**Scoring boundaries:**

```
0.00  All signals false
0.25  send_time_anomaly OR cadence_anomaly alone
0.50  urgency_language_detected OR writing_style_drift OR 2+ signals
0.75  urgency_language AND secrecy_language
      OR authority_language AND thread_initiation_changed
1.00  Any 0.75 combination AND payment action present within lookforward window
```

**Structural drift penalty link:** If communication_pattern_volatility changes are accepted into baseline, a 30-day `structural_drift_penalty` is applied to any payment route or approval channel changes for that vendor. Those keys face mandatory manual verification during the penalty window.

---

### Component 5 — artifact_structure_volatility

**Purpose:** Detect changes to document and attachment structure — invoice templates, PDF metadata, attachment types, file fingerprints.

**Input signals:**

| Signal | Type | Description |
|---|---|---|
| `pdf_producer_changed` | bool | PDF producer metadata changed vs baseline |
| `invoice_template_changed` | bool | Invoice template structure changed |
| `invoice_numbering_pattern_changed` | bool | Invoice number format changed |
| `attachment_type_changed` | bool | Attachment file type differs from baseline |
| `attachment_hash_not_in_baseline` | bool | Attachment hash never seen for this vendor |
| `document_metadata_anomaly` | bool | Document creation or modification metadata anomalous |
| `remittance_block_format_changed` | bool | Remittance block layout changed |

**Scoring boundaries:**

```
0.00  All signals false
0.25  invoice_numbering_pattern_changed alone OR document_metadata_anomaly alone
0.50  pdf_producer_changed OR invoice_template_changed OR attachment_type_changed
0.75  remittance_block_format_changed
      OR attachment_hash_not_in_baseline AND invoice_template_changed
1.00  Any 0.75 combination AND payment action present
      OR unknown_payment_destination_field_detected in document
```

---

### Component 6 — user_verification_volatility

**Purpose:** Detect whether the verification performed was genuine, channel-trustworthy, and sufficient for the risk level.

**Input signals:**

| Signal | Type | Description |
|---|---|---|
| `verification_channel_matches_historical_baseline` | bool | Channel was in trusted baseline before request |
| `verification_channel_source` | enum | historical_baseline | newly_supplied_payload | operator_entered | external_directory | unknown |
| `verification_performed` | bool | Out-of-band verification was attempted |
| `verification_outcome` | enum | confirmed | unconfirmed | failed | bypassed |
| `multi_party_verification_performed` | bool | Two or more independent human verifiers |
| `cryptographic_challenge_response_used` | bool | Cryptographic verification performed |

**Scoring boundaries:**

```
0.00  verification_channel_matches_historical_baseline == true
      AND verification_outcome == confirmed
      AND (multi_party_verification_performed OR any other volatility component < 0.50)

0.50  verification_performed but channel == operator_entered or external_directory
      (not from baseline, but not attacker-supplied)

0.75  verification not performed
      OR verification_outcome == unconfirmed

1.00  verification_channel_source == newly_supplied_payload
      OR verification_outcome == failed
      OR verification_outcome == bypassed
      OR verification_channel_matches_historical_baseline == false
```

**Multi-party verification rule:** If any other volatility component >= 0.75, single-factor out-of-band confirmation is insufficient. `multi_party_verification_required: true` and `verification_credential_class` must be `multi_party` or `cryptographic_challenge_response`.

Note: verification through a historically trusted channel does not guarantee the channel has not been compromised at the infrastructure level. The schema records the channel match as a fact. The multi-party requirement exists precisely because a single trusted channel can be intercepted.

---

### Weighted mean and ceiling breach

```
telemetry_volatility_score = weighted_mean(all six components)
```

Suggested weights: payment_metadata (0.30), user_verification (0.20), sender_identity (0.20), infrastructure (0.15), artifact_structure (0.10), communication_pattern (0.05). Weights are operator-configurable within signed config — agents cannot modify weights.

Thresholds:
```
>= 0.60  → unstable, review_required, auto_promotion_allowed: false
>= 0.80  → blocked, baseline_update_allowed: false
```

### Ceiling breach evaluation (independent of weighted mean)

Hard blocker fires if any of these are true:
```
any single component == 1.00
any two components >= 0.75
payment_metadata_volatility >= 0.75 AND any other component >= 0.50
sender_identity_volatility >= 0.75 AND infrastructure_volatility >= 0.75
user_verification_volatility >= 0.75 AND financial/action request present
```

### Cumulative Volatility Index

```
CVI = sqrt(sum of all active component scores squared)
CVI_block_threshold  = max(sqrt(n × 0.60²), 1.25)
CVI_review_threshold = max(sqrt(n × 0.50²), 1.00)
```

The floor constants `1.25` and `1.00` represent the CVI of two components simultaneously at approximately `0.88` and `0.71` respectively — the principled basis is that any two components simultaneously above those levels should trigger the threshold regardless of total component count.

---

## §11 — Evidence Diversity Model

**Status: CONCEPT-COMPLETE**

```
Evidence_Diversity_Coefficient =
  min(1.0,
    (unique_root_origin_count + unique_source_system_count
     + unique_collector_family_count + unique_evidence_type_count)
    / denominator
  )
```

Denominator from signed `active_source_family_config` (signed by Matt only). Default ceiling 8. Unlisted sources: `UNLISTED_TELEMETRY_SOURCE` flag, no denominator contribution.

```
0.00 – 0.39  = low → blocked, review_required
0.40 – 0.69  = medium
0.70 – 1.00  = high
```

---

## §12 — Actor Lineage and Separation of Duties

**Status: CONCEPT-COMPLETE**

Full `actor_lineage_chain` on every candidate. Agents may observe, collect, normalize, score, request, and recommend. Agents may not approve, reject as final authority, clear poisoning, or finalize rollback.

Service accounts, MCP tools, and external systems may not hold approval authority.

`approver_actor_id` must not appear anywhere in `actor_lineage_chain` with roles: observed, collected, normalized, scored, or requested.

---

## §13 — Delegation Rules

**Status: CONCEPT-COMPLETE**

Valid delegation requires: `delegation_id` exists, authority scope covers the key class, delegation predates candidate, delegator not in lineage as requester/scorer/collector, `delegation_root_actor_type == human`.

Agent-to-agent delegation is forbidden. Any chain where `delegation_root_actor_type != human` fires `hard_blockers: [agent_delegation_chain]`.

---

## §14 — Verification Channel Integrity

**Status: CONCEPT-COMPLETE**

Verification only counts when the channel was trusted before the request arrived. Attacker-supplied channels are immediately blocked (`closed_loop_verification_channel` hard blocker).

When any volatility component >= 0.75: single-factor verification is insufficient. `multi_party_verification_required: true`. `verification_credential_class` must be `multi_party` or `cryptographic_challenge_response`. Specific cryptographic protocol is deferred to the contract.

---

## §15 — Normalization Versioning and Primordial Evidence Root

**Status: CONCEPT-COMPLETE**

Every normalized evidence item bound to pinned normalization engine, version, and ruleset hash. Re-normalization produces a new immutable record — originals never overwritten.

All re-normalized records must carry `ancestral_raw_evidence_id` pointing to primordial root. Intermediate generations cannot become new roots. `normalization_generation > 2` blocks.

`unresolvable` (permanent): block immediately.
`resolution_pending` (temporary): hold with operator-configurable timeout (suggested default 4 hours). Escalate to operator on timeout.

---

## §16 — Baseline Staleness and Epoch Handling

**Status: CONCEPT-COMPLETE**

| Class | inactivity_threshold_seconds | Status after threshold |
|---|---|---|
| money_movement | 0 | Never trust by inactivity alone |
| payment_approval_channel | 0 | Always re-verify |
| iam / security_control | 0 | Always re-verify |
| vendor_identity | 7,776,000 | Stale after 90 days |
| invoice_structure | 7,776,000 | Stale after 90 days |
| infrastructure_metadata | 2,592,000 | Stale after 30 days |
| communication_pattern | 2,592,000 | Stale after 30 days |
| benign_metadata | 15,552,000 | Stale after 180 days |

Stale baselines may increase suspicion. They may not reduce risk without fresh evidence.

---

## §17 — Structural Drift and Cumulative Drift

**Status: CONCEPT-COMPLETE**

Drift compares against `last_locked_baseline_configuration`, not the previous candidate. Fluid candidates cannot become comparison anchors.

### Cumulative drift window defaults

| Class | cumulative_structural_drift_window_seconds |
|---|---|
| money_movement, payment_approval_channel, iam, alert_suppression, security_control, legal_identity | No cumulative window — any drift triggers immediate review |
| vendor_identity, invoice_structure | 7,776,000 (90 days) |
| communication_pattern, infrastructure_metadata | 2,592,000 (30 days) |
| benign_metadata | 15,552,000 (180 days) |

```
cumulative_structural_drift_score >= 0.70  → review_required
cumulative_structural_drift_score >= 1.00  → blocked
```

Severity classes: `single | compound | critical`. Critical fires when combined weight >= 1.00 or any two hard triggers simultaneously.

---

## §18 — Temporal Arbitrage Prevention: Vendor-Scoped Adaptive Lookforward Watch

**Status: CONCEPT-COMPLETE**

A vendor-scoped adaptive lookforward watch is initiated whenever a baseline modification is accepted for any vendor and baseline key combination.

### Watch behavior

Initial window: 30 days from modification acceptance.

Renewal trigger: any subsequent event touching the modified baseline key OR its dependent key classes for that vendor. General communication from the vendor does not renew the watch. The renewal trigger scope is `events_touching_modified_baseline_key OR events_touching_dependent_key_classes`.

Maximum total watch: `maximum_total_watch_seconds` (default 7,776,000 = 90 days).

### Capped state

When the watch hits its maximum duration without explicit operator sign-off, `temporal_risk_decay_state` transitions to `capped` — not `expired`. While `capped`:
- All transactions involving the modified baseline key route to mandatory human review
- Auto-promotion is blocked
- The key cannot be used to reduce risk on any detection
- State clears only when Matt or named MSP authority explicitly signs off

`expired` state is only valid when the watch completes AND operator sign-off is received. A watch that hits the maximum without sign-off is always `capped`, never `expired`.

### Write-lock state

If `operator_exception_with_logged_risk` is applied to a blocked candidate, the affected baseline key enters `baseline_key_write_lock_status: locked`. While locked:
- All subsequent transactions involving the key are blocked from auto-promotion
- The lock is visible on every transaction UI touchpoint involving the key
- Lock is released only by Matt or designated MSP authority signing a separate key-unlock
- Lock scope matches against normalized canonical vendor identity, not raw string

The canonical vendor entity registry is seeded at tenant onboarding. It must be populated before baseline evaluation begins for any vendor. Agents cannot populate the canonical registry.

---

## §19 — Baseline Integrity Status and Poisoning Determination

**Status: CONCEPT-COMPLETE — OQ-2 LOCKED**

### Integrity status values

```
trusted | under_review | suspected_poisoned | confirmed_poisoned | rolled_back
```

### OQ-2 — Locked rule

Independent poisoning clearance requires:
```
actor_type: human
authority_scope: approve_high_risk
```

No service account, MCP tool, external system, low-privilege account, or agent may clear poisoning or finalize rollback under any condition. This rule is absolute and has no exceptions.

The original approver of a candidate may not determine whether that candidate is poisoned, safe, cleared, or rolled back. No actor appearing in the `actor_lineage_chain` with any role may serve as the sole authority for poisoning clearance.

Automated systems may raise suspicion and populate `suspected_poisoned`. Confirming `confirmed_poisoned` and authorizing rollback requires a human with `approve_high_risk` authority not involved in the original candidate lifecycle.

---

## §20 — Rollback, Taint Analysis, and Downstream Re-Review

**Status: CONCEPT-COMPLETE**

Rollback is not complete until all downstream influenced detections and pending artifacts are marked for re-review.

Lookback minimums: locked classes 30 days, review-required classes 7 days, low-risk metadata 24 hours.

Dynamic lookforward: `max(minimum_lookforward_seconds, max_downstream_execution_delay_seconds)`. Minimum lookforward 1 hour for all classes.

Pending artifact states requiring inclusion: `pending | scheduled | queued | awaiting_approval | awaiting_payment | awaiting_export | awaiting_sync | unexecuted`.

UI must show active warning on tainted historical records. They must not display as clean until explicitly reviewed and cleared by a human with `approve_high_risk` authority.

---

## §21 — Audit Record Requirements

**Status: CONCEPT-COMPLETE**

Every baseline candidate produces an immutable audit record at creation. Audit records are never overwritten.

Required fields include: `audit_record_id`, `candidate_baseline_change_id`, `tenant_id`, `created_at`, normalization fields (all three — engine ID, version, ruleset hash), `pre_normalization_hash`, `post_normalization_hash`, `actor_lineage_chain` snapshot, `approval_status`, `promotion_confidence_class`, `hard_blockers` array at decision time, `sensitive_key_registry_signature_block` snapshot, `cvi_block_threshold` at evaluation time.

No audit record may depend on private chain-of-thought from any agent. All evidence references must be to committed, resolvable artifacts.

---

## §22 — UI Flags and Operator-Facing Language

**Status: CONCEPT-COMPLETE**

| Flag | Condition |
|---|---|
| `LOW_EVIDENCE_DIVERSITY` | diversity_coefficient < 0.40 |
| `DO_NOT_TREAT_AS_INDEPENDENT_CONFIRMATION` | diversity_coefficient < 0.40 |
| `SINGLE_ROOT_ORIGIN` | unique_root_origin_count < 2 |
| `MULTI_AGENT_REVIEW_DOES_NOT_EQUAL_MULTI_SOURCE_EVIDENCE` | unique_root_origin_count < 2 |
| `HIGH_UNKNOWN_ORIGIN_RATIO` | unknown_origin_ratio > 40% |
| `SYSTEMIC_VISIBILITY_LOSS` | unextracted_high_risk_signal_count > 2 |
| `UNLISTED_TELEMETRY_SOURCE` | source not in signed active_source_family_config |
| `SOURCE_FAMILY_NOT_DENOMINATOR_ELIGIBLE` | source not in signed config |
| `BASELINE_TAINTED` | baseline_taint_status == tainted |
| `RE_REVIEW_REQUIRED` | re_review_required == true |
| `CUMULATIVE_DRIFT_WARNING` | cumulative_structural_drift_score >= 0.70 |
| `STRUCTURAL_DRIFT_CRITICAL` | structural_drift_severity_class == critical |
| `VERIFICATION_CHANNEL_ATTACKER_SUPPLIED` | verification_channel_source == newly_supplied_payload |
| `MULTI_PARTY_VERIFICATION_REQUIRED` | any volatility component >= 0.75 |
| `STALE_BASELINE_CANNOT_REDUCE_RISK` | baseline_staleness_status != active used to reduce risk |
| `POISONING_DETERMINATION_CONFLICT` | poisoning_determination_actor_lineage_conflict == true |
| `BASELINE_KEY_WRITE_LOCKED` | baseline_key_write_lock_status == locked |
| `TEMPORAL_WATCH_CAPPED` | temporal_risk_decay_state == capped |
| `UNKNOWN_PAYMENT_DESTINATION_DETECTED` | unknown_payment_destination_field_detected == true |

All UI language must be plain English readable by a non-technical MSP operator.

---

## §23 — Open Questions

**OQ-1 — Telemetry volatility component inputs** ← **RESOLVED**

All six components are fully defined in §10 with input signals, scoring boundaries, hard blocker triggers, schema fields, UI flags, and example calculations. Build authorization for the volatility model is unblocked.

**OQ-2 — Poisoning determination reviewer qualification** ← **LOCKED**

Locked in §19. Independent poisoning clearance requires `actor_type: human` AND `authority_scope: approve_high_risk`. No exceptions.

**OQ-3 — Source family config rotation and revocation** ← RESOLVED IN DOCUMENT

Addressed in §11. `active_source_family_config` must carry `config_expiry_timestamp` and `config_revocation_status`. Expired or revoked config triggers `review_required`.

**OQ-4 — Cumulative drift window defaults** ← RESOLVED IN DOCUMENT

Addressed in §17. Class-specific defaults defined. Locked classes have no cumulative window — any drift triggers immediate review.

**OQ-5 — Primordial root resolution timeout** ← RESOLVED IN DOCUMENT

Addressed in §15. `resolution_pending` state with operator-configurable timeout (suggested default 4 hours). Escalate to operator on timeout. Never auto-promote during pending state.

**Remaining carry-forward items for contract session:**

CF-1: CVI_review_threshold uses same floor treatment as CVI_block_threshold — confirm in contract invariants.
CF-2: Financial routing regex set must be operator-signed in same registry as sensitive key class registry — confirm authority in contract.
CF-3: Canonical vendor entity registry must be seeded at tenant onboarding — define onboarding gate in contract.
CF-4: Soft_Dampener_Score floor directionality (0.85 is a dampener floor, not a confidence floor) — document explicitly in contract invariants.

---

## §24 — Build Readiness Gate

**Status: CONCEPT-COMPLETE — CONTRACT SESSION AUTHORIZED**

All open questions are resolved. The concept document is complete.

A separate signed §11 design contract is required before any implementation begins. The contract must address all carry-forward items CF-1 through CF-4.

The concept document may be shared with Todd Chapman or external MSP reviewers as a product architecture reference.

---

## §25 — Failure Modes and Required Tests

| Test ID | Failure mode | Test |
|---|---|---|
| TBI-T-01 | Evidence theater via single-type high volume | Submit 50 evidence items all email_header — verify diversity blocks |
| TBI-T-02 | Lineage collusion via multi-channel single-source | Three collectors same root_origin_entropy_hash — verify counted as one |
| TBI-T-03 | Agent self-assignment of sensitive_key_class | Agent submits money_movement self-declared — verify registry overrides |
| TBI-T-04 | Agent-to-agent delegation approval | Agent_A delegates to Agent_B; Agent_B approves — verify blocked |
| TBI-T-05 | Rollback gap on downstream detections | Baseline poisoned; rollback triggered — verify all influenced detections marked tainted |
| TBI-T-06 | Normalization hash drift | Engine updated; old evidence re-hashed — verify original immutable, new record created |
| TBI-T-07 | Time-shifted replay | Old retired baseline hash re-submitted — verify staleness blocks risk reduction |
| TBI-T-08 | Low-risk tunneling pre-staging payment attack | Communication drift accepted; payment change submitted — verify structural_drift_penalty applied |
| TBI-T-09 | Closed-loop verification channel | New callback number in payload used for verification — verify blocked as attacker_supplied |
| TBI-T-10 | Score zero-flattening via conflict injection | Conflicting low-reliability evidence injected — verify volatility score elevated, alert emitted |
| TBI-T-11 | Primordial root chain laundering | Evidence re-normalized twice submitted as root — verify normalization_generation > 2 blocks |
| TBI-T-12 | Poisoning clearance by original approver | Original approver attempts clearance — verify actor_lineage_conflict blocks |
| TBI-T-13 | Pending artifact missed in rollback | Scheduled invoice in taint window — verify included in pending_downstream_artifact_ids |
| TBI-T-14 | Unlisted source alters denominator | Unlisted source contributes evidence — verify denominator unchanged, flag shown |
| TBI-T-15 | Registry version mismatch | Old registry evaluated; new registry active — verify atomic block catches mismatch |
| TBI-T-16 | Null signal laundering | Signal returns null — verify treated as unextracted with penalty score, not false |
| TBI-T-17 | Temporal arbitrage across session boundary | Payment change in session 1, execution in session 2 day 31 — verify capped state blocks |
| TBI-T-18 | Sub-threshold squatting via six-vector spread | All six components at 0.74 — verify CVI threshold fires hard block |
| TBI-T-19 | Payment rail misdirection via unregistered field | Unknown field with IBAN pattern in non-payment document region — verify regex override fires |
| TBI-T-20 | Operator exception write-lock circumvention | Vendor name permutation submitted after write-lock — verify canonical entity resolver catches |
| TBI-T-21 | Visibility collapse via component unextracted | Full artifact_structure_signals block returns unextracted — verify systemic_visibility_loss if high-risk count exceeded |
| TBI-T-22 | Watch cap exploitation at day 91 | Lookforward watch at maximum; attacker waits out — verify capped state requires operator sign-off, not expired |

---

## §26 — Non-Negotiable Rules (Summary)

1. Agents may observe, collect, normalize, score, request, or recommend. Agents may not approve, reject as final authority, clear poisoning, or finalize rollback.
2. Service accounts and MCP tools may not approve baseline changes.
3. Matt or named MSP authority must sign all sensitive authority-changing configuration including registries, source family configs, and weight configs.
4. No sensitive key may be auto-promoted.
5. Unknown-origin evidence may not create independent confirmation.
6. Multi-agent review is not multi-source evidence.
7. Verification must use historically trusted channels. Attacker-supplied channels are blocked.
8. Structural drift compares against the last locked baseline, not the most recent fluid candidate.
9. Rollback is incomplete until downstream influenced detections and pending artifacts are marked for re-review.
10. No audit record may depend on private chain-of-thought.
11. Weighted telemetry volatility cannot launder component-level ceiling breaches.
12. Registry version, hash, and signature must be validated atomically.
13. Re-normalized evidence must resolve to a primordial raw evidence root.
14. Poisoning clearance requires actor_type: human AND authority_scope: approve_high_risk. No exceptions.
15. Stale baselines may increase suspicion. They may not reduce risk without fresh evidence.
16. Unextracted signals take a class-specific penalty score — they must never default to false.
17. A watch that hits its maximum duration without operator sign-off is capped, not expired.
18. Write-locked baseline keys are visible on every transaction touchpoint involving that key.
19. Vendor identity matching for write-lock scope uses canonical normalized entity identity, not raw strings.
20. Single-factor verification is insufficient when any volatility component >= 0.75.
21. Payment rail changes and remittance address changes that coincide with action requests are elevated to hard-block territory.
22. The canonical vendor entity registry must be seeded at tenant onboarding. Agents cannot populate it.
