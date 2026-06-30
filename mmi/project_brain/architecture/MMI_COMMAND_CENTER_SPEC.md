# MMI Command Center Spec

Last updated: 2026-06-28T17:04:54-07:00  
Authority: Matt (Super)  
Owner: Codex (Backbone / runtime support)  
Source task: `mmi-command-center-spec`

---

## Purpose

The MMI command center is a local, read-only operating panel for Matt and lane owners. It shows the current task pipe state, the active task, the assigned lane, the next action, and direct links to the MMI project brain.

This spec defines the first skeleton only. It does not create a web app, run npm, deploy anything, or reactivate paused Social Architect, DAX, or Trades lanes.

---

## MVP Outcome

The first runnable skeleton should answer five questions immediately:

1. Is the MMI pipe loaded, on hold, blocked, or dry?
2. What task is active?
3. What is the task score?
4. Who owns the next action?
5. Which project-brain files explain the current scope?

---

## Recommended Form

Build the first skeleton as a local Python CLI panel, not a web UI.

Recommended future file:

`mmi/command_center.py`

Reasoning:

- Existing data sources are Python scripts and `tasks.json`.
- No browser, npm, or Social Architect `web/` surface is needed.
- A CLI panel is easiest to verify from the current pipe commands.
- It can later be wrapped by a TUI or static local page if Matt asks.

---

## Data Sources

| Source | Use |
|---|---|
| `tasks.json` | Active task id, score, assignee, tier, instruction, status |
| `scripts/reload_mmi_pipes.py` | Pipe status semantics: LOADED, HOLD, BLOCKED, DRY |
| `scripts/next_task.py` | Existing next-task display contract |
| `mmi/project_brain/status/MMI_ACTIVE_SCOPE.md` | Current scope lock |
| `mmi/project_brain/status/MMI_PHASE2_START.md` | Phase-2 start state |
| `mmi/project_brain/architecture/MMI_PHASE2_MVP_ARCHITECTURE.md` | Phase-2 boundaries and increments |
| `mmi/project_brain/status/MMI_LANE_ROUTING.md` | Lane ownership and routing |
| `mmi/project_brain/status/MMI_TASK_REGISTRY_LOCAL.md` | Queue conventions |

The command center should read data directly where practical. It should not shell out to `npm`, `ops/run.py`, Social Architect operators, or external services.

---

## Pipe Status Model

The skeleton should map local queue state to one of four statuses:

| Status | Meaning | Next action |
|---|---|---|
| `LOADED` | Active MMI task exists | Show task and owner |
| `HOLD` | No active build task because Matt/Super input is required | Show blocker and requested directive |
| `BLOCKED` | Active task is non-MMI or malformed | Stop and show correction needed |
| `DRY` | No active task and no hold blocker | Ask Cursor PM or Matt to seed the next bounded MMI task |

The current implementation can derive these states from the same rules used by `reload_mmi_pipes.py`.

---

## Display Contract

The first screen should be dense and plain. Example output:

```text
MMI COMMAND CENTER
PIPE STATUS: LOADED

ACTIVE TASK
  ID:       mmi-command-center-spec
  SCORE:    88
  OWNER:    Codex
  TIER:     Backbone / runtime support
  STATUS:   pending

NEXT ACTION
  Codex: write mmi/project_brain/architecture/MMI_COMMAND_CENTER_SPEC.md

PROJECT BRAIN
  Scope:        mmi/project_brain/status/MMI_ACTIVE_SCOPE.md
  Phase start:  mmi/project_brain/status/MMI_PHASE2_START.md
  Architecture: mmi/project_brain/architecture/MMI_PHASE2_MVP_ARCHITECTURE.md
  Routing:      mmi/project_brain/status/MMI_LANE_ROUTING.md
```

The display must include:

- task id
- score
- assignee
- tier
- pipe status
- next action
- project-brain links

---

## Next Action Rules

| Condition | Next action text |
|---|---|
| Active task assigned to Codex | `Codex executes the required output, then marks task complete or reports blocker.` |
| Active task assigned to Cursor PM | `Cursor PM completes PM-owned queue/status work.` |
| Active task assigned to Matt | `Matt provides directive or approval before work continues.` |
| Active task assigned to Claude | `Route design/spec work to Claude.` |
| Active task assigned to Gemini Paid API | `Route audit/check work to Gemini Paid API.` |
| Active task assigned to Gemini | `Route primary research to Gemini.` |
| Active task assigned to ChatGPT | `Route deep/secondary research to ChatGPT.` |
| Non-MMI active task | `BLOCKED: pause or complete non-MMI task before continuing.` |
| No active task and no hold | `DRY: Cursor PM should seed the next bounded MMI task after Matt approval.` |

