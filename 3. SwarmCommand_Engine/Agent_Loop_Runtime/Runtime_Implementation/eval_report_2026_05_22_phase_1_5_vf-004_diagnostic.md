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

- `vf-004`: PASS

### Raw LLM Responses

#### vf-004

```json
{
  "summary": "Thread-hijack style vendor invoice request with 'Re:' subject and 'as discussed' phrasing but no quoted history or prior context. Sender domain matches vendor name in PDF; no banking changes or wire details present. Invoice attached requesting $13,770 payment upon receipt.",
  "action_items": [
    {
      "task": "Verify invoice and thread legitimacy with known Vendor Co contact",
      "owner": null,
      "due_date": null
    }
  ],
  "risk_analysis": {
    "risk_score": 70,
    "risk_factors": ["thread-hijack indicators", "no quoted prior context despite In-Reply-To header"],
    "phishing_signals": [],
    "urgency_signals": ["process today"],
    "financial_risk": "high",
    "vendor_fraud_score": 68,
    "wire_transfer_anomaly_score": 10,
    "invoice_authenticity_score": 35,
    "behavioral_deviation_flags": []
  },
  "impersonation_analysis": {
    "impersonation_likelihood": 10,
    "suspicious_elements": ["fabricated thread continuity"],
    "sender_legitimacy_notes": "Sender domain matches vendor identity in attachment; no executive impersonation"
  },
  "recommended_action": "needs_review"
}
```
