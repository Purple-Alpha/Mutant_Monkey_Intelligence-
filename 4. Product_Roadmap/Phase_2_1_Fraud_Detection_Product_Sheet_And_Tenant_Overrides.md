# Phase 2.1 — Fraud Detection Product Sheet + Per-Tenant Parameter Overrides

**Roadmap month:** Month 6 follow-on from the Month 5 closeout direction.
**Status:** **§11 LOCKED by Matt 2026-05-21. Runtime implementation LANDED.** Spec was landed first with no runtime changes; all five §11 decisions are approved and implemented.
**Runtime baseline:** 461 / 461 tests green (Month 5 inherited baseline 419; Phase 2.1 adds 15 override-runtime + 9 operator-CLI + 18 evidence-report tests).
**Primary artifacts:** `Product_Sheets/Fraud_Detection_Product_Sheet.md` and this implementation contract.

## §0 Purpose

Phase 2.1 turns the closed technical loop into two business-critical surfaces:

1. A customer-facing fraud detection product sheet that a buyer or MSP can understand without knowing the agent runtime.
2. A per-tenant parameter override surface that lets NorthStar tune defensive sensitivity by client while preserving the global governance model.

This phase landed in two passes: the customer-facing product sheet shipped with the spec-first pass; the per-tenant override surface shipped in the runtime pass after Matt locked §11 on 2026-05-21.

## §1 Product-Sheet Contract

The product sheet must be plain-English and careful about current runtime boundaries.

It must say NorthStar Inbox Shield does:

- Analyze email-fraud and ransomware-precursor risk.
- Produce structured scoring and recommendations.
- Support leadership summaries, daily digests, and evidence workflows.
- Use sandbox evaluation and signed policy updates to improve defensive sensitivity.

It must not imply NorthStar currently:

- Blocks, quarantines, deletes, or remediates email.
- Fetches URLs or executes attachments.
- Replaces human financial approval.
- Provides a customer self-serve portal in the MVP runtime.

## §2 Proof Points Allowed in Sales Copy

The following proof points are approved for product-sheet use:

| Claim | Evidence |
|---|---|
| Month 2 fraud eval gate passed on `grok-4` | `eval_report_2026_05_21_final_recovery_grok4.md` |
| Fraud precision reached 100% in the gate run | Month 2 final report |
| Legit false-positive rate was 0% in the gate run | Month 2 final report |
| All required fraud subcategory recall floors were met | Month 2 final report |
| Sandbox-to-production sensitivity loop is closed | `test_close_the_loop_red_battery_to_next_cycle_effect` |
| Month 5 runtime baseline was green | `Month_5_Closeout_Readiness.md`, 419 / 419 tests |

Do not turn internal eval proof into a guarantee. These are internal validation results, not promises of universal detection.

## §3 Per-Tenant Override Problem

Phase 1.4 introduced production parameters that affect scoring sensitivity:

- `fraud_risk_floor_lift`
- `attachment_risk_floor_lift`
- `url_obfuscation_floor_lift`

Today those values live in a tenant's `ProductionPolicyState.parameters` dict as the applied policy state for that tenant. Phase 2.1 needs a deliberate operator-facing override layer so client-specific tuning is explicit, auditable, bounded, and reversible.

Examples:

- A finance-heavy client may need a higher fraud sensitivity floor.
- A client with frequent legitimate invoice attachments may need careful attachment sensitivity.
- An MSP pilot tenant may need conservative defaults until false-positive tolerance is understood.

## §4 Override Model

Recommended model: **policy baseline plus operator override overlay**.

Effective parameters are resolved in this order:

1. Global code default (`0` for all three Phase 1.4 lifts).
2. Signed policy state for the tenant.
3. Operator-approved per-tenant override.

Override writes reject values outside the same 0–25 range used by Phase 1.4. Runtime read paths remain defensive: corrupt on-disk override state is ignored and audited rather than applied.

```text
---------------------+
| code defaults      |
+----------+----------+
           |
           v
+----------+----------+
| signed tenant      |
| policy parameters  |
+----------+----------+
           |
           v
+----------+----------+
| operator override  |
| overlay            |
+----------+----------+
           |
           v
+----------+----------+
| effective scoring  |
| parameters         |
+---------------------+
```

## §5 Override Schema

Recommended new runtime object:

