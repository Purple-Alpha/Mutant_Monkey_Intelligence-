# Real-Customer-Data Controls — Deep Dive

**Status:** §11 SIGNED 2026-06-05 by Matt Nichol. Authored 2026-06-05 by Cursor on Matt Nichol's instruction, rolling forward from the real-customer-data controls decision (Option B; `_Real_Customer_Data_Controls_Consequence_Matrix.md`); §10 resolved to D9-D15 on Matt's "agree all" instruction; §11 signed the same day after a clean readiness gate. Signing locks the controls contract (D1-D15) only. It authorizes no runtime code, no infrastructure, no §13/IQ3 pin change, no real-customer-data handling, and no buyer delivery — each of those remains a separate explicit operator gate per the decisions below.

**Owner:** Matt Nichol

**Purpose:** Define the controls that must be in place before any real (non-synthetic) Cyber Insurance Evidence Package is audited, rendered, or treated as package-done — so real customer data never transits an external model and never crosses tenant boundaries.

---

## §0 Purpose

The Cyber Insurance Evidence Package generator (stages 8/9/10 + criterion-14 signature + PDF renderer) is built and proven on synthetic/test data only. The §13/IQ3 pins currently route the Stage 9 package audit to an external model (Grok-4 / temperature 0). That is acceptable for synthetic/test packages but not for real customer packages.

The real-customer-data controls decision (Option B, 2026-06-05) set the direction: real customer packages are audited by operator-controlled local AI on a locked machine; the external model stays limited to synthetic/test packages until sunset. This spec turns that direction into a controls contract: what must be true, and what is forbidden, before a real package can move through audit, render, delivery, or done-declaration.

This spec is a controls / boundary contract. It does not build the local-AI substrate, does not stand up a production datastore, and does not authorize handling real customer data by itself. Each of those is a separate, explicitly-authorized build behind this contract.

---

## §1 Scope

### In scope
- The control boundary separating the synthetic/test audit path (external model permitted) from the real-customer audit path (local-AI-only).
- Requirements for the local-AI audit substrate: operator-controlled host, builder/auditor separation, a NorthStar package-audit brief, and audit-output parity with the Stage 9 contract so Done Criteria 11/12 can be satisfied without an external model.
- Data-handling controls for real packages: tenant isolation, redaction, key handling, and the no-external-egress rule.
- The revision path: how the §13/IQ3 pins are changed (spec edit -> gate -> operator sign-off) before any real package is audited.
- The sunset rule for the external model on the synthetic/test path.

### Out of scope
- The synthetic/test path itself, which is unchanged (external model permitted while in force per §13/IQ3).
- The Private Test-Data Store, which stays test/lab forever (D14 of that spec) and never holds real customer evidence packages.
- A production datastore design for real customer artifacts — flagged here as a dependency, specified separately (see §10 Q4).
- Buyer-facing commercial terms, pricing, and the buyer PDF delivery authorization (separate explicit operator decisions).
- Any new external/compliance/insurance claim. This spec adds none.

---

## §2 Locked Design Decisions (proposed; lock at §11)

