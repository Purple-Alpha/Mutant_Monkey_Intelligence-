# Real-Customer-Data Controls Consequence Matrix

**Status:** Operator-triggered Consequence Matrix. Pre-spec, non-binding.  
**Date:** 2026-06-05  
**Owner:** Matt Nichol  
**Decision layer:** Butterfly-effect / path-setting. This matrix surfaces second-order effects; Matt decides.

---

## Decision

**Decision:** What control path must be in place before any non-synthetic Cyber Insurance Evidence Package is audited, rendered for buyer delivery, or treated as package-done?

**Why this matters:** Current signed implementation pins Grok-4 / temperature 0 for the package audit path and the current built pipeline is synthetic/test only. Matt has logged an intent to move real customer packages toward NorthStar's own AI on a locked operator-controlled machine. Allowing real customer data into an external model, buyer-rendered PDF, or production datastore without a separate controls decision would violate the project's data-sovereignty boundary and tenant-isolation posture.

**Hard current boundaries:**
- Synthetic/test packages may continue using the existing Stage 9 Grok audit path.
- No real customer package goes to Grok/xAI under the current operating intent.
- The signed Private Test-Data Store is strictly test/lab forever and never holds real customer evidence packages.
- Buyer PDF delivery remains excluded until explicitly authorized.
- Any change to the real-package audit model requires the normal path: operator decision -> spec edit -> fresh gate -> operator sign-off.

---

## Options

- **Option A: Redacted external audit path.** Permit real customer packages to use the existing Grok audit path only after a strict pre-audit redaction/anonymization gate removes customer identifiers and raw sensitive material.
- **Option B: Locked-machine local AI audit path.** Keep Grok limited to synthetic/test packages; real customer packages are audited by operator-controlled local AI on a locked machine, using a NorthStar-specific audit brief and separated roles (builder != auditor).
- **Option C: Human-only real-package review path.** No external AI and no local AI for real customer packages; real packages require manual operator review plus signed acceptance until a production audit model is spec'd later.
- **Option D: Defer real customer packages.** Keep all package generation synthetic/test only; do not permit real customer packages or buyer delivery until the first signed MSP pilot or a later production-data spec.

---

## Short-Term Consequences (0-30 days)

| Option | Opens | Closes | Build Surface Added | Reduces Risk | Creates Risk | Pipeline Signal |
|---|---|---|---|---|---|---|
| A | Fastest route to a real-package audit using existing Stage 9 mechanics. | Closes the "never send real customer data to external AI" intent unless redaction is treated as sufficient. | Redaction/anonymization gate, redaction evidence, external-send approval log. | Reduces build delay. | Highest accidental disclosure risk; redaction bugs become customer-data incidents. | Tests whether the existing Grok audit packet can survive a production-like redaction layer. |
| B | Opens a sovereign real-package audit lane aligned with Matt's locked-machine intent. | Closes direct real-customer Grok submission. | Local model runtime, NorthStar audit brief, machine hardening checklist, audit-output schema, operator machine evidence. | Strongest data-sovereignty and tenant-isolation posture. | More setup and maintenance; local AI quality must be proven before trusting it. | Produces the clearest proof that real customer packages can be audited without external model exposure. |
| C | Opens a minimal manual real-package review lane without model exposure. | Closes AI-assisted independent audit for real packages in v1. | Manual review checklist, operator acceptance record, package-level review log. | Removes model-exfiltration risk. | Weakens independent negative-feedback layer; higher operator-time burden. | Shows whether manual review can bridge the gap for first pilot only. |
| D | Keeps current system clean and synthetic-only. | Closes real customer package readiness for now. | No new build surface. | Eliminates near-term real-data mishandling risk. | Delays revenue/pilot readiness; no proof of real-data handling. | Signals discipline, but no production-readiness evidence. |

---

## Long-Term Consequences (3-12 months)

