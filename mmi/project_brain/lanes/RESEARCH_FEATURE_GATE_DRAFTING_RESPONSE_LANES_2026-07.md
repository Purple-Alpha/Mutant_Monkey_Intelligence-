# MMI Feature Gate — Drafting vs Response Lanes (Research)

**Status:** RESEARCH / CONCEPT — NOT BUILT  
**Authority:** Matt (Super) — research lane  
**Date filed:** 2026-07-03  
**Purpose:** Preserve the modular Feature Gate doctrine for email/outbound authority: capability may mature through evidence; authority may only move by operator-signed promotion.

**Related (built doctrine — do not re-litigate):**
- `architecture/MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md` — H5: file existence ≠ authorization; re-verify + consume-once
- `chaos/mmi_control_envelope.py` — loop cannot self-ack; fail-closed HALT/SUSPEND
- `architecture/MMI_CONTROLLED_CHAOS_DEFENSIVE_WEAPON_CONCEPT_2026-07.md` §8–§9 — signed envelopes, rotate nonces not grammar
- `lanes/REDDIT_VENDOR_EMAIL_ROUTINE_INTAKE_2026-07.md` — field evidence for human-gate patterns
- `lanes/RESEARCH_SENDINTENT_OUTBOUND_CONTAINMENT_CRITIQUE_2026-07.md` — empirical critique, SendIntent protocol, Levenshtein rejected
- `lanes/MMI_EMAIL_DRAFTING_RESPONSE_CONTAINMENT_HANDOFF_2026-07-03.md` — **master architecture handoff** (consolidates above)

**Parallel build (parked):** AGI §5 step 5 genomic loop — BUILDABLE, awaiting `authorize build step 5 genomic loop`. This research does not authorize email/outbound build.

**Not build authorization.**

---

## Core invariant

```text
MMI can evolve capability.
MMI cannot evolve authority.
```

Supporting boundary:

```text
The system may earn trust evidence.
The system may recommend promotion.
The system may not auto-promote itself into outbound authority.
```

Sending email is not merely a technical capability — it is identity, reputation, legal exposure, and social authority.

---

## Preferred rule

```text
Drafting Lane can be enabled by policy.

Response Lane can only move upward by signed human authority.

Trust metrics may support promotion, but may not execute promotion.
```

**Forbidden pattern:**

```text
ReputationScore > Threshold_Alpha
→ auto-enable GATE_RESPONSE_LAYER
```

**Required pattern:**

```text
ReputationScore > Threshold_Alpha
→ emit PROMOTION_RECOMMENDATION
→ require Matt/operator signature
→ then move Response_Lane from DISABLED to GATED
```

---

## GATE_DRAFTING_LAYER

```text
Status: DISABLED | MONITOR_ONLY | ENABLED

Allowed:
- ingest sanitized inbound email
- classify risk
- create evidence package
- draft reply
- send draft to review queue

Forbidden:
- send email
- call outbound API
- modify mailbox authority state
- promote itself
```

More freedom inside analysis and drafting: **yes.**  
Freedom to switch into outbound response mode: **no.**

---

## GATE_RESPONSE_LAYER

```text
Status: DISABLED | RECOMMEND_ONLY | HUMAN_APPROVED_SEND | TEMPLATE_LIMITED_AUTO | CONDITIONAL_AUTO

Allowed only when signed:
- suggest sending
- request human approval
- send exact approved response
- later, maybe send template-limited responses

Forbidden by default:
- free-form autonomous external communication
- high-risk categories
- payment / account / legal / credential / authority decisions
- promotion without signed operator approval
```

Avoid a plain `ENABLED` state too early — authority level must be obvious from the mode name.

---

## Trust Metric Engine — advisory only

The Trust Metric Engine is **not** a switch-flipper. It is a **promotion evidence generator**.

**Inputs (examples):**

```text
emails analyzed
drafts generated
critic-ring pass rate
prompt-injection catches
template-selection accuracy
false-positive rate
false-negative rate
human edits required
human rejections
unsafe-draft incidents
policy violations
outbound-risk category hits
```

**Output (example):**

