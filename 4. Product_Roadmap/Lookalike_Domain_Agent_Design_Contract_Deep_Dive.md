# Lookalike Domain Agent Design Contract — Spec-First Deep Dive

**Status:** §11 SIGNED 2026-06-25 by Matt Nichol (MMI-DEC-214). Q5 step 3 metadata-only retrofit complete at Agent Design Contract layer. Promotes `LookalikeDomainAgent` wrapper to governed parity with #6/#8/#27 peers. **Not** detector-logic change; **not** default-registry registration; **not** production dispatch; **not** scoring-pipeline default-on change.

**Owner:** Matt Nichol

**Candidate:** #10 — Lookalike Domain

**Implementation:** Built — `LookalikeDomainAgent` at `core/orchestrator/lookalike_domain_agent.py` (MMI-DEC-212); 13 focused tests; scoreboard `AWAITING_AUDIT` pending completion gate

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`
- `4. Product_Roadmap/Lookalike_Domain_Detector_Deep_Dive.md` (§11 SIGNED 2026-06-05 — immutable detector D1–D9)
- `4. Product_Roadmap/Ghost_Thread_Agent_Design_Contract_Deep_Dive.md` (closest Layer 2 peer)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#10 row; Q5 step 3)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/lookalike_domain_detector.py` (immutable underlying detector)
- `VISION.md`

**Build path:** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/lookalike_domain_agent.py`

---

## Agent Design Contract block

**Boundary:** This contract governs the Lookalike Domain **agent wrapper** (`LookalikeDomainAgent`). It is additive governance under template §7.0. It does **not** edit, reinterpret, relax, or extend the §11-signed detector contract (`detect_lookalike_domains`, D1–D9, scoring bands, default-off integration posture, or scoring-pipeline wiring). Those remain immutable.

| Field | Value |
|---|---|
| Agent name | Lookalike Domain Agent (`LookalikeDomainAgent`) |
| Swarm inventory ID | #10 — Lookalike Domain |
| Canonical layer | 2 — Detection |
| Canonical team / case type | Email identity / sender analysis; trusted-domain impersonation via sending-identity domain vs tenant known-good set |
| Authority level | Level 3 — Specialist Agent (matches #6 / #8 / #21) |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (see template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic.** Validated on synthetic test data only; intentionally NOT registered in `build_default_registry` / production dispatch. |
| Role | Produce facts-only lookalike-sender-domain evidence by running the deterministic lookalike detector against header identity domains and a caller-supplied tenant known-good domain set. |
| Boundary | The detector is not the decision. The agent must not decide fraud, approve/deny mail, block/quarantine, change payment behavior, mutate scoring overlays, or alter the signed Client-Facing 5-Axis Email Scoring Rubric. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no DNS/WHOIS/network lookup; no buyer-facing claim; no default-registry registration; no production dispatch at Evidence Stage 1; no emission of numeric lookalike score, findings payloads, or raw domains in the contribution. |
| Inputs | One `EMAIL_INBOUND` Blackboard record via `MissionContext.source_record_id` (per-tenant path); reads `sender` and `headers` (`From` / `Reply-To` identity domains per detector D9). Caller-owned `known_good_domains` tuple supplied at agent construction — wrapper does not read Vendor Baseline Store directly at ES1. |
| Outputs | One `AgentContribution` (layer 2): `observed_facts` = `("lookalike_sender_domain",)` when the detector fires, otherwise empty. No verification/challenge/evidence/score field is emitted. |
| Evidence emitted | Closed-set indicator `lookalike_sender_domain` when identity domains are a deliberate look-alike of a caller-supplied known-good domain; nothing else. Numeric `lookalike_domain_score`, `LookalikeDomainFinding` details, and raw domain strings are intentionally NOT carried into the contribution. |
| Data minimization | No mailbox body content, no raw header values, no matched-domain strings, and no secret/value leakage in the contribution — only the closed-set indicator name. `inputs_digest` is a SHA-256 of the email payload, not the payload itself. |
| Tenant isolation | Reads only the tenant Blackboard path; caller supplies per-tenant `known_good_domains`; tenant A known-good set must never be reused for tenant B at the wiring boundary. |
| Two-pass role | Pass 1 (detect) only. `challenge()` returns `None`. |
| Decision Evidence Record contribution | `observed_facts`: `lookalike_sender_domain` when present; `interpretations`: none; `assumptions`: caller-known-good set is current for the tenant; `missing_evidence`: empty known-good set yields no fire; `recommended_verification`: none at Layer 2; `final_outcome_contribution`: sender-identity lookalike fact only; `retest_or_learning_record`: per template §6.5. |
| Human review trigger | None authored by this agent; Commander disposition and downstream layers own escalation. |
| Verification trigger | None authored at Layer 2; lookalike facts may feed future Verification / Challenge agents. |
| Scoring / action posture | Facts-only contribution. No scoring lift authored by this wrapper; pipeline default-off integration remains outside this agent. |
| Default rollout | Evidence Stage 1: not in `build_default_registry`; explicit callers/tests only until signed Stage 2 promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`. |
| Promotion conditions | Per template §6.2 Stage 1→2 bar: clean tests, real-sample review, signed promotion record. |
| Demotion conditions | Per template §6.3. |
| Retest evidence | Per template §6.5 progressive hardening. |
| Calibration requirement | Detector default-off calibration record (detector §10.A Q5) is separate from wrapper Evidence Stage promotion. |
| Failure modes | See §5. |
| Required tests | `tests/test_lookalike_domain_agent.py` plus underlying `tests/test_lookalike_domain_detector.py`. |
| Audit requirements | Subject to `complete_gate.py` on build slice; contract gated before §11 signature. |
| Signed-spec dependencies | `Lookalike_Domain_Detector_Deep_Dive.md`, `Agent_Design_Contract_Template_Deep_Dive.md`, `VISION.md`, `Vendor_Baseline_Store_Deep_Dive.md`, `Compliance_and_Trend_Watch_Process.md`. |
| Build Authorization dependency | Q5 step 3 operator authorization (2026-06-25) authorizes wrapper + focused tests only at Evidence Stage 1. No detector mutation. No Stage 2/3 registration without separate promotion record. |