---

## Project-Brain Link Set

The skeleton should always show these links:

| Label | Path |
|---|---|
| Active scope | `mmi/project_brain/status/MMI_ACTIVE_SCOPE.md` |
| Phase-2 start | `mmi/project_brain/status/MMI_PHASE2_START.md` |
| Phase-2 architecture | `mmi/project_brain/architecture/MMI_PHASE2_MVP_ARCHITECTURE.md` |
| Lane routing | `mmi/project_brain/status/MMI_LANE_ROUTING.md` |
| Task registry | `mmi/project_brain/status/MMI_TASK_REGISTRY_LOCAL.md` |

Optional later links:

- `mmi/project_brain/mission/MMI_MISSION_BRIEF.md`
- `mmi/project_brain/status/MMI_DEPLOYER_QUEUE_CHECK.md`
- latest status file under `mmi/project_brain/status/`

---

## Skeleton Interface

Recommended CLI flags for the future skeleton:

```bash
python3 mmi/command_center.py
python3 mmi/command_center.py --json
python3 mmi/command_center.py --watch --seconds 60
```

| Flag | Behavior |
|---|---|
| none | Print human-readable panel once |
| `--json` | Print structured state for future tools |
| `--watch --seconds N` | Reprint panel every N seconds, minimum 5 |

Structured output shape:

```json
{
  "pipe_status": "LOADED",
  "active_task": {
    "id": "mmi-command-center-spec",
    "score": 88,
    "assignee": "Codex",
    "tier": "Backbone / runtime support",
    "status": "pending",
    "instruction": "PROJECT: MMI. ..."
  },
  "next_action": "Codex executes the required output, then marks task complete or reports blocker.",
  "project_brain_links": [
    "mmi/project_brain/status/MMI_ACTIVE_SCOPE.md",
    "mmi/project_brain/status/MMI_PHASE2_START.md",
    "mmi/project_brain/architecture/MMI_PHASE2_MVP_ARCHITECTURE.md",
    "mmi/project_brain/status/MMI_LANE_ROUTING.md",
    "mmi/project_brain/status/MMI_TASK_REGISTRY_LOCAL.md"
  ]
}
```

---

## Validation Checks

The skeleton should fail closed:

1. `tasks.json` missing or invalid JSON -> `BLOCKED`
2. active task exists but id does not start with `mmi-` and instruction does not start with `PROJECT: MMI.` -> `BLOCKED`
3. more than one active task -> `BLOCKED` with list of active task ids
4. active MMI task exists -> `LOADED`
5. no active task but `mmi-await-matt-phase2` is paused -> `HOLD`
6. no active task and no hold -> `DRY`

This is stricter than `scripts/next_task.py`, which only prints the first active task. The command center should protect Matt from silent queue ambiguity.

---

## Implementation Notes For Next Increment

The next Codex task should implement the skeleton in a small, testable Python module.

Suggested file:

`mmi/command_center.py`

Suggested functions:

| Function | Responsibility |
|---|---|
| `load_tasks(path)` | Read and validate `tasks.json` |
| `active_tasks(tasks)` | Return all active-status tasks |
| `is_mmi_task(task)` | Enforce MMI id/instruction guard |
| `detect_pipe_status(tasks)` | Return `LOADED`, `HOLD`, `BLOCKED`, or `DRY` |
| `next_action_for(task, pipe_status)` | Produce lane-aware next action |
| `project_brain_links()` | Return fixed link set |
| `render_text(state)` | Human-readable CLI panel |
| `render_json(state)` | Machine-readable JSON |

Keep the module read-only in the first implementation. It should not mutate `tasks.json`.

---

## Hard Stops

- Do not run `npm`.
- Do not edit `web/`.
- Do not run `ops/run.py`.
- Do not call external services.
- Do not infer active scope from root Social Architect docs.
- Do not route active work to DAX, Trades, SAGE, MAVEN, HAVEN, or Social Architect Phase 1 unless Matt explicitly reactivates that lane.
- Do not seed additional tasks from the command-center skeleton itself.

---

## Completion Criteria

This spec is complete when:

1. It defines the local command-center purpose and MVP boundary.
2. It specifies display fields for task id, score, assignee, pipe status, next action, and project-brain links.
3. It identifies existing pipe scripts as the source concept.
4. It recommends a local Python CLI skeleton instead of web/npm work.
5. It defines validation and hard-stop behavior for the next implementation increment.
