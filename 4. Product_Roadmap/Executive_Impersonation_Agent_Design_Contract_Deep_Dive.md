# Executive Impersonation Agent Design Contract — Spec-First Deep Dive

**Status:** DRAFT UNSIGNED — Q5 step 3 metadata-only retrofit (Build Sequencer pinned order). Authored 2026-06-25 by Cursor on Matt operator authorization to continue Q5 step 3 after #10 GATED closeout (MMI-DEC-215). Places a full Agent Design Contract over the §11-signed detector blueprint and future `ExecutiveImpersonationAgent` wrapper. **Not** §11 signed; **not** detector implementation; **not** wrapper build until detector exists + explicit Build Authorization; **not** default-registry registration; **not** production dispatch; **not** scoring-pipeline default-on change.

**Owner:** Matt Nichol

**Candidate:** #21 — Executive Impersonation

**Implementation:** **Not built** — detector code absent (`core/scoring/executive_impersonation_detector.py` does not exist). Wrapper path reserved at `core/orchestrator/executive_impersonation_agent.py`. Scoreboard `NEEDS_SIGNED_CONTRACT` pending §11 + detector Build Authorization.

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `4. Product_Roadmap/Executive_Impersonation_Detector_Deep_Dive.md` (§11 SIGNED 2026-06-06 — immutable detector D1–D9 + §10.A)
- `4. Product_Roadmap/Lookalike_Domain_Agent_Design_Contract_Deep_Dive.md` (closest Q5 retrofit peer)
- `4. Product_Roadmap/Ghost_Thread_Agent_Design_Contract_Deep_Dive.md` (Layer 2 peer)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#21 row; Q5 step 3)
- `core/scoring/lookalike_domain_detector.py` (`extract_identity_domains` — reused by detector D4)
- `core/scoring/callback_phishing_detector.py` (TOAD pattern-engine style reference — not imported by detector)
- `VISION.md`

