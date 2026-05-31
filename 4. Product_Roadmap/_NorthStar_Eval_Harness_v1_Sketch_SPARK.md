# NorthStar Eval Harness v1 — Sketch SPARK

**Status:** SPARK ONLY. Pre-spec. Unsigned. Not §11. Not implementation authorization. Not a build start. Not pricing. Not client-facing copy. Not a contract. Not a new required gate.
**Captured:** 2026-05-31 by Cursor (Claude Opus 4.7) at operator request, after commit `9e14f8a` (Email Security Testing & Evidence Framework §10 fully closed pre-§11).
**Architect:** Matt. The structure, scope, and direction of any future eval harness are Matt's to design.
**Purpose:** Preserve a *shape sketch* for the five surfaces the operator named in his 2026-05-31 today-list item 6 (fixture format, expected verdict, evidence bundle, failure card, precision/recall output) so the design decisions surface for a future spec pass, without committing to any of them.
**Authority gate:** All implementation work on the v1 eval harness remains gated on `4. Product_Roadmap/Email_Security_Testing_Evidence_Framework_Deep_Dive.md` §11 being signed **and** a separate explicit operator start-build instruction. This sketch does not satisfy either condition.

---

## What this SPARK is preserving

A bounded shape sketch for v1, anchored to the now-fully-resolved Email Security Testing & Evidence Framework draft. Five surfaces, drafted only to the level that lets a future spec pass critique them or replace them. Every surface here cites the framework D-decision it answers to; no new design decision is introduced.

This sketch is *not* a competing source of truth. If a surface here contradicts a framework D-decision after §11 signs, the framework wins. The sketch's value is exposing the shape so the gap between framework and implementation is visible before code starts.

---

## Surface 1 — Fixture format

**Anchored to:** D1 (four-value category status), D6 (v1 test-data sources), D7 (v1 implementation surface — synthetic-fixture eval harness wrapper).

**Proposed shape:** Per-case `.json` (one file per case), under `core/scoring/eval/fixtures/<category>/<case_id>.json`. Plain JSON, no YAML, no exotic format — matches existing `fraud_eval_dataset.jsonl` style except split per file for individual editability and per-case audit-trail correlation. JSONL aggregation is a derived artifact (concatenate the per-file JSONs at run time), not the source of truth.

Per-case fields (v1 minimum):

```text
case_id                  string, unique, stable
category                 string, must appear in capability registry (§6.2)
expected_status          one of {supported, not_supported_yet, not_present_in_sample}
                         (evidence_missing is run-time only, not fixture-authored)
expected_verdict         one of the five D2 values (legitimate / needs_review / high_risk /
                         blocked_or_hold_recommended / unknown)
fixture_source           string, repo-relative path to the .eml or synthetic input file
fixture_source_sha256    sha256 of the input file content
expected_signals[]       list of (signal_name, expected_value_or_predicate) — used by
                         §9.1 evidence-required validation
expected_categories[]    list of category names the case should fire on
adversarial_intent       optional string; required only for §4.3 adversarial fixtures
mission_id               optional string; required only for §4.4 red-team fixtures
red_team_mission_ref     optional repo-relative path; required only for §4.4 fixtures
authored_by              operator initials + UTC timestamp (no email, no PII)
notes                    optional string, capped at 600 chars
```

**Why JSON-per-case not JSONL-monolith:** v1 D7 calls for evidence-required validation and per-case failure cards. Per-file fixtures make case-level git history readable, let two cases be edited in parallel without merge conflict, and let `complete_gate.py` packets reference individual fixture changes without dragging the whole dataset.

**Open question for the spec pass:** does v1 keep `fraud_eval_dataset.jsonl` as a parallel concatenated view, or does it deprecate JSONL entirely? Sketch leans "keep both, JSONL is derived; JSONL stays as the regression-test input surface so existing `core/scoring/eval/` harness reads work unchanged."

---

## Surface 2 — Expected verdict

**Anchored to:** D2 (five-value verdict enum), D8 (verdict vocabulary aligned with `REACTION_TIMING_TEST_LOG.md`), D24 (`confidence_bucket` boundaries), D25 (`adjacent` strictly excluded from accuracy denominators).

**Proposed shape:** Per-case `expected_verdict` is a single string from the five-value enum. No multi-valued expected verdicts in v1. No "either A or B is acceptable" cases — if a case is genuinely ambiguous, the expected verdict is `needs_review` (which is the D2 middle band carrying that semantic). This keeps `verdict_match` from §7.3 binary in spirit: `exact` vs not-exact, with `adjacent` / `mismatch` / `unscored` providing the diagnostic detail.

**Per-case `verdict_match` computation (matches framework §7.3):**

