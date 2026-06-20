# Plain-English Explanation Agent Design Contract — missing out-of-scope fixture

**Status:** §11 SIGNED 2026-06-20 by Matt Nichol (fixture)

## §1 Scope

### In scope
- Wrapper only.

## FLOW CONTRACT

| Field | Value |
|---|---|
| output_location | `EmailAnalysisPayload.client_facing_rubric` |
| output_format | `ClientFacingRubricPayload` |
| downstream_consumer | `core/drafting/daily_digest_agent.py` |
| consumer_usage | Reads `analysis.client_facing_rubric.axes[*].why_this_score` |

## BUILD CONDITIONS

- CHECK: file_exists: 3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/client_facing_rubric.py
