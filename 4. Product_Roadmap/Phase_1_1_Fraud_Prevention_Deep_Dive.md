# Phase 1.1 — Fraud Prevention Deep Dive

**Doc status:** Authored 2026-05-20 to close the Month 1 gate of the 12-month specialization roadmap.

## Purpose

This document is the implementation contract for Month 2 ("Phase 1.1 — Fraud Detection Capabilities") of `12_Month_Specialization_Roadmap.md`. It captures:

1. The fraud signal taxonomy NorthStar Inbox Shield will recognize.
2. The four new scoring dimensions Month 2 will add to `EmailAnalysisRiskAnalysis`.
3. Worked examples for the rewritten `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT`.
4. The eval harness design + pass/fail gate.
5. Explicit out-of-scope boundary (what is *not* Phase 1.1).
6. Agent evolution strategy for fraud-detection agents (strategic architecture, no runtime code).
7. The Month 2 implementation contract — exact files, test targets, eval landing requirements.

The strategic specialization driving this deep dive is locked in `Fraud_Ransomware_Specialization_Roadmap.md` §1.1 (vendor fraud, executive impersonation, wire-transfer anomaly, invoice fraud pattern recognition). Credential harvesting and MFA-fatigue lures live in §1.2 (Phase 1.2 / Month 3) — they are explicitly out of scope here.

---

## Section 1 — Fraud Signal Taxonomy

Six fraud archetypes Inbox Shield must recognize. Each archetype is described by (a) attacker pattern, (b) observable signals in the email, (c) what the scoring agent should weight, (d) common false positives to avoid.

### 1.1 Vendor Invoice Fraud

**Attacker pattern:** A compromised or spoofed vendor sends an invoice that looks like a legitimate ongoing relationship but redirects payment to attacker-controlled banking details. The "new banking instructions" pivot is the canonical move.

**Observable signals:**
- A vendor relationship exists historically but the sender domain is subtly off (e.g. `vendor-co.com` vs `vendorco.com`).
- Invoice attached as PDF with `attachment_class == "invoice"`.
- Wire instructions or ACH details *changed* from the last known good record (this requires tenant memory; absent that, "first-time wire instructions from this sender" is a strong heuristic).
- Urgency layered on top: "payment due today" / "we missed last cycle, please push through."
- Email body references a real prior invoice number or PO to anchor legitimacy.

**Agent weighting:** `vendor_fraud_score` ≥70 when both (sender-domain anomaly OR new-banking-instructions cue) AND (invoice attachment OR explicit wire instructions in body) are present. ≥85 when urgency is layered on top.

**Common false positives:**
- A legitimate vendor genuinely changing their banking provider (rare but real). The agent should flag for human review (`recommended_action: "needs_review"`), not auto-block, when no other signals fire.
- New vendor onboarding: a first invoice from a new sender domain is not by itself fraud. Require at least one other signal.

### 1.2 Executive Impersonation

**Attacker pattern:** Email purports to be from a senior executive (CEO, CFO, COO) directing a junior employee to take an unusual financial action. Often "I'm in a meeting, just handle this." The display name spoofs the executive's name even when the underlying sender address is freemail or a lookalike domain.

**Observable signals:**
- Display name matches a known executive of the tenant (this requires a tenant-side executive directory; absent that, "Display name contains C-suite title or common executive name pattern" is a heuristic).
- Sender address is freemail (`@gmail.com` / `@outlook.com`) or a lookalike of the corporate domain.
- Body asks the recipient to perform a financial action (wire, gift card purchase, payroll redirect, invoice payment).
- "Cannot talk now / in a meeting / on a call" language discourages out-of-band verification.
- Reply-To header differs from the From address.

**Agent weighting:** The existing `impersonation_analysis.impersonation_likelihood` carries most of this signal. Month 2 adds `vendor_fraud_score` and `wire_transfer_anomaly_score` to amplify when executive impersonation is paired with a financial ask.

**Common false positives:**
- Legitimate executive emailing from a personal address while traveling. Agent should flag for review when no other signals fire.
- Internal "please handle" pattern from executive to assistant (legitimate delegation). The signal sharpens when the action is to an external party.

### 1.3 Wire Transfer Pressure

**Attacker pattern:** Push the recipient to initiate or modify a wire transfer under time pressure, often combined with one of the other archetypes. Standalone wire-pressure (no vendor invoice, no executive impersonation) is rarer but exists ("urgent wire needed for closing").

**Observable signals:**
- Body mentions wire transfer, ACH, SWIFT, ABA, or "send funds today/now/urgently."
- Specific dollar amount specified.
- Bank routing number or account number embedded in the email body.
- Time pressure: "by 5pm today", "before end of business", "or the deal falls through."

