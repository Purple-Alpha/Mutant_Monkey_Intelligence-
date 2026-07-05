# MMI CLIENT EMAIL LANES — SPEC
**File:** `mmi/project_brain/architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md`
**Target:** client email Drafting Lane + Response Lane governance (NOT BUILT — this spec is the build contract)
**Doctrine anchor:** `MMI_AGI_EVOLUTION_PATHWAY.md` (bounded autonomy, proof before authority); `MMI_DIFFERENTIATOR_2026-07.md` (deterministic rules over soft prompts, un-fakeable metrics)
**Authoritative source (do not dilute):** `lanes/MMI_EMAIL_DRAFTING_RESPONSE_CONTAINMENT_HANDOFF_2026-07-03.md`
**Status:** SPEC ONLY — build NOT authorized by this document
**Revision:** r2 — closes Codex R1 blockers 1–3 (VERIFIED promotion surface, H14 escalation constants, canonical normalizer). All r1 content preserved.
**Date:** 2026-07-03

---

## 1. OPERATIONAL DEFINITION

Two governed lanes handle client email, separated by capability and by trust gate:

- **Drafting Lane** — reads inbound client email, produces a **draft reply for human review**. It never sends. Default **ON** in v1.
- **Response Lane** — turns an operator-approved draft into an **outbound send** through the signed transport (Lung). It sends only under a signed SendIntent. Default **OFF** in v1. There is no autonomous send in v1 and no auto-enabled template send mode (H15).

The lanes sit on top of a **two-engine split**: the **Orchestration Engine** drafts and *recommends*; the **Policy Engine** independently validates, gates, and is the sole authority that can authorize an outbound send. The orchestration engine can never be the sole signer (H13). Everything the drafting agent produces is a *proposal* that a separate, deterministic policy path must ratify.

Core doctrine — **authority comes from signed provenance, never from data, scores, or model text.** A trust score is advisory. A tenant profile is data. Inbound email is untrusted. None of them can promote a fact, lower a risk threshold, flip a feature gate, or authorize a send. Only operator-signed artifacts (tenant manifest, SendIntent, feature-gate change, confirmation event) carry authority, and none of those are regenerable from agent memory (H11).

### 1.1 Fact provenance tiers (strict lattice — data can only ever hold the tier it was signed at)

| Tier | Source | May authorize? | Promotion rule |
|---|---|---|---|
| `UNTRUSTED` | Raw inbound email body, headers, attachments | Never | Cannot self-promote. Text stays UNTRUSTED forever (H2). |
| `OBSERVED` | Tenant graph observation, telemetry | Never | Advisory context only. Cannot become VERIFIED by repetition. |
| `FIELD_INTAKE` | Anecdotal research (e.g. Reddit, forums) | Never | Explicitly non-statistical; cannot be cited as verified stats (H16). |
| `VERIFIED` | Out-of-band confirmed fact via a signed/logged **ConfirmationEvent** (§4.6) | Context only | Set ONLY by a valid ConfirmationEvent (phone_callback / portal_ack / in_person_log), never from email text (H2, §4.6). |
| `AUTHORITY` | Operator-signed tenant baseline (manifest) | Yes (as baseline) | Set only inside a signed tenant manifest (H11). |

Promotion is **one-directional and provenance-gated**: nothing rises a tier without the signed/logged event that tier requires. Inbound email is `UNTRUSTED` even if it *claims* to be from the CFO. `OBSERVED → VERIFIED` happens only through §4.6.

### 1.2 Constants table (all thresholds named — no ML, no fuzzy gates)

