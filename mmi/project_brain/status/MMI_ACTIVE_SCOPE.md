# MMI Active Scope

Last updated: 2026-06-29

## Current Directive

We are strictly working on MMI.

## Operating Roles

| Role | Owner |
|---|---|
| Super | Matt |
| PM | Cursor |
| Backbone / runtime support | Codex |
| Design | Claude |
| Audit | Gemini Paid API |
| Main research | Gemini |
| Deep / secondary research | ChatGPT |

## Hard Stops

- Do not route active work to Social Architect Phase 1.
- Do not route active work to DAX or Trades unless Matt explicitly reactivates that lane.
- Do not seed non-MMI tasks into `tasks.json`.
- Do not treat old role docs as current if they conflict with this file.

## Current Queue Rule

`scripts/next_task.py` and `task_runner.py` should show MMI tasks only for active work.

## Local-First Policy

See `mmi/project_brain/architecture/MMI_LOCAL_CLOUD_POLICY.md`.

- **Local:** project brain, `tasks.json`, execution, command center
- **Cloud:** cold backup only (git-remote or encrypted sync) — not live runtime
- **NorthStar:** isolated — no bridge
- **Orchestrator scope:** `architecture/MMI_ORCHESTRATOR_SCOPE.md`

## Product Lanes (Matt-authorized)

| Lane | Status | Authority |
|------|--------|-----------|
| **MMI Security Intel** | Active (research ingested) | Matt decision A 2026-06-29 |

See `lanes/MMI_SECURITY_INTEL_LANE.md` and `architecture/MMI_SECURITY_INTEL_PRODUCT_SCOPE.md`. Core queue/war room/backup **unchanged** — intel pipeline runs **after** `mmi-war-room-v1`. Endpoint swarm from research is **not** build scope.
