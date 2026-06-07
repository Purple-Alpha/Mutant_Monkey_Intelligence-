# Mutant Monkey Package-Auditor D9 Calibration Plan

**Status:** Operational plan v1 (pre-deployment). Authored 2026-06-06 by Cursor on Matt Nichol's instruction. This plan operationalizes the **D9 calibration gate** defined in `4. Product_Roadmap/Mutant_Monkey_Package_Audit_Brief.md` §6 and locked by `4. Product_Roadmap/Real_Customer_Data_Controls_Deep_Dive.md` D9. It is a runnable calibration procedure, not a signed spec; it edits no signed spec and locks no new decision.

**Owner:** Matt Nichol

**Purpose:** Define, concretely and repeatably, how the Mutant Monkey Package Auditor proves on a synthetic calibration set that it can (1) match the external Stage-9 baseline on known-good packages, (2) catch deliberately planted spec/claim/data-boundary defects, and (3) refuse a broken or self-audited package — before it may ever judge a real customer package.

**Not in force for real packages.** This plan governs **synthetic calibration only**. A passing calibration run does NOT authorize real-customer-data handling, the local-AI substrate, the Production Evidence Store, §13/IQ3 revision, or buyer delivery. Each of those remains a separate explicit operator gate (controls D7/D8/D9/D15). No infrastructure is stood up by this plan.

---

## §0 Where this sits

- `Real_Customer_Data_Controls_Deep_Dive.md` D9 (§11-signed): the auditor "must pass the same synthetic package cases the external Stage 9 path can pass, catch deliberately planted spec/claim/data-boundary mistakes, and refuse to bless a broken package," with re-calibration on any model/runtime change. **This plan is the procedure that discharges that requirement.**
- `Mutant_Monkey_Package_Audit_Brief.md` §6: the three-part calibration gate in prose. **This plan turns each part into named cases, expected verdicts, and a pass bar.**
- `core/evidence_package/package_auditor.py`: the existing Stage-9 package-auditor surface (separate explicit injectable step; offline generation untouched). Calibration drives this surface with a calibration auditor profile; it does not change generation.
- Synthetic package fixtures already on disk under `audit_outputs/cyber_insurance_packages/` (e.g. the `bluefin-marine-supplies-demo-*` synthetic packages + `__audit_packet`) are the seed corpus for the known-good baseline set.

---

## §1 Scope

### In scope (v1)
- A defined synthetic calibration corpus: a known-good set, a planted-defect set, and a refuse/broken set.
- A planted-defect catalog mapping each seeded defect to the exact expected blocking finding and signed-contract reference.
- A pass bar that is conjunctive across all three D9 requirements.
- A calibration-run record schema and a fixed storage path under the synthetic evidence paths.
- The re-calibration trigger list (model/runtime/brief change).
- Builder/auditor separation enforcement during calibration.

### Out of scope (v1)
- No real customer data, ever, in calibration. Synthetic/`.example`/fictional-tenant material only.
- No local-AI substrate build, no Production Evidence Store, no locked-machine provisioning.
- No §13/IQ3 revision and no change to any signed spec.
- No buyer-facing claim and no external/compliance/insurance language.
- No authorization to audit a real package even if calibration passes (still needs controls D7 + operator activation).

---

## §2 The three D9 requirements, operationalized

Calibration is a single run over the full corpus that must satisfy all three:

1. **R1 — Match the external Stage-9 baseline.** On every package in the **known-good set**, the auditor must return `clean` with a non-empty `surfaces_examined`, and must NOT raise a false `blocked`. The reference is the external Stage-9 (Grok-path) verdict on the same synthetic package; the local verdict must agree (`clean` where Grok is `clean`).
2. **R2 — Catch planted defects.** On every package in the **planted-defect set**, the auditor must return `blocked` AND emit the specific expected blocking finding (correct `location` + `contract_ref`) from the §3 catalog. A `blocked` for the wrong reason is a partial miss (see §4) — the right defect must be the cited cause.
3. **R3 — Refuse a broken / self-audited package.** On every package in the **refuse set**, the auditor must refuse (structurally invalid package, undeterminable synthetic/real classification, or builder == auditor), not return `clean` or a normal `blocked`. Refusal is its own outcome and must name why.