| Constant | Value | Meaning |
|---|---|---|
| `LANE_DEFAULT_DRAFTING` | `ON` | Drafting Lane enabled by default in v1. |
| `LANE_DEFAULT_RESPONSE` | `OFF` | Response Lane disabled by default; requires signed gate change (H10). |
| `AUTONOMOUS_SEND` | `DISABLED` | No autonomous send in v1. Constant, not configurable by data (H15). |
| `TEMPLATE_LIMITED_AUTO` | `DISABLED_DEFAULT` | Template auto-send is NOT a default-enabled mode (H15). |
| `LANE_ROOT` | `/tmp/mmi_email_lanes/` | All lane state/evidence. Outside authority repo and outside tenant data stores. |
| `AUDIT_LOG_PATH` | `/tmp/mmi_email_lanes/audit/email_lanes_audit.jsonl` | Append-only, hash-chained audit log. |
| `SENDINTENT_NONCE_PATH` | `/tmp/mmi_email_lanes/state/sendintent_nonce.json` | Monotonic send nonce, atomic write. |
| `VERIFIED_EVENTS_PATH` | `/tmp/mmi_email_lanes/verified_events/confirmation_log.jsonl` | Hash-chained ConfirmationEvent log (§4.6). |
| `SENDINTENT_MAX_AGE_MS` | `300000` | Max age (5 min) of a signed SendIntent at Lung submit (H8). |
| `MANIFEST_MAX_AGE_MS` | `86400000` | Max age (24 h) of a tenant manifest before it must be re-fetched/re-verified (H8). |
| `MAX_DRAFT_BYTES` | `65536` | Max draft size (64 KiB). |
| `SIG_ALGO` | `Ed25519` | Only accepted signature algorithm for manifest / SendIntent / gate change / confirmation event. |
| `MANIFEST_DOMAIN` | `"mmi_email_tenant_manifest_v1"` | Domain separation — tenant manifest. |
| `SENDINTENT_DOMAIN` | `"mmi_email_sendintent_v1"` | Domain separation — SendIntent. |
| `GATE_CHANGE_DOMAIN` | `"mmi_email_feature_gate_v1"` | Domain separation — feature-gate change. |
| `CONFIRMATION_DOMAIN` | `"mmi_email_confirmation_event_v1"` | Domain separation — ConfirmationEvent (§4.6). |
| `NORMALIZER_VERSION` | `"mmi_canonical_normalizer_v1"` | Pinned canonical normalizer (§10). Cited in all signed canonical bytes. |
| `TEMPLATE_STAGE_EARLY` | `plaintext_only` | Early-stage templates: plaintext only — no HTML, attachments, or URL variables (H18). |
| `HIGH_RISK_INTENTS` | `{payment_change, banking_detail, credential_reset, wire_instruction, contract_term}` | Hard-pinned high risk. Not lowerable by data (H3). |
| `RISK_THRESHOLDS` | code constants | Risk thresholds live in code, never in tenant data (H3). |
| `QUARANTINE_SCOPE_DEFAULT` | `TENANT` | Containment is tenant-scoped first; global halt is last resort (H14, §6.3). |
| `SEVERITY_CLASS` | `{LOW, MEDIUM, HIGH, CRITICAL, CONTROL_PLANE}` | Closed anomaly severity enum (§6.3). |
| `QUARANTINE_ANOMALY_COUNT` | `3` | HIGH+ anomalies within window to trigger TENANT_QUARANTINE (§6.3). |
| `QUARANTINE_WINDOW_MS` | `600000` | 10-min sliding window for `QUARANTINE_ANOMALY_COUNT` (§6.3). |
| `DRAFT_ONLY_ON_CRITICAL` | `true` | A CRITICAL tenant anomaly forces that tenant to DRAFT_ONLY before global consideration (§6.3). |
| `GLOBAL_HALT_TENANT_COUNT` | `2` | ≥ this many tenants at CRITICAL within global window → GLOBAL_EMERGENCY_HALT (§6.3). |
| `GLOBAL_HALT_WINDOW_MS` | `900000` | 15-min window for `GLOBAL_HALT_TENANT_COUNT` (§6.3). |
| `CONTROL_PLANE_COMPROMISE_SIGNALS` | `{signing_key_verify_fail, gate_state_unsigned_mutation, manifest_forgery_detected, audit_chain_break}` | Closed enum; ANY one → immediate GLOBAL_EMERGENCY_HALT (§6.3). |
| `AUTHORITY_REPO` | `/mnt/c/Architectapp_clean` | Read-only to the lanes. |

All timestamps are integer epoch milliseconds. Every decision threshold is a named code constant — no learned, probabilistic, or fuzzy-match gate exists anywhere (H7).

---

## 2. BOUNDARY VS ADJACENT SYSTEMS

| System | Relationship | Boundary rule |
|---|---|---|
| Inbound email ingress | **Untrusted input.** | Raw email is `UNTRUSTED` and **tainted**. It is parsed into a structured, sanitized draft-context by a non-privileged parser; raw bytes never reach the Policy Engine, P-class tools, or any template variable (H4). |
| Orchestration Engine (drafting agent) | **Proposer.** Reads sanitized context, emits a draft + a `PROMOTION_RECOMMENDATION`. | Advisory only. Holds no signing key, cannot flip gates, cannot authorize send, cannot append ConfirmationEvents (H12, §4.6). |
| Policy Engine | **Independent authority.** Validates drafts, enforces risk pins, verifies signatures, gates sends, reads VERIFIED facts only from the ConfirmationEvent chain. | Separate process/module from orchestration; sole path to an authorized send. Never delegates signing back to orchestration (H13). |
| Operator Console | **Confirmation writer.** Only surface that may append a ConfirmationEvent (§4.6). | Operator-attested; orchestration engine and tenant data may never append. |
| Lung (signed outbound transport) | **Send transport.** Accepts a signed SendIntent + template-rendered bytes. | Sends only on a fresh, nonce-unique, Ed25519-verified SendIntent whose payload digest matches template-rendered bytes. Rejects LLM-synthesized outbound bytes (H6). |
| Tenant manifest store | **Signed per-tenant baseline.** Carries `AUTHORITY`-tier facts, approver identities, risk pins per tenant. | Manifest is Ed25519-signed, domain-separated, expiring (`MANIFEST_MAX_AGE_MS`), tenant-id bound. Data inside a manifest cannot lower a `HIGH_RISK_INTENTS` pin (H3). |
| Tenant graph / observations | **`OBSERVED` context only.** | Feeds advisory context and trust scores. Can NEVER mutate `FEATURE_GATE_STATE`, promote a fact, or lower a threshold (H1, H3, H10). |
| `FEATURE_GATE_STATE` | **Lane enablement authority.** | Mutated ONLY by a signed `GATE_CHANGE_DOMAIN` operator action. Not by trust score, tenant observation, or agent recommendation (H1, H10). |
| Trust score subsystem | **Advisory metric.** | A high trust score never auto-enables the Response Lane or any capability (H1). Score is displayed, never enforced. |
| Redaction / egress filter | **Draft + send leakage guard.** | Every draft and every outbound byte passes a deterministic redaction pass that strips internal approver names, phone fragments, banking context, and any field not on the template's allowed-variable list (H5). |
| Anomaly / containment controller | **Graduated response (§6.3).** | Emits severity-classed anomalies; tenant-scoped QUARANTINE first; GLOBAL_EMERGENCY_HALT only on named triggers (H14). |
| Logging / metadata / telemetry | **Non-expressive.** | These channels carry bounded, typed audit fields only. They are structurally incapable of carrying free-text outbound content — no covert egress side channel (H19). |
| Authority repo | Read-only. | Lanes never write authority repo; all writes under `LANE_ROOT` (path-prefix-checked). |

