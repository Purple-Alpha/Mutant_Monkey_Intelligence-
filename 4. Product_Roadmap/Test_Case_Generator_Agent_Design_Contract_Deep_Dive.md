# Test Case Generator Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_61_TEST_CASE_GENERATOR_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** DRAFT — UNSIGNED (Claude draft relayed by Matt 2026-06-21; Cursor repo reconciliation applied). Evidence Stage 1 (Synthetic) agent wrapper only when §11-signed. **No build**, **no scoreboard reconcile**, **no Blueprint-of-Record population**, **no registry/default dispatch**, **no AUTH-5**.

**Candidate:** #61 — Test Case Generator

**Owner:** Matt Nichol

**Track:** BREADTH / Test-support (Layer 5 Challenge / Red-Team scoreboard row)

**Authority repo:** `/home/socialarchitect/northstar`

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#61 Test Case Generator)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/sandbox/red_agents/` (existing synthetic case generators — reference patterns only, not authority for target behavior)
- `audit_tools/complete_gate.py` (downstream completion gate consumer for generated-case verification lanes)
- `VISION.md` (Stage A — analyze / recommend / evidence only)

**Proposed future build path (not authorized here):** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/sandbox/test_case_generator_agent.py` (name TBD at build). No file is authorized until §11 signature.

---

## Agent Design Contract block

**Boundary:** #61 generates structured test cases from one target agent's **signed** Agent Design Contract. It does **not** run tests, judge pass/fail, detect threats, score, build the target agent, read target implementation code, or write governance/state.

| Field | Value |
|---|---|
| Agent name | Test Case Generator Agent (`TestCaseGeneratorAgent`) |
| Swarm inventory ID | #61 — Test Case Generator |
| Canonical layer | 5 — Challenge / Red-Team (test-support generator) |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed |
| Role | Read one target's §11-signed Agent Design Contract; emit deterministic test cases (input + expected outcome) traceable to contract `CHECK:` / required-test clauses only |
| Boundary | Contract-in, test-cases-out. No execution, no evaluation, no implementation-code reads, no invented tests beyond contract requirements |
| Inputs | One target §11-signed Agent Design Contract on disk at `4. Product_Roadmap/<Target>_Agent_Design_Contract_Deep_Dive.md` with parseable `## BUILD CONDITIONS` (`CHECK:` lines) and `## §6 Required tests` (or equivalent required-tests section) |
| Outputs | Structured test-case set per Section 6 envelope, or `INPUT_INSUFFICIENT_CANNOT_GENERATE` with named gaps |
| Explicit non-authorities | No test execution; no pass/fail judgment; no target code reads; no scoreboard/registry/state writes; no AUTH-5; no autonomous/background operation |

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-21 (draft placement only):

