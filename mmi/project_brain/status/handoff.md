# Cursor Agent Handoff

**Updated:** 2026-06-27
**Authority:** Session handoff for worker agents. Does not authorize build, promotion, or production dispatch. Live queue truth: `python3 scripts/mmi_pm_voice.py` + `python3 scripts/mmi_dispatch.py --verify`.

**Team model:** Single Builder on hot worktree (`/home/socialarchitect/northstar`). Cold DriftWatcher worktree parked unless Matt explicitly delegates.

---

## Identity

| Field | Value |
|-------|-------|
| **Project** | Mutant Monkey Security (not "NorthStar" in operator prose) |
| **Authority repo** | `/home/socialarchitect/northstar` (WSL — hot tree) |
| **Branch** | `safety/queue-drift-cleanup-20260528` |
| **HEAD at handoff** | `83710f2`+ (post #22 GOVERNED_AGENT MMI-DEC-267) |
| **Windows venture path** | Secondary/reference only — do not treat as authority |

---

## Operator console (run first every session — hot tree)

```bash
cd /home/socialarchitect/northstar
python3 scripts/mmi_pm_voice.py
python3 scripts/mmi_dispatch.py --verify
```

**Expected at handoff:** `MODE: ALL_CLEAR` — BREADTH runway **46/70 GOVERNED_AGENT**; BOR v40 Blackboard-Mesh pre-build gate PASS (MMI-DEC-270); awaiting Matt §11.

---

## Hot lane — #22 Payroll Diversion (`GOVERNED_AGENT` — MMI-DEC-267)

| Item | Detail |
|------|--------|
| **Build** | `PayrollDiversionAgent` (`payroll_diversion_001`) + contract §3 detector — `83710f2` |
| **Gate** | `audit_outputs/payroll_diversion_20260627T182904Z.md` (0 blocking / 2 warnings) |
| **Scope** | ES1 email-only detect-not-enact; mission_context routes `payroll_diversion_detection`; SemanticFilter DER hardening |
| **Not authorized** | `build_default_registry`, production dispatch, AUTH-5, DEPTH (#84–#94) while gate CLOSED |

---

## Next operator actions

1. **Blackboard-Mesh** — Matt §11 sign contract (pre-build gate PASS MMI-DEC-270); then build auth for Mode A ledger gate.
2. Iterative Crucible / Phoenix: synthetic harness only until Evidence Backer v1 exists.
3. DEPTH stack (#84–#94) held until BS-D3 gate opens.
4. BREADTH runway 46/70; no agent build without separate unpark.