```text
exact:     actual == expected
adjacent:  one step apart on the severity ladder
           (legitimate <-> needs_review)
           (needs_review <-> high_risk)
           (high_risk <-> blocked_or_hold_recommended)
mismatch:  two or more steps apart, or actual is `unknown` while expected is not
unscored:  case has evidence_missing or not_supported_yet-dominant categories
           (excluded from accuracy per D3)
```

**Confidence bucket per case (matches D12 / D24):** computed at run time from `actual_risk_score`:

```text
low:           risk_score in [0, 25]
medium:        risk_score in [26, 60]
high:          risk_score in [61, 100] AND verdict_match in {exact, adjacent}
overconfident: risk_score in [61, 100] AND verdict_match == mismatch
```

No additional thresholds, no continuous reliability score in v1 (D12 is explicit).

**Open question for the spec pass:** does the harness emit a per-case `confidence_calibration_delta` (actual_score minus the midpoint of the expected bucket) as a v1 diagnostic, or hold that for v1.1? Sketch leans "hold for v1.1" — the four-bucket distribution from §8.5 is already the v1 calibration surface.

---

## Surface 3 — Evidence bundle

**Anchored to:** D4 (evidence required for every score), D5 (no chain-of-thought), §9.1 (evidence bundle schema), D23 (Pydantic-as-source-of-truth).

**Proposed shape:** Per-case evidence bundle written by the harness to `audit_outputs/testing_framework/runs/<test_run_id>/cases/<case_id>/evidence_bundle.json`. Schema exactly matches §9.1; v1 implementation uses a Pydantic model `EvidenceBundle` whose JSON dump round-trips byte-for-byte through the model (D23).

Concrete v1 file layout per run:

```text
audit_outputs/testing_framework/runs/<test_run_id>/
  run_summary.json                  (top-level dashboard payload for this run)
  audit_trail.jsonl                 (append-only per §9.2)
  cases/
    <case_id>/
      evidence_bundle.json          (per §9.1)
      decision_path.json            (structured fields per §9.3 — NO raw LLM text)
      failure_card.md               (only present if case failed per §9.4)
      reviewer_notes.json           (only present if a reviewer note exists per §9.6)
```

**v1 size discipline:** every file on disk is plaintext, deterministic, and small. No binary evidence, no PDFs, no rendered HTML. If the future v1.1 adds rendering, rendered artifacts live alongside under a separate `rendered/` subdir; the source-of-truth files stay structured.

**Open question for the spec pass:** does v1 ship a `bundle_sha256` integrity field computed across the evidence bundle contents (per §9.1) at write time, and re-verify on every subsequent read? Sketch leans "yes for v1" — the §9.1 schema already lists `bundle_sha256` as the last field, and verifying on read is a 1-line cost.

---

## Surface 4 — Failure card

**Anchored to:** D9 (failure card mandatory before retest), D20 (failed-test acceptance is conjunctive), D29 (`decision_audit_candidate_id` linkage for `schema_violation` / `scope_violation`), §9.4 (failure card schema), §9.5 (retest loop).

**Proposed shape:** Markdown file `audit_outputs/testing_framework/runs/<test_run_id>/cases/<case_id>/failure_card.md`. Format exactly matches §9.4 with D29 linkage. Written by the harness automatically whenever the case meets the §9.4 failure trigger (verdict mismatch, overconfident bucket, or evidence missing).

v1 failure-card template (Markdown, populated by the harness with placeholders for operator-required fields):

```text
# Failure card — <case_id>

- Test run: <test_run_id>
- Case ID: <case_id>
- Failure type: <one of: verdict_mismatch, overconfident, evidence_missing,
                 schema_violation, scope_violation>
- Expected verdict: <expected>
- Actual verdict: <actual>
- verdict_match: <exact|adjacent|mismatch|unscored>
- Hypothesised root cause: <BLANK — operator-authored, capped 1200 chars>
- Affected capability registry entries: <auto-filled from case categories>
- Proposed fix scope: <BLANK — operator-authored>
- Decision: <one of: file_only, retest_required, spec_change_required,
             registry_demote_required>
- decision_audit_candidate_id: <nullable string; MUST be non-null when
                                failure_type ∈ {schema_violation, scope_violation}
                                per D29>
- Linked PR or commit: <BLANK — populated when fix lands>
- Retest record reference: <BLANK — populated when retest closes the loop>
- Signed off by / signed off at UTC: <BLANK — operator-only>
```

**v1 enforcement:** the harness writes the card on failure, then `audit_tools/pre_ship_audit.py` (the D22 enforcement authority) reads the card to apply the §9.4 + D20 conjunctive acceptance rule. If a failing case has no card, or the card is missing any of the D20 four required fields (recorded failure, classified failure type, signed operator acceptance, linked retest), the commit is blocked.

