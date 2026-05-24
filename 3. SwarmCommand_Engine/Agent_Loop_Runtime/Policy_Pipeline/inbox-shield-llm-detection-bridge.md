# Inbox Shield LLM Detection Bridge

Definition of Done - Bridge from business PoC to governed runtime producer.

## Purpose

The runnable Inbox Shield PoC lives in:

```text
C:\Unified Folder Structure NorthStar + SwarmCommand Venture\AI_Phishing_Simulation_Business\Inbox_Shield\inbox_shield_langgraph.py
```

That script is allowed to move fast as a business demo. The governed runtime
cannot treat raw LLM output as production truth. This bridge defines how the
PoC graduates into SwarmCommand without bypassing audit, signed policy
promotion, Guardrail 11, the regression detector, or rollback.

## Runtime role

New future producer:

```text
llm_detection_001
```

Environment:

```text
sandbox only
```

Allowed output:

```text
detection_result
```

Not allowed:

- Direct production writes.
- Direct workflow triggers.
- Direct `production_state` mutation.
- Direct rollback requests.
- Direct policy updates.

## Input contract

The producer receives one normalized inbound email text payload:

```json
{
  "tenant_id": "string",
  "email_text": "string",
  "received_at": "ISO-8601 string | null",
  "source_ref": "string | null"
}
```

The producer may call the business PoC analyzer, but the runtime wrapper owns
all tenant routing, source identity, and Blackboard writes.

## Output mapping

The PoC currently returns:

```json
{
  "summary": "string",
  "action_items": [],
  "risk_analysis": {
    "risk_score": 0,
    "risk_factors": [],
    "phishing_signals": [],
    "urgency_signals": [],
    "financial_risk": "low"
  },
  "impersonation_analysis": {
    "impersonation_likelihood": 0,
    "suspicious_elements": [],
    "sender_legitimacy_notes": "string"
  },
  "recommended_action": "safe"
}
```

The runtime wrapper maps it into the existing `DetectionResultPayload` surface:

- `detection_label`
  - `safe` -> `no_obvious_threat`
  - `needs_review` -> `suspicious`
  - `block` -> `high_risk_phishing`
- `confidence`
  - max(`risk_score`, `impersonation_likelihood`) / 100
- `signals`
  - union of `phishing_signals`, `urgency_signals`, and `suspicious_elements`
- `explanation`
  - concise source marker: `NorthStar Inbox Shield LLM analysis via grok-4.3`

The full PoC JSON may be preserved in the audit trail as structured detail only
if the existing Blackboard schema permits it. Do not loosen schema rules just to
store the full response.

## Guardrails

1. `llm_detection_001` is sandbox-only until explicit promotion.
2. The model output is evidence, not authority.
3. `audit_001` must review any candidate behavior change before promotion.
4. Production may only observe the effect through a signed policy update and
   `apply_signed_policy`.
5. Regression detector remains downstream of production application and can
   emit `policy_regression_alert` if the LLM-backed policy causes regressions.
6. Alert subscriber remains the only automated rollback trigger.
7. Multi-tenant isolation hardening must land before any customer tenant uses
   this bridge outside demo data.

## Phase plan

### Phase 1 - Business PoC

Complete:

- `Inbox_Shield/inbox_shield_langgraph.py`
- Pydantic validation.
- Retry-on-bad-JSON.
- Conservative fallback JSON.
- Manual email-file input.

### Phase 2 - Runtime wrapper

Add a new sandbox module that imports or adapts the PoC logic and emits a
schema-valid `DetectionResultPayload` as `llm_detection_001`.

Required tests:

1. Safe email maps to `no_obvious_threat`.
2. Wire-fraud email maps to `high_risk_phishing`.
3. Bad model output maps to conservative `needs_review` / suspicious result.
4. Wrapper writes only to sandbox Blackboard.
5. Wrapper rejects missing tenant id.
6. Wrapper does not create workflow triggers, policy updates, or production
   state writes.

### Phase 3 - Evaluation harness

Connect the wrapper to the existing Grok evaluation reports under
`Runtime_Implementation` so prompt changes are measured against replayable
emails before any policy promotion.

### Phase 4 - Promotion

Only after evaluation and audit:

- Propose a policy update that changes production detection parameters to
  account for LLM-backed confidence/signals.
- Sign it in sandbox.
- Promote through the existing policy pipeline.
- Apply through Guardrail 11.
- Monitor through regression detector and alert subscriber.

## Verification target

The bridge is not implementation-complete until the runtime suite passes and
adds explicit coverage for Phase 2:

```text
python -m pytest tests
```

Minimum expected increase when Phase 2 lands: +6 tests.