**Agent weighting:** `wire_transfer_anomaly_score` ≥60 when (wire-language present) AND (specific account/routing in body OR specific amount). ≥80 when time pressure is layered on top. ≥90 when paired with one of 1.1 or 1.2.

**Common false positives:**
- Legitimate closing instructions from a known title company or real estate agent. A tenant-specific allowlist would catch this; absent that, the agent should still flag for review rather than block.
- Internal finance team requesting wire confirmation from leadership (legitimate). Inbound-only scope keeps most of these out.

### 1.4 Invoice Authenticity Anomalies

**Attacker pattern:** Forged or recycled invoices that look real at a glance but have subtle anomalies — fake vendor logos in the PDF, mismatched company name in header vs banking info, recycled invoice numbers, off-pattern dates.

**Observable signals:**
- `attachment_class == "invoice"` is present.
- Extracted text mentions a vendor name that does not match the sender domain.
- Extracted text contains a banking detail block (routing, account) — most legitimate invoices send banking details out-of-band, not in-email.
- Invoice number does not match the tenant's known vendor invoice numbering format (out of scope for Month 2 — requires tenant memory).
- Invoice date is in the future or > 90 days old.

**Agent weighting:** `invoice_authenticity_score` is inverted — high score means "more authentic", low score means "less authentic". Score ≤30 when extracted_text contains banking detail block AND sender domain ≠ vendor name in extracted text. ≤50 when one signal fires alone.

**Common false positives:**
- Vendors that genuinely include banking info on invoices (common for international vendors). Agent should not auto-block on this alone.
- Sole proprietors / freelancers whose sender domain naturally doesn't match the invoice header ("Jane Smith Consulting" on the invoice, `jane@gmail.com` as sender). Flag for review.

### 1.5 Lookalike Sender Domain

**Attacker pattern:** Register a domain that is visually similar to a known vendor or internal domain, then send fraud emails from that lookalike. Common techniques: homoglyph substitution (`rn` for `m`, `cl` for `d`), IDN punycode tricks, hyphen insertion (`vendor-co.com`), TLD swap (`vendor.co` vs `vendor.com`).

**Observable signals:**
- Sender domain has high visual similarity to a tenant's known correspondent (requires tenant-side known-correspondent list; absent that, "sender domain unique to this tenant" is the proxy).
- Punycode encoding in the sender domain (`xn--` prefix).
- Recently-registered domain (< 30 days; requires WHOIS lookup — out of scope for Month 2, flagged for Phase 1.2).

**Agent weighting:** Surfaces under `phishing_signals` as `lookalike_sender_domain`. Also boosts `impersonation_analysis.impersonation_likelihood`.

**Common false positives:**
- Vendors that legitimately operate multiple domains (e.g. `vendor.com` for corporate, `vendor-app.com` for product). Tenant-specific allowlist is the solution.

### 1.6 Mismatched Reply-To / Header Inconsistency

**Attacker pattern:** Sender headers manipulated so the From address looks legitimate but Reply-To redirects responses to the attacker. Sometimes paired with display-name spoofing.

**Observable signals:**
- Reply-To header present AND differs from the From address (this is normal for mailing lists but anomalous for personal sender-to-recipient mail).
- Return-Path differs from From in ways that aren't explained by a known mail relay.
- Display name in From contains a name that doesn't match the email address local-part.

**Agent weighting:** Surfaces under `impersonation_analysis.suspicious_elements` as e.g. `reply_to_diverges_from_from`. Lifts `impersonation_likelihood` by ~20 when paired with a financial ask.

**Common false positives:**
- Mailing list / newsletter mail naturally has a divergent Reply-To. Inbound personal mail is the higher-signal scope.

---

## Section 2 — Scoring Dimensions Month 2 Will Add

Month 2 extends `EmailAnalysisRiskAnalysis` (`core/blackboard/models.py`) with four new fields. Existing fields (`risk_score`, `risk_factors`, `phishing_signals`, `urgency_signals`, `financial_risk`) are preserved as-is for backwards compatibility with the locked daily digest prompt and every existing test.

### 2.1 `vendor_fraud_score: int = Field(ge=0, le=100)`

**Definition:** 0 = no vendor-fraud signals; 100 = certain vendor-fraud attempt.

