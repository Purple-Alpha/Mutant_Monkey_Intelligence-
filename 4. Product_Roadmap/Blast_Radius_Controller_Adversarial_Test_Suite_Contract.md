# Mutant Monkey Inbox Shield — Blast Radius Controller Adversarial Test Suite Contract

**Status:** SIGNED — §11 authorized for build
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Source:** Gemini adversarial red-team — 12 test families, June 14 2026
**Component under test:** Blast Radius Controller #89 (GATED 95 ELITE, hash f1c817e)
**Core attack surface:** The BRC is the execution spine — the gateway every control-plane action must pass through in order: identity → ring → budget → breaker → mode → dispatch → telemetry. Bypassing or corrupting any gate means uncontained dispatch. Every test targets that lifecycle.

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

Every test must be able to fail. A test that cannot produce a failure against a deliberately weakened BRC is not a test — it is a rubber stamp and must be rewritten.

The BRC's failure mode is not a crash. It is silent gateway bypass — an agent dispatches without passing all lifecycle steps, a budget is crossed without authorization, a ring advances without verified promotion, or telemetry is forged to hide the breach. Every test targets that failure class.

---

## Test Family 1 — Identity Spoofing

**Target:** `AgentIdentityGateway` (Gate 5)

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| BRC-ADV-1-01 | Submit request with identity token from a different agent type | Gateway rejects; token signature must cryptographically match explicit agent type registration | CRITICAL |
| BRC-ADV-1-02 | Emulate high-privilege agent context using low-privilege credentials | Gateway rejects regardless of payload validity | CRITICAL |
| BRC-ADV-1-03 | Submit request with valid token from a decommissioned agent identity | Decommissioned identity rejected; registration state checked before acceptance | CRITICAL |
| BRC-ADV-1-04 | Forge agent identity header to claim gateway PID signing authority | PID signature verification rejects forged claim | CRITICAL |

---

## Test Family 2 — Budget Isolation

**Target:** `SessionBudgetStore` (Gate 1)

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| BRC-ADV-2-01 | Spoof sub-budget approval flag to cross-borrow tokens from another voter's allocation | Cross-voter allocation change rejected without verifiable encrypted controller signature | CRITICAL |
| BRC-ADV-2-02 | Systematically deplete single voter's 50K sub-budget to fracture ensemble | Depletion produces `incomplete_budget_exhausted` status immediately | HIGH |
| BRC-ADV-2-03 | Attempt pre-dispatch without locking maximum possible token fee against session budget | Dispatch blocked until maximum token fee locked against budget | CRITICAL |
| BRC-ADV-2-04 | Submit parallel requests to race token exhaustion against downstream dispatch execution | Pre-dispatch decrement atomic — race condition produces budget lock, not double-spend | CRITICAL |

---

## Test Family 3 — Queue and Tenant Isolation

**Target:** `TenantSegmentationController` (Gate 2)

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| BRC-ADV-3-01 | Inject non-alphanumeric delimiter characters into `tenant_id` routing key | Hard fault handler triggered; request dropped | CRITICAL |
| BRC-ADV-3-02 | Inject Unicode control characters or null bytes into `tenant_id` | Ingress tokenization validation rejects; never silently normalized | CRITICAL |
| BRC-ADV-3-03 | Submit `tenant_id` with embedded SQL injection or path traversal characters | Characters rejected at ingress — not sanitized-and-passed | HIGH |
| BRC-ADV-3-04 | Attempt routing key collision between two tenants sharing a domain prefix | Collision detected; tenants not merged through shared prefix match | HIGH |

---

## Test Family 4 — Epoch Replay

