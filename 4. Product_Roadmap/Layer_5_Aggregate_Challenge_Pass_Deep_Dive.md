# Layer 5 Aggregate Challenge Pass - Spec-First Deep Dive

**Status:** §11 SIGNED 2026-06-07 by Matt Nichol. In force. Authored 2026-06-07 by Cursor on Matt Nichol's instruction, grounded in a Section 0 due-diligence research pass (verifier-pattern, multi-agent verification, security-AI ensemble corroboration, and the multi-agent conformity literature - see §9). This spec governs a spine/mechanism change: how the Swarm Commander runs the Pass-2 Layer 5 challenge pass, and the `Agent.challenge()` contract signature. It does **not** govern any single Challenge agent - the first real aggregate Challenge agent gets its own Agent Design Contract (build Section 5) and a separate signature.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey**. No rename implied.

**Source-of-truth links:**
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent` protocol - the `challenge()` signature this spec changes; `AgentContribution`, `ChallengeResult`, `DecisionEvidenceRecord`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/swarm_commander.py` (the challenge-pass loop this spec rewires; `_determine_disposition`)
- `core/orchestrator/header_divergence_agent.py`, `ghost_thread_agent.py`, `email_authentication_agent.py` (the three governed wrappers whose `challenge()` stubs migrate)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (§6 Evidence Stage / promotion / §6.5 progressive hardening; §7.0 detector immutability)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (Layer 5 Challenge/Red-Team promotion bar; spine build order)
- `AGENTS.md` §5 (reaction-timing / negative-evidence discipline), §11 (build momentum; experiment boundary)
- `VISION.md` (Stage A = analyze + recommend; the seven non-negotiables)

---

## §0 Purpose

The two-pass model is the core of the premium claim: Pass 1 detectors emit facts; a Pass 2 Layer 5 Challenge agent independently reviews those facts and returns `confirmed` / `contradicted` / `inconclusive` before anything escalates. Today the spine runs Pass 2 **one contribution at a time** (`swarm_commander.py` loops `challenge_agent.challenge(contribution)` per contribution; `Agent.challenge()` takes a single `AgentContribution`). That structurally prevents a Challenge agent from seeing the **aggregate** picture.

The operator constraint (recorded 2026-06-07): a Challenge agent must review the **full per-case `AgentContribution` set**, not one contribution in isolation. A ghost-thread indicator plus an SPF failure plus a header divergence **in the same email** is a different, stronger risk signal than any one of them alone - and, conversely, a lone weak signal deserves to be downgraded rather than escalated.

This spec locks the design that makes aggregate review possible, grounded in the Section 0 research (§9), and defines the documented-failure test discipline (§6) that governs how we earn confidence: not by passing every test, but by documenting the failures and the path to completing them.

This spec builds nothing by itself. It authorizes the sectioned implementation in §8, each step separately gated.

---

## §1 Scope

### In scope
- The `Agent.challenge()` contract signature change: from a single `AgentContribution` to the full per-case `tuple[AgentContribution, ...]`.
- The `swarm_commander.py` challenge-pass rewire: invoke each Layer 5 agent once per case over the full contribution set.
- The mechanical migration of the three existing governed wrappers' `challenge()` stubs (they return `None`) and the challenge-agent test doubles to the new signature.
- The corroborate-don't-vote-count reasoning rule (D4) and the authority-drift guard (D5) as locked behavioral constraints for any future Challenge agent.
- The documented-failure test discipline (§6): the three test classes and the failure register.

### Out of scope
- Any change to detector logic, scoring bands, or any Detection-layer `analyze()` behavior (immutable per template §7.0).
- Building, registering, or promoting any specific Challenge agent. The first real aggregate Challenge agent is build Section 5, under its own signed Agent Design Contract.
- Any change to the `_determine_disposition` precedence rules (the v1 conservative rules are preserved unchanged; see §10 Q2 for the deferred `escalate` question).
- `build_default_registry` registration or production dispatch of any Challenge agent.
- Any autonomous action, buyer-facing claim, or Stage B/C autonomy.

---

## §2 Locked Design Decisions (to confirm and lock at §11)