| Placeholder | Resolved value | Repo evidence |
|---|---|---|
| Target contract source | `4. Product_Roadmap/<Target>_Agent_Design_Contract_Deep_Dive.md` — `## BUILD CONDITIONS` (`CHECK:` lines) + required-tests section | Sibling contracts (#52, #47, #48) use `## BUILD CONDITIONS` with `CHECK:` prefixes; Architect Mode A parser expects this shape |
| Done-condition basis | `CHECK:` lines and §6 required-tests clauses in the target contract — not target implementation code | Template + #52 `BUILD CONDITIONS` pattern |
| Downstream consumer | Focused `pytest` suite for the target agent wrapper + `audit_tools/complete_gate.py --task <task_id>` | Proven breadth lane (#47, #52): build → tests → AWAITING_AUDIT → Grok gate → GATED |
| Reference artifact (non-authority) | `core/sandbox/red_agents/` synthetic generators | Scoreboard #61 evidence surface; patterns only — tests derive from **contract**, not generator code |

Repo-reconciliation placeholders: **resolved for draft review.** §11 signature still required before build authorization.

---

## §0 Purpose

Unblock swarm #61 Test Case Generator by placing the Agent Design Contract the MMI crew expects at this path. The agent closes the gap between a target's signed contract done-conditions and the deterministic test cases that prove them — without executing tests or reading implementation code.

This contract is governance + draft placement only. It does not build runtime code, sign §11, reconcile scoreboard lifecycle, or unlock AUTH-5.

---

## §1 Scope

### In scope
- Generating structured test cases from one target's signed contract per run.
- Traceability: every test case maps to a named contract done-condition or required-test clause.
- `INPUT_INSUFFICIENT_CANNOT_GENERATE` when the target contract lacks checkable conditions.

### Out of scope
- Running or evaluating tests (pytest/gate are separate consumers).
- Reading target implementation source to derive tests.
- Inventing tests for behavior the contract never specified.
- Building or modifying the target agent.
- Scoreboard/registry/state/governance writes.
- AUTH-5, autonomous operation, default registry, production dispatch.

---

## FLOW CONTRACT

| Field | Value |
|---|---|
| upstream_input | Target §11-signed Agent Design Contract at `4. Product_Roadmap/<Target>_Agent_Design_Contract_Deep_Dive.md` |
| input_fields | `## BUILD CONDITIONS` (`CHECK:` lines); `## §6 Required tests` (or equivalent required-tests section) |
| output_location | Stdout / in-memory structured test-case set returned to explicit caller or test harness only at Stage 1 |
| output_format | Section 6 `TEST_CASE` structure (id, derives_from, input, expected, type) |
| downstream_consumer | Target-agent focused `pytest` module under `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/` + `audit_tools/complete_gate.py` |
| consumer_usage | pytest executes generated or generator-emitted cases against the target wrapper; completion gate audits the implementation slice before GATED |
| insufficient_output | `INPUT_INSUFFICIENT_CANNOT_GENERATE` — target contract lacks checkable done-conditions; names gaps; emits no test cases |

---

## TWO-OUTPUT ENVELOPE

### Test-case envelope

```text
TEST_CASE
id: <unique id>
derives_from: <contract CHECK line or required-test clause>
input: <deterministic test input>
expected: <deterministic expected outcome>
type: <functional | edge | negative>
```

**Hard rule:** every `TEST_CASE` must map to a specific contract requirement. No invented tests.

### Refusal envelope

```text
INPUT_INSUFFICIENT_CANNOT_GENERATE
gaps:
- <named gap>
WHY:
Target contract lacks checkable done-conditions required to derive tests.
BOUNDARY:
advisory only; no test cases emitted; no execution; no AUTH-5
```

---

### Out of scope

- Test execution or pass/fail evaluation.
- Reading target implementation code.
- Invented tests beyond contract requirements.
- Detection/scoring/verdict logic.
- State/scoreboard/registry/governance writes.
- AUTH-5, autonomous/background operation.

---

## BUILD CONDITIONS

- CHECK: file_exists: 4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md
- CHECK: path_exact: target contract path resolves under `4. Product_Roadmap/` with `Agent` and `Design_Contract` in filename
- CHECK: field_present: target contract `## BUILD CONDITIONS` with at least one `CHECK:` line
- CHECK: field_present: target contract required-tests section (`## §6 Required tests` or equivalent)
- CHECK: command_expect: pytest focused suite for target wrapper passes when cases supplied|exit_code=0
- CHECK: consumer_named: complete_gate.py
- CHECK: sentinel_exact: INPUT_INSUFFICIENT_CANNOT_GENERATE
- CHECK: invariant_present: every generated TEST_CASE derives_from a named contract clause — no invented tests
- CHECK: invariant_present: generator never reads target implementation modules — contract-only input

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

- **D1 — Identity.** Test Case Generator is Layer 5 Challenge/test-support, Authority L3, Stage A, Evidence Stage 1 at signing.
- **D2 — Contract-only input.** Tests derive from the target's signed contract, never from target implementation code.
- **D3 — Generate only.** No execution, no pass/fail judgment, no gate substitution.
- **D4 — Traceability.** Every test case maps to a contract `CHECK:` or required-test clause.
- **D5 — Refusal on thin input.** Missing checkable conditions → `INPUT_INSUFFICIENT_CANNOT_GENERATE`, never guessed tests.
- **D6 — Zero writes.** No scoreboard/registry/state/governance mutation at Stage 1.
- **D7 — No autonomy / AUTH-5 blocked.**

---

## §5 Failure modes

- **Invented-test drift** — tests for behavior the contract never specified. Mitigation: Section 6 hard rule + adversarial suite.
- **Code-reading leak** — derives tests from implementation (circular). Mitigation: contract-only input (D2).
- **Execution creep** — agent runs tests it generates. Mitigation: generate-only boundary (D3).
- **Fabrication on thin input** — invents cases when contract lacks `CHECK:` lines. Mitigation: D5 refusal envelope.

---

## §6 Required tests

Focused wrapper tests must prove:

1. Traceable generation — every case maps to a named contract clause (T1).
2. No invention — absent contract behavior gets no test (T2).
3. Contract-only — never reads target implementation modules (T3).
4. Insufficient input → `INPUT_INSUFFICIENT_CANNOT_GENERATE` (T4).
5. No execution path (T5).
6. Consumable output structure for pytest harness (T6).
7. Zero governance/state writes (T7).
8. Each contract done-condition yields at least one functional case when checkable (T8).

Existing rubric/gate tests for the **target** agent remain authoritative for target behavior; #61 tests prove generator boundary only.

---

## §10 Open questions

1. Single-target vs multi-target manifest for Mode A (fixed manifest like Architect, or operator-selected target per run).
2. Whether generated cases are persisted to disk in Stage 1 or stdout/in-memory only.
3. Formal task_id naming for `complete_gate.py` when #61 itself is gated.

---

## §11 Sign-off

**§11 UNSIGNED — draft placement only.**

- [ ] I approve this contract as written.
- [ ] I authorize Grok pre-build gate review (Codex lane).
- [ ] On clean gate, I §11-sign and authorize reconcile to SIGNED_UNBUILT.

Confirmed: #61 generates test cases from a contract; it never runs, judges, or builds.

Upstream contract-source + downstream test-runner reconciled against repo:
- [x] yes (Cursor reconcile 2026-06-21)
- [ ] pending operator review

Signature: ____________________________

Date: ____________________________

Commit: ____________________________
