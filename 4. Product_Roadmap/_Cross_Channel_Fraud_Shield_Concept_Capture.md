# Cross-Channel Fraud Shield — Spark Capture

**Status:** SPARK ONLY. Pre-spec. Unsigned. Not §11. Not a roadmap commitment. Not a product.
**Captured:** 2026-05-30 evening PT (immediately after committing the TOAD §10 resolution at `6c4b28f`).
**Architect:** Matt. The structure, scope, and direction of any future spec are Matt's to design.
**Purpose:** Preserve the kernel of a bigger "email-to-phone fraud handoff" idea that surfaced in a separate proposal block alongside (and unrelated to) the TOAD §10 commit. Do not begin construction without Matt's lead. Do not promote any of it to a signed document.

---

## What this SPARK is preserving

A three-stage framing for **email-to-phone fraud handoff protection**, kept deliberately stage-gated so each stage either lives inside an existing NorthStar lane or sits behind an explicit gate:

- **Stage A — Email side (already exists in spec).** The Callback Phishing / TOAD detector v1 (`4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md`, pre-§11, locked decisions D1–D9 + D11–D15) detects phone-pressure language in `body_plain` email. Five closed phrase categories. Lift-only. Default-OFF. Mandatory out-of-band-verification wording on hit. This is **already the project's posture** — Stage A is named in this SPARK only so the cross-channel framing is honest about where it starts.
- **Stage B — Known-channel phone baseline (deferred; gated on existing pending spec).** Per-tenant baseline of *known-legitimate* phone numbers a tenant's vendors use, similar in shape to the Vendor Baseline Store's existing per-tenant routing / SWIFT / IBAN baselines. Gated on the existing pending-signature `4. Product_Roadmap/Vendor_Baseline_Signal_Type_Enum_Revision_Deep_Dive.md` (which already proposes a `vendor_callback_phone_number` enum entry). Stage B does **not** add a new live-call surface; it adds a new closed-enum baseline that the existing detector chain can consult. No phone-system integration, no real-time call surface, no third-party reputation API.
- **Stage C — Phone-system integration of any kind (parked behind legal review).** Anything that listens to, transcribes, records, blocks, or reroutes a live phone call. Includes SIP-gateway hooks, real-time speech-to-text, voicemail transcription, IVR routing, and any third-party telephony API. **Not work, not a product, not a spec.** Cannot be started without a written legal / consent review covering Canadian PIPEDA, US two-party-consent states, UK / EU GDPR Art. 6 + Art. 9, and sectoral overlays for any vertical it might be pitched to. Until that review exists, Stage C is a no-touch.

---

## What this SPARK is NOT

- Not a product. Not a brand. Not a sub-entity of NorthStar Security.
- Not a revenue plan. No pricing, no per-user / per-minute / per-channel rate, no customer-segment matrix is captured here. Pricing belongs in `REVENUE_MAP.md` or `THIRTY_DAY_PLAN.md` and only after a real proof exists.
- Not a §11-signed spec, and not even a draft of one. Drafting begins only if a trigger condition below fires AND Matt leads.
- Not authorization to record, transcribe, scan, or otherwise interact with live phone audio. Stage C is parked; do not draft Stage C content here.
- Not a re-statement of the TOAD detector. The TOAD spec (`4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md`) is the only authority on what Stage A does.
- Not a re-statement of the Vendor Baseline Store. The Vendor Baseline Signal Type Enum Revision spec is the only authority on what closed-enum baseline shapes the project will admit.

---

## Failure modes this SPARK is parking

These are recorded so the next time this idea surfaces, the discussion does not need to re-discover them:

- **Wiretap / consent risk on Stage C.** Real-time call audio capture is governed by jurisdiction-specific consent law (Canadian PIPEDA single-party-consent baseline, US federal one-party-consent with two-party-consent state overlays — CA, FL, IL, MD, MA, MT, NH, PA, WA, plus partial states — UK Investigatory Powers Act 2016, EU GDPR Art. 6 lawful-basis + Art. 9 special-category data when conversations touch financial / health detail). No NorthStar artifact may imply Stage C is in scope, pilotable, or deliverable without that legal review.
- **Forbidden-language slip.** Any client-facing artifact that positions a cross-channel offering for "banks," "insurance," or "call centers / BPOs" engages `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` and the AGENTS.md §8 forbidden-language list. Do not use those buyer labels in NorthStar voice without re-reading that process file.
- **Identity drift.** The project is **NorthStar Security**. Spinning up a new sub-brand (e.g. a separate "Telefraud" entity, a "Core / LiveGuard" two-tier product) is an operator-level brand decision, not a SPARK entry. Any such sub-brand requires its own decision lane (Decision Auditor packet + `4. Product_Roadmap/Consequence_Matrix_Process.md` trigger check + explicit operator sign-off) before it appears in any project document.
- **Decision laundering.** A rubric or revenue matrix later "concluding" that Stage C is worth building does not authorize Stage C. Rubrics rank; humans decide; legal review is a hard gate. AGENTS.md §11 "authority drift" / "decision laundering" name this failure mode explicitly.
- **Free-work perception.** If Stage B or Stage C is ever pitched to MSPs / clients without an explicit pricing and scope envelope, NorthStar gets committed to ongoing work without compensation. AGENTS.md §11 "free-work perception" names this.
- **Scope creep into the TOAD spec.** The TOAD detector (commit `6c4b28f`, D1–D9 + D11–D15 locked) is an email-only, `body_plain`-only, no-`phone_number_assessment` detector. This SPARK does not modify that spec. Any future cross-channel work that wants to add phone-side surfaces must do so through its own additive spec, not through edits to the signed-pending TOAD spec.
- **Sycophancy and praise-stacking.** External proposals that frame the existing TOAD decisions as "incredible business foresight" or otherwise reverse-engineer commercial intent from spec-discipline decisions misrepresent what was locked. D11–D15 are scope-discipline decisions for an email detector. They are not commercial design.

