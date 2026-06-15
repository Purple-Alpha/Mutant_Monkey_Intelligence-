# Mutant Monkey Inbox Shield — ReconciliationAgent Adversarial Test Suite Contract

**Status:** SIGNED — §11 authorized for build
**Date:** June 14 2026
**Authority:** Matt Nichol — sole signing authority
**Source:** Gemini adversarial red-team — 23 attack vectors, June 14 2026
**Component under test:** ReconciliationAgent #88 (GATED 88 ELITE, hash 1b2ac0c)
**Core attack surface:** The ReconciliationAgent is the sole verdict producer. Compromising it does not produce one bad alert — it corrupts the organism's entire trust chain. Every test in this suite targets that fact.

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

Every test must be able to fail. A test that cannot produce a failure against a deliberately weakened ReconciliationAgent is not a test — it is a rubber stamp and must be rewritten.

The ReconciliationAgent's failure mode is not a crash. It is a corrupted verdict that appears legitimate — a CLEAR verdict produced from poisoned evidence, a CRITICAL verdict suppressed through voter manipulation, or a cross-tenant verdict routed to the wrong operator. Every test targets that failure class.

---

## Test Family 1 — Blackboard Trust Boundary

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| RA-ADV-1-01 | Inject fake Layer 1 detection agent contributions directly into blackboard | Injected contributions rejected; provenance validation required before voter consumption | CRITICAL |
| RA-ADV-1-02 | Feed highly malformed or partially truncated Layer 1 data structures into verification pipeline | Error handling returns safe error state — not unintended verdict or open state | CRITICAL |
| RA-ADV-1-03 | Wrap explicit threat vector entirely inside `zero_day_candidate` identifier to route away from primary verdict path | Zero-day referral does not suppress evidence from primary verdict | HIGH |
| RA-ADV-1-04 | Mask critical fraud pattern inside layout that triggers only `spam_signal_only` ImageClassifier #83 | Spam-only classification does not route active fraud pattern down benign DELIVERY_PROBLEM track | HIGH |
| RA-ADV-1-05 | Manipulate Layer 0 threat-intel briefings consumed by R2 Pattern Match Voter so live malicious indicators no longer match known profiles | Baseline pattern poisoning detected — R2 voter confidence degraded, not silently trusted | CRITICAL |

---

## Test Family 2 — Tenant Isolation and Join-Key Collision

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| RA-ADV-2-01 | Submit payload where `email_id` belongs to Tenant A but Layer 1 contributions contain metadata from Tenant B | Cross-tenant contribution rejected; tenant isolation enforced at blackboard query level | CRITICAL |
| RA-ADV-2-02 | Manipulate `sender_domain` join key to cross-reference unrelated tenant evidence streams | Join key collision detected; unrelated tenant evidence not merged into verdict | CRITICAL |
| RA-ADV-2-03 | Intercept finalized output object and swap `tenant_id` at serialization boundary | Tenant ID swap detected; output tenant_id verified against input tenant_id before write | CRITICAL |
| RA-ADV-2-04 | Introduce `email_id` collision across two tenants with same domain to force shared blackboard read | Same-domain collision does not produce cross-tenant evidence merge | HIGH |

---

## Test Family 3 — Voter Independence

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| RA-ADV-3-01 | Exploit shared local variables, global state caches, or parallel threads to let R1 view R2 or R3 tentative choices before votes are locked | Voter isolation enforced — no voter reads another voter's intermediate state | CRITICAL |
| RA-ADV-3-02 | Exploit shared thread context to let R2 pattern match voter observe R1 signal weight calculation before R2 vote is cast | R2 vote produced independently of R1 result | CRITICAL |
| RA-ADV-3-03 | Modify Layer 1 contribution in memory or on blackboard during microsecond window between individual voter query and collective vote aggregation | Blackboard snapshot taken before voter queries begin — mid-deliberation writes do not affect outcome | CRITICAL |
| RA-ADV-3-04 | Bridge input channels so user-influenced threat variables reach R1 directly, violating P4-D4 | User-influenced variables blocked from R1 input path | HIGH |

---

## Test Family 4 — 2-of-3 Consensus Manipulation

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| RA-ADV-4-01 | Inflate R1 confidence inputs to guarantee R1 vote, then pair with R2 pattern poisoning to manufacture false 2-of-3 majority | Coordinated multi-voter manipulation detected via confidence anomaly scoring — verdict flagged for review | CRITICAL |
| RA-ADV-4-02 | Design adversarial payload that appeals perfectly to R1 numbers, conflicts with R2 pattern logic, and baffles R3 history correlation — forcing perpetual 3-way split | Perpetual ESCALATE state is logged and operator-notified — not silently looped | HIGH |
| RA-ADV-4-03 | Exploit 1:1:1 equal weight structure by compromising R1 and R2 to mathematically neutralize R3 conflict logic | Two-voter compromise produces ESCALATE or flagged verdict — not clean CLEAR | CRITICAL |
| RA-ADV-4-04 | Trigger processing lag on blackboard to route or read verdict downstream before ensemble completes 2-of-3 resolution | Verdict not written or consumed until ensemble resolution is confirmed complete | CRITICAL |

---

