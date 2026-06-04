# Consequence Matrix — Stage 9 Grok Package Audit Wiring

**Status:** Operator-triggered analysis (pre-§11, non-binding). Run 2026-06-04 per `Consequence_Matrix_Process.md`.
**This file surfaces second-order effects. Matt decides; the outcome is recorded in §Outcome.**

## Decision
**Decision:** Whether and how to wire stage 9 — the live Grok package audit — for the Cyber Insurance Evidence Package generator, expanding the operator-authorized 2026-06-04 "Pass-1 internal scope" that deferred it.
**Date:** 2026-06-04
**Owner:** Matt Nichol
**Why this matters:** The §11-signed implementation spec §10 *requires* a Grok package audit (Done Criteria 11/12) for any package to be "done" — so this is a required pipeline stage, not optional. But wiring it means generated package content (rendered claims, evidence surfaces) is submitted to an **external model** (Grok-4 / xAI), it adds API cost (HC11), and it nudges the runtime toward calling third parties. That is path-setting (third-party data exposure + cost + autonomy + architecture).

## Options
- **Option A — Inline auto-audit:** `generate_package_from_test_plan` submits to Grok on every generation.
- **Option B — Separate explicitly-invoked audit step:** a `package_auditor` module + script entry (mirroring `audit_tools/complete_gate.py` and `scripts/cyber_insurance_package_generate.py`); assembles the packet (already built), submits to Grok only on explicit invocation, saves output, maps findings -> drift incidents, satisfies criteria 11/12. Generation stays offline + deterministic; live call is opt-in; synthetic/test packages only for now.
- **Option C — Keep deferred:** status quo; criteria 11/12 stay structurally unmet.

## Short-Term Consequences (0-30 days)

| Option | Opens | Closes | Build Surface Added | Reduces Risk | Creates Risk | Pipeline Signal |
|---|---|---|---|---|---|---|
| A | Every package auto-reaches criteria 11/12 | Deterministic, offline generation + offline tests | Submission client + findings->drift mapping + criteria wiring **in the hot path**; network mocking everywhere | None meaningful | **High** — non-deterministic/networked tests, per-run cost, external send baked into generation, future real-package over-send | "Done" package demo |
| B | Criteria 11/12 reachable via an explicit, logged audit step | Little | `package_auditor` module + script + injected Grok client (real live / fake in tests) | Keeps generation deterministic + offline; isolates the external call; HC11 cost monitoring attaches to the explicit step | A manual step (operator runs it) — acceptable, mirrors the gate | Same demo, controlled |
| C | Nothing | A "done" package stays impossible | None | None | Nothing | None (product can't complete a package) |

## Long-Term Consequences (3-12 months)

| Option | Architecture Lock-In | Trust / Credibility | Legal / Insurance Exposure | Maintenance Burden | Evidence / Data Value | Doctrine Drift Risk | Claim / Forbidden-Language Risk | Operator-Time Burden | Long-Term Reversibility |
|---|---|---|---|---|---|---|---|---|---|
| A | Toward inline external calls in the runtime (against local-first) | Risk of accidental over-send of future real packages | **High** — real-customer package content to an external model with no controls gate | High (mock everywhere) | Neutral | **High** — contradicts the `complete_gate.py` separate-tool pattern + VISION local-first | Low | Low | **Low** — hard to unbake |
| B | Clean seam; external call isolated + opt-in; matches existing pattern | High — explicit + logged, like the gate operators already trust | The explicit step is the natural enforcement point for "synthetic-only now; real-customer send needs its own controls decision" | Low | Neutral | Low — consistent with VISION + gate pattern | Low | One explicit invocation per audit | **High** |
| C | None | Neutral | None | None | Neutral | Mild (required stage indefinitely unbuilt) | None | None | High |

## Decision Notes
- **Biggest upside (B):** makes criteria 11/12 reachable with the disciplined, logged, opt-in pattern operators already trust; generation stays deterministic + offline; real-customer-send stays a separate future decision.
- **Biggest downside (A):** bakes a third-party call into the runtime hot path — against VISION local-first and the established `complete_gate.py` separate-tool pattern — and risks over-sending future real packages.
- **Hidden dependency:** the eventual "send real customer package content to an external model" decision (needs its own controls spec); Option B keeps that door explicit, Option A quietly walks through it.
- **Assumption that must be true (B):** a manual/explicit audit invocation per package is acceptable (it is — it mirrors `complete_gate.py`).
- **Optionality killed by A:** cheap ability to keep the runtime free of inline external calls.
- **What A implicitly authorizes:** auto-submitting package content to a third party as a normal generation side effect.
- **Reverse trigger (B):** if explicit invocation proves too manual at scale, revisit batching — but only with the real-customer-data controls decision made first.
- **Evidence needed before any real-customer send (either option):** a separate controls/redaction-for-external-audit decision; v1 stays synthetic/test packages only.

## Outcome
**Operator decision:** **Option B** — build stage 9 as a separate, explicitly-invoked, opt-in audit step (mirroring `audit_tools/complete_gate.py`); generation stays offline + deterministic; synthetic/test packages only in v1. Authorized by Matt Nichol 2026-06-04, conditioned on the agent's honest assessment that the build is warranted on the merits (the §11-signed spec §10 *requires* the Grok audit for Done Criteria 11/12 — it is a required stage, not an optional add). This expands the operator-authorized 2026-06-04 Pass-1 internal scope to include the live package audit on synthetic packages.
**Reason:** Criteria 11/12 are unreachable without stage 9, so a package can never be "done" without it; milestone A (done-declaration) exposed 11/12 as the exact gaps. Option B isolates the external call behind an explicit, logged step consistent with VISION local-first and the existing gate pattern, and keeps "send REAL customer package content to an external model" as a separate future controls decision (synthetic-only now).
**Review trigger or date:** Before any real-customer package is ever submitted to Grok — that requires its own controls/redaction-for-external-audit decision and spec. v1 stays synthetic/test packages only.