**Build path:** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/executive_impersonation_agent.py` (blocked until detector implementation)

---

## Agent Design Contract block

**Boundary:** This contract governs the Executive Impersonation **agent wrapper** (`ExecutiveImpersonationAgent`). It is additive governance under template §7.0. It does **not** edit, reinterpret, relax, or extend the §11-signed detector contract (`detect_executive_impersonation`, D1–D9, scoring bands/floors, default-off integration posture, or scoring-pipeline wiring). Those remain immutable.

| Field | Value |
|---|---|
| Agent name | Executive Impersonation Agent (`ExecutiveImpersonationAgent`) |
| Swarm inventory ID | #21 — Executive Impersonation (CEO/CFO urgency/secrecy) |
| Canonical layer | 2 — Detection |
| Canonical team / case type | Vendor-payment / BEC; executive-authority impersonation |
| Authority level | Level 3 — Specialist Agent (matches #6 / #8 / #10) |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (see template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic.** Validated on synthetic test data only; intentionally NOT registered in `build_default_registry` / production dispatch. |
| Role | Produce facts-only executive-impersonation evidence by running the deterministic executive-impersonation detector against display name, identity domains, caller-supplied principal roster, and body pressure vocabulary. |
| Boundary | The detector is not the decision. The agent must not decide fraud, approve/deny mail, block/quarantine, change payment behavior, mutate scoring overlays, alter the signed Client-Facing 5-Axis Rubric, or change the LLM `impersonation_likelihood` relationship. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no org-chart sync/network lookup; no phone-number extraction; no buyer-facing claim; no default-registry registration; no production dispatch at Evidence Stage 1; no emission of numeric score, findings payloads, roster strings, or raw body/header material in the contribution. |
| Inputs | One `EMAIL_INBOUND` Blackboard record via `MissionContext.source_record_id` (per-tenant path); reads sender display name, `sender`, `headers` (`From` / `Reply-To` via `extract_identity_domains`), and `body_plain`. Caller-owned Known-Good Principal Roster supplied at agent construction — wrapper does not read Vendor Baseline Store or roster persistence directly at ES1. Optional caller-supplied lookalike cue when wiring enables it. |
| Outputs | One `AgentContribution` (layer 2): `observed_facts` = `("executive_impersonation_pattern",)` when the detector fires, otherwise empty. No verification/challenge/evidence/score field is emitted. |
| Evidence emitted | Closed-set indicator `executive_impersonation_pattern` when roster-name match pairs with identity mismatch and corroborating pressure/task-directive per detector §3; nothing else. Numeric `executive_impersonation_score`, `ExecutiveImpersonationFinding` details, principal names, domains, and body substrings are intentionally NOT carried into the contribution. |
| Data minimization | No mailbox body content, no raw header values, no roster display-name strings, no matched-domain strings, and no secret/value leakage in the contribution — only the closed-set indicator name. `inputs_digest` is a SHA-256 of the email payload, not the payload itself. |
| Tenant isolation | Reads only the tenant Blackboard path; caller supplies per-tenant principal roster; tenant A roster must never be reused for tenant B at the wiring boundary. |
| Two-pass role | Pass 1 (detect) only. `challenge()` returns `None`. |
| Decision Evidence Record contribution | `observed_facts`: `executive_impersonation_pattern` when present; `interpretations`: none; `assumptions`: caller principal roster is current for the tenant; `missing_evidence`: empty roster, absent body_plain, or missing identity fields yield no fire; `recommended_verification`: none authored at Layer 2; `final_outcome_contribution`: executive-impersonation pattern fact only; `retest_or_learning_record`: per template §6.5. |
| Human review trigger | None authored by this agent; Commander disposition and downstream layers own escalation. |
| Verification trigger | None authored at Layer 2; executive-impersonation facts may feed future Verification / Challenge agents. |
| Scoring / action posture | Facts-only contribution. No scoring lift authored by this wrapper; pipeline default-off integration remains outside this agent. |
| Default rollout | Evidence Stage 1: not in `build_default_registry`; explicit callers/tests only until signed Stage 2 promotion. Detector default-off calibration (detector §10.A Q5) is separate. |
| Autonomous action | None. `autonomous_action_allowed = False`. |
| Promotion conditions | Per template §6.2 Stage 1→2 bar: clean tests, real-sample review, signed promotion record. |
| Demotion conditions | Per template §6.3. |
| Retest evidence | Per template §6.5 progressive hardening. |
| Calibration requirement | Detector default-off calibration record (detector §10.A Q5) is separate from wrapper Evidence Stage promotion. |
| Failure modes | See §5. |
| Required tests | `tests/test_executive_impersonation_agent.py` plus underlying `tests/test_executive_impersonation_detector.py` when detector exists. |
| Audit requirements | Subject to `complete_gate.py` on build slice; contract gated before §11 signature. |
| Signed-spec dependencies | `Executive_Impersonation_Detector_Deep_Dive.md`, `Agent_Design_Contract_Template_Deep_Dive.md`, `VISION.md`, `Vendor_Baseline_Store_Deep_Dive.md`, `Compliance_and_Trend_Watch_Process.md`. |
| Build Authorization dependency | Q5 step 3 places contract only. Detector implementation requires separate operator Build Authorization per detector §10.B. Wrapper build requires detector on disk + §11-signed agent contract + explicit build lane. No Stage 2/3 registration without separate promotion record. |

---

## §0 Purpose

Complete the Q5 step 3 metadata-only retrofit for swarm #21: place a full Agent Design Contract governing the future `ExecutiveImpersonationAgent` wrapper over the §11-signed executive-impersonation detector blueprint without changing detector logic. Closes governance parity gap (#21 at SPEC_ONLY with embedded metadata only) by matching the standalone contract + wrapper pattern proven on #10/#6/#8/#27. **Does not** implement detector or wrapper code in this slice.

---

## §1 Scope

### In scope
- Agent Design Contract block governing `ExecutiveImpersonationAgent`.
- Evidence Stage 1 (Synthetic) declaration.
- Wrapper design calling `detect_executive_impersonation` read-only with caller-owned principal roster (when detector exists).
- Focused test plan proving Agent contract → AgentContribution → Blackboard → DER path.

### Out of scope
- Any change to future `executive_impersonation_detector.py` logic, thresholds, technique set, or scoring-pipeline default-on posture once implemented.
- Detector implementation in this Q5 contract-placement slice.
- Domain-only look-alike detection (#10) or callback/TOAD pressure (#39).
- Default registry / production dispatch at ES1.
- Autonomous action or buyer-facing claims.

---

## §2 Locked Design Decisions (draft — lock at §11)

- **D1 — Identity.** Executive Impersonation is Layer 2 Detection, Authority Level 3, VISION Stage A, Evidence Stage 1 at signing. `agent_id = executive_impersonation_001`.
- **D2 — Detector immutability.** Wrapper-only; detector D1–D9 + §10.A immutable (template §7.0).
- **D3 — Facts-only contribution.** Emits only `executive_impersonation_pattern` as `observed_fact`; no score, findings struct, roster strings, or body material.
- **D4 — Input surface.** `EMAIL_INBOUND` via `source_record_id`; display name + `sender` + `headers` + `body_plain`; caller-owned principal roster at construction; optional lookalike cue at wiring boundary.
- **D5 — Persistence + rollout.** Registry-gated `AGENT_CONTRIBUTION`; not in `build_default_registry` at ES1.
- **D6 — Stage A / no autonomy.** No block/quarantine/deny; no autonomous action.
- **D7 — Evidence Stage governance.** Template §6.2 / §6.3 / §6.5 apply.
- **D8 — Data minimization + tenant isolation.** Per-tenant Blackboard reads; per-tenant roster wiring; pressure-only never fires without identity finding (detector §3).
- **D9 — Tests are promotion-bar evidence.** `tests/test_executive_impersonation_agent.py` is the ES1 runtime proof baseline once wrapper is built.

---

## §3 Data surface and output schema

- **Reads:** `EmailInboundPayload` display name (from headers/sender surface), `sender`, `headers`, `body_plain`.
- **Detector (future):** `detect_executive_impersonation(display_name=..., from_address=..., headers=..., body_plain=..., principal_roster=..., lookalike_cue=...)`.
- **Fires when:** assessment.`fired` is True (identity finding required; pressure/task-directive corroborates only).
- **Emits:** `observed_facts=("executive_impersonation_pattern",)` or empty tuple.

---

## §4 Evidence Stage declaration

- **Current:** Stage 1 — Synthetic.
- **Stage 2/3:** Separate Matt-signed promotion per template §6.2.

---

## §5 Failure modes

- Empty principal roster → no fire (detector short-circuit).
- Authorized-domain executive mail → no fire.
- Pressure-only without identity finding → no fire.
- Cross-tenant roster leakage at wiring → governance failure.
- Raw score/roster/body leakage in contribution → schema/policy failure.

---

## §6 Required tests

`tests/test_executive_impersonation_agent.py` must prove (once built): roster-name + domain mismatch fires; authorized executive clear; free-mail executive claim fires; pressure-only no-fire; Reply-To surface; persistence; tenant-scoped reads; missing/invalid source record errors; facts-only boundary (no score); `challenge()` None; Commander DER integration.

---

## §10 Open Questions

- **Q1 — Roster sourcing at ES2.** Should Stage 2 wire Vendor Baseline Store / principal-roster reads inside the wrapper vs continue caller-owned roster? Deferred to Stage 2 promotion.
- **Q2 — Lookalike cue wiring.** Should wrapper always accept optional `LookalikeDomainAssessment` from caller vs internal lookalike-agent coupling? Deferred to detector build + ES2 wiring review.
- **Q3 — Registry posture.** Explicitly-wired through Stage 2 per Ghost Thread Q2 resolution pattern; default registry only at Stage 3.

---

## §11 Sign-off

**DRAFT UNSIGNED** — pending pre-build gate + Matt §11 signature. Wrapper build remains blocked until detector implementation + separate Build Authorization.

> §11 SIGNATURE — (pending)