```python
@dataclass(frozen=True)
class TenantParameterOverride:
    tenant_id: str
    parameters: dict[str, int]
    reason: str
    requested_by: str
    approved_by: str
    created_at: datetime
    expires_at: datetime | None = None
    status: Literal["active", "paused", "revoked"] = "active"
```

Only keys in `RESERVED_PARAMETER_KEYS` are allowed. The first implementation should allow only the three Phase 1.4 lift keys unless there is an explicit reason to expose legacy `confidence_boost`.

## §6 Guardrails

Per-tenant overrides must obey the same core governance posture as signed policy updates:

- No unreserved parameter keys.
- No value below 0 or above 25.
- No cross-tenant writes.
- No sandbox tenant may write production overrides.
- No override may mutate prompts, agent roles, mutation kinds, or registry permissions.
- No override may disable the kill switch, Guardrail 11, the promotion pipeline, or audit logging.
- No override may fetch external resources or interact with live email systems.

## §7 Audit Trail

Every override action must write an audit record or local append-only audit event:

- `tenant_parameter_override_created`
- `tenant_parameter_override_updated`
- `tenant_parameter_override_paused`
- `tenant_parameter_override_revoked`
- `tenant_parameter_override_expired`

Minimum audit fields:

- `tenant_id`
- `parameters_before`
- `parameters_after`
- `reason`
- `requested_by`
- `approved_by`
- `source`
- `timestamp`

Operator notes should be human-readable because these changes may need to be explained during client review.

## §8 Safe Default Behavior

If no override exists, the runtime must behave exactly as it does at Month 5 closeout.

If an override file is missing, unreadable, expired, paused, revoked, or invalid, the runtime must:

1. Ignore the override.
2. Continue with signed policy state.
3. Write an audit finding for operator review.
4. Never fail open into unbounded sensitivity.

## §9 Implementation Receipt — LANDED

Implementation landed after Matt approved §11.

Runtime files:

- `core/production_state/tenant_overrides.py` — `TenantParameterOverride`, `TenantOverrideAuditEvent`, local JSON path helpers, append-only audit JSONL helpers, write-time validation, create/update/pause/revoke APIs, load, effective-parameter resolver, expired / paused / revoked / invalid fallback auditing.
- `core/production_state/__init__.py` — re-export override helpers and constants.
- `core/production/loop.py` — reads effective tenant parameters once per cycle through `resolve_effective_parameters(...)` before building the scoring-agent config.
- `core/scoring/email_risk_scoring_agent.py` — no behavioral change required; Phase 1.4 already accepts the three lift config fields.
- `tests/test_tenant_parameter_overrides.py` — 15 tests covering all §10 gate criteria plus the five §11 locked decisions.
- `core/production_state/tenant_override_operator.py` — operator CLI (`create`, `pause`, `revoke`, `effective`, `audit`, `show`); not imported by agent or loop code.
- `tests/test_tenant_override_operator_cli.py` — 9 CLI integration tests.
- `4. Product_Roadmap/Tenant_Override_Operator_Runbook.md` — operator command reference.

### Evidence-package visibility landing (2026-05-22)

- `core/production_state/effective_parameters_report.py` — read-only Effective Parameter Report builder. It joins signed policy state, on-disk tenant override state, and recent override audit events into an MSP-facing report.
- `RecordType.EFFECTIVE_PARAMETERS_REPORT`, `EffectiveParameterProvenance`, and `EffectiveParametersReportPayload` — schema surface for appending the report to future evidence chains.
- `core/orchestrator/routes.py::submit_effective_parameters_report` and registry agent `evidence_reporting_001` — controlled production write path for future evidence-package append.
- `tenant_override_operator report` — text / markdown / json report (`--format`, `--at`, `--audit-limit`, `--out`) for signed baseline vs tenant override vs effective values with per-key provenance.
- `tests/test_effective_parameters_report.py` — 18 tests covering provenance per key, active/paused/revoked/expired/invalid override, audit tail ordering/limit, text/markdown/json renderers, CLI report subcommand, and `--out` file write.

Tracking docs:

- `MASTER_INDEX.md`
- `PROJECT_HANDSHAKE.md`
- `PROJECT_ACTIVITY_LOG.md`
- `Month_6_Closeout_Readiness.md`

## §10 Gate Criteria

Minimum Month 6 implementation gate:

