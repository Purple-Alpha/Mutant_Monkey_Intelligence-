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
  "summary": "Sender claims to be Acme Manufacturing requesting urgent payment of $48,920 for invoice 4471 with new ACH details provided in both body and attached PDF.",
  "action_items": [
    {
      "task": "Verify invoice and banking details with known Acme Manufacturing contacts via established channels",
      "owner": null,
      "due_date": null
    },
    {
      "task": "Do not process payment or reply with confirmation",
      "owner": null,
      "due_date": null
    }
  ],
  "risk_analysis": {
    "risk_score": 88,
    "risk_factors": ["new banking instructions", "urgent payment request", "sender domain anomaly"],
    "phishing_signals": ["lookalike sender domain"],
    "urgency_signals": ["push through today", "missed last cycle"],
    "financial_risk": "high",
    "vendor_fraud_score": 88,
    "wire_transfer_anomaly_score": 72,
    "invoice_authenticity_score": 25,
    "behavioral_deviation_flags": ["new_banking_instructions", "urgency_paired_with_finance", "lookalike_sender_domain"]
  },
  "impersonation_analysis": {
    "impersonation_likelihood": 75,
    "suspicious_elements": ["domain .co instead of expected corporate domain", "new ACH details only in this message"],
    "sender_legitimacy_notes": "Sender domain does not match typical Acme Manufacturing corporate domains"
  },
  "recommended_action": "block"
}
```
