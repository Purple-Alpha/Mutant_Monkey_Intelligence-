# Month 6 Closeout Readiness

**Status:** Month 6 Phase 2.1 (Fraud Detection Product Sheet + Per-Tenant Parameter Overrides + Evidence Visibility) is complete and verified as of 2026-05-22.

**Build track:** SwarmCommand Agent Loop Runtime + NorthStar Inbox Shield + Fraud / Ransomware Specialization.

**Runtime baseline:** **461 tests passing** (exit code 0). **+15** override-runtime tests in `tests/test_tenant_parameter_overrides.py`; **+9** operator-CLI tests in `tests/test_tenant_override_operator_cli.py`; **+18** evidence-report tests in `tests/test_effective_parameters_report.py`.

**Inherited baseline:** Month 5 Phase 1.4 closed the mutation loop at 419 / 419 tests. Month 6 adds per-tenant override resolution without changing the Phase 1.4 scoring-agent contract.

## Purpose

This file is the Month 6 closeout checkpoint. Month 6 had two jobs:

1. Translate the internal fraud-detection runtime into a safe customer-facing product sheet.
2. Add a per-tenant override layer for the three Phase 1.4 sensitivity lift keys while preserving the signed policy baseline, auditability, and bounded production surface.

Both are now complete.

## Five §11 Decisions — Locked and Landed

All five Matt-approved decisions from `Phase_2_1_Fraud_Detection_Product_Sheet_And_Tenant_Overrides.md` §11 are implemented and pinned by tests:

| # | Decision | Landing | Test pin |
|---|---|---|---|
| 1 | Local JSON per tenant for v1, plus append-only audit events | `core/production_state/tenant_overrides.py` writes `<tenant>.override.json` and `<tenant>.override.audit.jsonl` | `test_create_override_writes_local_json_and_append_only_audit`, `test_update_override_appends_updated_audit_event` |
| 2 | Reject invalid values at write time; do not clamp silently | Writer API raises `GovernanceError` before persistence | `test_invalid_values_are_rejected_at_write_time_not_clamped` |
| 3 | Optional `expires_at` in v1 | `TenantParameterOverride.expires_at`; resolver ignores expired overrides and audits | `test_expired_override_is_ignored_and_audited` |
| 4 | Require separate `requested_by` and `approved_by` | Both required; same principal rejected | `test_override_write_requires_separate_requester_and_approver` |
| 5 | Expose only the three Phase 1.4 lift keys | `EXPOSED_TENANT_OVERRIDE_KEYS` excludes legacy `confidence_boost` | `test_exposed_tenant_override_keys_are_only_phase_1_4_lifts` |

## Runtime Deliverables

1. **Product sheet**
   - `4. Product_Roadmap/Product_Sheets/Fraud_Detection_Product_Sheet.md`.
   - Plain-English SMB / MSP positioning.
   - Safe claim boundary: analysis, scoring, reporting, recommendations, evidence support only; no blocking, quarantine, remediation, URL fetching, attachment execution, or customer self-serve portal claims.

2. **Per-tenant override module**
   - `core/production_state/tenant_overrides.py`.
   - `TenantParameterOverride` frozen dataclass.
   - `TenantOverrideAuditEvent` frozen dataclass.
   - Local JSON current-state file per tenant.
   - Append-only local JSONL audit file per tenant.
   - Create / update / pause / revoke APIs.
   - Effective-parameter resolver: code defaults -> signed policy state -> valid active tenant override.
   - Missing / invalid / expired / paused / revoked overrides are ignored and audited, never applied.

3. **Production loop wiring**
   - `core/production/loop.py` now calls `resolve_effective_parameters(...)` before building `EmailRiskScoringConfig`.
   - No override means the Month 5 path is byte-identical to signed policy state.
   - Valid tenant override can raise only the three Phase 1.4 lift values for that tenant.

4. **Tests**
   - `tests/test_tenant_parameter_overrides.py`.
   - 15 tests covering storage, audit, write-time rejection, approval separation, tenant isolation, expiry, revoked fallback, invalid-on-disk fallback, no-override identity, and production-loop scoring effect.

5. **Evidence visibility**
   - `core/production_state/effective_parameters_report.py`.
   - Read-only builder that joins signed policy state, tenant override state, and recent audit events.
   - `RecordType.EFFECTIVE_PARAMETERS_REPORT` + payload schema allow future evidence-chain append.
   - `tenant_override_operator report` emits Markdown / JSON with per-parameter provenance.
   - `tests/test_effective_parameters_report.py` adds 9 tests.

## Verification

```text
python -m pytest tests/test_tenant_parameter_overrides.py -q
15 passed in 0.29s
exit code 0

python -m pytest tests -q
452 passed in 8.47s
exit code 0
```

The known post-success Windows `pytest-current` cleanup warning may appear and remains non-functional.

## Boundary Held

Phase 2.1 does not expose:

- `confidence_boost`.
- Prompt edits.
- Mutation-kind edits.
- Agent registry or role edits.
- Kill-switch, Guardrail 11, promotion-pipeline, or rollback bypasses.
- Any live email, URL, DNS, attachment execution, or external-resource action.

## Q2 Closeout — Months 4–6 Complete (3/3)

| Month | Phase | Status | Key proof |
|---|---|---|---|
| 4 | Phase 1.3 Sandbox Training Pit | LANDED | Seven §7 gate tests; 397 tests |
| 5 | Phase 1.4 Mutation Engine Specialisation | LANDED | Close-the-loop end-to-end; 419 tests |
| 6 | Phase 2.1 Product sheet + per-tenant overrides + evidence visibility | LANDED | 42 Phase 2.1 tests; **461 tests** |

Q1 (Months 1–3) and Q2 (Months 4–6) operator closeout gates for the fraud/ransomware specialization spine are both satisfied on the current runtime baseline.

## Operator Workflow — LANDED

`python -m core.production_state.tenant_override_operator` (from `Runtime_Implementation/`):

| Subcommand | Purpose |
|---|---|
| `create` | Create or replace active override (three lift flags, optional expiry) |
| `pause` | Pause without deleting audit history |
| `revoke` | Revoke override |
| `effective` | Review signed policy vs override vs effective lift parameters |
| `report` | Render MSP-facing Markdown / JSON evidence report with provenance |
| `audit` | Inspect append-only override audit JSONL |
| `show` | Show current on-disk override record |

Runbook: `4. Product_Roadmap/Tenant_Override_Operator_Runbook.md`. Tests: `tests/test_tenant_override_operator_cli.py` (9 tests) and `tests/test_effective_parameters_report.py` (18 tests). CLI `report` subcommand: text / markdown / json with `--out` and `--audit-limit`. Baseline after evidence visibility landing: **461** tests.

## Conditions for Next Phase

Likely next work:

1. SMB tier matrix in `Product_Sheets/Fraud_Detection_Product_Sheet.md`.
2. One-hour autonomous trigger scanner if autonomy returns to the active thread.
3. Phase 1.5 A/B numeric improvement proof on the 40-case fraud-eval dataset if API budget is approved.
4. Bucket E live-eval diagnostics after a promoted `fraud_pattern_threshold` mutation.

## Last Updated

2026-05-22
