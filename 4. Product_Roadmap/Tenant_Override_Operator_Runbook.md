# Tenant Override Operator Runbook

**Purpose:** Day-to-day operator commands for Phase 2.1 per-tenant sensitivity lift overrides. No API budget required.

**Module:** `python -m core.production_state.tenant_override_operator`

**Working directory:** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation`

## Prerequisites

- `--blackboard-root` points at the tenant blackboard root (the directory that contains `production_state/`).
- `--tenant-id` is the production tenant id (for example `tenant_demo`).
- Write commands require **separate** `--requested-by` and `--approved-by` operator ids.
- Only these lift keys may be overridden: `fraud_risk_floor_lift`, `attachment_risk_floor_lift`, `url_obfuscation_floor_lift` (integers **0–25**).

## Commands

### 1. Create override

```powershell
python -m core.production_state.tenant_override_operator `
  --blackboard-root C:\path\to\blackboard `
  --tenant-id tenant_demo `
  create `
  --reason "Finance-heavy pilot through month-end" `
  --requested-by operator_a `
  --approved-by operator_b `
  --fraud-risk-floor-lift 8 `
  --expires-at 2026-06-30T23:59:59+00:00
```

Creates or replaces the active override. Optional `--attachment-risk-floor-lift` and `--url-obfuscation-floor-lift`.

### 2. Pause override

```powershell
python -m core.production_state.tenant_override_operator `
  --blackboard-root C:\path\to\blackboard `
  --tenant-id tenant_demo `
  pause `
  --reason "Hold during client review" `
  --requested-by operator_c `
  --approved-by operator_d
```

### 3. Revoke override

```powershell
python -m core.production_state.tenant_override_operator `
  --blackboard-root C:\path\to\blackboard `
  --tenant-id tenant_demo `
  revoke `
  --reason "Pilot ended" `
  --requested-by operator_e `
  --approved-by operator_f
```

### 4. Review effective parameters

```powershell
python -m core.production_state.tenant_override_operator `
  --blackboard-root C:\path\to\blackboard `
  --tenant-id tenant_demo `
  effective
```

Shows signed policy lift values, on-disk override state, whether the override would apply for scoring, and the effective lift parameters. Add `--format json` for scripting.

Optional `--at 2026-05-21T12:00:00+00:00` to evaluate expiry at a specific time.

### 5. Inspect audit history

```powershell
python -m core.production_state.tenant_override_operator `
  --blackboard-root C:\path\to\blackboard `
  --tenant-id tenant_demo `
  audit
```

Reads the append-only JSONL audit log at `production_state/tenant_overrides/<tenant>.override.audit.jsonl`. Use `--format json` for machine-readable export.

### 6. Generate evidence report

```powershell
python -m core.production_state.tenant_override_operator `
  --blackboard-root C:\path\to\blackboard `
  --tenant-id tenant_demo `
  report
```

Renders an MSP/client-shareable effective-parameter report. Default output is plain text; use `--format markdown` for a shareable document or `--format json` for scripting.

The report shows signed policy baseline, current tenant override, effective values, per-parameter provenance (`default` / `signed_policy` / `tenant_override`), whether the override is applied for scoring (with reason if not), and recent audit events.

```powershell
python -m core.production_state.tenant_override_operator `
  --blackboard-root C:\path\to\blackboard `
  --tenant-id tenant_demo `
  --format markdown `
  report `
  --at 2026-05-22T09:00:00+00:00 `
  --audit-limit 5 `
  --out C:\exports\tenant_demo_effective_report.md
```

- `--at` — optional evaluation time for expiry checks (timezone-aware ISO-8601).
- `--audit-limit` — number of most-recent audit events (default 5; use `0` to omit).
- `--out` — optional path to write the rendered report (stdout still prints).

### Show current override (helper)

```powershell
python -m core.production_state.tenant_override_operator `
  --blackboard-root C:\path\to\blackboard `
  --tenant-id tenant_demo `
  show
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Governance error (validation, missing override, etc.) |
| 2 | Usage error |

## Boundaries

- Operator CLI does **not** bypass signed policy promotion, Guardrail 11, or the kill switch.
- Invalid writes are rejected before persistence; production scoring ignores bad on-disk override state and audits the reason.

## Last updated

2026-05-22
