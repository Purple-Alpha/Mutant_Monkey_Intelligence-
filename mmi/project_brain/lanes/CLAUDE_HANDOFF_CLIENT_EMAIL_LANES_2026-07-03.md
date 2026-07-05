# Claude Handoff — Client Email Lanes (Drafting / Response / Containment)

**Task id:** `mmi-client-email-lanes-spec`  
**Assignee:** Claude (Design)  
**Build auth:** NOT_AUTHORIZED — **spec only**  
**Framework:** `lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md`

**Evidence basis:** Consolidated architecture handoff filed 2026-07-03. Email capability is **research → spec** lane. Does **not** compete with AGI §5 step 5 genomic loop (BUILDABLE, awaiting Matt build auth).

**Workflow:** Copy **SINGLE PASTE** below into one fresh Claude window. This is **greenfield r1 authoring** (no prior spec exists). Claude drafts the spec, runs internal adversarial self-review, outputs **final r1 only**.

**Important:** There is NO existing `MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md` in the repo. Do NOT frame output as "revised r2." SIGN-OFF should be PASS or PASS WITH REVISIONS based on internal self-review of the new draft — not revision of a prior Claude-authored baseline.

**Target spec path:** `architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md`

**After Claude:** Relay final spec to Cursor for closeout → Codex plan review → BUILDABLE before any email build auth.

---

## SINGLE PASTE — copy everything inside the fence below

