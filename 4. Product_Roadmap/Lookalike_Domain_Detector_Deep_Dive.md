# Lookalike Domain Detector — Spec-First Deep Dive

**Status:** §11 SIGNED 2026-06-05 by Matt Nichol. First agent promoted from the operator-adopted `agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md` (swarm agent #10, "Lookalike Domain Agent"), team 2 (email identity / sender analysis). §10 resolved into §10.A operator-confirmed decisions; D1-D9 locked as the detector contract. Signing authorizes a future build slice but **no code begins** until a separate explicit operator "start build" instruction; signing does not wire the detector default-on or change the signed Client-Facing 5-Axis Rubric.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey**. No rename implied.

**Source-of-truth links:**
- `agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md` (swarm map; this is agent #10)
- `core/precursor/url_obfuscation_detector.py` (existing punycode/homoglyph machinery for **body URLs** — reused here, see D4/D5)
- `core/scoring/header_divergence_detector.py` and `core/scoring/email_authentication_detector.py` (existing **header/auth** divergence — bounded against in §1)
- `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md` (per-tenant known-good source; privacy/isolation posture inherited)
- `4. Product_Roadmap/Tiered_Detection_Intensity_Deep_Dive.md` (lift-only invariant)
- `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` (`sender_identity` axis — consumer of this signal; §10 Q7)
- `VISION.md` (Stage A = analyze + recommend only; the seven non-negotiables)

---

## Agent Design Contract Wrapper (metadata-only retrofit)

**Retrofit boundary:** This wrapper is additive governance metadata only, applied under `Agent_Design_Contract_Template_Deep_Dive.md` §7. It does **not** edit, reinterpret, relax, or extend the signed detector contract below. D1-D9, §10.A, scoring bands/floors, default-off posture, input surface, data-minimization rules, rubric linkage, Build Authorization status, and §11 remain unchanged.

| Field | Value |
|---|---|
| Agent name | Lookalike Domain Detector |
| Swarm inventory ID | #10 — Lookalike Domain Agent (v1 map inventory/backlog reference only) |
| Canonical layer | Detection |
| Canonical team / case type | Email identity / sender analysis; trusted-domain impersonation |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | Stage A analyze/recommend only |
| Role | Produce deterministic domain-impersonation evidence by comparing message identity domains against the tenant's known-good domain set. |
| Boundary | The detector is not the decision. It must not decide fraud, approve/deny mail, block/quarantine, change payment behavior, or alter the signed Client-Facing 5-Axis Email Scoring Rubric. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no DNS/WHOIS/network lookup; no buyer-facing claim; no default-on enablement without the signed calibration record required by §10.A Q5. |
| Inputs | Header `From` and `Reply-To` identity domains, tenant known-good domain set, and `tenant_id`, exactly as locked in D9 / §10.A Q6. |
| Outputs | `LookalikeDomainAssessment`-style internal assessment: `lookalike_domain_score`, ordered findings, and max-merge `recommended_risk_floor_lift` evidence. |
| Evidence emitted | Observed identity-domain relationship, matched technique, bounded domain evidence, matched known-good reference per D8 / §10.A, and whether the result supports a `sender_identity` evidence tag only. |
| Data minimization | No mailbox body content, no raw secret/value leakage, and no cross-tenant known-good leakage; inherits Vendor Baseline Store isolation/privacy posture. |
| Tenant isolation | Per-tenant known-good source only; tenant A's known-good domains must never influence tenant B. |
| Two-pass role | Pass 1 detection only until the Two-Pass Decision Model spec is signed; provides evidence a future Pass 2 challenge can inspect. |
| Decision Evidence Record contribution | `observed_facts`: identity domains + known-good comparison result; `interpretations`: look-alike technique classification; `assumptions`: tenant known-good set is current; `missing_evidence`: absent/stale known-good data or calibration gaps; `recommended_verification`: known-good channel review for high-risk sender-identity anomalies; `final_outcome_contribution`: sender-identity evidence tag / risk-floor input only; `retest_or_learning_record`: false-positive/false-negative correction evidence after calibration failures. |
| Human review trigger | Strong or probable look-alike evidence on payment, credential, or executive-authority context should route to human review through existing Stage A review vocabulary. |
| Verification trigger | Any look-alike evidence tied to money movement, credential requests, vendor changes, or executive authority should trigger known-good out-of-band verification before action. |
| Scoring / action posture | Max-merge floor lift only, non-additive; strong look-alike findings may feed `sender_identity` as evidence attribution only; no rubric point-structure change in this retrofit. |
| Default rollout | Default-off / opt-in until a signed calibration record exists. |
| Autonomous action | None. |
| Promotion conditions | Signed calibration record showing acceptable false-positive behavior, adversarial coverage, benign near-neighbor coverage, cross-tenant isolation, no raw-value leakage, deterministic results, and useful evidence output. |
| Demotion conditions | Overclaims beyond evidence, false positives above accepted calibration boundary, missed serious look-alike cases, cross-tenant leakage, raw-value leakage, unsupported recommendations, autonomous-action wording, or failed retests. |
| Retest evidence | Updated synthetic/adversarial/benign cases plus regression proof after any correction. |
| Calibration requirement | The signed calibration record required by §10.A Q5 before default-on or increased influence. |
| Failure modes | Inherits §4 named failure modes: new-vendor false positive, regional-brand false positive, homoglyph false negative, combosquat over-firing, cross-tenant leakage, input DoS, and authority drift. |
| Required tests | Inherits §5 test requirements: unit, break-it, no-network, no-block-verb, no raw-value leak, default-off no-regression, crash resistance, cross-tenant isolation, and determinism. |
| Audit requirements | Any implementation or future retrofit/revision remains subject to `complete_gate.py`; this wrapper itself is gated as metadata-only. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `Vendor_Baseline_Store_Deep_Dive.md`, `Tiered_Detection_Intensity_Deep_Dive.md`, `Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`, `VISION.md`, and `Compliance_and_Trend_Watch_Process.md`. |
| Build Authorization dependency | The existing implementation remains governed by the signed detector spec and prior build authorization; this wrapper authorizes no new code, no default-on, no rubric change, no buyer-facing claim, and no runtime behavior change. |

---

## §0 Purpose

Catch the case where an email's **sending identity domain** is a deliberate look-alike of a domain the tenant already trusts — a typosquat, homoglyph, combosquat, TLD-swap, or subdomain-spoof of a known-good vendor/brand domain — even when SPF/DKIM/DMARC pass for the look-alike domain itself (the attacker owns it and authenticates it correctly).

The existing detectors do not cover this:
- `url_obfuscation_detector.py` scores **URLs inside the body**, not the sender's own domain.
- `header_divergence_detector` / `email_authentication_detector` score **authentication and routing divergence**, which a properly-configured attacker-owned look-alike domain passes cleanly.

This detector closes that gap: it compares the message's **identity domains** against the tenant's **known-good domain set** and scores how likely the sending domain is impersonating a trusted one. It is a Stage A analyze-and-recommend signal (`VISION.md`), never an autonomous block.

---

## §1 Scope

### In scope (v1)
- A pure-function detector that, given a message's identity domains plus a tenant's known-good domain set, returns a `0-100 lookalike_domain_score` and the `LookalikeFinding` indicators that justify it.
- Detection techniques: exact-match allowlisting (score 0), typosquatting (bounded edit distance), homoglyph / confusable substitution (reusing existing machinery), punycode / IDN (`xn--`) decoding, combosquatting (known-good brand token embedded in a foreign domain, e.g. `paypal-secure.example`), TLD-swap (same second-level label, different TLD), and subdomain-spoof (known-good label as a subdomain of an attacker domain, e.g. `vendor.com.attacker.example`).
- Per-tenant known-good source backed by the Vendor Baseline Store, with the same privacy/isolation posture.
- Deterministic, offline, no-network operation (string + provided-set inference only).
- A default-off / opt-in wiring posture and a lift-only scoring-overlay contribution (no standalone block).
- Crash-resistance / scan-cap behavior for hostile inputs.

### Out of scope (v1)
- No DNS resolution, WHOIS lookup, domain-age check, or any network call (those are a separate future "Domain Reputation Agent" #9).
- No autonomous action — never emits block / quarantine / deny / reject (Stage A; matches Financial State Ledger D11 and the Tiered Detection lift-only invariant).
- No body-URL scoring (that stays in `url_obfuscation_detector.py`).
- No change to the signed Client-Facing 5-Axis Email Scoring Rubric; whether/how this feeds its `sender_identity` axis is §10 Q7.
- No buyer-facing claim language; outputs are internal evidence consumed by the scoring/explanation layer under the existing claim-boundary spec.

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

| # | Decision | Locked value |
|---|---|---|
| D1 | Detector identity | Scores the **sending/identity domain vs known-good domains**. Distinct artifact from `url_obfuscation_detector` (body URLs) and `header_divergence_detector` (auth/routing). |
| D2 | Determinism + offline | Pure function. No network, no DNS, no WHOIS. Same input + same known-good set => identical score and findings. Same posture as `url_obfuscation_detector`. |
| D3 | Stage discipline | Analyze + recommend only. The detector contributes a **floor lift** to the risk overlay; it never produces an autonomous block/quarantine/deny verb. `recommended_action` stays within the Stage A vocabulary. |
| D4 | Reuse, don't reinvent | Homoglyph / confusable mapping and punycode handling are **reused from `url_obfuscation_detector.py`** (shared into a small common module if needed), not re-implemented, so the two detectors cannot drift apart. |
| D5 | Known-good source + privacy | Known-good domains come from the **per-tenant Vendor Baseline Store** (plus, pending §10 Q2, an optional operator-curated trusted-brand seed list). Per-tenant isolation and the hash-only / per-tenant-salt privacy posture of the Vendor Baseline Store are inherited; no cross-tenant known-good leakage. |
| D6 | Lift-only integration | Integration into the risk score is a max-merge floor lift (respecting the signed scoring rubric and the Tiered Detection lift-only invariant), never additive stacking, never a score ceiling change. |
| D7 | Default-off rollout | Ships **default-off / opt-in** (like the Callback Phishing detector) until a calibration dataset shows acceptable FPR; enabling is §10 Q5. |
| D8 | Data minimization | Findings carry the matched technique, the offending domain, the matched known-good domain (or its hash per Q2), and the distance metric — not raw mailbox content. No raw secret/value leakage into the full assessment dump. |
| D9 | Input surface | v1 scores the header `From` domain at minimum; whether `Reply-To`, envelope-`From`, and display-name-embedded domains are also in scope is §10 Q6. |

---

## §3 Detector Structure

### 3.1 Inputs
- The message identity domains (at least header-`From` domain; see D9 / Q6).
- The tenant's known-good domain set (Vendor Baseline Store; see D5 / Q2).
- `tenant_id` for isolation.

### 3.2 Technique checks (each emits a `LookalikeFinding` with `technique`, `offending_domain`, `matched_known_good`, `distance`/evidence)
1. **Exact match** — offending domain ∈ known-good set => score 0, short-circuit (prevents self-FP on legitimate mail).
2. **Typosquat** — bounded Damerau-Levenshtein distance to a known-good domain (threshold by length, §10 Q1).
3. **Homoglyph / confusable** — normalize via the shared confusable map; if the normalized form matches a known-good domain, flag.
4. **Punycode / IDN** — decode `xn--`; re-run homoglyph/typosquat on the decoded label.
5. **Combosquat** — known-good brand token present as a substring/label in a non-known-good domain (FPR-controlled token list, §10 Q4).
6. **TLD-swap** — identical second-level label, different TLD, not in known-good set.
7. **Subdomain-spoof** — known-good label appears as a subdomain of a different registrable domain.

### 3.3 Output
- `lookalike_domain_score` (0-100), set by the highest-severity matched technique (max-merge, not additive — D6).
- Ordered `findings` list.
- Suggested band reads (interpretive, not gates): `0` exact-match/no-match; `1-49` weak/ambiguous; `50-84` probable look-alike; `85-100` strong look-alike (clear typosquat/homoglyph of a known-good domain).

---

## §4 Failure Modes (named)
- **New-vendor false positive** — a legitimate new vendor domain near an existing known-good one. Mitigation: bounded thresholds (Q1), exact-match short-circuit, default-off until calibrated.
- **Regional-brand false positive** — legitimate `brand.co.uk` vs known-good `brand.com` flagged as TLD-swap. Mitigation: Q4 token/known-good curation; band interpretation.
- **Homoglyph false negative** — confusable not in the shared map. Mitigation: shared map with `url_obfuscation_detector` so improvements help both.
- **Combosquat over-firing** — common dictionary words as brand tokens. Mitigation: tight, documented token list (Q4).
- **Cross-tenant leakage** — tenant A's known-good set influencing tenant B. Mitigation: per-tenant isolation (D5), isolation test required.
- **Input DoS** — huge domain/recipient lists or pathological unicode. Mitigation: scan caps + crash-resistance tests.
- **Authority drift** — emitting a block. Mitigation: D3 lift-only; adversarial test asserts no block verb ever appears.

## §5 Audit Requirements
- `complete_gate.py` worker manifest before any implementation commit; `core/` path in hook scope.
- Unit tests per technique + a `break-it` adversarial suite mirroring the Callback Phishing posture: false-positive resistance, false-negative resistance, scope-violation probes (no block verb, no raw-value leak, default-off no-regression), crash resistance (empty / whitespace / control chars / zero-width unicode / oversized inputs / scan caps), cross-tenant isolation, and determinism.
- No network in any test path.
- Independent Grok gate stays in force.

---

## §10 Open Questions (operator-only)
- **Q1 — Edit-distance thresholds.** Distance bands by domain length (e.g. 1 for short SLDs, 2 for longer) — exact values?
- **Q2 — Known-good source + brand seed.** Vendor Baseline Store only, or also an operator-curated global trusted-brand seed list? If seeded, hashed or plaintext, and where stored?
- **Q3 — Scoring overlay mapping.** Exact floor-lift value / band-to-score mapping into the signed rubric (must respect the signed scoring rubric's structure).
- **Q4 — Combosquat token list.** Which brand tokens, and the FPR-control rule for adding one.
- **Q5 — Rollout.** Default-off until calibration (recommended), and what calibration dataset gates enabling default-on.
- **Q6 — Identity-domain surface.** Header-`From` only in v1, or also `Reply-To` / envelope-`From` / display-name-embedded domains?
- **Q7 — Client-facing linkage.** Does this feed the signed Client-Facing 5-Axis Rubric `sender_identity` axis, and if so, how (without a rubric revision)?

### §10.A Operator-Confirmed Decisions (2026-06-05, pre-§11)

Operator ("lock the defaults", 2026-06-05) confirmed all seven questions. These resolve §10 and feed the §11 signature, but this block does **not** sign §11 and authorizes **no** code.

1. **Q1 — Edit-distance thresholds.** Exact match short-circuits to 0. Damerau-Levenshtein against each known-good second-level label: SLD length `<5` => max distance 1; length `5-9` => max distance 1; length `10+` => max distance 2. Transposition counts as one edit. Never compute distance against a public-suffix/TLD label alone.
2. **Q2 — Known-good source + brand seed.** Vendor Baseline Store **only** in v1. No operator-curated global trusted-brand seed list yet; adding one is a later operator-signed amendment. Per-tenant isolation + hash-only / per-tenant-salt posture inherited; no cross-tenant known-good leakage.
3. **Q3 — Scoring overlay mapping.** Detector emits `0-100`; risk integration is **max-merge floor lift only** (never additive, never a ceiling change): weak/ambiguous findings do not lift above 25; probable look-alike floors to 70; strong look-alike (clear typosquat / homoglyph / subdomain-spoof of a known-good domain) floors to 85. Respects the signed scoring rubric and the Tiered Detection lift-only invariant.
4. **Q4 — Combosquat token list.** Tokens are derived from the tenant's own known-good domains only. FPR controls: minimum token length 5; no common dictionary / generic business words (e.g. `pay`, `secure`, `invoice`, `billing`); no tokens from public suffixes; no one-letter / short abbreviations unless operator-curated per tenant.
5. **Q5 — Rollout.** Ships **default-off / opt-in**. Default-on requires a signed calibration record including synthetic adversarial cases, benign near-neighbor cases, cross-tenant isolation tests, and a false-positive review. No default-on before that record exists.
6. **Q6 — Identity-domain surface.** v1 inspects header `From` **and** `Reply-To` domains. Envelope-`From` and display-name-embedded domains are deferred to a later pass (heavier parsing / higher false-positive risk).
7. **Q7 — Client-facing linkage.** **No rubric revision now.** Strong look-alike findings may feed the signed Client-Facing 5-Axis Rubric `sender_identity` axis as an **evidence tag only**, within the existing explanation boundary; no new buyer-facing claim language. A future rubric amendment may formalize exact point mapping if the detector proves useful.

### §10.B Implementation Boundary

These decisions are pre-§11. Locking them authorizes **no** code, **no** detector implementation, **no** wiring into the risk overlay, **no** default-on, **no** change to the signed Client-Facing 5-Axis Rubric, and **no** buyer-facing claim. Implementation begins only after operator §11 signature **and** a separate explicit "start build" instruction.

## §11 Sign-off

Pre-§11 draft. Signing will lock D1-D9 as the detector contract and authorize a build slice. Signing does NOT itself wire the detector default-on or change the signed scoring rubric. A revision to any locked decision requires the normal path: operator instruction -> spec edit -> fresh `complete_gate.py` audit -> new operator §11 signature.

> §11 SIGNED — Matt Nichol June 5th 2026

This §11 signature locks D1-D9 and the §10.A operator-confirmed decisions as the governing Lookalike Domain Detector contract and authorizes a future build slice. It does **not** wire the detector default-on, change the signed Client-Facing 5-Axis Rubric, or start any code: implementation begins only on a separate explicit operator "start build" instruction.
