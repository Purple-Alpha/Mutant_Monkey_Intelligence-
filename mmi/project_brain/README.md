# MMI Project Brain

This folder is the operator-facing project brain for Mutant Monkey Intelligence.
It exists to keep the build pointed at a real milestone instead of letting the
queue drift into whatever file changed last.

## Brain Map (canonical)

There is **one** operator project brain: this folder (`mmi/project_brain/`).
The former Windows folder `project-brainarchitecturereality-controller` was merged
into `architecture/reality_controller/` (2026-06-26). Do not maintain a second copy.

## Daily Command

Use this first:

```bash
python3 scripts/mmi_pm_voice.py
```

The default output should stay small:

```text
MMI_OPERATOR_CONSOLE
status: ACTION | NO_BUILDABLE | BLOCKED
task: the next concrete task
for: Matt | Cursor | Codex | Claude | Gemini | ChatGPT | Grok
score: n/10
```

## Control Rule

No task is considered healthy unless it has all four fields:

- `milestone`: what larger objective it advances
- `lane`: what kind of work it is
- `owner`: who should handle it
- `score`: how strong the next action is

If any field is missing, the task should be treated as weak or blocked until it
is clarified.

## Brain Map

- `mission/`: what we are building toward
  - `short_term_goals.md` — ~30–90 day direction (read weekly)
  - `long_term_goals.md` — 12 mo → 5 yr strategic arc (read each major cycle)
  - `milestone_map.md` — M1–M5 engineering milestones
- `lanes/`: categories for routing work
- `architecture/`: system boundaries and technical maps
  - `purple_translation_layer.md` — defensive-first Blue/Purple research
  - `reality_controller/` — merged lab-only deception stack (RESEARCH_DESIGN; not build)
- `decisions/`: links to decision records and signed authority
- `runbooks/`: how to operate the control plane
- `status/`: current task, blocked items, and next actions

## Score Meaning

- `8-10`: strong action; likely worth doing now
- `4-7`: useful but should be checked against the active milestone
- `1-3`: weak/backlog; do not let it become the main build unless Matt picks it
- `n/a`: no buildable task

