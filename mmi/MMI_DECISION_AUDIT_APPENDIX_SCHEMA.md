# MMI Decision Audit Appendix Schema — Schema Only

**Status:** Tier 1 passive schema (F4). **No live decision history.** **Does not authorize autonomous selection.**

**Parent contract:** `mmi/MMI_AUTONOMOUS_BRAIN_TIER1_FOUNDATION_CONTRACT_DRAFT.md` (§11 SIGNED 2026-06-18)

**Parent doctrine:** `mmi/MMI_AUTONOMOUS_BRAIN_FOUNDATION_REVIEW_MATERIAL.md` §6

**Not created at Tier 1:** separate `MMI_DECISION_AUDIT_APPENDIX.md`, JSONL decision history, or populated appendix data files.

---

## Purpose

Define append-only records that preserve **every eligible candidate**, **lower-ranked alternatives**, and **full scoring reasoning** at each selection point. Prevents alternative laundering.

Illustrative examples below are **inside this schema doc only** — not live appendix data.

---

## Selection event (definition)

A **selection event** occurs when a single candidate becomes the active routed target, including:

- `NEXT_DELEGATED_TASK` set under `MODE: DELEGATE` (including mechanical top-score delegation)
- `RECOMMENDED_DIRECTION` emitted under `MODE: PROJECT_DIRECTION_RESEARCH`
- any equivalent current-state routed target naming one active candidate

Each selection event requires an appendix record **when a live appendix surface exists**. At Tier 1, only this schema exists.

---

## `decided_by` rules

| Phase | `decided_by` | Scope |
|---|---|---|
| Before AUTH-5 separately authorized | `MATT` | All selection events, including when dispatcher mechanically picks top delegation task |
| After AUTH-5 only, if ever separately authorized | `MMI` | Autonomous-selection events within AUTH-5 scope only |
| Never without AUTH-5 | `MMI` | Signatures, hardening claims, gate promotions, scoreboard flips |

---

## Record shape (append-only)

| Field | Type | Required | Notes |
|---|---|---|---|
| `selection_event_id` | string | yes | Unique; e.g. `SEL-2026-06-18-001` |
| `timestamp_utc` | ISO-8601 | yes | When selection recorded |
| `mode` | string | yes | e.g. `DELEGATE`, `PROJECT_DIRECTION_RESEARCH` |
| `selected_candidate` | string | yes | Name / label of chosen target |
| `selected_score` | string | no | Total or summary score string |
| `selected_reasoning` | string | yes | Axis breakdown or delegation reason |
| `eligible_candidates` | array | yes | All candidates considered |
| `non_selected_alternatives` | array | yes | Lower-ranked with scores + reasoning |
| `decided_by` | `MATT` \| `MMI` | yes | Per rules above |
| `evidence_cites` | string[] | yes | Paths / commits supporting scores |
| `candidates_not_authorization_note` | string | yes | Must state recommendation ≠ authorization |

### `eligible_candidates` / `non_selected_alternatives` entry

| Subfield | Required |
|---|---|
| `name` | yes |
| `score` | yes (or `blocked` + reason) |
| `axis_breakdown` | when project-direction rubric used |
| `blocked_reason` | when not eligible |

---

## Non-deletion rule

Appendix records are **never deleted**. Rejected, parked, and superseded candidates remain in `non_selected_alternatives` history.

---

## Illustrative example (fiction — not live data)

```text
selection_event_id: SEL-EXAMPLE-001
timestamp_utc: 2026-06-18T12:00:00Z
mode: PROJECT_DIRECTION_RESEARCH
selected_candidate: Draft #47 Case Timeline Agent Design Contract
selected_score: 16/20
selected_reasoning: revenue_market=1,product_foundation=2,... (full axis string)
eligible_candidates:
  - name: Draft #47 Case Timeline... | score: 16/20
  - name: Layer 5 Challenge agent... | score: 13/20
non_selected_alternatives:
  - name: Layer 5 Challenge... | score: 13/20 | axis_breakdown: ...
  - name: Stabilize... | score: 9/20 | ...
decided_by: MATT
evidence_cites: [agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md, mmi/MMI_DECISION_LOG.md]
candidates_not_authorization_note: RECOMMENDED_DIRECTION ranks only; Matt selects.
```

---

## Explicit non-authorization

This schema does **not**:

- authorize AUTH-5 autonomous task selection
- replace `MMI_DECISION_LOG.md` ACCEPT rows
- authorize dispatcher to read appendix for routing (future surfaces need explicit gate)
