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

- `vf-003`: PASS

### Raw LLM Responses

#### vf-003

```json
{
  "summary": "Email requests processing of attached invoice using new remittance address (PO Box 9912, Victoria, BC) and states old instructions are no longer valid. Sender domain harbor-tech-billing.example includes billing suffix on vendor stem. Invoice attachment confirms same remit-to details and $22,180 total.",
  "action_items": [
    {
      "task": "Verify remittance address change with known Harbor Tech contacts via established channels",
      "owner": null,
      "due_date": null
    },
    {
      "task": "Do not process payment until address authenticity confirmed",
      "owner": null,
      "due_date": null
    }
  ],
  "risk_analysis": {
    "risk_score": 68,
    "risk_factors": ["new remittance instructions", "sender domain anomaly"],
    "phishing_signals": [],
    "urgency_signals": [],
    "financial_risk": "high",
    "vendor_fraud_score": 65,
    "wire_transfer_anomaly_score": 35,
    "invoice_authenticity_score": 40,
    "behavioral_deviation_flags": ["new_banking_instructions", "lookalike_sender_domain"]
  },
  "impersonation_analysis": {
    "impersonation_likelihood": 45,
    "suspicious_elements": ["billing-specific sender domain", "remittance change claim"],
    "sender_legitimacy_notes": "Domain uses -billing suffix on vendor name stem; no prior history indicated"
  },
  "recommended_action": "needs_review"
}
```
