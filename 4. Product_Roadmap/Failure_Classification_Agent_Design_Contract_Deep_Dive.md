# Failure Classification Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_64_FAILURE_CLASSIFICATION_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** DRAFT — UNSIGNED (Matt-authored contract text filed 2026-06-21; Cursor §5/§7 reconciliation applied; Grok pre-build gate clean `mmi_64_contract_gate_20260621T214737Z` 0/0; **not** §11; **not** build; **not** SIGNED_UNBUILT reconcile)

**Candidate:** #64 — Failure Classification

**Owner:** Matt Nichol

**Track:** BREADTH / Test-support (Layer 5 Challenge / Red-Team scoreboard row)

**Lane:** Agent Design Contract

**Authority repo:** `/home/socialarchitect/northstar`

**Implementation:** BLOCKED until §11 sign-off + reconcile to SIGNED_UNBUILT

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `4. Product_Roadmap/Test_Case_Generator_Agent_Design_Contract_Deep_Dive.md` (#61 sibling — generates tests)
- `4. Product_Roadmap/Regression_Test_Agent_Design_Contract_Deep_Dive.md` (#62 sibling — regression tests)
- `4. Product_Roadmap/Adversarial_Test_Agent_Design_Contract_Deep_Dive.md` (#63 sibling — adversarial tests)
- `4. Product_Roadmap/Email_Security_Testing_Evidence_Framework_Deep_Dive.md` (failure-analysis discipline context — not authority for taxonomy)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#64 Failure Classification)
- `audit_tools/complete_gate.py` (recorded gate-failure artifact producer)
- `scripts/mmi_authority_escalation_probe.py` (recorded authority-invariant breach producer)
- `scripts/mmi_contradiction_report.py` (recorded epistemic-drift report producer)
- `scripts/mmi_dispatch.py --verify` (recorded routing/drift verify failure producer)
- `VISION.md` (Stage A — analyze / recommend / evidence only)

**Proposed future build path (not authorized here):** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/sandbox/failure_classification_agent.py` (name TBD at build). No file is authorized until §11 signature.

---

## Agent Design Contract block

**Boundary:** #64 reads one **recorded failure record** and assigns a category + severity from a fixed taxonomy, each label traced to evidence in the record. It **never** decides what to do about the failure, fixes it, routes it, blocks anything, escalates, or recommends a next step.

| Field | Value |
|---|---|
| Agent name | Failure Classification Agent (`FailureClassificationAgent`) |
| Swarm inventory ID | #64 — Failure Classification |
| Canonical layer | 5 — Challenge / Red-Team (test-support classifier) |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed |
| Role | Read one recorded failure record; emit a taxonomy-bound classification (category + severity + evidence_ref + rationale) or `INPUT_INSUFFICIENT_CANNOT_CLASSIFY` |
| Boundary | Record-in, classification-out. No response, fix, re-run, routing, block decision, or governance writes |
| Inputs | One recorded failure record per Section 5 |
| Outputs | Section 6 `FAILURE_CLASSIFICATION` envelope, `INPUT_INSUFFICIENT_CANNOT_CLASSIFY`, or `UNCLASSIFIED` |
| Explicit non-authorities | No fix/retry/route/escalate/block; no remediation or re-execution; no live-traffic judgment; no invented category; no recommendation in rationale; no scoreboard/registry/state writes; no AUTH-5; no autonomous/background operation |

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-21 (draft placement only):

| Placeholder | Resolved value | Repo evidence |
|---|---|---|
| Upstream failure-record sources (recorded only) | (1) Grok gate artifacts under `audit_outputs/*.md` from `audit_tools/complete_gate.py` (`VERDICT: FAIL`, blocking lines, warnings); (2) focused `pytest` failure captures for agent wrapper suites (`tests/test_*_agent.py` stdout/stderr bundles passed in as record text — not live re-run by #64); (3) authority probe panic blocks from `scripts/mmi_authority_escalation_probe.py` (`AUTHORITY_INVARIANT_BREACH` envelope); (4) Tier 2C contradiction report stdout from `scripts/mmi_contradiction_report.py` (`REPORT_ONLY_FINDINGS` / `REVIEW_REQUIRED`); (5) dispatcher verify failure text from `scripts/mmi_dispatch.py --verify` (`VERDICT: FAIL` lines); (6) future handoff-integrity probe records when Lane 2 exists | Proven breadth lane artifacts (#61–#63 gates); MMI-DEC-082 authority probe; MMI-DEC-032 contradiction report; dispatcher verify discipline |
| Record shape at build time | Structured text envelope with at minimum: `failure_ref`, source path or record id, captured output body, optional source_kind tag (`gate` / `pytest` / `authority_probe` / `contradiction_report` / `dispatch_verify`) | Build must define parser against these live shapes; #64 does not invent fields |
| Downstream consumer (named) | **Operator review surface** (Matt) and **read-only PM Voice triage relay** (human chooses; PM Voice must not auto-act on classification); optional future internal triage log (stdout-only at build — no scoreboard/registry writes) | `scripts/mmi_pm_voice.py` advisory relay; proven pattern: human reads classification, operator decides response |
| Taxonomy vs repo failure types | `AUTHORITY_BOUNDARY` ← authority probe breach / forbidden AUTH-5 elevation text in record; `EPISTEMIC_DRIFT` ← contradiction report findings / artifact contradictions; `GATE_EVIDENCE_MISSING` ← GATED or complete claims without gate artifact reference in record; `CONTRACT_ALIGNMENT` ← contract/parser/Architect mismatch records; `HANDOFF_INTEGRITY` ← reserved for Lane 2 handoff probe records when present; `FUNCTIONAL` ← plain logic/assert failures; `REGRESSION` ← baseline-compare failure records (#62-shaped); `FLAKE` ← record must cite non-deterministic re-run evidence; else `UNCLASSIFIED` | Maps to live MMI + test-support surfaces without expanding authority |
| Email Security Testing failure cards | Long-horizon consumer named in scoreboard evidence; **not** a live parser input today — future structured failure-card envelope may extend Section 5 at a separate contract amendment | Scoreboard code evidence + `Email_Security_Testing_Evidence_Framework_Deep_Dive.md` context only |

Repo-reconciliation placeholders: **resolved for draft review.** §11 signature still required before build authorization.

---

## §0 Purpose — Executive Summary

The Failure Classification agent reads a recorded failure (a failed test, a gate failure, a
detected contradiction, a halted run) and assigns it a **category and severity** from a fixed,
declared taxonomy. It labels what kind of failure occurred; it does not decide what to do about
it, fix it, or judge whether it should block anything.

Input is a recorded failure record. Output is a classification (category + severity + the
evidence the label is drawn from). It names the failure; the operator and the normal signed
path decide the response.

Fits the test-support track alongside #61 (generates tests), #62 (regression tests), #63
(adversarial tests) — those produce/run checks; #64 *labels the failures they surface* so the
failures can be sorted and routed.

This contract is governance + draft placement only. It does not build runtime code, sign §11,
reconcile scoreboard lifecycle, or unlock AUTH-5.

---

## §1 Scope — Problem Statement

When a test fails, a gate fails, or a contradiction is detected, the raw failure is unsorted:
is it a flaky test, a real regression, an authority-boundary breach, a serialization-drift
anomaly, or a contract/Architect mismatch? Today that triage is manual and inconsistent. #64
makes it deterministic: it reads the failure and assigns a category and severity from a fixed
taxonomy, each label traced to the evidence in the failure record.

The critical boundary: classifying a failure and *responding* to it are two different acts. #64
does the first (label, with evidence) and is forbidden from the second (fix, route, block,
escalate, or decide). It tells you *what broke and how bad*; you decide what happens next.

### In scope
- Reading one recorded failure record.
- Assigning a category and severity from the fixed taxonomy (Section 6).
- Tracing each label to the evidence in the record.
- Returning the classification.

One failure record in, one classification out.

### Out of scope
- Deciding what to do about a failure (fix, retry, route, escalate, block).
- Repair, patch, or remediate the failure.
- Deciding whether a failure blocks a gate or build.
- Re-running the failed test or re-executing anything.
- Forming a verdict on live traffic/data or detecting anything itself.
- Inventing a category outside the declared taxonomy.
- Assigning a severity not grounded in the failure evidence.
- Writing to scoreboard, registry, state, governance files, or the failure record.
- Running autonomously or as a background process.
- Unlocking AUTH-5 or enabling registry-fed routing.

---

## §2 Locked Design Decisions

| ID | Decision |
|---|---|
| D1 | Record-in, classification-out; one failure record per invocation |
| D2 | Fixed category taxonomy (Section 6); no-match → `UNCLASSIFIED`, never guess |
| D3 | Fixed severity mapping grounded in record evidence; `AUTHORITY_BOUNDARY` → `CRITICAL` |
| D4 | Every label carries `evidence_ref`; ungrounded labels forbidden |
| D5 | Rationale is explanatory only — **no** recommendation, fix, or next-step language |
| D6 | Input is recorded failure text/envelope only — no implementation-code root-cause reads |
| D7 | Insufficient record → `INPUT_INSUFFICIENT_CANNOT_CLASSIFY` with named gap |
| D8 | Zero writes to governance/state/scoreboard/registry/failure record |
| D9 | Downstream consumer is human review + PM Voice relay; classification does not auto-route |

---

## §3 Inputs (Fixed)

Reads exactly one input:
- **A recorded failure record** — the evidence of a failure: failed-test output, gate-failure
  artifact, contradiction report, halt/panic log, with its identifiers and details.

Must **not** read: live traffic to form its own failure judgment, the implementation code to
guess at root cause beyond what the record states, research notes, or chat memory.

If the failure record lacks the evidence needed to classify →
`INPUT_INSUFFICIENT_CANNOT_CLASSIFY`, naming the gap. No guessed category.

---

## §4 Output — The Classification (fixed taxonomy)

Each classification:

```
FAILURE_CLASSIFICATION
id:               <unique id>
failure_ref:      <the failure record being classified>
category:         <one of the fixed taxonomy categories below>
severity:         <one of the fixed severity levels below>
evidence_ref:     <the evidence in the record that the label is drawn from>
rationale:        <plain statement of why this label, traced to evidence — no recommendation>
```

**Fixed category taxonomy (declared; reconciled against repo failure types in REPO_RECONCILIATION):**
- `FLAKE` — non-deterministic/transient failure (passes on identical re-run per record).
- `REGRESSION` — previously-passing behavior now failing.
- `AUTHORITY_BOUNDARY` — a failure touching an authority/escalation invariant.
- `EPISTEMIC_DRIFT` — contradiction / omission / serialization-anomaly between artifacts.
- `HANDOFF_INTEGRITY` — lost/duplicate/stale/misrouted handoff failure.
- `CONTRACT_ALIGNMENT` — contract vs. parser/Architect/implementation mismatch.
- `GATE_EVIDENCE_MISSING` — GATED/complete claim without backing evidence.
- `FUNCTIONAL` — a plain functional/logic failure not in the above classes.
- `UNCLASSIFIED` — evidence present but matches no declared category (flagged for human review).

**Fixed severity levels:**
- `CRITICAL` — touches an authority/safety invariant (e.g. AUTHORITY_BOUNDARY).
- `HIGH` — breaks a governance integrity property (drift, handoff, gate-evidence).
- `MEDIUM` — functional/regression failure with no governance-invariant impact.
- `LOW` — flake/transient.

**Hard classification rule:** every label (category + severity) must trace to evidence in the
failure record (`evidence_ref`). A label with no evidence basis is not assigned — the agent
emits `UNCLASSIFIED` rather than guessing. The `rationale` states why the label fits; it
contains **no** recommendation, fix, or next-step (that would cross into responding).

---

## §5 Flow Contract (what "flowing" means)

- **Input source (named):** recorded failure envelopes listed in REPO_RECONCILIATION (gate artifacts, pytest captures, authority probe breach blocks, contradiction report stdout, dispatch verify FAIL text).
- **Output format:** the Section 4 classification structure.
- **Downstream consumer (named):** operator review surface / read-only PM Voice triage relay (Matt chooses response; no auto-routing from classification).
- **"Flows" means:** the downstream consumer can consume the classification, every label traces
  to record evidence, and the output carries no response/decision — only the label.

---

## §6 Done Conditions (checkable)

- Given a failure record with sufficient evidence → produces a classification, each label
  traced to evidence, from the fixed taxonomy.
- Given insufficient evidence → `INPUT_INSUFFICIENT_CANNOT_CLASSIFY`, gap named.
- Given evidence matching no category → `UNCLASSIFIED`, flagged for human review.
- Assigns no category outside the taxonomy; no severity ungrounded in evidence.
- Emits no recommendation, fix, or next-step.
- Output matches Section 4; the consumer can consume it.
- Writes nothing; no governance/state/record mutation.
- Gate: `complete_gate.py 0/0` on functional + adversarial suites.

---

## §7 Gate Expectation

- Functional suite passes (correct labels from sample failure records).
- Adversarial suite passes (no invented-category path; no recommendation-emission path; no
  fix/remediation path; no re-execution path).
- `complete_gate.py 0/0` before GATED.
- Runs the proven breadth lane: build → AWAITING_AUDIT → Grok gate → GATED.

---

## §8 Out-of-Scope Boundaries (carried into blueprint)

- No response, fix, retry, route, escalate, or block decision.
- No remediation or repair.
- No block/gate decision.
- No re-execution.
- No live-traffic judgment or self-detection.
- No category outside the taxonomy; no ungrounded severity.
- No recommendation in the rationale.
- No state/scoreboard/registry/governance/record writes.
- No AUTH-5, no autonomous/background operation.

---

## §9 Security & Authority Risks

- **Response-creep (primary risk):** a classifier starts recommending or applying fixes.
  Mitigation: Section 1 + Section 4 hard rule — label only, rationale carries no next-step;
  adversarial test for any recommendation/fix path.
- **Severity inflation/deflation:** mislabels severity to influence what gets prioritized.
  Mitigation: severity is grounded in evidence + fixed mapping (AUTHORITY_BOUNDARY→CRITICAL etc.);
  adversarial test for ungrounded severity.
- **Invented category:** assigns a label outside the taxonomy. Mitigation: fixed taxonomy;
  no-match → `UNCLASSIFIED`, never a guess.
- **Root-cause overreach:** reads implementation to guess causes beyond the record. Mitigation:
  input is the recorded failure only; reading code to infer is a violation.
- **Authority-failure mishandling:** an AUTHORITY_BOUNDARY failure is the most sensitive class —
  the agent must label it CRITICAL and stop, never suggest how to "resolve" it. Mitigation:
  fixed mapping + no-recommendation rule.

---

## §10 Falsifiable Acceptance Tests

- **T1 — Evidence-traced:** every label carries an evidence_ref to the failure record.
- **T2 — Taxonomy-bound:** no category outside the fixed taxonomy; no-match → `UNCLASSIFIED`.
- **T3 — Grounded severity:** severity follows the fixed mapping and the record; never inflated/deflated.
- **T4 — Insufficient input:** missing evidence → `INPUT_INSUFFICIENT_CANNOT_CLASSIFY`.
- **T5 — No response:** output contains no fix/retry/route/escalate/block/recommendation.
- **T6 — No remediation/re-execution:** the agent never repairs or re-runs anything.
- **T7 — No root-cause overreach:** never reads implementation beyond the record to infer cause.
- **T8 — Consumable output:** the consumer can consume the Section 4 structure.
- **T9 — Zero writes:** no state/scoreboard/registry/governance/record mutation. Verified before/after.
- **T10 — Authority-failure handling:** an AUTHORITY_BOUNDARY failure is labeled CRITICAL with
  no suggested resolution.

A build is admissible for sign-off only if T1–T10 all pass.

---

## §11 What Must Not Be Built

- No response/fix/retry/route/escalate/block logic.
- No remediation or re-execution.
- No block/gate decision.
- No live-traffic judgment or self-detection.
- No category outside the taxonomy; no ungrounded severity.
- No recommendation in output.
- No state/governance/record writes.
- No AUTH-5, no autonomous/background operation, no registry-fed routing.

---

## §12 Matt §11 Signature Block

```
§11 SIGN-OFF — MMI_64_FAILURE_CLASSIFICATION_AGENT_DESIGN_CONTRACT

I, Matt Nichol, have reviewed this Agent Design Contract draft for #64.

[ ] I approve this contract as written.
[ ] I authorize gate (Grok pre-build review).
[ ] On clean gate, I §11-sign and authorize reconcile to SIGNED_UNBUILT.

Confirmed: #64 CLASSIFIES failures from recorded evidence; it never responds, fixes, routes,
blocks, escalates, or recommends. Label only.
[ ] yes

Fixed taxonomy (categories + severities, Section 4) is correct as written:
[ ] yes  [ ] revise: _______________________________

Upstream failure-record source + downstream consumer reconciled against repo:
[x] yes (Cursor reconcile 2026-06-21 — draft record only)  [ ] pending

Signature: ____________________________
Date:      ____________________________
Commit:    ____________________________
```

---

## §13 Non-Authority Footer

```
This is a CONTRACT DRAFT — UNSIGNED. It is not authority.
No §11 sign-off. No build. No SIGNED_UNBUILT reconcile. No state mutated.
#64 labels recorded failures only; it never responds, fixes, routes, blocks, escalates, or recommends.
Classification output does not auto-route work; Matt chooses all responses.
AUTH-5 remains blocked. Human authority held throughout.
```
