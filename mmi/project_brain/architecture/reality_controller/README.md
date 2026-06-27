# Swarm Command Reality Controller

**Status:** `RESEARCH_DESIGN` — not build authority  
**Merged from:** `C:\Unified Folder Structure NorthStar + SwarmCommand Venture\project-brainarchitecturereality-controller` (2026-06-26)  
**Related:** `purple_translation_layer.md`, MMI-DEC-223/226/227, `#43 Geo-Context`, `#70 Final Review`

---

## What this is

Research doctrine for a **lab-only deception and adversarial-resilience stack**. These
modules describe how an isolated decoy environment *could* frustrate attacker
reconnaissance and harvest forensic intelligence — not how production MMI should
behave today.

This folder is **not** a second project brain. Operator queue truth remains
`mmi/project_brain/status/` and `python3 scripts/mmi_pm_voice.py`.

---

## Module index

| Module | File | Role |
|--------|------|------|
| Beacon Injector | `beacon_injector.md` | Artifact telemetry / attribution (lab decoys) |
| Geo-Fence Manager | `geo_fence_manager.md` | **Reality Anchor (CORE TIER)** — entrapment by validation, synthetic telemetry |
| Network Mutator | `network_mutator.md` | Moving-target defense topology |
| Tarpit Orchestrator | `tarpit_orchestrator.md` | Session prolongation / resource exhaustion |
| Trap / Hack / Rot Bots | `trap_hack_rot_bots.md` | Active engagement — highest liability |

---

## Hard boundaries (all modules)

- **No build** without signed contract + Matt authorization + legal/safety review
- **No production dispatch** or customer-facing deployment
- **No autonomous exploitation**, counter-attack, or internet scanning
- **Lab / owned infrastructure only** unless separately authorized
- **No AUTH-5** — human authority for any outward or destructive action
- Integrations that reference `project-brain` mean **MMI project brain** (facts in,
  operator decisions out) — not autonomous enactment

---

## Relationship to Purple Translation Layer

Defensive-first path remains: **Blue evidence → normalized facts → Purple gap
analysis → human review**.

Reality-controller modules are **parked high-liability research**. They may inform
future `#43` geo-context design and adversarial harness concepts, but do not
override BREADTH/DEPTH build sequencing or signed agent contracts.

---

## When this branch becomes actionable

1. Separate legal/safety contract for deception / active engagement
2. Lab environment definition + blast-chamber controls
3. Matt explicit authorization — distinct from §11 agent contracts
4. First buildable slice likely mirrors **Adversarial Resilience Harness**
   (synthetic fixtures, governance drift) — not live tarpits or beacon injection

---

## Doctrine stack (v2 — 2026-06-27)

**Anchor module:** `geo_fence_manager.md` (`RESEARCH_DESIGN — CORE TIER`, Lane 4 PARK)

```
Ingress metadata -> geo-fence-manager (Reality Anchor)
    -> project brain: Reality Anchor + Entrapment Score
    -> network-mutator: maintain regional persona (Session Continuity)
    -> [optional, gated] trap_hack_rot_bots: Hack-Bot on Reality Mismatch
```

**#43 separation:** Production geo-context research lives in
`geo_context_43_research_lanes.md` (Lanes 1–2 only). Do not import Lane 4 deception
into #43 ES1 contracts.

**Governance:** Doctrine changes require Founder review + MMI-DEC record. Never automate
Reality Controller evolution.
