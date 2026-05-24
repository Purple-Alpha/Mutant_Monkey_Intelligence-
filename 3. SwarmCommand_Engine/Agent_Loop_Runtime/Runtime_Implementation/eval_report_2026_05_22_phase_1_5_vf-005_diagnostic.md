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

- `vf-005`: PASS

### Raw LLM Responses

#### vf-005

```json
{
  "summary": "High-value emergency invoice for $96,400 from Pacific Logistics requesting same-day approval to avoid shipment delay. Sender domain matches vendor name with no banking changes or thread anomalies. Attachment is a PDF invoice with matching details.",
  "action_items": [
    {
      "task": "Review and verify invoice authenticity and shipment urgency with operations",
      "owner": "AP team",
      "due_date": "2026-06-15"
    }
  ],
  "risk_analysis": {
    "risk_score": 78,
    "risk_factors": ["high dollar amount", "end-of-day approval pressure", "emergency shipment claim"],
    "phishing_signals": [],
    "urgency_signals": ["approve before end of day", "shipment not delayed"],
    "financial_risk": "high",
    "vendor_fraud_score": 70,
    "wire_transfer_anomaly_score": 45,
    "invoice_authenticity_score": 45,
    "behavioral_deviation_flags": ["unusual_dollar_amount", "urgency_paired_with_finance"]
  },
  "impersonation_analysis": {
    "impersonation_likelihood": 10,
    "suspicious_elements": [],
    "sender_legitimacy_notes": "Sender domain pacific-logistics.example matches vendor name Pacific Logistics with no anomalies"
  },
  "recommended_action": "needs_review"
}
```
