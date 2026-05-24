# NorthStar Inbox Shield — Effective Parameter Report

**Tenant:** acme-industries-demo
**Evaluated at:** 2026-05-23T15:30:00+00:00
**Signed policy version:** acme-demo-policy-v1

## Effective Lift Parameters

| Parameter | Effective Value | Source | Signed Policy | Tenant Override |
|---|---|---|---|---|
| `attachment_risk_floor_lift` | `0` | `signed_policy` | `0` | `(none)` |
| `fraud_risk_floor_lift` | `10` | `tenant_override` | `5` | `10` |
| `url_obfuscation_floor_lift` | `8` | `tenant_override` | `5` | `8` |

Other signed policy parameters (not tenant-tunable):

- `confidence_boost`: `0.2`
- `vendor_invoice_recall_floor`: `phase_1_5`

## Tenant Override

- **Status:** `active`
- **Reason:** Finance-heavy MSP pilot: raise invoice fraud and URL obfuscation review thresholds for the first 30 days.
- **Requested by:** `msp_operator_jane`
- **Approved by:** `msp_owner_dave`
- **Created at:** 2026-05-23T15:15:00+00:00
- **Expires at:** 2026-06-22T15:30:00+00:00
- **Override parameters:**
  - `fraud_risk_floor_lift`: `10`
  - `url_obfuscation_floor_lift`: `8`

**Override applied for scoring:** yes

## Recent Override Audit Events (last 2)

| Timestamp | Event | Requester | Approver | Source | Reason |
|---|---|---|---|---|---|
| 2026-05-23T15:15:00+00:00 | `tenant_parameter_override_updated` | `msp_operator_jane` | `msp_owner_dave` | `demo_effective_parameter_report_generator` | Finance-heavy MSP pilot: raise invoice fraud and URL obfuscation review thresholds for the first 30 days. |
| 2026-05-23T15:00:00+00:00 | `tenant_parameter_override_created` | `msp_operator_jane` | `msp_owner_dave` | `demo_effective_parameter_report_generator` | Initial pilot tuning for suspicious attachment-heavy invoices. |

