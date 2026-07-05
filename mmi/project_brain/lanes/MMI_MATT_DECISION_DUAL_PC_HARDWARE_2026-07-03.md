# Matt Decision — Dual-PC Hardware Topology (Chaos + Local Inference)

**Date:** 2026-07-03  
**Authority:** Matt (product owner)  
**Status:** DECISION RECORD — binds hardware procurement and agent lanes  
**Purchase window (Matt):** ~3.5–5 weeks for second PC (faster / stronger)  
**Related:** `MMI_WEAPON_RUNTIME_BLOCKERS_2026-07.md` §2, `MMI_PURPLE_TEAM_ATTACK_SCOPE_2026-07.md`, `MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` §8/§17, `MMI_PROJECT_ROADMAP_2026-07.md` (polyglot critic ring)

**Not claimed:** BUILDABLE, PERFECT, M4 closed, ladder complete, build authorization for Phase 11.

---

## Decision

MMI will operate on **two physically separated machines** once PC2 arrives:

| Machine | Codename | Role |
|---------|----------|------|
| **PC1** | **Authority / TCB** | Live brain: `C:\Architectapp_clean`, evidence root, signing/`KEY_CUSTODY`, Windows-native boundary daemon (WFP + minifilter), orchestrator, operator seat, Codex/Cursor build lane |
| **PC2** | **Chaos / Forge** | Battlefield + local inference: chaos clone, purple assault, mirror/tarpit workloads, **local LLM shards** (critic ring + assault pressure), draft-patch replay sandbox — **never** authority writes |

**Principle (unchanged):** *Destroy the clone, not the brain.*

Dual LLM is **not** two API tabs on one laptop. It is **heterogeneous models on separated hardware** — aligned with polyglot defense and runtime blocker §2 (avoid cloud rate-limit self-DoS during inflation).

---

## Network & trust rules (non-negotiable)

1. **PC2 has no write path to `AUTHORITY_ROOT`** — no SMB admin share, no synced git push to live brain, no shared `%TEMP%` workflow.
2. **Evidence signing stays on PC1 only** — PC2 may emit assault telemetry; chain append + exit artifacts are TCB on PC1 (or PC1-attached `EVIDENCE_ROOT` volume).
3. **Treat PC2 as hostile-adjacent** — separate VLAN or firewall rules; assault traffic identities ≠ operator identities.
4. **WSL on PC1 is not the M4 perimeter** — host-native boundary still required on PC1 per research + §8.
5. **Sanitizer before any LLM reads hostile logs** — on **both** machines; hardware separation does not replace `deterministic_sanitizer.py` or §13.1 replay bar.

---

## PC2 procurement intent (Matt: 3.5–5 weeks)

**Primary job:** local inference + honest purple/chaos — not a generic second dev box.

| Priority | Spec guidance |
|----------|----------------|
| **GPU** | Discrete GPU, **16GB+ VRAM** class preferred (room for 7–8B quant + parallel critic/assault shards later) |
| **RAM** | **32GB minimum**, 64GB if budget allows (containers + clone + inference headroom) |
| **Storage** | Fast NVMe — clone churn, evidence mirrors, model weights |
| **CPU** | Strong single-thread + enough cores for Docker/Podman air-lock pattern (blocker §3) |
| **Network** | Wired Ethernet; static or reserved DHCP; document MAC for firewall rules |

**PC1 during transition:** prioritize stability, TPM path for future `KEY_CUSTODY`, Windows Pro for WFP/minifilter work — GPU optional on brain box.

---

## Predictions — what we have until the ladder is built

**Ladder definition:** `MMI_M4_EVOLUTION_GATE_SPEC_2026-07.md` §17 — Phases **0→11**, 48h runner **last**. Matt ruling r2.5: full matrix bar at `M4_MET` (capture + replay per exploit).

**As of 2026-07-03 (honest posture):**

| Milestone | State |
|-----------|--------|
| Phase 0 (import ban) | Built; **Codex diff re-review pending** (dynamic import fix) |
| Spec | r2.5 filed + Matt no-shortcuts ruling committed |
| Phases 1–11 implementation | **Not built** (design + Phase 0 only) |
| Host boundary daemon | **Design only** — long pole |
| Phase 11 (48h M4 FINAL) | **Not authorized** |

### Window A — **Now → PC2 arrival (~3.5–5 weeks)** — PC1 only

