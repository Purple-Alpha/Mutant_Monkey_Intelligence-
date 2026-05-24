# Policy Regression Detector
Automated Producer for `policy_regression_alert`

## Purpose
The alert subscriber can already consume a `policy_regression_alert` and turn it into a sandbox-signed rollback. This detector is the first automated producer of those alerts.

It watches production telemetry after a policy has been applied and raises an operational `audit_001.audit_verdict` only when the current active policy appears to have made detection behavior materially worse.

## Scope
The detector is intentionally conservative:

- It does not mutate `production_state`.
- It does not sign rollbacks.
- It does not bypass the alert subscriber.
- It emits the same alert shape as an operator would emit through `emit_regression_alert`.

## Signal
Prototype regression signal:

1. Find the most recent `policy_applied` audit verdict for the tenant.
2. Gather detection/risk records created after that apply.
3. Flag a regression when both are true:
   - at least `minimum_samples` post-apply detection results exist
   - the post-apply alert ratio is at or above `alert_ratio_threshold`

An alert-like result is either:

- a `risk_score` record at or above `risk_score_threshold`, or
- a `detection_result` record with confidence at or above `detection_confidence_threshold`

The prototype pairs risk scores to detections by parent relationship when available. If no risk score exists, detection confidence alone can still count.

## Idempotency
The detector writes a `policy_regression_detector_checked` marker for each checked `policy_applied` audit. Once an alert is emitted or a no-regression check is recorded, the same applied policy is not evaluated again.

This keeps repeated production cycles from repeatedly emitting the same alert.

## Behavior Contract

| Scenario | Outcome |
|---|---|
| No applied policy exists | No-op result. |
| Applied policy exists but insufficient post-apply samples | No-op result; no marker, so later telemetry can still satisfy the sample floor. |
| Enough samples but below threshold | Writes checked marker; no alert. |
| Enough samples and threshold exceeded | Emits `policy_regression_alert`; writes checked marker. |
| Re-run after marker exists | No-op; no duplicate alert. |

## Verification Target
From `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation`:

```text
python -m pytest tests
```

Target: previous 59 tests plus focused detector coverage.
