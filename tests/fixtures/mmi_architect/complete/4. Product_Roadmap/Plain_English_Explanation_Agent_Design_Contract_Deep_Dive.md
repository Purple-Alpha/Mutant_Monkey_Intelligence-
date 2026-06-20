# Plain-English Explanation Agent Design Contract - Spec-First Deep Dive

**Status:** §11 SIGNED 2026-06-20 by Matt Nichol. Evidence Stage 1 (Synthetic) agent wrapper only.

**Owner:** Matt Nichol

**Source-of-truth links:**
- `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` (§11 signed rubric spec)
- `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/client_facing_rubric.py` (immutable projection function)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (governing template)

---

## Agent Design Contract block

| Field | Value |
|---|---|
| Agent name | Plain-English Explanation Agent (`PlainEnglishExplanationAgent`) |
| Swarm inventory ID | #52 — Plain-English Explanation |
| Canonical layer | 4 — Evidence |
| Role | Emit plain-English per-axis `why_this_score` strings by running the signed client-facing rubric projection over one validated `EmailAnalysisPayload`. |
| Inputs | One tenant-scoped `EMAIL_ANALYSIS` Blackboard record via `MissionContext.source_record_id`; reads validated analysis fields only. |
| Outputs | One `AgentContribution` (layer 4) carrying closed-set plain-English axis explanation facts derived from `ClientFacingRubricPayload`. |

---

## §1 Scope

### In scope
- Evidence Stage 1 synthetic wrapper around existing `client_facing_rubric.py` projection.
- Facts-only plain-English explanation emission per signed rubric §6 rendering contract.

### Out of scope
- No replacement of existing `risk_score` or `recommended_action`.
- No new network calls, GeoIP lookups, ASN lookups, phone lookup, or external enrichment.
- No new detector families.
- No ML model retraining or new LLM prompt complexity.
- No tenant-specific custom axis definitions in v1.
- No client-configurable weighting in v1.
- No autonomous action, block/quarantine/deny/reject verb, or buyer-facing compliance claim.
- No mutation of `core/scoring/client_facing_rubric.py` logic without separate signed spec revision.

---

## FLOW CONTRACT

| Field | Value |
|---|---|
| output_location | `EmailAnalysisPayload.client_facing_rubric` on tenant-scoped `EMAIL_ANALYSIS` Blackboard record |
| output_format | `ClientFacingRubricPayload` per `4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md` §5 |
| downstream_consumer | `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/drafting/daily_digest_agent.py` (`DailyDigestAgent`) |
| consumer_usage | Reads `analysis.client_facing_rubric.axes[*].why_this_score` and `axis_total` for digest rendering per rubric spec §6 when `rubric_status == "available"` |

---

## BUILD CONDITIONS

- CHECK: file_exists: 3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/client_facing_rubric.py
- CHECK: file_exists: 4. Product_Roadmap/Client_Facing_5_Axis_Email_Scoring_Rubric_Deep_Dive.md
- CHECK: field_present: EmailAnalysisPayload.client_facing_rubric
- CHECK: command_expect: python3 -m unittest tests.test_client_facing_rubric -v|exit_code=0
- CHECK: consumer_named: DailyDigestAgent

---

## §11 Sign-off

**§11 SIGNED — Matt Nichol, June 20 2026.**

Evidence Stage 1 synthetic wrapper only. No production dispatch at signing.
