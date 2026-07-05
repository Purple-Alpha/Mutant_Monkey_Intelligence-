# Claude Handoff — AGI §5 Step 5 Genomic Realignment Loop

**Task id:** `mmi-genomic-realignment-loop-spec`  
**Assignee:** Claude (Design)  
**Build auth:** NOT_AUTHORIZED — **spec only**  
**Framework:** `lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md`

**Evidence basis:** AGI §5 steps 1–4 CLOSED (Phase 1 PASS, Gate B Codex CLEAN, control envelope Codex CLEAN, console server Codex CLEAN + Matt E2E signoff). Step 5 is the only macro candidate per falsification table in `status/MMI_MACRO_BUILD_DECISION_2026-07-03.md` (step 4 closed).

**Two-message workflow (mandatory):**
1. Paste **MESSAGE 1** below into a fresh Claude window — generation pass.
2. After Claude returns the spec, paste **MESSAGE 2** — adversarial self-review pass.
3. Relay **final revised spec** to Cursor for closeout. Do not skip MESSAGE 2.

---

## MESSAGE 1 — Generate spec (paste this first)

```
PROJECT: MMI
TASK ID: mmi-genomic-realignment-loop-spec
ASSIGNEE: Claude (Design)
SCORE: 93
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
Evolution gate: OUTSTANDING — 48h proof NOT built; cannot claim PERFECT or Phase 3

Prereqs CLOSED (step 5 dependencies — all must be wired, not re-designed):
  AGI §5 step 2 — Gate B proof gate:
    - scripts/proof_gate_harness.py — proof-of-fix + proof-of-no-regression; --console-bindings v2
    - chaos/weapon_battlefield_scoring.py — generate_proof_bundle(), fingerprint_digest()
    - architecture/MMI_PROOF_GATE_CONSOLE_BINDINGS_SPEC_2026-07.md (r1) — BUILT
    - chaos/mmi_canonical_digest.py, chaos/console_fingerprint_ledger.py — BUILT
    - tests/test_proof_gate_console_bindings.py — BUILT

  AGI §5 step 3 — Budget ceiling + dead-man:
    - chaos/mmi_control_envelope.py — pre_iteration_gate(), sticky latch, budget caps
    - architecture/MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md — Codex CLEAN
    - scripts/control_envelope_harness.py — T1–T3 CLEAN
    - §4.6 pre-iteration call order for any future self-directed loop (loop NOT built in step 3)

  AGI §5 step 4 — Ed25519 evidence gate:
    - scripts/console_server.py — FastAPI verify-only, loopback 127.0.0.1, Body(...) JSON routes
    - chaos/console_evidence_gate.py — V0–V16, S1–S8 validate/sign core
    - chaos/console_ack_adapter.py — poll/verify/consume signed SIGN_ACK / SIGN_RESUME records
    - scripts/console_bundle_builder.py, scripts/console_sign_client.py — operator client path
    - scripts/console_server_harness.py — T1/T2/T3 + T2e/T2f HTTP + H4/H6/H8/H10 — CLEAN
    - architecture/MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md (r3) — Codex CLEAN
    - Matt E2E lab: VALID → Ed25519 ACCEPTED (real signoff, not harness-only)

  Mirror / dissection (partial — loop consumes, does not replace):
    - chaos/mirror_dimension_router.py — route_to_mirror(), harvest_exploit_telemetry()
    - scripts/mirror_dimension_router.py — CLI route/status/harvest
    - chaos/MMI_MIRROR_DIMENSION_ROUTER_SPEC_2026-07.md

  Adversary / regression suites (loop must invoke, not trust self-report):
    - chaos/purple_evasion_suite.py — run_purple_evasion_suite(), list_scenarios()
    - scripts/chaos_lab_provisioner.py — purple-evasion, smash-all, mesh-smash subcommands
    - chaos/action_integrity_gate.py — bounded schema validation (patches must stay inside envelope)

Doctrine (authoritative):
  - architecture/MMI_AGI_EVOLUTION_PATHWAY.md — §2 Pillar 3 (Genomic Self-Healing), §5 step 5, §6 non-goals
  - architecture/MMI_DIFFERENTIATOR_2026-07.md — proof before signature; verifiable self-modification
  - status/MMI_CONSOLE_SERVER_STEP4_CLOSEOUT_2026-07-03.md — step 4 closed; step 5 next

NOT BUILT (out of scope for this spec):
  - ops/genomic_realignment_loop.py — TARGET of this spec (path per AGI pathway; justify ops/ vs scripts/)
  - central_brain.py (AGI step 6)
  - Host boundary Go daemon, M4 48h continuous assault
  - Production auto-apply / promote tooling (signoff record consumption is separate downstream)
  - Unbounded self-authored runtime code (AGI §6 explicit non-goal)
</current_state_inventory>

<existing_implementation_pattern>
AGI Pillar 3 guardrail (pathway §2 — normative, spec must implement):

  On breach of a critic node:
    1. Dissect attack inside mirror_dimension_router (isolated copy, not authority repo)
    2. Extract failure core logic from harvest telemetry
    3. Synthesize a BEHAVIORAL CONSTRAINT (bounded typed patch — NOT arbitrary code)
    4. Before human sign-off eligibility:
       a. Proof-of-fix: re-run exact exploit scenario; attack must fail to breach
       b. Proof-of-no-regression: full purple_evasion_suite must stay green
       c. Rollback token: pre-patch known-good snapshot hashed and bound in Gate B summary
    5. Present bundle to console_server validate → operator Ed25519 sign
    6. NEVER apply patch without consumed signoff record (H5 downstream — define loop obligations)

Control envelope pre-iteration gate (step 3 — loop MUST call every tick):
  pre_iteration_gate() ordering: latch → heartbeat/halt → budget
  Loop CANNOT: advance ack_seq, clear HALT/SUSPEND, raise caps, write fingerprint ledger
  Human ack via ConsoleAckAdapter signed records (SIGN_ACK / SIGN_RESUME)

Gate B → Console pipeline (step 2+4 — loop produces, does not bypass):
  patch_context MUST be outside authority repo (proof_gate_harness enforces)
  proof_gate_harness --console-bindings → suite proof_gate_v2_console_bindings
  CLEAN summary required before console validate PASS
  console_fingerprint_ledger append on CLEAN — written by proof_gate ONLY, NEVER by evolution loop

Proof gate harness exit contract:
  overall_gate_status CLEAN|BLOCKED — binary, no partial pass
  evidence under /tmp/mmi_proof_gate/ or caller patch-context EVIDENCE dir

Mirror router harvest shape (dissection input):
  harvest_exploit_telemetry(agent_id) → telemetry dict for evidence hub
  route_to_mirror(agent_id, payload) → routed bool + containment metadata
</existing_implementation_pattern>

<task_definition>
Write the complete markdown spec file:

  mmi/project_brain/architecture/MMI_GENOMIC_REALIGNMENT_LOOP_SPEC_2026-07.md

Scope — AGI §5 step 5 only: genomic_realignment_loop (governed self-healing loop)

1. OPERATIONAL DEFINITION
   - What the loop does: detect breach signal → mirror dissection → bounded constraint synthesis → Gate B → console sign eligibility → STAGING ONLY (no apply in v1 unless Matt explicitly defines promote sub-step)
   - What it does NOT do: unbounded code gen, authority repo writes, ledger writes, auto-sign, auto-apply
   - Constants table: tick interval ms, max iterations per incident, max patch bytes, lab_root paths, audit_root under /tmp/mmi_genomic_loop/, replay windows

2. BOUNDARY VS ADJACENT SYSTEMS
   - mirror_dimension_router (read/harvest only in v1?)
   - proof_gate_harness (mandatory invoke — loop cannot self-certify)
   - console_server + console_ack_adapter (sign poll/consume — loop waits, never forges)
   - mmi_control_envelope pre_iteration_gate (mandatory every tick)
   - console_fingerprint_ledger (read-only for loop; proof_gate writes on CLEAN)
   - action_integrity_gate (patch shape validation before Gate B)
   - purple_evasion_suite (full regression — name scenarios or class, not "run tests")

3. LOOP STATE MACHINE
   - States: IDLE, INCIDENT_DETECTED, DISSECTING, SYNTHESIZING, PROOF_PENDING, AWAITING_SIGN, STAGED, HALTED, SUSPENDED
   - Transitions with fail-closed rules; budget/dead-man can preempt any state
   - Incident trigger sources (v1): explicit CLI/lab signal only OR named breach hook — no fake autonomous 24/7 claim in v1 unless bounded + budget gated

4. PATCH / CONSTRAINT ARTIFACT SCHEMA
   - patch_content format (diff, config delta, prompt-template constraint — pick one v1 canonical form)
   - patch_context layout outside authority (mirror proof_context.json pattern from Gate B)
   - rollback object binding per bindings spec §3.4
   - Relationship to fix_id, run_id, bundle_id across loop → Gate B → console

5. INTEGRATION CALL ORDER (normative diagram or numbered steps)
   - Full tick: envelope gate → incident handler → mirror harvest → synthesize → integrity gate → write patch context → proof_gate_harness → bundle_builder → console validate (HTTP or in-process adapter) → await operator sign → stage signoff record → STOP (apply is downstream v2 or separate spec)
   - Explicit failure paths: Gate B BLOCKED, console REJECTED, envelope HALTED — what gets logged, what gets discarded

6. PASS / FAIL LINES + HARD RULES (H-rules)
   - H1: No patch reaches console without Gate B CLEAN
   - H2: No signoff consumption by loop (loop stages only)
   - H3: No fingerprint ledger writes by loop
   - H4: No authority repo writes (path-prefix check like console H4)
   - H5: Rollback token required before proof run
   - H6: purple_evasion_suite full run on proof-of-no-regression (define minimum scenario set)
   - H7: Budget/dead-man preempt — loop must exit cleanly with evidence artifact
   - H8: Audit hash chain or append-only JSONL for loop events (mirror console audit pattern)
   - Fail-closed on any missing proof field

7. FALSIFIABLE TEST SCENARIOS T1–T5
   - T1: Simulated breach → dissection → synthesize → Gate B CLEAN → console VALID → staged signoff await (mock operator sign in harness)
   - T2: Gate B BLOCKED (regression fail) → loop must NOT reach console sign path; evidence shows BLOCKED
   - T3: Envelope HALTED mid-loop → loop stops; no patch staged
   - T4: Tampered patch_context inside authority path → refused before Gate B
   - T5: Replay / duplicate incident_id → rejected (idempotency)

8. HARNESS SPEC
   - scripts/genomic_realignment_loop_harness.py (name fixed) — mirror console_server_harness / proof_gate_harness patterns
   - Hermetic --evidence-dir reset (rerunnable on same dir)
   - Emits genomic_loop_summary.json with scenarios + overall_gate_status CLEAN|BLOCKED
   - Exit 0 iff CLEAN

9. NON-GOALS
   - central_brain Phase 2 synthesis (step 6)
   - 30-day Phase 3 continuous operation claim
   - M4 48h, host boundary daemon, PERFECT evolution gate
   - Loop writing ack_seq or clearing HALT without signed console record
   - LLM free-form patch generation without integrity gate + registered capability set
   - Kinetic war room UI (optional read-only telemetry hook only)

Required spec sections (mirror console/control envelope layout):
  1. Operational Definition (+ constants table)
  2. Boundary vs Adjacent Systems
  3. Loop State Machine
  4. Data Schema (patch, incident, audit, summary)
  5. Integration Sketch (call order)
  6. Pass / Fail Lines (+ H-rules)
  7. Falsifiable Test Scenarios T1–T5
  8. Harness Spec
  9. Non-Goals
  Footnotes for assumptions
  SIGN-OFF line: PASS | PASS WITH REVISIONS | FAIL
</task_definition>

<execution_constraints>
1. Deliver the complete markdown spec file only — no chat intro, no closeout prose.
2. Spec-only. No Python. No tasks.json edits. No build authorization.
3. Every threshold must be a named constant — no ML probability scores, no soft prompts as gates.
4. Evidence/audit paths must stay outside authority repo (/tmp/... pattern).
5. Five falsifiable T1–T5 scenarios with expected verdict + state transition.
6. MMI hard stops: no unbounded self-modification, no fake pass rates, no scope outside task_definition.
7. Explicitly define how loop rejects "self-certify safe patch" attacks (machine bypass of Gate B / console).
8. v1 scope honesty: if 24/7 autonomous loop is deferred, say so; define minimal CLI-driven incident path that still proves the genomic chain.
</execution_constraints>

<no_explanations_directive>
Respond with the production-grade markdown spec file payload only. Assumptions go in spec footnotes — not chat prose.
</no_explanations_directive>
```