**Realistic build progress (if Codex CLEAN + staged auth continues):**

| Weeks | Likely ladder position | What you're actually running |
|-------|------------------------|------------------------------|
| **0–1** | Phase 0 CLEAN → Phase 1–2 | Invariant suite, fuzz harness on authority repo |
| **1–2** | Phase 3 (+ start Phase 4 design) | Sandbox escape suite; boundary daemon **spec/build start** |
| **2–3.5** | Phase 4 in progress | TCB work (Go daemon, WFP, minifilter, `KEY_CUSTODY` design) — **slow** |
| **3.5** | Possibly Phase 4 min-viable slice **if** boundary lands | Still **no** honest dual-machine purple |

**What you have (capabilities, not claims):**

- Single-machine dev + chaos clone patterns (`chaos_lab_provisioner.py`)
- Purple against **clone on same host** — useful, but **not** production-honest separation
- Cloud/API LLMs for research + spec lanes — **not** polyglot inflation at scale (blocker §2 risk)
- Track B ops (closeout, war room, iceberg ingress) — **continues independently**
- **No** 48h ceremony, **no** PERFECT, **no** `M4_MET` from a real run

**Prediction (confidence: medium):** In 3.5 weeks on PC1 alone, **Phases 0–3 done + Phase 4 partially built** is aggressive-but-plausible; **Phase 4 min-viable complete** is optimistic; **C2+ endurance runs** unlikely before PC2 unless boundary surprises easy.

### Window B — **PC2 online (week ~4–5+)** — dual machine

**Unlocks (not shortcuts — enablers):**

- Honest **purple LLM vs defender/critic LLM** without shared host compromise
- **Local shards** for assault + critic ring — reduces API rate-limit self-DoS (blocker §2)
- **C4 dress rehearsal** for §13.1 draft-patch + replay on isolated hardware before M4 FINAL
- Parallel compute while PC1 stays clean operator/TCB seat

**Still required after PC2 (unchanged):**

- Phase 4 boundary min-viable on **PC1**
- Full §17 ladder through C-M4 → C2 → C3 → C4 → M4
- Matt `authorize build` + Codex CLEAN per phase
- 48h wall clock for Phase 11

### Window C — **Full ladder to Phase 11 (48h runnable)**

**Prediction (confidence: medium-low — boundary is the wild card):**

| Scenario | Earliest Phase 11 *runnable* | Notes |
|----------|------------------------------|-------|
| **Optimistic** | ~**8–10 weeks** from 2026-07-03 | Phase 4 lands fast; endurance stages schedule cleanly |
| **Base case** | ~**10–14 weeks** | Boundary daemon + minifilter iteration normal |
| **Conservative** | ~**14–18+ weeks** | TCB surprises, replay pipeline rework, purple finds structural gaps |

**PC2 at week 4–5 does not pull Phase 11 into week 5.** It pulls **honest adversarial topology** into week 5 — the ladder still walks Phase 0→10 first.

**PERFECT / GATED:** Only after a **real** Phase 11 run passes all pass lines + operator attestation — not when PC2 ships, not when spec is clean.

---

## Sequencing — what to do before PC2 arrives

1. **Finish Phase 0** — Codex diff CLEAN on import ban.
2. **Walk Phases 1–3 on PC1** — invariants, fuzz, sandbox escape (no 48h detours).
3. **Start Phase 4 on PC1** — boundary daemon is the critical path; PC2 does not replace this.
4. **Draft `MMI_CRITIC_RING_RULES_v1`** (design lane) — so PC2 GPU has a job day one.
5. **Document PC2 network rules before plug-in** — firewall/VLAN checklist, no authority share.
6. **Do not** treat PC2 as permission to skip ladder rungs or soften r2.5 replay bar.

---

## What PC2 is NOT

- Not a substitute for Windows-native boundary on PC1
- Not proof of PERFECT or M4 closed
- Not an excuse to run max chaos against live `AUTHORITY_ROOT`
- Not "dual LLM" marketing — it's **separated roles with sanitizer + evidence discipline**

---

## Agent lane binding

All agents: reference this doc for hardware topology questions. Do not propose single-machine purple as production-equivalent. Do not shorten §17 because PC2 exists. Procure and wire PC2 per roles above.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-07-03 | Matt decision + ladder timeline predictions (3.5–5 wk PC2 window) |
