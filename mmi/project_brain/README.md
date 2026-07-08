# MMI Project Brain

This folder holds local operating context for MMI only.

Use it to keep mission, architecture, lane ownership, decisions, runbooks, and status notes grounded in Matt's current directives. Do not copy NorthStar or other project content into MMI unless Matt explicitly authorizes it.

## Folders

- `mission/`: MMI purpose, active objectives, and scope boundaries.
- `architecture/`: System shape, components, data flow, and technical constraints.
- `lanes/`: Ownership rules for Cursor, Codex, Claude, Gemini, Gemini Paid API, and ChatGPT.
- `status/`: Current queue state, task reports, and active operating notes.
- `decisions/`: Approved decisions and dated rationale.
- `runbooks/`: Repeatable commands and operating procedures.

## Mandatory Authority Laws - 2026-07-07

All agents must read and obey mmi/project_brain/status/MMI_BUILD_AND_PRESERVATION_AUTHORITY_LAWS_20260707.md before selecting a next lane, committing/pushing, proposing build work, running audits, or closing a session.

Key binding points:

- Evidence decides the next lane; Matt is not asked to choose when rubric evidence decides.
- Every next lane must name the primary model, secondary review model, execution operator, forbidden tools, and ownership reason.
- Daily backup, commit, push, and remote-head verification are preservation law, not optional hygiene.
- No build, execution, cleanup, delete, reset, force-push, kernel/minifilter/IOCTL testing, or restore-check script execution without explicit Matt authorization.
- Accepted artifacts must be committed and pushed, or explicitly listed as intentionally untracked/quarantine. No silent loose files.