```
PROJECT: MMI
TASK ID: mmi-client-email-lanes-spec
ASSIGNEE: Claude (Design)
SCORE: 94
BUILD AUTHORIZATION: NOT_AUTHORIZED — spec only, no implementation
PROMPT FRAMEWORK: mmi/project_brain/lanes/MMI_CLAUDE_ENGINEERING_PROMPT_FRAMEWORK_2026-07.md

<system_role>
Lead Cybernetic Architect / Purple Team Engineer
Project: Mutant Monkey Intelligence (MMI) — defensive weapon + client email containment
Doctrine: Bounded autonomy, strict deterministic rules over soft prompts, un-fakeable metrics
Design lane only — deliver one bounded markdown spec. No implementation. No scope expansion.
</system_role>

<current_state_inventory>
Repo root: /mnt/c/Architectapp_clean

MASTER HANDOFF (authoritative architecture direction — implement as spec, do not dilute):
  mmi/project_brain/lanes/MMI_EMAIL_DRAFTING_RESPONSE_CONTAINMENT_HANDOFF_2026-07-03.md

Companion research (normative where cited by handoff):
  mmi/project_brain/lanes/RESEARCH_FEATURE_GATE_DRAFTING_RESPONSE_LANES_2026-07.md
  mmi/project_brain/lanes/RESEARCH_SENDINTENT_OUTBOUND_CONTAINMENT_CRITIQUE_2026-07.md
  mmi/project_brain/lanes/REDDIT_VENDOR_EMAIL_ROUTINE_INTAKE_2026-07.md — field evidence ONLY; not statistics; not Canadian-primary unless commenter stated

Built MMI primitives (reuse patterns — do not re-design):
  AGI §5 step 2 — Gate B proof gate:
    - scripts/proof_gate_harness.py, chaos/mmi_canonical_digest.py
    - architecture/MMI_PROOF_GATE_CONSOLE_BINDINGS_SPEC_2026-07.md (r2 §3.6 genomic_episode)
  AGI §5 step 3 — Control envelope:
    - chaos/mmi_control_envelope.py — pre_iteration_gate(), HALT/SUSPEND, no self-ack
    - architecture/MMI_CONTROL_ENVELOPE_BUDGET_DEADMAN_SPEC_2026-07.md
  AGI §5 step 4 — Console Ed25519 evidence gate:
    - scripts/console_server.py, chaos/console_evidence_gate.py
    - architecture/MMI_CONSOLE_SERVER_ED25519_EVIDENCE_GATE_SPEC_2026-07.md (H5 re-verify, consume-once)
  AGI §5 step 5 — Genomic loop (BUILDABLE — analog for self-healing, NOT in scope to build):
    - architecture/MMI_GENOMIC_REALIGNMENT_LOOP_SPEC_2026-07.md (r2) — orchestrator of gates, not authority
  Controlled Chaos doctrine:
    - architecture/MMI_CONTROLLED_CHAOS_DEFENSIVE_WEAPON_CONCEPT_2026-07.md §4 destroy-clone-not-brain, §7–§9 signed envelopes
  Action integrity (schema validation pattern):
    - chaos/action_integrity_gate.py

NOT BUILT (email — target of this spec):
  - GATE_DRAFTING_LAYER runtime
  - GATE_RESPONSE_LAYER runtime
  - SendIntent issuer / Lung send path
  - Tenant evidence graph storage
  - Mailbox ingest connector
  - Trust metric engine runtime
  - Authority microkernel process separation (spec may define; v1 may defer physical split)

Parallel build (DO NOT claim email build authorized):
  - Genomic loop plan review: BUILDABLE — Matt has NOT authorized step 5 build
  - Evolution gate: OUTSTANDING — no PERFECT / Phase 3 / 30-day claims
</current_state_inventory>

<core_doctrine>
Non-negotiable (must appear verbatim or equivalent in spec §1):

  MMI may evolve capability.
  MMI may not evolve authority.

Expanded:
  Disposable agents. Persistent evidence. Signed authority. Regenerating capability. Non-regenerating trust.

Security goal (realistic):
  Build an AI that remains useful under partial compromise: detect infection, shed compromised layer,
  preserve evidence, regenerate clean capability from signed authority, rejoin only after proof.

First product lane name (v1):
  Human-Approved Email Response Drafting Layer
  NOT "Email Responder Agent"

Client evolution framing:
  Same vault. Different maze. No tenant can redesign the vault.
  Do not build client-evolving agents.
  Build globally fixed agents that consult tenant-specific evidence graphs.
  Tenant graph influences risk assessment; tenant graph cannot grant permission.

Self-healing:
  MMI may self-heal capability. MMI may not self-heal authority.
</core_doctrine>

<existing_implementation_pattern>
Console signoff pattern (extend to tenant promotion / SendIntent — new manifest domain):
  - Operator signs canonical manifest bytes; server re-verifies
  - H5: downstream must re-verify; file existence ≠ authorization
  - consume-once (bundle_id, sign_seq) or nonce replay cache for SendIntent

Control envelope pattern:
  - Fail-closed HALT/SUSPEND; loop cannot self-ack
  - Monotonic seals; sticky latch

Proof gate pattern:
  - overall_gate_status CLEAN|BLOCKED — binary
  - Evidence outside authority repo (/tmp/mmi_* pattern)

Genomic loop pattern (self-healing analog for email tenant/case):
  detect → freeze → preserve evidence → shed → restore from signed clean source → reduced mode → signed promotion

SendIntent (from handoff + SendIntent critique — normative for Response Lane when built):
  - Lung recomputes all hashes; rejects expired/replayed/mismatched
  - No LLM synthesis of security-sensitive outbound bytes
  - Region-aware canonical verification — NOT Levenshtein
  - Signed template manifest binds context (not bare hash)

Evidence tiers (memory firewall):
  OBSERVED → CORROBORATED → VERIFIED → AUTHORITY
  Unverified inbound email must NOT update high-trust baselines directly.

Taint labels (typed information flow):
  UNTRUSTED_INBOUND_EMAIL, SANITIZED_EVIDENCE, TENANT_OBSERVATION, VERIFIED_TENANT_FACT,
  AUTHORITY_POLICY, DRAFT_TEXT, SEND_INTENT, OUTBOUND_EXECUTION
  TENANT_OBSERVATION may never flow to FEATURE_GATE_STATE.
  DRAFT_TEXT may not flow to OUTBOUND_EXECUTION.
  Only SIGNED_SEND_INTENT may flow to OUTBOUND_EXECUTION.

Agent classes:
  Q-class: see raw email, no tools, no send, no authority writes
  P-class: tools only, sanitized evidence in, no raw email
  Lung: send only, no LLM, no draft, no template choice — signed SendIntent only
</existing_implementation_pattern>

<task_definition>
Write the complete markdown spec file:

  mmi/project_brain/architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md

Scope — client email lanes v1 spec: drafting + containment architecture; Response Lane defined but DISABLED in v1 default posture.

1. OPERATIONAL DEFINITION
   - v1 honest scope: Drafting ON (policy-enabled), Response OFF (default DISABLED), no autonomous send, no mailbox mutation authority
   - Product stage model: DAY 1 → MATURITY → PROMOTION → NEVER (from handoff)
   - Constants table: max draft bytes, max evidence retention, observation decay TTLs, case freeze duration, rate limits, /tmp audit roots, tenant isolation boundaries
   - Realistic security claim level: FORMALLY_BOUNDED_OUTBOUND_AUTHORITY under explicit assumptions — NOT "mathematically unbreakable"

2. BOUNDARY VS ADJACENT SYSTEMS
   - GATE_DRAFTING_LAYER vs GATE_RESPONSE_LAYER vs Global Authority Kernel vs Tenant Evidence Graph
   - Trust engine: ADVISORY_ONLY — emits PROMOTION_RECOMMENDATION, never mutates gates
   - Console Ed25519 gate (operator promotion signoff — define relationship: new manifest domain vs console subtype)
   - Control envelope (case/tenant loop budget if applicable)
   - Genomic loop (control-plane self-healing analog — reference only)
   - Reddit field intake (design input only — no fabricated SMB statistics)
   - Forbidden v1: auto-send, auto-reply, mailbox delete/archive/move, link click, attachment open without sandbox, inbound email as instructions, self-promotion, acting as Matt identity

3. FEATURE GATE STATE MACHINE
   - Drafting Lane states: DISABLED | MONITOR_ONLY | ENABLED
   - Response Lane states: DISABLED | RECOMMEND_ONLY | HUMAN_APPROVED_SEND | TEMPLATE_LIMITED_AUTO | CONDITIONAL_AUTO
   - Transitions: ONLY via signed operator/client authority + tenant manifest; never via trust score threshold alone
   - Monotonic authority: authority_after(M) <= authority_before(M) unless valid_operator_signature + signed_policy_allows_transition
   - Degraded modes: CASE_FREEZE, TENANT_QUARANTINE, DRAFT_ONLY, EVIDENCE_ONLY, RESPONSE_LANE_DISABLED, GLOBAL_EMERGENCY_HALT

4. DATA SCHEMAS
   - TenantEvidenceGraph node/edge schema (vendors, domains, contacts, cadence, verification outcomes — all with evidence tier + decay)
   - Verified tenant fact record (source, confidence, verification status, last_seen, decay, tenant_id, case_id, evidence hash, verifier, allowed_use, not_allowed_use)
   - SanitizedEvidence object (from UNTRUSTED_INBOUND_EMAIL)
   - DraftResponse object (redacted drafting context — separate from detection context)
   - PROMOTION_RECOMMENDATION object (advisory — from, to, confidence, evidence_window, invariant_failures, human_rejection_rate, required_signature)
   - TenantMaturityManifest / FeatureGateManifest (signed — binds gate state, tenant_id, policy snapshot, expiry)
   - SendIntent schema (full fields from handoff — spec for future Response Lane; v1 defines, v1 default does not execute)
   - SignedTemplateManifest (template bytes hash + risk class + allowed variables + recipient class + lane mode + signer + expiry)
   - Append-only authority ledger event types

5. TYPED INFORMATION FLOW + MEMORY FIREWALL
   - Normative taint labels and allowed/forbidden flows (diagram or table)
   - Baseline poisoning attack pattern + required OBSERVED/CORROBORATED/VERIFIED/AUTHORITY tier rules
   - Authority-by-data prohibition: tenant profile may provide evidence, not set thresholds/gates/risk boundaries
   - Draft leakage: detection may use rich graph; drafting receives minimal safe communication view

6. Q-CLASS / P-CLASS / LUNG SEPARATION
   - Capability matrix: what each class can see, tool, write, send
   - Physical separation recommendation (agent runtime / authority kernel / Lung) — v1 may spec defer implementation
   - Key classes: operator, policy, template manifest, tenant maturity, SendIntent, audit — external/HSM preferred

7. PASS / FAIL LINES + HARD RULES (H-rules)
   Minimum H-rules (expand with adversarial coverage):
   - H1: No outbound send without valid signed SendIntent verified by Lung
   - H2: No LLM-generated bytes on auto-send path (template-limited auto bypasses LLM for final bytes)
   - H3: No gate promotion without operator signature (trust score cannot flip gates)
   - H4: No unverified inbound → VERIFIED tenant fact or AUTHORITY tier
   - H5: No TENANT_OBSERVATION → FEATURE_GATE_STATE flow
   - H6: No cross-tenant action
   - H7: Tenant quarantine on anomaly before global halt (except control-plane compromise)
   - H8: Self-heal capability only from signed clean artifacts — not compromised memory/agent output
   - H9: Append-only audit for every authority change and send attempt
   - H10: Unsigned authority expansion → EMERGENCY_HALT
   - Fail-closed on any schema/signature/taint violation

8. SELF-HEALING / SHED / REGENERATE LOOP (tenant/case scope)
   - 10-step loop from handoff (detect → freeze → evidence → cut capabilities → shed → restore signed clean → rebuild verified facts only → invariant tests → reduced mode → signed promotion)
   - What may regenerate vs non-regenerating trust (signing keys, approvals, gate authority, SendIntent permissions)
   - Relationship to genomic loop (control-plane) vs tenant email containment (data-plane)

9. FALSIFIABLE TEST SCENARIOS T1–T7
   - T1: Inbound vendor spoof → drafting produces evidence + draft to review queue; no send; no gate change
   - T2: Trust score exceeds threshold → PROMOTION_RECOMMENDATION emitted; Response Lane stays DISABLED until signed manifest
   - T3: Baseline poisoning attempt (3-month slow norm) → unverified OBSERVED data cannot elevate to VERIFIED without human/out-of-band
   - T4: Prompt injection in email body → Q-class ingests; P-class receives sanitized evidence only; injection cannot reach AUTHORITY_POLICY or FEATURE_GATE_STATE
   - T5: Draft with sensitive tenant detail → redacted drafting view blocks internal phone/approver leak in draft output
   - T6: Agent attempts raw send / unsigned SendIntent → Lung rejects; audit line written
   - T7: Tenant anomaly → TENANT_QUARANTINE + DRAFT_ONLY; global lane unaffected; evidence preserved

10. HARNESS SPEC (name fixed for future build)
   - scripts/client_email_lanes_harness.py — hermetic --evidence-dir, scenarios T1–T7
   - Emits client_email_lanes_summary.json with overall_gate_status CLEAN|BLOCKED
   - Exit 0 iff CLEAN
   - v1 harness may simulate without live mailbox (fixture emails from chaos/fixtures pattern)

11. NON-GOALS
   - v1 autonomous send / auto-reply / mailbox mutation
   - v1 TEMPLATE_LIMITED_AUTO activation (define schema; default DISABLED)
   - Live mailbox OAuth/production connector (defer — spec interfaces only)
   - Claim PERFECT / evolution gate / 30-day continuous operation
   - Replace genomic loop, console server, or control envelope
   - Generic "Email Responder Agent" product positioning
   - Reddit anecdotes as industry statistics or Canadian-primary evidence
   - Levenshtein as security boundary
   - Orchestration engine as sole signer

Required spec sections (mirror genomic/console layout):
  1. Operational Definition (+ constants + claim level)
  2. Boundary vs Adjacent Systems
  3. Feature Gate State Machine (+ degraded modes)
  4. Data Schemas
  5. Typed Information Flow + Memory Firewall
  6. Q/P/Lung Separation
  7. Pass / Fail Lines (+ H-rules)
  8. Self-Healing Loop
  9. Falsifiable Test Scenarios T1–T7
  10. Harness Spec
  11. Non-Goals
  Footnotes for assumptions
  SIGN-OFF line: PASS | PASS WITH REVISIONS | FAIL
</task_definition>

<execution_constraints>
1. Deliver the complete markdown spec file only — no chat intro, no closeout prose.
2. Spec-only. No Python. No tasks.json edits. No build authorization.
3. Every threshold must be a named constant — trust scores are advisory metrics, not gate switches.
4. Evidence/audit paths outside authority repo (/tmp/mmi_client_email/ or similar pattern).
5. Seven falsifiable T1–T7 scenarios with expected verdict + state transition.
6. v1 honesty: first shippable lane is drafting + evidence + human review queue; Response Lane spec-complete but default DISABLED.
7. Field research from Reddit intake informs workflow questions (email → business action) — do not cite as verified SMB statistics.
8. Explicitly reject: auto-promotion from ReputationScore, Levenshtein outbound validation, LLM outbound byte synthesis, inbound email mutating gates.
9. Multi-party authorization table for gate transitions (operator, tenant admin, policy review for higher modes).
</execution_constraints>

<adversarial_self_review>
This is greenfield r1 — no prior spec exists in repo or in your session history.

Workflow:
1. Author the complete draft spec per task_definition.
2. Immediately perform adversarial self-review on your own draft (do not stop for user input between steps).
3. Fix every finding inline.
4. Output ONE final spec file only.

Attack scenarios to defend against (bake in as H-rules and T1–T7 where applicable):

- Auto-enable Response Lane when trust score exceeds threshold (self-promotion bypass)
- Write VERIFIED or AUTHORITY tier facts directly from inbound email text (baseline poisoning)
- Lower risk thresholds via tenant profile so payment-change email becomes "low risk" (authority-by-data)
- Smuggle prompt injection from raw email into P-class tools or policy kernel (taint violation)
- Leak internal approver names, phone fragments, or banking context in drafts (draft leakage)
- Send email via Lung without signed SendIntent or with LLM-synthesized outbound bytes
- Use Levenshtein or fuzzy "close enough" validation instead of region-aware canonical equality
- Replay stale SendIntent, expired tenant manifest, or reused nonce
- Cross-tenant send or read (tenant isolation failure)
- Mutate FEATURE_GATE_STATE from TENANT_OBSERVATION or agent recommendation
- Regenerate signing keys, operator approval, or gate authority from compromised memory (non-regenerating trust violation)
- Confuse PROMOTION_RECOMMENDATION with authorized promotion
- Use orchestration engine as sole signer without policy engine separation
- Skip tenant quarantine and trigger unnecessary GLOBAL_EMERGENCY_HALT
- Claim v1 includes autonomous send or TEMPLATE_LIMITED_AUTO as default enabled
- Cite Reddit field intake as verified Canadian SMB statistics
- Treat template hash alone as sufficient authorization (missing signed manifest context)
- Allow HTML, attachments, or URL variables in early-stage templates
- Split authority across undocumented side channels (logging, metadata, telemetry as expressive outbound)

Fix every finding inline in the spec. Do not output a draft plus review notes — output ONE final r1 spec file only.
SIGN-OFF: PASS if clean on first internal pass; PASS WITH REVISIONS if self-review changed material content. Never claim this is r2 or a revision of a prior spec you did not write.
</adversarial_self_review>

<no_explanations_directive>
Respond with the production-grade markdown spec file payload only. Assumptions go in spec footnotes — not chat prose.
</no_explanations_directive>
```

---

## Closeout checklist (Cursor PM — after Matt relays design)

- [x] Spec path: `architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md`
- [x] SIGN-OFF: PASS WITH REVISIONS
- [x] Core doctrine present (capability vs authority, non-regenerating trust)
- [x] v1 scope honest (Drafting ON, Response OFF default)
- [x] T1–T7 falsifiable scenarios present
- [x] SendIntent + signed manifest defined; Levenshtein rejected
- [x] Evidence tiers + memory firewall + taint flow rules
- [x] Trust engine advisory only; no auto-promotion path
- [x] Harness spec with exit 0 iff CLEAN
- [x] Codex plan review handoff filed
- [x] Does NOT authorize email build or compete with genomic loop BUILDABLE gate

**Codex handoff:** `lanes/CODEX_HANDOFF_CLIENT_EMAIL_LANES_PLAN_REVIEW_2026-07-03.md`

**After Codex BUILDABLE:** Matt `authorize build client email lanes v1` → Cursor implementation → Codex diff review.
