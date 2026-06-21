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

**Open handoff:** latest line whose `state` starts with `DONE_AWAITING_`.

**Rules:** Do not edit or delete existing lines. PM Voice reads this log; PM Voice never writes it.

---
ts=2026-06-20T22:30:00Z | task=ARCHITECT_PARSER_ALIGNMENT_PATCH | by=Cursor | did=parser patch built (829175b, d53ef03) | state=DONE_AWAITING_CLOSEOUT | next_step=close MMI records (DEC + LAST_COMPLETED) | evidence=829175b/d53ef03
