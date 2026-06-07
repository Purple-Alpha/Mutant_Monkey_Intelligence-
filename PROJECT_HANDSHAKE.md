# Project Handshake
NorthStar + SwarmCommand Venture

## Purpose
The "start here before doing work" file. Read it after `AGENTS.md` and `VISION.md`.
It tells a new session, in one screen: where we are now, the single next action, the
verification baseline, and what is uncommitted.

**HYGIENE RULE (added 2026-06-03 to stop new-chat drift):** keep this file SHORT and CURRENT.
"Current State" and "Current Next Step" are **REPLACED each session, never appended**. Superseded
detail moves to `PROJECT_HANDSHAKE_ARCHIVE_*.md`. If this file grows past ~one screen, rotate it.
The old append-style handshake (235 lines of stale "next step" bullets) is what caused new-chat
drift; do not recreate it.

## Current Active Build Track
Email fraud + inbox-layer MDR for SMBs via MSPs (Stage A). NorthStar Inbox Shield +
SwarmCommand Agent Loop Runtime + Fraud / Ransomware specialization.

## Current Development Surface
WSL2 Ubuntu at `/home/socialarchitect/northstar` (primary since 2026-06-01). The Windows path is
backup / reference only. If the two ever diverge, stop and reconcile by commit hash before editing.

## Verification Baseline
**1128 tests passing, 1 skipped** (verified 2026-06-05, after the buyer-brand boundary revision slice) from
`3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation`.

## Current State (2026-06-03)
- **Environment (2026-06-06): git freeze cleared; Linux-native committed.** The git "freeze" (no-exit-status commands forcing manual relays) is dead — verified by running git directly in the Linux terminal. The Windows copy is now **cold-backup-only; editing it is abandoned.** Linux (`/home/socialarchitect/northstar`) is the sole development surface. The freeze is logged as environment friction (not a lane-structure failure) and is excluded from the 2026-06-09 lane-trial review. See `PROJECT_ACTIVITY_LOG.md` and `CURRENT_STATE_MAP.md` Development-surface entry.
- **Cyber Insurance Evidence Package deep-dive: §13 SIGNED** (Matt; operating entity name TBD, project rename parked) and **§13 buyer-brand boundary revision RE-SIGNED 2026-06-05** with Matt-authored wording: "Approved by Matt Nichol, Sovereign Operator." D1-D11 locked. **D10 is OVERRIDDEN, not met** — signed operator override; basis is ad-hoc confirmation signal, not validated market proof. The §2 required boundary statement now names **Mutant Monkey Inbox Shield** on buyer-facing package surfaces; "NorthStar Inbox Shield" remains the internal codename per rebrand Option B.
- **Cyber Insurance Evidence Package IMPLEMENTATION spec: §11 SIGNED 2026-06-03** by Matt Nichol (Zebra-Comit), authored in-chat and committed (`4308b22`). Build-layer §3-§16 locked (IQ1-IQ7 + §13 pins: Grok-4 / temp 0 / dedicated PDF toolchain / `vf-001`+legit pair). Signed-spec slice Grok audit is **clean: 0 blocking / 0 warnings** (`audit_outputs/cyber_insurance_section11_spec_signature_slice_20260603_20260604T001901Z.md`). Signing did not authorize code beyond the later operator-selected runner-first milestone.
- **§14 test-plan runner-first milestone: EXECUTED / PASS** (live `grok-4`, 2026-06-04T00:49Z). Evidence under `audit_outputs/cyber_insurance_v1_test_plan/stage_a_vendor_payment_redirect_001/`; `run_summary.md` and `verdict.json` show all seven §14.4 conditions passed, all nine §7 gates passed, and zero drift incidents. This is internal test evidence only, not buyer-facing output or D10 market proof.
- **Cyber Insurance gate library + generator Pass 1: COMMITTED** (Markdown-first, internal only). Gate library `db32cd5` (fresh Grok gate clean); generator + CLI `ff0f41e` via `complete_gate.py --operator-override` (the §11-signed implementation spec is a no-code document; Matt explicitly authorized generator Pass-1 start-build, internal scope, 2026-06-04 — recorded in `PROJECT_ACTIVITY_LOG.md`; warning-level drift incident logged). `core/evidence_package/` gate/generator surface + `scripts/cyber_insurance_package_generate.py` produce a deterministic Markdown bundle under `audit_outputs/cyber_insurance_packages/` from the §14 artifacts. Focused tests: **16 passed**; live CLI all nine gates passed. No PDF, no Grok package audit, no package done declaration, no buyer-facing release.
- **Wave 3.1 score-sheet review ledger helper:** implemented, Grok-clean, committed (`audit_tools/review_ledger.py` + scanner + hook + tests).
- **Doc rotation done (2026-06-03):** `PROJECT_ACTIVITY_LOG.md`, `PROGRESS.md`, `MASTER_INDEX.md`, and this handshake were trimmed to active heads with verbatim archives, to fit the audit-gate packet cap (200KB / 50KB per file).
- **AGENTS.md §3.1 Decision Presentation Rule added:** decisions arrive pre-scored (ranking, why, consequence, recommended default) routed through the existing rubric engines; no bare unscored menus.
- **Project rename away from "NorthStar": PARKED.** Collisions found (Zebra, Axion, cyan AG, etc.); no name chosen; needs a real USPTO + registrar clearance pass.

