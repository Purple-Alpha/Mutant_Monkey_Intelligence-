# Callback Phishing / TOAD Body-Language Detector — Deep Dive (Part 1)

**Status:** DRAFT (pre-§11). §10 sub-questions still open and require the standard 7-axis stress-test discipline before signature.

**Scope reminder:** This document specifies **Part 1 only** — body-language detection. Part 2 (phone-number baselining via a `phone_number` closed-enum entry on Vendor Baseline Store) is explicitly **out of scope** for this spec. Part 2 is gated on a separate Vendor Baseline Store enum revision per `4. Product_Roadmap/Vendor_Baseline_Signal_Type_Enum_Revision_Deep_Dive.md`. Part 1 ships independently as a pure-function deterministic detector, the same shape as `header_divergence_detector` and `prompt_injection_detector`.

**Selected by:** Build queue framework rule on 2026-05-25. The build queue ordering in `PROJECT_HANDSHAKE.md` names B-tier as `Callback Phishing / TOAD body-language detector, Micro-Temporal Mismatches, Client-facing 5-axis Email Scoring Rubric`. Of the remaining two B items after the rubric shipped, Callback Phishing scores 10/10 vs Micro-Temporal 8/10 in `think_sheet.md`, and its stress test (`ST=Y`) explicitly says "body-language detection ships independently."

---

## §1 Purpose + Scope

### Purpose

Detect inbound emails that try to move a financial fraud off the email channel and onto the phone — telling the recipient to call a number provided in the email — so NorthStar's existing Stage A controls (Inbox Shield scoring, Two-Channel Confirmation enforcement, daily digest, Decision Auditor) can lift risk and surface the mandatory out-of-band verification step *before* the recipient picks up the phone.

This is the body-language slice of the broader TOAD (Telephone-Oriented Attack Delivery) attack family. It does not attempt phone-number identity decisions — those depend on Part 2 phone-number baselining, which is gated on a Vendor Baseline Store enum revision.

### In scope (v1, Part 1)

- Pure deterministic function over `EmailInboundPayload.body_plain` (and a deferred-decision `body_html` path — see §10 Q4).
- Closed phrase-category vocabulary scored by a deterministic rule set.
- Optional max-merge of an additive `callback_phishing_assessment` overlay onto `EmailAnalysisRiskAnalysis`.
- Feature flag default OFF (matches §9-step-5 activation discipline locked across prior detectors).
- Mandatory out-of-band verification wording emitted in evidence text when the detector fires, mirroring the Financial State Ledger / Two-Channel Confirmation contract.

### Out of scope (v1)

- Phone-number extraction, normalisation, baselining, or storage of any kind. (Reserved for Part 2 + Vendor Baseline Store enum revision.)
- Phone-number reputation / VoIP lookups, paid carrier APIs, or any external network call.
- LLM-driven body-language classification. v1 is rule-based for auditability and deterministic re-projection through the 5-axis rubric (`origin_timing` axis).
- Voicemail / call-recording integration, IVR handling, or any non-email surface.
- Portal-based confirmation surface (deferred to NorthStar Portal moonshot per `think_sheet.md`).

### Boundary

- Additive only on `EmailAnalysisPayload`. No mutation of existing fields.
- No new network calls, no external enrichment, no new infrastructure surface.
- Tenant-isolation: the detector reads only the email payload it is given. No cross-tenant state, no global mutable state, no `production_state/` reads or writes.
- D1: this is **not** a second detector stack. It is one additional deterministic overlay alongside the existing seven Stage A detectors.
- Kill switch + lift-only invariant: detector cannot decrease an existing `risk_score`, cannot soften a `recommended_action`, cannot bypass forced escalation, cannot suppress an existing finding from another detector.

---

## §2 Locked Decisions (D1–D...)

