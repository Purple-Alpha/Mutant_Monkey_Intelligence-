# Matt Build Authorization — M4 Evolution Gate Phase 4

**Date:** 2026-07-04  
**Authority:** Matt (explicit Phase 4 authorization)  
**Task:** `mmi-m4-evolution-gate`  
**Spec:** `MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` (r2.5) §17 Phase 4, §8  
**Plan:** `MMI_M4_PHASE4_TCB_HOST_BOUNDARY_PLAN_2026-07-04.md`  
**Codex plan review:** BUILDABLE (2026-07-04, no P4-B blockers)  
**Prerequisite:** Phase 0–3 Codex CLEAN; P4-Q1..Q10 answered

---

## Authorized

**Phase 4:** TCB + host-boundary min-viable slice — sub-phases **4A→4G only**

| Sub-phase | Deliverable |
|-----------|-------------|
| **4A** | `KEY_CUSTODY` adapter + `stage_attestation` sign/verify/lineage |
| **4B** | H0 FileId seal + signed policy manifest |
| **4C** | `host_boundary/mmi_boundary_daemon/` skeleton (Go) |
| **4D** | FS minifilter FileId enforcement (+ 9P relay fixture) |
| **4E** | WFP default-deny callout |
| **4F** | Dead-man + clock witness |
| **4G** | Integration gate → `host_boundary_min_viable` |

**Exit gate (4G):** T1, T2, T4, T7 PASS; signed-manifest refusal; clock witness live; `VERIFY_FINGERPRINT`; `host_boundary_min_viable == true`.

**Assurance scope:** Min-viable live boundary on PC1 — **not** endurance, **not** M4_MET, **not** containment-proven. R-001/R-008/R-031 targeted at **fixture scope**; remain OPEN for 48h assault until Phase 11 evidence.

**TPM/HSM:** Required for min-viable exit; software stub dev/unit only.

**Not authorized:** Phase 5+, Phase 11, 48h runner, PERFECT, GATED, M4 closed.

---

## Posture

`evolution_gate`: OUTSTANDING  
`perfect_claim`: false (pinned)  
**Blocked until:** Codex Phase 4 diff review CLEAN after 4G.

---

## Build order

Start **4A** first. Sequential 4A→4G. STOP for Codex diff review after 4G — not plan+build+gate in one pass.
