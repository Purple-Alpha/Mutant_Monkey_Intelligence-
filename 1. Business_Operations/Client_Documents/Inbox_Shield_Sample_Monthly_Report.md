# NorthStar Inbox Shield — Sample Monthly Report

**Prepared by:** NorthStar Security  
**Client:** Acme Industries Demo  
**MSP / Operator:** Example MSP Partner  
**Month:** May 2026  
**Version:** 1.0  
**Report type:** MSP-facing Inbox Shield monthly review

---

## 1. Executive Summary

This month, NorthStar Inbox Shield reviewed inbound email-risk patterns for the fictional `acme-industries-demo` tenant. The monitoring focus was vendor invoice fraud, new banking instructions, wire-transfer pressure, executive impersonation, lookalike sender domains, invoice authenticity anomalies, and early ransomware-precursor signals.

Overall monthly risk posture: **Elevated, finance-focused**.

The main driver was not general phishing volume. The main driver was a small number of payment-related emails that combined vendor-invoice language with urgency, new remittance instructions, or high dollar amounts. These are the exact patterns that tend to create business-loss risk for SMBs because they target finance workflow trust rather than employee curiosity.

NorthStar Inbox Shield remains a **decision-support and evidence layer**. It does not block, quarantine, delete, or remediate messages directly. Recommended action labels such as `needs_review` and `block` are advisory labels for MSP and client-side review workflows.

---

## 2. Monthly Snapshot

| Metric | Result | Notes |
|---|---:|---|
| Emails reviewed | 125 | Demo volume for monthly-report walkthrough |
| Emails marked `safe` | 103 | No meaningful payment, identity, attachment, or URL anomaly |
| Emails marked `needs_review` | 18 | Human review recommended before action |
| Emails marked `block` | 4 | Advisory label only; mailbox blocking is not performed by Inbox Shield today |
| Finance-related emails | 31 | Vendor invoices, payment reminders, remittance updates, wire language |
| High-risk finance emails | 7 | `risk_score >= 70` or strong vendor / wire signal |
| Legitimate vendor invoices | 24 | No new-bank, urgency, or sender-domain anomaly detected |
| False-positive review candidates | 2 | Useful for tuning review; no production policy change made silently |

---

## 3. Risk Category Breakdown

| Category | Count | Highest Score | Monthly Read |
|---|---:|---:|---|
| Vendor invoice fraud | 7 | 88 | Primary risk driver this month |
| New or unusual banking instructions | 5 | 88 | Requires out-of-band vendor verification |
| Wire-transfer pressure | 3 | 72 | Concentrated in finance and operations workflows |
| Executive impersonation | 2 | 81 | Low volume, high consequence |
| Lookalike sender domains | 4 | 88 | Mostly vendor-name variants and payment subdomains |
| Invoice authenticity anomalies | 3 | 70 | PDF-only remit details and inconsistent vendor context |
| Ransomware-precursor signals | 4 | 76 | Suspicious attachment / URL / credential-language overlays |

---

## 4. Top Findings

### Finding 1 — Vendor-invoice pressure concentrated in finance

Seven finance-related messages crossed the monthly review threshold. The strongest case combined a lookalike sender domain, urgent payment language, and new ACH details.

Example scoring pattern:

| Field | Value |
|---|---|
| `risk_score` | 88 |
| `vendor_fraud_score` | 88 |
| `wire_transfer_anomaly_score` | 72 |
| `invoice_authenticity_score` | 25 |
| `recommended_action` | `block` |
| `behavioral_deviation_flags` | `new_banking_instructions`, `urgency_paired_with_finance`, `lookalike_sender_domain` |

Recommended business action:

- Do not process payment from email instructions alone.
- Verify banking changes through a known phone number or existing vendor portal.
- Treat future first-time or changed-remittance invoices as `needs_review` by default.

### Finding 2 — PDF-only remittance details need a standard review step

Some invoices did not place remittance changes in the email body. The banking instruction appeared only inside the PDF attachment. This is a realistic vendor-invoice fraud pattern because it can look cleaner to a busy AP team.

Recommended business action:

