# MMI Active Scope

Last updated: 2026-07-13

## Current Directive

MMI and MMS product work is under a strict custody-maintenance freeze. No feature development resumes until `status/MMI_MMS_CUSTODY_MAINTENANCE_2026-07.md` closes its maintenance register and Matt explicitly lifts the freeze.

The prior product roadmap remains preserved but is not an active build queue during maintenance. **Operator roadmap:** `status/MMI_PROJECT_ROADMAP_2026-07.md` · **Moat:** `architecture/MMI_DIFFERENTIATOR_2026-07.md`

## MMI / MMS Product Identity Boundary

Matt defined the following distinct identities on 2026-07-13. This is a scope and custody boundary only; it does not authorize product implementation or runtime action.

| Product | Functional identity | Scope boundary |
|---|---|---|
| **MMI — Mutant Monkey Intelligence** | **The Self-Healing Organism** | Brain, internal autonomy, evidence, reasoning, decision-making, immune/self-healing loop, and Radar sensory awareness. Mutant Monkey Radar is **MMI-Core**. |
| **MMS — Mutant Monkey Security** | **The Reputation Fortress** | Purple-team defense and assault cost-maximization: an operational protection layer intended to increase the time, cost, and difficulty of attacks while protecting system and operator reputation. |

Within MMS, **fracturing** means lawful defensive disruption of an attacker's workflow and economics through resilience, detection, containment, evidence preservation, and recovery. It does not authorize retaliation, unauthorized access, harassment, public accusation, offensive reputation attacks, or action outside Matt-approved legal and operational boundaries.

Architectural guardrail: moving Radar into MMS configuration, source, or custody is a boundary violation unless Matt explicitly amends this definition. The loose Threat Intelligence Daemon remains an unassigned intelligence-input component pending a separate custody decision.

## Matt rule — concepts stay on the map

**PARKED ≠ rejected.** Ideas that feel like fantasy remain in `architecture/MMI_CONCEPT_INVENTORY_AND_GAPS_2026-07.md` and the roadmap PARKED table until chaos-lab falsification or explicit Matt retirement. Build order controls **when**, not **whether**.

## Operating Roles

| Role | Owner |
|---|---|
| Sole approval authority | Matt |
| Disk-aware controller / documentation custodian / bounded Git operator | Codex |
| Read-only design and bounded independent reviewer | Claude Code in terminal Plan mode, only for an exact Matt-authorized task |
| Bounded independent reviewer | Cursor, only for an exact Matt-authorized task; no PM or repository-control authority |
| Local bounded read-only precheck and cross-check | Qwen — specialist only; not repository controller or self-grader |
| Parked external models | Gemini and Grok — historical evidence preserved; no invocation, spend, or current role until Matt explicitly reactivates one |
| Historical editor/PM | Cursor — current authority removed by Matt 2026-07-13 |

## Hard Stops

- No product feature work during the custody-maintenance freeze.
- No account deletion, remote change, cleanup, restore-over-live-tree, commit, or push without its bounded maintenance gate and Matt authorization.
- Do not route active work to Social Architect Phase 1.
- Do not route active work to DAX or Trades unless Matt explicitly reactivates that lane.
- Do not seed non-MMI tasks into `tasks.json`.
- Do not treat old role docs as current if they conflict with this file.
- Do not drop PARKED concepts for sounding unrealistic — route to research or inventory.
- Do not invoke or spend on Gemini or Grok unless Matt explicitly reactivates the named model for a later bounded task.

## Current Queue Rule

No product task is active during maintenance. Repository state, backup custody, recovery proof, GitHub identity, data-location inventory, and governance correction are the only current lanes. Do not run queue-reload or task-runner scripts merely to manufacture product work.

## Local-First Policy

See `mmi/project_brain/architecture/MMI_LOCAL_CLOUD_POLICY.md`.

- **Local:** project brain, `tasks.json`, execution, command center
- **Cloud:** cold backup only (git-remote or encrypted sync) — not live runtime
- **NorthStar:** isolated — no bridge
- **Orchestrator scope:** `architecture/MMI_ORCHESTRATOR_SCOPE.md`

## Product Lanes (Matt-authorized)

| Lane | Status | Authority |
|------|--------|-----------|
| **MMI Security Intel** | Maintenance freeze (prior research preserved) | Matt maintenance directive 2026-07-13 |

See `lanes/MMI_SECURITY_INTEL_LANE.md` and `architecture/MMI_SECURITY_INTEL_PRODUCT_SCOPE.md`. Core queue/war room/backup **unchanged** — intel pipeline runs **after** `mmi-war-room-v1`. Endpoint swarm from research is **not** build scope.

## Mandatory Authority Laws - 2026-07-07

All agents must read and obey mmi/project_brain/status/MMI_BUILD_AND_PRESERVATION_AUTHORITY_LAWS_20260707.md before selecting a next lane, committing/pushing, proposing build work, running audits, or closing a session.

Key binding points:

- Evidence decides the next lane; Matt is not asked to choose when rubric evidence decides.
- Every next lane must name the primary model, secondary review model, execution operator, forbidden tools, and ownership reason.
- Daily backup, commit, push, and remote-head verification are preservation law, not optional hygiene.
- No build, execution, cleanup, delete, reset, force-push, kernel/minifilter/IOCTL testing, or restore-check script execution without explicit Matt authorization.
- Accepted artifacts must be committed and pushed, or explicitly listed as intentionally untracked/quarantine. No silent loose files.