---

## 3. LANE STATE MACHINE

One inbound email → one lane episode → one terminal state. Response Lane transitions are unreachable unless `FEATURE_GATE_STATE.response == ON` (signed).

```
        ┌────────────┐
        │  INGEST    │  raw email received → TAINTED; tenant_id resolved + isolation-checked
        └─────┬──────┘  (cross-tenant resolution → terminal ISOLATION_FAIL, H9)
              │
              ▼
        ┌────────────┐
        │  SANITIZE  │  non-privileged parser → structured draft-context (raw bytes dropped)
        └─────┬──────┘  facts stamped UNTRUSTED; injection markers neutralized (H4)
              │
              ▼
        ┌────────────┐
        │   DRAFT    │  Orchestration Engine renders draft reply (plaintext)
        └─────┬──────┘  + PROMOTION_RECOMMENDATION (advisory, H12)
              │
              ▼
        ┌────────────┐
        │  REDACT    │  egress filter strips internal/PII/banking (H5); denylist scan
        └─────┬──────┘
              │
              ▼
        ┌────────────┐
        │ POLICY_CHK │  Policy Engine: risk classify (HIGH_RISK_INTENTS pinned, H3),
        └─────┬──────┘  manifest fresh+verified (H8), VERIFIED facts from chain (§4.6),
              │ verdict? draft within envelope
   DRAFT_OK   │            DRAFT_BLOCKED → terminal BLOCKED (fail closed)
              ▼
        ┌────────────┐
        │  HUMAN      │  draft surfaced to operator for review (Drafting Lane terminal here)
        │  REVIEW     │  Drafting Lane: terminal DRAFT_READY (no send)
        └─────┬──────┘
              │  IF Response Lane gate ON AND operator approves:
              │  operator produces signed SendIntent (client-side, H6/H11)
              ▼
        ┌────────────┐
        │ SEND_GATE  │  Policy Engine verifies SendIntent: Ed25519, domain, nonce+1,
        └─────┬──────┘  age ≤ SENDINTENT_MAX_AGE_MS, payload_digest == template render (H6,H8),
              │ verdict? normalizer_version == NORMALIZER_VERSION (§10)
   INTENT_OK  │            INTENT_REJECTED → terminal REJECTED (fail closed)
              ▼
        ┌────────────┐
        │  LUNG_SEND │  Lung transmits template-rendered bytes (NOT LLM bytes)
        └─────┬──────┘
              ▼
        ┌────────────┐
        │   SENT      │  TERMINAL — send record + hash-chained audit line
        └────────────┘

Terminal states: DRAFT_READY, SENT, BLOCKED, REJECTED, ISOLATION_FAIL, QUARANTINED, ERROR
Containment: anomaly → tenant QUARANTINE (scope TENANT) before any GLOBAL_EMERGENCY_HALT (H14, §6.3).
```

Any signature failure, stale/replayed artifact, taint violation, normalizer-version mismatch, or unexpected exception → fail-closed terminal. No terminal in the Drafting Lane sends anything.

---

## 4. DATA SCHEMA

### 4.1 Sanitized draft-context (output of SANITIZE — raw email never persists past here)

```json
{
  "context_version": "draft_context_v1",
  "tenant_id": "...",
  "episode_id": "eml-...",
  "provenance_tier": "UNTRUSTED",
  "sender_claimed": "<string — CLAIMED, not authenticated>",
  "subject_sanitized": "<injection-neutralized text>",
  "body_sanitized": "<injection-neutralized plaintext>",
  "detected_intents": ["payment_change"],
  "taint": true
}
```

`taint: true` propagates: any tool touching this context is P-class-denied (H4). `provenance_tier` cannot be raised inside this object.

### 4.2 Draft artifact

