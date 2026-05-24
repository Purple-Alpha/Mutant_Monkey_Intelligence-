# Financial State Ledger / Delta Tripwire — Implementation Spec (Deep Dive)

**Status:** §11 SIGNED 2026-05-24 by Matt; implementation landed 2026-05-24; runtime verification 621 passed, 1 skipped; independent Grok audit approved.  
**Authors:** Matt (operator decisions) + AI scribe (capture).  
**Last reviewed:** 2026-05-24 UTC.  
**Source-of-truth links:** `think_sheet.md` (Financial State Ledger promote row), `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md` (baseline primitive), `PROJECT_GUARDRAILS.md` (Guardrails 11 + 12).

This document is the specification contract for the Financial State Ledger / Delta Tripwire detector. No implementation lands until the §11 Lockdown Signature is filled in by the operator. Once signed, every implementation receipt must cite this file by section number.

---

## §0 Purpose

The Financial State Ledger / Delta Tripwire flags a high-risk condition before money moves:

> A known vendor email contains a payment-destination signal that has not been seen before for that vendor and tenant.

The detector is intentionally narrow. It does **not** decide whether the new payment detail is fraudulent. It decides whether the payment detail is **new enough to require out-of-band verification**. The business control is simple and client-legible:

1. Extract payment-destination signals from an inbound email.
2. Compare each signal against the tenant's historical Vendor Baseline Store.
3. If any signal is `new` or `expired`, emit a Delta Tripwire finding.
4. Establish or refresh the baseline after checking, so the first observation is flagged and later observations become known.
5. Attach a mandatory verification recommendation: verify through a previously-known vendor channel, not the email that introduced the change.

This is the first detector built on top of the Vendor Baseline Store primitive. It is the clearest SMB BEC control in the current roadmap because it maps directly to the highest-dollar fraud pattern: payment redirection through new ACH, routing, IBAN, SWIFT/BIC, account, or payment-portal details.

---

## §1 Scope

### In scope (v1)

- Deterministic extraction from:
  - `EmailInboundPayload.body_plain`
  - `EmailAttachmentMeta.extracted_text`
- Closed payment-signal set:
  - `routing_number`
  - `swift_bic_code`
  - `iban`
  - `account_number`
  - `payment_portal_url`
- Vendor Baseline Store integration using the check-then-ingest pattern from `Vendor_Baseline_Store_Deep_Dive.md` Appendix A.
- Tenant isolation through the Vendor Baseline Store only; no new persistent database.
- Pure dataclass assessment return object for scoring/reporting consumers.
- Risk-floor recommendation and action recommendation for downstream scoring overlay / daily digest.
- Gate tests proving first-seen, known, expired, malformed, multi-signal, and attachment-text paths.

### Out of scope (v1)

- Raw PDF parsing, OCR, image-only invoice handling, or attachment sandboxing. v1 consumes only already-populated `extracted_text`.
- Fuzzy matching or near-match financial-number detection. The Vendor Baseline Store is hash-only and exact-match-after-normalization.
- Bank-account ownership verification, bank API lookup, vendor KYB lookup, sanctions screening, or payment-rail validation.
- A portal, confirmation UI, or workflow state machine.
- Automatic blocking, quarantine, or email deletion.
- Cross-tenant reputation sharing.
- Storing raw financial strings anywhere outside the short-lived in-memory extraction path.

---

## §2 Locked Architectural Decisions

