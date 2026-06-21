# Regression Test Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_62_REGRESSION_TEST_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** DRAFT — UNSIGNED (Claude draft relayed by Matt 2026-06-21; Cursor repo reconciliation applied). Evidence Stage 1 (Synthetic) agent wrapper only when §11-signed. **No build**, **no scoreboard reconcile**, **no Blueprint-of-Record population**, **no registry/default dispatch**, **no AUTH-5**.

**Candidate:** #62 — Regression Test

**Owner:** Matt Nichol

**Track:** BREADTH / Test-support (Layer 5 Challenge / Red-Team scoreboard row)

**Authority repo:** `/home/socialarchitect/northstar`

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `4. Product_Roadmap/Test_Case_Generator_Agent_Design_Contract_Deep_Dive.md` (#61 sibling — new-requirement tests vs regression)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#62 Regression Test)
- `audit_outputs/` (recorded prior-verified behavior — completion gate artifacts)
- `mmi/MMI_DECISION_LOG.md` (recorded gate outcomes with commit hashes)
- `audit_tools/complete_gate.py` (downstream completion gate consumer)
- `VISION.md` (Stage A — analyze / recommend / evidence only)

**Proposed future build path (not authorized here):** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/sandbox/regression_test_agent.py` (name TBD at build). No file is authorized until §11 signature.

---

## Agent Design Contract block

**Boundary:** #62 generates regression test cases from one target's **signed** contract plus **recorded prior-verified behavior**. It does **not** run tests, judge pass/fail or regression-vs-intended-change, detect threats, score, build the target agent, use current implementation as baseline, or write governance/state.

| Field | Value |
|---|---|
| Agent name | Regression Test Agent (`RegressionTestAgent`) |
| Swarm inventory ID | #62 — Regression Test |
| Canonical layer | 5 — Challenge / Red-Team (test-support generator) |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed |
| Role | Read target §11-signed contract + recorded prior-verified baseline; emit regression cases traceable to real baseline evidence only |
| Boundary | Contract + recorded-baseline in, regression-cases-out. No execution, no evaluation, no current-code baseline, no invented baseline |
| Inputs | Target §11-signed contract at `4. Product_Roadmap/<Target>_Agent_Design_Contract_Deep_Dive.md` + recorded prior-verified behavior from `audit_outputs/<task_id>_*.md` (0/0 gate) and/or `mmi/MMI_DECISION_LOG.md` gate records with commit hash |
| Outputs | Structured regression-case set per Section 6 envelope, or `NO_BASELINE_CANNOT_GENERATE_REGRESSION` with named gaps |
| Explicit non-authorities | No test execution; no pass/fail or regression verdict; no current implementation as baseline; no scoreboard/registry/state writes; no AUTH-5; no autonomous/background operation |

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-21 (draft placement only):

| Placeholder | Resolved value | Repo evidence |
|---|---|---|
| Target contract source | `4. Product_Roadmap/<Target>_Agent_Design_Contract_Deep_Dive.md` — scope + `## BUILD CONDITIONS` | Sibling contracts (#47, #52, #61) |
| Prior-verified baseline source | `audit_outputs/<task_id>_<timestamp>Z.md` with `blocking=0` / `warnings=0` (Grok completion gate); cross-check `mmi/MMI_DECISION_LOG.md` MMI-DEC-* gate records naming artifact path + commit hash; scoreboard GATED row gate citation | #61 `test_case_generator_20260621T080345Z.md` + MMI-DEC-063; #52 `plain_english_explanation_20260621T061124Z.md` + MMI-DEC-055/056 |
| Baseline anti-pattern (forbidden) | Current target implementation modules under `core/` — never the baseline | Contract D3 / Section 5 hard rule |
| Downstream consumer | Focused `pytest` suite for target wrapper + `audit_tools/complete_gate.py --task <task_id>` | Proven breadth lane (#47, #52, #61) |
| Distinction from #61 | #61 derives tests from contract requirements; #62 derives regression cases from **recorded** prior-verified outcomes only | #61 `TestCaseGeneratorAgent` contract |

Repo-reconciliation placeholders: **resolved for draft review.** §11 signature still required before build authorization.

---

## §0 Purpose

Unblock swarm #62 Regression Test by placing the Agent Design Contract the MMI crew expects at this path. The agent protects already-verified behavior from silent regression by generating cases pinned to real recorded baselines — without executing tests or using current code as the baseline.

This contract is governance + draft placement only. It does not build runtime code, sign §11, reconcile scoreboard lifecycle, or unlock AUTH-5.

---

## §1 Scope

### In scope
- Generating regression test cases from one target's signed contract + recorded prior-verified baseline per run.
- Traceability: every regression case maps to a named prior-verified behavior with `baseline_ref` to real evidence.
- `NO_BASELINE_CANNOT_GENERATE_REGRESSION` when no recorded baseline exists.

### Out of scope
- Running or evaluating tests (pytest/gate are separate consumers).
- Using current implementation source as the baseline.
- Inventing baselines or regression cases without recorded evidence.
- Deciding regression vs. intended change on a failing test (operator's call).
- Building or modifying the target agent.
- Scoreboard/registry/state/governance writes.
- AUTH-5, autonomous operation, default registry, production dispatch.

---

## FLOW CONTRACT

| Field | Value |
|---|---|
| upstream_input | Target §11-signed contract + recorded prior-verified baseline |
| contract_input | `4. Product_Roadmap/<Target>_Agent_Design_Contract_Deep_Dive.md` |
| baseline_input | `audit_outputs/<task_id>_<timestamp>Z.md` (0/0) + `mmi/MMI_DECISION_LOG.md` gate record + scoreboard GATED citation |
| output_location | Stdout / in-memory structured regression-case set returned to explicit caller or test harness only at Stage 1 |
| output_format | Section 6 `REGRESSION_CASE` structure |
| downstream_consumer | Target-agent focused `pytest` module under `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/` + `audit_tools/complete_gate.py` |
| consumer_usage | pytest executes generated regression cases against the target wrapper; completion gate audits the implementation slice before GATED |
| insufficient_output | `NO_BASELINE_CANNOT_GENERATE_REGRESSION` — no recorded prior-verified behavior; names gaps; emits no regression cases |

---

## TWO-OUTPUT ENVELOPE

### Regression-case envelope

```text
REGRESSION_CASE
id: <unique id>
protects: <prior-verified behavior / done-condition guarded>
baseline_ref: <audit_outputs artifact path and/or MMI-DEC commit record>
input: <deterministic test input>
expected: <outcome that must continue to hold>
type: <behavior-preservation | invariant-hold>
```

**Hard rule:** every `REGRESSION_CASE` must map to a **recorded** prior-verified behavior with a real `baseline_ref`. No invented baseline.

### Refusal envelope

```text
NO_BASELINE_CANNOT_GENERATE_REGRESSION
gaps:
- <named gap>
WHY:
No recorded prior-verified behavior exists to protect; regression cases cannot be invented.
BOUNDARY:
advisory only; no regression cases emitted; no execution; no AUTH-5
```

---

## BUILD CONDITIONS

- CHECK: file_exists: 4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md
- CHECK: path_exact: target contract path resolves under `4. Product_Roadmap/` with `Agent` and `Design_Contract` in filename
- CHECK: baseline_source_named: audit_outputs completion gate artifacts with 0/0 + MMI-DEC gate records
- CHECK: field_present: target contract `## BUILD CONDITIONS` with at least one `CHECK:` line
- CHECK: command_expect: pytest focused suite for target wrapper passes when regression cases supplied|exit_code=0
- CHECK: consumer_named: complete_gate.py
- CHECK: sentinel_exact: NO_BASELINE_CANNOT_GENERATE_REGRESSION
- CHECK: invariant_present: every generated REGRESSION_CASE has baseline_ref to recorded evidence — no invented baseline
- CHECK: invariant_present: generator never uses current target implementation modules as baseline

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

- **D1 — Identity.** Regression Test is Layer 5 Challenge/test-support, Authority L3, Stage A, Evidence Stage 1 at signing.
- **D2 — Recorded baseline only.** Baseline is prior-verified gate artifacts / MMI records — never current implementation code.
- **D3 — Generate only.** No execution, no pass/fail judgment, no regression-vs-intended verdict.
- **D4 — Traceability.** Every regression case maps to a recorded prior-verified behavior with `baseline_ref`.
- **D5 — Refusal on missing baseline.** No recorded baseline → `NO_BASELINE_CANNOT_GENERATE_REGRESSION`, never guessed baselines.
- **D6 — Zero writes.** No scoreboard/registry/state/governance mutation at Stage 1.
- **D7 — No autonomy / AUTH-5 blocked.**
- **D8 — Distinct from #61.** #61 generates new-requirement tests from contract; #62 protects recorded verified behavior only.

---

## §5 Failure modes

- **Invented-baseline drift** — regression cases against assumed state. Mitigation: D5 refusal + baseline_ref hard rule.
- **Self-certifying baseline** — current code defines "correct." Mitigation: D2 forbidden read path.
- **Execution creep** — agent runs regression tests. Mitigation: D3 generate-only boundary.
- **False regression authority** — agent declares intended vs. regression. Mitigation: operator decides on failure; #62 flags divergence only.

---

## §6 Required tests

Focused wrapper tests must prove:

1. Baseline-traced generation — every case has `baseline_ref` to real recorded evidence (T1).
2. No invented baseline — absent recorded baseline → `NO_BASELINE_CANNOT_GENERATE_REGRESSION` (T2).
3. Not self-certifying — never uses current implementation as baseline (T3).
4. No execution path (T4).
5. No regression verdict path (T5).
6. Consumable output structure for pytest harness (T6).
7. Zero governance/state writes (T7).
8. Each recorded prior-verified behavior yields at least one regression case when checkable (T8).

---

## §10 Open questions

1. Single-target vs operator-selected target manifest per run (fixed like Architect vs. explicit selection).
2. Whether regression cases persist to disk in Stage 1 or stdout/in-memory only.
3. Formal `task_id` naming for `complete_gate.py` when #62 itself is gated.

---

## §11 Sign-off

**§11 UNSIGNED — draft placement only.**

- [ ] I approve this contract as written.
- [ ] I authorize Grok pre-build gate review (Codex lane).
- [ ] On clean gate, I §11-sign and authorize reconcile to SIGNED_UNBUILT.

Confirmed: #62 generates regression tests from recorded verified behavior; it never runs, judges, or builds; operator decides regression vs. intended change.

Upstream contract + recorded-baseline source + downstream test-runner reconciled against repo:
- [x] yes (Cursor reconcile 2026-06-21)
- [ ] pending operator review

Signature: ____________________________

Date: ____________________________

Commit: ____________________________