| Option | Architecture Lock-In | Trust / Credibility Impact | Legal / Insurance Exposure | Maintenance Burden | Evidence / Data Value | Doctrine Drift Risk | Claim / Forbidden-Language Risk | Operator-Time Burden | Long-Term Reversibility |
|---|---|---|---|---|---|---|---|---|---|
| A | Locks toward external-model auditing plus redaction controls. | Mixed: faster, but harder to explain sovereignty if customers ask where data goes. | Highest exposure if redaction fails or provider terms change. | Medium: redaction must be maintained and re-tested constantly. | Useful redaction evidence, but external-send logs become sensitive. | High: invites "redacted enough" shortcuts. | Medium: easy to overstate safety of redaction. | Low-to-medium once built. | Partially reversible; trust damage from one leak is not cleanly reversible. |
| B | Locks toward local sovereign audit infrastructure for real packages. | Strong: matches "operator-owned keys, host, and audit path" story. | Lower external-provider exposure; still needs production-data handling controls. | High at first: hardware, local model, hardening, audit brief, eval calibration. | Strongest durable evidence for sovereignty and audit separation. | Medium: local AI must not become unaudited self-approval. | Low if boundaries are documented. | Medium: setup burden now, lower recurring decision burden later. | Reversible as architecture, but setup time is sunk cost. |
| C | Locks toward manual review as the first production bridge. | Honest but less scalable; may reassure first pilot if operator-led. | Low model exposure; review quality depends on human discipline. | Low engineering, high human process. | Produces operator-review evidence, not model-audit evidence. | Medium: risks weakening "independent auditor" doctrine for real packages. | Low-to-medium if manual wording drifts into claims. | High. | Fully reversible technically; process habits may linger. |
| D | Locks current work to lab-only until later. | Conservative and honest, but may look unready to MSPs. | Lowest immediate exposure. | Lowest. | No real-package evidence generated. | Low. | Low. | Low. | Fully reversible; simply decide later. |

---

## Decision Notes

- **Biggest upside:** Option B creates the cleanest sovereignty story for real customer packages: synthetic/test can keep using Grok, while real packages stay on operator-controlled infrastructure.
- **Biggest downside:** Option B requires a real audit brief and quality calibration for the local AI; "our own AI" is not automatically trustworthy just because it is local.
- **Hidden dependency:** Matt's external agent roster is not yet a NorthStar cyber-insurance audit system. Dax is structurally independent from Maven, but its current brief is website-focused; it needs a NorthStar package-audit brief before it can replace Grok for real packages.
- **Assumption that must be true:** A local model can produce useful negative-feedback audit findings against the signed package specs without seeing training data or builder internals that compromise independence.
- **Optionality killed:** Option A weakens the "never send real customer data to external AI" posture. Option D kills near-term production-package learning.
- **What this implicitly authorizes:** None yet. A selected option authorizes the next spec/edit path only; it does not authorize real customer data handling by itself.
- **Reverse trigger:** Any real customer data exposure, ambiguous provider terms, local-auditor rubber-stamp behavior, or tenant-boundary uncertainty stops the lane and reopens the matrix.
- **Evidence needed before committing:** a signed production-data controls spec or amendment; redaction/tenant-isolation tests; local-audit or manual-review artifact schema; gate-clean audit packet; operator sign-off.

---

## Ranked Decision Aid

This ranking is advisory evidence, not authority.

1. **Option B (locked-machine local AI audit path): strongest default.** Best alignment with Matt's logged intent, data sovereignty, tenant isolation, and future buyer-trust story. Cost is setup and audit-quality proof.
2. **Option C (human-only bridge): safest temporary fallback.** Useful if local AI is not ready, but it does not scale and weakens the independent-audit story if left in place too long.
3. **Option D (defer): safest no-build posture.** Clean, reversible, and low-risk, but it blocks real-package learning and buyer-readiness.
4. **Option A (redacted external audit): weakest fit.** Fastest mechanically, but it conflicts with the emerging sovereignty posture and makes redaction correctness carry too much risk.

---

## Outcome

**Operator decision:** Option B — locked-machine local AI audit path. Real customer packages are audited by operator-controlled local AI on a locked machine; Grok/xAI stays limited to synthetic/test packages until sunset (tokens run out or no longer considered safe).

**Reason:** Best alignment with the logged operator intent (2026-06-04), data sovereignty (operator owns host, keys, and audit path), tenant isolation, and the buyer-trust story. The setup/quality-calibration cost is accepted as the price of not exposing real customer data to an external model.

**Boundary set by this decision (the "scope boundary" half of the milestone):**
- Synthetic/test packages: existing Stage 9 Grok audit path remains valid.
- Real customer packages: no external-model submission; audited only by the operator-controlled local AI on the locked machine, with a NorthStar-specific audit brief and builder/auditor separation (the auditor never audits its own build).
- The signed Private Test-Data Store stays test/lab forever and never holds real customer evidence packages (D14).
- This decision authorizes the next spec/draft path only. It does NOT by itself authorize real customer data handling, buyer PDF delivery, or any change to the §13/IQ3 pins. Those still require: spec edit -> fresh gate -> operator §11/§13 sign-off.

**Review trigger or date:** Re-open this matrix on any real customer data exposure, ambiguous external-provider terms, local-auditor rubber-stamp behavior, tenant-boundary uncertainty, or before the first real (non-synthetic) package is ever audited or buyer-rendered.