| # | Decision | Locked Value | Rationale |
|---|---|---|---|
| D1 | Runtime location | `core/scoring/financial_state_ledger.py` | This is a detector/scoring input, not a new production-state primitive. Persistent state remains in Vendor Baseline Store. |
| D2 | Persistent storage | Vendor Baseline Store only | Avoids a second state surface and preserves the hash-only, TTL-bounded posture already audited. |
| D3 | Public API shape | Pure dataclass return + explicit stateful baseline calls inside one detector function | Calling code receives a deterministic assessment; the detector handles check-then-ingest so downstream callers cannot accidentally ingest before checking. |
| D4 | Input surface | `EmailInboundPayload` + explicit `tenant_id` + explicit `vendor_domain` + explicit `now` | Keeps tenant and vendor identity caller-owned. The detector does not infer tenant id and does not re-normalize vendor identity beyond validation. |
| D5 | Signal extraction sources | `body_plain` and attachment `extracted_text` only | These are the current governed text surfaces. Raw PDF/OCR remains a separate detector/tooling decision. |
| D6 | Signal types | Reuse the five existing Vendor Baseline Store financial signal types | No Vendor Baseline Store schema revision is needed for v1. |
| D7 | Baseline order | Always `check_signal` before `ingest_signal` | The first observation must be visible as `new`; ingesting first would erase the alert. |
| D8 | Reads/writes | `check_signal` reads do not audit; `ingest_signal` writes audit through Vendor Baseline Store | Inherits the already-audited baseline audit discipline. |
| D9 | Risk floor | Any `new` or `expired` financial signal recommends risk floor `85` and action `needs_review` | High enough to force human review, below absolute max because legitimacy is possible. |
| D10 | Verification guidance | Every Delta Tripwire finding includes the same mandatory wording | "Verify through a previously-known vendor channel; do not use phone numbers, links, or instructions from this email." |
| D11 | No autonomous payment decision | Detector never marks a payment as safe, approved, blocked, or confirmed | NorthStar flags and explains; the human workflow performs verification. |
| D12 | Kill switch | No separate kill-switch check in this detector; Vendor Baseline Store entry points enforce Guardrail 12 | Avoids duplicating the gate. If baseline state is stopped, the detector cannot check or ingest. |
| D13 | Data minimization | Raw extracted financial strings are never returned in findings or persisted | Findings return signal type, baseline state, source surface, redacted display, and hash only. |
| D14 | Client artifact | Finding text must be digest/report friendly | This detector exists to give MSPs a concrete client-facing line: "New payment destination observed for vendor; verify out-of-band before payment." |

Changing any locked decision requires reopening this spec, not a code-level workaround.

---

## §3 Signal Extraction Contract

### Extraction sources

The detector inspects text in this order:

1. `email.body_plain`
2. Each `attachment.extracted_text` where `extracted_text is not None`

Each extracted signal records its source:

```python
SignalSource = Literal["body_plain", "attachment_extracted_text"]
```

For attachments, the finding also records:

- `attachment_filename`
- `attachment_index`

The detector does **not** read raw attachment bytes, `content_ref`, live files, URLs, or external network resources.

### Closed extracted signal types

```python
FinancialSignalType = Literal[
    "routing_number",
    "swift_bic_code",
    "iban",
    "account_number",
    "payment_portal_url",
]
```

These map one-to-one to existing Vendor Baseline Store signal types. The detector must not invent signal types.

### Extraction rules

| Signal | v1 extraction rule | Required guardrail |
|---|---|---|
| `routing_number` | Match labelled ABA / routing phrases plus 9-digit candidates near payment language | Do not treat every standalone 9-digit number as a routing number. |
| `swift_bic_code` | Match labelled SWIFT / BIC phrases plus 8 or 11 alphanumeric candidate | Must pass Vendor Baseline Store normalization before use. |
| `iban` | Match labelled IBAN phrases plus country-code-prefixed alphanumeric candidate length 5–34 | Must pass Vendor Baseline Store normalization before use. |
| `account_number` | Match labelled account / acct / account no. phrases plus numeric candidate | Must require nearby financial label; no free-floating number harvesting. |
| `payment_portal_url` | Extract URLs or host-like strings near pay / remit / portal / invoice / billing language | Store only host via Vendor Baseline Store normalization. |

The extractor may be conservative. A missed extraction is safer than a noisy detector that turns every invoice reference number into an account-number alert. v1 should bias toward high-precision labelled patterns.

### Duplicate handling

Within one email:

