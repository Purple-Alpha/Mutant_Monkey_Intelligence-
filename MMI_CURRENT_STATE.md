# MMI Current State

**Read this at the start of every session instead of asking what to do.**

This file is derived ONLY from committed files (git history + tracked docs). It invents nothing from chat memory. Every claim cites its committed source. If a field below disagrees with a committed source, the committed source wins and this file is stale — refresh it (see "How to refresh").

- **As of HEAD:** `e44a377` (2026-06-13, `docs: index Mutant Monkey architecture directive`)
- **Branch:** `safety/queue-drift-cleanup-20260528`
- **Primary remote:** `github/safety/queue-drift-cleanup-20260528` (per `CURRENT_STATE_MAP.md` lines 13-27)
- **Repo authority:** `/home/socialarchitect/northstar` is the PRIMARY CODEBASE; Windows surface is secondary/reference only (`CURRENT_STATE_MAP.md` lines 13-27)

---

## 1. Current mode

**DESIGN / DOC-ONLY. Build is PAUSED pending operator authorization.**

Derivation:
- The newest committed operator-facing direction is the `PROJECT_HANDSHAKE.md` "CURRENT NEXT ACTION" block: the next work is a "clarification/amendment pass on existing signed artifacts," and explicitly "No code, no build, no Phase execution until the operator authorizes a specific §11-signed scope."
- The last five commits (`git log`, 2026-06-13: `37431e3`, `383ab79`, `31741e8`, `3924a36`, `e44a377`) are all doc-only (authority record, handshake refresh, MMI routing doctrine, architecture directive, index). No build commit since 2026-06-12.

---

## 2. Current authorized task

**No build task is currently authorized. The most recent doc pass is complete and committed.**

Derivation:
- Completed + committed (2026-06-13): WSL primary-authority record, handshake refresh + matrix naming, MMI Worker Routing Doctrine (`AGENTS.md` §2.2), Mutant Monkey Architecture Directive (`agent_concepts/Mutant_Monkey_Architecture_Directive.md`) + its index entry.
- `PROJECT_HANDSHAKE.md` "IF BLOCKED" reads: "Not blocked — tree is clean and pushed. Awaiting operator direction on the clarification/amendment pass."
- **Next candidate build when work resumes (NOT yet authorized):** Shadow Watcher Swarm **Layer 2 — Alarm Layer**, per the newest committed decision-cycle entry (`decision_cycles_log.md` lines 50-78, "SHADOW WATCHER SWARM LAYER 1 CLOSURE", NEXT: "Next guided build when work resumes is Shadow Watcher Swarm Layer 2 — Alarm Layer"). This requires operator authorization before any code (see §5).

---

## 3. Current phase and gate status

**Last gated build: Shadow Watcher Swarm Layer 1 — GATED, clean. Working tree clean and pushed.**

Derivation (`decision_cycles_log.md` lines 50-78; `git log`):
- **Phase / layer:** Shadow Watcher Swarm — Layer 1 Watch Layer.
- **Contract:** `4. Product_Roadmap/Shadow_Watcher_Swarm_Contract.md`, §11 SIGNED 2026-06-12 (Matt Nichol, `5320ba0`), Layer 1 block authorized.
- **Built:** `core/shadow_watchers/` package — 6 Q-class observe-only agents (Sender/Payment/Language/Attachment/Geo/VendorHistory), append-only `ShadowObservationLog`.
- **Gate:** 0/0 clean (`audit_outputs/shadow_watcher_layer1_20260613T052829Z.md`); commit `03cd7d2`.
- **Test baseline (authoritative, newest committed):** full runtime suite **1740 passed / 1 skipped / 49 xfailed** (`decision_cycles_log.md` line 71).
- Other June-12 gated milestones in history (`git log`): Dual LLM pattern (`696ee45`), Watcher Agents #85-87 (`6da6284`), Load Fission #90 (`190002f`), Specialisation Fission #91 (`c7ef023`), Blast Radius Controller #89 (`f1c817e`).
- **Gates closed:** DEPTH gate CLOSED (Stage 2+ blocked until real-data intake) and STAGE_B gate CLOSED (autonomy blocked until signed Stage B auth), per `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` lines 24-26.

---

## 4. What is blocked