```text
PROMOTION_RECOMMENDATION:
  from: DRAFTING_ENABLED
  to: RESPONSE_RECOMMEND_ONLY
  confidence: 0.93
  evidence_window: 100 reviewed emails
  invariant_failures: 0
  human_rejection_rate: 2%
  required_signature: Matt
```

**Forbidden:**

```text
The system trusts itself enough, so it gives itself more power.
```

---

## Feature gate schema (v1 draft)

```yaml
MMI_Feature_Gates:
  version: "1.0.0"

  Drafting_Lane:
    status: "ENABLED"
    isolation_level: "FULL_NO_OUTBOUND"
    allowed_outputs:
      - "risk_summary"
      - "evidence_package"
      - "draft_response"
      - "verification_recommendation"
    forbidden_capabilities:
      - "send_email"
      - "archive_email"
      - "delete_email"
      - "click_link"
      - "open_attachment_without_sandbox"
      - "mutate_project_authority"
      - "self_promote_gate"

  Response_Lane:
    status: "DISABLED"
    activation_model: "SIGNED_OPERATOR_ONLY"
    current_mode: "NO_OUTBOUND"
    allowed_modes:
      - "DISABLED"
      - "RECOMMEND_ONLY"
      - "HUMAN_APPROVED_SEND"
      - "TEMPLATE_LIMITED_AUTO"
    forbidden_categories:
      - "payment_change"
      - "banking"
      - "credentials"
      - "legal"
      - "contracts"
      - "hr"
      - "client_commitment"
      - "project_authority"
    approved_templates:
      - "verification_request"
      - "security_ack"
      - "secure_channel_redirect"
    max_risk_score_for_template_auto: 0.05
    requires_evidence_bundle: true
    requires_outbound_ledger_entry: true
    requires_human_signature_until_stage: "TEMPLATE_LIMITED_AUTO"

  Promotion_Control:
    trust_metric_engine: "ADVISORY_ONLY"
    auto_promotion_allowed: false
    promotion_requires:
      - "operator_signature"
      - "evidence_window"
      - "zero_critical_invariant_failures"
      - "critic_ring_pass"
      - "rollback_plan"
      - "kill_switch_verified"

  Emergency_Control:
    unsigned_gate_change_action: "EMERGENCY_HALT"
    outbound_violation_action: "SINGULARITY_QUARANTINE"
    prompt_injection_escape_action: "CASE_FREEZE_AND_REVIEW"
```

---

## Transition path

```text
Drafting intelligence matures through evidence.
Trust engine measures performance.
Critic Ring validates behavior.
Promotion report is generated.
Matt signs or rejects.
Only then does the Response Gate move.
```

---

## Mapping to existing MMI gates (when built)

| Research concept | Existing / planned primitive |
|------------------|------------------------------|
| Operator-signed promotion | Console Ed25519 signoff (H5 re-verify) |
| Promotion recommendation only | Proof gate / genomic episode evidence bundle |
| No self-promote | Control envelope ack channel separation |
| Outbound schema limitation | Action integrity + structured control verbs |
| Emergency halt | Envelope HALT/SUSPEND sticky latch |
| Evidence before send | Gate B CLEAN + console VALID |

---

## Open research questions (partially resolved — see companion critique)

1. Where does `MMI_Feature_Gates` state live — authority repo vs chaos lab ledger? **Open.**
2. Is gate promotion a console signoff record type, or a separate promotion manifest domain? **Leaning: separate domain or signoff subtype; both require operator Ed25519.**
3. How does `TEMPLATE_LIMITED_AUTO` bind to exact template bytes? **Resolved in companion:** SendIntent + Lung recompute; no LLM synthesis; region-aware render proof.
4. Sidecar commit proxy vs in-process validator for Response Lane state changes? **Leaning:** signer outside swarm; gate snapshot hash bound at Lung execution time.

---

## Lane note

ChatGPT/Gemini = research. Claude = contract when promoted to spec. Codex = plan/diff review. Cursor = implementation only after BUILDABLE + Matt build auth. This file stays **RESEARCH** until Matt promotes it.
