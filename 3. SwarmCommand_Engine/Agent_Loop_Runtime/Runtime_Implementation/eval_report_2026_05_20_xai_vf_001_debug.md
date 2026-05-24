## Fraud Eval Report — 1 cases

- Overall passed: 1 / 1
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
| vendor_invoice_fraud | 1 | 1 | 100.00% |

### Case Failure Details

- `vf-001`: PASS

### Raw LLM Responses

#### vf-001

```json
{
  "summary": "Urgent payment request for invoice 4471 ($48,920) from billing@acme-manufacturing.co with new ACH details in body and attached PDF invoice.",
  "action_items": [
    {
      "task": "Verify new banking details directly with known Acme Manufacturing contact using established channels",
      "owner": null,
      "due_date": null
    }
  ],
  "risk_analysis": {
    "risk_score": 88,
    "risk_factors": ["new banking instructions", "urgent payment request", "sender domain anomaly"],
    "phishing_signals": ["lookalike sender domain"],
    "urgency_signals": ["missed last cycle", "push through today"],
    "financial_risk": "high",
    "vendor_fraud_score": 88,
    "wire_transfer_anomaly_score": 72,
    "invoice_authenticity_score": 25,
    "behavioral_deviation_flags": ["new_banking_instructions", "urgency_paired_with_finance", "lookalike_sender_domain"]
  },
  "impersonation_analysis": {
    "impersonation_likelihood": 65,
    "suspicious_elements": ["lookalike sender domain", "new ACH details embedded in invoice"],
    "sender_legitimacy_notes": "Domain acme-manufacturing.co differs from typical vendor corporate domain; first-time banking change request"
  },
  "recommended_action": "block"
}
```
