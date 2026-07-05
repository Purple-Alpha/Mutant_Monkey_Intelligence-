# MMI GENOMIC REALIGNMENT LOOP — SPEC

**File:** `mmi/project_brain/architecture/MMI_GENOMIC_REALIGNMENT_LOOP_SPEC_2026-07.md`  
**Target:** `ops/genomic_realignment_loop.py` (NOT BUILT — this spec is the build contract)  
**Doctrine anchor:** `MMI_AGI_EVOLUTION_PATHWAY.md` §2 Pillar 3 (Genomic Self-Healing), §5 step 5, §6 non-goals; `MMI_DIFFERENTIATOR_2026-07.md` (proof before signature; verifiable self-modification)  
**Status:** SPEC ONLY — build NOT authorized by this document  
**Revision:** r2 — adversarial self-review applied (see REVISION LOG)  
**Depends on (all BUILT + CLEAN):** proof_gate step 2, control_envelope step 3, console_server step 4  
**Date:** 2026-07-03

---

## 1. OPERATIONAL DEFINITION

The genomic realignment loop is the **governed self-healing orchestrator** for AGI §5 step 5. It detects a critic-node breach, dissects it in an isolated mirror, synthesizes a **bounded behavioral constraint** (a typed patch, never arbitrary code), proves that constraint through Gate B, and presents the resulting evidence bundle to the console for human Ed25519 sign-off. It is an **orchestrator of existing gates, not a new authority.** Every safety property it appears to have is enforced by a subsystem it calls, not by the loop itself — so a compromised loop degrades to "produces bundles that get rejected," never "applies an unsafe change."

**What the loop is allowed to do:** route an exploit to the mirror, read harvest telemetry from the isolated mirror root, emit a typed constraint artifact into an out-of-repo patch context, invoke `proof_gate_harness --console-bindings`, and hand a CLEAN bundle to `console_server` validate. That is the full extent of its authority.

**What the loop is structurally incapable of doing** (enforced by callees, §6): applying or promoting a patch; advancing `ack_seq`; clearing HALT/SUSPEND; raising budget caps; writing the console fingerprint ledger; forging rollback lineage; authoring free-form runtime code; declaring its own success; declaring project maturity (PERFECT/Phase 3).

**v1 honesty — the 24/7 autonomous loop is DEFERRED.** v1 ships the **CLI-driven incident path**: a human (or a scheduled invocation) triggers one realignment *episode* for one detected breach, the episode runs the full genomic chain to a signed-or-rejected terminal state, and stops. This proves the genomic chain end-to-end (breach → mirror → constraint → Gate B → console VALID → operator Ed25519 ACCEPTED) without a self-directed runtime. Apply/promote stays downstream and out of scope (§9). Continuous autonomous operation is a v2 concern gated on the M4 48h proof, which remains OUTSTANDING — this spec does not claim PERFECT, 30-day continuous operation, or Phase 3, and the loop is forbidden from emitting any such claim (H18).¹

### 1.1 Constants table (all thresholds named — no ML, no probability gates)

| Constant | Value | Meaning |
|---|---|---|
| `LOOP_MODE` | `"cli_incident_v1"` | Only supported mode in v1. Autonomous mode absent by design. |
| `EPISODE_ROOT` | `/tmp/mmi_genomic_loop/` | All loop state/evidence. Outside authority repo. |
| `EPISODE_STATE_PATH` | `/tmp/mmi_genomic_loop/episodes/<episode_id>/state.json` | Atomic-write episode state. |
| `EPISODE_LEDGER_PATH` | `/tmp/mmi_genomic_loop/state/episode_ledger.jsonl` | Single-use ledger of `(incident_id, episode_id)` — replay guard. |
| `PATCH_CONTEXT_ROOT` | `/tmp/mmi_genomic_loop/patch_ctx/` | Out-of-repo patch context handed to proof_gate. |
| `MIRROR_LAB_ROOT` | `/tmp/mmi_mirror_dimension/` | Isolated mirror substrate. Harvest MUST originate here (H13). |
| `AUDIT_LOG_PATH` | `/tmp/mmi_genomic_loop/audit/genomic_audit.jsonl` | Append-only, hash-chained audit log. |
| `ARTIFACT_VERSION` | `"genomic_constraint_v1"` | Only accepted constraint artifact schema. |
| `MAX_CONSTRAINT_BYTES` | `65536` | Max serialized constraint artifact (64 KiB). Oversize → `ARTIFACT_TOO_LARGE`. |
| `MAX_SYNTH_ATTEMPTS` | `3` | Max synth→proof retries per episode before terminal `EXHAUSTED`. |
| `EPISODE_TTL_MS` | `3600000` | Max episode wall-clock (1 h) before terminal `TIMED_OUT`. |
| `MIRROR_HARVEST_TIMEOUT_MS` | `120000` | Max wait on `harvest_exploit_telemetry` (2 min). |
| `PROOF_GATE_SUITE` | `"proof_gate_v2_console_bindings"` | Required suite; loop invokes `--console-bindings`. |
| `PROOF_GATE_TIMEOUT_MS` | `1800000` | Max wait on proof_gate harness (30 min). |
| `PROOF_SUMMARY_MAX_AGE_MS` | `900000` | Max age (15 min) of the proof_gate summary at bundle-build time (freshness — V14 class). |
| `ALLOWED_CONSTRAINT_TYPES` | `{"rate_limit","action_deny","schema_tighten","route_isolate","param_clamp"}` | Closed enum of behavioral-constraint kinds. No other type validates. |
| `AUTHORITY_REPO` | `/mnt/c/Architectapp_clean` | Read-only to the loop, always. |

