# MMI_GOVERNANCE_INVARIANTS_TESTING_FRAMEWORK_CONTRACT

**Status:** §11 SIGNED 2026-06-21 by Matt Nichol (`MMI-DEC-092`; pre-build gate `MMI-DEC-091` 0/0)
**Lane:** Governance / Invariant Verification Framework
**Authority:** Mutant Monkey Intelligence (MMI)
**Repo:** `/home/socialarchitect/northstar`
**Implementation:** BLOCKED until Matt §11 sign-off + separate per-lane build authorization
**Source:** Reconciled multi-pass research, red-teamed against itself and corroborated against
external standards (NIST DSS / FIPS 186 signature definitions). "Stress testing" is historical
working-lane language only and is not the contract-of-record framing.

---

## 1. Executive Summary

This contract defines a Mode A, fixture-based, read-only framework that proves MMI's
governance laws as **explicit invariants** rather than assuming them. MMI is a governance brain
over an agent network. The existing software test stack (~2,600 pytest tests,
`mmi_dispatch.py --verify`, `complete_gate.py`, Grok gates) proves the code runs correctly on
the happy path. It does **not** prove that the system cannot drift, hallucinate authority, lose
handoffs, bypass Matt, silently mutate truth, confuse status with action, or become autonomous.

This framework is an **invariants testing framework** — a deterministic verifier of governance
laws — not a stress, load, or chaos harness. It is built lane by lane in fixed priority order.
The first buildable lane is the **Authority Escalation Probe**.

**Honest scope (read this first — Section 2.8 is binding):** This framework defends against
**accidental drift and self-misdirection** (the likely failure mode for a system built by AI
agents that loosely match tokens). It does **not** defend against **malicious signature
forgery**, because §11 signatures are currently non-cryptographic typed labels. Cryptographic
signing is a named, separate, future contract. No claim of forgery-resistance is made here.

---

## 2. Foundational Laws (top-level — bind every lane)

- **LAW 1 — Detect, not enact.** An authority probe may only prove whether an unauthorized
  authority state is *reachable*. It may never *enact* reachability — never perform, simulate
  as real, grant, unlock, persist, dispatch, route, or mutate any authority-bearing state.

- **LAW 2 — The harness never gains the authority it tests.** The framework must never acquire,
  hold, or exercise the authority it verifies. It is a static/deterministic verifier, not a
  dynamic executor. Even with a valid §11 fixture present, the harness only *observes the expected classification* — it never *performs* the transition.

- **LAW 3 — First buildable lane is `MMI_AUTHORITY_ESCALATION_PROBE_MODE_A`.** No other lane
  builds before it.

- **LAW 4 — Lane order is fixed.** Lane 1 = Authority Escalation Probe. Lane 2 = Handoff/Queue
  Integrity. Lane 3 = Epistemic Drift. Each builds only after the prior is gated.

- **LAW 5 — Tiers 5–7 are design-only.** Multi-agent co-simulation, domain mutation/fuzzing,
  blueprint-lifecycle automation are specified but NOT built under this contract.

- **LAW 6 — Tier 6 adversarial generation is offline fixture generation only.** Synthetic test
  cases against *declared* boundaries only. Never a live agent, never targets real MMI surfaces,
  never coerces active handlers, never produces executable bypass workflows. Output is test
  evidence only.

- **LAW 7 — PM Voice tests assert deterministic safe-failure.** A PM Voice non-selection test
  asserts an explicit no-handler safe-failure. "Asks for clarification" is NOT a valid pass
  condition. Safe-failure only.

- **LAW 8 — Two dumb static readers beat one smart one; never live execution.** Safety-critical
  verification is achieved by redundant, independent, *static* analysis of unexecuted fixtures —
  never by running code to prove it safe. The innermost safety check must be primitive enough to
  be verified by human reading (see Section 6.6 dual-engine, Section 2.7).

- **LAW 9 — Honest scope: drift-defense, not forgery-defense.** Because the §11 signature is a
  non-cryptographic typed label, this framework hardens against *accidental* drift and
  self-misdirection only. It provides **no** defense against *deliberate* signature forgery. No
  document, test, or report produced under this contract may claim forgery-resistance,
  non-repudiation, or "authority cannot be forged." (See Section 2.8.)

