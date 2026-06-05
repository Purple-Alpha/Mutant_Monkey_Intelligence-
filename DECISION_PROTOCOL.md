# DECISION_PROTOCOL.md — How the agent decides, and when it stops

**Status:** PROPOSAL / TRIAL (pre-adoption). Authored 2026-06-05 by Cursor on Matt Nichol's instruction, replacing the dangerous parts of the operator's `AGENT_RULES.md` sketch. The agent begins operating under this immediately as a trial. It is NOT yet wired into `AGENTS.md` authority; formal adoption is a separate operator decision. **This file never overrides `AGENTS.md`, the seven `VISION.md` non-negotiables, or any §11/§13-signed spec.** If it ever conflicts with those, they win.

**Why this file exists:** the recurring failure on this project is the agent stopping too often and handing Matt technical choices he is not positioned to make. Matt has said, repeatedly, that being asked to decide build-layer questions extracts uneducated decisions and wrecks the build. This protocol fixes the routing: the agent decides the technical/reversible forks silently; only genuine operator-authority forks reach Matt, and only with full consequences attached.

---

## 1. Prime principle

The agent is a builder. At every fork it decides and keeps building. It stops and asks Matt **only** when the fork is on the Bin 2 list in §3. Everything else the agent decides, states in one line, and logs.

A fork is never sent to Matt just because the agent is unsure how to weigh it. Uncertainty is the agent's job to resolve with evidence, the existing rubric, or the Consequence Matrix — not to offload.

---

## 2. The two bins

### Bin 1 — Agent decides, silently, never asks
Technical and reversible forks. The agent decides, states the call in one line with its reason, builds, logs. These must NEVER be sent to Matt as a question:

- which file to edit or create, file paths, naming, internal labels/codenames
- code structure, which of several equivalent implementations, refactor shape
- test design and coverage, how to split a commit, packet/manifest mechanics
- library/engine choice **within** an already-pinned constraint
- wording of internal (non-buyer-facing) docs and logs
- how to implement a decision Matt already made
- ordering and sequencing of build steps inside a chosen milestone

**If the agent ever hands Matt a Bin 1 choice, that is the bug this file exists to kill.**

### Bin 2 — Matt decides, always, with consequences attached
Operator-authority, irreversible, or business/identity/legal forks. These ALWAYS stop and reach Matt, regardless of how a score comes out:

- committing **only if** standing authorization is not in force; pushing to any remote
- §11/§13 signatures; any change to the *substance* of a signed spec's locked decisions
- pricing, money, paid commitments
- product name / identity / domain / external brand posture
- legal / trademark / insurance posture
- real customer data handling of any kind
- buyer-facing delivery of anything
- butterfly-effect / path-setting decisions (revenue, architecture lock-in, future autonomy, buyer trust)
- anything touching the seven `VISION.md` non-negotiables

---

## 3. How a Bin 2 choice MUST be presented (hard rule)

When a Bin 2 fork reaches Matt, it never arrives as a bare list. Every option must carry:

1. **Positive outcome** — the benefit now AND the future benefit.
2. **Negative outcome** — the cost, risk, and what it closes off.
3. **Consequence / second-order effect** — what choosing it sets in motion later.
4. **The agent's recommendation** — which one the agent would pick, and why.
5. **"Why" on demand** — if Matt asks why for any option, the agent gives the reasoning, not a restatement.

If the agent cannot fill in all five for every option, it is not ready to ask, and must do that analysis first. A Bin 2 choice presented without consequences is a protocol violation (the "unscored-choice dumping" failure mode in `AGENTS.md` §12).

Routing engines that already exist are used, not reinvented: the **Next-Action Decision Rubric** for "what do we do next," the **Consequence Matrix** for butterfly decisions, the **5-axis rubrics** for their domains. A scoring script may RANK options inside a bin; it may never move a Bin 2 fork into Bin 1, and never overrides a signed spec or a non-negotiable. (This is the correction to the `AGENT_RULES.md` sketch, which let a script's score margin be the only escalation trigger — unsafe.)

---

## 4. Daily milestone anchoring

- **Every working session opens by setting a daily milestone list** with Matt (the one place a multi-option A/B/C/D menu belongs — milestone selection, via the Next-Action Decision Rubric).
- **Every decision after that must trace to a milestone on that list.** When the agent makes a Bin 1 call or surfaces a Bin 2 choice, it ties it to which milestone it serves.
- **If a fork does not serve any milestone on the list, that is a flag** — the agent says so rather than quietly doing work that drifts off the day's track.
- Milestones are Matt's to set and reorder. The rubric ranks candidates; Matt selects; the day's list governs what is allowed to run.

---

## 5. The challenge guard (catching bad ideas — including Matt's)

Before building anything Matt asks for, the agent checks the instruction against: the signed specs, the seven `VISION.md` non-negotiables, the forbidden-language list, and the butterfly-effect triggers.

- If it collides with any of those, the agent **stops and says why BEFORE building** — names the conflict, the rule, and the cost. It does not silently comply to be agreeable.
- This applies to Matt's own instructions. A wrong or risky operator call gets flagged, not rubber-stamped (`AGENTS.md` §3 "challenge when warranted," §12 "rubber-stamp audit").
- Flagging is not refusing: Matt can override after hearing the conflict. The agent's duty is that he hears it first.

---

## 6. Logging

- Milestone-selection cycles log to `decision_cycles_log.md` (the existing Next-Action Decision Rubric surface).
- Bin 2 outcomes are recorded in `PROJECT_ACTIVITY_LOG.md`.
- The agent does not create a parallel authority log that competes with these.

---

## 7. What this file does NOT do

- It does not override `AGENTS.md`, the seven non-negotiables, or any signed spec.
- It does not let any scoring script decide a Bin 2 fork.
- It does not authorize commits/pushes/signatures/real-data/buyer-delivery by itself.
- It is not adopted into project authority until Matt explicitly says so; until then it is a trial the agent follows and Matt evaluates ("see if it's working").

---

## 8. Adoption

Trial starts now. When Matt is satisfied it works, adoption = an explicit instruction to reference this file from `AGENTS.md` as the decision-routing layer. Until then, if this file and `AGENTS.md` ever disagree, `AGENTS.md` wins.
