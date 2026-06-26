# Next Target Evidence Board

This file exists so Matt does not have to pick the next build blind.

## Naming

Old term: `chain of command`

Current terms:

- `project brain`: the living project memory and milestone map
- `PM Voice`: the short operator console
- `dispatcher`: the queue truth checker
- `mission map`: historical stage map; useful context, not enough by itself

The old chain-of-command idea is now split across the project brain, PM Voice,
dispatcher, and mission map.

## Current Evidence Snapshot

Source commands:

```bash
python3 scripts/mmi_pm_voice.py
python3 scripts/mmi_dispatch.py --route-detail
python3 scripts/mmi_estimator.py
python3 scripts/mmi_next_action_rubric.py --limit 12
```

Findings:

- PM Voice asks Matt to pick a next project-brain milestone target.
- Dispatcher reports `ALL_CLEAR`.
- Dispatcher reports `0 SIGNED_UNBUILT` rows.
- Dispatcher reports `0 AWAITING_AUDIT` rows.
- Estimator reports `NO_BUILDABLE_CANDIDATES`.
- Estimator excludes `#10 Lookalike Domain` because it is already `GATED`.
- Estimator excludes `#21 Executive Impersonation` because it is already `GATED`.
- Estimator excludes `#105 MMI Governance Invariants Testing Framework` because it is `SIGNED_CONTRACT`, not a build lane; Lane 2+ is held.
- Current live rubric only surfaces weak/admin actions:
  - admin lane board sync: `5/10`
  - promotion `#10`: `1/10`
  - promotion `#21`: `1/10`
  - hold: `3/10`

## Important Drift Finding

The historical mission map still references old BOR feedstock language such as
`#71 Token Usage Tracker` as rank-1. That is stale for current routing because
the live scoreboard/decision log now show `#71` as already governed and the
dispatcher reports no buildable candidates.

This means Matt should not be asked to pick from the old mission-map text alone.
The next target needs a fresh evidence-backed candidate board.

## Reconciliation Result

The apparent "build next" queue is empty. The next useful action is not Cursor
implementation. It is selecting the next target lane and preparing the correct
contract/review path.

The next target should be chosen from the evidence below.

## Ranked Next Targets

### 1. `#19 Dual-Approval` contract lane

Recommended owner: `Claude` for contract drafting, then `Codex` for pre-build
gate review.

Lane: `CONTRACT`

Score: `8/10`

Evidence:

- Scoreboard row `#19` is `SPEC_ONLY`.
- Blocker is `NEEDS_SIGNED_CONTRACT`.
- Source evidence is `Vendor Payment Verification Workflow (draft)`.
- SPARK map explicitly marks Dual-Approval as specced/partial.
- Vendor-payment integrity is a strong business spine already referenced in
  product-roadmap material.

Why this is strongest:

- It creates real buildable feedstock after contract/gate/sign.
- It advances vendor-payment / BEC controls rather than admin cleanup.
- It avoids pretending `GATED` cleanup is a new build.

Boundary:

- Not a Cursor build yet.
- Needs contract draft, pre-build gate, Matt §11, then explicit build
  authorization.

### 2. `#70 Final Review Agent` contract/boundary lane — **CONTRACT DRAFT PLACED (MMI-DEC-242)**

**Boundary review (MMI-DEC-240):** `GOVERNANCE_DOC_ONLY (partial — surfaces mapped)`. Slice A satisfied;
Slice B needs contract.

**Contract (MMI-DEC-242):** `4. Product_Roadmap/Final_Review_Agent_Design_Contract_Deep_Dive.md`
— DRAFT pre-§11; Step 00 31/31 PASS. Pre-build gate **0 blocking / 2 warnings** (MMI-DEC-243).

Recommended owner: `Matt` §11 signature.

Lane: `CONTRACT` (active — SIGNABLE)

Score: `8/10`

Evidence:

- Scoreboard row `#70` surfaces mapped; stale `NEEDS_BUILD_AUTH` cleared.
- Code evidence: `audit_tools/complete_gate.py` plus
  `core/evidence_package/package_auditor.py` (Slice A); `agent_contract.py`
  `FINAL_REVIEW_AGENT_ID` hook (Slice B unbuilt).
- Final Review belongs in Learning/Governance, not Command — self-approval risk
  documented.

Why useful:

- Clarifies what existing gate tools cover vs what still needs a contract.
- Unblocks honest contract drafting without pretending gates are the agent.

Boundary:

- Must not become self-approval.
- Must not authorize its own outputs.
- Needs contract before Slice B build.

### 3. `#66 Drift Watch` re-triage lane — **COMPLETE (MMI-DEC-236)**

**Verdict:** `RECLASSIFY` — operator process only (`Compliance_and_Trend_Watch_Process.md` + `Frontier_Intake_Log.md`). Not buildable agent. Distinct from #86 W2 DriftWatcher.

**Artifact:** `mmi/project_brain/status/drift_watch_66_re_triage.md`

Recommended owner: `Codex`.

Lane: `DRIFT_CHECK`

Score: `6/10` (at time of original evidence; triage now closed)

Evidence:

