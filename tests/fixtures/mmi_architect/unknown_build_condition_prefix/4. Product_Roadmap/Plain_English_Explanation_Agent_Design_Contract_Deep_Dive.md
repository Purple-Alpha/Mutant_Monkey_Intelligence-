# Unknown build condition prefix fixture

**Status:** §11 SIGNED 2026-06-20 by Matt Nichol (fixture)

## §1 Scope

### Out of scope
- No autonomous action.

## FLOW CONTRACT

| Field | Value |
|---|---|
| output_location | fixture output location |
| output_format | fixture output format |
| downstream_consumer | fixture consumer |
| consumer_usage | fixture usage |

## BUILD CONDITIONS

- CHECK: file_exists: 3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/scoring/client_facing_rubric.py
- CHECK: bogus_prefix: not allowed