| # | Decision | Note |
|---|----------|------|
| D1 | Pure-function detector, not a second stack | Mirrors `header_divergence_detector.py` + `prompt_injection_detector.py` shape. Lifts existing `recommended_risk_floor`; never introduces a parallel scoring path. |
| D2 | Closed phrase-category vocabulary in v1 | Adds `callback_phishing_pattern` to `BehavioralDeviationFlag` Literal. Sub-categories live inside the detector, not on the schema, to keep the public contract small. (Adding new sub-categories is a v1.1 change requiring a spec addendum.) |
| D3 | Body-language only | No phone-number extraction, no phone-number storage, no phone-number reputation. Part 2 spec lives separately and is gated on Vendor Baseline Store enum revision. |
| D4 | Read `body_plain` only | Standard project convention; matches existing detector inputs. (See §10 Q4 — `body_html` decision deferred to stress-test outcome.) |
| D5 | Lift-only invariant | Detector can raise `recommended_risk_floor` and add `behavioral_deviation_flags` and `callback_phishing_assessment` overlay. It cannot lower any score, soften any action, or remove any flag. |
| D6 | Default OFF activation | New `EmailRiskScoringConfig.enable_callback_phishing_detection: bool = False`. Matches the §9-step-5 activation discipline used for ransomware precursor overlay and client-facing rubric. |
| D7 | No PII / no raw phone numbers in evidence text | Phrase categories may name themselves (e.g. `"call_now_pressure_phrase_detected"`) but evidence strings must not echo the raw email body, raw phone-number digits, or the raw lure text back to client surfaces. Same posture as D7 on the rubric spec. |
| D8 | Mandatory out-of-band verification wording on hit | When the detector fires, the analysis evidence (and any downstream rendered surface) must include the existing project-standard wording: "verify through a previously-known channel, not via the number in this email." This is the shared contract with Financial State Ledger and Two-Channel Confirmation Enforcement. |
| D9 | Tenant isolation by construction | Detector takes `EmailInboundPayload` as input and returns a frozen result object. No global state, no `production_state/` reads, no per-tenant configuration beyond the existing `enable_callback_phishing_detection` flag. |
| D10 | Forward-compatible schema for Part 2 | The v1 schema reserves a `phone_number_assessment: PhoneNumberAssessment | None = None` field on the `CallbackPhishingAssessment` overlay so Part 2 can fill it without bumping the assessment shape. v1 always emits `phone_number_assessment = None`. (See §10 Q5.) |

Additional D-decisions live in §10 sub-questions; they will be locked here when the stress test resolves them.

---

## §3 Detector Definition

### Phrase categories detected (closed list, v1)

The detector searches `body_plain` for membership in a fixed set of phrase categories. Each category is a small set of pattern variants. Categories were chosen from the stress-test answer (think_sheet 2026-05-24 Callback Phishing entry) and from the public callback-phishing literature; they are **NOT** a learned model, and **NOT** an open list. Adding or removing a category is a v1.1 spec change.

| Category | Intent | Example phrase shapes (illustrative — exact patterns live in code, not in this spec) |
|---|---|---|
| `call_now_pressure` | Urgency + phone | "call us immediately", "call within 24 hours to avoid", "do not delay — call now" |
| `do_not_use_known_channel` | Misdirection away from baselines | "do not use the number on file", "ignore previous contact info", "the old number is no longer valid" |
| `voice_only_finalize` | Forces resolution off email | "we cannot complete this over email", "call to confirm — email won't be checked", "the rest of this needs to happen by phone" |
| `support_line_substitution` | Substitute attacker number for a brand support line | "call our updated support line", "reach our new fraud-prevention desk at" |
| `payment_redirect_call` | Combines callback with a financial change | "call to confirm the new ACH instructions", "phone us to authorise the rerouted wire" |

### Score / flag emission contract

A deterministic rule set maps the set of categories that fire to:

- `behavioral_deviation_flags`: append `callback_phishing_pattern` once when **any** category fires.
- `recommended_risk_floor`: lift to a category-driven floor — see §4.1 below.
- `callback_phishing_assessment`: emit the dedicated overlay (see §5).

