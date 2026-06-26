# Active Task

## Current State

status: `ACTION`

task: `Authorize build lane — VPV workflow module then #19 DualApprovalAgent (both §11 signed MMI-DEC-231/232)`

for: `Matt`

score: `n/a`

milestone: `M1_CONTROL_PLANE_RESTORED`

lane: `BUILD_AUTH`

## Why This Is Active

Matt §11 signed both the Vendor Payment Verification Workflow Design Contract
(MMI-DEC-231) and #19 Dual-Approval Agent Design Contract (MMI-DEC-232) on
2026-06-25. Scoreboard #19 is `SIGNED_UNBUILT` / `NEEDS_BUILD_AUTH`. Pre-build
gates were already clean (MMI-DEC-229/230). No Cursor build until Matt explicitly
authorizes the build lane.

## Done When

- Matt authorizes VPV workflow build (`core/workflows/vendor_payment_verification.py`)
- Matt authorizes #19 wrapper build after VPV ES1 exists or in declared order
- Codex pre-build on implementation slices as required
- completion gates 0/0 before GATED reconcile

## Closeout

MMI-DEC-231 / MMI-DEC-232. §11 does not authorize build, promotion, or AUTH-5.
