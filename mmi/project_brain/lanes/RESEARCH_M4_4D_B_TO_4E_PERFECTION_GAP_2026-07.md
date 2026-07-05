# RESEARCH_M4_4D_B_TO_4E_PERFECTION_GAP_2026-07

## Authority Class

`AUDIT_ONLY`

This artifact is documentation/audit material only.

It does **not** authorize build.
It does **not** promote lifecycle state.
It does **not** close M4.
It does **not** advance PERFECT.
It does **not** claim boundary containment.
It does **not** replace PM, Superintendent, or operator authority.

Recommended repo path:

```text
lanes/RESEARCH_M4_4D_B_TO_4E_PERFECTION_GAP_2026-07.md
```

---

# Doctrine

```text
MMI must only accept claims that are perfectly bounded by evidence,
perfectly bounded by scope, perfectly bound to lineage,
and perfectly blocked whenever uncertainty remains.
```

```text
When uncertainty exists, the system moves downward in authority, never upward.
```

---

# Final Status Phrase

```text
4E_SPEC_PREP_ALLOWED_WITH_BLOCKERS_RECORDED

This authorizes scoped specification preparation only.
It does not prove boundary containment.
It does not close M4.
It does not advance PERFECT.
It does not authorize build.
It does not promote any lifecycle state.
```

---

# Core Claim Rule

```text
Claim supported only within explicitly tested scope;
no cross-layer closure inferred.
```

---

# One-Way Failure Rules

```text
evidence missing      -> INVALID
lineage missing       -> INVALID
scope drift           -> INVALID
cross-layer inference -> INVALID
authority missing     -> NO PROMOTION
recovery missing      -> NO ENDURANCE CLAIM
reviewer disagreement -> OPEN
residual risk open    -> NO CLOSURE CLAIM
summary unbound       -> NON-EVIDENCE
model-only result     -> NO LIVE CLAIM
single-phase result   -> NO CROSS-LAYER CLOSURE
```

---

# Closure Semantics

## OPEN
No sufficient proof exists for the scoped claim.

## REDUCED_WITHIN_EXPLICITLY_TESTED_SCOPE_ONLY
Partial evidence exists inside a declared scope, but the risk remains open outside that tested scope.

Do not shorten this to `REDUCED` in summaries. The full phrase is required to prevent overread.

## CLOSED_EXACT_SCOPED_CLAIM_ONLY
The exact claim is fully supported within the explicitly declared scope, with raw evidence, negative tests, recovery behavior, reviewer validation, and residual-risk linkage.

Do not shorten this to `CLOSED` in summaries. The full phrase is required to prevent overread.

## INVALID
The claim is broader than the evidence, combines layers without proof, relies on summary without raw lineage, or attempts to promote without authority metadata.

---

# Non-Inheritance Warnings

These warnings must be repeated in any 4D_b, 4E, PM, Superintendent, or summary artifact that cites this research.

```text
4D_b does not prove network egress containment.
4E does not prove file-boundary containment.
4D_b + 4E do not prove host containment.
4D_b + 4E do not close R-001.
4D_b + 4E do not close R-008.
4D_b + 4E do not close R-030.
4D_b + 4E do not close R-031 unless the later fixture matrix proves the exact scoped claim.
4D_b + 4E do not close M4.
4D_b + 4E do not advance PERFECT.
No cross-layer closure is inferred.
```

---

# Perfection-Gap Checklist

## 1. Cross-Layer Overreading

### Risk
4D_b and 4E may be mentally combined into “boundary proven.”

### Required Rule
4D_b and 4E must each carry an explicit non-inheritance warning.

### Pass Criteria
- 4D_b states: `This does not prove network egress containment.`
- 4E states: `This does not prove file-boundary containment.`
- Both state: `This does not prove host containment, sandbox escape closure, PC2->PC1 closure, M4 closure, or PERFECT.`
- Any combined claim points to a separate cross-layer proof artifact.

### Fail Criteria
- Any artifact says or implies `boundary proven` from 4D_b + 4E alone.
- Any summary uses `contained`, `closed`, `safe`, `perfect`, or `M4-ready` without scoped evidence.

### Status Rule
If violated, mark the claim `INVALID`, not reduced.

---

## 2. Modeled Proof vs Live Proof

### Risk
Policy-model success may be treated as live Windows host containment.

### Required Rule
Modeled results and live enforcement results must be stored in separate evidence classes.