If no category fires, the detector emits no flag, no overlay, and does not lift any floor (D5 lift-only invariant).

---

## §4 Consistency / Boundary Contract

### §4.1 Risk-floor lift band table

```
fired categories                      → recommended_risk_floor lift
----------------------------------------------------------------
1 category, no payment overlap         → 50  (needs_review band)
1 category overlapping payment_redirect_call
   OR ≥2 categories                    → 70  (block-eligible band)
≥3 categories OR payment_redirect_call
   plus do_not_use_known_channel       → 85  (matches FSL hit floor)
```

`recommended_risk_floor` lifts use the same max-merge semantics as `header_divergence_detector` and Financial State Ledger: the final value is `max(current_floor, lift_value)`. The detector can never decrease a floor.

### §4.2 Interaction with existing detectors

- If `recommended_action` is already `block` from another detector or from a forced-escalation trigger, the detector adds its overlay and flag but does not override.
- If the email is already flagged `mismatched_invoice_vendor_name` or `new_banking_instructions` from FSL, a `payment_redirect_call` category hit is treated as corroborating evidence and bumps the floor to 85 even on a single-category fire.
- The `client_facing_rubric.origin_timing` axis is the natural rendering surface — see §6.

### §4.3 Forward compatibility with Part 2

When Part 2 phone-number baselining ships:

- Part 2 fills `CallbackPhishingAssessment.phone_number_assessment` with a `PhoneNumberAssessment` payload.
- v1 leaves that field at `None`.
- v1 never inspects, extracts, normalises, or hashes any phone-number-shaped substring.

---

## §5 Schema

Locked additive block (final form — exact field names reviewed at §11 sign):

```python
class CallbackPhishingCategory(StrictModel):
    category_name: Literal[
        "call_now_pressure",
        "do_not_use_known_channel",
        "voice_only_finalize",
        "support_line_substitution",
        "payment_redirect_call",
    ]
    why_this_category: str = Field(min_length=1, max_length=160)


class CallbackPhishingAssessment(StrictModel):
    detector_version: Literal["v1"] = "v1"
    fired: bool
    categories: tuple[CallbackPhishingCategory, ...]
    recommended_risk_floor_lift: int = Field(ge=0, le=100)
    out_of_band_verification_required: bool
    phone_number_assessment: None = None  # reserved for Part 2; v1 always None
```

Integration shape on `EmailAnalysisPayload`:

```python
callback_phishing_assessment: CallbackPhishingAssessment | None = None
```

Schema invariants (validator-enforced):

- When `fired == False`, `categories == ()`, `recommended_risk_floor_lift == 0`, and `out_of_band_verification_required == False`.
- When `fired == True`, `len(categories) >= 1` and `recommended_risk_floor_lift >= 50` (matches §4.1 minimum).
- `out_of_band_verification_required` follows D8 — true whenever `fired == True`.
- `phone_number_assessment` is `None` for v1 (§4.3 forward compat) and the validator rejects any non-`None` value until Part 2 lands.

`BehavioralDeviationFlag` Literal gains `"callback_phishing_pattern"` as one new entry.

Boundary: additive only; no mutation/removal of existing fields. Backward compat: existing payloads pre-v1 validate identically (default value preserves the old shape).

---

## §6 Rendering Contract

For each analyzed email included in client reporting:

- When the detector fires, the surface that already shows `recommended_action` adds the bounded line: "Phone-based escalation pattern detected — verify through a previously-known channel, not via the number in this email."
- Show `categories` by their `category_name` only — do not surface the raw phrase from the email body (D7 PII / lure-text safety).
- The `client_facing_rubric.origin_timing` axis is the natural projection. The deterministic rubric mapper (`core/scoring/client_facing_rubric.py`) gains a single new evidence-tag mapping: presence of `callback_phishing_pattern` in `behavioral_deviation_flags` lifts `origin_timing` to score 1 even without out-of-band-pressure, and to score 2 when paired with elevated `risk_score >= 50`. (This is a §11.1 amendment to the rubric spec when this detector signs — see §10 Q3.)
- The `recommended_action` element remains the most prominent surface element (matches D16 of the rubric spec).

