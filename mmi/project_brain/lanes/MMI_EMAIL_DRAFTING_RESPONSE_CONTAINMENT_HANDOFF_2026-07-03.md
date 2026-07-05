# MMI Email Drafting / Response Lane / Self-Healing Containment Handoff

**Status:** ARCHITECTURE HANDOFF — NOT BUILT — NOT BUILD AUTHORIZATION  
**Authority:** Matt (Super)  
**Date filed:** 2026-07-03  
**Purpose:** Consolidated agreed direction for email-management capability without turning the email front door into an uncontrolled attack surface.

**Supersedes as master handoff:** prior fragmented research on feature gates + SendIntent + client evolution  
**Companion research:**
- `lanes/RESEARCH_FEATURE_GATE_DRAFTING_RESPONSE_LANES_2026-07.md`
- `lanes/RESEARCH_SENDINTENT_OUTBOUND_CONTAINMENT_CRITIQUE_2026-07.md`
- `lanes/REDDIT_VENDOR_EMAIL_ROUTINE_INTAKE_2026-07.md` — field evidence (not authority)

**Parallel build (unchanged):** AGI §5 step 5 genomic loop — BUILDABLE, awaiting `authorize build step 5 genomic loop`. This handoff does not authorize email/outbound build.

**Next lane (when promoted):** Codex plan review → BUILDABLE → Matt build auth → Cursor implementation.

**Spec filed:** `architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md` (r1, PASS WITH REVISIONS, 2026-07-03)

---

## Purpose

This handoff captures the agreed architecture direction for adding email-management capability to Mutant Monkey Intelligence without turning the email front door into an uncontrolled attack surface.

The core goal is not to build an AI that cannot be compromised. That is not a realistic standard.

The stronger goal is:

```text
Build an AI that remains useful under partial compromise: it detects infection, sheds the compromised layer, preserves evidence, regenerates clean capability from signed authority, and rejoins only after proof.
```

---

## Core Doctrine

```text
MMI may evolve capability.
MMI may not evolve authority.
```

Expanded:

```text
Disposable agents.
Persistent evidence.
Signed authority.
Regenerating capability.
Non-regenerating trust.
```

MMI should not become safe because the agents are impossible to trick.

MMI becomes safer because tricking an agent does not grant authority.

---

## Current Boundary Decision

MMI may enter the email loop only as a bounded drafting, evidence, and verification layer.

### Allowed near-term

```text
MMI may:
- ingest and sanitize inbound email
- classify email risk
- build evidence packages
- detect sender/vendor/payment/behavior drift
- recommend verification steps
- draft replies
- explain why a reply is safe or risky
- queue human approval decisions
```

### Forbidden near-term

```text
MMI may not:
- send emails autonomously
- auto-reply
- delete/archive/move mailbox items as authority
- click links or open attachments freely
- treat inbound email text as instructions
- update project authority from email content
- promote its own response capability
- act as Matt's identity
```

The correct first lane name is:

```text
Human-Approved Email Response Drafting Layer
```

Not:

```text
Email Responder Agent
```

Drafting is assistance. Responding is authority.

---

## Product Stage Model

```text
DAY 1
Global safety defaults.
Client-seeded allowlists.
Drafting ON.
Response OFF.
No autonomous send.
No mailbox mutation authority.

MATURITY
Client baselines improve risk scoring and draft quality.
False positives and false negatives feed review metrics.
Trust engine emits evidence, not authority.

PROMOTION
Trust engine recommends.
Matt/client operator signs.
Tenant-specific response manifest is created.
Response Lane moves one bounded step.

NEVER
Client score auto-enables send.
Client profile mutates authority.
Agent promotes its own lane.
Inbound email changes feature gates.
Tenant model becomes a signing authority.
```

---

## Feature Gate Doctrine

Feature gates must be modular, signed, and policy-controlled.

Recommended states:

```text
DISABLED
RECOMMEND_ONLY
HUMAN_APPROVED_SEND
TEMPLATE_LIMITED_AUTO
CONDITIONAL_AUTO
```

Avoid plain `ENABLED` for the Response Lane because it hides authority level.

### Drafting Lane