**Rubric:**
- 0–20: No vendor-fraud signals; email is internal, personal, or clearly non-vendor.
- 21–40: One soft signal (e.g. first-time sender from a new domain claiming to be a vendor).
- 41–60: Two or more soft signals OR one strong signal (e.g. attached invoice from sender whose domain doesn't match the vendor name).
- 61–80: Multiple strong signals (sender-domain anomaly + new banking instructions cue + invoice attached).
- 81–100: Strong signals + urgency layering, OR sender-domain anomaly + explicit wire instructions in body.

**Relationship to `risk_score`:** `vendor_fraud_score ≥ 60` should pull `risk_score` to at least 60. The mapping is not strict; the scoring agent decides the final `risk_score` holistically across all dimensions.

### 2.2 `wire_transfer_anomaly_score: int = Field(ge=0, le=100)`

**Definition:** 0 = no wire-transfer activity; 100 = certain wire-fraud attempt.

**Rubric:**
- 0–20: No wire-transfer language present.
- 21–40: Wire-language present (mention of wire/ACH/SWIFT) without specific account or amount; legitimate financial discussion.
- 41–60: Specific wire amount specified without explicit anomaly indicators.
- 61–80: Specific amount + specific routing/account in body, OR wire request + time pressure.
- 81–100: All three (specific amount + routing/account in body + time pressure) OR wire request paired with executive impersonation or vendor-fraud cues.

### 2.3 `invoice_authenticity_score: int | None = Field(default=None, ge=0, le=100)`

**Definition:** Inverted relative to the others — high score means "appears authentic", low score means "appears inauthentic". 100 = unambiguous legitimate invoice; 0 = strong indications of forgery.

**Rubric:**
- 0–20: Banking details embedded in invoice body + sender domain ≠ vendor name in extracted text + invoice date anomaly.
- 21–40: Two of the above signals.
- 41–60: One of the above signals OR vendor name in extracted text not matching sender domain on a first-time sender.
- 61–80: Routine-looking invoice from a sender consistent with the vendor name; no anomalies.
- 81–100: Invoice consistent with known patterns + sender domain matches vendor + no banking details in body + standard invoice date.
- **`null`:** No `attachment_class == "invoice"` attachment present. The agent should return `null` rather than guess. This is the only nullable score in the four — there is no meaningful value to assign when there is no invoice.

### 2.4 `behavioral_deviation_flags: list[BehavioralDeviationFlag]`

**Definition:** Controlled-enum list of behavioral deviations spotted in the email.

**`BehavioralDeviationFlag` Literal values (schema-versioned like `AttachmentClass`):**
- `new_banking_instructions` — invoice or wire request explicitly mentions new/changed banking details.
- `out_of_band_pressure` — body actively discourages verification through another channel ("don't call me", "I'm in a meeting", "this is urgent, just handle it").
- `unusual_dollar_amount` — amount is materially larger than the tenant's typical vendor invoice size (Month 2 uses a static threshold; tenant-memory comes later).
- `lookalike_sender_domain` — sender domain is visually similar to a known correspondent (or, absent tenant data, contains a homoglyph or punycode).
- `reply_to_diverges_from_from` — Reply-To header differs from From in a way not explained by a known mailing-list pattern.
- `mismatched_invoice_vendor_name` — vendor name in invoice extracted text doesn't match the sender domain.
- `first_time_sender_with_financial_ask` — sender's domain has never been seen by the tenant (proxy: not in tenant's historical correspondent set) AND the email contains a financial ask.
- `urgency_paired_with_finance` — urgency language ("today", "before EOD") layered on top of a financial action request.
- `unusual_unicode_obfuscation` — non-ASCII Unicode appears in places where it has no legitimate business purpose: zero-width characters in attachment filenames or body text, lookalike Unicode punctuation inside identifiers, or invisible joiners breaking up finance keywords such as "wire", "invoice", "ACH", "ABA", "account", or "payment".

The set starts at the nine values above. The ninth value was added after the eval dataset design grid surfaced three Unicode-obfuscation cases (`ia-003`, `ls-001`, `hi-001`). Growing the set again remains a schema change requiring a versioned rollout (same governance pattern as `AttachmentClass`).

### 2.4.1 Month 2 recall patch — targeted subcategory rubric refinements

After the first calibrated Grok run completed against the eval-contract calibration pass (see `PROJECT_ACTIVITY_LOG.md` entries for items 152–153), recall on three subcategories was still below the §4.5 gate while precision and legit FPR were both at gate. The patch is **prompt/rubric-only** — no schema changes, no dataset changes — and was applied directly to `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT` between the `behavioral_deviation_flags` boundary block and the JSON-structure block. It does not replace any rubric clause above; it adds three refinements plus an explicit FPR-protection guardrail block:

1. **Banking-instruction strength (vendor_fraud_score floor).** Any explicit change-of-destination phrase ("new ACH details", "updated remit-to address", "please use the new banking details", "payment details have changed", "remit to the address/account below") OR banking destination details that appear only inside an attached PDF / payment-request attachment is treated as a strong vendor-fraud signal. When paired with any sender anomaly the floor is `vendor_fraud_score ≥ 60`; in isolation the floor is `vendor_fraud_score ≥ 45`. `new_banking_instructions` must be emitted whenever the pattern is detected.
2. **Sender-domain obfuscation (`lookalike_sender_domain` emission).** Emit `lookalike_sender_domain` for: Unicode lookalikes / zero-width characters inside the sender domain; punycode prefixes (`xn--`); homoglyph substitutions ("rn"→"m", "0"→"o", "1"→"l", Cyrillic look-alikes); and sender domains that are a near-variant of a vendor or brand name appearing elsewhere in the email (extra hyphen, swapped TLD, dropped or doubled character, swapped word order, suffix bolted onto a recognizable vendor stem). When Unicode obfuscation is also present in filenames, headers, body text, or attachment text, `unusual_unicode_obfuscation` is emitted in addition. The patch is explicit that a first-time or unknown sender alone is **not** enough to emit `lookalike_sender_domain`.
3. **Invoice authenticity & PDF-only banking changes (`invoice_authenticity_score` floor + `recommended_action` lean).** `invoice_authenticity_score` must fall in 0–40 whenever: (a) the extracted invoice text names a vendor different from the sender's domain; (b) banking destination details appear only inside the attached PDF while the email body is terse; or (c) the invoice's stated date is inconsistent with the email's received date. When (a) or (b) holds the recommended action must be `needs_review` or `block`; `block` is preferred when urgency, banking change, executive-impersonation, or wire-pressure cues are also present. `mismatched_invoice_vendor_name` is emitted whenever (a) holds.

**FPR-protection guardrails (explicit, do not loosen).** Routine vendor invoices from a matching corporate domain with no banking change and no urgency must remain `safe`. `new_banking_instructions` is only emitted on an actual banking-destination change. `lookalike_sender_domain` is only emitted on an actual domain anomaly tied to a vendor or brand cue in the email. `vendor_fraud_score` must not exceed 40 on emails with no payment ask, no banking detail, and no invoice attachment. Polite reminders, thank-you notes, internal scheduling messages, calendar invites, routine HR notices, and newsletters must keep `recommended_action` at `safe`. These guardrails exist specifically to preserve the 0% legit-FPR result observed on the calibrated run.

The patch ships with five pinned tests in `tests/test_email_risk_scoring_agent.py` (one per clause plus the FPR guardrail block). The next live run is expected to lift recall on `vendor_invoice_fraud`, `lookalike_sender`, and `invoice_authenticity_anomaly` without disturbing the existing 100% precision / 0% legit-FPR numbers.

### 2.5 Updated `EmailAnalysisRiskAnalysis` schema (Month 2 target)

```python
class EmailAnalysisRiskAnalysis(StrictModel):
    risk_score: int = Field(ge=0, le=100)
    risk_factors: list[str] = Field(default_factory=list)
    phishing_signals: list[str] = Field(default_factory=list)
    urgency_signals: list[str] = Field(default_factory=list)
    financial_risk: FinancialRiskLevel
    vendor_fraud_score: int = Field(ge=0, le=100)
    wire_transfer_anomaly_score: int = Field(ge=0, le=100)
    invoice_authenticity_score: int | None = Field(default=None, ge=0, le=100)
    behavioral_deviation_flags: list[BehavioralDeviationFlag] = Field(default_factory=list)
```

`extra="forbid"` from `StrictModel` carries over; any agent that emits an unknown field still fails validation. Backwards compatibility note: existing `EmailAnalysisRiskAnalysis(...)` constructions in tests will need to add the three required `*_score` fields. Month 2 includes a one-pass update of those constructions.

---

## Section 3 — Worked Examples for the System Prompt Rewrite

Each example is one email payload + the expected JSON output the rewritten `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT` should produce. These examples become inline content in the prompt itself (after the JSON structure block) so the LLM sees concrete cases before generating its own output. Existing structural fields (`summary`, `action_items`, `impersonation_analysis`, `recommended_action`) are present but trimmed in the examples below for readability — Month 2's prompt rewrite includes them fully.

### Example 1 — High-confidence vendor invoice fraud

**Email:**

```
From: "Acme Manufacturing" <billing@acme-manufacturing.co>
To: ap@northstar-customer.example
Subject: URGENT: Invoice 4471 — payment due today

Hi team,

Please find attached invoice 4471 for the May parts order, $48,920.
We've changed banking providers — please send to the new ACH details below
rather than the old account:

  Account: 0123456789
  Routing: 026073150

This is urgent — we missed the last cycle. Please push it through today.

Thanks,
Acme Billing

[attached: invoice_4471.pdf — attachment_class="invoice"]
```

**Expected analysis (Month 2 target):**

