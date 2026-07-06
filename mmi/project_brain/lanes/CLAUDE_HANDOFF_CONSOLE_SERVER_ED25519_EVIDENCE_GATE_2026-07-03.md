# Claude Handoff — AGI §5 Step 4 Console Server Ed25519 Evidence-Gate

**Task id:** `mmi-console-server-ed25519-evidence-gate-spec`  
**Assignee:** Claude (Design)  
**Build auth:** NOT_AUTHORIZED — **spec only**  
**Framework:** `lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md`

**Evidence basis (macro AGI ladder):** Steps 1–3 CLOSED (Phase 1 PASS, Gate B Codex CLEAN, control envelope Codex CLEAN). Step 4 is the only macro candidate with full dependency clearance per `status/MMI_MACRO_BUILD_DECISION_2026-07-03.md`.

**Two-message workflow (mandatory):**
1. Paste **MESSAGE 1** below into a fresh Claude window — generation pass.
2. After Claude returns the spec, paste **MESSAGE 2** — adversarial self-review pass.
3. Relay **final revised spec** to Cursor for closeout. Do not skip MESSAGE 2.

---

## MESSAGE 1 — Generate spec (paste this first)

```
PROJECT: MMI
TASK ID: mmi-console-server-ed25519-evidence-gate-spec
ASSIGNEE: Claude (Design)
SCORE: 92
BUILD AUTHORIZATION: NOT_AUTHORIZED — spec only, no implementation
PROMPT FRAMEWORK: mmi/project_brain/lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md

<system_role>
Lead Cybernetic Architect / Purple Team Engineer
Project: Mutant Monkey Intelligence (MMI) — systems-domain AGI matrix
Doctrine: Bounded autonomy, strict deterministic rules over soft prompts, un-fakeable metrics
Design lane only — deliver one bounded markdown spec. No implementation. No scope expansion.
</system_role>

<current_state_inventory>
Repo root: /mnt/c/MMI
Phase 1 weapon stack: PASS (tiers [4,4,4] — do not re-litigate)
Gate B proof gate: BUILT + Codex CLEAN (do not re-litigate)
Control envelope step 3: BUILT + Codex CLEAN — budget/dead-man + sticky latch
Evolution gate: OUTSTANDING — 48h proof NOT built; cannot claim PERFECT

Prereqs CLOSED (step 4 dependencies):
  - scripts/proof_gate_harness.py — Gate B; produces proof_gate_summary.json with overall_gate_status
  - chaos/weapon_battlefield_scoring.py — generate_proof_bundle(), fingerprint_digest()
  - chaos/mmi_control_envelope.py — human_advance_ack / human_clear_* ; §1.3 ack channel shaped for Ed25519 signed writer (step 4 replaces file-based interim)
  - chaos/metadata_ingress_gate.py — Ed25519 verify pattern (cryptography Ed25519PrivateKey/PublicKey)

Partial console (telemetry only — NOT the evidence gate):
  - scripts/kinetic_war_room_server.py — FastAPI, 127.0.0.1 bind, WebSocket telemetry, patch preview HTML
  - architecture/MMI_KINETIC_WARFARE_DASHBOARD_SPEC_2026-07.md — [EXECUTE IMMUNIZATION] Ed25519 button NOT BUILT

Doctrine (authoritative):
  - architecture/MMI_AGI_EVOLUTION_PATHWAY.md — §2 Pillar 4 (Asymmetric Signature Gate), §5 step 4
  - architecture/MMI_DIFFERENTIATOR_2026-07.md — §2 Proof before signature
  - architecture/MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md — §2 future console_server ack channel
  - lanes/RESEARCH_LUNG_V2_REFACTOR_2026-06.md — Ed25519 asymmetric verify, replay window (research reference only)

NOT BUILT (out of scope for this spec):
  - scripts/console_server.py — TARGET of this spec (does not exist yet)
  - genomic_realignment_loop.py (AGI step 5)
  - central_brain.py (AGI step 6)
  - Host boundary Go daemon, M4 48h proof
</current_state_inventory>

<existing_implementation_pattern>
Gate B proof bundle writer (weapon_battlefield_scoring.py):

    def generate_proof_bundle(summary_data: dict, evidence_dir: Path) -> dict:
        bundle = {"suite": "proof_gate_v1", **summary_data}
        # atomic write to evidence_dir / proof_gate_summary.json
        return bundle

Gate B summary fields (proof_gate_harness.py output shape):
  fix_id, timestamp, authority_hash, authority_intact, regression_verdict,
  fix_verdict, overall_gate_status (CLEAN|BLOCKED), blockers[],
  proof_of_fix, proof_of_regression, evidence_dir, authority_fingerprint_after_digest

AGI Pillar 4 — fixed evidence bundle the human signature MUST cover:
  1. hash of exact patch (prompt/config diff)
  2. proof-of-fix result (which exploit, now contained)
  3. proof-of-no-regression result (full suite still green)
  4. rollback token (hash of pre-patch known-good state)
  5. budget/telemetry snapshot for the run that produced it

Hard rule: signature over patch with failed or missing proof bundle is REJECTED by the gate —
cannot sign unsafe change even if operator wants to.

Control envelope §1.3 ack channel (interim → step 4):
  - Human ack via monotonic ack_seq — loop cannot write
  - Step 4: Ed25519 signed writer replaces file-based human_advance_ack for attendance/resume

Ed25519 verify pattern (metadata_ingress_gate.py family):
  - Ed25519PublicKey.from_public_bytes / verify
  - Canonical manifest binds payload via sha256
  - Fail-closed on InvalidSignature

Kinetic console server patterns to mirror (structure only):
  - FastAPI, default bind 127.0.0.1
  - Evidence/audit paths outside authority repo (/tmp/...)
  - Local chaos lab only — not production deploy authority
</existing_implementation_pattern>

<task_definition>
Write the complete markdown spec file:

  mmi/project_brain/architecture/MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md

Scope — AGI §5 step 4 only: scripts/console_server.py Ed25519 evidence-gate

1. OPERATIONAL DEFINITION
   - What the console gate does: present evidence bundle, verify proofs BEFORE accept, bind Ed25519 signature to canonical manifest
   - Operator signs evidence, not intent
   - Constants table (replay window ms, max bundle bytes, audit paths under /tmp/mmi_console_server/)

2. EVIDENCE BUNDLE SCHEMA (canonical, versioned)
   - Required fields mapping to AGI Pillar 4 five elements
   - Input: Gate B proof_gate_summary.json (overall_gate_status must be CLEAN to sign)
   - patch_hash, proof_of_fix_ref, proof_of_regression_ref, rollback_token_hash, budget_telemetry_snapshot
   - Canonical JSON serialization rules for signature (sort_keys, no float drift)
   - bundle_id, bundle_version, operator_action enum (SIGN_PROMOTE | SIGN_RESUME | SIGN_ACK)

3. SIGN / VERIFY API CONTRACT
   - POST /api/v1/evidence-bundle/validate — read-only; returns VALID|REJECTED + reasons[]
   - POST /api/v1/evidence-bundle/sign — requires operator Ed25519 signature over manifest; server verify-only holds Matt public key
   - GET /api/v1/evidence-bundle/{bundle_id} — staging review (side-by-side diff view data model)
   - Reject paths: overall_gate_status != CLEAN, missing field, hash mismatch, stale replay, authority_intact false
   - Signed output: console_signoff_record.json outside authority repo

4. INTEGRATION SKETCH
   - Gate B → bundle ingest → validate → human review UI → sign → audit log
   - Wire to mmi_control_envelope: signed ack/resume/window-reset replaces human_advance_ack file writes (define adapter interface only)
   - Relationship to kinetic_war_room_server.py: extend vs separate process — pick one, justify
   - Private key NEVER on server; sign happens client-side or isolated operator step; server verify-only

5. PASS / FAIL LINES + HARD RULES
   - Fail-closed: any missing proof → REJECTED (no sign)
   - Signature covers full manifest hash, not free-text intent
   - Replay: monotonic sign_seq or nonce persisted outside authority
   - Authority repo read-only during validate/sign flows
   - No promote/apply until sign record exists

6. FALSIFIABLE TEST SCENARIOS T1–T3
   - T1: CLEAN Gate B bundle → validate PASS → sign accepted → audit record exists
   - T2: BLOCKED or tampered bundle → validate REJECTED → sign endpoint refuses even with valid Ed25519 sig over wrong manifest
   - T3: Replay / stale timestamp / manifest field swap → REJECTED

7. HARNESS SPEC
   - scripts/console_server_harness.py (name fixed) — mirror proof_gate_harness + control_envelope_harness patterns
   - Exit 0 + overall_gate_status CLEAN; evidence under /tmp/mmi_console_server/

8. NON-GOALS
   - genomic_realignment_loop (step 5)
   - central_brain Phase 2 (step 6)
   - Production orchestrator auto-apply
   - Private key storage on server
   - Replacing metadata_ingress_gate agent packet signing
   - M4 / PERFECT claims

Required spec sections (mirror control envelope / iceberg L5/L7 layout):
  1. Operational Definition (+ constants table)
  2. Boundary vs Adjacent Systems (proof_gate, control_envelope, kinetic_war_room, metadata_ingress)
  3. Pass / Fail Lines (+ hard rules)
  4. Data Schema (bundle, manifest, signoff record, audit log)
  5. Integration Sketch (diagram or call order)
  6. Falsifiable Test Scenarios T1–T3
  7. Non-Goals
  Footnotes for assumptions
  SIGN-OFF line: PASS | PASS WITH REVISIONS | FAIL
</task_definition>

<execution_constraints>
1. Deliver the complete markdown spec file only — no chat intro, no closeout prose.
2. Spec-only. No Python. No tasks.json edits. No build authorization.
3. Every threshold must be a named constant — no ML, no soft prompts.
4. Evidence/audit paths must stay outside authority repo (/tmp/... pattern).
5. Three falsifiable T1–T3 scenarios with expected verdict + route.
6. MMI hard stops: no unbounded self-modification, no fake pass rates, no scope outside task_definition.
7. Explicitly define how gate rejects "sign intent only" attacks (operator haste / machine bypass).
</execution_constraints>

<no_explanations_directive>
Respond with the production-grade markdown spec file payload only. Assumptions go in spec footnotes — not chat prose.
</no_explanations_directive>
```