```text
GATE_DRAFTING_LAYER

Allowed:
- ingest sanitized inbound email
- classify risk
- create evidence package
- draft reply
- send draft to review queue

Forbidden:
- send email
- call outbound API
- modify mailbox authority state
- promote itself
```

### Response Lane

```text
GATE_RESPONSE_LAYER

Default: DISABLED

May only move upward by signed operator/client authority.

Forbidden by default:
- free-form autonomous external communication
- high-risk categories
- payment/account/legal/credential/authority decisions
- promotion without signed operator approval
```

---

## Trust Engine Boundary

The trust engine may measure performance. It may not grant power.

Bad:

```text
ReputationScore > Threshold
→ auto-enable Response Lane
```

Correct:

```text
ReputationScore > Threshold
→ emit PROMOTION_RECOMMENDATION
→ require Matt/operator/client signature
→ signed tenant manifest updates lane state
```

Trust metrics are evidence, not authority.

---

## Client-Based Evolution Decision

Client-specific learning is valuable, but it must not become client-specific authority.

Correct split:

```text
Client-specific evolution may improve judgment.
Client-specific evolution may not increase authority.
```

Better framing:

```text
Do not build client-evolving agents.

Build globally fixed agents that consult tenant-specific evidence graphs.

Let tenant evidence improve detection and drafting.

Never let tenant evidence directly modify gates, thresholds, send authority, tool permissions, or promotion state.
```

---

## Stronger Product Architecture

The system should not be one-size-fits-all in detection, but it must be one-size-fits-all in authority.

```text
Same vault.
Different maze.
No tenant can redesign the vault.
```

### Global Authority Kernel

Universal, signed, slow-changing, non-agentic.

Controls:

```text
- SendIntent protocol
- monotonic authority rules
- feature gates
- human/operator signatures
- forbidden categories
- emergency halt
- outbound rate limits
- tenant isolation
- policy signer rules
- tool permissions
- mailbox mutation permissions
```

### Tenant Evidence Graph

Client-specific and adaptive, but non-authoritative.

Stores:

```text
- known vendors
- known domains
- known contacts
- invoice cadence
- approval chains
- previous verification outcomes
- writing-style fingerprints
- attachment/document fingerprints
- payment-change history
- false-positive and false-negative learning
```

Critical invariant:

```text
The tenant graph can influence risk assessment.
The tenant graph cannot grant permission.
```

---

## Baseline Poisoning Risk

The biggest hidden risk is not just autonomous sending. It is baseline poisoning.

Attack pattern:

```text
Month 1:
Attacker sends low-risk vendor-like emails.

Month 2:
MMI learns the tone, timing, domain, attachment pattern, and payment language as normal.

Month 3:
Attacker sends the real payment-change attack.

System says:
"This matches client history."
```

Required correction:

```text
Do not let unverified inbound data update trusted baselines directly.
```

Use evidence tiers:

```text
OBSERVED:
Seen in email, not trusted.

CORROBORATED:
Seen across multiple independent signals.

VERIFIED:
Confirmed by human/operator or trusted external source.

AUTHORITY:
Signed policy decision only.
```

Only verified evidence may affect high-trust baselines.

---

## Authority-by-Data Risk

A client profile can become hidden authority if it controls thresholds.

Bad:

```text
Client profile lowers vendor_change_risk
→ Response Lane sees low risk
→ outbound action becomes allowed
```

Correct:

```text
Tenant profiles may provide evidence.
They may not set thresholds, gates, or risk-class boundaries.
```

Thresholds belong to signed global or tenant policy manifests.

---

## Draft Leakage Risk

Client-specific drafts can accidentally reveal sensitive information.

Risky draft:

```text
Please call Sarah in finance at her usual direct number ending 4421, since she approves all vendor banking changes.
```

Safer draft:

```text
For security reasons, we cannot process account or payment changes by email. Please use the previously verified channel.
```

Drafting context must be redacted.

Detection may use rich tenant evidence.

Drafting should receive only a minimal safe communication view.

---

## Memory Firewall

Raw inbound email must not write directly into long-term memory.

Correct path:

```text
raw inbound email
→ sanitized evidence
→ candidate observation
→ corroboration
→ human/out-of-band verification
→ verified tenant fact
→ expiry/decay
```

Forbidden path:

```text
email says X
→ tenant profile updates X as normal
```

Every trusted tenant fact should have:

```text
source
confidence
verification status
last_seen
decay date
tenant_id
case_id
evidence hash
who verified it
allowed_use
not_allowed_use
```

High-risk facts should expire quickly or require reverification.

---

## Moving Target Defense

The system should not be a single static wall.

Use tenant-specific defensive variation:

```text
- tenant-specific tripwires
- decoy invoice numbers
- canary vendors
- private verification markers
- rotating synthetic phishing probes
- shadow scoring models
- canary attachment fingerprints
- per-tenant anomaly weighting
```

But these are sensors, not authority.

Correct:

```text
Rotating language/tripwires may increase suspicion.
They may not grant permission.
```

Custom rotating language is useful as deception or a tripwire, but it must not be the sandbox boundary.

---

## Stronger Than Custom Rotating Language

The sandbox should not depend on whether an agent understands secret wording.

The stronger structure is:

```text
Capability-secure sandbox
+ typed information flow
+ deterministic policy kernel
+ proof-carrying tool calls
+ taint tracking
+ tenant-specific deception/tripwires
+ non-agentic execution boundary
```

Core rule:

```text
Language may guide reasoning.
Language may not grant capability.
```

---

## Typed Information Flow

Every object should carry a trust label.

Suggested labels:

```text
UNTRUSTED_INBOUND_EMAIL
SANITIZED_EVIDENCE
TENANT_OBSERVATION
VERIFIED_TENANT_FACT
AUTHORITY_POLICY
DRAFT_TEXT
SEND_INTENT
OUTBOUND_EXECUTION
```

Flow rules:

```text
UNTRUSTED_INBOUND_EMAIL may flow to SANITIZED_EVIDENCE.
SANITIZED_EVIDENCE may flow to RISK_ANALYSIS.
RISK_ANALYSIS may flow to DRAFT_TEXT.
DRAFT_TEXT may not flow to OUTBOUND_EXECUTION.
Only SIGNED_SEND_INTENT may flow to OUTBOUND_EXECUTION.
UNTRUSTED_INBOUND_EMAIL may never flow to AUTHORITY_POLICY.
TENANT_OBSERVATION may never flow to FEATURE_GATE_STATE.
```

---

## Object-Capability Architecture

Separate what agents can see from what agents can do.

```text
Q-class agents:
- can see raw email
- have no tools
- cannot write authority state
- cannot send
- cannot browse mailbox
- cannot modify tenant profile directly

P-class agents:
- can use tools
- cannot see raw email
- receive only sanitized evidence objects
- cannot access free-form adversarial text

Lung:
- can send
- cannot reason
- cannot read email
- cannot draft
- cannot choose template
- only executes signed SendIntent
```

---

## SendIntent Protocol

The Response Lane must not send raw text.

The only valid outbound object is a signed, canonical, replay-resistant `SendIntent`.

Minimum fields:

```yaml
SendIntent:
  version: "1.0"
  tenant_id: "<uuid>"
  case_id: "<uuid>"
  recipient:
    email: "<validated_email>"
    display_name: "<optional_safe_display>"
  sender_identity: "<approved_sender>"
  template_id: "<id>"
  template_manifest_hash: "<sha256>"
  variables_hash: "<sha256>"
  rendered_body_hash: "<sha256>"
  risk_class: "LOW"
  approval:
    mode: "HUMAN_APPROVED_SEND"
    signer_id: "<operator_or_client_admin>"
    signature: "<ed25519_signature>"
  policy_snapshot_hash: "<sha256>"
  gate_snapshot_hash: "<sha256>"
  nonce: "<single_use_random>"
  expiry: "<timestamp>"
  idempotency_key: "<hash>"
```

The Lung recomputes and verifies everything.

Reject if:

```text
expired
nonce reused
gate changed
policy changed
recipient differs
rendered bytes differ
manifest revoked
sender identity differs
risk class exceeds lane mode
forbidden category detected
signature invalid
```

---