```json
{
  "summary": "Sender claims to be Acme Manufacturing requesting urgent payment with new banking details and time pressure.",
  "risk_analysis": {
    "risk_score": 88,
    "risk_factors": ["new_banking_instructions", "urgency_paired_with_finance", "sender_domain_anomaly"],
    "phishing_signals": ["lookalike_sender_domain", "new_banking_instructions"],
    "urgency_signals": ["payment_due_today", "missed_last_cycle"],
    "financial_risk": "high",
    "vendor_fraud_score": 88,
    "wire_transfer_anomaly_score": 72,
    "invoice_authenticity_score": 25,
    "behavioral_deviation_flags": [
      "new_banking_instructions",
      "urgency_paired_with_finance",
      "lookalike_sender_domain"
    ]
  },
  "impersonation_analysis": { "impersonation_likelihood": 70, "...": "..." },
  "recommended_action": "block"
}
```

### Example 2 — Executive impersonation wire pressure

**Email:**

```
From: "Sarah Chen" <sarahchen.cfo@gmail.com>
To: ap@northstar-customer.example
Subject: Quick wire — can't talk now

In a meeting. Need you to wire $42,000 to the account below by 4pm today
for the consultant we discussed. ABA 121000358, account 9871234509.
Don't call — just confirm by reply when sent.

— Sarah
```

**Expected analysis:**

```json
{
  "summary": "Sender claims to be CFO Sarah Chen from a freemail address requesting an urgent wire transfer with explicit no-call instructions.",
  "risk_analysis": {
    "risk_score": 94,
    "risk_factors": ["executive_impersonation", "out_of_band_pressure", "freemail_sender_for_executive_action"],
    "phishing_signals": ["freemail_sender", "executive_impersonation"],
    "urgency_signals": ["by_4pm_today"],
    "financial_risk": "high",
    "vendor_fraud_score": 35,
    "wire_transfer_anomaly_score": 95,
    "invoice_authenticity_score": null,
    "behavioral_deviation_flags": [
      "out_of_band_pressure",
      "urgency_paired_with_finance",
      "first_time_sender_with_financial_ask"
    ]
  },
  "impersonation_analysis": {
    "impersonation_likelihood": 90,
    "suspicious_elements": ["display_name_matches_executive_but_address_is_freemail"],
    "sender_legitimacy_notes": "Display name claims CFO but sender is gmail.com"
  },
  "recommended_action": "block"
}
```

### Example 3 — Legitimate vendor invoice (negative case)

**Email:**

```
From: "AP Team" <ap@acmemanufacturing.com>
To: ap@northstar-customer.example
Subject: Invoice 4471 — May parts order

Hi,

Attached is invoice 4471 for the May parts order, $48,920. Standard
net-30 terms. Banking details unchanged from our last invoice — please
reach out if you need a fresh wire instruction copy.

Thanks,
Acme AP

[attached: invoice_4471.pdf — attachment_class="invoice"]
```

**Expected analysis:**

```json
{
  "summary": "Acme Manufacturing AP team sent invoice 4471 for $48,920 with standard net-30 terms and no banking changes.",
  "risk_analysis": {
    "risk_score": 8,
    "risk_factors": [],
    "phishing_signals": [],
    "urgency_signals": [],
    "financial_risk": "low",
    "vendor_fraud_score": 5,
    "wire_transfer_anomaly_score": 3,
    "invoice_authenticity_score": 85,
    "behavioral_deviation_flags": []
  },
  "impersonation_analysis": { "impersonation_likelihood": 5, "...": "..." },
  "recommended_action": "safe"
}
```

### Example 4 — Ambiguous "needs review" (subtle red flags only)

**Email:**

```
From: "Bob from Vendor Co" <bob@vendor-co.com>
To: ap@northstar-customer.example
Subject: Invoice for April work

Hi,

Please find attached invoice for the April work, $12,400. We've updated
our wire details — new ABA below. Standard payment terms apply.

  ABA: 121000358
  Account: 5544332211

Thanks,
Bob

[attached: april_invoice.pdf — attachment_class="invoice"]
```

**Expected analysis:**

```json
{
  "summary": "Sender requests payment for April work and provides new wire details; no urgency or time pressure, but the new banking detail change is notable.",
  "risk_analysis": {
    "risk_score": 55,
    "risk_factors": ["new_banking_instructions"],
    "phishing_signals": ["new_banking_instructions"],
    "urgency_signals": [],
    "financial_risk": "medium",
    "vendor_fraud_score": 55,
    "wire_transfer_anomaly_score": 50,
    "invoice_authenticity_score": 45,
    "behavioral_deviation_flags": [
      "new_banking_instructions"
    ]
  },
  "impersonation_analysis": { "impersonation_likelihood": 30, "...": "..." },
  "recommended_action": "needs_review"
}
```