1. Override accepts only reserved Phase 1.4 lift keys.
2. Override values are rejected at write time outside 0–25; no silent clamp.
3. Tenant A override cannot affect Tenant B.
4. Missing or invalid override falls back to signed policy state.
5. Expired / paused / revoked override is ignored.
6. Runtime at no override remains byte-identical to Month 5 scoring.
7. Audit trail records create / revoke / invalid-override events.
8. Full test suite remains green.

## §11 Decisions — LOCKED 2026-05-21

Matt approved all five choices. These are now implementation requirements:

| # | Decision | Locked choice | Implementation implication |
|---|---|---|---|
| 1 | Storage format | **Local JSON per tenant for v1, plus append-only audit events** | Store the current override as one JSON document per production tenant; every create/update/pause/revoke/invalid/expired event appends one local JSONL audit event. |
| 2 | Invalid-value behavior | **Reject at write time, not clamp silently** | Any operator write with an unexposed key, non-integer value, value outside 0–25, empty reason, or invalid approval fields fails before persistence and writes no active override. Runtime read paths may ignore corrupt on-disk state and audit the invalid read, but writer APIs must reject bad inputs. |
| 3 | Expiry | **Include optional `expires_at` in v1** | `expires_at` is nullable; expired active overrides are ignored at effective-parameter resolution time and append a `tenant_parameter_override_expired` audit event for operator review. |
| 4 | Approval model | **Require separate `requested_by` and `approved_by`** | Both fields are required, non-empty, and stored on both the current override JSON and every audit event. The implementation should reject a write where the same principal is used for both fields so approval is not self-attestation. |
| 5 | Key exposure | **Expose only the three Phase 1.4 lift keys** | Allowed override keys are exactly `fraud_risk_floor_lift`, `attachment_risk_floor_lift`, and `url_obfuscation_floor_lift`. Do **not** expose legacy `confidence_boost` through the tenant-override surface. |

## §12 Implementation Receipt

### Spec-first pass (2026-05-21)

- Customer-facing product sheet v1 at `Product_Sheets/Fraud_Detection_Product_Sheet.md`.
- Phase 2.1 implementation contract in this file (initial §11 decisions drafted; locked after Matt approval in the same session).
- Tracking updates in `MASTER_INDEX.md`, `PROJECT_HANDSHAKE.md`, and `PROJECT_ACTIVITY_LOG.md`.
- No runtime code changed in this pass; inherited baseline remained **419 / 419** from Month 5.

### Runtime landing (2026-05-21, §11 locked)

- `core/production_state/tenant_overrides.py` stores one current override JSON document per tenant at `production_state/tenant_overrides/<tenant>.override.json`.
- The same module appends local JSONL audit events at `production_state/tenant_overrides/<tenant>.override.audit.jsonl`.
- Write APIs reject invalid keys, non-int values, values outside 0–25, empty reason, empty requester/approver, or same requester/approver before persistence.
- Optional `expires_at` is supported; expired overrides are ignored and audited.
- Only `fraud_risk_floor_lift`, `attachment_risk_floor_lift`, and `url_obfuscation_floor_lift` are exposed.
- `run_production_cycle` now resolves code defaults → signed policy state → tenant override before constructing `EmailRiskScoringConfig`.
- `tests/test_tenant_parameter_overrides.py` adds 15 tests.

Verification:

```text
python -m pytest tests/test_tenant_parameter_overrides.py -q
15 passed in 0.29s
exit code 0

python -m pytest tests -q
452 passed in 8.47s
exit code 0
```

Known post-success Windows temp cleanup warning for `pytest-current` may still appear; it is not a functional failure.

## §13 Q2 Closeout (Months 4–6)

With Month 6 runtime landed, **Q2 (Months 4–6) is complete (3/3)**:

| Month | Phase | Deliverable | Runtime baseline contribution |
|---|---|---|---|
| Month 4 | Phase 1.3 Sandbox Training Pit | Four Red profiles, typed failure substrate, in-memory Blue path | +38 tests → **397** |
| Month 5 | Phase 1.4 Mutation Engine Specialisation | Typed mutation kinds, dual-boundary parameter keys, close-the-loop gate | +22 tests → **419** |
| Month 6 | Phase 2.1 Product sheet + per-tenant overrides | Customer-facing sheet + `tenant_overrides.py` + operator CLI + evidence visibility | +33 tests → **452** |

See `Month_5_Closeout_Readiness.md`, `Month_6_Closeout_Readiness.md`, and `PROJECT_HANDSHAKE.md` Completed items 161–163 for receipts.