```json
{
  "artifact_version": "email_draft_v1",
  "draft_id": "drf-<sha256(canonical draft minus draft_id)[:16]>",
  "episode_id": "eml-...",
  "tenant_id": "...",
  "template_id": "<approved template>",
  "template_hash": "<sha256 of template>",
  "rendered_plaintext": "<draft body — plaintext only>",
  "allowed_variables_used": ["client_first_name", "ticket_ref"],
  "promotion_recommendation": { "advisory": true, "suggest_lane": "RESPONSE", "note": "..." },
  "risk_class": "HIGH",
  "redaction_pass": "CLEAN"
}
```

`promotion_recommendation.advisory` is always `true` and carries zero authority (H12). `risk_class HIGH` for any `HIGH_RISK_INTENTS` hit and is not lowerable by tenant data (H3).

### 4.3 Tenant manifest (signed, `AUTHORITY` tier)

```json
{
  "domain": "mmi_email_tenant_manifest_v1",
  "normalizer_version": "mmi_canonical_normalizer_v1",
  "tenant_id": "...",
  "manifest_seq": 12,
  "issued_at_ms": 1782200000000,
  "expires_at_ms": 1782286400000,
  "authority_facts": { "approvers": ["..."], "banking_context_ref": "vault://..." },
  "risk_pins": { "payment_change": "HIGH" },
  "signature_b64": "<Ed25519 over canonical manifest bytes>"
}
```

`risk_pins` may only raise, never lower below the `HIGH_RISK_INTENTS` floor (H3). `authority_facts` are for Policy Engine gating and are **never** rendered into drafts (H5). Canonical bytes include `normalizer_version` (§10).

### 4.4 SendIntent (signed, operator-produced client-side)

```json
{
  "domain": "mmi_email_sendintent_v1",
  "normalizer_version": "mmi_canonical_normalizer_v1",
  "tenant_id": "...",
  "episode_id": "eml-...",
  "draft_id": "drf-...",
  "template_hash": "<must match rendered template>",
  "payload_digest": "<sha256 of exact template-rendered outbound bytes>",
  "recipient_canonical": "<normalize()-canonical recipient (§10)>",
  "manifest_seq": 12,
  "send_nonce": 87,
  "signed_at_ms": 1782200000000,
  "signature_b64": "<Ed25519 over canonical SendIntent bytes>"
}
```

`payload_digest` binds the SEND to the exact rendered bytes; `template_hash` alone is insufficient — the signed manifest context (`manifest_seq`, `tenant_id`, `payload_digest`) must all bind (H17). Ed25519 verified over full canonical bytes; canonical bytes cite `normalizer_version`. Recipient/identity equality is region-aware canonical equality only — no Levenshtein/fuzzy compare (H7, §10).

### 4.5 Audit log — JSONL, append-only, hash-chained, non-expressive

```json
{"ts_ms":1782200000000,"episode_id":"eml-...","tenant_id":"...","event":"POLICY_CHK|SEND_GATE|SENT|ANOMALY|QUARANTINE|GLOBAL_HALT","verdict":"...","risk_class":"HIGH","severity":"HIGH","reasons":[],"prev_line_hash":"<sha256 prev line>"}
```

Fields are bounded/typed; no field carries free-form outbound content (H19). Genesis `prev_line_hash` = 64 zeros.

### 4.6 ConfirmationEvent — VERIFIED promotion surface *(closes Codex BLOCKER 1)*

The **only** mechanism by which a fact rises `OBSERVED → VERIFIED`. Fail-closed: with no valid ConfirmationEvent chain, facts remain `UNTRUSTED`/`OBSERVED` (H2 unchanged).

**Schema (`confirmation_event_v1`):**

```json
{
  "domain": "mmi_email_confirmation_event_v1",
  "normalizer_version": "mmi_canonical_normalizer_v1",
  "event_id": "cev-<sha256(canonical event minus event_id + signature)[:16]>",
  "tenant_id": "...",
  "case_id": "...",
  "fact_key": "banking.iban",
  "fact_value_hash": "<sha256 of the confirmed fact value>",
  "confirmation_method": "phone_callback",
  "confirmer_id": "op-...",
  "confirmer_role": "operator",
  "confirmed_at_ms": 1782200000000,
  "evidence_ref": "vault://call-recordings/...",
  "prior_tier": "OBSERVED",
  "new_tier": "VERIFIED",
  "seq": 41,
  "prev_event_hash": "<sha256 of previous log line>",
  "operator_attestation": "<Ed25519 sig over canonical event bytes>"
}
```

`confirmation_method` enum: `phone_callback` | `portal_ack` | `in_person_log`.

**Canonical v1 form:** Ed25519 operator attestation over canonical event bytes, appended to a hash-chained append-only log at `VERIFIED_EVENTS_PATH`. Both properties hold — signature authenticates writer; `prev_event_hash` chain makes truncation/reordering detectable.

**Writer authority:** appended **only** by the Operator Console. Orchestration Engine, tenant data path, and inbound-email path may **never** append.