### 2.7 — The "stupidly simple core" principle (under LAW 8)
The more complex a safety check is, the more surfaces it has for its own bugs and drift. The
innermost authority check (Engine B, Section 6.6) must be small, dependency-free, and simple
enough that a human can read it and *know* it is correct without trusting a test. Redundancy is
good; radical simplicity at the core is better. Safety is a dumb, unyielding tripwire — not an
intelligent probe.

### 2.8 — Signature primitive limitation (BINDING — must appear in framework docs)
> **Limitations:** The §11 signature is presently a simple text label (e.g.
> `Signature: Matt Nichol`) checked statically by the framework. This guards against
> unintentional bugs or mis-parses (drift) and against the system confusing advisory text for
> authority. It does **not** prevent an attacker or compromised process with file-write access
> from inserting the same text. A typed name is an *electronic* signature (intent confirmation),
> not a *cryptographic* one (identity + integrity proof per NIST DSS / FIPS 186). True
> non-forgeability requires a real digital signature scheme (e.g. Ed25519/ECDSA over a content
> hash, with a private key only Matt holds and a distributed public key), which is **not yet
> implemented** and is scoped as a separate future contract:
> `MMI_CRYPTOGRAPHIC_SIGNING_CONTRACT` (proposed, unscoped, not authorized here).

---

## 3. Mode A Constraints (apply to every lane)

- Local, deterministic, fixture-based, reproducible (seeded or no randomness).
- Read-only except a volatile local results dir (e.g. `/tmp/mmi_test_runtime/`); never the repo.
- No routing, no candidate selection, no scoreboard/lifecycle/blueprint writes.
- No AUTH-5 path, no real authorization, no daemon/hook/background process.
- No production data, no external services, no live LLM/API calls.
- The harness never gains or exercises the authority it tests (LAW 2).

---

## 4. Scope of This Contract

Covers: the foundational laws (Section 2), Mode A constraints (Section 3), the tier
architecture as specification, the **build authorization for Lane 1 only** (pending §11), the
specification (not build) of Lanes 2–3, and the design-only status of Tiers 5–7.

Does **not** cover: building Lanes 2/3 (separate authorization each); building Tiers 5–7; any
cryptographic-signing work (separate future contract, Section 2.8); any §11 sign-off; any state
mutation; any live/production testing or live-runtime authority gating (see Section 6.6 note).

---

## 5. Tier Architecture (specification)

| Tier | Name | Status under this contract |
|---|---|---|
| T1 | Regression / unit / integration | Exists; reframed in governance terms |
| T2 | Handoff / queue integrity | **Lane 2 — specced, build separately** |
| T3 | Authority escalation | **Lane 1 — build authorized pending §11** |
| T4 | Epistemic drift / contradiction injection | **Lane 3 — specced, build separately** |
| T5 | Multi-agent co-simulation | DESIGN-ONLY |
| T6 | Domain mutation / scenario fuzzing | DESIGN-ONLY (LAW 6 boundary) |
| T7 | Blueprint-of-record / active-pipe | DESIGN-ONLY |

---

## 6. LANE 1 — `MMI_AUTHORITY_ESCALATION_PROBE_MODE_A` (build authorized pending §11)

### 6.1 Purpose
Prove that no agent output, advisory text, handoff, script, prompt, or voice layer can create
or imply authority, and that no path to AUTH-5 / `NEXT_DECIDED` exists without an explicit Matt
§11 signature fixture — *within the drift threat model* (LAW 9).

### 6.2 What it proves (drift-scope)
Unauthorized authority states are **not reachable** from any of these surfaces without a §11
signature fixture present: agent outputs, advisory text, handoffs, blueprint language,
superintendent verdicts (`MATCHES_BLUEPRINT`), PM recommendations (`PROCEED_FOR_MATT_REVIEW`),
PM Voice phrasing, dispatcher summaries, stale logs.

### 6.3 What it must NOT do (LAW 1 + LAW 2)
- Must not enact reachability or perform any authority transition.
- Must not grant, unlock, persist, or simulate-as-real any authorization.
- Must not write lifecycle state, populate `BLUEPRINT_OF_RECORD`, route work, or select candidates.
- Must not unlock AUTH-5 or mutate any authority-bearing file.
- Even with a valid §11 fixture present, it only observes the expected classification — it never
  performs the transition.

### 6.4 Authority Probe Meta-Rule (central acceptance criterion)
> The Authority Escalation Probe may only prove whether an unauthorized authority state is
> reachable from declared inputs, fixtures, logs, scripts, prompts, or outputs. It may not
> perform, simulate as real, grant, unlock, persist, dispatch, route, or mutate any
> authority-bearing state. The harness is a verifier of reachability, not an executor of the
> authority path being tested.