- **Cyber Insurance implementation spec §18 amendment: SIGNED 2026-06-04** (Matt, Zebra-Comit; committed `3aec44b`; pre+post-signature gate audits clean). Declares `core/evidence_package/` the authorized generator code home; in-scope generator code now commits clean through the gate with **no `--operator-override` and no per-commit signature**. Operator signature is required only for §18.4 architectural changes (locked decisions, boundary, scope, external claims). The independent Grok audit stays in force.

- **Next-Action Decision Rubric: §11 SIGNED 2026-06-04** (Matt, Zebra-Comet). All 7 §10 questions locked as D13–D19; gate audit clean (grok-4, 0 blocking / 0 warnings, `audit_outputs/next_action_decision_rubric_signoff_20260604T062334Z.md`). `decision_cycles_log.md` created (D15). The rubric is now the live tactical decision engine: it ranks candidates on 5 axes; Matt selects; cycles log to `decision_cycles_log.md`.
- **AGENTS.md decision-calibration guardrail added 2026-06-04:** §3.1.2 now grades escalation by substance + reversibility (not "touches a signed file"); §3.1.8 + §12 "trivia-escalation / decision-inversion" failure mode added. Fixes the inversion of heavy-guardrailing trivia (e.g. an internal name change) while dumping real decisions raw.

## Current Next Step (single live action)
**Multi-model lane structure is on a 3-day TRIAL (opened 2026-06-06, review 2026-06-09).** Execution vs advisory lanes + the git-step rule + handoff routing (AGENTS.md §2.1 / §2.1.1) are being evaluated, not locked. Log lane incidents inline in `PROJECT_ACTIVITY_LOG.md` (stale-step incidents, relays per decision, gate rejections from lane confusion, advisory catch rate, friction notes). Review question on 2026-06-09: did lane discipline reduce stale errors more than it added relay cost? War room substrate stays parked until that review produces evidence. No code/build authorized.


