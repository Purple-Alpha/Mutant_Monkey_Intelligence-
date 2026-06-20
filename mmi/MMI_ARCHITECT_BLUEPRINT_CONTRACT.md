# MMI Architect — Blueprint Contract

**Status:** §11 SIGNED 2026-06-20 by Matt Nichol. Build authorized for `scripts/mmi_architect.py` Mode A (stdout-only) per MMI-DEC-041. Contract aligned to implemented behavior per MMI-DEC-042.

**Classification:** `SIGNED_CONTRACT` · Crew role: Architect

**Owner:** Matt Nichol

**Authority repo:** `/home/socialarchitect/northstar` (Mutant Monkey Security)

**Parent model:** Five-role crew operating model (Estimator / Architect / Superintendent / PM / Blueprint of Record)

**Date:** 2026-06-20

---

## 1. Purpose

The **Architect** is a read-only structural blueprint emitter for **one operator-selected build candidate** at a time. It reads a fixed candidate manifest and on-disk source contracts only. It does **not** score, select, route, authorize, or persist blueprints.

**Two outputs only:**

1. `BLUEPRINT` — checkable build blueprint for the selected candidate when all required source material resolves
2. `INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT` — named gaps when source contract, flow contract, out-of-scope boundaries, checkable build conditions, or artifact basis are missing or invalid; **this is a valid safety outcome, not a tool failure**

Mode A is **read-only / stdout-only**. Mode B (Blueprint-of-Record population) is **not authorized**.

---

## 2. Scope

### In scope (Mode A build slice)

- `scripts/mmi_architect.py` Mode A (stdout only, zero file writes at runtime)
- Acceptance tests T1–T11 (§16); fixtures are static inputs under `tests/fixtures/mmi_architect/` only
- Contract alignment to implemented envelope (MMI-DEC-042)

### Out of scope

- Mode B persistence or `mmi/BLUEPRINT_OF_RECORD.md` population
- Superintendent verification role (separate contract)
- PM owner-interface build (separate contract)
- Estimator scoring changes
- Dispatcher edits, registry-fed routing, scoreboard writes
- AUTH-5 autonomous selection or routing
- Drafting or placing missing Agent Design Contracts during Architect runs
- Inventing downstream consumers, flow formats, build conditions, or out-of-scope boundaries

---

## 3. Locked design decisions

| ID | Decision |
|---|---|
| A-D1 | **Selected candidate only:** `--candidate` names exactly one id; no unselected blueprinting |
| A-D2 | **Fixed manifest:** candidate → agent contract path + artifact basis paths are code-locked; not scoreboard-fed at runtime |
| A-D3 | **Source contract required:** per-candidate signed Agent Design Contract must exist on disk and be readable |
| A-D4 | **No invention:** missing flow consumer/format, out-of-scope, or CHECK conditions → cannot-blueprint |
| A-D5 | **Research exclusion:** `mmi/research/` notes are never authority for blueprint requirements |
| A-D6 | **Checkable conditions only:** build conditions must use `CHECK:` prefixes with deterministic observables |
| A-D7 | **Forbidden verdict tokens** per §9 — never emitted as Architect conclusions |
| A-D8 | **Refresh = re-read disk;** no learning between runs |
| A-D9 | **Non-authority posture:** stdout blueprint is not build authorization, operator selection, or Blueprint-of-Record write |

---

## 4. Candidate manifest (reconciled 2026-06-20)

**Manifest reconciled:** YES (Mode A v1 — `#52` only)

| Candidate | Name | Required agent contract | Artifact basis |
|---|---|---|---|
| `#52` | Plain-English Explanation | `4. Product_Roadmap/Plain_English_Explanation_Agent_Design_Contract_Deep_Dive.md` | `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`; `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/client_facing_rubric.py` |

**Live repo note (2026-06-20):** `#52` currently emits `INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT` because the required agent contract path above is **not on disk**. Supporting rubric spec and `client_facing_rubric.py` exist; the Architect correctly refuses to invent the missing contract, flow contract, or boundaries from those artifacts alone.

