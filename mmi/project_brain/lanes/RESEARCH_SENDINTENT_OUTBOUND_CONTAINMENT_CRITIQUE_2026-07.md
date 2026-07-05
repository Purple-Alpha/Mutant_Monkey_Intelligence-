# MMI SendIntent Outbound Containment — Empirical Critique (Research)

**Status:** RESEARCH / CONCEPT — NOT BUILT  
**Authority:** Matt (Super) — research lane (ChatGPT/Gemini synthesis)  
**Date filed:** 2026-07-03  
**Purpose:** Empirical fact-check and structural hardening of Response Lane / template-limited auto doctrine. Rejects Levenshtein and “mathematically unbreakable” claims; defines SendIntent protocol and formally bounded outbound authority.

**Companion:** `lanes/RESEARCH_FEATURE_GATE_DRAFTING_RESPONSE_LANES_2026-07.md`  
**Master handoff:** `lanes/MMI_EMAIL_DRAFTING_RESPONSE_CONTAINMENT_HANDOFF_2026-07-03.md`  
**Parallel build (parked):** AGI §5 step 5 genomic loop — BUILDABLE, not authorized. This research does not authorize outbound/email build.

**Not build authorization.**

---

## Claim level (corrected)

**Achievable:**

```text
Mathematically bounded outbound authority under a formally specified trusted computing base.
Formally bounded authority under explicit assumptions.
```

**Not claimed:**

```text
Mathematically unbreakable zero-trust containment system.
Prompt injection eliminated.
LLM behavior proven safe.
Fuzzing complete against all attacks.
Withstood 100% of attacks.
```

---

## 1. Empirical fact-check of core assertions

### Claim 1: “Token Smuggling via Semantic Variance”

**Verdict: substantially correct, imprecisely named.**

Empirical support: OWASP LLM Top 10 — prompt injection via hidden text in emails, documents, attachments as indirect carriers. 2025 special-character attack research — Unicode manipulation, homoglyphs, structural perturbation, encoding obfuscation; encoding-based attacks especially effective.

**Naming correction:** Not “deterministic vulnerability” (transformers are probabilistic). The defect is architectural:

```text
Security-sensitive outbound bytes must not be synthesized by an LLM.
Any generative reconstruction of an approved template creates an uncontrolled output channel
whose behavior cannot be proven equivalent to the approved artifact.
```

Precise class:

```text
untrusted expressive output channel + parser/rendering differential + downstream authority
```

### Claim 2: Deterministic manifest-based template compilation closes smuggling

**Verdict: closes one major class, not the whole vector.**

Correct direction — eliminates LLM paraphrase/smuggle in template body. Does **not** close:

```text
variable fields          template selection       manifest lookup
template repo compromise schema ambiguity         renderer/client interpretation
MIME/header encoding     logging side channels    approval UI rendering mismatch
downstream email client  attachments              link rewriting / IDN / tracking pixels
```

Narrower security property:

```text
Given: trusted template repo, valid signed manifest, deterministic renderer,
      canonical variable map, exact outbound envelope validator, capability-limited sender,
Then: the LLM cannot alter outbound template bytes outside approved variable fields.
```

### Claim 3: Byte-level Levenshtein validation as outbound boundary

**Verdict: weak control — diagnostic only, not authorization path.**

Levenshtein measures edit distance, not parser equivalence, MIME safety, Unicode normalization, or renderer behavior.

**Required invariant (region-aware canonical equality):**

```text
For every byte outside declared variable spans: payload_byte[i] == template_byte[i]
For every byte inside variable spans: value ∈ schema_language(variable_name)
Then: payload == deterministic_render(template_id, canonical_variables)
```

Levenshtein may remain as **telemetry only**.

### Claim 4: Genomic Loop + AST fingerprinting + fuzzing as definitive build gate

**Verdict: overclaimed.**

AST catches some static drift; not behavior safety for dynamic code, reflection, config indirection, prompt-conditioned behavior, parser differentials. Fuzzing is sampling, not proof. NIST AI RMF: ongoing risk management, not absence-of-failure certification.

