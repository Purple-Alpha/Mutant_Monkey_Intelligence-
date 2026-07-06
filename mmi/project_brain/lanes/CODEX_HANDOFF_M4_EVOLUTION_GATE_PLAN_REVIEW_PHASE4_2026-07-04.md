# Codex Plan Review — M4 Evolution Gate Phase 4

**Task id:** `mmi-m4-evolution-gate`  
**Review type:** PRE-BUILD PLAN REVIEW (Phase 4 — TCB / host boundary)  
**Date:** 2026-07-04  
**Build auth:** NOT AUTHORIZED — plan review only  
**Spec:** `MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` (r2.5) §8, §3.1, §17 Phase 4  
**Plan artifact:** `MMI_M4_PHASE4_TCB_HOST_BOUNDARY_PLAN_2026-07-04.md`  
**Prerequisites:** Phase 0–3 Codex CLEAN; Phase 3 policy-model scope only

**Verdict:** **BUILDABLE** (2026-07-04) — no P4-B blockers  
**Matt auth:** Phase 4 build authorized 2026-07-04 (`MMI_MATT_AUTH_M4_PHASE4_BUILD_2026-07-04.md`)

**Not claimed:** M4_MET, containment-proven, GATED, PERFECT

---

## Codex verdict (recorded)

```text
BUILDABLE — no P4-B blockers found.
```

1. P4-Q1..Q10 answered with concrete TCB boundaries, key custody, exit signing/verification, chaos read/write limits, daemon death, WFP/minifilter fail-closed, PC2 residual scope.
2. Min-viable exit testable: T1, T2, T4, T7, signed-manifest refusal, clock witness, VERIFY_FINGERPRINT.
3. Sub-phases 4A→4G sequential; endurance blocked until 4G.
4. Residuals honest: R-030 OPEN until PC2 ops; no containment-proven / M4_MET / GATED / PERFECT claims.
5. TPM/HSM required for min-viable exit; software stub unit/dev only.

**Scope if Matt authorizes:** Phase 4A–4G only. Build authorized 2026-07-04.

---

## Codex prompt (paste this)

```
PROJECT: MMI
TASK ID: mmi-m4-evolution-gate
REVIEW TYPE: PRE-BUILD PLAN REVIEW (Phase 4)
ASSIGNEE: Codex
AUTHORITY REPO: /mnt/c/MMI

SPEC PHASE: §17 Phase 4 — KEY_CUSTODY, stage_attestation, host_boundary/mmi_boundary_daemon + WFP/minifilter (§8)

PLAN ARTIFACT:
  mmi/project_brain/lanes/MMI_M4_PHASE4_TCB_HOST_BOUNDARY_PLAN_2026-07-04.md

PREREQUISITE:
  Phase 0–3 Codex CLEAN
  Phase 3 = policy model only (SE-FS..SE-KEY DENY/CONTAINED) — NOT live boundary

PRE-BUILD GATE:
  P4-Q1..Q10 answered in plan artifact (assurance case updated to ANSWERED-plan)

MIN-VIABLE EXIT (§8):
  T1/T2 deny-write, T4 dead-man, T7 WFP default-deny,
  signed-manifest refusal, clock-witness live
  → host_boundary_min_viable == true

PLAN SUB-PHASES: 4A custody → 4B seal/manifest → 4C daemon → 4D minifilter → 4E WFP → 4F dead-man/clock → 4G integration

VERIFY (read-only):
  Read plan artifact §2 (P4-Q1..Q10) against spec §8, §3.1, §14 T1/T2/T4/T7
  Read dual-PC decision memo for P4-Q10 layering
  Confirm assurance case P4-Q table shows ANSWERED-plan

ASSURANCE SCOPE:
  Plan defines bounded min-viable slice — NOT endurance, NOT M4_MET, NOT full canary engine (Phase 6)
  R-030 remains OPEN until PC2 ops proof — plan states this honestly

POSTURE: evolution_gate OUTSTANDING — no PERFECT, no M4 closed

REQUIRED OUTPUT: BUILDABLE | NOT BUILDABLE with numbered findings (P4-B1..)

If BUILDABLE:
  - Scope is Phases 4A–4G only
  - Matt may consider matt_auth_phase4 AFTER Codex BUILDABLE
  - Still NO build until Matt authorizes

Do NOT authorize build. Do NOT claim GATED or M4 met.
```

---

## Plan lane summary (for Matt relay)

Phase 4 plan answers all ten pre-build questions:

| Q | One-line answer |
|---|-----------------|
| P4-Q1 | TCB = PC1 KEY_CUSTODY, stage_attestation, Go daemon, minifilter, WFP, EVIDENCE_ROOT, H0 seal, dead-man, clock witness |
| P4-Q2 | Outside = clone/PC2 forge, LAB_ROOT, runner (no keys), read-only snapshot, observability read-only |
| P4-Q3 | Signing keys in TPM/HSM on PC1 only; ENFORCEMENT_KEY is FileId set not crypto |
| P4-Q4 | KEY_CUSTODY signs exits over full tuple incl. signed_H0 + parent_exit_hash |
| P4-Q5 | verify_exit + H0 match + lineage to single C-M4; forged → CANARY-023 |
| P4-Q6 | Snapshot read only; no live authority mount; no keys/evidence/production |
| P4-Q7 | Default deny all authority FileId writes + link-create + non-allowlist egress |
| P4-Q8 | Dead-man >30s → CANARY-005 → HALT unpoliced_perimeter |
| P4-Q9 | WFP/minifilter/daemon failure → fail-closed HALT; no monitor-only mode |
| P4-Q10 | Layered: network ops + T1/T2/FileId + fingerprint; R-030 OPEN until PC2 proof |

Build sliced **4A→4G**; exit = `host_boundary_min_viable` per T1/T2/T4/T7 + manifest refusal + clock witness.

---

## Expected Codex checks

| Check | Plan reference |
|-------|----------------|
| FileId-not-SID (9P) | P4-Q7, 4D exit, R-031 |
| EXIT_BINDS_H0 | P4-Q4/Q5, 4A exit |
| AUTHORITY_MOUNT_DEFAULT | P4-Q6 |
| BOUNDARY_DEADMAN_GAP_S = 30 | P4-Q8, 4F |
| H-EVID-001 EVIDENCE_ROOT placement | P4-Q1, 4B |
| TPM required for min-viable exit (no stub) | P4-Q3 |
| Phase 6 canary engine not conflated | §1 bounds |
| No endurance before 4G | §3 sub-phases |

---

## Next steps after Codex

| Codex verdict | Next lane |
|---------------|-----------|
| **BUILDABLE** | Matt `matt_auth_phase4` → Cursor 4A first → Codex diff after 4G |
| **NOT BUILDABLE** | Claude/plan lane revises plan → re-review |

**Blocked regardless:** build, GATED, M4 claim, Phase 11.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-04 | Phase 4 plan review handoff filed |