---

## Trigger conditions for un-deferring

This SPARK stays parked unless **at least one** of the following is true:

1. **Stage B (phone-number baseline) becomes the natural next move.** The Vendor Baseline Signal Type Enum Revision spec gets §11-signed AND a real MSP discovery conversation surfaces a concrete miss where a known-vendor-callback-phone-number baseline would have caught a redirected fraud attempt the TOAD email detector did not catch. At that point Stage B becomes a candidate for its own pre-§11 deep-dive draft inside the existing baseline-store lane.
2. **Cheaper-proof first for Stage B.** A real-traffic miss-set (at least three observed cases, post-TOAD-implementation) shows that body-language alone catches the attempt but not the substituted phone number. This is the "cheaper proof first" axis of the standard 7-axis stress test.
3. **A signed §11 spec needs a Stage B hook.** For example, the Financial State Ledger / Delta Tripwire (`Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md`, §11-SIGNED) might benefit from a `vendor_callback_phone_number` cross-check. If so, that integration becomes the trigger — not this SPARK.
4. **Operator decision to revisit.** Matt explicitly opens this file and asks for either a Stage B draft, a Stage C legal-research note, or a structured cross-channel discussion. Until that explicit ask, the SPARK is read-only.

Stage C **never auto-triggers**. Stage C requires a separate, named operator decision after legal review. No combination of Stage A signal volume, Stage B baseline adoption, or buyer demand auto-promotes Stage C.

---

## What this SPARK deliberately does NOT include

(Mirroring the `_SPARK_Bibles_Concept_Capture.md` pattern.)

- No product name. No "Core / LiveGuard / SIP-gateway / real-time scanner / streaming NLP audio engine" labels.
- No new entity name. "Northstar Telefraud Solutions" was a proposed sub-brand that has no operator sign-off; it is not recorded here as a candidate.
- No revenue matrix. No customer-segment table. No per-user / per-channel / per-minute pricing.
- No proposed Stage B schema. No proposed Stage C technical design.
- No legal opinion. The wiretap / consent overview above lists the surface law; it is not legal advice and does not substitute for a real legal review.

These are operator-level decisions and should not be pre-populated.

---

## Why this file exists at all

A separate proposal block in chat tried to bundle the TOAD §10 commit, a new sub-brand, a hypothetical real-time call-audio scanner, a multi-tier revenue matrix, and a re-narration of D11–D15 as commercial foresight — all into a single "let's add this to think_sheet" ask. The disciplined response per AGENTS.md §3 (challenge when warranted) and §11 (named failure modes: authority drift, decision laundering, sycophancy, forbidden-language slip, free-work perception) was to refuse the bundling, hold the TOAD commit clean, and offer to preserve only the salvageable kernel — the cross-channel framing itself — in a clearly-marked SPARK file like this one.

This file is the holding pattern. Nothing more, nothing less.

---

## Cross-references (raw material, not endorsements)

- `4. Product_Roadmap/Callback_Phishing_TOAD_Detector_Deep_Dive.md` — Stage A authority; pre-§11, D1–D9 + D11–D15 locked, §11 still pending.
- `4. Product_Roadmap/Vendor_Baseline_Signal_Type_Enum_Revision_Deep_Dive.md` — pending-signature spec that already proposes the `vendor_callback_phone_number` closed-enum entry Stage B would consume.
- `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md` — §11-SIGNED 2026-05-23; the existing per-tenant, hash-only, TTL-bounded baseline primitive any Stage B work would build on.
- `4. Product_Roadmap/Financial_State_Ledger_Delta_Tripwire_Deep_Dive.md` — §11-SIGNED 2026-05-24; the closest existing detector that integrates Vendor Baseline Store signals and might surface a real Stage B trigger.
- `4. Product_Roadmap/Compliance_and_Trend_Watch_Process.md` — forbidden-language carve-outs; required reading before any client-facing positioning of any future stage.
- `4. Product_Roadmap/Consequence_Matrix_Process.md` — operator-triggered process for path-setting decisions; the right tool to run before any decision to start a Stage B or Stage C spec.
- `4. Product_Roadmap/_SPARK_Bibles_Concept_Capture.md` — the precedent for "park a big idea without pretending it is a product."
- `AGENTS.md` — §3 tone (no sycophancy, challenge when warranted), §4 no proxy decisions, §11 named failure modes (authority drift, decision laundering, free-work perception, forbidden-language slip).

---

## Tomorrow's actual first move (Matt's call to accept or reject)

The tomorrow path remains whatever is at the top of `PROJECT_HANDSHAKE.md` / `PROGRESS.md` / the build queue. This SPARK does not move the queue. It only ensures the cross-channel framing survives long enough to be re-examined when (and if) a real trigger fires.