**Target:** Mode Controller Interface (Gate 4)

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| BRC-ADV-4-01 | Replay stale validation packet with outdated epoch counter | Stale epoch triggers immediate fallback to ISOLATED mode | CRITICAL |
| BRC-ADV-4-02 | Submit mode configuration from a previous epoch as if current | Epoch counter verified monotonically — out-of-sequence counter rejected | CRITICAL |
| BRC-ADV-4-03 | Replay valid packet within same epoch but after state has advanced | Epoch counter and state hash both verified — packet rejected if state hash mismatch | HIGH |
| BRC-ADV-4-04 | Skew system clock to make stale packet appear fresh | Timestamp skew detected; epoch counter verification does not rely on clock alone | HIGH |

---

## Test Family 5 — Loop Evasion

**Target:** `LoopDetector` (Gate 1)

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| BRC-ADV-5-01 | Add trailing whitespace or metadata noise to arguments before hashing | Arguments canonicalized before hash — metadata stripped, keys alphabetized, string minified | HIGH |
| BRC-ADV-5-02 | Add semantically identical but structurally different argument to evade hash match | Canonical form comparison catches semantic equivalence | HIGH |
| BRC-ADV-5-03 | Execute recursive calls with microsecond delays to evade sliding window detection | Sliding window detection not defeatable by delay alone | HIGH |
| BRC-ADV-5-04 | Insert benign intermediate call between recursive calls to break loop detection chain | Loop detection tracks argument hash across non-consecutive calls within window | HIGH |

---

## Test Family 6 — Breaker Recovery Exploitation

**Target:** `BreakerStore` (Gate 1)

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| BRC-ADV-6-01 | Execute resource spike inside transient cooldown window | Secondary trip within 10-minute sliding window enforces sustained 5-minute lockout | HIGH |
| BRC-ADV-6-02 | Time resource spikes to hit exactly at cooldown window boundary | Boundary condition treated as within window | HIGH |
| BRC-ADV-6-03 | Cause breaker timeout and verify fail-open vs fail-closed behavior | Breaker timeout treated as sustained trip — not recovered state | CRITICAL |
| BRC-ADV-6-04 | Replay old `breaker_pass` state decision during cooldown window | Breaker pass not replayable — state freshness verified | HIGH |

---

## Test Family 7 — Privacy Filter Interface Fail-Closed

**Target:** `PrivacyFilterInterface` (Gate 2)

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| BRC-ADV-7-01 | Sever async connection link between gateway interface and Privacy Filter | Interface breaker snaps to OPEN within 50ms of link lag | CRITICAL |
| BRC-ADV-7-02 | Cause Privacy Filter to become unavailable without triggering gateway-side alert | Continuous active echo/heartbeat detects unavailability | CRITICAL |
| BRC-ADV-7-03 | Slow Privacy Filter response to just under 50ms threshold | 50ms threshold enforced strictly — just-under responses accumulate toward trip | HIGH |
| BRC-ADV-7-04 | Spoof Privacy Filter heartbeat while filter is actually unavailable | Heartbeat requires challenge-response — spoofed static heartbeat rejected | CRITICAL |

---

## Test Family 8 — Budget Exhaustion Race Hardening

**Target:** `SessionBudgetStore` (Gate 1)

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| BRC-ADV-8-01 | Flood parallel requests to exhaust budget while dispatch is in flight | Pre-dispatch decrement atomic — in-flight dispatch does not consume unlocked budget | CRITICAL |
| BRC-ADV-8-02 | Submit burst of requests timed to hit budget check simultaneously | Concurrent budget checks serialized — no double-spend possible | CRITICAL |
| BRC-ADV-8-03 | Exhaust budget via low-cost requests then submit high-cost request before exhaustion propagates | Budget exhaustion propagates before any subsequent request accepted | HIGH |

---

## Test Family 9 — Component Bypass via Unmonitored Paths

