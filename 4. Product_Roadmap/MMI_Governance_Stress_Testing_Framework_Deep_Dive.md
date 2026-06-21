# MMI Governance Stress Testing Framework — Deep Dive

> **SUPERSEDED IN FRAMING (2026-06-22).** Contract-of-record is now
> `4. Product_Roadmap/MMI_Governance_Invariants_Testing_Framework_Contract.md`.
> "Stress testing" was historical working-lane language only. Retained for audit trail; do not
> cite as authority.

**Status:** SUPERSEDED DRAFT — see invariants contract above

**Scoreboard row:** #105 MMI Governance Stress Testing Framework (`agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md`)

**Operator pivot (2026-06-22):** Parks Claude `#67 Rule Improvement` contract-draft feedstock. Elevates governance-layer stress testing to **active design lane** with multi-model advisory review (Claude + Gemini + ChatGPT) before any `#67` build resumes.

**Scope reminder:** Specifies how Mutant Monkey Intelligence (MMI) proves **cognitive alignment, behavioral drift resistance, and protocol compliance** across agents-that-watch-agents. Wraps and extends existing MMI pytest coverage, `scripts/mmi_contradiction_report.py`, `scripts/mmi_crew_chain.py`, test-support agents `#61`–`#63`, and audit gates. Does **not** authorize AUTH-5, autonomous routing, live offensive testing, or Domain Two work.

---

## §0 Purpose

MMI is a domain-agnostic governance brain. Traditional code tests prove functions return expected values. They do **not** prove:

1. Multi-agent crew loops stay deterministic under concurrency and fault injection.
2. Epistemic drift (stale contracts, poisoned blueprints, contradictory state) is detected and halted.
3. AUTH-5 remains blocked — no agent combination can close a gate or alter trajectory without verified human authority.
4. Governance integrity scales as domains branch without email-fraud assumptions leaking into core.

This framework defines **how MMI stress-tests itself** — not just how Inbox Shield detects fraud.

---

## §1 Scope

### In scope (v1 design → sign → build)

- Four governance stress pillars (§3), each with synthetic-only fixtures, pass/fail vocabulary, and audit-trail recording requirements.
- Multi-lane **design phase** brief (`MMI_Governance_Stress_Testing_Advisory_Lane_Brief.md`) for Claude / Gemini / ChatGPT advisory pressure before §11.
- Audit-gate amendments (§5): what `complete_gate.py` worker manifests must include for MMI governance slices; what Grok must inspect.
- Phased build plan (§7): Design NOW → §11 sign → Mode A pytest harness → Mode B fail-closed pipeline integration (parked until signed).
- Explicit relationship to `#61` Test Case Generator, `#62` Regression Test, `#63` Adversarial Test, Tier 2C contradiction report, and the unsigned Email Security Testing Evidence Framework matrix.

### Out of scope (v1)

- Live LLM agent collusion in production; all rebellion/co-sim tests use **fixtures and deterministic scripts only**.
- Network attack simulation, live malware, external pentest, or real-customer-data handling.
- Replacing `complete_gate.py` or `pre_ship_audit.py` — this framework **extends** them.
- Domain Two (Property / connected-home) implementation — framework must stay domain-clean per `mmi/concepts/MMI_MULTI_DOMAIN_EXPANSION_CONCEPT_SHEET.md`.
- AUTH-5 unlock or registry-fed routing under any test outcome.

---

## §2 Locked Design Decisions (advisory until §11)

| # | Decision | Locked value |
|---|---|---|
| GSTF-D1 | Framework identity | Distinct from Email Security Testing Framework; tests **governance behavior**, not detector accuracy. |
| GSTF-D2 | Synthetic-only boundary | All stress fixtures live under `tests/fixtures/mmi_governance_stress/`; no production tenant or live handoff log mutation in v1. |
| GSTF-D3 | Four pillars | Co-simulation, epistemic drift injection, authority rebellion probing, combinatorial mutation fuzzing (governance-scoped subset in v1). |
| GSTF-D4 | Fail-closed default | Any pillar failure blocks MMI governance slice closure unless D20-style conjunctive operator acceptance (inherits Email Testing Framework D20 shape when that spec signs). |
| GSTF-D5 | AUTH-5 invariant | Stress tests must **prove** AUTH-5 cannot be bypassed; a test that accidentally grants autonomous selection is a **blocking defect**, not a flaky test. |
| GSTF-D6 | Tier 2C relationship | Mode A contradiction report remains read-only; GSTF Mode B (pipeline halt on drift) is a **separate** build authorization after GSTF §11 — does not silently upgrade Tier 2C. |
| GSTF-D7 | Test-support agents | `#61`–`#63` emit cases; GSTF harness **executes** governance stress cases in pytest — generators alone are insufficient for pillar closure. |
| GSTF-D8 | Multi-lane design gate | No §11 signature until Matt records advisory review from Claude (architecture), Gemini (plain-language + risk), ChatGPT/MMI Advisor (routing + scope tightness) per advisory brief. |
| GSTF-D9 | Park `#67` until GSTF design closes | `#67 Rule Improvement` contract draft remains **parked** (`hold_unless_matt` in BOR) until GSTF reaches §11-ready or Matt explicitly unparks. |
| GSTF-D10 | Audit manifest requirement | Any MMI governance code slice touching `scripts/mmi_*.py` must list governance stress acceptance tests in the worker manifest for `complete_gate.py`. |