---

## MESSAGE 2 — Adversarial self-review (paste after MESSAGE 1 output)

```
<review_mode>
You just wrote MMI_GENOMIC_REALIGNMENT_LOOP_SPEC_2026-07.md.

Adversarial self-review — assume a compromised loop OR hostile operator trying to:
- Skip proof_gate_harness and present a patch directly to console validate
- Self-report proof-of-fix / proof-of-no-regression without invoking purple_evasion_suite
- Write patch_context or evidence inside /mnt/c/Architectapp_clean authority repo
- Append to console_fingerprint_ledger or forge rollback lineage (V15 class attack)
- Auto-apply a patch without a consumed Ed25519 signoff record (H5 bypass)
- Advance ack_seq, clear HALT/SUSPEND, or raise budget caps from loop code
- Synthesize unbounded arbitrary code outside action_integrity_gate registered capabilities
- Replay an old incident_id or reuse a stale Gate B summary (V14 freshness class)
- Harvest mirror telemetry from authority paths instead of isolated lab mirror root
- Continue running when pre_iteration_gate returns HALTED/SUSPENDED
- Confuse staging a signoff record with authorization to promote
- Claim Phase 3 / PERFECT / 30-day continuous operation in v1 scope
- Split patch across multiple small changes to evade regression suite

Fix every finding inline. Output the COMPLETE revised spec file (not a diff). Update SIGN-OFF to PASS WITH REVISIONS if you changed anything material.
</review_mode>
```

---

## Closeout checklist (Cursor PM — after Matt relays design)

- [x] Spec path: `architecture/MMI_GENOMIC_REALIGNMENT_LOOP_SPEC_2026-07.md`
- [x] SIGN-OFF: PASS WITH REVISIONS (r2)
- [x] T1–T7 falsifiable scenarios present
- [x] Gate B + console chain explicit (no self-certify path)
- [x] control_envelope pre_iteration_gate mandatory every tick
- [x] fingerprint ledger loop-write forbidden (H6/H15)
- [x] authority repo write forbidden (H9)
- [x] Harness spec with exit 0 iff CLEAN
- [ ] Codex plan review → BUILDABLE before Matt `authorize build step 5`

**Codex handoff:** `lanes/CODEX_HANDOFF_GENOMIC_REALIGNMENT_LOOP_PLAN_REVIEW_2026-07-03.md`
