# MMI Governed Swarm Program Charter — Federation-Adjacent 70-Agent Motion

**Document Reference:** MMI-CHT-2026-06-24

**Status:** **PROGRAM CHARTER** — §11 SIGNED 2026-06-24 by Matt Nichol (MMI-DEC-140) · NOT BUILD AUTHORIZED · NOT GOVERNED_AGENT · NOT AUTH-5

**Lane:** Stage B · b04 — governance envelope for the Blue Team swarm program

**Closeout:** MMI-DEC-136

**Owner:** Matt Nichol — sole signing authority on every §11, contract, and routing decision

**Authority repo:** `/home/socialarchitect/northstar`

**Boundary:** This charter governs *how* agents enter the swarm. It does **not** deploy them, authorize waves, or relax AUTH-5. **Not** the Todd pilot (MMI-DEC-129). **Not** a buyer-proof quiz.

**Source-of-truth links:**
- `agent_concepts/Blue_Team_Swarm_70_Agent_Scoreboard.md` (live roster + build sequencer — reconciled §4)
- `agent_concepts/_Blue_Team_Swarm_Architecture_Map_SPARK.md` (70-agent inventory origin)
- `agent_concepts/Mutant_Monkey_Blue_Team_Swarm_Design_Tree.md` (canonical 6-layer design map)
- `4. Product_Roadmap/Agent_Design_Contract_Template_Deep_Dive.md` (per-agent gate template)
- `docs/mmi/contracts/004_immune_federation_mesh_contract.md` (federation mesh — b03; topology/pricing at b05)
- `mmi/research/MMI_FEDERATION_SMB_SEAT_ECONOMICS_RESEARCH_MMI-DEC-132.md` (seat economics — b05 fork)
- `PROJECT_HANDSHAKE.md` (#1 terminal target = full 70-agent governed swarm)

**Standing rule (binding on this program):**

```text
Charter acceptance ≠ agent authorization.
No agent enters the swarm without its own signed Agent Design Contract + §11 + scoreboard row + Evidence Stage gating.
```

---

## §1 Intent

Establish the governing frame under which the Mutant Monkey Security Blue Team swarm scales toward a **70-agent planning ceiling** across federated SMB seats — expanding detection coverage **without scaling risk linearly**.

Evidence-first. Detect-not-enact. Per-agent gating. The charter is the **program envelope**; individual agents still run the full Rubric → spec → gate → §11 path.

---

## §2 The "70" — read this first

### What 70 means

| Claim | Truth |
|---|---|
| **70 is authorization** | **FALSE.** Charter acceptance spins up **zero** agents. |
| **70 is a hard runtime cap** | **FALSE.** It is a **planning ceiling** from the SPARK inventory. |
| **70 is seat-economics-derived** | **FALSE at this lane.** The number comes from Matt's operator-declared ten-team SPARK map (`_Blue_Team_Swarm_Architecture_Map_SPARK.md`), adopted as the non-reducible terminal target in `PROJECT_HANDSHAKE.md`. Seat-economics bounds (agents-per-seat, cost-per-seat) land at **b05** (MMI-DEC-140), not here. |
| **Scoreboard = exactly 70 rows** | **FALSE.** The scoreboard tracks SPARK **#1–#70** plus net-new infrastructure and control-plane rows (**#71–#105+**). Program scope includes both; the **70** label names the SPARK inventory ceiling. |

### Per-agent entry gate (unchanged)

Every agent enters only through:

1. Signed **Agent Design Contract**
2. **Evidence Stage 1 → 2 → 3** promotion discipline
3. **§11 signature (Matt-only)**
4. Assigned **scoreboard row**
5. Dispatcher-routed lifecycle (`SIGNED_UNBUILT` → build → audit → `GATED` / `GOVERNED_AGENT`)
6. **7-component Health Score** (grade A–F per `Agent_Health_Score_Deep_Dive.md`)

No agent runs ungoverned. No agent without a scoreboard row. No wave without its own gate.

---

## §3 Founding constraints (non-negotiable spine)

| Constraint | Rule |
|---|---|
| **AUTH-5** | Autonomous task selection **blocked**, swarm-wide. The 70-agent motion does not relax this. |
| **Detect-not-enact** | Swarm surfaces evidence; takes no autonomous enacting action on tenant mail at Stage A. Stage B autonomy agents (e.g. #38) remain behind `NEEDS_STAGE_B_AUTH`. |
| **Per-agent gating** | Evidence Stages + promotion/demotion conditions + §6.5 progressive hardening (every real-case miss → permanent regression test before re-promotion). |
| **Blast Radius Controller** (`#89` / adversarial `#101`) | Cross-tenant / cross-agent impact bounded. **Precondition satisfied** for multi-agent wave governance (see §4.3). Fission pre-condition: real-tenant calibration still open per scoreboard. |
| **Watcher Agents** (`#85–87`) | Swarm health monitoring in-path; sole legitimate fission trigger source (WA-D1). **GATED.** |
| **Safe-Stop** (`#94` / adversarial `#102`) | Matt-only exit. Swarm-wide kill switch live for the program's life. **GATED + adversarially hardened.** |
| **Mode Controller** (`#92` / adversarial `#99`) | Homeostasis, quorum, mesh consent modes. OQ decisions hold (120s quorum-loss timeout, etc.). **GATED + adversarially hardened.** |
| **§11** | Per agent/component, Matt-only. Charter filing does not substitute. |
| **Rule 4 (scoreboard)** | Scoreboard rows rank and record; they never mean "approved to build." |

---

## §4 Scoreboard alignment (reconciled 2026-06-24 · git `3ef88e0`)

Cursor reconciled live `Blue_Team_Swarm_70_Agent_Scoreboard.md` against this charter. **Alignment verified** for program framing; individual row promotion remains per-agent.

### §4.1 SPARK inventory snapshot (#1–#70)

| Runtime status (prefix) | Count | Program note |
|---|---:|---|
| `GOVERNED_AGENT` | 14 | W0 seed + breadth runway (ES1 Synthetic) |
| `GATED` | 10+ | Built wrappers/control rows within SPARK band; **not GOVERNED_AGENT** unless promoted |
| `NOT_STARTED` | ~19 | Net-new detection/orchestration; W1+ candidates |
| `SPEC_ONLY` / `DETECTOR_FUNCTION` | ~12 | Contract or code exists; promotion bar not cleared |
| `GOVERNANCE_DOC_ONLY` | 7 | Doc-only surfaces (#4, #5, #51, #53, #65, #66, #70-partial) |
| `RECLASSIFY` / `merged` | 10 | Triaged — not silent exclusions |

**Headline (scoreboard):** detector stack + partially wired governance spine — **not yet a fully governed 70-agent swarm**. 14 of 70 SPARK agents at `GOVERNED_AGENT`.

### §4.2 W0 — Seed wave (confirm Evidence Stage + health)

| # | Agent | Status | Evidence Stage | Health |
|---|---|---|---|---|
| 6 | Header Analysis | `GOVERNED_AGENT` | ES1 Synthetic | 87 |
| 6A | Email Authentication | `GOVERNED_AGENT` | ES1 Synthetic | 87 |
| 8 | Ghost Thread | `GOVERNED_AGENT` | ES1 Synthetic | 87 |

**W0 gate:** PASS for ES1 confirmation. W0 does **not** authorize W1.

### §4.3 Control-plane preconditions (multi-agent waves)

| Precondition | Row | Status | Adversarial hardening |
|---|---|---|---|
| Blast Radius Controller | #89 | `GATED` | #101 ACCEPT (2026-06-15) |
| Safe-Stop State Machine | #94 | `GATED` | #102 ACCEPT (2026-06-15) |
| Mode Controller | #92 | `GATED` | #99 ACCEPT (2026-06-15) |
| Watcher Agents | #85–87 | `GATED` | Built 2026-06-12 |
| Load / Specialisation Fission | #90 / #91 | `GATED` | Real-tenant threshold calibration still open |
| Command spine | #1–#3 | `GATED` | **Not GOVERNED_AGENT**; not production wired |

**Multi-agent wave envelope:** BRC + Safe-Stop + Mode Controller + Watchers **sufficient for charter acceptance**. W1+ expansion still requires per-agent contracts; fission at scale still blocked on tenant calibration per MMI-DEC-133.

### §4.4 Beyond SPARK (#71+) — in program scope

Net-new rows (Phase 1–6 infrastructure, knowledge foundation, detection phases, MMI #105) are **in program scope** but outside the "70" SPARK label. They follow the same per-row gate. Notable:

- **#84** ReconciliationAgent — GATED, adversarially hardened (#100)
- **#105** MMI Governance Invariants — `SIGNED_CONTRACT` + Lane 1 probe; Lane 2+ held

### §4.5 Agents without satisfactory rows

**No SPARK #1–#70 agent lacks a scoreboard row.** Rows marked `RECLASSIFY`, `merged`, or `NOT_STARTED` are present with explicit blockers — not silent exclusions.

---

## §5 Federation / seat-economics boundary

**b04 holds the gate. b05 holds the numbers.**

| Topic | Owner | This charter |
|---|---|---|
| Tenant isolation | Load-bearing everywhere | Enforced via blast radius (`#89`/`#101`), load fission (`#90`), specialisation fission (`#91`), Privacy Filter (`#93`) |
| Seat economics (agents-per-seat, cost-per-seat) | **b05** · MMI-DEC-140 · Matt §11 | Named only — no numbers locked |
| Federation mesh topology / pricing / consent | **b05** + mesh contract §11 | Federation-**adjacent** only; mesh contract at `docs/mmi/contracts/004_immune_federation_mesh_contract.md` (CONTRACT_DRAFT) |
| Lung production | Downstream Stage C | **BLOCKED** per MMI-DEC-133 |

**Federation-adjacent** means: swarm growth must respect tenant namespace boundaries and opt-in federation consent when mesh I/O exists. It does **not** mean uncontrolled cross-tenant data sharing. Guardrail 11 preserved.

---

## §6 Program structure and phasing

Growth runs in **gated waves**. A wave does not open until the prior wave's evidence clears.

| Wave | Contents | Gate |
|---|---|---|
| **W0 — Seed** | #6, #6A, #8 (Header, Email Auth, Ghost Thread) | **CONFIRMED** ES1 + health baseline |
| **W0b — Command spine** | #1–#3 GATED wrappers | Per-agent GOVERNED_AGENT promotion + wiring — **not** implied by charter |
| **W1+ — Expansion** | New agents toward SPARK ceiling | **Each** requires signed Agent Design Contract + §11 + scoreboard row + blast-radius coverage |
| **Program rollup** | Health rollup across active agents | Manual Health Score board + demotion enforcement at Build Loop Step 6.5 |

**Depth gate:** Stage 2+ promotion blocked until real-data intake opens (`NEEDS_REAL_DATA` on #54–#60).

**Stage B gate:** Autonomy agents blocked until signed Stage B authorization (`NEEDS_STAGE_B_AUTH` on #38).

---

## §7 Evidence and decision gates

| Gate | Rule |
|---|---|
| Charter acceptance | Recorded MMI-DEC-136 as governing frame — **not** operational green light |
| Agent authorization | **Never** implied by this charter |
| Per-wave outcomes | ACCEPT / REVISE / REJECT / PARK / VERIFY / ESCALATE — each evidence-backed in decision log |
| Promotion | Evidence Stage ledger in `decision_cycles_log.md`; §6.5 regression tests on demotion |

---

## §8 Roles

| Role | Who | Boundary |
|---|---|---|
| Signing authority | Matt Nichol | All §11, routing, Safe-Stop exit |
| Advisory | Claude (b04 prose) | Plans only — no repo write |
| Execution | Cursor | Repo write, DEC-136, closeout |
| Review / red-team | Codex / Gemini / ChatGPT | Adversarial cross-check before individual wave builds |

---

## §9 Matt §11 and charter acceptance

**§11 SIGNED 2026-06-24 (MMI-DEC-140)** — bundled with federation economics fork and Immune Federation Mesh platform contract at Stage B end.

### Sign-off line

> Matt Nichol June 24th 2026

Per Authorship Rule: operator-authored signature, placed verbatim.

**Charter acceptance (MMI-DEC-136 + MMI-DEC-140):** ACCEPT as governing envelope with standing rule §2/§7 attached.

**Not authorized by §11 signature:** any agent build, wave opening beyond W0 confirmation, GOVERNED_AGENT promotion, production dispatch, AUTH-5, Todd pilot, mesh bus implementation.

---

## §10 Open items (deferred)

1. ~~Matt §11 signature on charter text~~ — **SIGNED 2026-06-24 (MMI-DEC-140).**
2. Seat-economics caps tying agent count to SMB tiers — operator direction affirmed; locked MSRP still deferred to commercial execution.
3. W0b command-spine GOVERNED_AGENT promotion decision.
4. Real-tenant fission threshold calibration (scoreboard pre-condition on #90/#91).
5. Per-wave adversarial review cadence for W1+ (Codex pre-build per existing BUILD route doctrine).

Matt Nichol — program charter filed Stage B b04 (MMI-DEC-136).
