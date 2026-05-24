# NorthStar Security MVP Dashboard Design Specification

## 1. Introduction

This document outlines the revised design for the NorthStar Security MVP Dashboard, tailored to accurately reflect the current capabilities of NorthStar Inbox Shield. The dashboard is designed to provide small and mid-sized business owners, office managers, MSP partners, and non-technical leadership with a clear, trust-focused, and actionable overview of their human-layer cyber risk.

It presents email-risk analysis and reporting in plain English, avoiding technical jargon and a dark security aesthetic.

## 2. MVP Scope

The NorthStar MVP Dashboard focuses on presenting analysis and reporting of email-borne threats. It provides insights into detected risks, trends, and recommended business actions based on the analysis performed by NorthStar Inbox Shield.

## 3. Explicit Non-Goals

Based on the current NorthStar Inbox Shield runtime, the dashboard does not include:

- Email blocking, quarantining, neutralizing, or remediation. The system currently analyzes and reports on risk; it does not take direct action on emails.
- Secure portal access. Direct access to a secure portal for detailed incident review is not part of the current MVP.

These capabilities are future enhancements.

## 4. Audience and Purpose

Audience:

- SMB owner
- Office manager
- MSP partner
- Non-technical leadership

Purpose:

To show monthly human-layer risk in plain English, serving as a practical SMB security report rather than a SaaS landing page.

## 5. Design Principles

- Plain English and non-technical.
- Trust-focused, not scary.
- No dark hacker aesthetic.
- Dense enough for operational use.
- Practical SMB security report feel.

## 6. Page Layout

```text
+-------------------------------------------------------------------+
| NorthStar Security Dashboard                                      |
+-------------------------------------------------------------------+
| [Executive Summary]                                               |
|                                                                   |
| [Key Metrics Overview]                                            |
|   - Total Emails Analyzed                                         |
|   - High-Risk Emails Identified                                   |
|                                                                   |
| [Fraud Categories Detected]                                       |
|   - Vendor Invoice Fraud                                          |
|   - Wire-Transfer Pressure                                        |
|   - Lookalike Sender Domains                                      |
|   - Invoice Authenticity Anomalies                                |
|   - Executive Impersonation                                       |
|   - Header Inconsistency                                          |
|   - Phishing                                                      |
|   - Ransomware Precursor Signals                                  |
|                                                                   |
| [Top Risk Signals]                                                |
|                                                                   |
| [Recommended Actions]                                             |
|                                                                   |
| [Evidence Package Status]                                         |
|                                                                   |
| [Month-over-Month Trend]                                          |
|                                                                   |
| [Client-Ready Leadership Summary]                                 |
|                                                                   |
| [Operator Notes (Internal Only)]                                  |
+-------------------------------------------------------------------+
```

## 7. Data-Field Mapping

| Dashboard Field | Schema Field | Description |
| --- | --- | --- |
| Overall Risk Score | `risk_analysis.risk_score` | Aggregated score indicating the overall risk level of an email. |
| Recommended Action | `recommended_action` | Suggested business action based on detected risk. |
| Vendor Fraud Score | `risk_analysis.vendor_fraud_score` | Score indicating likelihood of vendor invoice fraud. |
| Wire Transfer Anomaly Score | `risk_analysis.wire_transfer_anomaly_score` | Score indicating likelihood of wire-transfer pressure or fraud. |
| Invoice Authenticity Score | `risk_analysis.invoice_authenticity_score` | Score indicating the authenticity of an invoice. |
| Behavioral Deviation Flags | `risk_analysis.behavioral_deviation_flags` | Flags for unusual sender or payment behavior. |
| Impersonation Likelihood | `impersonation_analysis.impersonation_likelihood` | Score indicating likelihood of executive, vendor, or brand impersonation. |
| General Risk Factors | `risk_analysis.risk_factors` | General indicators of risk. |
| Phishing Signals | `risk_analysis.phishing_signals` | Specific signals indicating a phishing attempt. |
| Urgency Signals | `risk_analysis.urgency_signals` | Signals indicating undue pressure or urgency. |
| Financial Risk | `risk_analysis.financial_risk` | Indicators related to potential financial loss. |

## 8. Dashboard Sections

### 8.1 Executive Summary

Purpose:

Provide a concise, high-level overview of the organization's human-layer security posture for the reporting period.

Data fields:

- Overall security posture, such as `Good`, `Improving`, or `Needs Attention`, derived from `risk_analysis.risk_score`.
- Key highlights or significant changes from the previous period.

Example copy:

> This month, NorthStar Security continued to provide critical insights into evolving email threats. Our analysis shows a Good overall security posture, with a notable reduction in identified high-risk email interactions compared to last month. We identified several sophisticated phishing attempts and potential fraud attempts, giving your team the information needed to mitigate these risks.

### 8.2 Total Emails Analyzed

Purpose:

Show the volume of email traffic processed by NorthStar Inbox Shield.

Data fields:

- Total number of emails analyzed.
- Percentage change from the previous month.

Example copy:

> NorthStar Inbox Shield analyzed 12,500 emails this month, a 5% increase from the previous period, supporting continuous visibility across your inbound communications.

### 8.3 High-Risk Emails Identified

Purpose:

Highlight emails that posed significant risk and were identified through analysis.

Data fields:

- Total number of high-risk emails identified, based on `risk_analysis.risk_score`.
- Breakdown by risk level, such as critical, high, or medium.
- Percentage of high-risk emails relative to total emails analyzed.

Example copy:

> Out of all emails analyzed, 25 were identified as high-risk, representing 0.2% of your total inbound mail. These emails were flagged due to potential phishing, invoice fraud, or other critical threats, allowing your team to take informed action.

