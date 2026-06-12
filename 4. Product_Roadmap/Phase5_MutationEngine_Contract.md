# Phase 5 — Mutation Engine Agent Design Contract
## Layer 5: Controlled, human-signed swarm evolution

**Document type:** Agent Design Contract
**Status:** §11 SIGNED — Matt Nichol June 12th 2026. Build authorization granted per §11 scope.
**Date drafted:** June 12 2026
**Drafted by:** Cursor (execution lane). This phase had **no operator-dictated concept doc** — the design below is Cursor's draft, grounded in already-signed surfaces and the Swarm Build Map's Layer 5 component list. **The operator must read this before signing**; the signature certifies operator review of a Cursor-authored scope, so it cannot be applied in the same motion that drafts it.
**Authority:** Matt Nichol — sole signing authority
**Depends on:** Phase 1 (`fe355da`) + Phase 2 (`43b5511`) + Phase 3 (`6deffd9` / closed `ce386f7`) + Phase 4 (ReconciliationAgent `d0cc849`, verdict surface + CIRT amendment). Prior art: `core/mutation/engine.py` (sandbox-only, Phase 1.4) and `Phase_1_4_Mutation_Engine_Specialization_Deep_Dive.md`.

---

## §0 — Purpose

The Mutation Engine is how the swarm **gets smarter under pressure** without ever changing its own production behaviour autonomously. It observes confirmed detection gaps, proposes a defensive pattern mutation, proves the mutation against a benign stream, and then **stops** — waiting for the operator's signature before anything reaches production. Every step is sandbox-only until that signature; every deployment is reversible. This phase extends the existing `core/mutation/engine.py`; it does not rebuild it.

The non-negotiable shape (VISION + Build Map Layer 5): **3-shot confirmation → automated validation → human sign-off → full rollback.** No mutation deploys to production without Matt's signature (the `DEPLOY_MUTATION` capability is OPERATOR-only, already enforced in `role_separation.py`).

---

## §1 — Scope

