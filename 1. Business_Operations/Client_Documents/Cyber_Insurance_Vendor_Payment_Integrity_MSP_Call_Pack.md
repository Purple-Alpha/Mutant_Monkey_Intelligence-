# Cyber Insurance / Vendor Payment Integrity MSP Call Pack

**Status:** Operator-facing discovery aid. Not client-facing copy. Not a spec. Not a signed claim. Not pricing approval.
**Date:** 2026-05-31
**Owner:** Matt Nichol
**Source runbook:** `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Cheaper_Proof_Runbook.md`
**Worksheet:** `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv`

---

## One-Sentence Positioning

NorthStar helps MSPs produce structured evidence that vendor-payment changes were identified, reviewed, and documented, so SMBs can better support cyber-insurance underwriting, renewal, and post-incident conversations.

Use this as discovery framing only. Do not turn it into buyer-facing copy without a separate operator pass.

---

## 10-Minute Call Flow

1. **Minute 0-1 - Context**
   "I'm testing a narrow NorthStar evidence-support idea for MSPs. The question is whether SMB clients with upcoming insurance or underwriting conversations need better evidence around vendor-payment changes."

2. **Minute 1-2 - Boundary**
   "This is not replacing your broader insurance, MFA, EDR, backup, incident-response, or patch-management work. I only want to know whether email-fraud and vendor-payment-change evidence would help in real conversations you already have."

3. **Minute 2-7 - Discovery questions**
   Ask the seven questions below. Keep the call practical. The target is evidence of need, not a sale.

4. **Minute 7-9 - D10 anchor check**
   Confirm whether they can name both a real SMB context and a real upcoming insurance / underwriting conversation.

5. **Minute 9-10 - Close**
   "This proof only decides whether the evidence-package framing is worth continuing. It does not start implementation and it is not a client-facing offer yet."

---

## Questions To Ask

1. Do you have any SMB clients right now, or in the next 90 days, dealing with cyber-insurance renewal, underwriting, or claim-documentation questions?
2. When those conversations happen, what evidence do clients or brokers usually ask you for?
3. Do vendor-payment changes, invoice fraud, wire-transfer review, or social-engineering exposure come up in those conversations?
4. Would an email-fraud evidence package help if it showed detected vendor-payment changes, review history, operator actions, and source artifacts without pretending to cover MFA, EDR, backups, incident response, or patching?
5. Can you name one SMB client context where this would matter? A verbal business-name anchor is enough; do not share private documents.
6. Can you name the upcoming insurance / underwriting / renewal conversation tied to that SMB?
7. If this became part of your MSP offering later, would you bundle it, surcharge it, absorb it, or skip it?

Question 7 is pricing signal only. It does not approve pricing.

---

## D10 Go / No-Go Criteria

A conversation counts as a **strong yes** only when all four are true:

- The MSP is relevant to SMB cyber-insurance or vendor-payment conversations.
- They can name a real SMB context.
- They can name an upcoming insurance / underwriting / renewal conversation tied to that SMB.
- They say the evidence package would be useful enough to continue exploring.

A conversation is **partial** when:

- The MSP likes the idea but cannot name both anchors.
- The MSP has the right buyer pain but no near-term insurance / underwriting conversation.
- The MSP wants a different evidence shape than the current package direction.

A conversation is **no** when:

- The MSP has no relevant SMB clients.
- They do not recognize the need.
- They reject the framing.
- The idea cannot connect to a real SMB insurance / underwriting conversation.

The cheaper-proof gate is met only if **2 of 3 relevant MSP conversations are strong yeses**.

---

## What Not To Say

Do not say NorthStar:

- proves compliance;
- certifies a client;
- is approved by any insurer, carrier, broker, or underwriter;
- reduces premiums;
- qualifies a client for a policy;
- guarantees an insurance outcome;
- guarantees fraud will be prevented;
- replaces MFA, EDR, backups, incident-response planning, patching, or MSP controls.

Use these safer replacements:

| Risky wording | Use instead |
|---|---|
| Compliance Engine | Evidence Readiness Engine |
| Integrity Certificate | Monthly Evidence Summary |
| Premium Reducer | Insurance Conversation Support |
| NorthStar Verified | Verified Review Recorded |
| Required by carriers | Structured around common underwriting evidence requests |
| Approves coverage | Supports underwriting conversations |

---

## Worksheet Logging

Log one row in `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv`.

Use:

- `relevant_msp`: `yes`, `partial`, or `no`.
- `named_smb_anchor`: record the volunteered SMB anchor, or `missing`.
- `named_underwriting_anchor`: record the volunteered insurance / underwriting / renewal anchor, or `missing`.
- `d10_yes`: `yes` only for a strong yes; otherwise `partial` or `no`.
- `buyer_pain_summary`: one plain-English sentence.
- `current_evidence_gap`: what they cannot currently prove or package cleanly.
- `pricing_signal`: bundle / surcharge / absorb / skip / unknown.
- `follow_up_needed`: next practical follow-up.
- `notes`: privacy-safe context only.

Do not record raw emails, raw headers, attachments, account numbers, routing numbers, policy documents, insurer applications, customer secrets, or private employee details.

---

## Follow-Up Email Template

Subject: NorthStar evidence-package discovery follow-up

Hi <name>,

Thanks for the quick conversation today. I am validating a narrow NorthStar evidence-support idea for MSPs: structured evidence that vendor-payment changes were identified, reviewed, and documented, so SMBs can better support cyber-insurance underwriting, renewal, and post-incident conversations.

My notes from the call:

- SMB context: <named SMB anchor or missing>
- Insurance / underwriting timing: <anchor or missing>
- Evidence gap you described: <one sentence>
- Useful enough to continue exploring: <yes / partial / no>

I am not asking for client documents, raw emails, policy files, or private customer data. A plain-English summary is enough for this discovery proof.

Thanks,
Matt

---

## Close-Out Rule

After three relevant MSP conversations, compare the worksheet rows to the D10 gate:

- 2 or 3 strong yeses: move to §13 sign-off readiness review. No implementation starts yet.
- 1 strong yes: signal exists, but the gate is not met. Decide whether to run more conversations or revise framing.
- 0 strong yeses: do not continue toward implementation spec without revisiting the idea in `think_sheet.md`.

This call pack does not change the active queue. The active queue remains MSP discovery.

