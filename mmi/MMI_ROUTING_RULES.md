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

## Matt target vs MMI lane (operator decisions 2026-06-16; delegation restore 2026-06-18)

```text
Matt authorizes scope, signatures, and authority forks.
MMI delegates the next evidence-backed task and assigns the lane by task shape.
MMI scores/ranks candidates and explains why the top task wins.
Matt only intervenes when routing affects authority, scope, live data, or material risk.
```

Dispatcher output labels: `OPERATOR_NAMES_TARGET`, `MMI_ASSIGNS_LANE`,
`LANE_ESCALATION_TO_MATT`, `BUILD_AUTHORIZATION_IMPLIED`, `CURRENT_PROJECT_TRUTH`,
`TASK_SCOREBOARD`, `NEXT_DELEGATED_TASK`, `TASK_SCORE`, `WHY_THIS_TASK`,
`LOWER_SCORE_ALTERNATIVES`, `SOURCE_EVIDENCE`, `REQUIRED_UPDATE_AFTER_COMPLETION`.

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
| Queue empty of build/audit/review lanes (`MODE: DELEGATE`) | MMI delegates highest-scored evidence-backed task |

**Escalate to Matt only when** the routing decision itself affects authority, signed scope,
live/customer data, or material project risk — not for routine Cursor vs Codex assignment.

---

## Delegation scoring (`MODE: DELEGATE`)

When no BUILD/AUDIT/REVIEW/DESIGN lane is active, MMI scores repo evidence and delegates:

| Classification | Score | Typical worker |
|---|---|---|
| `SCOREBOARD_READY` | 100 | Cursor → Codex → Cursor |
| `NEEDS_SCOREBOARD_ROW` | 88 | Cursor (tracker) |
| `INTAKE_CLASSIFY_BATCH` | 72 | Cursor (classify parked drafts) |
| `EXTERNAL_LANE` | 68 | Cursor (external repo) |
| `NEEDS_MMI_REVIEW` | 65 | Claude |
| `RESEARCH` | 58 | ChatGPT / Gemini |
| `PARKED_DRAFT` | 25 | Cursor (single-file classify) |

`MODE: ALL_CLEAR` only when **no** evidence-backed task exists. It does **not** mean
"Matt must manually name the next target" when delegable evidence exists.

---

## Worker completion → MMI update first

After Cursor, Codex, Claude, ChatGPT, Gemini, or Grok completes work:

1. Append evidence to the relevant MMI record (`MMI_INTAKE_RECORDS.md`, gate registry, or decision log).
2. Update `MMI_CURRENT_STATE.md` `LAST_COMPLETED` prose.
3. Run `python3 scripts/mmi_dispatch.py --sync`.
4. Commit routing-authority files.
5. Run `python3 scripts/mmi_dispatch.py --verify`.

---

## Build loop

```
§11 signed → Cursor drafts build plan → Codex reviews plan → Cursor builds
→ Codex post-build review (where required) → adversarial suite (when required)
→ complete_gate.py 0/0 → GATED
```

---

## ALL_CLEAR vs DELEGATE

- **`MODE: DELEGATE`** — MMI scored repo evidence and delegated the top task. Matt is not
  required to manually name the next target unless `OPERATOR_ACTION_REQUIRED: YES`.
- **`MODE: ALL_CLEAR`** — no evidence-backed task surfaced. Matt must supply new evidence
  (signed contract, scoreboard row, or intake).

Lower-scored alternatives appear in `LOWER_SCORE_ALTERNATIVES` and `CANDIDATES` for
context only — not authorization.

---

## Rule

> No model gets to both design, build, approve, and audit the same thing.

Routing assigns a task to exactly one lane at a time. A task that has been built by Cursor is audited by Grok and accepted by Matt — never re-approved by the lane that produced it.
