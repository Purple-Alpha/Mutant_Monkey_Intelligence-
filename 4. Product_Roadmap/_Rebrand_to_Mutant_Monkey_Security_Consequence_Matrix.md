# Consequence Matrix — Rebrand to Mutant Monkey Security

**Status:** Operator-triggered analysis (pre-§11, non-binding). Run 2026-06-04 per `Consequence_Matrix_Process.md`.
**This file surfaces second-order effects. It does not decide. Matt decides; the outcome is recorded in §Outcome.**

## Decision
**Decision:** How far to propagate the name "Mutant Monkey Security" (`mutantmonkeysecurity.com`, registered 2026-06-04) across the project.
**Date:** 2026-06-04
**Owner:** Matt Nichol
**Why this matters:** The current name ("NorthStar" / "SwarmCommand") appears in `VISION.md`, multiple §11/§13-signed specs, code namespaces (e.g. `3. SwarmCommand_Engine/`), trackers, and any future client-facing artifact. Product identity is a §2/§7 path-setting surface; renaming signed specs is operator-authority + a gate re-run per spec (§6 spec-first).

## Options
- **Option A — Full rebrand now:** rename across VISION, all signed specs, code namespaces, trackers, and client-facing material.
- **Option B — External brand now, internal codenames stay:** use "Mutant Monkey Security" + the domain on all buyer-facing/commercial surfaces immediately; leave "NorthStar"/"SwarmCommand" as internal repo codenames; run trademark clearance in parallel; defer any deep rename to a real trigger.
- **Option C — Defer entirely:** hold the name (domain parked), change nothing, revisit later.

## Short-Term Consequences (0-30 days)

| Option | Opens | Closes | Build Surface Added | Reduces Risk | Creates Risk | Pipeline Signal |
|---|---|---|---|---|---|---|
| A | One unified brand everywhere | Any "NorthStar" recognition (minimal, pre-revenue) | **Large** — every signed spec needs operator-authorized revision + fresh gate; code namespace + path churn | Future brand-inconsistency | **High** — mass signed-spec edits = drift + gate burden + broken refs mid-flight | Neutral (pre-pipeline) |
| B | Buyer-facing brand + domain usable immediately | Almost nothing | **Tiny** — README done; a one-line name-mapping note | Avoids premature mass edits; lets trademark clearance run in parallel | Mild dual-name confusion (internal vs external) — manageable | **Positive** — real brand on early MSP materials |
| C | Nothing | Putting a brand on early materials | None | None beyond B | Domain bought but no recorded brand decision = drift | None |

## Long-Term Consequences (3-12 months)

| Option | Architecture Lock-In | Trust / Credibility | Legal / Insurance Exposure | Maintenance Burden | Evidence / Data Value | Doctrine Drift Risk | Claim / Forbidden-Language Risk | Operator-Time Burden | Long-Term Reversibility |
|---|---|---|---|---|---|---|---|---|---|
| A | Name baked into namespaces/paths | Consistent, but churn now risks internal errors | **Premature** — domain != trademark; deep commit before class-35/42 cyber clearance | High now, low later | Neutral | **High** — bulk signed-spec edits is the high-burden op doctrine warns against | Low (name itself is clean) | High now | **Low** — re-rename is expensive |
| B | None new | External consistency; internal codename is normal practice | Lets trademark clearance precede deep commitment (safer) | Low | Neutral | Low — no signed-spec churn | Low | Low | **High** — can promote to full rename or switch names cheaply |
| C | None | Slightly worse than B (no brand on materials) | Same as B | Low | Neutral | Mild (undecided identity lingers) | Low | Low | High |

## Decision Notes
- **Biggest upside (B):** bank the brand + domain on buyer-facing surfaces now, zero signed-spec churn, trademark clearance runs in parallel, fully reversible.
- **Biggest downside (A):** triggers an operator-authorized revision + gate re-run on every signed spec, before trademark class clearance — high cost, low reversibility (the butterfly trap).
- **Hidden dependency:** trademark clearance in the cybersecurity classes (est. 9/42, and 35 for services) — `mutantmonkeysecurity.com` being available is *not* trademark clearance.
- **Assumption that must be true (B):** an internal codename ("NorthStar") diverging from the external brand is acceptable (it is — common practice).
- **Optionality killed by A:** cheap ability to change the name again.
- **What A implicitly authorizes:** treating the rename as bigger than the product work it interrupts.
- **Reverse trigger (B):** first signed MSP pilot, or trademark clearance result, is the natural point to decide on a deep rename.
- **Evidence needed before committing to A:** trademark clearance in the cyber classes.

## Outcome
**Operator decision:** **Option B** — use "Mutant Monkey Security" + `mutantmonkeysecurity.com` on all buyer-facing / commercial surfaces now; keep "NorthStar" / "SwarmCommand" as internal repo codenames; run trademark clearance (cyber classes) in parallel; defer any deep rename of signed specs / code namespaces. Selected by Matt Nichol 2026-06-04.
**Reason:** Banks the brand + domain immediately with ~zero internal churn and full reversibility, and lets trademark clearance precede any deep commitment. Avoids the mass signed-spec revision + gate burden of Option A before the name is legally cleared.
**Review trigger or date:** First signed MSP pilot, OR the trademark-clearance result in the cybersecurity classes — whichever comes first — is the trigger to revisit a deep rename.