**Agent Design Contract Template §11 SIGNED + BANKED (2026-06-06)** by Matt Nichol ("Matt Nichol June 6th 2026", placed verbatim). Spec: `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md`. Turns the adopted 6-layer agentic evidence swarm into a required template for future promoted agents. §10.A locks defaults: enforce before §10 resolution; immediate metadata-only #10/#21 retrofit after sign-off; Stage A detectors default Level 3 Specialist; seven-field decision evidence record; promotion/demotion spec-only in v1; pure detectors may declare Pass 1 only until the Two-Pass spec signs; v2 design tree canonical / v1 map inventory-only. **Operator-directed hardening folded into the signed text:** §7.0 immutability boundary — the signed detector contract is immutable; a retrofit adds governance fields to a wrapper only and is NOT permission to touch detection logic; and Q7 settles the v1 map as inventory-only (not a competing design source, not to be relitigated). Gate clean 0/0 (`audit_outputs/Agent Design Contract Template §11 sign-off_20260606T220951Z.md`); committed as signed-spec slice `d5decc0`, followed by AGENTS/tracker/lane handoff slices through `be6d8df`. Pushed to GitHub + backup. No implementation, runtime enforcement, retrofits, or new agent behavior are authorized.

**Production Evidence Store §11 SIGNED + BANKED (2026-06-05).** §10.A locks all five questions (Q1 same host / isolated MinIO instance; Q2 per-tenant credentials day one; Q3 indefinite-until-explicit-delete for evidence-bearing classes; Q4 operator off-site media only; Q5 read-only-from-locked-machine + egress-deny v1). Committed in four gate-clean slices and pushed to GitHub + backup through `4145dc2`. Locks the contract only — no infrastructure, no real-customer-data handling, until a separate explicit start-build instruction.

**Session opening 2026-06-06:** set today's milestone list, then pick one. Recommended next: **Local-AI audit substrate planning (spec-only)** — advances the real-customer-data path (Dax/NorthStar local auditor per controls D6/D11) with no infrastructure and no real data. Alternatives: promote another swarm-map agent build slice; draft the Mutant Monkey package-auditor D9 calibration plan; §13/IQ3 revision prep. Todd/MSP parked until Tuesday.

**Real-customer-data controls remain signed but not operationally started:** controls spec §11 signed (`e77f85c`), D11 package-audit brief authored (`6026deb`), Lookalike Domain Detector build slice banked (`13f3cb1`/`0ceb582`). No real-customer-data handling, §13/IQ3 revision, local-AI substrate, production evidence store infrastructure, or buyer delivery starts without separate operator authorization. Todd/MSP motion parked until Tuesday by operator instruction.

## Commit Cadence (operator §4 decision, 2026-06-04; EXTENDED 2026-06-05)
**STANDING authorization in force, extended per operator instruction 2026-06-05.** Any gate-clean, fully-green slice is committed + logged automatically with no per-step prompt — this now covers in-scope code (`core/evidence_package/`) AND doc / log / spec-draft / matrix slices. Decisions chain (AGENTS §3.1.9, §3.2); the agent decides on ranked defaults and rolls forward. **Only these still stop and reach Matt, never auto-proceeding:** pushes to remote; §11/§13 sign-offs; scope / pricing / legal-trademark / external-identity changes; butterfly path-setting decisions; the seven VISION non-negotiables; and any change to the substance of a signed spec's locked decisions. Pushes are never inferred.

## Git State
Branch `safety/queue-drift-cleanup-20260528`. Working tree clean. **Local HEAD is `e9d9d95` ("Refresh handshake for be6d8df banked state"), which is `[ahead 1]` of `github` (at `be6d8df`)** — `e9d9d95` is an unpushed local commit; this is normal local-first state, not drift. Local backup (`/mnt/c/northstar_backups/northstar.git`, remote `backup`) likewise trails HEAD by the same commit. The **git "freeze" is cleared** (verified 2026-06-06: `git status -sb` and `git log --oneline -3` run directly in the Linux terminal returned clean, exit code 0, no hang, no relay). Pushes remain explicit operator actions; use the Linux integrated terminal for authenticated GitHub pushes. STANDING governs gate-clean local commits; pushes remain explicit. Run `git status -sb` to confirm the live state at session start.

