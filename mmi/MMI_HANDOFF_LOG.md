# MMI Handoff Log

Append-only. Each worker/model appends one line per handoff event using `scripts/mmi_handoff.py --append`.

**Line schema (one line per event):**

```text
ts=<ISO-8601> | task=<id> | by=<actor> | did=<summary> | state=<state> | next_step=<action> | evidence=<refs>
```

**States:**

- `DONE_AWAITING_CLOSEOUT`
- `DONE_AWAITING_GATE`
- `DONE_AWAITING_SIGN`
- `DONE_CLOSED`

**Open handoff:** among tasks whose **latest** log line is not `DONE_CLOSED`, the chronologically last line whose `state` starts with `DONE_AWAITING_` (append-only closeout: a later `DONE_CLOSED` for the same `task` closes that lane).

**Rules:** Do not edit or delete existing lines. PM Voice reads this log; PM Voice never writes it.

---
ts=2026-06-20T22:30:00Z | task=ARCHITECT_PARSER_ALIGNMENT_PATCH | by=Cursor | did=parser patch built (829175b, d53ef03) | state=DONE_AWAITING_CLOSEOUT | next_step=close MMI records (DEC + LAST_COMPLETED) | evidence=829175b/d53ef03
ts=2026-06-20T23:00:00Z | task=HANDOFF_SIGNAL_AND_PM_ROUTING | by=Cursor | did=handoff log writer + PM IN_FLIGHT routing built | state=DONE_AWAITING_SIGN | next_step=Matt §11 sign + close | evidence=953e1bc
ts=2026-06-21T06:00:00Z | task=HANDOFF_SIGNAL_AND_PM_ROUTING | by=Matt Nichol | did=Matt §11 signed handoff signal lane closed | state=DONE_CLOSED | next_step=lane closed | evidence=MMI-DEC-051; gate blockers resolved by operator closeout
ts=2026-06-21T06:30:00Z | task=ARCHITECT_PARSER_ALIGNMENT_PATCH | by=Matt Nichol | did=parser patch MMI closeout complete | state=DONE_CLOSED | next_step=lane closed | evidence=MMI-DEC-052; 829175b/d53ef03