**Architect does not read:** scoreboard, task registry, dispatcher, or orchestrator at runtime.

---

## 5. Source contract requirements

The agent contract file must contain parseable sections:

| Section | Requirement | Cannot-blueprint if |
|---|---|---|
| Agent contract file | Exists and is readable at manifest path | `missing_source:` or `unreadable_source:` |
| Artifact basis files | All manifest `artifact_basis` paths exist | `missing_artifact_basis:` |
| `## FLOW CONTRACT` | Table with four fields populated | `missing_flow_contract_field:` per field |
| Out of scope | `### Out of scope` bullet list with ≥1 item | `missing_out_of_scope_source` |
| `## BUILD CONDITIONS` | ≥1 `- CHECK:` line with allowed prefix | `missing_build_conditions_section` or `non_checkable_build_condition:` |
| Research authority | No `mmi/research/` used as authority | `research_note_authority_forbidden:` |

### 5.1 FLOW CONTRACT fields (all required)

| Field | Meaning |
|---|---|
| `output_location` | Exact output location path/field |
| `output_format` | Exact output format or schema reference |
| `downstream_consumer` | Named downstream consumer (exact path or module) |
| `consumer_usage` | How the consumer reads/uses the output |

### 5.2 Allowed CHECK prefixes

`file_exists:`, `field_present:`, `command_expect:`, `path_exact:`, `format_exact:`, `consumer_named:`

Vague language (`works well`, `good`, `clean`, `reasonable`, `robust`, `appropriate`, `properly`) in build conditions triggers `vague_build_condition:` unless tied to a deterministic CHECK (forbidden in output conditions).

---

## 6. Cannot-blueprint triggers

Emit `INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT` with named `gaps:` when any of:

- `unknown_candidate:` — id not in fixed manifest
- `missing_source:` — agent contract path absent
- `missing_artifact_basis:` — listed basis file absent
- `unreadable_source:` — agent contract empty/unreadable
- `missing_flow_contract_field:` — any FLOW CONTRACT field empty
- `missing_out_of_scope_source` — no out-of-scope bullets parsed
- `missing_build_conditions_section` — no BUILD CONDITIONS section
- `non_checkable_build_condition:` — condition lacks allowed CHECK prefix
- `vague_build_condition:` — vague wording in a condition
- `research_note_authority_forbidden:` — research note cited as authority

**Safety rule:** cannot-blueprint is preferred over inventing missing downstream consumers, flow formats, build conditions, or out-of-scope boundaries.

---

## 7. Blueprint output envelope (Section 7 parts)

When all inputs resolve, emit `BLUEPRINT` with these sections in order:

### 7.1 Candidate identity

```text
section: 1 CANDIDATE
selected_candidate: #N
selected_name: ...
```

Only the selected candidate appears. No `#1`, `#3`, or other unselected candidate blueprint blocks.

### 7.2 Source manifest

```text
section: 2 SOURCE MANIFEST
agent_contract: ...
artifact_basis: ...
```

### 7.3 Build conditions

```text
section: 3 BUILD CONDITIONS
condition: CHECK:...
```

Every condition line must be observable/checkable (file exists, field present, command expected result, exact path, exact format, named downstream consumer).

### 7.4 Flow contract

```text
section: 4 FLOW CONTRACT
output_location: ...
output_format: ...
downstream_consumer: ...
consumer_usage: ...
```

Missing any field invalidates the blueprint; tool must not emit `BLUEPRINT`.

### 7.5 Out-of-scope boundaries

```text
section: 5 OUT OF SCOPE
boundary: ...
```

Boundaries are copied from the source contract out-of-scope section only — not invented.

### 7.6 Evidence requirements

```text
section: 6 EVIDENCE REQUIREMENTS
requirement: WORKER_COMPLETION_PACKET with ...
requirement: CHECK:...
```

