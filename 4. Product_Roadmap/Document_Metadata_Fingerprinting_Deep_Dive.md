# Document Metadata Fingerprinting — Implementation Spec (Deep Dive)

**Status:** §11 SIGNED 2026-05-24 by Matt Nichol; implementation landed 2026-05-24; runtime verification 745 passed, 1 skipped.  
**Authors:** Matt (operator decisions) + AI scribe (capture).  
**Last reviewed:** 2026-05-24 UTC.  
**Source-of-truth links:** `think_sheet.md` (Document Metadata Fingerprinting promote row), `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md` (baseline primitive), `4. Product_Roadmap/Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` (paired BEC detector), `PROJECT_GUARDRAILS.md` (Guardrails 11 + 12).

This document is the specification contract for Document Metadata Fingerprinting v1. Once signed, every implementation receipt must cite this file by section number.

---

## §0 Purpose

Document Metadata Fingerprinting flags invoice/document-integrity anomalies before payment:

> A known vendor email includes a PDF Producer or Creator fingerprint that has not been seen before for that vendor and tenant.

The detector does **not** prove the PDF was forged. It proves the document tooling fingerprint is **new or stale** relative to vendor memory, which is a strong BEC precursor when paired with Financial State Ledger / Delta Tripwire.

v1 is metadata-only: upstream extractors populate bounded `pdf_metadata` on `EmailAttachmentMeta`. The runtime does not parse PDF bytes, run OCR, or fetch attachments from disk or network.

---

## §1 Scope

### In scope (v1)

- Bounded attachment field `pdf_metadata` with optional `producer` and `creator` strings (max 512 chars each).
- Deterministic extraction from qualifying PDF / invoice attachments only.
- Vendor Baseline Store integration via `pdf_producer_fingerprint` signal type and check-then-ingest ordering.
- Pure dataclass assessment for scoring overlay consumers.
- Risk-floor recommendation and `needs_review` action on `new` / `expired` fingerprints.
- Profile gating: LOW skips the check; MEDIUM runs normal floor; HIGH applies a stricter floor (+10, cap 95) — same pattern as email authentication, without expanding Tiered Detection `DetectorIdentity` enum.
- Gate tests for extraction, baseline states, lift-only overlay, kill switch, and tenant isolation.

### Out of scope (v1)

- PDF byte parsing, `pypdf` / `pdfplumber`, OCR, password-protected PDF handling, image-only PDF analysis.
- Storing raw Producer/Creator strings in Vendor Baseline Store (hash-only via existing normalization).
- Automatic block/quarantine.
- New `DetectorIdentity` enum entry.
- Cross-tenant reputation.

---

## §2 Locked Architectural Decisions

| # | Decision | Locked Value | Rationale |
|---|---|---|---|
| D1 | Runtime location | `core/scoring/document_metadata_detector.py` | Scoring-layer detector, not a new production-state primitive. |
| D2 | Persistent storage | Vendor Baseline Store only (`pdf_producer_fingerprint`) | Reuses audited hash-only baseline; no schema revision. |
| D3 | Public API | `assess_document_metadata_fingerprint(...)` returning frozen dataclasses | Matches Financial State Ledger pattern. |
| D4 | Input surface | `EmailInboundPayload` + explicit `tenant_id`, `vendor_domain`, `now` | Caller-owned tenant/vendor identity. |
| D5 | Metadata source | `EmailAttachmentMeta.pdf_metadata` only | No raw attachment bytes in v1. |
| D6 | Qualifying attachments | PDF-like (`content_type` contains `pdf`, filename ends with `.pdf`) OR `attachment_class` in `invoice`, `payment_request` | Avoids flagging non-document attachments. |
| D7 | Fingerprint candidates | Non-empty `producer` and `creator` each become separate `pdf_producer_fingerprint` checks | Producer-or-Creator baseline rule from Vendor Baseline Store. |
| D8 | Baseline order | `check_signal` before `ingest_signal` | First observation must surface as `new`. |
| D9 | Risk floor | Any `new` or `expired` fingerprint → floor `75`, action `needs_review` | Moderate/high document-integrity signal; below FSL `85` because legitimacy is common. |
| D10 | Verification guidance | Findings recommend human review of document tooling change before trusting invoice authenticity | Client-legible; pairs with FSL out-of-band payment verification. |
| D11 | Lift-only | Never lowers LLM or other deterministic scores | Same invariant as all overlay detectors. |
| D12 | Profile gating | Skip on LOW; MEDIUM/HIGH run; HIGH adds +10 floor bump (cap 95) | Mirrors email authentication without enum expansion. |
| D13 | Kill switch | Inherited from Vendor Baseline Store entry points | No duplicate gate in detector. |
| D14 | Data minimization | Returned findings use `redacted_display` + hash only; raw metadata not persisted | Aligns with baseline hash-only contract. |

