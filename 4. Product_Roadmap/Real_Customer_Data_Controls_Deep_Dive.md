# Real-Customer-Data Controls — Deep Dive

**Status:** DRAFT (pre-§11). Authored 2026-06-05 by Cursor (Claude Opus 4.8) on Matt Nichol's instruction, rolling forward from the real-customer-data controls decision (Option B; `_Real_Customer_Data_Controls_Consequence_Matrix.md`). No runtime code, no infrastructure, no signed-spec change is authorized by this draft. The §10 open questions are operator-only. §11 signature is blank by design.

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

## §10 Open Questions (operator-only)

These are path-setting and remain Matt's to resolve; the agent will bring each pre-scored when this spec is taken toward §11.

- **Q1 — Local AI substrate.** Which local model + runtime on the locked machine (and the minimum quality/calibration bar before it is trusted to audit real packages)?
- **Q2 — Locked-machine definition.** What exactly makes the machine "locked" (network isolation, disk encryption, no-sync, physical control) and how is that verified?
- **Q3 — Auditor agent.** Reuse an operator-roster agent (e.g. Dax) with a new NorthStar package-audit brief, or define a dedicated NorthStar auditor? Either way, how is builder/auditor independence proven?
- **Q4 — Production datastore.** Does the real-package production datastore get its own deep-dive spec (recommended), and what production controls does it require beyond the test store?
- **Q5 — Done-Criteria parity.** Exact output schema the local audit must emit so Done Criteria 11/12 evaluate identically to the external path.
- **Q6 — External-model sunset trigger.** The precise condition(s) that retire Grok even for synthetic/test (token exhaustion, terms change, safety judgment) and what replaces it.
- **Q7 — Buyer delivery linkage.** Whether real-package buyer delivery is gated only by D8 here or also folded into a separate buyer-delivery spec.

---

## §11 Sign-off

_§11 signature blank by design. This draft iterates freely (pre-§11). Implementation, infrastructure, the §13/IQ3 revision, and any handling of real customer data do not begin until every §10 question is resolved, the spec is §11-signed by Matt, and a separate explicit operator start-build instruction is issued._

**Operator signature:** _(blank — operator-authored at §11)_
