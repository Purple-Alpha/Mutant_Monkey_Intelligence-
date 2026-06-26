# Short-Term Goals

**Horizon:** ~30–90 days (through end of Q3 2026)  
**Last updated:** 2026-06-25  
**Authority:** Human direction sheet. Does not authorize build, promotion, or production dispatch. For live queue truth use `python3 scripts/mmi_pm_voice.py` and `python3 scripts/mmi_dispatch.py --verify`.

---

## One-Line Focus

**Finish the #19 depth lane (VPV upstream → Dual-Approval wrapper) under signed contracts and clean gates, while keeping the operator control plane honest.**

---

## Active Milestone

`M1_CONTROL_PLANE_RESTORED` — mostly done; console restored. Remaining M1 hygiene is listed under Goal 5.

---

## Goals (in order)

### 1. Matt authorizes the build lane

**What:** Explicit operator authorization to implement VPV workflow ES1, then #19 DualApprovalAgent wrapper.

**Why:** Both contracts are §11 signed (MMI-DEC-231/232) and pre-build gates are clean (MMI-DEC-229/230). §11 ≠ build authorization.

**Done when:**
- Matt names the build target(s) in a decision record or direct instruction
- `active_task.md` lane moves from `BUILD_AUTH` to `BUILD`

---

### 2. Build VPV Workflow (upstream)

**What:** `core/workflows/vendor_payment_verification.py` per signed VPV Workflow Design Contract.

**Scope:** Tier A (baseline-free) checks first; emits `vpv_evidence_packet_v1` with `risk_verdict` CLEAR / ELEVATED / HIGH. Detect-and-report only.

**Path:** Cursor draft plan → Codex pre-build → Cursor implement → focused tests → completion gate 0 blocking.

**Done when:**
- Wrapper exists with focused synthetic tests
- Completion gate 0 blocking / warnings documented
- Scoreboard reflects `AWAITING_AUDIT` or `GATED` per reconcile rules

**Not in scope:** VPV Ergonomics sibling (Stage 2 disposition) — still DRAFT; open §10 Q1–Q6.

---

### 3. Build #19 Dual-Approval wrapper

**What:** `core/orchestrator/dual_approval_agent.py` per signed #19 contract.

**Depends on:** VPV workflow emitting `vpv_evidence_packet_v1` (schema lock from contract §3).

**Rules:** Layer 3 Verification; detect-not-enact; never an approver; consumes VPV packet; no AUTH-5.

**Done when:**
- Wrapper + tests pass
- Completion gate 0 blocking
- Scoreboard #19 advances from `SIGNED_UNBUILT` toward `GATED`

---

### 4. Execute Matt's depth queue (#66, #70) — **COMPLETE (MMI-DEC-241)**

**What:** MMI-DEC-222 selected order executed:

| Order | Agent | Outcome |
|-------|-------|---------|
| 1 | #19 Dual-Approval | GOVERNED_AGENT (MMI-DEC-238) |
| 2 | #66 Drift Watch | RECLASSIFY (MMI-DEC-236) |
| 3 | #70 Final Review | Surfaces mapped (MMI-DEC-240) |
| hold | #43 Geo-Context | Research only |

**Done when:** Each item has a clear contract or triage outcome recorded — **met**.

---

### 5. Control-plane hygiene (M1 tail)

**What:** Small fixes so the brain stays trustworthy.

| Item | Done when |
|------|-----------|
| `next_target_evidence.md` matches live scoreboard | #19 shows as `SIGNED_UNBUILT`, not stale `0 SIGNED_UNBUILT` |
| Console shows lane + milestone (optional) | `pm_voice` prints `lane:` / `milestone:` when data is stable |
| Drift test for weak recommendations | Test fails if `1/10` task surfaces while `8/10` milestone task exists |

---

### 6. Optional breadth promotions (only if Matt authorizes)

**What:** Promotion review for already-GATED rows — not the main depth lane.

| Agent | Status | Note |
|-------|--------|------|
| #10 Lookalike Domain | GATED MMI-DEC-215 | GOVERNED_AGENT promotion when authorized |
| #21 Executive Impersonation | GATED MMI-DEC-219 | Same |

**Done when:** Separate Matt authorization + promotion gate; not mixed with #19 build.

---

## Current Scoreboard Snapshot

| Metric | Value |
|--------|-------|
| BREADTH runway | 40 / 70 `GOVERNED_AGENT` |
| #19 Dual-Approval | GOVERNED_AGENT MMI-DEC-236 | depth lane closed at ES1 |
| DEPTH gate (#84–#94) | CLOSED (BS-D3) |
| STAGE_B gate (#38 etc.) | CLOSED |

---

## Explicitly Not Short-Term

- Production dispatch for Stage 1 wrappers
- DEPTH stack build (#84–#94) until real-data gate opens
- Stage B autonomy (#38 Containment, etc.)
- Purple Translation Layer implementation (research only — MMI-DEC-223/226/227)
- VPV Ergonomics Stage 2 integration
- Pushing unpushed commits unless Matt requests

---

## Weekly Check-In (60 seconds)

```bash
python3 scripts/mmi_pm_voice.py
python3 scripts/mmi_dispatch.py --verify
```

Ask:
1. Is the console showing one honest next action?
2. Is #19 still the authorized depth target?
3. Did any gate run produce blocking findings?
4. Is `active_task.md` still the task Matt would pick?

---

## Related Files

- `status/active_task.md` — current operator task
- `mission/milestone_map.md` — milestone definitions
- `mission/long_term_goals.md` — strategic arc
- `MMI_CURRENT_STATE.md` — session handoff prose
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` — row truth
