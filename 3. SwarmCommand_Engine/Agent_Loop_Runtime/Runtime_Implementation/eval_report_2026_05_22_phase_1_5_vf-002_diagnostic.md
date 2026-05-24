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

- `vf-002`: PASS

### Raw LLM Responses

#### vf-002

```json
{
  "summary": "First invoice after onboarding from billing@trusted-vendor-payments.example requests remittance instructions only in attached PDF for $18,240.",
  "action_items": [
    {
      "task": "Verify vendor onboarding and banking details via known contact",
      "owner": null,
      "due_date": null
    },
    {
      "task": "Do not process payment until confirmed",
      "owner": null,
      "due_date": null
    }
  ],
  "risk_analysis": {
    "risk_score": 65,
    "risk_factors": ["first invoice after onboarding", "remittance instructions only in PDF"],
    "phishing_signals": [],
    "urgency_signals": [],
    "financial_risk": "medium",
    "vendor_fraud_score": 60,
    "wire_transfer_anomaly_score": 40,
    "invoice_authenticity_score": 45,
    "behavioral_deviation_flags": ["first_time_sender_with_financial_ask", "new_banking_instructions", "lookalike_sender_domain"]
  },
  "impersonation_analysis": {
    "impersonation_likelihood": 25,
    "suspicious_elements": ["payments subdomain on vendor stem"],
    "sender_legitimacy_notes": "Domain anomaly present but no executive impersonation"
  },
  "recommended_action": "needs_review"
}
```
