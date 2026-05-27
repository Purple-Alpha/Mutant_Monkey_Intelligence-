# Sender-Provenance / Geo-Velocity - Cheaper-Proof Runbook

**Status:** Operator runbook for manual proof collection  
**Date:** 2026-05-25  
**Owner:** Matt Nichol  
**Companion protocol:** `4. Product_Roadmap/Sender_Provenance_GeoVelocity_Cheaper_Proof_Protocol.md`  
**Worksheet:** `4. Product_Roadmap/Sender_Provenance_GeoVelocity_Proof_Worksheet.csv`  
**Build boundary:** This runbook does **not** authorize detector implementation.

---

## Purpose

This runbook turns the cheaper-proof protocol into a short manual workflow.

The question to answer is narrow:

> Are enough business-critical vendors stable enough in real email headers to justify a future sender-origin baseline detector?

If the answer is no, the detector stays out of the build queue. If the answer is yes, the result only unlocks the next spec-first discussion; it still does not authorize runtime code.

---

## Proof Target

Collect and classify:

- At least **30 vendor-like email samples**.
- At least **10 distinct sender domains**.
- Prefer financially relevant senders: suppliers, subcontractors, payroll, accounting, benefits, software vendors, banking, or payment services.

Suggested pass threshold:

- At least **50% of business-critical sender domains** classify as `stable_high_value`.
- The noisy / cloud-normalized subset is understandable and skippable.
- A future finding could be explained to an MSP client in one sentence without exposing raw headers.

---

## Privacy Boundary

Use raw headers only. Do not collect bodies, attachments, private links, account numbers, routing numbers, invoice PDFs, passwords, tokens, or employee personal notes.

Allowed fields to preserve:

- `From`
- `Reply-To` if present
- `Return-Path` if present
- all `Received` headers
- `Authentication-Results`
- `DKIM-Signature` domain if present
- `Date`
- subject label only, such as `invoice`, `quote`, `software`, `banking`, `payroll`, `newsletter`, or `unknown`

If a header contains sensitive personal or financial data, redact that value before recording notes. Keep pseudonyms consistent: if `vendor-a.example` is used once for a sender, use the same pseudonym for every sample from that sender.

---

## Materials

- One safe mailbox with recent vendor / invoice / payment-related email.
- Local spreadsheet editor for `Sender_Provenance_GeoVelocity_Proof_Worksheet.csv`.
- A scratch note file or local text editor for temporary header viewing.
- No network lookup service is required for this proof.

Do not paste raw headers into public websites, LLM chats, or enrichment tools for this proof run.

---

## Step 1 - Pick The Mailbox

Use one mailbox source that can safely provide raw headers.

Good candidates:

- A business mailbox owned by Matt.
- A test / demo mailbox with real vendor-like traffic.
- A mailbox where the operator has explicit permission to inspect headers.

Bad candidates:

- A client mailbox without explicit permission.
- A personal mailbox with sensitive family / medical / legal content mixed in.
- A mailbox where bodies or attachments cannot be avoided.

Record the source at the end of the protocol under `## Outcome Log`, using a safe label such as `operator-owned business mailbox` or `demo mailbox`.

---

## Step 2 - Select Samples

Search recent mail for financially relevant patterns:

- `invoice`
- `payment`
- `ACH`
- `wire`
- `quote`
- `statement`
- `receipt`
- `payroll`
- `accounting`
- known vendor names

For each candidate, confirm it is vendor-like before opening raw headers. The sample does not need to be suspicious. Normal vendor mail is the point: the proof asks whether legitimate origin patterns are stable enough to baseline.

Aim for breadth first:

- 10 sender domains x 3 samples each is better than 30 samples from one sender.
- Include repeat samples from the same sender only when they help judge stability.
- Include a small number of newsletters or marketing emails only as `not_vendor` / noise examples.

---

## Step 3 - Extract Header Facts

For each email, inspect the raw headers and fill one worksheet row.

Use the worksheet columns this way:

| Column | How to fill it |
|---|---|
| `sample_id` | Continue sequentially: `spg-003`, `spg-004`, etc. |
| `pseudonymized_sender_domain` | Stable pseudonym for the sender, for example `vendor-c.example`. |
| `sender_category` | `invoice_vendor`, `subcontractor`, `payroll`, `accounting`, `software_vendor`, `banking`, `payments`, `newsletter`, or `unknown`. |
| `received_date_bucket` | Week bucket only, for example `2026-05-week-4`. Do not preserve exact timestamps unless needed. |
| `from_domain` | Domain from `From`, pseudonymized if needed. |
| `reply_to_domain` | Domain from `Reply-To`, blank if absent. |
| `return_path_domain` | Domain from `Return-Path`, pseudonymized if needed. |
| `dkim_domain` | Signing domain from `DKIM-Signature`, blank if absent. |
| `auth_result_summary` | Compact summary such as `dkim=pass spf=pass dmarc=pass`. |
| `received_header_count` | Count of `Received` headers. |
| `top_observed_relay_provider` | Broad relay class: `microsoft_365`, `google_workspace`, `aws_ses`, `sendgrid`, `mailchimp`, `fixed_business_relay`, `unknown`, etc. |
| `observed_country_class` | `canada`, `us`, `eu`, `global_cloud`, `unknown`, or another broad class. Do not guess. |
| `observed_asn_or_provider_class` | Broad class only, such as `microsoft_cloud`, `google_cloud`, `aws_cloud`, `business_isp_or_static_provider`, `esp_shared_pool`, or `unknown`. |
| `classification_label` | One of the protocol labels. |
| `would_new_origin_matter` | `yes`, `no`, or `unclear`. |
| `explainable_one_sentence` | `yes` only if an MSP-facing explanation would be clear without raw headers. |
| `notes` | Short reason for the classification. No raw `Received` strings. |

When unsure, choose `unknown`, `unclear`, or `insufficient_history`. Do not force a stable label.

---

## Step 4 - Classify Per Sender

After the first 30 rows, group by `pseudonymized_sender_domain`.

For each sender domain, answer:

1. Is this sender financially relevant?
2. Are there enough samples to judge stability?
3. Does the observed provider / ASN / country class stay consistent enough to baseline?
4. Would a new origin be meaningful, or is the sender naturally cloud-normalized / noisy?
5. Would the signal add value beyond existing DKIM/SPF/DMARC, header divergence, Financial State Ledger, Document Metadata, Prompt Injection, and Two-Channel Confirmation coverage?

Classification guidance:

- `stable_high_value` - financially relevant sender with stable origin metadata. Counts toward implementation case.
- `stable_low_value` - stable but not important enough to alert on.
- `cloud_normalized` - only generic Google / Microsoft / AWS / ESP infrastructure is visible.
- `noisy_legitimate` - legitimate origin shifts too often.
- `insufficient_history` - too few samples to judge.
- `not_vendor` - marketing, newsletter, personal, or unrelated traffic.

Only `stable_high_value` counts toward the pass threshold.

---

## Step 5 - Record The Outcome

Update `## Outcome Log` in the protocol with:

- Date
- Source mailbox label
- Sample count
- Distinct sender domains
- `stable_high_value` count
- `cloud_normalized` count
- `noisy_legitimate` count
- `insufficient_history` count
- Decision
- Notes

Use one of these decisions:

- `pass_to_spec` - proof supports writing a sender-provenance detector deep dive.
- `needs_more_samples` - sample was useful but too small or skewed.
- `fail_hold_in_think_sheet` - proof did not justify detector work.

Do not use `pass_to_implementation`. A passing proof opens a spec lane, not code.

---

## Stop Immediately If

- Raw bodies or attachments are required to make the proof work.
- Sensitive account / routing / password / token data cannot be excluded.
- Samples come from a mailbox without permission.
- The only stable senders are newsletters or low-risk SaaS notices.
- The proof depends on live network lookup services.
- Notes require preserving raw `Received` headers to be understandable.

---

## Expected Time Box

Recommended first pass:

- 5 minutes: choose mailbox and sample search terms.
- 20 minutes: collect 30 worksheet rows.
- 10 minutes: group senders and classify.
- 5 minutes: update the protocol outcome log.

Stop after 40 minutes even if the data is messy. Messy data is part of the proof.