**Open question for the spec pass:** does v1 auto-populate the `Hypothesised root cause` field with a structured "first-pass diagnostic" (e.g., which detector was responsible based on `decision_path.json`), or leave it strictly operator-authored? Sketch leans "strictly operator-authored" — auto-filled diagnostic creates a Pass-1-wiring-bug-shaped risk where the operator signs off on a hypothesis the harness generated.

---

## Surface 5 — Precision / recall output

**Anchored to:** D3 (accuracy denominators supported-only), D14 (UDR first-class metric), D25 (strict accuracy exclusion of adjacent), D26 (0 pp regression default), D28 (no composite quality score), §8.5 (v1 dashboard metric set).

**Proposed shape:** Per-run `run_summary.json` (machine-readable) + `run_summary.md` (human-readable) at `audit_outputs/testing_framework/runs/<test_run_id>/`. Both surfaces emit exactly the §8.5 metric set; no composite score per D28.

v1 `run_summary.json` shape (sketch):

```text
{
  "test_run_id": <string>,
  "run_started_at_utc": <ISO-8601>,
  "run_finished_at_utc": <ISO-8601>,
  "tier": <one of: smoke, regression, adversarial, red-team>,
  "sample_size": <int>,
  "accuracy_supported_only": <float, 0-1>,
  "precision_per_verdict": {
    "legitimate": <float>,
    "needs_review": <float>,
    "high_risk": <float>,
    "blocked_or_hold_recommended": <float>,
    "unknown": <float>
  },
  "recall_per_verdict": { ... same shape as precision_per_verdict ... },
  "false_positive_rate": <float>,
  "false_negative_rate": <float>,
  "confidence_bucket_distribution": {
    "low": <int>,
    "medium": <int>,
    "high": <int>,
    "overconfident": <int>
  },
  "overconfident_case_list": [<list of case_ids>],
  "evidence_missing_case_count": <int>,
  "udr": <float>,
  "udr_new_failure_modes": [<list of names>],
  "capability_coverage": <float, 0-1>,
  "not_supported_yet_categories": [<list of category names>],
  "verdict_match_distribution": {
    "exact": <int>,
    "adjacent": <int>,
    "mismatch": <int>,
    "unscored": <int>
  },
  "regression_delta_vs_baseline": {
    "<subcategory_name>": <float, signed pp delta>
  },
  "regression_tolerance_violations": [
    {"subcategory": <name>, "delta_pp": <float>, "tolerance_pp": <float>,
     "operator_widening_ref": <nullable string>}
  ]
}
```

`run_summary.md` is a deterministic rendering of the same JSON — same field order, same labels, no narrative prose. The human-readable surface is one screen of plain Markdown so an operator or MSP can scan it without parsing JSON.

**Regression-tolerance enforcement (D26):** the harness reads the prior run's `run_summary.json` from the baseline path, computes per-subcategory delta, and fails the regression tier on any drop greater than the per-subcategory tolerance (default `0` pp). Any `regression_tolerance_violations` entry triggers a failure card per §9.4.

**Open question for the spec pass:** does v1 emit the `regression_delta_vs_baseline` against the most recent prior run or against a pinned baseline run? Sketch leans "pinned baseline run named in an audit-trail event," because most-recent-prior creates compounding-drift risk (each new run becomes the next baseline, so a slow slide goes undetected).

---

## What this sketch does NOT do

- **Does not authorize implementation.** Implementation requires both §11 signature on `Email_Security_Testing_Evidence_Framework_Deep_Dive.md` and a separate explicit operator start-build instruction. This sketch is neither.
- **Does not propose new D-decisions.** Every shape decision here cites an existing D-decision from the framework. The four open questions called out above are the ones the future spec pass must answer; this sketch leans on each but does not lock any.
- **Does not introduce a new schema authority.** D23 makes Pydantic models authoritative; this sketch follows that rule and does not propose an alternative.
- **Does not ship a composite score.** D28 forbids it; the sketch's `run_summary.json` is the multi-dimensional v1 surface, not a single number.
- **Does not change any existing artifact in `core/scoring/eval/`.** Sketch only describes a wrapping shape; the existing harness is unchanged.
- **Does not touch runtime code.** Nothing in this SPARK runs. Everything is text-on-disk in this document.
- **Does not pre-commit to dashboard rendering technology.** Rendering surface (Markdown, JSON, Cursor canvas, eventual portal) is explicitly out of scope per the framework §1.2; the sketch only defines metric shape.
- **Does not address Decision Auditor runner integration.** D29 locks trigger condition only; runner is v1.1 with its own §11-signed spec. Sketch does not propose runner shape.

