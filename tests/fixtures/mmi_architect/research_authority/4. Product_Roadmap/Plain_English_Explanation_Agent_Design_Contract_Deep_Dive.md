# Plain-English Explanation Agent Design Contract — research authority fixture

**Status:** §11 SIGNED 2026-06-20 by Matt Nichol (fixture)

## §1 Scope

### Out of scope
- No autonomous action.

## FLOW CONTRACT

| Field | Value |
|---|---|
| output_location | `mmi/research/MMI_FIXTURE_RESEARCH.md` (authority source) |
| output_format | research note |
| downstream_consumer | research note |
| consumer_usage | Uses `mmi/research/MMI_FIXTURE_RESEARCH.md` as required authority for done conditions |

## BUILD CONDITIONS

- CHECK: file_exists: mmi/research/MMI_FIXTURE_RESEARCH.md
