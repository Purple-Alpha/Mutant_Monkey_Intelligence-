# Lookalike Domain Detector — Spec-First Deep Dive

**Status:** DRAFT (pre-§11). Authored 2026-06-05 by Cursor on Matt Nichol's instruction (next-milestone selection: "spec the first swarm-map agent"). This is the first agent promoted from the operator-adopted `agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md` (swarm agent #10, "Lookalike Domain Agent"), team 2 (email identity / sender analysis). **§11 signature is blank by design.** This draft authorizes no code; it is the spec contract that a later build slice implements after operator §10 resolution + §11 sign-off.

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

## §11 Sign-off

Pre-§11 draft. Signing will lock D1-D9 as the detector contract and authorize a build slice. Signing does NOT itself wire the detector default-on or change the signed scoring rubric. A revision to any locked decision requires the normal path: operator instruction -> spec edit -> fresh `complete_gate.py` audit -> new operator §11 signature.

> §11 SIGNED — _(blank; operator to author)_