### Pass Criteria
- Modeled test artifacts are labeled `MODEL_ONLY`.
- Live enforcement artifacts are labeled `LIVE_HOST_ENFORCEMENT`.
- No `MODEL_ONLY` artifact is cited as evidence for live containment.
- Fixtures reused across model/live tests include a separation note.

### Fail Criteria
- Model output is cited for live containment.
- Same fixture set is reused without declaring whether behavior is modeled or live.
- Reviewer accepts policy success as proof that live behavior is probably fine.

### Status Rule
Model proof can reduce design uncertainty only. It cannot close live enforcement risk.

---

## 3. WFP Scope Boundary

### Risk
WFP success is overread as host containment.

### Required Rule
4E supports only claims within the explicitly tested network-enforcement scope.

### Required Negative Tests
- Default-deny behavior
- IPv4 egress
- IPv6 egress
- DNS leakage
- Loopback / localhost paths
- Local proxy path
- WSL-originated process traffic
- Rule persistence after reboot
- Daemon/service death
- Rule corruption
- Policy removal attempt

### Required Evidence Fields
Each WFP test must record:

```text
test_id
policy_hash
active_rule_snapshot
source_process
source_namespace_or_context
destination
protocol
expected_action
observed_action
event_log_pointer
timestamp_source
pass_fail
residual_risk_link
```

### Fail Criteria
- Rule installation is treated as enforcement proof.
- IPv4 passes but IPv6 is untested.
- DNS is untested.
- Loopback is untested.
- Daemon death fails open.
- Missing telemetry is treated as inconclusive instead of failed.

### Status Rule
A WFP pass supports only network-egress control inside the explicitly tested scope.

---

## 4. Minifilter Scope Boundary

### Risk
A lab-success file barrier fails on real Windows path behavior.

### Required Rule
4D_b supports only file I/O boundary claims inside explicitly tested scope.

### Required Negative Tests
- Driver unload
- Driver crash
- Service crash
- Rename-then-write
- Temp-file write then move
- Case variation
- Short path / 8.3 path if enabled
- Symlink
- Junction
- Reparse point
- Hardlink
- Alternate Data Stream
- Volume mount point
- UNC/path alias where applicable
- Admin override attempt
- WSL/DrvFs relay attempt
- 9P relay attempt
- Concurrent write/race attempt

### Required Evidence Fields
Each minifilter test must record:

```text
test_id
driver_hash
driver_version
loaded_filter_state
altitude_or_order_if_applicable
path_attempted
canonical_path_resolved
operation_type
expected_action
observed_action
event_log_pointer
pass_fail
cleanup_result
residual_risk_link
```

### Fail Criteria
- Basic write blocked is treated as barrier proof.
- Path canonicalization is not tested.
- ADS, hardlinks, junctions, or rename patterns are not tested.
- Driver unload/crash behavior is not tested.
- Admin override assumptions are not documented.

### Status Rule
A minifilter pass supports only file I/O boundary control inside explicitly tested scope.

---

## 5. Formal TCB Boundary Map

### Risk
Trusted boundary becomes vague.

### Required Rule
Every claim must identify which components are trusted, untrusted, semi-trusted, or out of scope.

### Required TCB Rows
- Windows kernel
- WFP engine
- Filter Manager
- Minifilter driver
- Boundary daemon
- Signing key/certificate
- Policy manifest
- Evidence writer
- Clock witness
- Test harness
- WSL clone
- PC1
- PC2
- Operator
- Reviewer
- Summary generator

### Required Fields Per Row
```text
component
trust_role
reason_for_trust
compromise_consequence
evidence_required
may_close_claims_yes_no
```

### Fail Criteria
- Component is trusted by implication.
- Test harness is allowed to prove itself.
- Reviewer or operator authority is assumed but not logged.
- Signing key custody is not declared.

### Status Rule
If the TCB is undefined, any containment claim is `INVALID`.

---

## 6. Recovery and Rollback

### Risk
The system blocks during a demo but cannot safely recover, repair, quarantine, or prevent bad promotion.

### Required Rule
Recovery is part of boundary assurance, not a later convenience.

### Required Tests
- Bad WFP rule rollback
- Minifilter bad-state recovery
- Daemon crash recovery
- Service restart behavior
- Reboot behavior
- Quarantine on uncertain state
- Evidence preservation during failure
- No-promotion after failed run
- Operator override logging
- Safe cleanup after failed test

### Required Evidence Fields
Each recovery test must record:

```text
test_id
failure_injected
expected_safe_state
observed_safe_state
rollback_command_or_path
evidence_preserved_yes_no
promotion_blocked_yes_no
reviewer_result
residual_risk_link
```

