# Mutant Monkey Inbox Shield — Mode Controller Adversarial Test Suite Contract

**Status:** SIGNED — §11 authorized for build
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Source:** Gemini adversarial red-team — 29 attack vectors, June 14 2026
**Component under test:** Mode Controller #92 (GATED 95 ELITE, hash 85b455f)
**Core attack surface:** State confusion — wrong mode, stale mode, spoofed mode, replayed mode, mode changed after validation, output falsely claiming mode validation

---

## §11 Signature Block

```
Signed: Matt Nichol
Name:   Matt Nichol
Date:   June 14th 2026
Authority: Sole signing authority — Mutant Monkey Inbox Shield
```

---

## Governing Rule

Every test must be able to fail. A test that cannot produce a failure against a deliberately weakened Mode Controller is not a test — it is a rubber stamp and must be rewritten.

The Mode Controller's failure mode is not a crash. It is silent state confusion — the organism believes it is in NORMAL when it is in DEGRADED, believes a mode transition is validated when it was spoofed, or believes a validation passed when the validator was bypassed. Every test in this suite targets that failure class.

---

## Test Family 1 — Mode-Label Injection

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| MC-ADV-1-01 | Inject hidden carriage returns or Unicode control characters inside mode label parameters | Label rejected; violation logged | CRITICAL |
| MC-ADV-1-02 | Inject `MODE: PRODUCTION` string inside a `MODE: RESEARCH` context payload body | Mode state unchanged; injection detected and logged | CRITICAL |
| MC-ADV-1-03 | Shift raw execution arguments into `feature_name`, `metadata`, or `debug` schema fields | Fields inspected regardless of declared type; injection blocked | HIGH |
| MC-ADV-1-04 | Submit mode label with trailing whitespace, null bytes, or zero-width characters | Label rejected or normalized; never silently accepted | HIGH |
| MC-ADV-1-05 | Submit mode label in alternate encoding — Unicode homoglyph, base64, URL-encoded | Label rejected; encoding evasion detected | HIGH |

---

## Test Family 2 — Authorization Replay and Token Binding

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| MC-ADV-2-01 | Replay signed authorization token from high-clearance lane against low-clearance task | Token rejected; clearance mismatch logged | CRITICAL |
| MC-ADV-2-02 | Replay valid token against different payload — token not bound to payload hash | Token rejected; payload hash mismatch detected | CRITICAL |
| MC-ADV-2-03 | Replay valid token outside its timestamp window | Token rejected; expiry enforced | HIGH |
| MC-ADV-2-04 | Forge validation signature output artifact claiming mode validation occurred | Forged artifact rejected; verification requires origin proof | CRITICAL |
| MC-ADV-2-05 | Clone cryptographic approval hash from previous valid state transition and apply to new transition | Hash rejected; epoch or payload mismatch detected | CRITICAL |

---

## Test Family 3 — Route Override and Agent Assignment Injection

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| MC-ADV-3-01 | Inject `ASSIGNED_TO: ChatGPT` or equivalent routing directive inside unstructured payload body | Routing directive in payload body ignored; system routing variables not overwritten | CRITICAL |
| MC-ADV-3-02 | Inject routing parameters inside `summary`, `reason`, or `explanation` fields | Routing parameters in non-routing fields rejected | HIGH |
| MC-ADV-3-03 | Spoof internal namespace header to claim elevated routing privilege | Namespace claim rejected; directory context does not grant routing authority | HIGH |
| MC-ADV-3-04 | Mimic system directory structure to trigger permissive safety boundary | Directory-based privilege escalation blocked | HIGH |
| MC-ADV-3-05 | Wrap unsafe operational command inside allowlisted system call type | Command body inspected regardless of wrapper type; unsafe command rejected | HIGH |

---

## Test Family 4 — State-Transition Race Conditions

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| MC-ADV-4-01 | Flood mode-switch frames during cold start or system warmup | Mode transitions blocked until initialization complete | CRITICAL |
| MC-ADV-4-02 | Flood mode-switch frames during configuration reload | Stale config window does not permit mode transition | CRITICAL |
| MC-ADV-4-03 | Flood mode-switch frames during leader election | Leader election window produces no unauthorized mode transitions | CRITICAL |
| MC-ADV-4-04 | Trigger boundary violation write to audit log while concurrent queue dispatches payload before cancellation propagates | Dispatch blocked until violation resolution confirmed | CRITICAL |
| MC-ADV-4-05 | Push high-volume payloads into queues before mode-switch evaluation resolves | Pre-evaluation payloads held; not dispatched until mode state confirmed | HIGH |
| MC-ADV-4-06 | Pass mutable object pointer to Mode Controller; mutate memory address after validation but before serialization | Object immutable after validation entry; mutation detected or serialization uses validated snapshot | CRITICAL |

---

## Test Family 5 — Canonicalization Mismatch

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| MC-ADV-5-01 | Structure command to parse safe under canonical form but transform into different instruction under downstream serializer | Downstream serialization verified against validated canonical form before execution | CRITICAL |
| MC-ADV-5-02 | Alter system clock offset or skew event timestamps to bypass freshness checks | Timestamp skew detected; stale or future-dated transitions rejected | HIGH |
| MC-ADV-5-03 | Alter or truncate `source_lineage_id` to make isolated lane data look like global stream | Lineage manipulation detected; isolated data not promoted to global stream | HIGH |
| MC-ADV-5-04 | Validate payload under old policy version while claiming current authority on broadcast | Policy version verified at execution point; version mismatch rejected | HIGH |
| MC-ADV-5-05 | Exploit configuration delivery asymmetry — stale policy on one node while monitoring reads clean config from another | Single-node stale config does not authorize mode transition across system | HIGH |

