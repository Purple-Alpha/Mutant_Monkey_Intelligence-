# MMI Security Intel — MVP Architecture

Project: MMI  
Lane: Design  
Status: Draft — design spec, not runtime  
Repo root: `C:\MMI` / `/mnt/c/MMI`  
Deliverable path: `mmi/project_brain/architecture/MMI_SECURITY_INTEL_MVP_ARCHITECTURE.md`

## Purpose

MMI Security Intel helps an SMB-scale operator understand, prioritize, and recover from modern automated threats. v1 is research synthesis plus local operator playbooks, not enterprise SOC software and not endpoint defense. It turns threat research into scannable, ATT&CK-tagged briefs and actionable operator checklists that live local-first in the project brain. It informs the human; it never acts on a host.

## Core Doctrine

- Local-first: source of truth is local `tasks.json` plus `mmi/project_brain/`. Cloud is cold backup only through B2, git, or encrypted sync. No hosted DB, no live queue, no cloud runtime, no NorthStar bridge.
- Advisory only: Security Intel produces briefs, indexes, and checklists. It never blocks, contains, quarantines, or touches an endpoint. Detect and inform, not enact.
- Evidence-disciplined: every numeric or external claim is source-verified or stamped `NEEDS VERIFY`. No unverified stat is presented as fact or published.

## MVP Deliverables

1. Intel Brief Template — a repeatable structured doc for synthesizing one threat into operator-readable form, ATT&CK-tagged, with a source-status field.
2. ATT&CK Tagging Structure — SMB-scoped technique mapping embedded in each brief.
3. Research Index — links research lane docs to briefs to operator recommendations, so a recommendation is always traceable back to its source.
4. Operator OpSec Checklist — Mini PC hardening: MFA, phish discipline, backup cadence, restore drill. Actionable, state-tracked, local.
5. Optional Local Intel View — parked until after War Room v1; structure defined here, build deferred.

## Information Architecture

```text
mmi/project_brain/
├── lanes/
│   ├── RESEARCH_polymorphic_ransomware_delivery_2026-06.md
│   └── RESEARCH_smb_threat_landscape_2026-06.md
├── intel/
│   ├── briefs/
│   │   └── INTEL_<slug>_<yyyy-mm>.md
│   ├── INTEL_INDEX.md
│   └── templates/
│       └── INTEL_BRIEF_TEMPLATE.md
└── opsec/
    └── OPERATOR_OPSEC_CHECKLIST.md
```

Flow: research lane raw input to intel brief synthesis with ATT&CK tags, then index entry with traceable links, then operator recommendation or opsec action. One direction only. Briefs cite lanes; recommendations cite briefs; nothing is recommended without a traceable source.

## ATT&CK Template Structure

Each brief carries an ATT&CK block. SMB-scoped only: use techniques relevant to an SMB operator, not the full enterprise matrix.

| Field | Content |
|---|---|
| `technique_id` | Example: `T1566.002` |
| `technique_name` | Example: `Spearphishing Link` |
| `chain_stage` | Where in the chain: delivery, execution, C2, impact |
| `smb_relevance` | Why an SMB operator should care, one to two lines |
| `operator_signal` | What the operator might observe, mail-derived only |
| `mitigation_ref` | Link to the opsec checklist item that addresses it |
| `source_status` | `VERIFIED`, `NEEDS VERIFY`, or `RESEARCH-ONLY` |

Seed set from polymorphic ransomware research:

- `T1566.002` Spearphishing Link — delivery
- `T1204.001` User Execution: Malicious Link — execution
- `T1027` Obfuscated Files/Information — defense evasion
- `T1082` System Information Discovery — discovery, client profiling
- `T1071.001` Web Protocols — command and control over HTTPS
- `T1486` Data Encrypted for Impact — impact

Documented chain, research-only narrative:

```text
spearphish link
→ client profiling
→ sandbox-benign or human HTML smuggling
→ HTTPS C2
→ ransomware execution
```

Boundary: the chain is documented to inform defense and prioritize opsec. It is a threat description, never a build guide. The theoretical endpoint swarm referenced in research is `RESEARCH-ONLY` and is not authorized for MMI implementation.

## Operator OpSec Checklist Structure

A local, state-tracked checklist for the operator's Mini PC.

| Field | Content |
|---|---|
| `item_id` | `OPSEC-<n>` |
| `control` | Example: MFA on all admin and email accounts |
| `category` | `MFA`, `PHISH`, `BACKUP`, `RESTORE`, `DISCIPLINE` |
| `why` | Which ATT&CK techniques this blunts |
| `cadence` | `one-time`, `daily`, `weekly`, `monthly`, `quarterly` |
| `state` | `NOT_STARTED`, `IN_PROGRESS`, `DONE`, `OVERDUE` |
| `last_done` | Date |
| `verify_method` | How the operator confirms it is real, not assumed |