Do not render:

- raw phone-number digits
- raw lure-phrase text from the email body
- header chains, account numbers, or routing identifiers (unchanged from the rubric §6 contract)
- unbounded model-generated text — there is no LLM in this detector

---

## §7 Failure Modes + Guardrails

1. **False positive on legitimate "call our published billing line" emails:** mitigated by D2 closed-vocabulary discipline. The phrase categories were chosen specifically to require *misdirection* (`do_not_use_known_channel`), *urgency* (`call_now_pressure`), or *off-channel coercion* (`voice_only_finalize`), which legitimate vendor mail rarely needs. A simple "please call our billing line at xxx-xxxx" without those framings does not fire the detector.
2. **False negative on novel phrasing:** mitigated by accepting that v1 catches a known-shape signal and is not a learned model. New phrasings are surfaced through real-traffic review and become v1.1 spec additions, not silent code patches.
3. **Body-language alone too noisy:** mitigated by §4.1's banding — single-category fire only lifts to 50 (`needs_review`), not to `block`. Block-tier requires multi-category corroboration or payment-overlap.
4. **Lure-text leakage into client-facing surface:** mitigated by D7 + §6 rendering boundary. Evidence may name the *category* but never the raw phrase or raw phone digits.
5. **Drift via phrase-list creep:** mitigated by D2 closed-vocabulary lock. Adding categories is a spec change, not a code change.
6. **Cross-tenant leak:** mitigated by D9 construction discipline. Detector takes a single email payload and returns a frozen result; no global state, no cross-tenant reads.
7. **Activation-by-accident:** mitigated by D6 default-OFF flag with the exact same activation discipline as the rubric and ransomware precursor overlay. Production loop rebuild path must explicitly preserve the flag (lesson learned from the rubric Activation Pass).

---

## §8 Gate Tests (implementation must pass before closure)

1. Detector returns `fired=False` and emits no flag / no overlay / no floor lift on benign mail (control fixture).
2. Detector returns `fired=True` with exactly one category on a single-category fixture; floor lift `== 50`; flag added; overlay attached; out-of-band wording emitted.
3. Detector returns `fired=True` with `>=2` categories on a multi-category fixture; floor lift `== 70`; same emission contract.
4. Detector returns `fired=True` with payment-overlap (`payment_redirect_call` + `do_not_use_known_channel`) on a corroborated fixture; floor lift `== 85`; same emission contract.
5. Detector is deterministic for the same input payload (same fixture run twice yields equal `CallbackPhishingAssessment`).
6. Detector does not mutate the input `EmailInboundPayload` (snapshot before == snapshot after).
7. Detector has no global state and no per-tenant configuration leak (cross-tenant fixture: two tenants run on the same blackboard root, each with the flag enabled, neither tenant's analysis records reference the other tenant's evidence; mirrors the §8.13 rubric isolation gate test pattern).
8. Lift-only invariant: when `risk_score` already equals 95 from an upstream detector, the detector adds its overlay and flag but does not lower `risk_score`. When `recommended_action` is already `block`, the detector does not soften it.
9. D7 PII safety: assertion on `why_this_category` strings — no `@`-symbols, no raw digit sequences ≥7 chars, no raw `Received:` header content, no echoed email-body substrings of length > 60 chars.
10. D8 wording: when `fired == True`, the rendered surface (via `daily_digest_agent` prompt + deterministic demo renderer) emits the exact phrase "verify through a previously-known channel, not via the number in this email."
11. Rubric integration: when `callback_phishing_pattern` flag is present, `client_facing_rubric.origin_timing` axis score is `>=1` (and `==2` when `risk_score >= 50`), confirming the rubric §11.1 amendment landing.
12. Forward-compat: `phone_number_assessment` validator rejects any non-`None` value at this stage (Part 2 readiness without Part 2 enabling).
13. Activation discipline: with `enable_callback_phishing_detection=False` (default), the detector never runs, no overlay attaches, no flag lifts, no floor changes — even on a fixture that would otherwise fire.
14. Production-loop rebuild preserves the flag: the same regression covered for the rubric's `enable_client_facing_rubric` (see `test_production_loop_preserves_client_facing_rubric_flag_through_rebuild`) is reproduced for `enable_callback_phishing_detection`.