- **D1 — Real customer data never transits an external model.** Real (non-synthetic) customer evidence packages, their source artifacts, and their audit packets are never submitted to Grok/xAI or any third-party model. The Stage 9 audit for real packages runs only on operator-controlled local AI on a locked machine.
- **D2 — External model is synthetic/test only, with a sunset.** Grok/xAI remains permitted for synthetic/test package audits while §13/IQ3 keeps it pinned and while the operator considers it safe. It is retired when API tokens run out or it is no longer considered safe; retirement does not require re-spec, only an operator note.
- **D3 — Builder/auditor separation for the local AI.** The local audit substrate keeps the project's non-negotiable separation: the auditor never audits its own build. If an operator-roster agent fills the auditor role, it carries a NorthStar package-audit brief (the spec-compliance audit equivalent of `complete_gate.py`), not a generic or website brief.
- **D4 — Real packages require a separate production datastore.** Real customer artifacts are never stored in the Private Test-Data Store or in synthetic/test locations. A production datastore with production controls is a prerequisite, specified separately, before any real package is generated or stored.
- **D5 — Real-package data-handling controls are at least as strict as synthetic.** Tenant isolation (Guardrail 11), the redaction gate, forbidden-language gate, and no-secrets-in-repo discipline all apply to real packages at least as strictly as to synthetic packages; real-package controls may add requirements but never relax the synthetic baseline.
- **D6 — Local audit output must satisfy the Done-Criteria contract.** The local-AI audit produces output parity with the Stage 9 contract (a saved audit artifact dated after generation, deviations as Drift Incident Reports) so Done Criteria 11/12 can be evaluated identically regardless of which auditor ran. A local audit that cannot produce this parity is not a valid package audit.
- **D7 — §13/IQ3 revision is a precondition for any real-package audit.** The implementation spec currently pins the package audit to Grok-4. No real package may be audited until §13/IQ3 is revised through the normal path (operator decision -> spec edit -> fresh gate -> operator §13 sign-off) to authorize the local-AI auditor for the real path. This draft does not perform that revision.
- **D8 — No buyer delivery of real packages until separately authorized.** The renderer remains internal/synthetic; buyer-facing delivery of a real package is a separate explicit operator decision (ties to the standing buyer-delivery gate).
- **D9 — Local-AI substrate locks to calibration criteria, not a forever model.** The real-package auditor is selected by a local substrate profile and calibration gate, not by hard-marrying the project to one model name in this spec. Before it may audit real packages, the local AI must pass the same synthetic package cases the external Stage 9 path can pass, catch deliberately planted spec/claim/data-boundary mistakes, and refuse to bless a broken package. The exact model/runtime is selected when the locked machine is built and may be changed later only by rerunning the calibration gate and logging the change.
- **D10 — "Locked machine" means verifiable operator control.** Minimum v1 locked-machine controls are: operator physical control, full-disk encryption, no cloud-sync folder for real artifacts, no browser/session sharing during audits, no external network during real-package audit runs except explicitly logged local-network dependencies, and a short per-run checklist recording those facts. "Locked" is not a trust statement; it is a recorded condition of the audit run.
- **D11 — Dax is the default local auditor role, with a NorthStar package-audit brief.** The operator's existing Dax auditor agent is the default local-auditor shell because it already exists as a separated auditor role. It must receive a NorthStar Cyber Insurance Package Audit Brief before it may audit this surface; its current non-NorthStar / website-focused brief is not sufficient. If Dax built or materially edited a package, Dax cannot audit that package; builder/auditor separation always wins.
- **D12 — Production datastore gets its own deep-dive spec.** Real customer package artifacts require a separate Production Evidence Store spec before any real package is generated, stored, audited, rendered, or delivered. The Private Test-Data Store remains test/lab forever and cannot be widened by this spec. The production store spec must cover tenant isolation, encryption/key handling, backup/restore, retention, deletion, access control, audit trail, and no-cloud-sync boundaries.
- **D13 — Local audit output must mirror the Stage 9 evidence contract.** The local AI must emit a saved, timestamped audit artifact with package ID, auditor identity/profile, input package hash, spec references checked, verdict, findings, and Drift Incident Reports for deviations. A bare pass/fail, chat transcript, or unstructured thumbs-up does not satisfy Done Criteria 11/12.
- **D14 — Grok/xAI synthetic sunset trigger is explicit and low-friction.** Grok/xAI is retired even for synthetic/test audits when any of these occur: API tokens run out, provider terms or safety posture become unacceptable to the operator, the local-AI auditor passes the synthetic calibration gate and the operator chooses to consolidate, or any external-model data-boundary incident occurs. Retiring Grok for synthetic/test audits needs an operator log entry; re-authorizing it later requires a fresh controls decision.
- **D15 — Buyer delivery stays separately gated.** This spec's D8 remains the live buyer-delivery boundary. Detailed delivery mechanics belong in a later Buyer Delivery / Production Package Delivery spec, not as a side effect of real-data controls. No real package is buyer-delivered until that later authorization path is run.

---

## §3 Control Boundary (synthetic vs real)

| Dimension | Synthetic / test path | Real customer path |
|---|---|---|
| Audit model | External model (Grok-4 / temp 0) while §13/IQ3 in force | Operator-controlled local AI on a locked machine only (D1) |
| Data store | Private Test-Data Store (test/lab only) | Separate production datastore with production controls (D4) |
| Egress | Audit packet may leave to the external model | No external egress of real data, ever (D1) |
| Render/deliver | Internal synthetic render only | Internal until buyer delivery separately authorized (D8) |
| Done Criteria 11/12 | Satisfied by the external Stage 9 audit | Satisfied by the local audit with output parity (D6) |
| Authorization to run | Standing internal/synthetic envelope | Requires §13/IQ3 revision + operator sign-off (D7) |