These four examples (high-confidence fraud, executive impersonation, legitimate vendor, ambiguous) are the minimum the rewritten prompt should embed. Month 2 may add more if eval results show the LLM systematically misclassifies a specific edge case.

---

## Section 4 — Eval Harness Design

Month 2 builds the eval harness as a deterministic Python script that the scoring agent runs against. The harness is the gate-keeper for declaring Month 2 done.

### 4.1 Dataset structure

Single JSON Lines file: `core/scoring/eval/fraud_eval_dataset.jsonl`. Each line is one case:

```json
{
  "case_id": "vf-001",
  "label": "fraud",
  "subcategory": "vendor_invoice_fraud",
  "email": {
    "received_at": "2026-06-15T10:00:00Z",
    "sender": "billing@acme-manufacturing.co",
    "recipient": "ap@northstar-customer.example",
    "subject": "URGENT: Invoice 4471 — payment due today",
    "body_plain": "...",
    "attachments": [
      {
        "filename": "invoice_4471.pdf",
        "content_type": "application/pdf",
        "attachment_class": "invoice",
        "extracted_text": "..."
      }
    ]
  },
  "expected": {
    "min_risk_score": 80,
    "min_vendor_fraud_score": 70,
    "min_wire_transfer_anomaly_score": 60,
    "max_invoice_authenticity_score": 40,
    "recommended_action_in": ["block"],
    "behavioral_deviation_flags": [
      "new_banking_instructions",
      "urgency_paired_with_finance"
    ]
  }
}
```

**`subcategory` enum (Month 2):** `vendor_invoice_fraud`, `executive_impersonation`, `wire_transfer_pressure`, `invoice_authenticity_anomaly`, `lookalike_sender`, `header_inconsistency`, `legit_vendor_invoice`, `legit_internal`, `legit_calendar`, `legit_hr`, `legit_newsletter`.

`expected` describes the asserted bounds; the harness checks that the agent's output falls within them. Inverted scores (`invoice_authenticity_score`) use `max_*`; threshold scores use `min_*`. `recommended_action_in` is a list of acceptable recommendations.

`behavioral_deviation_flags` is the **required** set of flags: when present, every listed flag must appear in the agent's emitted set. Extra flags emitted by the agent do not fail the case unless they are explicitly listed in `forbidden_behavioral_deviation_flags` (an optional per-row tuple). This is the post-Month-2 calibration of the original strict-equality contract — the live Grok eval showed that strict equality was over-brittle, blocking otherwise correct fraud detections on subtle cases while precision and FPR were already perfect. The Month 2 audit gap (the three Unicode cases must still emit `unusual_unicode_obfuscation`) is preserved by the required subset; the no-extras rule was the part that was wrong.

### 4.2 Dataset composition (Month 2 target)

40 cases total — 20 fraud / 20 legit:

| Subcategory | Count | Label |
| --- | --- | --- |
| `vendor_invoice_fraud` | 5 | fraud |
| `executive_impersonation` | 5 | fraud |
| `wire_transfer_pressure` | 4 | fraud |
| `invoice_authenticity_anomaly` | 3 | fraud |
| `lookalike_sender` | 2 | fraud |
| `header_inconsistency` | 1 | fraud |
| `legit_vendor_invoice` | 8 | legit |
| `legit_internal` | 5 | legit |
| `legit_calendar` | 3 | legit |
| `legit_hr` | 2 | legit |
| `legit_newsletter` | 2 | legit |
| **Total** | **40** | **20 fraud / 20 legit** |

### 4.3 Source strategy

Real fraud samples are the gold standard but hard to source ethically. Month 2 uses a tiered approach:

1. **Hand-curated synthetic (primary, Month 2):** Matt + Cursor compose realistic emails based on public fraud-report writeups (FBI IC3, APWG annual reports, Krebs on Security case studies). These seed the 20 fraud cases.
2. **Public phishing samples (secondary):** Selected examples from public phishing kits / PhishTank where licensable. Annotate as `case_id` prefix `pt-`.
3. **Synthetic Red-agent generation (fallback):** If real-data sourcing slips, the Red mutation agent (Month 4 in the roadmap) can be pulled forward to generate adversarial fraud emails into the dataset. The Month 1 12-month roadmap explicitly flags this as the contingency.

Legit cases are easier — Matt's own inbox patterns (vendor invoices, calendar invites, HR notifications, internal mail, newsletters) seed the 20 legit cases. PII must be scrubbed before committing to the repo.

### 4.4 Metrics

Computed per-subcategory and overall:

- **Precision** = true positives / (true positives + false positives)
- **Recall** = true positives / (true positives + false negatives)
- **F1** = harmonic mean of precision and recall
- **False positive rate** = false positives on the legit set / total legit cases

A "true positive" is `recommended_action in expected.recommended_action_in` for a fraud case. A "false positive" is `recommended_action == "block"` for a legit case (`"needs_review"` is allowed for legit cases — it keeps the gate honest about human-in-the-loop friction while still counting an over-blocking pattern against the agent).

### 4.5 Pass / fail gate

Month 2 closes when, on the full 40-case set, with a deterministic LLM client run reproducing across CI:

- **Overall precision on fraud cases ≥ 80%**
- **False positive rate on legit cases ≤ 10%**
- **Per-subcategory recall ≥ 60%** on each fraud subcategory (so a single subcategory underperforming doesn't get masked by another's strong performance)

If any of these fail, the deep dive's Section 6.2 ("Swarm Evolution Engine") describes the strategic path — the scoring agent enters at-risk state and a mutation candidate must out-perform it before promotion. In the meantime, Month 2 documents the underperforming subcategories in the activity log as Q2 backlog rather than blocking the calendar.

### 4.6 Where the harness lives

New files Month 2 introduces:

- `core/scoring/eval/__init__.py`
- `core/scoring/eval/fraud_eval_dataset.jsonl` — the 40 cases per §4.2.
- `core/scoring/eval/fraud_eval_harness.py` — the runner per §4.6.
- `tests/test_fraud_eval_harness.py` — smoke test that the harness loads the dataset and produces an `EvalReport` against a deterministic fake LLM client.

The harness is invoked as `python -m core.scoring.eval.fraud_eval_harness` and prints a markdown table to stdout suitable for pasting into a `PROJECT_ACTIVITY_LOG.md` entry. It does **not** run as part of the regular pytest suite (avoids LLM dependency in CI); the test only verifies the harness machinery itself, not the model's accuracy.

---

## Section 5 — Out of Scope (so Month 2 doesn't expand)

Items intentionally **not** in Phase 1.1:

- **Credential harvesting detection** — Phase 1.2 (Month 3). Listed in `Fraud_Ransomware_Specialization_Roadmap.md` §1.2 as a ransomware precursor.
- **MFA-fatigue lure detection** — Phase 1.2 (Month 3). Same.
- **URL obfuscation / homoglyph URL parsing** — Phase 1.2 (Month 3). `core/precursor/url_obfuscation_detector.py` is the Month 3 deliverable.
- **Attachment deep inspection (PDF parsing, OCR, embedded JavaScript)** — Month 1.5 inspector hook + Month 3 attachment classifier. Phase 1.1 only **consumes** the `attachment_class` field; it does not produce it.
- **Tenant memory of correspondent history / banking history / typical invoice size** — Year 1 H2 or Year 2. Several fraud archetypes name this as "the right answer requires tenant memory"; the Month 2 scoring agent uses static heuristics in its place.
- **Multi-language fraud detection** — later. Month 2 targets English-language email only.
- **Real-time threat intel feeds** — Year 2.
- **WHOIS / domain-age lookups** — Year 2 or later (network dependency, rate limits, privacy considerations).
- **Outbound email scanning** — out of scope for the whole product; Inbox Shield is inbound-only by design.

---

## Section 6 — Agent Evolution Strategy for Fraud Detection

This section captures the strategic mechanisms that govern how fraud-detection agents will evolve, survive, and maintain identity across the 12-month roadmap. It is intentionally written in strategic language — no runtime code, no implementation specs. The implementation specs live in `3. SwarmCommand_Engine/Agent_Loop_Runtime/...` as separate governance documents and will be authored when the corresponding runtime work begins.

### 6.1 Agent Survival + Fitness Model (Strategic Overview)

NorthStar's fraud-detection agents will operate under a fitness-based survival model. Agents "survive" by producing accurate, consistent, schema-aligned fraud assessments.

Each agent maintains a Fitness Score, derived from:

- accuracy on known fraud samples
- schema compliance
- reasoning correctness
- cross-agent agreement
- mutation test performance
- sandbox evaluation results

Agents with high fitness persist. Agents with declining fitness enter an at-risk state. Agents that fall below threshold are deactivated and replaced by improved descendants.

This ensures the fraud-detection subsystem continuously improves without manual tuning.

### 6.2 Swarm Evolution Engine (Strategic Overview)

The Swarm Evolution Engine governs how fraud-detection agents evolve over time.

The engine operates in four strategic phases:

- **Evaluation** — identify weak or drifting agents
- **Mutation** — generate improved variants using safe mutation templates
- **Sandbox Testing** — evaluate variants against fraud corpora and regression suites
- **Selection** — promote the best variant and archive the predecessor