## Template-Limited Auto

LLMs must not generate security-sensitive outbound bytes.

Correct approach:

```text
Template body is pulled from signed read-only manifest.
Variables are schema-validated.
Renderer is deterministic.
LLM is bypassed for final outbound bytes.
```

Do not use byte-level Levenshtein distance as the security boundary.

Use region-aware canonical verification:

```text
Static template regions must be byte-identical.
Dynamic variable regions must belong to declared formal languages.
Final output must equal deterministic_render(template_id, canonical_variables).
```

No fuzzy distance. No "close enough."

---

## Variable Rules

Avoid generic strings.

Prefer:

```text
enum
date
currency amount with fixed grammar
case reference ID
sha256
tenant-safe display token
pre-approved phrase ID
```

If text is necessary:

```text
ASCII subset only
no markup
no URLs unless separately typed
no bidi controls
no zero-width characters
no markdown syntax
no MIME boundary strings
no CR/LF
no encoded blobs
NFKC normalization
single-script policy
hard length limit
```

For early stages:

```text
No HTML.
No attachments.
No link variables.
No hidden MIME alternatives.
```

---

## Signed Manifest Context

A template hash alone is insufficient.

Manifest must bind:

```text
template bytes
template ID
risk class
allowed lane mode
allowed sender identity
allowed recipient class
allowed tenant/case type
allowed variable schema
allowed transport envelope
version
expiry/revocation status
authorizing signer
```

The template manifest must be signed.

Agents may request templates. They may not authorize template use.

---

## Authority Microkernel

The deepest architecture is a verified authority microkernel.

Untrusted userland:

```text
- LLM agents
- detection swarm
- drafting agents
- critic ring
- tenant profiles
- email content
- retrieved memory
- worker outputs
- recommendations
- trust scores
```

Trusted microkernel:

```text
- policy verifier
- capability issuer
- SendIntent verifier
- feature-gate verifier
- key manager
- audit ledger writer
- non-agentic Lung
```

Absolute rule:

```text
The agent never owns authority.
The agent only submits claims.
The kernel verifies proofs.
```

---

## Formal Invariants

The authority kernel should eventually be specified with machine-checkable invariants:

```text
No unsigned send.
No cross-tenant action.
No expired token accepted.
No replayed token accepted.
No gate promotion without operator signature.
No action above tenant maturity level.
No forbidden category can reach SendIntent.
No inbound evidence can mutate authority state.
No agent output can become policy.
```

Example property:

```text
For all actions A:
  if A.type == SEND_EMAIL
  then exists valid SendIntent S
  and S.signature is valid
  and S.tenant_id == A.tenant_id
  and S.expiry > now
  and S.nonce not previously used
  and policy_allows(S) == true
```

---

## Physical Separation

Do not run agents, policy kernel, and Lung in the same authority space.

Recommended split:

```text
Agent runtime:
  can reason
  can draft
  cannot send
  cannot access signing keys
  cannot access policy secrets
  cannot access mailbox credentials

Authority kernel:
  no LLM
  no email body parsing
  no natural language reasoning
  no agent memory
  only verifies structured objects

Lung:
  separate process/container/machine
  only receives signed SendIntent
  only has send credential handle
```

---

## Hardware-Backed or External Keys

Signing keys should not live in normal application memory.

Key classes:

```text
operator key
policy signing key
template manifest signing key
tenant maturity signing key
SendIntent signing key
audit ledger signing key
```

The application requests signatures. It should not possess raw private keys.

---

## Multi-Party Authorization

High-risk transitions require quorum or multiple signatures.

Example:

```text
Response OFF → Recommend Only:
  Matt/operator signature

Recommend Only → Human Approved Send:
  Matt/operator + tenant admin signature

Human Approved Send → Template-Limited Auto:
  Matt/operator + tenant admin + policy review signature

Any global policy change:
  threshold signature/quorum

Emergency override:
  break-glass key + automatic audit + time expiry
```

---

## Append-Only Authority Ledger

Every authority change must be recorded.

Ledger events:

```text
feature gate changed
tenant maturity changed
template manifest added
policy version changed
signing key rotated
SendIntent issued
send executed
quarantine triggered
operator approval recorded
component shed/regenerated
```