- Deduplicate by `(signal_type, normalized_value, source_kind)`.
- If the same normalized signal appears in body and attachment text, keep both source records but count the baseline state once for risk-floor purposes.
- Never include raw values in the returned assessment. Use `redacted_display`, e.g.:
  - routing/account numbers: `***6789`
  - IBAN: `GB82...5432`
  - SWIFT/BIC: first 4 + `...`
  - portal URL: hostname only

---

## §4 API Contract

### Module: `core/scoring/financial_state_ledger.py`

Public surface:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from core.blackboard import EmailInboundPayload
from core.production_state.vendor_baseline import SignalState


FinancialSignalType = Literal[
    "routing_number",
    "swift_bic_code",
    "iban",
    "account_number",
    "payment_portal_url",
]

SignalSource = Literal["body_plain", "attachment_extracted_text"]


@dataclass(frozen=True)
class ExtractedFinancialSignal:
    signal_type: FinancialSignalType
    source: SignalSource
    redacted_display: str
    attachment_filename: str | None = None
    attachment_index: int | None = None


@dataclass(frozen=True)
class DeltaTripwireFinding:
    signal_type: FinancialSignalType
    baseline_state: SignalState  # "new" | "known" | "expired"
    redacted_display: str
    source: SignalSource
    signal_hash: str | None
    attachment_filename: str | None = None
    attachment_index: int | None = None
    explanation: str = ""
    recommended_verification: str = ""


@dataclass(frozen=True)
class FinancialStateLedgerAssessment:
    vendor_domain: str
    extracted_signals: tuple[ExtractedFinancialSignal, ...]
    findings: tuple[DeltaTripwireFinding, ...]
    recommended_risk_floor: int
    recommended_action: Literal["none", "needs_review"]
    requires_out_of_band_verification: bool
```

### Functions

```python
def assess_financial_state_delta(
    *,
    tenant_id: str,
    vendor_domain: str,
    email: EmailInboundPayload,
    now: datetime,
) -> FinancialStateLedgerAssessment:
    """Extract financial destination signals, check each against the Vendor
    Baseline Store, then ingest each valid signal after checking.

    Behaviour:
    - Validates `vendor_domain` as already-normalized lowercase domain.
    - Extracts only the five locked financial signal types from §3.
    - Calls `check_signal` before `ingest_signal` for each valid signal.
    - Emits one finding for every signal whose baseline state is "new" or
      "expired".
    - Emits no finding for "known" signals, but still refreshes the baseline.
    - Returns `recommended_risk_floor=85` and `recommended_action="needs_review"`
      if any finding exists; otherwise returns `0` and `"none"`.
    - Never returns raw financial strings.
    - Does not write Blackboard records directly; Vendor Baseline Store writes
      its own audit records on ingest.
    """
```

Internal helper functions may exist for extraction, redaction, and source assembly, but the only public function is `assess_financial_state_delta`.

---

## §5 Baseline Consumption Pattern

For every valid extracted signal:

```python
lookup = check_signal(
    tenant_id=tenant_id,
    vendor_domain=vendor_domain,
    signal_type=signal.signal_type,
    raw_value=raw_value,
    now=now,
)

if lookup.state in ("new", "expired"):
    # Emit DeltaTripwireFinding before learning the value.
    ...

