# Agent Design Contract Template — Spec-First Deep Dive

**Status:** §11 SIGNED 2026-06-06 by Matt Nichol. Authored 2026-06-06 by Cursor on Matt Nichol's instruction after the operator adopted the 6-layer `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` as the canonical agent-design map. All seven §10 questions are locked in §10.A (2026-06-06). This is a governance/template contract only. Signing locks D1-D10 + §10.A as the Agent Design Contract Template; it authorizes **no** code, **no** runtime wiring, **no** new agent behavior, **no** autonomous action, **no** detector retrofit, and **no** change to any signed detector spec. A separate explicit operator Build Authorization or metadata-retrofit instruction is required before implementation.

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey**. No rename implied.

**Source-of-truth links:**
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (ADOPTED CANONICAL DESIGN MAP, 2026-06-06)
- `agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md` (preserved v1 70-agent inventory/cross-map)
- `VISION.md` (Stage A/B/C discipline and seven non-negotiables)
- `AGENTS.md` (project authority / audit / gate discipline)
- `PROJECT_HANDSHAKE.md` (current route: Agent Design Contract before more promoted agents)
- `4. Product_Roadmap/Lookalike_Domain_Detector_Deep_Dive.md` (#10, signed detector to retrofit later)
- `4. Product_Roadmap/Executive_Impersonation_Detector_Deep_Dive.md` (#21, signed detector to retrofit later)
- `4. Product_Roadmap/Tiered_Detection_Intensity_Deep_Dive.md` (lift-only invariant)
- `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` (client-facing score boundary)
- `Compliance_and_Trend_Watch_Process.md` (claim-safe language boundary)

---

## §0 Purpose

This spec defines the required **Agent Design Contract** that every promoted Mutant Monkey / NorthStar swarm agent must declare before Build Authorization.

The canonical design rule is now:

> Each agent has a role, a boundary, evidence requirements, failure modes, promotion conditions, demotion conditions, and a signed record of why it was trusted.

This template turns that rule into a repeatable, gate-checkable contract. It prevents future agents from being drafted as loose detectors that later need governance retrofits. It also gives the future two-pass decision model and command layer a stable interface: every agent must say what it observes, what it may decide, what it may not decide, what evidence it emits, how it is challenged, and how it earns or loses trust.

---

## §1 Scope

### In scope
- A required template section for future agent deep-dive specs in `4. Product_Roadmap/`.
- A light retrofit template for already-promoted agents (#10 Lookalike Domain and #21 Executive Impersonation) that adds governance metadata **without changing their signed detection contracts**.
- Canonical fields for:
  - six-layer placement;
  - authority level;
  - role and boundary;
  - input / output / evidence contract;
  - two-pass decision-model role;
  - decision-evidence-record contribution;
  - promotion and demotion conditions;
  - failure modes and retest evidence;
  - default-off / lift-only / no-autonomous-action posture where applicable.
- A reusable table/checklist that `complete_gate.py` / independent reviewers can inspect during spec review.

### Out of scope
- No implementation of an orchestrator, Swarm Commander, reputation engine, memory layer, or two-pass runtime.
- No retrofit edits to #10 or #21 in this draft.
- No default-on activation for any detector.
- No client-facing claim language.
- No change to signed specs, signed rubrics, `VISION.md`, `AGENTS.md`, or the seven non-negotiables.
- No real-customer-data handling, production datastore use, or buyer delivery.

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

| # | Decision | Locked value |
|---|---|---|
| D1 | Contract identity | The Agent Design Contract is a **required governance template** for promoted swarm agents, not a runtime feature. |
| D2 | Canonical map | Agents are designed against the 6-layer canonical map: Command, Detection, Verification, Evidence, Challenge/Red-Team, Learning/Governance. |
| D3 | Detector-not-decision rule | A detector signal is a trigger for verification or review, not the final decision. Any exception requires a signed Stage B/C spec and still obeys human-in-the-loop / kill-switch rules. |
| D4 | Authority declaration | Every agent declares its authority level (Observer, Analyst, Specialist, Commander, Challenge, Final Review) and the actions it can/cannot take. |
| D5 | Evidence-first output | Every agent declares its evidence record: observed facts, interpretations, assumptions, missing evidence, recommended verification, final outcome contribution, and retest linkage. |
| D6 | Two-pass fit | Every agent declares whether it participates in Pass 1 detection, Pass 2 challenge/verification, final output, or learning/retest. |
| D7 | Promotion/demotion | Every agent declares promotion conditions, demotion conditions, and minimum retest evidence before its influence can increase. |
| D8 | Stage discipline | Stage A agents analyze/recommend only. Stage B/C autonomy requires a separate signed spec, explicit Build Authorization, reversible action design, audit trail, and kill-switch compatibility. |
| D9 | Retrofit posture | **The signed detector contracts for #10/#21 are IMMUTABLE.** A retrofit adds governance metadata to a separate Agent Design Contract **wrapper block only**; it never edits, reinterprets, relaxes, or extends the detection logic or any signed decision. "Retrofit" is explicitly NOT permission to touch a detector contract. Any change to detection logic, scoring bands, default-off posture, input surface, or rubric boundary requires that detector's own operator instruction -> spec edit -> `complete_gate.py` -> new §11 signature — never this template. |
| D10 | Claim-safe boundary | Buyer-facing wording remains governed by `Compliance_and_Trend_Watch_Process.md`; internal slogans and agent labels are not buyer claims. |

---

## §3 Required Agent Design Contract

Every future promoted agent spec must include this block before §10 is considered resolved.

```text
## Agent Design Contract

Agent name:
Swarm inventory ID:
Canonical layer:
Canonical team / case type:
Authority level:
Stage posture:

Role:
Boundary:
Explicit non-authorities:

Inputs:
Outputs:
Evidence emitted:
Data minimization:
Tenant isolation:

Two-pass role:
Decision Evidence Record contribution:
Human review trigger:
Verification trigger:

Scoring / action posture:
Default rollout:
Autonomous action:

Promotion conditions:
Demotion conditions:
Retest evidence:
Calibration requirement:

Failure modes:
Required tests:
Audit requirements:
Signed-spec dependencies:
Build Authorization dependency:
```

### 3.1 Field meanings

- **Agent name** — the internal name used in specs/code.
- **Swarm inventory ID** — the v1 map number or canonical layer label, when applicable.
- **Canonical layer** — one of: Command, Detection, Verification, Evidence, Challenge/Red-Team, Learning/Governance.
- **Canonical team / case type** — the domain where this agent is allowed to operate (vendor-payment fraud, phishing, ransomware precursor, cyber-insurance evidence, executive impersonation, etc.).
- **Authority level** — one of the six canonical authority levels from the design tree.
- **Stage posture** — Stage A analyze/recommend only unless a signed Stage B/C spec says otherwise.
- **Role** — what the agent is for.
- **Boundary** — what the agent must not do, even when it fires.
- **Explicit non-authorities** — forbidden outputs/actions (block, quarantine, approve payment, declare fraud, claim compliance, etc.).
- **Inputs** — exact surfaces the agent may read.
- **Outputs** — exact structured assessment or evidence fields it may write.
- **Evidence emitted** — facts/tags/findings the agent contributes to the decision evidence record.
- **Data minimization** — what raw values cannot be echoed/stored.
- **Tenant isolation** — how the agent prevents cross-tenant leakage.
- **Two-pass role** — Pass 1 detect, Pass 2 challenge, final review, or learning/retest.
- **Decision Evidence Record contribution** — observed facts, interpretations, assumptions, missing evidence, recommended verification, final outcome contribution.
- **Human review trigger** — what condition forces review.
- **Verification trigger** — what condition requires known-good verification.
- **Scoring / action posture** — lift-only, evidence-tag-only, no score change, or other signed behavior.
- **Default rollout** — default-off, opt-in, calibration-gated, or other.
- **Autonomous action** — normally `none` in Stage A; any non-none requires Stage B/C gating.
- **Promotion conditions** — measurable evidence that increases trust/influence.
- **Demotion conditions** — false positives, false negatives, overclaims, unsupported recommendations, or failed retests.
- **Retest evidence** — what proof must exist after correction.
- **Calibration requirement** — data/test set required before default-on or authority increase.
- **Failure modes** — named ways the agent can mislead the system.
- **Required tests** — unit, integration, break-it, cross-tenant, no-network, no-overclaim, no-autonomous-action tests.
- **Audit requirements** — gate outputs and evidence records required before commit/ship.
- **Signed-spec dependencies** — governing specs this agent inherits.
- **Build Authorization dependency** — explicit operator instruction required before implementation.

---

## §4 Canonical authority levels

| Level | Name | May do | Must not do |
|---|---|---|---|
| 1 | Observer | Detect/report signals, flag suspicious details, provide observations | Make final decisions, recommend business action alone |
| 2 | Analyst | Classify risk, suggest severity, recommend more review | Finalize high-risk cases alone |
| 3 | Specialist | Produce domain-specific evidence | Override command rules |
| 4 | Commander | Assign agents, route cases, set review paths, escalate | Ignore evidence rules |
| 5 | Challenge | Challenge weak decisions, flag assumptions/missing evidence, force review | Approve risky actions without required evidence |
| 6 | Final Review | Approve final decision package, confirm evidence completeness | Overclaim beyond evidence |

Stage A default: promoted detectors are Level 1 or Level 3 unless their signed spec says otherwise.

---

## §5 Decision Evidence Record interface

Every agent must state which fields it can contribute:

```text
observed_facts:
interpretations:
assumptions:
missing_evidence:
recommended_verification:
final_outcome_contribution:
retest_or_learning_record:
```

Rules:
- Observed facts must be sourced from explicit input surfaces.
- Interpretations must be separated from facts.
- Assumptions must be labeled.
- Missing evidence must not be hidden.
- Recommended verification must use known-good channels when money, credentials, executive authority, or real-customer-data exposure is involved.
- Final outcome contribution must not overclaim.
- Retest/learning record is required after a correction, failure, or demotion event.

---

## §6 Promotion / demotion contract

### Promotion conditions
An agent may gain influence only when it has:
- repeatable accuracy evidence for a specific case type;
- low false-positive evidence under benign tests;
- low false-negative evidence under adversarial tests;
- useful evidence output, not vague claims;
- deterministic or bounded behavior;
- retest evidence after prior failures;
- no open boundary violations.

### Demotion conditions
An agent loses influence when it:
- overclaims beyond evidence;
- misses a serious threat in its scoped domain;
- produces unsupported recommendations;
- triggers false positives above the accepted calibration boundary;
- leaks raw sensitive values or cross-tenant evidence;
- violates Stage A no-autonomous-action rules;
- fails retesting after correction.

Promotion/demotion is **case-type specific**, not universal. An agent can be trusted for vendor-payment fraud and untrusted for ransomware precursor review.

---

## §7 Retrofit rule for #10 and #21

The first retrofit target is metadata-only:
- `Lookalike_Domain_Detector_Deep_Dive.md`
- `Executive_Impersonation_Detector_Deep_Dive.md`

### §7.0 Immutability boundary (read this first)

**The signed detector contract is immutable. A retrofit only adds governance fields to a wrapper, not to the detection logic itself.**

This distinction is binding and must not be re-interpreted by any future session:

- The "signed detector contract" = the detector's locked D-decisions, its §10.A operator-confirmed decisions, its scoring bands/floors, its default-off/opt-in posture, its input surface, its data-minimization rules, its `sender_identity`/rubric boundary, and its detection logic. **All of that is frozen.**
- A "retrofit" adds a **separate Agent Design Contract wrapper block** (the §3 fields: layer, authority level, two-pass role, evidence-record contribution, promotion/demotion conditions, etc.) **around** the existing signed spec. It is additive governance metadata only.
- **"Retrofit" is NOT permission to open, edit, relax, extend, or reinterpret the detector contract.** A future session agent must not treat a retrofit instruction as license to touch detection logic, scoring, posture, or any signed decision.
- If any retrofit would require changing one word of the detection logic or a signed decision, **stop** — that is a detector-spec revision, which requires that detector's own operator instruction -> spec edit -> `complete_gate.py` -> new §11 signature, and it is out of scope for a retrofit.

Allowed retrofit:
- add the Agent Design Contract wrapper block (governance metadata) to the spec;
- declare canonical layer, authority level, two-pass role, evidence-record contribution, and promotion/demotion conditions;
- preserve, verbatim and unchanged, all existing signed D decisions, §10.A decisions, scoring bands, default-off posture, input surface, and rubric boundaries.

Forbidden retrofit:
- changing or reinterpreting detector logic;
- changing scoring floors or bands;
- changing default-off/default-on posture;
- changing the input surface or data-minimization rules;
- changing the signed Client-Facing 5-Axis Rubric or the `sender_identity` evidence-attribution boundary;
- adding Build Authorization by implication;
- treating "retrofit" as authority to reopen the signed detector contract for any reason.

---

## §8 Failure Modes

- **Standalone-detector drift.** Future agents are drafted as isolated detectors, not swarm members. Mitigation: required Agent Design Contract block.
- **Authority creep.** An agent starts recommending or taking actions beyond its signed level. Mitigation: authority-level field + explicit non-authorities + no-autonomous-action tests.
- **Evidence laundering.** Interpretations get presented as facts. Mitigation: Decision Evidence Record separation.
- **Rubric bypass.** Evidence tags become hidden point changes. Mitigation: signed-rubric boundary and evidence-attribution-only language.
- **Promotion without proof.** An agent gains trust because it sounds plausible. Mitigation: promotion conditions require retestable evidence.
- **Demotion gap.** A bad agent remains trusted after failures. Mitigation: demotion conditions + correction/retest record.
- **Map drift.** v1/v2/canonical maps diverge again. Mitigation: `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` is the canonical design source; v1 remains inventory only.

---

## §9 Audit Requirements

- Any future promoted agent spec must include the Agent Design Contract block before §10 can be considered resolved.
- Any implementation commit for a promoted agent must cite the signed agent spec and its Agent Design Contract fields.
- Any retrofit to #10/#21 must be gated as metadata-only and must not change signed detector behavior.
- `complete_gate.py` remains the independent decision auditor for spec/sign-off/build claims.
- Buyer-facing wording remains subject to `Compliance_and_Trend_Watch_Process.md` §5.

---

## §10 Open Questions (operator-only)

- **Q1 — Template enforcement point.** Does every future agent deep-dive require the Agent Design Contract block before §10 resolution, or before §11 signature only?
- **Q2 — Existing signed agents.** Should #10 Lookalike and #21 Executive Impersonation receive a metadata-only retrofit immediately after this spec signs, or only when each is next touched for build/revision?
- **Q3 — Authority-level defaults.** Should Stage A detectors default to Level 1 Observer or Level 3 Specialist?
- **Q4 — Decision Evidence Record field set.** Is the seven-field interface in §5 sufficient, or should `confidence`, `evidence_strength`, and `contradictions` be first-class fields now?
- **Q5 — Promotion/demotion storage.** In v1, are promotion/demotion conditions spec-only text, or should there be a future ledger/schema for agent reputation events?
- **Q6 — Two-pass linkage.** Should every detector declare both Pass 1 and Pass 2 roles now, or may pure detectors declare Pass 1 only until the Two-Pass Decision Model spec is signed?
- **Q7 — Canonical source.** Confirm `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` remains the canonical design source and the v1 map remains inventory/backlog only.

### §10.A Operator-Confirmed Decisions (2026-06-06, pre-§11)

Operator ("lock it in", 2026-06-06) confirmed all seven questions with the defaults below. These resolve §10 and feed the §11 signature, but this block does **not** sign §11 and authorizes **no** implementation, no runtime enforcement, no retrofits, and no new agent behavior.

1. **Q1 — Template enforcement point.** Every future promoted agent deep-dive requires the Agent Design Contract block **before §10 can be considered resolved**, not merely before §11 signature. Consequence: design gaps are caught while decisions are still open, before the operator is asked to sign.
2. **Q2 — Existing signed agents.** #10 Lookalike Domain and #21 Executive Impersonation receive a **metadata-only retrofit immediately after this template is §11-signed**. The retrofit may add layer, role, authority level, two-pass role, decision-evidence-record contribution, promotion/demotion conditions, and related governance metadata. It must not change signed detector logic, scoring floors, default-off/default-on posture, rubric linkage, or Build Authorization status.
3. **Q3 — Authority-level defaults.** Stage A promoted detectors default to **Level 3 — Specialist Agent**: they may produce domain-specific evidence and review specialized risks, but they cannot override command rules, finalize high-risk cases alone, approve risky actions, or act autonomously. A detector may be lower (Level 1 Observer) if its evidence is immature; any higher level requires its own signed authority decision.
4. **Q4 — Decision Evidence Record field set.** The seven-field interface in §5 is sufficient for v1: `observed_facts`, `interpretations`, `assumptions`, `missing_evidence`, `recommended_verification`, `final_outcome_contribution`, and `retest_or_learning_record`. `confidence`, `evidence_strength`, and `contradictions` are deferred to a later signed amendment so the v1 contract stays simple and avoids inventing premature scoring semantics.
5. **Q5 — Promotion/demotion storage.** Promotion/demotion conditions are **spec-only text in v1**. A future ledger/schema for agent reputation events is explicitly deferred until there is enough real or synthetic correction evidence to design it honestly. No reputation engine is implied by this template.
6. **Q6 — Two-pass linkage.** Pure detectors may declare **Pass 1 only** until the Two-Pass Decision Model spec is signed. They should still state what evidence they provide for a future Pass 2 challenge, but they do not need to define challenge behavior before that orchestration contract exists.
7. **Q7 — Canonical source (settled, do not relitigate).** `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` is the **canonical design source** for agent design and milestone shaping — permanently, going forward. `agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md` (the v1 70-agent map) is **inventory/backlog cross-map only** and is **not a competing design source**. The v1 map served its purpose and will not be reinstated as canonical; future sessions must not treat it as the design authority or "look back" to it for design decisions. Any change to this canonical-source decision requires an explicit operator instruction, not a session interpretation.

### §10.B Implementation Boundary

Resolving §10 and signing §11 authorizes **no** implementation, no runtime enforcement, no retrofits, and no new agent behavior. It locks the governance template only. Applying it to #10/#21 or future agents is a separate gated slice.

## §11 Sign-off

Pre-§11 draft. §10 is resolved in §10.A and this spec is ready for operator signature. Signing will lock D1-D10 and the §10.A operator-confirmed decisions as the Agent Design Contract Template. Signing does **not** implement a runtime agent registry, reputation engine, two-pass orchestrator, or any detector retrofit. No code generation or environment writes occur until a separate explicit operator Build Authorization or metadata-retrofit instruction.

> §11 SIGNED — Matt Nichol June 6th 2026

This §11 signature locks D1-D10 and the §10.A operator-confirmed decisions as the governing Agent Design Contract Template. It does **not** implement a runtime agent registry, reputation engine, two-pass orchestrator, or any detector retrofit; no code generation or environment writes occur until a separate explicit operator Build Authorization or metadata-retrofit instruction.
