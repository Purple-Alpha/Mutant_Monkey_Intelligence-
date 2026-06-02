# Internal Testing Evidence Discipline — Deep Dive
**Status:** Pre-§11 draft. Authored 2026-06-01 by Cursor under operator instruction. §11 sign-off pending operator authorship; do not infer signature. §10 carries the direction recorded by tonight's stress test, the still-open questions, and the recommended staged cadence (Wave 0–Wave 4). No D-decisions are locked tonight. Pre-spec footing artifacts: `4. Product_Roadmap/Research_Inputs/Testing_Score_Sheet_Schema.md` and `4. Product_Roadmap/Research_Inputs/Testing_Plan_V1.md` remain the source of truth for the row schema until §11 of this deep-dive is signed.
**Authority:** Matt Nichol. Pre-§11 changes flow operator → spec edit → next gate. No implementation, D10, §13, client-facing copy, compliance, certification, insurer-approval, coverage, premium, or fraud-prevention authorization is granted by this draft.
---
## §0 Purpose
NorthStar accumulates evidence of its own learning by recording every meaningful test event in a single, scannable, internally-consistent shape. The discipline preserves the original failure or pass, names what was tested, records the outcome and the plain-English reason it mattered, classifies failure type when one exists, links any correction to retest evidence, and never weakens a test to make a failure disappear. Over time the accumulated record becomes the durable substrate for a future internal agent bible. This deep-dive formalizes the discipline already drafted in pre-spec form in the Testing Score Sheet Schema and Testing Plan V1.
This spec is a **discipline contract**, not a runtime implementation. It locks the row shape, the verdict and failure-type vocabulary, the authority model, the closure rules, the internal/external boundary, and the candidate-vs-evidence boundary for any future auto-derivation. It does not authorize a runtime score-sheet writer, candidate emitter, dashboard, portal, or client-facing render — those are future spec work per §10.
---
## §1 Scope
### §1.1 In scope
- The 13-column row contract (12 columns from the pre-spec footing plus a new `track` column).
- The closed `event_type`, `pass_fail`, `failure_type`, `recorded_by`, and `track` enums.
- The authority model for who authors and closes rows.
- The closure rules for `fail`, `pass`, `partial`, and `blocked` rows.
- The internal/external boundary: internal-only in v1.
- The single-canonical-ledger rule: one ledger surface; per-track scanning is filtered views over that surface, never separate ledger files.
- The candidate-vs-evidence boundary: future auto-derivation produces candidate rows under `audit_outputs/score_sheet_candidates/`; promotion to evidence requires operator review and explicit promotion. Promoted candidate files are renamed or moved to a `_promoted/` archive subfolder, never deleted.
- The relationship between this discipline and existing repo surfaces (`REACTION_TIMING_TEST_LOG.md`, eval reports under `core/scoring/eval/`, regression suites under `tests/`, `Email_Security_Testing_Evidence_Framework_Deep_Dive.md`, `audit_tools/decision_audit_runner.py`, `audit_tools/grok_audit_runner.py`, `audit_tools/pre_ship_audit.py`, `audit_tools/complete_gate.py`).
- The named failure modes the discipline must protect against.
- The audit requirements that make a row durable evidence rather than ad-hoc commentary.
### §1.2 Out of scope
- Implementation of any candidate-emit hook in any existing surface (`pre_ship_audit.py`, eval harness, regression suites, audit runners, etc.). Future spec work per §10 Wave 1 / Wave 2.
- Implementation of a `review_ledger.py` interactive review script. Future spec work per §10 Wave 3.
- Implementation of a no-PII / no-secrets pre-commit hook. Future spec work bundled with the review-script spec per §10 Wave 3.
- Modification of any §11-signed test contract or verdict floor (Phase 1.5 vendor-invoice recall floor, the rubric's lift-only invariant, TOAD D11 phrase-category vocabulary, FSL D9 floor, vendor-baseline TTL bounds, etc.).
- Replacement of `REACTION_TIMING_TEST_LOG.md` (timing-specific ledger; remains its own surface; flows into this discipline via `retest_evidence` pointers).
- Replacement of `Email_Security_Testing_Evidence_Framework_Deep_Dive.md` (verdict-match / failure-card framework; narrower scope; remains its own surface).
- Compliance, certification, insurer-approval, coverage-qualification, premium-reduction, or fraud-prevention claims in any context, including footnotes and seed examples.
- D10 (Cyber Insurance Evidence Package discovery) advance, §13 sign-off, or buyer-facing copy.
- Authorization for any LLM, network, or external-API call beyond what the operator has separately authorized.
- Per-track separate ledger files (explicitly rejected; per §3.2 single-canonical-ledger rule).
---
## §2 Locked Design Decisions
**Pre-§11. No D-decisions are locked tonight.** Verdict candidates from the 2026-06-01 7-axis stress test live in `think_sheet.md` under the entry titled "Sub-question stress test — Internal Testing Evidence Discipline §10 (2026-06-01)". §10 of this spec records the direction those verdict candidates point toward; promotion to D-decisions requires explicit operator instruction in a future session.
---
## §3 Row schema, single-canonical-ledger rule, candidate lifecycle
### §3.1 Column carry-forward and the `track` column addition
This deep-dive adopts the 12-column row schema verbatim from `4. Product_Roadmap/Research_Inputs/Testing_Score_Sheet_Schema.md` §4 and **adds a 13th column named `track`**. The full 13-column row is `test_id`, `event_type`, `what_was_tested`, `expected_outcome`, `actual_outcome`, `pass_fail`, `why_plain_english`, `failure_type` (nullable), `corrective_action` (nullable), `retest_evidence` (nullable), `recorded_at`, `recorded_by`, `track`.
Field rules and seed examples for columns 1–12 remain in the pre-spec schema doc until §11 of this deep-dive is signed. Once signed, this section becomes the source of truth and the schema doc receives a §11.x amendment recording the addition of `track`.
`track` is a **closed enum** with a single value or `cross_track`. The emitting tool (operator-authored or future auto-derivation) tags the row with its known track at row creation. Operator may re-tag during review. Cross-track rows must explicitly name the tracks touched in `why_plain_english` or in a parenthetical at the row's end. The exact closed taxonomy is §10 Q11 carry-forward; tonight's working set is in §4.
### §3.2 Single canonical ledger rule
The discipline maintains **one canonical evidence surface**, not per-track separate ledger files.
The canonical surface starts as schema-only (rows live as repo-resident artifact references inside the schema doc plus per-event linkage in `PROJECT_ACTIVITY_LOG.md`). Promotion to a dedicated ledger file is permitted only when row count justifies it AND operator explicitly authorizes it (§10 Q1 carry-forward).
Per-track scanability is preserved through **filtered views** over the canonical surface, not through separate files. A future tooling pass may produce per-track filter scripts; that tooling does not split the underlying evidence.
Per-track separate ledger files are a §8 named failure mode and are explicitly rejected.
### §3.3 Candidate lifecycle (auto-derivation boundary)
Future auto-derivation work (§10 Wave 1 / Wave 2 cadence) emits **candidate rows**, not evidence rows. Candidates live under:
`audit_outputs/score_sheet_candidates/`
The directory is gitignored (consistent with the rest of `audit_outputs/`). Candidates carry `recorded_by = AI-drafted` at emit time. They are not evidence until operator review promotes them.
The candidate lifecycle is:
1. **Created.** An emitting tool writes a candidate file (format locked at §10 Q12). Default `track` is set by the emitter based on its own scope.
2. **Reviewed.** Operator reads the candidate, edits `why_plain_english` and `corrective_action` to operator-authored content, and decides on promotion or deferral.
3. **Promoted.** Operator promotes by writing the row into the canonical ledger and changing `recorded_by` from `AI-drafted` to `operator-Matt + AI-drafted under operator review`. The candidate file is **renamed (suffix `_promoted_<UTC-timestamp>.yaml`) or moved to `audit_outputs/score_sheet_candidates/_promoted/`**, never deleted. The promoted ledger row carries a back-pointer to the archived candidate file.
4. **Deferred or rejected.** If a candidate is not promoted, it remains in the candidate folder until an explicit operator decision (close, re-emit, or archive). Stale-candidate rules are §10 Q3 carry-forward.
**Candidate files are never silently deleted.** Silent deletion is a §8.12 named failure mode.
### §3.4 Pre-spec → spec carry-forward
Field rules and seed examples remain in `Testing_Score_Sheet_Schema.md` until §11 of this deep-dive is signed. Once signed, the pre-spec schema doc is downgraded to historical reference plus a §11.x amendment recording the `track` column addition.
---
## §4 Vocabulary (closed enums)
Each enum is closed unless a future §11.x amendment expands it. Adding a value silently is a §8 named failure mode.
- **`event_type`**: `smoke`, `regression`, `adversarial`, `red_team`, `eval_subcategory`, `eval_full`, `live_diagnostic`, `live_runtime_case`, `calibration_observation`.
- **`pass_fail`**: `pass`, `fail`, `partial`, `blocked`. Mirrors `REACTION_TIMING_TEST_LOG.md`.
- **`failure_type`** (nullable): `false_negative`, `false_positive`, `expectation_contract`, `fixture`, `prompt`, `detector`, `workflow`, `schema_violation`, `scope_violation`, `calibration_observation`. Null only when the row is a clean pass and no calibration observation is being recorded.
- **`recorded_by`**: `operator-Matt`, `operator-Matt + AI-drafted under operator review`, `AI-drafted`. The bare `AI-drafted` value is the pending state; the row does not count as evidence until promotion.
- **`track`**: closed enum. Working set (operator-owned final taxonomy at §10 Q11): `inbox_shield_core`, `policy_pipeline`, `operator_state_kill_switch`, `sandbox_mutation`, `cyber_insurance_evidence_track`, `audit_infrastructure`, `threat_intel`, `cross_track`.
The relationship between `failure_type = calibration_observation` and `event_type = calibration_observation` is intentional: a successful run can carry calibration_observation as a failure_type even when its event_type is `live_runtime_case` or `eval_full`. The reverse — an event_type of `calibration_observation` — is reserved for events whose entire purpose is calibration, not pass/fail evaluation.
---
## §5 Authority model
- **Matt decides row closure.** Rubrics rank, scoring is advisory, AI-drafted rows are pending until operator review (`AGENTS.md` §2).
- **AI-drafted rows do not count as evidence.** They live in the working tree or candidate folder as drafts and become evidence only after the operator promotes the `recorded_by` value to one of the operator-bearing forms.
- **Candidate auto-derivation is input only.** Auto-derivation tools may emit candidate rows; they may not promote candidates to evidence, may not author `why_plain_english` as a closure rationale, may not author `corrective_action`, and may not touch `cer-*` correction-evidence linkage.
- **No row may weaken a test expectation.** Corrections must be scoped, proportionate, and retestable per the `CURRENT_STATE_MAP.md` correction-evidence-loop doctrine.
- **Authorship Rule.** AI does not author the operator's why-warranted rationale, the §11 signature line, or any operator-voiced closure narrative.
- **Decision-laundering boundary.** A row is evidence; it is not approval, sign-off, or authorization. Citing a closed row as approval outside an operator-authored decision record is a §8 named failure mode.
---
## §6 Closure rules
Reproduced and bound by reference from `Testing_Score_Sheet_Schema.md` §4.1 + `Testing_Plan_V1.md` §6:
- **`fail` rows** must either link to a correction-evidence record (`cer-*`) via `retest_evidence`, or explicitly state `open — no correction yet, see <reference>`.
- **`pass` rows** may carry `failure_type = calibration_observation` when the pass teaches something useful. The four candidate triggers from tonight's stress test (carry-forward; not D-locked): auth-pass under content risk; previously failing case now passing under retest; benign edge case staying quiet despite high inherent ambiguity; detector firing for the intended evidence reason rather than a coincident score.
- **`partial` rows** must name the missing field, output, or precondition. `partial` is not a softer pass.
- **`blocked` rows** must name the failed precondition (environment, dependency, missing fixture, missing key, operator stop) and, when later cleared, link forward to the row that proves the block was resolved.
- **Candidate rows** (auto-derivation output) follow the §3.3 candidate lifecycle. They are not subject to closure rules until promoted to evidence.
- A stale-row review trigger is §10 Q3 carry-forward.
---
## §7 Internal / external boundary
The discipline is **internal-only in v1**. No row in the canonical ledger or the candidate folder is buyer-facing, underwriter-facing, MSP-facing, or press-facing without a separate §11-signed disclosure spec.
External rendering of any score-sheet field requires:
1. A separate §11-signed disclosure deep-dive defining the abstraction layer per audience tier.
2. Operator §11 signature on that disclosure spec.
3. A pre-ship gate run on the rendering implementation.
The internal/external abstraction table sketched in `Testing_Score_Sheet_Schema.md` §6 is reference, not authorization.
Until that future spec exists, no field from a score-sheet row is authorized for rendering outside the repo's controlled-audit channels.
---
## §8 Named failure modes
Recognize and stop on these by name:
1. **Test-weakening drift.** Lowering the expected outcome to match the actual outcome after a failure.
2. **Pass-row calibration noise.** Recording every pass with a vague "nothing notable" calibration observation.
3. **Failure-row laundering.** Closing a `fail` row by reclassifying its expected outcome, event_type, or failure_type to make the failure look like something else.
4. **Authority drift.** AI-drafted rows being treated as evidence without operator promotion of `recorded_by`. Candidate-emit tools auto-promoting their own output is an authority-drift failure mode.
5. **Decision laundering.** Citing a closed row as approval, sign-off, certification, or authorization.
6. **Schema drift.** Silently changing column rules, enum values, required-field expectations, or the `track` taxonomy between rows or between sessions.
7. **Premature buyer-disclosure.** Treating internal rows as eligible for client-facing render without the §7 separate signed disclosure spec.
8. **Mismatch with §11-signed test floors.** Any row whose `corrective_action` lowers a §11-signed verdict floor.
9. **Forbidden-language slip.** Using compliance / certified / insurer-approved / policy / coverage / premium / fraud-prevention vocabulary in any free-text field outside an explicit `Forbidden-language drill` event_type.
10. **Naming collision.** Reusing a `test_id` across rows.
11. **Per-track ledger split.** Creating a separate ledger file per track instead of using filtered views over the single canonical ledger. Explicitly rejected by §3.2.
12. **Silent candidate deletion.** Deleting a candidate file from `audit_outputs/score_sheet_candidates/` without preserving it in the `_promoted/` archive subfolder or recording an explicit operator-authored close decision.
13. **PII / secrets / raw-payload contamination.** Any row containing personal information, secrets, raw payloads, or real tenant identifiers (fictional demos like `acme-industries-demo` and `bluefin-marine-supplies-demo` excepted).
14. **Auto-promotion drift.** A candidate-emit tool, an audit runner, or any automated surface writing the operator-bearing `recorded_by` value without an explicit operator-authored promotion act.
---
## §9 Audit requirements
A row counts as evidence only when **all** of the following are true:
1. **No PII / secrets / raw payloads / real tenant data.** Hard guard. Rows that contain personal information, API keys, passwords, tokens, raw email bodies, raw headers, real account / routing / IBAN / SWIFT numbers, or real (non-fictional) tenant identifiers are drafts, not evidence; they must be redacted in place. Deleting the row is itself a §8.12 failure mode. Compliance with this rule is the precondition for retention under §10 Q5.
2. All 13 columns are present (nulls allowed where §3.1 / pre-spec §4.1 permits).
3. Closed enums hold legal values from §4.
4. `recorded_at` is an ISO-8601 UTC timestamp.
5. `recorded_by` is in one of the two operator-bearing values, or the row is explicitly marked pending and lives in the candidate folder, not the canonical ledger.
6. `why_plain_english` is ≤ 280 characters and contains no raw payloads, no secrets, no real tenant identifiers, no chain-of-thought.
7. `retest_evidence` paths, when present, resolve to repo-resident files.
8. For `fail` rows, end-to-end inspectability is preserved: failure → why-warranted → correction → retest-evidence chain reconstructible from repo paths alone.
9. For `pass` rows with `failure_type = calibration_observation`, the calibration trigger matches one of the §6 closed list items (or a future-amended set).
10. `track` value is in the closed enum (or is `cross_track` with explicitly named tracks).
11. The row does not weaken any §11-signed test floor.
12. If the row was promoted from a candidate file, the candidate file exists in the `_promoted/` archive (or under its renamed-with-promoted-suffix form) and the row carries a back-pointer.
A row that fails any of the above is a **draft**, not evidence. Drafts may live in the tree but are excluded from any buyer-facing or audit-facing accounting.
---
## §10 Open questions and recommended staged cadence
This section carries (A) the direction recorded by tonight's 7-axis stress test as verdict candidates (NOT D-decisions), (B) questions still open for future stress-test → D-lockdown, and (C) the recommended staged cadence (Wave 0 through Wave 4).
The 7-axis stress test entries with full reasoning are in `think_sheet.md` under "Sub-question stress test — Internal Testing Evidence Discipline §10 (2026-06-01)". Tonight's session does not lock any verdict candidate as a D-decision and does not sign §11.
### §10.A — Direction recorded tonight (verdict candidates; not D-decisions)
- **Q1 (storage shape).** Single canonical ledger, schema-only initially, with required `track` column and per-track filtered views. Per-track separate ledgers explicitly rejected. Promotion to a dedicated ledger file is gated on row count + explicit operator authorization.
- **Q4 (calibration-observation triggers).** Closed list of four triggers — auth-pass under content risk; previously failing case now passing under retest; benign edge case staying quiet despite high inherent ambiguity; detector firing for the intended evidence reason rather than coincident score. Outside those triggers, pass rows record without calibration_observation.
- **Q5 (retention).** Permanent retention for compliant rows; rows that violate §9.1 PII / secrets / raw-payloads guard are drafts, not evidence; redact in place rather than delete. Index by year + event_type + track. Counsel review required before live client / underwriter / MSP data touches the surface.
- **Q7 (relationship to existing surfaces).** Score sheet is the canonical event-record surface; supersets `Email_Security_Testing_Evidence_Framework_Deep_Dive.md` without replacing it; flows from `REACTION_TIMING_TEST_LOG.md` via `retest_evidence` pointers; auto-derivation produces candidate rows only (per §3.3), never evidence rows.
- **Q10 (mandatory fields).** All 13 columns mandatory; nulls allowed where §3.1 / pre-spec §4.1 permit; `pending` is not a valid value for any field; per-event-type required-field map and per-track required-tag map are future amendments.
### §10.B — Still-open questions for future operator-authorized stress-test → D-lockdown
- **Q2.** Append authority lifecycle details — exact promotion semantics for the `recorded_by` value, audit-log entries on promotion, whether the operator-bearing value can ever revert.
- **Q3.** Stale-row review trigger N — tonight's stress-test proposed 60 days; not adopted as D-decision.
- **Q6.** External-render abstraction — tonight's direction is "v1 internal-only with future signed disclosure spec gate"; confirmation as a D-decision is deferred.
- **Q8.** Agent-bible relationship — substrate, sibling, or successor; tonight's direction is "substrate, with bible as separately authorized future sibling spec"; not D-locked.
- **Q9.** Schema-revision rule — tonight's direction is "§11.x amendment-block pattern with explicit MIGRATION-NOTE for any column or enum change"; not D-locked.
- **Q11.** `track` enum closed taxonomy — operator-owned; tonight's working set is in §4. Final taxonomy locked at Wave 1 spec or earlier.
- **Q12.** Candidate file format — YAML or JSON, exact field-by-field schema. Locked at Wave 1 spec.
- **Q13.** PII pre-commit hook scope — exact regex / pattern set, allowlist for fictional demo identifiers. Locked at Wave 3 spec.
### §10.C — Recommended staged cadence (Wave 0 → Wave 4)
| Wave | Scope | Authority required |
|---|---|---|
| **Wave 0 (tonight)** | Draft this deep-dive plus the 2026-06-01 stress-test entry in `think_sheet.md`. Gate the artifact packet only. **No §11 sign-off. No tracker entries in the same packet. No implementation.** | Authorized by tonight's operator instruction. |
| **Wave 1 (future session)** | (a) Operator §11 signs this deep-dive after stress-test → D-lockdown of §10.A and §10.B verdict candidates. (b) Draft `Score_Sheet_Candidate_Emit_Deep_Dive.md` covering candidate file format (Q12), first emitter (`audit_tools/pre_ship_audit.py`), candidate lifecycle, default `track` tagging by emitter, candidate folder pollution rule, full §10 stress test. Operator §11 on the candidate-emit spec. | Explicit operator authorization required. Not authorized tonight. |
| **Wave 2 (future session)** | Implement the candidate-emit hook in `audit_tools/pre_ship_audit.py` only. No other emitters. Tests + Grok audit + `complete_gate.py` + commit. | Explicit operator "start build" instruction required. Not authorized tonight. |
| **Wave 3 (future session)** | Draft `Score_Sheet_Interactive_Review_Deep_Dive.md` covering the `audit_tools/review_ledger.py` script behavior, append rules to canonical ledger, promotion semantics that preserve candidate files (no delete), and PII / no-secrets pre-commit hook contract (Q13). Operator §11. Then implement. | Explicit operator authorization for both spec and build. Not authorized tonight. |
| **Wave 4 (future sessions, gradual)** | Expand emitters to additional surfaces (`fraud_eval_harness`, `REACTION_TIMING_TEST_LOG.md`, `audit_tools/decision_audit_runner.py`, `audit_tools/grok_audit_runner.py`, etc.). Each new emitter is an amendment to the candidate-emit spec, not a new deep-dive. Aggregation rules per surface are part of each amendment. | Explicit operator authorization per emitter. Not authorized tonight. |
**Authority boundary tonight:** Wave 0 is the only authorized action. Waves 1 through 4 are future operator decisions. This spec records the recommended cadence; it does not authorize future waves.
---
## §11 Sign-off
**Pending operator authorship.** Do not infer, draft, or auto-fill.