All timestamps are integer epoch milliseconds. All thresholds are named constants — there are no learned or probabilistic decision points anywhere in the loop.

---

## 2. BOUNDARY VS ADJACENT SYSTEMS

| System | Relationship | Boundary rule |
|---|---|---|
| `chaos/mirror_dimension_router.py` | **Dissection substrate.** Loop calls `route_to_mirror(agent_id, payload)` then `harvest_exploit_telemetry(agent_id)`. | Dissection happens ONLY in the mirror (isolated copy under `MIRROR_LAB_ROOT`). `route_to_mirror` must return `routed=true` + containment metadata whose root is `MIRROR_LAB_ROOT`, NOT an authority path (H13). Loop never dissects against the authority repo. Harvest telemetry is read-only input to synthesis. |
| `chaos/purple_evasion_suite.py` | **Regression truth (via proof_gate).** | Loop NEVER calls the suite directly to self-grade. Regression verdict comes only from the proof_gate summary. Loop trusting its own suite run = anti-pattern, forbidden (H7). |
| `chaos/action_integrity_gate.py` | **Constraint schema + capability bound.** Every synthesized artifact must pass bounded schema validation AND target only registered capabilities before it can be written to patch context. | A constraint that fails action_integrity schema, or that targets an unregistered capability, is rejected pre-proof (`ARTIFACT_SCHEMA_FAIL` / `CAPABILITY_UNREGISTERED`). The loop cannot emit a patch outside the action envelope or invent a new capability surface (H8). |
| `scripts/proof_gate_harness.py` (Gate B, step 2) | **Proof authority.** Loop invokes `--console-bindings`; consumes `proof_gate_summary.json`. | Loop cannot fabricate a CLEAN status. `overall_gate_status` is binary and produced by the harness. patch_context MUST be under `PATCH_CONTEXT_ROOT`. Summary must bind THIS episode's `constraint_id` + patch-context digest and be fresh (H14). |
| `chaos/console_fingerprint_ledger.py` | **Rollback anchor.** Written by proof_gate ONLY on CLEAN. | **Loop NEVER writes the ledger and never forges rollback lineage.** `rollback_token_hash` is set by proof_gate/console-builder from a ledger-known fingerprint; the console enforces ledger membership (step 4 V15). Attempted ledger write or hand-crafted rollback token by the loop is a harness failure (H6/H15). |
| `scripts/console_server.py` + `chaos/console_evidence_gate.py` (step 4) | **Sign-off authority.** Loop calls `POST /validate`; a VALID verdict is the loop's success terminal. | Loop terminates at VALID (bundle staged) OR at the operator ACCEPTED record. Loop holds no operator key, performs no sign, cannot self-approve. Staging a bundle is NOT authorization to promote (H16). |
| `chaos/mmi_control_envelope.py` (step 3) | **Per-tick governor.** Loop calls `pre_iteration_gate()` before every state transition that consumes budget. | Ordering latch → heartbeat/halt → budget honored. Loop CANNOT advance `ack_seq`, clear HALT/SUSPEND, raise caps, or write the ledger. On HALT/SUSPEND the episode goes terminal `HALTED` immediately (H11). |
| `chaos/console_ack_adapter.py` (step 4) | **Human presence source.** | Resume/ack come only from signed `SIGN_ACK`/`SIGN_RESUME` records via the adapter. Loop never synthesizes presence. |
| Authority repo (`/mnt/c/Architectapp_clean`) | Read-only. | Loop opens repo paths read-only; all writes path-prefix-checked against `EPISODE_ROOT`/`PATCH_CONTEXT_ROOT` (H9). No apply, no promote, ever (§9). |