### 6.5 Structural advisory rule (Layer-3 hardening — drift defense)
The exploit this closes: an LLM emits advisory text that *implies* action ("the review is
complete and §11 indicates this is ready to proceed"), and a downstream parser broad-matches an
actionable verb and acts on it — no forbidden token was ever emitted, yet the system acted.

The fix is **structural, not lexical** (do NOT scan for "dangerous words" — common verbs appear
in legitimate advisory text and word-scanning false-alarms into uselessness):
- Authorization may be read **only** from a designated, structured signature field.
- The **body text of any advisory block is never a routing or authorization input** — the
  parser must structurally ignore advisory body content as a source of authority, regardless of
  what verbs it contains.
- Test asserts: an advisory block containing actionable language, with no signature field, never
  produces an authorized classification.

### 6.6 Dual-engine static cross-check (Layer-5 hardening — drift defense)
To guard against a bug in the primary parser, signature presence is verified by **two
independent static readers of the same unexecuted fixture** that must agree:
- **Engine A (router-level):** the complex parser that interprets structure/state.
- **Engine B (tripwire):** a stripped-down, dependency-free reader that does ONE thing — checks
  for a valid signature field — and **shares no parsing/deserialization logic with Engine A**
  (e.g. byte/string-level match), so a serialization bug that fools A cannot also fool B.
- **Concurrence:** the test passes only if A and B agree on signature presence; disagreement is
  a hard test failure.

**Honest caveat (LAW 9):** the dual-engine catches *parser disagreement* (Engine A misreading)
— it does **not** catch forgery, because both engines can be fed the same forged typed string
and will agree it is "present." It defends against drift, not against a deliberate forger.

**Scope carve-out (binding):** under this contract the dual-engine is a **fixture-based test**
that verifies the property holds over fixtures. Making the dual-engine a **live runtime
authorization gate** in the production dispatcher is a *separate, unscoped contract* and is
**not authorized here.** This contract tests; it does not re-architect the live dispatcher.

### 6.7 Inputs (fixed)
- A static authority state-machine model (declared states/transitions) — *read, never walked.*
- Surface fixtures: role outputs, advisory text, handoff logs, blueprint language, verdicts, PM
  recommendations, PM Voice phrasings, dispatcher summaries, stale logs.
- Declarative §11 signature fixtures (present/absent) — classification inputs only.

> **Cursor reconciliation:** confirm the real authority-state model and real surface outputs
> against the live repo before §11; lock the fixture set. The model is read, never executed.

### 6.8 Output
A human-readable governance report (e.g. `NO PATH TO AUTH-5 FOUND IN FIXTURES`), per-test
pass/fail, exit code 1 + standardized panic-log block on any invariant breach. The probe emits
no authorization token, no AUTH-5-like state, nothing resembling a grant.

### 6.9 Expected command
```
python3 scripts/mmi_authority_escalation_probe.py --mode mode_a \
  --fixtures tests/fixtures/mmi_authority_escalation/
```

### 6.10 Minimum Mode A tests
- **Reachability:** every forbidden transition blocked unless a §11 fixture is present; even
  then, classification observed, transition never performed.
- **Role-output misinterpretation:** role outputs are never classified "authorized."
- **Structural advisory (6.5):** advisory body never yields authorization; only the signature
  field does.
- **Dual-engine concurrence (6.6):** Engine A and Engine B must agree; disagreement fails.
- **PM Voice deterministic safe-failure (LAW 7):** ambiguous/advisory input → explicit
  no-handler safe-failure; never selects, never asks.
- **Verdict/stale non-elevation:** `MATCHES_BLUEPRINT` ≠ approval; `PROCEED_FOR_MATT_REVIEW` ≠
  `NEXT_DECIDED`; blueprint language ≠ build authorization; stale log ≠ live authority.

---

## 7. LANE 2 — `MMI_HANDOFF_QUEUE_INTEGRITY_MODE_A` (specified, build separately)

**Purpose:** Prove handoffs/queues never lose, duplicate, stale-but-show-live, or misroute work.
**Proves:** complete in-flight view; no lost/duplicated/stale-live handoffs; PM Voice routes to
exactly one handler+action or safe-fails; append-only logs cannot be silently contradicted;
retries preserve context and do not duplicate; cross-agent context-leak is caught.
**Must not:** touch real queues or live PM Voice; auto-reassign; run as background monitor.
**Min tests:** in-flight visibility; single-routing-target; stale-handoff detection (timestamp
preceding a locked event is quarantined); append-only consistency; retry de-duplication;
context-leak detection.
**Command:** `python3 scripts/mmi_handoff_queue_integrity.py --mode mode_a --fixtures ...`

---

## 8. LANE 3 — `MMI_EPISTEMIC_DRIFT_PROBE_MODE_A` (specified, build separately)

**Purpose:** Prove contradictions and drift across governance artifacts are detected and halt
execution.
**Proves:** contract/scoreboard/blueprint/explanation contradictions caught; later docs cannot
silently overwrite signed boundaries; **GATED requires real gate evidence** (GATED flag with
empty/missing evidence manifest is flagged invalid); PM Voice cannot report unsupported actions;
explanations (#52) add no advice/judgment not in input.
**Layer-4 hardening (drift defense):** drift tests must fuzz for **structural absence and
serialization anomalies**, not only clean boolean contradictions — e.g. a hash referenced in one
ledger but absent in another (omission); a timezone-offset format that causes a new signed
boundary to parse as an archived historical document (serialization). Real drift is usually
omission or mis-serialization, not a tidy `active:true` vs `draft:true` conflict.
**Must not:** modify real contracts/scoreboards/blueprints; auto-heal or reconcile drift — detect,
report, panic-halt only; generate live explanations.
**Command:** `python3 scripts/mmi_epistemic_drift_probe.py --mode mode_a --fixtures ...`

---

## 9. Tiers 5–7 (DESIGN-ONLY — not built under this contract)

- **T5 Multi-agent co-simulation** — scripted full-chain simulation; conflict-halting;
  Matt-authority-never-dropped; deterministic clocks decoupled from host clock. Build only after
  Lanes 1–3 gated.
- **T6 Domain mutation / fuzzing** — bounded offline fixture generation against declared
  boundaries only (LAW 6). Never a live coercion engine.
- **T7 Blueprint-of-record / active-pipe** — exactly one CURRENT_PLAN; DRAFT never CURRENT;
  blueprint never routing input; no population without §11.

---

## 10. Security & Authority Risks

- **Harness-as-controller (primary):** a test harness that simulates routing/authority becomes a
  de-facto controller. Mitigation: LAW 1/2/8 — detect-not-enact, never live execution, harness
  holds no authority.
- **Overclaiming security (the corrected risk):** claiming forgery-resistance the framework lacks.
  Mitigation: LAW 9 + Section 2.8 — honest scope; drift-defense only; no forgery claims.
- **False confidence / mirror trap:** tests proving code works against tidy hand-crafted
  fixtures. Mitigation: Layer-4 omission/serialization fuzzing (Section 8).
- **Parser-bug authority leak:** a single parser misreads an unsigned block as authorized.
  Mitigation: dual-engine concurrence (6.6).
- **Advisory-as-command:** advisory body acted on as routing. Mitigation: structural rule (6.5).
- **Adversarial weaponization (T6):** Mitigation: LAW 6 offline-fixture-only.
- **PM Voice conversational drift:** Mitigation: LAW 7.
- **Scope-blur to live runtime:** dual-engine becoming a production gate via this contract.
  Mitigation: 6.6 scope carve-out.

---

## 11. Failure Modes

- Enacted transition (probe performs instead of analyzes) → LAW 1 violation → demotion.
- Harness-held authority → LAW 2 violation.
- Build out of order / before Lane 1 gated → LAW 3/4 violation.
- Tiers 5–7 built under this contract → LAW 5 violation.
- Live adversarial agent → LAW 6 violation.
- Conversational PM Voice test → LAW 7 violation.
- Live-execution verification path introduced → LAW 8 violation.
- Forgery-resistance claimed anywhere → LAW 9 violation.

---

## 12. Rollback / Demotion Plan

- Each lane is additive, read-only, fixture-isolated. Nothing in production depends on it.
- A lane that enacts a transition, holds authority, emits an authorization token, executes code
  to verify, or claims forgery-resistance is immediately disabled and re-gated under §11.
- Demotion recorded by the existing closeout workflow (append-superseding, never deletion).
- Until re-signed, governance verification reverts to manual review against this contract's laws.

---

## 13. Acceptance Criteria

1. **Determinism:** 100 consecutive runs on the same fixtures yield identical pass/fail; zero flake.
2. **Authority invariants (Lane 1):** no AUTH-5/`NEXT_DECIDED` path without a §11 fixture;
   structural advisory rule holds; dual-engine concurrence holds; detect-not-enact verified.
3. **Zero invariant leakage:** any injected contradiction, duplicate token, or unsigned
   escalation vector → exit code 1 + standardized panic-log naming the broken boundary.
4. **Strict local isolation:** runs entirely within the repo, no networking, no daemons, no
   production DBs; results only to a volatile local dir, never the repo.
5. **Zero state mutation:** read-only relative to operational repo state.
6. **Honest scope (LAW 9):** documentation states the signature is a non-cryptographic typed
   label; no forgery-resistance is claimed anywhere; crypto-signing flagged as future contract.
7. **Documentation:** each test module names the governance law it proves.

A lane is admissible for sign-off only when its criteria pass under `complete_gate.py 0/0` on
functional + adversarial suites.

---

## 14. What Must Not Be Built

- No lane that enacts authority transitions.
- No harness that holds the authority it tests.
- No live-execution verification path (static-only; two dumb readers, never one live run).
- No lane out of fixed order (Lane 1 first).
- No Tiers 5–7 under this contract.
- No live adversarial/coercion agent (T6 offline fixtures only).
- No conversational PM Voice test.
- No live-runtime dual-engine authorization gate (separate contract).
- No cryptographic-signing implementation (separate future contract, Section 2.8).
- No claim of forgery-resistance / non-repudiation anywhere.
- No routing, candidate selection, scoreboard/lifecycle/blueprint writes; no AUTH-5; no daemon;
  no production data; no external services.

---

## 15. Future Work (named, NOT authorized here)

- **`MMI_CRYPTOGRAPHIC_SIGNING_CONTRACT`** (proposed) — replace the typed-name §11 label with a
  real digital signature (e.g. Ed25519/ECDSA over a content hash; private key only Matt holds;
  public-key distribution to verifiers). This is what would extend the framework from
  drift-defense (Threat A) to forgery-defense (Threat B). Unscoped, unauthorized, separate §11.
- Tiers 5–7 builds, each a separate authorization.

---

## 16. Matt §11 Signature Block

```
§11 SIGN-OFF — MMI_GOVERNANCE_INVARIANTS_TESTING_FRAMEWORK_CONTRACT

I, Matt Nichol, have reviewed this governance invariants testing framework contract draft.

[x] I approve this contract as written.
[x] I authorize gate (Codex pre-build review) of this contract — completed clean 0/0.
[x] On clean gate, I §11-sign and authorize the BUILD OF LANE 1 ONLY
    (MMI_AUTHORITY_ESCALATION_PROBE_MODE_A).

Confirmed: the nine foundational laws (Section 2) are correct as written.
[x] yes

Confirmed: I understand and accept the honest-scope limitation (LAW 9 / Section 2.8) —
this framework defends against accidental drift, NOT malicious signature forgery, because
the §11 signature is currently a non-cryptographic typed label. Cryptographic signing is a
separate future contract. No forgery-resistance is claimed.
[x] yes

Confirmed: detect-not-enact; harness holds no authority; static-only (no live execution);
dual-engine is a fixture test, not a live runtime gate; Lane 1 first; Lanes 2-3 specced;
Tiers 5-7 design-only; Tier 6 offline fixtures only; PM Voice deterministic safe-failure.
[x] yes

Authority state-model + surface fixtures reconciled against repo:
[x] yes (Cursor reconcile MMI-DEC-083 — pre-§11 implementation record only)  [ ] pending

Reconciliation surfaces locked in `tests/fixtures/mmi_authority_escalation/`:
dispatcher ALL_CLEAR routing summary, PM Voice regular-lane feedstock relay, plus
Mode A advisory/signature/role/pm_voice/verdict fixtures from contract §6.10.
Matt §11 signature below remains operator-only.

> Matt Nichol June 21st 2026
```

---

## 17. Non-Authority Footer

```
§11 SIGNED (MMI-DEC-092). Authorizes Lane 1 (MMI_AUTHORITY_ESCALATION_PROBE_MODE_A) only;
Lane 1 Mode A probe already on disk (MMI-DEC-082). Lanes 2-3, Tiers 5-7, crypto-signing,
registry/default dispatch, production runtime gate, and AUTH-5 remain blocked without
separate operator authorization. Detect, never enact. LAW 9 honest-scope: drift-defense,
not forgery-defense.
```
