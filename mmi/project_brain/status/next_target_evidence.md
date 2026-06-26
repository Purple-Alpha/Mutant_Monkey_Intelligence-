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

### 2. `#70 Final Review Agent` contract/boundary lane

Recommended owner: `Codex` for boundary review, then `Claude` for contract draft
if Matt selects it.

Lane: `DESIGN`

Score: `7/10`

Evidence:

- Scoreboard row `#70` is `GOVERNANCE_DOC_ONLY (partial)`.
- Code evidence exists: `complete_gate.py` plus
  `core/evidence_package/package_auditor.py`.
- The user need is explicit: "audit / check over / drift" visibility.
- Final Review belongs in Learning/Governance, not Command, so it needs a tight
  authority boundary before build.

Why useful:

- It could become the "check over everything before done" brain component.
- It directly addresses completion-quality anxiety.

Boundary:

- Must not become self-approval.
- Must not authorize its own outputs.
- Needs contract before build.

### 3. `#66 Drift Watch` re-triage lane

Recommended owner: `Codex`.

Lane: `DRIFT_CHECK`

Score: `6/10`

Evidence:

- Scoreboard row `#66` is `GOVERNANCE_DOC_ONLY`.
- Source evidence is signed `Compliance_and_Trend_Watch_Process.md`.
- Runtime already contains watcher drift logic under watcher surfaces
  (`DriftWatcher`), so this needs re-triage before any new build.

Why useful:

- It addresses the operator concern about project drift.
- It may be a reconcile/contract task rather than fresh implementation.

Boundary:

- Do not build blindly; first determine whether `#66` is already covered by
  watcher row `#86` or needs a separate governed surface.

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

- Active task becomes `#19` contract lane for Claude.
- `#66` and `#70` stay queued behind `#19`.
- `#43` stays research/design only until its relationship to governed
  `#79 GeoVelocityAgent` is reconciled.
- No Cursor build is authorized by this selection.