**Why `ops/` not `scripts/`:** `scripts/` in this repo holds operator-invoked, single-purpose tools (harnesses, clients, provisioners). The realignment loop is an *orchestration surface* that composes multiple governed subsystems and carries episode lifecycle state — it belongs with operational orchestrators, not one-shot scripts. Placing it in `ops/` also creates a bright line for future review policy: everything under `ops/` composes authority-bearing gates and gets stricter change control than `scripts/`.² The AGI pathway names the `ops/` path; this justifies it rather than re-litigating.

---

## 3. LOOP STATE MACHINE

Single episode, deterministic, one breach in → one terminal state out. Every transition is preceded by `pre_iteration_gate()` and appends an audit line before the transition commits.

```
        ┌────────────┐
        │   INIT     │  episode_id minted; incident_id replay-checked against EPISODE_LEDGER (H17)
        └─────┬──────┘  breach descriptor loaded READ-ONLY
              │ pre_iteration_gate OK
              ▼
        ┌────────────┐
        │ DISSECTING │  route_to_mirror → assert containment root == MIRROR_LAB_ROOT (H13)
        └─────┬──────┘  harvest_exploit_telemetry  (timeout → TIMED_OUT)
              │ telemetry captured
              ▼
        ┌─────────────┐
        │ SYNTHESIZING│ build genomic_constraint_v1 (typed, ALLOWED_CONSTRAINT_TYPES)
        └─────┬───────┘ → action_integrity_gate schema + capability check
              │ PASS (fail → SYNTHESIZING, attempt++; capability fail → REJECTED)
              ▼
        ┌────────────┐
        │  PROVING   │  write COMPLETE patch_context; proof_gate_harness --console-bindings
        └─────┬──────┘  (partial/fragment constraint forbidden — H8b anti-salami)
              │ overall_gate_status?
       CLEAN  │           BLOCKED
              ▼             │  attempt < MAX_SYNTH_ATTEMPTS → SYNTHESIZING (attempt++)
        ┌────────────┐     │  attempt == MAX_SYNTH_ATTEMPTS → EXHAUSTED (terminal)
        │ PRESENTING │◄────┘  bind + freshness check summary to THIS episode (H14)
        └─────┬──────┘  console_bundle_builder; console_server POST /validate
              │ verdict?
      VALID   │            REJECTED → terminal REJECTED (fail closed)
              ▼
        ┌────────────┐
        │  AWAITING  │  bundle staged; poll ConsoleAckAdapter for operator ACCEPTED
        │  SIGNOFF   │  (v1: may terminate here as VALID_STAGED — NOT an apply authorization)
        └─────┬──────┘
              │ operator Ed25519 ACCEPTED record observed (optional in v1)
              ▼
        ┌────────────┐
        │   SIGNED   │  TERMINAL — signoff record exists; apply/promote is DOWNSTREAM (H16)
        └────────────┘

Terminal states: SIGNED, VALID_STAGED, REJECTED, EXHAUSTED, TIMED_OUT, HALTED, ERROR
On reaching any terminal: append (incident_id, episode_id) to EPISODE_LEDGER (single-use).
```

Any `pre_iteration_gate()` returning HALT/SUSPEND at any transition → **HALTED** (terminal). Any unhandled exception / callee error → **ERROR** (terminal, fail closed). No terminal state applies a patch.

---

## 4. PATCH / CONSTRAINT ARTIFACT SCHEMA

### 4.1 `genomic_constraint_v1` (the synthesized behavioral constraint)

```json
{
  "artifact_version": "genomic_constraint_v1",
  "constraint_id": "grc-<sha256(canonical artifact minus constraint_id)[:16]>",
  "episode_id": "gre-...",
  "incident_id": "<from breach descriptor — replay-guarded (H17)>",
  "created_at_ms": 1782200000000,
  "breach_ref": {
    "critic_node": "<breached critic id>",
    "exploit_id": "<scenario id from purple_evasion_suite / harvest>",
    "mirror_agent_id": "<agent routed to mirror>",
    "mirror_containment_root": "/tmp/mmi_mirror_dimension/..."
  },
  "constraint_type": "action_deny",
  "constraint_completeness": "complete_single_bundle",
  "constraint_body": {
    "target": "<action / route / param the constraint binds>",
    "rule": "<typed, declarative — e.g. deny|clamp[min,max]|rate[n_per_window]|isolate|schema>",
    "params": { "...": "typed scalars/ints only, no code" }
  },
  "provenance": {
    "harvest_digest": "<sha256 of harvest telemetry that motivated this>",
    "synth_attempt": 1
  }
}
```