- **D1 - Aggregate input.** `Agent.challenge()` receives the full per-case `contributions: tuple[AgentContribution, ...]`, not a single contribution. The Commander invokes each Layer 5 agent **once per case** over the complete set. This is the operator constraint made literal.
- **D2 - One verdict per Challenge agent.** `challenge()` returns `ChallengeResult | None` - one case-level verdict per Challenge agent (its assessment of the whole picture), or `None` when it has no verdict. The `ChallengeResult` schema and the `_determine_disposition` precedence are unchanged.
- **D3 - Verifier-pattern isolation (facts-only).** The Challenge agent sees only the `AgentContribution` facts/outcomes and the `MissionContext` digest - never any reasoning trace, chain-of-thought, or detector internals (none exist in the DER by prior design). This is the independent-verifier pattern: a reviewer that did not generate the facts does not inherit the generator's bias. (§9 finding 1.)
- **D4 - Corroborate, do not vote-count.** A Challenge agent evaluates each contribution as an **independent claim checked against the case facts**, not as a vote to be tallied. Signal *count* or *agreement* alone is never sufficient evidence; corroboration is meaningful only because our detectors are genuinely independent (different attack surfaces). This is a behavioral constraint on every future Challenge agent. (§9 finding 3 - the conformity/agreement-amplifies-errors result.)
- **D5 - No authority; verdict only.** A Challenge agent authors a verdict only; the Commander owns disposition. `authority_level` is for dispatch gating, never verdict weighting. `autonomous_action_allowed = False`; no block/quarantine/deny/reject. The challenge pass remains orchestration support. (Authority-drift guard - §9 findings 2 and the cognitive-bias source.)
- **D6 - Detector + analyze() immutability.** This spec changes the `challenge()` signature, the Commander challenge loop, and migrates `challenge()` stubs. It changes **no** detector logic, **no** scoring, and **no** Detection-agent `analyze()` behavior. The three governed Detection agents continue to return `None` from `challenge()`.
- **D7 - Documented-failure test discipline.** The promotion bar is **not** "all tests green." It is: every expected-pass test green, every adversarial/break-it case documented, and every known gap named with a completion path. Three committed test classes (see §6): (1) expected-pass, (2) adversarial/break-it, (3) known-gap `xfail` with a documented reason. Every failure carries `test_id`, probe, expected vs actual, verdict (`pass`/`partial`/`fail`/`blocked`), and what completing it requires. Negative evidence is project evidence (AGENTS §5; template §6.5).
- **D8 - Total migration, no split signature.** All `challenge()` implementers migrate to the new signature in the same change set: the three governed wrappers and every challenge-agent test double. No implementer is left on the old single-contribution signature; there is exactly one challenge contract in the tree.
- **D9 - Stage posture.** Stage A only. This spec registers and promotes no Challenge agent. The first aggregate Challenge agent is Section 5, under its own Agent Design Contract and signature, at Evidence Stage 1 (Synthetic).

---

## §3 Mechanism (how the aggregate challenge pass works)

1. The Commander runs Pass 1: dispatches Detection agents, collects `contributions: tuple[AgentContribution, ...]` (unchanged).
2. The Commander runs Pass 2: for each supplied Layer 5 `challenge_agent`, it validates dispatch (registry + Stage A/autonomy guard + Layer-5 check, unchanged) and invokes `challenge_agent.challenge(contributions)` **once**, passing the full set.
3. Each Challenge agent returns one `ChallengeResult | None`. A returned result must carry the agent's own `agent_id` (guard unchanged).
4. The Commander assembles `challenge_pass: tuple[ChallengeResult, ...]` and runs the existing `_determine_disposition` precedence: contradicted -> `human_required`; inconclusive -> `hold`; else the contribution-driven rule. Unchanged by this spec.

The only contract change is the shape of what `challenge()` receives (D1) and the per-case (not per-contribution) invocation (D1/D2).

---

## §4 The corroborate-don't-vote-count rule (D4 expanded)

The naive aggregate model is "more agreeing signals -> more confidence." The multi-agent conformity literature (§9 finding 3) shows that treating agreement as truth amplifies errors: wrong agreement misleads more than right agreement corrects. The safe model treats each contribution as a **claim checked against the email's own facts**.

For our swarm this is safe **and** valuable because the detectors are independent surfaces:
- Header divergence (From / Reply-To / Return-Path / Sender domain drift)
- Ghost thread (subject threading prefix + missing `In-Reply-To`/`References`)
- Email authentication (SPF/DKIM/DMARC gateway posture)

A Challenge agent confirming a case should be able to state *why the independent signals corroborate* (e.g. "authentication failure and header divergence both point at the same spoofed sending domain"), not merely "three signals fired." A lone weak signal with a plausible benign explanation should pull toward `inconclusive`/`contradicted`, not `confirmed`. This rule is what makes the aggregate pass a false-positive reducer (§9 finding 2) rather than an error amplifier (§9 finding 3).

---

## §5 Failure modes

- **Authority drift** - a Challenge agent (or caller) treating its verdict as the decision, or its `authority_level` as verdict weight. Mitigation: D5; Commander owns disposition; verdict-only `ChallengeResult`; no autonomous action.
- **Vote-counting / conformity trap** - treating signal count or agreement as confidence. Mitigation: D4; adversarial test (§6) that fires many weak/benign-explained signals and asserts the design does not auto-confirm on count alone.
- **Reasoning-trace leakage** - a future Challenge agent being handed detector internals or a chain-of-thought. Mitigation: D3; the DER stores facts/outcomes only; the `challenge()` input is the contribution tuple + `MissionContext` digest, nothing else.
- **Split-signature drift** - some implementers left on the old single-contribution signature. Mitigation: D8; the migration is total in one change set; the protocol has exactly one `challenge()` shape.
- **Disposition creep** - quietly changing the conservative disposition rules under cover of the wiring change. Mitigation: D2/scope; `_determine_disposition` is untouched; any change is a separate decision (§10 Q2).
- **Green-suite complacency** - declaring the pass "done" because tests are green while real gaps are hidden. Mitigation: D7; the known-gap `xfail` class keeps gaps visible; the bar is documented failure, not all-green.

