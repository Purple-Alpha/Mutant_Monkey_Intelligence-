## Fraud Eval Report — 40 cases

- Overall passed: 36 / 40
- Precision on fraud cases: 100.00%
- False positive rate on legit cases: 0.00%

### Pass Gate (Phase 1.1 deep dive §4.5)

| Criterion | Threshold | Actual | Met |
| --- | --- | --- | --- |
| Precision on fraud | >= 80% | 100.00% | YES |
| FPR on legit | <= 10% | 0.00% | YES |
| Per-fraud-subcategory recall | >= 60% each | vendor_invoice_fraud 40.00% | NO |

**Gate verdict:** FAIL

### Per-subcategory breakdown

| Subcategory | Total | Passed | Recall |
| --- | --- | --- | --- |
| executive_impersonation | 5 | 4 | 80.00% |
| header_inconsistency | 1 | 1 | 100.00% |
| invoice_authenticity_anomaly | 3 | 3 | 100.00% |
| legit_calendar | 3 | 3 | 100.00% |
| legit_hr | 2 | 2 | 100.00% |
| legit_internal | 5 | 5 | 100.00% |
| legit_newsletter | 2 | 2 | 100.00% |
| legit_vendor_invoice | 8 | 8 | 100.00% |
| lookalike_sender | 2 | 2 | 100.00% |
| vendor_invoice_fraud | 5 | 2 | 40.00% |
| wire_transfer_pressure | 4 | 4 | 100.00% |