**Hard schema rules (enforced by action_integrity_gate before write):**
- `constraint_type` ∈ `ALLOWED_CONSTRAINT_TYPES` — closed enum; anything else → `ARTIFACT_SCHEMA_FAIL`.
- Every `constraint_body.target` must resolve to a **registered** action_integrity capability; unregistered → `CAPABILITY_UNREGISTERED` (H8).
- `constraint_body` is **declarative typed data only** — no executable strings, no eval targets, no code fields. A constraint is a rule the runtime *interprets*, never code the runtime *runs* (§9 non-goal, AGI §6).
- Integers/scalars only in `params`; no floats in anything hashed into the Gate B / manifest chain.
- Serialized artifact ≤ `MAX_CONSTRAINT_BYTES`.
- `constraint_id` must recompute (self-consistency), mirroring console bundle_id discipline.
- `constraint_completeness` MUST be `"complete_single_bundle"` — a fragment/partial constraint is invalid. Anti-salami (H8b): the full behavioral change for a breach is proven as one bundle against the full suite; it cannot be split into sub-patches that each individually pass regression while the composite is harmful.

### 4.2 Episode state (`EPISODE_STATE_PATH`, atomic write)

```json
{
  "episode_id": "gre-...",
  "incident_id": "...",
  "state": "PROVING",
  "breach_ref": { "...": "..." },
  "constraint_id": "grc-...",
  "synth_attempt": 1,
  "patch_context_dir": "/tmp/mmi_genomic_loop/patch_ctx/gre-.../",
  "patch_context_digest": "<sha256 of patch context tree>",
  "proof_gate_summary_path": "/tmp/mmi_proof_gate/.../proof_gate_summary.json",
  "proof_gate_summary_digest": null,
  "proof_gate_status": null,
  "console_verdict": null,
  "signoff_record_path": null,
  "started_at_ms": 1782200000000,
  "updated_at_ms": 1782200000000,
  "terminal": false
}
```

### 4.3 Evidence bundle handed to console

The loop does **not** invent bundle fields. It calls the existing `console_bundle_builder` (step 4) over the CLEAN proof_gate summary + patch context. The bundle is the step-4 `console_evidence_v1` schema unchanged; the loop's only inputs are the summary path and patch context. This guarantees the loop cannot smuggle fields past the console's V0–V16, cannot forge `rollback_token_hash` (builder sources it from the ledger-known fingerprint), and cannot present a summary that fails the console's own freshness/binding rules.

### 4.4 Audit log — JSONL, append-only, hash-chained

```json
{"ts_ms":1782200000000,"episode_id":"gre-...","incident_id":"...","event":"STATE|SYNTH|PROOF|PRESENT","from":"SYNTHESIZING","to":"PROVING","detail":"...","constraint_id":"grc-...","prev_line_hash":"<sha256 prev line>"}
```

Genesis `prev_line_hash` = 64 zeros. Truncation/deletion detectable by linear scan (mirrors console step-4 H8).

---

## 5. INTEGRATION CALL ORDER

```
CLI: genomic_realignment_loop run --breach <descriptor.json>       (v1 entrypoint)
  │
  ├─ INIT: mint episode_id; load breach descriptor READ-ONLY from EPISODE_ROOT/inbox
  │        replay guard: (incident_id) absent from EPISODE_LEDGER else REJECTED (H17)
  │
  ├─ pre_iteration_gate()  ── HALT/SUSPEND ─► HALTED (terminal)
  │
  ├─ DISSECTING:
  │     route_to_mirror(agent_id, payload)          # isolated copy only
  │     assert containment_root under MIRROR_LAB_ROOT else ERROR (H13)
  │     harvest_exploit_telemetry(agent_id)         # read-only, from mirror root
  │
  ├─ pre_iteration_gate()
  ├─ SYNTHESIZING:
  │     build genomic_constraint_v1 (typed, complete_single_bundle)
  │     action_integrity_gate.validate(artifact)    # schema + registered capability
  │        schema fail ─► retry (attempt++) or EXHAUSTED
  │        capability fail ─► REJECTED (terminal)
  │     write COMPLETE artifact + patch files → PATCH_CONTEXT_ROOT/<episode_id>/  (OUTSIDE repo)
  │     record patch_context_digest
  │
  ├─ pre_iteration_gate()
  ├─ PROVING:
  │     proof_gate_harness --console-bindings --patch-context <dir>
  │     read proof_gate_summary.json; record proof_gate_summary_digest
  │        BLOCKED ─► retry (attempt++) or EXHAUSTED
  │        CLEAN   ─► (proof_gate appends console_fingerprint_ledger — NOT the loop)
  │
  ├─ pre_iteration_gate()
  ├─ PRESENTING:
  │     bind check: summary references THIS episode's constraint_id + patch_context_digest,
  │                 and summary age ≤ PROOF_SUMMARY_MAX_AGE_MS   (H14) else REJECTED
  │     console_bundle_builder over CLEAN summary + patch context
  │     POST http://127.0.0.1:<console>/api/v1/evidence-bundle/validate
  │        REJECTED ─► REJECTED (terminal, fail closed)
  │        VALID    ─► bundle staged  (NOT an apply authorization — H16)
  │
  ├─ AWAITING_SIGNOFF:
  │     v1 default: terminate VALID_STAGED (hand off to operator out-of-band)
  │     optional: poll ConsoleAckAdapter for operator Ed25519 ACCEPTED record
  │        observed ─► SIGNED (terminal)
  │
  ├─ TERMINAL: append (incident_id, episode_id) to EPISODE_LEDGER (single-use, H17)
  │
  └─ DOWNSTREAM (OUT OF SCOPE, §9): promote tooling re-verifies signoff (step-4 H5),
        checks patch_hash, consume-once, then applies. The loop never touches this.
```