### Fail Criteria
- Recovery is described but not tested.
- Rollback depends on undocumented operator knowledge.
- Failed run can still be promoted.
- Evidence is lost during recovery.
- Quarantine is optional.

### Status Rule
No recovery proof means no endurance claim.

---

## 7. Canary Failure Semantics

### Risk
Canaries go quiet and the run still looks clean.

### Required Rule
Silent canary failure is itself a failure.

### Required Tests
- Positive hit
- Negative miss
- Bypass variation
- Log-loss simulation
- Alert transport failure
- Canary rule corruption
- Canary disable attempt
- Summary mismatch

### Pass Criteria
- Known hostile action fires.
- Known benign action does not fire.
- Similar hostile path also fires.
- Missing telemetry invalidates the run.
- Alert transport failure invalidates the run.
- Summary matches raw canary ledger.

### Fail Criteria
- No alert is treated as success without telemetry proof.
- Canary transport failure is warning only.
- Canary log gaps do not fail the run.
- Summary says no canary hits without proving canary health.

### Status Rule
Canary silence without health proof equals failed run.

---

## 8. Evidence Integrity and Summary Drift

### Risk
A summary overclaims while raw artifacts remain ambiguous.

### Required Rule
A summary is not evidence unless hash-bound to the raw artifact set it summarizes.

### Required Evidence Bundle
- Raw logs
- Test outputs
- Event logs
- Policy/rule snapshots
- Driver/service hashes
- Harness version
- Clock witness
- Reviewer notes
- Residual-risk ledger
- Summary hash
- Raw artifact manifest hash

### Pass Criteria
- Every summary claim links to raw artifact IDs.
- Every raw artifact has a hash.
- Summary declares exact scope.
- Summary declares what it does not prove.
- Raw artifact set is immutable after summary generation.

### Fail Criteria
- Summary contains claims not found in raw evidence.
- Summary uses broader wording than test scope.
- Raw artifacts are missing, mutable, or unhashed.
- Reviewer signs summary without checking raw lineage.

### Status Rule
Unbound summary equals non-evidence.

---

## 9. Clock and Continuity

### Risk
Restarts, gaps, or log discontinuities hide failed endurance.

### Required Rule
Continuity proof is required for every endurance or sustained-control claim, not only final 48h proof.

### Required Tests
- Monotonic clock check
- Wall-clock drift check
- Heartbeat sequence
- Restart detection
- Log gap detection
- Event sequence continuity
- Evidence writer interruption
- Resume semantics
- Run invalidation after unsupported gap

### Pass Criteria
- Gaps are recorded as first-class evidence.
- Restart semantics are declared before the run.
- Unsupported restart invalidates the run.
- Heartbeat loss fails the run.
- Clock drift is bounded and reported.

### Fail Criteria
- Run duration is measured only by wall clock.
- Restart hides a gap.
- Missing heartbeat is warning only.
- Logs resume without discontinuity marker.

### Status Rule
No continuity proof means no endurance claim.

---

## 10. Residual Risk as Live Blocker

### Risk
Residual risk becomes bookkeeping.

### Required Rule
Open residuals must block related closure claims.

### Required Fields
Each residual must have:

```text
residual_id
owner
affected_claim
current_state
closure_condition
required_evidence
phase_dependency
last_reviewed_date
stale_date_threshold
```

### Fail Criteria
- Closure claim exists while linked residual is OPEN.
- Residual is stale.
- Residual has no owner.
- Residual has no closure condition.
- Residual is not linked to claims.

### Status Rule
Open, stale, or unlinked residual risk blocks claim closure.

---

## 11. Reviewer Failure Modes

### Risk
Reviewer approval masks scope or evidence failure.

### Required Reviewer Counter-Checks
- Scope misread
- Incomplete evidence accepted
- Model proof confused with live proof
- WFP proof confused with file proof
- Minifilter proof confused with network proof
- Summary accepted as raw proof
- Residual risk ignored
- Recovery skipped
- Canary silence accepted
- Authority metadata missing

### Required Reviewer Questions
Reviewer record must answer:

```text
What exact claim is being reviewed?
What exact evidence supports it?
What evidence is missing?
What does this not prove?
Which residuals remain open?
Is promotion allowed?
Who has authority?
```

### Fail Criteria
- Reviewer signs broad conclusion.
- Reviewer cites summary only.
- Reviewer does not check residual ledger.
- Reviewer resolves disagreement by momentum.
- Reviewer authorizes promotion without authority metadata.

### Status Rule
Reviewer failure invalidates promotion, not just the review.

---

