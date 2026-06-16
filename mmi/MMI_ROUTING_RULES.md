# MMI_ROUTING_RULES.md — Which Model Gets Which Task

**Authority:** Matt Nichol — authorized June 16 2026

---

| Model/tool | Role |
|---|---|
| ChatGPT | Research, review, adversarial critique, synthesis |
| Gemini | Cross-check, second-opinion, adversarial validation |
| Claude | Concept docs, architecture writeups, governance drafts |
| Cursor | Code execution against signed specs only |
| Grok | Completion gate auditor |
| Matt | Final approval, acceptance, priority, authority |

---

## Rule

> No model gets to both design, build, approve, and audit the same thing.

Routing assigns a task to exactly one lane at a time. A task that has been built by Cursor is audited by Grok and accepted by Matt — never re-approved by the lane that produced it.