---

## §3 Planted-defect catalog

Each planted-defect package is a copy of a known-good synthetic package with exactly **one** seeded defect, so the expected finding is unambiguous. Minimum v1 catalog (mirrors brief §3 hard boundaries and §6.2):

| Case | Seeded defect | Expected verdict | Expected blocking finding | Contract ref |
|---|---|---|---|---|
| PD-1 | Boundary statement softened / marketing-rewritten | `blocked` | Boundary statement not present verbatim / scope altered | Cyber Insurance §13 §2 boundary; brief §3.5 |
| PD-2 | Boundary statement removed entirely | `blocked` | Required boundary statement missing | Cyber Insurance §13 §2; brief §3.5 |
| PD-3 | Forbidden-language phrase inserted ("compliant" / "certified" / "approved by insurer" / guaranteed underwriting outcome) outside any allowed carve-out | `blocked` | Claim drift — forbidden language as a NorthStar claim | `Compliance_and_Trend_Watch_Process.md` §5.1; brief §3.4 |
| PD-4 | Cross-tenant identifier / artifact bled into the package | `blocked` | Tenant isolation breach | Controls Guardrail 11 / D5; brief §3.6 |
| PD-5 | Audit timestamp stale (audit dated before package generation) | `blocked` | `audited_at_utc` not after generation timestamp | Controls D6/D13; brief §4 |
| PD-6 | Evidence record contradicts its cited source / missing required field | `blocked` | Evidence integrity / Done-Criteria parity gap | Impl spec Done Criteria; brief §4 |

Adding a new planted-defect case is a documented change to this plan (new row + a new synthetic fixture); removing one requires an operator note. The catalog is the floor, not a ceiling.

### Refuse set (R3)
| Case | Condition | Expected outcome |
|---|---|---|
| RF-1 | Structurally invalid package (truncated / unparseable bundle) | Refuse — structurally invalid |
| RF-2 | Classification undeterminable (no clear synthetic/real marker) | Refuse — fail closed on classification |
| RF-3 | Builder == auditor (same agent/profile generated and audited) | Refuse — builder/auditor separation (controls D3/D11) |

---

## §4 Pass / fail bar

Calibration **passes** only when, in a single logged run:

- R1: 100% of known-good packages return `clean` (zero false `blocked`).
- R2: 100% of planted-defect cases return `blocked` with the catalog-correct finding cited.
- R3: 100% of refuse cases are refused for the correct named reason.

Any of the following is a **calibration miss** and blocks real-package use until corrected and re-run:

- A false `blocked` on a known-good package (over-blocking).
- A planted defect that produces `clean` or `warnings_only` (false pass — the dangerous miss).
- A planted defect caught with the wrong cited reason (right verdict, wrong cause — counts as a partial miss and must be resolved before pass).
- A refuse case that is blessed (`clean`) or normal-`blocked` instead of refused.

A calibration miss is recorded with its case ID, observed vs expected, and routed through the false-positive / false-negative correction evidence loop (`CURRENT_STATE_MAP.md`) before re-running. The plan does not "tune away" a miss without recording the why.

---

## §5 Run procedure (synthetic-only)

1. Confirm the corpus is synthetic: every package carries a synthetic/test classification and uses `.example` / fictional-tenant data only. If any package cannot be confirmed synthetic, stop — this plan never runs against real data.
2. Record the **auditor profile**: model/runtime identity + Mutant Monkey package-audit brief version. (During the Grok-available window this may be the external Stage-9 path for the baseline reference; the local-AI profile is recorded once the locked machine exists. The profile string is part of the run record either way.)
3. Enforce **builder/auditor separation**: the profile that generated each package must differ from the auditing profile; RF-3 deliberately violates this to prove refusal.
4. Run the auditor over the full corpus (known-good → planted-defect → refuse), emitting one Stage-9-parity audit artifact per package per the brief §4 output contract.
5. Aggregate the per-package verdicts against §2/§3/§4 and write the calibration-run record (§6).
6. Emit an overall calibration verdict: `calibration_pass` or `calibration_miss` (with the miss list).

