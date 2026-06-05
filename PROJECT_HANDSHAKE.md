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
**Private Test-Data Store spec is §11 SIGNED (2026-06-05, Matt Nichol)** — all seven §10 questions resolved to D9-D15; Q3 mesh = **self-hosted WireGuard** (Option B, full sovereignty; operator overrode an initial Tailscale lean). Signing locks the design contract only; standing up infrastructure still needs a separate explicit operator start-build instruction. Next live action is operator's call (next milestone). Larger gated track: real-customer-data controls decision (best run once Codex finishes consolidating the agent folder). PDF render surface is COMPLETE: IQ2 engine pinned to ReportLab 4.2.5 (pure-Python; smallest cross-platform supply-chain surface, the dimension IQ2 flagged), internal/synthetic-only deterministic renderer built (separate explicit step, not auto-wired, no buyer delivery), gate clean, 1128 green. Buyer-facing package boundary revision is also complete/re-signed: **Mutant Monkey Inbox Shield** is now the product name printed in the §2 package boundary statement; "NorthStar Inbox Shield" stays internal codename. The Cyber Insurance generator now has stages 8 (audit-packet assembly), 9 (Grok package audit — explicit, injectable, synthetic-only), 10 (done-declaration), the criterion-14 signature evidence mechanism, and the PDF renderer wired/proven. Remaining before a real package can be "done" or shipped: a separate real-customer-data controls/redaction decision (required before ANY non-synthetic Grok submission OR buyer render — v1 is synthetic/test only), buyer PDF delivery (gated, explicit operator decision), and Matt's actual package-level signature for a concrete package. Operator intent logged 2026-06-04: real customer packages should move toward NorthStar's own AI on a locked operator-controlled machine; Grok remains for synthetic/test audits only while tokens remain and while the operator considers it safe. This is not yet a §13/IQ3 revision. Rebrand decided (Option B): "Mutant Monkey Security" external/commercial brand + domain now; NorthStar/SwarmCommand stay internal codenames; trademark clearance in parallel; deep rename deferred to first signed MSP pilot OR trademark-clearance result. Build loop canonical (AGENTS §3.2); STANDING in force.

## Commit Cadence (operator §4 decision, 2026-06-04; EXTENDED 2026-06-05)
**STANDING authorization in force, extended per operator instruction 2026-06-05.** Any gate-clean, fully-green slice is committed + logged automatically with no per-step prompt — this now covers in-scope code (`core/evidence_package/`) AND doc / log / spec-draft / matrix slices. Decisions chain (AGENTS §3.1.9, §3.2); the agent decides on ranked defaults and rolls forward. **Only these still stop and reach Matt, never auto-proceeding:** pushes to remote; §11/§13 sign-offs; scope / pricing / legal-trademark / external-identity changes; butterfly path-setting decisions; the seven VISION non-negotiables; and any change to the substance of a signed spec's locked decisions. Pushes are never inferred.

## Git State
Branch `safety/queue-drift-cleanup-20260528`. GitHub current at `16f75ef`; push through the agent is credential-blocked (`could not read Username for https://github.com`), so the off-site GitHub push remains an explicit operator terminal step. Local `backup` remote (`/mnt/c/northstar_backups/northstar.git`) is durable through `815431d`. Local-only commits ahead of GitHub: `07d297c` (buyer-brand boundary §13 re-signature), `7a028dc` (tracker), `815431d` (Gemini briefing), plus this session's real-customer-data controls slice. Earlier today: `a65babf` criterion-14 operator-signature mechanism, `d75c3e7` done-declaration, `0aea29a` cycle-2 log, `729a964` rebrand matrix, `7cf4361` test-data store spec, `f59f54c` day-arc trackers, `264a340` stage-9 auditor, `7d4b3c1` milestone-E closeout, `ab9846a` integration test, `0e9002d` Cycle-3 tracker refresh. STANDING governs auto-commits in the code home; pushes remain explicit.

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
2026-06-05 - Updated after Cyber Insurance buyer-brand boundary revision: §2 package boundary now
prints Mutant Monkey Inbox Shield, Matt re-signed the §13 revision, gate clean, 1128 green. Next live
action remains operator's milestone call; remote push still requires explicit operator instruction.