Seed categories from SMB landscape research:

- MFA — on email, admin, backup, and recovery accounts.
- PHISH discipline — link-hover, sender-auth awareness, out-of-band confirmation on payment or credential changes.
- BACKUP cadence — frequency plus offline or immutable copy.
- RESTORE drill — periodically prove a restore works.

The restore drill is the highest-value item: a backup nobody has restored is an assumption, not a control. State-track it like any other.

## Research Index Structure

`INTEL_INDEX.md` is the traceability spine.

| Field | Purpose |
|---|---|
| `brief_id` | Stable brief identifier |
| `threat` | Threat name |
| `source_lanes` | Research files used |
| `attack_ids` | ATT&CK IDs referenced |
| `recommendations` | Linked operator recommendations |
| `source_status` | Verification state |
| `updated` | Last update date |

Every recommendation in MMI Security Intel must resolve through this index back to a research lane. A recommendation with no traceable source is a defect, not a feature.

## Source Verification Rules

- Every numeric claim, including percentages, dollar figures, incident counts, and time-to-compromise claims, is `NEEDS VERIFY` unless tied to a named, dated, checkable source.
- `source_status` enum: `VERIFIED` for named source plus date, `NEEDS VERIFY` for retained but unverified claims, `RESEARCH-ONLY` for theoretical or internal material never presented as fact.
- `NEEDS VERIFY` claims may be used internally for prioritization but never published externally and never shown to a third party as fact.
- No stat leaves MMI as a factual claim while stamped `NEEDS VERIFY`. External-facing material uses `VERIFIED` only.
- When research and a verified source conflict, verified wins and the conflict is logged in the brief.

## Local-First Constraints

- Source of truth: local `tasks.json` plus `mmi/project_brain/`.
- Cloud equals cold backup only via B2, git, or encrypted sync.
- No hosted DB.
- No live cloud queue.
- No cloud runtime.
- No NorthStar bridge.
- No `npm`, `web/`, or `ops/run.py` unless Matt explicitly assigns it.
- Default surface is local files and operator specs, not a web app.

## Out Of Scope V1

- Endpoint agent swarm — not authorized for implementation. The research reference to a theoretical endpoint swarm is `RESEARCH-ONLY`. MMI Security Intel does not deploy, design, or build endpoint agents.
- Live telemetry, Sysmon, or EDR — no host instrumentation.
- Automated blocking or containment — MMI informs; the operator acts.
- External publication of unverified stats.
- Enterprise SOC tooling, SIEM, or hosted systems.
- Optional local intel view is deferred until after War Room v1; structure only, no build in this MVP.

## Codex Handoff

Design-ready but not authorized by this document alone. Each item requires Matt approval and a separate build task.

1. Scaffold the directory structure: `intel/`, `intel/briefs/`, `intel/templates/`, `opsec/`. File creation only, no logic.
2. Create `INTEL_BRIEF_TEMPLATE.md` as a fillable markdown template using the ATT&CK and source-status structures above.
3. Create `OPERATOR_OPSEC_CHECKLIST.md` seeded with the category/item structure and blank state fields.
4. Create `INTEL_INDEX.md` with the specified columns.
5. Deferred: local intel read-view after War Room v1, only if Matt assigns it.

Codex implements against this spec only. No runtime logic, no telemetry hooks, no endpoint work.

## What Still Needs Verification

- The six ATT&CK IDs are correct as IDs from the research context, but each technique name and SMB-relevance framing should be checked against the live ATT&CK matrix before external use.
- Every stat carried from the SMB landscape research is `NEEDS VERIFY` until sourced. None are source-verified in the provided context.
- The polymorphic chain is research narrative. Confirm it stays descriptive and never drifts toward instructional detail in any brief built from it.
- Whether the optional intel view reads from the same project-brain files or needs its own index is deferred with the view.

## Acceptance Criteria

- [ ] Intel Brief Template exists with ATT&CK block and `source_status` field.
- [ ] ATT&CK structure is SMB-scoped and each technique links to a mitigation item.
- [ ] Operator OpSec Checklist covers MFA, phish, backup cadence, and restore drill, each state-trackable with a `verify_method`.
- [ ] Research Index makes every recommendation traceable to a source lane.
- [ ] `NEEDS VERIFY` rules are stated and every unsourced numeric claim is flagged.
- [ ] Local-first constraints are explicit; no cloud, hosted, or NorthStar dependency.
- [ ] Out-of-scope names endpoint swarm explicitly as not authorized.
- [ ] Codex handoff lists implementable items, each gated on Matt approval and separate build auth.
- [ ] No runtime code in this deliverable.
