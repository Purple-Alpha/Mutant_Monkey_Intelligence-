# Claude Handoff — Client Email Lanes Spec R2 (Codex blockers)

**Task id:** `mmi-client-email-lanes-spec-r2`  
**Assignee:** Claude (Design)  
**Build auth:** NOT AUTHORIZED — **spec revision only**  
**Baseline:** `architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md` (r1, PASS WITH REVISIONS)  
**Codex R1:** NOT BUILDABLE — 3 blockers (below)

**Workflow:** One paste → output **complete revised spec r2** (not a diff addendum). Fold in r1 entirely; add/pin the three missing contracts.

---

## SINGLE PASTE

```
PROJECT: MMI
TASK ID: mmi-client-email-lanes-spec-r2
ASSIGNEE: Claude (Design)
BUILD AUTHORIZATION: NOT_AUTHORIZED — spec revision only

<system_role>
Lead Cybernetic Architect. Revise MMI_CLIENT_EMAIL_LANES_SPEC to r2 closing Codex R1 blockers.
Output the COMPLETE revised spec file. Do not output a patch or diff-only addendum.
</system_role>

<baseline>
  mmi/project_brain/architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md (r1)
  SIGN-OFF r1: PASS WITH REVISIONS
  Codex R1: NOT BUILDABLE — 3 blockers
</baseline>

<codex_blockers>
BLOCKER 1 — VERIFIED promotion surface (H2 / footnote 3)
  r1 assumes out-of-band VERIFIED promotion but defines no build contract.
  r2 MUST add a normative subsection defining:
  - ConfirmationEvent schema (event_id, tenant_id, case_id, fact_key, fact_value_hash,
    confirmation_method enum: phone_callback|portal_ack|in_person_log, confirmer_id,
    confirmer_role, confirmed_at_ms, evidence_ref, prior_tier, new_tier=VERIFIED)
  - Writer: who may append (operator console only — NOT orchestration engine)
  - Signature/log: Ed25519 over canonical event bytes OR hash-chained append-only log with
    operator attestation field — pick one v1 canonical form
  - Storage path: under LANE_ROOT, outside authority repo (e.g. /tmp/mmi_email_lanes/verified_events/)
  - Verifier: Policy Engine reads VERIFIED facts only from signed/logged events
  - API surface: minimal — append_confirmation_event() + verify_confirmation_chain()
  - Falsifiable test T3a: valid logged callback promotes OBSERVED→VERIFIED; email-only path cannot
  - Fail-closed: no confirmation surface → facts stay UNTRUSTED/OBSERVED (unchanged H2)

BLOCKER 2 — H14 escalation constants (T7(b))
  r2 MUST add named constants table + severity model:
  - SEVERITY_CLASS: {LOW, MEDIUM, HIGH, CRITICAL, CONTROL_PLANE}
  - TENANT_QUARANTINE_TRIGGER: e.g. HIGH anomaly count ≥ N in WINDOW_MS
  - GLOBAL_EMERGENCY_HALT_TRIGGER: CONTROL_PLANE compromise OR ≥ M tenants CRITICAL in GLOBAL_WINDOW_MS
  - Named constants (no policy prose only): QUARANTINE_ANOMALY_COUNT, QUARANTINE_WINDOW_MS,
    GLOBAL_HALT_TENANT_COUNT, GLOBAL_HALT_WINDOW_MS, CONTROL_PLANE_COMPROMISE_SIGNALS (closed enum)
  - Escalation state machine: anomaly → TENANT_QUARANTINE → (optional) DRAFT_ONLY → GLOBAL only on trigger
  - T7(b) must specify exact counts/windows and expected terminal per branch

BLOCKER 3 — Region-aware canonical normalizer (H7 / footnote 5)
  r2 MUST pin:
  - NORMALIZER_VERSION: "mmi_canonical_normalizer_v1" (or bump if rules change)
  - Supported fields: email_local, email_domain, display_name, tenant_id, template_id (closed list v1)
  - Rules per field: NFKC, lowercase domain, punycode decode, strip bidi/zero-width, ASCII-only display_name v1
  - Rejection rules: mixed-script display_name, IDN homoglyph outside allowlist → REJECT not normalize
  - Equality: normalize(a) == normalize(b) — deterministic, no Levenshtein
  - SendIntent/manifest verification MUST cite normalizer version in canonical bytes
  - Harness static check: NORMALIZER_VERSION constant present; no fuzzy compare imports
</codex_blockers>

<constraints>
- Preserve all r1 H-rules H1–H20 and T1–T7; extend scenarios where blockers require new branches
- v1 default unchanged: Drafting ON, Response OFF, no autonomous send
- Constants table must grow — every new threshold named
- Evidence paths stay under LANE_ROOT, outside authority repo
- Spec-only. No Python. No build authorization.
</constraints>

<output>
Complete file: mmi/project_brain/architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md
Revision: r2
SIGN-OFF: PASS | PASS WITH REVISIONS | FAIL
If all 3 blockers closed: target PASS (or PASS WITH REVISIONS if minor footnotes remain)
</output>

<no_explanations_directive>
Respond with the production-grade markdown spec file payload only.
</no_explanations_directive>
```

---

## After Claude r2

1. Relay spec to Cursor for filing
2. Codex R2 plan review → target BUILDABLE
3. Matt build auth only after BUILDABLE

**Parallel:** Genomic loop independent — `authorize build step 5 genomic loop` when ready.