### In scope (six components)
1. **MutationEngine (extend)** — extend `core/mutation/engine.py`; consume confirmed weakness evidence, emit a typed, signed-candidate mutation proposal. Sandbox-only.
2. **3ShotConfirmationTracker** — a candidate pattern must be **independently confirmed 3×** before it is eligible for validation. Append-only confirmation ledger; tenant-aware.
3. **ValidationGate** — automated test of a candidate mutation against a **benign stream** (false-positive guard) before it can be proposed for sign-off.
4. **HumanSignOffGate** — the operator-signature checkpoint. A validated candidate is *proposed*, never deployed, until the operator signs (`DEPLOY_MUTATION`, OPERATOR-only).
5. **RollbackMechanism** — every deployed mutation is reversible; auto-rollback triggers on a post-deployment false-positive spike.
6. **ZeroDayCapture** — the `zero_day_candidate` flag from AttachmentSandbox (#82), referred (not verdict-altering) by ReconciliationAgent (#84, `zero_day_referred`), enters here as an unknown-behaviour candidate → 3-shot → proposed.

### Explicitly out of scope
- **AgentFissionController** — agent division (one agent → two specialised children) is **its own signed contract** (Build Map: "CONCEPT — own contract"). Not built here.
- **The Collective Immune System** — DEPTH GATE CLOSED.
- **The Lung / scaling dials** — separate contract; needs real tenant data.
- **Any autonomous production write.** Production deployment requires the operator signature, full stop.
- **Any change to Phase 1/2/3/4 signed surfaces.**

---

## §2 — Locked Design Decisions (proposed — confirm at signing)

| # | Decision | Proposed locked value |
|---|---|---|
| P5-D1 | Sandbox-only until signed | Every mutation step (propose, confirm, validate) runs sandbox-only. Production write happens only after `DEPLOY_MUTATION` operator sign-off. Inherits the existing `validate_record_against_registry` "mutation is sandbox-only" rule. |
| P5-D2 | 3-shot independent confirmation | A pattern must be confirmed **3× independently** before it is validation-eligible, where **independent = distinct `email_id` AND distinct `tenant_id`** (operator-locked). Three hits on one tenant, or three on one email across tenants, do **not** satisfy it. One incident never mutates the swarm. |
| P5-D3 | Benign-stream validation | A candidate must pass the `ValidationGate` against a benign stream (no false-positive regression beyond the configured threshold) before it can be proposed. |
| P5-D10 | Launch-conservative thresholds, not permanent | The benign-stream FP-regression threshold and the post-deploy spike threshold launch at **conservative static values** and are validated across a **defined test-cycle count** (§3.3 / §3.5). They are **not locked permanently** — they are tunable via a signed amendment once real-tenant data exists. No autonomous re-tuning. |
| P5-D4 | Human sign-off mandatory | No mutation deploys without the operator's signature. `HumanSignOffGate` is deterministic, not advisory. |
| P5-D5 | Full rollback | Every deployed mutation is reversible to the prior signed policy state; auto-rollback fires on a post-deploy false-positive spike above a signed threshold. |
| P5-D6 | Append-only audit trail | Every proposed and deployed mutation is recorded to a `MutationAuditTrail` (append-only) with timestamp, evidence chain, signer, and outcome. |
| P5-D7 | No new output types autonomously | A mutation may tune thresholds/weights/heuristics within the existing typed `MutationKind` enum; introducing a net-new mutation kind or evidence type requires a signed amendment. |
| P5-D8 | Tenant isolation | Confirmation, validation, and deployment scope are tenant-aware; no cross-tenant pattern bleed without an explicit signed broadcast path (that path is the Collective Immune System — gate closed). |
| P5-D9 | Health score target + new track | ELITE 85+ on the Agent Health Score Rubric. A **new Layer 5 rubric track** is added by amendment (mirroring the Layer 4 / ReconciliationAgent precedent), scored on the components that matter for a mutation engine (confirmation integrity, validation rigor, sign-off enforcement, rollback safety, audit completeness). Gate does not close below 85. |
| P5-D11 | Single ensemble scoreboard row | The Mutation Engine takes **one scoreboard row** for the ensemble; the six components (MutationEngine / 3ShotConfirmationTracker / ValidationGate / HumanSignOffGate / RollbackMechanism / ZeroDayCapture) are internal, exactly as #84 covered R1/R2/R3 under one row. |
| P5-D12 | Zero-day routes to Matt only | ZeroDayCapture proposals route to the **operator (Matt) only** — not the governance layer, not the tenant's CIRT individual. Unknown-behaviour patterns are an operator-only decision. |

---

## §3 — Component detail

### §3.1 — MutationEngine (extend `core/mutation/engine.py`)
Reuses the existing sandbox-only engine, `MutationKind` enum, `run_mutation_cycle`, and signed-candidate path. The Phase 5 extension adds the swarm-level wiring: consume confirmed weaknesses from the 3ShotConfirmationTracker rather than raw evaluations, and route validated candidates to the HumanSignOffGate. **Extend, don't rebuild.**

### §3.2 — 3ShotConfirmationTracker
Append-only ledger keyed by candidate pattern. Records each independent confirmation (`email_id` + `tenant_id` + evidence reference). A candidate is `validation_eligible` only at the **3rd confirmation that is distinct on BOTH `email_id` AND `tenant_id`** (P5-D2). A repeat of the same `email_id`, or a third hit from an already-counted `tenant_id`, does **not** advance the count — this blocks a single noisy tenant or a replayed case from mutating the swarm.

### §3.3 — ValidationGate
Runs the candidate mutation against a benign stream (synthetic at ES2; real-traffic shadow at ES3) across a **defined test-cycle count** (`VALIDATION_CYCLES`, launch value locked at signing). Computes the false-positive delta vs the current signed baseline on each cycle; rejects any candidate whose regression exceeds the **launch-conservative threshold** (P5-D10) on any cycle. The threshold and cycle count are tunable by signed amendment, not autonomously. Output is a pass/fail with the measured per-cycle delta — recorded to the audit trail.

#### §3.3.1 — The Anomaly Detection Pipeline (named, ordered, gating)

The ValidationGate is the anchor of the **named Anomaly Detection Pipeline** — the ordered sequence every candidate mutation must clear in full. **Nothing is stamped as a Mutant Monkey standard until it clears every stage.** A candidate that fails any stage stops there; it is recorded and does not advance.

| # | Stage | What it means | Enforced by |
|---|---|---|---|
| 1 | **Anomaly detected** | An anomaly is **flagged, not acted on**. Detection raises a candidate; it never mutates anything on its own. | Detection swarm (Phase 3) + ZeroDayCapture (§3.6) |
| 2 | **Laws-of-average baseline comparison** | Compare against the baseline to decide: **genuine outlier or edge-case variation?** Normal variation is dropped; only a true deviation continues. | Baseline comparator (§3.3) |
| 3 | **3-shot confirmation** | Confirmed **3× across distinct `email_id` AND distinct `tenant_id`** (P5-D2) before it is eligible to validate. | 3ShotConfirmationTracker (§3.2) |
| 4 | **ValidationGate benign-stream test** | False-positive risk check against the benign stream; regression beyond the conservative threshold rejects the candidate. | ValidationGate (§3.3) |
| 5 | **Human sign-off** | **Matt approves before any deployment** (`DEPLOY_MUTATION`, OPERATOR-only). No signature → no deployment. | HumanSignOffGate (§3.4) |
| 6 | **Conservative threshold testing** | A **defined number of cycles** (`VALIDATION_CYCLES`) runs at the launch-conservative threshold before that threshold is treated as locked. | ValidationGate (§3.3) + P5-D10 |
| 7 | **Amendment path** | Thresholds adjust **from real data, not assumptions** — only via a signed amendment, never autonomously. | P5-D10 amendment path |

Stages 1-2 are pre-confirmation triage (flag + baseline), stage 3 is the independence gate, stage 4 is the false-positive gate, stage 5 is the human gate, and stages 6-7 govern how the thresholds themselves are set and revised. The pipeline is **ordered and gating**: a candidate must clear them in sequence, and the "Mutant Monkey standard" stamp is applied only after stage 7's discipline is satisfied.

### §3.4 — HumanSignOffGate
A validated candidate becomes a **proposal**, never a deployment. The gate exposes the proposal + its evidence chain to the operator. Deployment requires `DEPLOY_MUTATION` (OPERATOR-only). No timeout auto-approves; absence of a signature means no deployment.

### §3.5 — RollbackMechanism
Records the prior signed policy state before any deployment. Provides a deterministic revert. Monitors post-deploy false-positive rate over the **defined post-deploy observation window**; on a spike above the **launch-conservative threshold** (P5-D10), auto-reverts and writes a rollback record to the audit trail. Threshold and window are tunable by signed amendment.

### §3.6 — ZeroDayCapture
Bridges Phase 3/4 to Phase 5: an AttachmentSandbox `zero_day_candidate` (recorded by ReconciliationAgent as `zero_day_referred`, never verdict-altering) becomes an unknown-behaviour candidate. It enters the same 3-shot → validate → sign-off pipeline. A zero-day never auto-deploys. **Zero-day capture proposals route to Matt only** (operator-locked, P5-D12) — not to the governance layer and not to the tenant's CIRT individual. A novel/unknown-behaviour pattern is an operator-only decision surface.

---

## §4 — Relationship to signed surfaces

- **Phase 1** — mutation candidates and audit records use the `core/blackboard/` append-only discipline; `RoleSeparationController` already gates `APPROVE_MUTATION` (AUDITOR) and `DEPLOY_MUTATION` (OPERATOR).
- **Phase 3** — `AttachmentSandbox` (#82) `zero_day_candidate` is the ZeroDayCapture input.
- **Phase 4** — `ReconciliationAgent` (#84) `zero_day_referred` is the referral signal; the Mutation Engine never changes a verdict.
- **Existing `core/mutation/engine.py`** — extended, not replaced; the Month 0 / Phase 1.4 paths stay valid.

---

## §5 — Scoreboard (operator-locked)

Watchers reserved #85-87 (concept). The Mutation Engine takes **one row — #88 — for the ensemble** (P5-D11); its six components are internal, exactly as #84 covers R1/R2/R3 under one row. Row #88 flips `SIGNED_UNBUILT → GATED` at phase closure, ELITE 85+ on the new Layer 5 rubric track (P5-D9).

---

## §6 — Test requirements (three classes, per AGENTS.md §5)

**Class 1 — Expected pass**
- A pattern confirmed 3× across distinct `email_id` AND distinct `tenant_id` becomes validation-eligible; fewer than 3 such confirmations does not.
- ValidationGate passes a clean candidate and records the FP delta.
- A validated candidate is *proposed*, not deployed, until signed.
- A signed deployment writes through; rollback restores the prior signed state.
- ZeroDayCapture routes an AttachmentSandbox zero-day into the pipeline without altering any verdict.
- A candidate that clears all seven Anomaly Detection Pipeline stages (§3.3.1) in order earns the "Mutant Monkey standard" stamp; a candidate that fails any stage stops there and is not stamped.

**Class 2 — Adversarial (ELITE standard)**
- A mutation cannot reach production without `DEPLOY_MUTATION` (OPERATOR-only) — enforced, not conventional.
- Duplicate confirmations of the same case do not satisfy 3-shot.
- A candidate that regresses the benign stream beyond threshold is rejected.
- Auto-rollback fires on a simulated post-deploy false-positive spike.
- A mutation cannot introduce a net-new `MutationKind` / evidence type without a signed amendment.
- Cross-tenant pattern bleed is blocked (P5-D8).
- Sandbox-only holds: a mutation write to production outside the signed path is rejected.

**Class 3 — Known-gap xfail**
- Real-traffic shadow validation (ES3) — deferred; needs real tenant stream. Completion path: post-onboarding.
- AgentFissionController — out of scope; separate signed contract.
- Collective-immune broadcast of a confirmed pattern — DEPTH GATE CLOSED.

---

## §7 — Failure modes

| Failure mode | Detection | Response |
|---|---|---|
| Mutation deploys without sign-off | Class 2 | Immediate fail — cannot ship |
| 1-shot (or duplicate) mutates the swarm | Class 2 | Immediate fail — 3-shot violated |
| Validated candidate regresses benign stream | ValidationGate | Rejected; recorded |
| No rollback path for a deployed mutation | Class 1/2 | Immediate fail — P5-D5 |
| Net-new mutation kind without amendment | Class 2 | Immediate fail — P5-D7 |
| Cross-tenant pattern bleed | Class 2 | Immediate fail — P5-D8 |
| Health score below 85 | Rubric | Phase does not close |

---

## §8 — Open questions — RESOLVED (operator, June 12 2026)

| Question | Resolution |
|---|---|
| Scoreboard layout | **One ensemble row, #88** (P5-D11). Six components internal, as #84 did for R1/R2/R3. |
| Rubric track | **New Layer 5 rubric track** added by amendment (P5-D9), mirroring the Layer 4 precedent. |
| Thresholds | **Launch-conservative static values** with a defined test-cycle count and a signed-amendment tuning path; **not locked permanently** (P5-D10). No autonomous re-tuning. |
| 3-shot independence | **Distinct `email_id` AND distinct `tenant_id`** (P5-D2). |
| ZeroDayCapture routing | **Matt only** (P5-D12) — not governance, not CIRT. |

A new Layer 5 Agent Health Score Rubric track (P5-D9) is a pre-build amendment, to be drafted and signed alongside this contract — mirroring how the Layer 4 ReconciliationAgent track landed before the Phase 4 build.

---

## §14 — Operator Sign-Off

**Status:** §11 SIGNED — build authorization granted per §11 scope.

**Signed:** Matt Nichol
**Date:** June 12th 2026
