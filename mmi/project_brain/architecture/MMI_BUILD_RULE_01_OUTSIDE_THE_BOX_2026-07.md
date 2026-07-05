# MMI Build Rule #1 — Outside the Box

**Status:** ACTIVE DOCTRINE — ALL BUILDS  
**Authority:** Matt (Super)  
**Date filed:** 2026-07-01  
**Priority:** **Rule #1** — supersedes generic defaults, sandbox conservatism, and "that's not how people usually do it."

---

## The rule (Matt, verbatim intent)

**If it's generic — we think different.**

**If it's no — we ask why and how come.**

**If it's possible — we want to make it possible.**

**Absolutely no working inside the box. We are to always be thinking outside the box.**

---

## What this means in practice

| Situation | Wrong response | Rule #1 response |
|-----------|----------------|------------------|
| Solution looks like every other security product | Ship the generic version | Rethink until it is distinctly MMI |
| Someone says "that won't work" / "can't be done" | Accept and substitute a safe alternative | Ask **why** and **how come** — then engineer around the wall |
| Idea is hard, unproven, or "fantasy" | Kill it by default | Treat as **design pressure** — make it possible if it serves the weapon concept |
| Agent defaults to enterprise/SOC patterns | Compliance-tool path | Weapon path — controlled chaos, inflation, mirror, tarpit, evolution |
| Tradeoff is "easier to build" vs "what Matt asked for" | Build easier | Build what was asked; document cost, don't swap the concept |

---

## Hard stops (unchanged — not "inside the box," these are Matt's boundaries)

Rule #1 does **not** mean:

* Hack-back or attacking systems Matt does not own
* Mutating the live authority repo during max chaos
* Auto-promoting archives or auto-patching from hostile logs without Matt sign-off
* Pretending generic ops plumbing (Track B gates) **is** the lung / weapon (Track A)

Outside the box **within** Matt's stated hard boundaries in `MMI_CONTROLLED_CHAOS_DEFENSIVE_WEAPON_CONCEPT_2026-07.md` §2–4.

---

## Agent / lane obligation

Any lane (Cursor PM, Codex, Claude, research) that encounters a blocker must output:

1. **Why** — stated reason for no  
2. **How come** — assumptions behind the no  
3. **Make-possible path** — what would need to exist for yes (even if v0 is ugly)  
4. **Generic trap check** — is the proposed fallback generic? If yes, think different.

**Forbidden:** Silent substitution — replacing Matt's architecture with a generic equivalent and using the same names.

---

## Related doctrine

| File | Relationship |
|------|----------------|
| `architecture/MMI_CONTROLLED_CHAOS_DEFENSIVE_WEAPON_CONCEPT_2026-07.md` | North star product |
| `chaos/MMI_DESTRUCTIVE_EVOLUTION_MATRIX_2026-07.md` | How we smash until perfect |
| `architecture/MMI_ORCHESTRATOR_SCOPE.md` Addendum 04 | Air-Lock — make inflation possible without spawn |
| `architecture/MMI_WEAPON_RUNTIME_BLOCKERS_2026-07.md` | Walls to engineer through, not reasons to quit |

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-01 | Matt Build Rule #1 filed |