### 8.4 Fraud Categories Detected

Purpose:

Categorize the types of fraud and threats identified through analysis.

Data fields:

- Vendor Invoice Fraud from `risk_analysis.vendor_fraud_score`.
- Wire-Transfer Pressure from `risk_analysis.wire_transfer_anomaly_score`.
- Lookalike Sender Domains from `impersonation_analysis.impersonation_likelihood` and `risk_analysis.behavioral_deviation_flags`.
- Invoice Authenticity Anomalies from `risk_analysis.invoice_authenticity_score`.
- Executive Impersonation from `impersonation_analysis.impersonation_likelihood`.
- Header Inconsistency from `risk_analysis.behavioral_deviation_flags`.
- Phishing from `risk_analysis.phishing_signals`.
- Ransomware Precursor Signals from `risk_analysis.risk_factors`.

Example copy:

> This month, NorthStar Inbox Shield identified potential threats across multiple categories: 15 phishing incidents, 5 vendor invoice fraud attempts, 3 lookalike sender domain cases, 2 ransomware precursor signals, and 1 executive impersonation attempt.

### 8.5 Top Risk Signals

Purpose:

Detail the most prevalent indicators or patterns that contributed to high-risk email identification.

Data fields:

- Top 3-5 signals from `risk_analysis.risk_factors`, `risk_analysis.phishing_signals`, `risk_analysis.urgency_signals`, `risk_analysis.behavioral_deviation_flags`, `impersonation_analysis.impersonation_likelihood`, and `risk_analysis.financial_risk`.
- Frequency of each signal.

Example copy:

> The most common risk signals identified this period included suspicious links, unusual sender domains, invoice mismatches, urgent tone, and new banking instructions.

### 8.6 Recommended Actions

Purpose:

Provide clear, plain-English business actions derived from `recommended_action`.

Data fields:

- Prioritized recommendations.
- Status of previous recommendations, if applicable.

Example actions:

- Verify vendor banking changes by phone using a known, trusted phone number.
- Pause payment for suspicious invoices until reviewed.
- Run micro-training on executive impersonation.
- Review approval workflow for large transfers.

### 8.7 Evidence Package Status

Purpose:

Inform users about the status of assembled reports or evidence files for identified high-risk emails.

Data fields:

- Status, such as `Assembled`, `Processing`, or `Not Applicable`.
- Delivery or storage note.

Example copy:

> Your monthly Evidence Package is assembled and prepared for delivery. This report provides supporting details for identified threats and is available for review.

### 8.8 Month-over-Month Trend

Purpose:

Visualize changes in key security metrics over time to show progress or identify emerging patterns.

Data fields:

- Total emails analyzed.
- High-risk emails identified.
- Top fraud categories.
- Three-month or six-month comparison.

Example copy:

> Month-over-month trends are reviewed alongside training completion, client notes, and incident context to provide a more complete understanding of your human-layer security posture.

### 8.9 Client-Ready Leadership Summary

Purpose:

Provide an executive-friendly summary suitable for sharing with leadership or board members.

Data fields:

- Key takeaways from the executive summary.
- Overall security posture rating.
- Impact of NorthStar Security's analysis.

Example copy:

> NorthStar Security provides essential insight into potential email threats. This month's report highlights a strong security posture, with analysis that identified potential fraud attempts and helped your team make informed decisions.

### 8.10 Operator Notes Area

Purpose:

Provide an internal-only area for notes, observations, and client communications. This section is visible only to NorthStar Security operators or MSP operators, not normal client leadership.

Data fields:

- Note text.
- Timestamp.
- Author.

Example note:

> 2026-05-21, NorthStar Security Operator: Client reported a suspicious email from `accounts@vendor.com`, which Inbox Shield identified as high-risk. Followed up with a micro-training recommendation on vendor impersonation.

## 9. Role-Specific Views

SMB owner or office manager:

- Emphasize Executive Summary, Recommended Actions, and Client-Ready Leadership Summary.
- Detailed fraud categories and risk signals may be collapsed by default.

MSP partner:

- Emphasize fraud categories, top risk signals, and operator notes for clients where the MSP is acting as the operator.
- Multi-client aggregate views are future enhancements.

Non-technical leadership:

- Emphasize Executive Summary and Client-Ready Leadership Summary.
- Allow drill-down into Recommended Actions.

## 10. Future Enhancements

- Interactive trend analysis.
- Drill-down capabilities for anonymized high-risk email details.
- Customizable reporting.
- Training module links.
- Multi-client view for MSP partners.
- Alerts and notifications.
- Email blocking, quarantining, or remediation.
- Secure portal access.
- User feedback mechanism.

## 11. Example Monthly Leadership Summary

# NorthStar Security Monthly Threat Report: May 2026

Overall Security Posture: Good

This month, NorthStar Security continued to provide essential insights into potential email threats. Our analysis shows a Good overall security posture, with a notable reduction in identified high-risk email interactions compared to last month. NorthStar Inbox Shield identified several sophisticated phishing attempts and potential fraud attempts, giving your team the information needed to mitigate these risks.

Key highlights:

- 12,500 emails analyzed by NorthStar Inbox Shield.
- 25 high-risk emails identified, representing 0.2% of total inbound mail.
- 15 phishing incidents and 5 vendor invoice fraud attempts identified.
- Recommended actions provided to strengthen human-layer defense, including verifying vendor banking changes by phone and pausing payment for suspicious invoices.

NorthStar Security's analysis identifies potential fraud attempts and helps reduce human-layer risk by enabling informed decision-making within your organization.
