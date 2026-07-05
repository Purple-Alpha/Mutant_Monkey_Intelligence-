# MMI Operator Signing Threat Model

**Status:** HARD CONTROL — documentation only  
**Date:** 2026-07-04  
**Related:** RR-M4-007, AGI Pillar 4 (Alignment)

**Forbidden claims:** self-healing without sign-off, GATED without evidence bundle.

---

## Thesis

Human cryptographic sign-off is **necessary but attackable**. The operator is part of the threat surface.

---

## Threats

| ID | Threat |
| -- | ------ |
| OS-01 | Operator fatigue |
| OS-02 | Urgency / near-pass pressure |
| OS-03 | Forged or incomplete completion summaries |
| OS-04 | Forged CLEAN statements from wrong lane |
| OS-05 | Stolen credentials / key misuse |
| OS-06 | Compromised signing keys |
| OS-07 | Ambiguous "buildable" / "authorize" language |
| OS-08 | Out-of-band instruction spoofing |
| OS-09 | Summary manipulation (broad safety from narrow pass) |
| OS-10 | Coercive escalation after partial phase pass |

---

## Controls (required before GATED)

- Signature covers **evidence bundle**, not intent alone (AGI pathway Pillar 4).
- Sign-off checklist: patch hash, proof-of-fix, proof-of-no-regression, rollback token, budget snapshot.
- **No-sign-on-ambiguity:** reject signatures over incomplete or unbound summaries.
- Separate **summary** from **raw evidence** (`MMI_EVIDENCE_SUMMARY_BINDING_2026-07.md`).
- Record signer identity, timestamp, and scope of authorization.
- `perfect_claim: false` pinned until explicit operator GATED after M4 FINAL — never default true.

---

## Forbidden inference

- Matt authorized Phase N build ≠ Matt authorized M4_MET.
- Human sign-off on a narrow phase ≠ system-level safety attestation.
- Signature without evidence binding = invalid promotion path.