Tier 2A-style completion packet fields required in blueprint evidence section: `task_or_contract_ref`, `files_changed`, `exact_commit_hash`, `scope_confirmation`, `tests_gates_run`, `deviations_from_contract`, verify output, `git_status_short`, and out-of-scope confirmations.

### 7.7 Non-authority footer

Closing record lines establish non-authority posture:

```text
source_contract_path: ...
```

Blueprint output is stdout-only, unpersisted, and not Blueprint-of-Record population. A blueprint does not authorize builds, operator selection, or crew role expansion. Forbidden verdict tokens (§9) must not appear as Architect conclusions.

---

## 8. Output envelopes

### BLUEPRINT

```text
BLUEPRINT
candidate_id: #52
name: Plain-English Explanation
---
section: 1 CANDIDATE
...
section: 6 EVIDENCE REQUIREMENTS
...
source_contract_path: ...
```

Exit code: `0`

### INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT

```text
INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT
candidate_id: #52
gaps:
  - missing_source: 4. Product_Roadmap/Plain_English_Explanation_Agent_Design_Contract_Deep_Dive.md
```

Exit code: `2` (valid safety outcome)

---

## 9. Forbidden tokens (tool output)

Never emit as Architect conclusions: `SELECTED`, `AUTHORIZED`, `APPROVED`, `RECOMMENDED`, `BUILD_AUTHORIZED`, `COMPLETE`, `SIGNED`, `VERIFIED`, `PASS`, `FAIL`, `PROMOTED`, `NEXT_DECIDED`.

Also forbidden: raw `VERDICT:` lines copied from dispatcher verify output.

Evidence bodies and `CHECK:command_expect:` requirement lines may reference external tools without adopting their verdict tokens as Architect conclusions.

---

## 10. Authority boundaries

- Matt selects candidates; Architect blueprints the selected candidate only when sources resolve
- AUTH-5 remains **BLOCKED**
- Registry-fed routing remains **FORBIDDEN**
- No dispatcher import or runtime call
- No scoreboard / registry / decision-log / Blueprint-of-Record writes
- No Mode B persistence
- Research notes under `mmi/research/` are excluded as authority (may appear only as excluded-input citations)

---

## 11. Sign-off

**§11 SIGNED — Matt Nichol, June 20 2026.**

- Build mode: **Mode A (read-only / stdout-only)**
- Two outputs: **`BLUEPRINT`** | **`INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT`**
- Manifest reconciled: **YES** (§4 — `#52` only in Mode A v1)
- Build authorization: **`scripts/mmi_architect.py` Mode A** (MMI-DEC-041)
- Contract alignment: **MMI-DEC-042** (this file matches implemented/tests behavior)
- Mode B / Blueprint-of-Record population: **NOT authorized**
- Superintendent / PM: signed elsewhere; **not build-authorized** here

---

## 16. Acceptance tests

| Test | Name | Pass condition |
|---|---|---|
| T1 | Selected-only | Output blueprints only the `--candidate` id; no `#1`/`#3`/other unselected blocks |
| T2 | Missing source | Absent agent contract → `INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT` with `missing_source:` named |
| T3 | No invention | Missing flow contract fields → cannot-blueprint; no invented downstream consumers |
| T4 | Blueprint checkable | Every `condition:` line uses `CHECK:`; flow fields and paths are exact |
| T5 | Flow contract required | `BLUEPRINT` includes all four FLOW CONTRACT fields |
| T6 | Out-of-scope carried | Boundaries from source contract; absent out-of-scope → cannot-blueprint |
| T7 | Evidence requirements | `section: 6 EVIDENCE REQUIREMENTS` with WORKER_COMPLETION_PACKET fields |
| T8 | Forbidden tokens | No §9 forbidden verdict tokens on output lines |
| T9 | Zero writes | Live repo immutable path digests unchanged after run |
| T10 | No dispatcher/registry/scoreboard coupling | No dispatcher import; no scoreboard/registry paths in tool source |
| T11 | No research-note authority | Research paths as authority → `research_note_authority_forbidden` gap |
