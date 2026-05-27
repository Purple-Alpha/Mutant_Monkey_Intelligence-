# Client-Facing 5-Axis Email Scoring Rubric — Spec-First Deep Dive

**Status:** §11 SIGNED 2026-05-25 by Matt Nichol; implementation not yet started.  
**Date:** 2026-05-25  
**Owner:** Matt Nichol  
**Source-of-truth links:** `think_sheet.md` (promote row + 2026-05-24 idea-level stress test + 2026-05-25 §10 sub-question stress test), `PROJECT_HANDSHAKE.md` (2026-05-25 Stage A scope + A→B→C→D ordering), `THREAT_INTEL_LOG.md` (2026-05-25 strategic rationale), `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/email_risk_scoring_agent.py` (internal 0-100 scoring path), `4. Product_Roadmap/Product_Sheets/Fraud_Detection_Product_Sheet.md`.

This document is the signed specification contract for a client-facing explanation layer that sits on top of the existing internal runtime score.

---

## §0 Purpose

NorthStar currently produces rich internal scoring (`risk_score` 0-100 + detector/overlay evidence), but client-facing reporting risk is still too opaque for non-technical SMB operators.

The 5-axis rubric exists to solve one problem:

> Explain *why* an email is risky in a stable, human-readable format that MSPs can use in monthly reviews, without weakening or replacing the internal scoring engine.

This is a translation layer, not a second detector stack.

---

## §1 Scope

### In scope (v1)

- A deterministic projection from existing analysis outputs to five client-facing axes, each scored `0..2`.
- A single derived total `axis_total` in `0..10`.
- Axis labels that remain stable once released:
  1. `sender_identity`
  2. `conversation_continuity`
  3. `vendor_payment_history`
  4. `document_integrity`
  5. `origin_timing`
- A plain-English explanation block per axis (`why_this_score`), bounded-length and safe for reports.
- A deterministic consistency contract so the 5-axis score cannot materially contradict the internal `risk_score`.
- Report-surface contract only (analysis payload extension + digest/report rendering contract).
- Gate-test plan (spec-level now; implementation tests later).

### Out of scope (v1)

- No replacement of existing `risk_score` or `recommended_action`.
- No new network calls, GeoIP lookups, ASN lookups, phone lookup, or external enrichment.
- No new detector families.
- No ML model retraining or new LLM prompt complexity.
- No tenant-specific custom axis definitions in v1.
- No client-configurable weighting in v1.

---

## §2 Locked Design Decisions (§11)

| # | Decision | Locked value |
|---|---|---|
| D1 | Rubric type | Explanation layer only; internal scoring remains source of truth. |
| D2 | Axis count | Exactly five axes, 0-2 each (max total 10). |
| D3 | Axis naming stability | Axis names are versioned product vocabulary; no rename without spec revision. |
| D4 | Determinism | Axis outputs must be deterministic from existing validated analysis payload + deterministic detectors. |
| D5 | Lift-only relationship | Axis projection may increase explainability, never downgrade internal risk or action. |
| D6 | Contradiction guard | If axis output would understate a high-risk internal result, guardrails force an override band + explanation. |
| D7 | Data minimization | No raw body snippets, no full headers, no account/routing numbers in client-facing axis text. |
| D8 | Tenant isolation | Axis records derive only from same-tenant analysis artifacts. |
| D9 | Version pin | First release label pinned as `rubric_version = "v1"`. |
| D10 | Weighting | Equal weighting (`sum(axis_scores)`), no per-axis weighting in v1. |
| D11 | Explainability bounds | Each `why_this_score` capped to strict max length. Final v1 cap is 160 chars per D15. |
| D12 | Failure posture | On rubric-projection failure, do not fail-open: internal analysis still emits; rubric marks `unavailable` with explicit audit marker. |
| D13 | Axis weighting | Equal weights for v1. Weight revision deferred to v2 and gated on real per-axis FP/FN data collected after v1 ships. (See `think_sheet.md` 2026-05-25 sub-question stress test, Q1.) |
| D14 | Axis order | Fixed axis order for v1 in the order listed in §3. Rendering contract must include the explicit line "order is fixed for stability, not priority" wherever the rubric is shown so the order isn't read as a ranking. (See sub-question stress test Q2.) |
| D15 | `why_this_score` max length | 160 chars for v1, hard validator. v2 may relax the cap (proposed 220) **only** if v1 production data shows ≥ 5% of `why_this_score` outputs truncating useful content. (See sub-question stress test Q3.) |
| D16 | `axis_total` visibility | `axis_total` is visible to clients in v1, but the rendering contract pins `recommended_action` (`safe` / `needs_review` / `block`) as the most prominent element and uses the per-axis breakdown — not the total — as the primary reasoning surface. The total is a navigation aid, not the headline. (See sub-question stress test Q4.) |
| D17 | v1 client-facing surface | Report-only / monthly digest in v1. Per-email operator-side rubric view explicitly deferred to v1.1, gated on at least one MSP discovery conversation requesting it. (See sub-question stress test Q5.) |