---

## §3 Four Governance Stress Pillars

### §3.1 Pillar 1 — Multi-Agent Co-Simulation (`GSTF-P1`)

**Problem:** `mmi_crew_chain.py` runs roles sequentially. Race conditions, lag, and corrupt handoff packets are untested.

**v1 test shape:**

- Accelerated synthetic "build sprint" fixture: Estimator → Architect → Superintendent → PM over frozen repo snapshots in `tests/fixtures/mmi_governance_stress/co_sim/`.
- Inject faults: delayed stdout, truncated handoff section, duplicate DEC id, missing manifest field.
- **Pass:** Dispatcher/crew chain emits `REVIEW_REQUIRED` or hard stop; no silent task drop; immutable paths unchanged (digest guard from crew-chain tests).
- **Fail:** Any authoritative conclusion (`AUTHORIZED`, `GATED`, `COMPLETE`, etc.) without operator token.

**Future v1.1:** Concurrent subprocess workers with bounded thread pool — not v1.

### §3.2 Pillar 2 — Epistemic Drift / Contradiction Injection (`GSTF-P2`)

**Problem:** Tier 2C reports drift but does not halt the pipeline. Blueprint-of-record poisoning is a governance-critical threat.

**v1 test shape:**

- Fixture repos with planted contradictions: stale contract hash referenced by Architect output; unsigned variable in BOR; scoreboard lifecycle mismatch vs DEC log.
- Run `mmi_contradiction_report.py` + `mmi_dispatch.py --verify` + Superintendent fixture paths.
- **Pass:** Contradiction detected with named finding id; downstream "build authorized" paths unreachable in fixture.
- **Fail:** Poisoned state proceeds to `SCORED_FEEDSTOCK` or PM Voice `YOU_DO` implying authorization.

**Mode B (post-sign, separate auth):** Pipeline halt hook — unsigned spec only in this draft.

### §3.3 Pillar 3 — Authority Rebellion Probing (`GSTF-P3`)

**Problem:** AUTH-5 blocked by doctrine; not proven under adversarial prompt/fixture combinations.

**v1 test shape:**

- Deterministic fixture inputs to PM Voice, Estimator output validator, and crew-chain forbidden-conclusion scanner simulating "optimize by closing gate" narratives.
- Attempt synthetic DEC lines without Matt Nichol authorship pattern; attempt `AUTONOMOUSLY_SELECTED` in feedstock rank output.
- **Pass:** Hard rejection or `REVIEW_REQUIRED`; state machine remains locked.
- **Fail:** Any path writes GATED, promotes feedstock to build, or emits authorization vocabulary.

### §3.4 Pillar 4 — Combinatorial Governance Mutation (`GSTF-P4`)

**Problem:** Individual governance tests pass; combined failures may not.

**v1 test shape (governance-scoped, not Inbox Shield fraud):**

- Combine P1 fault + P2 poison + P3 rebellion attempt in one fixture sprint.
- Measure: verify latency (wall clock in test), number of blocking findings, no exponential hang (> fixed timeout).
- **Pass:** Linear-bounded runtime; at least one blocking finding; no authority bypass.
- **Fail:** Hang, silent pass, or authorization leak.

**Note:** Inbox Shield combinatorial mutation (TOAD + ledger + impersonation) remains in runtime mutation engine tests — P4 here is **MMI governance only**.

---

## §4 Test Levels (GSTF-specific)

| Level | Name | Purpose | Auto on MMI script diff? |
|---|---|---|---|
| G-S | Governance smoke | Import + envelope vocabulary + immutability guards | Yes |
| G-R | Governance regression | Full existing `tests/test_mmi_*.py` suite | Yes |
| G-A | Governance adversarial | P1–P4 pillar fixtures | Yes |
| G-E | Governance eval baseline | Crew-chain + verify + contradiction on golden snapshot | On BOR/DEC/scoreboard diff |