The loop's success is **"produced a VALID/SIGNED bundle through the real gates,"** never "changed the system." The apply boundary is owned entirely by downstream tooling that independently re-verifies the Ed25519 signature.

---

## 6. PASS / FAIL LINES + HARD RULES

### 6.1 Episode PASS / FAIL lines

- **PASS (v1):** episode reaches `VALID_STAGED` or `SIGNED` with a matching, fresh, episode-bound proof_gate CLEAN summary, a console VALID verdict, and a complete hash-chained audit trail. Nothing applied.
- **FAIL / non-pass terminals:** `REJECTED`, `EXHAUSTED`, `TIMED_OUT`, `HALTED`, `ERROR`. All fail closed; none apply a patch. A non-pass terminal is a valid, honest outcome — not something to be papered over.

### 6.2 Hard rules (enforced by callees + loop code, not prose)

- **H1 — Fail closed.** Any callee error, timeout, parse failure, or unexpected exception → terminal `ERROR`/`TIMED_OUT`. No warn-and-continue, no "assume CLEAN."
- **H2 — No self-certification.** The loop NEVER derives proof-of-fix or proof-of-no-regression from its own execution. Both come exclusively from the proof_gate summary. Loop reading `purple_evasion_suite` results to grade itself is forbidden and statically checked (H2 lint).
- **H3 — No Gate B bypass.** The only path to PRESENTING is a proof_gate summary with `overall_gate_status == "CLEAN"` written by the harness, digest-recorded at read time. The loop cannot synthesize, edit, or backdate a summary; presenting without a recorded `proof_gate_summary_digest` is a harness failure.
- **H4 — No console bypass / no self-sign.** Loop holds no operator private key (H4 lint: no signing-primitive import), performs no signature, terminates at VALID or at an operator-produced ACCEPTED record only.
- **H5 — No apply, no promote.** No code path in `genomic_realignment_loop.py` writes to the authority repo or invokes promote tooling. Apply is downstream and re-verifies independently. Presence of an apply/promote call in the module is a harness failure.
- **H6 — Loop cannot write governed ledgers/state.** No write to `console_fingerprint_ledger`, no `ack_seq` advance, no HALT/SUSPEND clear, no cap raise. Attempted write → harness failure.
- **H7 — Regression truth is external.** Proof-of-no-regression = full `purple_evasion_suite` green **as reported by the proof_gate summary**, never a loop-local run.
- **H8 — Constraints are data within registered capabilities.** Only `ALLOWED_CONSTRAINT_TYPES` typed declarative artifacts, each `target` a **registered** action_integrity capability; action_integrity_gate rejects anything else. No arbitrary/self-authored runtime code, no invented capability surface (AGI §6).
- **H8b — Anti-salami.** One episode = one breach_ref = one `complete_single_bundle` constraint, proven against the FULL suite. The loop cannot split a logical change into fragments that each pass regression individually. Composite constraints must be proven as a single bundle; `constraint_completeness != "complete_single_bundle"` → rejected pre-proof.
- **H9 — All evidence outside authority repo.** `EPISODE_ROOT`, `PATCH_CONTEXT_ROOT`, `MIRROR_LAB_ROOT`, audit, state all under `/tmp/...`; path-prefix-checked. Authority repo opened read-only only. Any write whose resolved path escapes the allowed roots → harness failure.
- **H10 — Bounded episode.** `MAX_SYNTH_ATTEMPTS` and `EPISODE_TTL_MS` cap every episode; no unbounded retry, no infinite loop. Autonomous continuous mode absent in v1 (LOOP_MODE fixed).
- **H11 — Governor every tick.** `pre_iteration_gate()` is called before every budget-consuming transition, honoring latch → heartbeat/halt → budget ordering. HALT/SUSPEND → immediate terminal `HALTED`; continuing past a HALTED gate is a harness failure. A tick that skips the gate is a harness failure.
- **H12 — Hash-chained audit.** Every transition appends a chained audit line before committing; broken chain is detectable and is a harness failure.
- **H13 — Mirror isolation.** Dissection and harvest occur ONLY against `MIRROR_LAB_ROOT`. `route_to_mirror` containment metadata must confirm the isolated root; harvest that resolves to any authority path → terminal `ERROR`. The loop never reads exploit telemetry from `AUTHORITY_REPO`.
- **H14 — Summary freshness + episode binding.** Before PRESENTING, the proof_gate summary must (a) reference THIS episode's `constraint_id` and `patch_context_digest`, and (b) be no older than `PROOF_SUMMARY_MAX_AGE_MS`. A stale or mismatched summary (V14-class replay) → `REJECTED`. Prevents reuse of an old CLEAN summary for a new/different patch.
- **H15 — No forged rollback lineage.** `rollback_token_hash` is never hand-authored by the loop; it is sourced by the bundle builder from a `console_fingerprint_ledger`-known fingerprint and independently enforced by console V15. The loop supplying its own rollback token → harness failure.
- **H16 — Staging ≠ authorization.** A console VALID verdict / staged bundle is NOT permission to promote. Only a downstream, re-verified, consume-once Ed25519 signoff record authorizes apply (step-4 H5). The loop must never describe VALID_STAGED as "applied," "authorized," or "promoted" in any emitted field or log.
- **H17 — Incident replay guard.** Each `incident_id` is single-use: checked against `EPISODE_LEDGER_PATH` at INIT and appended at terminal. A replayed incident_id → `REJECTED`. Prevents re-running an old incident to manufacture a fresh-looking signoff.
- **H18 — No status inflation.** The loop MUST NOT emit `PERFECT`, `Phase 3`, `30-day`, `M4`, or any maturity/continuous-operation claim in any artifact, log, or summary. Emitting such a claim is a harness failure. Project maturity is asserted only by human closeout docs, never by the loop.