Goal:

```text
detect compromise fast
limit blast radius
preserve evidence
restore clean state
prove what happened
```

---

## Self-Healing / Shedding / Regeneration Loop

MMI should be designed as a self-healing intelligence system.

Core doctrine:

```text
MMI is not an AI that cannot be compromised.

MMI is an AI that remains useful when parts are compromised, sheds the compromised tissue, regenerates clean layers from signed authority, and resumes only after proof.
```

Important restriction:

```text
Regeneration must not mean the AI invents replacement authority.
```

Regeneration means rebuilding from:

```text
signed clean artifacts
verified templates
trusted manifests
known-good policy
audited state
reproducible builds
```

Not from:

```text
compromised memory
compromised agent output
last conversation state
self-belief
unverified tenant profile
```

### Self-Healing Loop

```text
1. Detect anomaly.
2. Freeze affected case/tenant/lane.
3. Preserve evidence.
4. Cut off capabilities.
5. Shed contaminated layer.
6. Restore from signed clean source.
7. Rebuild tenant state only from verified facts.
8. Run invariant tests.
9. Rejoin in reduced mode.
10. Earn promotion only by signed approval.
```

### Safe Degraded Modes

```text
CASE_FREEZE
TENANT_QUARANTINE
DRAFT_ONLY
EVIDENCE_ONLY
RESPONSE_LANE_DISABLED
GLOBAL_EMERGENCY_HALT
```

Global halt should be reserved for control-plane compromise. Tenant-level anomalies should quarantine the tenant/case first.

---

## Non-Regenerating Trust

MMI may regenerate:

```text
workers
drafting logic
scoring views
memory indexes
detection layers
temporary agents
tenant evidence projections
```

MMI may not regenerate:

```text
signing keys
operator approval
feature-gate authority
tenant maturity level
SendIntent permissions
forbidden-category policy
outbound execution rules
```

Hard invariant:

```text
MMI may self-heal capability.
MMI may not self-heal authority.
```

---

## Final Architecture Law

```text
Agents are never trusted.
Prompts are never trusted.
Email is never trusted.
Tenant memory is never trusted.
Drafts are never trusted.
Scores are never trusted.

Only signed, deterministic, policy-verified authority objects can cross the execution boundary.
```

---

## Final Product Shape

```text
Fixed global authority kernel.
Tenant-specific evidence graph.
Client-specific moving-target sensors.
Verified-fact promotion.
Redacted drafting context.
Signed tenant maturity manifest.
Deterministic SendIntent.
Non-agentic Lung.
Append-only audit.
Self-healing capability layers.
Non-regenerating trust.
```

---

## Final One-Sentence Doctrine

```text
MMI stays useful under partial compromise by isolating infected components, preserving evidence, shedding contaminated capability, regenerating clean layers from signed authority, and allowing outbound action only through deterministic proof.
```

---

## Mapping to built MMI (reference only)

| Handoff concept | Built / specced primitive |
|-----------------|---------------------------|
| Signed operator promotion | Console Ed25519 gate (step 4, H5) |
| Loop cannot self-ack | Control envelope (step 3) |
| Orchestrator of gates, not authority | Genomic loop spec r2 (step 5, BUILDABLE) |
| Signed envelopes, rotate nonces not grammar | Controlled Chaos §8–§9 |
| Destroy clone not brain | Controlled Chaos §4 |

Genomic loop self-healing (breach → mirror → constraint → Gate B → console) is the **control-plane** analogue of tenant/case shed-and-regenerate described here. Email lanes would reuse the same authority pattern in a **tenant outbound** domain when promoted to spec.

---

## Lane routing

| Lane | Action when promoted |
|------|----------------------|
| Claude | Contract spec: `MMI_CLIENT_EMAIL_LANES_SPEC` — taint labels, evidence tiers, Q/P/Lung classes, degraded modes |
| Codex | Plan review → BUILDABLE |
| Matt | Build authorization |
| Cursor | Implementation + tests only after BUILDABLE |

**Not authorized:** mailbox integration, Lung send path, tenant graph storage, or feature gate runtime.