---

## §3 Axis Definitions (0–2 each)

### 3.1 `sender_identity`

Measures confidence that sender identity context is consistent.

- **0 (stable):** No meaningful sender-identity anomaly evidence.
- **1 (caution):** One moderate anomaly (e.g., first-time finance ask without strong impersonation cues).
- **2 (high concern):** Strong identity anomaly pattern (lookalike domain, major header divergence, strong impersonation cues).

Primary evidence sources:
- `header_divergence_detector`
- `impersonation_analysis`
- `behavioral_deviation_flags` (`lookalike_sender_domain`, etc.)

---

### 3.2 `conversation_continuity`

Measures whether thread/context continuity appears authentic.

- **0:** No continuity anomaly pattern.
- **1:** Mild continuity uncertainty.
- **2:** Strong ghost-thread / fabricated continuity pattern.

Primary evidence sources:
- `ghost_thread_detector`
- thread-continuity language and supporting structured indicators already present in analysis path.

---

### 3.3 `vendor_payment_history`

Measures risk around payment-destination change behaviors and vendor financial-change context.

- **0:** No payment-change anomaly context.
- **1:** Ambiguous or moderate financial change signal.
- **2:** Strong payment-change / financial destination anomaly requiring known-channel verification.

Primary evidence sources:
- Financial State Ledger / Delta Tripwire outputs
- `vendor_fraud_score`, `wire_transfer_anomaly_score`
- `behavioral_deviation_flags` (`new_banking_instructions`, `first_time_sender_with_financial_ask`, `urgency_paired_with_finance`)

---

### 3.4 `document_integrity`

Measures whether attached document evidence appears structurally/authentically consistent.

- **0:** No meaningful document-integrity concerns.
- **1:** Moderate integrity concerns.
- **2:** Strong invoice/document authenticity concerns.

Primary evidence sources:
- Document Metadata Fingerprinting output
- `invoice_authenticity_score` (inverted semantics already defined in runtime prompt contract)
- attachment-level anomaly indicators from existing deterministic overlays.

---

### 3.5 `origin_timing`

Measures timing and origin-pattern anomalies currently available from existing runtime evidence (without new enrichment).

- **0:** No notable origin/timing anomaly.
- **1:** One moderate timing/origin inconsistency.
- **2:** Strong origin/timing inconsistency contributing to fraud likelihood.

Primary evidence sources (v1):
- temporal/date inconsistency signals already represented in current analysis evidence
- existing header-context anomalies that map to origin/timing concerns without requiring GeoIP/ASN.

Important boundary:
- Sender-provenance/geo-velocity remains separately gated behind cheaper proof; this axis must **not** imply that geo-velocity is implemented.

---

## §4 Consistency Contract with Internal 0-100 Score

The 5-axis rubric is explanatory and must not conflict with internal routing logic.

### 4.1 Band mapping

| Internal `risk_score` band | Expected `axis_total` band |
|---|---|
| 0–24 | 0–2 |
| 25–49 | 2–5 |
| 50–74 | 4–8 |
| 75–100 | 7–10 |

### 4.2 Contradiction guard

If computed `axis_total` falls outside expected band by more than 1 point, projection must:

1. Apply a deterministic guard adjustment toward the internal band floor.
2. Emit `rubric_consistency_override=true`.
3. Emit `rubric_consistency_reason` with bounded explanation for audit/reporting.

This prevents “internal says high risk, rubric looks mild” drift.

---

## §5 Data Contract Additions (analysis payload surface)

Locked additive block:

```python
class EmailRiskAxisBreakdown(StrictModel):
    axis_name: Literal[
        "sender_identity",
        "conversation_continuity",
        "vendor_payment_history",
        "document_integrity",
        "origin_timing",
    ]
    score: int = Field(ge=0, le=2)
    why_this_score: str = Field(min_length=1, max_length=160)
    evidence_tags: tuple[str, ...] = ()


class ClientFacingRubricPayload(StrictModel):
    rubric_version: Literal["v1"]
    rubric_status: Literal["available", "unavailable"] = "available"  # added §11.1 (D12 sentinel)
    axis_total: int = Field(ge=0, le=10)
    axes: tuple[EmailRiskAxisBreakdown, ...]  # exactly 5 when rubric_status == "available"
    rubric_consistency_override: bool = False
    rubric_consistency_reason: str | None = Field(default=None, max_length=220)
```

Integration shape: `EmailAnalysisPayload.client_facing_rubric: ClientFacingRubricPayload | None`

Boundary:
- Additive only; no mutation/removal of existing fields.

D12 unavailable sentinel shape (added §11.1 amendment 2026-05-25):

When rubric projection raises, the payload still emits with the following bounded shape so "projection crashed" is never indistinguishable from "rubric disabled":

- `rubric_status = "unavailable"`
- `axis_total = 0`
- `axes = ()` (empty tuple — no fabricated axis rows)
- `rubric_consistency_override = True`
- `rubric_consistency_reason` is required and bounded to 220 chars; must not leak exception detail beyond the exception class name.

The validator enforces all five conditions when `rubric_status == "unavailable"`. The five-axis / sum-equals-total / fixed-order invariants apply only when `rubric_status == "available"`.

---

## §6 Rendering Contract (MSP/client report lane)

For each analyzed email included in client reporting:

- Show `recommended_action` (`safe | needs_review | block`) as the most prominent element.
- When `rubric_status == "available"`:
  - Show `axis_total` (`/10`) as a navigation aid, not the headline.
  - Show each axis score (`/2`) and make the per-axis breakdown the primary reasoning surface.
  - Show one-line `why_this_score` per axis.
  - Include this exact disclaimer wherever the five-axis order is shown: "Order is fixed for stability, not priority."
  - If `rubric_consistency_override=true`, show the exact subtle marker:
    "Score normalized to match high-risk internal evidence."
- When `rubric_status == "unavailable"` (added §11.1 amendment 2026-05-25):
  - Show the exact line: "Rubric: unavailable - internal analysis emitted; client-facing axis projection unavailable."
  - Do not render axis rows, do not show `axis_total`, do not invent a substitute breakdown.

Disclaimer scope clarification (added §11.1 amendment 2026-05-25): the "Order is fixed for stability, not priority." line is required *with each rubric block* on a per-email basis when `rubric_status == "available"`. Reports that group multiple emails do not need a single global disclaimer; per-block placement is the canonical placement.

Do not render:
- raw header chains
- raw payment destination values
- raw account/routing identifiers
- unbounded model-generated text

---

## §7 Failure Modes + Guardrails

1. **Axis drift over time:** locked names + versioned schema.
2. **Contradiction with internal risk:** band mapping + override flag.
3. **Over-simplification risk:** axis-level explanations required, not just total.
4. **Client over-trusting total:** report must always show axis breakdown + recommended action.
5. **Detector expansion drift:** any new detector-to-axis mapping requires explicit spec addendum before release.

---

## §8 Gate Tests (implementation must pass before closure)

1. Exactly five axes emitted in fixed order with fixed names.
2. Each axis score constrained to `0..2`; total constrained to `0..10`.
3. Projection deterministic for same input payload.
4. Known high-risk fixture (`risk_score >= 75`) cannot emit low rubric (`axis_total <= 5`) unless override fires and is labeled.
5. Known benign fixture (`risk_score <= 20`, `recommended_action="safe"`) cannot emit high rubric (`axis_total >= 6`).
6. Ghost-thread fixture elevates `conversation_continuity`.
7. Banking-change fixture elevates `vendor_payment_history`.
8. Invoice-authenticity anomaly fixture elevates `document_integrity`.
9. Lookalike/header-divergence fixture elevates `sender_identity`.
10. Date/timing anomaly fixture elevates `origin_timing`.
11. No raw header/body/account/routing leakage into `why_this_score`.
12. Report renderer displays both rubric and internal `recommended_action`.
13. Tenant isolation test: no cross-tenant rubric evidence leak.
14. Kill-switch behavior unchanged for core scoring path (rubric must not bypass existing safeguards).

---

## §9 Rollout Sequence (spec-first discipline)

1. **Spec sign-off (§11):** lock D1–D17 and schema names.
2. **Implementation pass 1:** deterministic mapper + payload extension + unit tests.
3. **Implementation pass 2:** report rendering + fixture tests for explanation clarity.
4. **Audit pass:** pre-ship gate + optional independent code audit target if added.
5. **Activation:** feature-flag off by default until operator confirms report quality on a bounded fixture set.

