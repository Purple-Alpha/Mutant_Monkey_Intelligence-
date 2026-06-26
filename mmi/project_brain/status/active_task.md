# Active Task

This file records what the project brain believes is active right now. It should
match the short operator console.

## Current State

status: `ACTION`

task: `Run pre-build gate review on #19 Dual-Approval contract draft`

for: `Codex`

score: `8/10`

milestone: `M1_CONTROL_PLANE_RESTORED`

lane: `CONTRACT`

## Why This Is Active

Matt selected the evidence-board order: `#19` first, then `#66`, then `#70`.
`#43` is held for more research/design instead of build. The `#19 Dual-Approval`
contract draft is now on disk and must receive pre-build gate review before any
Matt §11 consideration.

## Done When

- Codex runs pre-build gate review on the `#19` contract draft
- findings are recorded in an audit output / evidence packet
- Matt reviews §11 only after a clean gate
- Cursor receives no build task until signed authority and explicit build
  authorization exist

## Closeout

MMI-DEC-224 records #19 contract draft placement. This pre-build gate task does
not authorize build, promotion, signing, production wiring, or AUTH-5.
