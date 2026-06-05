# Cyber Insurance / Vendor Payment Integrity MSP Call Pack

**Status:** Operator-facing discovery aid. Not client-facing copy. Not a spec. Not a signed claim. Not pricing approval.
**Date:** 2026-05-31 (spoken language updated to the Mutant Monkey buyer brand 2026-06-05)
**Owner:** Matt Nichol
**Brand:** all spoken / buyer-heard language uses **Mutant Monkey** (rebrand Option B external brand). "NorthStar" / "SwarmCommand" remain internal engineering codenames and must not be said to an MSP or client.
**Source runbook:** `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Cheaper_Proof_Runbook.md`
**Worksheet:** `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv`

---

## One-Sentence Positioning

Mutant Monkey helps MSPs produce structured evidence that vendor-payment changes were identified, reviewed, and documented, so SMBs can better support cyber-insurance underwriting, renewal, and post-incident conversations.

Use this as discovery framing only. Do not turn it into buyer-facing copy without a separate operator pass.

---

## 10-Minute Call Flow

1. **Minute 0-1 - Context**
   "I'm testing a narrow Mutant Monkey evidence-support idea for MSPs. The question is whether SMB clients with upcoming insurance or underwriting conversations need better evidence around vendor-payment changes."

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

## Anticipated Questions + Prepared Answers (keep the conversation going)

These are the questions an engaged MSP owner like Todd is likely to ask. Answers are claim-safe and honest. Speak them plainly; do not read them like a script. Stay inside the "What Not To Say" list below.

**Q: "What exactly is the vision of the project?"**
"Near-term, it helps small businesses catch email fraud — especially vendor-payment changes, fake invoices, and impersonation — before it turns into a payment mistake, and it turns what gets reviewed into clear, plain-English evidence you and your clients can use for leadership and insurance conversations. Longer-term, it's a defensive layer that keeps learning new fraud patterns. I'm deliberately keeping the first version narrow: the email and vendor-payment evidence surface, done well, rather than trying to be a whole security stack."

**Q: "How long until it's launch-ready?"** (honest, no hard date)
"I'm being straight with you: it's early. The detection-and-evidence engine works and I've validated it against fraud test cases internally, but it hasn't been run with a real MSP and their clients yet. That's exactly why I wanted to talk — I'm looking for one or two MSP design partners to pilot it on real, historical examples before any wider launch. I'm not putting a hard launch date on it because I'd rather get it right with partner input than ship to a deadline. If it's useful to you, you'd be shaping it early, not buying a finished box."

**Q: "What problems are you looking to lessen?"**
"Four, mainly: (1) payment mistakes from business-email-compromise and vendor bank-detail changes; (2) the renewal-week scramble where nobody can quickly show what was reviewed; (3) the gap between 'we have controls' and 'prove the control actually operated' that underwriters now push on; and (4) alert fatigue — I want to surface the few things that matter, with evidence, not add another noisy feed."

**Q: "How is this different from what I already run (M365 Defender, my email security stack)?"**
"It's not a gateway or a blocker and it's not trying to replace your stack — it sits beside it. Your tools try to stop bad mail; this documents the human-layer fraud risk that gets through and produces the review-and-evidence record. It's the evidence and explanation layer, not another filter."

**Q: "Is this safe for my clients' data? What do you actually need from me?"**
"For a first look, nothing live and no admin access. You'd hand me a bounded batch of real emails you've already received — forwarded suspicious messages or a small export — and I analyze them on a controlled machine and give you back the report and evidence package. No mailbox connection, no settings changes, and I don't need policy documents, account numbers, or private customer details."

**Q: "What does it cost?"**
"I'm still in discovery, so I'm not quoting pricing yet — that'd be premature. The first one is about learning together. If it earns a place in your offering later, we'd figure out bundle-or-surcharge then." (This is discovery framing only; it does not set or approve pricing.)

**Q: "Why should I trust an early-stage tool?"**
"You shouldn't take my word for it — that's the point of starting with your own historical emails and a report you can check. It changes nothing in your environment, you stay in control, and if the evidence isn't useful, you've risked nothing. I'd rather under-promise and let the output speak."

**Bridge lines to keep it going if it stalls:** "What does a renewal conversation actually look like for your clients today?" / "When a client almost sent a payment to a changed account, how did you handle it?" / "If you could hand a client one clean page before their renewal call, what would it need to show?"

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

Do not say Mutant Monkey:

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
| Mutant Monkey Verified | Verified Review Recorded |
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

## First-Contact / Coffee-Request Email (send BEFORE the meeting)

Friendly, low-pressure, claim-safe. Adjust the opening line depending on your last exchange with Todd (whether he offered coffee or you're initiating). Keep it short — the goal is a 15-minute coffee, not a sale.

Subject: Quick coffee? An evidence idea for MSP cyber-insurance conversations

Hi Todd,

Thanks again for being open to connecting — I appreciated your candor on the wording, it was fair.

Quick context on what I'm doing: I'm building a small tool called **Mutant Monkey** that helps MSPs produce clear, structured evidence that email-fraud risks — especially vendor-payment changes, fake invoices, and impersonation — were identified, reviewed, and documented. The idea is to make it easier for your SMB clients to support cyber-insurance renewal and underwriting conversations, without pretending to cover MFA, EDR, backups, incident response, or patching. It's the evidence-and-review layer, not another filter, and it doesn't touch your clients' environments.

I'm early and genuinely in learning mode — I'm not selling anything and there's no deck. I'm trying to talk to a couple of MSP owners who actually live these renewal and vendor-payment conversations, to find out whether this is useful or whether I'm solving the wrong problem.

Could I buy you a coffee for 15-20 minutes? I'd mostly ask questions and show you a sample of what the evidence output looks like (no client data involved). Whatever works for you — happy to come to you.

Thanks,
Matt

*(Operator note: this is discovery outreach, not a client-facing offer or a signed claim. Keep it inside the "What Not To Say" list. Do not attach client documents or make any insurance/compliance/guarantee claim.)*

---

## Follow-Up Email Template (send AFTER the meeting)

Subject: Mutant Monkey evidence-package discovery follow-up

Hi <name>,

Thanks for the quick conversation today. I am validating a narrow Mutant Monkey evidence-support idea for MSPs: structured evidence that vendor-payment changes were identified, reviewed, and documented, so SMBs can better support cyber-insurance underwriting, renewal, and post-incident conversations.

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

