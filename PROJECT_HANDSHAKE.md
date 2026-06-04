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
**1072 tests passing, 1 skipped** (verified 2026-06-03) from
`3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation`.

## Current State (2026-06-03)
- **Cyber Insurance Evidence Package deep-dive: §13 SIGNED** (Matt; operating entity name TBD, project rename parked). D1-D11 locked. **D10 is OVERRIDDEN, not met** — signed operator override; basis is ad-hoc confirmation signal, not validated market proof.
- **Cyber Insurance Evidence Package IMPLEMENTATION spec: §11 SIGNED 2026-06-03** by Matt Nichol (Zebra-Comit), authored in-chat. Build-layer §3-§16 locked (IQ1-IQ7 + §13 pins: Grok-4 / temp 0 / dedicated PDF toolchain / `vf-001`+legit pair). Signed-spec slice Grok audit is **clean: 0 blocking / 0 warnings** (`audit_outputs/cyber_insurance_section11_spec_signature_slice_20260603_20260604T001901Z.md`). Signature is staged from the audit slice, **uncommitted**. Signing ≠ code authorization. No code yet.
- **Wave 3.1 score-sheet review ledger helper:** implemented, Grok-clean, committed (`audit_tools/review_ledger.py` + scanner + hook + tests).
- **Doc rotation done (2026-06-03):** `PROJECT_ACTIVITY_LOG.md`, `PROGRESS.md`, `MASTER_INDEX.md`, and this handshake were trimmed to active heads with verbatim archives, to fit the audit-gate packet cap (200KB / 50KB per file).
- **AGENTS.md §3.1 Decision Presentation Rule added:** decisions arrive pre-scored (ranking, why, consequence, recommended default) routed through the existing rubric engines; no bare unscored menus.
- **Project rename away from "NorthStar": PARKED.** Collisions found (Zebra, Axion, cyan AG, etc.); no name chosen; needs a real USPTO + registrar clearance pass.

## Current Next Step (single live action)
**Commit authorization is the next operator-authority decision.** The implementation spec §11 is now
operator-signed (2026-06-03, in-chat) and the signed-spec audit slice is Grok-clean (0 blocking / 0
warnings). The §13 sign-off (`85f2069`) and Wave 3.1 (`24a1498`) are ALREADY committed; the only
uncommitted work is exactly three files: the implementation spec (with the §11 signature) plus this
handshake and `PROJECT_ACTIVITY_LOG.md`. AFTER a separate explicit operator start-build instruction:
build the **§14 test-plan runner first** (IQ7), discharging Done Criterion 15. The §14 v1 test plan
has not yet been executed.

## Git State
Branch `safety/queue-drift-cleanup-20260528`, **7 commits ahead of `github`, NOT pushed** (count
verified via `git status` 2026-06-03; pushing is an explicit operator instruction, never inferred).
The §11 sign-off + tracker edits above are working-tree changes not yet committed.

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
2026-06-03 - Rotated to crisp resume-here form to stop new-chat drift; full prior handshake
preserved verbatim in `PROJECT_HANDSHAKE_ARCHIVE_2026-06-03.md`.
