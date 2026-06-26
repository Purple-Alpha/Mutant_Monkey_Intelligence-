# Active Task

This file records what the project brain believes is active right now. It should
match the short operator console.

## Current State

status: `ACTION`

task: `Start #19 Dual-Approval contract lane from Vendor Payment Verification evidence`

for: `Claude`

score: `8/10`

milestone: `M1_CONTROL_PLANE_RESTORED`

lane: `CONTRACT`

## Why This Is Active

Matt selected the evidence-board order: `#19` first, then `#66`, then `#70`.
`#43` is held for more research/design instead of build. The active lane is now
the `#19 Dual-Approval` contract lane because it has spec-only evidence, a clear
signed-contract blocker, and vendor-payment integrity value.

## Done When

- Claude drafts or refreshes the `#19 Dual-Approval` Agent Design Contract
- Codex runs pre-build gate review after draft is ready
- Matt reviews §11 only after a clean gate
- Cursor receives no build task until signed authority and explicit build
  authorization exist

## Closeout

MMI-DEC-222 records Matt's target order: `#19` then `#66` then `#70`, with
`#43` research/design requested. This contract-lane task does not authorize
build, promotion, signing, production wiring, or AUTH-5.