- **Shadow Watcher Layer 2 (Alarm Layer):** not started; blocked on operator authorization / §11 layer sign-off before any build (`decision_cycles_log.md` lines 50-78).
- **#48 Verification Outcome Agent:** boundary contract DRAFTED + gated clean + committed (`8e2b787`), "BLOCKED ON §11 SIGNATURE" per `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` line 22. NOTE: this header is dated CYCLE 25 / 2026-06-09 and predates the 2026-06-12 work — treat as possibly superseded until the scoreboard is reconciled (see §7).
- **Stage 2+ promotions (DEPTH):** blocked until real-data intake opens (Production Evidence Store infra + controls activation + separate operator authorization).
- **Stage B autonomy agents (e.g. #38 Containment):** blocked until a signed Stage B authorization.

---

## 5. What requires Matt sign-off

Per `AGENTS.md` §4 (No proxy decisions) and §2.1.1.B (operator sign-off scope):

- §11 / §13 signatures on any spec or contract (including Shadow Watcher Layer 2 and the #48 Verification Outcome contract).
- New Build Authorization or scope expansion (Evidence Stage 2/3 promotion, default-registry/production dispatch, anything enabling autonomous action, anything touching a signed spec's substance or the seven `VISION.md` non-negotiables).
- Pushes to remote (always an explicit operator step; never inferred).
- Destructive / irreversible git actions.
- Scope, pricing, legal/trademark/external-identity, business-direction, and butterfly path-setting decisions.

---

## 6. Who owns what right now

Per `AGENTS.md` §2.2 (MMI Worker Routing Doctrine) and §2.1 (partner lanes):

- **Matt — sole authority.** Current ball: decide the next move (authorize a build, authorize a doc/tracker reconciliation, or set direction). Nothing proceeds to build without this.
- **Cursor (execution lane) — repo builder/editor.** Owns live repo edits, multi-file changes, git, and tracker reconciliation. Holds the only live repo/terminal visibility.
- **Codex — reviewer / command planner / adversarial checker.** Owns verification of claims, diff review, second opinions. No repo-truth claim without pasted output.
- **Claude — architecture critic / long-form / doctrine-spec reviewer.** Owns design, governance, spec review, overengineering checks.

Routing rule: MMI routes by task shape and escalates to Matt only on authority/risk/live-data/scope forks. Routing is not authority.

---

## 7. Source-of-truth drift warning (derived from committed files)

The committed trackers currently DISAGREE with each other and with git history. This is the live risk this file exists to surface. Until reconciled, trust the newest committed source and git history over the older trackers:

- **Scoreboard header is stale.** `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` lines 14-28 are dated CYCLE 25 / 2026-06-09 and name next = "#48 Verification Outcome." This predates the 2026-06-12 gated wave (Shadow Watcher Layer 1, Dual LLM, Watchers #85-87, Fission #90/#91, Blast Radius #89) visible in `git log`.
- **Test baseline conflicts across committed files:** `PROJECT_HANDSHAKE.md` line 119 says `1447`; its milestone list (line 146) says `1247`; `decision_cycles_log.md` line 71 (newest) says `1740`. Authoritative = **1740** (newest committed, 2026-06-12).
- **Scoreboard internal count conflict:** "13 governed agents" (header, line 20) vs "12" (tally, line 266).
- **Handshake live block** is labeled "as of `37431e3`" and does not yet mention the later doc commits (`383ab79`..`e44a377`).

No deterministic verifier exists yet to catch this automatically (`audit_tools/complete_gate.py` checks changed-file audit coverage only; `scripts/health_check.py` trusts the docs). Reconciling the scoreboard/handshake against code+git is the obvious next doc-only task (Cursor lane) if the operator chooses it.

---

## How to refresh this file

This file is hand-derived and will go stale. To refresh, re-derive each field from committed sources only:

1. `git log -8 --date=short --pretty=format:'%h %ad %s'` — newest commits + dates (mode, last build).
2. Top entry of `decision_cycles_log.md` (newest closure/cycle) — authorized task, next build, test baseline, gate status.
3. `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` header — blockers/gates (check its date against `git log` for staleness).
4. `PROJECT_HANDSHAKE.md` "CURRENT NEXT ACTION" block — operator-facing direction.
5. `CURRENT_STATE_MAP.md` lines 13-27 — repo/remote authority.
6. `AGENTS.md` §2.1 / §2.2 / §4 — ownership and sign-off rules.

Update the "As of HEAD" line and re-flag any new tracker disagreements in §7.
