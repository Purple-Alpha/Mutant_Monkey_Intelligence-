## Fraud Eval Report — 40 cases

- Overall passed: 36 / 40
- Precision on fraud cases: 100.00%
- False positive rate on legit cases: 0.00%

### Pass Gate (Phase 1.1 deep dive §4.5)

| Criterion | Threshold | Actual | Met |
| --- | --- | --- | --- |
| Precision on fraud | >= 80% | 100.00% | YES |
| FPR on legit | <= 10% | 0.00% | YES |
| Per-fraud-subcategory recall | >= 60% each | all fraud subcategories meet floor | YES |

**Gate verdict:** PASS

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
| vendor_invoice_fraud | 5 | 3 | 60.00% |
| wire_transfer_pressure | 4 | 3 | 75.00% |

### Case Failure Details

- `vf-001`: PASS
- `vf-002`: FAIL
  - assertion: `behavioral_deviation_flags missing required ['first_time_sender_with_financial_ask']`
- `vf-003`: PASS
- `vf-004`: PASS
- `vf-005`: FAIL
  - assertion: `risk_score 52 < min 75`
  - assertion: `vendor_fraud_score 45 < min 70`
  - assertion: `wire_transfer_anomaly_score 15 < min 45`
  - assertion: `invoice_authenticity_score 68 > max 50`
- `ei-001`: PASS
- `ei-002`: PASS
- `ei-003`: PASS
- `ei-004`: PASS
- `ei-005`: FAIL
  - assertion: `risk_score 78 < min 80`
- `wt-001`: PASS
- `wt-002`: PASS
- `wt-003`: PASS
- `wt-004`: FAIL
  - assertion: `risk_score 42 < min 45`
  - assertion: `wire_transfer_anomaly_score 38 < min 40`
- `ia-001`: PASS
- `ia-002`: PASS
- `ia-003`: PASS
- `ls-001`: PASS
- `ls-002`: PASS
- `hi-001`: PASS
- `lv-001`: PASS
- `lv-002`: PASS
- `lv-003`: PASS
- `lv-004`: PASS
- `lv-005`: PASS
- `lv-006`: PASS
- `lv-007`: PASS
- `lv-008`: PASS
- `li-001`: PASS
- `li-002`: PASS
- `li-003`: PASS
- `li-004`: PASS
- `li-005`: PASS
- `lc-001`: PASS
- `lc-002`: PASS
- `lc-003`: PASS
- `lh-001`: PASS
- `lh-002`: PASS
- `ln-001`: PASS
- `ln-002`: PASS
