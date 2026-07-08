# MMI Path Authority

Date: 2026-06-30  
Authority: Matt (Super)  
Status: **LOCKED** — all agents must read this before repo file lookups

---

## The only MMI repo root

| Environment | Path |
|-------------|------|
| **Windows** | `C:\MMI` |
| **WSL** | `/mnt/c/MMI` |
| **Windows (UNC)** | `\\wsl.localhost\Ubuntu\mnt\c\MMI` |

---

## NOT MMI (do not read design from these)

| Wrong path | What it is |
|------------|------------|
| `/home/socialarchitect/northstar` | Social Architect / NorthStar — **different project** |
| `3. Mutant_Monkey_Intelligence_Engine\...` | **Not the repo** — product nickname only; not a filesystem root |
| `\\wsl.localhost\Ubuntu\home\socialarchitect\northstar` | NorthStar — wrong |

**"Mutant Monkey"** is legacy branding in one doc header — it is **not** a folder you open. MMI code and project brain live under **`MMI/mmi/`**.

---

## Verified paths (exist on disk 2026-06-30)

```
mmi/project_brain/intel/WAR_ROOM_SCORING_MATRIX.md
mmi/project_brain/lanes/MMI_RESEARCH_RIGOR_PROTOCOL.md
mmi/project_brain/architecture/MMI_WAR_ROOM_SPEC.md
mmi/project_brain/architecture/MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md
mmi/war_room.py
mmi/command_center.py
```

---

## If MCP / Claude cannot see files

1. Open **`C:\MMI`** as the connected workspace folder in Cursor/Claude — not Mutant Monkey, not NorthStar.
2. Or: Matt pastes file contents into the chat — PM lane provides paste blocks.
3. Do **not** invent alternate directory trees.

---

## Agent rule

If `mmi/project_brain/` is not found at repo root → **STOP** and report wrong workspace — do not design from memory or guesses.

## Mandatory Authority Laws - 2026-07-07

All agents must read and obey mmi/project_brain/status/MMI_BUILD_AND_PRESERVATION_AUTHORITY_LAWS_20260707.md before selecting a next lane, committing/pushing, proposing build work, running audits, or closing a session.

Key binding points:

- Evidence decides the next lane; Matt is not asked to choose when rubric evidence decides.
- Every next lane must name the primary model, secondary review model, execution operator, forbidden tools, and ownership reason.
- Daily backup, commit, push, and remote-head verification are preservation law, not optional hygiene.
- No build, execution, cleanup, delete, reset, force-push, kernel/minifilter/IOCTL testing, or restore-check script execution without explicit Matt authorization.
- Accepted artifacts must be committed and pushed, or explicitly listed as intentionally untracked/quarantine. No silent loose files.
