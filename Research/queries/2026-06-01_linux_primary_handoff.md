# 2026-06-01 — Linux Primary Handoff (updated 19:19 PT)

**Captured:** 2026-06-01 ~19:19 PT (Pacific) by Cursor at operator request. Supersedes the earlier 19:16 PT version of this same file.
**Status:** Operator-authored handoff block. Pre-spec context only. Not §11. Not §13. Not D10. No `complete_gate.py` run required for this file (it is a handoff note, not a spec).
**Purpose:** Durable on-disk copy of the operator's updated paste-and-go state block for the Linux primary repo, so the next chat or future agent picks up clean.
**Authorship boundary:** Block below is operator-authored and preserved verbatim. The header above is AI-drafted under operator instruction.

---

## Verbatim handoff block (operator-authored, 2026-06-01 19:19 PT)

```text
Use Linux primary only from here:
  /home/socialarchitect/northstar

Cursor is currently in the Windows mirror, so do not keep writing there as primary.

Current Linux state:
- Linux already has the earlier cyber-insurance research/synthesis/record-set work.
- Linux already has the v1 runner package:
  Research/v1_test_plan_runners/stage_a_vendor_payment_redirect_001/
- Runner files match Windows by SHA256, so do not replay/overwrite that folder.

Windows-only work that still needs to be replayed into Linux:
- 4. Product_Roadmap/Research_Inputs/Testing_Score_Sheet_Schema.md
- 4. Product_Roadmap/Research_Inputs/Testing_Plan_V1.md
- Research/queries/2026-06-01_linux_primary_handoff.md
- Research/queries/2026-06-01_testing_scoring_correction_evidence_brief.md
- Research/queries/2026-06-01_testing_scoring_correction_evidence_research.md
- Relevant tracker updates from Windows:
  MASTER_INDEX.md
  PROJECT_ACTIVITY_LOG.md
  PROGRESS.md

Do not copy Windows AGENTS.md or PROJECT_HANDSHAKE.md; those appear to be line-ending/status noise, not real content changes.

Do not stage or commit yet. After replaying the Windows-only testing docs/query notes into Linux, inspect the diff, write a worker manifest, and run complete_gate.py before making any done/commit claim.

Known noise:
- Windows has empty untracked file: Are
- Linux has odd untracked command-output files:
  moke first
  moke looks right, the live run (one grok-4 call)
Inspect before deleting, but do not commit them.

D10 is still not complete.
No §13 sign-off.
No implementation authorized.
This remains pre-spec research/testing-shape work.
```

---

**End of handoff record. No gate required.**
