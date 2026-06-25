# MMI Transition Gate Map — Zero-Guesswork State Transitions

**Status:** Canonical routing authority for pre-build / audit transitions (MMI-DEC-186)

**Owner:** Matt Nichol — §11, promotion, production, AUTH-5 only

**Last updated:** 2026-06-25

**Rule:** Every map transition clears the gates below in order. Failures halt forward progress and route backward to the Creator crew with evidence — no operator pick menus.

---

## Pipeline overview

```text
[1 PRE-BUILD / INPUT]
Cursor or Codex produces contract/build payload
        │
        ▼
[2 PRIMARY AUDIT ENGINE — always on]
Step 00  scripts/validate_agent_contract_block.py  (deterministic §3 field count)
Step 01  Template §3 block completeness (+ signed infra exception if applicable)
Step 02  VISION.md seven non-negotiables
Step 03  AGENTS.md builder-auditor isolation
Step 04  audit_tools/complete_gate.py (forbidden language, §11 in packet, manifest/git)
Step 05  MMI-DEC-* alignment (human filing + optional contradiction report)
        │
        ▼
[3 CONDITIONAL CONTEXT GATES — lane-triggered only]
Cyber insurance package specs · Agent Health Score · IFM-AUD / BRC-ADV checklists
        │
        ▼
[4 ORCHESTRATION — no scoring loop]
scripts/mmi_pm_voice.py relay + MMI-DEC filing + MMI_CURRENT_STATE update
        │
   FAIL ─┴─► CREATOR repair packet (evidence strings, missing field IDs, re-run commands)
   PASS ───► next lane (§11 sign · build · promotion · gate re-run as documented)
```

**Not default rubric:** NIST, ISO 27001, SOC2, OWASP — unless the active lane contract explicitly requires them.

---

## Programmatic state transition table

| Step | Gate | Target artifact | Hard stop (auto-reject) |
|------|------|-----------------|-------------------------|
| 00 | Structural pre-flight | `scripts/validate_agent_contract_block.py` | Field count below template §3 required list; no signed infrastructure template exception |
| 01 | Contract block | `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` §3 | Incomplete Agent Design Contract block in payload |
| 02 | Ideological safety | `VISION.md` | Weakening or bypass of seven non-negotiables |
| 03 | Architecture isolation | `AGENTS.md` | Builder-auditor separation or build-loop collapse |
| 04 | Static execution | `audit_tools/complete_gate.py` | Forbidden language, missing §11 packet, manifest/git mismatch |
| 05 | Authority matrix | `mmi/MMI_DECISION_LOG.md` | Action conflicts with active lane or historical MMI-DEC-* |
| 06 | Secondary variance | Lane contract + context logs | Insurance / health score / adversarial checklist miss when lane requires |

---

## Runtime roles (repo-accurate names)

| Role | Actor | Writes |
|------|-------|--------|
| Creator | Claude / Cursor | Contract drafts, code, tests, manifests under `audit_outputs/pending/` |
| Auditor | `complete_gate.py` → Grok or Gemini | `audit_outputs/*.md` only (gitignored) |
| Orchestrator | PM Voice + superintendent | `MMI-DEC-*`, `MMI_CURRENT_STATE.md`, `decision_cycles_log.md` |
| Operator | Matt Nichol | §11 signatures, promotion, production, AUTH-5 |

Creator and Auditor **never share a session** and **never share write authority**.

---

## Step 00 — local pre-gate barrier

Run before every contract pre-build gate:

```bash
python3 scripts/validate_agent_contract_block.py \
  "4. Product_Roadmap/<Agent>_Agent_Design_Contract_Deep_Dive.md"
```

Exit 0 required. Exit 1 prints missing field labels and blocks expensive auditor calls.

JSON output for orchestration relays:

```bash
python3 scripts/validate_agent_contract_block.py --json "<contract-path>"
```

---

## Auditor JSON contract (Gemini / Grok relay)

When Codex relays to the completion gate auditor, require this shape in the audit summary:

```json
{
  "contract_fields_found": 0,
  "contract_fields_required": 0,
  "exception_validated": false,
  "non_negotiables_passed": true,
  "complete_gate_status": "PASS",
  "mmi_log_aligned": true,
  "secondary_checks_triggered": [],
  "failure_reasons": []
}
```

Primary rubric only unless Step 06 lane flags fire.

---

## Gate failure notification (operator trace)

When any step blocks, append to `decision_cycles_log.md` and update `MMI_CURRENT_STATE.md`:

```text
GATE_ROLLBACK — {task_id} — {UTC}
Failure step: {00–06 name}
Evidence: {exact strings — e.g. 11/31 fields; missing Canonical team / case type}
Artifact: audit_outputs/{file}.md (if Step 04+)
SHA256: {hash}
Automated action: halt forward progress; pipe repair packet to Creator
Matt required: NO (crew fix) | YES (§11 / promotion / production / AUTH-5)
Next command: {exact shell command}
Decision slot: MMI-DEC-{next}
```

Human-readable header for PMV / chat relay:

```text
TRANSITION GATE BLOCKED: TASK #{id}
Source: Cursor/Codex {lane}
Failure point: {step name}
Evidence base: {counts + missing fields}
Automated action: progression halted; repair packet routed to Creator
Matt required: {NO|YES — reason}
```

---

## Creator → Auditor packet boundary

**Creator output** (paths + lane metadata only — no self-PASS):

- `transition_id` / `task_id` (e.g. `mmi_71_contract_gate`)
- `lane.candidate_id`, `lane.lane_type`, `authority_ref` (MMI-DEC placement)
- `artifacts.primary_path` + optional implementation paths
- `governance_context_paths` (template, VISION, AGENTS, decision log)

**Audit request** (built by relay — not Creator):

- `audit_outputs/pending/{task_id}.manifest.json`
- `python3 audit_tools/complete_gate.py --task {task_id} --claim "{claim}"`

Step 00 must pass before the manifest is submitted to Step 04.

---

## Repair packet template (contract block)

When Step 00/01 fails, Creator receives:

1. Exact missing field labels from validator stderr or JSON `missing_fields`
2. Canonical shape from template §3 fenced block (`Agent name:` … `Build Authorization dependency:`)
3. Explicit FORBIDDEN list: self-audit, §11 sign, scoreboard flip, AUTH-5, default registry
4. Re-run commands: Step 00 → manifest → complete_gate.py

---

## #71 reference failure (MMI-DEC-185)

| Item | Value |
|------|-------|
| Failure | 11-field summary table vs full §3 labeled block |
| Fix | MMI-DEC-186 — full block + Step 00 validator |
| Path | `4. Product_Roadmap/Token_Usage_Tracker_Agent_Design_Contract_Deep_Dive.md` |
| Next after PASS | Pre-build gate re-run → Matt §11 → promotion review |

---

## Related authority files

- `mmi/MMI_MISSION_MAP.md` — staged chain of command
- `mmi/MMI_CHAIN_OF_COMMAND_MISSION_MAP.yaml` — machine map
- `scripts/mmi_pm_voice.py` — standing queue relay
- `scripts/mmi_packet_intake.py` — worker completion packet shape (Tier 2A)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` — §3 field source of truth

---

*End of transition gate map.*