---

## §9 Rollout Sequence (spec-first discipline)

1. **§10 sub-question stress test** — apply the project's standard 7-axis test (failure mode, hidden cost, specific buyer, cost of inaction, cheaper proof first, existing competitor, pre-mortem) to each open §10 sub-question, record verdicts in `think_sheet.md`, lock verdicts back into §2 of this spec as new D-decisions, then convert §10 to "Resolved."
2. **§11 lockdown signature** by Matt Nichol once §10 is resolved.
3. **Implementation pass 1** — pure-function detector + schema additions + unit tests (gates §8.1–§8.9, §8.12).
4. **Implementation pass 2** — scoring-agent wiring + activation flag + rendering integration + rubric §11.1 amendment for the `origin_timing` mapping + integration tests (gates §8.10, §8.11, §8.13).
5. **Independent Grok audit** — run `python audit_tools/grok_audit_runner.py callback_phishing_toad` (audit package added with the spec, implementation files, and tests).
6. **Pre-ship audit** — `python audit_tools/pre_ship_audit.py`.
7. **Activation** — feature flag default OFF until operator confirms behaviour on a bounded fixture set (matches §9-step-5 activation discipline used for the rubric and prior detectors).

---

## §10 Open Questions — Stress Test Required Before §11 Signature

The following sub-questions have not been answered and are blocking signature. Each goes through the standard 7-axis test in `think_sheet.md` before its verdict is locked into §2 as a new D-decision.

| Q | Question | Why it matters |
|---|----------|----------------|
| Q1 | What is the closed list of phrase categories for v1? Is the §3 list final, or does the stress test add `mfa_bypass_call` or remove `support_line_substitution`? | The category list is the public contract. Adding categories later is a v1.1 spec addendum, not a code change, so the v1 list must be defensible at signature. |
| Q2 | Should the score emit shape be a flag-only signal or carry a numeric `callback_phishing_score` field? | Other detectors (FSL, document-metadata) carry a numeric score. Callback phishing's signal is closer to binary-with-tiers. The §4.1 banding could live entirely in `recommended_risk_floor_lift` (current draft) or also in a numeric `callback_phishing_score` for symmetry with sibling detectors. |
| Q3 | What is the rubric `origin_timing` mapping when the detector fires — should it lift to 1 only, or 1/2 with the §4.1 banding? | This decides whether this spec's signature triggers a §11.1 amendment to the rubric spec or not. |
| Q4 | Should the detector read `body_html` in addition to `body_plain`? | `body_html` is richer (stylised "Call now!" buttons), but most existing detectors stay on `body_plain` to avoid HTML-parsing complexity. Decision affects implementation surface and gate-test fixture set. |
| Q5 | Should v1 schema reserve `phone_number_assessment` as a typed forward-compat slot (current draft) or omit it entirely until Part 2 ships? | Reserving the field locks the v1 contract in a way that constrains Part 2's design. Omitting requires a Part 2 schema migration. Trade-off is locked at signature time. |

§10 stays "Open" until each row has a recorded verdict in `think_sheet.md` and the corresponding D-decision is added to §2.

---

## §11 Lockdown Signature

**Status:** UNSIGNED. Pending §10 stress-test resolution.

**Signed by:** ______________________  
**Date:** ______________________  
**Decisions locked at signature:** D1–D10 plus the verdicts moved in from §10.

Signature is incomplete. Implementation does **not** begin until Matt's explicit start-build instruction after signature, and pre-ship gate must complete before commit.