```text
The Genomic Loop can provide evidence of bounded conformance under specified assumptions.
It cannot be a definitive proof of safety for arbitrary self-modifying logic.
```

---

## 2. Structural vulnerability matrix

| Area | Spec control | Hidden failure mode | Severity | Required correction |
|------|-------------|---------------------|----------|---------------------|
| Template generation | LLM bypassed | Template choice / variables still agent-driven | High | Separate `template_selection` from `template_execution` |
| Manifest hash | Hash lookup | Hash ≠ authorization context | High | Signed manifest: hash + variables + risk class + signer + version + expiry |
| Variable schema | Primitive-only | “String sanitized” underspecified | High | Per-field regular languages, not generic primitives |
| Unicode stripping | Remove homoglyphs | Normalization mismatch validator vs client | High | Canonicalize once; validate after; render from canonical bytes |
| String variables | Length-bound | Short malicious URL/domain/token still passes | High | Allowlisted enums; safe alphabets; semantic constraints |
| Levenshtein validator | Byte edit distance | Cannot identify legal variable spans | **Critical** | Deterministic render equality + span proofs |
| Output boundary | Body validation | Headers/subject/display-name bypass body gate | **Critical** | Validate entire outbound envelope |
| The Lung | Execution layer | If it accepts arbitrary payloads, it is the TCB | **Critical** | Lung accepts only signed `SendIntent`; never raw text |
| Draft approval UI | Human review | UI renders normalized text; signed bytes differ | **Critical** | Approve canonical artifact + byte hash + diff |
| Template repository | Read-only runtime | CI/CD / release pipeline compromise | **Critical** | Signed releases, reproducible builds, transparency log |
| Trust score | Promotion trigger | Self-measured trust → self-promotion | **Critical** | Advisory only; no authority mutation |
| Genomic AST | Static fingerprint | Dynamic dispatch, plugins, deserialization | **Critical** | Capability-secure runtime + deny-by-default policy |
| Fuzzing | Automated attacks | Coverage illusion | High | Property tests + static constraints + red-team corpus |
| State mutation | Genomic Loop | Drift via config, prompt, memory, vector DB, flags | **Critical** | Treat config/data/prompt/memory as code-equivalent authority |
| Infinite loops | Time-bounded sandbox | Recurrence across cycles / queue amplification | High | Global work budget, depth limits, per-tenant fuses |
| Token smuggling | Template controls | Metadata, IDs, telemetry as expressive channels | High | Validate all channels; structured channels non-expressive |
| Agent containment | Feature gates | Stale/cached/racy gate reads | **Critical** | Gate state read transactionally at Lung execution time |

### Added optimization rows (stress test)

| Optimization | Intended property | Hidden failure | Severity | Correction |
|--------------|-------------------|----------------|----------|------------|
| Dual-buffer layout | Static vs variable separation | Renderer joins buffers wrong; MIME/HTML drift | Critical | Typed template AST + proof-carrying spans |
| XOR static equality | Static bytes unchanged | Index alignment fails when variable lengths vary | High | AST region identity, not raw byte indices |
| Regex-bound variables | Block encoding tricks | Unicode, URLs, header context unsafe | High | Per-context grammars + canonical encoders |
| Signed token proofs | Bind template to auth | Orchestrator as signing oracle | Critical | Separate proposer / policy / signer / executor |
| Agent clearance check | Block unauthorized invoke | Stale clearance, tenant/case confusion | Critical | Bind token to tenant, case, template, gate snapshot, nonce, expiry |
| WASM sandbox | Limit execution | Host imports, fuel exhaustion, compiler bugs | High | Zero imports; fuel; no host I/O; reproducible chain |
| Abstract execution proving | Memory/time bounds | Undecidable for expressive programs | Critical | Non-Turing-complete policy DSL for mutations only |
| Write-once Lung | Reduce exploitability | Replay, duplicate sends, stale approvals | Critical | Nonce, idempotency key, expiry, monotonic ledger |
| Template-limited auto | Bounded response | Template **selection** is authority | Critical | Selection policy-derived, not agent-derived |