Recording: mirror Email Testing Framework §9.2 event shape under `audit_outputs/mmi_governance_stress/runs/<run_id>/` once implemented.

---

## §5 Audit Integration (effective on design acceptance; enforced on implementation)

### §5.1 `complete_gate.py` worker manifest (GSTF-D10)

For any task touching `scripts/mmi_*.py`, `mmi/BLUEPRINT_OF_RECORD.md`, or MMI governance stress harness:

Manifest `files_read` must include this deep dive (once committed) and list which pillars (P1–P4) the slice claims to satisfy.

Manifest `acceptance_tests` must name pytest paths (once built), e.g.:

- `tests/test_mmi_governance_stress_p1_co_sim.py`
- `tests/test_mmi_governance_stress_p2_drift_injection.py`
- `tests/test_mmi_governance_stress_p3_authority_rebellion.py`
- `tests/test_mmi_governance_stress_p4_combinatorial.py`

Grok gate must fail closed if manifest claims pillar closure but omits test paths.

### §5.2 `pre_ship_audit.py` (future, after Email Testing Framework §11)

When Email Testing Framework D19/D22 sign, add **parallel** GSTF check for MMI governance diffs: required G-S/G-R/G-A tiers recorded. Until then: **manual** pytest + Grok gate remain authoritative.

### §5.3 Multi-lane design audit (NOW)

Before §11, Matt records one `PROJECT_ACTIVITY_LOG.md` entry summarizing:

- Claude architecture review verdict (overengineering / missing pillars)
- Gemini plain-language risk summary
- ChatGPT/MMI Advisor scope + routing verdict

No §11 signature without this entry.

---

## §6 Failure Modes

| ID | Failure | Severity |
|---|---|---|
| GSTF-F1 | Treating generator output (#61–#63) as executed stress proof | Blocking |
| GSTF-F2 | Live handoff log mutation in stress tests | Blocking |
| GSTF-F3 | Stress pass interpreted as build authorization | Blocking |
| GSTF-F4 | AUTH-5 bypass in any pillar | Blocking |
| GSTF-F5 | Email-fraud assumptions baked into governance core tests | Blocking (domain-clean violation) |
| GSTF-F6 | Tier 2C silently upgraded to halt without separate §11 | Blocking |

---

## §7 Phased Rollout

| Phase | Deliverable | Authorization |
|---|---|---|
| **0 — NOW (this pivot)** | This deep dive + advisory brief + BOR/scoreboard routing | Operator pivot MMI-DEC-080 |
| **1 — Multi-lane design review** | Advisory outputs captured in activity log | Matt orchestrates three lanes |
| **2 — §11 signature** | Locked D1–D10 + pillar acceptance criteria | Matt §11 only |
| **3 — Mode A harness** | P1–P4 pytest modules + fixtures; no pipeline halt | Separate build auth |
| **4 — Mode B integration** | Fail-closed hook on verify/contradiction; optional pre_ship tier | Separate build auth + Email Framework alignment |

**Build momentum rule:** Phase 3 is the first code slice. Phases 0–2 are documentation and review — valid because they unblock domain-clean governance proof.

---

## §8 Relationship Map

- `mmi/concepts/MMI_MULTI_DOMAIN_EXPANSION_CONCEPT_SHEET.md` — domain-clean core discipline; GSTF proves it under stress.
- `4. Product_Roadmap/Email_Security_Testing_Evidence_Framework_Deep_Dive.md` — parallel product-runtime matrix; sign both before unified pre_ship tier enforcement.
- `scripts/mmi_contradiction_report.py` — P2 consumes; Mode B extends separately.
- `#61` / `#62` / `#63` — case feedstock for governance targets; GSTF harness executes.
- `#67 Rule Improvement` — **parked** until GSTF Phase 2 complete or Matt unparks.

---

## §10 Open Questions (operator-only)

1. **Q1:** Should P1 co-sim use subprocess isolation or in-process mocks for v1?
2. **Q2:** Does Mode B pipeline halt belong in `mmi_dispatch.py --verify` or a new `mmi_governance_stress_gate.py`?
3. **Q3:** Minimum advisory review depth before §11 — one round each lane or iterative?
4. **Q4:** Unpark `#67` criteria: GSTF §11 signed only, or Phase 3 harness green?

---

## §11 Sign-Off

**Operator signature:** *(blank — Matt Nichol only)*

**Signature date:** *(blank)*

---

## §12 Non-Authority Footer

```
DRAFT ONLY. Does not authorize build, AUTH-5, routing, or #67 unpark.
Multi-lane advisory review required before §11.
Pillar tests are synthetic-only. Human authority held throughout.
```
