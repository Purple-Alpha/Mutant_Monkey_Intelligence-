# Active Task

## Current State

status: `ACTION`

task: `#70 Final Review Agent — contract DRAFT placed (MMI-DEC-242); pre-build gate pending`

for: `Codex` (pre-build gate) then `Matt` (§11)

score: `7/10`

milestone: `M1_CONTROL_PLANE_RESTORED`

lane: `CONTRACT`

## Why This Is Active

Claude advisory draft reconciled and placed at
`4. Product_Roadmap/Final_Review_Agent_Design_Contract_Deep_Dive.md` (Slice B only).
Slice A gates remain separate infrastructure (MMI-DEC-240). Step 00 validation pending
confirm. **Not** build authorization.

## Done When

- [x] Contract DRAFT placed with REPO_RECONCILIATION (Slice A/B, gate registry, stages)
- [x] Step 00 `validate_agent_contract_block.py` PASS (31/31)
- [ ] Codex pre-build gate 0 blocking on contract
- [ ] Matt §11 signature (separate from placement)
- [ ] `mmi_dispatch.py --verify` PASS after commit

## Closeout

MMI-DEC-242. §11 + explicit build auth required before `FinalReviewAgent` implementation.
