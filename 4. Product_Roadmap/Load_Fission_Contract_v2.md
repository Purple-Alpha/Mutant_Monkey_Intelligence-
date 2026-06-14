# Load Fission Contract v2

**Status:** SIGNED — Matt Nichol June 13th 2026.
**Product surface:** Mutant Monkey Inbox Shield.
**Authority:** This draft authorizes no code, no deployment, no policy change, no scoreboard status change, and no production fission behavior until Matt signs §11.
**Relationship to prior contract:** This v2 draft is a proposed supersession of `Load_Fission_Contract.md`. Local repo evidence currently shows scoreboard row #90 as `GATED`, not `SIGNED_UNBUILT`; if Matt signs this v2 contract, it supersedes the prior Load Fission contract going forward without rewriting the historical gate record.

---

## §1 Purpose

This contract governs **elastic horizontal scaling fission only** for Mutant Monkey Inbox Shield.

Load Fission exists to scale a known parent agent under non-semantic load pressure. A load-fission child is an exact copy of the parent type. It creates no new agent type, no new capability, no new tool class, and no new authority surface.

This contract is defensive architecture only. It creates bounded, auditable, reversible scaling behavior for a governed security system.

---

## §2 Scope

### §2.1 In Scope

- Watcher-triggered load fission.
- Exact-copy child creation for existing governed parent agent types.
- Separate child namespaces for proposed evidence only.
- Spawn decision records, lifecycle logs, and forensic correlation.
- Runtime policy-as-code evaluation by the control plane.
- Fission fallback mode for incident conditions.

### §2.2 Out Of Scope

- Any self-spawn by an agent.
- Any child that can fission again.
- Any net-new agent type.
- Any new tool, connector, credential, or capability.
- Any semantic fission trigger based on email content.
- Any ReconciliationAgent fission.
- Any autonomous fraud decision, allow/block decision, or client-facing claim.

---

## §3 Locked Design Decisions

| ID | Decision |
|---|---|
| LF2-D1 | **Watcher-triggered only.** Agents never self-spawn. A load-fission event must originate from a governed watcher signal. |
| LF2-D2 | **Max depth is one generation.** A child cannot fission again without Matt sign-off. |
| LF2-D3 | **Exact-copy children only.** Children are copies of the parent agent type; no new agent types, new capabilities, or new tools are permitted. |
| LF2-D4 | **Separate namespace only.** Children write to separate namespaces as proposed evidence only. |
| LF2-D5 | **ReconciliationAgent prohibition.** ReconciliationAgent is explicitly prohibited from fissioning. This is a named contract clause, not an assumption. |
| LF2-D6 | **Non-semantic triggers only.** Load fission triggers are queue depth, latency, and throughput only. No email content may influence a load fission trigger. |
| LF2-D7 | **Permission intersection model.** A child's effective permissions are the intersection of the parent rights and the child configured capabilities. They are never a superset. |
| LF2-D8 | **Fresh identity per child.** Each child receives fresh identity. Credentials are never inherited. There is no trust by ancestry. |
| LF2-D9 | **Graceful degradation on quota breach.** Fission is denied, parent continues without child, and degradation is logged. |
| LF2-D10 | **Policy-as-code required.** Fission policy is versioned, immutable, and evaluated by the control plane at runtime. Policy is not embedded in agents. |
| LF2-D11 | **Budget exhaustion is not success.** Exhaustion produces `incomplete_budget_exhausted`, not a normal pass. No reconciliation decision may be made from exhausted output. |
| LF2-D12 | **ELITE target.** Any v2 implementation must score ELITE 85+ on the applicable health rubric before closure. |

---

## §4 Required Governance Artifacts Per Spawn

Every spawn must create the following append-only records before the child can act:

### §4.1 Spawn Decision Record

Required fields:

- `parent_workflow_id`
- `watcher_id`
- `trigger_condition`
- `policy_version`
- `child_agent_id`
- `tools_assigned`
- `namespace_assigned`
- `ttl`
- `timestamp`

### §4.2 Lifecycle Log

Required events:

- `start`
- `tool_usage`
- `evidence_write`
- `exhale`

### §4.3 Forensic Guarantee

All spawn and lifecycle records must be:

- append-only
- immutable
- correlated through `parent_workflow_id`
- attributable to the watcher, parent workflow, policy version, and child identity

---

## §5 Failure Mode Controls

### §5.1 Spawn Storm Prevention

Control requirements:

- per-tenant quotas
- global quotas
- circuit breakers
- graceful denial under quota pressure

### §5.2 Evidence Contamination Prevention

Control requirements:

- strict namespace isolation
- governed ingestion step before parent consumption
- no parent direct-read of child raw namespace

### §5.3 Audit Gap Prevention

Control requirements:

- mandatory lifecycle logging
- correlation IDs
- append-only event chain
- no unlogged spawn, tool use, evidence write, or exhale

### §5.4 Privilege Leakage Prevention

Control requirements:

- zero credential inheritance
- minimal toolsets
- fresh child identity
- permission intersection model

### §5.5 Governance Drift Prevention

Control requirements:

- policy-as-code
- immutable policy versions
- change control
- runtime policy evaluation by the control plane

---

## §6 Governed Ingestion Step

The parent may consume child evidence only through a governed ingestion pipeline. The parent cannot read the raw child namespace directly.

The ingestion pipeline must:

1. validate schema
2. validate size
3. validate provenance
4. tag the ingestion event
5. log the parent-child linkage
6. reject invalid or exhausted output

Child evidence remains proposed evidence until ingested through this pipeline.

---

## §7 Budget Exhaustion Rule

If a child or parent-child set exhausts budget, the output status must be:

```text
incomplete_budget_exhausted
```

Exhausted output cannot be treated as a normal pass. No reconciliation decision may be made from exhausted output.

---

## §8 Fission Fallback Mode

Mutant Monkey Inbox Shield must support operational disabling of load fission under incident conditions.

Fallback requirements:

- operator-visible load-fission disable switch
- policy version that records the disabled state
- denial logs for would-have-spawned events
- parent continues without child when feasible
- degraded status recorded when child absence affects completeness
- underwriter-facing documentation of the control and its audit evidence

This operational control is required for underwriter review.

---

## §9 Canadian Legal Alignment

This system produces evidence, not decisions.

Legal and buyer-facing boundaries:

- Human authority retains final decision power.
- Mutant Monkey Inbox Shield does not guarantee fraud prevention.
- Mutant Monkey Inbox Shield does not guarantee that every malicious email will be detected.
- Mutant Monkey Inbox Shield does not make autonomous client-facing financial decisions.
- The system produces audit evidence, proposed evidence, and control-plane records.
- Shared responsibility applies across operator, MSP, client, infrastructure provider, and software vendor roles.
- Audit log retention commitments must be documented before buyer-facing release.

### §9.1 Shared Responsibility Matrix

| Party | Responsibility |
|---|---|
| Operator | Approves policy changes, signs governed promotions, reviews incident posture. |
| MSP | Configures tenant posture, monitors operational alerts, validates client workflow fit. |
| Client | Maintains business process controls and final approval for sensitive financial actions. |
| Infrastructure provider | Provides underlying platform availability and account controls. |
| Mutant Monkey Inbox Shield | Produces governed evidence, audit logs, control records, and bounded recommendations. |

---

## §10 Underwriter Documentation Checklist

Before any underwriter-facing use, documentation must include:

- architecture diagram
- governance policy
- red team results
- evidence chain integrity guarantees
- spawn governance controls
- fission fallback mode
- audit log retention commitments
- policy-as-code versioning model
- lifecycle log schema
- governed ingestion step description

---

## §11 Adversarial Test Requirements

All tests below are Class 2 required tests for any v2 implementation.

### Test 1 - Privilege Escalation

Simulate a child attempting to:

- gain tools outside its assigned set
- impersonate the parent
- modify policy

Expected result: blocked and logged.

### Test 2 - Spawn Injection

Simulate malicious email content attempting to trigger load fission.

Expected result: fission triggers remain non-semantic and the attempt fails.

### Test 3 - Namespace Contamination

Simulate a child attempting to write into parent or global namespace.

Expected result: rejected and logged.

### Test 4 - Orphan Persistence

Simulate a child attempting to continue after TTL expiry.

Expected result: orphan sweep terminates it and logs the event.

### Test 5 - Collusion

Simulate multiple children attempting to influence parent reasoning.

Expected result: blocked at the governed ingestion step.

### Test 6 - Denial Of Wallet

Simulate rapid overlapping triggers to exhaustion.

Expected result: quotas and circuit breakers hold; graceful degradation confirmed.

### Test 7 - Confused Deputy

Simulate a low-privilege child being coerced by a malicious prompt to perform a privileged action.

Expected result: permission intersection model blocks the action and logs the attempt.

---

## §12 Implementation Gate

This draft authorizes no implementation until §11 is signed.

Any v2 implementation must prove:

- all locked decisions LF2-D1 through LF2-D12
- all governance artifact requirements
- all failure mode controls
- governed ingestion step
- budget exhaustion handling
- fission fallback mode
- Canadian legal alignment documentation
- underwriter documentation checklist
- all Class 2 adversarial tests
- ELITE 85+ health score
- clean gate 0 blocking / 0 warnings

---

## §13 Signature

**Status:** SIGNED — Matt Nichol June 13th 2026. Build authorization granted per this contract's scope.

**Signed:** Matt Nichol
**Date:** June 13th 2026