---

## §10 Open Questions — Resolved 2026-05-25 by Stress Test

The five sub-questions originally drafted here were stress-tested on 2026-05-25 using the standard 7-axis rubric (`failure mode`, `hidden cost`, `specific buyer`, `cost of inaction`, `cheaper proof first`, `existing competitor`, `pre-mortem`). The full stress-test record lives in `think_sheet.md` under "Sub-question stress test — Client-facing 5-axis Email Scoring Rubric §10 (2026-05-25)."

Verdicts moved into §2 as locked decisions:

| Original §10 question | Locked verdict | §2 anchor |
|---|---|---|
| Q1. Equal axis weights vs weighted? | Equal weights for v1; weight revision deferred to v2 and gated on real per-axis FP/FN data. | D13 |
| Q2. Fixed axis order acceptable? | Fixed order for v1, with explicit "order is fixed for stability, not priority" line in rendering contract. | D14 |
| Q3. `why_this_score` max length? | 160 chars for v1; documented upgrade path to 220 if v1 production data shows ≥ 5% useful truncation. | D15 |
| Q4. Show `axis_total` to clients? | Yes, but `recommended_action` is the most prominent element and per-axis breakdown is the primary reasoning surface. The total is a navigation aid, not the headline. | D16 |
| Q5. v1 surface — report-only or also per-email? | Report-only / monthly digest in v1; per-email operator view deferred to v1.1, gated on MSP discovery feedback. | D17 |

§10 is now closed. No additional sub-questions remain blocking §11 signature.

---

## §11 Lockdown Signature

**Signed by:** _____Matt Nichol _______________  
**Date:** ________May, 25th. 2026____________  
**Decisions locked:** D1–D17 (D13–D17 added 2026-05-25 from sub-question stress test), §3 axis definitions, §4 consistency contract, §5 schema, §6 rendering contract, §7 failure-mode guardrails, §8 gate tests.

Signature is complete. Implementation still requires Matt's explicit start-build instruction and the normal pre-ship gate before commit.

---

## §11.1 Amendment — D12 Failure Sentinel + Rendering Scope (2026-05-25)

**Trigger:** Grok activation audit `client_facing_rubric_grok_audit_20260526T035658Z.md` returned `approve with notes` and identified that D12 ("On rubric-projection failure, do not fail-open: rubric marks `unavailable` with explicit audit marker.") had no schema-level sentinel field and no audit-marker contract. The follow-up audit `client_facing_rubric_grok_audit_20260526T040505Z.md` identified the resulting schema delta (the new `rubric_status` field) as a §5 contract divergence, and identified a §6 rendering-scope ambiguity around the disclaimer line.

**Contract delta locked here:**

- §5 — `ClientFacingRubricPayload` gains `rubric_status: Literal["available", "unavailable"] = "available"`.
- §5 — `axes` is exactly five rows iff `rubric_status == "available"`. When `rubric_status == "unavailable"`: `axes == ()`, `axis_total == 0`, `rubric_consistency_override == True`, and `rubric_consistency_reason` is required (≤ 220 chars, must not leak exception detail beyond the exception class name).
- §6 — Adds the exact unavailable render line and forbids fabricated axis rows when unavailable.
- §6 — Clarifies disclaimer scope: per-block placement is canonical; no global disclaimer is required.
- §7 — Implicit add: D12 audit-marker emission is a production-cycle contract, not just a mapper concern. The `EMAIL_ANALYSIS_COMPLETE` audit marker findings list must include one of `client_facing_rubric=available`, `client_facing_rubric=disabled`, or `client_facing_rubric=unavailable; projection_failed=true`. This was not previously written down.

**Decisions added:**

- D18 — Failure sentinel field name and shape are `rubric_status`-driven, not a separate top-level optional. Rationale: keeps the contract single-payload and avoids two parallel "rubric is/isn't here" paths.
- D19 — Audit marker findings must surface rubric availability state on every analyzed email when the flag is enabled. Operators reading the marker stream can distinguish "disabled by config" from "projection crashed at runtime."

**Backward compatibility:** existing `available` payloads pre-amendment validate identically (default value preserves old shape). No data migration required.

**Re-signed by:** _____Matt Nichol _______________  
**Re-signed date:** ________May, 25th. 2026____________  
**Decisions locked by amendment:** D18, D19, plus the §5 / §6 / §7 deltas above.