The boundary is enforced by classification: a package is either synthetic/test or real. There is no mixed mode. A real package that cannot meet the real-path controls is not generated, not audited, and not rendered — it fails closed.

---

## §5 Failure Modes

1. **Real data to external model.** Any path that sends real customer data, artifacts, or audit packets to Grok/xAI. Mitigation: D1 hard rule; classification gate; no-egress check on the real path.
2. **Local-auditor rubber-stamp.** The local AI approves its own build or returns success on any input (the documented stub-gate failure mode). Mitigation: D3 builder/auditor separation; D6 output parity so findings are real Drift Incident Reports, not a boolean.
3. **Production datastore scope creep.** Real artifacts leak into the test store or synthetic locations. Mitigation: D4 separate production datastore; Private Test-Data Store D14 test/lab-forever boundary.
4. **Tenant bleed.** Real packages cross tenant boundaries. Mitigation: D5 keeps Guardrail 11 at least as strict as synthetic.
5. **Silent pin change.** The audit model is swapped without revising §13/IQ3. Mitigation: D7 makes the revision a precondition; the pin change is operator-signed, not inferred.
6. **Over-claim drift.** A real package implies compliance/certification/coverage. Mitigation: the §13-signed boundary statement and forbidden-language gate apply unchanged.

---

## §6 Audit / Evidence Requirements

- Standing up the local-AI audit substrate and the production datastore are infrastructure changes; each runs its own setup runbook + verification, logged through the normal evidence surfaces.
- The §13/IQ3 revision that authorizes the local auditor runs `complete_gate.py` in its own slice and requires operator sign-off.
- No real customer package may be audited or rendered until D7's revision is signed; until then this spec is a controls contract only.
- Any external hand-off remains an explicit, logged action; the default is no external egress for the real path.

---

## §10 Resolved Questions

Resolved 2026-06-05 by Matt Nichol's "agree all" instruction after the seven questions were presented one by one with defaults and consequences. These resolutions are encoded as D9-D15 above and are ready for §11 review.

- **Q1 — Local AI substrate -> D9.** Lock the calibration gate and selection criteria, not a forever model name.
- **Q2 — Locked-machine definition -> D10.** Locked means verifiable operator control: physical control, disk encryption, no cloud sync, no shared sessions, no external network during audit runs except logged local dependencies, and a per-run checklist.
- **Q3 — Auditor agent -> D11.** Reuse Dax as the default auditor role, but only with a NorthStar Cyber Insurance Package Audit Brief and never on packages Dax built or materially edited.
- **Q4 — Production datastore -> D12.** Real customer package artifacts require their own Production Evidence Store deep-dive spec; the Private Test-Data Store stays test/lab forever.
- **Q5 — Done-Criteria parity -> D13.** Local audit output mirrors the Stage 9 evidence contract with timestamped audit artifacts and Drift Incident Reports, not bare pass/fail.
- **Q6 — External-model sunset trigger -> D14.** Retire Grok/xAI for synthetic/test when tokens run out, provider terms/safety posture fail, local calibration passes and the operator consolidates, or any external-model data-boundary incident occurs.
- **Q7 — Buyer delivery linkage -> D15.** Buyer delivery stays separately gated here, with detailed mechanics deferred to a later Buyer Delivery / Production Package Delivery spec.

---

## §11 Sign-off

This spec is §11 SIGNED. Signing locks D1-D15 as the controls contract. It does NOT authorize implementation, infrastructure, the §13/IQ3 revision, real-customer-data handling, or buyer delivery; each of those still requires a separate explicit operator start-build or sign-off per the decisions above. A revision to any locked decision requires the normal path: operator instruction -> spec edit -> fresh `complete_gate.py` audit -> new operator §11 signature.

> §11 SIGNED — Matt Nichol(Zebra-Comet) June,5th. 2026

*Authorship note: Matt authored the signature line above in-session; the assistant only placed it. The §10 resolutions D9-D15 reflect Matt's explicit "agree all" instruction after the seven questions were presented one by one with defaults and consequences.*