---

## 7. FALSIFIABLE TEST SCENARIOS

| ID | Setup | Expected terminal | Expected transitions / evidence |
|---|---|---|---|
| **T1 — happy path** | Real breach; mirror harvest succeeds from `MIRROR_LAB_ROOT`; `action_deny` constraint passes action_integrity; proof_gate CLEAN, summary binds episode; console VALID | `VALID_STAGED` (and `SIGNED` if operator signs) | Full transition chain; CLEAN summary present + episode-bound + fresh; console VALID; ledger appended by proof_gate (NOT loop); incident_id appended to EPISODE_LEDGER; chained audit intact |
| **T2 — proof BLOCKED then exhausted** | Constraint fails to contain exploit; proof_gate BLOCKED every attempt | `EXHAUSTED` after `MAX_SYNTH_ATTEMPTS` | PROVING→SYNTHESIZING exactly `MAX_SYNTH_ATTEMPTS` times; no console call; no bundle; nothing applied; proves H3 |
| **T3 — anti-self-certify** | Loop instrumented to self-grade via `purple_evasion_suite` (claims green) while proof_gate returns BLOCKED | non-pass; H2/H7 lint FAIL flagged | Self-report ignored; only proof_gate summary consulted; static check catches forbidden path; no CLEAN manufactured |
| **T4 — governor HALT mid-episode** | `pre_iteration_gate()` returns HALT during PROVING | `HALTED` (terminal) | Episode stops at the gate; no further transition; no console call; nothing applied; proves H11 |
| **T5 — out-of-envelope / code-smuggling** | Synthesis emits (a) `constraint_type` outside enum; (b) `constraint_body` with an executable string; (c) `target` on an unregistered capability | `REJECTED` (`ARTIFACT_SCHEMA_FAIL` / `CAPABILITY_UNREGISTERED`) | action_integrity rejects pre-proof; artifact never written; proof_gate never invoked; proves H8 + closed enum |
| **T6 — stale/replayed proof + incident** | (a) Present a CLEAN summary older than `PROOF_SUMMARY_MAX_AGE_MS` or bound to a different constraint_id; (b) re-run an `incident_id` already in `EPISODE_LEDGER` | (a) `REJECTED` (H14); (b) `REJECTED` at INIT (H17) | No bundle staged for (a); episode never leaves INIT for (b); proves V14-class + replay guards; no reuse of old CLEAN for new patch |
| **T7 — mirror-escape + salami + rollback-forge** | (a) `route_to_mirror` containment root points at an authority path; (b) constraint marked as a fragment (`constraint_completeness != complete_single_bundle`); (c) loop attempts to author `rollback_token_hash` / write fingerprint ledger | `ERROR`/`REJECTED`; H6/H8b/H13/H15 flagged | (a) harvest refused, terminal ERROR; (b) rejected pre-proof; (c) harness catches ledger write + hand-authored token; nothing applied, no forged lineage |