**Commit discipline (learned 2026-06-05 from an avoidable mess):** ALWAYS run `complete_gate.py` (or `--pre-commit` with only the intended slice staged) and see "clean" BEFORE `git commit` — never commit first and gate after. NEVER `git reset` past the last pushed commit (`git log --oneline -5` shows the `github/`+`backup/` ref; do not soft-reset below it). If a packet is `too_large` (200KB cap), split into smaller staged slices and gate each — do not commit the oversized packet anyway.

## Decision Routing (trial, 2026-06-05)
`DECISION_PROTOCOL.md` is in TRIAL (committed `6a83bfc`, not yet adopted into AGENTS.md authority). The agent operates under it now: Bin 1 (technical/reversible) = agent decides silently, never asks; Bin 2 (operator-authority/irreversible/money/identity/legal/real-data/buyer-delivery/butterfly/non-negotiable) = always reaches Matt with each option's positives, negatives, consequence, recommendation, and why-on-demand. Every session opens by setting a daily milestone list; every decision traces to it. The agent challenges any instruction (including Matt's) that collides with signed specs / the seven non-negotiables / forbidden language / butterfly triggers, before building. On any conflict AGENTS.md wins until Matt formally adopts the protocol.

## Required Files to Check Before Work
Follow the `AGENTS.md` §1 session-start read order first. Core governance files:
`MASTER_INDEX.md`, `PROJECT_HANDSHAKE.md`, `PROJECT_GUARDRAILS.md`, `PROJECT_ACTIVITY_LOG.md`,
`CURRENT_STATE_MAP.md`, `PROGRESS.md`, `PROJECT_BUILD_AND_AUDIT_QUEUE.md`.
(The exhaustive per-file checklist was archived 2026-06-03 to `PROJECT_HANDSHAKE_ARCHIVE_2026-06-03.md`;
use `MASTER_INDEX.md` as the live map of all artifacts.)

## Required Files to Update After Work
- `PROJECT_ACTIVITY_LOG.md` (new entry)
- `PROJECT_HANDSHAKE.md` — **replace** Current State + Current Next Step (do not append)
- `MASTER_INDEX.md` if a new major artifact is added

## Resume Rule
"Where do we keep going from?" -> read this file's **Current State** + **Current Next Step**,
then the latest `PROJECT_ACTIVITY_LOG.md` entry. That is the resume point.

## Current Owner
Matt

## Last Updated
2026-06-06 - Git freeze cleared (verified by direct Linux terminal `git status -sb` + `git log --oneline -3`,
clean / exit 0). Linux-native commitment recorded; Windows copy demoted to cold-backup-only (editing abandoned).
Freeze logged as environment friction, excluded from the 2026-06-09 lane-trial review. Git State corrected to
show local `e9d9d95` `[ahead 1]` of `github`/`backup` (`be6d8df`); prior "both remotes resolve to be6d8df" text was stale.

2026-06-06 - 3-day lane-structure trial opened and banked through `be6d8df`: execution vs advisory
lanes, git-step rule, 4-phase Design -> Logic -> Audit -> Execute pipeline, away rule, and war-room
substrate parked. Trial review date: 2026-06-09. GitHub + backup both resolve to `be6d8df`.

2026-06-06 - Partner-lanes (model-strengths) contract added to `AGENTS.md` §2.1: Matt decides /
Grok audits / Codex builds / Claude designs+governs, each with strengths, guardrails, and lane, plus
shared cross-lane rules. Banked and pushed as part of the `be6d8df` remote-aligned state.

2026-06-06 - Agent Design Contract Template §11 SIGNED + BANKED by Matt Nichol at
`4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (with operator-directed §7.0 detector-contract
immutability boundary + Q7 v1-map-inventory-only confirmation folded into the signed text). Canonical design
adoption banked through `01e12ee`; signed-spec and tracker/lane slices banked through `be6d8df`. No code,
runtime enforcement, retrofits, or new agent behavior authorized.