## Test Family 5 — ESCALATE and CIRT Routing

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| RA-ADV-5-01 | Target window after tenant onboarding or personnel change where `cirt_individual` string is blank or stale | Blank or stale CIRT identifier caught before ESCALATE routes — operator notified, not silently dropped | CRITICAL |
| RA-ADV-5-02 | Force ESCALATE state with unmonitored `cirt_individual` to verify if escalation stalls silently | Silent stall not permitted — ESCALATE with undeliverable CIRT target triggers secondary alert path | CRITICAL |
| RA-ADV-5-03 | Submit payload engineered to loop in ESCALATE indefinitely without resolution | ESCALATE loop detected after defined timeout — operator intervention required, not infinite loop | HIGH |

---

## Test Family 6 — Lung Integration Fail-Closed

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| RA-ADV-6-01 | Withhold high-risk signals to keep engine at MEDIUM_RISK while causing Lung to fail to transmit Deep Breath state | Lung transmission failure treated as lockdown-required — not as MEDIUM_RISK confirmation | CRITICAL |
| RA-ADV-6-02 | Suppress `lockdown_applied` boolean flag in output payload while P4-D3 automatic upgrade is executing | Lockdown state verified at output write — suppressed flag detected as mismatch | CRITICAL |
| RA-ADV-6-03 | Cause Lung module unavailability during HIGH_RISK verdict | Lung unavailability does not suppress lockdown — fail-closed behavior required | CRITICAL |

---

## Test Family 7 — Verdict Enum Serialization

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| RA-ADV-7-01 | Craft output dictionary payload where illegal verdict value is masqueraded inside un-vetted object property | Illegal verdict value rejected at serialization; closed enum enforced | HIGH |
| RA-ADV-7-02 | Submit verdict object with correct top-level enum but illegal nested state in supporting fields | All supporting fields validated against schema — not top-level only | HIGH |
| RA-ADV-7-03 | Exploit dynamic typing to coerce string verdict into numeric or boolean representation that bypasses enum check | Type coercion detected; verdict value must match exact enum member | HIGH |

---

## Test Family 8 — Operator Narrative Integrity

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| RA-ADV-8-01 | Influence upstream text extraction to force specific reassuring strings into `plain_english_chain` while structural verdict records threat indicator | Narrative generated from verified evidence chain only — not from raw upstream text | HIGH |
| RA-ADV-8-02 | Submit evidence that produces CLEAR verdict with narrative that describes threat behavior | Narrative-verdict mismatch detected — operator flagged | HIGH |
| RA-ADV-8-03 | Inject contradictory evidence that produces accurate narrative but incorrect verdict enum | Narrative-verdict consistency verified before output write | HIGH |

---

## Test Family 9 — Minority Opinion Preservation

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| RA-ADV-9-01 | Target logging pipeline during 2-of-3 split to drop or strip `minority_opinion` string | Minority opinion write is atomic with verdict write — cannot be dropped independently | HIGH |
| RA-ADV-9-02 | Submit unanimous verdict payload that actually had internal voter disagreement resolved before logging | Voter-level disagreement logged before aggregation — post-aggregation unanimity does not erase pre-aggregation dissent | HIGH |
| RA-ADV-9-03 | Force log rotation or compaction during minority opinion write | Minority opinion write confirmed before log rotation permitted | HIGH |

---

## Test Family 10 — Mock vs Live Integration Truth

| Test ID | Attack | Expected safe behavior | Failure severity |
|---|---|---|---|
| RA-ADV-10-01 | Pass mock validation structures through deferred Class 3 xfail states to fool `verify_build_truth.py` into reporting ELITE 85+ health score | Mock structures cannot produce live health score — deferred integrations scored separately | CRITICAL |
| RA-ADV-10-02 | Induce massive validation faults across unrelated files to fill `audit_outputs/pending/` and hide unauthorized cross-tenant ledger modification | Audit output flooding detected — pending directory size monitored, anomalous growth triggers alert | HIGH |
| RA-ADV-10-03 | Use xfail test markers to mask a genuine failing test as an expected failure | xfail markers verified against signed contract — unmarked xfails are build failures | HIGH |
| RA-ADV-10-04 | Submit build where Lung and CIRT integrations pass in mock but are not wired in production | Production integration verified in CI — mock pass does not satisfy live gate | CRITICAL |

---

## Failure Severity Definitions

| Severity | Meaning | Required action |
|---|---|---|
| CRITICAL | Verdict can be corrupted, tenant isolation broken, or sole authority bypassed | Full stop — patch before any other build proceeds |
| HIGH | Audit integrity, operator visibility, or enum safety compromised but core verdict not directly corrupted | Patch before hardened status granted |

---

## Gate Requirement

```
All 10 test families: 0 failures
Every test ID above: executed and logged
No test skipped without signed waiver from Matt Nichol
CRITICAL failures: full stop — patch immediately
HIGH failures: patch before hardened status granted
```

ReconciliationAgent #88 is ADVERSARIALLY HARDENED only when all families pass 0/0.

---

## Non-Authorizations

- This contract authorizes Cursor to implement the adversarial test suite only.
- This contract does not authorize changes to verdict logic, voter weights, or CIRT routing.
- This contract does not amend the Phase 4 ReconciliationAgent signed contract.
- Signing this contract authorizes Cursor to build tests that intentionally attempt to corrupt, bypass, or spoof ReconciliationAgent verdicts — find real vulnerabilities — and report them for patching.