---

## Test Family 6 — Breaker and Validator Fail-Closed

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| MC-ADV-6-01 | Introduce latency spikes or resource starvation targeting independent validation breaker | Breaker timeout treated as deny — not fail-open | CRITICAL |
| MC-ADV-6-02 | Target consensus microservice with starvation to verify fail-open fallback | No fail-open path exists; starvation forces safe-stop or deny | CRITICAL |
| MC-ADV-6-03 | Exploit shared logical dependency between Mode Controller and security gate — trigger exception causing both to clear state simultaneously | Shared dependency failure does not produce open state; both failing = deny | CRITICAL |
| MC-ADV-6-04 | Induce hard validation exception to trigger error-handling fallback | Error-handling block does not default to allow; exception treated as deny | CRITICAL |
| MC-ADV-6-05 | Target cluster node with stale policy while monitoring reads clean config | Stale-policy node does not execute mode transitions independently | HIGH |

---

## Test Family 7 — Manual Override Spoofing

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| MC-ADV-7-01 | Construct transaction metadata block mimicking operator-approved bypass signature | Forged bypass rejected; verification requires origin proof from Matt Nichol identity | CRITICAL |
| MC-ADV-7-02 | Replay previous genuine operator override against different state transition | Override not reusable; bound to specific transition instance | CRITICAL |
| MC-ADV-7-03 | Submit override without separation-of-duties compliance | Override rejected; SoD failure logged | CRITICAL |
| MC-ADV-7-04 | Submit override with valid signature but expired timestamp | Override rejected; timestamp enforced | HIGH |

---

## Test Family 8 — Log Silence and Fake-Pass Detection

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| MC-ADV-8-01 | Block, drop, or silence error outputs and security metrics | Absence of validation record treated as deny, not pass | CRITICAL |
| MC-ADV-8-02 | Flood low-severity notifications until critical breach alerts are rate-limited or dropped | Critical mode transition alerts exempt from rate limiting | CRITICAL |
| MC-ADV-8-03 | Craft fake verification event claiming autonomous check completed | Fake event does not authorize state transition | CRITICAL |
| MC-ADV-8-04 | Write fake audit entries claiming validation occurred | Fake entries detected via chain validation | HIGH |
| MC-ADV-8-05 | Delete audit entries showing mode transition denial | Deletion detected via broken chain | HIGH |
| MC-ADV-8-06 | Use linguistic framing or multi-layered conversational context to collapse strict instruction boundaries | Mode Controller not subject to natural language context collapse; state machine logic is deterministic | CRITICAL |

---

## Test Family 9 — Side-Channel and Transport Leakage

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| MC-ADV-9-01 | Force private restricted variables into transport headers, trace IDs, proxy parameters, or routing keys | Transport metadata sanitized; restricted variables not permitted outside payload | HIGH |
| MC-ADV-9-02 | Inject raw variables into distributed tracing metrics, monitoring spans, or external exception tags | Observability tooling sanitized before export | HIGH |
| MC-ADV-9-03 | Force private operational variables into shared cache tables, storage paths, or temp directory filenames | Shared resources sanitized; mode variables not exposed globally | HIGH |
| MC-ADV-9-04 | Sanitize top-level fields while leaving debugger tracebacks or environment variables visible in nested arrays | All nested fields inspected; tracebacks and env vars not exposed | HIGH |

---

## Test Family 10 — Direct Broker Bypass and Infrastructure Attacks

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| MC-ADV-10-01 | Use stolen internal API keys to write commands directly onto pipeline topics bypassing Mode Controller | Broker ACLs prevent direct publish without Mode Controller routing | CRITICAL |
| MC-ADV-10-02 | Swap live mode security component for mock test fixture during update cycle | CI verifies production path against real components; mock substitution detected | CRITICAL |
| MC-ADV-10-03 | Ship build where tests pass against mock Mode Controller but production uses different path | Production path verified in CI against real Mode Controller | CRITICAL |
| MC-ADV-10-04 | Deploy worker with Mode Controller disabled, in permissive mode, or pointed at mock validator | Deployment validation rejects permissive configuration | CRITICAL |
| MC-ADV-10-05 | Route production mode transitions through staging/dev environment with weaker enforcement | Environment separation enforced; production transitions cannot use non-production paths | HIGH |

---

## Failure Severity Definitions

| Severity | Meaning | Required action |
|---|---|---|
| CRITICAL | Mode Controller can be put in wrong state, bypassed, or silenced | Full stop — patch before any other build proceeds |
| HIGH | Leakage or partial bypass possible but organism mode state not directly compromised | Patch before hardened status granted |

---

## Gate Requirement

```
All 10 test families: 0 failures
Every test ID above: executed and logged
No test skipped without signed waiver from Matt Nichol
CRITICAL failures: full stop — patch immediately
HIGH failures: patch before hardened status granted
```

Mode Controller #92 is ADVERSARIALLY HARDENED only when all families pass 0/0.

---

## Non-Authorizations

- This contract authorizes Cursor to implement the adversarial test suite only.
- This contract does not authorize build of new Mode Controller features.
- This contract does not amend the Mode Controller #92 signed contract.
- Signing this contract authorizes Cursor to build tests that intentionally attempt to put the Mode Controller in wrong, stale, spoofed, or bypassed state — find real vulnerabilities — and report them for patching.