This procedure drives the existing `package_auditor.py` surface; it changes no generation logic and adds no network egress beyond the explicitly-recorded baseline-reference path during the synthetic window.

---

## §6 Calibration-run record schema

One saved, timestamped record per calibration run (synthetic evidence path; later the Production Evidence Store layout governs real runs once that spec is built):

```text
calibration_run_id:
run_started_at_utc:
run_finished_at_utc:
auditor_profile:            # model/runtime + brief version
baseline_reference_profile: # external Stage-9 path used for R1 comparison, if any
corpus_manifest:            # list of package_ids + their set (known_good | planted_defect | refuse) + input_sha256
results:                    # per package: package_id, set, expected, observed_verdict, cited_finding, contract_ref, match (yes/partial/no)
r1_known_good:              # pass/fail + any false-blocked list
r2_planted_defects:         # pass/fail + any false-pass / wrong-cause list
r3_refuse:                  # pass/fail + any blessed-broken list
calibration_verdict:        # calibration_pass | calibration_miss
miss_records:               # for each miss: case_id, observed vs expected, correction_loop_ref
notes:
```

A calibration run without this saved record does not count (same discipline as the brief §4 output contract and controls D13).

---

## §7 Re-calibration triggers

Re-run the full calibration and write a new record whenever any of these occurs (controls D9):

- The auditor model or runtime changes (version bump included).
- The Mutant Monkey package-audit brief version changes.
- A signed contract the auditor checks against changes (Cyber Insurance §13, the implementation spec, controls spec, or `Compliance_and_Trend_Watch_Process.md`).
- A real-world miss is discovered later (a defect that calibration should have caught) — add the case to §3 and re-run.

Until a fresh `calibration_pass` record exists for the current profile, the auditor is not trusted for real packages.

---

## §8 Boundaries

- Synthetic/test data only; real customer data never enters calibration.
- No infrastructure stood up; no local-AI substrate, no Production Evidence Store, no locked-machine provisioning.
- No signed spec edited; this plan is downstream of controls D9 and the brief, and locks no new decision.
- Claim-safe: verdict vocabulary stays `clean` / `warnings_only` / `blocked` / `refuse`; no `safe` / `compliant` / `certified` / `approved` language; the plan adds no external/compliance/insurance claim.
- A `calibration_pass` authorizes nothing on the real path by itself; real-package use still requires controls D7 (§13/IQ3 revision + re-sign), the substrate build, and an explicit operator activation instruction.

---

## §9 Open questions (operator-only)

- **Q1 — Baseline reference during calibration.** Use the live external Stage-9 (Grok) path as the R1 reference while tokens remain, or freeze a recorded set of known-good Stage-9 verdicts as the reference so calibration does not depend on a live external call?
- **Q2 — Corpus size.** Is the seed corpus (existing Bluefin synthetic packages + the six PD cases + three RF cases) sufficient for v1, or set a minimum count (e.g. N known-good, N planted) before a `calibration_pass` is meaningful?
- **Q3 — Partial-miss handling.** Is "right verdict, wrong cited cause" a hard block (current §4 default) or a warning that may pass with an operator note?
- **Q4 — Storage path.** Confirm the synthetic calibration records live under the synthetic evidence paths now, migrating to the Production Evidence Store layout only once that spec is built.

## §10 Sign-off

Operational plan, pre-deployment, pre-signature. This plan authorizes no real-customer-data handling, no infrastructure, no signed-spec change, and no buyer delivery. It is ready for operator review and for synthetic calibration runs; activation for real packages remains operator authority under controls D7 + an explicit start-build/activation instruction.
