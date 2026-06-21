# Adversarial Test Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_63_ADVERSARIAL_TEST_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** §11 SIGNED 2026-06-21 by Matt Nichol (Grok pre-build gate clean `mmi_63_contract_gate_20260621T191927Z` 0/0). Evidence Stage 1 (Synthetic) agent wrapper authorized by signature. Signing locks D1-D9 and authorizes the `AdversarialTestAgent` wrapper build + focused tests **only**. It authorizes **no** Blueprint-of-Record population, **no** default-registry registration, **no** production dispatch, **no** autonomous action, and **no** AUTH-5. Scoreboard `SIGNED_UNBUILT` reconcile reconciled in same signing action per MMI-DEC-075.

**Candidate:** #63 — Adversarial Test

**Owner:** Matt Nichol

**Track:** BREADTH / Test-support (Layer 5 Challenge / Red-Team scoreboard row)

**Authority repo:** `/home/socialarchitect/northstar`

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `4. Product_Roadmap/Test_Case_Generator_Agent_Design_Contract_Deep_Dive.md` (#61 sibling — requirement tests)
- `4. Product_Roadmap/Regression_Test_Agent_Design_Contract_Deep_Dive.md` (#62 sibling — regression tests)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#63 Adversarial Test)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/sandbox/red_battery.py` (reference patterns only — not authority for target behavior)
- `audit_tools/complete_gate.py` (downstream completion gate consumer)
- `VISION.md` (Stage A — analyze / recommend / evidence only)

**Proposed future build path (not authorized here):** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/sandbox/adversarial_test_agent.py` (name TBD at build). No file is authorized until §11 signature.

---

## Agent Design Contract block

**Boundary:** #63 generates adversarial test cases that attempt to break a target's **declared** contract boundaries. It does **not** run tests, judge pass/fail, attack live systems, generate real exploits or weapon tooling, read target implementation code, build the target agent, or write governance/state.

| Field | Value |
|---|---|
| Agent name | Adversarial Test Agent (`AdversarialTestAgent`) |
| Swarm inventory ID | #63 — Adversarial Test |
| Canonical layer | 5 — Challenge / Red-Team (test-support generator) |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed |
| Role | Read one target's §11-signed contract non-goals, out-of-scope boundaries, failure modes, and forbidden behaviors; emit adversarial cases that try to cross each declared boundary with `expected` always the target's correct refusal/safe handling |
| Boundary | Contract-boundaries in, adversarial-cases-out. No execution, no evaluation, no implementation-code reads, no invented boundaries, no weaponization |
| Inputs | One target §11-signed Agent Design Contract at `4. Product_Roadmap/<Target>_Agent_Design_Contract_Deep_Dive.md` with parseable out-of-scope / failure-mode / explicit-non-authority sections |
| Outputs | Structured adversarial-case set per Section 6 envelope, or `NO_BOUNDARIES_CANNOT_GENERATE_ADVERSARIAL` with named gaps |
| Explicit non-authorities | No test execution; no pass/fail judgment; no live-system attacks; no real exploit/weapon generation; no retaliation/honeypot/personal-tracking behavior; no target code reads; no scoreboard/registry/state writes; no AUTH-5; no autonomous/background operation |

---

## REPO_RECONCILIATION

Cursor reconciliation applied 2026-06-22 (draft placement only):

| Placeholder | Resolved value | Repo evidence |
|---|---|---|
| Target contract source | `4. Product_Roadmap/<Target>_Agent_Design_Contract_Deep_Dive.md` — `§1 Scope` out-of-scope, `§5 Failure modes`, Agent Design Contract block explicit non-authorities, `## BUILD CONDITIONS` | Sibling contracts (#61, #62, #52) |
| Boundary attack basis | Declared non-goals, out-of-scope lists, failure modes, forbidden behaviors in the target contract — not target implementation code | Contract D2 / Section 5 hard rule |
| Downstream consumer | Target-agent focused `pytest` module (including `tests/test_*_adversarial.py` pattern) + `audit_tools/complete_gate.py --task <task_id>` | Proven adversarial suite lanes (#98–#102) + breadth lane (#61, #62) |
| Reference artifact (non-authority) | `core/sandbox/red_battery.py` synthetic red-battery cycle | Scoreboard #63 evidence surface; patterns only — cases derive from **contract boundaries**, not red_battery behavior |
| Distinction from #61 / #62 | #61 proves requirements; #62 protects recorded baselines; #63 attacks declared boundaries to harden before GATED | #61 `TestCaseGeneratorAgent`; #62 `RegressionTestAgent` |

Repo-reconciliation placeholders: **resolved for draft review.** §11 signature still required before build authorization.

---

## §0 Purpose

Unblock swarm #63 Adversarial Test by placing the Agent Design Contract the MMI crew expects at this path. The agent closes the gap between "the contract declares a boundary" and "a harness case that proves the boundary holds under hostile input" — without executing tests, hunting implementation weaknesses, or generating weapons outside the test harness.

This contract is governance + draft placement only. It does not build runtime code, sign §11, reconcile scoreboard lifecycle, or unlock AUTH-5.

---

## §1 Scope

### In scope
- Generating adversarial test cases from one target's signed contract declared boundaries per run.
- Traceability: every adversarial case maps to a named contract boundary, non-goal, or failure mode.
- `NO_BOUNDARIES_CANNOT_GENERATE_ADVERSARIAL` when the target contract declares no attackable boundaries.

### Out of scope
- Running or evaluating adversarial cases (pytest/gate are separate consumers).
- Attacking live systems, production data, or anything outside the test harness.
- Generating real exploit tooling or weapon-grade attack artifacts.
- Reading target implementation source to hunt weaknesses.
- Inventing boundaries or cases the contract never declared.
- Defining target failure as the pass condition (`expected` is always correct refusal/safe handling).
- Retaliation, honeypot, or personal-tracking behavior.
- Building or modifying the target agent.
- Scoreboard/registry/state/governance writes.
- AUTH-5, autonomous operation, default registry, production dispatch.

---

## FLOW CONTRACT

| Field | Value |
|---|---|
| upstream_input | Target §11-signed Agent Design Contract at `4. Product_Roadmap/<Target>_Agent_Design_Contract_Deep_Dive.md` |
| input_fields | `§1 Scope` out-of-scope; `§5 Failure modes`; Agent Design Contract block explicit non-authorities; `## BUILD CONDITIONS` forbidden paths where present |
| output_location | Stdout / in-memory structured adversarial-case set returned to explicit caller or test harness only at Stage 1 |
| output_format | Section 6 `ADVERSARIAL_CASE` structure |
| downstream_consumer | Target-agent focused `pytest` module under `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/tests/` (including adversarial suite pattern) + `audit_tools/complete_gate.py` |
| consumer_usage | pytest executes generated adversarial cases against the target wrapper; completion gate audits the implementation slice before GATED |
| insufficient_output | `NO_BOUNDARIES_CANNOT_GENERATE_ADVERSARIAL` — target contract lacks declared boundaries to attack; names gaps; emits no adversarial cases |

---

## TWO-OUTPUT ENVELOPE

### Adversarial-case envelope

```text
ADVERSARIAL_CASE
id: <unique id>
attacks: <which declared contract boundary / non-goal / failure mode this targets>
hostile_input: <the input designed to cross that boundary>
attempted_violation: <what the input tries to make the target do wrong>
expected: <the correct behavior — the target's required refusal / safe handling>
type: <boundary-violation | forbidden-output | scope-escape | invalid-input-handling>
```

**Hard rule:** every `ADVERSARIAL_CASE` must map to a **declared** contract boundary. The `expected` field is always the target's **correct** behavior — the case proves the boundary holds; it never defines success as the target failing.

### Refusal envelope

```text
NO_BOUNDARIES_CANNOT_GENERATE_ADVERSARIAL
gaps:
- <named gap>
WHY:
Target contract lacks declared boundaries / failure modes required to derive adversarial cases.
BOUNDARY:
advisory only; no adversarial cases emitted; no execution; no AUTH-5
```

---

## BUILD CONDITIONS

- CHECK: file_exists: 4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md
- CHECK: path_exact: target contract path resolves under `4. Product_Roadmap/` with `Agent` and `Design_Contract` in filename
- CHECK: field_present: target contract `§1 Scope` out-of-scope section or equivalent boundary list
- CHECK: field_present: target contract `§5 Failure modes` or equivalent failure-mode section
- CHECK: field_present: target contract Agent Design Contract block explicit non-authorities
- CHECK: command_expect: pytest focused suite for target wrapper passes when adversarial cases supplied|exit_code=0
- CHECK: consumer_named: complete_gate.py
- CHECK: sentinel_exact: NO_BOUNDARIES_CANNOT_GENERATE_ADVERSARIAL
- CHECK: invariant_present: every generated ADVERSARIAL_CASE attacks a declared contract boundary — no invented boundaries
- CHECK: invariant_present: every case expected is correct refusal or safe handling — never target-fails-as-pass
- CHECK: invariant_present: generator never reads target implementation modules — contract-boundaries-only input

---

## §2 Locked Design Decisions (§11 signed 2026-06-21)

- **D1 — Identity.** Adversarial Test is Layer 5 Challenge/test-support, Authority L3, Stage A, Evidence Stage 1 at signing.
- **D2 — Contract-boundaries-only input.** Cases derive from declared contract boundaries, never from target implementation code.
- **D3 — Generate only.** No execution, no pass/fail judgment, no gate substitution.
- **D4 — Traceability.** Every adversarial case maps to a declared boundary, non-goal, or failure mode.
- **D5 — Refusal on thin input.** Missing declared boundaries → `NO_BOUNDARIES_CANNOT_GENERATE_ADVERSARIAL`, never guessed boundaries.
- **D6 — Correct expected.** Every case `expected` is the target's correct refusal/safe handling — never inverted success.
- **D7 — No weaponization.** Output is test-harness challenge cases only; no live-system attacks, real exploits, retaliation, or honeypot behavior.
- **D8 — Zero writes.** No scoreboard/registry/state/governance mutation at Stage 1.
- **D9 — No autonomy / AUTH-5 blocked.** Distinct from #61 (requirements) and #62 (recorded baselines).

---

## §5 Failure modes

- **Weaponization drift** — generates working exploits instead of harness cases. Mitigation: D2 contract-only input, D7 hard boundary, D6 correct-expected rule.
- **Invented-boundary drift** — attacks boundaries the contract never declared. Mitigation: D4 traceability + D5 refusal envelope.
- **Implementation-hunting** — reads target code to find weaknesses. Mitigation: D2 forbidden read path.
- **Execution creep** — agent runs the cases it generates. Mitigation: D3 generate-only boundary.
- **Inverted success** — case defines target failure as pass. Mitigation: D6 hard rule on `expected`.
- **Retaliation/honeypot drift** — Mitigation: explicit out-of-scope + D7.

---

## §6 Required tests

Focused wrapper tests must prove:

1. Boundary-traced generation — every case maps to a declared contract boundary (T1).
2. Correct expected — every case `expected` is correct refusal/safe handling, never target failure (T2).
3. Contract-only — never reads target implementation modules (T3).
4. No boundaries — absent declared boundaries → `NO_BOUNDARIES_CANNOT_GENERATE_ADVERSARIAL` (T4).
5. No execution path (T5).
6. No weaponization path — no live-system attack, real exploit, retaliation, or honeypot output (T6).
7. Consumable output structure for pytest adversarial harness (T7).
8. Zero governance/state writes (T8).
9. Coverage — each declared boundary/failure mode yields at least one adversarial case when checkable (T9).

---

## §10 Open questions

1. Single-target vs operator-selected target manifest per run (fixed like Architect vs. explicit selection).
2. Whether adversarial cases persist to disk in Stage 1 or stdout/in-memory only.
3. Formal `task_id` naming for `complete_gate.py` when #63 itself is gated.
4. Minimum boundary vocabulary required in target contracts for reliable parsing (section titles vs. structured fields).

---

## §11 Sign-off

SIGNED. This signature locks D1-D9 and authorizes the Evidence Stage 1 (Synthetic) `AdversarialTestAgent` wrapper build + focused tests only; no Blueprint-of-Record population, no default-registry registration, no production dispatch, no autonomous action, no AUTH-5. Matt also authorized `MMI_63_SCOREBOARD_SIGNED_UNBUILT_RECONCILE_ONLY` in this signing action.

- [x] I approve this contract as written.
- [x] I authorize Grok pre-build gate review (Codex lane) — completed clean 0/0.
- [x] On clean gate, I §11-sign and authorize reconcile to SIGNED_UNBUILT.

Confirmed: #63 generates contract-boundary adversarial test cases; never runs, judges, builds, weaponizes, attacks live systems, or retaliates. Expected outcome is always the target's correct refusal.

Upstream contract-boundary source + downstream adversarial-runner reconciled against repo:
- [x] yes (Cursor reconcile 2026-06-22)
- [x] yes (operator review complete)

> Matt Nichol June 21st 2026