---

## MESSAGE 2 — Adversarial self-review (paste after MESSAGE 1 output)

```
<review_mode>
You just wrote MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md.

Adversarial self-review — assume a hostile operator OR a compromised loop trying to:
- Sign a patch without a passing Gate B proof (overall_gate_status != CLEAN)
- Sign a subset of the evidence bundle while omitting failed proof-of-regression
- Replay an old valid signoff record to authorize a new patch
- Swap manifest fields after signature (field reorder, hash substitution)
- Use a valid Ed25519 signature over a different manifest than displayed in UI
- Bypass the gate via kinetic_war_room_server telemetry endpoints
- Store or exfiltrate Matt's private key through the server process
- Confuse AFE display metrics with signoff authority
- Auto-promote to authority repo without signed audit record
- Forge rollback_token or patch_hash while proofs fail

Fix every finding inline. Output the COMPLETE revised spec file (not a diff). Update SIGN-OFF to PASS WITH REVISIONS if you changed anything material.
</review_mode>
```

---

## Closeout checklist (Cursor PM)

- [x] Spec path: `architecture/MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md`
- [x] SIGN-OFF: PASS WITH REVISIONS (r2)
- [x] T1–T3 falsifiable scenarios present (+ T2a–d, T3a–e sub-cases)
- [x] Five Pillar 4 bundle fields explicitly mapped
- [x] Gate rejects sign-on-failed-proof (fail-closed)
- [x] Private key off-server / verify-only server explicit (H6, H10)
- [x] Control envelope ack adapter interface defined (§5.2)
- [ ] Codex plan review → BUILDABLE before Matt `authorize build`