---

## §6 Test discipline (the documented-failure register)

Three committed test classes. The suite is honest only if all three exist.

**Class 1 - Expected pass (the proven path).** Aggregate challenge invoked once per case over the full set; verdict flows into `challenge_pass`; disposition precedence holds; `agent_id` guard holds; Detection wrappers still return `None`.

**Class 2 - Adversarial / break-it (probe the boundary).** Each tries to make the challenge pass misbehave; each is documented with its verdict. Two are seeded by the Section 0 research:
- **Vote-counting probe** - feed several weak / benign-explained independent signals and assert the mechanism does not, by itself, force `confirmed` on count alone (D4).
- **Authority-drift probe** - assert a Challenge agent cannot author a disposition or an autonomous action, and that its verdict does not bypass the Commander (D5).
- Plus: reasoning-trace-leakage probe (D3), split-signature probe (D8), and an `agent_id`-mismatch probe (existing guard).

**Class 3 - Known gap (expected to FAIL at v1, documented).** Marked `xfail` (or equivalent) with a written reason so the failure is **visible, not hidden**. These are the map from "cannot prove yet" to "completed when ...". Each carries: `test_id`, what it probes, expected vs actual, verdict (`pass`/`partial`/`fail`/`blocked`), and the completion path. Candidate v1 known gaps (to be confirmed during Section 6): real-email corroboration quality (needs Stage 2 real samples), and any multi-Challenge-agent cross-arbitration case (deferred per §10 Q1).

**Promotion bar (D7):** every Class 1 test green; every Class 2 case documented with a verdict; every Class 3 gap named with a completion path. A passing suite that hides a known gap does not meet the bar.

A durable failure-register artifact accompanies the test commit (mirroring the AGENTS §5 reaction-timing record shape), so a future session reads the gaps and the path, not a misleading all-green.

---

## §7 Audit requirements

Each build section (§8) is gated through `complete_gate.py` at its commit boundary. The contract-type change (Section 2) and the Commander rewire (Section 3) are code gates; the first aggregate Challenge agent (Section 5) carries its own signed Agent Design Contract. This spec must be gated as a spec artifact before signature or commit. No Challenge agent registration, default-on, or production dispatch is authorized by signing this spec.

---

## §8 Build sections (implementation order; each separately gated)

- **Section 1 (this spec).** Design + locked decisions + test discipline. Spec-first; operator signs §11.
- **Section 2.** `agent_contract.py`: change `Agent.challenge()` to take `tuple[AgentContribution, ...]`. Minimal, tested. Code gate.
- **Section 3.** `swarm_commander.py`: invoke each Layer 5 agent once per case over the full set; preserve `_determine_disposition`. Code gate.
- **Section 4.** Migrate the three governed wrappers' `challenge()` stubs + challenge-agent test doubles to the new signature (mechanical; return `None`). Code gate.
- **Section 5.** First real aggregate Challenge agent: a governed Layer 5 agent that corroborates independent signals (D4) and returns one verdict (D2). Its own Agent Design Contract + operator signature + Evidence Stage 1. Code + spec gates.
- **Section 6.** End-to-end tests across all three classes (§6) + the failure register; scoreboard/tracker updates.

---

## §10 Open Questions (operator-only)

- **Q1 - Multiple Challenge agents per case.** When more than one Layer 5 agent reviews a case, do their verdicts need cross-arbitration, or does the existing precedence (any contradicted -> human; any inconclusive -> hold) suffice? Deferred; v1 keeps the precedence as-is.
- **Q2 - The unused `escalate` disposition.** `SwarmDisposition` includes `escalate`, which `_determine_disposition` never returns. Strong multi-signal corroboration may be exactly when `escalate` (vs `suspicious`) should fire. This is a disposition-logic change, out of scope here (D2); revisit with real-case evidence after Section 5.
- **Q3 - Provenance field.** Should `ChallengeResult` record which contributions it reviewed (`reviewed_agent_ids`)? Deferred for v1: with one verdict per agent over the full set, "what it reviewed" is reconstructable as all contributions in the DER. Revisit if the audit trail needs it explicitly once a real Challenge agent exists.

---

## §11 Sign-off

This spec is not in force until Matt Nichol signs below. Signing locks D1-D9 and authorizes the sectioned implementation in §8 (each step separately gated). Signing authorizes **no** detector-logic change, **no** Challenge-agent registration or promotion, **no** disposition-rule change, **no** production dispatch, and **no** autonomous action. The first aggregate Challenge agent is a separate, later, Matt-signed Agent Design Contract.

> §11 SIGNATURE - Matt Nichol June 7th 2026