- Add an AP checklist item: **"If banking details are in an attachment only, verify out-of-band before approval."**
- Require a second approver for any first invoice after onboarding.

### Finding 3 — Ransomware-precursor signals were present but not dominant

Four messages included suspicious attachment, URL, or credential-language signals. None required direct remediation by Inbox Shield because the current product scope is analysis and reporting only. The signals are still useful for MSP triage and monthly client education.

Recommended business action:

- Keep attachment inspection and URL-review awareness in the next training session.
- Escalate repeated suspicious attachment patterns to the MSP security stack owner.

---

## 5. Effective Parameter Summary

This tenant used a client-specific sensitivity override during the month. The real generated Effective Parameter Report for this demo tenant is available at:

`1. Business_Operations/Client_Documents/Generated/Acme_Effective_Parameter_Report_Demo.md`

Summary:

| Parameter | Effective Value | Source | Signed Policy | Tenant Override |
|---|---:|---|---:|---:|
| `attachment_risk_floor_lift` | 0 | `signed_policy` | 0 | none |
| `fraud_risk_floor_lift` | 10 | `tenant_override` | 5 | 10 |
| `url_obfuscation_floor_lift` | 8 | `tenant_override` | 5 | 8 |

Interpretation:

- Fraud and URL-obfuscation sensitivity were raised for this finance-heavy pilot.
- Attachment sensitivity stayed at the signed policy baseline.
- The override was approved with separate requester / approver attribution.
- No change was silent; the full audit trail is in the generated report.

---

## 6. Recommended Client Actions

| Priority | Recommendation | Owner |
|---|---|---|
| High | Require out-of-band verification for any vendor banking change, even if the sender appears known. | Client finance lead |
| High | Add second-person approval for first invoices after onboarding and for invoices above the client's high-dollar threshold. | Client finance lead + MSP |
| Medium | Review lookalike sender-domain examples with AP staff during the next 15-minute awareness session. | MSP operator |
| Medium | Keep current fraud-risk override active for the remaining pilot window. | MSP operator |
| Low | Re-check false-positive candidates during the next monthly review before changing signed baseline policy. | MSP operator |

---

## 7. MSP Operator Notes

- This report is appropriate for a monthly business review or cyber-insurance evidence file.
- NorthStar Inbox Shield does not directly enforce mailbox actions. If the MSP chooses to block, quarantine, or delete mail through Microsoft 365, Google Workspace, or another mail gateway, that action is outside the current Inbox Shield runtime.
- The generated Effective Parameter Report should be attached when discussing why this tenant had elevated fraud sensitivity during the month.
- The client should understand that `block` is an advisory label in the report, not proof that mailbox-level blocking occurred.

---

## 8. Evidence Package

Attach or reference these artifacts for the monthly record:

| Artifact | Purpose |
|---|---|
| `MSP_Discovery_Evidence_Package.md` | Broader MSP proof package: eval results, guardrails, pilot offer, source-of-truth appendix |
| `Generated/Acme_Effective_Parameter_Report_Demo.md` | Real generated per-tenant effective-parameter report |
| `eval_report_2026_05_22_phase_1_5_vf-00{1..5}_diagnostic.md` | Vendor-invoice post-patch diagnostic proof |
| `Fraud_Detection_Product_Sheet.md` | Client-safe claim boundary and SMB tier matrix |

---

## 9. Safe Claim Boundary

Use this language with the client:

- "NorthStar identified and reported suspicious email-fraud patterns this month."
- "NorthStar helped prioritize which payment-related emails needed human review."
- "NorthStar provided evidence-friendly reporting for the MSP and client leadership."

Avoid this language:

- "NorthStar stopped all phishing."
- "NorthStar guaranteed fraud prevention."
- "NorthStar quarantined malicious email."
- "NorthStar replaced finance approval controls."

---

## 10. Next Monthly Review

Next review focus:

1. Confirm whether the fraud-risk override reduced missed vendor-invoice patterns without creating excess false positives.
2. Review any payment emails marked `needs_review` that the client later confirmed as legitimate.
3. Decide whether to continue, lower, or revoke the tenant override before expiry.
4. Compare finance-related risk volume against this month to identify whether the elevated posture is improving, stable, or worsening.
