============================================================
MUTANT MONKEY TESTING LAB RECORD
============================================================
Artifact: Project Drift Detector (scripts/detect_drift.py)
Type: Build
Date: 2026-06-14
Operator: Matt Nichol
Repo/Branch: northstar @ safety/queue-drift-cleanup-20260528
Related Files:
  - scripts/detect_drift.py
  - 4. Product_Roadmap/Project_Drift_Detector_Concept_Doc.md (spec)
  - 4. Product_Roadmap/Mutant_Monkey_Testing_Lab_Protocol.md (this protocol)

This is the FIRST lab specimen — the lab tests its own first automated detector,
proving the protocol works before any machinery is trusted.

LAB SUMMARY
Product Truth:        PASS
Threat Intelligence:  WARN
Evidence Quality:     PASS
Governance Safety:    PASS
Build Readiness:      WARN
Cutting Edge:         PASS

------------------------------------------------------------
BENCH NOTES
------------------------------------------------------------
Bench 1 — Product Truth: PASS
  Strengthens dispatcher integrity and prevents signed-contract routing drift —
  the exact failure class (#88/#89/#92/#99) that has derailed governed dispatch.
  Tied to swarm governance, which is a core Mutant Monkey product layer.

Bench 2 — Threat Intelligence: PASS_WITH_WARNINGS
  Catches governance drift (signed-no-row, phantom evidence, dirty routing files)
  that normal CI does not. WARNING: it validates evidence PRESENCE, not evidence
  QUALITY — a parallel session that edits both the scoreboard and an audit file
  consistently could still satisfy D3. The detector reduces silent drift; it does
  not prove an audit was real.

Bench 3 — Evidence Quality: PASS
  Produces a human-readable BLOCK/WARN/INFO report stating the exact source
  disagreement (which contract, which row, which missing path/hash). Reversible
  and reviewable; uses no guarantee language; exit code is defined.

Bench 4 — Governance Safety: PASS
  Read-only. HR-1 enforced (no edit/commit/stash/move/track/promote/repair).
  HR-2 enforced in code: PROMOTED_CHECKS is empty, so every finding is advisory
  and the detector exits 0 — it cannot hard-stop the dispatcher. No
  auditor-of-the-auditor recursion: it reports, it does not rule.

Bench 5 — Build Readiness: PASS_WITH_WARNINGS
  Spec precise, files named, exit codes defined, stdlib-only, runs clean in WSL
  (1.6s). WARNING (predicted by the spec's own Build Readiness note): D2 matches
  contract FILENAMES against the scoreboard, but the board references most
  historical contracts by AGENT NAME, so D2 currently over-reports gated
  historical contracts. Alias resolution is required before D2 is promotable.

Bench 6 — Cutting Edge: PASS
  Detects governance drift between signed contracts, scoreboard claims, and
  dispatcher inputs — a failure class ordinary CI / security tooling does not
  cover. This is governance-routing integrity, specific to a signed-contract swarm.

------------------------------------------------------------
FINDINGS (from live run, 2026-06-14)
------------------------------------------------------------
[BLOCK]  none — no check is promoted (HR-2); detector exits 0.

[WARN]   D2 over-reports: 11 signed contracts flagged "no row", but most are
         GATED agents referenced by agent name not filename (Blast_Radius_Controller,
         Phase4_ReconciliationAgent, Phase5_MutationEngine, Watcher_Agents,
         Load/Specialisation_Fission_v2, Dual_LLM, Phase3 amendment,
         Shadow_Watcher_Swarm). These are false positives pending the alias map.
[WARN]   D2 genuine-signal candidates worth operator eyes:
           - Safe_Stop_Adversarial_Test_Suite_Contract.md (signed, no row — may be
             real parallel-workflow drift)
           - Threat_Intelligence_Daemon_Design_Contract.md (intentionally external
             to Northstar; expected to have no row — confirm and exempt)
[WARN]   D5 state file MODE 'REVIEW PENDING' != dispatcher MODE 'BUILD' — expected:
         Runtime Instrumentation is awaiting Matt's review while the dispatcher
         routes the next build. Visible, not fatal.
[WARN]   D1 6 untracked routing-input docs in 4. Product_Roadmap/ (parallel-session
         normal; includes the two artifacts created in this build).

[INFO]   D3 29 GATED rows checked — ALL cited audit evidence + commit hashes
         present and resolvable. Proof chain clean.
[INFO]   D4 no tracked files modified.
[INFO]   D6 no duplicate row ids in the control-plane governance table.

------------------------------------------------------------
REQUIRED RETESTS
------------------------------------------------------------
- RT-1: Add a contract->agent alias map to D2, re-run, confirm gated historical
  contracts drop out, leaving only genuine signed-but-unrowed drift.
- RT-2: Operator triage of the 6 untracked roadmap docs (track / delete / ignore);
  re-run D1.
- RT-3: Confirm Threat_Intelligence_Daemon_Design_Contract.md is intentionally
  external and add a documented D2 exemption; investigate
  Safe_Stop_Adversarial_Test_Suite_Contract.md for a missing scoreboard row.
- RT-4: Do NOT promote any check from BLOCK-candidate to BLOCK until RT-1 lands and
  D2 is clean; promotion is a recorded operator act (HR-2).

------------------------------------------------------------
FINAL LAB VERDICT
------------------------------------------------------------
ACCEPT

Reason: The detector is sound, read-only, advisory, and already surfaced real,
actionable signal (clean proof chain on 29 gated rows; one expected state mismatch;
candidate parallel-workflow drift). Build it, keep it advisory, and resolve RT-1
before considering any promotion. The lab protocol itself is validated by this run:
it found a genuine limitation (D2 alias matching) and logged it as a retest rather
than silently passing the tool.