**Target:** `GatewayController` (The Spine)

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| BRC-ADV-9-01 | Route agent-to-agent invocation via memory-mapped file store bypassing gateway | Memory boundary isolation enforced — calling process environment validated against gateway PID | CRITICAL |
| BRC-ADV-9-02 | Fork thread to invoke tool directly without passing through gateway lifecycle | Thread fork tool invocation rejected — entry point not signed by gateway PID fails | CRITICAL |
| BRC-ADV-9-03 | Attempt direct tool invocation via internal API without gateway routing | All tool invocations require gateway PID signature | CRITICAL |
| BRC-ADV-9-04 | Use inter-process communication channel to bypass gateway identity check | IPC channel subject to same identity verification as API channel | CRITICAL |

---

## Test Family 10 — Ring Promotion Integrity

**Target:** `RingController` (Gate 3)

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| BRC-ADV-10-01 | Poison external baseline repository to make failed tests appear to pass | RingController independently queries verification log files and matches cryptographic hash of test corpus | CRITICAL |
| BRC-ADV-10-02 | Spoof regression results to force ring advancement without genuine test pass | Out-of-band double-entry verification — spoofed results do not match independent log hash | CRITICAL |
| BRC-ADV-10-03 | Advance ring by submitting partial test corpus that passes hash check on subset only | Hash verification covers full corpus — partial corpus hash mismatch detected | CRITICAL |
| BRC-ADV-10-04 | Replay previous valid ring advancement for different component | Ring advancement bound to specific component identity and epoch | HIGH |

---

## Test Family 11 — Ledger and Audit Integrity

**Target:** `BreakerStore` Auditing

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| BRC-ADV-11-01 | Flood transaction state changes to trigger log compaction that erases historical entries | Breaker state transitions duplicated to isolated append-only security log outside standard rotation | HIGH |
| BRC-ADV-11-02 | Trigger log rotation during active breaker state transition | Transition write confirmed to append-only log before rotation permitted | HIGH |
| BRC-ADV-11-03 | Delete or modify entries in standard audit log | Deletion detected via append-only log chain comparison | HIGH |
| BRC-ADV-11-04 | Fill audit log storage to force emergency compaction | Storage pressure does not trigger compaction of append-only security log | HIGH |

---

## Test Family 12 — Telemetry Forgery

**Target:** Control Plane Observability

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| BRC-ADV-12-01 | Inject cloned heartbeat execution frames to hide gate failures | Cryptographic heartbeats contain rolling challenge-response derived from gateway's changing memory state — cloned frames rejected | CRITICAL |
| BRC-ADV-12-02 | Replay previous valid telemetry signal to mask current failure state | Rolling challenge-response not replayable | CRITICAL |
| BRC-ADV-12-03 | Suppress telemetry output entirely while gateway continues operating | Absence of telemetry signal treated as gate failure | CRITICAL |
| BRC-ADV-12-04 | Flood telemetry with low-severity events to hide high-severity gate failure | High-severity gate failure events exempt from rate limiting and flooding suppression | CRITICAL |

---

## Failure Severity Definitions

| Severity | Meaning | Required action |
|---|---|---|
| CRITICAL | Gateway lifecycle can be bypassed, skipped, or spoofed — uncontained dispatch possible | Full stop — patch before any other build proceeds |
| HIGH | Audit integrity, budget isolation, or loop detection degraded but core lifecycle not directly bypassed | Patch before hardened status granted |

---

## Gate Requirement

```
All 12 test families: 0 failures
Every test ID above: executed and logged
No test skipped without signed waiver from Matt Nichol
CRITICAL failures: full stop — patch immediately
HIGH failures: patch before hardened status granted
```

Blast Radius Controller #89 is ADVERSARIALLY HARDENED only when all families pass 0/0.

---

## Non-Authorizations

- This contract authorizes Cursor to implement the adversarial test suite only.
- This contract does not authorize changes to gateway lifecycle, ring definitions, or budget structure.
- This contract does not amend the Blast Radius Controller #89 signed contract.
- Signing this contract authorizes Cursor to build tests that intentionally attempt to bypass, spoof, or exhaust the BRC gateway lifecycle — find real vulnerabilities — and report them for patching.
