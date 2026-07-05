# Claude Handoff — AGI §5 Step 3 Budget Ceiling + Dead-Man Switch

**Task id:** `mmi-control-envelope-budget-deadman-spec`  
**Assignee:** Claude (Design)  
**Build auth:** NOT_AUTHORIZED — **spec only**  
**Framework:** `lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md`

**Evidence basis (macro AGI ladder — not a menu):**  
Derived winner from AGI §5 dependency order + §6 non-goals. Steps 1–2 closed (Phase 1 PASS, Gate B CLEAN). Step 3 is the only macro candidate with full dependency clearance and safety-gate requirement. See `status/MMI_MACRO_BUILD_DECISION_2026-07-03.md`.

**Two-message workflow (mandatory):**
1. Paste **MESSAGE 1** below into a fresh Claude window — generation pass.
2. After Claude returns the spec, paste **MESSAGE 2** — adversarial self-review pass.
3. Relay **final revised spec** to Cursor for closeout. Do not skip MESSAGE 2.

---

## MESSAGE 1 — Generate spec (paste this first)

```
PROJECT: MMI
TASK ID: mmi-control-envelope-budget-deadman-spec
ASSIGNEE: Claude (Design)
SCORE: 90
BUILD AUTHORIZATION: NOT_AUTHORIZED — spec only, no implementation
PROMPT FRAMEWORK: mmi/project_brain/lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md

<system_role>
Lead Cybernetic Architect / Purple Team Engineer
Project: Mutant Monkey Intelligence (MMI) — systems-domain AGI matrix
Doctrine: Bounded autonomy, strict deterministic rules over soft prompts, un-fakeable metrics
Design lane only — deliver one bounded markdown spec. No implementation. No scope expansion.
</system_role>

<current_state_inventory>
Repo root: /mnt/c/Architectapp_clean
Phase 1 weapon stack: PASS (tiers [4,4,4] — do not re-litigate)
Gate B proof gate: BUILT + Codex CLEAN (do not re-litigate)
Evolution gate: OUTSTANDING — 48h proof NOT built; cannot claim PERFECT

Existing envelope (preserve — do not break):
  - chaos/mmi_control_envelope.py — MMIControlEnvelope.enforce_boundary() only
    STATUS: CONCEPT / ARCHIVE — agent-output volumetric + schema invariants
    NOT wired: budget ceiling, dead-man switch, heartbeat, spend ledger

Related read-only inputs:
  - chaos/kinetic_telemetry.py — AFE ledger math (lab economics; not a kill-switch)
  - scripts/proof_gate_harness.py — Gate B harness pattern (evidence outside authority)
  - scripts/phase1_stability_harness.py — Phase 1 PASS record

Doctrine (authoritative):
  - architecture/MMI_AGI_EVOLUTION_PATHWAY.md — §2 Pillar 2 guardrails, §5 step 3, §6 non-goals
  - architecture/MMI_WEAPON_BATTLEFIELD_SCORING_MATRIX_v1.md — §6 evolution links (M4 blocked)
  - chaos/MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md — M4 PERFECT proof not built

Matt locked constraint: 15-minute loop interval for future soak/M4 dry-runs (heartbeat check interval N).
</current_state_inventory>

<existing_implementation_pattern>
Current mmi_control_envelope.py API (must remain backward-compatible):

    class MMIControlEnvelope:
        def __init__(self, max_token_length: int = 2048): ...
        def enforce_boundary(self, raw_agent_output: str, expected_schema: Dict) -> Tuple[bool, str]:
            # volumetric + forbidden directive + JSON schema — unchanged behavior

Gate B harness evidence pattern (mirror for control-envelope smoke harness):

    - Evidence under /tmp/mmi_control_envelope/<run_id>/EVIDENCE/ only
    - Authority repo read-only throughout
    - Exit 0 + JSON verdict with overall_gate_status field
    - assert paths outside authority before write

AGI §2 Pillar 2 requirements (spec must implement as testable contract):

    Budget ceiling:
      - per-hour and per-day token/compute cap declared in envelope config
      - on breach: loop SUSPENDS itself + structured alert artifact (not silent continue)

    Dead-man switch:
      - heartbeat file check every N minutes (default N=15 per Matt lock)
      - human ack within configured window OR runaway-cost/restart pattern → HALT
      - halt writes evidence bundle (reason, last heartbeat, spend snapshot)
</existing_implementation_pattern>

<task_definition>
Write the complete markdown spec file:

  mmi/project_brain/architecture/MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md

Scope — AGI §5 step 3 only:
1. BUDGET CEILING module contract
   - Config schema: per_hour_cap, per_day_cap, unit definition (tokens vs compute cycles — pick one, justify)
   - Rolling window accounting (file-backed persistence — justify atomic write pattern)
   - record_spend(amount) / check_budget() / on_breach → SUSPENDED verdict + alert artifact path
   - Integration hook: pre-iteration gate for any future self-directed loop

2. DEAD-MAN SWITCH module contract
   - Heartbeat file path, interval N, ack mechanism (file-based ack acceptable — console_server.py is step 4)
   - check_heartbeat() / record_heartbeat() / on_stale → HALTED verdict
   - Runaway detection: cost spike OR restart-loop pattern within window (define thresholds as constants)
   - Evidence bundle schema on halt

3. PRESERVE v0 enforce_boundary()
   - Additive API only; metadata_ingress_gate.py references must not break

4. TESTING + HARNESS (script-measurable — mirror proof_gate_harness.py)
   - pytest: budget breach → SUSPENDED; stale heartbeat → HALTED; runaway pattern → HALTED
   - CLI harness entrypoint spec: scripts/control_envelope_harness.py (name fixed in spec)
   - Falsifiable scenarios T1–T3 with expected verdict + evidence paths

5. OUT OF SCOPE (explicit non-goals section)
   - console_server.py Ed25519 gate (AGI step 4)
   - genomic_realignment_loop (step 5)
   - Gate C 15-min soak harness implementation (measurement infra — spec-only note OK)
   - M4 48h assault, canary alert rules, host boundary daemon
   - Production orchestrator wiring

Required spec sections (mirror iceberg L5/L7 spec layout):
  1. Operational Definition (+ constants table)
  2. Boundary vs Adjacent Systems (enforce_boundary v0, proof_gate, kinetic AFE, future console)
  3. Pass / Fail Lines (+ hard rules: no silent overspend, no unattended loop without heartbeat)
  4. Data Schema (persisted spend ledger, heartbeat state — no authority repo writes)
  5. Integration Sketch (call order before loop iteration)
  6. Falsifiable Test Scenarios T1–T3
  7. Non-Goals
  Footnotes for assumptions
  SIGN-OFF line: PASS | PASS WITH REVISIONS | FAIL
</task_definition>

<execution_constraints>
1. Deliver the complete markdown spec file only — no chat intro, no closeout prose.
2. Spec-only. No Python. No tasks.json edits. No build authorization.
3. Every threshold must be a named constant — no ML, no soft prompts.
4. Evidence paths must stay outside authority repo (/tmp/... pattern).
5. Three falsifiable T1–T3 scenarios with expected verdict + route.
6. MMI hard stops: no unbounded self-modification, no fake pass rates, no scope outside task_definition.
</execution_constraints>

<no_explanations_directive>
Respond with the production-grade markdown spec file payload only. Assumptions go in spec footnotes — not chat prose.
</no_explanations_directive>
```