---

## 3. Answers to four research questions

### Q1: Is “Token Smuggling via Semantic Variance” empirically accurate?

**Yes, with naming corrections.** OWASP indirect injection carriers; 2025 Unicode/encoding attack literature. Not every homoglyph “decodes to exploit” — many create filter bypass or rendering differential.

### Q2: Does deterministic manifest compilation entirely close Response Lane smuggling?

**No.** Closes LLM-authored template body smuggling only. Remaining: malicious variables, wrong template, repo compromise, UI deception, MIME/header injection, reply-thread confusion, IDN spoofing, metadata side channels.

### Q3: Latent failure modes of Levenshtein validation?

1. Global distance vs regional policy (legal variable expansion indistinguishable from mutation)  
2. No parser semantics (one byte in MIME boundary / URL / header delimiter)  
3. Variable length dominates distance metric  
4. Validator/recipient Unicode normalization mismatch  
5. Non-body channels unprotected (subject, reply-to, attachments, HTML/plain multipart)

**Replacement pipeline:**

```text
1. Parse template into typed AST.
2. Each hole: type, max length, canonicalization, allowed language, context (body vs subject vs header).
3. Canonicalize variables before render.
4. Render deterministically.
5. Independently re-parse rendered output.
6. Assert: rendered_bytes == renderer(template_id, canonical_variables)
           non_variable_spans == template_spans
           variable_spans ∈ declared languages
           outbound_envelope ∈ signed policy
7. Sign final canonical SendIntent.
8. Lung sends only signed SendIntent objects.
```

No threshold. No fuzzy distance. No “close enough.”

### Q4: AST fingerprint bypasses for mutating LLM-generated code/config?

Dynamic import, reflection, deserialization hooks, decorators, dependency substitution, env/feature-flag behavior, prompt-as-code drift, vector-memory poisoning, time bombs, network callbacks, parser differentials scanner vs runtime.

**AST checks = admission filter only. Runtime capability control = actual boundary.**

Genomic Loop must inspect not only source code but: prompts, tool policies, template manifests, feature gates, routing rules, memory/vector DB policy content, schema files, CI/CD, dependencies, container images, environment variables.

---

## 4. Architectural optimizations (definitive corrections)

### A. Formally bounded, not unbreakable

Achievable invariants:

```text
System cannot send unless Lung receives valid signed SendIntent.
Lung cannot construct SendIntent objects.
Agents cannot access send capabilities.
Templates cannot execute code.
Variables cannot escape declared languages.
Gate state cannot promote without signed authority.
All outbound actions append-only logged.
```

### B. SendIntent protocol (capability-secure Lung)

Agents never call `send()`. Only `Lung` sends. Lung accepts only:

```yaml
SendIntent:
  version: "1.0"
  send_intent_id: "<uuid>"
  tenant_id: "<uuid>"
  case_id: "<uuid>"
  recipient:
    email: "<validated_email>"
    display_name: "<optional_safe_display>"
  template_id: "<id>"
  template_manifest_hash: "<sha256>"
  variables_hash: "<sha256>"
  rendered_body_hash: "<sha256>"
  rendered_envelope_hash: "<sha256>"
  risk_class: "LOW"
  approval:
    mode: "HUMAN_APPROVED_SEND"
    signer_id: "Matt"
    signature: "<ed25519>"
  policy_snapshot_hash: "<sha256>"
  gate_snapshot_hash: "<sha256>"
  nonce: "<uuid>"
  idempotency_key: "<uuid>"
  expiry: "<timestamp>"
  ledger_seq: "<monotonic>"
```

Lung **recomputes everything**. Any hash mismatch → refuse.

### C. Signed manifests (not bare hashes)

Manifest binds:

```text
template bytes hash
template ID + version
risk class + allowed lane mode
allowed recipients / recipient classes
allowed variable schema (per-context grammars)
allowed tenant + sender identity
transport envelope policy
expiry + revocation pointer
authorizing signer + policy version
```

