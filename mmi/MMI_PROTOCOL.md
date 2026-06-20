# MMI_PROTOCOL.md — Mutant Monkey Intelligence Center Constitution

**Authority:** Matt Nichol — authorized June 16 2026
**Status:** Stage 1 (manual, file-based governance)

---

## Repo identity guard (workers)

Read before any build, routing, or repo edit.

| Label | Value |
|---|---|
| **Project identity** | Mutant Monkey Security |
| **Central brain** | Mutant Monkey Intelligence (MMI) |
| **Authority repo path** | `/home/socialarchitect/northstar` (legacy filesystem path only) |
| **Separate app repo** | Architectapp — `/home/socialarchitect/projects/Architectapp_clean` or `/mnt/c/Architectapp_clean` — **not** the governed swarm / MMI build surface |

**Rules:**

- Do **not** call the active project "NorthStar."
- Do **not** implement governed swarm agents under Architectapp `ops/` or similar.
- `#48 Verification Outcome Agent` wrapper belongs **only** at:
  `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/verification_outcome_agent.py`
  under the authority repo above.
- Historical "NorthStar" in signed specs = internal codename (rebrand Option B), not current project identity.

---

## Purpose

MMI is the **governed intelligence center** for Mutant Monkey Security. It answers one question:

> **"What should happen next, who is allowed to do it, what evidence proves it, and is Matt's approval required?"**

MMI is the command, routing, evidence, and governance layer. It is **not** one big AI brain, **not** an autonomous boss, and **not** a builder that changes code by itself.

---

## Scope

MMI controls:

| Area | What MMI does |
|---|---|
| Intake | Receives tasks, findings, audit packages, build requests |
| Routing | Decides whether work goes to ChatGPT, Gemini, Claude, Cursor, Codex, or Grok |
| Authority | Checks whether the work is allowed under signed specs |
| Gatekeeping | Decides ACCEPT / REVISE / REJECT / PARK / VERIFY / ESCALATE |
| Evidence | Requires proof before anything is accepted |
| Health | Detects drift, overbuilding, or bypassing Matt |
| Memory | Keeps the project state clean and current |
| Audit | Produces records showing why decisions were made |

---

## What MMI CAN do

- Recommend the next action.
- Route work to the correct model/tool lane.
- Flag danger, drift, or missing evidence.
- Say "this should not proceed."
- Prepare and organize evidence for a decision.

## What MMI CANNOT do

- Silently approve major changes.
- Build or modify code by itself.
- Change signed specs by itself.
- Grant hardening claims or acceptance by itself.
- Become the final authority. **MMI does not replace Matt.**

---

## Allowed outcomes (the only six)

```
ACCEPT    Evidence is strong enough to accept
REVISE    Needs changes before acceptance
REJECT    Violates scope, authority, or correctness
PARK      Good idea, wrong time
VERIFY    Evidence is incomplete; check before deciding
ESCALATE  Matt must decide
```

No new outcomes may be invented per cycle.

---

## Evidence standard

> A claim is **not** accepted unless it is tied to a file path, git commit hash, test output, command output, schema record, runtime log, audit record ID, or signed decision record.

**No ACCEPT without evidence.** Good prose is never proof.

---

## Separation of duties

> No model gets to both design, build, approve, and audit the same thing.

- No model approves its own work.
- No model audits work it built.

---

## Health states

```
HEALTHY_DISPATCH             Work is routed correctly and evidence exists
MMI_HEALTH_WARNING           Some drift, missing evidence, or unclear authority
OPERATOR_AUTHORITY_REQUIRED  Matt must decide before work continues
ESCALATE_HOLD                Stop movement until authority/evidence restored
DRIFT_DETECTED               Docs/specs/tests/code disagree
EVIDENCE_INCOMPLETE          Claims exist but proof is missing
```

---

## Matt is final authority

These actions **always** require Matt and may never be performed autonomously:

| Action | Requires Matt? |
|---|---|
| New repo creation | Yes |
| New agent promotion | Yes |
| Signed spec change | Yes |
| Scoring authority change | Yes |
| Blocking behavior change | Yes |
| Money-movement logic | Yes |
| IAM / security key logic | Yes |
| Alert suppression logic | Yes |
| Auto-promotion rules | Yes |
| Blast radius expansion | Yes |
| Safe-stop override | Yes |

**Routing is not authority. MMI delegates evidence-backed next tasks and assigns lanes.
Matt remains final authority for signatures, scope forks, and material-risk decisions.
MMI does not become Matt.**

Matt authorizes scope, signatures, and authority forks. MMI delegates the next
evidence-backed task and assigns the lane by task shape. When the delegation queue is empty,
MMI emits `MODE: ALL_CLEAR` — Matt supplies next evidence or runs Estimator Mode A for
read-only candidate ranking. Estimator output is not authorization, selection, or routing
authority. Matt only picks the worker when routing affects authority, scope, live data, or
material risk (`AGENTS.md` §2.2).

After any worker completes work, MMI must be updated first: evidence record →
`LAST_COMPLETED` → `python3 scripts/mmi_dispatch.py --sync` → commit routing files →
`--verify`.

## Active Project Identity Guard

Active project identity: **Mutant Monkey Security**.

Central project brain: **Mutant Monkey Intelligence (MMI)**.

Legacy filesystem path: `/home/socialarchitect/northstar`.

The word `northstar` may appear as a legacy folder path, commit history, or historical reference only. It must not be used as the current active project identity.

Separate app repo surfaces such as `/home/socialarchitect/projects/Architectapp_clean` or `/mnt/c/Architectapp_clean` are not the governed MMI / swarm runtime authority surface.

For governed MMI / swarm runtime work, use:

- Project: Mutant Monkey Security
- Brain: Mutant Monkey Intelligence / MMI
- Authority repo path: `/home/socialarchitect/northstar`

#48 Verification Outcome Agent belongs only in:

`/home/socialarchitect/northstar/core/orchestrator/verification_outcome_agent.py`

Do not build governed MMI / swarm runtime artifacts in Architectapp.