- Scoreboard row `#66` was `GOVERNANCE_DOC_ONLY` with stale `NEEDS_BUILD_AUTH`.
- Source evidence is signed `Compliance_and_Trend_Watch_Process.md` (no runtime path per spec §1).
- Runtime `#86 W2 DriftWatcher` is unrelated (confidence drift observer, GATED).

Boundary:

- No build unless Matt authorizes new contract for intake automation.

### 4. `#43 Geo-Context` reconcile lane

Recommended owner: `Codex`.

Lane: `DRIFT_CHECK`

Score: `4/10`

Evidence:

- Scoreboard row `#43` is `SPEC_ONLY`.
- It references Sender Provenance / Geo-Velocity proof protocol.
- Runtime already has governed `#79 GeoVelocityAgent`.

Why weak:

- This appears likely stale or partially superseded by `#79`.
- It should not become a build target until reconciled.

## Weak Cleanup Options

`#10` and `#21` promotion reviews remain available, but live rubric gives each
only `1/10`. They are cleanup, not the next build direction.

## Recommendation

Recommended next operator pick:

```text
task: Start #19 Dual-Approval contract lane from Vendor Payment Verification evidence
for: Claude
score: 8/10
```

If Matt wants to focus on the project-control problem instead of product build
feedstock, choose:

```text
task: Boundary review for #70 Final Review Agent
for: Codex
score: 7/10
```

Do not send a build to Cursor until one of these paths produces signed
authority and explicit build authorization.

## Matt Selection

Matt selected the following order:

1. `#19 Dual-Approval` contract lane
2. `#66 Drift Watch` re-triage lane
3. `#70 Final Review Agent` boundary/design lane

Matt also requested more research/design on `#43 Geo-Context`.

Routing consequence:

- `#19` contract draft is now placed at
  `4. Product_Roadmap/Dual_Approval_Agent_Design_Contract_Deep_Dive.md`.
- Codex pre-build gate review for the #19 draft completed and BLOCKED.
- Gate artifact:
  `audit_outputs/mmi_19_contract_gate_20260626T045557Z.md`
- Gate result: `1 blocking / 1 warning`; packet SHA256
  `46cad25e3bf1d96616f459a988ade024651c73d1c898081368f4fb8a9772dd57`.
- Active task becomes upstream Vendor Payment Verification workflow dependency
  repair before #19 can be re-gated.
- `#66` and `#70` stay queued behind `#19`.
- `#43` stays research/design only until its relationship to governed
  `#79 GeoVelocityAgent` is reconciled.
- No Cursor build is authorized by this selection.

Blocking reason:

- `#19` depends on
  `4. Product_Roadmap/Vendor_Payment_Verification_Workflow_Ergonomics_Deep_Dive.md`.
- That upstream workflow is still DRAFT pre-§11 and has open questions Q1-Q6.
- #19 is therefore not signable until that dependency is signed or explicitly
  carved out.

Warning:

- Replace the phrase `substitute controls` with plainer wording before re-gate.

## Purple Team Research Branch

Matt supplied a defensive-first Purple Team design concept. It is captured at:

`mmi/project_brain/architecture/purple_translation_layer.md`

Classification:

- lane: `RESEARCH` / `DESIGN`
- related targets: `#43` and `#70`
- build status: not authorized

Design direction:

- build Blue/Purple evidence handling before Red/safe simulation
- start with a Unified Fact Schema
- keep Red and Blue logic separate
- MLLM role is evidence translation/correlation, not autonomous action
- no active probing, exploitation, customer scanning, rule deployment, or AUTH-5
  from this research branch

## Agentic Swarm Command Center Research Addendum

Matt supplied additional Blue Team Swarm Command Center research covering
orchestrator/sub-agent structure, forensic/header analysis, behavioral context,
threat-intel enrichment, ERP/accounting checks, HITL gates, analyst evidence
trails, deception concepts, and active-response concepts.

Captured at:

`mmi/project_brain/architecture/purple_translation_layer.md`

Classification:

- lane: `RESEARCH` / `DESIGN`
- related targets: `#43` and `#70`
- build status: not authorized

Routing impact:

- does not interrupt the active Claude task for #19 upstream dependency repair
- future safe first contract should be a read-only Blue Analysis Module, not
  the full autonomous swarm
- deception, payload modification, mailbox clawback, account lockout, prompt
  mutation, generated-rule deployment, and external reporting stay parked behind
  separate legal/safety authority

## Adversarial Resilience Harness Research Note

Matt also raised the need for an internal system that pushes Mutant Monkey
Security software to its limits before release. Captured as:

`MMI Adversarial Resilience Harness`

Location:

`mmi/project_brain/architecture/purple_translation_layer.md`

Classification:

- lane: `RESEARCH` / `DESIGN`
- related targets: `#70` and governance testing
- build status: not authorized

Safe framing:

- not an autonomous hack bot
- owned local repo and lab fixtures only
- first buildable slice should be deterministic breaker tests for routing,
  contracts, tenant isolation, evidence-chain handling, and gate-skipping drift
- no real targets, internet scanning, exploit deployment, malware behavior,
  credential harvesting, destructive action, production dispatch, or AUTH-5