---

## §3 Metadata Extraction Contract

### Attachment qualification

An attachment is inspected when:

1. `pdf_metadata` is not `None`, and
2. At least one of `producer` or `creator` is non-empty after strip, and
3. Any of:
   - `content_type` contains `pdf` (case-insensitive), or
   - `filename` ends with `.pdf` (case-insensitive), or
   - `attachment_class` is `invoice` or `payment_request`.

### Normalization

Reuse Vendor Baseline Store `pdf_producer_fingerprint` normalization: lowercase, collapse whitespace, strip. Malformed/empty strings after normalization are dropped silently.

### Dedupe

Within one email, dedupe by normalized fingerprint string before baseline lookup (one check/ingest per unique fingerprint).

---

## §4 API Contract

### Module: `core/scoring/document_metadata_detector.py`

```python
assess_document_metadata_fingerprint(
    *,
    tenant_id: str,
    vendor_domain: str,
    email: EmailInboundPayload,
    now: datetime,
) -> DocumentMetadataAssessment
```

### Types

- `ExtractedDocumentFingerprint` — source attachment index/filename, field (`producer` | `creator`), `redacted_display`
- `DocumentMetadataFinding` — baseline state, hash, explanation
- `DocumentMetadataAssessment` — vendor_domain, extracted, findings, `recommended_risk_floor`, `recommended_action`, `indicators`

---

## §5 Scoring Contract

| Condition | `recommended_risk_floor` | `recommended_action` |
|---|---:|---|
| No qualifying metadata | `0` | `"none"` |
| Only `known` fingerprints | `0` | `"none"` |
| At least one `new` or `expired` | `75` | `"needs_review"` |

Overlay integration: max-merge floor into `_overlay_ransomware_precursor`; append `document_metadata:*` indicators to `risk_factors` / `phishing_signals` when lifted.

---

## §6 Gate Tests

1. Public API surface locked (`__all__`, frozen dataclasses).
2. No-metadata path: no findings, floor 0, no baseline rows.
3. First-seen producer: `new` finding, floor 75, baseline row written.
4. Known producer: no finding on second run.
5. Expired producer: `expired` finding after TTL expiry.
6. Check-before-ingest ordering (spy).
7. Creator-only attachment path works.
8. Non-PDF attachment without invoice class ignored.
9. Malformed/empty metadata ignored without crash.
10. No raw producer/creator leakage in assessment representation.
11. Vendor domain validation raises `GovernanceError`.
12. Kill switch inheritance.
13. Tenant isolation.
14. Overlay lift-only invariant.
15. Overlay skips on LOW profile.
16. Overlay HIGH stricter floor (+10, cap 95).
17. Duplicate producer across two attachments deduped for floor purposes.
18. `grok_audit_runner.py` exposes `document_metadata_fingerprinting` target.

---

## §7 Boundaries & Safety

| Concern | Enforcement |
|---|---|
| Tenant isolation | Vendor Baseline Store per-tenant files only. |
| Kill switch | Inherited from baseline APIs. |
| Scope creep | No PDF parser dependency in v1. |
| External I/O | None. |

---

## §8 §11 Lockdown Signature

**Signed by:** Matt Nichol  
**Date:** 2026-05-24  
**Decisions locked:** D1–D14 above; v1 metadata-only; `pdf_producer_fingerprint` only; floor 75; no `DetectorIdentity` enum expansion; profile gating mirrors email authentication.

Implementation may proceed against this contract.
