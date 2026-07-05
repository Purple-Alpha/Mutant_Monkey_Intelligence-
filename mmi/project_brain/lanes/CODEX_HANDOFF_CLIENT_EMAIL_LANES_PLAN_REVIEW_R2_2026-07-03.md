# Codex Handoff — Client Email Lanes PLAN REVIEW (R2)

**Task id:** `mmi-client-email-lanes`  
**Assignee:** Codex (pre-build plan review — re-run)  
**Build auth:** NOT AUTHORIZED  
**Spec:** `architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md` (r2, PASS)

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-client-email-lanes
REVIEW TYPE: PRE-BUILD PLAN REVIEW (R2 — post spec r2)
ASSIGNEE: Codex
AUTHORITY REPO: /mnt/c/Architectapp_clean

SPEC:
  mmi/project_brain/architecture/MMI_CLIENT_EMAIL_LANES_SPEC_2026-07.md (r2)
  SIGN-OFF: PASS (Claude Design, 2026-07-03)

R1 NOT BUILDABLE blockers — claimed closed in r2:
  1. §4.6 ConfirmationEvent — schema, operator-console writer, hash-chained log at VERIFIED_EVENTS_PATH, API, T3a
  2. §6.3 H14 escalation — QUARANTINE_ANOMALY_COUNT=3, QUARANTINE_WINDOW_MS=600000, GLOBAL_HALT_TENANT_COUNT=2, GLOBAL_HALT_WINDOW_MS=900000, CONTROL_PLANE_COMPROMISE_SIGNALS enum, T7b
  3. §10 NORMALIZER_VERSION=mmi_canonical_normalizer_v1 — field rules, rejection rules, version in signed bytes

v1 DEFAULT (unchanged): Drafting ON, Response OFF, AUTONOMOUS_SEND DISABLED

TARGET BUILD (NOT BUILT):
  Policy Engine + orchestration proposer + email_lanes_harness.py (T1–T7, T3a, T7b)

REQUIRED OUTPUT: BUILDABLE | NOT BUILDABLE with numbered blockers
```

---

## R1 blockers — resolution record

| # | R1 blocker | R2 closure |
|---|------------|------------|
| 1 | VERIFIED promotion unspecified | §4.6 + T3a |
| 2 | H14 escalation policy-only | §6.3 + named constants + T7b |
| 3 | Normalizer not pinned | §10 + harness NORMALIZER_VERSION check |

---

## After Codex BUILDABLE

Matt: `authorize build client email lanes v1` → Cursor implementation → Codex diff review.

**Parallel:** Genomic loop BUILDABLE — independent gate.

---

## Codex verdict (2026-07-03 R2)

**BUILDABLE**

R2 closes the three prior blockers with concrete build contracts:

1. ConfirmationEvent — schema, domain, log path, writer authority, verifier API, chain/signature requirements, T3a
2. H14 escalation — named constants, severity enum, exact tenant/global trigger rules, T7b
3. Canonical normalizer — `NORMALIZER_VERSION = "mmi_canonical_normalizer_v1"`, closed fields, deterministic rules, rejection rules, signed-artifact version binding

No remaining pre-build blockers.

**After BUILDABLE:** Matt `authorize build client email lanes v1` → Cursor implementation → Codex diff review.