Then sign. Bare hash proves identity of bytes, not permission to send in context.

### D. Formal languages for variables (not generic strings)

Prefer: `enum`, `CASE_ID`, `RFC3339 date`, fixed-precision currency, `sha256`, pre-approved phrase ID.

For necessary text: ASCII subset, no markup, no URLs (Stage 1–2 ban URLs entirely), no bidi/zero-width, NFKC, single-script policy, no CR/LF in headers.

Context-specific typing example:

```yaml
Variable:
  name: "case_reference"
  type: "CASE_ID"
  context: ["plain_text_body"]
  grammar: "MMI_CASE_ID_V1"
  canonicalization: "ASCII_UPPER"
  max_length: 32
  encoder: "plain_text_no_markup"
```

Variable approved for `plain_text_body` must not appear in subject, HTML attribute, URL, MIME header, attachment filename, or display name without separate grammar.

### E. Full email envelope validation

Validate: From, Reply-To, To, Cc/Bcc, Subject, Message-ID policy, References/In-Reply-To, plain body, HTML (if ever allowed), multipart consistency, attachments, links, display names, provider headers.

**Early stages: disallow HTML and attachments entirely.**

### F. Prompts / memory / config = code-equivalent authority

“No code change” can still mutate behavior via prompts, gates, templates, vector DB.

### G. Proof tiers (replace “100% fuzz pass”)

```text
Tier 0: Static schema validation
Tier 1: Deterministic render equivalence
Tier 2: Capability isolation test
Tier 3: Property-based fuzzing
Tier 4: Red-team corpus regression
Tier 5: Reproducible build + signed artifact
Tier 6: Runtime policy enforcement
Tier 7: Append-only audit verification
```

Pass: no known failing case; no critical invariant breach; coverage threshold; mutation cannot widen authority; promotion requires operator signature.

### H. Monotonic authority constraint

```text
For any mutation M:
  authority_after(M) <= authority_before(M)
unless: valid_operator_signature AND signed_policy_allows_transition
        AND rollback_plan AND emergency_stop verified
```

### I. Loop and queue fuses

```text
max cycles per case | max spawned tasks | max retry count
max critic-ring recursion | max token spend | max wall-clock time
max outbound recommendations per tenant | duplicate-state detection
idempotency keys | circuit breaker
```

### J. Trusted computing base (explicit)

**TCB:**

```text
policy engine | manifest signer | template compiler | schema compiler
canonicalizer | SendIntent signer/verifier | Lung | key management
gate ledger | audit ledger | approval UI | runtime sandbox | CI/CD artifact signer
```

**Untrusted / semi-trusted:**

```text
LLMs | agents | retrievers | email body/metadata | vector memory
draft text | critic-ring opinions | trust scores | external documents
```

---

## 5. Lung design (corrected)

Not literally zero state. **Minimal, explicit, non-agentic, non-expressive state.**

```text
The Lung is a deterministic capability endpoint that accepts only signed, canonical
SendIntent objects, recomputes policy validity, emits exactly one outbound effect,
and writes an append-only audit record.
```

**Forbidden:** LLM, prompt, template selection, variable interpretation beyond schema verify, mailbox browsing, attachment/HTML generation, arbitrary body input.

**Permitted state:** verification keys, sender credential handle, policy verify code, nonce/replay cache, rate counters, audit sink, transport adapter.

---

## 6. Correct flow (agents propose, never send)

```text
1. Agent proposes ResponseRequest.
2. Policy engine evaluates.
3. Template compiler renders deterministic artifact.
4. Validator proves region constraints + full envelope.
5. Human or auto-policy gate signs SendIntent.
6. Lung recomputes and sends (idempotent, replay-resistant).
7. Audit ledger records immutable outcome.
```

**Separation of duties:**

```text
Agent proposes → Policy evaluates → Signer signs (outside swarm) → Lung executes
```

Orchestration engine must **not** be sole signer. Higher-risk modes: threshold authorization (e.g. 2-of-2 for template-limited auto activation).

---

## 7. Negative capability tests (required)