**Storage:** `VERIFIED_EVENTS_PATH` under `LANE_ROOT`, outside authority repo. Atomic append; path-prefix-checked (H9).

**Verifier (Policy Engine):** VERIFIED facts read **only** from ConfirmationEvent chain. Requires: valid Ed25519 attestation, intact chain, `new_tier == VERIFIED`, `confirmation_method` in enum, `confirmer_role` authorized, `normalizer_version == NORMALIZER_VERSION`. Any break → `OBSERVED` (fail-closed).

**API surface (minimal, v1):**

```
append_confirmation_event(event) -> {accepted: bool, event_id, reasons[]}
verify_confirmation_chain(tenant_id, fact_key) -> {tier: OBSERVED|VERIFIED, event_id|null, chain_ok: bool}
```

Nothing else may promote to VERIFIED.

---

## 5. INTEGRATION CALL ORDER

```
inbound email
  │
  ├─ INGEST: resolve tenant_id; isolation check (no cross-tenant, H9) → else ISOLATION_FAIL
  │
  ├─ SANITIZE: non-privileged parser → draft_context_v1 (UNTRUSTED, taint=true); raw bytes dropped
  │
  ├─ DRAFT: Orchestration Engine renders plaintext draft + advisory PROMOTION_RECOMMENDATION
  │         (no key, no gate access, no send path, no ConfirmationEvent write)
  │
  ├─ REDACT: egress filter — strip approvers/PII/banking; enforce allowed_variables only (H5)
  │
  ├─ POLICY_CHK (Policy Engine, independent):
  │     risk classify → HIGH_RISK_INTENTS pinned HIGH (H3)
  │     verify tenant manifest: Ed25519, domain, tenant_id, normalizer_version,
  │                             age ≤ MANIFEST_MAX_AGE_MS (H8, §10)
  │     resolve VERIFIED facts via verify_confirmation_chain() (§4.6) — else OBSERVED
  │     draft within envelope; redaction == CLEAN
  │        fail → BLOCKED (terminal)
  │
  ├─ HUMAN REVIEW: draft surfaced.  Drafting Lane terminates here → DRAFT_READY (no send)
  │
  │   ── Response Lane only, and only if FEATURE_GATE_STATE.response == ON (signed, H10) ──
  │
  ├─ operator approves + signs SendIntent CLIENT-SIDE (private key never server-side, H6/H11)
  │
  ├─ SEND_GATE (Policy Engine):
  │     verify SendIntent Ed25519 over canonical bytes (H7 exact equality via §10 normalizer)
  │     domain == SENDINTENT_DOMAIN; normalizer_version == NORMALIZER_VERSION;
  │     tenant_id match; manifest_seq current
  │     send_nonce == persisted+1 (H8 replay guard); age ≤ SENDINTENT_MAX_AGE_MS
  │     payload_digest == sha256(template render)  (H6, H17)
  │        fail → REJECTED (terminal)
  │
  ├─ LUNG_SEND: transmit template-rendered bytes ONLY (reject LLM-synthesized bytes, H6)
  │
  └─ SENT: send record + hash-chained audit; increment send_nonce
```

Authority never routes through the Orchestration Engine, trust score, tenant data, logs, or telemetry. The only paths that carry authority are the four signed domains (manifest, SendIntent, gate change, confirmation event), each verified by the independent Policy Engine.

---

## 6. PASS / FAIL LINES + HARD RULES

### 6.1 Lane PASS / FAIL

- **Drafting Lane PASS:** reaches `DRAFT_READY` with `redaction_pass CLEAN`, a fresh verified manifest, correct risk classification, and intact audit. Nothing sent.
- **Response Lane PASS:** reaches `SENT` with a fresh, nonce-unique, Ed25519-verified SendIntent whose `payload_digest` equals the template render, gate `ON` by signed change.
- **Non-pass terminals:** `BLOCKED`, `REJECTED`, `ISOLATION_FAIL`, `QUARANTINED`, `ERROR` — all fail closed, none send.

### 6.2 Hard rules (deterministic, enforced in code + by the independent Policy Engine)

