# Executive Impersonation Detector — Spec-First Deep Dive

**Status:** §11 SIGNED 2026-06-06 by Matt Nichol. Second agent promoted from the operator-adopted `agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md` (swarm agent #21, "Executive Impersonation", team 3 — vendor-payment / BEC). Followed the proven path of the §11-signed Lookalike Domain Detector (#10): spec-first → §10 → §10.A operator-confirmed decisions → §11 signature. D1-D9 + §10.A are locked as the detector contract. Signing locks the contract only — it authorizes **no** code, **no** wiring, **no** default-on, and **no** change to the signed Client-Facing 5-Axis Rubric; a separate explicit operator Build Authorization is required before any implementation.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey**. No rename implied.

**Source-of-truth links:**
- `agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md` (swarm map; this is agent #21, "Executive Impersonation (CEO/CFO urgency/secrecy)")
- `core/scoring/callback_phishing_detector.py` (existing **TOAD closed-vocabulary pressure-phrase engine** — reused here for authority/urgency/secrecy pressure, see D4)
- `core/scoring/lookalike_domain_detector.py` (existing `extract_identity_domains` From+Reply-To surface and the `LookalikeDomainAssessment`/`LookalikeDomainFinding` schema pattern — reused/mirrored here, see D4/D9)
- `4. Product_Roadmap/Vendor_Baseline_Store_Deep_Dive.md` (per-tenant known-good source; privacy/isolation posture inherited, see D5)
- `4. Product_Roadmap/Tiered_Detection_Intensity_Deep_Dive.md` (lift-only invariant)
- `core/scoring/client_facing_rubric.py` `_score_sender_identity` (the `sender_identity` axis — consumer of this signal; §10 Q7)
- `core/blackboard/models.py` `EmailAnalysisImpersonationAnalysis.impersonation_likelihood` (existing impersonation surface this detector corroborates, see §3.3 / Q7)
- `VISION.md` (Stage A = analyze + recommend only; the seven non-negotiables)

---

## Agent Design Contract Wrapper (metadata-only retrofit)

**Retrofit boundary:** This wrapper is additive governance metadata only, applied under `Agent_Design_Contract_Template_Deep_Dive.md` §7. It does **not** edit, reinterpret, relax, or extend the signed detector contract below. D1-D9, §10.A, scoring bands/floors, default-off posture, input surface, data-minimization rules, rubric linkage, Build Authorization status, and §11 remain unchanged.

| Field | Value |
|---|---|
| Agent name | Executive Impersonation Detector |
| Swarm inventory ID | #21 — Executive Impersonation (CEO/CFO urgency/secrecy) (v1 map inventory/backlog reference only) |
| Canonical layer | Detection |
| Canonical team / case type | Vendor-payment / BEC; executive-authority impersonation |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | Stage A analyze/recommend only |
| Role | Produce deterministic executive-impersonation evidence when a claimed executive/authority identity is paired with an identity mismatch and authority/secrecy/urgency/task-directive pressure. |
| Boundary | The detector is not the decision. It must not decide fraud, approve/deny mail, block/quarantine, alter payment behavior, create a new rubric point rule, or change the LLM `impersonation_likelihood` relationship. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no org-chart sync/network lookup; no phone-number extraction; no buyer-facing claim; no default-on enablement without the signed calibration record required by §10.A Q5. |
| Inputs | Sender display name, `From` and `Reply-To` domains via `extract_identity_domains`, per-tenant Known-Good Principal Roster, `body_plain`, `tenant_id`, and optional consumed look-alike cue, exactly as locked in D9 / §10.A Q6. |
| Outputs | `ExecutiveImpersonationAssessment`-style internal assessment: `executive_impersonation_score`, ordered findings, and max-merge `recommended_risk_floor_lift` evidence. |
| Evidence emitted | Claimed principal role/label, domain relationship, matched technique, pressure category, bounded non-echoing evidence string, and whether the result supports the `executive_impersonation_pattern` evidence tag only. |
| Data minimization | No raw mailbox body, no body substring over 60 chars, no raw headers beyond scoped identity-domain evidence, no phone digits, no tenant secret material, and no cross-tenant roster leakage. |
| Tenant isolation | Per-tenant Known-Good Principal Roster only; tenant A's roster must never influence tenant B. Plaintext display-name forms remain tenant-local per §10.A Q1. |
| Two-pass role | Pass 1 detection only until the Two-Pass Decision Model spec is signed; provides evidence a future Pass 2 challenge can inspect. |
| Decision Evidence Record contribution | `observed_facts`: claimed display-name match, identity-domain relationship, pressure/task-directive category; `interpretations`: executive-impersonation pattern classification; `assumptions`: tenant roster is current and operator-maintained; `missing_evidence`: absent/stale roster, missing body_plain, missing look-alike cue, or calibration gaps; `recommended_verification`: known-good out-of-band verification for executive/payment/credential requests; `final_outcome_contribution`: `executive_impersonation_pattern` evidence tag / risk-floor input only; `retest_or_learning_record`: false-positive/false-negative correction evidence after calibration failures. |
| Human review trigger | Probable or strong executive-impersonation evidence on payment, credential, secrecy, urgency, or executive-authority context should route to human review through existing Stage A review vocabulary. |
| Verification trigger | Any executive-impersonation evidence tied to money movement, vendor changes, credentials, gift cards, or confidential executive directives should trigger known-good out-of-band verification before action. |
| Scoring / action posture | Max-merge floor lift only, non-additive; `executive_impersonation_pattern` may feed `sender_identity` as evidence attribution only; no deterministic axis-score lift or point-structure change in this retrofit. |
| Default rollout | Default-off / opt-in until a signed calibration record exists. |
| Autonomous action | None. |
| Promotion conditions | Signed calibration record showing acceptable false-positive behavior, synthetic adversarial executive-BEC coverage, benign authorized-executive cases, common-name collision coverage, cross-tenant isolation, no raw-value/body leakage, deterministic results, and useful evidence output. |
| Demotion conditions | Overclaims beyond evidence, pressure-only over-fire, false positives above accepted calibration boundary, missed serious executive-impersonation cases, cross-tenant leakage, raw-value/body leakage, unsupported recommendations, autonomous-action wording, or failed retests. |
| Retest evidence | Updated synthetic/adversarial/benign cases plus regression proof after any correction. |
| Calibration requirement | The signed calibration record required by §10.A Q5 before default-on or increased influence. |
| Failure modes | Inherits §4 named failure modes: legitimate-executive false positive, common-name collision, pressure-only over-fire, roster staleness, cross-tenant leakage, vocabulary false negative, input DoS, and authority drift. |
| Required tests | Inherits §5 test requirements: unit, break-it, integration, no-network, no-block-verb, no raw-value/body leak, no phone-digit extraction, default-off no-regression, crash resistance, cross-tenant isolation, and determinism. |
| Audit requirements | Any implementation or future retrofit/revision remains subject to `complete_gate.py`; this wrapper itself is gated as metadata-only. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `Vendor_Baseline_Store_Deep_Dive.md`, `Tiered_Detection_Intensity_Deep_Dive.md`, `Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`, `VISION.md`, and `Compliance_and_Trend_Watch_Process.md`. |
| Build Authorization dependency | A separate explicit Build Authorization is still required before implementation; this wrapper authorizes no code, no wiring, no default-on, no rubric change, no buyer-facing claim, and no runtime behavior change. |

---

## §0 Purpose

Catch the classic Business Email Compromise (BEC) case where an inbound email **claims to be from a known executive or authority figure of the tenant** (CEO, CFO, owner, controller) and pairs that claimed authority with a pressured, secret, or time-boxed task directive (wire this, change the payment details, buy gift cards, "handle it before the close of business, keep it between us") — while the **sending identity is not** the executive's known-good identity (foreign domain, free-mail provider, or a look-alike of the tenant's own domain).

The existing detectors do not cover this specific pairing:
- `lookalike_domain_detector.py` scores **domain** look-alikes against a tenant's known-good **domain** set, but does not reason about a claimed **executive principal** (display name / role) or about authority/secrecy pressure language.
- `callback_phishing_detector.py` scores **callback/TOAD** pressure to move fraud onto a phone call, not executive-authority impersonation paired with a task directive.
- `EmailAnalysisImpersonationAnalysis.impersonation_likelihood` is an LLM-produced surface; this detector adds a **deterministic, offline** corroborating signal for the specific executive-impersonation pattern.

This detector closes that gap: given a message's sender display name + identity domains, the tenant's **known-good principal roster** (executive names + their authorized sending domains), and the message body, it deterministically scores how likely the message is an executive-impersonation BEC attempt and emits the `ExecutiveImpersonationFinding` indicators that justify it. It is a Stage A analyze-and-recommend signal (`VISION.md`), never an autonomous block.

---

## §1 Scope

### In scope (v1)
- A pure-function detector that, given (a) the sender display name, (b) the message identity domains (From + Reply-To, reusing `extract_identity_domains`), (c) the tenant's known-good principal roster, and (d) `body_plain`, returns a `0-100 executive_impersonation_score` plus the `ExecutiveImpersonationFinding` indicators that justify it.
- Detection logic built from two reused surfaces only:
  1. The **Tenant Known-Good roster pattern** (per-tenant principal roster: executive display-name forms + their authorized sending domains), inheriting the Vendor Baseline Store privacy/isolation posture.
  2. The **TOAD closed-vocabulary pressure-phrase engine** style from `callback_phishing_detector.py`, extended with an executive-authority / secrecy / task-directive closed vocabulary (English-only, conservative compiled patterns — same discipline as TOAD D11).
- Deterministic, offline, no-network operation (string + provided-roster inference only).
- A default-off / opt-in wiring posture and a max-merge lift-only scoring-overlay contribution (no standalone block, non-additive).
- A defined evidence-package structure feeding the `sender_identity` axis as evidence tags only (no rubric revision — §10 Q7).
- Crash-resistance / scan-cap behavior for hostile inputs.

### Out of scope (v1)
- No DNS resolution, WHOIS lookup, mailbox-history fetch, org-chart sync, or any network call.
- No autonomous action — never emits block / quarantine / deny / reject (Stage A; matches Financial State Ledger D11, Lookalike D3, and the Tiered Detection lift-only invariant).
- No phone-number extraction or storage (that boundary stays with the TOAD detector).
- No new buyer-facing claim language; outputs are internal evidence consumed by the scoring/explanation layer under the existing claim-boundary spec (`Compliance_and_Trend_Watch_Process.md`).
- No change to the signed Client-Facing 5-Axis Email Scoring Rubric; whether/how this feeds its `sender_identity` axis is §10 Q7 (evidence tag only in v1).
- No domain-only look-alike detection (that stays in `lookalike_domain_detector.py`; this detector *consumes* a lookalike signal as one corroborating cue, it does not re-implement it).
- Non-English pressure vocabulary, display-name-embedded domains, and envelope-`From` are deferred to a later pass (§10 Q6).

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

| # | Decision | Locked value |
|---|---|---|
| D1 | Detector identity | Scores a **claimed-executive-principal + authority-pressure + identity-mismatch** pattern. Distinct artifact from `lookalike_domain_detector` (domain-only), `callback_phishing_detector` (callback/TOAD), and the LLM `impersonation_likelihood` surface. |
| D2 | Determinism + offline | Pure function. No network, no DNS, no org-chart sync. Same inputs + same roster => identical score and findings. Same posture as Lookalike D2 / TOAD. |
| D3 | Stage discipline | Analyze + recommend only. Contributes a **max-merge floor lift** to the risk overlay; never an autonomous block/quarantine/deny verb. `recommended_action` stays within the Stage A vocabulary. |
| D4 | Reuse, don't reinvent | Identity-domain extraction reuses `extract_identity_domains` (From+Reply-To). Pressure-language detection reuses the **TOAD closed-vocabulary pattern-engine style** (conservative compiled regex, closed category enum, generic non-echoing reasons). The assessment/finding schema mirrors `LookalikeDomainAssessment`/`LookalikeDomainFinding` (fired-invariants). A look-alike domain cue is consumed from the Lookalike detector, not re-implemented. |
| D5 | Roster source + privacy | The known-good principal roster is a **per-tenant** structure (executive display-name forms + authorized sending domains) following the **Vendor Baseline Store** pattern; per-tenant isolation and the hash-only / per-tenant-salt privacy posture are inherited. No cross-tenant roster leakage. Exact storage shape is §10 Q1. |
| D6 | Lift-only integration | Integration into the risk score is a **max-merge floor lift** (respecting the signed scoring rubric and the Tiered Detection lift-only invariant), **never additive stacking**, never a score-ceiling change. Multiple findings do not sum. |
| D7 | Default-off rollout | Ships **default-off / opt-in** (like Lookalike D7 and the Callback Phishing detector) until a signed calibration record shows acceptable FPR; enabling is §10 Q5. |
| D8 | Data minimization | Findings carry the matched technique, the claimed principal role/label, a bounded non-echoing evidence string, the domain relationship (mismatch / lookalike / free-provider), and the pressure category — **not** raw mailbox body, raw headers, phone digits, or tenant secret material. No raw secret/value leakage into the full assessment dump; no email-body substring > 60 chars echoed; evidence strings <= 160 chars (the rubric `why_this_score` cap). |
| D9 | Input surface | v1 inspects the sender **display name**, the **From** and **Reply-To** identity domains (via `extract_identity_domains`), and **`body_plain`** for pressure vocabulary. Envelope-`From`, display-name-embedded domains, HTML body, and non-English vocabulary are deferred (§10 Q6). |

---

## §3 Detector Structure

### 3.1 Inputs
- Sender display name (message `display_name`).
- Identity domains (From + Reply-To) via `extract_identity_domains`.
- Tenant known-good principal roster (per-tenant; see D5 / Q1): for each principal, a set of accepted display-name forms and a set of that principal's authorized sending domains.
- `body_plain` for pressure-vocabulary scanning.
- `tenant_id` for isolation.
- (Optional, consumed not computed) a `lookalike_sender_domain` cue / `LookalikeDomainAssessment` if the Lookalike detector is also enabled.

### 3.2 Technique checks (each emits an `ExecutiveImpersonationFinding` with `technique`, `claimed_principal_role`, `domain_relationship`, `pressure_category`, bounded `evidence`)
1. **Roster-name match + domain mismatch** — sender display name matches a roster principal form (match rule per Q2), but the sending identity domain is **not** in that principal's authorized-domain set => identity-mismatch finding.
2. **Free-mail executive claim** — display name matches a roster principal, but the sending domain is a known consumer free-mail provider (gmail/outlook/yahoo/etc., list per Q6) rather than a tenant/authorized domain.
3. **Lookalike-domain executive claim** — roster-name match where the sending domain is a look-alike of an authorized domain (cue consumed from the Lookalike detector when enabled).
4. **Authority / secrecy / urgency pressure** — closed-vocabulary detection of executive-authority framing ("as the CEO/CFO, I need you to…"), secrecy ("keep this between us / confidential / do not loop in…"), urgency/time-box ("before the close of business / right now"), reusing the TOAD pattern-engine style. Pressure alone never fires the detector — it is a corroborating multiplier on an identity finding (see 3.3).
5. **Task directive** — closed-vocabulary detection of a high-risk directive paired with the above (wire transfer / change bank or ACH details / purchase gift cards / urgent payment). Task directive corroborates; it does not independently fire.

### 3.3 Output and scoring (max-merge floor lift, non-additive — D6)
- `executive_impersonation_score` (0-100), set by the **highest-severity matched combination** (max-merge, not additive).
- Ordered `findings` list.
- Banded floor-lift mapping (exact values are §10 Q4; recommended defaults below mirror Lookalike's 25/70/85 discipline):
  - **weak / ambiguous** (name resemblance only, no domain mismatch, no pressure) => does not lift above **25**.
  - **probable** (roster-name match **+** identity mismatch/free-mail/lookalike, **or** identity mismatch **+** authority pressure) => floors to **70**.
  - **strong** (roster-name match **+** identity mismatch/lookalike **+** authority/secrecy/urgency pressure **+** a task directive) => floors to **85** (parity with the FSL / TOAD strong-band floor).
- The detector contributes its banded value as `recommended_risk_floor_lift`; the scoring agent max-merges it onto the existing floor exactly as it does for `LookalikeDomainAssessment` and `CallbackPhishingAssessment`.

### 3.4 Evidence package structure for the `sender_identity` axis (per the operator's explicit requirement)
The detector produces a frozen, validator-checked assessment mirroring `LookalikeDomainAssessment`:

```text
ExecutiveImpersonationFinding (StrictModel)
  technique:            Literal["roster_name_domain_mismatch",
                                "free_mail_executive_claim",
                                "lookalike_domain_executive_claim",
                                "authority_pressure",
                                "task_directive"]
  claimed_principal_role: Literal["executive", "finance_authority", "owner", "other_authority"]
  domain_relationship:  Literal["mismatch", "free_provider", "lookalike", "not_applicable"]
  pressure_category:    Literal["authority", "secrecy", "urgency", "task_directive", "none"]
  evidence:             str (1..160 chars, generic, no raw lure echo, no body substring > 60 chars)

ExecutiveImpersonationAssessment (StrictModel)
  detector_version:            Literal["v1"] = "v1"
  fired:                       bool
  executive_impersonation_score: int (0..100)
  findings:                    tuple[ExecutiveImpersonationFinding, ...]
  recommended_risk_floor_lift: int (0..100)
  # fired-invariants identical in spirit to LookalikeDomainAssessment:
  #   fired=False  => score == 0, findings == (), lift == 0
  #   fired=True   => >= 1 finding, score >= 1, lift >= 1
```

Wiring into the `sender_identity` axis (§10 Q7; **evidence tag only**, no rubric revision in v1):
- When `fired` is True, the scoring agent appends a single behavioral flag `executive_impersonation_pattern` to `EmailAnalysisRiskAnalysis.behavioral_deviation_flags` (added to the `BehavioralDeviationFlag` Literal in the same build commit), exactly as Lookalike appends `lookalike_sender_domain`.
- `_score_sender_identity` may surface that flag as **`sender_identity` evidence attribution only** (the way it already reads `lookalike_sender_domain` for attribution). It **must not create a new axis-score lift or point-structure rule in v1** — no new deterministic point change to the signed rubric. A formal point mapping requires a signed rubric amendment.
- The assessment is attached to `EmailAnalysisPayload.executive_impersonation_assessment` (new optional slot, default `None`), persisted as overlay evidence like the lookalike assessment.

---

## §4 Failure Modes (named)
- **Legitimate-executive false positive** — a real CEO genuinely emails an urgent payment request from an authorized domain. Mitigation: identity finding requires a **domain mismatch / free-mail / lookalike**; authorized-domain mail short-circuits to no-fire. Default-off until calibrated.
- **Common-name collision** — a non-executive sender shares a display name with a roster principal. Mitigation: name-match rule (Q2) + domain-mismatch requirement; pressure/task corroboration required for the strong band.
- **Pressure-only over-fire** — urgency language with no identity anomaly. Mitigation: pressure never fires alone (D3.2/3.3); identity finding is required.
- **Roster staleness** — executive leaves / new exec not in roster. Mitigation: roster is operator-maintained per tenant; missing principal simply means no roster match (fails safe to no-fire), not a false positive.
- **Cross-tenant leakage** — tenant A's roster influencing tenant B. Mitigation: per-tenant isolation (D5); isolation test required.
- **Vocabulary false negative** — novel phrasing outside the closed vocabulary. Mitigation: closed-but-extensible vocabulary within v1 category bounds (TOAD discipline); a brand-new category is a v1.1 addendum.
- **Input DoS** — huge bodies / rosters / pathological unicode. Mitigation: scan caps + crash-resistance tests (mirror TOAD / Lookalike break-it posture).
- **Authority drift** — emitting a block verb. Mitigation: D3 lift-only; adversarial test asserts no block verb ever appears and `recommended_action` is never rewritten.

## §5 Audit Requirements
- `complete_gate.py` worker manifest before any implementation commit; `core/` path in hook scope.
- Unit tests per technique + a `break-it` adversarial suite mirroring the Callback Phishing / Lookalike posture: false-positive resistance (authorized-domain exec mail, common-name collision, pressure-only), false-negative resistance, scope-violation probes (no block verb, no raw-value / no body>60-char leak, no phone-digit extraction, default-off no-regression), crash resistance (empty / whitespace / control chars / zero-width unicode / oversized inputs / scan caps), cross-tenant isolation, and determinism.
- Integration tests proving default-off no-regression, explicit opt-in fire path, max-merge floor lift (non-additive), single `executive_impersonation_pattern` flag append, attach-always assessment overlay, and no autonomous-action rewrite — mirroring `test_lookalike_domain_scoring_integration.py`.
- No network in any test path.
- Independent Grok gate stays in force.

---

## §10 Open Questions (operator-only)
- **Q1 — Roster source + storage shape.** A dedicated per-tenant Known-Good Principal Roster (executive display-name forms + authorized sending domains). Stored following the Vendor Baseline Store pattern: hashed display-name forms (privacy) or plaintext (needed for fuzzy matching)? Where does it live, and who maintains it?
- **Q2 — Name-match algorithm.** Exact normalized-string match only (case/whitespace/punctuation-folded), or fuzzy match (reuse the Lookalike Damerau-Levenshtein machinery on display names) with a threshold? If fuzzy, what distance bands?
- **Q3 — Pressure vocabulary.** Which closed categories (authority / secrecy / urgency / task-directive), reuse the TOAD module directly or a new sibling module under `core/scoring/`? English-only closed vocabulary (TOAD D11 discipline) confirmed?
- **Q4 — Scoring overlay mapping.** Exact floor-lift bands (recommended: weak <=25 / probable 70 / strong 85). Confirm non-additive max-merge and the exact combination rules that reach each band.
- **Q5 — Rollout.** Default-off until calibration (recommended). What calibration record gates default-on (synthetic adversarial exec-BEC cases, benign authorized-exec cases, common-name collisions, cross-tenant isolation, false-positive review)?
- **Q6 — Input surface + free-mail list.** From + Reply-To + display name + `body_plain` in v1 (recommended). Which consumer free-mail provider list defines "free_provider"? Confirm envelope-`From`, display-name-embedded domains, HTML body, and non-English vocabulary are deferred.
- **Q7 — Client-facing linkage.** Feed the signed `sender_identity` axis as an **evidence tag only** (no rubric revision now), via the `executive_impersonation_pattern` flag, the way `lookalike_sender_domain` is already read? Confirm no point-structure change and no relationship change to LLM `impersonation_likelihood` in v1.

### §10.A Operator-Confirmed Decisions (2026-06-06, pre-§11)

Operator ("lock the defaults", 2026-06-06) confirmed all seven questions with the FP-safe, reuse-first defaults below. These resolve §10 and feed the §11 signature, but this block does **not** sign §11 and authorizes **no** code.

1. **Q1 — Roster source + storage shape.** A dedicated **per-tenant Known-Good Principal Roster**: for each principal, a set of accepted display-name forms plus that principal's authorized sending domains, following the Vendor Baseline Store pattern. **Plaintext display-name forms are a deliberate privacy tradeoff**: they are stored only inside the tenant-local roster because matching requires them. Salt does not protect plaintext — so the protection is structural: **per-tenant storage isolation, plus salted/hashed treatment for any *derived* identifiers, prevents cross-tenant roster reuse.** Operator-maintained per tenant. A hash-only variant for the display-name forms themselves is deferred (it would block matching). Adding org-chart sync or any network source is a later operator-signed amendment.
2. **Q2 — Name-match algorithm.** **Normalized exact match only in v1**: case-fold, collapse/strip whitespace, strip punctuation and titles/honorifics, before comparing against roster display-name forms. **No fuzzy display-name matching in v1** — fuzzy (reusing the Lookalike Damerau-Levenshtein machinery) is deferred to a v1.1 addendum once calibration data exists. Domain-side look-alike detection is still consumed from the Lookalike detector (not re-implemented).
3. **Q3 — Pressure vocabulary.** A **new sibling module** `core/scoring/executive_impersonation_detector.py` reuses the **TOAD pattern-engine style** (conservative compiled regex, closed category enum, generic non-echoing reasons) — it does **not** import the TOAD module directly, so the two detectors' vocabularies cannot drift into each other. Closed categories: `authority`, `secrecy`, `urgency`, `task_directive`. **English-only** closed vocabulary (TOAD D11 discipline); a brand-new category is a v1.1 addendum.
4. **Q4 — Scoring overlay mapping.** Detector emits `0-100`; risk integration is **max-merge floor lift only, non-additive** (never a ceiling change). Bands: weak/ambiguous (name resemblance only, no domain mismatch, no pressure) does not lift above **25**; **probable** (roster-name match + identity mismatch/free-mail/lookalike, **or** identity mismatch + authority pressure) floors to **70**; **strong** (roster-name match + identity mismatch/lookalike + authority/secrecy/urgency pressure + a task directive) floors to **85**. Pressure and task-directive findings never fire the detector alone — an identity finding is always required.
5. **Q5 — Rollout.** Ships **default-off / opt-in**. Default-on requires a signed calibration record including synthetic adversarial executive-BEC cases, benign authorized-executive cases, common-name collision cases, cross-tenant isolation tests, and a false-positive review. No default-on before that record exists.
6. **Q6 — Input surface + free-mail list.** v1 inspects sender **display name**, **From** and **Reply-To** domains (via `extract_identity_domains`), and **`body_plain`**. "free_provider" is defined by a curated, documented consumer free-mail list (e.g. gmail, googlemail, outlook/hotmail/live, yahoo, icloud/me/mac, aol, proton/protonmail, gmx, zoho, yandex); additions are a documented change. Envelope-`From`, display-name-embedded domains, HTML body, and non-English vocabulary are **deferred** to a later pass.
7. **Q7 — Client-facing linkage.** **No rubric revision now.** When the detector fires, the scoring agent appends a single `executive_impersonation_pattern` behavioral flag. The signed rubric §3.1 already enumerates `behavioral_deviation_flags` (with "etc."), so the flag **may be surfaced as `sender_identity` evidence attribution only; it must not create a new axis-score lift or point-structure rule in v1.** It is read the way `_score_sender_identity` already reads `lookalike_sender_domain` for attribution, with **no** new deterministic point lift and **no** change to the LLM `impersonation_likelihood` relationship. A formal point mapping requires a signed rubric amendment.

### §10.B Implementation Boundary

These decisions are pre-§11. Locking them authorizes **no** code, **no** detector implementation, **no** wiring into the risk overlay, **no** default-on, **no** change to the signed Client-Facing 5-Axis Rubric, and **no** buyer-facing claim. Implementation begins only after operator §11 signature **and** a separate explicit "start build" instruction.

## §11 Sign-off

Pre-§11 draft. Signing will lock D1-D9 and the §10.A operator-confirmed decisions as the governing Executive Impersonation Detector contract — a **stable engineering blueprint for a future build slice**. Signing does NOT itself wire the detector default-on or change the signed scoring rubric. **No code generation or environment writes occur until a separate explicit operator Build Authorization.** A revision to any locked decision requires the normal path: operator instruction -> spec edit -> fresh `complete_gate.py` audit -> new operator §11 signature.

> §11 SIGNED — Matt Nichol June 6th 2026

This §11 signature locks D1-D9 and the §10.A operator-confirmed decisions as the governing Executive Impersonation Detector contract — a stable engineering blueprint for a future build slice. It does **not** wire the detector default-on, change the signed Client-Facing 5-Axis Rubric, or start any code: no code generation or environment writes occur until a separate explicit operator Build Authorization.
