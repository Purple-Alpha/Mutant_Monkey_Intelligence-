# Active Task

This file records what the project brain believes is active right now. It should
match the short operator console.

## Current State

status: `ACTION`

task: `Resolve upstream Vendor Payment Verification workflow draft before #19 Dual-Approval re-gate`

for: `Claude`

score: `8/10`

milestone: `M1_CONTROL_PLANE_RESTORED`

lane: `CONTRACT`

## Why This Is Active

Matt selected the evidence-board order: `#19` first, then `#66`, then `#70`.
`#43` is held for more research/design instead of build. Codex ran the `#19`
pre-build gate and it blocked because `#19` depends on the upstream Vendor
Payment Verification workflow ergonomics draft, which is still pre-§11 and has
open questions.

## Done When

- upstream Vendor Payment Verification workflow ergonomics open questions are
  resolved or explicitly carved out
- the upstream workflow dependency is no longer an unsigned/open blocker for
  `#19`
- the `#19` contract warning language is cleaned up (`substitute controls` ->
  plain wording)
- Codex re-runs the `#19` pre-build gate
- Matt reviews §11 only after a clean gate
- Cursor receives no build task until signed authority and explicit build
  authorization exist

## Closeout

MMI-DEC-225 records the blocked #19 pre-build gate: 1 blocking finding and 1
warning. This upstream repair task does not authorize build, promotion, signing,
production wiring, or AUTH-5.
