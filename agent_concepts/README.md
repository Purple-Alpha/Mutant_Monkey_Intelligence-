# agent_concepts/

**Status:** Idea / theory staging area. Pre-spec, unsigned, NOT §11, authority-free. Created 2026-06-05 on Matt Nichol's instruction.

**Purpose:** A place for Matt to dump agent/swarm design theories and "what I want to build" ideas before they are committed to anything. This folder is the **operator's design backlog** — raw concepts and adopted maps that daily milestones get drawn from.

## Rules for this folder

1. **Nothing here builds, authorizes, or scopes anything.** Files here do not override `AGENTS.md`, the seven `VISION.md` non-negotiables, or any signed spec. If a concept here ever conflicts with those, they win.
2. **Concepts are not promotions.** A design here becomes real only by going through the normal path: Next-Action Decision Rubric (pick it as a milestone) -> spec-first deep-dive in `4. Product_Roadmap/` -> `complete_gate.py` -> operator sign-off.
3. **Brand:** buyer-facing surfaces use **Mutant Monkey**; "NorthStar" / "SwarmCommand" stay internal codenames per the rebrand Option B decision.
4. **Index new artifacts.** Add a `MASTER_INDEX.md` entry for anything substantive dropped here, same as anywhere else in the project.
5. **Two states per file:** RAW (a dump, not yet reviewed) or ADOPTED (operator has accepted it as a map/backlog source). Adoption still is not build authorization.

## Contents

- `_Blue_Team_Swarm_Architecture_Map_SPARK.md` — **ADOPTED 2026-06-05; superseded as canonical design source on 2026-06-06.** The original 70-agent / ten-team blue-team swarm architecture (Stage B/C articulation of `VISION.md`). Preserved as the inventory/backlog cross-map: each agent is mapped against current runtime + signed/drafted specs, with butterfly/boundary flags and the operator vision verbatim. It remains useful as the raw inventory; `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` is now the canonical design articulation and milestone-shaping source.
- `Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` — **ADOPTED CANONICAL DESIGN MAP 2026-06-06.** Supersedes the v1 70-agent map as the canonical agent-design articulation and milestone-shaping source, while the v1 map remains preserved as the original inventory/backlog cross-map. Adds the 6-layer governed swarm fit (Command, Detection, Verification, Evidence, Challenge/Red-Team, Learning/Governance), Rules of Engagement, six agent authority levels, an agent reputation system, a two-pass (detect -> challenge) decision model, a client-safe decision evidence record, conflict resolution, and a concrete V1 starting swarm. Authority-free; builds nothing; agent names/slogans are internal design labels, not approved buyer claims.
