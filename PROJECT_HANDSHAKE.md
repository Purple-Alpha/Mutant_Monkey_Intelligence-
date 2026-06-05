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
**Real-customer-data controls spec is DRAFT pre-§11 with §10 resolved (2026-06-05, Matt Nichol "agree all").** The controls path is Option B: real customer packages audited by operator-controlled local AI on a locked machine; Grok/xAI stays synthetic/test only until sunset; Private Test-Data Store stays test/lab forever. The draft now proposes D1-D15, including the seven resolved local-AI blueprint answers: D9 calibration gate over fixed model, D10 locked-machine checklist, D11 Dax as default auditor only with a NorthStar package-audit brief and builder/auditor separation, D12 separate Production Evidence Store spec, D13 Stage-9-parity local audit output, D14 Grok/xAI synthetic sunset triggers, D15 buyer delivery separately gated. **§11 is still blank and operator-authored.** No infrastructure, no §13/IQ3 revision, no real-customer-data handling, and no buyer delivery begin until §11 sign-off plus a separate explicit start-build instruction. PDF render surface is COMPLETE and synthetic/internal-only; buyer-brand boundary revision is complete/re-signed with **Mutant Monkey Inbox Shield** on package surfaces. The Cyber Insurance generator has stages 8/9/10, criterion-14 signature evidence, and PDF renderer wired/proven for synthetic packages. Rebrand Option B remains in force: Mutant Monkey Security external brand; NorthStar/SwarmCommand internal codenames; deep rename deferred. Build loop canonical (AGENTS §3.2); STANDING in force.

## Commit Cadence (operator §4 decision, 2026-06-04; EXTENDED 2026-06-05)
**STANDING authorization in force, extended per operator instruction 2026-06-05.** Any gate-clean, fully-green slice is committed + logged automatically with no per-step prompt — this now covers in-scope code (`core/evidence_package/`) AND doc / log / spec-draft / matrix slices. Decisions chain (AGENTS §3.1.9, §3.2); the agent decides on ranked defaults and rolls forward. **Only these still stop and reach Matt, never auto-proceeding:** pushes to remote; §11/§13 sign-offs; scope / pricing / legal-trademark / external-identity changes; butterfly path-setting decisions; the seven VISION non-negotiables; and any change to the substance of a signed spec's locked decisions. Pushes are never inferred.

## Git State
Branch `safety/queue-drift-cleanup-20260528`. Operator pushed GitHub successfully through `f1fb901` (`ec270a5..f1fb901`), restoring off-site backup for the buyer-brand, Gemini, controls-decision, and controls-draft commits. Push through the agent remains credential-blocked, so future GitHub pushes are still explicit operator terminal steps. Local `backup` remote (`/mnt/c/northstar_backups/northstar.git`) is durable through `f9ae055`. GitHub is currently ahead-needed by two local commits: `7440c6e` and `f9ae055`. STANDING governs gate-clean local commits; pushes remain explicit.

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
2026-06-05 - Updated after real-customer-data controls §10 resolution: GitHub pushed through `f1fb901`;
controls draft now has D1-D15 proposed and §10 resolved; §11 remains blank / operator-authored.
