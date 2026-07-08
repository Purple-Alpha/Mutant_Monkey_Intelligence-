# MMI Active Scope

Last updated: 2026-07-02

## Current Directive

We are strictly working on MMI. **Operator roadmap:** `status/MMI_PROJECT_ROADMAP_2026-07.md` · **Moat:** `architecture/MMI_DIFFERENTIATOR_2026-07.md`

## Matt rule — concepts stay on the map

**PARKED ≠ rejected.** Ideas that feel like fantasy remain in `architecture/MMI_CONCEPT_INVENTORY_AND_GAPS_2026-07.md` and the roadmap PARKED table until chaos-lab falsification or explicit Matt retirement. Build order controls **when**, not **whether**.

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
- Do not drop PARKED concepts for sounding unrealistic — route to research or inventory.

## Current Queue Rule

`scripts/next_task.py` and `task_runner.py` should show MMI tasks only for active work.

**Active (2026-07-02):** Cryptolalia lab wire **BUILT** — iceberg `MIRROR_DIMENSION` diverts emit cryptolalia in lab when `mirror_lab_root` set. Next: Option B provisioner wire + full iceberg chaos re-run.

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

## Mandatory Authority Laws - 2026-07-07

All agents must read and obey mmi/project_brain/status/MMI_BUILD_AND_PRESERVATION_AUTHORITY_LAWS_20260707.md before selecting a next lane, committing/pushing, proposing build work, running audits, or closing a session.

Key binding points:

- Evidence decides the next lane; Matt is not asked to choose when rubric evidence decides.
- Every next lane must name the primary model, secondary review model, execution operator, forbidden tools, and ownership reason.
- Daily backup, commit, push, and remote-head verification are preservation law, not optional hygiene.
- No build, execution, cleanup, delete, reset, force-push, kernel/minifilter/IOCTL testing, or restore-check script execution without explicit Matt authorization.
- Accepted artifacts must be committed and pushed, or explicitly listed as intentionally untracked/quarantine. No silent loose files.