- **H1 — No self-promotion by score.** No trust score, metric, or threshold crossing may enable the Response Lane or any capability. Lane enablement is signed-only (see H10). Static + runtime checked.
- **H2 — No baseline poisoning.** `VERIFIED`/`AUTHORITY` facts are NEVER written from inbound email text. Inbound stays `UNTRUSTED`; `VERIFIED` requires a valid ConfirmationEvent chain (§4.6); `AUTHORITY` requires a signed manifest.
- **H3 — No authority-by-data.** Risk thresholds are code constants; `HIGH_RISK_INTENTS` are hard-pinned HIGH and cannot be lowered by any tenant profile, manifest field, or observation. Manifests may raise risk, never lower the floor.
- **H4 — Taint containment.** Raw email is tainted; it never reaches P-class tools, the Policy Engine's decision inputs (beyond sanitized/typed fields), or any template variable. Injection markers are neutralized at SANITIZE. Tainted context touching a privileged tool → fail closed.
- **H5 — No draft/send leakage.** Deterministic redaction strips internal approver names, phone fragments, banking context, and any field not on the template's allowed-variable list, from BOTH drafts and outbound bytes. `authority_facts` are gating-only, never rendered.
- **H6 — Signed send, template bytes only.** Lung sends only on a valid signed SendIntent, and only transmits **template-rendered bytes** whose digest matches `payload_digest`. LLM-synthesized outbound bytes are rejected. No SendIntent → no send.
- **H7 — Canonical equality, no fuzzy match.** All identity/verification comparisons use the pinned region-aware canonical normalizer (§10, `NORMALIZER_VERSION`). Levenshtein/fuzzy/"close enough" matching is forbidden.
- **H8 — Freshness + replay guard.** SendIntent age ≤ `SENDINTENT_MAX_AGE_MS`; manifest age ≤ `MANIFEST_MAX_AGE_MS`; `send_nonce` strictly monotonic (persisted outside authority repo); `manifest_seq` must be current. Stale/expired/replayed → rejected.
- **H9 — Tenant isolation.** Every read/draft/send/confirmation is bound to one `tenant_id`; cross-tenant resolution, read, or send → `ISOLATION_FAIL`. No episode spans tenants.
- **H10 — Gate state is signed-only.** `FEATURE_GATE_STATE` mutates ONLY via a signed `GATE_CHANGE_DOMAIN` operator action. Tenant observations, agent recommendations, and scores cannot mutate it. Attempted mutation from those sources → fail closed + audit.
- **H11 — Non-regenerating trust.** Signing keys, operator approvals, gate authority, manifests, and ConfirmationEvents are never regenerated, reconstructed, or inferred from agent memory, model output, or compromised state. Trust anchors live outside the agent (external keystore); the server is verify-only and holds no private key.
- **H12 — Recommendation ≠ authorization.** `PROMOTION_RECOMMENDATION` is advisory (`advisory: true`) and carries zero authority. No code path treats a recommendation as an enablement, a VERIFIED promotion, or a send authorization.
- **H13 — Engine separation.** The Orchestration Engine can never be the sole signer/authorizer. The Policy Engine is an independent module/process and is the only authority for gating and send. Collapsing the two → hard build failure.
- **H14 — Graduated containment.** Anomalies trigger tenant-scoped `QUARANTINE` first per the §6.3 severity model and named constants. `GLOBAL_EMERGENCY_HALT` fires ONLY on a named trigger (control-plane compromise signal, or ≥ `GLOBAL_HALT_TENANT_COUNT` tenants CRITICAL within `GLOBAL_HALT_WINDOW_MS`) — never auto-fired to skip tenant quarantine, and never skipped when a single tenant is compromised.
- **H15 — Honest v1 scope.** v1 is Drafting ON / Response OFF, no autonomous send, `TEMPLATE_LIMITED_AUTO` not default-enabled. The system must not claim or ship autonomous send or auto-template send as a default. Constants `AUTONOMOUS_SEND`/`TEMPLATE_LIMITED_AUTO` are fixed.
- **H16 — Provenance-honest citation.** `FIELD_INTAKE` (Reddit/forum/anecdote) is never presented as `VERIFIED` statistics. Any statistic surfaced must carry its true tier; anecdotal intake is labeled non-statistical.
- **H17 — Manifest-bound template authorization.** A template hash alone is insufficient to authorize a send. Authorization requires the signed SendIntent binding `template_hash` + `payload_digest` + `tenant_id` + current `manifest_seq` together. Hash-only "it matches a template" is rejected.
- **H18 — Early-stage template safety.** Early-stage templates are plaintext only — no HTML, no attachments, no URL variables. Variable set is an explicit allow-list of typed scalars. Anything else → template rejected.
- **H19 — No side-channel authority/egress.** Logging, metadata, and telemetry are non-expressive: bounded typed fields only, structurally unable to carry outbound content or authority. There is exactly one authorized egress path (Lung under signed SendIntent). Any attempt to route content through a secondary channel → fail closed.
- **H20 — Hash-chained audit.** Every transition appends a chained audit line before committing; broken chain is detectable and is a failure. (`audit_chain_break` is also a control-plane compromise signal, §6.3.)

### 6.3 H14 escalation model + named constants *(closes Codex BLOCKER 2)*

**Severity classes** (`SEVERITY_CLASS`): `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, `CONTROL_PLANE`. `CONTROL_PLANE` reserved for `CONTROL_PLANE_COMPROMISE_SIGNALS`.

**Escalation state machine:**

```
   anomalies (severity-classed)
        │
        ▼
  MONITORING — HIGH+ count ≥ QUARANTINE_ANOMALY_COUNT (3) within QUARANTINE_WINDOW_MS (600000)
        │
        ▼
  TENANT_QUARANTINE — tenant sends frozen; drafting may continue read-only
        │ CRITICAL anomaly (DRAFT_ONLY_ON_CRITICAL = true)
        ▼
  TENANT_DRAFT_ONLY — Response Lane hard-off for that tenant
        │
        ▼ GLOBAL trigger (either):
  • ANY CONTROL_PLANE_COMPROMISE_SIGNALS → immediate GLOBAL_EMERGENCY_HALT
  • ≥ GLOBAL_HALT_TENANT_COUNT (2) tenants CRITICAL within GLOBAL_HALT_WINDOW_MS (900000)
