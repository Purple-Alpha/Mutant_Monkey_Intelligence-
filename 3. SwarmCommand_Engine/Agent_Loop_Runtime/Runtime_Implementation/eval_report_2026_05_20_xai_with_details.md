## Fraud Eval Report — 40 cases

- Overall passed: 24 / 40
- Precision on fraud cases: 100.00%
- False positive rate on legit cases: 0.00%

### Pass Gate (Phase 1.1 deep dive §4.5)

| Criterion | Threshold | Actual | Met |
| --- | --- | --- | --- |
| Precision on fraud | >= 80% | 100.00% | YES |
| FPR on legit | <= 10% | 0.00% | YES |
| Per-fraud-subcategory recall | >= 60% each | executive_impersonation 40.00%; header_inconsistency 0.00%; invoice_authenticity_anomaly 0.00%; lookalike_sender 0.00%; vendor_invoice_fraud 20.00%; wire_transfer_pressure 25.00% | NO |

**Gate verdict:** FAIL

### Per-subcategory breakdown

| Subcategory | Total | Passed | Recall |
| --- | --- | --- | --- |
| executive_impersonation | 5 | 2 | 40.00% |
| header_inconsistency | 1 | 0 | 0.00% |
| invoice_authenticity_anomaly | 3 | 0 | 0.00% |
| legit_calendar | 3 | 3 | 100.00% |
| legit_hr | 2 | 2 | 100.00% |
| legit_internal | 5 | 5 | 100.00% |
| legit_newsletter | 2 | 2 | 100.00% |
| legit_vendor_invoice | 8 | 8 | 100.00% |
| lookalike_sender | 2 | 0 | 0.00% |
| vendor_invoice_fraud | 5 | 1 | 20.00% |
| wire_transfer_pressure | 4 | 1 | 25.00% |

### Case Failure Details

- `vf-001`: PASS
- `vf-002`: FAIL
  - assertion: `risk_score 48 < min 65`
  - assertion: `vendor_fraud_score 42 < min 60`
  - assertion: `behavioral_deviation_flags missing ['lookalike_sender_domain']`
- `vf-003`: FAIL
  - assertion: `risk_score 52 < min 70`
  - assertion: `vendor_fraud_score 45 < min 65`
  - assertion: `wire_transfer_anomaly_score 25 < min 30`
  - assertion: `invoice_authenticity_score 55 > max 50`
  - assertion: `behavioral_deviation_flags missing ['first_time_sender_with_financial_ask']`
- `vf-004`: FAIL
  - assertion: `risk_score 42 < min 65`
  - assertion: `vendor_fraud_score 28 < min 60`
  - assertion: `wire_transfer_anomaly_score 15 < min 25`
  - assertion: `invoice_authenticity_score 68 > max 55`
  - assertion: `behavioral_deviation_flags missing ['first_time_sender_with_financial_ask']; extra ['urgency_paired_with_finance']`
- `vf-005`: FAIL
  - assertion: `risk_score 58 < min 75`
  - assertion: `vendor_fraud_score 42 < min 70`
  - assertion: `wire_transfer_anomaly_score 15 < min 45`
  - assertion: `invoice_authenticity_score 68 > max 50`
  - assertion: `behavioral_deviation_flags missing ['first_time_sender_with_financial_ask', 'unusual_dollar_amount']`
- `ei-001`: PASS
- `ei-002`: FAIL
  - assertion: `vendor_fraud_score 15 < min 20`
- `ei-003`: PASS
- `ei-004`: FAIL
  - assertion: `behavioral_deviation_flags extra ['first_time_sender_with_financial_ask']`
- `ei-005`: FAIL
  - assertion: `behavioral_deviation_flags extra ['out_of_band_pressure']`
- `wt-001`: FAIL
  - assertion: `behavioral_deviation_flags missing ['first_time_sender_with_financial_ask', 'new_banking_instructions']; extra ['out_of_band_pressure']`
- `wt-002`: PASS
- `wt-003`: FAIL
  - assertion: `behavioral_deviation_flags missing ['first_time_sender_with_financial_ask']; extra ['new_banking_instructions']`
- `wt-004`: FAIL
  - assertion: `behavioral_deviation_flags missing ['first_time_sender_with_financial_ask']`
- `ia-001`: FAIL
  - assertion: `risk_score 72 < min 75`
  - assertion: `recommended_action 'needs_review' not in ['block']`
  - assertion: `behavioral_deviation_flags missing ['first_time_sender_with_financial_ask']; extra ['new_banking_instructions']`
- `ia-002`: FAIL
  - assertion: `vendor_fraud_score 45 < min 50`
- `ia-003`: FAIL
  - assertion: `risk_score 62 < min 70`
  - assertion: `vendor_fraud_score 52 < min 55`
  - assertion: `behavioral_deviation_flags missing ['first_time_sender_with_financial_ask']`
- `ls-001`: FAIL
  - assertion: `risk_score 48 < min 70`
  - assertion: `vendor_fraud_score 42 < min 60`
  - assertion: `behavioral_deviation_flags missing ['first_time_sender_with_financial_ask', 'lookalike_sender_domain']`
- `ls-002`: FAIL
  - assertion: `risk_score 62 < min 75`
  - assertion: `vendor_fraud_score 55 < min 60`
  - assertion: `behavioral_deviation_flags missing ['first_time_sender_with_financial_ask']`
- `hi-001`: FAIL
  - assertion: `vendor_fraud_score 52 < min 55`
  - assertion: `behavioral_deviation_flags missing ['first_time_sender_with_financial_ask']; extra ['urgency_paired_with_finance']`
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
