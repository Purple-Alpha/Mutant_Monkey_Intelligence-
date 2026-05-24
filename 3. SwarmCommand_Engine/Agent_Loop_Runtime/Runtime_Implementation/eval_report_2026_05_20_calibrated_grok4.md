## Fraud Eval Report — 40 cases

- Overall passed: 29 / 40
- Precision on fraud cases: 100.00%
- False positive rate on legit cases: 0.00%

### Pass Gate (Phase 1.1 deep dive §4.5)

| Criterion | Threshold | Actual | Met |
| --- | --- | --- | --- |
| Precision on fraud | >= 80% | 100.00% | YES |
| FPR on legit | <= 10% | 0.00% | YES |
| Per-fraud-subcategory recall | >= 60% each | invoice_authenticity_anomaly 33.33%; lookalike_sender 0.00%; vendor_invoice_fraud 20.00% | NO |

**Gate verdict:** FAIL

### Per-subcategory breakdown

| Subcategory | Total | Passed | Recall |
| --- | --- | --- | --- |
| executive_impersonation | 5 | 3 | 60.00% |
| header_inconsistency | 1 | 1 | 100.00% |
| invoice_authenticity_anomaly | 3 | 1 | 33.33% |
| legit_calendar | 3 | 3 | 100.00% |
| legit_hr | 2 | 2 | 100.00% |
| legit_internal | 5 | 5 | 100.00% |
| legit_newsletter | 2 | 2 | 100.00% |
| legit_vendor_invoice | 8 | 8 | 100.00% |
| lookalike_sender | 2 | 0 | 0.00% |
| vendor_invoice_fraud | 5 | 1 | 20.00% |
| wire_transfer_pressure | 4 | 3 | 75.00% |

### Case Failure Details

- `vf-001`: PASS
- `vf-002`: FAIL
  - assertion: `risk_score 48 < min 65`
  - assertion: `vendor_fraud_score 42 < min 60`
  - assertion: `wire_transfer_anomaly_score 25 < min 35`
- `vf-003`: FAIL
  - assertion: `risk_score 52 < min 70`
  - assertion: `vendor_fraud_score 48 < min 65`
  - assertion: `wire_transfer_anomaly_score 25 < min 30`
  - assertion: `invoice_authenticity_score 55 > max 50`
- `vf-004`: FAIL
  - assertion: `risk_score 42 < min 65`
  - assertion: `vendor_fraud_score 28 < min 60`
  - assertion: `wire_transfer_anomaly_score 15 < min 25`
  - assertion: `invoice_authenticity_score 72 > max 55`
- `vf-005`: FAIL
  - assertion: `risk_score 58 < min 75`
  - assertion: `vendor_fraud_score 32 < min 70`
  - assertion: `wire_transfer_anomaly_score 5 < min 45`
  - assertion: `invoice_authenticity_score 68 > max 50`
- `ei-001`: PASS
- `ei-002`: FAIL
  - assertion: `vendor_fraud_score 10 < min 15`
- `ei-003`: PASS
- `ei-004`: PASS
- `ei-005`: FAIL
  - assertion: `vendor_fraud_score 25 < min 35`
- `wt-001`: FAIL
  - assertion: `vendor_fraud_score 20 < min 30`
  - assertion: `behavioral_deviation_flags missing required ['new_banking_instructions']`
- `wt-002`: PASS
- `wt-003`: PASS
- `wt-004`: PASS
- `ia-001`: FAIL
  - assertion: `risk_score 62 < min 75`
  - assertion: `recommended_action 'needs_review' not in ['block']`
- `ia-002`: PASS
- `ia-003`: FAIL
  - assertion: `risk_score 58 < min 70`
  - assertion: `vendor_fraud_score 48 < min 50`
  - assertion: `invoice_authenticity_score 52 > max 45`
- `ls-001`: FAIL
  - assertion: `risk_score 62 < min 70`
  - assertion: `vendor_fraud_score 48 < min 60`
  - assertion: `behavioral_deviation_flags missing required ['lookalike_sender_domain']`
- `ls-002`: FAIL
  - assertion: `risk_score 62 < min 75`
  - assertion: `vendor_fraud_score 58 < min 60`
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