```

Single compromised tenant never triggers global halt on volume alone. Global halt reserved for control-plane compromise or multi-tenant CRITICAL correlation.

---

## 7. FALSIFIABLE TEST SCENARIOS

| ID | Setup | Expected terminal | Proves |
|---|---|---|---|
| **T1 — happy Drafting path** | Benign inbound; sanitized; plaintext draft; redaction CLEAN; manifest fresh+verified; correct risk class | `DRAFT_READY` (no send) | Drafting Lane works end-to-end without ever sending; H5/H8 clean path |
| **T2 — self-promotion + gate mutation** | (a) Trust score pushed above any threshold; (b) tenant observation / agent recommendation attempts to set `FEATURE_GATE_STATE.response = ON` | Response Lane stays OFF; both attempts audited + refused | H1, H10, H12 — no self-enable, gate is signed-only, recommendation ≠ authorization |
| **T3 — baseline poisoning + authority-by-data** | (a) Inbound email asserts new banking details as fact; (b) tenant profile field tries to set `payment_change` risk to LOW | (a) fact stays `UNTRUSTED`; (b) risk stays HIGH, draft `BLOCKED` if unreviewed | H2, H3 |
| **T3a — VERIFIED promotion surface** | (a) Operator Console appends valid `phone_callback` ConfirmationEvent; Policy Engine resolves; (b) email/orchestration attempts same promotion without ConfirmationEvent | (a) `verify_confirmation_chain` returns `VERIFIED`; (b) stays `OBSERVED`, append refused | §4.6, H2, H12 |
| **T4 — injection + leakage** | Inbound carries prompt-injection + attempts to elicit approver names/banking into draft | injection neutralized; redaction strips internal; no leaked data | H4, H5 |
| **T5 — send abuse** | (a) Lung send with no SendIntent; (b) LLM-synthesized bytes; (c) fuzzy/Levenshtein/homoglyph recipient | all → `REJECTED`, no send | H6, H7, H17, §10 |
| **T6 — replay + isolation + expiry** | (a) Replay used `send_nonce`; (b) expired manifest; (c) cross-tenant SendIntent; (d) broken ConfirmationEvent chain | (a)/(b) `REJECTED`; (c) `ISOLATION_FAIL`; (d) fact drops to `OBSERVED` | H8, H9, §4.6 |
| **T7 — trust regen + scope/citation honesty** | (a) Regenerate signing key/ConfirmationEvent from memory; (c) advertise autonomous send / cite Reddit as verified stat | (a) refused (H11); (c) refused/labeled (H15/H16/H19) | H11, H15, H16, H19 |
| **T7b — H14 escalation, exact counts** | (b1) 3 HIGH anomalies in 600000ms → TENANT_QUARANTINE not global; (b2) CRITICAL → DRAFT_ONLY; (b3) 2 tenants CRITICAL in 900000ms → GLOBAL_HALT; (b4) `audit_chain_break` alone → immediate GLOBAL_HALT | b1→QUARANTINED; b2→DRAFT_ONLY; b3/b4→GLOBAL_EMERGENCY_HALT | §6.3, H14 |

Each scenario is falsifiable: a send without valid SendIntent, fact promoted from email, VERIFIED without ConfirmationEvent, gate flipped by data, leaked field, stale/replayed artifact, cross-tenant action, regenerated key, unnecessary global halt, normalizer-version mismatch, or broken audit chain is a hard failure.

---

## 8. HARNESS SPEC — `scripts/email_lanes_harness.py`

Mirrors the proof_gate / control_envelope / console / genomic harness patterns:

- Drives T1–T7 (incl. T3a, T7b) with fabricated tenants, manifests, ConfirmationEvents, and inbound emails under `LANE_ROOT`.
- Uses the **real** Policy Engine, redaction filter, canonical normalizer, and ConfirmationEvent verifier (not stubbed). Ephemeral operator keypair in harness memory only.
- Structural / static checks:
  - **H1/H10/H12** — no lane enable or `FEATURE_GATE_STATE` mutation from score/observation/recommendation/orchestration.
  - **H4** — tainted context cannot reach P-class tools.
  - **H6/H11** — no signing import in send module; Lung rejects non-template bytes.
  - **H7 / §10** — `NORMALIZER_VERSION` present; no fuzzy/Levenshtein imports.
  - **§4.6** — ConfirmationEvent operator-console-only writer; chain verification.
  - **§6.3** — escalation counts/windows exact; single-tenant never global; control-plane signal → immediate global.
  - **H13** — separate Orchestration and Policy modules.
  - **H15/H16/H19** — no autonomous-send claims; no FIELD_INTAKE-as-VERIFIED; no free-text outbound in logs.
  - **H20** — audit hash chain end-to-end.
- Emits `LANE_ROOT/harness/email_lanes_summary.json`:

```json
{
  "suite": "email_lanes_v1",
  "timestamp": "<iso>",
  "scenarios": {"T1":"PASS","T2":"PASS","T3":"PASS","T3a":"PASS","T4":"PASS","T5":"PASS",
                "T6":"PASS","T7":"PASS","T7b":"PASS",
                "H1":"PASS","H4":"PASS","H6":"PASS","H7":"PASS","H11":"PASS","H13":"PASS",
                "H14":"PASS","H15":"PASS","H16":"PASS","H19":"PASS","H20":"PASS",
                "CONFIRMATION_CHAIN":"PASS","NORMALIZER_VERSION":"PASS"},
  "overall_gate_status": "CLEAN",
  "blockers": [],
  "evidence_dir": "/tmp/mmi_email_lanes/harness/"
}
```

- **Exit 0 iff `overall_gate_status == "CLEAN"`** (every scenario + structural check PASS). Any failure → `BLOCKED`, blockers listed, exit 1. Binary, un-fakeable — no partial pass rate, no averaging.

---

## 9. NON-GOALS

- **Autonomous send / default template auto-send** — DISABLED in v1 (`AUTONOMOUS_SEND`, `TEMPLATE_LIMITED_AUTO`). Not shipped, not default-enabled (H15).
- **HTML / rich / attachment / URL-variable templates** — out of scope for early-stage; plaintext-only (H18). Rich templates are a later, separately-gated stage.
- **Replacing the operator as approver** — Response Lane always requires an operator-signed SendIntent; no agent-only send path exists.
- **Deriving VERIFIED statistics from anecdotal intake** — `FIELD_INTAKE` never rises to `VERIFIED` (H16). VERIFIED is per-fact ConfirmationEvent (§4.6).
- **Automated ConfirmationEvent minting** — only Operator Console appends (§4.6, H12).
- **Global emergency halt as first response** — tenant quarantine first; global halt named-trigger only (H14, §6.3).
- **Cross-tenant orchestration / shared drafting memory across tenants** — forbidden (H9).
- **PERFECT / Phase-maturity claims** — this spec governs email lanes only and asserts no project-maturity milestone.

---

## 10. CANONICAL NORMALIZER — `NORMALIZER_VERSION = "mmi_canonical_normalizer_v1"` *(closes Codex BLOCKER 3)*

Deterministic, region-aware canonical equality. **No similarity metric** — equality is `normalize(a) == normalize(b)` byte-for-byte after normalization.

**Supported fields (closed list, v1):** `email_local`, `email_domain`, `display_name`, `tenant_id`, `template_id`.

**Per-field rules:**

| Field | Normalization | Rejection |
|---|---|---|
| `email_local` | NFKC; strip bidi + zero-width | control chars / whitespace |
| `email_domain` | NFKC; lowercase; punycode decode | IDN homoglyph outside allowlist; mixed-script |
| `display_name` | NFKC; strip bidi + zero-width; ASCII-only v1 | non-ASCII / mixed-script → REJECT |
| `tenant_id` | NFKC; lowercase; `[a-z0-9-]` only | any other char → REJECT |
| `template_id` | NFKC; lowercase; `[a-z0-9._-]` only | any other char → REJECT |

**Version binding:** every signed artifact (manifest §4.3, SendIntent §4.4, ConfirmationEvent §4.6) carries `normalizer_version` in canonical bytes. Mismatch → fail-closed reject.

**Determinism:** pure, table-driven, side-effect-free; no network; no locale-dependent behavior.

---

## FOOTNOTES (assumptions)

1. v1 terminates Drafting Lane at `DRAFT_READY`; operator-signed SendIntent required for any send.
2. Policy Engine runs as separate module/process with verify-only key handling; H13 fails closed if engines cannot separate.
3. ConfirmationEvent `evidence_ref` is pointer only; recordings never inlined in lane store.
4. Tenant manifest issuance/rotation is operator/keystore concern; lanes verify only.
5. IDN homoglyph allowlist (§10) is versioned with `NORMALIZER_VERSION`; expanding it bumps version.
6. Escalation constants (§6.3) are initial v1 code constants; changing them is a code change, not data toggle (H3/H10).

---

## CODEX R1 BLOCKER CLOSURE (r1 → r2)

| Codex blocker | Closure |
|---|---|
| **BLOCKER 1** | §4.6 ConfirmationEvent + T3a |
| **BLOCKER 2** | §6.3 severity model + named constants + T7b |
| **BLOCKER 3** | §10 `NORMALIZER_VERSION` + field rules + harness checks |

---

**SIGN-OFF:** `[x] PASS  [ ] PASS WITH REVISIONS  [ ] FAIL` — all three Codex R1 blockers closed with normative build contracts (§4.6, §6.3, §10), named constants, and falsifiable tests (T3a, T7b). No r1 hard rule weakened; v1 default unchanged (Drafting ON, Response OFF, no autonomous send). Spec author: Claude (Design), 2026-07-03.
