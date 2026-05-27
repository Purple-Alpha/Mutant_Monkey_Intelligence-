# Sender-Provenance / Geo-Velocity — Cheaper-Proof Protocol

**Status:** Pre-build proof protocol  
**Date:** 2026-05-24  
**Owner:** Matt Nichol  
**Source idea:** `think_sheet.md` — Sender-provenance / geo-velocity detector, promoted but explicitly gated on cheaper proof  
**Build status:** Do **not** implement detector code yet

---

## Why This Exists

The sender-provenance / geo-velocity detector is a strong BEC idea:

> Flag when a known vendor's mail suddenly arrives from a new country or ASN.

The stress test in `think_sheet.md` deliberately blocked implementation until a cheaper proof answers the central assumption:

> Are enough business-critical vendors stable enough in real email headers to baseline sender origin without creating noise?

This protocol defines that proof so the next session does not drift into premature implementation.

---

## Decision Gate

The detector may graduate into `PROGRESS.md` and receive a spec-first deep dive only if the proof run shows:

- At least one real mailbox can provide enough historical vendor email headers to study.
- A meaningful subset of business-critical vendors has stable sender-origin patterns.
- The stable subset is valuable enough for a deterministic advisory signal.
- The noisy subset is understandable and can be skipped without pretending coverage exists.

Suggested pass threshold for a first proof:

- Review at least **30 vendor-like email samples** across at least **10 distinct sender domains**.
- At least **50% of business-critical sender domains** show stable enough origin metadata to baseline.
- Stability means the observed relay / ASN / country class does not churn so much that every legitimate M365 / Google / ESP relay migration would look suspicious.

If the proof fails, the idea stays in `think_sheet.md` and does not receive a runtime spec.

---

## Inputs To Collect

Use exported raw headers only. Do not collect message bodies or attachments.

Minimum fields to preserve:

- `From`
- `Reply-To` if present
- `Return-Path` if present
- all `Received` headers
- `Authentication-Results`
- `DKIM-Signature` domain if present
- `Date`
- subject can be replaced with a label like `invoice`, `quote`, `newsletter`, or `unknown`

Do not preserve:

- body text
- attachment names
- attachment content
- account numbers
- routing numbers
- invoice PDFs
- passwords, tokens, or private links
- employee personal notes

Recommended sample shape:

- 30 to 100 emails.
- 10 to 25 distinct sender domains.
- Prefer vendors that matter financially: suppliers, subcontractors, payroll, accounting, benefits, software vendors, banking / payments.
- Include a few normal newsletters or marketing senders only as noise examples, not as proof of BEC value.

---

## Manual Extraction Questions

For each sender domain, answer:

1. Does the mail consistently arrive through the same broad provider class?
2. Do `Received` headers expose a useful originating relay, or only generic Google / Microsoft / AWS infrastructure?
3. Is there a stable country signal, or is country meaningless because the provider is a global cloud relay?
4. Is there a stable ASN / provider signal?
5. Would a new ASN or country have been meaningful for this vendor?
6. Would this signal have caught anything that existing header divergence, DKIM/SPF/DMARC, Financial State Ledger, Document Metadata, Prompt Injection, and Two-Channel Confirmation do not already cover?
7. Would the finding be explainable to an MSP client in one sentence?

---

## Classification Labels

Use these labels while reviewing samples:

- `stable_high_value` — financially relevant sender with stable origin metadata. Candidate for future detector.
- `stable_low_value` — stable but not important enough to justify an alert.
- `cloud_normalized` — headers mostly expose generic Google / Microsoft / AWS / ESP infrastructure; origin may not identify the vendor's real sending environment.
- `noisy_legitimate` — legitimate vendor origin shifts too often to baseline safely.
- `insufficient_history` — too few samples to judge.
- `not_vendor` — newsletter, marketing blast, personal email, or unrelated traffic.

Only `stable_high_value` should count toward the implementation case.

---

## What A Future Detector Would Probably Do

This is **not** the spec. It is only the sketch to test against reality.

Likely v1 boundaries if the proof passes:

- Pure deterministic detector under `core/scoring/`.
- Consumes `EmailInboundPayload.headers` only.
- No live DNS, GeoIP, ASN lookup, or network call inside the runtime.
- Operator-side enrichment may be allowed later if a signed spec defines a local ASN / GeoLite source.
- Uses Vendor Baseline Store only after the signal enum is explicitly extended by spec.
- Emits family tags / advisory findings only; no raw `Received` header strings in analysis output.
- LOW profile likely skips; MEDIUM may use stable sender-origin baselines; HIGH may apply a higher lift or require extra verification.
- Any `new_origin` finding should be lift-only and should recommend known-channel verification, not automatic blocking.

Probable dependency:

- Vendor Baseline Store currently has a closed signal-type enum. Sender-origin baselining likely needs one or more new signal types such as `sender_origin_provider`, `sender_origin_asn`, or `sender_origin_country`. That requires a signed spec revision before implementation.

---

## Stop Conditions

Do not proceed to implementation if:

- The available email export includes bodies / attachments and cannot be sanitized.
- Most important vendors are cloud-normalized with no stable useful origin signal.
- The only stable senders are newsletters or low-risk SaaS notifications.
- The proof requires live network lookups inside the runtime path.
- The output cannot be explained without dumping raw `Received` headers.
- The finding duplicates existing DKIM/SPF/DMARC or header-divergence value without adding a clear per-vendor historical signal.

---

## Tomorrow's First Action

Find one mailbox source that can provide raw headers safely.

Use `4. Product_Roadmap/Sender_Provenance_GeoVelocity_Cheaper_Proof_Runbook.md` for the step-by-step collection workflow.

Ask for:

- 30 to 100 exported raw headers from recent vendor / invoice / payment-related emails.
- No bodies.
- No attachments.
- Sender domains may be anonymized consistently (`vendor-a.example`, `vendor-b.example`) as long as each vendor keeps the same pseudonym.

Then manually classify the sample using the labels above.

No code is needed until the classification result is known.

Use `4. Product_Roadmap/Sender_Provenance_GeoVelocity_Proof_Worksheet.csv` to record the samples. It includes two example rows:

- a `cloud_normalized` Microsoft 365-style sender where the signal is probably weak,
- a `stable_high_value` subcontractor-style sender where a new origin would be meaningful.

---

## Outcome Log

Use this section after the proof run.

### Proof Run 1

- Date: 2026-05-25
- Source mailbox: operator-owned personal Gmail training corpus
- Sample count: 12 entered samples (`spg-003` through `spg-014`)
- Distinct sender domains: 9 entered sender pseudonyms (8 after consolidating duplicate Perplexity naming)
- `stable_high_value` count: 1
- `cloud_normalized` count: 9
- `noisy_legitimate` count: 0
- `insufficient_history` count: 0
- Decision: `needs_more_samples`
- Notes: This was a partial training run, not a full 30-sample business-mailbox proof. The corpus was an operator-owned **personal** Gmail account dominated by Google / Amazon SES / Stripe / ESP-normalized senders. Of 12 entered rows only one showed a plausible stable high-value business relay. That outcome **does not disprove** the sender-provenance idea — it only shows that a personal-mail corpus is the wrong corpus to test it against. The verdict is therefore `needs_more_samples`, not `fail_hold_in_think_sheet`. No sender-provenance detector code, no signal-type enum implementation, no runtime GeoIP / ASN lookup, and no Vendor Baseline expansion is authorized **until** a real business mailbox with vendor invoice / payment traffic is sampled per this protocol. The training run is preserved as evidence that the manual collection workflow is operable.