---

## MESSAGE 2 — Adversarial self-review (paste after MESSAGE 1 output)

```
<review_mode>
You just wrote MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md.

Adversarial self-review — assume a hostile operator or runaway loop trying to:
- Silently exceed token/compute caps by splitting spend across windows or resetting counters
- Forge or stale-heartbeat without triggering HALT
- Bypass dead-man by touching heartbeat file without human ack semantics
- Continue loop execution after SUSPENDED or HALTED verdict (fake-pass path)
- Write evidence or state files inside the authority repo
- Confuse AFE ledger display metrics with actual budget enforcement
- Break existing enforce_boundary() callers (metadata_ingress_gate)

Fix every finding inline. Output the COMPLETE revised spec file (not a diff). Update SIGN-OFF to PASS WITH REVISIONS if you changed anything material.
</review_mode>
```

---

## Closeout checklist (Cursor PM)

- [x] Spec path: `architecture/MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md`
- [x] SIGN-OFF: PASS WITH REVISIONS (REV A)
- [x] T1–T3 falsifiable scenarios present
- [x] 15-min heartbeat default documented
- [x] enforce_boundary() preservation explicit (+ Cursor source-verified 2026-07-03)
- [x] Codex plan review → BUILDABLE before Matt `authorize build`
- [x] Codex diff review R1 → **CLEAN** (2026-07-03)