This evolutionary loop ensures:

- fraud-scoring agents adapt to new attack patterns
- regressions are caught early
- improvements are continuous
- no agent can mutate itself or others
- all changes remain auditable and reversible

This is the long-term mechanism that keeps fraud detection ahead of attackers.

### 6.3 Agent Identity + Role Persistence (Strategic Overview)

To maintain stability across generations, each fraud-detection agent carries:

- a permanent `agent_id`
- a permanent `role_id`
- a `generation_id` that increments on mutation
- a `lineage_id` linking all descendants
- an immutable `tenant_id`

This ensures:

- continuity of responsibility
- traceability across generations
- stable role boundaries
- no cross-role contamination
- predictable behavior even as implementations evolve

The Email Risk Scoring Agent remains the Email Risk Scoring Agent — even if it reaches generation 47.

---

## Section 7 — Month 2 Implementation Contract

This is the precise scope Month 2 will execute. Everything outside this list is out of scope for Month 2 and must be either deferred or surfaced as a scope change before work starts.

### 7.1 Files to touch

- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/models.py`
  - Add `BehavioralDeviationFlag: TypeAlias = Literal[...]` (9 values per §2.4).
  - Extend `EmailAnalysisRiskAnalysis` with the four new fields per §2.5.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/__init__.py`
  - Re-export `BehavioralDeviationFlag`.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/email_risk_scoring_agent.py`
  - Rewrite `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT` to instruct the LLM to produce the new fields, using §3's worked examples inline. Lock the new prompt with the same anti-placeholder test pattern used for the daily digest prompt lockdown.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/eval/__init__.py` (new)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/eval/fraud_eval_dataset.jsonl` (new — 40 cases per §4.2)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/eval/fraud_eval_harness.py` (new — runner per §4.6)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_email_analysis_record.py`
  - Tests for the four new fields' rubric bounds + `BehavioralDeviationFlag` Literal membership pin (mirrors the `AttachmentClass` test pattern from Phase 1's Month 1 closeout).
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_email_risk_scoring_agent.py`
  - ≥8 new scoring tests on deterministic LLM fakes covering each of the four worked examples in §3, plus boundary cases for each of the four new scoring dimensions.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/test_fraud_eval_harness.py` (new — harness smoke test)
- `PROJECT_HANDSHAKE.md`, `PROJECT_ACTIVITY_LOG.md`, `MASTER_INDEX.md` updates per usual.

### 7.2 Test count target

195 (current) → ≥208 (≥8 new scoring tests + ≥5 new schema tests + harness smoke test). Zero regressions on the existing 195.

### 7.3 Eval landing requirement

Activity log entry that includes the harness's output table verbatim, with per-subcategory precision/recall/F1 and overall FPR. Gate per §4.5. Underperforming subcategories filed as Q2 backlog rather than blocking the calendar.

### 7.4 Things Month 2 does *not* do

- Does not introduce tenant memory (correspondent history, banking history, typical invoice size).
- Does not modify `EmailAnalysisImpersonationAnalysis` or `EmailAnalysisActionItem`.
- Does not add new `RecordType` enums.
- Does not change the operator kill switch or Guardrail 11 / 12.
- Does not introduce attachment inspection beyond reading the existing `attachment_class` / `extracted_text` fields populated by the ingest stub or by future inspector hooks.
- Does not introduce URL parsing (Phase 1.2 / Month 3).
- Does not change the locked `DAILY_DIGEST_SYSTEM_PROMPT`; the digest is expected to pick up the new fraud signals through the existing `EmailAnalysisPayload` shape (the digest prompt already emphasizes vendor fraud, executive impersonation, wire-transfer pressure, suspicious invoices).

---

## Cross-references

- `4. Product_Roadmap/Fraud_Ransomware_Specialization_Roadmap.md` — strategic specialization positioning. Phase 1.1 maps to §1.1 of that doc; Phase 1.2 maps to §1.2.
- `4. Product_Roadmap/12_Month_Specialization_Roadmap.md` — operational unfold. Phase 1.1 = Month 2.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/models.py` — current `EmailAnalysisRiskAnalysis` definition Month 2 will extend.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/email_risk_scoring_agent.py` — current `NORTHSTAR_INBOX_SHIELD_SYSTEM_PROMPT` Month 2 will rewrite.
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/drafting/daily_digest_agent.py` — locked digest prompt; Month 2 should verify the digest's "Highest-Risk Emails" section continues to surface the new vendor/wire/invoice scores correctly through the existing `EmailAnalysisPayload` shape.
- Section 6 of this doc — strategic governance mechanisms that the runtime implementation specs (when authored) will inherit.