```text
agent attempts raw send → reject
template not authorized for case → reject
variable with CRLF → reject
HTML injection → reject
URL variable (Stage 1) → reject
stale gate snapshot → reject
expired token → reject
replayed SendIntent → reject
cross-tenant send → reject
high-risk category in template-limited mode → reject
unsigned response-lane promotion → emergency halt
```

---

## 8. WASM / self-mutation bounds

WASM = containment substrate, not mathematical proof. Zero imports, fuel metering, memory cap, no wall-clock/randomness/network/filesystem.

Self-evolution: tune declarations in **non-Turing-complete policy DSL** only — not arbitrary Python `decide_send()`.

AST fingerprint = tamper-evidence signal, not security boundary. Runtime must be safe even if AST inspection misses a construct.

---

## 9. Corrected bounded spec (draft)

```yaml
MMI_Response_Containment:
  claim_level: "FORMALLY_BOUNDED_OUTBOUND_AUTHORITY"
  not_claimed:
    - "mathematically_unbreakable_full_system"
    - "prompt_injection_eliminated"
    - "LLM_behavior_proven_safe"
    - "fuzzing_complete_against_all_attacks"

  core_invariants:
    - "Agents cannot send."
    - "LLMs cannot generate outbound bytes for auto-send."
    - "The Lung accepts only signed SendIntent objects."
    - "SendIntent signatures bind tenant, case, template, variables, policy, gate, recipient, sender, expiry, nonce."
    - "Templates are signed manifests, not bare hashes."
    - "Variables validated by context-specific formal grammars."
    - "Static template regions byte-identical to signed template bytes."
    - "Dynamic regions proven members of declared variable languages."
    - "Feature gates cannot self-promote."
    - "Unsigned authority expansion → emergency halt."
    - "All sends append-only logged."
    - "Runtime mutation only in non-Turing-complete policy DSL or zero-import bounded VM."

  response_modes:
    DISABLED: { outbound_allowed: false }
    RECOMMEND_ONLY: { outbound_allowed: false }
    HUMAN_APPROVED_SEND: { outbound_allowed: true, requires_human_signature: true }
    TEMPLATE_LIMITED_AUTO:
      outbound_allowed: true
      requires_human_signature: false
      allowed_templates: "signed_low_risk_only"
      max_risk_class: "LOW"
      forbidden_categories: [payment, credentials, legal, contracts, hr, authority, account_change]
```

---

## 10. Final architectural law

```text
MMI may evolve capability.
MMI may not evolve authority.
```

Hardened:

```text
Agents propose.
Policy proves.
Humans or signed gates authorize.
The Lung executes only canonical, signed, replay-resistant SendIntent objects.
Everything else is evidence, never authority.
```

---

## 11. Resolutions to companion doc open questions

| Question (feature gate doc) | Resolution (this critique) |
|-----------------------------|----------------------------|
| Q3: TEMPLATE_LIMITED_AUTO byte binding | Hash-locked `SendIntent` with Lung recompute; no LLM synthesis; context-specific variable grammars |
| Q2: Gate promotion signoff domain | Separate promotion manifest domain OR console signoff subtype — both require operator Ed25519; trust engine advisory only |
| Q4: Sidecar vs in-process | Lung + gate ledger read at send time; signer outside swarm; transactional gate snapshot hash in token |

---

## References

- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [OWASP LLM02: Insecure Output Handling](https://genai.owasp.org/llmrisk2023-24/llm02-insecure-output-handling/)
- [OWASP LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
- [Special-Character Adversarial Attacks (arXiv 2508.14070)](https://arxiv.org/html/2508.14070v1)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [SandboxEval: Securing Test Environment for Untrusted Code (arXiv 2504.00018)](https://arxiv.org/abs/2504.00018)
- [WebAssembly Core Specification](https://webassembly.github.io/spec/core/)

---

## Lane note

Research only. Promotion path: Claude contract spec → Codex BUILDABLE → Matt build auth → Cursor implementation. Aligns with console Ed25519 H5 pattern extended to outbound `SendIntent` domain.
