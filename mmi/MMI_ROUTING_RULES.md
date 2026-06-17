# MMI_ROUTING_RULES.md — Which Model Gets Which Task

**Authority:** Matt Nichol — authorized June 16 2026

MMI selects the lane. Matt authorizes phase, scope, and signatures — not routine tool choice.
`AGENTS.md` §2.2 remains the higher-level orientation source if wording conflicts.

---

| Model/tool | Role |
|---|---|
| ChatGPT | Research, scope guard, intent translation, synthesis |
| Gemini | Cross-check, second-opinion, adversarial validation |
| Claude | Concept docs, architecture writeups, governance drafts |
| Cursor | Repo execution — multi-file edits, implementation, git, verification runs |
| Codex | Pre-build plan review, diff review, command verification, adversarial critique, independent review |
| Grok | Completion gate auditor (negative-feedback gate) |
| Matt | Final approval, acceptance, priority, authority, §11 signatures |

---

## Matt target vs MMI lane (operator decisions 2026-06-16)

```text
Matt names the authorized target.
MMI assigns the lane by task shape.
Matt only picks the worker when routing affects authority, scope, live data, or material risk.
```

Dispatcher output labels: `OPERATOR_NAMES_TARGET`, `MMI_ASSIGNS_LANE`,
`LANE_ESCALATION_TO_MATT`, `BUILD_AUTHORIZATION_IMPLIED`.

---

## Auto-routing (MMI decides; Matt does not pick the tool)

| Task shape | Route to |
|---|---|
| Signed contract ready to build | Cursor plan → Codex pre-build review → Cursor build |
| Repo edit / implementation / multi-file change | Cursor |
| Diff review / command verification / adversarial critique | Codex |
| Independent review of gated adversarial evidence | Codex (`OPERATOR_ACTION_REQUIRED: NO`) |
| Long doctrine / architecture critique / spec prose | Claude |
| Intent translation / prompt construction / routing / scope guard | ChatGPT |
| Cross-check / red-team packet (pre-contract) | Gemini |
| Completion gate (0/0 blocking) | Grok (Cursor stages manifest + runs gate) |
| Signature / push / authority / business decision | Matt |
| Next phase when queue is empty (ALL_CLEAR) | Matt names target; MMI surfaces `CANDIDATES` |

**Escalate to Matt only when** the routing decision itself affects authority, signed scope,
live/customer data, or material project risk — not for routine Cursor vs Codex assignment.

---

## Build loop

```
§11 signed → Cursor drafts build plan → Codex reviews plan → Cursor builds
→ Codex post-build review (where required) → adversarial suite (when required)
→ complete_gate.py 0/0 → GATED
```

---

## ALL_CLEAR candidates

When `MODE: ALL_CLEAR`, MMI emits concrete next-direction candidates labeled:
`SCOREBOARD_READY`, `NEEDS_SCOREBOARD_ROW`, `NEEDS_MMI_REVIEW`, `PARKED_DRAFT`,
`NOT_AUTHORIZED`. Candidates are a routing compass — **not authorization**.

---

## Rule

> No model gets to both design, build, approve, and audit the same thing.

Routing assigns a task to exactly one lane at a time. A task that has been built by Cursor is audited by Grok and accepted by Matt — never re-approved by the lane that produced it.