---

## §0 Purpose

Complete the Q5 step 3 metadata-only retrofit for swarm #10: place a full Agent Design Contract and governed `LookalikeDomainAgent` wrapper over the existing §11-signed `detect_lookalike_domains` detector without changing detector logic. Closes health-score parity gap (#10 at 80 vs ES1 peer ceiling ~87) by matching the contract + wrapper pattern proven on #6/#8/#27.

---

## §1 Scope

### In scope
- Agent Design Contract block governing `LookalikeDomainAgent`.
- Evidence Stage 1 (Synthetic) declaration.
- Wrapper calling `detect_lookalike_domains` read-only with caller-owned known-good domains.
- Focused tests proving Agent contract → AgentContribution → Blackboard → DER path.

### Out of scope
- Any change to `lookalike_domain_detector.py` logic, thresholds, technique set, or scoring-pipeline default-on posture.
- Body-URL obfuscation detection (#27).
- Header/auth divergence (#6 / #6A).
- Default registry / production dispatch at ES1.
- Autonomous action or buyer-facing claims.

---

## §2 Locked Design Decisions

- **D1 — Identity.** Lookalike Domain is Layer 2 Detection, Authority Level 3, VISION Stage A, Evidence Stage 1 at signing. `agent_id = lookalike_domain_001`.
- **D2 — Detector immutability.** Wrapper-only; detector D1–D9 immutable (template §7.0).
- **D3 — Facts-only contribution.** Emits only `lookalike_sender_domain` as `observed_fact`; no score, findings struct, or raw domains.
- **D4 — Input surface.** `EMAIL_INBOUND` via `source_record_id`; `sender` + `headers`; caller-owned `known_good_domains` at construction.
- **D5 — Persistence + rollout.** Registry-gated `AGENT_CONTRIBUTION`; not in `build_default_registry` at ES1.
- **D6 — Stage A / no autonomy.** No block/quarantine/deny; no autonomous action.
- **D7 — Evidence Stage governance.** Template §6.2 / §6.3 / §6.5 apply.
- **D8 — Data minimization + tenant isolation.** Per-tenant Blackboard reads; per-tenant known-good wiring.
- **D9 — Tests are promotion-bar evidence.** `tests/test_lookalike_domain_agent.py` is the ES1 runtime proof baseline.

---

## §3 Data surface and output schema

- **Reads:** `EmailInboundPayload.sender`, `EmailInboundPayload.headers` (From / Reply-To domains).
- **Detector:** `detect_lookalike_domains(from_address=sender, headers=headers, known_good_domains=...)`.
- **Fires when:** assessment.`fired` is True.
- **Emits:** `observed_facts=("lookalike_sender_domain",)` or empty tuple.

---

## §4 Evidence Stage declaration

- **Current:** Stage 1 — Synthetic.
- **Stage 2/3:** Separate Matt-signed promotion per template §6.2.

---

## §5 Failure modes

- Empty known-good set → no fire (detector short-circuit).
- Exact domain match in known-good → no fire.
- Cross-tenant known-good leakage at wiring → governance failure.
- Raw domain/score leakage in contribution → schema/policy failure.

---

## §6 Required tests

`tests/test_lookalike_domain_agent.py` must prove: known typosquat fires; exact match clear; Reply-To surface; persistence; tenant-scoped reads; missing/invalid source record errors; facts-only boundary (no score); `challenge()` None; Commander DER integration.

---

## §10 Open Questions

- **Q1 — Known-good sourcing at ES2.** Should Stage 2 wire Vendor Baseline Store reads inside the wrapper vs continue caller-owned domains? Deferred to Stage 2 promotion.
- **Q2 — Registry posture.** Explicitly-wired through Stage 2 per Ghost Thread Q2 resolution pattern; default registry only at Stage 3.

---

## §11 Sign-off

SIGNED. This locks D1–D9 for swarm agent #10 Lookalike Domain at **Evidence Stage 1 (Synthetic)**. Signing authorizes the existing `LookalikeDomainAgent` wrapper + focused tests as the governed runtime surface. Signing authorizes **no** detector-logic change, **no** default-registry registration, **no** production dispatch, **no** scoring/rubric change, and **no** autonomous action.

> §11 SIGNATURE — Matt Nichol June 25th 2026
