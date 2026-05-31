# Cyber Insurance Evidence Package - Cheaper-Proof Runbook

**Status:** Operator runbook for MSP discovery. Pre-implementation. Not a spec. Not §13 sign-off.  
**Date:** 2026-05-31  
**Owner:** Matt Nichol  
**Companion spec:** `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md`  
**Worksheet:** `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv`  
**Build boundary:** This runbook does **not** authorize package-generation implementation.

---

## Purpose

This runbook turns the Cyber Insurance Evidence Package D10 cheaper-proof gate into a short operator workflow.

The question to answer is narrow:

> Do relevant MSPs have real SMB clients with upcoming insurance / underwriting conversations where a NorthStar email-fraud evidence package would be useful enough to continue?

If the answer is no, the implementation spec stays blocked. If the answer is yes, the result only unlocks the next sign-off readiness step; it still does not authorize runtime code.

---

## D10 Go Bar

The go bar is locked in `Cyber_Insurance_Evidence_Package_Deep_Dive.md` §12 Q10:

- Run **3 relevant MSP conversations** if possible.
- At least **2 of 3** must satisfy the per-MSP "yes" definition.
- A relevant MSP is one that can plausibly answer the framing for SMB cyber-insurance evidence packaging.
- A single MSP's "yes" requires **both** named anchors:
  1. A **named SMB**.
  2. A **named upcoming insurance / underwriting conversation** for that SMB.
- Verbal confirmation counts for the gate. Written follow-up strengthens evidence but is not required.

Do not lower the bar to "sounds interesting." Interest without both named anchors is a useful signal, but it is not a D10 yes.

---

## Privacy Boundary

Discovery is about buyer need, not customer data collection.

Do not collect:

- raw emails
- raw headers
- attachments
- account numbers
- routing numbers
- policy documents
- insurer applications
- customer secrets
- private employee names beyond what the MSP volunteers as ordinary business context

Allowed to record:

- MSP name
- conversation date
- contact role
- whether the MSP is relevant
- named SMB anchor, if voluntarily provided
- named upcoming insurance / underwriting conversation anchor, if voluntarily provided
- plain-English buyer pain
- whether the D10 yes definition is met
- follow-up needed

If an MSP starts to share private customer material, stop them and ask for a summary instead.

---

## Materials

Use existing NorthStar artifacts only. Do not invent a product sheet for this proof.

- `1. Business_Operations/Client_Documents/MSP_Discovery_Evidence_Package.md`
- `1. Business_Operations/Client_Documents/Inbox_Shield_Sample_Monthly_Report.md`
- `1. Business_Operations/Client_Documents/Generated/Acme_Effective_Parameter_Report_Demo.md`
- `1. Business_Operations/Client_Documents/Generated/Inbox_Shield_Daily_Digest_Demo.md`
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_Deep_Dive.md` §2, §6, §12 Q10, and §14
- `4. Product_Roadmap/Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv`

The proof does not need a polished deck. The point is to learn whether the evidence-package framing lands with MSPs that have a real client / underwriting need.

---

## Target MSP List

Starter targets come from `THREAT_INTEL_LOG.md` 2026-05-25 local MSP landscape notes:

- Carpathia IT
- NetDNA MSP
- EC Managed IT
- IT Works MSP BC
- SFY IT
- Good IT

Use whichever three can be reached fastest. Do not treat this list as exclusive; a relevant MSP outside the list can count if it can answer the D10 framing.

---

## Call Guide

Keep the call short. The desired outcome is a D10 yes/no/partial, not a sale.

### Opening

> I'm testing a narrow NorthStar evidence-package idea for MSPs. It is not a new control claim and it does not replace the rest of your cyber-insurance work. The idea is to package existing Inbox Shield email-fraud evidence into something an MSP can use when an SMB client has an insurance or underwriting conversation.

### Boundary sentence

Use the protected lane sentence exactly when useful:

> NorthStar helps identify, review, verify, and document high-risk financial exposure before action is taken.

Do not say NorthStar guarantees approval, reduces premiums, replaces an MSP's other controls, or covers non-email controls.

### Three Questions

1. **Do you have any SMB clients right now, or in the next 90 days, dealing with cyber-insurance renewal, underwriting, or claim-documentation questions?**
2. **For any one of those clients, would an email-fraud evidence package be useful if it showed detection evidence, review history, operator actions, and source artifacts without pretending to cover MFA / EDR / backups / IR / patching?**
3. **Can you name the SMB and the upcoming insurance / underwriting conversation well enough for me to log the discovery signal? Verbal is fine; I do not need private documents.**

### Pricing-Signal Question

Ask only after the framing lands:

> If this package were a separate line item inside your MSP offering, would you bundle it, surcharge it, absorb it, or skip it? If surcharge, what rough range would feel realistic?

This is signal only. It is not NorthStar pricing approval.

### Close

> This proof only decides whether the evidence-package framing is worth continuing. It does not start implementation and it is not a client-facing offer yet.

---

## Worksheet Instructions

Fill one row per MSP conversation in `Cyber_Insurance_Evidence_Package_MSP_Discovery_Worksheet.csv`.

Required for a D10 yes:

- `relevant_msp` = `yes`
- `named_smb_anchor` is non-empty
- `named_underwriting_anchor` is non-empty
- `d10_yes` = `yes`

Use `partial` when the MSP likes the idea but one or both named anchors are missing.

Use `no` when the MSP has no relevant clients, does not understand the need, rejects the framing, or cannot connect it to a real SMB insurance / underwriting conversation.

---

## Outcome Rule

After three relevant conversations:

- **2 or 3 D10 yes rows:** cheaper-proof validated. Next step is §13 sign-off readiness review. No implementation starts yet.
- **1 D10 yes row:** signal exists but the D10 threshold is not met. Log as partial; decide whether to run more conversations or revise framing.
- **0 D10 yes rows:** framing failed this proof. Do not continue toward implementation spec without revisiting the idea in `think_sheet.md`.

If fewer than three relevant MSPs can be reached, do not claim the gate is met. Log the attempts and keep the gate open.

---

## What This Runbook Does Not Authorize

- No §13 signature.
- No implementation spec.
- No package-generation runtime code.
- No new claims about NorthStar's scope.
- No client-facing copy.
- No collection of real customer evidence.
- No pricing approval.

This runbook only prepares the operator to collect the D10 cheaper-proof evidence cleanly.