Each scenario is falsifiable: a wrong terminal state, a manufactured CLEAN, a written/forged ledger entry, an applied patch, a mirror-escape harvest, a stale/replayed summary accepted, a broken audit chain, or a skipped `pre_iteration_gate()` is a hard harness failure.

---

## 8. HARNESS SPEC — `scripts/genomic_realignment_loop_harness.py`

Mirrors `proof_gate_harness` / `control_envelope_harness` / `console_server_harness` patterns:

- Drives the loop through T1–T7 with fabricated breach descriptors and stubbed-but-faithful callees (mirror router, proof_gate, console) under `EPISODE_ROOT` / `MIRROR_LAB_ROOT`.
- Uses the **real** `action_integrity_gate` for T5/T7(b) (schema + capability truth must not be stubbed).
- Structural / static checks:
  - **H2/H4/H5 lint** — module source contains no self-grading `purple_evasion_suite` grade path, no signing-primitive import, no apply/promote call.
  - **H6/H15** — no write to `console_fingerprint_ledger` / control-envelope governed state; no hand-authored `rollback_token_hash`.
  - **H9/H13** — no write outside allowed `/tmp` roots; no harvest/read resolving to `AUTHORITY_REPO`.
  - **H11** — `pre_iteration_gate()` invoked before every budget-consuming transition (call-count assertion); no transition past a HALTED gate.
  - **H12** — audit hash chain verifies end-to-end.
  - **H14/H17** — stale/mismatched summary rejected; replayed incident_id rejected.
  - **H18** — emitted artifacts/logs contain no `PERFECT|Phase 3|30-day|M4` maturity claim (denylist scan).
- Emits `EPISODE_ROOT/harness/genomic_loop_summary.json`:

```json
{
  "suite": "genomic_loop_v1",
  "timestamp": "<iso>",
  "scenarios": {"T1":"PASS","T2":"PASS","T3":"PASS","T4":"PASS","T5":"PASS","T6":"PASS","T7":"PASS",
                "H2":"PASS","H4":"PASS","H5":"PASS","H6":"PASS","H9":"PASS","H11":"PASS",
                "H12":"PASS","H13":"PASS","H14":"PASS","H15":"PASS","H17":"PASS","H18":"PASS"},
  "overall_gate_status": "CLEAN",
  "blockers": [],
  "evidence_dir": "/tmp/mmi_genomic_loop/harness/"
}
```

- **Exit 0 iff `overall_gate_status == "CLEAN"`** (every scenario + structural check PASS). Any failure → `BLOCKED`, blockers listed, exit 1. Binary, un-fakeable — no partial pass rate, no averaging.

---

## 9. NON-GOALS

- **24/7 autonomous loop** — deferred to v2, gated on M4 48h proof (OUTSTANDING). v1 is CLI-incident only.
- **Apply / promote to authority repo** — downstream tooling only; it independently re-verifies the Ed25519 signoff (step-4 H5), checks `patch_hash`, and consumes once. The loop never applies; staging is never authorization (H16).
- **`central_brain.py` (AGI step 6)** — not designed here.
- **Unbounded / self-authored runtime code** — explicit AGI §6 non-goal; constraints are typed declarative data on registered capabilities only (H8/H8b).
- **Re-designing proof_gate, control_envelope, console, mirror, action_integrity** — the loop wires them; it does not modify or re-litigate them.
- **Writing the console fingerprint ledger / rollback lineage** — owned by proof_gate (H6/H15).
- **Host boundary Go daemon / M4 continuous assault / PERFECT / 30-day / Phase 3 claims** — evolution gate remains OUTSTANDING; the loop is forbidden from asserting any of them (H18).

---

## 4.5 Breach descriptor v1 (`breach_descriptor_v1`)

Input file: `EPISODE_ROOT/inbox/<incident_id>.json`

```json
{
  "descriptor_version": "breach_descriptor_v1",
  "incident_id": "inc-<unique>",
  "critic_node": "<breached critic id>",
  "exploit_id": "<purple scenario id>",
  "mirror_agent_id": "<agent routed to mirror>",
  "payload": "<hostile payload string for route_to_mirror>"
}
```

