# Policy Regression Alert Subscriber
Closes the Loop From "Bad Apply Detected" Back to "Sandbox-Signed Rollback"

## Purpose
The rollback primitive ships the *capability* to revert a production policy. The alert subscriber ships the *trigger*: a clean way for operators (or automated detectors) to say "the most recent apply caused a regression," and have the rollback get signed, promoted, and applied automatically without any manual sandbox writes.

This is the last piece needed for an end-to-end "alert → rollback → reverted state" loop.

## What this is
- A new explicit `audit_001.audit_verdict` record type identified by `workflow_id="policy_regression_alert"`, `verdict=REJECTED`, and `target_record_id` pointing at the **most-recent** `policy_applied` audit for the tenant.
- A subscriber that scans production for unconsumed alerts each cycle, **validates provenance and target integrity**, calls `request_rollback_to_previous` only for valid alerts, and writes a consumption marker (`workflow_id="regression_alert_consumed"`) so the same alert never fires twice. Invalid alerts are dead-lettered with `requires_human_review=True`.
- A one-line wiring into the production loop. Default ON. Existing tests do not emit alerts, so the subscriber is a no-op for them.

## What this is *not*
- Not a regression *detector*. The detector — heuristic, statistical, or operator-driven — is the producer of the alert. This module is the *consumer* of the alert.
- Not a new write surface. It uses only existing surfaces: `audit_001.audit_verdict` (operational telemetry, observational-append-only per Guardrail 11) and the sandbox `policy_update` produced by `request_rollback_to_previous`. The actual production-state mutation still flows through the existing Guardrail 11 gate.
- Not coupled to the policy consumer. The subscriber and the consumer both run at end of cycle but are independent: the subscriber emits *sandbox* records; the consumer applies *production* triggers.

## Definition of Done

### What will be created
- `core/production/alert_subscriber.py`:
  - `AlertSubscriberConfig` — dataclass with `production_tenant_id`, `sandbox_tenant_id`, `alert_workflow_id="policy_regression_alert"`, `consumed_workflow_id="regression_alert_consumed"`, `signing_key`, `alert_agent_id="audit_001"`.
  - `AlertSubscriptionItem` — per-alert result: `alert_record_id`, `triggered_rollback`, `rollback_record_id`, `consumption_marker_id`, `skip_reason`.
  - `AlertSubscriptionResult` — `scanned`, `triggered`, `skipped`, `items: list[AlertSubscriptionItem]`.
  - `emit_regression_alert(context, *, reason, severity="high", config=None) -> RouteResult` — operator/automation-facing helper. Finds the most-recent `policy_applied` audit verdict for the tenant and writes an `audit_001.audit_verdict` targeting it with `workflow_id="policy_regression_alert"`. Raises `ValueError` if no policy was ever applied (nothing to flag).
  - `find_unconsumed_alerts(context, *, config=None) -> list[BlackboardRecord]` — returns **valid** unconsumed alerts in chronological order (passes acceptance checks below).
  - `run_alert_subscriber_cycle(context, *, config=None) -> AlertSubscriptionResult` — process each unconsumed alert workflow record: validate, then sign rollback only if valid; dead-letter invalid alerts with skip markers.
- `tests/test_alert_subscriber.py` — at least 6 tests, including the end-to-end loop test.

### What will be modified
- `core/production/loop.py`:
  - `ProductionLoopConfig` gains `run_alert_subscriber_at_end_of_cycle: bool = True` and optional `alert_subscriber_config` (sandbox tenant, signing key, alert agent id).
  - `ProductionLoopResult` gains `alert_subscriber: AlertSubscriptionResult | None`.
  - `run_production_cycle` runs the subscriber at the end, **before** the existing `apply_pending_policies` call, so the subscriber's freshly signed sandbox rollbacks are available to a separately-run promotion pipeline by the next cycle.
- `core/production/__init__.py` — exports.

### Behavior contract

### Alert acceptance checks (subscriber boundary)
An alert is actionable only when **all** of the following hold:
1. `source_agent == config.alert_agent_id` (default `audit_001`)
2. `payload.verdict == REJECTED`
3. `payload.target_record_id` resolves to a production `policy_applied` audit verdict
4. `payload.target_record_id` equals the most-recent `policy_applied` audit for the tenant

Alerts failing any check are dead-lettered with a `regression_alert_consumed` marker and `requires_human_review=True`. They never trigger rollback.

| Scenario | Outcome |
|---|---|
| No alerts in production | `scanned=0, triggered=0, skipped=0`. No new records. |
| Alert from non-`audit_001` source | Dead-lettered; no rollback. |
| Alert with verdict other than `REJECTED` | Dead-lettered; no rollback. |
| Alert target is not a `policy_applied` audit | Dead-lettered; no rollback. |
| Alert targets older (stale) `policy_applied` audit | Dead-lettered; no rollback. |
| One valid alert, history has >=2 applied states | Subscriber signs a rollback to the second-most-recent state, writes consumption marker. Rollback flows through promotion + consumer on subsequent runs/cycles. State reverts. |
| One alert, history < 2 applied states | Subscriber writes consumption marker with `requires_human_review=True` and `skip_reason="no previous applied state"`. No rollback signed. Alert is not re-processed. |
| Subscriber re-run after a successful processing | Already-consumed alerts are skipped. `scanned=0, triggered=0`. Idempotent. |
| Multiple unconsumed alerts in one run | Each gets its own consumption marker. Each fires its own rollback. (Multiple rollbacks targeting the same previous state are correct but noisy; documented limitation.) |
| `emit_regression_alert` called with no prior `policy_applied` audit | `ValueError("no policy_applied audit to flag")`. No record written. |

### Hard guardrails preserved
- The alert subscriber writes only to `audit_001.audit_verdict` (operational telemetry) and the sandbox `policy_update` via the existing rollback primitive. Both are existing allowed surfaces. Guardrail 11 surface list is unchanged.
- Every rollback the subscriber triggers still goes through:
  1. Sandbox signing (`request_rollback_to_previous` -> `sign_rollback_request`).
  2. Promotion pipeline (signature re-verification at the boundary).
  3. Guardrail 11 gate (history check + signature re-verification at the gate).
- No new bypass, no new producer agent.

### Known limitation (prototype scope)
A regression detector that fires alerts faster than the policy consumer can apply rollbacks will produce a queue of identical-target rollbacks. Each is correct in isolation; the cumulative effect on state is also correct (state ends at the target). The audit log will show duplicate `policy_applied` audits for the same target. This is acceptable for the prototype. A later iteration can collapse same-target queued alerts into one rollback.

### Verification command
From `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation`:

```text
python -m pytest tests
```

Target: existing 49 tests still pass + at least 6 new = **55 or more passed**.

## Next Step After This
A real regression detector (heuristic or statistical) that produces `policy_regression_alert` verdicts automatically based on post-apply telemetry. That detector becomes the producer; this subscriber is its consumer.