record = ingest_signal(
    tenant_id=tenant_id,
    vendor_domain=vendor_domain,
    signal_type=signal.signal_type,
    raw_value=raw_value,
    now=now,
)
```

The post-ingest `record.signal_hash` may be copied into the finding. The raw value must not be copied.

Malformed extracted candidates are dropped silently from the assessment but should be covered by tests. They are not findings because a malformed candidate does not prove a payment change.

---

## §6 Scoring & Action Contract

### Risk floor

| Condition | `recommended_risk_floor` | `recommended_action` | Verification |
|---|---:|---|---|
| No valid extracted financial signals | `0` | `"none"` | `False` |
| Only `known` signals | `0` | `"none"` | `False` |
| At least one `new` signal | `85` | `"needs_review"` | `True` |
| At least one `expired` signal | `85` | `"needs_review"` | `True` |
| Multiple `new` / `expired` signals | `85` | `"needs_review"` | `True` |

The detector does not return `block`. A new payment destination can be legitimate. The correct control is verified review, not automatic rejection.

### Required finding wording

Every finding must include wording equivalent to:

> New or stale payment-destination signal observed for this vendor. Verify through a previously-known vendor channel before payment. Do not use phone numbers, links, or payment instructions from this email to verify the change.

This wording is part of the client-facing artifact contract and must be pinned by tests.

---

## §7 Gate Tests

Implementation must pass all tests below before §4 can be claimed closed.

1. **Public API surface.** Module exports `assess_financial_state_delta` and the dataclasses/types listed in §4; no extra public mutating helpers.
2. **No-signal path.** Email with no financial signal returns no findings, risk floor `0`, action `"none"`, and writes no Vendor Baseline rows.
3. **First-seen routing number.** Labelled routing number in `body_plain` returns one `new` finding, risk floor `85`, action `"needs_review"`, verification required, and writes a baseline row after checking.
4. **Known signal path.** Running the same email a second time returns no finding and still refreshes the baseline.
5. **Expired signal path.** An expired baseline row returns an `expired` finding and refreshes the row after assessment.
6. **Check-before-ingest ordering.** A spy/fake around Vendor Baseline functions proves `check_signal` is called before `ingest_signal`.
7. **Attachment text path.** Labelled account number in `attachment.extracted_text` produces a finding with `source="attachment_extracted_text"`, filename, and index.
8. **Body + attachment dedupe.** Same normalized signal in body and attachment does not double-raise risk floor, but source metadata remains inspectable.
9. **Payment portal host extraction.** URL near payment/remit language produces a `payment_portal_url` finding with host-only redaction.
10. **Unlabelled number suppression.** Standalone invoice/reference numbers do not create routing/account findings.
11. **Malformed candidate suppression.** Bad routing/SWIFT/IBAN/account candidates do not crash and do not create findings.
12. **Multiple signal types.** Email containing routing number + account number + portal URL returns one finding per new/expired signal type.
13. **No raw value leakage.** Assessment string/dict representation contains no raw routing/account/IBAN values from the source email.
14. **Verification wording pin.** Findings include the required out-of-band verification language from §6.
15. **Vendor domain validation.** Uppercase, whitespace, path separators, empty, or dot-broken domains raise `GovernanceError`.
16. **Kill switch inheritance.** With the production kill switch engaged, assessment raises `KillSwitchEngaged` through Vendor Baseline Store and writes no rows.
17. **Tenant isolation.** Same signal for two tenants produces separate baseline state; tenant B does not make tenant A's first observation known.
18. **No direct Blackboard write.** Detector does not call orchestrator route functions directly; Vendor Baseline Store remains the only write path.
19. **No new persistent state.** Test scans for new SQLite/JSON state writes outside Vendor Baseline Store.
20. **Integration overlay hook.** Existing scoring overlay can max-merge the returned `recommended_risk_floor` without lowering any LLM-derived score.
21. **Digest/report readability.** Finding fields are sufficient to render a client-readable line without raw financial details.
22. **Grok audit package target.** `audit_tools/grok_audit_runner.py` can be extended with a `financial_state_ledger` target before implementation is claimed closed.

If any test in this list does not pass, the implementation receipt is not allowed to claim §4 closed.

---

## §8 Boundaries & Safety

| Concern | Enforcement |
|---|---|
| Guardrail 11 tenant isolation | Vendor Baseline Store per-tenant files and salts; detector never stores its own cross-tenant state. |
| Guardrail 12 kill switch | Inherited from Vendor Baseline Store calls; if baseline access is stopped, assessment stops. |
| Raw financial data | Raw strings exist only in memory long enough to call `check_signal` / `ingest_signal`; returned assessment uses redacted display + hash only. |
| False positives | Detector recommends review, not block. Legitimate bank changes are expected and handled by two-channel confirmation. |
| Alert fatigue | Conservative extraction, labelled patterns only, no unlabelled number harvesting. |
| Scope creep | No portal, no payment approval workflow, no bank verification, no OCR in v1. |
| External calls | None. No bank APIs, URL fetches, reputation feeds, or live vendor lookups. |

---

## §9 Downstream Integration

### Scoring overlay

The implementation should wire into `core/scoring/email_risk_scoring_agent.py` the same way header divergence and ghost-thread signals do: max-merge the returned `recommended_risk_floor` into the final `risk_score`, preserving the lift-only invariant.

If final score is lifted because of this detector, the analysis/reporting surface should include a factor such as:

```text
Financial Delta Tripwire: new payment destination observed for vendor.example.
Verify through a previously-known vendor channel before payment.
```

### Daily digest / report

The daily digest should be able to render:

- Vendor domain
- Signal type
- Baseline state (`new` / `expired`)
- Redacted display
- Source (`body_plain` / attachment filename)
- Required verification instruction

No raw financial strings should appear in digest output.

### Two-channel confirmation

This detector creates the strongest input for the future Two-channel confirmation enforcement workflow. It does not implement that workflow. The future workflow should consume the finding and record whether a human confirmed the payment change through a known-safe channel.

---

## §10 V2 Deferrals & Explicit Non-Goals

| Deferral | Rationale |
|---|---|
| OCR / image-only invoice extraction | Belongs to Structural Payload Anomalies / OCR dependency decision. |
| PDF metadata correlation | Belongs to Document Metadata Fingerprinting. |
| Phone-number baselining | Requires Vendor Baseline Store schema revision for `phone_number`; belongs to Callback Phishing / TOAD. |
| Vendor portal / challenge-response | Stage B workflow surface; not required for Stage A detector. |
| Bank API verification | Adds external dependency, compliance questions, and false sense of certainty. |
| Fuzzy account-number matching | Conflicts with hash-only exact-match baseline. |
| Auto-blocking payment changes | Legitimate changes exist; the correct action is human verification. |

---

## §11 Lockdown Signature

This spec is locked when the block below is filled in. The implementation receipt for the detector must cite this file by section number.

```text
LOCKED BY:  Matt (operator)
LOCK DATE:  2026-05-24
COMMENTS:   All §2 architectural decisions (D1-D14) locked end-to-end during
            the 2026-05-24 spec-first session. Highlights:
              - Detector lives in core/scoring/financial_state_ledger.py
                (scoring input, NOT a new production-state primitive).
              - Persistent state stays in Vendor Baseline Store only;
                no second state surface is opened.
              - Public surface is one function (assess_financial_state_delta)
                returning a frozen dataclass; no extra public mutators.
              - Extraction sources in v1 are EmailInboundPayload.body_plain
                and EmailAttachmentMeta.extracted_text only. No raw PDF /
                no OCR / no remote document fetch in v1.
              - Five financial signal types reuse Vendor Baseline Store
                enum entries (routing_number, swift_bic_code, iban,
                account_number, payment_portal_url).
              - check_signal is ALWAYS called before ingest_signal; ordering
                is enforced by a gate test, not a comment.
              - Any signal in state `new` or `expired` raises
                recommended_risk_floor = 85 and
                recommended_action     = needs_review.
              - Raw financial strings never leave the in-memory extraction
                path; only normalized hash digests reach storage.
              - Every finding includes the mandatory out-of-band
                verification wording (D14 client-artifact contract).
              - Kill switch inherits from Vendor Baseline Store entry
                points; the detector does NOT introduce its own kill path.
              - §7 22-test gate is the closure contract. Partial
                implementations do NOT close §4.
              - Grok independent-audit target for `financial_state_ledger`
                must be wired into audit_tools/grok_audit_runner.py
                BEFORE the implementation is claimed closed (§7 test #22).
              - Implementation work does NOT begin until Matt issues the
                explicit "start build" signal in chat.
```

Once signed:

- Every implementation receipt must cite this file by section number.
- Any deviation from a §2 locked decision requires a new spec revision.
- The §7 gate test list is the closure contract.
- Implementation still requires Matt's explicit `start build` signal after signature.