## 12. Audit vs Build-Prep Separation

### Risk
Research language accidentally becomes build authorization.

### Required Rule
Every artifact must declare its authority class.

### Valid Authority Classes
- `RESEARCH_ONLY`
- `AUDIT_ONLY`
- `SPEC_PREP_ONLY`
- `SIGNED_SPEC`
- `BUILD_AUTHORIZED`
- `BUILT_NEEDS_VERIFICATION`
- `GATED`
- `INVALID`

### Pass Criteria
- 4D_b audit material is labeled `AUDIT_ONLY` unless separately authorized.
- 4E planning material is labeled `SPEC_PREP_ONLY` unless separately authorized.
- No artifact uses `proceed` without stating whether it means research, spec, or build.
- Promotion requires explicit authority metadata.

### Fail Criteria
- `Clear to proceed` appears without authority class.
- Build-prep text is treated as build authorization.
- Research findings mutate project state.
- Gate status changes without explicit authorization.

### Status Rule
No authority metadata means no promotion.

---

# Required 4D_b Closeout Cleanup Check

```text
4D_B_CLOSEOUT_CLEANUP_CHECK:
- mmi_m4_boundary_probe absent
- temp staging dirs absent
- CAT/signing staging dirs absent or intentionally archived
- WFP test rules absent unless explicitly persistent
- minifilter test artifacts removed or logged
- pre/post VERIFY_FINGERPRINT attached
- dirty tree state recorded
```

---

# Required Pre-Codex Diff Preservation

```text
PRE_CODEX_DIFF_BUNDLE:
- git status --short
- git diff > evidence/pre_codex_4d_hotfixes.diff
- git diff --staged > evidence/pre_codex_4d_staged.diff
- driver signing/CAT staging notes
- known local-only files list
- reason each local change exists
- explicit statement: NOT REVIEWED, NOT AUTHORITY
```

---

# Risk-State Crosswalk

## R-001 Host Boundary Bypass
Current state: `OPEN`

4D_b may reduce file-boundary bypass risk inside tested scope only.
4E may reduce network-egress risk inside tested scope only.
Neither closes host containment.

Allowed after 4E only if tests pass:
`REDUCED_WITHIN_EXPLICITLY_TESTED_SCOPE_ONLY`

Forbidden after 4E:
`CLOSED_EXACT_SCOPED_CLAIM_ONLY` for host containment.

---

## R-008 Sandbox Escape
Current state: `OPEN`

4E may reduce consequence of escape by limiting egress inside tested scope.
4E does not prove process isolation, host isolation, kernel boundary safety, or sandbox escape closure.

Allowed after 4E only if tests pass:
`REDUCED_WITHIN_EXPLICITLY_TESTED_SCOPE_ONLY`

Forbidden after 4E:
Any claim that sandbox escape is closed.

---

## R-031 9P/DrvFs Relay
Current state: `REDUCED_WITHIN_EXPLICITLY_TESTED_SCOPE_ONLY`

4D_b can reduce risk only for file I/O paths tested directly.
Full closure requires later fixture matrix and explicit 9P/DrvFs relay proof.

Allowed after 4D_b:
`REDUCED_WITHIN_EXPLICITLY_TESTED_SCOPE_ONLY`

Forbidden after 4D_b:
Broad closure of 9P/DrvFs relay risk.

---

## R-030 PC2->PC1 Write Path
Current state: `OPEN`

Single-PC testing cannot close dual-PC write-path risk.

Allowed after 4D_b/4E:
`OPEN`

Forbidden:
Any closure claim without dual-PC proof.

---

# Final Perfection Gate

4E may move forward only as scoped spec-prep if all of the following are true:

- 4D_b does not claim file-boundary closure beyond tested scope.
- 4E does not claim host containment beyond tested network-enforcement scope.
- Cross-layer closure is explicitly forbidden without separate proof.
- WFP negative tests are named.
- Minifilter negative tests are named.
- TCB boundary map exists.
- Recovery and rollback tests are first-class.
- Canary silent failure invalidates the run.
- Summaries are hash-bound to raw artifacts.
- Continuity proof is required for endurance language.
- Residual risk blocks closure claims.
- Reviewer failure modes are explicitly tested.
- Audit/spec/build authority classes are separate.

If any item above is missing, the correct status is:

```text
4E_SPEC_PREP_ALLOWED_WITH_BLOCKERS_RECORDED
```

not:

```text
BOUNDARY_PROVEN
M4_READY
PERFECT_PROGRESS
CLOSED
BUILD_AUTHORIZED
```

