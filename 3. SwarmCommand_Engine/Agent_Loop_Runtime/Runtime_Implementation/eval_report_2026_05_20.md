## Fraud Eval Report — 40 cases

- Overall passed: 0 / 40
- Precision on fraud cases: 0.00%
- False positive rate on legit cases: 0.00%

### Pass Gate (Phase 1.1 deep dive §4.5)

| Criterion | Threshold | Actual | Met |
| --- | --- | --- | --- |
| Precision on fraud | >= 80% | 0.00% | NO |
| FPR on legit | <= 10% | 0.00% | YES |
| Per-fraud-subcategory recall | >= 60% each | executive_impersonation 0.00%; header_inconsistency 0.00%; invoice_authenticity_anomaly 0.00%; lookalike_sender 0.00%; vendor_invoice_fraud 0.00%; wire_transfer_pressure 0.00% | NO |

**Gate verdict:** FAIL

### Per-subcategory breakdown

| Subcategory | Total | Passed | Recall |
| --- | --- | --- | --- |
| executive_impersonation | 5 | 0 | 0.00% |
| header_inconsistency | 1 | 0 | 0.00% |
| invoice_authenticity_anomaly | 3 | 0 | 0.00% |
| legit_calendar | 3 | 0 | 0.00% |
| legit_hr | 2 | 0 | 0.00% |
| legit_internal | 5 | 0 | 0.00% |
| legit_newsletter | 2 | 0 | 0.00% |
| legit_vendor_invoice | 8 | 0 | 0.00% |
| lookalike_sender | 2 | 0 | 0.00% |
| vendor_invoice_fraud | 5 | 0 | 0.00% |
| wire_transfer_pressure | 4 | 0 | 0.00% |
