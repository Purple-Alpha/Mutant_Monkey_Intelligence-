# Cursor Agent Handoff

**Updated:** 2026-06-26  
**Authority:** Session handoff for worker agents. Does not authorize build, promotion, or production dispatch. Live queue truth: `python3 scripts/mmi_pm_voice.py` + `python3 scripts/mmi_dispatch.py --verify`.

---

## Identity

| Field | Value |
|-------|-------|
| **Project** | Mutant Monkey Security (not "NorthStar" in operator prose) |
| **Authority repo** | `/home/socialarchitect/northstar` (WSL — primary; use this for all work) |
| **Branch** | `safety/queue-drift-cleanup-20260528` |
| **HEAD at handoff** | `0b78503` — `MMI-DEC-233/234: Build VPV workflow ES1 and #19 DualApprovalAgent` |
| **Windows venture path** | Secondary/reference only — do not treat as authority |

---

## Operator console (run first every session)

```bash
cd /home/socialarchitect/northstar
python3 scripts/mmi_pm_voice.py
python3 scripts/mmi_dispatch.py --verify
```

**Expected at handoff:**

```text
MMI_OPERATOR_CONSOLE
status: ACTION
task: Run completion gate for Dual-Approval
for: completion gate auditor (complete_gate.py)
score: n/a

MODE: AUDIT
```

---

## What Matt authorized

Matt said **`go`** → explicit **build authorization** (MMI-DEC-233).

Prior context:
- §11 signed VPV Workflow + #19 Dual-Approval contracts (MMI-DEC-231/232)
- Pre-build gates clean (MMI-DEC-229/230)
- Goal sheets: `mmi/project_brain/mission/short_term_goals.md`, `long_term_goals.md`
- Reality-controller research merged to `mmi/project_brain/architecture/reality_controller/` (research only)
- BUILD-route `TASK_SCORE: 100` when `SIGNED_UNBUILT` drives dispatcher row

---

## Built (MMI-DEC-234) — complete

| Component | Path |
|-----------|------|
| VPV workflow ES1 (Tier A) | `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/workflows/vendor_payment_verification.py` |
| #19 DualApprovalAgent | `3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation/core/orchestrator/dual_approval_agent.py` |
| Tests (21 pass) | `.../tests/test_vendor_payment_verification.py`, `test_dual_approval_agent.py` |

```bash
cd "/home/socialarchitect/northstar/3. SwarmCommand_Engine/Agent_Loop_Runtime/Runtime_Implementation"
.venv/bin/python -m pytest tests/test_vendor_payment_verification.py tests/test_dual_approval_agent.py -q
```

**Boundaries:** not in `build_default_registry`; no production dispatch; no payment actions; no AUTH-5.

---

## Scoreboard

**#19 Dual-Approval** → `AWAITING_AUDIT` (`agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md`)

---

## Next job (immediate)

**Lane: AUDIT** — completion gate 0 blocking, then GATED reconcile.

1. Stage gate manifest if needed: `audit_outputs/pending/dual_approval.manifest.json`
2. Run completion gate:

```bash
cd /home/socialarchitect/northstar
python3 audit_tools/complete_gate.py --pre-commit \
  --task dual_approval \
  --claim "#19 Dual-Approval + VPV upstream build implemented + tested; ready for audit"
```

3. On 0 blocking: scoreboard `#19` `AWAITING_AUDIT` → `GATED`; append MMI-DEC; update `MMI_CURRENT_STATE.md`
4. `python3 scripts/mmi_dispatch.py --sync` + `--verify` + commit routing files

See also: `mmi/project_brain/status/active_task.md`

---

## Signed contracts

| Contract | DEC |
|----------|-----|
| `4. Product_Roadmap/Vendor_Payment_Verification_Workflow_Design_Contract_Deep_Dive.md` | MMI-DEC-231 |
| `4. Product_Roadmap/Dual_Approval_Agent_Design_Contract_Deep_Dive.md` | MMI-DEC-232 |

---

## Queue after depth lane (MMI-DEC-241)

MMI-DEC-222 **complete**: #19 GOVERNED_AGENT · #66 RECLASSIFY · #70 surfaces mapped · #43 held.

BREADTH: 41/70 `GOVERNED_AGENT`. #10/#21 GATED — promotion reviews separate.

Next optional lanes: #70 Slice B contract draft (`NEEDS_SIGNED_CONTRACT`), #43 research, #21 promotion.

---

## Environment

- Work in WSL at `/home/socialarchitect/northstar`
- PowerShell breaks heredocs — use `wsl git -C /path commit -m "..."`
- `complete_gate.py` packet cap 200KB — trim `files_read` in manifests if needed
- Do not build in Architectapp repos

---

## DEC sequence (relevant)

221–234. Latest: MMI-DEC-233 (build auth), MMI-DEC-234 (VPV + #19 built).

---

## One-line mission

**Run completion gate 0/0 on #19 Dual-Approval, reconcile to GATED, sync routing, verify PASS.**