Validated by `genomic_constraint_synth.validate_breach_descriptor()`.

Harness fixtures: `/tmp/mmi_genomic_loop/harness/fixtures/breach_descriptor_v1.json`.

---

## 4.6 v1 synthesis stub (deterministic — no LLM)

Implementation: `chaos/genomic_constraint_synth.py` — `synthesize_constraint_v1(harvest, breach_descriptor, episode_id=...)`.

Fixed mapping table `exploit_id → constraint_type + registered capability target`. Same harvest + descriptor → same `constraint_id` (harness reproducibility).

Writes `patch_context_dir/genomic_constraint.json` + `proof_context.json` via `write_constraint_artifact()`.

Validated by `genomic_constraint_validator.validate_genomic_constraint()` before proof_gate invoke.

---

## FOOTNOTES (assumptions)

1. v1 deliberately terminates at VALID_STAGED (or SIGNED if an operator signs in-episode). This is honest scope: the genomic chain is proven end-to-end through Gate B + console without asserting continuous autonomy or an apply capability the project has not authorized.
2. `ops/` vs `scripts/` is a placement + change-control assertion, not functional. If the repo lacks an `ops/` convention at build time, the constant/path is the only thing that moves; every H-rule holds regardless of directory.
3. Callees are assumed to behave per their CLEAN specs (step 2/3/4). The loop treats every callee verdict as authoritative and fails closed on any callee error; it does not "correct" or second-guess a callee.
4. Breach descriptor provenance (who declares a critic-node breach) is an input, assumed produced by the existing detection/critic surface. v1 accepts a descriptor file in `EPISODE_ROOT/inbox` carrying an `incident_id`; descriptor authenticity hardening is a separate concern, but replay of a known `incident_id` is already blocked (H17).
5. Summary→episode binding (H14) is implemented in proof_gate bindings r2 §3.6 (`genomic_episode` on summary when `--constraint-id` passed).

---

## REVISION LOG (r1 → r2, adversarial self-review)

| Finding | Fix |
|---|---|
| Skip proof_gate, present patch directly to console | H3 tightened: PRESENTING requires a recorded `proof_gate_summary_digest`; no summary → harness failure. Console independently requires CLEAN (step 4). |
| Self-report proof without invoking suite | H2/H7 unchanged in intent, reinforced with T3 static-lint catch; regression truth is proof_gate summary only. |
| Write patch_context/evidence inside authority repo | H9 hardened: resolved-path prefix check on every write; escape → harness failure. |
| Append fingerprint ledger / forge rollback lineage (V15 class) | H15 added: loop never authors `rollback_token_hash`; builder sources it from ledger; console V15 enforces membership. H6 covers ledger write. |
| Auto-apply without consumed signoff (H5 bypass) | H16 added: staging ≠ authorization; only downstream re-verified consume-once signoff applies. |
| Advance ack_seq / clear HALT / raise caps from loop | H6 (unchanged) + H11 hardened: immediate terminal HALTED, no transition past a HALTED gate. |
| Unbounded arbitrary code outside registered capabilities | H8 extended: `target` must be a registered action_integrity capability (`CAPABILITY_UNREGISTERED`); T5(c) added. |
| Replay incident_id / stale Gate B summary (V14 freshness) | H14 (summary freshness + episode binding) + H17 (incident replay guard via `EPISODE_LEDGER_PATH`); T6 added. |
| Harvest telemetry from authority paths not mirror | H13 added: containment root must be `MIRROR_LAB_ROOT`; authority-path harvest → ERROR; T7(a) added. |
| Continue running when pre_iteration_gate HALTED | H11 hardened (see above); T4 already covered, assertion strengthened. |
| Confuse staging with promote authorization | H16 added; language ban on "applied/authorized/promoted" for VALID_STAGED. |
| Claim Phase 3 / PERFECT / 30-day in v1 | H18 added: maturity-claim denylist, harness scan; §9 reinforced. |
| Split patch across small changes to evade regression | H8b anti-salami added: one breach = one `complete_single_bundle`, proven against full suite; fragments rejected pre-proof; T7(b) added. |

---

**SIGN-OFF:** `[ ] PASS  [x] PASS WITH REVISIONS  [ ] FAIL` — material hardening applied in r2 (H8b, H13–H18, T6–T7, freshness/replay/mirror-isolation/anti-salami/status-inflation guards). Two design calls still warrant reviewer ratification before build: (a) v1 terminating at `VALID_STAGED` rather than requiring in-episode SIGNED, and (b) the `ops/` placement + stricter change-control assertion. Neither affects any H-rule. Spec author: Claude (Design), 2026-07-03.
