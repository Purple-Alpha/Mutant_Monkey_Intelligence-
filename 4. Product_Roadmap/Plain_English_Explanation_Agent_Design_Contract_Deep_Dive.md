# Plain-English Explanation Agent Design Contract — Spec-First Deep Dive

**Draft ID:** `MMI_52_PLAIN_ENGLISH_EXPLANATION_AGENT_DESIGN_CONTRACT_DRAFT`

**Status:** DRAFT — UNSIGNED. **Not in force.** Pre-sign patch applied 2026-06-20 (`MMI_52_PRE_SIGN_PATCH_ONLY`). Does not authorize build, §11 signature, scoreboard reconcile, registry registration, production dispatch, or AUTH-5.

**Candidate:** #52 — Plain-English Explanation

**Owner:** Matt Nichol

**Brand:** internal codename **NorthStar Inbox Shield** in code/spec prose per rebrand Option B; buyer-facing surfaces use **Mutant Monkey** only where separately signed buyer-facing specs require it. No rename implied.

**Source-of-truth links:**
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (governing template; Evidence Stage model)
- `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` (§11-signed rubric spec; §5 schema; §6 rendering contract)
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (#52 Plain-English Explanation; Layer 4 Evidence)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design source)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/client_facing_rubric.py` (`project_client_facing_rubric`; immutable projection function)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/blackboard/models.py` (`EmailAnalysisPayload`, `ClientFacingRubricPayload`, `EmailRiskAxisBreakdown`)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/drafting/daily_digest_agent.py` (`DailyDigestAgent`; downstream digest/report consumer)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/agent_contract.py` (`Agent`, `AgentContribution`)
- `VISION.md` (Stage A = analyze / recommend / evidence only; seven non-negotiables)

**Proposed future build path (not authorized here):** `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/plain_english_explanation_agent.py` (`PlainEnglishExplanationAgent` wrapper + focused tests). No file is authorized until §11 signature / Build Authorization.

---

## Agent Design Contract block

**Boundary:** #52 explains an existing evidence/verdict object. It does **not** detect. It does **not** judge. It does **not** score. It does **not** advise beyond the input. It does **not** read raw source data. It does **not** send/transmit explanations. It writes nothing. It is **not** autonomous. **AUTH-5 remains blocked.**

This contract governs a future Plain-English Explanation **agent wrapper** around the signed deterministic rubric projection in `client_facing_rubric.py`. It is additive governance under `Agent_Design_Contract_Template_Deep_Dive.md` §7.0. It does **not** edit, reinterpret, relax, or extend the §11-signed Client-Facing 5-Axis Email Scoring Rubric spec, the projection logic in `client_facing_rubric.py`, internal `risk_score` / `recommended_action`, or any detector/scoring pipeline wiring.

| Field | Value |
|---|---|
| Agent name | Plain-English Explanation Agent (`PlainEnglishExplanationAgent`) |
| Swarm inventory ID | #52 — Plain-English Explanation |
| Canonical layer | 4 — Evidence |
| Canonical team / case type | Evidence / explainability; deterministic plain-English axis explanation over one validated analysis verdict |
| Authority level | Level 3 — Specialist Agent |
| Stage posture | VISION Stage A — analyze / recommend / evidence only. Distinct from Evidence Stage (template §6.0). |
| Evidence Stage (current) | **Stage 1 — Synthetic** at §11 signature, if signed. Validation is synthetic-only over validated `EmailAnalysisPayload` fixtures. Intentionally NOT registered in `build_default_registry` / production dispatch. Advancement requires template §6.2 and Matt-signed promotion. |
| Role | Emit plain-English per-axis `why_this_score` strings by running the signed client-facing rubric projection (`project_client_facing_rubric`) over one validated `EmailAnalysisPayload`. The wrapper explains the existing analysis verdict object; it does not create a new score, action, or disposition. |
| Boundary | Read-only Evidence agent over one validated analysis payload. The wrapper must not detect threats, mutate scoring, lower/raise risk, change `recommended_action`, invent advice beyond the signed rubric mapper output, read raw mailbox bodies/attachments/headers directly, transmit explanations, write Blackboard records, or alter `core/scoring/client_facing_rubric.py`. |
| Explicit non-authorities | No autonomous action; no block/quarantine/deny/reject verb; no buyer-facing compliance claim; no network/HTTP/DNS/LLM call; no raw-source read; no explanation send/transmit path; no Blackboard write at Stage 1; no default-registry registration; no production dispatch at Evidence Stage 1; no Evidence Stage 2/3 promotion; no AUTH-5; no scoring/rubric logic change. |
| Inputs | One tenant-scoped validated `EmailAnalysisPayload` on an `EMAIL_ANALYSIS` Blackboard record, located via `MissionContext.source_record_id`. Reads validated analysis sub-objects only (`EmailAnalysisRiskAnalysis`, `EmailAnalysisImpersonationAnalysis`, optional ransomware-precursor analysis, `behavioral_deviation_flags`, `forced_escalation_triggers`, and related validated fields already on the payload). Does **not** read raw `EMAIL_INBOUND` body, attachment bytes, or external systems. If `source_record_id` is missing, the record is absent, the payload fails validation, or required analysis sub-objects are not traceable, the wrapper must refuse with `INPUT_INSUFFICIENT_CANNOT_EXPLAIN` and name the missing field(s). |
| Outputs | Exactly one of two envelopes: (1) bounded explanation surface — projected `ClientFacingRubricPayload` on the in-memory analysis copy returned to the explicit caller/test, with every `why_this_score` line traceable to input payload fields via `project_client_facing_rubric()`; or (2) `INPUT_INSUFFICIENT_CANNOT_EXPLAIN` when required inputs are missing or not traceable. No verification/challenge/score/action fields are emitted. No plain-English explanation is emitted on the refusal path. |
| Evidence emitted | Closed-set plain-English axis explanation facts only, derived from `ClientFacingRubricPayload.axes[*].why_this_score`, `axis_total`, `rubric_status`, and bounded consistency markers when present. No new detector facts, no disposition, no payment guidance beyond what the signed rubric mapper already encodes. |
| Data minimization | Explanations are bounded by rubric D15 (160-char `why_this_score` cap) and D7 PII safety rules. No raw header chains, payment destinations, account/routing identifiers, mailbox body echoes, or unbounded generated text. |
| Tenant isolation | Reads only the tenant-scoped Blackboard path for the supplied `tenant_id`. Stage 1 tests must use isolated synthetic tenant IDs. Tenant A's analysis never explains tenant B. |
| Two-pass role | Evidence assembly only. `challenge()` returns `None`; Challenge / Final Review layers decide sufficiency. |
| Decision Evidence Record contribution | `observed_facts`: closed plain-English explanation facts only; `interpretations`: none; `assumptions`: upstream scoring/analysis pipeline produced a validated `EmailAnalysisPayload`; `missing_evidence`: wrapper does not prove operational production behavior or raw-mailbox fidelity; `recommended_verification`: none emitted directly; `final_outcome_contribution`: explanation projection only; `retest_or_learning_record`: every real-case miss or demotion trigger becomes a permanent regression test per template §6.5. |
| Human review trigger | Any move beyond synthetic explanation projection, any client-facing send/transmit path, any rubric-logic change, or any Evidence Stage promotion requires separate Matt-signed authorization. |
| Verification trigger | None authored by this agent. |
| Scoring / action posture | Facts-only explanation. The wrapper does not emit risk floors, recommended actions, payment decisions, or new axis scores beyond the signed rubric projection output. It never replaces internal scoring. |
| Default rollout | Evidence Stage 1: not registered in `build_default_registry`; wired only by explicit callers/tests until a later signed promotion. |
| Autonomous action | None. `autonomous_action_allowed = False`; Stage A router guard rejects autonomy. AUTH-5 remains blocked. |
| Promotion conditions | Per template §6.2. Stage 1 -> Stage 2 requires clean suite, zero open test failures, Matt review of >= 3 supervised explanation samples with expected axis wording, a `PROMOTION` entry in `decision_cycles_log.md`, and a Matt-signed Stage 2 promotion record. |
| Demotion conditions | Per template §6.3. Automatic: regression failure, cross-tenant contamination, raw-source/body/header/payment leakage, rubric-logic mutation, explanation send/transmit side effect, Blackboard write, out-of-layer field write, or external call. Matt-signed: auditor pattern flag or signed Challenge contradiction pattern. |
| Retest evidence | Per template §6.5 progressive hardening: every real-case miss / demotion trigger becomes a new permanent regression test. |
| Calibration requirement | Evidence Stage 1 is synthetic-only. Stage 2 requires supervised samples with operator-reviewed expected axis wording. Stage 3 requires Drift Watch active and real-data controls signed/open. |
| Failure modes | See §5. |
| Required tests | See §6 — wrapper tests must prove deterministic projection usage, read-only purity, tenant isolation, no raw-source reads, no send/transmit path, no Blackboard writes, no default registry, no network/subprocess behavior, and no scoring/action mutation. Existing rubric gate tests remain authoritative for mapper behavior. |
| Audit requirements | This contract draft and any future implementation remain subject to `complete_gate.py`. Draft gate required before §11 signature; implementation gate required before build close. |
| Signed-spec dependencies | `Agent_Design_Contract_Template_Deep_Dive.md`, `Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md`, `VISION.md`, `Compliance_and_Trend_Watch_Process.md`, and canonical design source `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md`. |
| Build Authorization dependency | At §11 signature, this agent is at **Evidence Stage 1** only. No build authorization is granted for Evidence Stage 2/3 registration, default registry, production dispatch, real-customer-data handling, explanation send/transmit, rubric/scoring mutation, or autonomous action until promotion conditions in §6.2 are satisfied and a separate promotion record is signed. |

---

## REPO_RECONCILIATION

Live-repo placeholders resolved 2026-06-20 (contract placement/reconcile only):

| Placeholder | Resolved value | Repo evidence |
|---|---|---|
| Upstream evidence/verdict schema | Validated `EmailAnalysisPayload` on tenant-scoped `EMAIL_ANALYSIS` Blackboard record (`MissionContext.source_record_id`) | `core/blackboard/models.py`; rubric spec integration shape `EmailAnalysisPayload.client_facing_rubric: ClientFacingRubricPayload \| None` |
| Projection function / explanation source | `project_client_facing_rubric()` in `core/scoring/client_facing_rubric.py` → `ClientFacingRubricPayload` with per-axis `why_this_score` | Signed rubric spec §5; immutable projection module docstring |
| Downstream consumer / report surface | `DailyDigestAgent` (`core/drafting/daily_digest_agent.py`) | Reads `analysis.client_facing_rubric.axes[*].why_this_score` and `axis_total` when `rubric_status == "available"`; rubric spec §6 / D17 report-only digest surface |

Repo-reconciliation placeholders: **resolved.**

Signability blockers from §10 operator dispositions: **resolved** (pre-sign patch 2026-06-20).

**No unresolved repo reconciliation items remain for §11 signature.**

---

## §0 Purpose

Unblock swarm #52 Plain-English Explanation by placing the Agent Design Contract that the MMI Architect, Estimator, and PM Voice layers already expect at `4. Product_Roadmap/Plain_English_Explanation_Agent_Design_Contract_Deep_Dive.md`.

The safe Stage 1 agent is narrower than a detector or scorer. It does not inspect raw mail, decide fraud, or send client reports. It runs the signed deterministic rubric projection over one validated analysis verdict object and makes the existing explanation surface available to governed downstream renderers such as the daily digest.

This contract is the governance step only. It does not build runtime code, sign §11, reconcile scoreboard lifecycle, populate Blueprint-of-Record, or unlock AUTH-5.

---

## §1 Scope

### In scope
- The Agent Design Contract block above, governing a future `PlainEnglishExplanationAgent` wrapper as a Layer 4 Evidence agent.
- Evidence Stage 1 (Synthetic) declaration at signature.
- Read-only use of validated `EmailAnalysisPayload` plus `project_client_facing_rubric()`.
- Facts-only plain-English explanation emission per signed rubric §6 rendering contract.
- Explicit non-goals: no detect/judge/score/advise-beyond-input, no raw-source read, no send/transmit, no writes, no autonomy, no AUTH-5.

### Out of scope
- Any change to `project_client_facing_rubric`, rubric axis definitions, band mapping, D15 length cap, or `ClientFacingRubricPayload` schema without a separate signed rubric revision.
- Replacement of existing `risk_score` or `recommended_action`.
- New network calls, GeoIP/ASN/phone lookup, external enrichment, or LLM prompt complexity.
- New detector families or tenant-specific custom axis definitions in v1.
- Client-configurable weighting in v1.
- Autonomous action, block/quarantine/deny/reject verbs, or buyer-facing compliance claims.
- Registering the agent in `build_default_registry` or production dispatch.
- Real-customer-data handling or Evidence Stage 2/3 promotion.
- Scoreboard lifecycle mutation, Blueprint-of-Record population, registry/default dispatch edits, or AUTH-5 unlock in this placement lane.

---

## FLOW CONTRACT

| Field | Value |
|---|---|
| upstream_input | Validated `EmailAnalysisPayload` on tenant-scoped `EMAIL_ANALYSIS` Blackboard record (`MissionContext.source_record_id`) |
| projection_source | `project_client_facing_rubric()` in `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/client_facing_rubric.py` |
| output_location | `EmailAnalysisPayload.client_facing_rubric` on the same tenant-scoped `EMAIL_ANALYSIS` Blackboard analysis context |
| output_format | `ClientFacingRubricPayload` per `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` §5 |
| downstream_consumer | `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/drafting/daily_digest_agent.py` (`DailyDigestAgent`) |
| consumer_usage | Reads `analysis.client_facing_rubric.axes[*].why_this_score` and `axis_total` for digest rendering per rubric spec §6 when `rubric_status == "available"`; shows unavailable sentinel when `rubric_status == "unavailable"` |
| insufficient_output | `INPUT_INSUFFICIENT_CANNOT_EXPLAIN` — required input fields are missing or not traceable; names missing field(s); emits no `ClientFacingRubricPayload` and no per-axis explanation lines |

---

## TWO-OUTPUT ENVELOPE

The Stage 1 wrapper emits **exactly one** of:

### Explanation envelope

Projected `ClientFacingRubricPayload` returned on the in-memory analysis copy. Every emitted `why_this_score` line must be backed by a trace to the input payload field(s) that produced it through `project_client_facing_rubric()`. When rubric projection fails validation, the signed rubric unavailable sentinel (`rubric_status="unavailable"`) is allowed; invented axis rows are not.

### Refusal envelope

```text
INPUT_INSUFFICIENT_CANNOT_EXPLAIN
missing_fields:
- <field_name>
WHY:
Required input fields are missing or not traceable, so #52 refuses to produce a plain-English explanation and names the missing field(s).
BOUNDARY:
advisory only; no explanation emitted; no scoring/action mutation; no send/transmit; no AUTH-5
```

**Per-line traceability invariant (checkable):** Every emitted explanation line must include or be backed by a trace to the input field(s) that produced it. If a line cannot be traced to an input field, it must not be emitted.

---

## BUILD CONDITIONS

- CHECK: file_exists: 3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/client_facing_rubric.py
- CHECK: file_exists: 4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md
- CHECK: field_present: EmailAnalysisPayload.client_facing_rubric
- CHECK: command_expect: python3 -m unittest 3.SwarmCommand_Engine.Agent_Loop_Runtime.Runtime_Implementation.tests.test_client_facing_rubric -v|exit_code=0
- CHECK: consumer_named: DailyDigestAgent
- CHECK: format_exact: bounded `ClientFacingRubricPayload` only; no raw-source read; no send/transmit; no scoring/action mutation
- CHECK: sentinel_exact: INPUT_INSUFFICIENT_CANNOT_EXPLAIN
- CHECK: invariant_present: per-line traceability — every emitted explanation line traceable to input field(s) or not emitted

Boundary enforcement targets (verified by §6 required tests):

- no raw `EMAIL_INBOUND` body/header/attachment read
- no explanation send/transmit path
- no Blackboard write from wrapper at Stage 1 unless separately signed
- no `risk_score` / `recommended_action` mutation
- no rubric-logic change inside `client_facing_rubric.py`
- tenant isolation enforced
- AUTH-5 remains blocked
- missing/untraceable input → `INPUT_INSUFFICIENT_CANNOT_EXPLAIN` with named `missing_fields:`
- every emitted explanation line traceable to input field(s) or not emitted

---

## §2 Locked Design Decisions (candidate — confirmed at §11)

- **D1 — Identity.** Plain-English Explanation is a Layer 4 Evidence agent, Authority Level 3 Specialist, VISION Stage A, Evidence Stage 1 (Synthetic) at signing. `agent_id = plain_english_explanation_001`.
- **D2 — Explain, do not detect.** The wrapper reads one validated `EmailAnalysisPayload`; it does not inspect raw mail or emit detector facts.
- **D3 — Projection-only boundary.** The only authorized explanation logic is `project_client_facing_rubric()` over the supplied payload. No alternate mapper, no LLM rewrite, no advice beyond signed rubric output.
- **D4 — Immutability of rubric/scoring surfaces.** This contract changes no rubric spec, projection code, internal scoring path, or digest prompt contract except through separate signed revisions.
- **D5 — Facts-only Layer 4 contribution.** The agent emits bounded explanation facts / `ClientFacingRubricPayload` only. It emits no verification/challenge/score/action/payment fields.
- **D6 — Read-only / no transmit.** Stage 1 produces explanation objects for governed consumers; it does not send email, publish buyer reports, or open network paths.
- **D7 — Persistence + rollout.** Contributions, if persisted, use registry-gated routes only when separately authorized. The agent is NOT in `build_default_registry` at Stage 1.
- **D8 — Stage A / no autonomy / AUTH-5 blocked.** No block/quarantine/deny/reject; no autonomous action; no AUTH-5 unlock at contract placement or Stage 1 build authorization.
- **D9 — Downstream consumer pin.** `DailyDigestAgent` is the named v1 digest/report consumer for `why_this_score` rendering per rubric D17.
- **D10 — Tests are the Stage 1 evidence.** Existing rubric gate tests plus focused wrapper tests must prove read-only purity, tenant isolation, no raw-source read, no send/transmit, missing-input refusal, per-line traceability, and no scoring/action mutation before build close.
- **D11 — Missing-input refusal.** When required inputs are missing or not traceable, the wrapper emits `INPUT_INSUFFICIENT_CANNOT_EXPLAIN`, names the missing field(s), and emits no plain-English explanation lines.
- **D12 — Per-line traceability.** Every emitted explanation line must include or be backed by a trace to the input field(s) that produced it. If a line cannot be traced to an input field, it must not be emitted. Traceability is satisfied when the line is produced solely by `project_client_facing_rubric()` over the supplied validated payload fields.
- **D13 — Stage 1 persistence shape (locked).** Stage 1 returns projected `ClientFacingRubricPayload` on the in-memory analysis copy to the explicit caller/test only. No Blackboard write and no Layer 4 `AgentContribution` persistence at Stage 1.
- **D14 — Scoring-agent path (locked).** `#52` complements and governs the optional `EmailRiskScoringAgent.enable_client_facing_rubric` path; it does not replace or mutate that scoring-agent flag or wiring. A caller chooses one projection path per analysis cycle; duplicate projection on the same payload in one pass is forbidden.
- **D15 — Downstream consumer pin (locked).** `DailyDigestAgent` is the sole named mandatory downstream consumer at §11 signature. Rubric §6 report-rendering fixtures/tests validate `ClientFacingRubricPayload` compatibility only; additional consumer registration requires Stage 2 promotion.

---

## §5 Failure modes

- **Detector creep** — wrapper starts reading raw mail or emitting detector facts. Mitigation: D2/D3 and explicit out-of-scope tests.
- **Scoring creep** — wrapper changes `risk_score`, `recommended_action`, or rubric mapper logic. Mitigation: D4/D5 and reuse of signed rubric tests.
- **Advice creep** — wrapper adds guidance beyond signed `why_this_score` strings. Mitigation: projection-only rule and digest consumer contract.
- **Transmit creep** — wrapper sends explanations directly. Mitigation: D6 explicit prohibition.
- **Write creep** — wrapper mutates Blackboard or scoring artifacts. Mitigation: Stage 1 read-only posture and boundary tests.
- **Cross-tenant bleed** — tenant A payload explained in tenant B context. Mitigation: tenant isolation tests mirroring rubric §8.13 discipline.
- **Silent invention** — wrapper emits explanation lines not traceable to input fields. Mitigation: D12 per-line traceability invariant and focused traceability tests.
- **Missing-input fabrication** — wrapper guesses explanations when inputs are absent. Mitigation: D11 `INPUT_INSUFFICIENT_CANNOT_EXPLAIN` refusal envelope.

---

## §6 Required tests

Minimum focused wrapper suite (future build):

1. Known validated payload projects deterministic `ClientFacingRubricPayload` with five fixed-order axes.
2. Each `why_this_score` respects the 160-char cap and contains no raw header/body/payment leakage.
3. Wrapper does not mutate input `risk_score` or `recommended_action`.
4. Wrapper does not read raw `EMAIL_INBOUND` records when only analysis payload is in scope.
5. Wrapper performs no send/transmit side effects.
6. Wrapper performs no unauthorized Blackboard writes at Stage 1.
7. Tenant isolation: tenant A analysis never explains tenant B.
8. Default registry exclusion preserved.
9. No network/subprocess calls.
10. Existing `test_client_facing_rubric` suite remains passing without mapper changes.
11. Missing or untraceable required input (absent `source_record_id`, missing analysis record, invalid payload, or absent required analysis sub-object) emits `INPUT_INSUFFICIENT_CANNOT_EXPLAIN`, names `missing_fields:`, and emits no `ClientFacingRubricPayload` or per-axis explanation lines.
12. Per-line traceability: every emitted `why_this_score` line is backed by a trace to input payload field(s) through `project_client_facing_rubric()`; untraceable lines are absent from output.

**Done conditions (Stage 1 build close):** wrapper tests 1–12 pass; `INPUT_INSUFFICIENT_CANNOT_EXPLAIN` refusal path proven; per-line traceability invariant proven; existing rubric gate tests unchanged and passing.

---

## §10 Operator dispositions — resolved (locked for §11)

All former open questions are locked by pre-sign patch `MMI_52_PRE_SIGN_PATCH_ONLY` (2026-06-20):

| Former question | Locked disposition | §2 anchor |
|---|---|---|
| Stage 1 persistence shape | In-memory `ClientFacingRubricPayload` on analysis copy returned to explicit caller/test only; no Blackboard write; no Layer 4 `AgentContribution` persistence at Stage 1 | D13 |
| Wrapper vs scoring-agent attachment | Complement and govern; do not replace or mutate `EmailRiskScoringAgent.enable_client_facing_rubric`; one projection path per analysis cycle | D14 |
| Additional consumers beyond digest | `DailyDigestAgent` is the sole named mandatory consumer at signature; rubric §6 fixtures are compatibility tests only until Stage 2 promotion | D15 |

No signability-blocking open questions remain in §10.

---

## FUTURE_BUILD_NOTES (not signability scope)

Stage 2 promotion may revisit Blackboard persistence shape, Layer 4 `AgentContribution` emission, and explicit enumeration of additional report consumers. Those items require template §6.2 promotion conditions and a separate Matt-signed promotion record; they are not open questions for §11 signature of this contract.

---

## §11 Sign-off

**DRAFT — UNSIGNED.** §11 signature is operator-only and is **not** present in this placement draft.

Signing, when separately authorized, would lock D1-D15 and could authorize Evidence Stage 1 (Synthetic) wrapper build + focused tests only. Signing would **not** authorize scoreboard reconcile, Blueprint-of-Record population, registry/default dispatch, production dispatch, explanation send/transmit, rubric/scoring mutation, Evidence Stage 2/3 promotion, or AUTH-5.

> Operator signature placeholder — not signed.
