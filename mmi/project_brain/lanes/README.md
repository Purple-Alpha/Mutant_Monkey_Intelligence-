# MMI Work Lanes

Every task must belong to exactly one lane. Lanes keep Matt from having to guess
whether work is design, build, audit, or drift control.

## Lanes

`RESEARCH`
: Gather facts, compare options, or investigate unknowns. No build authority.

`DESIGN`
: Shape architecture, data flow, UI flow, or product behavior before contract.

`CONTRACT`
: Draft or revise authority text. No implementation authority by itself.

`PRE_BUILD_REVIEW`
: Adversarial review of an unsigned or pre-build contract. Usually Grok,
  Gemini, ChatGPT, Claude, or Codex depending on risk.

`BUILD`
: Implement signed and authorized work. Usually Cursor when the scope is clear.

`TEST`
: Run or write tests that prove an implementation matches authority.

`AUDIT`
: Gate review, evidence packet, security review, or complete_gate work.

`PROMOTION`
: Review a GATED component for possible GOVERNED_AGENT promotion. This is not a
  rebuild.

`DRIFT_CHECK`
: Confirm repo truth, scoreboard truth, routing truth, and authority boundaries.

`REVENUE_DEMO`
: Demo, operator flow, customer-facing proof, or sales-supporting artifact.

`PARKED`
: Known work that is intentionally not active.

## Owner Defaults

- `Cursor`: scoped implementation
- `Codex`: code review, routing logic, tests, safety critique, handoff clarity
- `Claude`: broad design, product reasoning, long-form contract drafting
- `Gemini`: second-opinion design review, research synthesis, cross-checks
- `ChatGPT`: operator docs, UX copy, research framing, external explanation
- `Grok`: adversarial pre-build gate review
- `Matt`: authorization, signing, scope choice, business decision