---

## What the real spec would have to do beyond this sketch

If this SPARK becomes the seed for a future `Email_Security_Eval_Harness_v1_Deep_Dive.md`, that spec pass must additionally cover (this list is for spec-pass scoping, not implementation):

1. **Test-run identifier discipline.** Sketch uses `<test_run_id>` as a placeholder; the spec must lock its shape (UUID? operator-prefixed? timestamp + tier prefix?) and the rule for uniqueness across branches.
2. **Audit-trail event emission.** Sketch lists `run_summary.json` but does not specify which §9.2 events fire (`test_run_started`, `case_scored`, `test_run_finished`, etc.) on what conditions. Spec pass enumerates.
3. **Fixture promotion path.** Sketch describes per-case fixtures but not the operator-authorized promotion path from `audit_outputs/` candidate fixtures to `core/scoring/eval/fixtures/` permanent fixtures. Spec pass defines a single named promotion gate.
4. **Baseline-pinning mechanism.** Open question 5 (above) needs a locked answer with operator authorization recorded in `PROJECT_ACTIVITY_LOG.md`.
5. **Failure-card auto-population scope.** Open question 4 (above) needs a locked answer; if even partial auto-population is allowed, the spec pass enumerates exactly which fields and what evidence supports them.
6. **Integration with `audit_tools/pre_ship_audit.py`.** Sketch references D22 enforcement; spec pass must define the contract between the harness output (where `pre_ship_audit.py` reads) and the gate's verdict logic.
7. **Test-data fixture authorship discipline.** D6 locks five safe sources; the spec pass must lock how new fixtures pass the safety-source check at authoring time (pre-commit? gate-side? both?).
8. **§11 sign-off placeholder for the harness spec.** Same shape as the framework; only Matt signs.

---

## Why this is a SPARK, not a draft spec

A draft spec implies an intended §11 path. This SPARK does not. The framework is the §11-bound document; the harness implementation pattern is plumbing that the framework dictates. The right next move after the framework signs is to ask "do we even need a separate harness spec, or can the framework §10 + §9 + §8 be implemented directly?" The answer may be "no separate spec needed; just code against the framework." If so, this SPARK becomes the implementation note that gets archived once the v1 surface lands. If a separate spec is needed, this SPARK becomes its seed — but only by explicit operator direction.

Holding the work in SPARK form preserves the option without forcing it.

---

## Boundaries

- This SPARK does not decide.
- This SPARK does not replace the framework as source of truth on any contested point.
- This SPARK does not authorize a §11-revision cycle on the framework (the framework is still pre-§11 anyway; revision discipline only kicks in post-signature).
- This SPARK does not commit anything to client-facing wording or pricing.
- This SPARK does not authorize editing `core/scoring/eval/` or any runtime code.
- If a section of this SPARK conflicts with a future spec, the spec wins.
- If a section of this SPARK conflicts with the existing framework draft, the framework draft wins (and the conflict is a sketch bug to be fixed in a follow-up SPARK edit, not a framework revision).

---

## Named failure modes to avoid (project pattern)

- **Sketch-as-spec drift.** Treating this SPARK as if it were a signed spec is the failure mode the SPARK file-naming convention exists to prevent. The `_` prefix on the filename and the explicit "Status: SPARK ONLY" header up top are the structural reminders.
- **Pre-implementation lock-in.** Reading any of the open questions above as already-resolved is the failure mode that turns a sketch into accidental authority. Every "Sketch leans" phrase above is exactly that — a lean, not a lock.
- **Schema bypass.** Authoring fixtures or evidence bundles that do not round-trip through the Pydantic models (D23) creates a parallel schema. Avoid.
- **Composite-score creep.** Adding a single weighted score to `run_summary.json` because "buyers want one number" is the D28 failure mode. The §8.5 multi-dimensional surface is the contract; if buyer feedback later forces a composite, that is a §11-revision conversation.
- **Auto-populated failure-card root cause.** Sketch flagged the risk in surface 4 above; carry the warning into any spec pass.

---

## Index entry intent (for MASTER_INDEX.md)

When indexed, this SPARK should read as: pre-spec sketch of the v1 eval harness shape, gated entirely on the Email Security Testing & Evidence Framework §11 signature plus a separate operator start-build instruction; preserves five-surface shape (fixture, expected verdict, evidence bundle, failure card, precision/recall output) anchored to D1-D29 of the framework; introduces no new D-decisions; not a build authorization; not a §11 candidate of its own.

---

**End of SPARK. Sketch only. No decision implied.**
